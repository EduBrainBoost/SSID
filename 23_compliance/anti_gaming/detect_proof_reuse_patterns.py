#!/usr/bin/env python3
"""
detect_proof_reuse_patterns.py

Anti-Gaming Tool: Detect suspicious proof credential reuse patterns
Analyzes proof submissions for gaming indicators:
- Same proof used by multiple identities (credential sharing)
- Proof reused more frequently than legitimate use cases allow
- Batch submission patterns indicating automated gaming
- Time-window violations (same proof submitted too frequently)

MUST-002-ANTI-GAMING compliance requirement
Part of fraud detection pipeline
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Set, Tuple
from collections import defaultdict
import hashlib


class ProofReuseDetector:
    """Detects suspicious patterns in proof credential usage."""

    def __init__(self, audit_log_dir: str = "02_audit_logging/logs"):
        """
        Initialize detector with audit log directory.

        Args:
            audit_log_dir: Path to directory containing audit logs with proof submissions
        """
        self.audit_log_dir = Path(audit_log_dir)
        self.violations: List[Dict[str, Any]] = []

        # Detection thresholds (configurable per use case)
        self.max_reuse_count = 3  # Max times same proof can be used by different identities
        self.max_reuse_window_days = 7  # Max days between legitimate reuses
        self.suspicious_batch_size = 10  # Consecutive submissions with same proof
        self.min_submission_interval_hours = 1  # Min hours between legitimate reuses

    def analyze_proof_submissions(self) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Analyze all proof submissions for suspicious reuse patterns.

        Returns:
            Tuple of (violations_found, violations_list)
        """
        if not self.audit_log_dir.exists():
            return False, []

        # Load all proof submission events
        proof_submissions = self._load_proof_submissions()

        if not proof_submissions:
            return False, []

        # Group submissions by proof hash
        submissions_by_proof = defaultdict(list)
        for submission in proof_submissions:
            proof_hash = submission.get("proof_hash") or submission.get("credential_hash")
            if proof_hash:
                submissions_by_proof[proof_hash].append(submission)

        # Analyze each proof for suspicious patterns
        for proof_hash, submissions in submissions_by_proof.items():
            self._check_multi_identity_reuse(proof_hash, submissions)
            self._check_excessive_reuse_frequency(proof_hash, submissions)
            self._check_batch_submission_pattern(proof_hash, submissions)
            self._check_time_window_violations(proof_hash, submissions)

        return len(self.violations) > 0, self.violations

    def _load_proof_submissions(self) -> List[Dict[str, Any]]:
        """Load all proof submission events from audit logs."""
        submissions = []

        # Find all audit log files
        log_files = list(self.audit_log_dir.glob("**/*.json"))
        if not log_files:
            log_files = list(self.audit_log_dir.glob("**/*.jsonl"))

        for log_file in log_files:
            events = self._load_log_file(log_file)
            for event in events:
                # Filter for proof submission events
                event_type = event.get("event") or event.get("action") or event.get("type")
                if event_type in ["proof_submit", "credential_submit", "verification_submit", "kyc_proof"]:
                    submissions.append(event)

        return submissions

    def _load_log_file(self, log_file: Path) -> List[Dict[str, Any]]:
        """Load events from a log file (JSON or JSONL format)."""
        events = []
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content:
                    return []

                # Try JSON array first
                try:
                    data = json.loads(content)
                    if isinstance(data, list):
                        events = data
                    elif isinstance(data, dict):
                        events = [data]
                except json.JSONDecodeError:
                    # Try JSONL format
                    for line in content.split('\n'):
                        if line.strip():
                            try:
                                events.append(json.loads(line))
                            except json.JSONDecodeError:
                                continue
        except Exception:
            raise NotImplementedError("TODO: Implement this block")

        return events

    def _parse_timestamp(self, timestamp_str: str) -> datetime:
        """Parse ISO 8601 timestamp string, always returning timezone-naive datetime."""
        if not timestamp_str:
            return datetime.min

        try:
            if 'T' in timestamp_str:
                # Remove timezone info
                timestamp_str = timestamp_str.replace('Z', '').split('+')[0].split('-00:00')[0]
                try:
                    return datetime.fromisoformat(timestamp_str)
                except:
                    raise NotImplementedError("TODO: Implement this block")

            try:
                dt = datetime.fromisoformat(timestamp_str)
                if dt.tzinfo is not None:
                    dt = dt.replace(tzinfo=None)
                return dt
            except:
                return datetime.min
        except:
            return datetime.min

    def _check_multi_identity_reuse(self, proof_hash: str, submissions: List[Dict[str, Any]]) -> None:
        """Detect same proof used by multiple different identities."""
        identity_ids: Set[str] = set()

        for submission in submissions:
            identity_id = (
                submission.get("identity_id") or
                submission.get("user_id") or
                submission.get("entity_id")
            )
            if identity_id:
                identity_ids.add(identity_id)

        if len(identity_ids) > self.max_reuse_count:
            self.violations.append({
                "proof_hash": proof_hash,
                "violation_type": "multi_identity_reuse",
                "severity": "CRITICAL",
                "description": f"Proof credential used by {len(identity_ids)} different identities (threshold: {self.max_reuse_count})",
                "evidence": {
                    "unique_identities": len(identity_ids),
                    "threshold": self.max_reuse_count,
                    "submission_count": len(submissions)
                },
                "timestamp": datetime.utcnow().isoformat() + "Z"
            })

    def _check_excessive_reuse_frequency(self, proof_hash: str, submissions: List[Dict[str, Any]]) -> None:
        """Detect proof reused more frequently than expected for legitimate use."""
        if len(submissions) < 5:  # Need reasonable sample size
            return

        # Sort by timestamp
        sorted_submissions = sorted(
            submissions,
            key=lambda s: self._parse_timestamp(s.get("timestamp", ""))
        )

        # Calculate time span
        first_ts = self._parse_timestamp(sorted_submissions[0].get("timestamp", ""))
        last_ts = self._parse_timestamp(sorted_submissions[-1].get("timestamp", ""))

        if first_ts == datetime.min or last_ts == datetime.min:
            return

        time_span_days = (last_ts - first_ts).days + 1
        if time_span_days == 0:
            time_span_days = 1

        reuse_frequency = len(submissions) / time_span_days

        # Legitimate proofs (e.g., passport) shouldn't be submitted more than once per week on average
        if reuse_frequency > 1.0:  # More than 1 submission per day on average
            self.violations.append({
                "proof_hash": proof_hash,
                "violation_type": "excessive_reuse_frequency",
                "severity": "HIGH",
                "description": f"Proof submitted {len(submissions)} times in {time_span_days} days (avg {reuse_frequency:.2f}/day)",
                "evidence": {
                    "total_submissions": len(submissions),
                    "time_span_days": time_span_days,
                    "avg_submissions_per_day": round(reuse_frequency, 2),
                    "first_submission": first_ts.isoformat(),
                    "last_submission": last_ts.isoformat()
                },
                "timestamp": datetime.utcnow().isoformat() + "Z"
            })

    def _check_batch_submission_pattern(self, proof_hash: str, submissions: List[Dict[str, Any]]) -> None:
        """Detect batch submission patterns indicating automation."""
        if len(submissions) < self.suspicious_batch_size:
            return

        # Sort by timestamp
        sorted_submissions = sorted(
            submissions,
            key=lambda s: self._parse_timestamp(s.get("timestamp", ""))
        )

        # Check for rapid consecutive submissions
        rapid_batches = []
        current_batch = []

        for i, submission in enumerate(sorted_submissions):
            if i == 0:
                current_batch.append(submission)
                continue

            prev_ts = self._parse_timestamp(sorted_submissions[i-1].get("timestamp", ""))
            curr_ts = self._parse_timestamp(submission.get("timestamp", ""))

            if prev_ts == datetime.min or curr_ts == datetime.min:
                continue

            interval_seconds = (curr_ts - prev_ts).total_seconds()

            # If submitted within 60 seconds of previous, it's part of a batch
            if interval_seconds <= 60:
                current_batch.append(submission)
            else:
                # Batch ended
                if len(current_batch) >= self.suspicious_batch_size:
                    rapid_batches.append(current_batch)
                current_batch = [submission]

        # Check last batch
        if len(current_batch) >= self.suspicious_batch_size:
            rapid_batches.append(current_batch)

        if rapid_batches:
            self.violations.append({
                "proof_hash": proof_hash,
                "violation_type": "batch_submission_pattern",
                "severity": "HIGH",
                "description": f"Detected {len(rapid_batches)} batch submission patterns (automated gaming indicator)",
                "evidence": {
                    "batch_count": len(rapid_batches),
                    "largest_batch_size": max(len(batch) for batch in rapid_batches),
                    "total_submissions": len(submissions)
                },
                "timestamp": datetime.utcnow().isoformat() + "Z"
            })

    def _check_time_window_violations(self, proof_hash: str, submissions: List[Dict[str, Any]]) -> None:
        """Detect submissions too close together for legitimate use."""
        # Sort by timestamp
        sorted_submissions = sorted(
            submissions,
            key=lambda s: self._parse_timestamp(s.get("timestamp", ""))
        )

        violations_count = 0

        for i in range(1, len(sorted_submissions)):
            prev_ts = self._parse_timestamp(sorted_submissions[i-1].get("timestamp", ""))
            curr_ts = self._parse_timestamp(sorted_submissions[i].get("timestamp", ""))

            if prev_ts == datetime.min or curr_ts == datetime.min:
                continue

            interval_hours = (curr_ts - prev_ts).total_seconds() / 3600

            # Legitimate proof reuse (e.g., passport verification) shouldn't happen within 1 hour
            if interval_hours < self.min_submission_interval_hours:
                violations_count += 1

        if violations_count > 0:
            self.violations.append({
                "proof_hash": proof_hash,
                "violation_type": "time_window_violation",
                "severity": "MEDIUM",
                "description": f"Proof submitted {violations_count} times within {self.min_submission_interval_hours}h window",
                "evidence": {
                    "violation_count": violations_count,
                    "min_interval_hours": self.min_submission_interval_hours,
                    "total_submissions": len(submissions)
                },
                "timestamp": datetime.utcnow().isoformat() + "Z"
            })

    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive fraud detection report."""
        violations_by_severity = defaultdict(list)
        violations_by_type = defaultdict(int)

        for v in self.violations:
            violations_by_severity[v["severity"]].append(v)
            violations_by_type[v["violation_type"]] += 1

        return {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "tool": "detect_proof_reuse_patterns",
            "version": "1.0.0",
            "status": "FAIL" if self.violations else "PASS",
            "summary": {
                "total_violations": len(self.violations),
                "by_severity": {
                    "CRITICAL": len(violations_by_severity["CRITICAL"]),
                    "HIGH": len(violations_by_severity["HIGH"]),
                    "MEDIUM": len(violations_by_severity["MEDIUM"]),
                    "LOW": len(violations_by_severity["LOW"])
                },
                "by_type": dict(violations_by_type)
            },
            "violations": self.violations,
            "thresholds": {
                "max_reuse_count": self.max_reuse_count,
                "max_reuse_window_days": self.max_reuse_window_days,
                "suspicious_batch_size": self.suspicious_batch_size,
                "min_submission_interval_hours": self.min_submission_interval_hours
            }
        }


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Detect suspicious proof credential reuse patterns (fraud detection)"
    )
    parser.add_argument(
        "--audit-dir",
        default="02_audit_logging/logs",
        help="Directory containing audit logs"
    )
    parser.add_argument(
        "--output",
        help="Output file for violations report (default: stdout)"
    )
    parser.add_argument(
        "--save-violations",
        action="store_true",
        help="Save violations to 23_compliance/anti_gaming/violations/"
    )

    args = parser.parse_args()

    detector = ProofReuseDetector(audit_log_dir=args.audit_dir)
    violations_found, violations = detector.analyze_proof_submissions()

    report = detector.generate_report()

    # Save violations if requested
    if args.save_violations and violations_found:
        violations_dir = Path("23_compliance/anti_gaming/violations")
        violations_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        violations_file = violations_dir / f"proof_reuse_violations_{timestamp}.json"

        with open(violations_file, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"Violations saved to: {violations_file}", file=sys.stderr)

    # Output report
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"Report written to {args.output}")
    else:
        print(json.dumps(report, indent=2))

    # Exit with appropriate code
    sys.exit(1 if violations_found else 0)


if __name__ == "__main__":
    main()
