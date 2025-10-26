# Part1 Semantische Regeln - Manuelle Extraktion
**Quelle:** SSID_structure_level3_part1_MAX.md
**Zeilen:** 1-1257
**Datum:** 2025-10-21
**Methode:** Manuelle line-by-line Analyse

---

## Struktur-Regeln (STRUCTURE)

### STRUCT-P1-001: Genau 24 Root-Ordner bindend
- **Zeile:** 20
- **Text:** "Die obige v4.1-Liste ist bindend"
- **Typ:** MUST
- **Validierung:** `count(root_directories) == 24`
- **Severity:** CRITICAL
- **Evidence:** Directory listing of repository root

### STRUCT-P1-002: Root-Level Exceptions File existiert
- **Zeile:** 22
- **Text:** "Siehe kanonische Definition in `23_compliance/exceptions/root_level_exceptions.yaml`"
- **Typ:** MUST
- **Validierung:** `file_exists("23_compliance/exceptions/root_level_exceptions.yaml")`
- **Severity:** HIGH
- **Evidence:** File path validation

### STRUCT-P1-003: Erlaubte Root-Ausnahmen
- **Zeile:** 24
- **Text:** "Ausnahmen: .git/, .github/, LICENSE, README.md"
- **Typ:** MUST
- **Validierung:** `allowed_root_files = {".git/", ".github/", "LICENSE", "README.md"}`
- **Severity:** MEDIUM
- **Evidence:** Root directory whitelist

### STRUCT-P1-004: Structure Exceptions einzige gültige Datei
- **Zeile:** 25
- **Text:** "`23_compliance/exceptions/structure_exceptions.yaml` ist die einzige gültige Struktur-Exception"
- **Typ:** MUST
- **Validierung:** `unique_file("23_compliance/exceptions/structure_exceptions.yaml")` AND NOT `exists(root + "structure_exceptions.yaml")`
- **Severity:** CRITICAL
- **Evidence:** File uniqueness check

---

## YAML-Feld-Regeln - Token Architecture (YAML_TOKEN_ARCH)

### YAML-P1-001: Token Framework Version
- **Zeile:** 32
- **YAML-Pfad:** `20_foundation/tokenomics/ssid_token_framework.yaml`
- **Feld:** `version`
- **Erwarteter Wert:** "1.0"
- **Typ:** MUST
- **Validierung:** `yaml_field_equals("20_foundation/tokenomics/ssid_token_framework.yaml", "version", "1.0")`
- **Severity:** HIGH

### YAML-P1-002: Token Framework Datum
- **Zeile:** 33
- **YAML-Pfad:** `20_foundation/tokenomics/ssid_token_framework.yaml`
- **Feld:** `date`
- **Erwarteter Wert:** "2025-09-15"
- **Typ:** MUST
- **Validierung:** `yaml_field_equals("...", "date", "2025-09-15")`
- **Severity:** LOW

### YAML-P1-003: Token Framework Deprecated Flag
- **Zeile:** 34
- **YAML-Pfad:** `20_foundation/tokenomics/ssid_token_framework.yaml`
- **Feld:** `deprecated`
- **Erwarteter Wert:** `false`
- **Typ:** MUST
- **Validierung:** `yaml_field_equals("...", "deprecated", false)`
- **Severity:** CRITICAL

### YAML-P1-004: Token Framework Classification
- **Zeile:** 35
- **YAML-Pfad:** `20_foundation/tokenomics/ssid_token_framework.yaml`
- **Feld:** `classification`
- **Erwarteter Wert:** "PUBLIC - Token Framework Standards"
- **Typ:** MUST
- **Validierung:** `yaml_field_equals("...", "classification", "PUBLIC - Token Framework Standards")`
- **Severity:** MEDIUM

### YAML-P1-005: Token Purpose (3-fach)
- **Zeile:** 38
- **YAML-Pfad:** `20_foundation/tokenomics/ssid_token_framework.yaml`
- **Feld:** `token_definition.purpose`
- **Erwarteter Wert:** `["utility", "governance", "reward"]`
- **Typ:** MUST
- **Validierung:** `yaml_list_equals("...", "token_definition.purpose", ["utility", "governance", "reward"])`
- **Severity:** CRITICAL

### YAML-P1-006: Token Explicit Exclusions (5 Elemente)
- **Zeile:** 39
- **YAML-Pfad:** `20_foundation/tokenomics/ssid_token_framework.yaml`
- **Feld:** `token_definition.explicit_exclusions`
- **Erwarteter Wert:** `["investment", "security", "e_money", "yield_bearing", "redemption_rights"]`
- **Typ:** MUST
- **Validierung:** `yaml_list_equals("...", "token_definition.explicit_exclusions", [...])`
- **Severity:** CRITICAL

### YAML-P1-007: Legal Position
- **Zeile:** 40
- **YAML-Pfad:** `20_foundation/tokenomics/ssid_token_framework.yaml`
- **Feld:** `token_definition.legal_position`
- **Erwarteter Wert:** "Pure utility token for identity verification services"
- **Typ:** MUST
- **Validierung:** `yaml_field_equals("...", "token_definition.legal_position", "Pure utility token...")`
- **Severity:** CRITICAL

### YAML-P1-008: Blockchain Platform
- **Zeile:** 43
- **YAML-Pfad:** `20_foundation/tokenomics/ssid_token_framework.yaml`
- **Feld:** `technical_specification.blockchain`
- **Erwarteter Wert:** "Polygon (EVM Compatible)"
- **Typ:** MUST
- **Validierung:** `yaml_field_equals("...", "technical_specification.blockchain", "Polygon (EVM Compatible)")`
- **Severity:** HIGH

### YAML-P1-009: Token Standard
- **Zeile:** 44
- **YAML-Pfad:** `20_foundation/tokenomics/ssid_token_framework.yaml`
- **Feld:** `technical_specification.standard`
- **Erwarteter Wert:** "ERC-20 Compatible"
- **Typ:** MUST
- **Validierung:** `yaml_field_equals("...", "technical_specification.standard", "ERC-20 Compatible")`
- **Severity:** HIGH

### YAML-P1-010: Supply Model
- **Zeile:** 45
- **YAML-Pfad:** `20_foundation/tokenomics/ssid_token_framework.yaml`
- **Feld:** `technical_specification.supply_model`
- **Erwarteter Wert:** "Fixed cap with deflationary mechanisms"
- **Typ:** MUST
- **Validierung:** `yaml_field_equals("...", "technical_specification.supply_model", "Fixed cap...")`
- **Severity:** HIGH

### YAML-P1-011: Custody Model
- **Zeile:** 46
- **YAML-Pfad:** `20_foundation/tokenomics/ssid_token_framework.yaml`
- **Feld:** `technical_specification.custody_model`
- **Erwarteter Wert:** "Non-custodial by design"
- **Typ:** MUST
- **Validierung:** `yaml_field_equals("...", "technical_specification.custody_model", "Non-custodial by design")`
- **Severity:** CRITICAL

### YAML-P1-012: Smart Contract Automation
- **Zeile:** 47
- **YAML-Pfad:** `20_foundation/tokenomics/ssid_token_framework.yaml`
- **Feld:** `technical_specification.smart_contract_automation`
- **Erwarteter Wert:** "Full autonomous distribution"
- **Typ:** MUST
- **Validierung:** `yaml_field_equals("...", "technical_specification.smart_contract_automation", "Full autonomous distribution")`
- **Severity:** HIGH

### YAML-P1-013: Fee Structure Scope
- **Zeile:** 50
- **YAML-Pfad:** `20_foundation/tokenomics/ssid_token_framework.yaml`
- **Feld:** `fee_structure.scope`
- **Erwarteter Wert:** "identity_verification_payments_only"
- **Typ:** MUST
- **Validierung:** `yaml_field_equals("...", "fee_structure.scope", "identity_verification_payments_only")`
- **Severity:** CRITICAL

### YAML-P1-014: Total Fee 3%
- **Zeile:** 51
- **YAML-Pfad:** `20_foundation/tokenomics/ssid_token_framework.yaml`
- **Feld:** `fee_structure.total_fee`
- **Erwarteter Wert:** "3% of identity verification transactions"
- **Typ:** MUST
- **Validierung:** `yaml_field_equals("...", "fee_structure.total_fee", "3%...")`
- **Severity:** CRITICAL

### YAML-P1-015: Fee Allocation Split
- **Zeile:** 52
- **YAML-Pfad:** `20_foundation/tokenomics/ssid_token_framework.yaml`
- **Feld:** `fee_structure.allocation`
- **Erwarteter Wert:** "1% dev (direct), 2% system treasury"
- **Typ:** MUST
- **Validierung:** `yaml_field_equals("...", "fee_structure.allocation", "1% dev (direct), 2% system treasury")`
- **Severity:** CRITICAL

### YAML-P1-016: Burn from System Fee
- **Zeile:** 53
- **YAML-Pfad:** `20_foundation/tokenomics/ssid_token_framework.yaml`
- **Feld:** `fee_structure.burn_from_system_fee`
- **Erwarteter Wert:** "50% of 2% with daily/monthly caps"
- **Typ:** MUST
- **Validierung:** `yaml_field_contains("...", "fee_structure.burn_from_system_fee", "50%")`
- **Severity:** HIGH

### YAML-P1-017: Fee Collection Automated
- **Zeile:** 54
- **YAML-Pfad:** `20_foundation/tokenomics/ssid_token_framework.yaml`
- **Feld:** `fee_structure.fee_collection`
- **Erwarteter Wert:** "Smart contract automated"
- **Typ:** MUST
- **Validierung:** `yaml_field_equals("...", "fee_structure.fee_collection", "Smart contract automated")`
- **Severity:** HIGH

### YAML-P1-018: No Manual Intervention
- **Zeile:** 55
- **YAML-Pfad:** `20_foundation/tokenomics/ssid_token_framework.yaml`
- **Feld:** `fee_structure.no_manual_intervention`
- **Erwarteter Wert:** `true`
- **Typ:** MUST
- **Validierung:** `yaml_field_equals("...", "fee_structure.no_manual_intervention", true)`
- **Severity:** CRITICAL

---

## YAML-Feld-Regeln - Legal Safe Harbor (YAML_LEGAL)

### YAML-P1-019: Security Token FALSE
- **Zeile:** 58
- **YAML-Pfad:** `20_foundation/tokenomics/ssid_token_framework.yaml`
- **Feld:** `legal_safe_harbor.security_token`
- **Erwarteter Wert:** `false`
- **Typ:** MUST
- **Validierung:** `yaml_field_equals("...", "legal_safe_harbor.security_token", false)`
- **Severity:** CRITICAL

### YAML-P1-020: E-Money Token FALSE
- **Zeile:** 59
- **YAML-Pfad:** `20_foundation/tokenomics/ssid_token_framework.yaml`
- **Feld:** `legal_safe_harbor.e_money_token`
- **Erwarteter Wert:** `false`
- **Typ:** MUST
- **Validierung:** `yaml_field_equals("...", "legal_safe_harbor.e_money_token", false)`
- **Severity:** CRITICAL

### YAML-P1-021: Stablecoin FALSE
- **Zeile:** 60
- **YAML-Pfad:** `20_foundation/tokenomics/ssid_token_framework.yaml`
- **Feld:** `legal_safe_harbor.stablecoin`
- **Erwarteter Wert:** `false`
- **Typ:** MUST
- **Validierung:** `yaml_field_equals("...", "legal_safe_harbor.stablecoin", false)`
- **Severity:** CRITICAL

### YAML-P1-022: Yield Bearing FALSE
- **Zeile:** 61
- **YAML-Pfad:** `20_foundation/tokenomics/ssid_token_framework.yaml`
- **Feld:** `legal_safe_harbor.yield_bearing`
- **Erwarteter Wert:** `false`
- **Typ:** MUST
- **Validierung:** `yaml_field_equals("...", "legal_safe_harbor.yield_bearing", false)`
- **Severity:** CRITICAL

### YAML-P1-023: Redemption Rights FALSE
- **Zeile:** 62
- **YAML-Pfad:** `20_foundation/tokenomics/ssid_token_framework.yaml`
- **Feld:** `legal_safe_harbor.redemption_rights`
- **Erwarteter Wert:** `false`
- **Typ:** MUST
- **Validierung:** `yaml_field_equals("...", "legal_safe_harbor.redemption_rights", false)`
- **Severity:** CRITICAL

### YAML-P1-024: Passive Income FALSE
- **Zeile:** 63
- **YAML-Pfad:** `20_foundation/tokenomics/ssid_token_framework.yaml`
- **Feld:** `legal_safe_harbor.passive_income`
- **Erwarteter Wert:** `false`
- **Typ:** MUST
- **Validierung:** `yaml_field_equals("...", "legal_safe_harbor.passive_income", false)`
- **Severity:** CRITICAL

### YAML-P1-025: Investment Contract FALSE
- **Zeile:** 64
- **YAML-Pfad:** `20_foundation/tokenomics/ssid_token_framework.yaml`
- **Feld:** `legal_safe_harbor.investment_contract`
- **Erwarteter Wert:** `false`
- **Typ:** MUST
- **Validierung:** `yaml_field_equals("...", "legal_safe_harbor.investment_contract", false)`
- **Severity:** CRITICAL

### YAML-P1-026: Admin Controls Specification
- **Zeile:** 65
- **YAML-Pfad:** `20_foundation/tokenomics/ssid_token_framework.yaml`
- **Feld:** `legal_safe_harbor.admin_controls`
- **Erwarteter Wert:** "No privileged admin keys. Proxy owner = DAO Timelock; emergency multisig acts only via time-locked governance paths (no direct overrides)."
- **Typ:** MUST
- **Validierung:** `yaml_field_contains("...", "legal_safe_harbor.admin_controls", "No privileged admin keys")`
- **Severity:** CRITICAL

### YAML-P1-027: Upgrade Mechanism
- **Zeile:** 66
- **YAML-Pfad:** `20_foundation/tokenomics/ssid_token_framework.yaml`
- **Feld:** `legal_safe_harbor.upgrade_mechanism`
- **Erwarteter Wert:** "On-chain proposals only via DAO governance"
- **Typ:** MUST
- **Validierung:** `yaml_field_equals("...", "legal_safe_harbor.upgrade_mechanism", "On-chain proposals only via DAO governance")`
- **Severity:** CRITICAL

---

## YAML-Feld-Regeln - Business Model (YAML_BUSINESS)

### YAML-P1-028: Business Role
- **Zeile:** 69
- **YAML-Pfad:** `20_foundation/tokenomics/ssid_token_framework.yaml`
- **Feld:** `business_model.role`
- **Erwarteter Wert:** "Technology publisher and open source maintainer"
- **Typ:** MUST
- **Validierung:** `yaml_field_equals("...", "business_model.role", "Technology publisher and open source maintainer")`
- **Severity:** HIGH

### YAML-P1-029: Business NOT Role (4 Exclusions)
- **Zeile:** 70
- **YAML-Pfad:** `20_foundation/tokenomics/ssid_token_framework.yaml`
- **Feld:** `business_model.not_role`
- **Erwarteter Wert:** `["payment_service_provider", "custodian", "operator", "exchange"]`
- **Typ:** MUST
- **Validierung:** `yaml_list_equals("...", "business_model.not_role", [...])`
- **Severity:** CRITICAL

### YAML-P1-030: User Interactions
- **Zeile:** 71
- **YAML-Pfad:** `20_foundation/tokenomics/ssid_token_framework.yaml`
- **Feld:** `business_model.user_interactions`
- **Erwarteter Wert:** "Direct peer-to-peer via smart contracts"
- **Typ:** MUST
- **Validierung:** `yaml_field_equals("...", "business_model.user_interactions", "Direct peer-to-peer...")`
- **Severity:** HIGH

### YAML-P1-031: KYC Responsibility
- **Zeile:** 72
- **YAML-Pfad:** `20_foundation/tokenomics/ssid_token_framework.yaml`
- **Feld:** `business_model.kyc_responsibility`
- **Erwarteter Wert:** "Third-party KYC providers (users pay directly)"
- **Typ:** MUST
- **Validierung:** `yaml_field_equals("...", "business_model.kyc_responsibility", "Third-party KYC providers...")`
- **Severity:** HIGH

### YAML-P1-032: Data Custody
- **Zeile:** 73
- **YAML-Pfad:** `20_foundation/tokenomics/ssid_token_framework.yaml`
- **Feld:** `business_model.data_custody`
- **Erwarteter Wert:** "Zero personal data on-chain"
- **Typ:** MUST
- **Validierung:** `yaml_field_equals("...", "business_model.data_custody", "Zero personal data on-chain")`
- **Severity:** CRITICAL

---

## YAML-Feld-Regeln - Governance Framework (YAML_GOVERNANCE)

### YAML-P1-033: DAO Ready TRUE
- **Zeile:** 76
- **YAML-Pfad:** `20_foundation/tokenomics/ssid_token_framework.yaml`
- **Feld:** `governance_framework.dao_ready`
- **Erwarteter Wert:** `true`
- **Typ:** MUST
- **Validierung:** `yaml_field_equals("...", "governance_framework.dao_ready", true)`
- **Severity:** HIGH

### YAML-P1-034: Voting Mechanism
- **Zeile:** 77
- **YAML-Pfad:** `20_foundation/tokenomics/ssid_token_framework.yaml`
- **Feld:** `governance_framework.voting_mechanism`
- **Erwarteter Wert:** "Token-weighted governance"
- **Typ:** MUST
- **Validierung:** `yaml_field_equals("...", "governance_framework.voting_mechanism", "Token-weighted governance")`
- **Severity:** HIGH

### YAML-P1-035: Proposal System
- **Zeile:** 78
- **YAML-Pfad:** `20_foundation/tokenomics/ssid_token_framework.yaml`
- **Feld:** `governance_framework.proposal_system`
- **Erwarteter Wert:** "Snapshot + on-chain execution"
- **Typ:** MUST
- **Validierung:** `yaml_field_equals("...", "governance_framework.proposal_system", "Snapshot + on-chain execution")`
- **Severity:** HIGH

### YAML-P1-036: Upgrade Authority
- **Zeile:** 79
- **YAML-Pfad:** `20_foundation/tokenomics/ssid_token_framework.yaml`
- **Feld:** `governance_framework.upgrade_authority`
- **Erwarteter Wert:** "DAO only (no admin keys)"
- **Typ:** MUST
- **Validierung:** `yaml_field_equals("...", "governance_framework.upgrade_authority", "DAO only (no admin keys)")`
- **Severity:** CRITICAL

### YAML-P1-037: Emergency Procedures
- **Zeile:** 80
- **YAML-Pfad:** `20_foundation/tokenomics/ssid_token_framework.yaml`
- **Feld:** `governance_framework.emergency_procedures`
- **Erwarteter Wert:** "Community multisig"
- **Typ:** MUST
- **Validierung:** `yaml_field_equals("...", "governance_framework.emergency_procedures", "Community multisig")`
- **Severity:** HIGH

---

## YAML-Feld-Regeln - Jurisdictional Compliance (YAML_JURISDICTION)

### YAML-P1-038: Blacklist Jurisdictions (4 Sanctioned)
- **Zeile:** 85
- **YAML-Pfad:** `20_foundation/tokenomics/ssid_token_framework.yaml`
- **Feld:** `jurisdictional_compliance.blacklist_jurisdictions`
- **Erwarteter Wert:** `["IR", "KP", "SY", "CU"]`
- **Typ:** MUST
- **Validierung:** `yaml_list_contains_all("...", "jurisdictional_compliance.blacklist_jurisdictions", ["IR", "KP", "SY", "CU"])`
- **Severity:** CRITICAL

### YAML-P1-039: Excluded Entities (3 Categories)
- **Zeile:** 86-89
- **YAML-Pfad:** `20_foundation/tokenomics/ssid_token_framework.yaml`
- **Feld:** `jurisdictional_compliance.excluded_entities`
- **Erwarteter Wert:** `["RU_designated_entities", "Belarus_designated_entities", "Venezuela_government_entities"]`
- **Typ:** MUST
- **Validierung:** `yaml_list_equals("...", "jurisdictional_compliance.excluded_entities", [...])`
- **Severity:** CRITICAL

### YAML-P1-040: Excluded Markets (3 Countries)
- **Zeile:** 90
- **YAML-Pfad:** `20_foundation/tokenomics/ssid_token_framework.yaml`
- **Feld:** `jurisdictional_compliance.excluded_markets`
- **Erwarteter Wert:** `["India", "Pakistan", "Myanmar"]`
- **Typ:** MUST
- **Validierung:** `yaml_list_equals("...", "jurisdictional_compliance.excluded_markets", ["India", "Pakistan", "Myanmar"])`
- **Severity:** HIGH

### YAML-P1-041: Compliance Basis
- **Zeile:** 91
- **YAML-Pfad:** `20_foundation/tokenomics/ssid_token_framework.yaml`
- **Feld:** `jurisdictional_compliance.compliance_basis`
- **Erwarteter Wert:** "EU MiCA Article 3 + US Howey Test"
- **Typ:** MUST
- **Validierung:** `yaml_field_equals("...", "jurisdictional_compliance.compliance_basis", "EU MiCA Article 3 + US Howey Test")`
- **Severity:** HIGH

### YAML-P1-042: Regulatory Exemptions
- **Zeile:** 92
- **YAML-Pfad:** `20_foundation/tokenomics/ssid_token_framework.yaml`
- **Feld:** `jurisdictional_compliance.regulatory_exemptions`
- **Erwarteter Wert:** "Utility token exemption"
- **Typ:** MUST
- **Validierung:** `yaml_field_equals("...", "jurisdictional_compliance.regulatory_exemptions", "Utility token exemption")`
- **Severity:** HIGH

---

## YAML-Feld-Regeln - Risk Mitigation (YAML_RISK)

### YAML-P1-043: No Fiat Pegging TRUE
- **Zeile:** 95
- **YAML-Pfad:** `20_foundation/tokenomics/ssid_token_framework.yaml`
- **Feld:** `risk_mitigation.no_fiat_pegging`
- **Erwarteter Wert:** `true`
- **Typ:** MUST
- **Validierung:** `yaml_field_equals("...", "risk_mitigation.no_fiat_pegging", true)`
- **Severity:** CRITICAL

### YAML-P1-044: No Redemption Mechanism TRUE
- **Zeile:** 96
- **YAML-Pfad:** `20_foundation/tokenomics/ssid_token_framework.yaml`
- **Feld:** `risk_mitigation.no_redemption_mechanism`
- **Erwarteter Wert:** `true`
- **Typ:** MUST
- **Validierung:** `yaml_field_equals("...", "risk_mitigation.no_redemption_mechanism", true)`
- **Severity:** CRITICAL

### YAML-P1-045: No Yield Promises TRUE
- **Zeile:** 97
- **YAML-Pfad:** `20_foundation/tokenomics/ssid_token_framework.yaml`
- **Feld:** `risk_mitigation.no_yield_promises`
- **Erwarteter Wert:** `true`
- **Typ:** MUST
- **Validierung:** `yaml_field_equals("...", "risk_mitigation.no_yield_promises", true)`
- **Severity:** CRITICAL

### YAML-P1-046: No Marketing Investment TRUE
- **Zeile:** 98
- **YAML-Pfad:** `20_foundation/tokenomics/ssid_token_framework.yaml`
- **Feld:** `risk_mitigation.no_marketing_investment`
- **Erwarteter Wert:** `true`
- **Typ:** MUST
- **Validierung:** `yaml_field_equals("...", "risk_mitigation.no_marketing_investment", true)`
- **Severity:** HIGH

### YAML-P1-047: Clear Utility Purpose TRUE
- **Zeile:** 99
- **YAML-Pfad:** `20_foundation/tokenomics/ssid_token_framework.yaml`
- **Feld:** `risk_mitigation.clear_utility_purpose`
- **Erwarteter Wert:** `true`
- **Typ:** MUST
- **Validierung:** `yaml_field_equals("...", "risk_mitigation.clear_utility_purpose", true)`
- **Severity:** CRITICAL

### YAML-P1-048: Open Source License
- **Zeile:** 100
- **YAML-Pfad:** `20_foundation/tokenomics/ssid_token_framework.yaml`
- **Feld:** `risk_mitigation.open_source_license`
- **Erwarteter Wert:** "Apache 2.0"
- **Typ:** MUST
- **Validierung:** `yaml_field_equals("...", "risk_mitigation.open_source_license", "Apache 2.0")`
- **Severity:** MEDIUM

---

## YAML-Feld-Regeln - Token Utility Framework (YAML_UTILITY)

### YAML-P1-049: Utility Version
- **Zeile:** 106
- **YAML-Pfad:** `20_foundation/tokenomics/utility_definitions.yaml`
- **Feld:** `version`
- **Erwarteter Wert:** "1.0"
- **Typ:** MUST
- **Validierung:** `yaml_field_equals("20_foundation/tokenomics/utility_definitions.yaml", "version", "1.0")`
- **Severity:** HIGH

### YAML-P1-050: Identity Verification Smart Contract
- **Zeile:** 113
- **YAML-Pfad:** `20_foundation/tokenomics/utility_definitions.yaml`
- **Feld:** `primary_utilities.identity_verification.smart_contract`
- **Erwarteter Wert:** "20_foundation/tokenomics/contracts/verification_payment.sol"
- **Typ:** MUST
- **Validierung:** `yaml_field_equals("...", "primary_utilities.identity_verification.smart_contract", "20_foundation/...")`
- **Severity:** HIGH

### YAML-P1-051: Voting Weight Linear
- **Zeile:** 120
- **YAML-Pfad:** `20_foundation/tokenomics/utility_definitions.yaml`
- **Feld:** `primary_utilities.governance_participation.voting_weight`
- **Erwarteter Wert:** "Linear token holdings"
- **Typ:** MUST
- **Validierung:** `yaml_field_equals("...", "primary_utilities.governance_participation.voting_weight", "Linear token holdings")`
- **Severity:** HIGH

### YAML-P1-052: Proposal Threshold 1%
- **Zeile:** 121
- **YAML-Pfad:** `20_foundation/tokenomics/utility_definitions.yaml`
- **Feld:** `primary_utilities.governance_participation.proposal_threshold`
- **Erwarteter Wert:** "1% of total supply to propose"
- **Typ:** MUST
- **Validierung:** `yaml_field_contains("...", "primary_utilities.governance_participation.proposal_threshold", "1%")`
- **Severity:** HIGH

### YAML-P1-053: Reward Pools (3 Types)
- **Zeile:** 126
- **YAML-Pfad:** `20_foundation/tokenomics/utility_definitions.yaml`
- **Feld:** `primary_utilities.ecosystem_rewards.reward_pools`
- **Erwarteter Wert:** `["validation", "development", "community"]`
- **Typ:** MUST
- **Validierung:** `yaml_list_equals("...", "primary_utilities.ecosystem_rewards.reward_pools", ["validation", "development", "community"])`
- **Severity:** MEDIUM

---

## YAML-Feld-Regeln - Token Economics (YAML_ECONOMICS)

### YAML-P1-054: Total Supply 1 Billion
- **Zeile:** 153
- **YAML-Pfad:** `20_foundation/tokenomics/token_economics.yaml`
- **Feld:** `supply_mechanics.total_supply`
- **Erwarteter Wert:** "1,000,000,000 SSID"
- **Typ:** MUST
- **Validierung:** `yaml_field_contains("20_foundation/tokenomics/token_economics.yaml", "supply_mechanics.total_supply", "1,000,000,000")`
- **Severity:** CRITICAL

### YAML-P1-055: Ecosystem Development 40%
- **Zeile:** 155
- **YAML-Pfad:** `20_foundation/tokenomics/token_economics.yaml`
- **Feld:** `supply_mechanics.initial_distribution.ecosystem_development`
- **Erwarteter Wert:** "40%"
- **Typ:** MUST
- **Validierung:** `yaml_field_equals("...", "supply_mechanics.initial_distribution.ecosystem_development", "40%")`
- **Severity:** HIGH

### YAML-P1-056: Community Rewards 25%
- **Zeile:** 156
- **YAML-Pfad:** `20_foundation/tokenomics/token_economics.yaml`
- **Feld:** `supply_mechanics.initial_distribution.community_rewards`
- **Erwarteter Wert:** "25%"
- **Typ:** MUST
- **Validierung:** `yaml_field_equals("...", "supply_mechanics.initial_distribution.community_rewards", "25%")`
- **Severity:** HIGH

### YAML-P1-057: Team Development 15%
- **Zeile:** 157
- **YAML-Pfad:** `20_foundation/tokenomics/token_economics.yaml`
- **Feld:** `supply_mechanics.initial_distribution.team_development`
- **Erwarteter Wert:** "15%"
- **Typ:** MUST
- **Validierung:** `yaml_field_equals("...", "supply_mechanics.initial_distribution.team_development", "15%")`
- **Severity:** HIGH

### YAML-P1-058: Partnerships 10%
- **Zeile:** 158
- **YAML-Pfad:** `20_foundation/tokenomics/token_economics.yaml`
- **Feld:** `supply_mechanics.initial_distribution.partnerships`
- **Erwarteter Wert:** "10%"
- **Typ:** MUST
- **Validierung:** `yaml_field_equals("...", "supply_mechanics.initial_distribution.partnerships", "10%")`
- **Severity:** HIGH

### YAML-P1-059: Reserve Fund 10%
- **Zeile:** 159
- **YAML-Pfad:** `20_foundation/tokenomics/token_economics.yaml`
- **Feld:** `supply_mechanics.initial_distribution.reserve_fund`
- **Erwarteter Wert:** "10%"
- **Typ:** MUST
- **Validierung:** `yaml_field_equals("...", "supply_mechanics.initial_distribution.reserve_fund", "10%")`
- **Severity:** HIGH

### YAML-P1-060: Max Annual Inflation 0%
- **Zeile:** 166
- **YAML-Pfad:** `20_foundation/tokenomics/token_economics.yaml`
- **Feld:** `supply_mechanics.circulation_controls.max_annual_inflation`
- **Erwarteter Wert:** "0%"
- **Typ:** MUST
- **Validierung:** `yaml_field_equals("...", "supply_mechanics.circulation_controls.max_annual_inflation", "0%")`
- **Severity:** CRITICAL

---

## Constraint-Regeln (CONSTRAINTS)

### CONST-P1-001: Distribution Sum = 100%
- **Zeilen:** 155-159
- **Beschreibung:** Initial Distribution muss exakt 100% ergeben
- **Validierung:** `40% + 25% + 15% + 10% + 10% = 100%`
- **Typ:** MUST
- **Severity:** CRITICAL
- **Evidence:** Mathematical validation of distribution percentages

### CONST-P1-002: Fee Split = 3%
- **Zeile:** 175
- **Beschreibung:** Total fee must equal 3% (1% + 2%)
- **Validierung:** `dev_fee + system_treasury = 1% + 2% = 3%`
- **Typ:** MUST
- **Severity:** CRITICAL

### CONST-P1-003: Burn Rate = 50% of 2%
- **Zeile:** 180
- **Beschreibung:** Burn from treasury must be 50% of 2% system treasury
- **Validierung:** `burn_policy = 50%` AND `base = circulating_supply_snapshot`
- **Typ:** MUST
- **Severity:** HIGH

### CONST-P1-004: Daily Cap <= 0.5%
- **Zeile:** 183
- **Beschreibung:** Daily burn cap max 0.5% of circulating supply
- **Validierung:** `daily_cap_percent_of_circ <= 0.5`
- **Typ:** MUST
- **Severity:** HIGH

### CONST-P1-005: Monthly Cap <= 2.0%
- **Zeile:** 184
- **Beschreibung:** Monthly burn cap max 2.0% of circulating supply
- **Validierung:** `monthly_cap_percent_of_circ <= 2.0`
- **Typ:** MUST
- **Severity:** HIGH

---

## SUMMARY - Part1 Manuelle Extraktion

**Total Semantic Rules Identified:** 60+

**Kategorien:**
- STRUCTURE: 4 rules (Root-Struktur, Ausnahmen)
- YAML_TOKEN_ARCH: 18 rules (Token Framework Felder)
- YAML_LEGAL: 9 rules (Legal Safe Harbor)
- YAML_BUSINESS: 5 rules (Business Model)
- YAML_GOVERNANCE: 5 rules (Governance Framework)
- YAML_JURISDICTION: 5 rules (Jurisdictional Compliance)
- YAML_RISK: 6 rules (Risk Mitigation)
- YAML_UTILITY: 5 rules (Utility Framework)
- YAML_ECONOMICS: 6 rules (Token Economics)
- CONSTRAINTS: 5 rules (Mathematical constraints)

**Noch zu analysieren:** Zeilen 286-1257 (Language Strategy, Governance Parameters, etc.)

**Nächster Schritt:** Maschinelle Extraktion entwickeln, dann Vergleich.
