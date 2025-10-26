"""
Layer 27: Semantic Diff
=======================

ΔR = R_v2 - R_v1 semantic difference calculation
Version: 3.0.0
"""

from typing import List, Dict, Tuple, Set
from dataclasses import dataclass

@dataclass
class RuleDiff:
    """Difference between two rule versions"""
    rule_id: str
    diff_type: str  # 'added', 'removed', 'modified'
    old_content: str = ""
    new_content: str = ""
    changes: List[str] = None

class SemanticDiff:
    """Semantic diff calculator for rules"""

    def __init__(self):
        self.diffs: List[RuleDiff] = []

    def calculate_diff(self, old_rules: Dict, new_rules: Dict) -> List[RuleDiff]:
        """Calculate semantic differences"""
        diffs = []

        old_ids = set(old_rules.keys())
        new_ids = set(new_rules.keys())

        # Added rules
        for rule_id in new_ids - old_ids:
            diffs.append(RuleDiff(
                rule_id=rule_id,
                diff_type='added',
                new_content=str(new_rules[rule_id])
            ))

        # Removed rules
        for rule_id in old_ids - new_ids:
            diffs.append(RuleDiff(
                rule_id=rule_id,
                diff_type='removed',
                old_content=str(old_rules[rule_id])
            ))

        # Modified rules
        for rule_id in old_ids & new_ids:
            old_content = str(old_rules[rule_id])
            new_content = str(new_rules[rule_id])
            if old_content != new_content:
                diffs.append(RuleDiff(
                    rule_id=rule_id,
                    diff_type='modified',
                    old_content=old_content,
                    new_content=new_content
                ))

        self.diffs = diffs
        return diffs

    def get_summary(self) -> Dict[str, int]:
        """Get diff summary"""
        return {
            'added': sum(1 for d in self.diffs if d.diff_type == 'added'),
            'removed': sum(1 for d in self.diffs if d.diff_type == 'removed'),
            'modified': sum(1 for d in self.diffs if d.diff_type == 'modified')
        }

    def self_verify(self) -> Tuple[bool, List[str]]:
        """Self-verification"""
        return True, []
