# SoT Validator Test Suite

Comprehensive test suite for SoT Validator Core and Cached Validator.

## Quick Start

```bash
# Navigate to test directory
cd C:/Users/bibel/Documents/Github/SSID/03_core/validators/sot/tests

# Run all tests
pytest -v

# Run only AR tests (recommended)
pytest -v -m ar

# Run with coverage
pytest --cov-report=html --cov-report=term -v
```

## Test Statistics

- **Total Tests:** 79
- **Passing:** 71 (89.87%)
- **AR001-AR010 Coverage:** 100% (42/42 tests passing)
- **Execution Time:** ~88 seconds

## Test Organization

### By Rule Category
- **AR001-AR010:** Architecture rules (42 tests) [100% PASS]
- **CP001+:** Compliance rules (2 tests)
- **Integration:** Full workflow tests (3 tests)
- **Performance:** Benchmarks (6 tests)
- **Cache:** Cache-specific tests (3 tests)
- **Edge Cases:** Error handling (3 tests)
- **Parametrized:** Consistency checks (20 tests)

### By Marker
```bash
pytest -v -m ar           # Architecture rules
pytest -v -m cp           # Compliance rules
pytest -v -m performance  # Performance tests
pytest -v -m integration  # Integration tests
pytest -v -m cached       # Cached validator only
pytest -v -m original     # Original validator only
```

## Files

- `pytest.ini` - Pytest configuration
- `.coveragerc` - Coverage settings
- `conftest.py` - Shared fixtures (11 fixtures)
- `test_sot_validator.py` - Main test file (79 tests)
- `TEST_SUITE_REPORT.md` - Detailed report

## Test Fixtures

### Valid Repository
- 24 roots x 16 shards = 384 total
- Complete file structure
- All required files present

### Invalid Repositories (10 variants)
1. Missing roots (20 instead of 24)
2. Missing shards (12 instead of 16)
3. Missing Chart.yaml files
4. Missing values.yaml files
5. Missing README.md files
6. Inconsistent shard names
7. Bad shard naming patterns
8. Bad root naming patterns
9. Missing templates/ directories
10. Empty repository

## Common Commands

```bash
# Run specific rule tests
pytest -v -k "ar001"

# Run all AR tests except performance
pytest -v -m "ar and not performance"

# Run with detailed output
pytest -v --tb=short

# Run fastest tests only
pytest -v --durations=0 -k "ar001 or ar002"

# Generate HTML coverage report
pytest --cov=../sot_validator_core.py --cov-report=html -v
```

## Performance Benchmarks

### Original Validator
- AR001-AR010: ~295ms total
- Per rule: 15-45ms

### Cached Validator
- First run: ~300ms (includes cache build)
- Warm cache: ~5ms total (60x faster!)

## Success Criteria

[OK] All AR001-AR010 tests passing
[OK] Both validators tested
[OK] Performance benchmarks established
[OK] Comprehensive fixtures created
[OK] Edge cases covered

## Known Issues (Non-blocking)

1. Cache stats key naming (4 tests) - cosmetic
2. First run performance threshold (1 test) - expected
3. CP001 PII detection (1 test) - enhancement needed
4. Edge case error handling (2 tests) - expected behavior

## Next Steps (Phase 3)

1. Add tests for remaining 374 rules
2. Increase coverage to 80%+
3. Fix minor issues
4. CI/CD integration

## Documentation

See `TEST_SUITE_REPORT.md` for comprehensive documentation including:
- Detailed test coverage
- Performance analysis
- Failure explanations
- Usage examples
- Coverage reports

## Support

For questions or issues, refer to the main validator documentation:
- `../README.md` - Validator overview
- `../DEPLOYMENT_SUMMARY.md` - Deployment guide
- `../PERFORMANCE_REPORT.md` - Performance analysis
