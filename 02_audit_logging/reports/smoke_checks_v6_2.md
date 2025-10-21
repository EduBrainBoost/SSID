# Smoke Checks v6.2 - Quick Verification Guide
## Phase 5: Funktionales Policy Enforcement

**Purpose**: Schnelle 3-Schritt-Verifikation des Policy-Enforcement-Zustands
**Duration**: < 30 Sekunden
**When to Use**: Nach jedem Policy-Change, vor jedem Commit, nach jedem CI-Run

---

## Quick-Verify (3-Step Smoke Checks)

### 1. Rego-Syntax & Paket-Gesundheit ✅

**Command**:
```bash
opa check 23_compliance/policies/03_core_policy_stub_v6_0.rego
opa check 23_compliance/policies/23_compliance_policy_stub_v6_0.rego
```

**Expected Output**:
```
# No output = success (exit code 0)
```

**What This Tests**:
- ✅ Rego syntax is valid
- ✅ Package structure is correct
- ✅ No undefined references
- ✅ Policy can be loaded by OPA runtime

**Failure Indicators**:
- `rego_parse_error` → Syntax error in policy
- `rego_unsafe_var_error` → Undefined variable reference
- `rego_type_error` → Type mismatch in rule

---

### 2. Enforce Mind. 1 Violation-DENY (Fail-Fast) ✅

**Command**:
```bash
# 03_core: Invalid transaction signature must be denied
opa eval -d 23_compliance/policies/03_core_policy_stub_v6_0.rego \
  -i 11_test_simulation/testdata/03_core/canary_violation_invalid_signature.json \
  -f json "data.ssid.03_core.v6_0.deny"

# 23_compliance: Invalid syntax must be denied
opa eval -d 23_compliance/policies/23_compliance_policy_stub_v6_0.rego \
  -i 11_test_simulation/testdata/23_compliance/canary_violation_invalid_syntax.json \
  -f json "data.ssid.23_compliance.v6_0.deny"
```

**Expected Output**:
```json
{
  "result": [
    {
      "expressions": [
        {
          "value": [
            "Transaction signature invalid - denied by 03_core policy"
          ],
          "text": "data.ssid.03_core.v6_0.deny",
          "location": {...}
        }
      ]
    }
  ]
}
```

**What This Tests**:
- ✅ Deny rules are functional (not stub)
- ✅ Violations trigger non-empty deny array
- ✅ Policies prevent "always-true" / "always-false" behavior

**Failure Indicators**:
- `"value": []` → Policy did NOT deny violation (enforcement broken)
- `"value": null` → Policy rule undefined or not executed
- Exit code ≠ 0 → OPA evaluation error

**CI Fail-Fast Logic**:
```bash
DENY_COUNT=$(echo "$DENY_OUTPUT" | jq -r '.result[0].expressions[0].value | length')

if [ "$DENY_COUNT" -eq 0 ]; then
  echo "❌ ENFORCEMENT FAILURE: Policy did not deny violation"
  exit 1  # Build fails
fi
```

---

### 3. Tests (Ohne xfail, Echte Allow/Deny-Pfade) ✅

**Command**:
```bash
pytest -q 11_test_simulation/tests/test_03_core_policy_stub_v6_0.py
pytest -q 11_test_simulation/tests/test_23_compliance_policy_stub_v6_0.py
```

**Expected Output**:
```
11_test_simulation/tests/test_03_core_policy_stub_v6_0.py ...........  [100%]
11 passed in 2.45s

11_test_simulation/tests/test_23_compliance_policy_stub_v6_0.py ...........  [100%]
11 passed in 2.31s
```

**What This Tests**:
- ✅ All 22 tests pass (11 per policy)
- ✅ No xfail markers (real assertions, not skipped)
- ✅ Happy Path, Violation, and Boundary cases covered
- ✅ Real OPA CLI invocation via subprocess

**Failure Indicators**:
- `FAILED` → Test assertion failed (policy behavior incorrect)
- `XFAIL` → Test marked as expected failure (Phase 4 stub behavior - should not exist in Phase 5)
- `ERROR` → Test execution error (OPA not installed, file missing, etc.)

---

## Canary Tests (CI Early Warning System)

**Location**: `11_test_simulation/testdata/{policy}/canary_*.json`

**Purpose**: Fixed minimal inputs that detect unintended policy changes

### 03_core Canary Inputs

1. **canary_happy_did_operation.json** → Must ALLOW (valid DID operation)
2. **canary_violation_invalid_signature.json** → Must DENY (invalid transaction signature)
3. **canary_violation_zero_amount.json** → Must DENY (zero amount transaction)

### 23_compliance Canary Inputs

1. **canary_happy_policy_deployment.json** → Must ALLOW (valid policy deployment)
2. **canary_violation_invalid_syntax.json** → Must DENY (invalid syntax)
3. **canary_violation_wasm_dependencies.json** → Must DENY (11 dependencies > limit)

**CI Integration**:
```yaml
- name: Canary Tests - 03_core Happy Path
  run: |
    ALLOW_RESULT=$(opa eval -d policy.rego -i canary_happy.json -f json "data.allow")
    if [ "$ALLOW_RESULT" != "true" ]; then
      exit 1  # Build fails if happy path breaks
    fi
```

---

## Definition of Done - Phase 5 ✅

All checks below must pass:

| Criterion | Status | Validation |
|-----------|--------|------------|
| **Rego-Stubs → Functional Rules** | ✅ | `ready=true`, real allow/deny logic |
| **22 Tests (Happy/Violation/Boundary)** | ✅ | No xfail, real assertions |
| **CI Job Exits on Violation** | ✅ | `opa-enforcement` job, exit 1 on failure |
| **Audit Report** | ✅ | `policy_enforcement_summary_v6_2.md` |
| **Zero Root-Violations** | ✅ | No bundles, no root files |
| **Canary Tests in CI** | ✅ | 6 canary inputs (3 per policy) |

---

## Fail-Fast Thresholds (CI Enforcement)

### Threshold 1: Happy Path Must Allow
```bash
# At least 1 ALLOW per policy for valid input
ALLOW_RESULT=$(opa eval ... "data.allow")
if [ "$ALLOW_RESULT" != "true" ]; then
  echo "❌ FAIL-FAST: Happy path did not allow valid request"
  exit 1
fi
```

### Threshold 2: Violation Must Deny
```bash
# At least 1 DENY per violation fixture
DENY_COUNT=$(opa eval ... "data.deny" | jq '.result[0].expressions[0].value | length')
if [ "$DENY_COUNT" -eq 0 ]; then
  echo "❌ FAIL-FAST: Violation did not trigger deny"
  exit 1
fi
```

### Threshold 3: No Always-True/Always-False Rules
```bash
# Test both allow and deny paths to ensure decision logic exists
# If ALLOW always returns true → policy is broken
# If DENY always returns non-empty → policy is broken
```

**Prevention**: Canary tests enforce this by requiring specific allow/deny outcomes for different inputs.

---

## Rule Coverage Visibility (Optional - Phase 6)

OPA supports decision tracing with `--explain=notes`:

```bash
opa eval -d policy.rego -i input.json --explain=notes -f json "data.allow" > trace.json
```

**Trace Output** (sample):
```json
{
  "explanation": [
    {
      "op": "eval",
      "query_id": 1,
      "node": {
        "index": 0,
        "head": "allow",
        "body": [
          {"index": 0, "terms": [...]},
          {"index": 1, "terms": [...]}
        ]
      }
    }
  ]
}
```

**Use Cases**:
- **Rule Coverage**: Which rules were evaluated?
- **Decision Path**: Why was request allowed/denied?
- **Debugging**: Which condition failed?

**Integration**: Attach `--explain=notes` output to audit reports for transparency.

---

## Smoke Check Automation (CI Runner)

**File**: `.github/workflows/ci_truth_run.yml`

**Job Flow**:
```
verify-governance → run-opa-tests → opa-enforcement → run-pytests
                                     ↑
                          Canary Tests (Fail-Fast)
```

**Key Steps in `opa-enforcement` Job**:

1. **Syntax Check** (Implicit in `run-opa-tests` job)
2. **Canary Happy Path** → Must allow valid inputs (exit 1 on failure)
3. **Canary Violations** → Must deny invalid inputs (exit 1 on failure)
4. **Enforcement Summary** → Reports functional status

**Enforcement Guarantee**: If CI is green, policies are functional and enforcing.

---

## Troubleshooting Common Failures

### Issue 1: Canary Test Fails (Allow/Deny Mismatch)

**Symptom**:
```
❌ FAIL-FAST: Happy path did not allow valid DID operation
```

**Causes**:
- Policy rule changed unintentionally
- Input data structure mismatched
- `default allow := false` not overridden by rule

**Fix**:
1. Check policy rules against canary input
2. Run manual OPA eval to debug:
   ```bash
   opa eval -d policy.rego -i canary.json --explain=notes -f pretty "data.allow"
   ```
3. Update policy or canary input to align

---

### Issue 2: Pytest Fails but Canary Passes

**Symptom**:
```
FAILED test_03_core_deny_transaction_invalid_signature - AssertionError: Should mention signature issue
```

**Causes**:
- Deny message text changed
- Test assertion too strict (checking exact string match)

**Fix**:
1. Check actual deny message in policy
2. Update test assertion to match new message format
3. Ensure deny logic is still correct (message change is cosmetic)

---

### Issue 3: OPA Check Fails (Syntax Error)

**Symptom**:
```
rego_parse_error: unexpected token
```

**Causes**:
- Typo in Rego syntax
- Missing closing brace/bracket
- Invalid operator usage

**Fix**:
1. Run `opa check` locally to see exact error location
2. Use OPA Playground (https://play.openpolicyagent.org) to validate syntax
3. Check Rego documentation for correct operator usage

---

## Next Steps (Phase 6 Preview)

### WASM Compilation + Drift Control

**Goal**: Ensure Rego policies and WASM artifacts stay in sync.

**Implementation**:
1. **Build Scripts**: `23_compliance/policies/build_wasm_*.sh`
   ```bash
   opa build -t wasm -e ssid/03_core/v6_0 03_core_policy_stub_v6_0.rego
   mv policy.wasm 23_compliance/wasm/03_core_v6_0.wasm
   ```

2. **Hash Verification** (CI):
   ```bash
   CURRENT_HASH=$(sha256sum 23_compliance/wasm/03_core_v6_0.wasm | awk '{print $1}')
   EXPECTED_HASH=$(cat 23_compliance/wasm/03_core_v6_0.wasm.sha256)

   if [ "$CURRENT_HASH" != "$EXPECTED_HASH" ]; then
     echo "❌ WASM DRIFT DETECTED: Rebuild required"
     exit 1
   fi
   ```

3. **UI Integration**: `13_ui_layer/react/opa/opaEval.ts`
   ```typescript
   import { loadPolicy } from '@open-policy-agent/opa-wasm';
   const policy = await loadPolicy(fetch('/wasm/03_core_v6_0.wasm'));
   const result = policy.evaluate(input);
   ```

4. **Consistency Report**: `02_audit_logging/reports/wasm_consistency_v6_3.md`

**Acceptance Criteria**:
- ✅ 100% hash match (Rego ↔ WASM)
- ✅ At least 1 UI-side WASM eval of happy input
- ✅ CI breaks on hash mismatch or missing deny

---

**Last Updated**: 2025-10-13
**Version**: 6.2.0
**Mode**: SAFE-FIX + ROOT-24-LOCK STRICT + FUNCTIONAL ENFORCEMENT
