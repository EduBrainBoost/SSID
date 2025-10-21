#!/usr/bin/env python3
"""
Quick Performance Profile - Tests only a few rules for faster analysis
"""

import cProfile
import pstats
import time
from pathlib import Path
import sys

try:
    from sot_validator_core import SoTValidator
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent))
    from sot_validator_core import SoTValidator


def quick_profile(repo_root: Path):
    """Profile just a few representative rules"""

    print(f"[QUICK PROFILE] Testing on: {repo_root}\n")

    validator = SoTValidator(repo_root=repo_root)

    # Test AR001 (directory scanning)
    print("Testing AR001 (root count)...")
    profiler = cProfile.Profile()

    profiler.enable()
    start = time.time()
    result = validator.validate_ar001()
    end = time.time()
    profiler.disable()

    print(f"  Time: {end-start:.3f}s")
    print(f"  Result: {'PASS' if result.passed else 'FAIL'}")
    print(f"  Evidence: {result.evidence.get('actual_count', 'N/A')} roots\n")

    # Test AR002 (shard scanning - more intensive)
    print("Testing AR002 (shard count)...")
    profiler2 = cProfile.Profile()

    profiler2.enable()
    start = time.time()
    result2 = validator.validate_ar002()
    end = time.time()
    profiler2.disable()

    print(f"  Time: {end-start:.3f}s")
    print(f"  Result: {'PASS' if result2.passed else 'FAIL'}\n")

    # Test CP001 (file content scanning)
    print("Testing CP001 (PII check - file scanning)...")
    profiler3 = cProfile.Profile()

    profiler3.enable()
    start = time.time()
    result3 = validator.validate_cp001()
    end = time.time()
    profiler3.disable()

    print(f"  Time: {end-start:.3f}s")
    print(f"  Result: {'PASS' if result3.passed else 'FAIL'}\n")

    # Print combined stats
    print("=" * 80)
    print("TOP BOTTLENECKS (Cumulative Time)")
    print("=" * 80)

    combined_stats = pstats.Stats(profiler, profiler2, profiler3)
    combined_stats.strip_dirs()
    combined_stats.sort_stats('cumulative')
    combined_stats.print_stats(20)

    print("\n" + "=" * 80)
    print("TOP TIME CONSUMERS (Total Time)")
    print("=" * 80)
    combined_stats.sort_stats('tottime')
    combined_stats.print_stats(20)

    print("\n" + "=" * 80)
    print("MOST CALLED FUNCTIONS")
    print("=" * 80)
    combined_stats.sort_stats('ncalls')
    combined_stats.print_stats(20)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        repo_root = Path(sys.argv[1])
    else:
        repo_root = Path(__file__).parent.parent.parent.parent

    if not repo_root.exists():
        print(f"[ERROR] Repository root does not exist: {repo_root}")
        sys.exit(1)

    try:
        quick_profile(repo_root)
        print("\n[OK] Quick profiling complete!")
    except Exception as e:
        print(f"\n[ERROR] Error during profiling: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
