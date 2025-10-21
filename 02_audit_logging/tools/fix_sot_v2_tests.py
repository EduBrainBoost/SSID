#!/usr/bin/env python3
"""
Fix SOT-V2 Test Suite
======================
Fixes 189 SOT-V2 tests to call correct parametrized function validate_sot_v2(num)
instead of non-existent individual functions validate_sot_v2_XXXX().

Problem:
    Generated tests call: validator.validate_sot_v2_0001()
    But function is:      validator.validate_sot_v2(1)

Solution:
    Replace all test function calls with parametrized calls.

Usage:
    python fix_sot_v2_tests.py
"""

from pathlib import Path
import re
from datetime import datetime


def fix_sot_v2_tests(test_file: Path, dry_run=True):
    """Fix SOT-V2 test function calls to use parametrized validator."""

    print()
    print("=" * 80)
    print("FIX SOT-V2 TEST SUITE")
    print("=" * 80)
    print()

    if dry_run:
        print("[DRY RUN] No changes will be made - showing what WOULD be fixed")
        print()

    # Read test file
    with open(test_file, 'r', encoding='utf-8') as f:
        content = f.read()

    fixes = []
    modified_content = content

    # Pattern: result = validator.validate_sot_v2_0123()
    # Replace with: result = validator.validate_sot_v2(123)

    # Find all SOT-V2 test function calls
    pattern = r'validator\.validate_sot_v2_(\d{4})\(\)'

    def replace_call(match):
        """Replace individual function call with parametrized call."""
        rule_num = int(match.group(1))
        old_call = match.group(0)
        new_call = f'validator.validate_sot_v2({rule_num})'

        fixes.append({
            'rule_num': rule_num,
            'old': old_call,
            'new': new_call
        })

        return new_call

    modified_content = re.sub(pattern, replace_call, content)

    # Report changes
    print(f"[*] Found {len(fixes)} SOT-V2 test function calls to fix")
    print()

    if fixes:
        print("Sample fixes (first 10):")
        print("-" * 80)
        for fix in fixes[:10]:
            print(f"  Rule SOT-V2-{fix['rule_num']:04d}:")
            print(f"    OLD: {fix['old']}")
            print(f"    NEW: {fix['new']}")
            print()

    # Write fixed content
    if not dry_run:
        backup_path = test_file.with_suffix('.py.backup')
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"[+] Backup saved: {backup_path}")

        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(modified_content)
        print(f"[+] Fixed test file: {test_file}")

    print()
    print("=" * 80)
    print(f"FIXES APPLIED: {len(fixes)}")
    print("=" * 80)
    print()

    return len(fixes)


def main():
    test_file = Path("11_test_simulation/tests_compliance/test_sot_validator.py")

    if not test_file.exists():
        print(f"[ERROR] Test file not found: {test_file}")
        return 1

    # Step 1: Dry run to show changes
    print("[STEP 1] DRY RUN - Preview changes")
    print()
    fix_count = fix_sot_v2_tests(test_file, dry_run=True)

    if fix_count == 0:
        print("[OK] No fixes needed - tests already use parametrized functions!")
        return 0

    print()
    print("=" * 80)
    print("[STEP 2] Ready to execute")
    print("=" * 80)
    print()
    print(f"Will fix {fix_count} test function calls")
    print(f"Backup will be created: {test_file}.backup")
    print()

    response = input("Execute fixes? [yes/no]: ").strip().lower()

    if response == "yes":
        print()
        print("[STEP 2] EXECUTING FIXES...")
        print()
        fix_sot_v2_tests(test_file, dry_run=False)

        print("=" * 80)
        print("[SUCCESS] SOT-V2 tests fixed!")
        print("=" * 80)
        print()
        print("[NEXT] Run pytest to verify tests pass:")
        print("  pytest 11_test_simulation/tests_compliance/test_sot_validator.py -v")
        print()
    else:
        print()
        print("[CANCELLED] No changes made")
        print()

    return 0


if __name__ == "__main__":
    exit(main())
