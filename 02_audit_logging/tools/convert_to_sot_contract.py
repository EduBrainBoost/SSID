#!/usr/bin/env python3
"""
SoT Contract Generator - Converts Master-Rule-List to 2-Level Schema
====================================================================

Input:  02_audit_logging/reports/SoT_Manual_Coverage_Masterlist_CORRECTED_20251019.yaml
Output:
  - Level A: 16_codex/contracts/sot/sot_contract.yaml (264 semantic rules)
  - Level B: 16_codex/contracts/sot/sot_contract_expanded.yaml (1276+ machine rules)
  - Level B: 16_codex/contracts/sot/sot_line_rules.json (JSON mirror)

Author: Claude Code AI
Date: 2025-10-19
Version: 1.0.0
"""

import sys
import yaml
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

class SoTContractGenerator:
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.masterlist_path = repo_root / "02_audit_logging" / "reports" / "SoT_Manual_Coverage_Masterlist_CORRECTED_20251019.yaml"
        self.output_contract_path = repo_root / "16_codex" / "contracts" / "sot" / "sot_contract.yaml"
        self.output_expanded_path = repo_root / "16_codex" / "contracts" / "sot" / "sot_contract_expanded.yaml"
        self.output_json_path = repo_root / "16_codex" / "contracts" / "sot" / "sot_line_rules.json"

        self.semantic_rules = []
        self.machine_rules = []

    def load_master_list(self) -> Dict:
        """Load master rule list"""
        print(f"Loading Master-Rule-List from: {self.masterlist_path}")
        with open(self.masterlist_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def map_priority_to_severity(self, priority: str) -> str:
        """Map priority to severity"""
        mapping = {
            "CRITICAL": "CRITICAL",
            "HIGH": "HIGH",
            "MEDIUM": "MEDIUM",
            "LOW": "LOW",
            "INFO": "INFO"
        }
        return mapping.get(priority, "MEDIUM")

    def generate_semantic_rules(self, data: Dict) -> None:
        """Generate Level A: Semantic rules"""
        print("\nGenerating Level A: Semantic Rules...")

        sections = [
            ('grundprinzipien', 'Grundprinzipien'),
            ('token_architecture', 'Token Architecture'),
            ('token_utility', 'Token Utility'),
            ('token_economics', 'Token Economics'),
            ('language_strategy', 'Language Strategy'),
            ('multi_jurisdiction', 'Multi-Jurisdiction')
        ]

        for section_key, section_name in sections:
            if section_key not in data:
                continue

            section_data = data[section_key]

            # Handle different section structures
            if isinstance(section_data, dict) and 'regeln' in section_data:
                rules_list = section_data['regeln']
            elif isinstance(section_data, list):
                rules_list = section_data
            else:
                continue

            for rule in rules_list:
                semantic_rule = {
                    'rule_id': rule.get('regel_id', ''),
                    'source': f"{data['metadata']['source_file']}:{rule.get('zeile', 0)}",
                    'category': rule.get('kategorie', 'General'),
                    'severity': self.map_priority_to_severity(rule.get('priority', 'MEDIUM')),
                    'enforcement': rule.get('enforcement', 'MUST'),
                    'description': rule.get('beschreibung', '')
                }

                # Add optional fields
                if rule.get('originaltext'):
                    semantic_rule['originaltext'] = rule['originaltext']
                if rule.get('feld'):
                    semantic_rule['field'] = rule['feld']
                if rule.get('wert'):
                    semantic_rule['value'] = rule['wert']
                if rule.get('referenced_file'):
                    semantic_rule['referenced_file'] = rule['referenced_file']

                self.semantic_rules.append(semantic_rule)

        print(f"  Generated {len(self.semantic_rules)} semantic rules")

    def generate_machine_rules(self) -> None:
        """Generate Level B: Machine-expanded rules"""
        print("\nGenerating Level B: Machine-Expanded Rules...")

        # For each semantic rule, generate multiple machine rules
        for semantic_rule in self.semantic_rules:
            base_id = semantic_rule['rule_id']

            # 1. Line reference rule
            line_rule = {
                'rule_id': f"{base_id}-LINE",
                'line_ref': semantic_rule['source'],
                'hash_ref': hashlib.sha256(semantic_rule['description'].encode()).hexdigest()[:16],
                'auto_generated': True,
                'severity': semantic_rule['severity'],
                'enforcement': 'strict',
                'source': semantic_rule['source'],
                'description': f"Line reference validation for {base_id}",
                'parent_rule': base_id
            }
            self.machine_rules.append(line_rule)

            # 2. Enforcement rule
            enforcement_rule = {
                'rule_id': f"{base_id}-ENFORCE",
                'line_ref': semantic_rule['source'],
                'hash_ref': hashlib.sha256(semantic_rule['enforcement'].encode()).hexdigest()[:16],
                'auto_generated': True,
                'severity': semantic_rule['severity'],
                'enforcement': 'strict',
                'source': semantic_rule['source'],
                'description': f"Enforcement validation for {base_id}: {semantic_rule['enforcement']}",
                'parent_rule': base_id
            }
            self.machine_rules.append(enforcement_rule)

            # 3. Category compliance rule
            category_rule = {
                'rule_id': f"{base_id}-CAT",
                'line_ref': semantic_rule['source'],
                'hash_ref': hashlib.sha256(semantic_rule['category'].encode()).hexdigest()[:16],
                'auto_generated': True,
                'severity': semantic_rule['severity'],
                'enforcement': 'strict',
                'source': semantic_rule['source'],
                'description': f"Category compliance for {base_id}: {semantic_rule['category']}",
                'parent_rule': base_id
            }
            self.machine_rules.append(category_rule)

            # 4. Field validation rule (if field exists)
            if 'field' in semantic_rule:
                field_rule = {
                    'rule_id': f"{base_id}-FIELD",
                    'line_ref': semantic_rule['source'],
                    'hash_ref': hashlib.sha256(semantic_rule['field'].encode()).hexdigest()[:16],
                    'auto_generated': True,
                    'severity': semantic_rule['severity'],
                    'enforcement': 'strict',
                    'source': semantic_rule['source'],
                    'description': f"Field validation for {base_id}: {semantic_rule['field']}",
                    'parent_rule': base_id,
                    'field': semantic_rule['field']
                }
                if 'value' in semantic_rule:
                    field_rule['expected_value'] = semantic_rule['value']
                self.machine_rules.append(field_rule)

            # 5. Reference validation rule (if referenced_file exists)
            if 'referenced_file' in semantic_rule:
                ref_rule = {
                    'rule_id': f"{base_id}-REF",
                    'line_ref': semantic_rule['source'],
                    'hash_ref': hashlib.sha256(semantic_rule['referenced_file'].encode()).hexdigest()[:16],
                    'auto_generated': True,
                    'severity': semantic_rule['severity'],
                    'enforcement': 'strict',
                    'source': semantic_rule['source'],
                    'description': f"Reference validation for {base_id}: {semantic_rule['referenced_file']}",
                    'parent_rule': base_id,
                    'referenced_file': semantic_rule['referenced_file']
                }
                self.machine_rules.append(ref_rule)

        print(f"  Generated {len(self.machine_rules)} machine rules from {len(self.semantic_rules)} semantic rules")
        print(f"  Expansion ratio: {len(self.machine_rules) / len(self.semantic_rules):.2f}x")

    def write_semantic_contract(self) -> None:
        """Write Level A: sot_contract.yaml"""
        print(f"\nWriting Level A to: {self.output_contract_path}")

        contract = {
            'metadata': {
                'version': '1.0.0',
                'generated': datetime.now().isoformat(),
                'source': 'SoT_Manual_Coverage_Masterlist_CORRECTED_20251019.yaml',
                'total_rules': len(self.semantic_rules),
                'level': 'A_SEMANTIC',
                'usage': 'Python- und Rego-Validatoren, SoT-Audits, MiCA/eIDAS-Zertifizierung'
            },
            'rules': self.semantic_rules
        }

        self.output_contract_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.output_contract_path, 'w', encoding='utf-8') as f:
            yaml.dump(contract, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

        print(f"  OK Written {len(self.semantic_rules)} semantic rules")

    def write_expanded_contract(self) -> None:
        """Write Level B: sot_contract_expanded.yaml and JSON mirror"""
        print(f"\nWriting Level B (YAML) to: {self.output_expanded_path}")

        expanded = {
            'metadata': {
                'version': '1.0.0',
                'generated': datetime.now().isoformat(),
                'source': 'sot_contract.yaml (auto-generated expansion)',
                'total_rules': len(self.machine_rules),
                'level': 'B_MACHINE',
                'auto_generated': True,
                'usage': 'OPA-CI, Hash-Vergleiche, Drift-Detection, SAFE-FIX-Layer'
            },
            'rules': self.machine_rules
        }

        with open(self.output_expanded_path, 'w', encoding='utf-8') as f:
            yaml.dump(expanded, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

        print(f"  OK Written {len(self.machine_rules)} machine rules (YAML)")

        # JSON mirror
        print(f"\nWriting Level B (JSON) to: {self.output_json_path}")
        with open(self.output_json_path, 'w', encoding='utf-8') as f:
            json.dump(expanded, f, indent=2, ensure_ascii=False)

        print(f"  OK Written {len(self.machine_rules)} machine rules (JSON)")

    def generate_summary(self) -> None:
        """Generate summary report"""
        print("\n" + "="*80)
        print("SoT CONTRACT GENERATION - SUMMARY")
        print("="*80)
        print(f"\nLevel A (Semantic Rules):")
        print(f"  File: {self.output_contract_path}")
        print(f"  Rules: {len(self.semantic_rules)}")
        print(f"  Fields: rule_id, source, category, severity, enforcement, description")

        print(f"\nLevel B (Machine Rules):")
        print(f"  File (YAML): {self.output_expanded_path}")
        print(f"  File (JSON): {self.output_json_path}")
        print(f"  Rules: {len(self.machine_rules)}")
        print(f"  Fields: rule_id, line_ref, hash_ref, auto_generated, severity, enforcement, source")

        print(f"\nExpansion Statistics:")
        print(f"  Semantic -> Machine: {len(self.semantic_rules)} -> {len(self.machine_rules)}")
        print(f"  Expansion Ratio: {len(self.machine_rules) / len(self.semantic_rules):.2f}x")

        # Severity breakdown
        severity_counts = {}
        for rule in self.semantic_rules:
            sev = rule['severity']
            severity_counts[sev] = severity_counts.get(sev, 0) + 1

        print(f"\nSeverity Distribution (Semantic):")
        for sev in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO']:
            count = severity_counts.get(sev, 0)
            pct = (count / len(self.semantic_rules) * 100) if self.semantic_rules else 0
            print(f"  {sev:10s}: {count:3d} ({pct:5.1f}%)")

        print("\n" + "="*80)

def main():
    repo_root = Path(__file__).resolve().parent.parent.parent
    generator = SoTContractGenerator(repo_root)

    # Load master list
    data = generator.load_master_list()

    # Generate semantic rules (Level A)
    generator.generate_semantic_rules(data)

    # Generate machine rules (Level B)
    generator.generate_machine_rules()

    # Write outputs
    generator.write_semantic_contract()
    generator.write_expanded_contract()

    # Summary
    generator.generate_summary()

    print("\nDONE - SoT Contract Generation Complete")
    return 0

if __name__ == "__main__":
    sys.exit(main())
