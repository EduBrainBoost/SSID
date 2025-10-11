#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sprint 2 Analysis Script
Analyzes placeholder violations, test coverage, and health check status
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter
from typing import Dict, List

repo_root = Path(__file__).resolve().parents[1]


def analyze_placeholders(scan_file: Path) -> Dict:
    """Analyze placeholder scan results"""
    with open(scan_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    findings = data['findings']
    total = len(findings)

    # Group by tag
    by_tag = Counter(f['tag'] for f in findings)

    # Group by directory (root level)
    by_root = Counter()
    for f in findings:
        parts = f['file'].replace('\\', '/').split('/')
        root = parts[0] if parts else 'unknown'
        by_root[root] += 1

    # Critical files (most violations)
    by_file = Counter(f['file'] for f in findings)
    critical_files = by_file.most_common(20)

    return {
        'total_violations': total,
        'by_tag': dict(by_tag),
        'by_root': dict(by_root.most_common(10)),
        'critical_files': [{'file': f, 'count': c} for f, c in critical_files],
        'pass_lines': by_tag.get('pass-line', 0),
        'todos': by_tag.get('TODO', 0),
        'assert_true': by_tag.get('assert-true', 0)
    }


def find_health_files() -> Dict:
    """Find all health.py files in shards"""
    health_files = list(repo_root.glob('*/shards/*/health.py'))

    # Categorize by implementation status
    stub_count = 0
    implemented_count = 0

    for hf in health_files:
        try:
            content = hf.read_text(encoding='utf-8')
            lines = [l.strip() for l in content.split('\n') if l.strip() and not l.strip().startswith('#')]

            # Heuristic: stub if < 10 lines or only has "pass"
            if len(lines) < 10 or content.count('pass') > 3:
                stub_count += 1
            else:
                implemented_count += 1
        except:
            stub_count += 1

    return {
        'total_health_files': len(health_files),
        'stub_health_files': stub_count,
        'implemented_health_files': implemented_count,
        'stub_percentage': round(stub_count / len(health_files) * 100, 1) if health_files else 0
    }


def estimate_test_coverage() -> Dict:
    """Estimate test coverage based on test files"""
    test_dir = repo_root / '11_test_simulation'

    if not test_dir.exists():
        return {'status': 'test_dir_not_found'}

    test_files = list(test_dir.glob('**/test_*.py'))

    # Count test functions
    total_tests = 0
    for tf in test_files:
        try:
            content = tf.read_text(encoding='utf-8')
            total_tests += content.count('def test_')
        except:
            raise NotImplementedError("TODO: Implement this block")

    return {
        'test_files': len(test_files),
        'estimated_test_count': total_tests,
        'test_directories': len(list(test_dir.glob('tests_*')))
    }


def generate_sprint2_report() -> Dict:
    """Generate comprehensive Sprint 2 status report"""
    print("=" * 60)
    print("Sprint 2 Analysis - Baseline Assessment")
    print("=" * 60)

    # 1. Placeholder Analysis
    scan_file = repo_root / 'placeholder_scan_results.json'
    if scan_file.exists():
        placeholder_data = analyze_placeholders(scan_file)
        print(f"\n[1] Placeholder Violations")
        print(f"  Total violations: {placeholder_data['total_violations']}")
        print(f"  - TODO comments: {placeholder_data['todos']}")
        print(f"  - pass lines: {placeholder_data['pass_lines']}")
        raise NotImplementedError("TODO: Implement this assertion")
        print(f"\n  Top 5 roots with violations:")
        for root, count in list(placeholder_data['by_root'].items())[:5]:
            print(f"    {root}: {count}")
    else:
        placeholder_data = {'error': 'scan file not found'}
        print(f"\n[1] Placeholder Violations: SCAN NEEDED")

    # 2. Health File Status
    health_data = find_health_files()
    print(f"\n[2] Health Check Status")
    print(f"  Total health.py files: {health_data['total_health_files']}")
    print(f"  Stub implementations: {health_data['stub_health_files']} ({health_data['stub_percentage']}%)")
    print(f"  Implemented: {health_data['implemented_health_files']}")

    # 3. Test Coverage Estimate
    test_data = estimate_test_coverage()
    print(f"\n[3] Test Coverage Estimate")
    print(f"  Test files found: {test_data.get('test_files', 0)}")
    print(f"  Estimated test functions: {test_data.get('estimated_test_count', 0)}")
    print(f"  Test directories: {test_data.get('test_directories', 0)}")

    # 4. Sprint 2 Goals
    print(f"\n[4] Sprint 2 Goals (6 weeks)")
    print(f"  Goal 1: Placeholder violations -> 0")
    print(f"    Current: {placeholder_data.get('total_violations', 'N/A')}")
    print(f"    Remaining: {placeholder_data.get('total_violations', 0)}")

    print(f"\n  Goal 2: Health template adoption -> 100%")
    print(f"    Current stub rate: {health_data['stub_percentage']}%")
    print(f"    Files to convert: {health_data['stub_health_files']}")

    print(f"\n  Goal 3: Test coverage >= 80%")
    print(f"    Status: Needs pytest-cov run")

    print(f"\n  Goal 4: CI health workflow active")
    print(f"    Status: To be created")

    # Generate evidence
    evidence = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'sprint': 'Sprint 2 - Baseline',
        'placeholder_analysis': placeholder_data,
        'health_file_status': health_data,
        'test_coverage_estimate': test_data,
        'goals': {
            'placeholder_elimination': {
                'target': 0,
                'current': placeholder_data.get('total_violations', 0)
            },
            'health_template_adoption': {
                'target': '100%',
                'current': f"{100 - health_data['stub_percentage']:.1f}%"
            },
            'test_coverage': {
                'target': '≥80%',
                'current': 'TBD (needs coverage run)'
            }
        }
    }

    # Save evidence
    evidence_dir = repo_root / '23_compliance' / 'evidence' / 'sprint2'
    evidence_dir.mkdir(parents=True, exist_ok=True)

    evidence_file = evidence_dir / f'baseline_analysis_{datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")}.json'
    with open(evidence_file, 'w', encoding='utf-8') as f:
        json.dump(evidence, f, indent=2)

    print(f"\n{'=' * 60}")
    print(f"Evidence saved: {evidence_file.relative_to(repo_root)}")
    print(f"{'=' * 60}")

    return evidence


if __name__ == '__main__':
    report = generate_sprint2_report()

    # Exit with status based on readiness
    placeholders = report.get('placeholder_analysis', {}).get('total_violations', 999)
    if placeholders > 0:
        print(f"\n[ACTION REQUIRED] {placeholders} placeholder violations to fix")
        sys.exit(1)
    else:
        print(f"\n[OK] Ready for Sprint 2 implementation")
        sys.exit(0)
