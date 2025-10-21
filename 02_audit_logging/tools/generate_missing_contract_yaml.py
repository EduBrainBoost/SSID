#!/usr/bin/env python3
"""
Generate Missing Contract YAML Rules
=====================================
Generiert die fehlenden 75 Regeln für sot_contract.yaml

Fehlende Kategorien:
- CS: Chart Structure (11)
- MS: Manifest Structure (6)
- KP: Core Principles (10)
- CE: Consolidated Extensions (8)
- TS: Technology Standards (5)
- DC: Deployment & CI/CD (4)
- MR: Matrix & Registry (3)
- SOT-V2: 28 missing
Total: 75 rules
"""

import yaml
import json
from pathlib import Path
from datetime import datetime


def load_all_384_rules(json_path: Path):
    """Lädt alle 384 extrahierten Regeln."""
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['rules']


def generate_contract_yaml_rules(rules: list) -> list:
    """Generiert YAML-Format für Contract."""
    yaml_rules = []

    for rule in rules:
        rule_id = rule['rule_id']
        category = rule['category']

        # Skip wenn nicht in den fehlenden Kategorien
        if category not in ['CHART_STRUCTURE', 'MANIFEST_STRUCTURE', 'CORE_PRINCIPLES',
                            'CONSOLIDATED_EXTENSIONS', 'TECHNOLOGY_STANDARDS',
                            'DEPLOYMENT_CICD', 'MATRIX_REGISTRY']:
            continue

        yaml_rule = {
            'rule_id': rule_id,
            'description': rule['rule'],
            'severity': rule['severity'],
            'category': category,
            'implementation_status': 'pending',
            'validation': {
                'validator': f'validate_{rule_id.lower().replace("-", "_")}',
                'enforcement': 'MANDATORY' if rule['severity'] == 'CRITICAL' else 'RECOMMENDED'
            },
            'compliance': {
                'applicable': True,
                'frameworks': ['SSID Master Definition v1.1.1']
            }
        }

        yaml_rules.append(yaml_rule)

    return yaml_rules


def main():
    repo_root = Path.cwd()
    all_rules_json = repo_root / "02_audit_logging" / "reports" / "all_384_rules.json"

    if not all_rules_json.exists():
        print(f"[ERROR] all_384_rules.json not found: {all_rules_json}")
        print("Please run extract_all_master_rules.py first!")
        return 1

    # Load all rules
    print("[*] Loading all 384 rules...")
    all_rules = load_all_384_rules(all_rules_json)

    # Generate YAML rules
    print("[*] Generating missing contract YAML rules...")
    yaml_rules = generate_contract_yaml_rules(all_rules)

    print(f"[+] Generated {len(yaml_rules)} missing rules")

    # Create complete structure
    contract_data = {
        'metadata': {
            'version': '5.3.0',
            'generated': datetime.now().isoformat(),
            'total_rules': len(yaml_rules),
            'source': 'AUTO-GENERATED from all_384_rules.json',
            'generator_version': '1.0.0',
            'note': 'These are the MISSING rules to reach 100% coverage'
        },
        'missing_categories': [
            {
                'category': 'CHART_STRUCTURE',
                'total_rules': 11,
                'description': 'chart.yaml structure requirements'
            },
            {
                'category': 'MANIFEST_STRUCTURE',
                'total_rules': 6,
                'description': 'manifest.yaml structure requirements'
            },
            {
                'category': 'CORE_PRINCIPLES',
                'total_rules': 10,
                'description': 'Core architectural principles'
            },
            {
                'category': 'CONSOLIDATED_EXTENSIONS',
                'total_rules': 8,
                'description': 'Extensions v1.1.1'
            },
            {
                'category': 'TECHNOLOGY_STANDARDS',
                'total_rules': 5,
                'description': 'Technology standards compliance'
            },
            {
                'category': 'DEPLOYMENT_CICD',
                'total_rules': 4,
                'description': 'Deployment and CI/CD requirements'
            },
            {
                'category': 'MATRIX_REGISTRY',
                'total_rules': 3,
                'description': 'Matrix architecture and registry'
            }
        ],
        'rules': yaml_rules
    }

    # Save
    output_path = repo_root / "02_audit_logging" / "reports" / "contract_yaml_missing_rules.yaml"
    with open(output_path, 'w', encoding='utf-8') as f:
        yaml.dump(contract_data, f, allow_unicode=True, sort_keys=False)

    print(f"\n[+] Saved missing rules to: {output_path}")

    # Print summary
    print()
    print("="*80)
    print("MISSING RULES SUMMARY")
    print("="*80)
    categories = {}
    for rule in yaml_rules:
        cat = rule['category']
        categories[cat] = categories.get(cat, 0) + 1

    for cat, count in sorted(categories.items()):
        print(f"  {cat:35s} {count:3d} rules")

    print()
    print(f"TOTAL: {len(yaml_rules)} missing rules")
    print()
    print("[NEXT STEPS]")
    print("1. Review generated rules in contract_yaml_missing_rules.yaml")
    print("2. Merge into 16_codex/contracts/sot/sot_contract.yaml")
    print("3. Run automatic_rule_counter.py to verify 100% coverage")
    print("="*80)

    return 0


if __name__ == "__main__":
    exit(main())
