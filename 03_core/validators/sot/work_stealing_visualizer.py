#!/usr/bin/env python3
"""
Work Stealing Visualization Tool
=================================

Visualizes work stealing behavior and worker utilization using ASCII charts.

Generates:
1. Worker utilization timeline
2. Work stealing activity heatmap
3. Load distribution analysis
4. Idle time breakdown

No external dependencies required - uses pure ASCII art for visualization.
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class WorkerEvent:
    """Single worker event for visualization"""
    worker_id: int
    event_type: str  # "task", "steal", "idle"
    start_time: float
    duration: float
    task_id: str = ""


class WorkStealingVisualizer:
    """
    Visualizes work stealing behavior using ASCII charts.
    """

    def __init__(self):
        self.events: List[WorkerEvent] = []
        self.worker_count = 0
        self.total_time = 0.0

    def load_from_benchmark(self, benchmark_file: Path):
        """
        Load data from benchmark results JSON.

        Args:
            benchmark_file: Path to benchmark_adaptive_results.json
        """
        with open(benchmark_file, 'r') as f:
            data = json.load(f)

        # Extract adaptive results
        adaptive_results = [
            r for r in data.get("results", [])
            if r.get("mode", "").startswith("adaptive")
        ]

        if not adaptive_results:
            print("[WARN] No adaptive results found in benchmark file")
            return

        # Use first adaptive result
        result = adaptive_results[0]

        print(f"[VISUALIZER] Loaded: {result['name']}")
        print(f"[VISUALIZER] Total rules: {result['total_rules']}")
        print(f"[VISUALIZER] Total time: {result['total_time']:.3f}s")
        print(f"[VISUALIZER] Work steals: {result['total_steals']}")

        return result

    def print_utilization_chart(self, result: Dict[str, Any]):
        """
        Print worker utilization bar chart.

        Args:
            result: Benchmark result dictionary
        """
        print("\n" + "="*70)
        print("[WORKER UTILIZATION]")
        print("="*70)

        batch_workers = result.get("batch_workers", [])
        batch_utilizations = result.get("batch_utilizations", [])
        batch_times = result.get("batch_times", [])

        if not batch_utilizations:
            print("[INFO] No utilization data available")
            return

        # Print batch-by-batch utilization
        print(f"\n{'Batch':<6} {'Workers':<8} {'Util%':<8} {'Time':<10} {'Chart':<40}")
        print("-"*70)

        for i, util in enumerate(batch_utilizations):
            workers = batch_workers[i] if i < len(batch_workers) else 0
            time_s = batch_times[i] if i < len(batch_times) else 0.0

            # Create bar chart (40 chars = 100%)
            bar_length = int(util / 100 * 40)
            bar = "#" * bar_length + "." * (40 - bar_length)

            print(f"{i:<6} {workers:<8} {util:>5.1f}%  {time_s:>7.3f}s  [{bar}]")

        # Overall statistics
        avg_util = result.get("avg_worker_utilization", 0.0)
        min_util = result.get("min_worker_utilization", 0.0)
        max_util = result.get("max_worker_utilization", 0.0)
        variance = result.get("utilization_variance", 0.0)

        print("-"*70)
        print(f"Average: {avg_util:.1f}%")
        print(f"Range: {min_util:.1f}% - {max_util:.1f}%")
        print(f"Variance: {variance:.1f}%")
        print("="*70)

    def print_work_stealing_analysis(self, result: Dict[str, Any]):
        """
        Print work stealing activity analysis.

        Args:
            result: Benchmark result dictionary
        """
        print("\n" + "="*70)
        print("[WORK STEALING ANALYSIS]")
        print("="*70)

        total_tasks = result.get("total_rules", 0)
        total_steals = result.get("total_steals", 0)
        steal_pct = result.get("steal_percentage", 0.0)

        print(f"\nTotal Tasks: {total_tasks}")
        print(f"Work Steals: {total_steals} ({steal_pct:.1f}%)")

        if total_tasks > 0:
            # Show steal distribution
            print(f"\nSteal Rate by Batch:")
            batch_workers = result.get("batch_workers", [])
            batch_times = result.get("batch_times", [])

            # Estimate steals per batch (proportional to workers and time)
            total_worker_time = sum(
                w * t for w, t in zip(batch_workers, batch_times)
            )

            for i, (workers, time_s) in enumerate(zip(batch_workers, batch_times)):
                batch_work = workers * time_s
                if total_worker_time > 0:
                    estimated_steals = int(total_steals * batch_work / total_worker_time)
                else:
                    estimated_steals = 0

                # Bar chart
                if total_steals > 0:
                    bar_length = int(estimated_steals / total_steals * 40)
                else:
                    bar_length = 0

                bar = "#" * bar_length + "." * (40 - bar_length)

                print(f"  Batch {i}: ~{estimated_steals:3d} steals  [{bar}]")

        print("\n[INTERPRETATION]")
        if steal_pct < 5:
            print("  Low work stealing - workers are well-balanced from the start")
        elif steal_pct < 15:
            print("  Moderate work stealing - adaptive load balancing is working")
        elif steal_pct < 30:
            print("  High work stealing - significant load imbalance detected")
        else:
            print("  Very high work stealing - may indicate poor initial distribution")

        print("="*70)

    def print_efficiency_breakdown(self, result: Dict[str, Any]):
        """
        Print efficiency breakdown and comparison.

        Args:
            result: Benchmark result dictionary
        """
        print("\n" + "="*70)
        print("[EFFICIENCY BREAKDOWN]")
        print("="*70)

        avg_util = result.get("avg_worker_utilization", 0.0)
        overall_eff = result.get("overall_efficiency", 0.0)
        total_time = result.get("total_time", 0.0)
        workers = result.get("workers", 0)

        # Calculate waste
        ideal_time = total_time
        actual_worker_time = total_time * workers
        utilized_time = actual_worker_time * (avg_util / 100)
        wasted_time = actual_worker_time - utilized_time

        print(f"\nWorker Configuration:")
        print(f"  Base workers: {workers}")
        print(f"  Total execution time: {total_time:.3f}s")
        print(f"  Total worker-seconds: {actual_worker_time:.3f}s")

        print(f"\nTime Utilization:")
        print(f"  Productive work: {utilized_time:.3f}s ({avg_util:.1f}%)")
        print(f"  Idle/overhead: {wasted_time:.3f}s ({100-avg_util:.1f}%)")

        # Visualize breakdown
        work_bar = int(avg_util / 100 * 50)
        idle_bar = 50 - work_bar

        print(f"\n  [{'#'*work_bar}{'.'*idle_bar}]")
        print(f"   {'Work':<{work_bar}}{'Idle':<{idle_bar}}")

        print(f"\nEfficiency Metrics:")
        print(f"  Worker utilization: {avg_util:.1f}%")
        print(f"  Overall efficiency: {overall_eff:.1f}%")

        # Compare to targets
        print(f"\nTarget Comparison:")
        target_util = 98.0
        target_idle = 2.0
        actual_idle = 100 - avg_util

        util_status = "PASS" if avg_util >= target_util else "NEEDS IMPROVEMENT"
        idle_status = "PASS" if actual_idle <= target_idle else "NEEDS IMPROVEMENT"

        print(f"  Worker utilization: {avg_util:.1f}% (target: {target_util:.1f}%) [{util_status}]")
        print(f"  Idle time: {actual_idle:.1f}% (target: <{target_idle:.1f}%) [{idle_status}]")

        print("="*70)

    def print_batch_timeline(self, result: Dict[str, Any]):
        """
        Print timeline of batch execution.

        Args:
            result: Benchmark result dictionary
        """
        print("\n" + "="*70)
        print("[BATCH EXECUTION TIMELINE]")
        print("="*70)

        batch_times = result.get("batch_times", [])
        batch_workers = result.get("batch_workers", [])
        total_time = result.get("total_time", 0.0)

        if not batch_times:
            print("[INFO] No batch data available")
            return

        # Calculate cumulative times
        cumulative_time = 0.0

        print(f"\n{'Batch':<6} {'Workers':<8} {'Duration':<10} {'Cumulative':<12} {'Timeline':<30}")
        print("-"*70)

        for i, (time_s, workers) in enumerate(zip(batch_times, batch_workers)):
            # Timeline bar (30 chars = total_time)
            if total_time > 0:
                bar_length = int(time_s / total_time * 30)
            else:
                bar_length = 0

            bar = "=" * bar_length

            cumulative_time += time_s

            print(f"{i:<6} {workers:<8} {time_s:>7.3f}s  {cumulative_time:>9.3f}s  [{bar}]")

        print("-"*70)
        print(f"Total: {total_time:.3f}s")
        print("="*70)

    def print_comparison_with_fixed(self, benchmark_file: Path):
        """
        Print side-by-side comparison with fixed worker mode.

        Args:
            benchmark_file: Path to benchmark results
        """
        with open(benchmark_file, 'r') as f:
            data = json.load(f)

        results = data.get("results", [])

        fixed_result = next((r for r in results if r.get("mode") == "fixed"), None)
        adaptive_result = next((r for r in results if r.get("mode", "").startswith("adaptive")), None)

        if not fixed_result or not adaptive_result:
            print("[WARN] Both fixed and adaptive results needed for comparison")
            return

        print("\n" + "="*70)
        print("[FIXED vs ADAPTIVE COMPARISON]")
        print("="*70)

        # Calculate improvements
        time_improvement = (1 - adaptive_result["total_time"] / fixed_result["total_time"]) * 100
        util_improvement = adaptive_result.get("avg_worker_utilization", 0) - fixed_result.get("avg_worker_utilization", 0)

        print(f"\n{'Metric':<30} {'Fixed':<15} {'Adaptive':<15} {'Improvement':<15}")
        print("-"*70)

        # Time
        print(f"{'Total Time':<30} {fixed_result['total_time']:>12.3f}s  "
              f"{adaptive_result['total_time']:>12.3f}s  {time_improvement:>12.1f}%")

        # Utilization
        fixed_util = fixed_result.get("avg_worker_utilization", 0)
        adaptive_util = adaptive_result.get("avg_worker_utilization", 0)
        print(f"{'Worker Utilization':<30} {fixed_util:>12.1f}%  "
              f"{adaptive_util:>12.1f}%  {util_improvement:>12.1f}%")

        # Efficiency
        fixed_eff = fixed_result.get("overall_efficiency", 0)
        adaptive_eff = adaptive_result.get("overall_efficiency", 0)
        eff_improvement = adaptive_eff - fixed_eff
        print(f"{'Overall Efficiency':<30} {fixed_eff:>12.1f}%  "
              f"{adaptive_eff:>12.1f}%  {eff_improvement:>12.1f}%")

        # Throughput
        fixed_throughput = fixed_result.get("throughput", 0)
        adaptive_throughput = adaptive_result.get("throughput", 0)
        throughput_improvement = (adaptive_throughput / fixed_throughput - 1) * 100 if fixed_throughput > 0 else 0
        print(f"{'Throughput (rules/s)':<30} {fixed_throughput:>12.1f}   "
              f"{adaptive_throughput:>12.1f}   {throughput_improvement:>12.1f}%")

        # Work stealing (adaptive only)
        steals = adaptive_result.get("total_steals", 0)
        steal_pct = adaptive_result.get("steal_percentage", 0)
        print(f"{'Work Stealing':<30} {'N/A':<15} {steals:>6d} ({steal_pct:.1f}%)  {'N/A':<15}")

        print("="*70)

        # Success criteria
        print("\n[SUCCESS CRITERIA]")
        print("-"*70)

        criteria = [
            ("Speedup: >15% faster", time_improvement >= 15, f"{time_improvement:.1f}%"),
            ("Utilization: >98%", adaptive_util >= 98, f"{adaptive_util:.1f}%"),
            ("Idle time: <2%", (100 - adaptive_util) <= 2, f"{100-adaptive_util:.1f}%"),
            ("Load variance: <10%", adaptive_result.get("utilization_variance", 0) < 10, f"{adaptive_result.get('utilization_variance', 0):.1f}%"),
        ]

        for criterion, passed, value in criteria:
            status = "[PASS]" if passed else "[FAIL]"
            print(f"  {status} {criterion:<35} (actual: {value})")

        print("="*70)


# ============================================================
# MAIN
# ============================================================

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Work Stealing Visualization Tool")
    parser.add_argument('--benchmark', type=str, help='Path to benchmark results JSON')
    parser.add_argument('--all', action='store_true', help='Show all visualizations')
    parser.add_argument('--utilization', action='store_true', help='Show utilization chart')
    parser.add_argument('--stealing', action='store_true', help='Show work stealing analysis')
    parser.add_argument('--efficiency', action='store_true', help='Show efficiency breakdown')
    parser.add_argument('--timeline', action='store_true', help='Show batch timeline')
    parser.add_argument('--comparison', action='store_true', help='Show fixed vs adaptive comparison')

    args = parser.parse_args()

    # Find benchmark file
    if args.benchmark:
        benchmark_file = Path(args.benchmark)
    else:
        benchmark_file = Path(__file__).parent / "benchmark_adaptive_results.json"

    if not benchmark_file.exists():
        print(f"[ERROR] Benchmark file not found: {benchmark_file}")
        print("[INFO] Run benchmark_adaptive.py first to generate results")
        return 1

    print("="*70)
    print("[WORK STEALING VISUALIZER]")
    print("="*70)
    print(f"Benchmark file: {benchmark_file}")

    # Create visualizer
    visualizer = WorkStealingVisualizer()
    result = visualizer.load_from_benchmark(benchmark_file)

    if not result:
        print("[ERROR] Failed to load benchmark data")
        return 1

    # Determine what to show
    show_all = args.all or not any([
        args.utilization, args.stealing, args.efficiency, args.timeline, args.comparison
    ])

    if show_all or args.utilization:
        visualizer.print_utilization_chart(result)

    if show_all or args.stealing:
        visualizer.print_work_stealing_analysis(result)

    if show_all or args.efficiency:
        visualizer.print_efficiency_breakdown(result)

    if show_all or args.timeline:
        visualizer.print_batch_timeline(result)

    if show_all or args.comparison:
        visualizer.print_comparison_with_fixed(benchmark_file)

    print("\n[OK] Visualization complete!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
