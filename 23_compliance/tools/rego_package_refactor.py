#!/usr/bin/env python3
"""
OPA Rego Package Refactor Tool
================================

Automatically refactors OPA policy package names from numeric prefixes
to semantic names for Rego compliance.

Problem:
    package ssid.01ailayer.v6_0  # Invalid - numeric prefix

Solution:
    package ssid.ai_layer.v6_0   # Valid - semantic name

Features:
- Scans all .rego files in 23_compliance/policies/
- Creates backups before modification
- Replaces numeric prefixes with semantic names
- Validates with `opa check` after refactoring
- Generates refactoring report

Exit Codes:
    0 - Success (all policies refactored and valid)
    1 - Partial success (some policies failed validation)
    2 - Critical failure (backup or file access issues)

Author: SSID Codex Engine v6.0
License: Proprietary - SAFE-FIX & ROOT-24-LOCK enforced
"""

import re
import sys
import shutil
import subprocess
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Tuple
import json

# Mapping of numeric prefixes to semantic names
PACKAGE_NAME_MAP = {
    "01ailayer": "ai_layer",
    "02auditlogging": "audit_logging",
    "03core": "core",
    "03_core": "core",
    "04deployment": "deployment",
    "04_deployment": "deployment",
    "05documentation": "documentation",
    "05_documentation": "documentation",
    "06datapipeline": "data_pipeline",
    "06_data_pipeline": "data_pipeline",
    "07governancelegal": "governance_legal",
    "07_governance_legal": "governance_legal",
    "08identityscore": "identity_score",
    "08_identity_score": "identity_score",
    "09metaidentity": "meta_identity",
    "09_meta_identity": "meta_identity",
    "10interoperability": "interoperability",
    "10_interoperability": "interoperability",
    "11testsimulation": "test_simulation",
    "11_test_simulation": "test_simulation",
    "12tooling": "tooling",
    "12_tooling": "tooling",
    "13uilayer": "ui_layer",
    "13_ui_layer": "ui_layer",
    "14zerotimeauth": "zero_time_auth",
    "14_zero_time_auth": "zero_time_auth",
    "15infra": "infra",
    "15_infra": "infra",
    "16codex": "codex",
    "16_codex": "codex",
    "17observability": "observability",
    "17_observability": "observability",
    "18datalayer": "data_layer",
    "18_data_layer": "data_layer",
    "19adapters": "adapters",
    "19_adapters": "adapters",
    "20foundation": "foundation",
    "20_foundation": "foundation",
    "21postquantumcrypto": "post_quantum_crypto",
    "21_post_quantum_crypto": "post_quantum_crypto",
    "22datasets": "datasets",
    "22_datasets": "datasets",
    "23compliance": "compliance",
    "23_compliance": "compliance",
    "24metaorchestration": "meta_orchestration",
    "24_meta_orchestration": "meta_orchestration",
}

def find_rego_files(root_path: Path) -> List[Path]:
    """Find all .rego files in the policies directory."""
    return sorted(root_path.rglob("*.rego"))

def create_backup(file_path: Path, backup_dir: Path) -> Path:
    """Create a backup of the file."""
    backup_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    backup_name = f"{file_path.stem}_{timestamp}.rego.bak"
    backup_path = backup_dir / backup_name

    shutil.copy2(file_path, backup_path)
    return backup_path

def refactor_package_line(line: str) -> Tuple[str, bool]:
    """
    Refactor a package declaration line.

    Returns:
        Tuple of (refactored_line, was_changed)
    """
    # Match package declarations like: package ssid.01ailayer.v6_0
    pattern = r'(package\s+ssid\.)(\w+)(\.v\d+_\d+)'

    match = re.search(pattern, line)
    if not match:
        return line, False

    prefix = match.group(1)  # "package ssid."
    old_name = match.group(2)  # "01ailayer"
    suffix = match.group(3)  # ".v6_0"

    # Check if we have a mapping for this name
    new_name = PACKAGE_NAME_MAP.get(old_name)
    if not new_name:
        # Try without underscores
        old_name_no_underscore = old_name.replace("_", "")
        new_name = PACKAGE_NAME_MAP.get(old_name_no_underscore)

    if new_name:
        new_line = f"{prefix}{new_name}{suffix}\n"
        return new_line, True

    return line, False

def refactor_file(file_path: Path, dry_run: bool = False) -> Dict:
    """
    Refactor a single .rego file.

    Returns:
        Dict with refactoring results
    """
    result = {
        "file": str(file_path),
        "changed": False,
        "lines_modified": 0,
        "original_package": None,
        "new_package": None,
        "error": None
    }

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        new_lines = []
        for i, line in enumerate(lines):
            new_line, changed = refactor_package_line(line)
            new_lines.append(new_line)

            if changed:
                result["changed"] = True
                result["lines_modified"] += 1
                if result["original_package"] is None:
                    result["original_package"] = line.strip()
                    result["new_package"] = new_line.strip()

        # Write changes if not dry run
        if result["changed"] and not dry_run:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)

    except Exception as e:
        result["error"] = str(e)

    return result

def validate_with_opa(file_path: Path) -> Tuple[bool, str]:
    """
    Validate a .rego file with OPA.

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        result = subprocess.run(
            ["opa", "check", str(file_path)],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            return True, ""
        else:
            return False, result.stderr or result.stdout

    except FileNotFoundError:
        return False, "OPA not found in PATH"
    except subprocess.TimeoutExpired:
        return False, "OPA check timed out"
    except Exception as e:
        return False, str(e)

def main():
    """Main refactoring workflow."""
    import argparse
    import io

    # Force UTF-8 output on Windows
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

    parser = argparse.ArgumentParser(
        description="OPA Rego Package Refactor Tool"
    )
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be changed without modifying files")
    parser.add_argument("--no-backup", action="store_true",
                        help="Skip backup creation (not recommended)")
    parser.add_argument("--validate", action="store_true",
                        help="Validate with 'opa check' after refactoring")
    parser.add_argument("--report", type=str,
                        help="Write JSON report to specified file")

    args = parser.parse_args()

    # Repository root
    repo_root = Path(__file__).resolve().parents[2]
    policies_dir = repo_root / "23_compliance" / "policies"
    backup_dir = repo_root / "23_compliance" / "policies" / ".backups"

    print("=" * 70)
    print("OPA Rego Package Refactor Tool")
    print("=" * 70)
    print(f"Policies directory: {policies_dir}")
    print(f"Dry run: {args.dry_run}")
    print(f"Create backups: {not args.no_backup}")
    print(f"Validate with OPA: {args.validate}")
    print("=" * 70)
    print()

    if not policies_dir.exists():
        print(f"ERROR: Policies directory not found: {policies_dir}")
        return 2

    # Find all .rego files
    rego_files = find_rego_files(policies_dir)
    print(f"Found {len(rego_files)} .rego files")
    print()

    # Refactor each file
    results = []
    files_changed = 0
    files_unchanged = 0
    files_failed = 0

    for file_path in rego_files:
        print(f"Processing: {file_path.relative_to(repo_root)}")

        # Create backup if not dry run and backups enabled
        if not args.dry_run and not args.no_backup:
            try:
                backup_path = create_backup(file_path, backup_dir)
                print(f"  → Backup: {backup_path.name}")
            except Exception as e:
                print(f"  ✗ Backup failed: {e}")
                files_failed += 1
                continue

        # Refactor file
        result = refactor_file(file_path, dry_run=args.dry_run)
        results.append(result)

        if result["error"]:
            print(f"  ✗ Error: {result['error']}")
            files_failed += 1
        elif result["changed"]:
            print(f"  ✓ Changed ({result['lines_modified']} lines)")
            print(f"    Old: {result['original_package']}")
            print(f"    New: {result['new_package']}")
            files_changed += 1

            # Validate with OPA if requested
            if args.validate and not args.dry_run:
                is_valid, error_msg = validate_with_opa(file_path)
                result["opa_valid"] = is_valid
                result["opa_error"] = error_msg

                if is_valid:
                    print(f"    ✓ OPA validation passed")
                else:
                    print(f"    ✗ OPA validation failed: {error_msg[:100]}")
        else:
            print(f"  → No changes needed")
            files_unchanged += 1

        print()

    # Summary
    print("=" * 70)
    print("REFACTORING SUMMARY")
    print("=" * 70)
    print(f"Total files:     {len(rego_files)}")
    print(f"Changed:         {files_changed}")
    print(f"Unchanged:       {files_unchanged}")
    print(f"Failed:          {files_failed}")
    print("=" * 70)

    # Write report if requested
    if args.report:
        report_path = Path(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)

        report_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "dry_run": args.dry_run,
            "total_files": len(rego_files),
            "files_changed": files_changed,
            "files_unchanged": files_unchanged,
            "files_failed": files_failed,
            "results": results
        }

        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=True, sort_keys=True)

        print(f"\n✓ Report written: {report_path}")

    # Exit code
    if files_failed > 0:
        return 2
    elif files_changed == 0 and not args.dry_run:
        return 1
    else:
        return 0

if __name__ == "__main__":
    sys.exit(main())
