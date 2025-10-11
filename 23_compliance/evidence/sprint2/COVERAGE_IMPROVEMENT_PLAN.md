# Sprint 2 Coverage Improvement Plan
**Date:** 2025-10-09
**Sprint:** Sprint 2 - Week 5-6
**Current Coverage:** 4.91%
**Target Coverage:** 80%
**Gap:** 75.09 percentage points

---

## Executive Summary

**Challenge:** Baseline coverage analysis reveals only 4.91% test coverage across critical modules. 5 modules below 80% threshold, 26 files completely untested.

**Strategy:** Incremental, prioritized approach focusing on highest-impact modules first. Combine new test creation with test infrastructure improvements.

**Timeline:** 2 weeks (Week 5-6 of Sprint 2)

**Expected Outcome:** 60-80% coverage by end of Sprint 2

---

## Current State Analysis

### Coverage Baseline
| Module | Coverage | Statements | Missing | Status |
|--------|----------|------------|---------|--------|
| 02_audit_logging | 0.00% | 776 | 776 | CRITICAL |
| 03_core | 0.00% | 229 | 229 | CRITICAL |
| 24_meta_orchestration | 0.00% | 113 | 113 | CRITICAL |
| 08_identity_score | 0.00% | 21 | 21 | CRITICAL |
| 23_compliance | 12.76% | 713 | 622 | NEEDS WORK |

### What's Working
- **Test Infrastructure:** pytest, coverage.py, fixtures all configured
- **Existing Tests:** 75 passing tests in tests_compliance/
- **Anti-Gaming Tests:** Good coverage of anti-gaming validators (13 tests)

### Critical Gaps
1. **02_audit_logging:** 776 uncovered statements - validators, anti-gaming, bridges
2. **03_core:** 229 uncovered statements - health checks, bridge foundation
3. **23_compliance:** 622 uncovered statements - dependency graphs, policy engine

---

## Phased Implementation Plan

### Phase 1: Quick Wins (Days 1-2) - Target: +20-30%

**Focus:** High-value, easy-to-test files

#### Priority 1: Validators (02_audit_logging/validators/)
These are pure functions - easiest to test!

**Files:**
1. `check_hash_chain.py` (21 stmts) - 2 hours
2. `check_log_schema.py` (8 stmts) - 1 hour
3. `check_worm_storage.py` (9 stmts) - 1 hour

**Tests Already Exist:**
- test_hash_chain.py (FIXED import issues)
- test_log_schema.py (FIXED import issues)
- test_worm_meta.py (FIXED import issues)

**Action:** Run these tests and verify coverage!

**Expected Gain:** ~38 statements = +2.0%

#### Priority 2: Identity Score Calculator (08_identity_score/)
**Files:**
1. `identity_score_calculator.py` (21 stmts) - 2 hours

**Action:** Create test_identity_score.py with:
- Valid score calculation
- Edge cases (0, 100, negative)
- Invalid inputs

**Expected Gain:** ~21 statements = +1.1%

#### Priority 3: Simple Anti-Gaming Modules
**Files:**
1. `detect_duplicate_identity_hashes.py` (56 stmts, currently 30% covered) - 3 hours
2. `detect_circular_dependencies.py` (88 stmts, currently 45% covered) - 3 hours

**Action:** Expand existing tests to cover remaining branches

**Expected Gain:** ~60 statements = +3.2%

**Phase 1 Total:** +6-8% coverage (4.91% -> 11-13%)

---

### Phase 2: Core Infrastructure (Days 3-5) - Target: +30-40%

**Focus:** Health checks, bridges, core functionality

#### Health Check System (03_core/healthcheck/)
**Files:**
1. `health_check_core.py` (85 stmts) - 4 hours
2. `health_audit_logger.py` (43 stmts) - 3 hours
3. `generate_health_wrappers.py` (65 stmts) - 4 hours

**Test Strategy:**
- Mock HTTP endpoints
- Test status transitions (OK -> DEGRADED -> DOWN)
- Port checking logic
- Registry integration

**Create:** `11_test_simulation/tests_core/test_health_system.py`

**Expected Gain:** ~193 statements = +10.4%

#### Bridge Connectors (02_audit_logging/interconnect/, 03_core/interconnect/)
**Files:**
1. `bridge_compliance_push.py` (73 stmts) - 4 hours
2. `bridge_23compliance.py` (36 stmts) - 2 hours
3. `bridge_foundation.py` (32 stmts) - 2 hours

**Test Strategy:**
- Mock cross-module calls
- Test data transformation
- Error handling and retries

**Create:** `11_test_simulation/tests_bridges/test_bridge_connectors.py`

**Expected Gain:** ~141 statements = +7.6%

**Phase 2 Total:** +18% coverage (11-13% -> 29-31%)

---

### Phase 3: Anti-Gaming Deep Dive (Days 6-8) - Target: +25-35%

**Focus:** Remaining anti-gaming modules in 02_audit_logging

#### Anti-Gaming Suite (02_audit_logging/anti_gaming/)
**Files:**
1. `time_skew_analyzer.py` (107 stmts) - 5 hours
2. `anomaly_rate_guard.py` (111 stmts) - 5 hours
3. `replay_attack_detector.py` (96 stmts) - 5 hours
4. `overfitting_detector.py` (95 stmts) - 5 hours
5. `dependency_graph_generator.py` (95 stmts) - 5 hours
6. `circular_dependency_validator.py` (116 stmts) - 5 hours

**Test Strategy:**
- Create test fixtures for common scenarios
- Time-based tests (use freezegun for time mocking)
- Rate limiting tests (use time.sleep sparingly)
- Graph validation tests (use networkx if available)

**Create:**
- `11_test_simulation/tests_audit/test_anti_gaming_full_suite.py`
- Reuse existing tests from `tests_compliance/`

**Expected Gain:** ~620 statements = +33.5%

**Phase 3 Total:** +33% coverage (29-31% -> 62-64%)

---

### Phase 4: Policy Engine & Orchestration (Days 9-10) - Target: +15-20%

**Focus:** Remaining high-priority files

#### Policy Engine (23_compliance/policies/)
**Files:**
1. `policy_engine.py` (42 stmts) - 3 hours

**Test Strategy:**
- Policy loading and validation
- Rule evaluation
- Policy conflicts

**Create:** `11_test_simulation/tests_compliance/test_policy_engine.py`

**Expected Gain:** ~42 statements = +2.3%

#### Compliance Chain Trigger (24_meta_orchestration/)
**Files:**
1. `compliance_chain_trigger.py` (113 stmts) - 6 hours

**Test Strategy:**
- Event triggering
- Chain execution
- Error propagation

**Create:** `11_test_simulation/tests_orchestration/test_compliance_chain.py`

**Expected Gain:** ~113 statements = +6.1%

#### Dependency Graph Generators
**Files:**
1. `23_compliance/anti_gaming/dependency_graph_generator.py` (216 stmts) - 8 hours
2. `23_compliance/anti_gaming/badge_integrity_checker.py` (168 stmts, 31% covered) - 6 hours

**Test Strategy:**
- Graph construction
- Cycle detection
- Badge validation logic

**Expected Gain:** ~260 statements = +14.0%

**Phase 4 Total:** +22% coverage (62-64% -> 84-86%)

---

## Test Infrastructure Improvements

### 1. Test Templates (Day 1)
Create reusable test templates for common patterns:

**File:** `11_test_simulation/templates/`
- `test_template_validator.py` - For validator modules
- `test_template_bridge.py` - For bridge connectors
- `test_template_health.py` - For health checks
- `test_template_anti_gaming.py` - For anti-gaming detectors

**Benefit:** Reduce time per test from 30min to 15min

### 2. Fixtures & Helpers (Day 2)
**File:** `11_test_simulation/conftest.py`

```python
import pytest

@pytest.fixture
def sample_audit_log():
    """Sample audit log entries for testing"""
    return [
        {
            "ts": "2025-01-01T00:00:00Z",
            "level": "INFO",
            "message": "test",
            "source": "unit-test",
            "hash": "abc123"
        }
    ]

@pytest.fixture
def sample_hash_chain():
    """Sample hash chain for testing"""
    import hashlib
    def h(i, prev, payload):
        return hashlib.sha256(f"{i}|{prev}|{payload}".encode()).hexdigest()

    chain = [
        {
            "index": 0,
            "payload": "genesis",
            "prev_hash": "GENESIS",
            "hash": h(0, "GENESIS", "genesis")
        }
    ]
    return chain

@pytest.fixture
def mock_health_endpoint(monkeypatch):
    """Mock HTTP health endpoint"""
    def mock_get(*args, **kwargs):
        class MockResponse:
            status_code = 200
            def json(self):
                return {"status": "healthy"}
        return MockResponse()

    monkeypatch.setattr("requests.get", mock_get)
```

### 3. Coverage CI Integration (Day 3)
**File:** `.github/workflows/ci_coverage_enforcement.yml`

```yaml
name: Coverage Enforcement CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  coverage-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install pytest pytest-cov

      - name: Run tests with coverage
        run: |
          pytest --cov=. --cov-report=json --cov-report=term-missing

      - name: Check coverage threshold
        run: |
          COVERAGE=$(python -c "import json; print(json.load(open('coverage.json'))['totals']['percent_covered'])")
          echo "Coverage: $COVERAGE%"

          if (( $(echo "$COVERAGE < 60.0" | bc -l) )); then
            echo "ERROR: Coverage $COVERAGE% below minimum 60%"
            exit 1
          fi

      - name: Upload coverage artifact
        uses: actions/upload-artifact@v4
        with:
          name: coverage-report
          path: coverage.json
```

**Thresholds:**
- Week 5 (Days 1-5): >= 30%
- Week 6 (Days 6-10): >= 60%
- Sprint 2 End: >= 80%

---

## Implementation Schedule

### Week 5: Foundation (30-60% coverage)

**Day 1 (Monday):**
- ✅ Run coverage baseline (DONE)
- ✅ Create analysis tool (DONE)
- [ ] Fix existing validator tests
- [ ] Create test templates
- [ ] Set up fixtures in conftest.py

**Day 2 (Tuesday):**
- [ ] Phase 1: Validators (check_hash_chain, check_log_schema, check_worm_storage)
- [ ] Phase 1: Identity score calculator
- [ ] Run coverage - Target: 10-12%

**Day 3 (Wednesday):**
- [ ] Phase 1: Expand anti-gaming tests (duplicates, circular deps)
- [ ] Create coverage CI workflow
- [ ] Run coverage - Target: 15-18%

**Day 4 (Thursday):**
- [ ] Phase 2: Health check core tests
- [ ] Phase 2: Health audit logger tests
- [ ] Run coverage - Target: 25-30%

**Day 5 (Friday):**
- [ ] Phase 2: Bridge connector tests
- [ ] Phase 2: Health wrapper generator tests
- [ ] Run coverage - Target: 35-40%
- [ ] Week 5 checkpoint review

### Week 6: Deep Coverage (60-80%+ coverage)

**Day 6 (Monday):**
- [ ] Phase 3: Time skew analyzer tests
- [ ] Phase 3: Anomaly rate guard tests
- [ ] Run coverage - Target: 45-50%

**Day 7 (Tuesday):**
- [ ] Phase 3: Replay attack detector tests
- [ ] Phase 3: Overfitting detector tests
- [ ] Run coverage - Target: 55-60%

**Day 8 (Wednesday):**
- [ ] Phase 3: Dependency graph generator tests (02_audit_logging)
- [ ] Phase 3: Circular dependency validator tests
- [ ] Run coverage - Target: 65-70%

**Day 9 (Thursday):**
- [ ] Phase 4: Policy engine tests
- [ ] Phase 4: Compliance chain trigger tests
- [ ] Run coverage - Target: 72-76%

**Day 10 (Friday):**
- [ ] Phase 4: Dependency graph generator tests (23_compliance)
- [ ] Phase 4: Badge integrity checker expansion
- [ ] Final coverage run - Target: 78-82%
- [ ] Sprint 2 Week 5-6 completion report

---

## Resource Allocation

### Estimated Effort
- **Total Uncovered Statements:** 1,761
- **Tests to Create:** ~176 (1 test per 10 lines)
- **Time per Test:** ~30 min (reduced to 15 min with templates)
- **Total Effort:** ~44-88 hours (5.5-11 days)

### Parallelization Opportunities
- Validator tests (independent)
- Bridge tests (independent)
- Anti-gaming modules (independent after fixtures)

### Automation
- Test template generation
- Fixture auto-generation from code signatures
- Coverage diff in CI (show coverage change per PR)

---

## Success Criteria

### Primary Goal
- **Coverage >= 80%** by end of Sprint 2 Week 6

### Secondary Goals
1. All critical modules >= 60% coverage
2. No files with 0% coverage in priority modules
3. CI enforcement active
4. Test templates created and documented

### Stretch Goals
- Coverage >= 85%
- All modules >= 70%
- Integration tests for cross-module workflows

---

## Risk Mitigation

### Risk 1: Complex Module Logic
**Modules:** dependency_graph_generator.py, compliance_chain_trigger.py

**Mitigation:**
- Start with simple happy-path tests
- Add edge case tests incrementally
- Use mocking for external dependencies
- Consider deferring <5% to Sprint 3 if truly complex

### Risk 2: Import/Dependency Issues
**Issue:** Modules starting with numbers (02_, 03_, etc.)

**Mitigation:**
- ✅ Fixed with sys.path manipulation (DONE for validators)
- Create import helper in conftest.py
- Document pattern for future tests

### Risk 3: Time Constraints
**Issue:** 11 days of work, 10 days available

**Mitigation:**
- Prioritize ruthlessly (Phases 1-3 get to ~65%)
- Phase 4 is "nice to have" for 80%
- Accept 75-78% as "good enough" if needed
- Defer remaining coverage to Sprint 3

### Risk 4: Test Maintenance Overhead
**Issue:** 176+ new tests to maintain

**Mitigation:**
- Use templates for consistency
- Comprehensive docstrings
- Group related tests in same file
- Regular test review in Sprint 3+

---

## Deliverables

### Code Artifacts
1. **New Test Files:** ~15-20 files in 11_test_simulation/
2. **Test Templates:** 4 templates in 11_test_simulation/templates/
3. **Fixtures:** conftest.py with 10+ shared fixtures
4. **CI Workflow:** .github/workflows/ci_coverage_enforcement.yml

### Documentation
1. **Coverage Report:** COVERAGE_ANALYSIS_REPORT.md (✅ DONE)
2. **Improvement Plan:** COVERAGE_IMPROVEMENT_PLAN.md (this document)
3. **Test Writing Guide:** TEST_WRITING_GUIDE.md (to be created)
4. **Final Sprint 2 Report:** SPRINT2_WEEK5_6_COMPLETION_REPORT.md

### Evidence
1. **Baseline Coverage:** coverage_sprint2.json (✅ DONE)
2. **Daily Coverage Snapshots:** coverage_day{1-10}.json
3. **Final Coverage:** coverage_sprint2_final.json
4. **Coverage Trend Chart:** coverage_trend.png (optional)

---

## Next Steps (Immediate)

1. **Fix Validator Tests** (30 min)
   - Verify test_hash_chain.py works with fixed imports
   - Verify test_log_schema.py works
   - Verify test_worm_meta.py works
   - Run: `pytest 11_test_simulation/tests_audit/ --cov=02_audit_logging/validators -v`

2. **Create Test Templates** (1 hour)
   - Validator template
   - Bridge template
   - Health check template
   - Anti-gaming template

3. **Set Up Fixtures** (1 hour)
   - Create conftest.py
   - Add common fixtures (audit logs, hash chains, health responses)
   - Document usage

4. **Begin Phase 1** (4-6 hours)
   - Complete validator coverage
   - Add identity score tests
   - Expand anti-gaming tests

**Today's Target:** 10-12% coverage (up from 4.91%)

---

**Status:** READY TO IMPLEMENT
**Next Action:** Fix and run validator tests
**Owner:** Claude Code + SSID Team
**Deadline:** End of Sprint 2 (2 weeks)

---

**Progress Tracking:**
- [ ] Phase 1 Complete (Days 1-2)
- [ ] Phase 2 Complete (Days 3-5)
- [ ] Phase 3 Complete (Days 6-8)
- [ ] Phase 4 Complete (Days 9-10)
- [ ] Coverage >= 80% achieved
