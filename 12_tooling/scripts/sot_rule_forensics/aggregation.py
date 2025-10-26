"""
Layer 15: Hash-Aggregation
==========================

H_total = SHA512(Σ H_i)
Version: 3.0.0
"""

from typing import List, Tuple
import hashlib

class HashAggregation:
    """Hash aggregation for rule sets"""

    def __init__(self):
        self.individual_hashes: List[str] = []
        self.total_hash: str = ""

    def add_hash(self, hash_sig: str):
        """Add individual hash"""
        self.individual_hashes.append(hash_sig)

    def calculate_total_hash(self) -> str:
        """Calculate total aggregated hash"""
        combined = ''.join(sorted(self.individual_hashes))
        self.total_hash = hashlib.sha512(combined.encode()).hexdigest()
        return self.total_hash

    def self_verify(self) -> Tuple[bool, List[str]]:
        """Self-verification"""
        issues = []
        if not self.total_hash and len(self.individual_hashes) > 0:
            issues.append("Total hash not calculated")
        return len(issues) == 0, issues
