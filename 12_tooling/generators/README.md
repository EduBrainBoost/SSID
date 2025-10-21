# SoT Validator Generator

## Purpose

**Deterministic, reproducible generation of ALL 5 technical manifestations from single YAML contract**

## SoT Principle Enforcement

```
1 Regulatory Rule = 1 Scientific Foundation + 5 Technical Manifestations
```

### The 5 Manifestations (Per Rule)

| # | Manifestation | Purpose | Location |
|---|---|---|---|
| 1 | **YAML Contract Entry** | Rule definition, scientific foundation, priority | `16_codex/contracts/sot/sot_contract.yaml` |
| 2 | **Python Validator Function** | Deterministic validation logic | `03_core/validators/sot/sot_validator_core_generated.py` |
| 3 | **Rego Policy Rule** | OPA enforcement, CI integration | `23_compliance/policies/sot/sot_policy_generated.rego` |
| 4 | **CLI Command** | Isolated terminal-based validation | `12_tooling/cli/sot_validator_generated.py` |
| 5 | **Pytest Test** | Reproducibility, audit trail | `11_test_simulation/tests_compliance/test_sot_validator_generated.py` |

## Why NOT Abstraction?

### ❌ What Would Be Wrong

```python
# DON'T DO THIS - Generic mega-validator
def validate_all(data, contract):
    for rule in contract['rules']:
        # ... dynamic validation
```

### Problems with Abstraction

1. **Lost Prioritization**: MoSCoW not evaluable per rule
2. **Lost Auditability**: No separate exit codes per rule
3. **Lost Testability**: No pytest per validator function
4. **Lost Contract Link**: Bypass field_path mapping
5. **Lost Scientific Proof**: No reference to regulatory foundation

**Result**: Code without proof structure = NOT SSID-compliant

### ✅ What IS Correct

```python
# DO THIS - Individual, traceable validator per rule
def validate_sot_001_version_format(data: Any) -> Tuple[str, bool, str]:
    """
    SOT-001: Version Format Validation

    Scientific Foundation:
        Standard: Semantic Versioning 2.0.0
        Reference: https://semver.org/

    Technical Manifestation:
        - Python: 03_core/validators/sot/sot_validator_core.py::validate_sot_001
        - Rego: 23_compliance/policies/sot/sot_policy.rego
        - CLI: python 12_tooling/cli/sot_validator.py --rule SOT-001
        - Test: test_sot_001
    """
    rule_id = "SOT-001"

    if not isinstance(data, str):
        return (rule_id, False, f"[{rule_id}] FAIL: Expected string")

    pattern = r'^\d+\.\d+\.\d+$'
    if not re.match(pattern, data):
        return (rule_id, False, f"[{rule_id}] FAIL: Invalid version format")

    return (rule_id, True, f"[{rule_id}] PASS: Valid version")
```

**Benefits**:
- ✅ Individual rule ID
- ✅ Separate exit code
- ✅ Scientific reference
- ✅ Audit trail
- ✅ MoSCoW priority
- ✅ Test per function

## Generation Architecture

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  16_codex/contracts/sot/sot_contract.yaml              │
│  (SINGLE SOURCE OF TRUTH)                              │
│                                                         │
│  - 44 regulatory rules                                 │
│  - Scientific foundations                              │
│  - MoSCoW priorities                                   │
│  - Enforcement specifications                          │
│                                                         │
└────────────────┬────────────────────────────────────────┘
                 │
                 │ INPUT
                 ▼
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  12_tooling/generators/sot_validator_generator.py      │
│  (DETERMINISTIC GENERATOR ENGINE)                      │
│                                                         │
│  - Parse YAML contract                                 │
│  - Generate Python validators                          │
│  - Generate Rego policies                              │
│  - Generate CLI commands                               │
│  - Generate pytest tests                               │
│  - Generate SHA-256 audit log                          │
│                                                         │
└────────────────┬────────────────────────────────────────┘
                 │
                 │ OUTPUT
                 ▼
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  5 TECHNICAL MANIFESTATIONS (Auto-generated)           │
│                                                         │
│  1. Python: 03_core/validators/sot/                    │
│     sot_validator_core_generated.py                    │
│     → 165 validator functions                          │
│                                                         │
│  2. Rego: 23_compliance/policies/sot/                  │
│     sot_policy_generated.rego                          │
│     → 165 OPA policy rules                             │
│                                                         │
│  3. CLI: 12_tooling/cli/                               │
│     sot_validator_generated.py                         │
│     → 44 rule commands                                 │
│                                                         │
│  4. Tests: 11_test_simulation/tests_compliance/        │
│     test_sot_validator_generated.py                    │
│     → 165 parametrized tests                           │
│                                                         │
│  5. Audit: 02_audit_logging/logs/                      │
│     sot_generation_audit.json                          │
│     → SHA-256 hashes for all artifacts                 │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## Usage

### Quick Start

```bash
# Generate all manifestations from contract
python 12_tooling/generators/sot_validator_generator.py

# With custom contract path
python 12_tooling/generators/sot_validator_generator.py \
  --contract path/to/contract.yaml \
  --output /path/to/output

# Expected output:
# [LOAD] ✅ Loaded 44 rules from contract
# [GEN] ✅ Generated 165 Python validator functions
# [GEN] ✅ Generated 165 Rego policy rules
# [GEN] ✅ Generated CLI command interface
# [GEN] ✅ Generated parametrized pytest test suite
# [WRITE] ✅ sot_validator_core_generated.py
# [WRITE] ✅ sot_policy_generated.rego
# [WRITE] ✅ sot_validator_generated.py
# [WRITE] ✅ test_sot_validator_generated.py
# [AUDIT] ✅ SHA audit log written
# ✅ FULL SOT MATERIALIZATION COMPLETE
```

### Adding New Rules

1. **Edit YAML Contract** (`16_codex/contracts/sot/sot_contract.yaml`):

```yaml
rules:
  - rule_id: "SOT-NEW-001"
    priority: "must"  # MoSCoW: must/should/have
    rule_name: "New Regulatory Requirement"
    line_reference: 123
    scientific_foundation:
      standard: "Regulatory Framework XYZ"
      reference: "https://example.org/standard"
      principle: "Core compliance principle"
    technical_manifestation:
      validator: "03_core/validators/sot/sot_validator_core.py::validate_sot_new_001"
      opa_policy: "23_compliance/policies/sot/sot_policy.rego"
      cli_command: "python 12_tooling/cli/sot_validator.py --rule SOT-NEW-001"
      test_path: "11_test_simulation/tests_compliance/test_sot_validator.py"
    enforcement:
      exact_value: "compliant_value"  # or pattern, allowed_values, type, min_length
      examples_valid: ["compliant_value"]
      examples_invalid: ["non_compliant_value"]
    category: "regulatory_category"
    severity: "CRITICAL"  # CRITICAL/HIGH/MEDIUM/LOW
```

2. **Re-run Generator**:

```bash
python 12_tooling/generators/sot_validator_generator.py
```

3. **Verify Generated Files**:

```bash
# Check Python validator
grep -A 20 "def validate_sot_new_001" \
  03_core/validators/sot/sot_validator_core_generated.py

# Check Rego policy
grep -A 5 "SOT-NEW-001" \
  23_compliance/policies/sot/sot_policy_generated.rego

# Run tests
pytest 11_test_simulation/tests_compliance/test_sot_validator_generated.py::test_sot_validator_exists[SOT-NEW-001]
```

4. **Verify SHA Audit**:

```bash
cat 02_audit_logging/logs/sot_generation_audit.json
```

## Enforcement Types

The generator supports multiple enforcement patterns:

### 1. Exact Value

```yaml
enforcement:
  exact_value: "expected_value"
  examples_valid: ["expected_value"]
  examples_invalid: ["wrong_value"]
```

### 2. Regex Pattern

```yaml
enforcement:
  pattern: "^\\d{4}-\\d{2}-\\d{2}$"
  examples_valid: ["2025-10-17"]
  examples_invalid: ["17-10-2025", "2025/10/17"]
```

### 3. Allowed Values

```yaml
enforcement:
  allowed_values: ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
  examples_valid: ["CRITICAL"]
  examples_invalid: ["UNKNOWN"]
```

### 4. Type Checking

```yaml
enforcement:
  type: "boolean"  # boolean, string, number
  examples_valid: [true, false]
  examples_invalid: ["true", 1, null]
```

### 5. Minimum Length

```yaml
enforcement:
  min_length: 10
  examples_valid: ["Long enough string"]
  examples_invalid: ["Short"]
```

## MoSCoW Priority Model

| Priority | Enforcement | CI Behavior | Exit Code |
|---|---|---|---|
| **MUST** | Hard fail | Blocks CI | 24 on failure |
| **SHOULD** | Warning | Logged, no block | 0 (warning logged) |
| **HAVE** | Informational | Documented only | 0 (info logged) |

## SHA-256 Audit Trail

Every generation creates SHA-256 hashes:

```json
{
  "generation_metadata": {
    "timestamp": "2025-10-17T...",
    "generator_version": "1.0.0",
    "contract_source": "16_codex/contracts/sot/sot_contract.yaml",
    "total_rules": 44,
    "manifestations_count": 5
  },
  "sha256_registry": {
    "python_validators": "a7f3e2d1c4b5...",
    "rego_policy": "b8e4f3d2c5a6...",
    "cli_command": "c9f5e4d3b6a7...",
    "pytest_tests": "d0f6e5d4b7a8..."
  },
  "verification": {
    "method": "SHA-256",
    "algorithm": "hashlib.sha256",
    "encoding": "utf-8"
  }
}
```

## Verification

### Verify Generated Code Integrity

```bash
# Calculate SHA-256 of generated Python file
sha256sum 03_core/validators/sot/sot_validator_core_generated.py

# Compare with audit log
cat 02_audit_logging/logs/sot_generation_audit.json | \
  jq '.sha256_registry.python_validators'
```

### Run All Tests

```bash
# Test all generated validators
pytest 11_test_simulation/tests_compliance/test_sot_validator_generated.py -v

# Test specific rule
pytest 11_test_simulation/tests_compliance/test_sot_validator_generated.py::test_sot_validator_exists[SOT-001] -v
```

### Validate with OPA

```bash
# Test Rego policy
opa test 23_compliance/policies/sot/sot_policy_generated.rego
```

## Benefits

### Deterministic
- Same input (YAML) → Same output (code)
- Reproducible across machines, OS, Python versions
- No manual coding errors

### Auditable
- SHA-256 hashes for all artifacts
- Generation timestamp
- Full provenance trail

### Maintainable
- Edit 1 YAML → Regenerate all 5 manifestations
- No code duplication
- Single source of truth

### Testable
- 165 parametrized tests auto-generated
- Each rule independently verifiable
- CI-ready

### Compliant
- MoSCoW priority enforcement
- Scientific foundation references
- Regulatory traceability

## Badge: FULL SOT MATERIALIZATION

Once all 44 rules have been successfully generated and validated:

```
✅ FULL SOT MATERIALIZATION ACHIEVED

- 44 Regulatory Rules
- 220 Validator Functions (165 rule validators + 55 support functions)
- 5 Technical Manifestations
- 100% Contract Coverage
- SHA-256 Audited
- Deterministic Generation
- Reproducible Build
```

## Troubleshooting

### Issue: Generator fails to parse YAML

```bash
# Validate YAML syntax
yamllint 16_codex/contracts/sot/sot_contract.yaml

# Check for missing required fields
python -c "import yaml; yaml.safe_load(open('16_codex/contracts/sot/sot_contract.yaml'))"
```

### Issue: Generated tests fail

```bash
# Check test data in contract
cat 16_codex/contracts/sot/sot_contract.yaml | grep -A 5 "examples_valid"

# Run single test with verbose output
pytest -vv test_sot_validator_generated.py::test_sot_validator_valid_data[SOT-001-2.0.0]
```

### Issue: SHA mismatch

```bash
# Regenerate with clean state
rm -f 03_core/validators/sot/sot_validator_core_generated.py
python 12_tooling/generators/sot_validator_generator.py

# Verify new SHA
cat 02_audit_logging/logs/sot_generation_audit.json
```

## Contributing

When adding new regulatory rules:

1. Research scientific foundation (standard, reference, principle)
2. Define enforcement specification (exact_value, pattern, etc.)
3. Add test examples (valid and invalid)
4. Assign MoSCoW priority (must/should/have)
5. Document in YAML contract
6. Run generator
7. Verify all 5 manifestations
8. Commit with SHA audit log

## License

Part of SSID Framework - Internal Compliance System
