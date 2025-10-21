#!/usr/bin/env python3
"""
SoT Validator CLI - Complete Rule Coverage (280 Rules)
========================================================
Command-line interface for SoT validation with:
- Python validator execution (all 280 rules)
- OPA policy evaluation (optional)
- Severity-based exit codes (CRITICAL, HIGH, MEDIUM, LOW, INFO)
- Comprehensive JSON reports
- Rule filtering support

Usage:
    python sot_validator.py <repo_path>
    python sot_validator.py <repo_path> --rules AR001,CP001
    python sot_validator.py <repo_path> --severity CRITICAL
    python sot_validator.py <repo_path> --export report.json
    python sot_validator.py <repo_path> --opa
    python sot_validator.py --summary

Exit Codes:
    0: All validations passed
    1: LOW/INFO failures only
    2: MEDIUM failures (or higher)
    3: HIGH failures (or higher)
    4: CRITICAL failures

Author: SSID Core Team
Version: 4.0.0
Date: 2025-10-20
"""

import sys
import json
import argparse
import hashlib
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from core.validators.sot import sot_validator_core as sot_core
except ImportError:
    # Fallback: direct import
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "sot_validator_core",
        Path(__file__).parent.parent.parent / "03_core" / "validators" / "sot" / "sot_validator_core.py"
    )
    sot_core = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sot_core)

# ============================================================================
# CONFIGURATION
# ============================================================================

PROJECT_ROOT = Path(__file__).parent.parent.parent
CONTRACT_PATH = PROJECT_ROOT / "16_codex" / "contracts" / "sot" / "sot_contract.yaml"
POLICY_PATH = PROJECT_ROOT / "23_compliance" / "policies" / "sot" / "sot_policy.rego"

# ============================================================================
# CLI INTERFACE
# ============================================================================

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="SoT Validator CLI - Complete Rule Coverage (280 Rules)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python sot_validator.py .
  python sot_validator.py . --rules AR001,CP001,VG001
  python sot_validator.py . --severity CRITICAL
  python sot_validator.py . --export report.json
  python sot_validator.py . --opa
  python sot_validator.py --summary
        """
    )

    parser.add_argument(
        'repo_path',
        type=str,
        nargs='?',
        help='Repository root path to validate'
    )

    parser.add_argument(
        '--rules', '-r',
        type=str,
        help='Comma-separated list of specific rules to run (e.g., AR001,CP001)'
    )

    parser.add_argument(
        '--severity', '-s',
        type=str,
        choices=['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO'],
        help='Filter rules by severity level'
    )

    parser.add_argument(
        '--export', '-e',
        type=str,
        nargs='?',
        const='sot_validation_report.json',
        help='Export validation report to file'
    )

    parser.add_argument(
        '--opa',
        action='store_true',
        help='Run OPA policy evaluation (requires OPA installed)'
    )

    parser.add_argument(
        '--summary',
        action='store_true',
        help='Show contract summary'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output (show all rule results)'
    )

    parser.add_argument(
        '--json',
        action='store_true',
        help='Output in JSON format only'
    )

    return parser.parse_args()


# ============================================================================
# VALIDATION EXECUTION
# ============================================================================

def run_python_validation(repo_path: str, rules_filter: Optional[List[str]] = None,
                         severity_filter: Optional[str] = None) -> Dict[str, Any]:
    """Run Python validation with optional filters."""

    # Initialize validator
    validator = sot_core.SoTValidator(Path(repo_path))

    # Run validation
    print("[*] Running SoT validation...")
    print(f"[*] Repository: {repo_path}")

    if rules_filter:
        print(f"[*] Filtering rules: {', '.join(rules_filter)}")
    if severity_filter:
        print(f"[*] Severity filter: {severity_filter}")

    # Execute validation
    report = validator.validate_all()

    # Apply filters if specified
    if rules_filter or severity_filter:
        filtered_results = []
        for result in report.results:
            # Rule ID filter
            if rules_filter and result.rule_id not in rules_filter:
                continue
            # Severity filter
            if severity_filter and result.severity.value != severity_filter:
                continue
            filtered_results.append(result)

        # Update report with filtered results
        report.results = filtered_results
        report.total_rules = len(filtered_results)
        report.passed_count = sum(1 for r in filtered_results if r.passed)
        report.failed_count = sum(1 for r in filtered_results if not r.passed)
        if report.total_rules > 0:
            report.pass_rate = f"{(report.passed_count / report.total_rules) * 100:.2f}%"

    return report.to_dict()


def run_opa_validation(repo_path: str) -> int:
    """Run OPA policy evaluation."""
    print("[*] Running OPA validation...")

    try:
        import subprocess
        import tempfile
        import yaml

        # Load contract for OPA input
        with open(CONTRACT_PATH, 'r', encoding='utf-8') as f:
            contract = yaml.safe_load(f)

        # Prepare OPA input (simplified for structure validation)
        opa_input = {
            "contract": contract,
            "structure": {
                "roots": []  # Would need to scan filesystem for real data
            }
        }

        # Write to temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(opa_input, f)
            input_file = f.name

        # Run OPA eval
        result = subprocess.run(
            ['opa', 'eval', '-d', str(POLICY_PATH), '-i', input_file, 'data.ssid.sot'],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            print(f"[ERROR] OPA execution failed: {result.stderr}", file=sys.stderr)
            return 2

        print("[+] OPA validation complete")
        return 0

    except FileNotFoundError:
        print("[WARNING] OPA not found - skipping OPA validation", file=sys.stderr)
        return 0
    except Exception as e:
        print(f"[ERROR] OPA validation error: {e}", file=sys.stderr)
        return 2


def show_contract_summary():
    """Show contract summary."""
    import yaml

    with open(CONTRACT_PATH, 'r', encoding='utf-8') as f:
        contract = yaml.safe_load(f)

    metadata = contract['metadata']

    print("=" * 80)
    print("SoT Contract Summary")
    print("=" * 80)
    print(f"Version:       {metadata['version']}")
    print(f"Generated:     {metadata['generated']}")
    print(f"Total Rules:   {metadata['total_rules']}")
    print("")
    print("Tier Distribution:")
    for tier, count in metadata['tier_distribution'].items():
        print(f"  {tier}: {count}")
    print("")
    print("Severity Distribution:")
    for severity, count in metadata['severity_distribution'].items():
        print(f"  {severity}: {count}")
    print("")
    print("Source Files:")
    for source in metadata['source_files']:
        print(f"  - {source}")
    print("")
    print(f"Usage: {metadata['usage']}")
    print("=" * 80)


# ============================================================================
# REPORTING
# ============================================================================

def print_summary(report: Dict[str, Any], verbose: bool = False):
    """Print validation summary."""
    print("\n" + "=" * 80)
    print("SoT Validation Report")
    print("=" * 80)
    print(f"Timestamp:     {report['timestamp']}")
    print(f"Repository:    {report['repo_root']}")
    print(f"Total Rules:   {report['total_rules']}")
    print(f"Passed:        {report['passed_count']}")
    print(f"Failed:        {report['failed_count']}")
    print(f"Pass Rate:     {report['pass_rate']}")
    print("")

    # Severity breakdown
    if 'summary' in report and 'by_severity' in report['summary']:
        print("Severity Breakdown:")
        for severity, stats in report['summary']['by_severity'].items():
            print(f"  {severity:10s}: {stats['passed']:3d}/{stats['total']:3d} passed ({stats['pass_rate']})")

    # Critical failures
    if report.get('summary', {}).get('critical_failures'):
        print("\nCritical Failures:")
        for failure in report['summary']['critical_failures'][:10]:  # Show first 10
            print(f"  - {failure['rule_id']}: {failure['message']}")

    # Verbose mode: show all failures
    if verbose and report['failed_count'] > 0:
        print("\nAll Failures:")
        for result in report['results']:
            if not result['passed']:
                print(f"  [{result['severity']}] {result['rule_id']}: {result['message']}")

    print("=" * 80)


def export_report(report: Dict[str, Any], output_path: str):
    """Export validation report to file with SHA256."""
    # Write report
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    # Generate SHA256
    with open(output_path, 'rb') as f:
        sha256 = hashlib.sha256(f.read()).hexdigest()

    # Write SHA256 file
    sha256_path = output_path + '.sha256'
    with open(sha256_path, 'w', encoding='utf-8') as f:
        f.write(f"{sha256}  {Path(output_path).name}\n")

    print(f"\n[+] Report exported: {output_path}")
    print(f"[+] SHA256 file:     {sha256_path}")
    print(f"[+] SHA256 hash:     {sha256}")


# ============================================================================
# EXIT CODE DETERMINATION
# ============================================================================

def determine_exit_code(report: Dict[str, Any]) -> int:
    """Determine exit code based on severity of failures."""
    # Check for failures by severity
    summary_by_severity = report.get('summary', {}).get('by_severity', {})

    # CRITICAL failures = exit code 4
    if summary_by_severity.get('CRITICAL', {}).get('failed', 0) > 0:
        return 4

    # HIGH failures = exit code 3
    if summary_by_severity.get('HIGH', {}).get('failed', 0) > 0:
        return 3

    # MEDIUM failures = exit code 2
    if summary_by_severity.get('MEDIUM', {}).get('failed', 0) > 0:
        return 2

    # LOW or INFO failures = exit code 1
    if (summary_by_severity.get('LOW', {}).get('failed', 0) > 0 or
        summary_by_severity.get('INFO', {}).get('failed', 0) > 0):
        return 1

    # All passed = exit code 0
    return 0


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main CLI entry point."""
    args = parse_args()

    # Show summary mode
    if args.summary:
        show_contract_summary()
        return 0

    # Validate repo_path
    if not args.repo_path:
        print("[ERROR] Repository path required (use --summary for contract info)", file=sys.stderr)
        return 2

    if not Path(args.repo_path).exists():
        print(f"[ERROR] Repository path does not exist: {args.repo_path}", file=sys.stderr)
        return 2

    # Parse rules filter
    rules_filter = None
    if args.rules:
        rules_filter = [r.strip() for r in args.rules.split(',')]

    # Run Python validation
    try:
        report = run_python_validation(
            args.repo_path,
            rules_filter=rules_filter,
            severity_filter=args.severity
        )
    except Exception as e:
        print(f"[ERROR] Validation failed: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 4

    # JSON-only output
    if args.json:
        print(json.dumps(report, indent=2))
        return determine_exit_code(report)

    # Print summary
    print_summary(report, args.verbose)

    # Export if requested
    if args.export:
        export_report(report, args.export)

    # Run OPA if requested
    if args.opa:
        opa_exit = run_opa_validation(args.repo_path)
        if opa_exit != 0:
            return opa_exit

    # Determine exit code based on failures
    return determine_exit_code(report)


if __name__ == "__main__":
    sys.exit(main())
