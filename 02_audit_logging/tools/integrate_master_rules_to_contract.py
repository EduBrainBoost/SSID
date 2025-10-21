#!/usr/bin/env python3
"""
Integrate Missing Master Rules into Contract YAML
==================================================
Adds the 47 missing master rules (CS, MS, KP, CE, TS, DC, MR)
from master_rules_combined.yaml into sot_contract.yaml

Usage:
    python integrate_master_rules_to_contract.py
"""

import yaml
from pathlib import Path
from datetime import datetime


def load_master_rules():
    """Load master_rules_combined.yaml"""
    master_path = Path("16_codex/structure/level3/master_rules_combined.yaml")
    with open(master_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def extract_target_rules(master_data):
    """Extract CS, MS, KP, CE, TS, DC, MR rules"""
    target_categories = {
        'architecture_rules': {'AR'},  # Skip AR, already in contract
        'critical_policies': {'CP'},    # Skip CP, already in contract
        'versioning_governance': {'VG'}, # Skip VG, already in contract
    }

    # We need: CS, MS, KP, CE, TS, DC, MR (47 rules)
    # These don't have their own sections, they're new Master Rules

    # Let me check the structure - these might be in a different location
    extracted_rules = []

    # Scan all keys for our target prefixes
    for key, value in master_data.items():
        if isinstance(value, dict) and 'rule_id' in value:
            rule_id = value['rule_id']
            prefix = rule_id.split('-')[0] if '-' in rule_id else rule_id[:2]

            # Check if this is one of our target rules
            if prefix in ['CS', 'MS', 'KP', 'CE', 'TS', 'DC', 'MR']:
                extracted_rules.append(value)

    return extracted_rules


def convert_to_contract_format(rules):
    """Convert master rules to contract YAML format"""
    contract_rules = []

    for rule in rules:
        rule_id = rule['rule_id']

        contract_rule = {
            'rule_id': rule_id,
            'category': rule.get('category', 'GENERAL'),
            'type': rule.get('type', 'MUST'),
            'severity': rule.get('severity', 'HIGH'),
            'description': rule.get('rule', ''),
            'source': rule.get('source_section', 'SSID Master Definition v1.1.1'),
            'rationale': rule.get('rationale', ''),
            'enforcement': {
                'type': 'MANDATORY' if rule.get('severity') == 'CRITICAL' else 'RECOMMENDED',
                'validation': rule.get('sot_mapping', {}).get('core', 'TBD'),
                'policy': rule.get('sot_mapping', {}).get('policy', 'TBD'),
                'test': rule.get('sot_mapping', {}).get('test', 'TBD'),
            },
            'implementation_requirements': rule.get('implementation_requirements', [])
        }

        contract_rules.append(contract_rule)

    return contract_rules


def append_to_contract_yaml(new_rules):
    """Append new rules to sot_contract.yaml"""
    contract_path = Path("16_codex/contracts/sot/sot_contract.yaml")

    # Read existing contract
    if contract_path.exists():
        with open(contract_path, 'r', encoding='utf-8') as f:
            contract_data = yaml.safe_load(f) or {}
    else:
        contract_data = {
            'version': '3.0.0',
            'generated': datetime.now().isoformat(),
            'rules': []
        }

    # Get existing rule IDs to avoid duplicates
    existing_ids = {r['rule_id'] for r in contract_data.get('rules', [])}

    # Add new rules
    new_count = 0
    for rule in new_rules:
        if rule['rule_id'] not in existing_ids:
            contract_data['rules'].append(rule)
            new_count += 1

    # Update metadata
    contract_data['total_rules'] = len(contract_data['rules'])
    contract_data['last_updated'] = datetime.now().isoformat()

    # Write back
    with open(contract_path, 'w', encoding='utf-8') as f:
        yaml.dump(contract_data, f, allow_unicode=True, sort_keys=False, default_flow_style=False)

    return new_count


def main():
    print("[*] Integrating Master Rules into Contract YAML...")
    print()

    # Load master rules
    print("[*] Loading master_rules_combined.yaml...")
    master_data = load_master_rules()

    # Extract target rules
    print("[*] Extracting CS, MS, KP, CE, TS, DC, MR rules...")
    target_rules = extract_target_rules(master_data)
    print(f"[+] Found {len(target_rules)} target rules")

    if len(target_rules) == 0:
        print("[!] No target rules found - checking structure...")
        print(f"[!] Available keys in master_rules: {list(master_data.keys())[:20]}")
        return 1

    # Convert to contract format
    print("[*] Converting to contract format...")
    contract_rules = convert_to_contract_format(target_rules)

    # Append to contract YAML
    print("[*] Appending to sot_contract.yaml...")
    new_count = append_to_contract_yaml(contract_rules)

    print()
    print(f"[SUCCESS] Added {new_count} new rules to sot_contract.yaml")
    print("[+] Contract YAML updated successfully!")

    return 0


if __name__ == "__main__":
    exit(main())
