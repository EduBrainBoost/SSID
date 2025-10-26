# Rule Counting Methodology - SSID Validator Framework

**Date:** 2025-10-21
**Version:** 1.0
**Status:** DRAFT - Pending Final Verification

---

## Executive Summary

This document defines the correct methodology for counting enforceable rules in the SSID framework, clarifying the distinction between:
1. **Documentation elements** (fields, examples, metadata)
2. **Enforceable structural rules** (testable requirements)
3. **Implemented validators** (Python functions)

---

## The Counting Confusion

### Initial Miscounting: 3,889 "Rules"

**Problem:** Counted every YAML field and documentation element as a rule.

**Example of WRONG counting:**
```yaml
version: "1.0"          # Counted as 1 rule ❌
date: "2025-10-21"      # Counted as 1 rule ❌
deprecated: false       # Counted as 1 rule ❌
```

**Why wrong:** These are metadata fields, not enforceable requirements.

---

## Correct Rule Definition

### What IS an Enforceable Rule?

An enforceable rule MUST be:
1. **Deterministic** - Same input always produces same output
2. **Testable** - Can be validated programmatically
3. **Structural** - Defines a requirement about repository structure/content
4. **Documented** - Has clear success/failure criteria

### What IS NOT a Rule?

- Metadata fields (version, date, author)
- Examples and documentation
- Comments and explanations
- Historical data
- Formatting preferences

---

## Three Categories of Countable Items

### Category 1: Implemented Validators (Python Functions)

**Current Count: 221 validators**

**Definition:** Actual Python functions that perform validation.

**Breakdown:**
- `sot_validator_core.py`: 156 validators
- `critical_validators_v2.py`: 27 validators
- `important_validators_v2.py`: 38 validators

**How to count:**
```python
def count_validators_in_class(cls):
    methods = [m for m in dir(cls)
               if m.startswith('validate_')
               and callable(getattr(cls, m))]
    return len(methods)
```

**Example validators:**
- `validate_ar001()` - Root structure validation
- `validate_cy001()` - Chart.yaml must exist
- `validate_gdpr_001_hash_rotation()` - GDPR hash rotation enforcement

---

### Category 2: Enforceable YAML Constraints

**Current Count: 1,454 constraints**

**Definition:** Specific requirements in YAML configuration that can be validated.

**What counts:**
- Required fields: `chart.yaml MUST have version:`
- Required values: `version MUST be semver format`
- Required files: `Each shard MUST have policies/ directory`
- Forbidden items: `No .ipynb files allowed in root`
- Naming conventions: `Shard names MUST match Shard_NN_*`

**What does NOT count:**
- Metadata: `version: "1.0"` in the YAML config itself
- Examples: `example: "value"`
- Comments: `# This is a comment`

**Example from SOT:**
```yaml
required_folders:
  - chart.yaml          # 1 enforceable rule: "chart.yaml MUST exist"
  - policies/           # 1 enforceable rule: "policies/ MUST exist"
  - implementations/    # 1 enforceable rule: "implementations/ MUST exist"
```
**Count:** 3 rules (not 6, because the list itself isn't a rule)

---

### Category 3: SOT Structural Requirements

**Pending Count: TBD**

**Definition:** High-level architectural requirements from master definition files.

**Examples:**
1. "Repository MUST have exactly 24 root folders" (1 rule)
2. "Each root MAY have shards/ subdirectory" (1 rule)
3. "Each shard MUST have chart.yaml" (1 rule, applies to N shards)
4. "chart.yaml MUST contain version field" (1 rule, applies to N charts)

**Critical Question:**
- Do we count "chart.yaml MUST exist" as 1 rule OR 384 rules (once per shard)?

**Answer:**
- **1 rule with N instances** - The rule is defined once, validated N times
- Similar to: "All files MUST be UTF-8" = 1 rule, not 10,000 rules

---

## Current Validator Coverage

### Implemented vs. Theoretical

**Validators Implemented:** 221

**Coverage by Category:**

| Category | Rules Defined | Validators Implemented | Coverage |
|----------|---------------|------------------------|----------|
| Architecture | 13 | 13 | 100% |
| Chart YAML | 46 | 46 | 100% |
| Governance | 31 | 31 | 100% |
| Manifest YAML | 45 | 45 | 100% |
| Principles | 51 | 51 | 100% |
| Naming | 10 | 10 | 100% |
| Structure | 7 | 7 | 100% |
| Standards | 8 | 8 | 100% |
| Policies | 32 | 23 | 71.9% |
| **TOTAL** | **243** | **234** | **96.3%** |

**Note:** This is coverage of DEFINED rules in the validator modules, not total SOT requirements.

---

## Proposed Final Counting Method

### Step 1: Extract Structural Requirements from SOT

Count unique structural requirements from master definition files:

```python
def count_structural_rules(sot_files):
    rules = set()

    for file in sot_files:
        # Extract MUST/SHOULD/MAY statements
        # Extract required_* lists
        # Extract forbidden_* lists
        # Extract naming patterns
        # Extract file/folder requirements

    return len(rules)
```

### Step 2: Map to Implemented Validators

For each structural rule, identify:
1. **Rule ID** (e.g., AR-001)
2. **Validator Function** (e.g., validate_ar001)
3. **Rego Policy** (e.g., deny[msg] { ... })
4. **Test Coverage** (e.g., test_ar001_*)

### Step 3: Calculate Coverage

```
Coverage = (Implemented Validators / Total Structural Rules) * 100%
```

---

## Preliminary Estimates

### Conservative Estimate

**Structural Requirements from SOT:**
- Architecture rules: ~15
- Chart/Manifest rules: ~100
- Shard structure rules: ~30
- Naming conventions: ~15
- Policy requirements: ~40
- Security requirements: ~25
- Standards compliance: ~15
- GDPR/Regulatory: ~10

**TOTAL ESTIMATE: ~250 unique structural rules**

**Current Implementation: 221 validators**
**Estimated Coverage: ~88%**

---

## Next Steps

### 1. Systematic SOT Analysis

Run comprehensive analysis of all 4 master definition files:
- SSID_structure_level3_part1_MAX.md
- SSID_structure_level3_part2_MAX.md
- SSID_structure_level3_part3_MAX.md
- ssid_master_definition_corrected_v1.1.1.md

### 2. Extract MUST/SHOULD/MAY Statements

Parse for:
- "MUST exist"
- "MUST NOT contain"
- "MUST match pattern"
- "SHOULD follow"
- "MAY include"

### 3. Deduplicate Rules

Identify when multiple statements define the same rule:
```
"chart.yaml MUST exist" (stated 3 times)
  = 1 rule, not 3
```

### 4. Create Rule Registry

**Format:**
```yaml
rule_id: STRUCT-001
category: structure
priority: must
statement: "Each shard MUST have chart.yaml"
validator: validate_cy001
rego_policy: deny_missing_chart_yaml
test: test_cy001_missing_chart
instances: 384  # How many times this is checked
```

---

## Open Questions

### Question 1: Instance Counting

**Scenario:** "Every chart.yaml MUST have version field"

**Options:**
A) 1 rule (the requirement itself)
B) 384 rules (one per shard)
C) 1 rule with 384 validation instances

**Recommendation:** Option C - 1 rule, 384 instances

**Rationale:** The rule is defined once. We validate it N times.

### Question 2: Composite Rules

**Scenario:** "chart.yaml MUST have version AND name AND description"

**Options:**
A) 1 rule (chart.yaml completeness)
B) 3 rules (version required, name required, description required)

**Recommendation:** Option B - 3 atomic rules

**Rationale:** Each can fail independently and requires separate validation.

### Question 3: YAML Config vs. SOT Definition

**Scenario:** SOT defines 1,454 YAML constraints

**Question:** Are all 1,454 unique rules?

**Answer:** NO - Many are duplicates/instances of the same rule

**Example:**
```yaml
# This appears in 24 roots
required_files:
  - chart.yaml
```
**Count:** 1 rule ("root must have chart.yaml"), not 24

---

## Conclusion

**Correct Approach:**
1. Count unique structural requirements from SOT
2. Map to implemented validators (1:1 or 1:N)
3. Track coverage percentage
4. DO NOT count metadata, examples, or duplicate statements

**Preliminary Answer:**
- **~250 unique enforceable rules** (conservative estimate)
- **221 implemented validators** (current)
- **~88% coverage** (estimated)

**Final Count:** Pending systematic SOT analysis

---

**Document Status:** DRAFT
**Next Review:** After SOT validation completes
**Pending:** Rule registry creation

---

*Generated by Claude Code - Validator Integration Phase 6*
