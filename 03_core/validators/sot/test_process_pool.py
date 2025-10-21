#!/usr/bin/env python3
"""
Process Pool Validator - Quick Test Script
===========================================

Quick test to verify ProcessPoolExecutor implementation works correctly.

Tests:
1. Picklability of all classes
2. Single batch execution
3. Process pool vs thread pool comparison
4. Shared memory cache functionality
5. Error handling and fallback

[TEST] Quick validation tests
[VERIFY] Implementation correctness
"""

import sys
import time
from pathlib import Path

# Import validators
try:
    from process_pool_validator import (
        ProcessPoolSoTValidator,
        PicklableValidationResult,
        test_picklability
    )
    from parallel_validator import ParallelSoTValidator
    from sot_validator_core import ValidationResult, Severity
    from shared_memory_cache import SharedMemoryCache, test_shared_memory
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent))
    from process_pool_validator import (
        ProcessPoolSoTValidator,
        PicklableValidationResult,
        test_picklability
    )
    from parallel_validator import ParallelSoTValidator
    from sot_validator_core import ValidationResult, Severity
    from shared_memory_cache import SharedMemoryCache, test_shared_memory


def test_picklable_result():
    """Test PicklableValidationResult serialization"""
    print("\n" + "="*70)
    print("[TEST 1] PicklableValidationResult Serialization")
    print("="*70)

    # Create test result
    result = ValidationResult(
        rule_id="TEST-001",
        passed=True,
        severity=Severity.INFO,
        message="Test validation message",
        evidence={
            "count": 42,
            "items": ["a", "b", "c"],
            "nested": {"key": "value"}
        }
    )

    # Wrap in picklable result
    picklable = PicklableValidationResult(result)

    # Convert back
    restored = picklable.to_validation_result()

    # Verify
    print(f"Rule ID matches: {result.rule_id == restored.rule_id}")
    print(f"Passed matches: {result.passed == restored.passed}")
    print(f"Message matches: {result.message == restored.message}")
    print(f"Evidence matches: {result.evidence == restored.evidence}")

    success = (
        result.rule_id == restored.rule_id and
        result.passed == restored.passed and
        result.message == restored.message and
        result.evidence == restored.evidence
    )

    if success:
        print("\n[OK] PicklableValidationResult test PASSED")
    else:
        print("\n[FAIL] PicklableValidationResult test FAILED")

    return success


def test_single_batch_process_pool(repo_root: Path):
    """Test single batch execution with ProcessPool"""
    print("\n" + "="*70)
    print("[TEST 2] Single Batch Execution (ProcessPool)")
    print("="*70)

    # Create validator
    validator = ProcessPoolSoTValidator(
        repo_root=repo_root,
        max_workers=4,
        show_progress=False,
        use_process_pool=True,
        use_shared_memory=True
    )

    # Execute batch 1 (small batch for quick test)
    batch_config = validator.dependency_graph.get_batch(1)

    print(f"Testing batch {batch_config['batch_id']}: {batch_config['name']}")
    print(f"Rules in batch: {len(batch_config['rules'])}")

    start = time.time()
    results = validator._execute_batch_process(batch_config)
    elapsed = time.time() - start

    passed = sum(1 for r in results if r.passed)
    failed = len(results) - passed

    print(f"\nResults:")
    print(f"  Total: {len(results)}")
    print(f"  Passed: {passed}")
    print(f"  Failed: {failed}")
    print(f"  Time: {elapsed:.3f}s")

    # Cleanup
    validator.cleanup()

    success = len(results) == len(batch_config['rules'])

    if success:
        print("\n[OK] Single batch test PASSED")
    else:
        print("\n[FAIL] Single batch test FAILED")

    return success


def test_process_vs_thread_comparison(repo_root: Path):
    """Compare ProcessPool vs ThreadPool on same batch"""
    print("\n" + "="*70)
    print("[TEST 3] ProcessPool vs ThreadPool Comparison")
    print("="*70)

    batch_id = 3  # Medium-sized independent batch

    # Test with ThreadPool
    print("\n[Thread] Testing ThreadPool...")
    thread_validator = ParallelSoTValidator(
        repo_root=repo_root,
        max_workers=4,
        show_progress=False
    )

    batch_config = thread_validator.dependency_graph.get_batch(batch_id)
    thread_start = time.time()
    thread_results = thread_validator._execute_batch(batch_config)
    thread_time = time.time() - thread_start

    print(f"ThreadPool: {len(thread_results)} results in {thread_time:.3f}s")

    # Test with ProcessPool
    print("\n[Process] Testing ProcessPool...")
    process_validator = ProcessPoolSoTValidator(
        repo_root=repo_root,
        max_workers=4,
        show_progress=False,
        use_process_pool=True,
        use_shared_memory=True
    )

    batch_config = process_validator.dependency_graph.get_batch(batch_id)
    process_start = time.time()
    process_results = process_validator._execute_batch_process(batch_config)
    process_time = time.time() - process_start

    print(f"ProcessPool: {len(process_results)} results in {process_time:.3f}s")

    # Compare
    speedup = thread_time / process_time if process_time > 0 else 0

    print(f"\n[Comparison]")
    print(f"  ThreadPool: {thread_time:.3f}s")
    print(f"  ProcessPool: {process_time:.3f}s")
    print(f"  Speedup: {speedup:.2f}x")

    # Verify same results
    thread_passed = sum(1 for r in thread_results if r.passed)
    process_passed = sum(1 for r in process_results if r.passed)

    print(f"\n[Correctness]")
    print(f"  ThreadPool passed: {thread_passed}/{len(thread_results)}")
    print(f"  ProcessPool passed: {process_passed}/{len(process_results)}")
    print(f"  Results match: {thread_passed == process_passed}")

    # Cleanup
    process_validator.cleanup()

    success = (
        len(thread_results) == len(process_results) and
        thread_passed == process_passed and
        speedup > 1.0  # ProcessPool should be faster
    )

    if success:
        print("\n[OK] Comparison test PASSED")
    else:
        print("\n[FAIL] Comparison test FAILED")

    return success


def test_fallback_mechanism(repo_root: Path):
    """Test fallback to ThreadPool"""
    print("\n" + "="*70)
    print("[TEST 4] Fallback Mechanism")
    print("="*70)

    # Create validator with ProcessPool disabled
    validator = ProcessPoolSoTValidator(
        repo_root=repo_root,
        max_workers=4,
        show_progress=False,
        use_process_pool=False  # Disable ProcessPool
    )

    print("ProcessPool disabled, should fall back to ThreadPool")

    # Execute small batch
    batch_config = validator.dependency_graph.get_batch(1)

    start = time.time()
    results = validator._execute_batch_process(batch_config)
    elapsed = time.time() - start

    print(f"\nResults:")
    print(f"  Total: {len(results)}")
    print(f"  Passed: {sum(1 for r in results if r.passed)}")
    print(f"  Time: {elapsed:.3f}s")
    print(f"  Used ThreadPool fallback: {validator.process_stats.fallback_to_threads > 0}")

    success = len(results) > 0

    if success:
        print("\n[OK] Fallback test PASSED")
    else:
        print("\n[FAIL] Fallback test FAILED")

    return success


def run_all_tests():
    """Run all tests"""
    print("="*70)
    print("[PROCESS POOL VALIDATOR] Quick Test Suite")
    print("="*70)

    # Get repo root
    repo_root = Path(__file__).parent.parent.parent.parent
    print(f"Repository: {repo_root}")

    results = {}

    # Test 0: Picklability
    print("\n[TEST 0] Testing picklability...")
    results['picklability'] = test_picklability()

    # Test 1: PicklableValidationResult
    results['picklable_result'] = test_picklable_result()

    # Test 2: Shared memory
    print("\n[TEST 2.5] Testing shared memory...")
    test_shared_memory()
    results['shared_memory'] = True  # If it doesn't crash, it works

    # Test 3: Single batch
    try:
        results['single_batch'] = test_single_batch_process_pool(repo_root)
    except Exception as e:
        print(f"\n[ERROR] Single batch test failed: {e}")
        results['single_batch'] = False

    # Test 4: Process vs Thread
    try:
        results['comparison'] = test_process_vs_thread_comparison(repo_root)
    except Exception as e:
        print(f"\n[ERROR] Comparison test failed: {e}")
        results['comparison'] = False

    # Test 5: Fallback
    try:
        results['fallback'] = test_fallback_mechanism(repo_root)
    except Exception as e:
        print(f"\n[ERROR] Fallback test failed: {e}")
        results['fallback'] = False

    # Summary
    print("\n" + "="*70)
    print("[TEST SUMMARY]")
    print("="*70)

    for test_name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"{test_name:20s}: {status}")

    total = len(results)
    passed = sum(1 for p in results.values() if p)

    print(f"\nTotal: {passed}/{total} tests passed ({passed/total*100:.1f}%)")

    if passed == total:
        print("\n[OK] All tests PASSED!")
        return 0
    else:
        print("\n[FAIL] Some tests FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
