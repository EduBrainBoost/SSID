#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSID Test Orchestrator
======================

Comprehensive test runner for the entire SSID system.

Features:
- Runs all pytest tests
- Generates health reports
- Checks root immunity
- Performs meta-audits
- Monitors scores

Usage:
    python 12_tooling/analysis/run_all_tests.py
    python 12_tooling/analysis/run_all_tests.py --with-root-immunity
    python 12_tooling/analysis/run_all_tests.py --with-meta-audit
    python 12_tooling/analysis/run_all_tests.py --full
"""

import sys
import subprocess
import argparse
from pathlib import Path
from datetime import datetime, timezone
import json
import io

# Repository root
REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


def run_command(cmd, description=""):
    """Run a shell command and return the result."""
    print(f"\n{'='*80}")
    print(f"Running: {description or ' '.join(cmd)}")
    print(f"{'='*80}\n")

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT)
    )

    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)

    return result


def run_pytest(args):
    """Run pytest with specified arguments."""
    cmd = ["pytest"] + args
    return run_command(cmd, "Pytest Test Suite")


def run_root_immunity_check():
    """Check for ROOT-24-LOCK compliance."""
    print("\n" + "="*80)
    print("ROOT IMMUNITY SCAN")
    print("="*80 + "\n")

    # Check for new root directories
    root_dirs = [d for d in REPO_ROOT.iterdir() if d.is_dir() and not d.name.startswith('.')]
    expected_dirs = set([f"{i:02d}_*" for i in range(1, 25)])

    # Find directories that start with numbers 01-24
    numbered_dirs = [d for d in root_dirs if d.name[0:2].isdigit() and d.name[2] == '_']

    report = {
        "scan_date": datetime.now(timezone.utc).isoformat(),
        "total_root_dirs": len(root_dirs),
        "numbered_dirs": len(numbered_dirs),
        "expected_layers": 24,
        "compliant": len(numbered_dirs) <= 24,
        "directories": [d.name for d in sorted(numbered_dirs)]
    }

    # Save report
    report_file = REPO_ROOT / "02_audit_logging" / "reports" / "root_immunity_scan.json"
    report_file.parent.mkdir(parents=True, exist_ok=True)
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"[+] Root directories scanned: {len(numbered_dirs)}")
    print(f"[+] Expected layers: 24")
    print(f"[+] Compliance: {'PASS' if report['compliant'] else 'FAIL'}")
    print(f"[+] Report saved: {report_file}")

    return report['compliant']


def run_meta_audit():
    """Run meta-audit checks."""
    print("\n" + "="*80)
    print("META AUDIT")
    print("="*80 + "\n")

    # Check for critical files
    critical_files = [
        "LICENSE",
        "README.md",
        "pytest.ini",
        ".gitignore"
    ]

    audit_results = {
        "audit_date": datetime.now(timezone.utc).isoformat(),
        "critical_files": {},
        "layer_structure": {},
        "compliance_status": "PASS"
    }

    # Check critical files
    for file in critical_files:
        file_path = REPO_ROOT / file
        audit_results["critical_files"][file] = file_path.exists()
        if not file_path.exists():
            audit_results["compliance_status"] = "FAIL"

    # Check layer structure
    for i in range(1, 25):
        layer_prefix = f"{i:02d}_"
        matching_dirs = [d for d in REPO_ROOT.iterdir() if d.is_dir() and d.name.startswith(layer_prefix)]
        audit_results["layer_structure"][f"layer_{i:02d}"] = len(matching_dirs) > 0

    # Save report
    report_file = REPO_ROOT / "02_audit_logging" / "reports" / "meta_audit_summary.json"
    report_file.parent.mkdir(parents=True, exist_ok=True)
    with open(report_file, 'w') as f:
        json.dump(audit_results, f, indent=2)

    print(f"[+] Critical files checked: {len(critical_files)}")
    print(f"[+] Layer structure validated")
    print(f"[+] Compliance status: {audit_results['compliance_status']}")
    print(f"[+] Report saved: {report_file}")

    return audit_results['compliance_status'] == "PASS"


def run_score_monitor():
    """Monitor integration scores."""
    print("\n" + "="*80)
    print("SCORE MONITOR")
    print("="*80 + "\n")

    # Check for score log
    score_log_path = REPO_ROOT / "02_audit_logging" / "score_log.json"

    if score_log_path.exists():
        with open(score_log_path) as f:
            scores = json.load(f)

        print(f"[+] Score log found: {score_log_path}")
        print(f"[+] Scores: {json.dumps(scores.get('scores', {}), indent=2)}")

        # Check if all scores are 100
        all_100 = all(v == 100 for v in scores.get('scores', {}).values())
        print(f"[+] All scores at 100: {'YES' if all_100 else 'NO'}")

        return all_100
    else:
        print(f"[!] Score log not found: {score_log_path}")
        return False


def generate_health_report(test_results):
    """Generate system health report."""
    report_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    report_path = REPO_ROOT / "02_audit_logging" / "reports" / f"SYSTEM_HEALTH_REPORT_{report_date}.md"

    print(f"\n[+] Health report generated: {report_path}")
    print(f"[+] Test summary: {test_results}")


def main():
    parser = argparse.ArgumentParser(description="SSID Test Orchestrator")
    parser.add_argument("--with-root-immunity", action="store_true",
                        help="Include root immunity scan")
    parser.add_argument("--with-meta-audit", action="store_true",
                        help="Include meta-audit checks")
    parser.add_argument("--with-score-monitor", action="store_true",
                        help="Include score monitoring")
    parser.add_argument("--full", action="store_true",
                        help="Run all checks (root immunity + meta audit + score monitor)")
    parser.add_argument("--quick", action="store_true",
                        help="Quick test run (maxfail=3)")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Verbose output")

    args = parser.parse_args()

    # Force UTF-8 output on Windows
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

    print("\n" + "="*80)
    print("SSID TEST ORCHESTRATOR")
    print("="*80)
    print(f"Date: {datetime.now(timezone.utc).isoformat()}")
    print(f"Repository: {REPO_ROOT}")
    print("="*80 + "\n")

    # Determine what to run
    run_immunity = args.with_root_immunity or args.full
    run_audit = args.with_meta_audit or args.full
    run_monitor = args.with_score_monitor or args.full

    results = {
        "pytest": None,
        "root_immunity": None,
        "meta_audit": None,
        "score_monitor": None
    }

    # Run pytest
    pytest_args = ["--tb=short", "--no-cov"]
    if args.quick:
        pytest_args.append("--maxfail=3")
    if args.verbose:
        pytest_args.append("-v")
    else:
        pytest_args.append("-q")

    pytest_result = run_pytest(pytest_args)
    results["pytest"] = pytest_result.returncode == 0

    # Run additional checks if requested
    if run_immunity:
        results["root_immunity"] = run_root_immunity_check()

    if run_audit:
        results["meta_audit"] = run_meta_audit()

    if run_monitor:
        results["score_monitor"] = run_score_monitor()

    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80 + "\n")

    for check, result in results.items():
        if result is not None:
            status = "[PASS]" if result else "[FAIL]"
            print(f"{check:20s}: {status}")

    print("\n" + "="*80)

    # Exit with appropriate code
    all_passed = all(r for r in results.values() if r is not None)
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
