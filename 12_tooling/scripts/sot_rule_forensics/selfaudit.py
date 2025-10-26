"""
Layer 28: Self-Audit-Mode
=========================

Gold-Run verification against known-good baseline
Version: 3.0.0
"""

from typing import List, Tuple, Dict
import json
from pathlib import Path

class SelfAuditMode:
    """Self-audit against gold standard"""

    def __init__(self, gold_file: Path = Path('gold_run.json')):
        self.gold_file = gold_file
        self.gold_data: Dict = {}
        self.current_data: Dict = {}
        self.discrepancies: List[str] = []

    def load_gold_run(self):
        """Load gold standard run data"""
        if self.gold_file.exists():
            with open(self.gold_file, 'r') as f:
                self.gold_data = json.load(f)

    def save_gold_run(self, data: Dict):
        """Save current run as gold standard"""
        with open(self.gold_file, 'w') as f:
            json.dump(data, f, indent=2)
        self.gold_data = data

    def audit_against_gold(self, current: Dict) -> bool:
        """Audit current run against gold"""
        self.current_data = current
        self.discrepancies = []

        if not self.gold_data:
            self.discrepancies.append("No gold standard available")
            return False

        # Compare rule counts
        gold_count = self.gold_data.get('rule_count', 0)
        current_count = current.get('rule_count', 0)

        if gold_count != current_count:
            self.discrepancies.append(
                f"Rule count mismatch: {current_count} vs {gold_count} (gold)"
            )

        return len(self.discrepancies) == 0

    def get_discrepancies(self) -> List[str]:
        """Get list of discrepancies"""
        return self.discrepancies

    def self_verify(self) -> Tuple[bool, List[str]]:
        """Self-verification"""
        issues = []
        if self.discrepancies:
            issues.extend(self.discrepancies)
        return len(issues) == 0, issues
