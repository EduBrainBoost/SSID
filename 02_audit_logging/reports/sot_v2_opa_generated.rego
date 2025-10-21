# ============================================================
# SOT-V2 RULES (0001-0189): CONTRACT VALIDATION
# ============================================================
# Auto-generated from sot_contract_v2.yaml
# Date: 2025-10-20T21:39:55.043275
# Source: 16_codex/structure/level3/sot_contract_v2.yaml
# ============================================================

package ssid.sot_v2

import future.keywords.if
import future.keywords.in



# SOT-V2-0001: Semantic rule for 'business_model'.
# Severity: MEDIUM
# Category: GENERAL
# Field: business_model
deny[msg] {
    not input.contract.business_model
    msg := sprintf("SOT-V2-0001 VIOLATION: Missing required field 'business_model'", [])
}


# SOT-V2-0002: Semantic rule for 'business_model.data_custody'.
# Severity: MEDIUM
# Category: GENERAL
# Field: business_model.data_custody
deny[msg] {
    not input.contract.business_model.data_custody
    msg := sprintf("SOT-V2-0002 VIOLATION: Missing required field 'business_model.data_custody'", [])
}


# SOT-V2-0003: Semantic rule for 'business_model.kyc_responsibility'.
# Severity: MEDIUM
# Category: GENERAL
# Field: business_model.kyc_responsibility
deny[msg] {
    not input.contract.business_model.kyc_responsibility
    msg := sprintf("SOT-V2-0003 VIOLATION: Missing required field 'business_model.kyc_responsibility'", [])
}


# SOT-V2-0004: Semantic rule for 'business_model.not_role'.
# Severity: MEDIUM
# Category: GENERAL
# Field: business_model.not_role
deny[msg] {
    not input.contract.business_model.not_role
    msg := sprintf("SOT-V2-0004 VIOLATION: Missing required field 'business_model.not_role'", [])
}


# SOT-V2-0005: Semantic rule for 'business_model.role'.
# Severity: MEDIUM
# Category: GENERAL
# Field: business_model.role
deny[msg] {
    not input.contract.business_model.role
    msg := sprintf("SOT-V2-0005 VIOLATION: Missing required field 'business_model.role'", [])
}


# SOT-V2-0006: Semantic rule for 'business_model.user_interactions'.
# Severity: MEDIUM
# Category: GENERAL
# Field: business_model.user_interactions
deny[msg] {
    not input.contract.business_model.user_interactions
    msg := sprintf("SOT-V2-0006 VIOLATION: Missing required field 'business_model.user_interactions'", [])
}


# SOT-V2-0007: Semantic rule for 'classification'.
# Severity: INFO
# Category: METADATA
# Field: classification
deny[msg] {
    not input.contract.classification
    msg := sprintf("SOT-V2-0007 VIOLATION: Missing required field 'classification'", [])
}


# SOT-V2-0008: Semantic rule for 'compliance_utilities'.
# Severity: HIGH
# Category: COMPLIANCE
# Field: compliance_utilities
deny[msg] {
    not input.contract.compliance_utilities
    msg := sprintf("SOT-V2-0008 VIOLATION: Missing required field 'compliance_utilities'", [])
}


# SOT-V2-0009: Semantic rule for 'compliance_utilities.audit_payments'.
# Severity: HIGH
# Category: COMPLIANCE
# Field: compliance_utilities.audit_payments
deny[msg] {
    not input.contract.compliance_utilities.audit_payments
    msg := sprintf("SOT-V2-0009 VIOLATION: Missing required field 'compliance_utilities.audit_payments'", [])
}


# SOT-V2-0010: Semantic rule for 'compliance_utilities.legal_attestations'.
# Severity: HIGH
# Category: COMPLIANCE
# Field: compliance_utilities.legal_attestations
deny[msg] {
    not input.contract.compliance_utilities.legal_attestations
    msg := sprintf("SOT-V2-0010 VIOLATION: Missing required field 'compliance_utilities.legal_attestations'", [])
}


# SOT-V2-0011: Semantic rule for 'compliance_utilities.regulatory_reporting'.
# Severity: HIGH
# Category: COMPLIANCE
# Field: compliance_utilities.regulatory_reporting
deny[msg] {
    not input.contract.compliance_utilities.regulatory_reporting
    msg := sprintf("SOT-V2-0011 VIOLATION: Missing required field 'compliance_utilities.regulatory_reporting'", [])
}


# SOT-V2-0012: Semantic rule for 'date'.
# Severity: INFO
# Category: METADATA
# Field: date
deny[msg] {
    not input.contract.date
    msg := sprintf("SOT-V2-0012 VIOLATION: Missing required field 'date'", [])
}


# SOT-V2-0013: Semantic rule for 'deprecated'.
# Severity: INFO
# Category: METADATA
# Field: deprecated
deny[msg] {
    not input.contract.deprecated
    msg := sprintf("SOT-V2-0013 VIOLATION: Missing required field 'deprecated'", [])
}


# SOT-V2-0014: Semantic rule for 'fee_routing'.
# Severity: HIGH
# Category: ECONOMICS
# Field: fee_routing
deny[msg] {
    not input.contract.fee_routing
    msg := sprintf("SOT-V2-0014 VIOLATION: Missing required field 'fee_routing'", [])
}


# SOT-V2-0015: Semantic rule for 'fee_routing.system_fees'.
# Severity: HIGH
# Category: ECONOMICS
# Field: fee_routing.system_fees
deny[msg] {
    not input.contract.fee_routing.system_fees
    msg := sprintf("SOT-V2-0015 VIOLATION: Missing required field 'fee_routing.system_fees'", [])
}


# SOT-V2-0016: Semantic rule for 'fee_routing.system_fees.allocation'.
# Severity: HIGH
# Category: ECONOMICS
# Field: fee_routing.system_fees.allocation
deny[msg] {
    not input.contract.fee_routing.system_fees.allocation
    msg := sprintf("SOT-V2-0016 VIOLATION: Missing required field 'fee_routing.system_fees.allocation'", [])
}


# SOT-V2-0017: Semantic rule for 'fee_routing.system_fees.allocation.dev_fee'.
# Severity: HIGH
# Category: ECONOMICS
# Field: fee_routing.system_fees.allocation.dev_fee
deny[msg] {
    not input.contract.fee_routing.system_fees.allocation.dev_fee
    msg := sprintf("SOT-V2-0017 VIOLATION: Missing required field 'fee_routing.system_fees.allocation.dev_fee'", [])
}


# SOT-V2-0018: Semantic rule for 'fee_routing.system_fees.allocation.system_treasury'.
# Severity: HIGH
# Category: ECONOMICS
# Field: fee_routing.system_fees.allocation.system_treasury
deny[msg] {
    not input.contract.fee_routing.system_fees.allocation.system_treasury
    msg := sprintf("SOT-V2-0018 VIOLATION: Missing required field 'fee_routing.system_fees.allocation.system_treasury'", [])
}


# SOT-V2-0019: Semantic rule for 'fee_routing.system_fees.burn_from_system_fee'.
# Severity: HIGH
# Category: ECONOMICS
# Field: fee_routing.system_fees.burn_from_system_fee
deny[msg] {
    not input.contract.fee_routing.system_fees.burn_from_system_fee
    msg := sprintf("SOT-V2-0019 VIOLATION: Missing required field 'fee_routing.system_fees.burn_from_system_fee'", [])
}


# SOT-V2-0020: Semantic rule for 'fee_routing.system_fees.burn_from_system_fee.base'.
# Severity: HIGH
# Category: ECONOMICS
# Field: fee_routing.system_fees.burn_from_system_fee.base
deny[msg] {
    not input.contract.fee_routing.system_fees.burn_from_system_fee.base
    msg := sprintf("SOT-V2-0020 VIOLATION: Missing required field 'fee_routing.system_fees.burn_from_system_fee.base'", [])
}


# SOT-V2-0021: Semantic rule for 'fee_routing.system_fees.burn_from_system_fee.daily_cap_percent_of_circ'.
# Severity: HIGH
# Category: ECONOMICS
# Field: fee_routing.system_fees.burn_from_system_fee.daily_cap_percent_of_circ
deny[msg] {
    not input.contract.fee_routing.system_fees.burn_from_system_fee.daily_cap_percent_of_circ
    msg := sprintf("SOT-V2-0021 VIOLATION: Missing required field 'fee_routing.system_fees.burn_from_system_fee.daily_cap_percent_of_circ'", [])
}


# SOT-V2-0022: Semantic rule for 'fee_routing.system_fees.burn_from_system_fee.monthly_cap_percent_of_circ'.
# Severity: HIGH
# Category: ECONOMICS
# Field: fee_routing.system_fees.burn_from_system_fee.monthly_cap_percent_of_circ
deny[msg] {
    not input.contract.fee_routing.system_fees.burn_from_system_fee.monthly_cap_percent_of_circ
    msg := sprintf("SOT-V2-0022 VIOLATION: Missing required field 'fee_routing.system_fees.burn_from_system_fee.monthly_cap_percent_of_circ'", [])
}


# SOT-V2-0023: Semantic rule for 'fee_routing.system_fees.burn_from_system_fee.oracle_source'.
# Severity: HIGH
# Category: ECONOMICS
# Field: fee_routing.system_fees.burn_from_system_fee.oracle_source
deny[msg] {
    not input.contract.fee_routing.system_fees.burn_from_system_fee.oracle_source
    msg := sprintf("SOT-V2-0023 VIOLATION: Missing required field 'fee_routing.system_fees.burn_from_system_fee.oracle_source'", [])
}


# SOT-V2-0024: Semantic rule for 'fee_routing.system_fees.burn_from_system_fee.policy'.
# Severity: HIGH
# Category: ECONOMICS
# Field: fee_routing.system_fees.burn_from_system_fee.policy
deny[msg] {
    not input.contract.fee_routing.system_fees.burn_from_system_fee.policy
    msg := sprintf("SOT-V2-0024 VIOLATION: Missing required field 'fee_routing.system_fees.burn_from_system_fee.policy'", [])
}


# SOT-V2-0025: Semantic rule for 'fee_routing.system_fees.burn_from_system_fee.snapshot_time_utc'.
# Severity: HIGH
# Category: ECONOMICS
# Field: fee_routing.system_fees.burn_from_system_fee.snapshot_time_utc
deny[msg] {
    not input.contract.fee_routing.system_fees.burn_from_system_fee.snapshot_time_utc
    msg := sprintf("SOT-V2-0025 VIOLATION: Missing required field 'fee_routing.system_fees.burn_from_system_fee.snapshot_time_utc'", [])
}


# SOT-V2-0026: Semantic rule for 'fee_routing.system_fees.note'.
# Severity: HIGH
# Category: ECONOMICS
# Field: fee_routing.system_fees.note
deny[msg] {
    not input.contract.fee_routing.system_fees.note
    msg := sprintf("SOT-V2-0026 VIOLATION: Missing required field 'fee_routing.system_fees.note'", [])
}


# SOT-V2-0027: Semantic rule for 'fee_routing.system_fees.scope'.
# Severity: HIGH
# Category: ECONOMICS
# Field: fee_routing.system_fees.scope
deny[msg] {
    not input.contract.fee_routing.system_fees.scope
    msg := sprintf("SOT-V2-0027 VIOLATION: Missing required field 'fee_routing.system_fees.scope'", [])
}


# SOT-V2-0028: Semantic rule for 'fee_routing.system_fees.total_fee'.
# Severity: HIGH
# Category: ECONOMICS
# Field: fee_routing.system_fees.total_fee
deny[msg] {
    not input.contract.fee_routing.system_fees.total_fee
    msg := sprintf("SOT-V2-0028 VIOLATION: Missing required field 'fee_routing.system_fees.total_fee'", [])
}


# SOT-V2-0029: Semantic rule for 'fee_routing.validator_rewards'.
# Severity: HIGH
# Category: ECONOMICS
# Field: fee_routing.validator_rewards
deny[msg] {
    not input.contract.fee_routing.validator_rewards
    msg := sprintf("SOT-V2-0029 VIOLATION: Missing required field 'fee_routing.validator_rewards'", [])
}


# SOT-V2-0030: Semantic rule for 'fee_routing.validator_rewards.no_per_transaction_split'.
# Severity: HIGH
# Category: ECONOMICS
# Field: fee_routing.validator_rewards.no_per_transaction_split
deny[msg] {
    not input.contract.fee_routing.validator_rewards.no_per_transaction_split
    msg := sprintf("SOT-V2-0030 VIOLATION: Missing required field 'fee_routing.validator_rewards.no_per_transaction_split'", [])
}


# SOT-V2-0031: Semantic rule for 'fee_routing.validator_rewards.note'.
# Severity: HIGH
# Category: ECONOMICS
# Field: fee_routing.validator_rewards.note
deny[msg] {
    not input.contract.fee_routing.validator_rewards.note
    msg := sprintf("SOT-V2-0031 VIOLATION: Missing required field 'fee_routing.validator_rewards.note'", [])
}


# SOT-V2-0032: Semantic rule for 'fee_routing.validator_rewards.source'.
# Severity: HIGH
# Category: ECONOMICS
# Field: fee_routing.validator_rewards.source
deny[msg] {
    not input.contract.fee_routing.validator_rewards.source
    msg := sprintf("SOT-V2-0032 VIOLATION: Missing required field 'fee_routing.validator_rewards.source'", [])
}


# SOT-V2-0033: Semantic rule for 'fee_structure'.
# Severity: HIGH
# Category: ECONOMICS
# Field: fee_structure
deny[msg] {
    not input.contract.fee_structure
    msg := sprintf("SOT-V2-0033 VIOLATION: Missing required field 'fee_structure'", [])
}


# SOT-V2-0034: Semantic rule for 'fee_structure.allocation'.
# Severity: HIGH
# Category: ECONOMICS
# Field: fee_structure.allocation
deny[msg] {
    not input.contract.fee_structure.allocation
    msg := sprintf("SOT-V2-0034 VIOLATION: Missing required field 'fee_structure.allocation'", [])
}


# SOT-V2-0035: Semantic rule for 'fee_structure.burn_from_system_fee'.
# Severity: HIGH
# Category: ECONOMICS
# Field: fee_structure.burn_from_system_fee
deny[msg] {
    not input.contract.fee_structure.burn_from_system_fee
    msg := sprintf("SOT-V2-0035 VIOLATION: Missing required field 'fee_structure.burn_from_system_fee'", [])
}


# SOT-V2-0036: Semantic rule for 'fee_structure.fee_collection'.
# Severity: HIGH
# Category: ECONOMICS
# Field: fee_structure.fee_collection
deny[msg] {
    not input.contract.fee_structure.fee_collection
    msg := sprintf("SOT-V2-0036 VIOLATION: Missing required field 'fee_structure.fee_collection'", [])
}


# SOT-V2-0037: Semantic rule for 'fee_structure.no_manual_intervention'.
# Severity: HIGH
# Category: ECONOMICS
# Field: fee_structure.no_manual_intervention
deny[msg] {
    not input.contract.fee_structure.no_manual_intervention
    msg := sprintf("SOT-V2-0037 VIOLATION: Missing required field 'fee_structure.no_manual_intervention'", [])
}


# SOT-V2-0038: Semantic rule for 'fee_structure.scope'.
# Severity: HIGH
# Category: ECONOMICS
# Field: fee_structure.scope
deny[msg] {
    not input.contract.fee_structure.scope
    msg := sprintf("SOT-V2-0038 VIOLATION: Missing required field 'fee_structure.scope'", [])
}


# SOT-V2-0039: Semantic rule for 'fee_structure.total_fee'.
# Severity: HIGH
# Category: ECONOMICS
# Field: fee_structure.total_fee
deny[msg] {
    not input.contract.fee_structure.total_fee
    msg := sprintf("SOT-V2-0039 VIOLATION: Missing required field 'fee_structure.total_fee'", [])
}


# SOT-V2-0040: Semantic rule for 'governance_controls'.
# Severity: HIGH
# Category: GOVERNANCE
# Field: governance_controls
deny[msg] {
    not input.contract.governance_controls
    msg := sprintf("SOT-V2-0040 VIOLATION: Missing required field 'governance_controls'", [])
}


# SOT-V2-0041: Semantic rule for 'governance_controls.authority'.
# Severity: HIGH
# Category: GOVERNANCE
# Field: governance_controls.authority
deny[msg] {
    not input.contract.governance_controls.authority
    msg := sprintf("SOT-V2-0041 VIOLATION: Missing required field 'governance_controls.authority'", [])
}


# SOT-V2-0042: Semantic rule for 'governance_controls.note'.
# Severity: HIGH
# Category: GOVERNANCE
# Field: governance_controls.note
deny[msg] {
    not input.contract.governance_controls.note
    msg := sprintf("SOT-V2-0042 VIOLATION: Missing required field 'governance_controls.note'", [])
}


# SOT-V2-0043: Semantic rule for 'governance_controls.reference'.
# Severity: HIGH
# Category: GOVERNANCE
# Field: governance_controls.reference
deny[msg] {
    not input.contract.governance_controls.reference
    msg := sprintf("SOT-V2-0043 VIOLATION: Missing required field 'governance_controls.reference'", [])
}


# SOT-V2-0044: Semantic rule for 'governance_fees'.
# Severity: HIGH
# Category: GOVERNANCE
# Field: governance_fees
deny[msg] {
    not input.contract.governance_fees
    msg := sprintf("SOT-V2-0044 VIOLATION: Missing required field 'governance_fees'", [])
}


# SOT-V2-0045: Semantic rule for 'governance_fees.proposal_deposits'.
# Severity: HIGH
# Category: GOVERNANCE
# Field: governance_fees.proposal_deposits
deny[msg] {
    not input.contract.governance_fees.proposal_deposits
    msg := sprintf("SOT-V2-0045 VIOLATION: Missing required field 'governance_fees.proposal_deposits'", [])
}


# SOT-V2-0046: Semantic rule for 'governance_fees.voting_gas'.
# Severity: HIGH
# Category: GOVERNANCE
# Field: governance_fees.voting_gas
deny[msg] {
    not input.contract.governance_fees.voting_gas
    msg := sprintf("SOT-V2-0046 VIOLATION: Missing required field 'governance_fees.voting_gas'", [])
}


# SOT-V2-0047: Semantic rule for 'governance_framework'.
# Severity: HIGH
# Category: GOVERNANCE
# Field: governance_framework
deny[msg] {
    not input.contract.governance_framework
    msg := sprintf("SOT-V2-0047 VIOLATION: Missing required field 'governance_framework'", [])
}


# SOT-V2-0048: Semantic rule for 'governance_framework.dao_ready'.
# Severity: HIGH
# Category: GOVERNANCE
# Field: governance_framework.dao_ready
deny[msg] {
    not input.contract.governance_framework.dao_ready
    msg := sprintf("SOT-V2-0048 VIOLATION: Missing required field 'governance_framework.dao_ready'", [])
}


# SOT-V2-0049: Semantic rule for 'governance_framework.emergency_procedures'.
# Severity: HIGH
# Category: GOVERNANCE
# Field: governance_framework.emergency_procedures
deny[msg] {
    not input.contract.governance_framework.emergency_procedures
    msg := sprintf("SOT-V2-0049 VIOLATION: Missing required field 'governance_framework.emergency_procedures'", [])
}


# SOT-V2-0050: Semantic rule for 'governance_framework.proposal_system'.
# Severity: HIGH
# Category: GOVERNANCE
# Field: governance_framework.proposal_system
deny[msg] {
    not input.contract.governance_framework.proposal_system
    msg := sprintf("SOT-V2-0050 VIOLATION: Missing required field 'governance_framework.proposal_system'", [])
}


# SOT-V2-0051: Semantic rule for 'governance_framework.reference'.
# Severity: HIGH
# Category: GOVERNANCE
# Field: governance_framework.reference
deny[msg] {
    not input.contract.governance_framework.reference
    msg := sprintf("SOT-V2-0051 VIOLATION: Missing required field 'governance_framework.reference'", [])
}


# SOT-V2-0052: Semantic rule for 'governance_framework.upgrade_authority'.
# Severity: HIGH
# Category: GOVERNANCE
# Field: governance_framework.upgrade_authority
deny[msg] {
    not input.contract.governance_framework.upgrade_authority
    msg := sprintf("SOT-V2-0052 VIOLATION: Missing required field 'governance_framework.upgrade_authority'", [])
}


# SOT-V2-0053: Semantic rule for 'governance_framework.voting_mechanism'.
# Severity: HIGH
# Category: GOVERNANCE
# Field: governance_framework.voting_mechanism
deny[msg] {
    not input.contract.governance_framework.voting_mechanism
    msg := sprintf("SOT-V2-0053 VIOLATION: Missing required field 'governance_framework.voting_mechanism'", [])
}


# SOT-V2-0054: Semantic rule for 'governance_parameters'.
# Severity: HIGH
# Category: GOVERNANCE
# Field: governance_parameters
deny[msg] {
    not input.contract.governance_parameters
    msg := sprintf("SOT-V2-0054 VIOLATION: Missing required field 'governance_parameters'", [])
}


# SOT-V2-0055: Semantic rule for 'governance_parameters.delegation_system'.
# Severity: HIGH
# Category: GOVERNANCE
# Field: governance_parameters.delegation_system
deny[msg] {
    not input.contract.governance_parameters.delegation_system
    msg := sprintf("SOT-V2-0055 VIOLATION: Missing required field 'governance_parameters.delegation_system'", [])
}


# SOT-V2-0056: Semantic rule for 'governance_parameters.delegation_system.delegation_changes'.
# Severity: HIGH
# Category: GOVERNANCE
# Field: governance_parameters.delegation_system.delegation_changes
deny[msg] {
    not input.contract.governance_parameters.delegation_system.delegation_changes
    msg := sprintf("SOT-V2-0056 VIOLATION: Missing required field 'governance_parameters.delegation_system.delegation_changes'", [])
}


# SOT-V2-0057: Semantic rule for 'governance_parameters.delegation_system.delegation_enabled'.
# Severity: HIGH
# Category: GOVERNANCE
# Field: governance_parameters.delegation_system.delegation_enabled
deny[msg] {
    not input.contract.governance_parameters.delegation_system.delegation_enabled
    msg := sprintf("SOT-V2-0057 VIOLATION: Missing required field 'governance_parameters.delegation_system.delegation_enabled'", [])
}


# SOT-V2-0058: Semantic rule for 'governance_parameters.delegation_system.self_delegation_default'.
# Severity: HIGH
# Category: GOVERNANCE
# Field: governance_parameters.delegation_system.self_delegation_default
deny[msg] {
    not input.contract.governance_parameters.delegation_system.self_delegation_default
    msg := sprintf("SOT-V2-0058 VIOLATION: Missing required field 'governance_parameters.delegation_system.self_delegation_default'", [])
}


# SOT-V2-0059: Semantic rule for 'governance_parameters.delegation_system.vote_weight_calculation'.
# Severity: HIGH
# Category: GOVERNANCE
# Field: governance_parameters.delegation_system.vote_weight_calculation
deny[msg] {
    not input.contract.governance_parameters.delegation_system.vote_weight_calculation
    msg := sprintf("SOT-V2-0059 VIOLATION: Missing required field 'governance_parameters.delegation_system.vote_weight_calculation'", [])
}


# SOT-V2-0060: Semantic rule for 'governance_parameters.governance_rewards'.
# Severity: HIGH
# Category: GOVERNANCE
# Field: governance_parameters.governance_rewards
deny[msg] {
    not input.contract.governance_parameters.governance_rewards
    msg := sprintf("SOT-V2-0060 VIOLATION: Missing required field 'governance_parameters.governance_rewards'", [])
}


# SOT-V2-0061: Semantic rule for 'governance_parameters.governance_rewards.delegate_rewards'.
# Severity: HIGH
# Category: GOVERNANCE
# Field: governance_parameters.governance_rewards.delegate_rewards
deny[msg] {
    not input.contract.governance_parameters.governance_rewards.delegate_rewards
    msg := sprintf("SOT-V2-0061 VIOLATION: Missing required field 'governance_parameters.governance_rewards.delegate_rewards'", [])
}


# SOT-V2-0062: Semantic rule for 'governance_parameters.governance_rewards.minimum_participation'.
# Severity: HIGH
# Category: GOVERNANCE
# Field: governance_parameters.governance_rewards.minimum_participation
deny[msg] {
    not input.contract.governance_parameters.governance_rewards.minimum_participation
    msg := sprintf("SOT-V2-0062 VIOLATION: Missing required field 'governance_parameters.governance_rewards.minimum_participation'", [])
}


# SOT-V2-0063: Semantic rule for 'governance_parameters.governance_rewards.proposal_creator_rewards'.
# Severity: HIGH
# Category: GOVERNANCE
# Field: governance_parameters.governance_rewards.proposal_creator_rewards
deny[msg] {
    not input.contract.governance_parameters.governance_rewards.proposal_creator_rewards
    msg := sprintf("SOT-V2-0063 VIOLATION: Missing required field 'governance_parameters.governance_rewards.proposal_creator_rewards'", [])
}


# SOT-V2-0064: Semantic rule for 'governance_parameters.governance_rewards.voter_participation_rewards'.
# Severity: HIGH
# Category: GOVERNANCE
# Field: governance_parameters.governance_rewards.voter_participation_rewards
deny[msg] {
    not input.contract.governance_parameters.governance_rewards.voter_participation_rewards
    msg := sprintf("SOT-V2-0064 VIOLATION: Missing required field 'governance_parameters.governance_rewards.voter_participation_rewards'", [])
}


# SOT-V2-0065: Semantic rule for 'governance_parameters.proposal_framework'.
# Severity: HIGH
# Category: GOVERNANCE
# Field: governance_parameters.proposal_framework
deny[msg] {
    not input.contract.governance_parameters.proposal_framework
    msg := sprintf("SOT-V2-0065 VIOLATION: Missing required field 'governance_parameters.proposal_framework'", [])
}


# SOT-V2-0066: Semantic rule for 'governance_parameters.proposal_framework.proposal_deposit'.
# Severity: HIGH
# Category: GOVERNANCE
# Field: governance_parameters.proposal_framework.proposal_deposit
deny[msg] {
    not input.contract.governance_parameters.proposal_framework.proposal_deposit
    msg := sprintf("SOT-V2-0066 VIOLATION: Missing required field 'governance_parameters.proposal_framework.proposal_deposit'", [])
}


# SOT-V2-0067: Semantic rule for 'governance_parameters.proposal_framework.proposal_threshold'.
# Severity: HIGH
# Category: GOVERNANCE
# Field: governance_parameters.proposal_framework.proposal_threshold
deny[msg] {
    not input.contract.governance_parameters.proposal_framework.proposal_threshold
    msg := sprintf("SOT-V2-0067 VIOLATION: Missing required field 'governance_parameters.proposal_framework.proposal_threshold'", [])
}


# SOT-V2-0068: Semantic rule for 'governance_parameters.proposal_framework.proposal_types'.
# Severity: HIGH
# Category: GOVERNANCE
# Field: governance_parameters.proposal_framework.proposal_types
deny[msg] {
    not input.contract.governance_parameters.proposal_framework.proposal_types
    msg := sprintf("SOT-V2-0068 VIOLATION: Missing required field 'governance_parameters.proposal_framework.proposal_types'", [])
}


# SOT-V2-0069: Semantic rule for 'governance_parameters.proposal_framework.proposal_types::Emergency proposals (expedited process)'.
# Severity: HIGH
# Category: GOVERNANCE
# Field: governance_parameters.proposal_framework.proposal_types
deny[msg] {
    not input.contract.governance_parameters.proposal_framework.proposal_types
    msg := sprintf("SOT-V2-0069 VIOLATION: Missing required field 'governance_parameters.proposal_framework.proposal_types'", [])
}


# SOT-V2-0070: Semantic rule for 'governance_parameters.proposal_framework.proposal_types::Parameter changes (requires simple majority)'.
# Severity: HIGH
# Category: GOVERNANCE
# Field: governance_parameters.proposal_framework.proposal_types
deny[msg] {
    not input.contract.governance_parameters.proposal_framework.proposal_types
    msg := sprintf("SOT-V2-0070 VIOLATION: Missing required field 'governance_parameters.proposal_framework.proposal_types'", [])
}


# SOT-V2-0071: Semantic rule for 'governance_parameters.proposal_framework.proposal_types::Protocol upgrades (requires supermajority)'.
# Severity: HIGH
# Category: GOVERNANCE
# Field: governance_parameters.proposal_framework.proposal_types
deny[msg] {
    not input.contract.governance_parameters.proposal_framework.proposal_types
    msg := sprintf("SOT-V2-0071 VIOLATION: Missing required field 'governance_parameters.proposal_framework.proposal_types'", [])
}


# SOT-V2-0072: Semantic rule for 'governance_parameters.proposal_framework.proposal_types::Treasury allocation (requires quorum + majority)'.
# Severity: HIGH
# Category: GOVERNANCE
# Field: governance_parameters.proposal_framework.proposal_types
deny[msg] {
    not input.contract.governance_parameters.proposal_framework.proposal_types
    msg := sprintf("SOT-V2-0072 VIOLATION: Missing required field 'governance_parameters.proposal_framework.proposal_types'", [])
}


# SOT-V2-0073: Semantic rule for 'governance_parameters.timelock_framework'.
# Severity: HIGH
# Category: GOVERNANCE
# Field: governance_parameters.timelock_framework
deny[msg] {
    not input.contract.governance_parameters.timelock_framework
    msg := sprintf("SOT-V2-0073 VIOLATION: Missing required field 'governance_parameters.timelock_framework'", [])
}


# SOT-V2-0074: Semantic rule for 'governance_parameters.timelock_framework.emergency_proposals'.
# Severity: HIGH
# Category: GOVERNANCE
# Field: governance_parameters.timelock_framework.emergency_proposals
deny[msg] {
    not input.contract.governance_parameters.timelock_framework.emergency_proposals
    msg := sprintf("SOT-V2-0074 VIOLATION: Missing required field 'governance_parameters.timelock_framework.emergency_proposals'", [])
}


# SOT-V2-0075: Semantic rule for 'governance_parameters.timelock_framework.parameter_changes'.
# Severity: HIGH
# Category: GOVERNANCE
# Field: governance_parameters.timelock_framework.parameter_changes
deny[msg] {
    not input.contract.governance_parameters.timelock_framework.parameter_changes
    msg := sprintf("SOT-V2-0075 VIOLATION: Missing required field 'governance_parameters.timelock_framework.parameter_changes'", [])
}


# SOT-V2-0076: Semantic rule for 'governance_parameters.timelock_framework.protocol_upgrades'.
# Severity: HIGH
# Category: GOVERNANCE
# Field: governance_parameters.timelock_framework.protocol_upgrades
deny[msg] {
    not input.contract.governance_parameters.timelock_framework.protocol_upgrades
    msg := sprintf("SOT-V2-0076 VIOLATION: Missing required field 'governance_parameters.timelock_framework.protocol_upgrades'", [])
}


# SOT-V2-0077: Semantic rule for 'governance_parameters.timelock_framework.standard_proposals'.
# Severity: HIGH
# Category: GOVERNANCE
# Field: governance_parameters.timelock_framework.standard_proposals
deny[msg] {
    not input.contract.governance_parameters.timelock_framework.standard_proposals
    msg := sprintf("SOT-V2-0077 VIOLATION: Missing required field 'governance_parameters.timelock_framework.standard_proposals'", [])
}


# SOT-V2-0078: Semantic rule for 'governance_parameters.timelock_framework.treasury_allocations'.
# Severity: HIGH
# Category: GOVERNANCE
# Field: governance_parameters.timelock_framework.treasury_allocations
deny[msg] {
    not input.contract.governance_parameters.timelock_framework.treasury_allocations
    msg := sprintf("SOT-V2-0078 VIOLATION: Missing required field 'governance_parameters.timelock_framework.treasury_allocations'", [])
}


# SOT-V2-0079: Semantic rule for 'governance_parameters.voting_periods'.
# Severity: HIGH
# Category: GOVERNANCE
# Field: governance_parameters.voting_periods
deny[msg] {
    not input.contract.governance_parameters.voting_periods
    msg := sprintf("SOT-V2-0079 VIOLATION: Missing required field 'governance_parameters.voting_periods'", [])
}


# SOT-V2-0080: Semantic rule for 'governance_parameters.voting_periods.emergency_voting'.
# Severity: HIGH
# Category: GOVERNANCE
# Field: governance_parameters.voting_periods.emergency_voting
deny[msg] {
    not input.contract.governance_parameters.voting_periods.emergency_voting
    msg := sprintf("SOT-V2-0080 VIOLATION: Missing required field 'governance_parameters.voting_periods.emergency_voting'", [])
}


# SOT-V2-0081: Semantic rule for 'governance_parameters.voting_periods.parameter_voting'.
# Severity: HIGH
# Category: GOVERNANCE
# Field: governance_parameters.voting_periods.parameter_voting
deny[msg] {
    not input.contract.governance_parameters.voting_periods.parameter_voting
    msg := sprintf("SOT-V2-0081 VIOLATION: Missing required field 'governance_parameters.voting_periods.parameter_voting'", [])
}


# SOT-V2-0082: Semantic rule for 'governance_parameters.voting_periods.protocol_upgrade_voting'.
# Severity: HIGH
# Category: GOVERNANCE
# Field: governance_parameters.voting_periods.protocol_upgrade_voting
deny[msg] {
    not input.contract.governance_parameters.voting_periods.protocol_upgrade_voting
    msg := sprintf("SOT-V2-0082 VIOLATION: Missing required field 'governance_parameters.voting_periods.protocol_upgrade_voting'", [])
}


# SOT-V2-0083: Semantic rule for 'governance_parameters.voting_periods.standard_voting'.
# Severity: HIGH
# Category: GOVERNANCE
# Field: governance_parameters.voting_periods.standard_voting
deny[msg] {
    not input.contract.governance_parameters.voting_periods.standard_voting
    msg := sprintf("SOT-V2-0083 VIOLATION: Missing required field 'governance_parameters.voting_periods.standard_voting'", [])
}


# SOT-V2-0084: Semantic rule for 'governance_parameters.voting_requirements'.
# Severity: HIGH
# Category: GOVERNANCE
# Field: governance_parameters.voting_requirements
deny[msg] {
    not input.contract.governance_parameters.voting_requirements
    msg := sprintf("SOT-V2-0084 VIOLATION: Missing required field 'governance_parameters.voting_requirements'", [])
}


# SOT-V2-0085: Semantic rule for 'governance_parameters.voting_requirements.emergency_supermajority'.
# Severity: HIGH
# Category: GOVERNANCE
# Field: governance_parameters.voting_requirements.emergency_supermajority
deny[msg] {
    not input.contract.governance_parameters.voting_requirements.emergency_supermajority
    msg := sprintf("SOT-V2-0085 VIOLATION: Missing required field 'governance_parameters.voting_requirements.emergency_supermajority'", [])
}


# SOT-V2-0086: Semantic rule for 'governance_parameters.voting_requirements.quorum_emergency'.
# Severity: HIGH
# Category: GOVERNANCE
# Field: governance_parameters.voting_requirements.quorum_emergency
deny[msg] {
    not input.contract.governance_parameters.voting_requirements.quorum_emergency
    msg := sprintf("SOT-V2-0086 VIOLATION: Missing required field 'governance_parameters.voting_requirements.quorum_emergency'", [])
}


# SOT-V2-0087: Semantic rule for 'governance_parameters.voting_requirements.quorum_protocol_upgrade'.
# Severity: HIGH
# Category: GOVERNANCE
# Field: governance_parameters.voting_requirements.quorum_protocol_upgrade
deny[msg] {
    not input.contract.governance_parameters.voting_requirements.quorum_protocol_upgrade
    msg := sprintf("SOT-V2-0087 VIOLATION: Missing required field 'governance_parameters.voting_requirements.quorum_protocol_upgrade'", [])
}


# SOT-V2-0088: Semantic rule for 'governance_parameters.voting_requirements.quorum_standard'.
# Severity: HIGH
# Category: GOVERNANCE
# Field: governance_parameters.voting_requirements.quorum_standard
deny[msg] {
    not input.contract.governance_parameters.voting_requirements.quorum_standard
    msg := sprintf("SOT-V2-0088 VIOLATION: Missing required field 'governance_parameters.voting_requirements.quorum_standard'", [])
}


# SOT-V2-0089: Semantic rule for 'governance_parameters.voting_requirements.simple_majority'.
# Severity: HIGH
# Category: GOVERNANCE
# Field: governance_parameters.voting_requirements.simple_majority
deny[msg] {
    not input.contract.governance_parameters.voting_requirements.simple_majority
    msg := sprintf("SOT-V2-0089 VIOLATION: Missing required field 'governance_parameters.voting_requirements.simple_majority'", [])
}


# SOT-V2-0090: Semantic rule for 'governance_parameters.voting_requirements.supermajority'.
# Severity: HIGH
# Category: GOVERNANCE
# Field: governance_parameters.voting_requirements.supermajority
deny[msg] {
    not input.contract.governance_parameters.voting_requirements.supermajority
    msg := sprintf("SOT-V2-0090 VIOLATION: Missing required field 'governance_parameters.voting_requirements.supermajority'", [])
}


# SOT-V2-0095: Semantic rule for 'jurisdictional_compliance'.
# Severity: HIGH
# Category: COMPLIANCE
# Field: jurisdictional_compliance
deny[msg] {
    not input.contract.jurisdictional_compliance
    msg := sprintf("SOT-V2-0095 VIOLATION: Missing required field 'jurisdictional_compliance'", [])
}


# SOT-V2-0096: Semantic rule for 'jurisdictional_compliance.blacklist_jurisdictions'.
# Severity: HIGH
# Category: COMPLIANCE
# Field: jurisdictional_compliance.blacklist_jurisdictions
deny[msg] {
    not input.contract.jurisdictional_compliance.blacklist_jurisdictions
    msg := sprintf("SOT-V2-0096 VIOLATION: Missing required field 'jurisdictional_compliance.blacklist_jurisdictions'", [])
}


# SOT-V2-0097: Semantic rule for 'jurisdictional_compliance.blacklist_jurisdictions::CU'.
# Severity: HIGH
# Category: COMPLIANCE
# Field: jurisdictional_compliance.blacklist_jurisdictions
deny[msg] {
    not input.contract.jurisdictional_compliance.blacklist_jurisdictions
    msg := sprintf("SOT-V2-0097 VIOLATION: Missing required field 'jurisdictional_compliance.blacklist_jurisdictions'", [])
}


# SOT-V2-0098: Semantic rule for 'jurisdictional_compliance.blacklist_jurisdictions::IR'.
# Severity: HIGH
# Category: COMPLIANCE
# Field: jurisdictional_compliance.blacklist_jurisdictions
deny[msg] {
    not input.contract.jurisdictional_compliance.blacklist_jurisdictions
    msg := sprintf("SOT-V2-0098 VIOLATION: Missing required field 'jurisdictional_compliance.blacklist_jurisdictions'", [])
}


# SOT-V2-0099: Semantic rule for 'jurisdictional_compliance.blacklist_jurisdictions::KP'.
# Severity: HIGH
# Category: COMPLIANCE
# Field: jurisdictional_compliance.blacklist_jurisdictions
deny[msg] {
    not input.contract.jurisdictional_compliance.blacklist_jurisdictions
    msg := sprintf("SOT-V2-0099 VIOLATION: Missing required field 'jurisdictional_compliance.blacklist_jurisdictions'", [])
}


# SOT-V2-0100: Semantic rule for 'jurisdictional_compliance.blacklist_jurisdictions::SY'.
# Severity: HIGH
# Category: COMPLIANCE
# Field: jurisdictional_compliance.blacklist_jurisdictions
deny[msg] {
    not input.contract.jurisdictional_compliance.blacklist_jurisdictions
    msg := sprintf("SOT-V2-0100 VIOLATION: Missing required field 'jurisdictional_compliance.blacklist_jurisdictions'", [])
}


# SOT-V2-0101: Semantic rule for 'jurisdictional_compliance.compliance_basis'.
# Severity: HIGH
# Category: COMPLIANCE
# Field: jurisdictional_compliance.compliance_basis
deny[msg] {
    not input.contract.jurisdictional_compliance.compliance_basis
    msg := sprintf("SOT-V2-0101 VIOLATION: Missing required field 'jurisdictional_compliance.compliance_basis'", [])
}


# SOT-V2-0102: Semantic rule for 'jurisdictional_compliance.excluded_entities'.
# Severity: HIGH
# Category: COMPLIANCE
# Field: jurisdictional_compliance.excluded_entities
deny[msg] {
    not input.contract.jurisdictional_compliance.excluded_entities
    msg := sprintf("SOT-V2-0102 VIOLATION: Missing required field 'jurisdictional_compliance.excluded_entities'", [])
}


# SOT-V2-0103: Semantic rule for 'jurisdictional_compliance.excluded_entities::Belarus_designated_entities'.
# Severity: HIGH
# Category: COMPLIANCE
# Field: jurisdictional_compliance.excluded_entities
deny[msg] {
    not input.contract.jurisdictional_compliance.excluded_entities
    msg := sprintf("SOT-V2-0103 VIOLATION: Missing required field 'jurisdictional_compliance.excluded_entities'", [])
}


# SOT-V2-0104: Semantic rule for 'jurisdictional_compliance.excluded_entities::RU_designated_entities'.
# Severity: HIGH
# Category: COMPLIANCE
# Field: jurisdictional_compliance.excluded_entities
deny[msg] {
    not input.contract.jurisdictional_compliance.excluded_entities
    msg := sprintf("SOT-V2-0104 VIOLATION: Missing required field 'jurisdictional_compliance.excluded_entities'", [])
}


# SOT-V2-0105: Semantic rule for 'jurisdictional_compliance.excluded_entities::Venezuela_government_entities'.
# Severity: HIGH
# Category: COMPLIANCE
# Field: jurisdictional_compliance.excluded_entities
deny[msg] {
    not input.contract.jurisdictional_compliance.excluded_entities
    msg := sprintf("SOT-V2-0105 VIOLATION: Missing required field 'jurisdictional_compliance.excluded_entities'", [])
}


# SOT-V2-0106: Semantic rule for 'jurisdictional_compliance.excluded_markets'.
# Severity: HIGH
# Category: COMPLIANCE
# Field: jurisdictional_compliance.excluded_markets
deny[msg] {
    not input.contract.jurisdictional_compliance.excluded_markets
    msg := sprintf("SOT-V2-0106 VIOLATION: Missing required field 'jurisdictional_compliance.excluded_markets'", [])
}


# SOT-V2-0107: Semantic rule for 'jurisdictional_compliance.excluded_markets::India'.
# Severity: HIGH
# Category: COMPLIANCE
# Field: jurisdictional_compliance.excluded_markets
deny[msg] {
    not input.contract.jurisdictional_compliance.excluded_markets
    msg := sprintf("SOT-V2-0107 VIOLATION: Missing required field 'jurisdictional_compliance.excluded_markets'", [])
}


# SOT-V2-0108: Semantic rule for 'jurisdictional_compliance.excluded_markets::Myanmar'.
# Severity: HIGH
# Category: COMPLIANCE
# Field: jurisdictional_compliance.excluded_markets
deny[msg] {
    not input.contract.jurisdictional_compliance.excluded_markets
    msg := sprintf("SOT-V2-0108 VIOLATION: Missing required field 'jurisdictional_compliance.excluded_markets'", [])
}


# SOT-V2-0109: Semantic rule for 'jurisdictional_compliance.excluded_markets::Pakistan'.
# Severity: HIGH
# Category: COMPLIANCE
# Field: jurisdictional_compliance.excluded_markets
deny[msg] {
    not input.contract.jurisdictional_compliance.excluded_markets
    msg := sprintf("SOT-V2-0109 VIOLATION: Missing required field 'jurisdictional_compliance.excluded_markets'", [])
}


# SOT-V2-0110: Semantic rule for 'jurisdictional_compliance.reference'.
# Severity: HIGH
# Category: COMPLIANCE
# Field: jurisdictional_compliance.reference
deny[msg] {
    not input.contract.jurisdictional_compliance.reference
    msg := sprintf("SOT-V2-0110 VIOLATION: Missing required field 'jurisdictional_compliance.reference'", [])
}


# SOT-V2-0111: Semantic rule for 'jurisdictional_compliance.regulatory_exemptions'.
# Severity: HIGH
# Category: COMPLIANCE
# Field: jurisdictional_compliance.regulatory_exemptions
deny[msg] {
    not input.contract.jurisdictional_compliance.regulatory_exemptions
    msg := sprintf("SOT-V2-0111 VIOLATION: Missing required field 'jurisdictional_compliance.regulatory_exemptions'", [])
}


# SOT-V2-0112: Semantic rule for 'legal_safe_harbor'.
# Severity: HIGH
# Category: COMPLIANCE
# Field: legal_safe_harbor
deny[msg] {
    not input.contract.legal_safe_harbor
    msg := sprintf("SOT-V2-0112 VIOLATION: Missing required field 'legal_safe_harbor'", [])
}


# SOT-V2-0113: Semantic rule for 'legal_safe_harbor.admin_controls'.
# Severity: HIGH
# Category: COMPLIANCE
# Field: legal_safe_harbor.admin_controls
deny[msg] {
    not input.contract.legal_safe_harbor.admin_controls
    msg := sprintf("SOT-V2-0113 VIOLATION: Missing required field 'legal_safe_harbor.admin_controls'", [])
}


# SOT-V2-0114: Semantic rule for 'legal_safe_harbor.e_money_token'.
# Severity: HIGH
# Category: COMPLIANCE
# Field: legal_safe_harbor.e_money_token
deny[msg] {
    not input.contract.legal_safe_harbor.e_money_token
    msg := sprintf("SOT-V2-0114 VIOLATION: Missing required field 'legal_safe_harbor.e_money_token'", [])
}


# SOT-V2-0115: Semantic rule for 'legal_safe_harbor.investment_contract'.
# Severity: HIGH
# Category: COMPLIANCE
# Field: legal_safe_harbor.investment_contract
deny[msg] {
    not input.contract.legal_safe_harbor.investment_contract
    msg := sprintf("SOT-V2-0115 VIOLATION: Missing required field 'legal_safe_harbor.investment_contract'", [])
}


# SOT-V2-0116: Semantic rule for 'legal_safe_harbor.passive_income'.
# Severity: HIGH
# Category: COMPLIANCE
# Field: legal_safe_harbor.passive_income
deny[msg] {
    not input.contract.legal_safe_harbor.passive_income
    msg := sprintf("SOT-V2-0116 VIOLATION: Missing required field 'legal_safe_harbor.passive_income'", [])
}


# SOT-V2-0117: Semantic rule for 'legal_safe_harbor.redemption_rights'.
# Severity: HIGH
# Category: COMPLIANCE
# Field: legal_safe_harbor.redemption_rights
deny[msg] {
    not input.contract.legal_safe_harbor.redemption_rights
    msg := sprintf("SOT-V2-0117 VIOLATION: Missing required field 'legal_safe_harbor.redemption_rights'", [])
}


# SOT-V2-0118: Semantic rule for 'legal_safe_harbor.security_token'.
# Severity: HIGH
# Category: COMPLIANCE
# Field: legal_safe_harbor.security_token
deny[msg] {
    not input.contract.legal_safe_harbor.security_token
    msg := sprintf("SOT-V2-0118 VIOLATION: Missing required field 'legal_safe_harbor.security_token'", [])
}


# SOT-V2-0119: Semantic rule for 'legal_safe_harbor.stablecoin'.
# Severity: HIGH
# Category: COMPLIANCE
# Field: legal_safe_harbor.stablecoin
deny[msg] {
    not input.contract.legal_safe_harbor.stablecoin
    msg := sprintf("SOT-V2-0119 VIOLATION: Missing required field 'legal_safe_harbor.stablecoin'", [])
}


# SOT-V2-0120: Semantic rule for 'legal_safe_harbor.upgrade_mechanism'.
# Severity: HIGH
# Category: COMPLIANCE
# Field: legal_safe_harbor.upgrade_mechanism
deny[msg] {
    not input.contract.legal_safe_harbor.upgrade_mechanism
    msg := sprintf("SOT-V2-0120 VIOLATION: Missing required field 'legal_safe_harbor.upgrade_mechanism'", [])
}


# SOT-V2-0121: Semantic rule for 'legal_safe_harbor.yield_bearing'.
# Severity: HIGH
# Category: COMPLIANCE
# Field: legal_safe_harbor.yield_bearing
deny[msg] {
    not input.contract.legal_safe_harbor.yield_bearing
    msg := sprintf("SOT-V2-0121 VIOLATION: Missing required field 'legal_safe_harbor.yield_bearing'", [])
}


# SOT-V2-0122: Semantic rule for 'primary_utilities'.
# Severity: MEDIUM
# Category: GENERAL
# Field: primary_utilities
deny[msg] {
    not input.contract.primary_utilities
    msg := sprintf("SOT-V2-0122 VIOLATION: Missing required field 'primary_utilities'", [])
}


# SOT-V2-0123: Semantic rule for 'primary_utilities.ecosystem_rewards'.
# Severity: MEDIUM
# Category: GENERAL
# Field: primary_utilities.ecosystem_rewards
deny[msg] {
    not input.contract.primary_utilities.ecosystem_rewards
    msg := sprintf("SOT-V2-0123 VIOLATION: Missing required field 'primary_utilities.ecosystem_rewards'", [])
}


# SOT-V2-0124: Semantic rule for 'primary_utilities.ecosystem_rewards.description'.
# Severity: MEDIUM
# Category: GENERAL
# Field: primary_utilities.ecosystem_rewards.description
deny[msg] {
    not input.contract.primary_utilities.ecosystem_rewards.description
    msg := sprintf("SOT-V2-0124 VIOLATION: Missing required field 'primary_utilities.ecosystem_rewards.description'", [])
}


# SOT-V2-0125: Semantic rule for 'primary_utilities.ecosystem_rewards.distribution_method'.
# Severity: MEDIUM
# Category: GENERAL
# Field: primary_utilities.ecosystem_rewards.distribution_method
deny[msg] {
    not input.contract.primary_utilities.ecosystem_rewards.distribution_method
    msg := sprintf("SOT-V2-0125 VIOLATION: Missing required field 'primary_utilities.ecosystem_rewards.distribution_method'", [])
}


# SOT-V2-0126: Semantic rule for 'primary_utilities.ecosystem_rewards.reward_pools'.
# Severity: MEDIUM
# Category: GENERAL
# Field: primary_utilities.ecosystem_rewards.reward_pools
deny[msg] {
    not input.contract.primary_utilities.ecosystem_rewards.reward_pools
    msg := sprintf("SOT-V2-0126 VIOLATION: Missing required field 'primary_utilities.ecosystem_rewards.reward_pools'", [])
}


# SOT-V2-0127: Semantic rule for 'primary_utilities.ecosystem_rewards.reward_pools::community'.
# Severity: MEDIUM
# Category: GENERAL
# Field: primary_utilities.ecosystem_rewards.reward_pools
deny[msg] {
    not input.contract.primary_utilities.ecosystem_rewards.reward_pools
    msg := sprintf("SOT-V2-0127 VIOLATION: Missing required field 'primary_utilities.ecosystem_rewards.reward_pools'", [])
}


# SOT-V2-0128: Semantic rule for 'primary_utilities.ecosystem_rewards.reward_pools::development'.
# Severity: MEDIUM
# Category: GENERAL
# Field: primary_utilities.ecosystem_rewards.reward_pools
deny[msg] {
    not input.contract.primary_utilities.ecosystem_rewards.reward_pools
    msg := sprintf("SOT-V2-0128 VIOLATION: Missing required field 'primary_utilities.ecosystem_rewards.reward_pools'", [])
}


# SOT-V2-0129: Semantic rule for 'primary_utilities.ecosystem_rewards.reward_pools::validation'.
# Severity: MEDIUM
# Category: GENERAL
# Field: primary_utilities.ecosystem_rewards.reward_pools
deny[msg] {
    not input.contract.primary_utilities.ecosystem_rewards.reward_pools
    msg := sprintf("SOT-V2-0129 VIOLATION: Missing required field 'primary_utilities.ecosystem_rewards.reward_pools'", [])
}


# SOT-V2-0130: Semantic rule for 'primary_utilities.governance_participation'.
# Severity: MEDIUM
# Category: GENERAL
# Field: primary_utilities.governance_participation
deny[msg] {
    not input.contract.primary_utilities.governance_participation
    msg := sprintf("SOT-V2-0130 VIOLATION: Missing required field 'primary_utilities.governance_participation'", [])
}


# SOT-V2-0131: Semantic rule for 'primary_utilities.governance_participation.description'.
# Severity: MEDIUM
# Category: GENERAL
# Field: primary_utilities.governance_participation.description
deny[msg] {
    not input.contract.primary_utilities.governance_participation.description
    msg := sprintf("SOT-V2-0131 VIOLATION: Missing required field 'primary_utilities.governance_participation.description'", [])
}


# SOT-V2-0132: Semantic rule for 'primary_utilities.governance_participation.proposal_threshold'.
# Severity: HIGH
# Category: GOVERNANCE
# Field: primary_utilities.governance_participation.proposal_threshold
deny[msg] {
    not input.contract.primary_utilities.governance_participation.proposal_threshold
    msg := sprintf("SOT-V2-0132 VIOLATION: Missing required field 'primary_utilities.governance_participation.proposal_threshold'", [])
}


# SOT-V2-0133: Semantic rule for 'primary_utilities.governance_participation.voting_weight'.
# Severity: HIGH
# Category: GOVERNANCE
# Field: primary_utilities.governance_participation.voting_weight
deny[msg] {
    not input.contract.primary_utilities.governance_participation.voting_weight
    msg := sprintf("SOT-V2-0133 VIOLATION: Missing required field 'primary_utilities.governance_participation.voting_weight'", [])
}


# SOT-V2-0134: Semantic rule for 'primary_utilities.identity_verification'.
# Severity: MEDIUM
# Category: GENERAL
# Field: primary_utilities.identity_verification
deny[msg] {
    not input.contract.primary_utilities.identity_verification
    msg := sprintf("SOT-V2-0134 VIOLATION: Missing required field 'primary_utilities.identity_verification'", [])
}


# SOT-V2-0135: Semantic rule for 'primary_utilities.identity_verification.burn_clarification'.
# Severity: MEDIUM
# Category: GENERAL
# Field: primary_utilities.identity_verification.burn_clarification
deny[msg] {
    not input.contract.primary_utilities.identity_verification.burn_clarification
    msg := sprintf("SOT-V2-0135 VIOLATION: Missing required field 'primary_utilities.identity_verification.burn_clarification'", [])
}


# SOT-V2-0136: Semantic rule for 'primary_utilities.identity_verification.burn_source_note'.
# Severity: MEDIUM
# Category: GENERAL
# Field: primary_utilities.identity_verification.burn_source_note
deny[msg] {
    not input.contract.primary_utilities.identity_verification.burn_source_note
    msg := sprintf("SOT-V2-0136 VIOLATION: Missing required field 'primary_utilities.identity_verification.burn_source_note'", [])
}


# SOT-V2-0137: Semantic rule for 'primary_utilities.identity_verification.description'.
# Severity: MEDIUM
# Category: GENERAL
# Field: primary_utilities.identity_verification.description
deny[msg] {
    not input.contract.primary_utilities.identity_verification.description
    msg := sprintf("SOT-V2-0137 VIOLATION: Missing required field 'primary_utilities.identity_verification.description'", [])
}


# SOT-V2-0138: Semantic rule for 'primary_utilities.identity_verification.fee_burn_mechanism'.
# Severity: HIGH
# Category: ECONOMICS
# Field: primary_utilities.identity_verification.fee_burn_mechanism
deny[msg] {
    not input.contract.primary_utilities.identity_verification.fee_burn_mechanism
    msg := sprintf("SOT-V2-0138 VIOLATION: Missing required field 'primary_utilities.identity_verification.fee_burn_mechanism'", [])
}


# SOT-V2-0139: Semantic rule for 'primary_utilities.identity_verification.smart_contract'.
# Severity: MEDIUM
# Category: GENERAL
# Field: primary_utilities.identity_verification.smart_contract
deny[msg] {
    not input.contract.primary_utilities.identity_verification.smart_contract
    msg := sprintf("SOT-V2-0139 VIOLATION: Missing required field 'primary_utilities.identity_verification.smart_contract'", [])
}


# SOT-V2-0140: Semantic rule for 'primary_utilities.staking_utility'.
# Severity: HIGH
# Category: ECONOMICS
# Field: primary_utilities.staking_utility
deny[msg] {
    not input.contract.primary_utilities.staking_utility
    msg := sprintf("SOT-V2-0140 VIOLATION: Missing required field 'primary_utilities.staking_utility'", [])
}


# SOT-V2-0141: Semantic rule for 'primary_utilities.staking_utility.description'.
# Severity: HIGH
# Category: ECONOMICS
# Field: primary_utilities.staking_utility.description
deny[msg] {
    not input.contract.primary_utilities.staking_utility.description
    msg := sprintf("SOT-V2-0141 VIOLATION: Missing required field 'primary_utilities.staking_utility.description'", [])
}


# SOT-V2-0142: Semantic rule for 'primary_utilities.staking_utility.slashing_conditions'.
# Severity: HIGH
# Category: ECONOMICS
# Field: primary_utilities.staking_utility.slashing_conditions
deny[msg] {
    not input.contract.primary_utilities.staking_utility.slashing_conditions
    msg := sprintf("SOT-V2-0142 VIOLATION: Missing required field 'primary_utilities.staking_utility.slashing_conditions'", [])
}


# SOT-V2-0143: Semantic rule for 'primary_utilities.staking_utility.staking_rewards'.
# Severity: HIGH
# Category: ECONOMICS
# Field: primary_utilities.staking_utility.staking_rewards
deny[msg] {
    not input.contract.primary_utilities.staking_utility.staking_rewards
    msg := sprintf("SOT-V2-0143 VIOLATION: Missing required field 'primary_utilities.staking_utility.staking_rewards'", [])
}


# SOT-V2-0144: Semantic rule for 'risk_mitigation'.
# Severity: MEDIUM
# Category: GENERAL
# Field: risk_mitigation
deny[msg] {
    not input.contract.risk_mitigation
    msg := sprintf("SOT-V2-0144 VIOLATION: Missing required field 'risk_mitigation'", [])
}


# SOT-V2-0145: Semantic rule for 'risk_mitigation.clear_utility_purpose'.
# Severity: MEDIUM
# Category: GENERAL
# Field: risk_mitigation.clear_utility_purpose
deny[msg] {
    not input.contract.risk_mitigation.clear_utility_purpose
    msg := sprintf("SOT-V2-0145 VIOLATION: Missing required field 'risk_mitigation.clear_utility_purpose'", [])
}


# SOT-V2-0146: Semantic rule for 'risk_mitigation.no_fiat_pegging'.
# Severity: MEDIUM
# Category: GENERAL
# Field: risk_mitigation.no_fiat_pegging
deny[msg] {
    not input.contract.risk_mitigation.no_fiat_pegging
    msg := sprintf("SOT-V2-0146 VIOLATION: Missing required field 'risk_mitigation.no_fiat_pegging'", [])
}


# SOT-V2-0147: Semantic rule for 'risk_mitigation.no_marketing_investment'.
# Severity: MEDIUM
# Category: GENERAL
# Field: risk_mitigation.no_marketing_investment
deny[msg] {
    not input.contract.risk_mitigation.no_marketing_investment
    msg := sprintf("SOT-V2-0147 VIOLATION: Missing required field 'risk_mitigation.no_marketing_investment'", [])
}


# SOT-V2-0148: Semantic rule for 'risk_mitigation.no_redemption_mechanism'.
# Severity: MEDIUM
# Category: GENERAL
# Field: risk_mitigation.no_redemption_mechanism
deny[msg] {
    not input.contract.risk_mitigation.no_redemption_mechanism
    msg := sprintf("SOT-V2-0148 VIOLATION: Missing required field 'risk_mitigation.no_redemption_mechanism'", [])
}


# SOT-V2-0149: Semantic rule for 'risk_mitigation.no_yield_promises'.
# Severity: MEDIUM
# Category: GENERAL
# Field: risk_mitigation.no_yield_promises
deny[msg] {
    not input.contract.risk_mitigation.no_yield_promises
    msg := sprintf("SOT-V2-0149 VIOLATION: Missing required field 'risk_mitigation.no_yield_promises'", [])
}


# SOT-V2-0150: Semantic rule for 'risk_mitigation.open_source_license'.
# Severity: MEDIUM
# Category: GENERAL
# Field: risk_mitigation.open_source_license
deny[msg] {
    not input.contract.risk_mitigation.open_source_license
    msg := sprintf("SOT-V2-0150 VIOLATION: Missing required field 'risk_mitigation.open_source_license'", [])
}


# SOT-V2-0151: Semantic rule for 'secondary_utilities'.
# Severity: MEDIUM
# Category: GENERAL
# Field: secondary_utilities
deny[msg] {
    not input.contract.secondary_utilities
    msg := sprintf("SOT-V2-0151 VIOLATION: Missing required field 'secondary_utilities'", [])
}


# SOT-V2-0152: Semantic rule for 'secondary_utilities.api_access'.
# Severity: MEDIUM
# Category: GENERAL
# Field: secondary_utilities.api_access
deny[msg] {
    not input.contract.secondary_utilities.api_access
    msg := sprintf("SOT-V2-0152 VIOLATION: Missing required field 'secondary_utilities.api_access'", [])
}


# SOT-V2-0153: Semantic rule for 'secondary_utilities.data_portability'.
# Severity: MEDIUM
# Category: GENERAL
# Field: secondary_utilities.data_portability
deny[msg] {
    not input.contract.secondary_utilities.data_portability
    msg := sprintf("SOT-V2-0153 VIOLATION: Missing required field 'secondary_utilities.data_portability'", [])
}


# SOT-V2-0154: Semantic rule for 'secondary_utilities.marketplace_access'.
# Severity: MEDIUM
# Category: GENERAL
# Field: secondary_utilities.marketplace_access
deny[msg] {
    not input.contract.secondary_utilities.marketplace_access
    msg := sprintf("SOT-V2-0154 VIOLATION: Missing required field 'secondary_utilities.marketplace_access'", [])
}


# SOT-V2-0155: Semantic rule for 'secondary_utilities.premium_features'.
# Severity: MEDIUM
# Category: GENERAL
# Field: secondary_utilities.premium_features
deny[msg] {
    not input.contract.secondary_utilities.premium_features
    msg := sprintf("SOT-V2-0155 VIOLATION: Missing required field 'secondary_utilities.premium_features'", [])
}


# SOT-V2-0156: Semantic rule for 'staking_mechanics'.
# Severity: HIGH
# Category: ECONOMICS
# Field: staking_mechanics
deny[msg] {
    not input.contract.staking_mechanics
    msg := sprintf("SOT-V2-0156 VIOLATION: Missing required field 'staking_mechanics'", [])
}


# SOT-V2-0157: Semantic rule for 'staking_mechanics.discount_applies_to'.
# Severity: HIGH
# Category: ECONOMICS
# Field: staking_mechanics.discount_applies_to
deny[msg] {
    not input.contract.staking_mechanics.discount_applies_to
    msg := sprintf("SOT-V2-0157 VIOLATION: Missing required field 'staking_mechanics.discount_applies_to'", [])
}


# SOT-V2-0158: Semantic rule for 'staking_mechanics.maximum_discount'.
# Severity: HIGH
# Category: ECONOMICS
# Field: staking_mechanics.maximum_discount
deny[msg] {
    not input.contract.staking_mechanics.maximum_discount
    msg := sprintf("SOT-V2-0158 VIOLATION: Missing required field 'staking_mechanics.maximum_discount'", [])
}


# SOT-V2-0159: Semantic rule for 'staking_mechanics.minimum_stake'.
# Severity: HIGH
# Category: ECONOMICS
# Field: staking_mechanics.minimum_stake
deny[msg] {
    not input.contract.staking_mechanics.minimum_stake
    msg := sprintf("SOT-V2-0159 VIOLATION: Missing required field 'staking_mechanics.minimum_stake'", [])
}


# SOT-V2-0160: Semantic rule for 'staking_mechanics.slashing_penalty'.
# Severity: HIGH
# Category: ECONOMICS
# Field: staking_mechanics.slashing_penalty
deny[msg] {
    not input.contract.staking_mechanics.slashing_penalty
    msg := sprintf("SOT-V2-0160 VIOLATION: Missing required field 'staking_mechanics.slashing_penalty'", [])
}


# SOT-V2-0161: Semantic rule for 'staking_mechanics.system_fee_invariance'.
# Severity: HIGH
# Category: ECONOMICS
# Field: staking_mechanics.system_fee_invariance
deny[msg] {
    not input.contract.staking_mechanics.system_fee_invariance
    msg := sprintf("SOT-V2-0161 VIOLATION: Missing required field 'staking_mechanics.system_fee_invariance'", [])
}


# SOT-V2-0162: Semantic rule for 'staking_mechanics.unstaking_period'.
# Severity: HIGH
# Category: ECONOMICS
# Field: staking_mechanics.unstaking_period
deny[msg] {
    not input.contract.staking_mechanics.unstaking_period
    msg := sprintf("SOT-V2-0162 VIOLATION: Missing required field 'staking_mechanics.unstaking_period'", [])
}


# SOT-V2-0163: Semantic rule for 'supply_mechanics'.
# Severity: HIGH
# Category: ECONOMICS
# Field: supply_mechanics
deny[msg] {
    not input.contract.supply_mechanics
    msg := sprintf("SOT-V2-0163 VIOLATION: Missing required field 'supply_mechanics'", [])
}


# SOT-V2-0164: Semantic rule for 'supply_mechanics.circulation_controls'.
# Severity: HIGH
# Category: ECONOMICS
# Field: supply_mechanics.circulation_controls
deny[msg] {
    not input.contract.supply_mechanics.circulation_controls
    msg := sprintf("SOT-V2-0164 VIOLATION: Missing required field 'supply_mechanics.circulation_controls'", [])
}


# SOT-V2-0165: Semantic rule for 'supply_mechanics.circulation_controls.max_annual_inflation'.
# Severity: HIGH
# Category: ECONOMICS
# Field: supply_mechanics.circulation_controls.max_annual_inflation
deny[msg] {
    not input.contract.supply_mechanics.circulation_controls.max_annual_inflation
    msg := sprintf("SOT-V2-0165 VIOLATION: Missing required field 'supply_mechanics.circulation_controls.max_annual_inflation'", [])
}


# SOT-V2-0166: Semantic rule for 'supply_mechanics.circulation_controls.partnership_unlock'.
# Severity: HIGH
# Category: ECONOMICS
# Field: supply_mechanics.circulation_controls.partnership_unlock
deny[msg] {
    not input.contract.supply_mechanics.circulation_controls.partnership_unlock
    msg := sprintf("SOT-V2-0166 VIOLATION: Missing required field 'supply_mechanics.circulation_controls.partnership_unlock'", [])
}


# SOT-V2-0167: Semantic rule for 'supply_mechanics.circulation_controls.reserve_governance'.
# Severity: HIGH
# Category: ECONOMICS
# Field: supply_mechanics.circulation_controls.reserve_governance
deny[msg] {
    not input.contract.supply_mechanics.circulation_controls.reserve_governance
    msg := sprintf("SOT-V2-0167 VIOLATION: Missing required field 'supply_mechanics.circulation_controls.reserve_governance'", [])
}


# SOT-V2-0168: Semantic rule for 'supply_mechanics.circulation_controls.team_vesting_schedule'.
# Severity: HIGH
# Category: ECONOMICS
# Field: supply_mechanics.circulation_controls.team_vesting_schedule
deny[msg] {
    not input.contract.supply_mechanics.circulation_controls.team_vesting_schedule
    msg := sprintf("SOT-V2-0168 VIOLATION: Missing required field 'supply_mechanics.circulation_controls.team_vesting_schedule'", [])
}


# SOT-V2-0169: Semantic rule for 'supply_mechanics.deflationary_mechanisms'.
# Severity: HIGH
# Category: ECONOMICS
# Field: supply_mechanics.deflationary_mechanisms
deny[msg] {
    not input.contract.supply_mechanics.deflationary_mechanisms
    msg := sprintf("SOT-V2-0169 VIOLATION: Missing required field 'supply_mechanics.deflationary_mechanisms'", [])
}


# SOT-V2-0170: Semantic rule for 'supply_mechanics.deflationary_mechanisms.governance_burning'.
# Severity: HIGH
# Category: ECONOMICS
# Field: supply_mechanics.deflationary_mechanisms.governance_burning
deny[msg] {
    not input.contract.supply_mechanics.deflationary_mechanisms.governance_burning
    msg := sprintf("SOT-V2-0170 VIOLATION: Missing required field 'supply_mechanics.deflationary_mechanisms.governance_burning'", [])
}


# SOT-V2-0171: Semantic rule for 'supply_mechanics.deflationary_mechanisms.staking_slashing'.
# Severity: HIGH
# Category: ECONOMICS
# Field: supply_mechanics.deflationary_mechanisms.staking_slashing
deny[msg] {
    not input.contract.supply_mechanics.deflationary_mechanisms.staking_slashing
    msg := sprintf("SOT-V2-0171 VIOLATION: Missing required field 'supply_mechanics.deflationary_mechanisms.staking_slashing'", [])
}


# SOT-V2-0172: Semantic rule for 'supply_mechanics.initial_distribution'.
# Severity: HIGH
# Category: ECONOMICS
# Field: supply_mechanics.initial_distribution
deny[msg] {
    not input.contract.supply_mechanics.initial_distribution
    msg := sprintf("SOT-V2-0172 VIOLATION: Missing required field 'supply_mechanics.initial_distribution'", [])
}


# SOT-V2-0173: Semantic rule for 'supply_mechanics.initial_distribution.community_rewards'.
# Severity: HIGH
# Category: ECONOMICS
# Field: supply_mechanics.initial_distribution.community_rewards
deny[msg] {
    not input.contract.supply_mechanics.initial_distribution.community_rewards
    msg := sprintf("SOT-V2-0173 VIOLATION: Missing required field 'supply_mechanics.initial_distribution.community_rewards'", [])
}


# SOT-V2-0174: Semantic rule for 'supply_mechanics.initial_distribution.ecosystem_development'.
# Severity: HIGH
# Category: ECONOMICS
# Field: supply_mechanics.initial_distribution.ecosystem_development
deny[msg] {
    not input.contract.supply_mechanics.initial_distribution.ecosystem_development
    msg := sprintf("SOT-V2-0174 VIOLATION: Missing required field 'supply_mechanics.initial_distribution.ecosystem_development'", [])
}


# SOT-V2-0175: Semantic rule for 'supply_mechanics.initial_distribution.partnerships'.
# Severity: HIGH
# Category: ECONOMICS
# Field: supply_mechanics.initial_distribution.partnerships
deny[msg] {
    not input.contract.supply_mechanics.initial_distribution.partnerships
    msg := sprintf("SOT-V2-0175 VIOLATION: Missing required field 'supply_mechanics.initial_distribution.partnerships'", [])
}


# SOT-V2-0176: Semantic rule for 'supply_mechanics.initial_distribution.reserve_fund'.
# Severity: HIGH
# Category: ECONOMICS
# Field: supply_mechanics.initial_distribution.reserve_fund
deny[msg] {
    not input.contract.supply_mechanics.initial_distribution.reserve_fund
    msg := sprintf("SOT-V2-0176 VIOLATION: Missing required field 'supply_mechanics.initial_distribution.reserve_fund'", [])
}


# SOT-V2-0177: Semantic rule for 'supply_mechanics.initial_distribution.team_development'.
# Severity: HIGH
# Category: ECONOMICS
# Field: supply_mechanics.initial_distribution.team_development
deny[msg] {
    not input.contract.supply_mechanics.initial_distribution.team_development
    msg := sprintf("SOT-V2-0177 VIOLATION: Missing required field 'supply_mechanics.initial_distribution.team_development'", [])
}


# SOT-V2-0178: Semantic rule for 'supply_mechanics.total_supply'.
# Severity: HIGH
# Category: ECONOMICS
# Field: supply_mechanics.total_supply
deny[msg] {
    not input.contract.supply_mechanics.total_supply
    msg := sprintf("SOT-V2-0178 VIOLATION: Missing required field 'supply_mechanics.total_supply'", [])
}


# SOT-V2-0179: Semantic rule for 'technical_specification'.
# Severity: MEDIUM
# Category: GENERAL
# Field: technical_specification
deny[msg] {
    not input.contract.technical_specification
    msg := sprintf("SOT-V2-0179 VIOLATION: Missing required field 'technical_specification'", [])
}


# SOT-V2-0180: Semantic rule for 'technical_specification.blockchain'.
# Severity: MEDIUM
# Category: GENERAL
# Field: technical_specification.blockchain
deny[msg] {
    not input.contract.technical_specification.blockchain
    msg := sprintf("SOT-V2-0180 VIOLATION: Missing required field 'technical_specification.blockchain'", [])
}


# SOT-V2-0181: Semantic rule for 'technical_specification.custody_model'.
# Severity: MEDIUM
# Category: GENERAL
# Field: technical_specification.custody_model
deny[msg] {
    not input.contract.technical_specification.custody_model
    msg := sprintf("SOT-V2-0181 VIOLATION: Missing required field 'technical_specification.custody_model'", [])
}


# SOT-V2-0182: Semantic rule for 'technical_specification.smart_contract_automation'.
# Severity: MEDIUM
# Category: GENERAL
# Field: technical_specification.smart_contract_automation
deny[msg] {
    not input.contract.technical_specification.smart_contract_automation
    msg := sprintf("SOT-V2-0182 VIOLATION: Missing required field 'technical_specification.smart_contract_automation'", [])
}


# SOT-V2-0183: Semantic rule for 'technical_specification.standard'.
# Severity: MEDIUM
# Category: GENERAL
# Field: technical_specification.standard
deny[msg] {
    not input.contract.technical_specification.standard
    msg := sprintf("SOT-V2-0183 VIOLATION: Missing required field 'technical_specification.standard'", [])
}


# SOT-V2-0184: Semantic rule for 'technical_specification.supply_model'.
# Severity: HIGH
# Category: ECONOMICS
# Field: technical_specification.supply_model
deny[msg] {
    not input.contract.technical_specification.supply_model
    msg := sprintf("SOT-V2-0184 VIOLATION: Missing required field 'technical_specification.supply_model'", [])
}


# SOT-V2-0185: Semantic rule for 'token_definition'.
# Severity: MEDIUM
# Category: GENERAL
# Field: token_definition
deny[msg] {
    not input.contract.token_definition
    msg := sprintf("SOT-V2-0185 VIOLATION: Missing required field 'token_definition'", [])
}


# SOT-V2-0186: Semantic rule for 'token_definition.explicit_exclusions'.
# Severity: MEDIUM
# Category: GENERAL
# Field: token_definition.explicit_exclusions
deny[msg] {
    not input.contract.token_definition.explicit_exclusions
    msg := sprintf("SOT-V2-0186 VIOLATION: Missing required field 'token_definition.explicit_exclusions'", [])
}


# SOT-V2-0187: Semantic rule for 'token_definition.legal_position'.
# Severity: HIGH
# Category: COMPLIANCE
# Field: token_definition.legal_position
deny[msg] {
    not input.contract.token_definition.legal_position
    msg := sprintf("SOT-V2-0187 VIOLATION: Missing required field 'token_definition.legal_position'", [])
}


# SOT-V2-0188: Semantic rule for 'token_definition.purpose'.
# Severity: MEDIUM
# Category: GENERAL
# Field: token_definition.purpose
deny[msg] {
    not input.contract.token_definition.purpose
    msg := sprintf("SOT-V2-0188 VIOLATION: Missing required field 'token_definition.purpose'", [])
}


# SOT-V2-0189: Semantic rule for 'version'.
# Severity: INFO
# Category: METADATA
# Field: version
deny[msg] {
    not input.contract.version
    msg := sprintf("SOT-V2-0189 VIOLATION: Missing required field 'version'", [])
}
