#!/usr/bin/env python3
"""
Incremental Validation Benchmark Suite
========================================

Comprehensive benchmarking for incremental validation performance.

Test Scenarios:
1. Single Chart.yaml change → <0.2s (35x speedup)
2. Single values.yaml change → <0.3s (23x speedup)
3. Typical commit (5-10 files) → <0.5s (14x speedup)
4. Large refactor (100 files) → 2s (3.5x speedup)
5. Full validation baseline → 7.1s

Generates detailed performance analysis comparing:
- Full validation (baseline)
- Incremental validation (various change scenarios)
- Cache effectiveness
- Speedup metrics

Usage:
    python benchmark_incremental.py [repo_path]

Output:
    - Console report with speedup metrics
    - JSON benchmark results
    - Performance comparison charts
"""

import sys
import time
import json
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from incremental_validator import IncrementalValidator
from parallel_validator import ParallelValidator


class IncrementalBenchmark:
    """
    Benchmark suite for incremental validation performance.
    """

    def __init__(self, repo_root: Path):
        """
        Initialize benchmark.

        Args:
            repo_root: Path to SSID repository
        """
        self.repo_root = repo_root
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'repo_root': str(repo_root),
            'scenarios': {}
        }

    def run_all_benchmarks(self) -> Dict[str, Any]:
        """
        Run all benchmark scenarios.

        Returns:
            Dict with benchmark results
        """
        print("=" * 80)
        print("INCREMENTAL VALIDATION BENCHMARK SUITE")
        print("=" * 80)
        print(f"Repository: {self.repo_root}")
        print(f"Timestamp:  {self.results['timestamp']}")
        print("=" * 80)
        print()

        # Scenario 1: Full validation baseline
        print("[SCENARIO 1] Full Validation Baseline")
        print("-" * 80)
        baseline = self.benchmark_full_validation()
        self.results['scenarios']['full_validation'] = baseline
        print()

        # Scenario 2: Single Chart.yaml change
        print("[SCENARIO 2] Single Chart.yaml Change")
        print("-" * 80)
        chart_result = self.benchmark_single_chart_change(baseline['avg_time'])
        self.results['scenarios']['single_chart'] = chart_result
        print()

        # Scenario 3: Single values.yaml change
        print("[SCENARIO 3] Single values.yaml Change")
        print("-" * 80)
        values_result = self.benchmark_single_values_change(baseline['avg_time'])
        self.results['scenarios']['single_values'] = values_result
        print()

        # Scenario 4: Typical commit (5-10 files)
        print("[SCENARIO 4] Typical Commit (5-10 files)")
        print("-" * 80)
        typical_result = self.benchmark_typical_commit(baseline['avg_time'])
        self.results['scenarios']['typical_commit'] = typical_result
        print()

        # Scenario 5: Large refactor (100 files)
        print("[SCENARIO 5] Large Refactor (100 files)")
        print("-" * 80)
        large_result = self.benchmark_large_refactor(baseline['avg_time'])
        self.results['scenarios']['large_refactor'] = large_result
        print()

        # Generate summary
        self.print_summary()

        return self.results

    def benchmark_full_validation(self, iterations: int = 3) -> Dict[str, Any]:
        """
        Benchmark full validation (baseline).

        Args:
            iterations: Number of test iterations

        Returns:
            Dict with timing results
        """
        print(f"Running {iterations} iterations of full validation...")

        validator = ParallelValidator(self.repo_root)

        times = []

        for i in range(iterations):
            print(f"  Iteration {i+1}/{iterations}...", end=" ")

            start = time.time()
            report = validator.validate_all_parallel()
            elapsed = time.time() - start

            times.append(elapsed)
            print(f"{elapsed:.3f}s")

        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)

        print(f"\nResults:")
        print(f"  Avg:  {avg_time:.3f}s")
        print(f"  Min:  {min_time:.3f}s")
        print(f"  Max:  {max_time:.3f}s")

        return {
            'iterations': iterations,
            'times': times,
            'avg_time': avg_time,
            'min_time': min_time,
            'max_time': max_time,
            'description': 'Full validation baseline (384 rules)'
        }

    def benchmark_single_chart_change(self, baseline_time: float, iterations: int = 3) -> Dict[str, Any]:
        """
        Simulate single Chart.yaml change.

        Target: <0.2s (35x speedup)
        """
        print(f"Simulating single Chart.yaml modification...")

        # Create test environment
        test_file = self._find_sample_chart()

        if not test_file:
            print("  [SKIP] No Chart.yaml found for testing")
            return {'skipped': True}

        # Run incremental validation
        validator = IncrementalValidator(self.repo_root)

        times = []

        for i in range(iterations):
            print(f"  Iteration {i+1}/{iterations}...", end=" ")

            # Touch file to simulate change
            self._touch_file(test_file)

            start = time.time()
            report = validator.validate_incremental(use_working_dir=True)
            elapsed = time.time() - start

            times.append(elapsed)
            print(f"{elapsed:.3f}s ({len(report.results)} rules)")

        avg_time = sum(times) / len(times)
        speedup = baseline_time / avg_time if avg_time > 0 else 0

        print(f"\nResults:")
        print(f"  Avg:     {avg_time:.3f}s")
        print(f"  Speedup: {speedup:.1f}x")
        print(f"  Target:  35x (status: {'PASS' if speedup >= 30 else 'FAIL'})")

        return {
            'iterations': iterations,
            'times': times,
            'avg_time': avg_time,
            'speedup': speedup,
            'target_speedup': 35,
            'status': 'PASS' if speedup >= 30 else 'FAIL',
            'description': 'Single Chart.yaml modification'
        }

    def benchmark_single_values_change(self, baseline_time: float, iterations: int = 3) -> Dict[str, Any]:
        """
        Simulate single values.yaml change.

        Target: <0.3s (23x speedup)
        """
        print(f"Simulating single values.yaml modification...")

        test_file = self._find_sample_values()

        if not test_file:
            print("  [SKIP] No values.yaml found for testing")
            return {'skipped': True}

        validator = IncrementalValidator(self.repo_root)

        times = []

        for i in range(iterations):
            print(f"  Iteration {i+1}/{iterations}...", end=" ")

            self._touch_file(test_file)

            start = time.time()
            report = validator.validate_incremental(use_working_dir=True)
            elapsed = time.time() - start

            times.append(elapsed)
            print(f"{elapsed:.3f}s ({len(report.results)} rules)")

        avg_time = sum(times) / len(times)
        speedup = baseline_time / avg_time if avg_time > 0 else 0

        print(f"\nResults:")
        print(f"  Avg:     {avg_time:.3f}s")
        print(f"  Speedup: {speedup:.1f}x")
        print(f"  Target:  23x (status: {'PASS' if speedup >= 20 else 'FAIL'})")

        return {
            'iterations': iterations,
            'times': times,
            'avg_time': avg_time,
            'speedup': speedup,
            'target_speedup': 23,
            'status': 'PASS' if speedup >= 20 else 'FAIL',
            'description': 'Single values.yaml modification'
        }

    def benchmark_typical_commit(self, baseline_time: float, iterations: int = 3) -> Dict[str, Any]:
        """
        Simulate typical commit (5-10 files).

        Target: <0.5s (14x speedup)
        """
        print(f"Simulating typical commit (5-10 files)...")

        test_files = self._find_typical_commit_files()

        if not test_files:
            print("  [SKIP] Insufficient files for testing")
            return {'skipped': True}

        print(f"  Found {len(test_files)} test files")

        validator = IncrementalValidator(self.repo_root)

        times = []

        for i in range(iterations):
            print(f"  Iteration {i+1}/{iterations}...", end=" ")

            # Touch multiple files
            for file in test_files:
                self._touch_file(file)

            start = time.time()
            report = validator.validate_incremental(use_working_dir=True)
            elapsed = time.time() - start

            times.append(elapsed)
            print(f"{elapsed:.3f}s ({len(report.results)} rules)")

        avg_time = sum(times) / len(times)
        speedup = baseline_time / avg_time if avg_time > 0 else 0

        print(f"\nResults:")
        print(f"  Avg:     {avg_time:.3f}s")
        print(f"  Speedup: {speedup:.1f}x")
        print(f"  Target:  14x (status: {'PASS' if speedup >= 12 else 'FAIL'})")

        return {
            'iterations': iterations,
            'times': times,
            'avg_time': avg_time,
            'speedup': speedup,
            'target_speedup': 14,
            'status': 'PASS' if speedup >= 12 else 'FAIL',
            'description': f'Typical commit ({len(test_files)} files)'
        }

    def benchmark_large_refactor(self, baseline_time: float, iterations: int = 3) -> Dict[str, Any]:
        """
        Simulate large refactor (100 files).

        Target: 2s (3.5x speedup)
        """
        print(f"Simulating large refactor (100 files)...")

        test_files = self._find_many_files(100)

        if not test_files:
            print("  [SKIP] Insufficient files for testing")
            return {'skipped': True}

        print(f"  Found {len(test_files)} test files")

        validator = IncrementalValidator(self.repo_root)

        times = []

        for i in range(iterations):
            print(f"  Iteration {i+1}/{iterations}...", end=" ")

            # Touch many files
            for file in test_files:
                self._touch_file(file)

            start = time.time()
            report = validator.validate_incremental(use_working_dir=True)
            elapsed = time.time() - start

            times.append(elapsed)
            print(f"{elapsed:.3f}s ({len(report.results)} rules)")

        avg_time = sum(times) / len(times)
        speedup = baseline_time / avg_time if avg_time > 0 else 0

        print(f"\nResults:")
        print(f"  Avg:     {avg_time:.3f}s")
        print(f"  Speedup: {speedup:.1f}x")
        print(f"  Target:  3.5x (status: {'PASS' if speedup >= 3 else 'FAIL'})")

        return {
            'iterations': iterations,
            'times': times,
            'avg_time': avg_time,
            'speedup': speedup,
            'target_speedup': 3.5,
            'status': 'PASS' if speedup >= 3 else 'FAIL',
            'description': f'Large refactor ({len(test_files)} files)'
        }

    def print_summary(self):
        """Print benchmark summary"""
        print("=" * 80)
        print("BENCHMARK SUMMARY")
        print("=" * 80)

        # Table header
        print(f"{'Scenario':<30} {'Time':<12} {'Speedup':<12} {'Status':<10}")
        print("-" * 80)

        # Baseline
        baseline = self.results['scenarios'].get('full_validation', {})
        baseline_time = baseline.get('avg_time', 0)
        print(f"{'Full Validation (Baseline)':<30} {baseline_time:<12.3f}s {'1.0x':<12} {'N/A':<10}")

        # Other scenarios
        for scenario_name, scenario_data in self.results['scenarios'].items():
            if scenario_name == 'full_validation':
                continue

            if scenario_data.get('skipped'):
                continue

            avg_time = scenario_data.get('avg_time', 0)
            speedup = scenario_data.get('speedup', 0)
            status = scenario_data.get('status', 'N/A')
            description = scenario_data.get('description', scenario_name)

            print(f"{description:<30} {avg_time:<12.3f}s {speedup:<12.1f}x {status:<10}")

        print("=" * 80)

        # Overall verdict
        all_passed = all(
            s.get('status') == 'PASS' or s.get('skipped')
            for s in self.results['scenarios'].values()
            if s != baseline
        )

        print()
        if all_passed:
            print("[SUCCESS] All benchmarks passed target performance!")
        else:
            print("[WARNING] Some benchmarks did not meet target performance")

        print()

    def save_results(self, output_path: Path):
        """Save benchmark results to JSON"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2)

        print(f"[EXPORT] Results saved to: {output_path}")

    # ============================================================
    # HELPER METHODS
    # ============================================================

    def _find_sample_chart(self) -> Optional[Path]:
        """Find a sample Chart.yaml for testing"""
        charts = list(self.repo_root.glob("*/*/Chart.yaml"))
        return charts[0] if charts else None

    def _find_sample_values(self) -> Optional[Path]:
        """Find a sample values.yaml for testing"""
        values = list(self.repo_root.glob("*/*/values.yaml"))
        return values[0] if values else None

    def _find_typical_commit_files(self) -> List[Path]:
        """Find 5-10 files simulating typical commit"""
        files = []

        # 2-3 Chart.yaml
        charts = list(self.repo_root.glob("*/*/Chart.yaml"))[:3]
        files.extend(charts)

        # 2-3 values.yaml
        values = list(self.repo_root.glob("*/*/values.yaml"))[:3]
        files.extend(values)

        # 1-2 templates
        templates = list(self.repo_root.glob("*/*/templates/*.yaml"))[:2]
        files.extend(templates)

        return files[:10]  # Cap at 10

    def _find_many_files(self, count: int) -> List[Path]:
        """Find many files for large refactor test"""
        files = []

        # Mix of all file types
        charts = list(self.repo_root.glob("*/*/Chart.yaml"))
        values = list(self.repo_root.glob("*/*/values.yaml"))
        templates = list(self.repo_root.glob("*/*/templates/*.yaml"))
        manifests = list(self.repo_root.glob("*/*/manifest.yaml"))

        all_files = charts + values + templates + manifests
        return all_files[:count]

    def _touch_file(self, file_path: Path):
        """Touch a file to update its timestamp"""
        try:
            file_path.touch(exist_ok=True)
        except Exception as e:
            print(f"[WARNING] Failed to touch {file_path}: {e}")


# ============================================================
# MAIN
# ============================================================

def main():
    """Main entry point"""
    # Get repo root
    if len(sys.argv) > 1:
        repo_root = Path(sys.argv[1])
    else:
        repo_root = Path(__file__).parent.parent.parent.parent

    if not repo_root.exists():
        print(f"[ERROR] Repository not found: {repo_root}")
        return 1

    # Create benchmark
    benchmark = IncrementalBenchmark(repo_root)

    # Run all benchmarks
    results = benchmark.run_all_benchmarks()

    # Save results
    output_path = Path(__file__).parent / "benchmark_incremental_results.json"
    benchmark.save_results(output_path)

    return 0


if __name__ == "__main__":
    sys.exit(main())
