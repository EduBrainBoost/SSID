#!/usr/bin/env python3
"""
Process Pool vs Thread Pool Benchmark
======================================

Comprehensive comparison of ThreadPool vs ProcessPool execution:
1. Sequential execution (baseline)
2. ThreadPool execution (GIL-limited)
3. ProcessPool execution (GIL-bypass)
4. Different worker counts (2, 4, 8, 16)
5. Batch-by-batch overhead analysis

Metrics:
- Total execution time
- Speedup vs baseline
- Serialization overhead
- Process startup overhead
- Memory usage
- CPU utilization

Expected Results:
- Sequential: ~35-40s (baseline)
- ThreadPool (8 workers): ~12.1s (2.9x speedup)
- ProcessPool (8 workers): ~2.5-3s (4-5x additional speedup, 10-14x total)

[POOL] Thread pool vs process pool comparison
[GIL] GIL impact analysis
[OVERHEAD] Serialization and IPC overhead measurement
"""

import os
import sys
import time
import json
import psutil
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

# Import validators
try:
    from cached_validator import CachedSoTValidator
    from parallel_validator import ParallelSoTValidator
    from process_pool_validator import ProcessPoolSoTValidator, test_picklability
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent))
    from cached_validator import CachedSoTValidator
    from parallel_validator import ParallelSoTValidator
    from process_pool_validator import ProcessPoolSoTValidator, test_picklability


@dataclass
class BenchmarkResult:
    """Results from a single benchmark run"""
    name: str
    mode: str  # "sequential", "thread", "process"
    workers: int
    total_time: float
    total_rules: int
    passed_count: int
    failed_count: int
    batch_times: List[float] = field(default_factory=list)
    batch_names: List[str] = field(default_factory=list)
    cache_stats: Dict[str, Any] = field(default_factory=dict)
    process_stats: Dict[str, Any] = field(default_factory=dict)
    memory_peak_mb: float = 0.0
    cpu_percent: float = 0.0

    def get_throughput(self) -> float:
        """Calculate rules per second"""
        return self.total_rules / self.total_time if self.total_time > 0 else 0.0

    def get_speedup(self, baseline_time: float) -> float:
        """Calculate speedup vs baseline"""
        return baseline_time / self.total_time if self.total_time > 0 else 0.0


@dataclass
class OverheadAnalysis:
    """Analysis of overhead components"""
    serialization_overhead: float = 0.0
    process_startup_overhead: float = 0.0
    ipc_overhead: float = 0.0
    total_overhead: float = 0.0
    overhead_percentage: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "serialization_overhead": f"{self.serialization_overhead:.3f}s",
            "process_startup_overhead": f"{self.process_startup_overhead:.3f}s",
            "ipc_overhead": f"{self.ipc_overhead:.3f}s",
            "total_overhead": f"{self.total_overhead:.3f}s",
            "overhead_percentage": f"{self.overhead_percentage:.1f}%"
        }


class ProcessPoolBenchmark:
    """
    Comprehensive benchmark comparing Thread Pool vs Process Pool.
    """

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.results: List[BenchmarkResult] = []
        self.process = psutil.Process()

    def benchmark_sequential(self, runs: int = 3) -> BenchmarkResult:
        """
        Benchmark sequential execution (baseline).

        Args:
            runs: Number of runs to average

        Returns:
            BenchmarkResult with averaged timing
        """
        print("\n" + "="*70)
        print("[BENCHMARK] Sequential Execution (Baseline)")
        print("="*70)

        times = []
        memory_peaks = []

        for run in range(1, runs + 1):
            print(f"\n[RUN {run}/{runs}] Starting sequential validation...")

            # Reset memory stats
            self.process.memory_info()

            # Create validator
            validator = CachedSoTValidator(self.repo_root, cache_ttl=60)

            # Time execution
            start = time.time()
            report = validator.validate_all()
            elapsed = time.time() - start

            times.append(elapsed)
            memory_peaks.append(self.process.memory_info().rss / 1024 / 1024)  # MB

            print(f"[RUN {run}/{runs}] Complete: {elapsed:.3f}s")
            print(f"[RUN {run}/{runs}] Memory: {memory_peaks[-1]:.1f} MB")

        # Calculate averages
        avg_time = sum(times) / len(times)
        avg_memory = sum(memory_peaks) / len(memory_peaks)

        print(f"\n[SEQUENTIAL] Average: {avg_time:.3f}s (Memory: {avg_memory:.1f} MB)")

        # Get final report
        validator = CachedSoTValidator(self.repo_root, cache_ttl=60)
        report = validator.validate_all()

        result = BenchmarkResult(
            name="Sequential (CachedSoTValidator)",
            mode="sequential",
            workers=1,
            total_time=avg_time,
            total_rules=report.total_rules,
            passed_count=report.passed_count,
            failed_count=report.failed_count,
            cache_stats=validator.get_cache_stats(),
            memory_peak_mb=avg_memory
        )

        self.results.append(result)
        return result

    def benchmark_thread_pool(self, workers: int, runs: int = 3) -> BenchmarkResult:
        """
        Benchmark thread pool execution.

        Args:
            workers: Number of worker threads
            runs: Number of runs to average

        Returns:
            BenchmarkResult with averaged timing
        """
        print("\n" + "="*70)
        print(f"[BENCHMARK] Thread Pool ({workers} workers)")
        print("="*70)

        times = []
        batch_times_all = []
        batch_names = []
        memory_peaks = []

        for run in range(1, runs + 1):
            print(f"\n[RUN {run}/{runs}] Starting thread pool validation...")

            # Reset memory stats
            self.process.memory_info()

            # Create validator
            validator = ParallelSoTValidator(
                self.repo_root,
                max_workers=workers,
                show_progress=False,
                cache_ttl=60
            )

            # Time execution
            start = time.time()
            report = validator.validate_all_parallel()
            elapsed = time.time() - start

            times.append(elapsed)
            memory_peaks.append(self.process.memory_info().rss / 1024 / 1024)

            # Get batch times
            batch_times = [stat.duration for stat in validator.batch_stats]
            batch_times_all.append(batch_times)

            if not batch_names:
                batch_names = [stat.batch_name for stat in validator.batch_stats]

            print(f"[RUN {run}/{runs}] Complete: {elapsed:.3f}s")
            print(f"[RUN {run}/{runs}] Memory: {memory_peaks[-1]:.1f} MB")

        # Calculate averages
        avg_time = sum(times) / len(times)
        avg_memory = sum(memory_peaks) / len(memory_peaks)

        # Average batch times
        avg_batch_times = []
        if batch_times_all:
            num_batches = len(batch_times_all[0])
            for i in range(num_batches):
                batch_avg = sum(run[i] for run in batch_times_all) / len(batch_times_all)
                avg_batch_times.append(batch_avg)

        print(f"\n[THREAD {workers}W] Average: {avg_time:.3f}s (Memory: {avg_memory:.1f} MB)")

        # Get final report
        validator = ParallelSoTValidator(
            self.repo_root,
            max_workers=workers,
            show_progress=False,
            cache_ttl=60
        )
        report = validator.validate_all_parallel()

        result = BenchmarkResult(
            name=f"ThreadPool ({workers} workers)",
            mode="thread",
            workers=workers,
            total_time=avg_time,
            total_rules=report.total_rules,
            passed_count=report.passed_count,
            failed_count=report.failed_count,
            batch_times=avg_batch_times,
            batch_names=batch_names,
            cache_stats=validator.get_cache_stats(),
            memory_peak_mb=avg_memory
        )

        self.results.append(result)
        return result

    def benchmark_process_pool(self, workers: int, runs: int = 3) -> BenchmarkResult:
        """
        Benchmark process pool execution.

        Args:
            workers: Number of worker processes
            runs: Number of runs to average

        Returns:
            BenchmarkResult with averaged timing
        """
        print("\n" + "="*70)
        print(f"[BENCHMARK] Process Pool ({workers} workers)")
        print("="*70)

        times = []
        batch_times_all = []
        batch_names = []
        memory_peaks = []
        process_stats_all = []

        for run in range(1, runs + 1):
            print(f"\n[RUN {run}/{runs}] Starting process pool validation...")

            # Reset memory stats
            self.process.memory_info()

            # Create validator
            validator = ProcessPoolSoTValidator(
                self.repo_root,
                max_workers=workers,
                show_progress=False,
                cache_ttl=60,
                use_process_pool=True,
                use_shared_memory=True
            )

            # Time execution
            start = time.time()
            report = validator.validate_all_process_pool()
            elapsed = time.time() - start

            times.append(elapsed)
            memory_peaks.append(self.process.memory_info().rss / 1024 / 1024)

            # Get batch times
            batch_times = [stat.duration for stat in validator.batch_stats]
            batch_times_all.append(batch_times)

            if not batch_names:
                batch_names = [stat.batch_name for stat in validator.batch_stats]

            # Get process stats
            process_stats_all.append(validator.get_process_stats().to_dict())

            print(f"[RUN {run}/{runs}] Complete: {elapsed:.3f}s")
            print(f"[RUN {run}/{runs}] Memory: {memory_peaks[-1]:.1f} MB")

            # Cleanup
            validator.cleanup()

        # Calculate averages
        avg_time = sum(times) / len(times)
        avg_memory = sum(memory_peaks) / len(memory_peaks)

        # Average batch times
        avg_batch_times = []
        if batch_times_all:
            num_batches = len(batch_times_all[0])
            for i in range(num_batches):
                batch_avg = sum(run[i] for run in batch_times_all) / len(batch_times_all)
                avg_batch_times.append(batch_avg)

        # Average process stats
        avg_process_stats = process_stats_all[0] if process_stats_all else {}

        print(f"\n[PROCESS {workers}W] Average: {avg_time:.3f}s (Memory: {avg_memory:.1f} MB)")

        # Get final report
        validator = ProcessPoolSoTValidator(
            self.repo_root,
            max_workers=workers,
            show_progress=False,
            cache_ttl=60,
            use_process_pool=True,
            use_shared_memory=True
        )
        report = validator.validate_all_process_pool()

        result = BenchmarkResult(
            name=f"ProcessPool ({workers} workers)",
            mode="process",
            workers=workers,
            total_time=avg_time,
            total_rules=report.total_rules,
            passed_count=report.passed_count,
            failed_count=report.failed_count,
            batch_times=avg_batch_times,
            batch_names=batch_names,
            cache_stats=validator.get_cache_stats(),
            process_stats=avg_process_stats,
            memory_peak_mb=avg_memory
        )

        self.results.append(result)
        validator.cleanup()

        return result

    def benchmark_full_comparison(self, runs: int = 3):
        """
        Run full comparison: Sequential, ThreadPool, ProcessPool.

        Args:
            runs: Number of runs per configuration
        """
        print("\n" + "="*70)
        print("[BENCHMARK] Full Comparison: Sequential vs Thread vs Process")
        print("="*70)

        # Test picklability first
        print("\n[POOL] Testing picklability...")
        if not test_picklability():
            print("[ERROR] Picklability test failed - ProcessPool may not work")
            print("[INFO] Continuing with benchmark anyway...")

        # 1. Sequential baseline
        self.benchmark_sequential(runs)

        # 2. ThreadPool with optimal workers
        cpu_count = os.cpu_count() or 4
        thread_workers = min(8, cpu_count)
        self.benchmark_thread_pool(thread_workers, runs)

        # 3. ProcessPool with optimal workers
        process_workers = cpu_count
        self.benchmark_process_pool(process_workers, runs)

    def benchmark_scaling_comparison(self, worker_counts: List[int] = None, runs: int = 3):
        """
        Compare ThreadPool vs ProcessPool scaling across different worker counts.

        Args:
            worker_counts: List of worker counts to test
            runs: Number of runs per configuration
        """
        if worker_counts is None:
            cpu_count = os.cpu_count() or 4
            worker_counts = [2, 4, min(8, cpu_count), cpu_count]
            worker_counts = sorted(set(worker_counts))

        print("\n" + "="*70)
        print("[BENCHMARK] Scaling Comparison")
        print("="*70)
        print(f"Worker counts: {worker_counts}")

        # Baseline
        self.benchmark_sequential(runs)

        # Test each worker count for both thread and process
        for workers in worker_counts:
            self.benchmark_thread_pool(workers, runs)
            self.benchmark_process_pool(workers, runs)

    def analyze_overhead(self) -> OverheadAnalysis:
        """
        Analyze overhead components in ProcessPool execution.

        Returns:
            OverheadAnalysis with breakdown
        """
        # Find sequential baseline
        seq_result = next((r for r in self.results if r.mode == "sequential"), None)
        if not seq_result:
            return OverheadAnalysis()

        # Find best process pool result
        process_results = [r for r in self.results if r.mode == "process"]
        if not process_results:
            return OverheadAnalysis()

        best_process = min(process_results, key=lambda r: r.total_time)

        # Extract overhead from process stats
        serialization = 0.0
        if "serialization_overhead" in best_process.process_stats:
            overhead_str = best_process.process_stats["serialization_overhead"]
            serialization = float(overhead_str.rstrip('s'))

        # Estimate process startup overhead (first batch is typically slower)
        startup = 0.0
        if best_process.batch_times:
            # Compare first batch to average of remaining batches
            first_batch = best_process.batch_times[0]
            avg_other = sum(best_process.batch_times[1:]) / max(1, len(best_process.batch_times) - 1)
            startup = max(0, first_batch - avg_other)

        # Calculate theoretical speedup vs actual
        ideal_speedup = best_process.workers
        actual_speedup = best_process.get_speedup(seq_result.total_time)
        efficiency = actual_speedup / ideal_speedup if ideal_speedup > 0 else 0

        # Overhead is the gap between ideal and actual
        ideal_time = seq_result.total_time / ideal_speedup
        overhead = best_process.total_time - ideal_time

        analysis = OverheadAnalysis(
            serialization_overhead=serialization,
            process_startup_overhead=startup,
            total_overhead=max(0, overhead),
            overhead_percentage=(overhead / best_process.total_time * 100) if best_process.total_time > 0 else 0
        )

        return analysis

    def print_comparison_table(self):
        """Print comprehensive comparison table"""
        if not self.results:
            print("[WARN] No results to compare")
            return

        print("\n" + "="*70)
        print("[COMPARISON] Thread Pool vs Process Pool Performance")
        print("="*70)

        # Find baseline
        baseline = next((r for r in self.results if r.mode == "sequential"), self.results[0])

        # Print header
        print(f"\n{'Configuration':<30} {'Workers':<8} {'Time':<10} {'Speedup':<10} {'Rules/s':<10} {'Memory':<10}")
        print("-"*70)

        # Print results
        for result in self.results:
            speedup = result.get_speedup(baseline.total_time)
            throughput = result.get_throughput()

            print(f"{result.name:<30} {result.workers:<8} {result.total_time:>7.3f}s  "
                  f"{speedup:>7.2f}x   {throughput:>7.1f}    {result.memory_peak_mb:>7.1f} MB")

        print("="*70)

        # Find best configurations
        thread_results = [r for r in self.results if r.mode == "thread"]
        process_results = [r for r in self.results if r.mode == "process"]

        if thread_results:
            best_thread = min(thread_results, key=lambda r: r.total_time)
            thread_speedup = best_thread.get_speedup(baseline.total_time)

            print(f"\n[BEST THREAD] {best_thread.name}")
            print(f"              Time: {best_thread.total_time:.3f}s")
            print(f"              Speedup: {thread_speedup:.2f}x vs sequential")
            print(f"              Throughput: {best_thread.get_throughput():.1f} rules/s")

        if process_results:
            best_process = min(process_results, key=lambda r: r.total_time)
            process_speedup = best_process.get_speedup(baseline.total_time)

            print(f"\n[BEST PROCESS] {best_process.name}")
            print(f"               Time: {best_process.total_time:.3f}s")
            print(f"               Speedup: {process_speedup:.2f}x vs sequential")
            print(f"               Throughput: {best_process.get_throughput():.1f} rules/s")

            if thread_results:
                process_vs_thread = best_thread.total_time / best_process.total_time
                print(f"               Process vs Thread: {process_vs_thread:.2f}x faster")

    def print_batch_breakdown(self):
        """Print batch-by-batch comparison"""
        thread_results = [r for r in self.results if r.mode == "thread" and r.batch_times]
        process_results = [r for r in self.results if r.mode == "process" and r.batch_times]

        if not thread_results and not process_results:
            return

        print("\n" + "="*70)
        print("[BATCH BREAKDOWN] ThreadPool vs ProcessPool")
        print("="*70)

        # Get batch names from first result
        batch_names = thread_results[0].batch_names if thread_results else process_results[0].batch_names
        num_batches = len(batch_names)

        # Print header
        header = f"{'Batch':<6} {'Name':<30}"
        for result in thread_results[:2]:  # Limit to 2 thread configs
            header += f" T{result.workers}W     "
        for result in process_results[:2]:  # Limit to 2 process configs
            header += f" P{result.workers}W     "
        print(header)
        print("-"*70)

        # Print batch times
        for i in range(min(num_batches, len(batch_names))):
            row = f"{i:<6} {batch_names[i][:28]:<30}"

            for result in thread_results[:2]:
                if i < len(result.batch_times):
                    row += f" {result.batch_times[i]:>6.3f}s "

            for result in process_results[:2]:
                if i < len(result.batch_times):
                    row += f" {result.batch_times[i]:>6.3f}s "

            print(row)

        print("="*70)

    def print_overhead_analysis(self):
        """Print overhead analysis"""
        analysis = self.analyze_overhead()

        print("\n" + "="*70)
        print("[OVERHEAD ANALYSIS] ProcessPool Overhead Components")
        print("="*70)

        print(f"Serialization:      {analysis.serialization_overhead:.3f}s")
        print(f"Process Startup:    {analysis.process_startup_overhead:.3f}s")
        print(f"IPC:                {analysis.ipc_overhead:.3f}s")
        print(f"Total Overhead:     {analysis.total_overhead:.3f}s")
        print(f"Overhead %:         {analysis.overhead_percentage:.1f}%")

        print("="*70)

    def save_results(self, output_file: Path):
        """Save benchmark results to JSON"""
        data = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "repo_root": str(self.repo_root),
            "system": {
                "cpu_count": os.cpu_count(),
                "platform": sys.platform
            },
            "results": [],
            "overhead_analysis": self.analyze_overhead().to_dict()
        }

        for result in self.results:
            data["results"].append({
                "name": result.name,
                "mode": result.mode,
                "workers": result.workers,
                "total_time": result.total_time,
                "total_rules": result.total_rules,
                "passed_count": result.passed_count,
                "failed_count": result.failed_count,
                "throughput": result.get_throughput(),
                "memory_peak_mb": result.memory_peak_mb,
                "batch_times": result.batch_times,
                "batch_names": result.batch_names,
                "process_stats": result.process_stats
            })

        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"\n[SAVED] Results saved to: {output_file}")


# ============================================================
# MAIN
# ============================================================

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Process Pool vs Thread Pool Benchmark")
    parser.add_argument('--repo-root', type=str, help='Path to SSID repository root')
    parser.add_argument('--runs', type=int, default=3, help='Number of runs per config (default: 3)')
    parser.add_argument('--workers', type=str, help='Worker counts to test (comma-separated)')
    parser.add_argument('--mode', choices=['full', 'scaling'], default='full',
                       help='Benchmark mode (default: full)')
    parser.add_argument('--output', type=str, help='Save results to JSON file')

    args = parser.parse_args()

    # Get repo root
    if args.repo_root:
        repo_root = Path(args.repo_root)
    else:
        repo_root = Path(__file__).parent.parent.parent.parent

    print("="*70)
    print("[BENCHMARK] Process Pool Performance Analysis")
    print("="*70)
    print(f"Repository: {repo_root}")
    print(f"Runs per config: {args.runs}")
    print(f"CPU cores: {os.cpu_count()}")
    print(f"Platform: {sys.platform}")

    # Create benchmark
    benchmark = ProcessPoolBenchmark(repo_root)

    # Run benchmark
    if args.mode == 'full':
        benchmark.benchmark_full_comparison(args.runs)
    else:
        # Scaling comparison
        if args.workers:
            worker_counts = [int(w.strip()) for w in args.workers.split(',')]
        else:
            worker_counts = None
        benchmark.benchmark_scaling_comparison(worker_counts, args.runs)

    # Print results
    benchmark.print_comparison_table()
    benchmark.print_batch_breakdown()
    benchmark.print_overhead_analysis()

    # Save results
    if args.output:
        output_file = Path(args.output)
    else:
        output_file = Path(__file__).parent / "benchmark_process_pool_results.json"

    benchmark.save_results(output_file)

    print("\n[OK] Benchmark complete!")


if __name__ == "__main__":
    main()
