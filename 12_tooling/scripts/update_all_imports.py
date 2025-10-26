#!/usr/bin/env python3
"""
Update All Imports Script
==========================

Replaces old validator imports with new engine imports across the codebase.

Version: 4.0.0
"""

from pathlib import Path
import re
import sys


def update_file(file_path: Path) -> bool:
    """Update imports in a single file"""
    try:
        content = file_path.read_text(encoding='utf-8', errors='ignore')
    except Exception as e:
        print(f"  [WARN] Could not read {file_path.name}: {e}")
        return False

    original_content = content

    # Replacements: Old imports -> New imports
    replacements = [
        # Old validator imports
        (r'from\s+sot_validator_core\s+import\s+\w+',
         'from sot_validator_engine import RuleValidationEngine'),
        (r'from\s+sot_validator_complete\s+import\s+\w+',
         'from sot_validator_engine import RuleValidationEngine'),
        (r'from\s+sot_validator_core_v2\s+import\s+\w+',
         'from sot_validator_engine import RuleValidationEngine'),
        (r'from\s+sot_validator_autopilot\s+import\s+\w+',
         'from sot_validator_engine import RuleValidationEngine'),

        # Class name replacements
        (r'\bSoTValidatorCore\b', 'RuleValidationEngine'),
        (r'\bSoTValidatorComplete\b', 'RuleValidationEngine'),
        (r'\bSoTValidator\b', 'RuleValidationEngine'),
    ]

    modified = False
    for pattern, replacement in replacements:
        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)
            modified = True

    # Only write if changed
    if modified and content != original_content:
        try:
            file_path.write_text(content, encoding='utf-8')
            return True
        except Exception as e:
            print(f"  [WARN] Could not write {file_path.name}: {e}")
            return False

    return False


def main():
    # Set UTF-8 encoding for Windows console
    if sys.platform == 'win32':
        import os
        os.system('chcp 65001 > nul 2>&1')
        if sys.stdout.encoding != 'utf-8':
            import io
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    repo_root = Path(__file__).resolve().parents[2]

    print("="*60)
    print("UPDATING ALL IMPORTS TO NEW VALIDATOR ENGINE")
    print("="*60)
    print()

    # Directories to scan
    dirs_to_scan = [
        repo_root / '11_test_simulation',
        repo_root / '12_tooling',
        repo_root / '24_meta_orchestration',
        repo_root / '17_observability',
        repo_root / '02_audit_logging',
    ]

    updated_files = []
    skipped_files = []

    for directory in dirs_to_scan:
        if not directory.exists():
            print(f"[WARN] Directory not found: {directory.name}")
            continue

        print(f"Scanning: {directory.name}/")

        for py_file in directory.rglob('*.py'):
            # Skip __pycache__ and .pyc files
            if '__pycache__' in str(py_file) or py_file.suffix == '.pyc':
                continue

            # Skip the new engine itself
            if 'sot_validator_engine.py' in py_file.name:
                continue

            if update_file(py_file):
                updated_files.append(py_file)
                print(f"  [OK] Updated: {py_file.relative_to(repo_root)}")
            else:
                skipped_files.append(py_file)

    # Summary
    print()
    print("="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Scanned:  {len(updated_files) + len(skipped_files)} files")
    print(f"Updated:  {len(updated_files)} files")
    print(f"Skipped:  {len(skipped_files)} files (no changes needed)")
    print()

    if updated_files:
        print("Updated files:")
        for f in updated_files[:20]:  # Show first 20
            print(f"  - {f.relative_to(repo_root)}")
        if len(updated_files) > 20:
            print(f"  ... and {len(updated_files) - 20} more")

    print()
    print("[OK] Import update complete")
    return 0


if __name__ == '__main__':
    sys.exit(main())
