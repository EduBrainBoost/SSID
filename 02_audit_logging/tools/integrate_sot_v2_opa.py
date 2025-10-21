#!/usr/bin/env python3
"""
Integrate SOT-V2 OPA Policies
===============================
Replaces placeholder SOT-V2 policies in sot_policy.rego with generated real logic.

Usage:
    python integrate_sot_v2_opa.py
"""

from pathlib import Path
import re


def integrate_policies(generated_file: Path, main_policy: Path, dry_run=True):
    """Replace placeholder policies with generated ones."""

    print()
    print("=" * 80)
    print("INTEGRATE SOT-V2 OPA POLICIES")
    print("=" * 80)
    print()

    if dry_run:
        print("[DRY RUN] No changes will be made")
        print()

    # Read generated policies
    with open(generated_file, 'r', encoding='utf-8') as f:
        generated_content = f.read()

    # Parse generated policies into a dict {rule_num: policy_text}
    generated_policies = {}
    pattern = r'# SOT-V2-(\d{4}):.*?\n(.*?\n)*?}'

    for match in re.finditer(pattern, generated_content, re.MULTILINE):
        rule_num = int(match.group(1))
        policy_text = match.group(0)
        generated_policies[rule_num] = policy_text

    print(f"[+] Loaded {len(generated_policies)} generated policies")

    # Read main policy
    with open(main_policy, 'r', encoding='utf-8') as f:
        main_content = f.read()

    # Replace each placeholder
    modified_content = main_content
    replaced_count = 0

    for rule_num in range(1, 190):
        if rule_num in [91, 92, 93, 94]:
            # Skip - these have custom implementations
            continue

        if rule_num not in generated_policies:
            print(f"[WARN] No generated policy for SOT-V2-{rule_num:04d}")
            continue

        # Find placeholder for this rule
        placeholder_pattern = (
            rf'# SOT-V2-{rule_num:04d}:.*?\n'
            r'(.*?\n)*?'
            r'deny\[msg\] \{\s*\n'
            r'(.*?\n)*?'
            r'\s*false\s+# Placeholder.*?\n'
            r'(.*?\n)*?'
            r'\}'
        )

        matches = list(re.finditer(placeholder_pattern, modified_content, re.MULTILINE))

        if not matches:
            print(f"[WARN] No placeholder found for SOT-V2-{rule_num:04d}")
            continue

        if len(matches) > 1:
            print(f"[WARN] Multiple placeholders found for SOT-V2-{rule_num:04d}, using first")

        placeholder_text = matches[0].group(0)
        new_policy = generated_policies[rule_num]

        modified_content = modified_content.replace(placeholder_text, new_policy, 1)
        replaced_count += 1

        if replaced_count % 10 == 0:
            print(f"[+] Replaced {replaced_count}/185 placeholders...")

    print()
    print(f"[+] Replaced {replaced_count} placeholder policies")

    if not dry_run:
        # Backup main policy
        backup_path = main_policy.with_suffix('.rego.backup_before_integration')
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(main_content)
        print(f"[+] Backup created: {backup_path}")

        # Write modified policy
        with open(main_policy, 'w', encoding='utf-8') as f:
            f.write(modified_content)
        print(f"[+] Updated: {main_policy}")

    print()
    return replaced_count


def main():
    generated_file = Path("02_audit_logging/reports/sot_v2_opa_generated.rego")
    main_policy = Path("23_compliance/policies/sot/sot_policy.rego")

    if not generated_file.exists():
        print(f"[ERROR] Generated file not found: {generated_file}")
        print("[INFO] Run generate_sot_v2_opa_logic.py first")
        return 1

    if not main_policy.exists():
        print(f"[ERROR] Main policy not found: {main_policy}")
        return 1

    # Step 1: Dry run
    print("[STEP 1] DRY RUN - Preview changes")
    replaced = integrate_policies(generated_file, main_policy, dry_run=True)

    if replaced == 0:
        print("[ERROR] No placeholders found to replace!")
        print("[INFO] Check that sot_policy.rego has placeholder policies")
        return 1

    print()
    print("=" * 80)
    print("[STEP 2] Ready to execute")
    print("=" * 80)
    print()
    print(f"Will replace {replaced} placeholder policies with real validation logic")
    print()

    response = input("Execute integration? [yes/no]: ").strip().lower()

    if response == "yes":
        print()
        print("[STEP 2] EXECUTING INTEGRATION...")
        print()
        integrate_policies(generated_file, main_policy, dry_run=False)

        print("=" * 80)
        print("[SUCCESS] SOT-V2 policies integrated!")
        print("=" * 80)
        print()
        print("[NEXT] Test policies with:")
        print("  opa test 23_compliance/policies/sot/")
        print()
    else:
        print()
        print("[CANCELLED] No changes made")
        print()

    return 0


if __name__ == "__main__":
    exit(main())
