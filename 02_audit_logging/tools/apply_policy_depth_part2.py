#!/usr/bin/env python3
"""
Policy Depth Filtering Part2 - 715 Rules -> 256 Semantic Core Rules
====================================================================

Takes the complete Part2 masterlist (715 rules) and applies policy-depth
filtering to extract the 256 most important semantic rules.

Author: Claude Code AI
Date: 2025-10-19
Version: 3.0.0-PART2
"""

import sys
import yaml
from pathlib import Path
from typing import Dict, List
from datetime import datetime

class PolicyDepthFilterPart2:
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.complete_masterlist = repo_root / "02_audit_logging" / "reports" / "SoT_Complete_Masterlist_Part2_20251019.yaml"
        self.filtered_output = repo_root / "02_audit_logging" / "reports" / "SoT_Semantic_Core_Part2_256_20251019.yaml"

        self.all_rules = []
        self.semantic_rules = []

    def load_complete_masterlist(self):
        """Load complete 715-rule Part2 masterlist"""
        print(f"Loading complete Part2 masterlist: {self.complete_masterlist}")
        with open(self.complete_masterlist, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        # Extract all rules from all sections
        for section in data.get('sections', []):
            self.all_rules.extend(section.get('regeln', []))

        print(f"  Loaded {len(self.all_rules)} total Part2 rules")

    def is_structural_rule(self, rule: Dict) -> bool:
        """Check if rule is pure structure"""
        kategorie = rule.get('kategorie', '')
        return kategorie in [
            'Section Header',
            'Subsection Header',
            'Code Block End',
            'Documentation Structure Header'
        ]

    def is_low_value_metadata(self, rule: Dict) -> bool:
        """Check if rule is low-value metadata"""
        kategorie = rule.get('kategorie', '')
        feld = rule.get('feld', '').lower()

        if kategorie == 'Metadata':
            if 'date' in feld and 'release' not in feld:
                return True
            if 'deprecated' in feld and rule.get('wert') == 'false':
                return True

        return False

    def calculate_semantic_score(self, rule: Dict) -> int:
        """Calculate semantic importance score"""
        score = 0

        # Priority score
        priority = rule.get('priority', 'MEDIUM')
        priority_scores = {
            'CRITICAL': 1000,
            'HIGH': 500,
            'MEDIUM': 200,
            'LOW': 50,
            'INFO': 10
        }
        score += priority_scores.get(priority, 0)

        # Category score
        kategorie = rule.get('kategorie', 'General')
        category_scores = {
            'Guard/Enforcement': 400,
            'Anti-Gaming': 350,
            'Compliance': 300,
            'Governance': 250,
            'Registry': 220,
            'Structure': 180,
            'Review/Audit': 150,
            'ESG/Diversity': 120,
            'Multi-Sector': 100,
            'Metadata': 20,
            'General': 50
        }

        for cat_key, cat_score in category_scores.items():
            if cat_key.lower() in kategorie.lower():
                score += cat_score
                break

        # Bonus for enforcement
        enforcement = rule.get('enforcement', '')
        if 'MUST' in enforcement or 'strict' in enforcement:
            score += 100

        # Bonus for bash validation rules
        if 'Bash Validation' in kategorie:
            score += 150

        return score

    def filter_to_semantic_core(self, target: int = 256):
        """Filter to exactly 256 semantic core rules"""
        print(f"\nFiltering {len(self.all_rules)} Part2 rules to {target} semantic core...")

        # Step 1: Remove structural rules
        non_structural = [r for r in self.all_rules if not self.is_structural_rule(r)]
        print(f"  Removed {len(self.all_rules) - len(non_structural)} structural rules")

        # Step 2: Remove low-value metadata
        valuable = [r for r in non_structural if not self.is_low_value_metadata(r)]
        print(f"  Removed {len(non_structural) - len(valuable)} low-value metadata rules")

        # Step 3: Calculate semantic scores
        for rule in valuable:
            rule['semantic_score'] = self.calculate_semantic_score(rule)

        # Step 4: Sort by semantic score (descending)
        valuable.sort(key=lambda r: r['semantic_score'], reverse=True)

        # Step 5: Take top 256
        self.semantic_rules = valuable[:target]

        print(f"  Selected top {len(self.semantic_rules)} semantic rules")

        # Renumber rules
        for i, rule in enumerate(self.semantic_rules, start=1):
            rule['regel_id'] = f"SOT-PART2-SEM-{i:03d}"
            # Remove semantic_score from output
            if 'semantic_score' in rule:
                del rule['semantic_score']

    def write_semantic_core(self):
        """Write filtered Part2 semantic core to file"""
        print(f"\nWriting Part2 semantic core to: {self.filtered_output}")

        # Calculate severity distribution
        sev_dist = {}
        for rule in self.semantic_rules:
            priority = rule.get('priority', 'MEDIUM')
            sev_dist[priority] = sev_dist.get(priority, 0) + 1

        # Calculate category distribution
        cat_dist = {}
        for rule in self.semantic_rules:
            kategorie = rule.get('kategorie', 'General')
            cat_dist[kategorie] = cat_dist.get(kategorie, 0) + 1

        output = {
            'metadata': {
                'version': '3.0.0-PART2-SEMANTIC-CORE',
                'extraction_date': datetime.now().isoformat(),
                'source': 'SoT_Complete_Masterlist_Part2_20251019.yaml',
                'total_rules': len(self.semantic_rules),
                'target_rules': 256,
                'extraction_method': 'POLICY_DEPTH_FILTERING_PART2',
                'filtering_strategy': 'Priority-based + Category-weighted semantic scoring (Part2)',
                'severity_distribution': sev_dist,
                'category_distribution': cat_dist
            },
            'rules': self.semantic_rules
        }

        self.filtered_output.parent.mkdir(parents=True, exist_ok=True)
        with open(self.filtered_output, 'w', encoding='utf-8') as f:
            yaml.dump(output, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

        print(f"  OK Written {len(self.semantic_rules)} Part2 semantic core rules")

        # Print distributions
        print(f"\n  Priority Distribution:")
        for priority in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO']:
            count = sev_dist.get(priority, 0)
            pct = (count / len(self.semantic_rules) * 100) if self.semantic_rules else 0
            print(f"    {priority:10s}: {count:3d} ({pct:5.1f}%)")

        print(f"\n  Category Distribution (top 5):")
        top_categories = sorted(cat_dist.items(), key=lambda x: x[1], reverse=True)[:5]
        for cat, count in top_categories:
            pct = (count / len(self.semantic_rules) * 100) if self.semantic_rules else 0
            print(f"    {cat:30s}: {count:3d} ({pct:5.1f}%)")

    def process(self):
        """Main processing flow"""
        print("="*80)
        print("POLICY DEPTH FILTERING PART2 - 715 -> 256 Semantic Core")
        print("="*80)

        self.load_complete_masterlist()
        self.filter_to_semantic_core(256)
        self.write_semantic_core()

        print("\n" + "="*80)
        print(f"DONE - Filtered Part2 to {len(self.semantic_rules)} semantic core rules")
        print("="*80)

def main():
    repo_root = Path(__file__).resolve().parent.parent.parent
    filter_tool = PolicyDepthFilterPart2(repo_root)
    filter_tool.process()
    return 0

if __name__ == "__main__":
    sys.exit(main())
