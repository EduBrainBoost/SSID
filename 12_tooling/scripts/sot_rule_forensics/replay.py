"""
Layer 29: Evidence-Replay
=========================

Hash-chain replay and verification
Version: 3.0.0
"""

from typing import List, Tuple, Dict
from dataclasses import dataclass
from datetime import datetime
import hashlib

@dataclass
class ReplayEntry:
    """Replay entry"""
    timestamp: datetime
    rule_id: str
    operation: str
    hash_before: str
    hash_after: str

class EvidenceReplay:
    """Evidence chain replay system"""

    def __init__(self):
        self.replay_log: List[ReplayEntry] = []
        self.chain_valid = True

    def record_operation(self, rule_id: str, operation: str,
                        hash_before: str, hash_after: str):
        """Record an operation for replay"""
        entry = ReplayEntry(
            timestamp=datetime.now(),
            rule_id=rule_id,
            operation=operation,
            hash_before=hash_before,
            hash_after=hash_after
        )
        self.replay_log.append(entry)

    def replay_chain(self) -> bool:
        """Replay and verify the evidence chain"""
        self.chain_valid = True

        for i, entry in enumerate(self.replay_log):
            # Verify hash continuity
            if i > 0:
                prev_entry = self.replay_log[i-1]
                if entry.hash_before != prev_entry.hash_after:
                    self.chain_valid = False
                    return False

        return self.chain_valid

    def get_chain_hash(self) -> str:
        """Calculate hash of entire chain"""
        chain_data = ''.join([
            f"{e.timestamp.isoformat()}{e.rule_id}{e.operation}{e.hash_before}{e.hash_after}"
            for e in self.replay_log
        ])
        return hashlib.sha256(chain_data.encode()).hexdigest()

    def self_verify(self) -> Tuple[bool, List[str]]:
        """Self-verification"""
        issues = []
        if not self.replay_chain():
            issues.append("Evidence chain replay failed")
        return len(issues) == 0, issues
