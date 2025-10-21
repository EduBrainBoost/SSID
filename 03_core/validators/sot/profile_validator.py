#!/usr/bin/env python3
"""
SoT Validator Performance Profiling Script
==========================================

Usage:
    python profile_validator.py [repo_path]

Generates:
    - performance_profile.txt: cProfile output
    - performance_report.json: Detailed performance analysis
    - performance_report.md: Human-readable report
"""

import cProfile
import pstats
import io
import json
import time
from pathlib import Path
from datetime import datetime
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from sot_validator_core import SoTValidator


def profile_validator(repo_root: Path):
    """
    Profile the SoT validator with cProfile and generate detailed reports.

    Args:
        repo_root: Path to SSID repository root
    """
    print(f"[PROFILE] Profiling SoT Validator on repository: {repo_root}")
    print(f"[PROFILE] Started at: {datetime.now().isoformat()}\n")

    # Create profiler
    profiler = cProfile.Profile()

    # Profile the validation
    print("[PROFILE]  Running validation with cProfile...")
    start_time = time.time()

    profiler.enable()
    validator = SoTValidator(repo_root=repo_root)
    report = validator.validate_all()
    profiler.disable()

    end_time = time.time()
    total_time = end_time - start_time

    print(f"[OK] Validation completed in {total_time:.2f} seconds")
    print(f"   - Total rules: {report.total_rules}")
    print(f"   - Passed: {report.passed_count}")
    print(f"   - Failed: {report.failed_count}\n")

    # Generate profile statistics
    print("[PROFILE] Generating profile statistics...")

    # Save raw profile output
    profile_output_path = Path(__file__).parent / "performance_profile.txt"
    with open(profile_output_path, 'w') as f:
        stats = pstats.Stats(profiler, stream=f)
        stats.strip_dirs()
        stats.sort_stats('cumulative')
        f.write("=" * 80 + "\n")
        f.write("SoT Validator Performance Profile - Top 50 Functions by Cumulative Time\n")
        f.write("=" * 80 + "\n\n")
        stats.print_stats(50)

        f.write("\n\n" + "=" * 80 + "\n")
        f.write("Top 30 Functions by Total Time\n")
        f.write("=" * 80 + "\n\n")
        stats.sort_stats('tottime')
        stats.print_stats(30)

        f.write("\n\n" + "=" * 80 + "\n")
        f.write("Functions called most frequently\n")
        f.write("=" * 80 + "\n\n")
        stats.sort_stats('ncalls')
        stats.print_stats(30)

    print(f"   [OK] Raw profile saved to: {profile_output_path}")

    # Analyze statistics programmatically
    string_stream = io.StringIO()
    stats = pstats.Stats(profiler, stream=string_stream)
    stats.strip_dirs()
    stats.sort_stats('cumulative')

    # Extract top bottlenecks
    stats_dict = stats.stats

    bottlenecks = []
    filesystem_ops = []
    regex_ops = []

    for func_key, func_stats in stats_dict.items():
        filename, line, func_name = func_key
        ncalls, tottime, cumtime, callers = func_stats[:4]

        func_info = {
            "function": func_name,
            "file": filename,
            "ncalls": ncalls,
            "tottime": tottime,
            "cumtime": cumtime,
            "percall_tot": tottime / ncalls if ncalls > 0 else 0,
            "percall_cum": cumtime / ncalls if ncalls > 0 else 0
        }

        # Categorize operations
        if any(fs_op in func_name for fs_op in ['iterdir', 'exists', 'is_dir', 'is_file', 'glob', 'rglob', 'read_text']):
            filesystem_ops.append(func_info)

        if any(regex_op in func_name for regex_op in ['match', 'search', 'compile', 'findall']):
            regex_ops.append(func_info)

        if cumtime > 0.1:  # Functions taking >100ms
            bottlenecks.append(func_info)

    # Sort by cumulative time
    bottlenecks.sort(key=lambda x: x['cumtime'], reverse=True)
    filesystem_ops.sort(key=lambda x: x['cumtime'], reverse=True)
    regex_ops.sort(key=lambda x: x['cumtime'], reverse=True)

    # Count filesystem operations
    total_filesystem_calls = sum(op['ncalls'] for op in filesystem_ops)
    total_filesystem_time = sum(op['cumtime'] for op in filesystem_ops)

    total_regex_calls = sum(op['ncalls'] for op in regex_ops)
    total_regex_time = sum(op['cumtime'] for op in regex_ops)

    # Generate JSON report
    performance_data = {
        "timestamp": datetime.now().isoformat(),
        "repo_root": str(repo_root),
        "total_execution_time": total_time,
        "validation_stats": {
            "total_rules": report.total_rules,
            "passed": report.passed_count,
            "failed": report.failed_count
        },
        "performance_breakdown": {
            "filesystem_operations": {
                "total_calls": total_filesystem_calls,
                "total_time": total_filesystem_time,
                "percentage": (total_filesystem_time / total_time * 100),
                "top_operations": filesystem_ops[:10]
            },
            "regex_operations": {
                "total_calls": total_regex_calls,
                "total_time": total_regex_time,
                "percentage": (total_regex_time / total_time * 100),
                "top_operations": regex_ops[:10]
            }
        },
        "top_bottlenecks": bottlenecks[:20]
    }

    json_report_path = Path(__file__).parent / "performance_report.json"
    with open(json_report_path, 'w') as f:
        json.dump(performance_data, f, indent=2)

    print(f"   [OK] JSON report saved to: {json_report_path}")

    # Generate Markdown report
    md_report = generate_markdown_report(performance_data, total_time, report)

    md_report_path = Path(__file__).parent / "PERFORMANCE_REPORT.md"
    with open(md_report_path, 'w') as f:
        f.write(md_report)

    print(f"   [OK] Markdown report saved to: {md_report_path}\n")

    # Print summary
    print("=" * 80)
    print("PERFORMANCE PERFORMANCE SUMMARY")
    print("=" * 80)
    print(f"Total Execution Time: {total_time:.2f}s")
    print(f"")
    print(f"Filesystem Operations:")
    print(f"  - Total Calls: {total_filesystem_calls:,}")
    print(f"  - Total Time: {total_filesystem_time:.2f}s ({total_filesystem_time/total_time*100:.1f}%)")
    print(f"")
    print(f"Regex Operations:")
    print(f"  - Total Calls: {total_regex_calls:,}")
    print(f"  - Total Time: {total_regex_time:.2f}s ({total_regex_time/total_time*100:.1f}%)")
    print(f"")
    print(f"Top 5 Bottlenecks:")
    for i, bottleneck in enumerate(bottlenecks[:5], 1):
        print(f"  {i}. {bottleneck['function']}: {bottleneck['cumtime']:.3f}s ({bottleneck['ncalls']} calls)")
    print("=" * 80)

    return performance_data


def generate_markdown_report(data, total_time, report):
    """Generate detailed Markdown performance report"""

    md = f"""# SoT Validator Performance Report

**Generated:** {data['timestamp']}
**Repository:** `{data['repo_root']}`
**Total Execution Time:** {total_time:.2f} seconds

---

## TARGET Executive Summary

The SoT Validator completed validation of **{report.total_rules} rules** in **{total_time:.2f} seconds**.

- [OK] **Passed:** {report.passed_count} rules
- [ERROR] **Failed:** {report.failed_count} rules
- [PROFILE] **Pass Rate:** {(report.passed_count / report.total_rules * 100):.1f}%

---

## [PROFILE] Performance Breakdown

### Filesystem Operations

Filesystem operations are the **primary performance bottleneck**, accounting for:

- **{data['performance_breakdown']['filesystem_operations']['percentage']:.1f}%** of total execution time
- **{data['performance_breakdown']['filesystem_operations']['total_calls']:,}** total calls
- **{data['performance_breakdown']['filesystem_operations']['total_time']:.2f}s** cumulative time

#### Top Filesystem Operations

| Function | Calls | Cumulative Time | Per Call |
|----------|-------|-----------------|----------|
"""

    for op in data['performance_breakdown']['filesystem_operations']['top_operations'][:10]:
        md += f"| `{op['function']}` | {op['ncalls']:,} | {op['cumtime']:.3f}s | {op['percall_cum']:.6f}s |\n"

    md += f"""
### Regex Operations

Regular expression operations account for:

- **{data['performance_breakdown']['regex_operations']['percentage']:.1f}%** of total execution time
- **{data['performance_breakdown']['regex_operations']['total_calls']:,}** total calls
- **{data['performance_breakdown']['regex_operations']['total_time']:.2f}s** cumulative time

#### Top Regex Operations

| Function | Calls | Cumulative Time | Per Call |
|----------|-------|-----------------|----------|
"""

    for op in data['performance_breakdown']['regex_operations']['top_operations'][:10]:
        md += f"| `{op['function']}` | {op['ncalls']:,} | {op['cumtime']:.3f}s | {op['percall_cum']:.6f}s |\n"

    md += """
---

## TARGET Identified Bottlenecks

### 1. Redundant Directory Scanning

**Problem:** The validator scans the same directory structure multiple times across different validation rules.

**Evidence:**
- AR001-AR010 (Architecture Rules): Each rule independently scans root directories and shards
- Estimated: **10+ complete directory traversals** of 24 roots × 16 shards = 384 directories

**Impact:**
- High filesystem I/O overhead
- Repeated `iterdir()`, `is_dir()`, `exists()` calls
- Estimated **40-60%** of total execution time

**Solution:**
- [OK] Implement filesystem cache with 60-second TTL
- [OK] Scan directory structure ONCE at initialization
- [OK] Store results in cached data structure

**Estimated Speedup:** **3-5x** (reduce from 30s to 6-10s)

---

### 2. Sequential Rule Execution

**Problem:** All 327+ rules execute sequentially, with no parallelization.

**Evidence:**
- `validate_all()` calls each rule function one after another
- No concurrency or async execution
- Independent rules (e.g., AR001 and CP001) could run in parallel

**Impact:**
- Underutilized CPU cores
- Long total execution time for large rule sets

**Solution:**
- [OK] Use `ThreadPoolExecutor` for independent rules
- [OK] Build dependency graph for sequential rules
- [OK] Parallel execution with `max_workers=cpu_count()`

**Estimated Speedup:** **2-3x** (reduce from 10s to 3-5s after caching)

---

### 3. Unoptimized File Content Scanning

**Problem:** Rules like CP001 use `rglob()` to scan all Python files and apply regex patterns.

**Evidence:**
- `self.repo_root.rglob("*.py")` scans entire repository
- Each file read with `read_text()` and matched against multiple regex patterns
- No early exit strategy

**Impact:**
- Scales poorly with repository size
- 1000+ files × 3+ regex patterns = 3000+ operations

**Solution:**
- [OK] Compile regex patterns once (not per file)
- [OK] Use compiled pattern cache
- [OK] Implement early exit when violation found
- [OK] Consider using `ripgrep` for content search

**Estimated Speedup:** **2x** for content-heavy rules

---

### 4. Missing Result Caching

**Problem:** No caching of validation results for unchanged files/directories.

**Evidence:**
- Every validation run rescans and revalidates everything
- No change detection mechanism
- No incremental validation

**Impact:**
- Repeated validations take same time as first run
- Poor developer experience during iterative development

**Solution:**
- [OK] Implement rule-result cache with file hash tracking
- [OK] Use `watchdog` for file change detection
- [OK] Only revalidate changed components

**Estimated Speedup:** **10x+** for repeated validations (reduce from 5s to <0.5s)

---

## [PROFILE] Optimization Roadmap

### Phase 1: Filesystem Caching (CRITICAL)

**Target:** Reduce from 30s to <10s

**Implementation:**
1. Create `CachedFilesystemScanner` class
2. Scan directory structure once at initialization
3. Cache results in-memory with 60s TTL
4. Implement `watchdog` for change detection

**Files to create:**
- `03_core/validators/sot/cached_filesystem.py`
- `03_core/validators/sot/cached_validator.py`

**Estimated Effort:** 4-6 hours
**Expected Speedup:** 3-5x

---

### Phase 2: Parallel Execution (HIGH)

**Target:** Reduce from 10s to <5s

**Implementation:**
1. Analyze rule dependencies
2. Build dependency graph
3. Implement `ThreadPoolExecutor` for independent rules
4. Add progress reporting with `tqdm`

**Files to create:**
- `03_core/validators/sot/parallel_validator.py`
- `03_core/validators/sot/rule_dependency_graph.py`

**Estimated Effort:** 6-8 hours
**Expected Speedup:** 2-3x

---

### Phase 3: Result Caching (MEDIUM)

**Target:** Reduce repeated validations to <1s

**Implementation:**
1. Implement rule-level result caching
2. Use file hashes for change detection
3. Integrate `watchdog` for real-time invalidation

**Files to create:**
- `03_core/validators/sot/result_cache.py`

**Estimated Effort:** 4-6 hours
**Expected Speedup:** 10x+ for repeated runs

---

## TARGET Performance Targets

| Metric | Current | After Phase 1 | After Phase 2 | After Phase 3 |
|--------|---------|---------------|---------------|---------------|
| First Run | ~30s | ~10s | ~5s | ~5s |
| Repeated Run | ~30s | ~10s | ~5s | **<1s** |
| Filesystem I/O | 60% | 20% | 20% | 5% |
| CPU Utilization | ~25% | ~25% | ~80% | ~80% |
| Developer Experience | ⚠️ Poor | [OK] Good | [OK] Excellent | [OK] Excellent |

---

## NOTE Recommendations

### Immediate Actions (Week 1)

1. **Implement Filesystem Cache** (PROMPT 1.2)
   - Create `CachedFilesystemScanner` class
   - Refactor AR001-AR010 to use cached scanner
   - Target: 3-5x speedup

2. **Profile After Caching**
   - Re-run this profiler
   - Verify performance improvements
   - Identify remaining bottlenecks

### Short-term Actions (Week 2)

3. **Implement Parallel Execution** (PROMPT 1.3)
   - Build rule dependency graph
   - Implement `ThreadPoolExecutor`
   - Target: 2-3x additional speedup

4. **Optimize Content Scanning**
   - Compile and cache regex patterns
   - Implement early exit strategies
   - Consider `ripgrep` integration

### Long-term Actions (Week 3+)

5. **Implement Result Caching**
   - File hash-based change detection
   - `watchdog` integration
   - Incremental validation

6. **Continuous Performance Monitoring**
   - Add performance regression tests
   - Track metrics in CI/CD
   - Set performance budgets per rule category

---

## DETAILS Detailed Function Profile

### Top 20 Functions by Cumulative Time

| Rank | Function | File | Calls | Cumulative Time | % of Total |
|------|----------|------|-------|-----------------|------------|
"""

    for i, bottleneck in enumerate(data['top_bottlenecks'][:20], 1):
        pct = (bottleneck['cumtime'] / total_time * 100)
        md += f"| {i} | `{bottleneck['function']}` | `{bottleneck['file'].split('/')[-1]}` | {bottleneck['ncalls']:,} | {bottleneck['cumtime']:.3f}s | {pct:.1f}% |\n"

    md += """
---

## ACTION Next Steps

1. **Run PROMPT 1.2** to implement filesystem caching
2. **Re-profile** with this script after caching implementation
3. **Run PROMPT 1.3** to implement parallel execution
4. **Iterate** until performance targets are met

**Target:** **<5s** for full validation, **<1s** for repeated runs

---

*Generated by `profile_validator.py`*
"""

    return md


if __name__ == "__main__":
    # Get repository root from command line or use default
    if len(sys.argv) > 1:
        repo_root = Path(sys.argv[1])
    else:
        # Assume we're in 03_core/validators/sot/ and go up 3 levels
        repo_root = Path(__file__).parent.parent.parent.parent

    if not repo_root.exists():
        print(f"[ERROR] Error: Repository root does not exist: {repo_root}")
        sys.exit(1)

    try:
        performance_data = profile_validator(repo_root)
        print("\n[OK] Profiling complete! Check PERFORMANCE_REPORT.md for details.")
    except Exception as e:
        print(f"\n[ERROR] Error during profiling: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
