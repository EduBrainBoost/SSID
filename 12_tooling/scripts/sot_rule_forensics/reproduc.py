"""
Layer 25: Reproducibility-Test
==============================

Byte-identical output verification
Version: 3.0.0
"""

from typing import List, Tuple
import hashlib
import json

class ReproducibilityTest:
    """Test for byte-identical reproducibility"""

    def __init__(self):
        self.run_hashes: List[str] = []

    def calculate_output_hash(self, data: dict) -> str:
        """Calculate hash of output data"""
        # Sort keys for deterministic output
        json_str = json.dumps(data, sort_keys=True, indent=2)
        return hashlib.sha256(json_str.encode()).hexdigest()

    def record_run(self, data: dict):
        """Record a run's output hash"""
        output_hash = self.calculate_output_hash(data)
        self.run_hashes.append(output_hash)

    def verify_reproducibility(self) -> bool:
        """Verify all runs produce identical output"""
        if len(self.run_hashes) < 2:
            return True

        first_hash = self.run_hashes[0]
        return all(h == first_hash for h in self.run_hashes)

    def self_verify(self) -> Tuple[bool, List[str]]:
        """Self-verification"""
        issues = []
        if not self.verify_reproducibility():
            issues.append("Reproducibility check failed")
        return len(issues) == 0, issues
