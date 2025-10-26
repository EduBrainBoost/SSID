"""
Layer 24: Fail-Fast-Mechanismus
===============================

Exit 24 bei Anomalie detection
Version: 3.0.0
"""

from typing import List, Tuple
import sys

class FailFastMechanism:
    """Fail-fast with exit code 24"""

    EXIT_CODE_ANOMALY = 24

    def __init__(self):
        self.anomalies: List[str] = []
        self.enabled = True

    def detect_anomaly(self, condition: bool, message: str):
        """Detect anomaly and fail fast"""
        if condition:
            self.anomalies.append(message)
            if self.enabled:
                print(f"[FAIL-FAST] Anomaly detected: {message}")
                sys.exit(self.EXIT_CODE_ANOMALY)

    def check_rule_count(self, count: int, expected_min: int):
        """Check rule count meets minimum"""
        self.detect_anomaly(
            count < expected_min,
            f"Rule count {count} below minimum {expected_min}"
        )

    def check_hash_mismatch(self, hash1: str, hash2: str):
        """Check for hash mismatch"""
        self.detect_anomaly(
            hash1 != hash2,
            f"Hash mismatch: {hash1[:8]}... != {hash2[:8]}..."
        )

    def self_verify(self) -> Tuple[bool, List[str]]:
        """Self-verification"""
        issues = []
        if self.anomalies:
            issues.extend(self.anomalies)
        return len(issues) == 0, issues
