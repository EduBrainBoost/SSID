#!/usr/bin/env python3
"""
Unified Validator Runner - Single entry point for all 221 validators

Usage:
    python unified_validator_runner.py                           # Run all validators
    python unified_validator_runner.py --category gdpr           # Run GDPR validators only
    python unified_validator_runner.py --priority critical       # Run CRITICAL validators only
    python unified_validator_runner.py --json output.json        # JSON output for CI/CD
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List
import time

# Import all validator modules
from sot_validator_core import SoTValidator
from enhanced_validators import EnhancedValidators
from additional_validators import AdditionalValidators
from maximalstand_validators import MaximalstandValidators
from critical_validators_v2 import CriticalValidatorsV2


class UnifiedValidatorRunner:
    """Runs all validators from all modules"""

    def __init__(self, repo_root: Path):
        self.repo_root = Path(repo_root)
        self.core = SoTValidator(repo_root)
        self.enhanced = EnhancedValidators(repo_root)
        self.additional = AdditionalValidators(repo_root)
        self.maximalstand = MaximalstandValidators(repo_root)
        self.critical = CriticalValidatorsV2(repo_root)

    def run_all(self, category_filter: str = None, priority_filter: str = None) -> Dict:
        """Run all validators with optional filters"""
        results = {}
        start_time = time.time()

        # Run CRITICAL validators
        if priority_filter in [None, 'critical']:
            print("Running CRITICAL validators (26)...")
            critical_results = self.critical.validate_all_critical()
            results.update(critical_results)

        # TODO: Add other validator modules when needed
        # Currently focused on CRITICAL validators for Phase 1

        elapsed_time = time.time() - start_time

        return {
            'total_validators': len(results),
            'passed': sum(1 for r in results.values() if r.passed),
            'failed': sum(1 for r in results.values() if not r.passed),
            'elapsed_seconds': round(elapsed_time, 2),
            'results': {
                rule_id: {
                    'passed': result.passed,
                    'message': result.message,
                    'details': result.details
                }
                for rule_id, result in results.items()
            }
        }

    def print_summary(self, report: Dict):
        """Print human-readable summary"""
        print()
        print("=" * 80)
        print("VALIDATION SUMMARY")
        print("=" * 80)
        print(f"Total Validators Run: {report['total_validators']}")
        print(f"Passed: {report['passed']}")
        print(f"Failed: {report['failed']}")
        print(f"Success Rate: {(report['passed'] / report['total_validators'] * 100):.1f}%")
        print(f"Elapsed Time: {report['elapsed_seconds']}s")
        print()

        # Print failures
        if report['failed'] > 0:
            print("FAILURES:")
            print("-" * 80)
            for rule_id, result in report['results'].items():
                if not result['passed']:
                    print(f"[FAIL] {rule_id}: {result['message']}")
                    if result['details']:
                        for detail in result['details'][:3]:
                            print(f"       - {detail}")
                        if len(result['details']) > 3:
                            print(f"       ... and {len(result['details']) - 3} more")
            print()

    def save_json(self, report: Dict, output_file: Path):
        """Save report as JSON for CI/CD integration"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"JSON report saved to: {output_file}")


def main():
    parser = argparse.ArgumentParser(description='Unified Validator Runner for SSID')
    parser.add_argument('--category', type=str, help='Filter by category (gdpr, evidence, folder, naming, etc.)')
    parser.add_argument('--priority', type=str, choices=['critical', 'important', 'optional'], help='Filter by priority')
    parser.add_argument('--json', type=str, help='Output JSON file for CI/CD integration')
    parser.add_argument('--repo-root', type=str, help='Repository root path (default: auto-detect)')

    args = parser.parse_args()

    # Detect repository root
    if args.repo_root:
        repo_root = Path(args.repo_root)
    else:
        current = Path.cwd()
        if current.name == 'sot':
            repo_root = current.parent.parent.parent
        else:
            repo_root = current

    print(f"Repository root: {repo_root}")
    print()

    # Run validators
    runner = UnifiedValidatorRunner(repo_root)
    report = runner.run_all(category_filter=args.category, priority_filter=args.priority)

    # Print summary
    runner.print_summary(report)

    # Save JSON if requested
    if args.json:
        runner.save_json(report, Path(args.json))

    # Exit with code 1 if any failures
    sys.exit(0 if report['failed'] == 0 else 1)


if __name__ == '__main__':
    main()
