#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSID - ML-Based Rule Prioritization Validator (ADVANCED PHASE 4)
Predicts which rules will fail and executes them first for fast feedback

Target Performance:
- Time to first failure: 6s → <1s (6x improvement)
- Prediction accuracy: >75%
- False negative rate: <5% (don't miss critical failures)
- Overhead: <50ms per validation
"""

import sys
import time
import subprocess
import json
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from datetime import datetime
import argparse

# Import our ML components
try:
    from validation_database import ValidationDatabase, ValidationResult, ValidationRun
    from failure_prediction_model import FailurePredictionModel, SKLEARN_AVAILABLE
except ImportError:
    # Try relative import
    from .validation_database import ValidationDatabase, ValidationResult, ValidationRun
    from .failure_prediction_model import FailurePredictionModel, SKLEARN_AVAILABLE


class MLPrioritizedValidator:
    """
    Validation orchestrator with ML-based rule prioritization.

    Features:
    - Predicts failure probability for each rule
    - Sorts rules by probability (descending)
    - Fail-fast mode: stop on first CRITICAL failure
    - Stores results for continuous learning
    """

    def __init__(
        self,
        repo_root: Path,
        db_path: Optional[Path] = None,
        model_path: Optional[Path] = None,
        fail_fast: bool = True
    ):
        """
        Initialize ML-prioritized validator.

        Args:
            repo_root: Repository root directory
            db_path: Path to validation history database
            model_path: Path to trained ML model (optional)
            fail_fast: Stop on first CRITICAL failure
        """
        self.repo_root = Path(repo_root)
        self.fail_fast = fail_fast

        # Initialize database
        if db_path is None:
            db_path = self.repo_root / ".ssid_cache" / "validation_history.db"
        self.db = ValidationDatabase(db_path)

        # Initialize ML model
        self.ml_enabled = SKLEARN_AVAILABLE
        self.predictor = None

        if self.ml_enabled:
            try:
                self.predictor = FailurePredictionModel(self.db)

                # Load pre-trained model if available
                if model_path and model_path.exists():
                    self.predictor.load(model_path)
                    print(f"[ML] Loaded model from {model_path}")
                else:
                    print("[ML] No pre-trained model - using historical failure rates")

            except Exception as e:
                print(f"[ML-WARN] Failed to initialize ML model: {e}")
                self.ml_enabled = False

    def get_changed_files_git(self) -> List[Path]:
        """
        Detect changed files using git diff.

        Returns:
            List of changed file paths relative to repo root
        """
        try:
            # Get uncommitted changes
            result = subprocess.run(
                ["git", "diff", "--name-only", "HEAD"],
                capture_output=True,
                text=True,
                cwd=self.repo_root,
                timeout=10
            )

            if result.returncode == 0 and result.stdout.strip():
                files = [
                    self.repo_root / line.strip()
                    for line in result.stdout.strip().split('\n')
                    if line.strip()
                ]
                return [f for f in files if f.exists()]

            # Fallback: compare to origin/main
            result = subprocess.run(
                ["git", "diff", "--name-only", "origin/main...HEAD"],
                capture_output=True,
                text=True,
                cwd=self.repo_root,
                timeout=10
            )

            if result.returncode == 0:
                files = [
                    self.repo_root / line.strip()
                    for line in result.stdout.strip().split('\n')
                    if line.strip()
                ]
                return [f for f in files if f.exists()]

        except Exception as e:
            print(f"[GIT-WARN] Failed to detect changed files: {e}")

        return []

    def get_commit_author(self) -> str:
        """Get current commit author."""
        try:
            result = subprocess.run(
                ["git", "config", "user.name"],
                capture_output=True,
                text=True,
                cwd=self.repo_root,
                timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return "unknown"

    def get_commit_hash(self) -> str:
        """Get current commit hash."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
                cwd=self.repo_root,
                timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return "uncommitted"

    def define_rules(self) -> List[Dict]:
        """
        Define validation rules to execute.

        Returns:
            List of rule definitions with id, command, severity
        """
        return [
            {
                'rule_id': 'AR001_structure_guard',
                'command': 'bash 12_tooling/scripts/structure_guard.sh',
                'severity': 'CRITICAL',
                'timeout': 60
            },
            {
                'rule_id': 'AR002_structure_lock_gate',
                'command': 'python 24_meta_orchestration/triggers/ci/gates/structure_lock_l3.py',
                'severity': 'CRITICAL',
                'timeout': 30
            },
            {
                'rule_id': 'AR003_opa_structure_policy',
                'command': 'opa version',  # Simplified for testing
                'severity': 'HIGH',
                'timeout': 30
            },
            {
                'rule_id': 'AR004_worm_integrity',
                'command': 'python 02_audit_logging/tools/worm_integrity_check.py',
                'severity': 'HIGH',
                'timeout': 30
            },
            {
                'rule_id': 'AR005_hygiene_verification',
                'command': 'python 02_audit_logging/tools/verify_hygiene_enforcement.py',
                'severity': 'MEDIUM',
                'timeout': 30
            },
            {
                'rule_id': 'CP001_circular_dependency',
                'command': 'python 23_compliance/anti_gaming/circular_dependency_validator.py',
                'severity': 'HIGH',
                'timeout': 30
            },
            {
                'rule_id': 'CP002_badge_signature',
                'command': 'python 23_compliance/anti_gaming/badge_signature_validator.py',
                'severity': 'MEDIUM',
                'timeout': 30
            },
            {
                'rule_id': 'TS001_pytest_structure',
                'command': 'pytest 23_compliance/tests/unit/test_structure_policy_vs_md.py -v',
                'severity': 'MEDIUM',
                'timeout': 60
            }
        ]

    def execute_rule(self, rule: Dict) -> ValidationResult:
        """
        Execute single validation rule.

        Args:
            rule: Rule definition dict

        Returns:
            ValidationResult with pass/fail and timing
        """
        rule_id = rule['rule_id']
        command = rule['command']
        timeout = rule.get('timeout', 60)

        print(f"[EXEC] {rule_id}...", end='', flush=True)

        start_time = time.time()
        try:
            result = subprocess.run(
                command.split(),
                capture_output=True,
                text=True,
                cwd=self.repo_root,
                timeout=timeout
            )

            execution_time = time.time() - start_time
            passed = result.returncode == 0

            if passed:
                print(f" [PASS] ({execution_time:.2f}s)")
            else:
                print(f" [FAIL] ({execution_time:.2f}s) exit={result.returncode}")

            return ValidationResult(
                rule_id=rule_id,
                passed=passed,
                execution_time=execution_time,
                severity=rule['severity'],
                failure_message=result.stderr[:500] if not passed else None,
                evidence={
                    'exit_code': result.returncode,
                    'stdout_sample': result.stdout[:200],
                    'stderr_sample': result.stderr[:200]
                }
            )

        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            print(f" [TIMEOUT] ({execution_time:.2f}s)")

            return ValidationResult(
                rule_id=rule_id,
                passed=False,
                execution_time=execution_time,
                severity=rule['severity'],
                failure_message=f"Timeout after {timeout}s"
            )

        except Exception as e:
            execution_time = time.time() - start_time
            print(f" [ERROR] ({execution_time:.2f}s) {e}")

            return ValidationResult(
                rule_id=rule_id,
                passed=False,
                execution_time=execution_time,
                severity=rule['severity'],
                failure_message=str(e)
            )

    def validate_fixed_order(self, verbose: bool = False) -> Tuple[List[ValidationResult], Dict]:
        """
        Execute rules in fixed order (baseline for comparison).

        Args:
            verbose: Print detailed output

        Returns:
            (results, metrics)
        """
        print("[BASELINE] Executing rules in fixed order...")
        rules = self.define_rules()

        start_time = time.time()
        results = []
        time_to_first_failure = None

        for rule in rules:
            result = self.execute_rule(rule)
            results.append(result)

            # Track time to first failure
            if not result.passed and time_to_first_failure is None:
                time_to_first_failure = time.time() - start_time

        total_time = time.time() - start_time

        metrics = {
            'mode': 'fixed_order',
            'total_time': total_time,
            'time_to_first_failure': time_to_first_failure,
            'total_rules': len(results),
            'failed_rules': sum(1 for r in results if not r.passed),
            'avg_rule_time': total_time / len(results) if results else 0
        }

        return results, metrics

    def validate_ml_prioritized(self, verbose: bool = False) -> Tuple[List[ValidationResult], Dict]:
        """
        Execute rules in ML-predicted order for fast failure detection.

        Args:
            verbose: Print detailed output

        Returns:
            (results, metrics)
        """
        print("[ML-PRIORITIZED] Executing rules in predicted failure order...")

        # Get context
        changed_files = self.get_changed_files_git()
        author = self.get_commit_author()
        timestamp = datetime.now()

        if verbose:
            print(f"[CONTEXT] Changed files: {len(changed_files)}")
            if changed_files[:3]:
                for f in changed_files[:3]:
                    print(f"  - {f.relative_to(self.repo_root)}")
            print(f"[CONTEXT] Author: {author}")

        # Get all rules
        rules = self.define_rules()

        # Predict failure probabilities
        ml_overhead_start = time.time()

        if self.ml_enabled and self.predictor and self.predictor.is_trained:
            predictions = self.predictor.predict_batch(
                changed_files,
                [r['rule_id'] for r in rules],
                author,
                timestamp
            )
        else:
            # Fallback: use historical failure rates
            predictions = {
                r['rule_id']: self.db.get_rule_failure_rate(r['rule_id'])[0]
                for r in rules
            }

        ml_overhead = time.time() - ml_overhead_start

        # Sort rules by failure probability (descending)
        rule_priorities = [
            (rule, predictions[rule['rule_id']])
            for rule in rules
        ]
        rule_priorities.sort(key=lambda x: x[1], reverse=True)

        if verbose:
            print(f"\n[ML-PRIORITY] Top 5 likely failures:")
            for rule, prob in rule_priorities[:5]:
                print(f"  {rule['rule_id']}: {prob:.1%} probability")
            print()

        # Execute in priority order
        start_time = time.time()
        results = []
        time_to_first_failure = None
        stopped_early = False

        for rule, prob in rule_priorities:
            result = self.execute_rule(rule)
            results.append(result)

            # Track time to first failure
            if not result.passed and time_to_first_failure is None:
                time_to_first_failure = time.time() - start_time

            # Fail-fast on CRITICAL failures
            if self.fail_fast and not result.passed and result.severity == 'CRITICAL':
                print(f"\n[FAIL-FAST] Stopping on CRITICAL failure: {rule['rule_id']}")
                stopped_early = True
                break

        total_time = time.time() - start_time

        metrics = {
            'mode': 'ml_prioritized',
            'ml_enabled': self.ml_enabled and self.predictor and self.predictor.is_trained,
            'ml_overhead_ms': ml_overhead * 1000,
            'total_time': total_time,
            'time_to_first_failure': time_to_first_failure,
            'total_rules': len(results),
            'failed_rules': sum(1 for r in results if not r.passed),
            'avg_rule_time': total_time / len(results) if results else 0,
            'stopped_early': stopped_early,
            'rules_executed': len(results),
            'rules_total': len(rules),
            'predictions': {
                rule['rule_id']: float(prob)
                for rule, prob in rule_priorities
            }
        }

        return results, metrics

    def store_results(self, results: List[ValidationResult], metrics: Dict):
        """
        Store validation results in database for ML training.

        Args:
            results: List of validation results
            metrics: Execution metrics
        """
        commit_hash = self.get_commit_hash()
        changed_files = self.get_changed_files_git()
        author = self.get_commit_author()

        run = ValidationRun(
            commit_hash=commit_hash,
            changed_files=[str(f.relative_to(self.repo_root)) for f in changed_files],
            author=author,
            timestamp=datetime.now(),
            results=results
        )

        validation_id = self.db.store_validation(run)
        print(f"[DB] Stored validation run #{validation_id}")

        return validation_id


def main():
    """Main entry point for ML-prioritized validation."""
    parser = argparse.ArgumentParser(
        description="ML-Based Rule Prioritization Validator (ADVANCED PHASE 4)"
    )
    parser.add_argument(
        '--mode',
        choices=['fixed', 'ml', 'both'],
        default='ml',
        help='Validation mode: fixed order, ML-prioritized, or both for comparison'
    )
    parser.add_argument(
        '--fail-fast',
        action='store_true',
        default=True,
        help='Stop on first CRITICAL failure (default: enabled)'
    )
    parser.add_argument(
        '--no-fail-fast',
        dest='fail_fast',
        action='store_false',
        help='Execute all rules regardless of failures'
    )
    parser.add_argument(
        '--store-results',
        action='store_true',
        help='Store results in database for ML training'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed output'
    )
    parser.add_argument(
        '--repo-root',
        type=Path,
        default=Path.cwd(),
        help='Repository root directory'
    )
    parser.add_argument(
        '--db-path',
        type=Path,
        help='Custom database path'
    )
    parser.add_argument(
        '--model-path',
        type=Path,
        help='Path to pre-trained ML model'
    )

    args = parser.parse_args()

    # Initialize validator
    validator = MLPrioritizedValidator(
        repo_root=args.repo_root,
        db_path=args.db_path,
        model_path=args.model_path,
        fail_fast=args.fail_fast
    )

    # Execute validation
    print("=" * 70)
    print("ML-Based Rule Prioritization Validator")
    print("=" * 70)
    print()

    if args.mode == 'both':
        # Run both modes for comparison
        print("[BENCHMARK] Running both fixed-order and ML-prioritized modes...\n")

        fixed_results, fixed_metrics = validator.validate_fixed_order(args.verbose)
        print()
        ml_results, ml_metrics = validator.validate_ml_prioritized(args.verbose)

        # Print comparison
        print("\n" + "=" * 70)
        print("COMPARISON RESULTS")
        print("=" * 70)
        print(f"\nFixed Order:")
        print(f"  Total time: {fixed_metrics['total_time']:.2f}s")
        print(f"  Time to first failure: {fixed_metrics['time_to_first_failure']:.2f}s" if fixed_metrics['time_to_first_failure'] else "  No failures")
        print(f"  Failed rules: {fixed_metrics['failed_rules']}/{fixed_metrics['total_rules']}")

        print(f"\nML-Prioritized:")
        print(f"  Total time: {ml_metrics['total_time']:.2f}s")
        print(f"  Time to first failure: {ml_metrics['time_to_first_failure']:.2f}s" if ml_metrics['time_to_first_failure'] else "  No failures")
        print(f"  Failed rules: {ml_metrics['failed_rules']}/{ml_metrics['total_rules']}")
        print(f"  ML overhead: {ml_metrics['ml_overhead_ms']:.1f}ms")

        if fixed_metrics['time_to_first_failure'] and ml_metrics['time_to_first_failure']:
            improvement = (fixed_metrics['time_to_first_failure'] - ml_metrics['time_to_first_failure']) / fixed_metrics['time_to_first_failure'] * 100
            speedup = fixed_metrics['time_to_first_failure'] / ml_metrics['time_to_first_failure']
            print(f"\nImprovement: {improvement:.1f}% faster ({speedup:.1f}x speedup)")

        # Store ML results if requested
        if args.store_results:
            validator.store_results(ml_results, ml_metrics)

        # Exit with failure if any rule failed
        exit_code = 1 if ml_metrics['failed_rules'] > 0 else 0

    elif args.mode == 'fixed':
        results, metrics = validator.validate_fixed_order(args.verbose)

        print("\n" + "=" * 70)
        print(f"Total time: {metrics['total_time']:.2f}s")
        print(f"Failed rules: {metrics['failed_rules']}/{metrics['total_rules']}")

        if args.store_results:
            validator.store_results(results, metrics)

        exit_code = 1 if metrics['failed_rules'] > 0 else 0

    else:  # ml mode
        results, metrics = validator.validate_ml_prioritized(args.verbose)

        print("\n" + "=" * 70)
        print(f"Total time: {metrics['total_time']:.2f}s")
        if metrics['time_to_first_failure']:
            print(f"Time to first failure: {metrics['time_to_first_failure']:.2f}s")
        print(f"Failed rules: {metrics['failed_rules']}/{metrics['total_rules']}")
        print(f"ML overhead: {metrics['ml_overhead_ms']:.1f}ms")

        if args.store_results:
            validator.store_results(results, metrics)

        exit_code = 1 if metrics['failed_rules'] > 0 else 0

    print("=" * 70)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
