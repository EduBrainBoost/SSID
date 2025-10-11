#!/usr/bin/env python3
"""
Sprint 2 Test Coverage Analysis Tool
Analyzes pytest coverage JSON output to identify gaps and prioritize improvements
"""
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict
from datetime import datetime

def load_coverage_data(json_file: Path) -> Dict:
    """Load coverage JSON file"""
    with open(json_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def analyze_by_module(coverage_data: Dict) -> Dict[str, Dict]:
    """Group coverage by root module"""
    files = coverage_data.get('files', {})

    modules = defaultdict(lambda: {'total_stmts': 0, 'total_miss': 0, 'files': []})

    for file_path, file_data in files.items():
        # Normalize path separators
        normalized = file_path.replace('\\', '/')
        parts = normalized.split('/')

        if not parts:
            continue

        module = parts[0]

        summary = file_data.get('summary', {})
        stmts = summary.get('num_statements', 0)
        miss = summary.get('missing_lines', 0)
        covered = summary.get('covered_lines', 0)

        # Calculate percentage
        if stmts > 0:
            pct = (covered / stmts) * 100
        else:
            pct = 100.0

        modules[module]['total_stmts'] += stmts
        modules[module]['total_miss'] += miss
        modules[module]['files'].append({
            'path': file_path,
            'stmts': stmts,
            'miss': miss,
            'covered': covered,
            'percent': pct
        })

    # Calculate module percentages
    for module, data in modules.items():
        total_stmts = data['total_stmts']
        total_miss = data['total_miss']
        if total_stmts > 0:
            data['percent'] = ((total_stmts - total_miss) / total_stmts) * 100
        else:
            data['percent'] = 100.0

    return dict(modules)

def identify_critical_gaps(modules: Dict[str, Dict]) -> List[Tuple[str, Dict]]:
    """Identify modules with low coverage that need attention"""
    critical = []

    priority_modules = [
        '23_compliance',
        '02_audit_logging',
        '03_core',
        '24_meta_orchestration',
        '08_identity_score'
    ]

    for module in priority_modules:
        if module in modules:
            data = modules[module]
            if data['percent'] < 80:
                critical.append((module, data))

    # Sort by coverage (lowest first)
    critical.sort(key=lambda x: x[1]['percent'])

    return critical

def find_untested_files(modules: Dict[str, Dict]) -> List[Dict]:
    """Find files with 0% coverage"""
    untested = []

    for module, data in modules.items():
        for file_info in data['files']:
            if file_info['percent'] == 0 and file_info['stmts'] > 0:
                untested.append({
                    'module': module,
                    **file_info
                })

    # Sort by statements (most impactful first)
    untested.sort(key=lambda x: x['stmts'], reverse=True)

    return untested

def calculate_gap_to_target(current_pct: float, target_pct: float = 80.0) -> Dict:
    """Calculate what's needed to reach target coverage"""
    gap = target_pct - current_pct

    return {
        'current': current_pct,
        'target': target_pct,
        'gap': gap,
        'status': 'PASS' if current_pct >= target_pct else 'FAIL'
    }

def generate_report(coverage_data: Dict, output_file: Path):
    """Generate comprehensive coverage analysis report"""

    # Overall stats
    totals = coverage_data.get('totals', {})
    total_stmts = totals.get('num_statements', 0)
    total_miss = totals.get('missing_lines', 0)
    total_covered = totals.get('covered_lines', 0)

    if total_stmts > 0:
        overall_pct = (total_covered / total_stmts) * 100
    else:
        overall_pct = 0.0

    # Analyze by module
    modules = analyze_by_module(coverage_data)
    critical_gaps = identify_critical_gaps(modules)
    untested_files = find_untested_files(modules)

    # Gap analysis
    gap = calculate_gap_to_target(overall_pct)

    # Generate report
    report_lines = []
    report_lines.append("# Sprint 2 Test Coverage Analysis Report")
    report_lines.append(f"**Date:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
    report_lines.append(f"**Sprint:** Sprint 2 - Week 5-6 (Test Coverage Goal)")
    report_lines.append(f"**Target:** 80% coverage")
    report_lines.append("")
    report_lines.append("---")
    report_lines.append("")

    # Executive Summary
    report_lines.append("## Executive Summary")
    report_lines.append("")
    report_lines.append(f"**Current Coverage:** {overall_pct:.2f}%")
    report_lines.append(f"**Target Coverage:** {gap['target']}%")
    report_lines.append(f"**Gap:** {gap['gap']:.2f} percentage points")
    report_lines.append(f"**Status:** {gap['status']}")
    report_lines.append("")
    report_lines.append("### Key Metrics")
    report_lines.append(f"- **Total Statements:** {total_stmts:,}")
    report_lines.append(f"- **Covered:** {total_covered:,} ({(total_covered/total_stmts*100 if total_stmts > 0 else 0):.2f}%)")
    report_lines.append(f"- **Missing:** {total_miss:,} ({(total_miss/total_stmts*100 if total_stmts > 0 else 0):.2f}%)")
    report_lines.append(f"- **Modules Analyzed:** {len(modules)}")
    report_lines.append("")
    report_lines.append("---")
    report_lines.append("")

    # Module Breakdown
    report_lines.append("## Coverage by Module")
    report_lines.append("")
    report_lines.append("| Module | Statements | Covered | Missing | Coverage | Status |")
    report_lines.append("|--------|------------|---------|---------|----------|--------|")

    # Sort modules by priority then coverage
    priority_order = ['23_compliance', '02_audit_logging', '03_core', '24_meta_orchestration', '08_identity_score']
    sorted_modules = []

    for prio in priority_order:
        if prio in modules:
            sorted_modules.append((prio, modules[prio]))

    for module, data in sorted_modules:
        stmts = data['total_stmts']
        miss = data['total_miss']
        covered = stmts - miss
        pct = data['percent']
        status = 'OK' if pct >= 80 else 'CRITICAL' if pct < 20 else 'NEEDS WORK'

        report_lines.append(f"| {module} | {stmts:,} | {covered:,} | {miss:,} | {pct:.2f}% | {status} |")

    report_lines.append("")
    report_lines.append("---")
    report_lines.append("")

    # Critical Gaps
    report_lines.append("## Critical Coverage Gaps")
    report_lines.append("")

    if critical_gaps:
        report_lines.append(f"**{len(critical_gaps)} modules** below 80% coverage threshold:")
        report_lines.append("")

        for i, (module, data) in enumerate(critical_gaps[:5], 1):
            pct = data['percent']
            stmts = data['total_stmts']
            miss = data['total_miss']

            report_lines.append(f"### {i}. {module} ({pct:.2f}% coverage)")
            report_lines.append(f"- **Statements:** {stmts:,}")
            report_lines.append(f"- **Missing:** {miss:,}")
            report_lines.append(f"- **Gap to 80%:** {80 - pct:.2f} percentage points")
            report_lines.append(f"- **Files:** {len(data['files'])}")
            report_lines.append("")
    else:
        report_lines.append("No critical gaps found - all priority modules above 80% coverage!")
        report_lines.append("")

    report_lines.append("---")
    report_lines.append("")

    # Untested Files
    report_lines.append("## Top 20 Untested Files (0% Coverage)")
    report_lines.append("")
    report_lines.append("| File | Module | Statements | Priority |")
    report_lines.append("|------|--------|------------|----------|")

    for file_info in untested_files[:20]:
        module = file_info['module']
        path = file_info['path']
        stmts = file_info['stmts']

        # Determine priority
        if module in ['23_compliance', '02_audit_logging']:
            priority = 'HIGH'
        elif module in ['03_core', '24_meta_orchestration']:
            priority = 'MEDIUM'
        else:
            priority = 'LOW'

        report_lines.append(f"| {path} | {module} | {stmts} | {priority} |")

    report_lines.append("")
    report_lines.append(f"**Total Untested Files:** {len(untested_files)}")
    report_lines.append("")
    report_lines.append("---")
    report_lines.append("")

    # Recommendations
    report_lines.append("## Recommendations")
    report_lines.append("")
    report_lines.append("### Immediate Actions (Week 5)")

    if critical_gaps:
        top_gap = critical_gaps[0]
        module_name = top_gap[0]
        report_lines.append(f"1. **Focus on {module_name}** (currently {top_gap[1]['percent']:.2f}%)")
        report_lines.append(f"   - Add tests for untested files")
        report_lines.append(f"   - Target: Increase to >=50% coverage")
        report_lines.append("")

    report_lines.append("2. **Create test templates** for common patterns")
    report_lines.append("   - Anti-gaming validators")
    report_lines.append("   - Health check endpoints")
    report_lines.append("   - Bridge connectors")
    report_lines.append("")

    report_lines.append("3. **Set up coverage CI enforcement**")
    report_lines.append("   - Add coverage threshold to CI")
    report_lines.append("   - Block PRs that decrease coverage")
    report_lines.append("")

    report_lines.append("### Long-term Strategy (Week 6+)")
    report_lines.append("")
    report_lines.append("1. Incremental coverage improvement")
    report_lines.append("2. Required tests for new code")
    report_lines.append("3. Regular coverage reviews")
    report_lines.append("4. Integration with Sprint 3 work")
    report_lines.append("")
    report_lines.append("---")
    report_lines.append("")

    # Effort Estimation
    if total_miss > 0:
        # Assume 1 test per 10 uncovered lines
        estimated_tests_needed = total_miss // 10
        # Assume 30 minutes per test
        estimated_hours = (estimated_tests_needed * 0.5)
        estimated_days = estimated_hours / 8

        report_lines.append("## Effort Estimation")
        report_lines.append("")
        report_lines.append(f"**Uncovered Statements:** {total_miss:,}")
        report_lines.append(f"**Estimated Tests Needed:** ~{estimated_tests_needed}")
        report_lines.append(f"**Estimated Effort:** ~{estimated_days:.1f} days ({estimated_hours:.1f} hours)")
        report_lines.append("")
        report_lines.append("*Assumptions: 1 test per 10 lines, 30 min per test*")
        report_lines.append("")

    report_lines.append("---")
    report_lines.append("")
    report_lines.append(f"**Generated by:** Sprint 2 Coverage Analysis Tool")
    report_lines.append(f"**Evidence Location:** 23_compliance/evidence/sprint2/")
    report_lines.append("")

    # Write report
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))

    # Also print summary to console
    print("\n" + "="*80)
    print("SPRINT 2 TEST COVERAGE ANALYSIS - SUMMARY")
    print("="*80)
    print(f"Overall Coverage: {overall_pct:.2f}% (Target: 80%)")
    print(f"Gap: {gap['gap']:.2f} percentage points")
    print(f"Status: {gap['status']}")
    print(f"\nCritical Modules Below Threshold: {len(critical_gaps)}")
    print(f"Untested Files: {len(untested_files)}")
    print(f"\nEstimated Effort to 80%: ~{estimated_days:.1f} days" if total_miss > 0 else "")
    print(f"\nFull report: {output_file}")
    print("="*80 + "\n")

def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python analyze_coverage.py <coverage.json>")
        sys.exit(1)

    coverage_file = Path(sys.argv[1])

    if not coverage_file.exists():
        print(f"ERROR: Coverage file not found: {coverage_file}")
        sys.exit(1)

    # Load coverage data
    coverage_data = load_coverage_data(coverage_file)

    # Generate report
    output_file = Path("23_compliance/evidence/sprint2/COVERAGE_ANALYSIS_REPORT.md")
    output_file.parent.mkdir(parents=True, exist_ok=True)

    generate_report(coverage_data, output_file)

    # Also create JSON summary for CI
    totals = coverage_data.get('totals', {})
    total_stmts = totals.get('num_statements', 0)
    total_covered = totals.get('covered_lines', 0)
    overall_pct = (total_covered / total_stmts * 100) if total_stmts > 0 else 0

    summary = {
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'overall_coverage': overall_pct,
        'target': 80.0,
        'gap': 80.0 - overall_pct,
        'status': 'PASS' if overall_pct >= 80 else 'FAIL',
        'total_statements': total_stmts,
        'covered_statements': total_covered,
        'missing_statements': total_stmts - total_covered
    }

    summary_file = Path("23_compliance/evidence/sprint2/coverage_summary.json")
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)

    print(f"Summary JSON: {summary_file}\n")

if __name__ == '__main__':
    main()
