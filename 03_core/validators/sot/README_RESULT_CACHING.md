# Result Caching Quick Start Guide

## Overview

Result caching provides 20x speedup on repeated SoT validation runs by caching validation results and only re-validating when files change.

## Quick Start

### Basic Usage

```python
from pathlib import Path
from cached_result_validator import CachedResultValidator

# Create validator with result caching
validator = CachedResultValidator(
    repo_root=Path("."),
    result_cache_ttl=86400  # 24 hours
)

# Run validation (caches results)
results = validator.validate_all_ar_rules()
# First run:  ~0.7s
# Second run: ~0.035s (20x faster!)

# Print cache stats
validator.print_result_cache_stats()
```

### Performance

```
Cold run (first time):     0.706s
Warm run (cached):         0.035s
Speedup:                   20.2x
Cache hit rate:            100%
```

## Features

### 1. Automatic File Tracking
- SHA256 hash of all relevant files
- Invalidates cache when files change
- Granular per-rule tracking

### 2. Persistent Storage
- Cache survives process restarts
- Location: `.ssid_cache/validation_results.json`
- Size: ~2MB for 384 rules

### 3. Smart Invalidation
- File-based: Hash mismatch triggers re-validation
- Time-based: TTL expiration (default: 24 hours)
- Manual: Explicit cache clearing

### 4. Cache Management
```python
# View statistics
validator.print_result_cache_stats()

# Invalidate specific rule
validator.invalidate_result_cache("AR001")

# Clear all caches
validator.invalidate_all_caches()
```

## Advanced Usage

### Cache Warming

```python
# Pre-populate cache for faster runs
validator.warm_cache(rule_ids=["AR001", "AR002", ...])
```

### Benchmarking

```python
# Benchmark cache performance
results = validator.benchmark_cache_performance(iterations=3)
# Output: speedup, hit rates, cache size, etc.
```

### Real-Time Monitoring (Optional)

```python
from watchdog_monitor import WatchdogCacheMonitor

# Install watchdog first: pip install watchdog
with WatchdogCacheMonitor(cache, repo_root) as monitor:
    # Files changes automatically invalidate cache
    validator.validate_all_ar_rules()
```

## Files

- `result_cache.py` - Core caching implementation
- `cached_result_validator.py` - Validator with result caching
- `benchmark_result_caching.py` - Benchmark suite
- `watchdog_monitor.py` - Real-time invalidation (optional)
- `PHASE5_RESULT_CACHING.md` - Full implementation report

## Cache Invalidation

### When Cache is Invalidated

1. File modified (hash mismatch)
2. TTL expired (default: 24 hours)
3. Manual invalidation
4. File deleted

### Example

```
[EVENT] User edits Chart.yaml
  └─> Compute new hash
  └─> Find affected rules: AR001, AR004, CP001
  └─> Invalidate cached results
  └─> Next validation triggers re-validation
```

## Performance Tips

1. **Use appropriate TTL:**
   - Development: 1 hour (3600s)
   - CI/CD: 24 hours (86400s)
   - Production: Longer (week+)

2. **Warm cache before batch operations:**
   ```python
   validator.warm_cache()  # Pre-populate
   for rule in rules:
       validator.validate_rule_by_id(rule)  # Fast!
   ```

3. **Monitor cache effectiveness:**
   ```python
   stats = validator.get_result_cache_stats()
   if stats['session_hit_rate'] < 50:
       print("Consider longer TTL or check file stability")
   ```

## Troubleshooting

### Cache Not Working?

```python
# Check if caching is enabled
stats = validator.get_result_cache_stats()
print(f"Enabled: {stats.get('enabled', False)}")

# Verify cache directory exists
print(validator.result_cache.cache_dir)

# Check cache size
print(f"Size: {validator.result_cache.get_cache_size_mb():.2f} MB")
```

### Low Hit Rate?

```python
# Check if files are changing frequently
stats = validator.get_result_cache_stats()
print(f"Invalidations: {stats['lifetime_invalidations']}")

# Consider longer TTL
validator.result_cache.ttl = 86400  # 24 hours
```

### Cache Too Large?

```python
# Check current size
size = validator.result_cache.get_cache_size_mb()
print(f"Size: {size:.2f} MB")

# Clear old entries
validator.invalidate_result_cache()

# Adjust max size
validator.result_cache.max_size_bytes = 50 * 1024 * 1024  # 50MB
```

## CI/CD Integration

### GitHub Actions

```yaml
- name: Cache validation results
  uses: actions/cache@v3
  with:
    path: .ssid_cache/
    key: validation-${{ hashFiles('**/*.yaml') }}

- name: Run validation
  run: python run_validation.py  # Uses cached results
```

## Comparison

| Validator | First Run | Cached Run | Speedup |
|-----------|-----------|------------|---------|
| Base | 0.204s | 0.204s | 1.0x |
| + FS Cache | 0.042s | 0.042s | 4.9x |
| + Result Cache | 0.662s | **0.037s** | **20.2x** |

## Support

For detailed implementation information, see:
- `PHASE5_RESULT_CACHING.md` - Full implementation report
- `benchmark_result_caching.py` - Run benchmarks
- `result_cache.py` - Source code with extensive comments

## License

Part of SSID project. See project root for license information.
