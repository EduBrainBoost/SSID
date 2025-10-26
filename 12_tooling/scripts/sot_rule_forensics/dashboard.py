"""
Layer 21: Coverage Dashboard
============================

JSON statistics and scorecard generation
Version: 3.0.0
"""

from typing import Dict, List, Tuple
import json

class CoverageDashboard:
    """Coverage dashboard and reporting"""

    def __init__(self):
        self.stats: Dict = {}

    def collect_statistics(self, rules: dict) -> Dict:
        """Collect comprehensive statistics"""
        self.stats = {
            'total_rules': len(rules),
            'by_priority': {},
            'by_source': {},
            'by_root': {},
            'coverage_percentage': 0.0
        }

        for rule_id, rule in rules.items():
            # Count by priority
            priority = getattr(rule, 'priority', 'UNKNOWN')
            self.stats['by_priority'][str(priority)] = \
                self.stats['by_priority'].get(str(priority), 0) + 1

            # Count by source type
            source_type = getattr(rule, 'source_type', 'UNKNOWN')
            self.stats['by_source'][str(source_type)] = \
                self.stats['by_source'].get(str(source_type), 0) + 1

            # Count by root
            root = getattr(rule, 'root_folder', 'UNKNOWN')
            self.stats['by_root'][root] = \
                self.stats['by_root'].get(root, 0) + 1

        return self.stats

    def generate_scorecard(self) -> str:
        """Generate scorecard markdown"""
        lines = []
        lines.append("# SoT Parser Coverage Scorecard")
        lines.append("")
        lines.append(f"**Total Rules**: {self.stats.get('total_rules', 0)}")
        lines.append("")
        lines.append("## By Priority")
        for priority, count in self.stats.get('by_priority', {}).items():
            lines.append(f"- {priority}: {count}")
        lines.append("")
        lines.append("## By Source")
        for source, count in self.stats.get('by_source', {}).items():
            lines.append(f"- {source}: {count}")

        return "\n".join(lines)

    def export_json(self, filepath: str):
        """Export statistics to JSON"""
        with open(filepath, 'w') as f:
            json.dump(self.stats, f, indent=2)

    def self_verify(self) -> Tuple[bool, List[str]]:
        """Self-verification"""
        issues = []
        if not self.stats:
            issues.append("No statistics collected")
        return len(issues) == 0, issues
