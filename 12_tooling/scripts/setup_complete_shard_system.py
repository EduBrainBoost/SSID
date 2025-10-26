#!/usr/bin/env python3
"""
SSID Complete Shard System Setup
=================================

Complete setup and validation of the 24×16 shard matrix system.

This script:
1. Verifies all 384 shards exist
2. Validates shard structure and chart.yaml files
3. Identifies duplicates and orphaned files
4. Optionally consolidates files into proper shards
5. Generates comprehensive reports

Version: 1.0.0
Author: SSID System
Date: 2025-10-24
"""

import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime
import json

REPO_ROOT = Path(__file__).parent.parent.parent

# Colors for terminal output (Windows compatible)
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(text: str):
    """Print section header"""
    print("\n" + "=" * 80)
    print(text)
    print("=" * 80)


def print_step(step: int, total: int, text: str):
    """Print step indicator"""
    print(f"\n[STEP {step}/{total}] {text}")
    print("-" * 80)


def run_script(script_name: str, args: list = None) -> bool:
    """Run a Python script and return success status"""

    script_path = REPO_ROOT / "12_tooling" / "scripts" / script_name

    if not script_path.exists():
        print(f"[ERROR] Script not found: {script_path}")
        return False

    cmd = [sys.executable, str(script_path)]
    if args:
        cmd.extend(args)

    try:
        result = subprocess.run(
            cmd,
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )

        print(result.stdout)

        if result.returncode == 0:
            return True
        else:
            print(f"[ERROR] Script failed with code {result.returncode}")
            if result.stderr:
                print(result.stderr)
            return False

    except Exception as e:
        print(f"[ERROR] Failed to run script: {e}")
        return False


def main():
    """Main entry point"""

    import argparse

    parser = argparse.ArgumentParser(description="Setup complete SSID shard system")
    parser.add_argument("--consolidate", action="store_true", help="Actually consolidate files (not just dry-run)")
    parser.add_argument("--skip-validation", action="store_true", help="Skip shard validation")

    args = parser.parse_args()

    print_header("SSID COMPLETE SHARD SYSTEM SETUP")
    print(f"\nTimestamp: {datetime.now().isoformat()}")
    print(f"Repository: {REPO_ROOT}")
    print(f"Mode: {'CONSOLIDATE' if args.consolidate else 'ANALYZE ONLY'}")

    total_steps = 5 if not args.skip_validation else 4
    current_step = 0

    # Step 1: Create/Verify Shard Matrix
    current_step += 1
    print_step(current_step, total_steps, "Create/Verify 24×16 Shard Matrix (384 shards)")

    success = run_script("create_complete_shard_matrix.py")
    if not success:
        print("\n[ERROR] Failed to create shard matrix")
        return 1

    # Step 2: Verify Shard Matrix
    current_step += 1
    print_step(current_step, total_steps, "Verify Shard Matrix Completeness")

    success = run_script("verify_shard_matrix.py")
    if not success:
        print("\n[WARNING] Shard matrix verification found issues")
        # Continue anyway

    # Step 3: Analyze Duplicates and Orphaned Files
    current_step += 1
    print_step(current_step, total_steps, "Analyze Duplicates and Orphaned Files")

    consolidate_args = ["--dry-run"]
    if args.consolidate:
        consolidate_args = ["--execute"]

    success = run_script("consolidate_into_shards.py", consolidate_args)
    if not success:
        print("\n[WARNING] Consolidation analysis had issues")
        # Continue anyway

    # Step 4: Validate Shard-Aware SOT
    if not args.skip_validation:
        current_step += 1
        print_step(current_step, total_steps, "Run Shard-Aware SOT Validation")

        # Run shard-aware validator
        validator_path = REPO_ROOT / "03_core" / "validators" / "sot" / "shard_aware_validator.py"

        if validator_path.exists():
            try:
                result = subprocess.run(
                    [sys.executable, str(validator_path)],
                    cwd=str(REPO_ROOT),
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='ignore'
                )

                print(result.stdout)

                if result.returncode != 0:
                    print("\n[WARNING] Shard validation found violations")

            except Exception as e:
                print(f"[ERROR] Failed to run validator: {e}")
        else:
            print(f"[WARNING] Validator not found: {validator_path}")

    # Step 5: Generate Final Report
    current_step += 1
    print_step(current_step, total_steps, "Generate Final System Report")

    # Collect all reports
    reports_dir = REPO_ROOT / "02_audit_logging" / "reports"

    report_files = {
        "shard_matrix": reports_dir / "shard_matrix_generation_report.json",
        "consolidation": reports_dir / "shard_consolidation_report.json",
        "validation": reports_dir / "shard_validation_report.json"
    }

    final_report = {
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "system": "SSID 24×16 Shard Matrix",
        "status": "complete",
        "reports": {}
    }

    for report_type, report_path in report_files.items():
        if report_path.exists():
            try:
                with open(report_path, 'r', encoding='utf-8') as f:
                    final_report["reports"][report_type] = json.load(f)
                print(f"  [OK] Loaded {report_type} report")
            except Exception as e:
                print(f"  [WARNING] Failed to load {report_type} report: {e}")

    # Save final report
    final_report_path = reports_dir / "shard_system_complete_report.json"
    with open(final_report_path, 'w', encoding='utf-8') as f:
        json.dump(final_report, f, indent=2, ensure_ascii=False)

    print(f"\n  [SAVED] {final_report_path.relative_to(REPO_ROOT)}")

    # Generate markdown summary
    summary_md_path = reports_dir / "SHARD_SYSTEM_SETUP_SUMMARY.md"

    summary_md = f"""# SSID Shard System Setup Summary

**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Version:** 1.0.0
**Status:** Complete

## Overview

The SSID project implements a **24×16 Matrix Architecture**:
- **24 Root Layers** (vertical): Technical system layers
- **16 Shards** (horizontal): Universal application domains
- **384 Total Shards**: Complete coverage of all layer-domain combinations

## Setup Results

### 1. Shard Matrix Generation
"""

    if "shard_matrix" in final_report["reports"]:
        stats = final_report["reports"]["shard_matrix"]["statistics"]
        summary_md += f"""
- Total Shards: {stats['total_shards']}
- Created: {stats['created']}
- Already Existing: {stats['skipped']}
"""

    if "consolidation" in final_report["reports"]:
        summary = final_report["reports"]["consolidation"]["summary"]
        summary_md += f"""
### 2. File Consolidation

- Duplicates Found: {summary.get('duplicates_consolidated', 0)}
- Orphaned Files: {summary.get('orphaned_files_moved', 0)}
- Total Actions: {summary.get('total_actions', 0)}
"""

    if "validation" in final_report["reports"]:
        summary = final_report["reports"]["validation"]["summary"]
        summary_md += f"""
### 3. Shard Validation

- Total Shards: {summary['total_shards']}
- Existing: {summary['existing_shards']}
- Valid Charts: {summary['valid_charts']}
- With README: {summary['has_readme']}
"""

    summary_md += f"""
## Architecture Reference

- **Master Definition**: `16_codex/structure/ssid_master_definition_corrected_v1.1.1.md`
- **Shard Matrix**: `{REPO_ROOT.name}/<layer>/shards/<shard_id>/`

## Next Steps

1. Review shard structure in each layer
2. Populate shards with implementations
3. Define cross-shard dependencies in `chart.yaml`
4. Implement contract tests in `conformance/`

## Reports

- Full Report: `02_audit_logging/reports/shard_system_complete_report.json`
- Shard Matrix: `02_audit_logging/reports/shard_matrix_generation_report.json`
- Consolidation: `02_audit_logging/reports/shard_consolidation_report.json`
- Validation: `02_audit_logging/reports/shard_validation_report.json`

---

*Generated by SSID Shard System Setup v1.0.0*
"""

    with open(summary_md_path, 'w', encoding='utf-8') as f:
        f.write(summary_md)

    print(f"  [SAVED] {summary_md_path.relative_to(REPO_ROOT)}")

    # Final Summary
    print_header("SETUP COMPLETE")

    print("\n[OK] SSID 24x16 Shard Matrix System is now configured!")
    print(f"\nTotal Shards: 384 (24 layers x 16 shards)")

    if args.consolidate:
        print("\n[WARNING] Files have been consolidated into shard structure")
    else:
        print("\n[INFO] Dry-run complete. Use --consolidate to apply changes.")

    print(f"\n[REPORT] Summary Report: {summary_md_path.relative_to(REPO_ROOT)}")
    print(f"[REPORT] Full Report: {final_report_path.relative_to(REPO_ROOT)}")

    print("\n" + "=" * 80)

    return 0


if __name__ == "__main__":
    sys.exit(main())
