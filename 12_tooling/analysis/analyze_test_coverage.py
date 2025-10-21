#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Coverage Analyzer - Find all tests and compare with pytest discovery

Analyzes:
- All test files in repository
- Pytest collected tests
- Missing/non-integrated tests
- Test distribution across layers
"""

import json
import subprocess
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timezone

REPO_ROOT = Path(__file__).parent.parent.parent


def find_all_test_files():
    """Find all test files in repository."""
    test_files = []

    # Find test_*.py files
    for pattern in ["test_*.py", "*_test.py"]:
        test_files.extend(REPO_ROOT.rglob(pattern))

    # Exclude __pycache__ and .git
    test_files = [
        f for f in test_files
        if '__pycache__' not in str(f) and '.git' not in str(f)
    ]

    return sorted(test_files)


def get_pytest_collected_tests():
    """Get all tests collected by pytest."""
    result = subprocess.run(
        ["pytest", "--collect-only", "--no-cov", "-q"],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT
    )

    collected = []
    for line in result.stdout.split('\n'):
        if '<Function' in line or '<Method' in line:
            # Extract test function name
            if 'test_' in line:
                collected.append(line.strip())

    # Also get summary
    summary_line = [l for l in result.stdout.split('\n') if 'tests collected' in l]
    total_collected = 0
    if summary_line:
        try:
            total_collected = int(summary_line[0].split()[0])
        except:
            pass

    return collected, total_collected


def categorize_by_layer(test_files):
    """Categorize test files by layer."""
    by_layer = defaultdict(list)
    by_category = defaultdict(list)

    for test_file in test_files:
        path_str = str(test_file.relative_to(REPO_ROOT))

        # Extract layer number
        parts = path_str.split('/')
        if parts[0].startswith('11_test_simulation'):
            # In test directory
            if len(parts) > 1:
                category = parts[1]
                by_category[category].append(test_file)
            by_layer['11_test_simulation'].append(test_file)
        else:
            # Other layers
            layer = parts[0] if parts else 'root'
            by_layer[layer].append(test_file)

    return dict(by_layer), dict(by_category)


def check_pytest_discovery(test_file):
    """Check if a test file is discovered by pytest."""
    try:
        result = subprocess.run(
            ["pytest", "--collect-only", "--no-cov", "-q", str(test_file)],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            timeout=5
        )

        # Check if any tests collected
        if 'tests collected' in result.stdout or 'test collected' in result.stdout:
            return True, None
        elif 'no tests ran' in result.stdout.lower() or result.stdout.strip() == '':
            return False, "No tests found"
        else:
            return False, "Collection failed"

    except subprocess.TimeoutExpired:
        return False, "Timeout"
    except Exception as e:
        return False, str(e)


def main():
    """Main analysis."""
    print("=" * 80)
    print("TEST COVERAGE ANALYZER")
    print("=" * 80)
    print()

    # Find all test files
    print("[1/5] Finding all test files...")
    all_test_files = find_all_test_files()
    print(f"      Found: {len(all_test_files)} test files")

    # Get pytest collected tests
    print("[2/5] Analyzing pytest collection...")
    collected_tests, total_collected = get_pytest_collected_tests()
    print(f"      Pytest collected: {total_collected} tests")

    # Categorize by layer
    print("[3/5] Categorizing by layer...")
    by_layer, by_category = categorize_by_layer(all_test_files)

    print(f"      Layers with tests: {len(by_layer)}")
    print(f"      Test categories: {len(by_category)}")

    # Analyze integration
    print("[4/5] Analyzing test integration...")

    # Sample check: test first 50 files for integration
    sample_size = min(50, len(all_test_files))
    integrated = 0
    not_integrated = 0

    print(f"      Checking sample of {sample_size} files...")
    for test_file in all_test_files[:sample_size]:
        discovered, reason = check_pytest_discovery(test_file)
        if discovered:
            integrated += 1
        else:
            not_integrated += 1

    integration_rate = (integrated / sample_size * 100) if sample_size > 0 else 0

    # Generate report
    print("[5/5] Generating report...")

    report = {
        "analysis_date": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "total_test_files": len(all_test_files),
            "pytest_collected_tests": total_collected,
            "layers_with_tests": len(by_layer),
            "test_categories": len(by_category),
            "sample_integration_rate": round(integration_rate, 2)
        },
        "by_layer": {
            layer: len(files) for layer, files in sorted(by_layer.items())
        },
        "by_category": {
            cat: len(files) for cat, files in sorted(by_category.items())
        },
        "top_10_layers": sorted(
            [(layer, len(files)) for layer, files in by_layer.items()],
            key=lambda x: x[1],
            reverse=True
        )[:10],
        "analysis_notes": [
            f"Found {len(all_test_files)} test files across the repository",
            f"Pytest collects {total_collected} tests from these files",
            f"Estimated {100-integration_rate:.1f}% of test files may not be integrated",
            "Possible reasons: Wrong naming, wrong location, import errors"
        ]
    }

    # Save report
    report_file = REPO_ROOT / "02_audit_logging" / "reports" / "test_coverage_analysis.json"
    report_file.parent.mkdir(parents=True, exist_ok=True)
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()
    print(f"Total test files:        {len(all_test_files)}")
    print(f"Pytest collected tests:  {total_collected}")
    print(f"Layers with tests:       {len(by_layer)}")
    print(f"Test categories:         {len(by_category)}")
    print(f"Integration rate:        {integration_rate:.1f}%")
    print()
    print("Top 5 Layers with tests:")
    for i, (layer, count) in enumerate(report['top_10_layers'][:5], 1):
        print(f"  {i}. {layer:30s} {count:4d} files")
    print()
    print(f"Report saved: {report_file}")
    print("=" * 80)

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
