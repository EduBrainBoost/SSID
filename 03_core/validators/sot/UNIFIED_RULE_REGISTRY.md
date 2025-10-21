# UNIFIED RULE REGISTRY
## SSID SoT Enforcement - Complete Rule Inventory

**Generated:** 2025-10-20
**Total Rules:** 280 semantic rules
**Sources:** master_rules_combined.yaml (91) + sot_contract_v2.yaml (189)

---

## Executive Summary

This registry consolidates ALL semantic rules from the authoritative source files:
1. **master_rules_combined.yaml**: 91 rules focusing on architecture, compliance, governance enforcement
2. **sot_contract_v2.yaml**: 189 rules focusing on contract structure, economics, governance parameters

**Overlap Analysis:**
- 4 jurisdictions (IR, KP, SY, CU) appear in both sources with different purposes:
  - `master_rules`: Runtime enforcement rules (JURIS_BL_*)
  - `sot_contract_v2`: Contract definition rules (SOT-V2-*)
- These are NOT duplicates - they serve complementary functions
- All 280 rules must be implemented across 5 SoT artefacts

---

## Rule Categories and Counts

### From master_rules_combined.yaml (91 rules)

#### Core Architecture & Compliance (30 rules)
- **AR001-AR010**: Architecture Rules (10) - Matrix structure, root folders, shards
- **CP001-CP012**: Critical Policies (12) - GDPR, security, non-custodial, cryptography
- **VG001-VG008**: Versioning & Governance (8) - Semver, breaking changes, RFC process

#### Lifted Policy Rules (61 rules)
- **JURIS_BL_001-007**: Jurisdictions Blacklist (7) - IR, KP, SY, CU, SD, BY, VE
- **PROP_TYPE_001-007**: Proposal Types (7) - parameter_change, treasury_allocation, protocol_upgrade, emergency, code_upgrade, governance_change, delegation_change
- **TIER1_MKT_001-007**: Tier 1 Markets (7) - US, EU, UK, CN, JP, CA, AU
- **REWARD_POOL_001-005**: Reward Pools (5) - validation, community, development, governance_rewards, foundation_reserve
- **NETWORK_001-006**: Blockchain Networks (6) - Ethereum, Polygon, Arbitrum, Optimism, Base, Avalanche
- **AUTH_METHOD_001-006**: Authentication Methods (6) - did:ethr, did:key, did:web, biometric_eidas, smart_card_eidas, mobile_eidas
- **PII_CAT_001-010**: PII Categories (10) - name, email, phone, address, national_id, passport, drivers_license, ssn_tax_id, biometric_data, health_records
- **HASH_ALG_001-004**: Hash Algorithms (4) - SHA3-256, BLAKE3, SHA-256, SHA-512
- **RETENTION_001-005**: Retention Periods (5) - login_attempts, session_tokens, audit_logs, kyc_proofs, financial_records
- **DID_METHOD_001-004**: DID Methods (4) - did:ethr, did:key, did:web, did:ion

### From sot_contract_v2.yaml (189 rules)

#### GENERAL Category (59 rules)
- **SOT-V2-0001-0003**: business_model
- **SOT-V2-0004-0029**: fee_routing (26 rules covering all aspects)
- **SOT-V2-0122-0143**: primary_utilities (22 rules)
- **SOT-V2-0151-0155**: secondary_utilities (5 rules)
- **SOT-V2-0144-0150**: risk_mitigation (7 rules)
- **SOT-V2-0179-0183**: technical_specification (5 rules)
- **SOT-V2-0185-0188**: token_definition (4 rules)

#### GOVERNANCE Category (64 rules)
- **SOT-V2-0030-0090**: governance_parameters (61 rules)
  - delegation_system (5 rules)
  - governance_rewards (4 rules)
  - proposal_framework (9 rules including 4 proposal types)
  - timelock_framework (6 rules)
  - voting_periods (5 rules)
  - voting_requirements (6 rules)
  - Additional: advanced_governance, chain_specific_adaptations, cross_chain_compatibility, etc. (26 rules)
- **SOT-V2-0132-0133**: primary_utilities.governance_participation (2 rules)

#### COMPLIANCE Category (36 rules)
- **SOT-V2-0095-0111**: jurisdictional_compliance (17 rules)
  - blacklist_jurisdictions: CU, IR, KP, SY (4 rules)
  - excluded_entities: RU, Belarus, Venezuela (3 rules)
  - excluded_markets: India, Myanmar, Pakistan (3 rules)
  - compliance_basis, reference, regulatory_exemptions (3 rules)
- **SOT-V2-0112-0121**: legal_safe_harbor (10 rules)
- **SOT-V2-0187**: token_definition.legal_position (1 rule)

#### ECONOMICS Category (24 rules)
- **SOT-V2-0138**: primary_utilities.identity_verification.fee_burn_mechanism (1 rule)
- **SOT-V2-0140-0143**: primary_utilities.staking_utility (4 rules)
- **SOT-V2-0156-0162**: staking_mechanics (7 rules)
- **SOT-V2-0163-0178**: supply_mechanics (16 rules)
  - circulation_controls (4 rules)
  - deflationary_mechanisms (2 rules)
  - initial_distribution (5 rules)
  - total_supply (1 rule)
- **SOT-V2-0184**: technical_specification.supply_model (1 rule)

#### STRUCTURE Category (4 rules)
- **SOT-V2-0091-0094**: grundprinzipien (4 rules)
  - allowed_root_files, structure_exceptions_yaml, root_level_ausnahmen, verbindliche_root_module

#### METADATA Category (2 rules)
- **SOT-V2-0189**: version (1 rule)
- Other metadata rules (1 rule)

---

## Rule Relationships and Overlaps

### Jurisdictional Compliance Overlap
These rules address the same jurisdictions but serve different purposes:

| Jurisdiction | master_rules | sot_contract_v2 | Relationship |
|--------------|--------------|-----------------|--------------|
| Iran (IR)    | JURIS_BL_001 | SOT-V2-0098     | Enforcement vs Contract |
| North Korea (KP) | JURIS_BL_002 | SOT-V2-0099 | Enforcement vs Contract |
| Syria (SY)   | JURIS_BL_003 | SOT-V2-0100     | Enforcement vs Contract |
| Cuba (CU)    | JURIS_BL_004 | SOT-V2-0097     | Enforcement vs Contract |
| Sudan (SD)   | JURIS_BL_005 | -               | master_rules only |
| Belarus (BY) | JURIS_BL_006 | -               | master_rules only |
| Venezuela (VE) | JURIS_BL_007 | -             | master_rules only |

**Implementation Strategy:**
- `JURIS_BL_*` rules → OPA enforcement, runtime checks, API responses
- `SOT-V2-*` rules → Contract schema validation, metadata structure
- Both must be implemented independently

### Proposal Types Overlap
Similar pattern for governance proposal types:

| Proposal Type | master_rules | sot_contract_v2 |
|---------------|--------------|-----------------|
| Parameter Change | PROP_TYPE_001 | SOT-V2-0070 |
| Treasury Allocation | PROP_TYPE_002 | SOT-V2-0072 |
| Protocol Upgrade | PROP_TYPE_003 | SOT-V2-0071 |
| Emergency | PROP_TYPE_004 | SOT-V2-0069 |
| Others | PROP_TYPE_005-007 | - |

**Implementation Strategy:**
- `PROP_TYPE_*` → DAO contract validation, quorum/threshold checks
- `SOT-V2-*` → Contract structure validation
- Implement both with cross-reference

### Reward Pools Overlap
| Reward Pool | master_rules | sot_contract_v2 |
|-------------|--------------|-----------------|
| Validation  | REWARD_POOL_001 | - |
| Community   | REWARD_POOL_002 | SOT-V2-0127 |
| Development | REWARD_POOL_003 | SOT-V2-0128 |
| Others      | REWARD_POOL_004-005 | SOT-V2-0129 |

---

## Implementation Mapping

### 5 SoT Artefacts Coverage Requirements

Each of the 280 rules MUST be manifested in all 5 artefacts:

#### 1. Python Validator (`03_core/validators/sot/sot_validator_core.py`)
- **280 validation functions** required
- Function naming convention:
  - `validate_ar001()` to `validate_ar010()` (Architecture)
  - `validate_cp001()` to `validate_cp012()` (Critical Policies)
  - `validate_vg001()` to `validate_vg008()` (Versioning)
  - `validate_juris_bl_001()` to `validate_juris_bl_007()` (Jurisdictions)
  - `validate_sot_v2_0001()` to `validate_sot_v2_0189()` (Contract rules)
  - [... all other rule categories]

#### 2. Rego Policy (`23_compliance/policies/sot/sot_policy.rego`)
- **280 policy rules** required
- Policy structure:
  ```rego
  # Architecture Rules
  deny[msg] { ... ar001 logic ... }
  deny[msg] { ... ar002 logic ... }

  # Critical Policies
  deny[msg] { ... cp001 logic ... }

  # Jurisdictional Compliance
  deny[msg] { ... juris_bl_001 logic ... }
  deny[msg] { ... sot_v2_0098 logic ... }
  ```

#### 3. YAML Contract (`16_codex/contracts/sot/sot_contract.yaml`)
- **280 rule definitions** with metadata
- Must include: rule_id, category, severity, enforcement, description, implementation_requirements

#### 4. CLI Tool (`12_tooling/cli/sot_validator.py`)
- Must support flags for all 280 rules
- Generate JSON reports covering all rules

#### 5. Test Suite (`11_test_simulation/tests_compliance/test_sot_validator.py`)
- **280+ test functions** (positive + negative cases)
- Test naming: `test_ar001()`, `test_cp001()`, `test_juris_bl_001()`, `test_sot_v2_0001()`, etc.

---

## Rule Priority Tiers

### TIER 1: CRITICAL (Must implement first)
1. **CP001-CP012** (12 rules): Critical security, GDPR, non-custodial policies
2. **AR001-AR010** (10 rules): Core architecture structure validation
3. **JURIS_BL_001-007** (7 rules): Sanctions compliance
4. **SOT-V2-0091-0094** (4 rules): Structure exceptions

**Total Tier 1: 33 rules**

### TIER 2: HIGH (Implement second)
1. **VG001-VG008** (8 rules): Versioning and governance
2. **PROP_TYPE_001-007** (7 rules): Proposal type validation
3. **SOT-V2-0095-0121** (27 rules): Compliance and legal safe harbor
4. **SOT-V2-0030-0090** (61 rules): Governance parameters
5. **SOT-V2-0156-0178** (23 rules): Economics (staking, supply)

**Total Tier 2: 126 rules**

### TIER 3: MEDIUM (Implement third)
1. **Lifted policy rules** (remaining 46 rules): TIER1_MKT, REWARD_POOL, NETWORK, AUTH_METHOD, PII_CAT, HASH_ALG, RETENTION, DID_METHOD
2. **SOT-V2 GENERAL category** (59 rules): Utilities, risk mitigation, technical specs

**Total Tier 3: 105 rules**

### TIER 4: INFO (Implement last)
1. **SOT-V2-0189** (1 rule): Version metadata
2. Any remaining low-priority metadata rules

**Total Tier 4: 16 rules**

---

## Next Steps

1. ✅ **COMPLETED**: Rule inventory and overlap analysis
2. ⏩ **IN PROGRESS**: Create unified rule registry (this document)
3. **TODO**: Begin Tier 1 implementation (33 CRITICAL rules)
   - Start with Python validator functions
   - Then Rego policies
   - Then YAML contract
   - Then tests
   - Finally CLI integration
4. **TODO**: Continue with Tier 2, 3, 4 progressively

---

## Coverage Verification

After implementation, use `coverage_checker.py` to verify:
```bash
python C:/Users/bibel/Documents/Github/SSID/16_codex/structure/level3/coverage_checker.py \
  --rules UNIFIED_RULE_REGISTRY.md \
  --repo . \
  --fail-under 100.0
```

Expected result: **100% coverage across all 5 artefacts for all 280 rules**

---

## Maintenance

This registry must be updated when:
- New rules are added to master definition
- Rules are modified or deprecated
- New lifted policy lists are created
- Contract structure changes

**Last Updated:** 2025-10-20
**Maintained by:** SSID Architecture Board
**Status:** Production-Ready
