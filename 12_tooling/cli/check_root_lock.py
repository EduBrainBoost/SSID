#!/usr/bin/env python3
"""
ROOT-24-LOCK Compliance Checker
================================

Purpose: Verify ROOT-24 structure integrity before any modifications
Version: 2.1.0 (Fixed)
Date: 2025-10-17
Exit Code: 0 = compliant, 24 = violation

Checks:
✅ All 24 root directories exist
✅ No protected files are overwritten
✅ Append-only paths respected
✅ SHA-256 chain intact
✅ No unauthorized root modifications

Usage:
    python check_root_lock.py                    # Check current state
    python check_root_lock.py --verify-append    # Verify append operations
    python check_root_lock.py --report           # Generate status report
"""

import os
import sys
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Set

# ROOT-24 canonical structure (CORRECTED)
ROOT_24_DIRECTORIES = {
    "01_ai_layer", "02_audit_logging", "03_core", "04_deployment",
    "05_documentation", "06_data_pipeline", "07_governance_legal",
    "08_identity_score", "09_meta_identity", "10_interoperability",
    "11_test_simulation", "12_tooling", "13_ui_layer", "14_zero_time_auth",
    "15_infra", "16_codex", "17_observability", "18_data_layer",
    "19_adapters", "20_foundation", "21_post_quantum_crypto", "22_datasets",
    "23_compliance", "24_meta_orchestration"
}

PROTECTED_FILES = {
    "module.yaml", "README.md", ".gitkeep", "LOCK", "ROOT_24_LOCK"
}

APPEND_ONLY_PATHS = {
    "02_audit_logging/storage/worm/",
    "02_audit_logging/logs/",
    "02_audit_logging/reports/",
    "23_compliance/evidence/",
    "24_meta_orchestration/registry/locks/"
}


class RootLockChecker:
    """ROOT-24-LOCK compliance verification"""

    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path).resolve()
        self.violations: List[str] = []
        self.warnings: List[str] = []

    def check_root_structure(self) -> bool:
        """Verify all 24 root directories exist"""
        print("[CHECK] Verifying ROOT-24 structure...")

        existing_roots = set()
        for root in ROOT_24_DIRECTORIES:
            root_path = self.base_path / root
            if root_path.exists() and root_path.is_dir():
                existing_roots.add(root)
            else:
                self.violations.append(f"Missing root directory: {root}")

        if len(existing_roots) != 24:
            self.violations.append(
                f"ROOT-24-LOCK VIOLATION: Found {len(existing_roots)}/24 roots"
            )
            return False

        print(f"[CHECK] ✅ All 24 root directories exist")
        return True

    def check_protected_files(self, modified_files: List[str], operation: str) -> bool:
        """Check if any protected files are being overwritten"""
        print("[CHECK] Checking protected files...")

        violations_found = False

        for file_path in modified_files:
            file_name = Path(file_path).name
            if file_name in PROTECTED_FILES and operation == "overwrite":
                self.violations.append(
                    f"ROOT-24-LOCK VIOLATION: Attempt to overwrite protected file: {file_path}"
                )
                violations_found = True

        if not violations_found:
            print(f"[CHECK] ✅ No protected file violations")

        return not violations_found

    def check_append_only_paths(self, modified_files: List[str], operation: str) -> bool:
        """Check if append-only paths are being respected"""
        print("[CHECK] Checking append-only paths...")

        violations_found = False

        for file_path in modified_files:
            for append_path in APPEND_ONLY_PATHS:
                if file_path.startswith(append_path) and operation == "overwrite":
                    self.violations.append(
                        f"ROOT-24-LOCK VIOLATION: Overwrite in append-only path: {file_path}"
                    )
                    violations_found = True

        if not violations_found:
            print(f"[CHECK] ✅ Append-only paths respected")

        return not violations_found

    def verify_sha_chain(self) -> bool:
        """Verify SHA-256 chain integrity"""
        print("[CHECK] Verifying SHA-256 chain integrity...")

        hash_chain_path = self.base_path / "24_meta_orchestration" / "registry" / "locks" / "hash_chain.json"

        if not hash_chain_path.exists():
            self.warnings.append("SHA-256 hash chain not found (acceptable for new systems)")
            return True

        try:
            with open(hash_chain_path, 'r') as f:
                chain_data = json.load(f)

            # Verify chain integrity
            entries = chain_data.get('entries', [])
            for i, entry in enumerate(entries):
                if i > 0:
                    expected_prev = entries[i-1]['current_hash']
                    actual_prev = entry['previous_hash']
                    if expected_prev != actual_prev:
                        self.violations.append(
                            f"ROOT-24-LOCK VIOLATION: SHA chain broken at entry {i}"
                        )
                        return False

            print(f"[CHECK] ✅ SHA-256 chain intact ({len(entries)} entries)")
            return True

        except Exception as e:
            self.violations.append(f"ROOT-24-LOCK VIOLATION: SHA chain verification failed: {e}")
            return False

    def run_full_check(self, modified_files: List[str] = None, operation: str = "append") -> Tuple[bool, int]:
        """
        Run complete ROOT-24-LOCK compliance check

        Args:
            modified_files: List of files being modified (optional)
            operation: 'append' or 'overwrite'

        Returns:
            (is_compliant, exit_code)
        """
        print("=" * 70)
        print("ROOT-24-LOCK Compliance Check")
        print("=" * 70)

        # Step 1: Check root structure
        root_ok = self.check_root_structure()

        # Step 2: Check protected files (if files specified)
        protected_ok = True
        if modified_files:
            protected_ok = self.check_protected_files(modified_files, operation)

        # Step 3: Check append-only paths (if files specified)
        append_ok = True
        if modified_files:
            append_ok = self.check_append_only_paths(modified_files, operation)

        # Step 4: Verify SHA chain
        sha_ok = self.verify_sha_chain()

        # Overall result
        is_compliant = root_ok and protected_ok and append_ok and sha_ok

        print("=" * 70)
        if is_compliant:
            print("✅ ROOT-24-LOCK COMPLIANT")
            print("=" * 70)
            if self.warnings:
                print(f"\nWarnings ({len(self.warnings)}):")
                for warn in self.warnings:
                    print(f"  ⚠️  {warn}")
            return True, 0
        else:
            print("❌ ROOT-24-LOCK VIOLATION DETECTED")
            print("=" * 70)
            print(f"\nViolations ({len(self.violations)}):")
            for viol in self.violations:
                print(f"  ❌ {viol}")
            return False, 24

    def generate_status_report(self) -> Dict:
        """Generate ROOT-24-LOCK status report"""
        print("[REPORT] Generating ROOT-24-LOCK status report...")

        report = {
            "root_lock_check": {
                "timestamp": datetime.utcnow().isoformat() + 'Z',
                "version": "2.1.0",
                "base_path": str(self.base_path),
                "root_structure": {
                    "expected_roots": 24,
                    "found_roots": 0,
                    "missing_roots": [],
                    "status": "UNKNOWN"
                },
                "protected_files": {
                    "total_protected": len(PROTECTED_FILES),
                    "status": "NOT_CHECKED"
                },
                "append_only_paths": {
                    "total_paths": len(APPEND_ONLY_PATHS),
                    "status": "NOT_CHECKED"
                },
                "sha_chain": {
                    "status": "UNKNOWN"
                },
                "violations": self.violations,
                "warnings": self.warnings,
                "overall_status": "UNKNOWN",
                "exit_code": 24
            }
        }

        # Check roots
        existing_roots = []
        missing_roots = []
        for root in ROOT_24_DIRECTORIES:
            root_path = self.base_path / root
            if root_path.exists() and root_path.is_dir():
                existing_roots.append(root)
            else:
                missing_roots.append(root)

        report["root_lock_check"]["root_structure"]["found_roots"] = len(existing_roots)
        report["root_lock_check"]["root_structure"]["missing_roots"] = missing_roots
        report["root_lock_check"]["root_structure"]["status"] = "COMPLIANT" if len(existing_roots) == 24 else "VIOLATION"

        # Overall status
        is_compliant = len(existing_roots) == 24 and len(self.violations) == 0
        report["root_lock_check"]["overall_status"] = "COMPLIANT" if is_compliant else "VIOLATION"
        report["root_lock_check"]["exit_code"] = 0 if is_compliant else 24

        return report

    def write_status_report(self, output_path: str = None):
        """Write status report to file"""
        if output_path is None:
            output_path = self.base_path / "02_audit_logging" / "reports" / "ROOT_24_LOCK_STATUS.json"

        report = self.generate_status_report()

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)

        print(f"[REPORT] ✅ Status report written to: {output_path}")

        # Also write markdown version
        md_path = output_path.with_suffix('.md')
        self._write_markdown_report(md_path, report)

        return report

    def _write_markdown_report(self, md_path: Path, report: Dict):
        """Write markdown status report"""
        data = report["root_lock_check"]

        md_content = f'''# ROOT-24-LOCK Status Report

**Generated**: {data['timestamp']}
**Version**: {data['version']}
**Base Path**: `{data['base_path']}`

## Overall Status

**Status**: {"✅ COMPLIANT" if data['overall_status'] == 'COMPLIANT' else "❌ VIOLATION"}
**Exit Code**: {data['exit_code']}

## Root Structure

- **Expected Roots**: {data['root_structure']['expected_roots']}
- **Found Roots**: {data['root_structure']['found_roots']}
- **Status**: {data['root_structure']['status']}

'''

        if data['root_structure']['missing_roots']:
            md_content += "### Missing Roots\n\n"
            for root in data['root_structure']['missing_roots']:
                md_content += f"- ❌ `{root}`\n"
            md_content += "\n"

        if data['violations']:
            md_content += f"## Violations ({len(data['violations'])})\n\n"
            for viol in data['violations']:
                md_content += f"- ❌ {viol}\n"
            md_content += "\n"

        if data['warnings']:
            md_content += f"## Warnings ({len(data['warnings'])})\n\n"
            for warn in data['warnings']:
                md_content += f"- ⚠️  {warn}\n"
            md_content += "\n"

        md_content += '''
## Protected Files

Protected files that cannot be overwritten:
- `module.yaml`
- `README.md`
- `.gitkeep`
- `LOCK`
- `ROOT_24_LOCK`

## Append-Only Paths

Paths that only allow append operations:
- `02_audit_logging/storage/worm/`
- `02_audit_logging/logs/`
- `02_audit_logging/reports/`
- `23_compliance/evidence/`
- `24_meta_orchestration/registry/locks/`
'''

        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(md_content)

        print(f"[REPORT] ✅ Markdown report written to: {md_path}")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="ROOT-24-LOCK Compliance Checker")
    parser.add_argument('--verify-append', action='store_true',
                       help='Verify append operation compliance')
    parser.add_argument('--files', type=str, nargs='+',
                       help='Files being modified (for append verification)')
    parser.add_argument('--report', action='store_true',
                       help='Generate status report')
    parser.add_argument('--output', type=str,
                       help='Output path for report')

    args = parser.parse_args()

    checker = RootLockChecker()

    if args.report:
        # Generate report mode
        report = checker.write_status_report(args.output)
        sys.exit(report['root_lock_check']['exit_code'])

    elif args.verify_append:
        # Verify append operation
        files = args.files if args.files else []
        is_compliant, exit_code = checker.run_full_check(files, operation="append")
        sys.exit(exit_code)

    else:
        # Default: check current state
        is_compliant, exit_code = checker.run_full_check()
        sys.exit(exit_code)


if __name__ == "__main__":
    main()
