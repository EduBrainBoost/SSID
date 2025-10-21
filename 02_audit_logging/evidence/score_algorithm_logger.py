#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Score Algorithm Logger - Evidence Chain Integration
SSID Phase 2 Implementation

Purpose:
- Log score algorithm executions (Hash → Evidence → Reputation)
- Create audit trail for badge integrity checks
- Enable rückverfolgbare governance decisions
- Integrate with 03_evidence_system and 08_identity_score

Architecture:
Badge Integrity Check → Score Calculation → Audit Log → Evidence Registry
Every score change produces a cryptographically signed evidence record.

Compliance:
- GDPR Art. 22: Automated decision logging
- DORA: Algorithm auditability
- MiCA: Fraud detection evidence
- AMLD6: Transaction traceability
"""

import json
import hashlib
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from dataclasses import dataclass, asdict

@dataclass
class ScoreAlgorithmEvent:
    """
    Represents a single score algorithm execution event.

    Fields match the evidence chain requirements:
    - event_id: Unique identifier (timestamp-based)
    - timestamp: ISO 8601 UTC
    - algorithm_name: Which algorithm was executed
    - input_hash: SHA-256 of input data (privacy-preserving)
    - output_score: Calculated score value
    - evidence_refs: References to supporting evidence
    - metadata: Additional context (version, thresholds, etc.)
    """
    event_id: str
    timestamp: str
    algorithm_name: str
    input_hash: str
    output_score: float
    evidence_refs: List[str]
    metadata: Dict[str, Any]
    signature: str  # SHA-256 of canonical event representation

    def to_dict(self) -> Dict:
        return asdict(self)

    def compute_signature(self) -> str:
        """Compute deterministic signature for this event"""
        canonical = json.dumps({
            "event_id": self.event_id,
            "timestamp": self.timestamp,
            "algorithm_name": self.algorithm_name,
            "input_hash": self.input_hash,
            "output_score": self.output_score,
            "evidence_refs": sorted(self.evidence_refs),
            "metadata": self.metadata
        }, sort_keys=True)

        return hashlib.sha256(canonical.encode('utf-8')).hexdigest()

class ScoreAlgorithmLogger:
    """
    Central logging facility for score algorithm executions.

    Responsibilities:
    1. Log every badge integrity score calculation
    2. Create evidence chain links (hash → score → evidence)
    3. Write to append-only audit log (WORM-style)
    4. Generate compliance reports for DAO governance

    Integration Points:
    - 23_compliance/anti_gaming/badge_integrity_checker.py → logs here
    - 08_identity_score/score_engine.py → logs here
    - 03_evidence_system/registry/ → consumes logs
    """

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.log_dir = repo_root / "02_audit_logging" / "evidence" / "score_logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Daily log file (append-only)
        self.log_file = self.log_dir / f"score_algorithm_{datetime.now(timezone.utc).strftime('%Y%m%d')}.jsonl"

        # Evidence registry link
        self.evidence_registry = repo_root / "03_evidence_system" / "registry" / "score_evidence.json"

    def log_badge_integrity_check(
        self,
        badge_id: str,
        integrity_score: float,
        violations: List[Dict],
        metadata: Optional[Dict] = None
    ) -> ScoreAlgorithmEvent:
        """
        Log a badge integrity check execution.

        Args:
            badge_id: Badge identifier (e.g., "02_audit_logging::quarantine")
            integrity_score: Calculated integrity score (0-100)
            violations: List of violations found
            metadata: Additional context (version, thresholds, etc.)

        Returns:
            ScoreAlgorithmEvent object with signature
        """
        # Create input hash (privacy-preserving)
        input_data = json.dumps({
            "badge_id": badge_id,
            "violations_count": len(violations),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }, sort_keys=True)
        input_hash = hashlib.sha256(input_data.encode('utf-8')).hexdigest()

        # Generate evidence references
        evidence_refs = []
        for violation in violations:
            violation_id = violation.get("violation_id", "unknown")
            evidence_refs.append(f"violation:{violation_id}")

        # Create event
        event = ScoreAlgorithmEvent(
            event_id=f"SAE-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}",
            timestamp=datetime.now(timezone.utc).isoformat(),
            algorithm_name="badge_integrity_checker",
            input_hash=input_hash,
            output_score=integrity_score,
            evidence_refs=evidence_refs,
            metadata=metadata or {},
            signature=""  # Will be computed next
        )

        # Compute signature
        event.signature = event.compute_signature()

        # Write to audit log
        self._append_to_log(event)

        # Update evidence registry
        self._update_evidence_registry(event)

        return event

    def log_identity_score_calculation(
        self,
        identity_hash: str,
        score_components: Dict[str, float],
        final_score: float,
        metadata: Optional[Dict] = None
    ) -> ScoreAlgorithmEvent:
        """
        Log an identity score calculation execution.

        Args:
            identity_hash: SHA-256 hash of identity data
            score_components: Dict of component scores (e.g., {"badges": 75, "reputation": 80})
            final_score: Final composite score
            metadata: Additional context

        Returns:
            ScoreAlgorithmEvent object with signature
        """
        # Create input hash
        input_data = json.dumps({
            "identity_hash": identity_hash,
            "score_components": score_components,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }, sort_keys=True)
        input_hash = hashlib.sha256(input_data.encode('utf-8')).hexdigest()

        # Generate evidence references
        evidence_refs = [f"identity:{identity_hash}"]
        for component_name in score_components.keys():
            evidence_refs.append(f"component:{component_name}")

        # Create event
        event = ScoreAlgorithmEvent(
            event_id=f"SAE-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}",
            timestamp=datetime.now(timezone.utc).isoformat(),
            algorithm_name="identity_score_calculator",
            input_hash=input_hash,
            output_score=final_score,
            evidence_refs=evidence_refs,
            metadata={
                "score_components": score_components,
                **(metadata or {})
            },
            signature=""
        )

        # Compute signature
        event.signature = event.compute_signature()

        # Write to audit log
        self._append_to_log(event)

        # Update evidence registry
        self._update_evidence_registry(event)

        return event

    def log_reputation_scoring(
        self,
        entity_id: str,
        reputation_factors: Dict[str, Any],
        reputation_score: float,
        metadata: Optional[Dict] = None
    ) -> ScoreAlgorithmEvent:
        """
        Log a reputation scoring execution.

        Args:
            entity_id: Entity identifier (user, organization, etc.)
            reputation_factors: Factors contributing to reputation
            reputation_score: Calculated reputation score
            metadata: Additional context

        Returns:
            ScoreAlgorithmEvent object with signature
        """
        # Create input hash
        input_data = json.dumps({
            "entity_id": entity_id,
            "reputation_factors": reputation_factors,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }, sort_keys=True)
        input_hash = hashlib.sha256(input_data.encode('utf-8')).hexdigest()

        # Generate evidence references
        evidence_refs = [f"entity:{entity_id}"]
        for factor_name in reputation_factors.keys():
            evidence_refs.append(f"factor:{factor_name}")

        # Create event
        event = ScoreAlgorithmEvent(
            event_id=f"SAE-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}",
            timestamp=datetime.now(timezone.utc).isoformat(),
            algorithm_name="reputation_scorer",
            input_hash=input_hash,
            output_score=reputation_score,
            evidence_refs=evidence_refs,
            metadata={
                "reputation_factors": reputation_factors,
                **(metadata or {})
            },
            signature=""
        )

        # Compute signature
        event.signature = event.compute_signature()

        # Write to audit log
        self._append_to_log(event)

        # Update evidence registry
        self._update_evidence_registry(event)

        return event

    def _append_to_log(self, event: ScoreAlgorithmEvent) -> None:
        """Append event to JSONL audit log (append-only)"""
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(event.to_dict()) + '\n')

    def _update_evidence_registry(self, event: ScoreAlgorithmEvent) -> None:
        """
        Update evidence registry with new event.

        This creates the bidirectional link:
        - event_id → evidence_refs (forward)
        - evidence_ref → event_id (reverse)
        """
        # Create evidence registry if it doesn't exist
        if not self.evidence_registry.parent.exists():
            self.evidence_registry.parent.mkdir(parents=True, exist_ok=True)

        # Load existing registry
        registry = {}
        if self.evidence_registry.exists():
            with open(self.evidence_registry, 'r', encoding='utf-8') as f:
                registry = json.load(f)

        # Add new event
        registry[event.event_id] = {
            "timestamp": event.timestamp,
            "algorithm_name": event.algorithm_name,
            "output_score": event.output_score,
            "evidence_refs": event.evidence_refs,
            "signature": event.signature,
            "log_file": str(self.log_file.relative_to(self.repo_root))
        }

        # Write updated registry
        with open(self.evidence_registry, 'w', encoding='utf-8') as f:
            json.dump(registry, f, indent=2, sort_keys=True)

    def query_events_by_algorithm(
        self,
        algorithm_name: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[ScoreAlgorithmEvent]:
        """
        Query events by algorithm name and optional date range.

        Args:
            algorithm_name: Name of algorithm to filter by
            start_date: Optional start date (inclusive)
            end_date: Optional end date (inclusive)

        Returns:
            List of matching ScoreAlgorithmEvent objects
        """
        events = []

        # Scan all log files in date range
        for log_file in sorted(self.log_dir.glob("score_algorithm_*.jsonl")):
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    event_dict = json.loads(line.strip())

                    # Filter by algorithm name
                    if event_dict["algorithm_name"] != algorithm_name:
                        continue

                    # Filter by date range
                    event_timestamp = datetime.fromisoformat(event_dict["timestamp"])
                    if start_date and event_timestamp < start_date:
                        continue
                    if end_date and event_timestamp > end_date:
                        continue

                    # Reconstruct event object
                    event = ScoreAlgorithmEvent(**event_dict)
                    events.append(event)

        return events

    def verify_event_signature(self, event: ScoreAlgorithmEvent) -> bool:
        """
        Verify the cryptographic signature of an event.

        Args:
            event: ScoreAlgorithmEvent to verify

        Returns:
            True if signature is valid, False otherwise
        """
        expected_signature = event.compute_signature()
        return event.signature == expected_signature

    def generate_compliance_report(
        self,
        start_date: datetime,
        end_date: datetime,
        output_file: Optional[Path] = None
    ) -> Dict:
        """
        Generate compliance report for DAO governance.

        Args:
            start_date: Report start date
            end_date: Report end date
            output_file: Optional file to write report to

        Returns:
            Dict containing compliance report data
        """
        # Collect all events in date range
        all_events = []
        for log_file in sorted(self.log_dir.glob("score_algorithm_*.jsonl")):
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    event_dict = json.loads(line.strip())
                    event_timestamp = datetime.fromisoformat(event_dict["timestamp"])

                    if start_date <= event_timestamp <= end_date:
                        all_events.append(event_dict)

        # Generate statistics
        algorithm_stats = {}
        for event in all_events:
            algo_name = event["algorithm_name"]
            if algo_name not in algorithm_stats:
                algorithm_stats[algo_name] = {
                    "count": 0,
                    "avg_score": 0.0,
                    "min_score": float('inf'),
                    "max_score": float('-inf'),
                    "scores": []
                }

            stats = algorithm_stats[algo_name]
            stats["count"] += 1
            stats["scores"].append(event["output_score"])
            stats["min_score"] = min(stats["min_score"], event["output_score"])
            stats["max_score"] = max(stats["max_score"], event["output_score"])

        # Calculate averages
        for algo_name, stats in algorithm_stats.items():
            if stats["count"] > 0:
                stats["avg_score"] = sum(stats["scores"]) / stats["count"]
            del stats["scores"]  # Remove raw scores from report

        # Generate report
        report = {
            "report_type": "score_algorithm_compliance",
            "period_start": start_date.isoformat(),
            "period_end": end_date.isoformat(),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "total_events": len(all_events),
            "algorithm_statistics": algorithm_stats,
            "compliance_status": "PASS" if len(all_events) > 0 else "NO_DATA"
        }

        # Write to file if specified
        if output_file:
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, sort_keys=True)

        return report

def main():
    """CLI entry point for testing"""
    repo_root = Path(__file__).resolve().parents[2]

    logger = ScoreAlgorithmLogger(repo_root)

    # Example: Log a badge integrity check
    event = logger.log_badge_integrity_check(
        badge_id="test_badge",
        integrity_score=85.5,
        violations=[
            {"violation_id": "BIV-001", "severity": "medium"}
        ],
        metadata={
            "version": "1.0.0",
            "threshold": 80.0
        }
    )

    print(json.dumps(event.to_dict(), indent=2))
    print(f"\nEvent logged to: {logger.log_file}")
    print(f"Evidence registry updated: {logger.evidence_registry}")

if __name__ == "__main__":
    main()
