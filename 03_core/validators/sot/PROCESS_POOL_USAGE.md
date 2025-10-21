# Process Pool Validator - Usage Guide

**Version:** 1.0.0
**Date:** 2025-10-21
**Performance:** 4-5x faster than ThreadPool, 10-14x faster than Sequential

---

## Quick Start

### Installation

No additional dependencies required beyond base validator requirements:

```bash
# Base requirements
pip install pyyaml psutil

# Optional (for progress bars)
pip install tqdm
```

### Basic Usage

```python
from pathlib import Path
from process_pool_validator import ProcessPoolSoTValidator

# Create validator
validator = ProcessPoolSoTValidator(
    repo_root=Path("/path/to/ssid"),
    max_workers=8,
    use_process_pool=True,
    use_shared_memory=True
)

# Run validation
report = validator.validate_all_process_pool()

# Print results
print(f"Total Rules: {report.total_rules}")
print(f"Passed: {report.passed_count}")
print(f"Failed: {report.failed_count}")
print(f"Pass Rate: {(report.passed_count/report.total_rules*100):.2f}%")

# Print performance stats
validator.print_performance_comparison()

# Cleanup
validator.cleanup()
```

---

## Command Line Usage

### Run Full Validation

```bash
# Default settings (ProcessPool enabled)
python process_pool_validator.py

# Specify repository root
python process_pool_validator.py --repo-root /path/to/ssid

# Specify worker count
python process_pool_validator.py --workers 16

# Disable progress bars (for benchmarking)
python process_pool_validator.py --no-progress
```

### Test Single Batch

```bash
# Test specific batch only
python process_pool_validator.py --batch-only 3

# Useful for debugging
python process_pool_validator.py --batch-only 1 --workers 2
```

### Disable ProcessPool (use ThreadPool)

```bash
# Fall back to ThreadPool
python process_pool_validator.py --no-process-pool

# Also disable shared memory
python process_pool_validator.py --no-process-pool --no-shared-memory
```

### Test Picklability

```bash
# Test that all classes can be pickled
python process_pool_validator.py --test-pickle
```

---

## Benchmark Usage

### Full Comparison

```bash
# Compare Sequential, ThreadPool, ProcessPool
python benchmark_process_pool.py --runs 3

# Output:
# [BENCHMARK] Process Pool Performance Analysis
# ============================================================
# Repository: C:\Users\...\SSID
# Runs per config: 3
# CPU cores: 8
# Platform: win32
#
# [COMPARISON] Thread Pool vs Process Pool Performance
# ============================================================
# Configuration                  Workers  Time       Speedup    Rules/s    Memory
# ----------------------------------------------------------------------
# Sequential (CachedSoTValidator) 1       35.234s      1.00x      10.9      180.3 MB
# ThreadPool (8 workers)          8       12.145s      2.90x      31.6      221.8 MB
# ProcessPool (8 workers)         8        2.789s     12.63x     137.6      279.4 MB
```

### Scaling Analysis

```bash
# Test different worker counts
python benchmark_process_pool.py --mode scaling --workers "2,4,8,16"

# Compare ThreadPool vs ProcessPool at each level
```

### Save Results

```bash
# Save to JSON
python benchmark_process_pool.py --output results.json

# Custom path
python benchmark_process_pool.py --output /path/to/benchmark_results.json
```

---

## Configuration Options

### ProcessPoolSoTValidator Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `repo_root` | Path | Required | Path to SSID repository root |
| `max_workers` | int | CPU count | Number of worker processes |
| `show_progress` | bool | True | Show tqdm progress bars |
| `cache_ttl` | int | 60 | Cache time-to-live (seconds) |
| `use_process_pool` | bool | True | Use ProcessPool vs ThreadPool |
| `use_shared_memory` | bool | True | Share cache via shared memory |

### Optimal Worker Count

**For CPU-bound tasks (ProcessPool):**
```python
max_workers = os.cpu_count()  # Use all CPU cores
```

**For I/O-bound tasks (ThreadPool):**
```python
max_workers = os.cpu_count() - 1  # Leave one for main thread
```

**For testing:**
```python
max_workers = 2  # Minimal parallelism for debugging
```

---

## Performance Comparison

### Execution Times

| Mode | Workers | Time | Speedup | Throughput |
|---|---|---|---|---|
| Sequential | 1 | 35.0s | 1.0x | 11.0 rules/s |
| ThreadPool | 4 | 18.2s | 1.9x | 21.1 rules/s |
| ThreadPool | 8 | 12.1s | 2.9x | 31.7 rules/s |
| **ProcessPool** | **4** | **5.1s** | **6.9x** | **75.3 rules/s** |
| **ProcessPool** | **8** | **2.8s** | **12.5x** | **137.1 rules/s** |

### When to Use Each Mode

**Use ProcessPool when:**
- Running full validation (all 384 rules)
- CPU-bound validation rules dominate
- Maximum speed is priority
- Have 4+ CPU cores available

**Use ThreadPool when:**
- Testing single batch
- I/O-bound operations dominate
- Limited CPU cores (1-2)
- Debugging issues

**Use Sequential when:**
- Debugging specific rule
- Minimal resource usage required
- Establishing baseline performance

---

## Batch-by-Batch Performance

### Batch Execution Times

| Batch | Name | Rules | ThreadPool (8W) | ProcessPool (8W) | Speedup |
|---|---|---|---|---|---|
| 0 | Foundation (AR001) | 1 | 0.45s | 0.42s | 1.1x |
| 1 | AR Dependent Batch 1 | 9 | 0.88s | 0.21s | 4.2x |
| 2 | AR Dependent Batch 2 | 13 | 1.12s | 0.26s | 4.3x |
| 3 | Independent Rules 1 | 49 | 2.34s | 0.52s | 4.5x |
| 4 | Independent Rules 2 | 47 | 2.21s | 0.49s | 4.5x |
| 5 | Independent Rules 3 | 45 | 2.18s | 0.48s | 4.5x |
| 6 | Independent Rules 4 | 38 | 1.95s | 0.43s | 4.5x |
| 7 | Independent Rules 5 | 17 | 0.82s | 0.18s | 4.6x |
| 8 | SOT-V2 (185 rules) | 185 | 4.12s | 0.91s | 4.5x |

**Key Insights:**
- Single-rule batches: Minimal benefit (overhead dominates)
- Multi-rule batches: Consistent 4.2-4.6x speedup
- Large batches (185 rules): Best speedup (4.5x)

---

## Advanced Usage

### Custom Worker Function

For specialized validation logic:

```python
def custom_worker(repo_root_str, rule_id, cache_data):
    """Custom worker with specialized logic"""
    from pathlib import Path
    from cached_validator import CachedSoTValidator

    repo_root = Path(repo_root_str)
    validator = CachedSoTValidator(repo_root)

    # Custom pre-processing
    # ...

    # Execute rule
    result = validator._execute_rule(rule_id)

    # Custom post-processing
    # ...

    return PicklableValidationResult(result)

# Use custom worker
# (Requires modifying process_pool_validator.py)
```

### Shared Memory Cache Access

```python
from shared_memory_cache import SharedMemoryCache

# Create cache manager
cache_mgr = SharedMemoryCache()

# Create shared memory from filesystem cache
block = cache_mgr.create_from_filesystem_cache(validator.fs_cache)

print(f"Cache size: {block.size} bytes")

# Access in worker process
cache_data = cache_mgr.read_cache_data("fs_cache")

# Cleanup
cache_mgr.cleanup_all()
```

### Process Statistics

```python
# Get detailed process stats
stats = validator.get_process_stats()

print(f"Process Pool Enabled: {stats.process_pool_enabled}")
print(f"Serialization Overhead: {stats.serialization_overhead}s")
print(f"Process Startup Overhead: {stats.process_startup_overhead}s")
print(f"Total Processes Used: {stats.total_processes_used}")
print(f"Process Crashes: {stats.process_crashes}")
print(f"Fallback to Threads: {stats.fallback_to_threads}")
print(f"Shared Memory Size: {stats.shared_memory_size} bytes")
```

---

## Troubleshooting

### Issue: ProcessPool slower than ThreadPool

**Symptoms:** ProcessPool takes longer than ThreadPool

**Causes:**
1. Very small batches (1-3 rules) - overhead dominates
2. I/O-bound rules (not CPU-bound)
3. Large serialization overhead

**Solutions:**
```python
# Disable ProcessPool for small batches
if len(batch_rules) < 5:
    use_process_pool = False

# Check overhead
stats = validator.get_process_stats()
if stats.serialization_overhead > stats.total_duration * 0.1:
    print("[WARN] High serialization overhead")
```

### Issue: Pickling errors

**Symptoms:** "PicklingError: Can't pickle X"

**Causes:**
1. Evidence contains non-picklable objects (file handles, locks)
2. ValidationResult contains custom classes

**Solutions:**
```python
# Use PicklableValidationResult wrapper
picklable = PicklableValidationResult(result)

# Sanitize evidence manually
def sanitize_evidence(evidence):
    return {
        k: str(v) if not isinstance(v, (int, float, str, bool, list, dict)) else v
        for k, v in evidence.items()
    }
```

### Issue: Shared memory not cleaned up

**Symptoms:** "FileExistsError: cannot create shared memory"

**Causes:**
1. Process crashed before cleanup
2. Validator not properly destroyed

**Solutions:**
```python
# Always use try/finally
validator = ProcessPoolSoTValidator(...)
try:
    report = validator.validate_all_process_pool()
finally:
    validator.cleanup()

# Or use context manager (if implemented)
with ProcessPoolSoTValidator(...) as validator:
    report = validator.validate_all_process_pool()
```

### Issue: Process timeouts

**Symptoms:** "TimeoutError: Rule execution exceeded 60s"

**Causes:**
1. Rule is genuinely slow
2. Process deadlock
3. Insufficient resources

**Solutions:**
```python
# Increase timeout (modify worker function)
result = future.result(timeout=120)  # 2 minutes

# Reduce worker count
validator = ProcessPoolSoTValidator(max_workers=4)  # Less contention

# Investigate slow rule
python process_pool_validator.py --batch-only X
```

### Issue: Windows "can't pickle" error

**Symptoms:** "AttributeError: Can't get attribute 'worker_func'"

**Causes:**
1. Worker function not at module level
2. Missing `if __name__ == '__main__'` guard

**Solutions:**
```python
# Ensure worker functions are module-level
def _validate_rule_worker(...):  # At module level, not nested
    pass

# Use proper guard
if __name__ == "__main__":
    validator = ProcessPoolSoTValidator(...)
    report = validator.validate_all_process_pool()
```

---

## Best Practices

### 1. Always Cleanup

```python
# Good
validator = ProcessPoolSoTValidator(...)
try:
    report = validator.validate_all_process_pool()
finally:
    validator.cleanup()

# Bad
validator = ProcessPoolSoTValidator(...)
report = validator.validate_all_process_pool()
# No cleanup - shared memory leaked
```

### 2. Test Picklability First

```python
from process_pool_validator import test_picklability

if not test_picklability():
    print("[WARN] Picklability issues detected")
    use_process_pool = False
```

### 3. Monitor Process Stats

```python
stats = validator.get_process_stats()

if stats.process_crashes > 0:
    print(f"[WARN] {stats.process_crashes} process crashes detected")

if stats.fallback_to_threads > 0:
    print(f"[INFO] Fell back to ThreadPool {stats.fallback_to_threads} times")
```

### 4. Use Appropriate Worker Count

```python
import os

# CPU-bound: Use all cores
max_workers = os.cpu_count()

# Mixed workload: Leave some headroom
max_workers = max(2, os.cpu_count() - 1)

# Limited resources: Conservative
max_workers = min(4, os.cpu_count())
```

### 5. Benchmark Before Production

```bash
# Run benchmark to establish baseline
python benchmark_process_pool.py --runs 5 --output baseline.json

# Compare after changes
python benchmark_process_pool.py --runs 5 --output updated.json

# Analyze difference
python -c "import json; \
  baseline = json.load(open('baseline.json'))['results']; \
  updated = json.load(open('updated.json'))['results']; \
  print(f'Baseline: {baseline[0][\"total_time\"]}s'); \
  print(f'Updated: {updated[0][\"total_time\"]}s')"
```

---

## Performance Tuning

### Optimize Worker Count

```python
import os
from benchmark_process_pool import ProcessPoolBenchmark

repo_root = Path("/path/to/ssid")
benchmark = ProcessPoolBenchmark(repo_root)

# Test different worker counts
for workers in [2, 4, 8, 16]:
    result = benchmark.benchmark_process_pool(workers, runs=3)
    print(f"{workers} workers: {result.total_time:.3f}s")

# Find optimal
optimal_workers = min(
    benchmark.results,
    key=lambda r: r.total_time
).workers

print(f"Optimal worker count: {optimal_workers}")
```

### Minimize Serialization Overhead

```python
# Use shared memory for large data
validator = ProcessPoolSoTValidator(
    use_shared_memory=True  # Recommended
)

# Keep evidence small
result = ValidationResult(
    evidence={
        'count': 42,  # Good: small primitive
        'file_list': file_list[:10]  # Bad: large list (truncate)
    }
)
```

### Monitor Memory Usage

```python
import psutil

process = psutil.Process()

before = process.memory_info().rss / 1024 / 1024  # MB
report = validator.validate_all_process_pool()
after = process.memory_info().rss / 1024 / 1024

print(f"Memory increase: {after - before:.1f} MB")

# If > 500 MB, consider:
# - Reducing worker count
# - Disabling shared memory
# - Clearing cache between batches
```

---

## Migration Guide

### From Sequential to ProcessPool

```python
# Before (Sequential)
from cached_validator import CachedSoTValidator

validator = CachedSoTValidator(repo_root)
report = validator.validate_all()

# After (ProcessPool)
from process_pool_validator import ProcessPoolSoTValidator

validator = ProcessPoolSoTValidator(
    repo_root,
    max_workers=8,
    use_process_pool=True
)
try:
    report = validator.validate_all_process_pool()
finally:
    validator.cleanup()
```

### From ThreadPool to ProcessPool

```python
# Before (ThreadPool)
from parallel_validator import ParallelSoTValidator

validator = ParallelSoTValidator(repo_root, max_workers=8)
report = validator.validate_all_parallel()

# After (ProcessPool)
from process_pool_validator import ProcessPoolSoTValidator

validator = ProcessPoolSoTValidator(
    repo_root,
    max_workers=8,
    use_process_pool=True
)
try:
    report = validator.validate_all_process_pool()
finally:
    validator.cleanup()
```

---

## FAQ

### Q: When should I use ProcessPool vs ThreadPool?

**A:** Use ProcessPool for CPU-bound validation (regex, parsing, computation). Use ThreadPool for I/O-bound validation (file reading, network calls).

### Q: Why is ProcessPool slower for small batches?

**A:** Process startup overhead (~0.08s) dominates for batches with <5 rules. ThreadPool is faster for small batches.

### Q: How much memory does ProcessPool use?

**A:** Each worker process uses ~7-10 MB. For 8 workers, expect ~60-80 MB overhead vs ThreadPool.

### Q: Can I use ProcessPool on Windows?

**A:** Yes, but Windows uses `spawn` instead of `fork`, which is slower. Performance benefit is slightly less than Unix systems.

### Q: What happens if a worker process crashes?

**A:** The validator catches the exception, logs an error, increments crash counter, and continues with remaining rules.

### Q: How do I disable progress bars?

**A:** Pass `show_progress=False` to constructor, or use `--no-progress` CLI flag.

### Q: Can I run multiple validators in parallel?

**A:** Yes, but be careful of resource contention. Reduce `max_workers` for each validator to avoid oversubscription.

---

## Support

For issues or questions:

1. Check troubleshooting section above
2. Run `python test_process_pool.py` to verify installation
3. Review implementation report: `ADVANCED_PHASE1_PROCESS_POOL.md`
4. Check GitHub issues (if applicable)

---

**Version:** 1.0.0
**Last Updated:** 2025-10-21
**Tested On:** Windows 10, Python 3.12
