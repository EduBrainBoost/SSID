#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSID - Database Inspection Tool
View statistics and insights from validation history database
"""

import argparse
import json
from pathlib import Path
from datetime import datetime

try:
    from validation_database import ValidationDatabase
except ImportError:
    from .validation_database import ValidationDatabase


def print_stats(db: ValidationDatabase):
    """Print database statistics."""
    stats = db.get_stats()

    print("=" * 70)
    print("VALIDATION HISTORY DATABASE STATISTICS")
    print("=" * 70)

    print(f"\nOverall Stats:")
    print(f"  Total validations: {stats['total_validations']}")
    print(f"  Total rule executions: {stats['total_rule_executions']}")

    if stats['total_validations'] > 0:
        avg_rules_per_validation = stats['total_rule_executions'] / stats['total_validations']
        print(f"  Avg rules per validation: {avg_rules_per_validation:.1f}")

    if stats['avg_time_to_first_failure_ms']:
        print(f"  Avg time to first failure: {stats['avg_time_to_first_failure_ms']:.0f}ms "
              f"({stats['avg_time_to_first_failure_ms']/1000:.2f}s)")

    if 'top_failing_rules' in stats and stats['top_failing_rules']:
        print(f"\nTop Failing Rules:")
        for i, rule_stat in enumerate(stats['top_failing_rules'], 1):
            print(f"  {i}. {rule_stat['rule_id']}: {rule_stat['failures']} failures")

    if 'latest_model' in stats:
        model = stats['latest_model']
        print(f"\nLatest ML Model:")
        print(f"  Version: {model['version']}")
        print(f"  Accuracy: {model['accuracy']:.1%}")
        print(f"  False negative rate: {model['false_negative_rate']:.1%}")

    print("\nTraining Readiness:")
    for min_samples in [50, 100, 200, 500]:
        status = "READY" if stats['total_validations'] >= min_samples else "NOT READY"
        deficit = max(0, min_samples - stats['total_validations'])
        print(f"  {min_samples} samples: {status}", end='')
        if deficit > 0:
            print(f" (need {deficit} more)")
        else:
            print()

    print("=" * 70)


def export_json(db: ValidationDatabase, output_path: Path):
    """Export stats to JSON file."""
    stats = db.get_stats()

    output_data = {
        'timestamp': datetime.now().isoformat(),
        'database_stats': stats
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"[INFO] Stats exported to: {output_path}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Inspect validation history database"
    )
    parser.add_argument(
        '--db-path',
        type=Path,
        help='Database path (default: .ssid_cache/validation_history.db)'
    )
    parser.add_argument(
        '--repo-root',
        type=Path,
        default=Path.cwd(),
        help='Repository root directory'
    )
    parser.add_argument(
        '--json-output',
        type=Path,
        help='Export stats to JSON file'
    )

    args = parser.parse_args()

    # Determine database path
    if args.db_path:
        db_path = args.db_path
    else:
        db_path = args.repo_root / ".ssid_cache" / "validation_history.db"

    if not db_path.exists():
        print(f"[ERROR] Database not found: {db_path}")
        print(f"[INFO] Run ml_prioritization_validator.py with --store-results to create it")
        return 1

    # Load database
    db = ValidationDatabase(db_path)

    # Print stats
    print_stats(db)

    # Export JSON if requested
    if args.json_output:
        export_json(db, args.json_output)

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
