#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SoT CLI (Autopilot Mode)
========================

Version: 4.0.0
Status: PRODUCTION

Lightweight CLI for automated validation and monitoring.
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

# UTF-8 enforcement
if sys.platform == 'win32':
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / '03_core' / 'validators' / 'sot'))

from sot_validator_engine import RuleValidationEngine


def validate_all():
    """Validate all rules using real engine"""
    print("="*60)
    print("SoT Validation (Autopilot Mode)")
    print("="*60)

    try:
        # Initialize engine
        engine = RuleValidationEngine(repo_root=REPO_ROOT)
        print(f"Loaded {len(engine.registry.rules)} rules")

        # Run validation
        report = engine.validate_all()

        # Print results
        print()
        print(f"Results:")
        print(f"  Total:    {report.total_rules}")
        print(f"  Passed:   {report.passed}")
        print(f"  Failed:   {report.failed}")
        print(f"  Warnings: {report.warnings}")
        print(f"  Score:    {report.overall_score:.1f}%")

        # Save brief report
        reports_dir = REPO_ROOT / '02_audit_logging' / 'reports'
        reports_dir.mkdir(parents=True, exist_ok=True)

        report_file = reports_dir / 'autopilot_validation.json'
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'total': report.total_rules,
            'passed': report.passed,
            'failed': report.failed,
            'score': report.overall_score,
            'status': 'PASS' if report.overall_score >= 95.0 else 'FAIL'
        }
        report_file.write_text(json.dumps(report_data, indent=2))

        print(f"\n✅ Report saved: {report_file.name}")

        return 0 if report.failed == 0 else 1

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 2


def show_scorecard():
    """Display current scorecard from latest reports"""
    print("="*60)
    print("SoT Scorecard")
    print("="*60)

    reports_dir = REPO_ROOT / '02_audit_logging' / 'reports'

    # Try to load latest validation report
    report_file = reports_dir / 'validation_report.json'
    autopilot_file = reports_dir / 'autopilot_validation.json'

    if report_file.exists():
        with open(report_file) as f:
            data = json.load(f)
        print(f"\nValidation:")
        print(f"  Total Rules: {data.get('total', 'N/A')}")
        print(f"  Passed:      {data.get('passed', 'N/A')}")
        print(f"  Score:       {data.get('score', 0):.1f}%")
    elif autopilot_file.exists():
        with open(autopilot_file) as f:
            data = json.load(f)
        print(f"\nAutopilot Validation:")
        print(f"  Total Rules: {data.get('total', 'N/A')}")
        print(f"  Passed:      {data.get('passed', 'N/A')}")
        print(f"  Score:       {data.get('score', 0):.1f}%")
        print(f"  Status:      {data.get('status', 'UNKNOWN')}")
    else:
        print("\n⚠️  No validation reports found. Run 'validate' first.")
        return 1

    # Check completeness
    completeness_file = reports_dir / 'completeness_report_integrated.json'
    if completeness_file.exists():
        with open(completeness_file) as f:
            comp = json.load(f)
        print(f"\nCompleteness:")
        print(f"  Score: {comp.get('average_completeness', 0):.1f}%")

    print()
    return 0


def health_check():
    """Quick health check"""
    print("="*60)
    print("System Health Check")
    print("="*60)

    checks = {
        'Registry': REPO_ROOT / '16_codex/structure/auto_generated/sot_rules_full.json',
        'Contract': REPO_ROOT / '16_codex/contracts/sot/sot_contract.yaml',
        'Policy': REPO_ROOT / '23_compliance/policies/sot',
        'Validator': REPO_ROOT / '03_core/validators/sot/sot_validator_engine.py',
    }

    all_pass = True
    for name, path in checks.items():
        if path.exists():
            print(f"  ✅ {name}")
        else:
            print(f"  ❌ {name}")
            all_pass = False

    if all_pass:
        print("\n✅ All systems operational")
        return 0
    else:
        print("\n⚠️  Some systems missing")
        return 1


def main():
    parser = argparse.ArgumentParser(
        description="SSID SoT CLI (Autopilot Mode)",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "command",
        choices=["validate", "scorecard", "health"],
        help="Command to execute"
    )

    args = parser.parse_args()

    if args.command == "validate":
        return validate_all()
    elif args.command == "scorecard":
        return show_scorecard()
    elif args.command == "health":
        return health_check()


if __name__ == "__main__":
    sys.exit(main())
