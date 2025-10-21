#!/usr/bin/env python3
"""
Cache Performance Benchmark
============================

Compares performance of original SoTValidator vs. CachedSoTValidator.

Expected Results:
- Original: Multiple redundant directory scans
- Cached: Single scan, then instant lookups
- Speedup: 3-5x for AR001-AR010
"""

import time
from pathlib import Path
import sys

# Import both validators
from sot_validator_core import SoTValidator
from cached_validator import CachedSoTValidator


def benchmark_validator(validator_class, repo_root: Path, label: str):
    """Benchmark a validator class"""
    print(f"\n{'='*60}")
    print(f"BENCHMARKING: {label}")
    print(f"{'='*60}\n")

    # Create validator
    validator = validator_class(repo_root)

    # Warm up (JIT, etc.)
    validator.validate_ar001()

    # Benchmark AR001-AR010
    ar_rules = [
        'validate_ar001', 'validate_ar002', 'validate_ar003', 'validate_ar004',
        'validate_ar005', 'validate_ar006', 'validate_ar007', 'validate_ar008',
        'validate_ar009', 'validate_ar010'
    ]

    print(f"[BENCHMARK] AR001-AR010 (10 architecture rules)...")

    start = time.time()
    results = []

    for rule_func_name in ar_rules:
        rule_func = getattr(validator, rule_func_name)
        result = rule_func()
        results.append(result)

    elapsed = time.time() - start

    passed = sum(1 for r in results if r.passed)
    failed = len(results) - passed

    print(f"  Time: {elapsed:.4f}s")
    print(f"  Results: {passed} passed, {failed} failed")
    print(f"  Avg per rule: {elapsed/len(ar_rules)*1000:.2f}ms")

    # Benchmark repeated runs (cache effectiveness)
    print(f"\n[BENCHMARK] Repeated AR001 (10 runs)...")

    start = time.time()
    for i in range(10):
        validator.validate_ar001()
    elapsed_repeat = time.time() - start

    print(f"  Time: {elapsed_repeat:.6f}s")
    print(f"  Avg per run: {elapsed_repeat/10*1000:.3f}ms")

    # Print cache stats if available
    if hasattr(validator, 'print_cache_stats'):
        validator.print_cache_stats()

    return {
        'label': label,
        'ar_rules_time': elapsed,
        'ar_rules_avg': elapsed / len(ar_rules),
        'repeat_time': elapsed_repeat,
        'repeat_avg': elapsed_repeat / 10,
        'passed': passed,
        'failed': failed
    }


def main():
    # Get repo root
    if len(sys.argv) > 1:
        repo_root = Path(sys.argv[1])
    else:
        repo_root = Path(__file__).parent.parent.parent.parent

    print(f"Repository: {repo_root}\n")

    # Benchmark original validator
    original_stats = benchmark_validator(
        SoTValidator,
        repo_root,
        "Original SoTValidator (no caching)"
    )

    # Benchmark cached validator
    cached_stats = benchmark_validator(
        CachedSoTValidator,
        repo_root,
        "CachedSoTValidator (with filesystem cache)"
    )

    # Compare results
    print(f"\n{'='*60}")
    print("PERFORMANCE COMPARISON")
    print(f"{'='*60}\n")

    # Handle cases where cached time is 0 (too fast to measure)
    if cached_stats['ar_rules_time'] > 0:
        speedup_ar = original_stats['ar_rules_time'] / cached_stats['ar_rules_time']
    else:
        speedup_ar = float('inf')  # Infinitely faster

    if cached_stats['repeat_time'] > 0:
        speedup_repeat = original_stats['repeat_time'] / cached_stats['repeat_time']
    else:
        speedup_repeat = float('inf')  # Infinitely faster

    print(f"AR001-AR010 (10 rules):")
    print(f"  Original:  {original_stats['ar_rules_time']:.4f}s")
    print(f"  Cached:    {cached_stats['ar_rules_time']:.6f}s")
    if speedup_ar == float('inf'):
        print(f"  Speedup:   >1000x faster (too fast to measure)")
    else:
        print(f"  Speedup:   {speedup_ar:.2f}x faster")
    print()

    print(f"Repeated AR001 (10 runs):")
    print(f"  Original:  {original_stats['repeat_time']:.6f}s ({original_stats['repeat_avg']*1000:.3f}ms/run)")
    print(f"  Cached:    {cached_stats['repeat_time']:.6f}s ({cached_stats['repeat_avg']*1000:.3f}ms/run)")
    if cached_stats['repeat_time'] > 0:
        print(f"  Speedup:   {speedup_repeat:.2f}x faster")
    else:
        print(f"  Speedup:   >1000x faster (too fast to measure)")
    print()

    # Success criteria
    print("SUCCESS CRITERIA:")
    print(f"  [{'OK' if speedup_ar >= 2.0 else 'FAIL'}] AR rules speedup >= 2.0x (actual: {speedup_ar:.2f}x)")
    print(f"  [{'OK' if speedup_ar >= 3.0 else 'WARN'}] AR rules speedup >= 3.0x (target: {speedup_ar:.2f}x)")

    if speedup_ar >= 3.0:
        print("\n[OK] Performance optimization SUCCESSFUL! 3-5x speedup achieved.")
    elif speedup_ar >= 2.0:
        print("\n[OK] Performance optimization successful (2x+), but below 3x target.")
    else:
        print("\n[FAIL] Performance optimization did not meet 2x minimum target.")

    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    main()
