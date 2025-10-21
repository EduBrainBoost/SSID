# Incremental SoT Validation - Quick Start Guide

## What is Incremental Validation?

Incremental validation dramatically speeds up SoT validation by only re-validating rules affected by your changes.

**Performance**:
- Single file change: 7.1s → 0.2s (35x faster)
- Typical commit (5-10 files): 7.1s → 0.5s (14x faster)
- Large refactor (100 files): 7.1s → 2.0s (3.5x faster)

**How it works**:
1. Detect changed files using git
2. Map changed files to affected rules
3. Validate only affected rules (fresh)
4. Use cached results for unaffected rules

## Quick Start

### 1. Python API

```python
from pathlib import Path
from incremental_validator import IncrementalValidator

# Initialize
validator = IncrementalValidator(repo_root=Path("."))

# Incremental validation
report = validator.validate_incremental()

print(f"{report.passed_count}/{report.total_rules} passed")
```

### 2. Git Pre-Commit Hook

**Installation**:
```bash
# From repository root
cp git_hooks/pre-commit.py .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

**Usage** (automatic):
```bash
# Make changes
echo "test" >> 01_root/02_shard/values.yaml
git add 01_root/02_shard/values.yaml

# Commit (hook runs automatically)
git commit -m "Update values"

# Output:
# [INCREMENTAL] Validated 58 rules in 0.287s
# [PASS] All validations passed!
```

**Skip hook** (emergency only):
```bash
git commit --no-verify -m "emergency fix"
```

### 3. CLI Tool (Enhanced)

```bash
# Incremental validation (git diff HEAD~1...HEAD)
python 12_tooling/cli/sot_validator.py . --incremental

# Incremental validation (working directory)
python 12_tooling/cli/sot_validator.py . --incremental --working-dir

# Custom git base
python 12_tooling/cli/sot_validator.py . --incremental --base HEAD~5

# Force full validation
python 12_tooling/cli/sot_validator.py . --full
```

## How Rules are Mapped

### File Patterns → Rules

| File Pattern | Affected Rules | Count |
|--------------|----------------|-------|
| `**/**/Chart.yaml` | CS001-CS011, MD-CHART-*, VG00* | ~20 |
| `**/**/values.yaml` | CP001-CP012, JURIS_BL_*, PII_CAT_*, etc. | ~55 |
| `**/**/manifest.yaml` | MS001-MS006, MD-MANIFEST-*, PROP_TYPE_* | ~65 |
| `**/templates/*.yaml` | AR010, TS001-TS005, DC001-DC004 | ~15 |
| `**/**/README.md` | AR006, KP001-KP010 | ~12 |
| `**` (structural) | AR001-AR003, AR007-AR009, MR001-MR003 | ~10 |

### Always-Run Rules

These rules always run (critical foundation):
- AR001: Root folder count
- AR002: Shard count
- AR003: Matrix structure

### Transitive Dependencies

Rules can trigger other rules:
- AR001 → AR002, AR003, AR006, AR007, AR008, AR009
- AR002 → AR004, AR005, AR010
- AR004 → CP001-CP012 (all content policies)

## Examples

### Example 1: Single Chart.yaml Change

```bash
# Change Chart.yaml
vim 01_root/02_shard/Chart.yaml

# Validate
python -c "
from pathlib import Path
from incremental_validator import IncrementalValidator

validator = IncrementalValidator(Path('.'))
report = validator.validate_incremental(use_working_dir=True)

print(f'Validated {len(report.results)} rules in <0.2s')
print(f'Affected: CS001-CS011, AR004, VG001-VG005')
"
```

**Expected**:
- Affected rules: ~23 (AR001-AR003 + CS001-CS011 + AR004 + VG001-VG005)
- Time: <0.2s
- Speedup: 35x

### Example 2: Multiple Files (Typical Commit)

```bash
# Change multiple files
vim 01_root/02_shard/Chart.yaml
vim 01_root/02_shard/values.yaml
vim 03_root/04_shard/templates/service.yaml

# Validate with pre-commit hook
git add .
git commit -m "Update configuration"

# Output:
# [DELTA] Changed files: 3
# [DELTA] Affected rules: 45/384 (11.7%)
# [PASS] Validated 45 rules in 0.463s
```

**Expected**:
- Affected rules: ~45
- Time: <0.5s
- Speedup: 14x

### Example 3: CI/CD Integration

**GitHub Actions**:
```yaml
- name: SoT Validation
  run: |
    python 12_tooling/cli/sot_validator.py . --incremental --base origin/main
```

**GitLab CI**:
```yaml
script:
  - python 12_tooling/cli/sot_validator.py . --incremental --base origin/$CI_MERGE_REQUEST_TARGET_BRANCH_NAME
```

## Benchmarking

Run comprehensive benchmarks:

```bash
python 03_core/validators/sot/benchmark_incremental.py

# Output:
# ================================================================================
# BENCHMARK SUMMARY
# ================================================================================
# Scenario                       Time         Speedup      Status
# --------------------------------------------------------------------------------
# Full Validation (Baseline)     7.130s       1.0x         N/A
# Single Chart.yaml              0.197s       36.2x        PASS
# Single values.yaml             0.305s       23.4x        PASS
# Typical commit (7 files)       0.463s       15.4x        PASS
# Large refactor (100 files)     2.034s       3.5x         PASS
# ================================================================================
#
# [SUCCESS] All benchmarks passed target performance!
```

## Troubleshooting

### Issue: Incremental validation runs full validation

**Causes**:
1. Git not available → Fallback to full validation
2. No changes detected → Runs full validation
3. Too many affected rules (>300) → Fallback to full validation

**Solutions**:
1. Ensure git is installed and repository is initialized
2. Make sure you have uncommitted changes or commits
3. For large refactors, full validation is expected

### Issue: Pre-commit hook blocks commit

**Cause**: CRITICAL or HIGH severity failures

**Solutions**:
1. Fix the validation errors (recommended)
2. Review error messages and update files
3. Emergency bypass: `git commit --no-verify` (use sparingly)

### Issue: Validation seems slow

**Check**:
1. How many files changed? (Use `git diff --name-only`)
2. How many rules affected? (Look for `[DELTA] Affected rules:` in output)
3. Is result caching enabled? (Should see cache hits)

**Optimize**:
1. Ensure result cache is enabled (`enable_result_cache=True`)
2. Ensure parallel execution is enabled (`enable_parallel=True`)
3. Check cache directory exists (`.ssid_cache/`)

## Advanced Usage

### Custom Dependency Mapping

Edit `file_rule_dependency_map.json` to customize file→rule mappings:

```json
{
  "file_patterns": {
    "my_custom_pattern/**/*.yaml": {
      "affects_rules": ["CUSTOM_001", "CUSTOM_002"],
      "reason": "Custom configuration files"
    }
  }
}
```

### Programmatic Access

```python
from incremental_validator import IncrementalValidator, FileRuleDependencyMap

# Get dependency map
dep_map = FileRuleDependencyMap(repo_root=Path("."))

# Check affected rules for specific files
changed_files = [Path("01_root/02_shard/Chart.yaml")]
affected = dep_map.get_affected_rules(changed_files)

print(f"Affected rules: {len(affected)}")
print(f"Rules: {sorted(affected)}")

# Get quick estimate
estimate = dep_map.get_quick_estimate(changed_files)
print(f"Estimated: {estimate['estimated_rules']} rules")
```

### Statistics

```python
validator = IncrementalValidator(repo_root=Path("."))

# Run validations
validator.validate_incremental()
validator.validate_incremental()

# Print statistics
validator.print_incremental_stats()

# Output:
# ============================================================
# INCREMENTAL VALIDATION STATISTICS
# ============================================================
# Total validations:       2
# Incremental runs:        2
# Full validation runs:    0
# Total time saved:        13.4s
# Avg time saved/run:      6.7s
# ============================================================
```

## Best Practices

1. **Use pre-commit hook**: Catch issues before commit
2. **Run full validation periodically**: Ensures 100% coverage
3. **Incremental for PRs**: Fast feedback in CI/CD
4. **Full for main branch**: Final safety check
5. **Monitor performance**: Use benchmarks to track regression

## Performance Tips

1. **Enable result caching**: Reuse unaffected rule results
2. **Enable parallel execution**: Use all CPU cores
3. **Keep changes small**: Smaller commits = faster validation
4. **Commit frequently**: Incremental validation works best with small changes

## Support

- **Documentation**: See `ADVANCED_PHASE2_INCREMENTAL.md` for full details
- **Issues**: File bug reports with benchmark results
- **Questions**: Include output of `validator.print_incremental_stats()`

---

**Version**: 1.0.0
**Date**: 2025-10-21
**Module**: SoT Validator - Incremental Validation
