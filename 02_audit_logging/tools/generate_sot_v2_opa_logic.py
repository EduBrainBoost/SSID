#!/usr/bin/env python3
"""
Generate SOT-V2 OPA Logic
==========================
Generates real validation logic for 189 SOT-V2 OPA policies based on field paths
from sot_contract_v2.yaml.

Replaces placeholder policies:
    deny[msg] {
        false  # Placeholder
    }

With real field validation:
    deny[msg] {
        not input.contract.business_model.data_custody
        msg := "SOT-V2-0002 VIOLATION: Missing business_model.data_custody"
    }

Usage:
    python generate_sot_v2_opa_logic.py
"""

from pathlib import Path
import yaml
import re
from datetime import datetime


def load_sot_v2_rules(source_file: Path):
    """Load SOT-V2 rules with field paths from source YAML."""
    with open(source_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    rules = {}
    for rule in data.get('rules', []):
        rule_id = rule.get('rule_id', '')
        if rule_id.startswith('SOT-V2-'):
            num = int(rule_id.split('-')[2])
            rules[num] = {
                'rule_id': rule_id,
                'field_path': rule.get('source', {}).get('path', ''),
                'category': rule.get('category', 'GENERAL'),
                'severity': rule.get('severity', 'MEDIUM'),
                'description': rule.get('description', '')
            }

    return rules


def generate_opa_policy(rule: dict) -> str:
    """Generate OPA deny rule for a single SOT-V2 rule."""

    rule_id = rule['rule_id']
    field_path = rule['field_path']
    category = rule['category']
    severity = rule['severity']
    description = rule['description']

    # Convert field_path to OPA input path
    # business_model.data_custody -> input.contract.business_model.data_custody
    if field_path:
        opa_path = f"input.contract.{field_path}"
        field_name = field_path.split('.')[-1]
    else:
        # No field path - use placeholder
        return f'''
# {rule_id}: {description}
# Severity: {severity}
# Category: {category}
deny[msg] {{
    # TODO: No field path specified in source - needs manual implementation
    false  # Placeholder
    msg := sprintf("{rule_id} VIOLATION: {description}", [])
}}
'''

    # Generate field existence check
    policy = f'''
# {rule_id}: {description}
# Severity: {severity}
# Category: {category}
# Field: {field_path}
deny[msg] {{
    not {opa_path}
    msg := sprintf("{rule_id} VIOLATION: Missing required field '{field_path}'", [])
}}
'''

    return policy


def generate_all_policies(rules: dict, output_file: Path):
    """Generate OPA policies for all SOT-V2 rules."""

    print()
    print("=" * 80)
    print("GENERATE SOT-V2 OPA LOGIC")
    print("=" * 80)
    print()

    policies = []

    # Header
    policies.append('''# ============================================================
# SOT-V2 RULES (0001-0189): CONTRACT VALIDATION
# ============================================================
# Auto-generated from sot_contract_v2.yaml
# Date: ''' + datetime.now().isoformat() + '''
# Source: 16_codex/structure/level3/sot_contract_v2.yaml
# ============================================================

package ssid.sot_v2

import future.keywords.if
import future.keywords.in

''')

    # Generate policies for each rule (excluding 91-94 which have custom implementations)
    generated_count = 0
    for num in range(1, 190):
        if num in [91, 92, 93, 94]:
            # Skip - these have custom implementations
            continue

        if num in rules:
            rule = rules[num]
            policy = generate_opa_policy(rule)
            policies.append(policy)
            generated_count += 1

            if generated_count % 10 == 0:
                print(f"[+] Generated {generated_count}/185 policies...")
        else:
            print(f"[WARN] Missing rule definition for SOT-V2-{num:04d}")

    # Write output
    output_content = '\n'.join(policies)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(output_content)

    print()
    print(f"[+] Generated {generated_count} OPA policies")
    print(f"[+] Output: {output_file}")
    print()

    return generated_count


def integrate_into_main_policy(generated_file: Path, main_policy: Path, dry_run=True):
    """Integrate generated policies into main sot_policy.rego file."""

    print()
    print("=" * 80)
    print("INTEGRATE INTO MAIN POLICY")
    print("=" * 80)
    print()

    if dry_run:
        print("[DRY RUN] No changes will be made")
        print()

    # Read generated policies
    with open(generated_file, 'r', encoding='utf-8') as f:
        generated_content = f.read()

    # Read main policy
    with open(main_policy, 'r', encoding='utf-8') as f:
        main_content = f.read()

    # Find SOT-V2 section and replace placeholder policies
    # Pattern: # SOT-V2-XXXX: ... \n deny[msg] { \n false # Placeholder
    pattern = r'# SOT-V2-(\d{4}):.*?\n(.*?\n)*?false\s+# Placeholder.*?\n\}'

    def count_placeholders(content):
        return len(re.findall(pattern, content, re.MULTILINE))

    placeholders_before = count_placeholders(main_content)
    print(f"[*] Found {placeholders_before} placeholder policies in main file")

    if dry_run:
        print()
        print("[INFO] To integrate, run with --execute flag")
        print("[INFO] This will replace placeholder policies with field validation")
        return placeholders_before

    # Backup main policy
    backup_path = main_policy.with_suffix('.rego.backup')
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(main_content)
    print(f"[+] Backup created: {backup_path}")

    # Replace placeholder section with generated policies
    # Find SOT-V2 section start
    sot_v2_start = main_content.find('# ============================================================\n# SOT-V2 RULES')

    if sot_v2_start == -1:
        print("[ERROR] Could not find SOT-V2 section in main policy")
        return 0

    # Find next major section
    sot_v2_end = main_content.find('\n\n# ============================================================\n# ', sot_v2_start + 100)

    if sot_v2_end == -1:
        # No next section - append to end
        modified_content = main_content[:sot_v2_start] + generated_content
    else:
        # Replace section
        modified_content = main_content[:sot_v2_start] + generated_content + main_content[sot_v2_end:]

    # Write modified policy
    with open(main_policy, 'w', encoding='utf-8') as f:
        f.write(modified_content)

    placeholders_after = count_placeholders(modified_content)
    print(f"[+] Integrated policies into {main_policy}")
    print(f"[+] Placeholders before: {placeholders_before}")
    print(f"[+] Placeholders after: {placeholders_after}")
    print(f"[+] Replaced: {placeholders_before - placeholders_after}")
    print()

    return placeholders_before - placeholders_after


def main():
    source_file = Path("16_codex/structure/level3/sot_contract_v2.yaml")
    output_file = Path("02_audit_logging/reports/sot_v2_opa_generated.rego")
    main_policy = Path("23_compliance/policies/sot/sot_policy.rego")

    if not source_file.exists():
        print(f"[ERROR] Source file not found: {source_file}")
        return 1

    # Step 1: Load SOT-V2 rules
    print("[STEP 1] Loading SOT-V2 rules from source YAML...")
    rules = load_sot_v2_rules(source_file)
    print(f"[+] Loaded {len(rules)} SOT-V2 rules")

    # Step 2: Generate OPA policies
    print()
    print("[STEP 2] Generating OPA policies...")
    generated_count = generate_all_policies(rules, output_file)

    # Step 3: Show integration preview
    print()
    print("[STEP 3] Integration preview...")
    placeholders = integrate_into_main_policy(output_file, main_policy, dry_run=True)

    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"  Rules loaded:        {len(rules)}")
    print(f"  Policies generated:  {generated_count}")
    print(f"  Placeholders found:  {placeholders}")
    print(f"  Generated file:      {output_file}")
    print()

    print("[NEXT STEPS]")
    print(f"  1. Review generated policies: {output_file}")
    print(f"  2. Manually integrate into:   {main_policy}")
    print(f"  3. Test with: opa test 23_compliance/policies/sot/")
    print()

    return 0


if __name__ == "__main__":
    exit(main())
