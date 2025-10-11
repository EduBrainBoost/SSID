#!/usr/bin/env python3
"""
SoT Gap Report Generator (v2.0)

Analyzes current implementation status against SoT requirements
and generates actionable gap report for Phase beta implementation.

Usage:
    python3 23_compliance/tools/generate_gap_report.py
    python3 23_compliance/tools/generate_gap_report.py --json
    python3 23_compliance/tools/generate_gap_report.py --detailed
"""

import json
import yaml
import sys
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime


def load_sot_index() -> Dict:
    """Load SoT requirements index."""
    with open('23_compliance/sot_index.json') as f:
        return json.load(f)


def load_mapping_matrix() -> Dict:
    """Load current implementation mapping."""
    with open('23_compliance/mappings/sot_to_repo_matrix.yaml') as f:
        return yaml.safe_load(f)


def analyze_gaps(sot: Dict, matrix: Dict) -> Dict[str, List[Dict]]:
    """Analyze gaps between requirements and implementation."""
    gaps = {
        'MUST': [],
        'SHOULD': [],
        'HAVE': []
    }

    for tier in ['MUST', 'SHOULD', 'HAVE']:
        for req in matrix['mappings'][tier]:
            if req['status'] in ['partial', 'missing']:
                gap_info = {
                    'id': req['requirement_id'],
                    'name': req['name'],
                    'status': req['status'],
                    'confidence': req.get('confidence', 0.0),
                    'priority': 'CRITICAL' if tier == 'MUST' else 'HIGH' if tier == 'SHOULD' else 'MEDIUM',
                    'maps_to': req.get('repo_paths', []),
                    'effort_estimate': estimate_effort(req),
                    'issues': req.get('issues', []),
                    'dependencies': []  # Would be populated from dependency analysis
                }
                gaps[tier].append(gap_info)

    return gaps


def estimate_effort(req: Dict) -> str:
    """Estimate implementation effort in person-days."""
    # Simple heuristic based on requirement type
    if req['status'] == 'missing':
        return "5-10 days"
    elif req['status'] == 'partial':
        return "2-5 days"
    else:
        return "0 days"


def generate_gap_report(gaps: Dict, output_format: str = 'yaml') -> str:
    """Generate formatted gap report."""
    report = {
        'metadata': {
            'generated': datetime.utcnow().isoformat() + 'Z',
            'version': '2.0.0',
            'purpose': 'Phase beta Gap Analysis'
        },
        'summary': {
            'total_gaps': sum(len(gaps[tier]) for tier in gaps),
            'by_tier': {
                'MUST': len(gaps['MUST']),
                'SHOULD': len(gaps['SHOULD']),
                'HAVE': len(gaps['HAVE'])
            },
            'total_effort_estimate': calculate_total_effort(gaps)
        },
        'gaps': gaps,
        'recommendations': [
            {
                'priority': 'CRITICAL',
                'action': 'Complete MUST-026-TRAVEL-RULE by 2025-11-15',
                'reason': 'AMLD6 compliance deadline'
            },
            {
                'priority': 'HIGH',
                'action': 'Implement caching layer for performance',
                'reason': 'SHOULD requirements improve system resilience'
            },
            {
                'priority': 'MEDIUM',
                'action': 'Document HAVE features for compliance score',
                'reason': 'Many partial implementations just need documentation'
            }
        ]
    }

    if output_format == 'json':
        return json.dumps(report, indent=2, ensure_ascii=False)
    elif output_format == 'yaml':
        return yaml.dump(report, default_flow_style=False, allow_unicode=True)
    else:
        return format_human_readable(report)


def calculate_total_effort(gaps: Dict) -> str:
    """Calculate total estimated effort."""
    total_days = 0

    for tier in gaps:
        for gap in gaps[tier]:
            effort_str = gap['effort_estimate']
            # Parse "5-10 days" format and take average
            if '-' in effort_str:
                low, high = effort_str.replace(' days', '').split('-')
                avg_days = (int(low) + int(high)) / 2
                total_days += avg_days

    return f"{int(total_days)} person-days ({int(total_days / 5)} person-weeks)"


def format_human_readable(report: Dict) -> str:
    """Format report for human reading."""
    lines = []
    lines.append("=" * 80)
    lines.append("SoT Gap Analysis Report - Phase β")
    lines.append("=" * 80)
    lines.append(f"Generated: {report['metadata']['generated']}")
    lines.append("")

    lines.append("SUMMARY")
    lines.append("-" * 80)
    lines.append(f"Total Gaps: {report['summary']['total_gaps']}")
    lines.append(f"  MUST gaps: {report['summary']['by_tier']['MUST']}")
    lines.append(f"  SHOULD gaps: {report['summary']['by_tier']['SHOULD']}")
    lines.append(f"  HAVE gaps: {report['summary']['by_tier']['HAVE']}")
    lines.append(f"Total Effort: {report['summary']['total_effort_estimate']}")
    lines.append("")

    for tier in ['MUST', 'SHOULD', 'HAVE']:
        if report['gaps'][tier]:
            lines.append(f"{tier} REQUIREMENTS")
            lines.append("-" * 80)
            for gap in report['gaps'][tier]:
                lines.append(f"  [{gap['priority']}] {gap['id']}: {gap['name']}")
                lines.append(f"    Status: {gap['status']}")
                lines.append(f"    Confidence: {gap.get('confidence', 0.0)}")
                lines.append(f"    Effort: {gap['effort_estimate']}")
                lines.append(f"    Paths: {', '.join(gap['maps_to']) if gap['maps_to'] else 'N/A'}")
                if gap.get('issues'):
                    lines.append(f"    Issues: {', '.join(gap['issues'])}")
                lines.append("")

    lines.append("RECOMMENDATIONS")
    lines.append("-" * 80)
    for rec in report['recommendations']:
        lines.append(f"[{rec['priority']}] {rec['action']}")
        lines.append(f"  Reason: {rec['reason']}")
        lines.append("")

    lines.append("=" * 80)
    lines.append("Use this report to guide Phase β implementation")
    lines.append("=" * 80)

    return "\n".join(lines)


def save_report(report: str, filename: str):
    """Save report to file."""
    output_path = Path('23_compliance/reports') / filename
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"[OK] Gap report saved to: {output_path}")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Generate SoT gap analysis report')
    parser.add_argument('--json', action='store_true', help='Output JSON format')
    parser.add_argument('--yaml', action='store_true', help='Output YAML format (default)')
    parser.add_argument('--detailed', action='store_true', help='Include detailed analysis')
    parser.add_argument('--save', action='store_true', help='Save to file')

    args = parser.parse_args()

    # Determine output format
    if args.json:
        output_format = 'json'
        filename = 'sot_gap_report_phase_beta.json'
    elif args.yaml or not (args.json or args.detailed):
        output_format = 'yaml'
        filename = 'sot_gap_report_phase_beta.yaml'
    else:
        output_format = 'human'
        filename = 'sot_gap_report_phase_beta.txt'

    try:
        # Load data
        print("Loading SoT index...", file=sys.stderr)
        sot = load_sot_index()

        print("Loading mapping matrix...", file=sys.stderr)
        matrix = load_mapping_matrix()

        print("Analyzing gaps...", file=sys.stderr)
        gaps = analyze_gaps(sot, matrix)

        print("Generating report...", file=sys.stderr)
        report = generate_gap_report(gaps, output_format)

        # Output or save
        if args.save:
            save_report(report, filename)
        else:
            print(report)

        # Print summary to stderr
        total_gaps = sum(len(gaps[tier]) for tier in gaps)
        print(f"\n[OK] Analysis complete. Found {total_gaps} gaps.", file=sys.stderr)

        sys.exit(0)

    except FileNotFoundError as e:
        print(f"[FAIL] Error: Required file not found: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"[FAIL] Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
