#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSID - ML Prioritization Benchmark Tool (ADVANCED PHASE 4)
Compares ML-prioritized vs fixed-order execution performance

Metrics:
- Time to first failure (target: 6s → <1s)
- Total execution time
- ML overhead
- Prediction accuracy
- False negative rate
"""

import argparse
import json
import time
import statistics
from pathlib import Path
from typing import List, Dict
from datetime import datetime

try:
    from ml_prioritization_validator import MLPrioritizedValidator
    from validation_database import ValidationDatabase
except ImportError:
    from .ml_prioritization_validator import MLPrioritizedValidator
    from .validation_database import ValidationDatabase


class BenchmarkRunner:
    """
    Runs comprehensive benchmarks comparing validation strategies.

    Tests:
    - Fixed-order baseline
    - ML-prioritized with trained model
    - ML-prioritized without model (historical rates)
    - Multiple iterations for statistical significance
    """

    def __init__(self, repo_root: Path, iterations: int = 10):
        """
        Initialize benchmark runner.

        Args:
            repo_root: Repository root
            iterations: Number of iterations per test
        """
        self.repo_root = Path(repo_root)
        self.iterations = iterations
        self.results = []

    def run_benchmark(self, mode: str, validator: MLPrioritizedValidator) -> Dict:
        """
        Run benchmark for given mode.

        Args:
            mode: "fixed" or "ml"
            validator: Validator instance

        Returns:
            Benchmark metrics dict
        """
        print(f"\n[BENCHMARK-{mode.upper()}] Running {self.iterations} iterations...")

        times_total = []
        times_first_failure = []
        failed_rules_counts = []
        ml_overheads = []

        for i in range(self.iterations):
            print(f"  Iteration {i+1}/{self.iterations}...", end='', flush=True)

            if mode == "fixed":
                results, metrics = validator.validate_fixed_order(verbose=False)
            else:
                results, metrics = validator.validate_ml_prioritized(verbose=False)

            times_total.append(metrics['total_time'])
            if metrics['time_to_first_failure']:
                times_first_failure.append(metrics['time_to_first_failure'])
            failed_rules_counts.append(metrics['failed_rules'])

            if 'ml_overhead_ms' in metrics:
                ml_overheads.append(metrics['ml_overhead_ms'])

            print(f" {metrics['total_time']:.2f}s")

        # Calculate statistics
        benchmark_metrics = {
            'mode': mode,
            'iterations': self.iterations,
            'total_time': {
                'mean': statistics.mean(times_total),
                'median': statistics.median(times_total),
                'stdev': statistics.stdev(times_total) if len(times_total) > 1 else 0,
                'min': min(times_total),
                'max': max(times_total)
            },
            'failed_rules': {
                'mean': statistics.mean(failed_rules_counts),
                'mode': statistics.mode(failed_rules_counts) if failed_rules_counts else 0
            }
        }

        if times_first_failure:
            benchmark_metrics['time_to_first_failure'] = {
                'mean': statistics.mean(times_first_failure),
                'median': statistics.median(times_first_failure),
                'stdev': statistics.stdev(times_first_failure) if len(times_first_failure) > 1 else 0,
                'min': min(times_first_failure),
                'max': max(times_first_failure)
            }

        if ml_overheads:
            benchmark_metrics['ml_overhead_ms'] = {
                'mean': statistics.mean(ml_overheads),
                'median': statistics.median(ml_overheads),
                'max': max(ml_overheads)
            }

        return benchmark_metrics

    def run_full_benchmark(self, db_path: Path = None, model_path: Path = None) -> Dict:
        """
        Run complete benchmark comparing all modes.

        Args:
            db_path: Database path
            model_path: ML model path

        Returns:
            Complete benchmark results
        """
        print("=" * 70)
        print("ML PRIORITIZATION BENCHMARK")
        print("=" * 70)
        print(f"Repository: {self.repo_root}")
        print(f"Iterations per mode: {self.iterations}")
        print(f"Timestamp: {datetime.now().isoformat()}")

        # Create validator
        validator = MLPrioritizedValidator(
            repo_root=self.repo_root,
            db_path=db_path,
            model_path=model_path,
            fail_fast=True
        )

        # Run benchmarks
        fixed_metrics = self.run_benchmark("fixed", validator)
        ml_metrics = self.run_benchmark("ml", validator)

        # Calculate improvements
        improvements = self._calculate_improvements(fixed_metrics, ml_metrics)

        results = {
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'repo_root': str(self.repo_root),
                'iterations': self.iterations,
                'ml_enabled': validator.ml_enabled,
                'model_trained': validator.predictor.is_trained if validator.predictor else False
            },
            'fixed_order': fixed_metrics,
            'ml_prioritized': ml_metrics,
            'improvements': improvements,
            'success_criteria': self._check_success_criteria(improvements)
        }

        return results

    def _calculate_improvements(self, fixed: Dict, ml: Dict) -> Dict:
        """Calculate improvement metrics."""
        improvements = {}

        # Time to first failure improvement
        if 'time_to_first_failure' in fixed and 'time_to_first_failure' in ml:
            fixed_ttf = fixed['time_to_first_failure']['mean']
            ml_ttf = ml['time_to_first_failure']['mean']

            if fixed_ttf > 0:
                improvement_pct = (fixed_ttf - ml_ttf) / fixed_ttf * 100
                speedup = fixed_ttf / ml_ttf if ml_ttf > 0 else float('inf')

                improvements['time_to_first_failure'] = {
                    'fixed_mean': fixed_ttf,
                    'ml_mean': ml_ttf,
                    'improvement_pct': improvement_pct,
                    'speedup_factor': speedup,
                    'absolute_reduction_s': fixed_ttf - ml_ttf
                }

        # Total execution time
        fixed_total = fixed['total_time']['mean']
        ml_total = ml['total_time']['mean']

        if fixed_total > 0:
            total_improvement = (fixed_total - ml_total) / fixed_total * 100
            improvements['total_time'] = {
                'fixed_mean': fixed_total,
                'ml_mean': ml_total,
                'improvement_pct': total_improvement,
                'speedup_factor': fixed_total / ml_total if ml_total > 0 else float('inf')
            }

        # ML overhead
        if 'ml_overhead_ms' in ml:
            improvements['ml_overhead_ms'] = ml['ml_overhead_ms']['mean']

        return improvements

    def _check_success_criteria(self, improvements: Dict) -> Dict:
        """Check if improvements meet success criteria."""
        criteria = {}

        # Time to first failure: target <1s
        if 'time_to_first_failure' in improvements:
            ttf_ml = improvements['time_to_first_failure']['ml_mean']
            criteria['time_to_first_failure_under_1s'] = {
                'target': 1.0,
                'actual': ttf_ml,
                'met': ttf_ml < 1.0
            }

            # 6x improvement target
            speedup = improvements['time_to_first_failure']['speedup_factor']
            criteria['speedup_6x_or_better'] = {
                'target': 6.0,
                'actual': speedup,
                'met': speedup >= 6.0
            }

        # ML overhead: target <50ms
        if 'ml_overhead_ms' in improvements:
            overhead = improvements['ml_overhead_ms']
            criteria['ml_overhead_under_50ms'] = {
                'target': 50.0,
                'actual': overhead,
                'met': overhead < 50.0
            }

        # Overall success
        all_met = all(c['met'] for c in criteria.values())
        criteria['all_criteria_met'] = all_met

        return criteria

    def print_report(self, results: Dict):
        """Print formatted benchmark report."""
        print("\n" + "=" * 70)
        print("BENCHMARK RESULTS")
        print("=" * 70)

        print("\nFixed Order Execution:")
        fixed = results['fixed_order']
        print(f"  Total time: {fixed['total_time']['mean']:.2f}s "
              f"(±{fixed['total_time']['stdev']:.2f}s)")
        if 'time_to_first_failure' in fixed:
            print(f"  Time to first failure: {fixed['time_to_first_failure']['mean']:.2f}s "
                  f"(±{fixed['time_to_first_failure']['stdev']:.2f}s)")

        print("\nML-Prioritized Execution:")
        ml = results['ml_prioritized']
        print(f"  Total time: {ml['total_time']['mean']:.2f}s "
              f"(±{ml['total_time']['stdev']:.2f}s)")
        if 'time_to_first_failure' in ml:
            print(f"  Time to first failure: {ml['time_to_first_failure']['mean']:.2f}s "
                  f"(±{ml['time_to_first_failure']['stdev']:.2f}s)")
        if 'ml_overhead_ms' in ml:
            print(f"  ML overhead: {ml['ml_overhead_ms']['mean']:.1f}ms "
                  f"(max: {ml['ml_overhead_ms']['max']:.1f}ms)")

        print("\n" + "-" * 70)
        print("IMPROVEMENTS")
        print("-" * 70)

        improvements = results['improvements']

        if 'time_to_first_failure' in improvements:
            ttf = improvements['time_to_first_failure']
            print(f"\nTime to First Failure:")
            print(f"  Fixed order: {ttf['fixed_mean']:.2f}s")
            print(f"  ML-prioritized: {ttf['ml_mean']:.2f}s")
            print(f"  Improvement: {ttf['improvement_pct']:.1f}% faster ({ttf['speedup_factor']:.1f}x speedup)")
            print(f"  Absolute reduction: {ttf['absolute_reduction_s']:.2f}s")

        if 'total_time' in improvements:
            total = improvements['total_time']
            print(f"\nTotal Execution Time:")
            print(f"  Fixed order: {total['fixed_mean']:.2f}s")
            print(f"  ML-prioritized: {total['ml_mean']:.2f}s")
            print(f"  Improvement: {total['improvement_pct']:.1f}% faster ({total['speedup_factor']:.1f}x speedup)")

        print("\n" + "-" * 70)
        print("SUCCESS CRITERIA")
        print("-" * 70)

        criteria = results['success_criteria']

        for name, criterion in criteria.items():
            if name == 'all_criteria_met':
                continue

            status = "[PASS]" if criterion['met'] else "[FAIL]"
            print(f"\n{status} {name}:")
            print(f"  Target: {criterion['target']}")
            print(f"  Actual: {criterion['actual']:.2f}")

        print("\n" + "=" * 70)
        if criteria['all_criteria_met']:
            print("[SUCCESS] All performance criteria met!")
        else:
            print("[PARTIAL] Some criteria not met - see details above")
        print("=" * 70)


def main():
    """Main entry point for benchmarking."""
    parser = argparse.ArgumentParser(
        description="Benchmark ML-prioritized vs fixed-order rule execution"
    )
    parser.add_argument(
        '--iterations',
        type=int,
        default=10,
        help='Number of iterations per benchmark (default: 10)'
    )
    parser.add_argument(
        '--repo-root',
        type=Path,
        default=Path.cwd(),
        help='Repository root directory'
    )
    parser.add_argument(
        '--db-path',
        type=Path,
        help='Custom database path'
    )
    parser.add_argument(
        '--model-path',
        type=Path,
        help='Path to trained ML model'
    )
    parser.add_argument(
        '--json-output',
        type=Path,
        help='Write results to JSON file'
    )
    parser.add_argument(
        '--quick',
        action='store_true',
        help='Quick benchmark (3 iterations instead of 10)'
    )

    args = parser.parse_args()

    iterations = 3 if args.quick else args.iterations

    # Run benchmark
    runner = BenchmarkRunner(
        repo_root=args.repo_root,
        iterations=iterations
    )

    results = runner.run_full_benchmark(
        db_path=args.db_path,
        model_path=args.model_path
    )

    # Print report
    runner.print_report(results)

    # Save JSON if requested
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        with open(args.json_output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n[INFO] Results saved to: {args.json_output}")


if __name__ == "__main__":
    main()
