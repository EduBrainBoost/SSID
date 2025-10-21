#!/usr/bin/env python3
"""
Pytest Runner for CI v5.2
Executes pytest suite with JSON reporting and threshold checking.
"""
import argparse
import subprocess
import sys
import pathlib
import json

def main():
    ap = argparse.ArgumentParser(
        description="Pytest Runner - Execute pricing policy tests with JSON report"
    )
    ap.add_argument("--test-file", help="Path to test file (default: test_pricing_policy_v5_2.py)")
    ap.add_argument("--output-json", help="Output path for JSON report")
    ap.add_argument("--report", help="Output path for JSON report (legacy)")
    ap.add_argument("--fail-threshold", type=float, default=0.85,
                    help="Minimum pass rate threshold (0.0-1.0)")
    args = ap.parse_args()

    # Support both old and new argument names
    test_file = args.test_file or "11_test_simulation/tests/test_pricing_policy_v5_2.py"
    output_json = args.output_json or args.report

    if not output_json:
        print("[PYTEST] Error: --output-json or --report required", file=sys.stderr)
        return 1

    out = pathlib.Path(output_json)
    out.parent.mkdir(parents=True, exist_ok=True)

    print(f"[PYTEST] Running tests from: {test_file}")
    print(f"[PYTEST] Fail threshold: {args.fail_threshold:.2%}")

    cmd = [
        "pytest",
        "-v",
        test_file,
        "--json-report",
        "--json-report-file", str(out),
        "--tb=short"
    ]

    proc = subprocess.run(cmd, capture_output=True, text=True)

    # Try to load and analyze the JSON report
    try:
        if out.exists():
            report_data = json.loads(out.read_text())
            summary = report_data.get("summary", {})
            passed = summary.get("passed", 0)
            failed = summary.get("failed", 0)
            total = summary.get("total", 0)

            if total > 0:
                pass_rate = passed / total
                print(f"\n[PYTEST] Results: {passed}/{total} passed ({pass_rate:.2%})")

                if pass_rate < args.fail_threshold:
                    print(f"[PYTEST] FAILED: Pass rate {pass_rate:.2%} below threshold {args.fail_threshold:.2%}",
                          file=sys.stderr)
                    return 1
            else:
                print("[PYTEST] WARNING: No tests found", file=sys.stderr)
    except Exception as e:
        print(f"[PYTEST] Warning: Could not parse JSON report: {e}", file=sys.stderr)

    if proc.returncode == 0:
        print(f"[PYTEST] PASSED - Report: {output_json}")
        return 0
    else:
        print(f"[PYTEST] FAILED - Report: {output_json}", file=sys.stderr)
        print(proc.stdout)
        print(proc.stderr, file=sys.stderr)
        return proc.returncode

if __name__ == "__main__":
    sys.exit(main())
