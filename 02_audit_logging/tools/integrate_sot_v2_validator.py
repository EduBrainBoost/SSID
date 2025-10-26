#!/usr/bin/env python3
"""
Integrate SOT-V2 Validator Methods
====================================
Integrates generated validator methods into sot_validator_core.py.

Replaces generic validate_sot_v2() with specific field validation.

Usage:
    python integrate_sot_v2_validator.py
"""

from pathlib import Path
import re


def integrate_validator(generated_file: Path, core_file: Path, dry_run=True):
    """Integrate generated methods into core validator."""

    print()
    print("=" * 80)
    print("INTEGRATE SOT-V2 VALIDATOR METHODS")
    print("=" * 80)
    print()

    if dry_run:
        print("[DRY RUN] No changes will be made")
        print()

    # Read generated code
    with open(generated_file, 'r', encoding='utf-8') as f:
        generated_content = f.read()

    # Extract helper methods (everything from line 19 to before "# Main Validator Method")
    helper_start = generated_content.find('    def _validate_field(')
    helper_end = generated_content.find('\n\n# Main Validator Method')
    helper_methods = generated_content[helper_start:helper_end].strip()

    # Extract main method (everything from validate_sot_v2 to end)
    main_start = generated_content.find('    def validate_sot_v2(')
    main_method = generated_content[main_start:].strip()

    print(f"[+] Extracted helper methods: {len(helper_methods)} chars")
    print(f"[+] Extracted main method: {len(main_method)} chars")
    print()

    # Read core validator
    with open(core_file, 'r', encoding='utf-8') as f:
        core_content = f.read()

    # Find old validate_sot_v2 method
    # Pattern: def validate_sot_v2(self, num: int) -> ValidationResult:
    #          ... (content) ...
    #          return ValidationResult(...)
    #
    # We need to find start and end of the method

    old_method_pattern = r'    def validate_sot_v2\(self, num: int\) -> ValidationResult:.*?(?=\n    def |\n\n# =|\Z)'

    matches = list(re.finditer(old_method_pattern, core_content, re.DOTALL))

    if not matches:
        print("[ERROR] Could not find validate_sot_v2() method in core file")
        return False

    if len(matches) > 1:
        print(f"[WARN] Found {len(matches)} matches for validate_sot_v2(), using first")

    old_method_match = matches[0]
    old_method_start = old_method_match.start()
    old_method_end = old_method_match.end()

    print(f"[+] Found old validate_sot_v2() at lines {old_method_start}-{old_method_end}")

    # Check if helper methods already exist
    if '_validate_field' in core_content:
        print("[!] _validate_field() already exists - will replace")
        # Find and remove old helper
        helper_pattern = r'    def _validate_field\(.*?\).*?(?=\n    def )'
        core_content = re.sub(helper_pattern, '', core_content, count=1, flags=re.DOTALL)

    if '_get_severity' in core_content:
        print("[!] _get_severity() already exists - will replace")
        # Find and remove old helper
        severity_pattern = r'    def _get_severity\(.*?\).*?(?=\n    def )'
        core_content = re.sub(severity_pattern, '', core_content, count=1, flags=re.DOTALL)

    # Insert helper methods before validate_sot_v2
    modified_content = (
        core_content[:old_method_start] +
        helper_methods + '\n\n' +
        main_method + '\n\n' +
        core_content[old_method_end:]
    )

    # Verify changes
    changes_ok = all([
        '_validate_field' in modified_content,
        '_get_severity' in modified_content,
        'field_map = {' in modified_content,
        'business_model' in modified_content,
    ])

    if not changes_ok:
        print("[ERROR] Integration failed - methods not found in modified content")
        return False

    print()
    print("[+] Integration preview successful")
    print()

    if not dry_run:
        # Backup already created by caller
        with open(core_file, 'w', encoding='utf-8') as f:
            f.write(modified_content)
        print(f"[+] Updated: {core_file}")

    return True


def main():
    generated_file = Path("02_audit_logging/reports/sot_v2_validator_generated.py")
    core_file = Path("03_core/validators/sot/sot_validator_core.py")
    backup_file = Path("03_core/validators/sot/sot_validator_core.py.backup_before_phase3")

    if not generated_file.exists():
        print(f"[ERROR] Generated file not found: {generated_file}")
        print("[INFO] Run generate_sot_v2_validator.py first")
        return 1

    if not core_file.exists():
        print(f"[ERROR] Core validator not found: {core_file}")
        return 1

    if not backup_file.exists():
        print(f"[WARN] No backup found at: {backup_file}")
        print("[INFO] Creating backup now...")
        import shutil
        shutil.copy2(core_file, backup_file)
        print(f"[+] Backup created: {backup_file}")

    print()
    print("[STEP 1] DRY RUN - Preview integration")
    success = integrate_validator(generated_file, core_file, dry_run=True)

    if not success:
        print()
        print("[ERROR] Integration preview failed - check errors above")
        return 1

    print()
    print("=" * 80)
    print("[STEP 2] Ready to execute")
    print("=" * 80)
    print()
    print("Will replace validate_sot_v2() with specific field validation")
    print("Will add _validate_field() and _get_severity() helper methods")
    print()

    response = input("Execute integration? [yes/no]: ").strip().lower()

    if response == "yes":
        print()
        print("[STEP 2] EXECUTING INTEGRATION...")
        print()
        success = integrate_validator(generated_file, core_file, dry_run=False)

        if success:
            print()
            print("=" * 80)
            print("[SUCCESS] Validator methods integrated!")
            print("=" * 80)
            print()
            print("[NEXT] Test validator:")
            print("  python -c \"")
            print("  from pathlib import Path")
            print("  import sys")
            print("  sys.path.insert(0, '03_core/validators/sot')")
            print("  from sot_validator_engine import RuleValidationEngine")
            print("  validator = RuleValidationEngine(Path('.'))")
            print("  report = validator.validate_all()")
            print("  print(f'Pass rate: {report.passed_count / report.total_rules * 100:.1f}%')")
            print("  \"")
            print()
        else:
            print()
            print("[ERROR] Integration failed")
            return 1
    else:
        print()
        print("[CANCELLED] No changes made")
        print()

    return 0


if __name__ == "__main__":
    exit(main())
