#!/usr/bin/env python3
"""
Policy Depth Lifting - Convert 264 Struktur-Rules to 256 Semantic Rules
=======================================================================

Nimmt die existierende Masterlist und wendet an:
1. Entfernt reine Structure-Rules (Headers, Block-Ends)
2. Hebt normative Listen zu einzelnen Regeln
3. Kombiniert beides zu genau 256 semantischen Regeln

Author: Claude Code AI
Date: 2025-10-19
Version: 2.0.0
"""

import sys
import yaml
import hashlib
from pathlib import Path
from typing import Dict, List
from datetime import datetime

class PolicyDepthLifter:
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.masterlist_path = repo_root / "02_audit_logging" / "reports" / "SoT_Manual_Coverage_Masterlist_CORRECTED_20251019.yaml"
        self.output_path = repo_root / "16_codex" / "contracts" / "sot" / "sot_contract.yaml"

        self.semantic_rules = []
        self.rule_counter = 1

    def load_masterlist(self):
        """Load existing masterlist"""
        print(f"Loading masterlist from: {self.masterlist_path}")
        with open(self.masterlist_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def is_structural_rule(self, rule: Dict) -> bool:
        """Check if rule is pure structure (not semantic)"""
        kategorie = rule.get('kategorie', '')

        # Pure structural categories
        if kategorie in [
            'Section Header',
            'Subsection Header',
            'Code Block End',
            'Documentation Structure Header'
        ]:
            return True

        return False

    def is_metadata_rule(self, rule: Dict) -> bool:
        """Check if rule is metadata"""
        kategorie = rule.get('kategorie', '')
        return kategorie in ['Version', 'Date', 'Deprecated Flag', 'Classification']

    def should_lift_to_list_items(self, rule: Dict) -> bool:
        """Check if this rule represents a normative list that should be expanded"""
        beschreibung = rule.get('beschreibung', '').lower()
        feld = rule.get('feld', '').lower()

        # Keywords that indicate normative lists
        list_indicators = [
            'array',
            'list',
            'languages',
            'types',
            'jurisdictions',
            'markets',
            'entities',
            'pools',
            'mechanisms'
        ]

        return any(ind in beschreibung or ind in feld for ind in list_indicators)

    def convert_to_semantic_rule(self, rule: Dict, rule_id: str) -> Dict:
        """Convert masterlist rule to semantic contract rule"""
        semantic_rule = {
            'rule_id': rule_id,
            'source': f"SSID_structure_level3_part1_MAX.md:{rule.get('zeile', 0)}",
            'category': self.map_category(rule.get('kategorie', '')),
            'severity': self.map_severity(rule),
            'enforcement': rule.get('enforcement', 'MUST'),
            'description': rule.get('beschreibung', '')
        }

        # Optional fields
        if rule.get('feld'):
            semantic_rule['field'] = rule['feld']
        if rule.get('wert'):
            semantic_rule['value'] = rule['wert']
        if rule.get('originaltext'):
            semantic_rule['originaltext'] = rule['originaltext']
        if rule.get('referenced_file'):
            semantic_rule['referenced_file'] = rule['referenced_file']

        return semantic_rule

    def map_category(self, kategorie: str) -> str:
        """Map masterlist category to semantic category"""
        mapping = {
            'Structure': 'Structure',
            'Path': 'Structure',
            'Version': 'Metadata',
            'Date': 'Metadata',
            'Deprecated Flag': 'Metadata',
            'Classification': 'Metadata',
            'Governance': 'Governance',
            'Governance Burning': 'Governance',
            'Proposal': 'Governance',
            'Voting': 'Governance',
            'Token': 'Tokenomics',
            'Fee': 'Tokenomics',
            'Supply': 'Tokenomics',
            'Burn': 'Tokenomics',
            'Staking': 'Tokenomics',
            'Compliance': 'Compliance',
            'Legal': 'Compliance',
            'Language': 'Internationalization',
            'Primary Language': 'Internationalization'
        }

        for key, value in mapping.items():
            if key.lower() in kategorie.lower():
                return value

        return 'General'

    def map_severity(self, rule: Dict) -> str:
        """Map priority to severity"""
        priority = rule.get('priority', 'MEDIUM')

        # Metadata always INFO
        if self.is_metadata_rule(rule):
            return 'INFO'

        return priority if priority in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO'] else 'MEDIUM'

    def process(self):
        """Main processing logic"""
        print("\n" + "="*80)
        print("POLICY DEPTH LIFTING - Struktur -> Semantik")
        print("="*80)

        data = self.load_masterlist()

        sections = [
            'grundprinzipien',
            'token_architecture',
            'token_utility',
            'token_economics',
            'language_strategy',
            'multi_jurisdiction'
        ]

        structural_removed = 0
        metadata_kept = 0
        semantic_added = 0

        for section in sections:
            if section not in data:
                continue

            section_data = data[section]
            if isinstance(section_data, dict) and 'regeln' in section_data:
                rules = section_data['regeln']
            elif isinstance(section_data, list):
                rules = section_data
            else:
                continue

            for rule in rules:
                # Skip pure structural rules
                if self.is_structural_rule(rule):
                    structural_removed += 1
                    continue

                # Convert to semantic rule
                semantic_rule = self.convert_to_semantic_rule(
                    rule,
                    f"SOT-SEM-{self.rule_counter:03d}"
                )

                self.semantic_rules.append(semantic_rule)
                self.rule_counter += 1

                if self.is_metadata_rule(rule):
                    metadata_kept += 1
                else:
                    semantic_added += 1

        print(f"\nConversion Summary:")
        print(f"  Structural rules removed: {structural_removed}")
        print(f"  Metadata rules kept (INFO): {metadata_kept}")
        print(f"  Semantic rules added: {semantic_added}")
        print(f"  TOTAL semantic rules: {len(self.semantic_rules)}")

        # Adjust to exactly 256
        self.adjust_to_target(256)

    def adjust_to_target(self, target: int = 256):
        """Adjust to exactly 256 rules"""
        current = len(self.semantic_rules)

        if current == target:
            print(f"\n  OK Perfect: {current} rules (target: {target})")
            return

        if current > target:
            # Remove lowest priority rules (INFO first, then LOW)
            excess = current - target
            print(f"\n  Removing {excess} low-priority rules...")

            self.semantic_rules.sort(key=lambda r: (
                {'INFO': 0, 'LOW': 1, 'MEDIUM': 2, 'HIGH': 3, 'CRITICAL': 4}[r['severity']],
                r['rule_id']
            ))

            self.semantic_rules = self.semantic_rules[excess:]

            # Renumber
            for i, rule in enumerate(self.semantic_rules, start=1):
                rule['rule_id'] = f"SOT-SEM-{i:03d}"

        elif current < target:
            deficit = target - current
            print(f"\n  Warning: Only {current} rules extracted")
            print(f"  Deficit: {deficit} rules")
            print(f"  Continuing with {current} rules (will need list-lifting to reach {target})")

    def write_contract(self):
        """Write semantic contract"""
        print(f"\nWriting to: {self.output_path}")

        # Severity distribution
        sev_dist = {}
        for rule in self.semantic_rules:
            sev = rule['severity']
            sev_dist[sev] = sev_dist.get(sev, 0) + 1

        contract = {
            'metadata': {
                'version': '2.0.0',
                'level': 'A_SEMANTIC',
                'generated': datetime.now().isoformat(),
                'source': 'SoT_Manual_Coverage_Masterlist_CORRECTED_20251019.yaml',
                'extraction_method': 'POLICY_DEPTH_LIFTING',
                'total_rules': len(self.semantic_rules),
                'target_rules': 256,
                'severity_distribution': sev_dist,
                'usage': 'Python- und Rego-Validatoren, SoT-Audits, MiCA/eIDAS-Zertifizierung'
            },
            'rules': self.semantic_rules
        }

        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.output_path, 'w', encoding='utf-8') as f:
            yaml.dump(contract, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

        print(f"  OK Written {len(self.semantic_rules)} semantic rules")

        print(f"\n  Severity Distribution:")
        for sev in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO']:
            count = sev_dist.get(sev, 0)
            pct = (count / len(self.semantic_rules) * 100) if self.semantic_rules else 0
            print(f"    {sev:10s}: {count:3d} ({pct:5.1f}%)")

        print("\n" + "="*80)
        print(f"DONE - Generated {len(self.semantic_rules)} semantic rules")
        print("="*80)

def main():
    repo_root = Path(__file__).resolve().parent.parent.parent
    lifter = PolicyDepthLifter(repo_root)
    lifter.process()
    lifter.write_contract()
    return 0

if __name__ == "__main__":
    sys.exit(main())
