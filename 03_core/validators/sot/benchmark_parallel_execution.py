#!/usr/bin/env python3
"""
Parallel vs Sequential Execution Benchmark
===========================================

Compares performance of:
1. Sequential execution (CachedSoTValidator)
2. Parallel execution (ParallelSoTValidator)
3. Different worker counts (1, 2, 4, 8, 16)

Outputs:
- Execution time comparison
- Speedup factor analysis
- Optimal worker count recommendation
- Batch-by-batch timing breakdown
"""

import os
import sys
import time
import json
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass, field

# Import validators
try:
    from cached_validator import CachedSoTValidator
    from parallel_validator import ParallelSoTValidator
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent))
    from cached_validator import CachedSoTValidator
    from parallel_validator import ParallelSoTValidator


@dataclass
class BenchmarkResult:
    """Results from a single benchmark run"""
    name: str
    workers: int
    total_time: float
    total_rules: int
    passed_count: int
    failed_count: int
    batch_times: List[float] = field(default_factory=list)
    cache_stats: Dict[str, Any] = field(default_factory=dict)


class ParallelBenchmark:
    """
    Benchmark harness for parallel vs sequential validation.
    """

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.results: List[BenchmarkResult] = []

    def benchmark_sequential(self, runs: int = 3) -> BenchmarkResult:
        """
        Benchmark sequential execution (CachedSoTValidator).

        Args:
            runs: Number of runs to average

        Returns:
            BenchmarkResult with averaged timing
        """
        print("\n" + "="*70)
        print("[BENCHMARK] Sequential Execution (CachedSoTValidator)")
        print("="*70)

        times = []

        for run in range(1, runs + 1):
            print(f"\n[RUN {run}/{runs}] Starting sequential validation...")

            # Create validator (fresh instance each time)
            validator = CachedSoTValidator(self.repo_root, cache_ttl=60)

            # Time execution
            start = time.time()
            report = validator.validate_all()
            elapsed = time.time() - start

            times.append(elapsed)

            print(f"[RUN {run}/{runs}] Complete: {elapsed:.3f}s")
            print(f"[RUN {run}/{runs}] Rules: {report.total_rules}, "
                  f"Passed: {report.passed_count}, Failed: {report.failed_count}")

        # Calculate average
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)

        print(f"\n[SEQUENTIAL] Average: {avg_time:.3f}s (min: {min_time:.3f}s, max: {max_time:.3f}s)")

        # Get final report for counts
        validator = CachedSoTValidator(self.repo_root, cache_ttl=60)
        report = validator.validate_all()

        result = BenchmarkResult(
            name="Sequential (CachedSoTValidator)",
            workers=1,
            total_time=avg_time,
            total_rules=report.total_rules,
            passed_count=report.passed_count,
            failed_count=report.failed_count,
            cache_stats=validator.get_cache_stats()
        )

        self.results.append(result)
        return result

    def benchmark_parallel(self, workers: int, runs: int = 3) -> BenchmarkResult:
        """
        Benchmark parallel execution with specified worker count.

        Args:
            workers: Number of parallel workers
            runs: Number of runs to average

        Returns:
            BenchmarkResult with averaged timing
        """
        print("\n" + "="*70)
        print(f"[BENCHMARK] Parallel Execution ({workers} workers)")
        print("="*70)

        times = []
        batch_times_all = []

        for run in range(1, runs + 1):
            print(f"\n[RUN {run}/{runs}] Starting parallel validation with {workers} workers...")

            # Create validator (fresh instance each time)
            validator = ParallelSoTValidator(
                self.repo_root,
                max_workers=workers,
                show_progress=False,  # Disable progress for clean benchmark
                cache_ttl=60
            )

            # Time execution
            start = time.time()
            report = validator.validate_all_parallel()
            elapsed = time.time() - start

            times.append(elapsed)

            # Get batch times
            batch_times = [stat.duration for stat in validator.batch_stats]
            batch_times_all.append(batch_times)

            print(f"[RUN {run}/{runs}] Complete: {elapsed:.3f}s")
            print(f"[RUN {run}/{runs}] Rules: {report.total_rules}, "
                  f"Passed: {report.passed_count}, Failed: {report.failed_count}")

        # Calculate averages
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)

        # Average batch times
        avg_batch_times = []
        if batch_times_all:
            num_batches = len(batch_times_all[0])
            for i in range(num_batches):
                batch_avg = sum(run[i] for run in batch_times_all) / len(batch_times_all)
                avg_batch_times.append(batch_avg)

        print(f"\n[PARALLEL {workers}W] Average: {avg_time:.3f}s "
              f"(min: {min_time:.3f}s, max: {max_time:.3f}s)")

        # Get final report for counts
        validator = ParallelSoTValidator(
            self.repo_root,
            max_workers=workers,
            show_progress=False,
            cache_ttl=60
        )
        report = validator.validate_all_parallel()

        result = BenchmarkResult(
            name=f"Parallel ({workers} workers)",
            workers=workers,
            total_time=avg_time,
            total_rules=report.total_rules,
            passed_count=report.passed_count,
            failed_count=report.failed_count,
            batch_times=avg_batch_times,
            cache_stats=validator.get_cache_stats()
        )

        self.results.append(result)
        return result

    def benchmark_scaling(self, worker_counts: List[int] = None, runs: int = 3):
        """
        Benchmark scaling with different worker counts.

        Args:
            worker_counts: List of worker counts to test (default: [1, 2, 4, 8])
            runs: Number of runs per configuration
        """
        if worker_counts is None:
            # Default: test 1, 2, 4, 8 workers (and CPU count if different)
            cpu_count = os.cpu_count() or 4
            worker_counts = [1, 2, 4, 8]
            if cpu_count not in worker_counts and cpu_count <= 16:
                worker_counts.append(cpu_count)
            worker_counts = sorted(set(worker_counts))

        print("\n" + "="*70)
        print("[BENCHMARK] Scaling Analysis")
        print("="*70)
        print(f"Worker counts: {worker_counts}")
        print(f"Runs per config: {runs}")

        # Benchmark each configuration
        for workers in worker_counts:
            self.benchmark_parallel(workers, runs)

    def print_comparison(self):
        """Print comparison table of all benchmark results"""
        if not self.results:
            print("[WARN] No benchmark results to compare")
            return

        print("\n" + "="*70)
        print("[COMPARISON] Sequential vs Parallel")
        print("="*70)

        # Find sequential baseline
        seq_result = next((r for r in self.results if r.workers == 1 and "Sequential" in r.name), None)
        baseline_time = seq_result.total_time if seq_result else self.results[0].total_time

        # Print table header
        print(f"\n{'Configuration':<30} {'Workers':<8} {'Time':<10} {'Speedup':<10} {'Rules/s':<10}")
        print("-"*70)

        # Print results
        for result in self.results:
            speedup = baseline_time / result.total_time
            rules_per_sec = result.total_rules / result.total_time

            print(f"{result.name:<30} {result.workers:<8} {result.total_time:>7.3f}s  "
                  f"{speedup:>7.2f}x   {rules_per_sec:>7.1f}")

        print("="*70)

        # Find optimal configuration
        parallel_results = [r for r in self.results if "Parallel" in r.name]
        if parallel_results:
            best = min(parallel_results, key=lambda r: r.total_time)
            best_speedup = baseline_time / best.total_time

            print(f"\n[OPTIMAL] {best.name}")
            print(f"          Time: {best.total_time:.3f}s")
            print(f"          Speedup: {best_speedup:.2f}x vs sequential")
            print(f"          Throughput: {best.total_rules / best.total_time:.1f} rules/s")

    def print_batch_breakdown(self):
        """Print batch-by-batch timing breakdown"""
        parallel_results = [r for r in self.results if "Parallel" in r.name and r.batch_times]

        if not parallel_results:
            print("[INFO] No parallel batch data available")
            return

        print("\n" + "="*70)
        print("[BATCH BREAKDOWN] Time per Batch by Worker Count")
        print("="*70)

        # Get batch count from first result
        num_batches = len(parallel_results[0].batch_times)

        # Print table header
        header = f"{'Batch':<6} "
        for result in parallel_results:
            header += f"{result.workers}W      "
        print(header)
        print("-"*70)

        # Print batch times
        for batch_id in range(num_batches):
            row = f"{batch_id:<6} "
            for result in parallel_results:
                if batch_id < len(result.batch_times):
                    row += f"{result.batch_times[batch_id]:>6.3f}s "
                else:
                    row += f"{'N/A':>7} "
            print(row)

        print("="*70)

    def save_results(self, output_file: Path):
        """Save benchmark results to JSON"""
        data = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "repo_root": str(self.repo_root),
            "results": []
        }

        for result in self.results:
            data["results"].append({
                "name": result.name,
                "workers": result.workers,
                "total_time": result.total_time,
                "total_rules": result.total_rules,
                "passed_count": result.passed_count,
                "failed_count": result.failed_count,
                "batch_times": result.batch_times,
                "throughput": result.total_rules / result.total_time
            })

        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"\n[SAVED] Results saved to: {output_file}")


# ============================================================
# MAIN BENCHMARK
# ============================================================

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Parallel Execution Benchmark")
    parser.add_argument('--repo-root', type=str, help='Path to SSID repository root')
    parser.add_argument('--runs', type=int, default=3, help='Number of runs per config (default: 3)')
    parser.add_argument('--workers', type=str, help='Worker counts to test (comma-separated, e.g., "1,2,4,8")')
    parser.add_argument('--sequential-only', action='store_true', help='Only benchmark sequential')
    parser.add_argument('--parallel-only', action='store_true', help='Only benchmark parallel (skip sequential)')
    parser.add_argument('--output', type=str, help='Save results to JSON file')

    args = parser.parse_args()

    # Get repo root
    if args.repo_root:
        repo_root = Path(args.repo_root)
    else:
        repo_root = Path(__file__).parent.parent.parent.parent

    print("="*70)
    print("[BENCHMARK] Parallel Execution Performance Analysis")
    print("="*70)
    print(f"Repository: {repo_root}")
    print(f"Runs per config: {args.runs}")
    print(f"CPU cores: {os.cpu_count()}")

    # Create benchmark
    benchmark = ParallelBenchmark(repo_root)

    # Parse worker counts
    if args.workers:
        worker_counts = [int(w.strip()) for w in args.workers.split(',')]
    else:
        cpu_count = os.cpu_count() or 4
        worker_counts = [2, 4, min(8, cpu_count), cpu_count]
        worker_counts = sorted(set(worker_counts))

    # Run benchmarks
    if args.sequential_only:
        benchmark.benchmark_sequential(args.runs)
    elif args.parallel_only:
        benchmark.benchmark_scaling(worker_counts, args.runs)
    else:
        # Full benchmark: sequential + parallel scaling
        benchmark.benchmark_sequential(args.runs)
        benchmark.benchmark_scaling(worker_counts, args.runs)

    # Print results
    benchmark.print_comparison()
    benchmark.print_batch_breakdown()

    # Save results
    if args.output:
        output_file = Path(args.output)
    else:
        output_file = Path(__file__).parent / "benchmark_results.json"

    benchmark.save_results(output_file)

    print("\n[OK] Benchmark complete!")


if __name__ == "__main__":
    main()
