#!/usr/bin/env python3
"""
Benchmark Result Caching Performance
====================================

Comprehensive benchmarking suite for result caching implementation.

Measures:
- First run (cold cache) vs. cached run speedup
- Cache hit/miss rates
- File hash computation overhead
- Cache invalidation performance
- Memory and disk usage

Expected Results:
- First run: ~15s (with parallel + filesystem cache)
- Cached run (no changes): <1s (15-20x speedup)
- Partial invalidation: Only affected rules re-validated
- Cache overhead: <100ms for hash computation
- Cache size: <10MB for 384 rules

Usage:
    python benchmark_result_caching.py [repo_root]
"""

import time
import sys
from pathlib import Path
from typing import Dict, List, Any
import json

# Import validators
try:
    from cached_result_validator import CachedResultValidator
    from cached_validator import CachedSoTValidator
    from sot_validator_core import SoTValidator
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent))
    from cached_result_validator import CachedResultValidator
    from cached_validator import CachedSoTValidator
    from sot_validator_core import SoTValidator


class ResultCacheBenchmark:
    """
    Benchmark suite for result caching performance.

    Compares three validator implementations:
    1. Base SoTValidator (no caching)
    2. CachedSoTValidator (filesystem cache only)
    3. CachedResultValidator (filesystem + result cache)
    """

    def __init__(self, repo_root: Path):
        """
        Initialize benchmark suite.

        Args:
            repo_root: Path to SSID repository root
        """
        self.repo_root = Path(repo_root)

        # Create validators
        print("[INIT] Creating validators...\n")

        # Base validator (no caching)
        self.base_validator = SoTValidator(repo_root)

        # Filesystem cache validator
        self.fs_validator = CachedSoTValidator(repo_root, cache_ttl=3600)

        # Result cache validator
        self.result_validator = CachedResultValidator(
            repo_root,
            fs_cache_ttl=3600,
            result_cache_ttl=3600,
            enable_result_cache=True
        )

        # Clear caches to start fresh
        self.result_validator.invalidate_all_caches()

    # ============================================================
    # BENCHMARK: COLD VS WARM CACHE
    # ============================================================

    def benchmark_cold_vs_warm(self, iterations: int = 3) -> Dict[str, Any]:
        """
        Benchmark cold (first run) vs. warm (cached) performance.

        Args:
            iterations: Number of warm cache iterations

        Returns:
            Dict with benchmark results
        """
        print("\n" + "="*60)
        print("BENCHMARK 1: Cold vs. Warm Cache Performance")
        print("="*60)

        # Clear result cache to ensure cold start
        self.result_validator.invalidate_result_cache()

        times = []

        # Cold run (first iteration)
        print("\n[COLD RUN] First validation (cache cold)...")
        start = time.time()
        results = self.result_validator.validate_all_ar_rules()
        cold_time = time.time() - start
        times.append(cold_time)

        print(f"[RESULT] Cold run: {cold_time:.3f}s")
        print(f"         {len(results)} rules validated\n")

        # Warm runs (cached)
        warm_times = []
        for i in range(iterations - 1):
            print(f"[WARM RUN {i+1}] Validation with warm cache...")
            start = time.time()
            results = self.result_validator.validate_all_ar_rules()
            warm_time = time.time() - start
            warm_times.append(warm_time)
            times.append(warm_time)

            print(f"[RESULT] Warm run {i+1}: {warm_time:.3f}s ({warm_time*1000:.1f}ms)")

        avg_warm = sum(warm_times) / len(warm_times) if warm_times else 0
        speedup = cold_time / avg_warm if avg_warm > 0 else 0

        print(f"\n[SUMMARY]")
        print(f"  Cold run:         {cold_time:.3f}s")
        print(f"  Avg warm run:     {avg_warm:.3f}s ({avg_warm*1000:.1f}ms)")
        print(f"  Speedup:          {speedup:.1f}x")
        print(f"  Time saved:       {cold_time - avg_warm:.3f}s per run")

        return {
            "cold_time": cold_time,
            "warm_times": warm_times,
            "avg_warm_time": avg_warm,
            "speedup": speedup,
            "time_saved": cold_time - avg_warm
        }

    # ============================================================
    # BENCHMARK: CACHE HIT/MISS RATES
    # ============================================================

    def benchmark_cache_hit_rates(self) -> Dict[str, Any]:
        """
        Measure cache hit/miss rates across validations.

        Returns:
            Dict with cache statistics
        """
        print("\n" + "="*60)
        print("BENCHMARK 2: Cache Hit/Miss Rates")
        print("="*60)

        # Clear caches and run twice
        self.result_validator.invalidate_result_cache()

        print("\n[RUN 1] First run (expect all misses)...")
        self.result_validator.validate_all_ar_rules()
        stats1 = self.result_validator.get_result_cache_stats()

        print(f"[STATS] Session hits:   {stats1['session_hits']}")
        print(f"        Session misses: {stats1['session_misses']}")
        print(f"        Hit rate:       {stats1['session_hit_rate']}")

        print("\n[RUN 2] Second run (expect all hits)...")
        self.result_validator.validate_all_ar_rules()
        stats2 = self.result_validator.get_result_cache_stats()

        print(f"[STATS] Session hits:   {stats2['session_hits']}")
        print(f"        Session misses: {stats2['session_misses']}")
        print(f"        Hit rate:       {stats2['session_hit_rate']}")

        # Calculate hit rate for second run only
        run2_hits = stats2['session_hits'] - stats1['session_hits']
        run2_misses = stats2['session_misses'] - stats1['session_misses']
        run2_total = run2_hits + run2_misses
        run2_hit_rate = (run2_hits / run2_total * 100) if run2_total > 0 else 0

        print(f"\n[RUN 2 ISOLATED]")
        print(f"  Hits:      {run2_hits}")
        print(f"  Misses:    {run2_misses}")
        print(f"  Hit rate:  {run2_hit_rate:.1f}%")

        return {
            "run1_stats": stats1,
            "run2_stats": stats2,
            "run2_hit_rate": run2_hit_rate,
            "run2_hits": run2_hits,
            "run2_misses": run2_misses
        }

    # ============================================================
    # BENCHMARK: FILE HASH OVERHEAD
    # ============================================================

    def benchmark_hash_overhead(self) -> Dict[str, Any]:
        """
        Measure file hash computation overhead.

        Returns:
            Dict with hash computation statistics
        """
        print("\n" + "="*60)
        print("BENCHMARK 3: File Hash Computation Overhead")
        print("="*60)

        # Get a sample of files to hash
        yaml_files = list(self.repo_root.glob('**/*.yaml'))[:50]  # Sample 50 files

        print(f"\n[HASH TEST] Hashing {len(yaml_files)} YAML files...")

        start = time.time()
        hashes = []

        for file_path in yaml_files:
            if file_path.exists():
                hash_val = self.result_validator.result_cache._compute_file_hash(file_path)
                hashes.append(hash_val)

        elapsed = time.time() - start

        avg_time = elapsed / len(yaml_files) if yaml_files else 0

        print(f"\n[RESULT]")
        print(f"  Files hashed:     {len(hashes)}")
        print(f"  Total time:       {elapsed:.3f}s")
        print(f"  Avg per file:     {avg_time*1000:.3f}ms")
        print(f"  Throughput:       {len(hashes)/elapsed:.1f} files/sec" if elapsed > 0 else "")

        return {
            "files_hashed": len(hashes),
            "total_time": elapsed,
            "avg_time_per_file": avg_time,
            "throughput": len(hashes)/elapsed if elapsed > 0 else 0
        }

    # ============================================================
    # BENCHMARK: CACHE INVALIDATION
    # ============================================================

    def benchmark_invalidation(self) -> Dict[str, Any]:
        """
        Measure cache invalidation performance.

        Returns:
            Dict with invalidation statistics
        """
        print("\n" + "="*60)
        print("BENCHMARK 4: Cache Invalidation Performance")
        print("="*60)

        # Warm up cache
        print("\n[SETUP] Warming cache...")
        self.result_validator.invalidate_result_cache()
        self.result_validator.validate_all_ar_rules()

        # Test single rule invalidation
        print("\n[TEST 1] Single rule invalidation...")
        start = time.time()
        self.result_validator.invalidate_result_cache("AR001")
        single_time = time.time() - start

        print(f"[RESULT] Single invalidation: {single_time*1000:.3f}ms")

        # Test full cache invalidation
        print("\n[TEST 2] Full cache invalidation...")
        start = time.time()
        self.result_validator.invalidate_result_cache()
        full_time = time.time() - start

        print(f"[RESULT] Full invalidation: {full_time*1000:.3f}ms")

        # Test re-validation after invalidation
        print("\n[TEST 3] Re-validation after invalidation...")
        start = time.time()
        self.result_validator.validate_ar001()  # Should be cache miss
        revalidate_time = time.time() - start

        print(f"[RESULT] Re-validation: {revalidate_time*1000:.3f}ms")

        return {
            "single_invalidation_ms": single_time * 1000,
            "full_invalidation_ms": full_time * 1000,
            "revalidation_ms": revalidate_time * 1000
        }

    # ============================================================
    # BENCHMARK: CACHE SIZE
    # ============================================================

    def benchmark_cache_size(self) -> Dict[str, Any]:
        """
        Measure cache storage requirements.

        Returns:
            Dict with cache size statistics
        """
        print("\n" + "="*60)
        print("BENCHMARK 5: Cache Storage Requirements")
        print("="*60)

        # Ensure cache is populated
        print("\n[SETUP] Populating cache...")
        self.result_validator.invalidate_result_cache()
        self.result_validator.validate_all_ar_rules()

        # Get cache stats
        stats = self.result_validator.get_result_cache_stats()

        cache_size_mb = stats.get('cache_size_mb', 0)
        total_entries = stats.get('total_entries', 0)

        # Calculate per-entry size
        per_entry_kb = (cache_size_mb * 1024 / total_entries) if total_entries > 0 else 0

        print(f"\n[RESULT]")
        print(f"  Cache file:       {self.result_validator.result_cache.cache_file}")
        print(f"  Total size:       {cache_size_mb:.3f} MB")
        print(f"  Total entries:    {total_entries}")
        print(f"  Avg per entry:    {per_entry_kb:.2f} KB")
        print(f"  Estimated 384:    {per_entry_kb * 384 / 1024:.2f} MB")

        return {
            "cache_size_mb": cache_size_mb,
            "total_entries": total_entries,
            "per_entry_kb": per_entry_kb,
            "estimated_full_cache_mb": per_entry_kb * 384 / 1024
        }

    # ============================================================
    # BENCHMARK: COMPARISON TABLE
    # ============================================================

    def benchmark_validator_comparison(self) -> Dict[str, Any]:
        """
        Compare all three validator implementations.

        Returns:
            Dict with comparison results
        """
        print("\n" + "="*60)
        print("BENCHMARK 6: Validator Implementation Comparison")
        print("="*60)

        results = {}

        # Note: Base validator is too slow for full benchmark
        # We'll only benchmark AR001-AR010 for all three

        print("\n[COMPARING] AR001-AR010 validation across 3 implementations...")

        # 1. Base validator (no caching)
        print("\n[1/3] Base SoTValidator (no caching)...")
        start = time.time()
        base_results = [
            self.base_validator.validate_ar001(),
            self.base_validator.validate_ar002(),
            self.base_validator.validate_ar003(),
            self.base_validator.validate_ar004(),
            self.base_validator.validate_ar005(),
            self.base_validator.validate_ar006(),
            self.base_validator.validate_ar007(),
            self.base_validator.validate_ar008(),
            self.base_validator.validate_ar009(),
            self.base_validator.validate_ar010(),
        ]
        base_time = time.time() - start
        results['base'] = base_time
        print(f"      Time: {base_time:.3f}s")

        # 2. Filesystem cache validator
        print("\n[2/3] CachedSoTValidator (filesystem cache)...")
        self.fs_validator.invalidate_cache()
        start = time.time()
        fs_results = [
            self.fs_validator.validate_ar001(),
            self.fs_validator.validate_ar002(),
            self.fs_validator.validate_ar003(),
            self.fs_validator.validate_ar004(),
            self.fs_validator.validate_ar005(),
            self.fs_validator.validate_ar006(),
            self.fs_validator.validate_ar007(),
            self.fs_validator.validate_ar008(),
            self.fs_validator.validate_ar009(),
            self.fs_validator.validate_ar010(),
        ]
        fs_time = time.time() - start
        results['filesystem'] = fs_time
        print(f"      Time: {fs_time:.3f}s")

        # 3. Result cache validator (cold)
        print("\n[3/3] CachedResultValidator (cold cache)...")
        self.result_validator.invalidate_all_caches()
        start = time.time()
        result_cold = self.result_validator.validate_all_ar_rules()
        result_cold_time = time.time() - start
        results['result_cold'] = result_cold_time
        print(f"      Time: {result_cold_time:.3f}s")

        # 4. Result cache validator (warm)
        print("\n[4/4] CachedResultValidator (warm cache)...")
        start = time.time()
        result_warm = self.result_validator.validate_all_ar_rules()
        result_warm_time = time.time() - start
        results['result_warm'] = result_warm_time
        print(f"      Time: {result_warm_time:.3f}s ({result_warm_time*1000:.1f}ms)")

        # Calculate speedups
        fs_speedup = base_time / fs_time if fs_time > 0 else 0
        result_cold_speedup = base_time / result_cold_time if result_cold_time > 0 else 0
        result_warm_speedup = base_time / result_warm_time if result_warm_time > 0 else 0

        print(f"\n[COMPARISON]")
        print(f"  Base (no cache):          {base_time:.3f}s  (1.0x baseline)")
        print(f"  Filesystem cache:         {fs_time:.3f}s  ({fs_speedup:.1f}x)")
        print(f"  Result cache (cold):      {result_cold_time:.3f}s  ({result_cold_speedup:.1f}x)")
        print(f"  Result cache (warm):      {result_warm_time:.3f}s  ({result_warm_speedup:.1f}x)")

        return {
            "base_time": base_time,
            "fs_time": fs_time,
            "result_cold_time": result_cold_time,
            "result_warm_time": result_warm_time,
            "fs_speedup": fs_speedup,
            "result_cold_speedup": result_cold_speedup,
            "result_warm_speedup": result_warm_speedup
        }

    # ============================================================
    # RUN ALL BENCHMARKS
    # ============================================================

    def run_all_benchmarks(self) -> Dict[str, Any]:
        """
        Run complete benchmark suite.

        Returns:
            Dict with all benchmark results
        """
        print("\n" + "="*70)
        print(" "*15 + "RESULT CACHE BENCHMARK SUITE")
        print("="*70)
        print(f"Repository: {self.repo_root}")
        print(f"Cache Dir:  {self.result_validator.cache_dir}")
        print("="*70)

        all_results = {}

        # Run benchmarks
        all_results['cold_vs_warm'] = self.benchmark_cold_vs_warm(iterations=3)
        all_results['hit_rates'] = self.benchmark_cache_hit_rates()
        all_results['hash_overhead'] = self.benchmark_hash_overhead()
        all_results['invalidation'] = self.benchmark_invalidation()
        all_results['cache_size'] = self.benchmark_cache_size()
        all_results['comparison'] = self.benchmark_validator_comparison()

        # Print final summary
        self.print_summary(all_results)

        return all_results

    def print_summary(self, results: Dict[str, Any]):
        """Print comprehensive benchmark summary"""
        print("\n" + "="*70)
        print(" "*20 + "BENCHMARK SUMMARY")
        print("="*70)

        # Cold vs Warm
        cold_warm = results['cold_vs_warm']
        print(f"\n[1] COLD VS WARM PERFORMANCE")
        print(f"    Cold run:         {cold_warm['cold_time']:.3f}s")
        print(f"    Warm run (avg):   {cold_warm['avg_warm_time']:.3f}s")
        print(f"    Speedup:          {cold_warm['speedup']:.1f}x")

        # Hit rates
        hit_rates = results['hit_rates']
        print(f"\n[2] CACHE HIT RATES")
        print(f"    Second run hits:  {hit_rates['run2_hit_rate']:.1f}%")
        print(f"    (Expected: >95%)")

        # Hash overhead
        hash_overhead = results['hash_overhead']
        print(f"\n[3] FILE HASH OVERHEAD")
        print(f"    Avg per file:     {hash_overhead['avg_time_per_file']*1000:.3f}ms")
        print(f"    Throughput:       {hash_overhead['throughput']:.0f} files/sec")

        # Invalidation
        invalidation = results['invalidation']
        print(f"\n[4] INVALIDATION PERFORMANCE")
        print(f"    Single rule:      {invalidation['single_invalidation_ms']:.3f}ms")
        print(f"    Full cache:       {invalidation['full_invalidation_ms']:.3f}ms")

        # Cache size
        cache_size = results['cache_size']
        print(f"\n[5] CACHE STORAGE")
        print(f"    Current size:     {cache_size['cache_size_mb']:.3f} MB")
        print(f"    Entries:          {cache_size['total_entries']}")
        print(f"    Est. full (384):  {cache_size['estimated_full_cache_mb']:.2f} MB")

        # Comparison
        comparison = results['comparison']
        print(f"\n[6] VALIDATOR COMPARISON (AR001-AR010)")
        print(f"    Base:             {comparison['base_time']:.3f}s  (baseline)")
        print(f"    + FS Cache:       {comparison['fs_time']:.3f}s  ({comparison['fs_speedup']:.1f}x)")
        print(f"    + Result (cold):  {comparison['result_cold_time']:.3f}s  ({comparison['result_cold_speedup']:.1f}x)")
        print(f"    + Result (warm):  {comparison['result_warm_time']:.3f}s  ({comparison['result_warm_speedup']:.1f}x)")

        print("\n" + "="*70)
        print(" "*15 + "BENCHMARK COMPLETE")
        print("="*70 + "\n")


# ============================================================
# MAIN
# ============================================================

def main():
    """Run benchmark suite"""
    # Get repo root
    if len(sys.argv) > 1:
        repo_root = Path(sys.argv[1])
    else:
        repo_root = Path(__file__).parent.parent.parent.parent

    print(f"Starting Result Cache Benchmark Suite...")
    print(f"Repository: {repo_root}\n")

    # Create benchmark
    benchmark = ResultCacheBenchmark(repo_root)

    # Run all benchmarks
    results = benchmark.run_all_benchmarks()

    # Save results to JSON
    output_file = repo_root / ".ssid_cache" / "benchmark_results.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n[SAVED] Benchmark results: {output_file}")

    print("\n[OK] Benchmark suite complete!")


if __name__ == "__main__":
    main()
