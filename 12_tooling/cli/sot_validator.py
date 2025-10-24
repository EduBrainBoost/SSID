#!/usr/bin/env python3
"""
GENERATED FILE - DO NOT EDIT MANUALLY
============================================================================
Generator: SotValidatorCliGenerator
Timestamp: 2025-10-24T14:55:30.289281
Source: SoT Rule Parser V4.0 ULTIMATE
============================================================================
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

# Add core validators to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / '03_core' / 'validators' / 'sot'))

try:
    # Try v2 first (with enforcement layer rules)
    from sot_validator_core_v2 import validate_all_sot_rules, ValidationResult, RULE_PRIORITIES
    print("[INFO] Using sot_validator_core_v2 (4.773 rules including 50 enforcement layer rules)")
except ImportError:
    try:
        from sot_validator_core import validate_all_sot_rules, ValidationResult, RULE_PRIORITIES
        print("[INFO] Using sot_validator_core (4.723 rules)")
    except ImportError:
        print("[ERROR] sot_validator_core not found")
        sys.exit(1)


def generate_scorecard(results: dict, output_format: str = 'json') -> str:
    """Generate scorecard in JSON or Markdown format"""

    total = len(results['results'])
    passed = sum(1 for r in results['results'].values() if r == ValidationResult.PASS)
    warned = sum(1 for r in results['results'].values() if r == ValidationResult.WARN)
    failed = sum(1 for r in results['results'].values() if r == ValidationResult.FAIL)

    pass_rate = (passed / total * 100) if total > 0 else 0

    if output_format == 'json':
        return json.dumps({
            'timestamp': results['timestamp'],
            'total_rules': total,
            'passed': passed,
            'warned': warned,
            'failed': failed,
            'pass_rate': round(pass_rate, 2)
        }, indent=2)
    else:  # markdown
        return f"""# SoT Validation Scorecard

**Generated:** {results['timestamp']}

## Summary

- **Total Rules:** {total}
- **Passed:** {passed} [OK]
- **Warned:** {warned} [WARN]
- **Failed:** {failed} [FAIL]
- **Pass Rate:** {pass_rate:.2f}%

## Status

{'[OK] ALL CHECKS PASSED' if failed == 0 else '[FAIL] VALIDATION FAILED'}
"""


def main():
    parser = argparse.ArgumentParser(
        description='SoT Validator CLI - Validate all SoT rules'
    )

    parser.add_argument('--verify-all', action='store_true',
                        help='Run all validations')
    parser.add_argument('--scorecard', action='store_true',
                        help='Generate scorecard')
    parser.add_argument('--format', choices=['json', 'md'], default='json',
                        help='Scorecard output format')
    parser.add_argument('--strict', action='store_true',
                        help='Exit with error if any validation fails')
    parser.add_argument('--show-evidence', action='store_true',
                        help='Show evidence for each rule')

    args = parser.parse_args()

    # Run validations
    results = validate_all_sot_rules()

    # Generate scorecard
    if args.scorecard:
        scorecard = generate_scorecard(results, args.format)
        print(scorecard)

        # Write scorecard files
        if args.format == 'json':
            Path('scorecard.json').write_text(scorecard)
        else:
            Path('scorecard.md').write_text(scorecard)

    # Verify all
    if args.verify_all:
        total = len(results['results'])
        failed = sum(1 for r in results['results'].values() if r == ValidationResult.FAIL)

        print(f"Validation complete: {total} rules checked")
        print(f"Failed: {failed}")

        if args.strict and failed > 0:
            sys.exit(1)

    return 0


if __name__ == '__main__':
    sys.exit(main())
