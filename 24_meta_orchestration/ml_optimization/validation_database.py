#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSID - Validation History Database (ADVANCED PHASE 4)
Tracks rule execution history for ML-based failure prediction

Storage:
- SQLite database for historical validation results
- Tracks which rules fail on each commit
- Records co-occurring failures for pattern detection
- Minimal overhead (<50ms per validation)
"""

import sqlite3
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timezone
from dataclasses import dataclass
import threading


@dataclass
class ValidationResult:
    """Single rule validation result."""
    rule_id: str
    passed: bool
    execution_time: float
    severity: str  # CRITICAL, HIGH, MEDIUM
    failure_message: Optional[str] = None
    evidence: Optional[Dict] = None


@dataclass
class ValidationRun:
    """Complete validation run metadata."""
    commit_hash: str
    changed_files: List[str]
    author: str
    timestamp: datetime
    results: List[ValidationResult]


class ValidationDatabase:
    """
    Thread-safe SQLite database for validation history.

    Designed for:
    - Fast inserts (<50ms overhead)
    - Efficient queries for ML training
    - No write contention in CI
    """

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._create_tables()

    def _create_tables(self):
        """Create database schema with indexes for ML queries."""
        with self._lock:
            conn = sqlite3.connect(str(self.db_path))
            try:
                # Main validations table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS validations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        commit_hash TEXT NOT NULL,
                        commit_hash_short TEXT NOT NULL,
                        changed_files TEXT NOT NULL,
                        changed_files_count INTEGER NOT NULL,
                        author TEXT NOT NULL,
                        branch TEXT DEFAULT 'main',
                        total_rules INTEGER DEFAULT 0,
                        failed_rules INTEGER DEFAULT 0,
                        total_time_ms INTEGER DEFAULT 0,
                        time_to_first_failure_ms INTEGER,
                        INDEX idx_commit (commit_hash),
                        INDEX idx_timestamp (timestamp),
                        INDEX idx_author (author)
                    )
                """)

                # Rule results table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS rule_results (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        validation_id INTEGER NOT NULL,
                        rule_id TEXT NOT NULL,
                        passed BOOLEAN NOT NULL,
                        execution_time_ms FLOAT NOT NULL,
                        severity TEXT NOT NULL,
                        failure_message TEXT,
                        evidence_json TEXT,
                        execution_order INTEGER,
                        FOREIGN KEY (validation_id) REFERENCES validations(id),
                        INDEX idx_rule_id (rule_id),
                        INDEX idx_passed (passed),
                        INDEX idx_validation (validation_id)
                    )
                """)

                # File change patterns table (for feature engineering)
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS file_patterns (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        validation_id INTEGER NOT NULL,
                        file_path TEXT NOT NULL,
                        file_extension TEXT,
                        file_type TEXT,
                        lines_added INTEGER DEFAULT 0,
                        lines_deleted INTEGER DEFAULT 0,
                        is_yaml BOOLEAN DEFAULT 0,
                        is_python BOOLEAN DEFAULT 0,
                        is_config BOOLEAN DEFAULT 0,
                        FOREIGN KEY (validation_id) REFERENCES validations(id),
                        INDEX idx_file_path (file_path),
                        INDEX idx_file_ext (file_extension)
                    )
                """)

                # Rule failure patterns (co-occurrence tracking)
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS failure_patterns (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        rule_id_1 TEXT NOT NULL,
                        rule_id_2 TEXT NOT NULL,
                        co_occurrence_count INTEGER DEFAULT 1,
                        last_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(rule_id_1, rule_id_2),
                        INDEX idx_rule1 (rule_id_1),
                        INDEX idx_rule2 (rule_id_2)
                    )
                """)

                # Model performance tracking
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS model_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        model_version TEXT NOT NULL,
                        trained_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        training_samples INTEGER NOT NULL,
                        accuracy FLOAT,
                        precision_score FLOAT,
                        recall_score FLOAT,
                        f1_score FLOAT,
                        false_positive_rate FLOAT,
                        false_negative_rate FLOAT,
                        feature_count INTEGER,
                        model_path TEXT,
                        INDEX idx_model_version (model_version),
                        INDEX idx_accuracy (accuracy)
                    )
                """)

                conn.commit()
            finally:
                conn.close()

    def store_validation(self, run: ValidationRun) -> int:
        """
        Store validation run in database.

        Args:
            run: ValidationRun with all results

        Returns:
            validation_id for correlation
        """
        with self._lock:
            conn = sqlite3.connect(str(self.db_path))
            try:
                # Calculate metrics
                total_rules = len(run.results)
                failed_rules = sum(1 for r in run.results if not r.passed)
                total_time_ms = int(sum(r.execution_time * 1000 for r in run.results))

                # Time to first failure
                time_to_first_failure_ms = None
                cumulative_time = 0.0
                for result in run.results:
                    if not result.passed:
                        time_to_first_failure_ms = int(cumulative_time * 1000)
                        break
                    cumulative_time += result.execution_time

                # Insert validation run
                cursor = conn.execute(
                    """
                    INSERT INTO validations (
                        timestamp, commit_hash, commit_hash_short, changed_files,
                        changed_files_count, author, total_rules, failed_rules,
                        total_time_ms, time_to_first_failure_ms
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        run.timestamp.isoformat(),
                        run.commit_hash,
                        run.commit_hash[:8] if len(run.commit_hash) >= 8 else run.commit_hash,
                        json.dumps(run.changed_files),
                        len(run.changed_files),
                        run.author,
                        total_rules,
                        failed_rules,
                        total_time_ms,
                        time_to_first_failure_ms
                    )
                )
                validation_id = cursor.lastrowid

                # Insert rule results
                for order, result in enumerate(run.results):
                    conn.execute(
                        """
                        INSERT INTO rule_results (
                            validation_id, rule_id, passed, execution_time_ms,
                            severity, failure_message, evidence_json, execution_order
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            validation_id,
                            result.rule_id,
                            result.passed,
                            result.execution_time * 1000,
                            result.severity,
                            result.failure_message,
                            json.dumps(result.evidence) if result.evidence else None,
                            order
                        )
                    )

                # Track file patterns
                for file_path in run.changed_files:
                    file_path_obj = Path(file_path)
                    ext = file_path_obj.suffix.lower()

                    conn.execute(
                        """
                        INSERT INTO file_patterns (
                            validation_id, file_path, file_extension,
                            is_yaml, is_python, is_config
                        ) VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (
                            validation_id,
                            file_path,
                            ext,
                            ext in ['.yaml', '.yml'],
                            ext == '.py',
                            'config' in file_path.lower() or ext in ['.yaml', '.yml', '.json', '.toml']
                        )
                    )

                # Track failure co-occurrence patterns
                failed_rule_ids = [r.rule_id for r in run.results if not r.passed]
                for i, rule_id_1 in enumerate(failed_rule_ids):
                    for rule_id_2 in failed_rule_ids[i+1:]:
                        # Ensure consistent ordering
                        r1, r2 = sorted([rule_id_1, rule_id_2])
                        conn.execute(
                            """
                            INSERT INTO failure_patterns (rule_id_1, rule_id_2, co_occurrence_count, last_seen)
                            VALUES (?, ?, 1, ?)
                            ON CONFLICT(rule_id_1, rule_id_2)
                            DO UPDATE SET
                                co_occurrence_count = co_occurrence_count + 1,
                                last_seen = excluded.last_seen
                            """,
                            (r1, r2, run.timestamp.isoformat())
                        )

                conn.commit()
                return validation_id

            finally:
                conn.close()

    def get_rule_failure_rate(self, rule_id: str, limit: int = 100) -> Tuple[float, float]:
        """
        Get historical failure rate and avg execution time for rule.

        Args:
            rule_id: Rule identifier
            limit: Number of recent results to consider

        Returns:
            (failure_rate, avg_execution_time_ms)
        """
        with self._lock:
            conn = sqlite3.connect(str(self.db_path))
            try:
                cursor = conn.execute(
                    """
                    SELECT passed, execution_time_ms
                    FROM rule_results
                    WHERE rule_id = ?
                    ORDER BY id DESC
                    LIMIT ?
                    """,
                    (rule_id, limit)
                )

                results = cursor.fetchall()
                if not results:
                    return 0.5, 10.0  # Unknown: assume 50% failure rate, 10ms time

                failures = sum(1 for passed, _ in results if not passed)
                failure_rate = failures / len(results)
                avg_time = sum(time_ms for _, time_ms in results) / len(results)

                return failure_rate, avg_time

            finally:
                conn.close()

    def get_file_pattern_failure_correlation(self, file_extensions: List[str], rule_id: str) -> float:
        """
        Get correlation between file pattern and rule failure.

        Args:
            file_extensions: List of file extensions in changed files
            rule_id: Rule to check

        Returns:
            Correlation score (0.0 to 1.0)
        """
        with self._lock:
            conn = sqlite3.connect(str(self.db_path))
            try:
                # Find validations with similar file patterns
                placeholders = ','.join('?' * len(file_extensions))
                cursor = conn.execute(
                    f"""
                    SELECT DISTINCT fp.validation_id
                    FROM file_patterns fp
                    WHERE fp.file_extension IN ({placeholders})
                    LIMIT 100
                    """,
                    file_extensions
                )

                validation_ids = [row[0] for row in cursor.fetchall()]
                if not validation_ids:
                    return 0.5

                # Check how often this rule failed in those validations
                placeholders = ','.join('?' * len(validation_ids))
                cursor = conn.execute(
                    f"""
                    SELECT passed
                    FROM rule_results
                    WHERE validation_id IN ({placeholders}) AND rule_id = ?
                    """,
                    validation_ids + [rule_id]
                )

                results = cursor.fetchall()
                if not results:
                    return 0.5

                failures = sum(1 for (passed,) in results if not passed)
                return failures / len(results)

            finally:
                conn.close()

    def get_co_occurring_failures(self, rule_id: str, limit: int = 10) -> List[Tuple[str, int]]:
        """
        Get rules that frequently fail together with given rule.

        Args:
            rule_id: Rule to check
            limit: Number of co-occurring rules to return

        Returns:
            List of (rule_id, co_occurrence_count) tuples
        """
        with self._lock:
            conn = sqlite3.connect(str(self.db_path))
            try:
                cursor = conn.execute(
                    """
                    SELECT
                        CASE
                            WHEN rule_id_1 = ? THEN rule_id_2
                            ELSE rule_id_1
                        END as other_rule,
                        co_occurrence_count
                    FROM failure_patterns
                    WHERE rule_id_1 = ? OR rule_id_2 = ?
                    ORDER BY co_occurrence_count DESC
                    LIMIT ?
                    """,
                    (rule_id, rule_id, rule_id, limit)
                )

                return cursor.fetchall()

            finally:
                conn.close()

    def get_training_data(self, min_samples: int = 100) -> Optional[Dict]:
        """
        Get historical data for ML training.

        Args:
            min_samples: Minimum number of validation runs required

        Returns:
            Dict with training data or None if insufficient samples
        """
        with self._lock:
            conn = sqlite3.connect(str(self.db_path))
            try:
                # Check if we have enough data
                cursor = conn.execute("SELECT COUNT(*) FROM validations")
                count = cursor.fetchone()[0]

                if count < min_samples:
                    return None

                # Get all validation runs with results
                cursor = conn.execute(
                    """
                    SELECT
                        v.id, v.commit_hash, v.changed_files, v.author,
                        v.timestamp, v.changed_files_count
                    FROM validations v
                    ORDER BY v.timestamp DESC
                    LIMIT 1000
                    """
                )

                validations = []
                for val_id, commit, files_json, author, timestamp, file_count in cursor.fetchall():
                    # Get rule results for this validation
                    rule_cursor = conn.execute(
                        """
                        SELECT rule_id, passed, execution_time_ms, severity
                        FROM rule_results
                        WHERE validation_id = ?
                        """,
                        (val_id,)
                    )

                    rules = []
                    for rule_id, passed, exec_time, severity in rule_cursor.fetchall():
                        rules.append({
                            'rule_id': rule_id,
                            'passed': passed,
                            'execution_time_ms': exec_time,
                            'severity': severity
                        })

                    # Get file patterns
                    file_cursor = conn.execute(
                        """
                        SELECT file_extension, is_yaml, is_python, is_config
                        FROM file_patterns
                        WHERE validation_id = ?
                        """,
                        (val_id,)
                    )

                    file_patterns = []
                    for ext, is_yaml, is_py, is_cfg in file_cursor.fetchall():
                        file_patterns.append({
                            'extension': ext,
                            'is_yaml': bool(is_yaml),
                            'is_python': bool(is_py),
                            'is_config': bool(is_cfg)
                        })

                    validations.append({
                        'validation_id': val_id,
                        'commit_hash': commit,
                        'changed_files': json.loads(files_json),
                        'changed_files_count': file_count,
                        'author': author,
                        'timestamp': timestamp,
                        'rules': rules,
                        'file_patterns': file_patterns
                    })

                return {
                    'validations': validations,
                    'total_samples': count,
                    'samples_returned': len(validations)
                }

            finally:
                conn.close()

    def store_model_metrics(self, model_version: str, metrics: Dict, model_path: str):
        """
        Store ML model performance metrics.

        Args:
            model_version: Model identifier
            metrics: Dict with accuracy, precision, recall, etc.
            model_path: Path to saved model file
        """
        with self._lock:
            conn = sqlite3.connect(str(self.db_path))
            try:
                conn.execute(
                    """
                    INSERT INTO model_metrics (
                        model_version, training_samples, accuracy, precision_score,
                        recall_score, f1_score, false_positive_rate,
                        false_negative_rate, feature_count, model_path
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        model_version,
                        metrics.get('training_samples', 0),
                        metrics.get('accuracy', 0.0),
                        metrics.get('precision', 0.0),
                        metrics.get('recall', 0.0),
                        metrics.get('f1_score', 0.0),
                        metrics.get('false_positive_rate', 0.0),
                        metrics.get('false_negative_rate', 0.0),
                        metrics.get('feature_count', 0),
                        model_path
                    )
                )
                conn.commit()
            finally:
                conn.close()

    def get_stats(self) -> Dict:
        """Get database statistics for monitoring."""
        with self._lock:
            conn = sqlite3.connect(str(self.db_path))
            try:
                stats = {}

                # Total validations
                cursor = conn.execute("SELECT COUNT(*) FROM validations")
                stats['total_validations'] = cursor.fetchone()[0]

                # Total rule executions
                cursor = conn.execute("SELECT COUNT(*) FROM rule_results")
                stats['total_rule_executions'] = cursor.fetchone()[0]

                # Average time to first failure
                cursor = conn.execute(
                    """
                    SELECT AVG(time_to_first_failure_ms)
                    FROM validations
                    WHERE time_to_first_failure_ms IS NOT NULL
                    """
                )
                avg_ttf = cursor.fetchone()[0]
                stats['avg_time_to_first_failure_ms'] = round(avg_ttf, 2) if avg_ttf else None

                # Top failing rules
                cursor = conn.execute(
                    """
                    SELECT rule_id, COUNT(*) as fail_count
                    FROM rule_results
                    WHERE passed = 0
                    GROUP BY rule_id
                    ORDER BY fail_count DESC
                    LIMIT 10
                    """
                )
                stats['top_failing_rules'] = [
                    {'rule_id': rule_id, 'failures': count}
                    for rule_id, count in cursor.fetchall()
                ]

                # Latest model metrics
                cursor = conn.execute(
                    """
                    SELECT model_version, accuracy, false_negative_rate
                    FROM model_metrics
                    ORDER BY id DESC
                    LIMIT 1
                    """
                )
                model_row = cursor.fetchone()
                if model_row:
                    stats['latest_model'] = {
                        'version': model_row[0],
                        'accuracy': model_row[1],
                        'false_negative_rate': model_row[2]
                    }

                return stats

            finally:
                conn.close()
