"""
Categorize Placeholder Violations by Priority and Type

Analyzes placeholder scan results and categorizes violations into:
- P1 (CRITICAL): Compliance-critical areas (23_compliance, 02_audit_logging)
- P2 (HIGH): Identity/Core logic (08_identity_score, 17_observability)
- P3 (MEDIUM): Tooling/Scripts (scripts/, 24_meta_orchestration, 11_test_simulation)
"""

import json
from pathlib import Path
from collections import defaultdict
from typing import Dict, List

def load_scan_results(scan_file: str) -> Dict:
    """Load placeholder scan JSON results"""
    with open(scan_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def categorize_violation(violation: Dict) -> str:
    """Categorize violation by priority based on file path"""
    file_path = violation['file']

    # P1 (CRITICAL): Compliance-critical areas
    if any(path in file_path for path in [
        '23_compliance/anti_gaming',
        '23_compliance/validators',
        '23_compliance/hooks',
        '23_compliance/reports',
        '23_compliance/tools',
        '23_compliance/federated_evidence',
        '02_audit_logging/validators'
    ]):
        return 'P1_CRITICAL'

    # P2 (HIGH): Identity and observability
    if any(path in file_path for path in [
        '08_identity_score',
        '17_observability',
        '13_ui_layer'
    ]):
        return 'P2_HIGH'

    # P3 (MEDIUM): Tooling, scripts, orchestration, test utilities
    if any(path in file_path for path in [
        'scripts/',
        '24_meta_orchestration',
        '11_test_simulation'
    ]):
        return 'P3_MEDIUM'

    # Default to P2 for unknown areas
    return 'P2_HIGH'


def analyze_violations(violations: List[Dict]) -> Dict:
    """Analyze violations and group by priority and type"""

    categorized = {
        'P1_CRITICAL': [],
        'P2_HIGH': [],
        'P3_MEDIUM': []
    }

    type_counts = defaultdict(int)
    file_counts = defaultdict(int)

    for v in violations:
        priority = categorize_violation(v)
        categorized[priority].append(v)
        type_counts[v['type']] += 1
        file_counts[v['file']] += 1

    return {
        'categorized': categorized,
        'type_counts': dict(type_counts),
        'file_counts': dict(file_counts),
        'summary': {
            'P1_CRITICAL': len(categorized['P1_CRITICAL']),
            'P2_HIGH': len(categorized['P2_HIGH']),
            'P3_MEDIUM': len(categorized['P3_MEDIUM']),
            'total': len(violations)
        }
    }


def generate_categorization_report(analysis: Dict, output_path: str):
    """Generate categorization report"""

    report = {
        'timestamp': '2025-10-10T00:00:00Z',
        'total_violations': analysis['summary']['total'],
        'priority_breakdown': analysis['summary'],
        'type_breakdown': analysis['type_counts'],
        'categorized_violations': analysis['categorized'],
        'files_affected': len(analysis['file_counts']),
        'top_offenders': sorted(
            analysis['file_counts'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

    return report


def print_summary(analysis: Dict):
    """Print human-readable summary"""

    print("\n" + "="*70)
    print("PLACEHOLDER VIOLATION CATEGORIZATION")
    print("="*70)

    summary = analysis['summary']
    print(f"\nTotal Violations: {summary['total']}")
    print(f"   [P1] CRITICAL:  {summary['P1_CRITICAL']:3d} - Compliance-critical areas")
    print(f"   [P2] HIGH:      {summary['P2_HIGH']:3d} - Identity/Core logic")
    print(f"   [P3] MEDIUM:    {summary['P3_MEDIUM']:3d} - Tooling/Scripts")

    print(f"\nViolation Types:")
    for vtype, count in sorted(analysis['type_counts'].items(), key=lambda x: x[1], reverse=True):
        print(f"   - {vtype:20s}: {count:3d}")

    print(f"\nTop 10 Files with Most Violations:")
    for filepath, count in sorted(analysis['file_counts'].items(), key=lambda x: x[1], reverse=True)[:10]:
        priority = categorize_violation({'file': filepath})
        prefix = {'P1_CRITICAL': '[P1]', 'P2_HIGH': '[P2]', 'P3_MEDIUM': '[P3]'}[priority]
        print(f"   {prefix} {filepath:60s}: {count:2d}")

    print("\n" + "="*70)


def main():
    """Main execution"""

    # Load scan results
    scan_file = Path(__file__).parent.parent / 'placeholder_scan_final.json'

    if not scan_file.exists():
        print(f"[ERROR] Scan file not found: {scan_file}")
        return

    print(f"[INFO] Loading scan results from: {scan_file}")
    scan_data = load_scan_results(str(scan_file))

    violations = scan_data.get('violations', [])
    print(f"[OK] Found {len(violations)} violations to categorize")

    # Analyze
    print("\n[INFO] Analyzing violations...")
    analysis = analyze_violations(violations)

    # Generate report
    output_path = Path(__file__).parent.parent / '23_compliance' / 'evidence' / 'sprint2' / 'placeholder_categorization.json'
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"\n[INFO] Generating categorization report: {output_path}")
    report = generate_categorization_report(analysis, str(output_path))

    # Print summary
    print_summary(analysis)

    print(f"\n[OK] Categorization complete!")
    print(f"    Report saved: {output_path}")
    print(f"\n[NEXT] Next Steps:")
    print(f"    1. Fix P1 (CRITICAL) violations first ({analysis['summary']['P1_CRITICAL']} violations)")
    print(f"    2. Fix P2 (HIGH) violations ({analysis['summary']['P2_HIGH']} violations)")
    print(f"    3. Fix P3 (MEDIUM) violations ({analysis['summary']['P3_MEDIUM']} violations)")


if __name__ == '__main__':
    main()
