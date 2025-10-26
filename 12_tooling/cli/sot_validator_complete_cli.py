#!/usr/bin/env python3
"""
SoT Validator CLI - Complete Interface
Production-ready CLI for SSID SoT validation

Version: 4.0.0
Status: PRODUCTION
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

# Add validator to path
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / '03_core' / 'validators' / 'sot'))

# Import REAL validator engine
from sot_validator_engine import RuleValidationEngine


def main():
    parser = argparse.ArgumentParser(
        description='SSID SoT Validator CLI v4.0.0',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('--verify-all', action='store_true', help='Verify all SoT rules')
    parser.add_argument('--scorecard', action='store_true', help='Generate scorecard')
    parser.add_argument('--strict', action='store_true', help='Fail on any warning')
    parser.add_argument('--output', type=str, help='Output file path (JSON)')
    parser.add_argument('--self-health', action='store_true', help='Run health check')

    args = parser.parse_args()

    # Initialize REAL validator engine
    print(f"Initializing validator engine...")
    print(f"Repository root: {REPO_ROOT}")

    try:
        engine = RuleValidationEngine(repo_root=REPO_ROOT)
        print(f"Loaded {len(engine.registry.rules)} rules from registry")
        print()
    except Exception as e:
        print(f"❌ Error initializing validator: {e}")
        return 2

    # Run validation
    if args.verify_all or args.scorecard or not any([args.self_health]):
        print("Running complete validation...")
        print()

        try:
            report = engine.validate_all()

            # Print summary
            print()
            print("=" * 80)
            print("VALIDATION RESULTS")
            print("=" * 80)
            print(f"Total Rules:     {report.total_rules}")
            print(f"Passed:          {report.passed}")
            print(f"Failed:          {report.failed}")
            print(f"Warnings:        {report.warnings}")
            print(f"Overall Score:   {report.overall_score:.2f}%")
            print()

            # MoSCoW breakdown
            print("MoSCoW Breakdown:")
            for priority in ['MUST', 'SHOULD', 'HAVE', 'CAN']:
                if priority in report.priority_scores:
                    score_data = report.priority_scores[priority]
                    print(f"  {priority:8} {score_data['pass']:5}/{score_data['total']:5} ({score_data['score']:.1f}%)")
            print("=" * 80)

            # Save results
            if args.output:
                output_path = Path(args.output)
            else:
                output_path = REPO_ROOT / '02_audit_logging' / 'reports' / 'validation_report.json'

            output_path.parent.mkdir(parents=True, exist_ok=True)

            output_data = {
                'timestamp': datetime.now().isoformat(),
                'version': '4.0.0',
                'total': report.total_rules,
                'passed': report.passed,
                'failed': report.failed,
                'warnings': report.warnings,
                'score': report.overall_score,
                'priority_scores': report.priority_scores,
                'results': [r.to_dict() for r in report.results[:100]]  # Save first 100 for size
            }

            output_path.write_text(json.dumps(output_data, indent=2))
            print(f"\n✅ Report saved: {output_path}")

            # Generate scorecard if requested
            if args.scorecard:
                scorecard_path = output_path.parent / 'validation_scorecard.json'
                scorecard = {
                    'timestamp': datetime.now().isoformat(),
                    'version': '4.0.0',
                    'overall_score': report.overall_score,
                    'priority_scores': report.priority_scores,
                    'status': 'PASS' if report.overall_score >= 95.0 else 'NEEDS_WORK'
                }
                scorecard_path.write_text(json.dumps(scorecard, indent=2))
                print(f"✅ Scorecard saved: {scorecard_path}")

            # Exit code
            if report.failed > 0:
                return 2 if args.strict else 1
            if args.strict and report.warnings > 0:
                return 1
            return 0

        except Exception as e:
            print(f"\n❌ Validation error: {e}")
            import traceback
            traceback.print_exc()
            return 2

    if args.self_health:
        print("Running health check...")

        # Check critical paths exist
        checks = {
            'Registry': REPO_ROOT / '16_codex/structure/auto_generated/sot_rules_full.json',
            'Contract': REPO_ROOT / '16_codex/contracts/sot/sot_contract.yaml',
            'Policy': REPO_ROOT / '23_compliance/policies/sot',
            'Validator': REPO_ROOT / '03_core/validators/sot/sot_validator_engine.py',
        }

        all_pass = True
        for name, path in checks.items():
            if path.exists():
                print(f"  ✅ {name}: {path.name}")
            else:
                print(f"  ❌ {name}: NOT FOUND")
                all_pass = False

        return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
