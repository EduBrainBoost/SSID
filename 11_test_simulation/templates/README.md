# Test Templates - SSID Test Suite

**Version:** Sprint 2 Week 5-6 Day 2
**Purpose:** Standardized test templates for rapid test development

---

## Available Templates

### 1. `test_template_validator.py`
**Use for:** Validator functions (schema validation, data validation)
**Target modules:** `02_audit_logging/validators/`
**Coverage impact:** ~2-5% per validator

**Key test scenarios:**
- ✅ Valid input (should pass)
- ❌ Invalid input (should fail with errors)
- ⚠️ Edge cases (empty, None, wrong types)
- 📊 Boundary values
- 🔍 Error message validation

**Example usage:**
```bash
cp templates/test_template_validator.py tests_audit/test_check_log_schema.py
# Edit: Replace VALIDATOR_NAME with check_log_schema
# Edit: Replace VALIDATOR_FUNCTION with validate_log_schema
```

---

### 2. `test_template_anti_gaming.py`
**Use for:** Anti-gaming detectors (anomaly detection, fraud detection)
**Target modules:** `02_audit_logging/anti_gaming/`, `23_compliance/anti_gaming/`
**Coverage impact:** ~5-10% per detector

**Key test scenarios:**
- ✅ Normal activity (should NOT flag)
- ❌ Suspicious activity (SHOULD flag)
- ⚠️ Edge cases (empty, single event)
- 🔧 Configuration tests (threshold, window)
- 📊 Anomaly details validation

**Example usage:**
```bash
cp templates/test_template_anti_gaming.py tests_compliance/test_replay_attack_detector.py
# Edit: Replace DETECTOR_MODULE with replay_attack_detector
# Edit: Replace DETECTOR_CLASS with ReplayAttackDetector
```

---

### 3. `test_template_health.py`
**Use for:** Health check systems (service monitoring, dependency checks)
**Target modules:** `03_core/healthcheck/`
**Coverage impact:** ~3-8% per health checker

**Key test scenarios:**
- ✅ All healthy (all systems ok)
- ⚠️ Degraded (slow/partial failure)
- ❌ Down (complete failure)
- ⏱️ Timeout handling
- 🔌 Dependency checks
- 📡 Port accessibility

**Example usage:**
```bash
cp templates/test_template_health.py tests_core/test_health_check_core.py
# Edit: Replace HEALTH_MODULE with health_check_core
# Edit: Replace HEALTH_CLASS with HealthChecker
```

---

### 4. `test_template_bridge.py`
**Use for:** Bridges and interconnects (data push, API communication)
**Target modules:** `02_audit_logging/interconnect/`
**Coverage impact:** ~2-5% per bridge

**Key test scenarios:**
- ✅ Successful push (HTTP 200)
- ❌ Failed push (connection error, timeout, HTTP errors)
- 🔄 Data transformation
- 🔐 Authentication headers
- 🔁 Retry logic (if applicable)
- 📦 Large payloads

**Example usage:**
```bash
cp templates/test_template_bridge.py tests_audit/test_bridge_compliance_push.py
# Edit: Replace BRIDGE_MODULE with bridge_compliance_push
# Edit: Replace BRIDGE_CLASS with CompliancePushBridge
```

---

## Quick Start Guide

### Step 1: Choose Template
Pick the template that matches your module type:
- Validators → `test_template_validator.py`
- Anti-Gaming → `test_template_anti_gaming.py`
- Health Checks → `test_template_health.py`
- Bridges → `test_template_bridge.py`

### Step 2: Copy Template
```bash
cp templates/test_template_CATEGORY.py tests_TARGET/test_YOUR_MODULE.py
```

### Step 3: Edit Placeholders
Replace these placeholders in the copied file:
- `VALIDATOR_NAME` → actual module name
- `VALIDATOR_FUNCTION` → actual function name
- `DETECTOR_MODULE` → actual detector module
- `DETECTOR_CLASS` → actual detector class
- `HEALTH_MODULE` → actual health module
- `HEALTH_CLASS` → actual health class
- `BRIDGE_MODULE` → actual bridge module
- `BRIDGE_CLASS` → actual bridge class

### Step 4: Implement Test Cases
- Fill in TODO comments with actual test data
- Adjust assertions based on module behavior
- Add module-specific edge cases

### Step 5: Run Tests
```bash
pytest tests_TARGET/test_YOUR_MODULE.py -v
```

---

## Template Features

### Common Features (All Templates)

✅ **Import helpers** - Automatic sys.path setup for number-prefixed modules
✅ **Fixtures** - Reusable test data from `conftest.py`
✅ **Edge cases** - Empty, None, malformed inputs
✅ **Error handling** - Exception and error message tests
✅ **Performance tests** - Optional performance benchmarks

### Mocking Patterns

All templates include common mocking patterns:

**HTTP Mocking:**
```python
with patch('requests.get') as mock_get:
    mock_get.return_value.status_code = 200
    # test code
```

**Socket Mocking:**
```python
with patch('socket.socket') as mock_socket:
    mock_socket_instance.connect_ex.return_value = 0
    # test code
```

**Time Mocking:**
```python
from freezegun import freeze_time
with freeze_time("2025-01-01 12:00:00"):
    # test code
```

---

## Coverage Strategy

### Phase 1: Quick Wins (Days 1-2)
**Target:** 6.8% → 10% coverage
**Templates:** Validator template
**Modules:**
- `check_hash_chain.py` (edge cases only)
- `identity_score_calculator.py` (new tests)

**Expected effort:** 2.5 hours
**Expected gain:** +1.2%

---

### Phase 2: Health System (Days 3-5)
**Target:** 10% → 20% coverage
**Templates:** Health template
**Modules:**
- `health_check_core.py`
- `health_audit_logger.py`
- `generate_health_wrappers.py`

**Expected effort:** 9 hours
**Expected gain:** +10%

---

### Phase 3: Anti-Gaming (Days 6-15)
**Target:** 20% → 75% coverage
**Templates:** Anti-gaming template
**Modules:**
- `time_skew_analyzer.py`
- `anomaly_rate_guard.py`
- `replay_attack_detector.py`
- `overfitting_detector.py`
- `dependency_graph_generator.py` (both modules)
- `circular_dependency_validator.py`
- `badge_integrity_checker.py`

**Expected effort:** 45 hours
**Expected gain:** +54%

---

### Phase 4: Infrastructure (Days 16-18)
**Target:** 75% → 85%+ coverage
**Templates:** Bridge template
**Modules:**
- `bridge_compliance_push.py`
- `bridge_23compliance.py`
- `bridge_foundation.py`
- `policy_engine.py`
- `compliance_chain_trigger.py`

**Expected effort:** 16 hours
**Expected gain:** +16%

---

## Best Practices

### ✅ DO

- **Use fixtures** from `conftest.py` instead of hardcoding test data
- **Mock external dependencies** (HTTP, DB, filesystem)
- **Test edge cases** (empty, None, malformed)
- **Assert error messages** (not just that errors occur)
- **Add docstrings** to every test function
- **Use descriptive test names** (`test_validator_handles_empty_input`)

### ❌ DON'T

- Don't hardcode test data (use fixtures)
- Don't skip error handling tests
- Don't test implementation details (test behavior)
- Don't write tests that depend on external services
- Don't leave TODO comments unfilled
- Don't forget to remove template comments

---

## Testing Checklist

Before marking a module as "complete", ensure:

- [ ] All TODO comments replaced with real test code
- [ ] Valid input tests (happy path)
- [ ] Invalid input tests (error cases)
- [ ] Edge cases (empty, None, boundaries)
- [ ] Error messages validated
- [ ] Integration with fixtures (if applicable)
- [ ] Performance tests (if applicable)
- [ ] All tests passing (`pytest tests_*/test_*.py -v`)
- [ ] Coverage increased (`pytest --cov`)

---

## Troubleshooting

### Import Errors
**Problem:** `ModuleNotFoundError: No module named '02_audit_logging'`

**Solution:** Use import helper from `conftest.py`:
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "02_audit_logging"))
```

---

### Fixture Not Found
**Problem:** `fixture 'sample_audit_log' not found`

**Solution:** Ensure `conftest.py` is in parent directory:
```
11_test_simulation/
├── conftest.py          ← Fixtures defined here
├── tests_audit/
│   └── test_*.py        ← Tests use fixtures
```

---

### Mocking Not Working
**Problem:** Real HTTP requests being made instead of mocks

**Solution:** Patch at the right location:
```python
# ❌ Wrong
with patch('requests.get'):
    validator.check()  # validator uses 'module.requests.get'

# ✅ Correct
with patch('module.requests.get'):
    validator.check()
```

---

## Dependencies

Required packages (install with `pip install`):

```bash
pip install pytest pytest-cov pytest-mock freezegun requests-mock
```

**Core:**
- `pytest` - Test framework
- `pytest-cov` - Coverage reports
- `pytest-mock` - Mocking utilities

**Optional:**
- `freezegun` - Time mocking
- `requests-mock` - HTTP mocking
- `faker` - Fake data generation

---

## Support

**Documentation:** `23_compliance/evidence/sprint2/TEST_STRATEGIE_SPRINT2.md`
**Examples:** `tests_compliance/`, `tests_audit/`
**Fixtures:** `11_test_simulation/conftest.py`

---

**Last Updated:** 2025-10-10
**Version:** 1.0.0
**Maintainer:** SSID Compliance Team
