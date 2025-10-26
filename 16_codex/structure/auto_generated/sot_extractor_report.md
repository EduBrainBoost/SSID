# SSID SoT Universal Extractor Report

**Version:** 3.2.0
**Mode:** comprehensive
**Timestamp:** 2025-10-24T16:42:15.495245
**Total Rules:** 66099

## Extraction Statistics

- **Files Scanned:** 129
- **Rules Found:** 66099
- **Duplicates Removed:** 14513

### Rules by Source

| Source | Count |
|--------|-------|
| contract | 42367 |
| policy | 18608 |
| test | 348 |
| validator | 4776 |

### Rules by Priority (MoSCoW)

| Priority | Count |
|----------|-------|
| CAN | 114 |
| HAVE | 5926 |
| MUST | 21009 |
| SHOULD | 23933 |
| UNKNOWN | 15084 |
| have | 4 |
| must | 25 |
| should | 4 |

### Rules by Category

| Category | Count |
|----------|-------|
| AI Ethics | 2 |
| Audit & Compliance | 6 |
| Authentication | 18 |
| Bash Validation | 112 |
| Bias & Fairness | 3 |
| Blockchain Integration | 18 |
| Breaking Changes | 3 |
| CHART_STRUCTURE | 32 |
| COMPLIANCE | 109 |
| CONSOLIDATED_EXTENSIONS | 16 |
| CORE_PRINCIPLES | 32 |
| CRITICAL_POLICIES | 10 |
| Change Process | 3 |
| Compliance | 160 |
| Contracts | 3 |
| Cryptography | 24 |
| DAO Governance | 21 |
| DEPLOYMENT_CICD | 8 |
| Data Protection | 14 |
| Data Protection - PII | 20 |
| Deprecation | 3 |
| Directory Structure | 6 |
| ECONOMICS | 186 |
| ESG/Diversity | 12 |
| EXTENSIONS | 8 |
| Evidence & Audit | 6 |
| File Structure | 6 |
| GDPR Compliance | 39 |
| GDPR Retention | 15 |
| GENERAL | 141 |
| GOVERNANCE | 161 |
| General | 1696 |
| Governance | 80 |
| Governance - Proposals | 14 |
| Governance Roles | 6 |
| Guard/Enforcement | 20 |
| Hash-Only Data Policy | 6 |
| Identity & Authentication | 20 |
| Identity Standards | 12 |
| Infrastructure | 12 |
| Integration | 8 |
| MANIFEST_STRUCTURE | 68 |
| MATRIX_REGISTRY | 6 |
| METADATA | 15 |
| Market Coverage | 21 |
| Markets | 14 |
| Matrix Architecture | 29 |
| Metadata | 90 |
| Multi-Sector | 4 |
| Naming Convention | 6 |
| Non-Custodial | 6 |
| Privacy | 4 |
| Promotion Rules | 3 |
| Quarantine/Evidence | 84 |
| RFC Process | 3 |
| Registry | 4 |
| Regulatory | 44 |
| Review/Audit | 164 |
| Review/Documentation | 32 |
| STRUCTURE | 24 |
| Sanctions Compliance | 35 |
| Secrets Management | 6 |
| Security | 4 |
| Semantic Versioning | 3 |
| Standards | 4 |
| Structure | 34 |
| TECHNOLOGY_STANDARDS | 10 |
| Tokenomics | 45 |
| VERSIONING_GOVERNANCE | 14 |
| Versioning | 6 |
| compliance | 351 |
| crypto | 80 |
| entry_markers | 7 |
| eu_regulatorik | 15 |
| global_foundations | 5 |
| hierarchy_markers | 4 |
| performance | 19 |
| policy | 37202 |
| security | 83 |
| structure | 5404 |
| test | 691 |
| testing | 122 |
| unknown | 8709 |
| validator | 9552 |
| yaml_markers | 2 |

## Completeness Analysis

**Average Completeness Score:** 34.51%

| Completeness | Count |
|--------------|-------|
| 100% | 0 |
| 80-99% | 0 |
| 60-79% | 763 |
| 40-59% | 46441 |
| 0-39% | 18895 |

## Sample Rules (Top 10 by Completeness)

### PY_ACCU_919A: test_accuracies_above_one

- **Description:** Test with accuracy values > 1.0 (invalid but handled).
- **Priority:** MUST
- **Category:** test
- **Completeness:** 60%
- **Sources:** policy, contract, test
- **Hash:** `1b53431524404b95...`

### PY_ACCU_919A: 

- **Description:** PY_ACCU_919A: Test with accuracy values > 1.0 (invalid but handled).
- **Priority:** MUST
- **Category:** policy
- **Completeness:** 60%
- **Sources:** policy, contract, test
- **Hash:** `b73beb29d053fe3b...`

### PY_ACCU_919A: test_accuracies_above_one

- **Description:** Test with accuracy values > 1.0 (invalid but handled).
- **Priority:** MUST
- **Category:** test
- **Completeness:** 60%
- **Sources:** policy, contract, test
- **Hash:** `aa4b65f1dbd9b560...`

### PY_ALL_0BB8: test_all_valid_badges

- **Description:** Test with all valid badge signatures.
- **Priority:** MUST
- **Category:** test
- **Completeness:** 60%
- **Sources:** policy, contract, test
- **Hash:** `5523fba2d8a3a482...`

### PY_ALL_0BB8: 

- **Description:** PY_ALL_0BB8: Test with all valid badge signatures.
- **Priority:** MUST
- **Category:** policy
- **Completeness:** 60%
- **Sources:** policy, contract, test
- **Hash:** `b77c757ee8852800...`

### PY_ALL_0BB8: test_all_valid_badges

- **Description:** Test with all valid badge signatures.
- **Priority:** MUST
- **Category:** test
- **Completeness:** 60%
- **Sources:** policy, contract, test
- **Hash:** `76df3be8a3c048c9...`

### PY_ALL_3A13: test_all_duplicates

- **Description:** Test when all hashes are the same.
- **Priority:** MUST
- **Category:** test
- **Completeness:** 60%
- **Sources:** policy, contract, test
- **Hash:** `90df6747cca670a5...`

### PY_ALL_3A13: 

- **Description:** PY_ALL_3A13: Test when all hashes are the same.
- **Priority:** MUST
- **Category:** policy
- **Completeness:** 60%
- **Sources:** policy, contract, test
- **Hash:** `7d8c7af60e963458...`

### PY_ALL_3A13: test_all_duplicates

- **Description:** Test when all hashes are the same.
- **Priority:** MUST
- **Category:** test
- **Completeness:** 60%
- **Sources:** policy, contract, test
- **Hash:** `95a2d1a3a1d3b614...`

### PY_ANAL_059A: test_analyze_model_metrics_warning_test_val_mismatch

- **Description:** Test warning for test/validation mismatch
- **Priority:** MUST
- **Category:** test
- **Completeness:** 60%
- **Sources:** policy, contract, test
- **Hash:** `047c3160f55d9723...`
