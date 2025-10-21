#!/usr/bin/env python3
"""
CLI Command: check_soc2_cc1_1
==============================

Scientific Basis:
-----------------
AICPA TSC CC1.1 - Integrity and Ethical Values
COSO Principle 1

Technical Manifestation:
------------------------
Command-line interface for validating SOC2 CC1.1 compliance

Usage:
    python 12_tooling/scripts/compliance/check_soc2_cc1_1.py [--verbose] [--json] [--fail-on-warning]

Exit Codes:
    0 - Fully compliant
    1 - Compliance violations detected
    2 - Configuration error

Author: SSID Compliance Team
Version: 1.0.0
Date: 2025-10-17
"""

import sys
import argparse
import json
from pathlib import Path

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "23_compliance" / "mappings" / "soc2" / "src"))

try:
    from cc1_1_integrity_ethics import CC11IntegrityEthicsValidator
except ImportError as e:
    print(f"ERROR: Cannot import CC1.1 validator module: {e}", file=sys.stderr)
    print("Ensure 23_compliance/mappings/soc2/src/cc1_1_integrity_ethics.py exists", file=sys.stderr)
    sys.exit(2)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="SOC2 CC1.1 - Integrity & Ethical Values Compliance Check",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic check
  python check_soc2_cc1_1.py

  # Verbose output
  python check_soc2_cc1_1.py --verbose

  # JSON output for CI/CD integration
  python check_soc2_cc1_1.py --json

  # Fail on warnings (strict mode)
  python check_soc2_cc1_1.py --fail-on-warning

Exit Codes:
  0 = Fully compliant
  1 = Violations detected
  2 = Configuration/runtime error
        """
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output with detailed findings"
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results in JSON format (for CI/CD integration)"
    )

    parser.add_argument(
        "--fail-on-warning",
        action="store_true",
        help="Treat warnings as failures (strict mode)"
    )

    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="Repository root path (default: current directory)"
    )

    args = parser.parse_args()

    # Initialize validator
    try:
        repo_root = args.repo_root or Path.cwd()
        validator = CC11IntegrityEthicsValidator(repo_root=repo_root)
    except Exception as e:
        print(f"ERROR: Failed to initialize validator: {e}", file=sys.stderr)
        return 2

    # Run validation
    try:
        is_compliant, findings = validator.validate()
    except Exception as e:
        print(f"ERROR: Validation failed with exception: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 2

    # Generate evidence hash
    evidence_hash = validator.generate_evidence_hash()

    # Determine exit code
    exit_code = 0 if is_compliant else 1

    # Check fail-on-warning mode
    if args.fail_on_warning and not is_compliant:
        has_warnings = any(f.get("severity") == "WARNING" for f in findings)
        if has_warnings:
            exit_code = 1

    # Output results
    if args.json:
        # JSON output
        output = {
            "rule": "SOC2_CC1.1",
            "rule_name": "Integrity and Ethical Values",
            "is_compliant": is_compliant,
            "exit_code": exit_code,
            "evidence_hash": evidence_hash,
            "findings": findings,
            "summary": {
                "total_findings": len(findings),
                "critical": sum(1 for f in findings if f.get("severity") == "CRITICAL"),
                "high": sum(1 for f in findings if f.get("severity") == "HIGH"),
                "medium": sum(1 for f in findings if f.get("severity") == "MEDIUM"),
                "low": sum(1 for f in findings if f.get("severity") == "LOW"),
                "info": sum(1 for f in findings if f.get("severity") == "INFO"),
                "warnings": sum(1 for f in findings if f.get("severity") == "WARNING")
            }
        }
        print(json.dumps(output, indent=2))
    else:
        # Human-readable output
        print(f"\n{'='*80}")
        print(f"SOC2 CC1.1 - Integrity & Ethical Values Validation")
        print(f"{'='*80}\n")

        # Group findings by severity
        severity_order = ["CRITICAL", "HIGH", "MEDIUM", "LOW", "WARNING", "INFO"]
        findings_by_severity = {s: [] for s in severity_order}

        for finding in findings:
            sev = finding.get("severity", "INFO")
            findings_by_severity[sev].append(finding)

        # Print findings by severity
        for severity in severity_order:
            severity_findings = findings_by_severity[severity]
            if not severity_findings:
                continue

            print(f"\n{severity} Findings ({len(severity_findings)}):")
            print("-" * 80)

            for finding in severity_findings:
                icon = "✓" if finding.get("status") == "PASS" else "✗" if severity in ["CRITICAL", "HIGH"] else "⚠"

                if args.verbose:
                    print(f"\n{icon} [{severity}] {finding.get('finding')}")
                    if "path" in finding:
                        print(f"  Path: {finding['path']}")
                    if "remediation" in finding:
                        print(f"  Remediation: {finding['remediation']}")
                else:
                    print(f"{icon} {finding.get('finding')}")

        # Summary
        print(f"\n{'='*80}")
        print(f"Summary:")
        print(f"  Total Findings: {len(findings)}")
        print(f"  Critical: {findings_by_severity['CRITICAL'].__len__()}")
        print(f"  High: {findings_by_severity['HIGH'].__len__()}")
        print(f"  Warnings: {findings_by_severity['WARNING'].__len__()}")
        print(f"\nOverall Compliance: {'PASS ✓' if is_compliant else 'FAIL ✗'}")
        print(f"Evidence Hash: {evidence_hash}")
        print(f"Exit Code: {exit_code}")
        print(f"{'='*80}\n")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
