#!/usr/bin/env python3
"""
SSID QA/SoT Dual-Layer Policy Enforcer (Standalone Script)
===========================================================
Version: 1.0.0
Date: 2025-10-18
Author: SSID Core Team

This is the standalone version of the QA/SoT policy enforcer.
It can be used independently or integrated into .git/hooks/pre-commit

PURPOSE:
Ensure QA/system test files are ONLY added to the unified QA corpus,
preventing governance pollution and test chaos.

USAGE:
    python qa_policy_enforcer.py
    python qa_policy_enforcer.py --check-file path/to/file.py

POLICY:
- All QA test files (.py, .yaml, .yml, .rego, .json) MUST reside in:
  02_audit_logging/archives/qa_master_suite/

EXCEPTIONS:
- SoT governance artifacts (5 files only):
  * 16_codex/contracts/sot/sot_contract.yaml
  * 03_core/validators/sot/sot_validator_core.py
  * 23_compliance/policies/sot/sot_policy.rego
  * 12_tooling/cli/sot_validator.py
  * 11_test_simulation/tests_compliance/test_sot_validator.py
"""

import sys
import argparse
import subprocess
from pathlib import Path
from typing import List, Set

# ==============================================================================
# CONFIGURATION
# ==============================================================================

# Allowed directories for QA test files
ALLOWED_QA_DIRS = [
    "02_audit_logging/archives/qa_master_suite/"
]

# SoT governance artifacts (exempt from QA policy)
SOT_GOVERNANCE_FILES = {
    "16_codex/contracts/sot/sot_contract.yaml",
    "03_core/validators/sot/sot_validator_core.py",
    "23_compliance/policies/sot/sot_policy.rego",
    "12_tooling/cli/sot_validator.py",
    "11_test_simulation/tests_compliance/test_sot_validator.py"
}

# File extensions that trigger QA policy check
QA_TEST_EXTENSIONS = {".py", ".yaml", ".yml", ".rego", ".json"}

# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def is_qa_test_file(filename: str) -> bool:
    """Check if file is a QA test file based on extension."""
    return any(filename.endswith(ext) for ext in QA_TEST_EXTENSIONS)

def is_sot_governance_file(filename: str) -> bool:
    """Check if file is one of the 5 SoT governance artifacts."""
    # Normalize path separators for Windows/Unix compatibility
    normalized = filename.replace("\\", "/")
    return normalized in SOT_GOVERNANCE_FILES

def is_in_allowed_qa_dir(filename: str) -> bool:
    """Check if file is in an allowed QA directory."""
    # Normalize path separators
    normalized = filename.replace("\\", "/")
    return any(normalized.startswith(allowed_dir) for allowed_dir in ALLOWED_QA_DIRS)

def get_staged_files() -> List[str]:
    """Get list of files staged for commit."""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
            capture_output=True,
            text=True,
            check=True
        )
        return [f for f in result.stdout.strip().split("\n") if f]
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Git command failed: {e}")
        return []

def check_file(filepath: str) -> bool:
    """Check if a single file violates QA policy."""
    if not is_qa_test_file(filepath):
        return True  # Not a QA test file, policy doesn't apply

    if is_sot_governance_file(filepath):
        return True  # SoT governance file, exempt from policy

    if is_in_allowed_qa_dir(filepath):
        return True  # In allowed QA directory

    return False  # Policy violation

def print_violation_report(violations: List[str]):
    """Print formatted violation report."""
    print("=" * 70)
    print("❌ QA/SoT DUAL-LAYER POLICY VIOLATION")
    print("=" * 70)
    print()
    print("The following QA test files are outside the allowed QA corpus:")
    print()
    for v in violations:
        print(f"  ❌ {v}")
    print()
    print("POLICY:")
    print("  All QA test files (.py, .yaml, .yml, .rego, .json) MUST reside in:")
    print("    - 02_audit_logging/archives/qa_master_suite/")
    print()
    print("EXCEPTIONS:")
    print("  Only the 5 SoT governance artifacts are exempt:")
    for sot_file in sorted(SOT_GOVERNANCE_FILES):
        print(f"    - {sot_file}")
    print()
    print("ACTION REQUIRED:")
    print("  1. Move test files to qa_master_suite/")
    print("  2. OR remove from commit (git reset HEAD <file>)")
    print("  3. Review policy: 02_audit_logging/archives/qa_master_suite/README.md")
    print()
    print("=" * 70)
    print()

# ==============================================================================
# MAIN FUNCTIONS
# ==============================================================================

def check_staged_files() -> int:
    """Check all staged files for policy violations."""
    staged_files = get_staged_files()

    if not staged_files:
        print("No staged files to check.")
        return 0

    violations = []

    for filepath in staged_files:
        if not check_file(filepath):
            violations.append(filepath)

    if violations:
        print_violation_report(violations)
        return 1

    print(f"✅ All {len(staged_files)} staged files comply with QA/SoT policy")
    return 0

def check_single_file(filepath: str) -> int:
    """Check a single file for policy violation."""
    if check_file(filepath):
        print(f"✅ {filepath} complies with QA/SoT policy")
        return 0
    else:
        print_violation_report([filepath])
        return 1

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='SSID QA/SoT Dual-Layer Policy Enforcer',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python qa_policy_enforcer.py
  python qa_policy_enforcer.py --check-file path/to/test.py
  python qa_policy_enforcer.py --list-sot-files
        """
    )

    parser.add_argument('--check-file', metavar='PATH',
                        help='Check a single file for policy compliance')
    parser.add_argument('--list-sot-files', action='store_true',
                        help='List SoT governance files exempt from policy')
    parser.add_argument('--version', action='version', version='QA Policy Enforcer 1.0.0')

    args = parser.parse_args()

    # List SoT files
    if args.list_sot_files:
        print("SoT Governance Files (exempt from QA policy):")
        for sot_file in sorted(SOT_GOVERNANCE_FILES):
            print(f"  - {sot_file}")
        return 0

    # Check single file
    if args.check_file:
        return check_single_file(args.check_file)

    # Default: check all staged files
    return check_staged_files()

if __name__ == "__main__":
    sys.exit(main())
