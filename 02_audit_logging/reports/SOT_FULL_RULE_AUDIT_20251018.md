# SoT Full Rule Extraction - Audit Report
**Date:** 2025-10-18
**Total Rules:** 1650

## Rule Inventory by Source

### SSID_structure_level3_part1_MAX.md
**Rules:** 625

| Priority | Count |
|----------|-------|
| MUST | 26 |
| SHOULD | 587 |
| HAVE | 12 |

### SSID_structure_level3_part2_MAX.md
**Rules:** 589

| Priority | Count |
|----------|-------|
| MUST | 33 |
| SHOULD | 529 |
| HAVE | 27 |

### SSID_structure_level3_part3_MAX.md
**Rules:** 308

| Priority | Count |
|----------|-------|
| MUST | 27 |
| SHOULD | 277 |
| HAVE | 4 |

### ssid_master_definition_corrected_v1.1.1.md
**Rules:** 128

| Priority | Count |
|----------|-------|
| MUST | 9 |
| SHOULD | 109 |
| HAVE | 10 |

## Complete Rule List

| Rule ID | Title | Priority | Category | Source Line |
|---------|-------|----------|----------|-------------|
| SOT-001 | version Validation | should | token_architecture_legal_safe_harbor | SSID_structure_level3_part1_MAX.md:30 |
| SOT-002 | date Validation | should | token_architecture_legal_safe_harbor | SSID_structure_level3_part1_MAX.md:30 |
| SOT-003 | deprecated Validation | should | token_architecture_legal_safe_harbor | SSID_structure_level3_part1_MAX.md:30 |
| SOT-004 | classification Validation | should | token_architecture_legal_safe_harbor | SSID_structure_level3_part1_MAX.md:30 |
| SOT-005 | token_definition.purpose[0] Validation | should | token_architecture_legal_safe_harbor | SSID_structure_level3_part1_MAX.md:30 |
| SOT-006 | token_definition.purpose[1] Validation | should | token_architecture_legal_safe_harbor | SSID_structure_level3_part1_MAX.md:30 |
| SOT-007 | token_definition.purpose[2] Validation | should | token_architecture_legal_safe_harbor | SSID_structure_level3_part1_MAX.md:30 |
| SOT-008 | token_definition.explicit_exclusions[0] Validation | should | token_architecture_legal_safe_harbor | SSID_structure_level3_part1_MAX.md:30 |
| SOT-009 | token_definition.explicit_exclusions[1] Validation | should | token_architecture_legal_safe_harbor | SSID_structure_level3_part1_MAX.md:30 |
| SOT-010 | token_definition.explicit_exclusions[2] Validation | should | token_architecture_legal_safe_harbor | SSID_structure_level3_part1_MAX.md:30 |
| SOT-011 | token_definition.explicit_exclusions[3] Validation | should | token_architecture_legal_safe_harbor | SSID_structure_level3_part1_MAX.md:30 |
| SOT-012 | token_definition.explicit_exclusions[4] Validation | should | token_architecture_legal_safe_harbor | SSID_structure_level3_part1_MAX.md:30 |
| SOT-013 | token_definition.legal_position Validation | should | token_architecture_legal_safe_harbor | SSID_structure_level3_part1_MAX.md:30 |
| SOT-014 | technical_specification.blockchain Validation | should | token_architecture_legal_safe_harbor | SSID_structure_level3_part1_MAX.md:30 |
| SOT-015 | technical_specification.standard Validation | should | token_architecture_legal_safe_harbor | SSID_structure_level3_part1_MAX.md:30 |
| SOT-016 | technical_specification.supply_model Validation | should | token_architecture_legal_safe_harbor | SSID_structure_level3_part1_MAX.md:30 |
| SOT-017 | technical_specification.custody_model Validation | should | token_architecture_legal_safe_harbor | SSID_structure_level3_part1_MAX.md:30 |
| SOT-018 | technical_specification.smart_contract_automation ... | should | token_architecture_legal_safe_harbor | SSID_structure_level3_part1_MAX.md:30 |
| SOT-019 | fee_structure.scope Validation | should | token_architecture_legal_safe_harbor | SSID_structure_level3_part1_MAX.md:30 |
| SOT-020 | fee_structure.total_fee Validation | should | token_architecture_legal_safe_harbor | SSID_structure_level3_part1_MAX.md:30 |
| SOT-021 | fee_structure.allocation Validation | should | token_architecture_legal_safe_harbor | SSID_structure_level3_part1_MAX.md:30 |
| SOT-022 | fee_structure.burn_from_system_fee Validation | should | token_architecture_legal_safe_harbor | SSID_structure_level3_part1_MAX.md:30 |
| SOT-023 | fee_structure.fee_collection Validation | should | token_architecture_legal_safe_harbor | SSID_structure_level3_part1_MAX.md:30 |
| SOT-024 | fee_structure.no_manual_intervention Validation | should | token_architecture_legal_safe_harbor | SSID_structure_level3_part1_MAX.md:30 |
| SOT-025 | legal_safe_harbor.security_token Validation | should | token_architecture_legal_safe_harbor | SSID_structure_level3_part1_MAX.md:30 |
| SOT-026 | legal_safe_harbor.e_money_token Validation | should | token_architecture_legal_safe_harbor | SSID_structure_level3_part1_MAX.md:30 |
| SOT-027 | legal_safe_harbor.stablecoin Validation | should | token_architecture_legal_safe_harbor | SSID_structure_level3_part1_MAX.md:30 |
| SOT-028 | legal_safe_harbor.yield_bearing Validation | should | token_architecture_legal_safe_harbor | SSID_structure_level3_part1_MAX.md:30 |
| SOT-029 | legal_safe_harbor.redemption_rights Validation | should | token_architecture_legal_safe_harbor | SSID_structure_level3_part1_MAX.md:30 |
| SOT-030 | legal_safe_harbor.passive_income Validation | should | token_architecture_legal_safe_harbor | SSID_structure_level3_part1_MAX.md:30 |
| SOT-031 | legal_safe_harbor.investment_contract Validation | should | token_architecture_legal_safe_harbor | SSID_structure_level3_part1_MAX.md:30 |
| SOT-032 | legal_safe_harbor.admin_controls Validation | should | token_architecture_legal_safe_harbor | SSID_structure_level3_part1_MAX.md:30 |
| SOT-033 | legal_safe_harbor.upgrade_mechanism Validation | should | token_architecture_legal_safe_harbor | SSID_structure_level3_part1_MAX.md:30 |
| SOT-034 | business_model.role Validation | should | token_architecture_legal_safe_harbor | SSID_structure_level3_part1_MAX.md:30 |
| SOT-035 | business_model.not_role[0] Validation | should | token_architecture_legal_safe_harbor | SSID_structure_level3_part1_MAX.md:30 |
| SOT-036 | business_model.not_role[1] Validation | should | token_architecture_legal_safe_harbor | SSID_structure_level3_part1_MAX.md:30 |
| SOT-037 | business_model.not_role[2] Validation | should | token_architecture_legal_safe_harbor | SSID_structure_level3_part1_MAX.md:30 |
| SOT-038 | business_model.not_role[3] Validation | should | token_architecture_legal_safe_harbor | SSID_structure_level3_part1_MAX.md:30 |
| SOT-039 | business_model.user_interactions Validation | should | token_architecture_legal_safe_harbor | SSID_structure_level3_part1_MAX.md:30 |
| SOT-040 | business_model.kyc_responsibility Validation | should | token_architecture_legal_safe_harbor | SSID_structure_level3_part1_MAX.md:30 |
| SOT-041 | business_model.data_custody Validation | should | token_architecture_legal_safe_harbor | SSID_structure_level3_part1_MAX.md:30 |
| SOT-042 | governance_framework.dao_ready Validation | should | token_architecture_legal_safe_harbor | SSID_structure_level3_part1_MAX.md:30 |
| SOT-043 | governance_framework.voting_mechanism Validation | should | token_architecture_legal_safe_harbor | SSID_structure_level3_part1_MAX.md:30 |
| SOT-044 | governance_framework.proposal_system Validation | should | token_architecture_legal_safe_harbor | SSID_structure_level3_part1_MAX.md:30 |
| SOT-045 | governance_framework.upgrade_authority Validation | should | token_architecture_legal_safe_harbor | SSID_structure_level3_part1_MAX.md:30 |
| SOT-046 | governance_framework.emergency_procedures Validati... | should | token_architecture_legal_safe_harbor | SSID_structure_level3_part1_MAX.md:30 |
| SOT-047 | governance_framework.reference Validation | have | token_architecture_legal_safe_harbor | SSID_structure_level3_part1_MAX.md:30 |
| SOT-048 | jurisdictional_compliance.reference Validation | should | token_architecture_legal_safe_harbor | SSID_structure_level3_part1_MAX.md:30 |
| SOT-049 | jurisdictional_compliance.blacklist_jurisdictions[... | should | token_architecture_legal_safe_harbor | SSID_structure_level3_part1_MAX.md:30 |
| SOT-050 | jurisdictional_compliance.blacklist_jurisdictions[... | should | token_architecture_legal_safe_harbor | SSID_structure_level3_part1_MAX.md:30 |
| SOT-051 | jurisdictional_compliance.blacklist_jurisdictions[... | should | token_architecture_legal_safe_harbor | SSID_structure_level3_part1_MAX.md:30 |
| SOT-052 | jurisdictional_compliance.blacklist_jurisdictions[... | should | token_architecture_legal_safe_harbor | SSID_structure_level3_part1_MAX.md:30 |
| SOT-053 | jurisdictional_compliance.excluded_entities[0] Val... | should | token_architecture_legal_safe_harbor | SSID_structure_level3_part1_MAX.md:30 |
| SOT-054 | jurisdictional_compliance.excluded_entities[1] Val... | should | token_architecture_legal_safe_harbor | SSID_structure_level3_part1_MAX.md:30 |
| SOT-055 | jurisdictional_compliance.excluded_entities[2] Val... | should | token_architecture_legal_safe_harbor | SSID_structure_level3_part1_MAX.md:30 |
| SOT-056 | jurisdictional_compliance.excluded_markets[0] Vali... | should | token_architecture_legal_safe_harbor | SSID_structure_level3_part1_MAX.md:30 |
| SOT-057 | jurisdictional_compliance.excluded_markets[1] Vali... | should | token_architecture_legal_safe_harbor | SSID_structure_level3_part1_MAX.md:30 |
| SOT-058 | jurisdictional_compliance.excluded_markets[2] Vali... | should | token_architecture_legal_safe_harbor | SSID_structure_level3_part1_MAX.md:30 |
| SOT-059 | jurisdictional_compliance.compliance_basis Validat... | should | token_architecture_legal_safe_harbor | SSID_structure_level3_part1_MAX.md:30 |
| SOT-060 | jurisdictional_compliance.regulatory_exemptions Va... | should | token_architecture_legal_safe_harbor | SSID_structure_level3_part1_MAX.md:30 |
| SOT-061 | risk_mitigation.no_fiat_pegging Validation | should | token_architecture_legal_safe_harbor | SSID_structure_level3_part1_MAX.md:30 |
| SOT-062 | risk_mitigation.no_redemption_mechanism Validation | should | token_architecture_legal_safe_harbor | SSID_structure_level3_part1_MAX.md:30 |
| SOT-063 | risk_mitigation.no_yield_promises Validation | should | token_architecture_legal_safe_harbor | SSID_structure_level3_part1_MAX.md:30 |
| SOT-064 | risk_mitigation.no_marketing_investment Validation | should | token_architecture_legal_safe_harbor | SSID_structure_level3_part1_MAX.md:30 |
| SOT-065 | risk_mitigation.clear_utility_purpose Validation | should | token_architecture_legal_safe_harbor | SSID_structure_level3_part1_MAX.md:30 |
| SOT-066 | risk_mitigation.open_source_license Validation | should | token_architecture_legal_safe_harbor | SSID_structure_level3_part1_MAX.md:30 |
| SOT-067 | version Validation | should | token_utility_framework | SSID_structure_level3_part1_MAX.md:104 |
| SOT-068 | date Validation | should | token_utility_framework | SSID_structure_level3_part1_MAX.md:104 |
| SOT-069 | deprecated Validation | should | token_utility_framework | SSID_structure_level3_part1_MAX.md:104 |
| SOT-070 | primary_utilities.identity_verification.descriptio... | should | token_utility_framework | SSID_structure_level3_part1_MAX.md:104 |
| SOT-071 | primary_utilities.identity_verification.smart_cont... | should | token_utility_framework | SSID_structure_level3_part1_MAX.md:104 |
| SOT-072 | primary_utilities.identity_verification.fee_burn_m... | should | token_utility_framework | SSID_structure_level3_part1_MAX.md:104 |
| SOT-073 | primary_utilities.identity_verification.burn_sourc... | should | token_utility_framework | SSID_structure_level3_part1_MAX.md:104 |
| SOT-074 | primary_utilities.identity_verification.burn_clari... | must | token_utility_framework | SSID_structure_level3_part1_MAX.md:104 |
| SOT-075 | primary_utilities.governance_participation.descrip... | should | token_utility_framework | SSID_structure_level3_part1_MAX.md:104 |
| SOT-076 | primary_utilities.governance_participation.voting_... | should | token_utility_framework | SSID_structure_level3_part1_MAX.md:104 |
| SOT-077 | primary_utilities.governance_participation.proposa... | should | token_utility_framework | SSID_structure_level3_part1_MAX.md:104 |
| SOT-078 | primary_utilities.ecosystem_rewards.description Va... | should | token_utility_framework | SSID_structure_level3_part1_MAX.md:104 |
| SOT-079 | primary_utilities.ecosystem_rewards.distribution_m... | should | token_utility_framework | SSID_structure_level3_part1_MAX.md:104 |
| SOT-080 | primary_utilities.ecosystem_rewards.reward_pools[0... | should | token_utility_framework | SSID_structure_level3_part1_MAX.md:104 |
| SOT-081 | primary_utilities.ecosystem_rewards.reward_pools[1... | should | token_utility_framework | SSID_structure_level3_part1_MAX.md:104 |
| SOT-082 | primary_utilities.ecosystem_rewards.reward_pools[2... | should | token_utility_framework | SSID_structure_level3_part1_MAX.md:104 |
| SOT-083 | primary_utilities.staking_utility.description Vali... | should | token_utility_framework | SSID_structure_level3_part1_MAX.md:104 |
| SOT-084 | primary_utilities.staking_utility.staking_rewards ... | should | token_utility_framework | SSID_structure_level3_part1_MAX.md:104 |
| SOT-085 | primary_utilities.staking_utility.slashing_conditi... | should | token_utility_framework | SSID_structure_level3_part1_MAX.md:104 |
| SOT-086 | compliance_utilities.audit_payments Validation | should | token_utility_framework | SSID_structure_level3_part1_MAX.md:104 |
| SOT-087 | compliance_utilities.regulatory_reporting Validati... | should | token_utility_framework | SSID_structure_level3_part1_MAX.md:104 |
| SOT-088 | compliance_utilities.legal_attestations Validation | should | token_utility_framework | SSID_structure_level3_part1_MAX.md:104 |
| SOT-089 | secondary_utilities.marketplace_access Validation | should | token_utility_framework | SSID_structure_level3_part1_MAX.md:104 |
| SOT-090 | secondary_utilities.premium_features Validation | should | token_utility_framework | SSID_structure_level3_part1_MAX.md:104 |
| SOT-091 | secondary_utilities.api_access Validation | should | token_utility_framework | SSID_structure_level3_part1_MAX.md:104 |
| SOT-092 | secondary_utilities.data_portability Validation | should | token_utility_framework | SSID_structure_level3_part1_MAX.md:104 |
| SOT-093 | version Validation | should | token_economics_distribution | SSID_structure_level3_part1_MAX.md:146 |
| SOT-094 | date Validation | should | token_economics_distribution | SSID_structure_level3_part1_MAX.md:146 |
| SOT-095 | deprecated Validation | should | token_economics_distribution | SSID_structure_level3_part1_MAX.md:146 |
| SOT-096 | supply_mechanics.total_supply Validation | should | token_economics_distribution | SSID_structure_level3_part1_MAX.md:146 |
| SOT-097 | supply_mechanics.initial_distribution.ecosystem_de... | should | token_economics_distribution | SSID_structure_level3_part1_MAX.md:146 |
| SOT-098 | supply_mechanics.initial_distribution.community_re... | should | token_economics_distribution | SSID_structure_level3_part1_MAX.md:146 |
| SOT-099 | supply_mechanics.initial_distribution.team_develop... | should | token_economics_distribution | SSID_structure_level3_part1_MAX.md:146 |
| SOT-100 | supply_mechanics.initial_distribution.partnerships... | should | token_economics_distribution | SSID_structure_level3_part1_MAX.md:146 |
| SOT-1000 | controls.enterprise_badge_validation.description V... | should | badge_integrity_framework_enterprise | SSID_structure_level3_part2_MAX.md:864 |
| SOT-1001 | controls.enterprise_badge_validation.script Valida... | should | badge_integrity_framework_enterprise | SSID_structure_level3_part2_MAX.md:864 |
| SOT-1002 | controls.enterprise_badge_validation.script_deprec... | should | badge_integrity_framework_enterprise | SSID_structure_level3_part2_MAX.md:864 |
| SOT-1003 | controls.enterprise_badge_validation.frequency Val... | should | badge_integrity_framework_enterprise | SSID_structure_level3_part2_MAX.md:864 |
| SOT-1004 | controls.enterprise_badge_validation.documentation... | must | badge_integrity_framework_enterprise | SSID_structure_level3_part2_MAX.md:864 |
| SOT-1005 | controls.enterprise_badge_validation.business_revi... | should | badge_integrity_framework_enterprise | SSID_structure_level3_part2_MAX.md:864 |
| SOT-1006 | controls.enterprise_badge_validation.source_valida... | should | badge_integrity_framework_enterprise | SSID_structure_level3_part2_MAX.md:864 |
| SOT-1007 | controls.enterprise_badge_validation.formula_verif... | should | badge_integrity_framework_enterprise | SSID_structure_level3_part2_MAX.md:864 |
| SOT-1008 | dependency_graph_generation.enabled Validation | should | badge_integrity_framework_enterprise | SSID_structure_level3_part2_MAX.md:864 |
| SOT-1009 | dependency_graph_generation.script Validation | should | badge_integrity_framework_enterprise | SSID_structure_level3_part2_MAX.md:864 |
| SOT-101 | supply_mechanics.initial_distribution.reserve_fund... | should | token_economics_distribution | SSID_structure_level3_part1_MAX.md:146 |
| SOT-1010 | dependency_graph_generation.output_directory Valid... | should | badge_integrity_framework_enterprise | SSID_structure_level3_part2_MAX.md:864 |
| SOT-1011 | dependency_graph_generation.formats.dot Validation | should | badge_integrity_framework_enterprise | SSID_structure_level3_part2_MAX.md:864 |
| SOT-1012 | dependency_graph_generation.formats.json Validatio... | should | badge_integrity_framework_enterprise | SSID_structure_level3_part2_MAX.md:864 |
| SOT-1013 | dependency_graph_generation.formats.svg Validation | should | badge_integrity_framework_enterprise | SSID_structure_level3_part2_MAX.md:864 |
| SOT-1014 | dependency_graph_generation.formats.enterprise_das... | should | badge_integrity_framework_enterprise | SSID_structure_level3_part2_MAX.md:864 |
| SOT-1015 | dependency_graph_generation.formats.confidential_m... | should | badge_integrity_framework_enterprise | SSID_structure_level3_part2_MAX.md:864 |
| SOT-1016 | dependency_graph_generation.update_frequency Valid... | should | badge_integrity_framework_enterprise | SSID_structure_level3_part2_MAX.md:864 |
| SOT-1017 | dependency_graph_generation.ci_integration Validat... | should | badge_integrity_framework_enterprise | SSID_structure_level3_part2_MAX.md:864 |
| SOT-1018 | dependency_graph_generation.classification Validat... | should | badge_integrity_framework_enterprise | SSID_structure_level3_part2_MAX.md:864 |
| SOT-1019 | external_review_cycle.frequency Validation | should | badge_integrity_framework_enterprise | SSID_structure_level3_part2_MAX.md:864 |
| SOT-102 | supply_mechanics.deflationary_mechanisms.governanc... | should | token_economics_distribution | SSID_structure_level3_part1_MAX.md:146 |
| SOT-1020 | external_review_cycle.last_review Validation | should | badge_integrity_framework_enterprise | SSID_structure_level3_part2_MAX.md:864 |
| SOT-1021 | external_review_cycle.next_review Validation | should | badge_integrity_framework_enterprise | SSID_structure_level3_part2_MAX.md:864 |
| SOT-1022 | external_review_cycle.internal_review Validation | should | badge_integrity_framework_enterprise | SSID_structure_level3_part2_MAX.md:864 |
| SOT-1023 | external_review_cycle.reviewer_requirements[0] Val... | should | badge_integrity_framework_enterprise | SSID_structure_level3_part2_MAX.md:864 |
| SOT-1024 | external_review_cycle.reviewer_requirements[1] Val... | should | badge_integrity_framework_enterprise | SSID_structure_level3_part2_MAX.md:864 |
| SOT-1025 | external_review_cycle.reviewer_requirements[2] Val... | should | badge_integrity_framework_enterprise | SSID_structure_level3_part2_MAX.md:864 |
| SOT-1026 | external_review_cycle.reviewer_requirements[3] Val... | should | badge_integrity_framework_enterprise | SSID_structure_level3_part2_MAX.md:864 |
| SOT-1027 | external_review_cycle.reviewer_requirements[4] Val... | should | badge_integrity_framework_enterprise | SSID_structure_level3_part2_MAX.md:864 |
| SOT-1028 | external_review_cycle.review_scope[0] Validation | should | badge_integrity_framework_enterprise | SSID_structure_level3_part2_MAX.md:864 |
| SOT-1029 | external_review_cycle.review_scope[1] Validation | should | badge_integrity_framework_enterprise | SSID_structure_level3_part2_MAX.md:864 |
| SOT-103 | supply_mechanics.deflationary_mechanisms.staking_s... | should | token_economics_distribution | SSID_structure_level3_part1_MAX.md:146 |
| SOT-1030 | external_review_cycle.review_scope[2] Validation | should | badge_integrity_framework_enterprise | SSID_structure_level3_part2_MAX.md:864 |
| SOT-1031 | external_review_cycle.review_scope[3] Validation | should | badge_integrity_framework_enterprise | SSID_structure_level3_part2_MAX.md:864 |
| SOT-1032 | external_review_cycle.review_scope[4] Validation | should | badge_integrity_framework_enterprise | SSID_structure_level3_part2_MAX.md:864 |
| SOT-1033 | external_review_cycle.review_scope[5] Validation | should | badge_integrity_framework_enterprise | SSID_structure_level3_part2_MAX.md:864 |
| SOT-1034 | external_review_cycle.review_scope[6] Validation | should | badge_integrity_framework_enterprise | SSID_structure_level3_part2_MAX.md:864 |
| SOT-1035 | external_review_cycle.review_scope[7] Validation | should | badge_integrity_framework_enterprise | SSID_structure_level3_part2_MAX.md:864 |
| SOT-1036 | name Validation | should | review_ci_cd_integration_enterprise | SSID_structure_level3_part2_MAX.md:1019 |
| SOT-1037 | True[0] Validation | should | review_ci_cd_integration_enterprise | SSID_structure_level3_part2_MAX.md:1019 |
| SOT-1038 | True[1] Validation | should | review_ci_cd_integration_enterprise | SSID_structure_level3_part2_MAX.md:1019 |
| SOT-1039 | jobs.check_review_status.runs-on Validation | should | review_ci_cd_integration_enterprise | SSID_structure_level3_part2_MAX.md:1019 |
| SOT-104 | supply_mechanics.circulation_controls.max_annual_i... | should | token_economics_distribution | SSID_structure_level3_part1_MAX.md:146 |
| SOT-1040 | jobs.check_review_status.steps.name Validation | should | review_ci_cd_integration_enterprise | SSID_structure_level3_part2_MAX.md:1019 |
| SOT-1041 | jobs.check_review_status.steps.run Validation | must | review_ci_cd_integration_enterprise | SSID_structure_level3_part2_MAX.md:1019 |
| SOT-1042 | jobs.check_review_status.steps.name Validation | should | review_ci_cd_integration_enterprise | SSID_structure_level3_part2_MAX.md:1019 |
| SOT-1043 | jobs.check_review_status.steps.run Validation | should | review_ci_cd_integration_enterprise | SSID_structure_level3_part2_MAX.md:1019 |
| SOT-1044 | jobs.check_review_status.steps.name Validation | should | review_ci_cd_integration_enterprise | SSID_structure_level3_part2_MAX.md:1019 |
| SOT-1045 | jobs.check_review_status.steps.run Validation | should | review_ci_cd_integration_enterprise | SSID_structure_level3_part2_MAX.md:1019 |
| SOT-1046 | root_depth_matrix.01_ai_layer.max_depth Validation | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1047 | root_depth_matrix.01_ai_layer.level_3[0] Validatio... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1048 | root_depth_matrix.01_ai_layer.level_3[1] Validatio... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1049 | root_depth_matrix.01_ai_layer.level_3[2] Validatio... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-105 | supply_mechanics.circulation_controls.team_vesting... | should | token_economics_distribution | SSID_structure_level3_part1_MAX.md:146 |
| SOT-1050 | root_depth_matrix.01_ai_layer.level_3[3] Validatio... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1051 | root_depth_matrix.01_ai_layer.level_3[4] Validatio... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1052 | root_depth_matrix.02_audit_logging.max_depth Valid... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1053 | root_depth_matrix.02_audit_logging.level_3[0] Vali... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1054 | root_depth_matrix.02_audit_logging.level_3[1] Vali... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1055 | root_depth_matrix.02_audit_logging.level_3[2] Vali... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1056 | root_depth_matrix.02_audit_logging.level_3[3] Vali... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1057 | root_depth_matrix.02_audit_logging.level_3[4] Vali... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1058 | root_depth_matrix.02_audit_logging.level_3[5] Vali... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1059 | root_depth_matrix.02_audit_logging.level_4[0] Vali... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-106 | supply_mechanics.circulation_controls.partnership_... | should | token_economics_distribution | SSID_structure_level3_part1_MAX.md:146 |
| SOT-1060 | root_depth_matrix.02_audit_logging.level_4[1] Vali... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1061 | root_depth_matrix.02_audit_logging.level_4[2] Vali... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1062 | root_depth_matrix.02_audit_logging.level_5[0] Vali... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1063 | root_depth_matrix.02_audit_logging.level_5[1] Vali... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1064 | root_depth_matrix.03_core.max_depth Validation | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1065 | root_depth_matrix.03_core.level_3[0] Validation | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1066 | root_depth_matrix.03_core.level_3[1] Validation | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1067 | root_depth_matrix.03_core.level_3[2] Validation | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1068 | root_depth_matrix.03_core.level_3[3] Validation | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1069 | root_depth_matrix.03_core.level_3[4] Validation | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-107 | supply_mechanics.circulation_controls.reserve_gove... | should | token_economics_distribution | SSID_structure_level3_part1_MAX.md:146 |
| SOT-1070 | root_depth_matrix.04_deployment.max_depth Validati... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1071 | root_depth_matrix.04_deployment.level_3[0] Validat... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1072 | root_depth_matrix.04_deployment.level_3[1] Validat... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1073 | root_depth_matrix.04_deployment.level_3[2] Validat... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1074 | root_depth_matrix.04_deployment.level_3[3] Validat... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1075 | root_depth_matrix.05_documentation.max_depth Valid... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1076 | root_depth_matrix.05_documentation.level_3[0] Vali... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1077 | root_depth_matrix.05_documentation.level_3[1] Vali... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1078 | root_depth_matrix.05_documentation.level_3[2] Vali... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1079 | root_depth_matrix.05_documentation.level_3[3] Vali... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-108 | fee_routing.system_fees.scope Validation | should | token_economics_distribution | SSID_structure_level3_part1_MAX.md:146 |
| SOT-1080 | root_depth_matrix.05_documentation.level_3[4] Vali... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1081 | root_depth_matrix.05_documentation.level_4[0] Vali... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1082 | root_depth_matrix.05_documentation.level_5[0] Vali... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1083 | root_depth_matrix.05_documentation.level_5[1] Vali... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1084 | root_depth_matrix.05_documentation.disabled[0] Val... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1085 | root_depth_matrix.06_data_pipeline.max_depth Valid... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1086 | root_depth_matrix.06_data_pipeline.level_3[0] Vali... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1087 | root_depth_matrix.06_data_pipeline.level_3[1] Vali... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1088 | root_depth_matrix.06_data_pipeline.level_3[2] Vali... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1089 | root_depth_matrix.06_data_pipeline.level_3[3] Vali... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-109 | fee_routing.system_fees.note Validation | should | token_economics_distribution | SSID_structure_level3_part1_MAX.md:146 |
| SOT-1090 | root_depth_matrix.06_data_pipeline.level_3[4] Vali... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1091 | root_depth_matrix.07_governance_legal.max_depth Va... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1092 | root_depth_matrix.07_governance_legal.level_3[0] V... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1093 | root_depth_matrix.07_governance_legal.level_3[1] V... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1094 | root_depth_matrix.07_governance_legal.level_3[2] V... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1095 | root_depth_matrix.07_governance_legal.level_3[3] V... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1096 | root_depth_matrix.08_identity_score.max_depth Vali... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1097 | root_depth_matrix.08_identity_score.level_3[0] Val... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1098 | root_depth_matrix.08_identity_score.level_3[1] Val... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1099 | root_depth_matrix.08_identity_score.level_3[2] Val... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-110 | fee_routing.system_fees.total_fee Validation | should | token_economics_distribution | SSID_structure_level3_part1_MAX.md:146 |
| SOT-1100 | root_depth_matrix.09_meta_identity.max_depth Valid... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1101 | root_depth_matrix.09_meta_identity.level_3[0] Vali... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1102 | root_depth_matrix.09_meta_identity.level_3[1] Vali... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1103 | root_depth_matrix.09_meta_identity.level_3[2] Vali... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1104 | root_depth_matrix.10_interoperability.max_depth Va... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1105 | root_depth_matrix.10_interoperability.level_3[0] V... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1106 | root_depth_matrix.10_interoperability.level_3[1] V... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1107 | root_depth_matrix.10_interoperability.level_3[2] V... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1108 | root_depth_matrix.11_test_simulation.max_depth Val... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1109 | root_depth_matrix.11_test_simulation.level_3[0] Va... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-111 | fee_routing.system_fees.allocation.dev_fee Validat... | should | token_economics_distribution | SSID_structure_level3_part1_MAX.md:146 |
| SOT-1110 | root_depth_matrix.11_test_simulation.level_3[1] Va... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1111 | root_depth_matrix.11_test_simulation.level_3[2] Va... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1112 | root_depth_matrix.12_tooling.max_depth Validation | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1113 | root_depth_matrix.12_tooling.level_3[0] Validation | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1114 | root_depth_matrix.12_tooling.level_3[1] Validation | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1115 | root_depth_matrix.12_tooling.level_3[2] Validation | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1116 | root_depth_matrix.12_tooling.level_3[3] Validation | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1117 | root_depth_matrix.13_ui_layer.max_depth Validation | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1118 | root_depth_matrix.13_ui_layer.level_3[0] Validatio... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1119 | root_depth_matrix.13_ui_layer.level_3[1] Validatio... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-112 | fee_routing.system_fees.allocation.system_treasury... | should | token_economics_distribution | SSID_structure_level3_part1_MAX.md:146 |
| SOT-1120 | root_depth_matrix.13_ui_layer.level_3[2] Validatio... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1121 | root_depth_matrix.13_ui_layer.level_3[3] Validatio... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1122 | root_depth_matrix.13_ui_layer.level_4[0] Validatio... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1123 | root_depth_matrix.13_ui_layer.level_4[1] Validatio... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1124 | root_depth_matrix.13_ui_layer.level_4[2] Validatio... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1125 | root_depth_matrix.14_zero_time_auth.max_depth Vali... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1126 | root_depth_matrix.14_zero_time_auth.level_3[0] Val... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1127 | root_depth_matrix.14_zero_time_auth.level_3[1] Val... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1128 | root_depth_matrix.14_zero_time_auth.level_3[2] Val... | have | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1129 | root_depth_matrix.14_zero_time_auth.level_3[3] Val... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-113 | fee_routing.system_fees.burn_from_system_fee.polic... | should | token_economics_distribution | SSID_structure_level3_part1_MAX.md:146 |
| SOT-1130 | root_depth_matrix.15_infra.max_depth Validation | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1131 | root_depth_matrix.15_infra.level_3[0] Validation | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1132 | root_depth_matrix.15_infra.level_3[1] Validation | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1133 | root_depth_matrix.15_infra.level_3[2] Validation | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1134 | root_depth_matrix.15_infra.level_3[3] Validation | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1135 | root_depth_matrix.16_codex.max_depth Validation | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1136 | root_depth_matrix.16_codex.level_3[0] Validation | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1137 | root_depth_matrix.16_codex.level_3[1] Validation | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1138 | root_depth_matrix.16_codex.level_3[2] Validation | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1139 | root_depth_matrix.17_observability.max_depth Valid... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-114 | fee_routing.system_fees.burn_from_system_fee.base ... | should | token_economics_distribution | SSID_structure_level3_part1_MAX.md:146 |
| SOT-1140 | root_depth_matrix.17_observability.level_3[0] Vali... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1141 | root_depth_matrix.17_observability.level_3[1] Vali... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1142 | root_depth_matrix.17_observability.level_3[2] Vali... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1143 | root_depth_matrix.17_observability.level_3[3] Vali... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1144 | root_depth_matrix.17_observability.level_3[4] Vali... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1145 | root_depth_matrix.18_data_layer.max_depth Validati... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1146 | root_depth_matrix.18_data_layer.level_3[0] Validat... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1147 | root_depth_matrix.18_data_layer.level_3[1] Validat... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1148 | root_depth_matrix.18_data_layer.level_3[2] Validat... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1149 | root_depth_matrix.18_data_layer.level_3[3] Validat... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-115 | fee_routing.system_fees.burn_from_system_fee.snaps... | should | token_economics_distribution | SSID_structure_level3_part1_MAX.md:146 |
| SOT-1150 | root_depth_matrix.19_adapters.max_depth Validation | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1151 | root_depth_matrix.19_adapters.level_3[0] Validatio... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1152 | root_depth_matrix.19_adapters.level_3[1] Validatio... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1153 | root_depth_matrix.19_adapters.level_3[2] Validatio... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1154 | root_depth_matrix.19_adapters.level_3[3] Validatio... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1155 | root_depth_matrix.19_adapters.level_3[4] Validatio... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1156 | root_depth_matrix.20_foundation.max_depth Validati... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1157 | root_depth_matrix.20_foundation.level_3[0] Validat... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1158 | root_depth_matrix.20_foundation.level_3[1] Validat... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1159 | root_depth_matrix.20_foundation.level_3[2] Validat... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-116 | fee_routing.system_fees.burn_from_system_fee.daily... | should | token_economics_distribution | SSID_structure_level3_part1_MAX.md:146 |
| SOT-1160 | root_depth_matrix.21_post_quantum_crypto.max_depth... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1161 | root_depth_matrix.21_post_quantum_crypto.level_3[0... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1162 | root_depth_matrix.21_post_quantum_crypto.level_3[1... | have | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1163 | root_depth_matrix.21_post_quantum_crypto.level_3[2... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1164 | root_depth_matrix.22_datasets.max_depth Validation | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1165 | root_depth_matrix.22_datasets.level_3[0] Validatio... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1166 | root_depth_matrix.22_datasets.level_3[1] Validatio... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1167 | root_depth_matrix.22_datasets.level_3[2] Validatio... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1168 | root_depth_matrix.22_datasets.level_3[3] Validatio... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1169 | root_depth_matrix.22_datasets.level_3[4] Validatio... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-117 | fee_routing.system_fees.burn_from_system_fee.month... | should | token_economics_distribution | SSID_structure_level3_part1_MAX.md:146 |
| SOT-1170 | root_depth_matrix.23_compliance.max_depth Validati... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1171 | root_depth_matrix.23_compliance.level_3[0] Validat... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1172 | root_depth_matrix.23_compliance.level_3[1] Validat... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1173 | root_depth_matrix.23_compliance.level_3[2] Validat... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1174 | root_depth_matrix.23_compliance.level_3[3] Validat... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1175 | root_depth_matrix.23_compliance.level_3[4] Validat... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1176 | root_depth_matrix.23_compliance.level_3[5] Validat... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1177 | root_depth_matrix.23_compliance.level_3[6] Validat... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1178 | root_depth_matrix.23_compliance.level_3[7] Validat... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1179 | root_depth_matrix.23_compliance.level_3[8] Validat... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-118 | fee_routing.system_fees.burn_from_system_fee.oracl... | should | token_economics_distribution | SSID_structure_level3_part1_MAX.md:146 |
| SOT-1180 | root_depth_matrix.23_compliance.level_3[9] Validat... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1181 | root_depth_matrix.23_compliance.level_4[0] Validat... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1182 | root_depth_matrix.23_compliance.level_4[1] Validat... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1183 | root_depth_matrix.23_compliance.level_4[2] Validat... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1184 | root_depth_matrix.23_compliance.level_4[3] Validat... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1185 | root_depth_matrix.23_compliance.level_4[4] Validat... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1186 | root_depth_matrix.23_compliance.level_5[0] Validat... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1187 | root_depth_matrix.23_compliance.level_5[1] Validat... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1188 | root_depth_matrix.23_compliance.level_5[2] Validat... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1189 | root_depth_matrix.23_compliance.level_6[0] Validat... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-119 | fee_routing.validator_rewards.source Validation | should | token_economics_distribution | SSID_structure_level3_part1_MAX.md:146 |
| SOT-1190 | root_depth_matrix.24_meta_orchestration.max_depth ... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1191 | root_depth_matrix.24_meta_orchestration.level_3[0]... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1192 | root_depth_matrix.24_meta_orchestration.level_3[1]... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1193 | root_depth_matrix.24_meta_orchestration.level_3[2]... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1194 | root_depth_matrix.24_meta_orchestration.level_4[0]... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1195 | root_depth_matrix.24_meta_orchestration.level_4[1]... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1196 | root_depth_matrix.24_meta_orchestration.level_4[2]... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1197 | root_depth_matrix.24_meta_orchestration.level_4[3]... | should | maximalstand_addendum_root_depth_matrix_ebene_3_6_ | SSID_structure_level3_part2_MAX.md:1194 |
| SOT-1198 | shard_profile_default.S01_policies Validation | should | maximalstand_addendum_shard_16_globale_pflicht_bel | SSID_structure_level3_part2_MAX.md:1288 |
| SOT-1199 | shard_profile_default.S02_evidence Validation | should | maximalstand_addendum_shard_16_globale_pflicht_bel | SSID_structure_level3_part2_MAX.md:1288 |
| SOT-120 | fee_routing.validator_rewards.no_per_transaction_s... | should | token_economics_distribution | SSID_structure_level3_part1_MAX.md:146 |
| SOT-1200 | shard_profile_default.S03_configs Validation | should | maximalstand_addendum_shard_16_globale_pflicht_bel | SSID_structure_level3_part2_MAX.md:1288 |
| SOT-1201 | shard_profile_default.S04_registry Validation | should | maximalstand_addendum_shard_16_globale_pflicht_bel | SSID_structure_level3_part2_MAX.md:1288 |
| SOT-1202 | shard_profile_default.S05_tests Validation | should | maximalstand_addendum_shard_16_globale_pflicht_bel | SSID_structure_level3_part2_MAX.md:1288 |
| SOT-1203 | shard_profile_default.S06_simulation Validation | should | maximalstand_addendum_shard_16_globale_pflicht_bel | SSID_structure_level3_part2_MAX.md:1288 |
| SOT-1204 | shard_profile_default.S07_tooling Validation | should | maximalstand_addendum_shard_16_globale_pflicht_bel | SSID_structure_level3_part2_MAX.md:1288 |
| SOT-1205 | shard_profile_default.S08_docs Validation | should | maximalstand_addendum_shard_16_globale_pflicht_bel | SSID_structure_level3_part2_MAX.md:1288 |
| SOT-1206 | shard_profile_default.S09_api Validation | should | maximalstand_addendum_shard_16_globale_pflicht_bel | SSID_structure_level3_part2_MAX.md:1288 |
| SOT-1207 | shard_profile_default.S10_adapters Validation | should | maximalstand_addendum_shard_16_globale_pflicht_bel | SSID_structure_level3_part2_MAX.md:1288 |
| SOT-1208 | shard_profile_default.S11_datasets Validation | should | maximalstand_addendum_shard_16_globale_pflicht_bel | SSID_structure_level3_part2_MAX.md:1288 |
| SOT-1209 | shard_profile_default.S12_governance Validation | should | maximalstand_addendum_shard_16_globale_pflicht_bel | SSID_structure_level3_part2_MAX.md:1288 |
| SOT-121 | fee_routing.validator_rewards.note Validation | should | token_economics_distribution | SSID_structure_level3_part1_MAX.md:146 |
| SOT-1210 | shard_profile_default.S13_security Validation | should | maximalstand_addendum_shard_16_globale_pflicht_bel | SSID_structure_level3_part2_MAX.md:1288 |
| SOT-1211 | shard_profile_default.S14_interop Validation | should | maximalstand_addendum_shard_16_globale_pflicht_bel | SSID_structure_level3_part2_MAX.md:1288 |
| SOT-1212 | shard_profile_default.S15_observability Validation | should | maximalstand_addendum_shard_16_globale_pflicht_bel | SSID_structure_level3_part2_MAX.md:1288 |
| SOT-1213 | shard_profile_default.S16_deployment Validation | should | maximalstand_addendum_shard_16_globale_pflicht_bel | SSID_structure_level3_part2_MAX.md:1288 |
| SOT-1214 | **FAIL (Exit 24)**, wenn | must | ci_gate_anpassungen_erzwingen_semantik | SSID_structure_level3_part2_MAX.md:1358 |
| SOT-1215 | version Validation | should | 6_datenschutz_globale_abdeckung_v2_2 | SSID_structure_level3_part3_MAX.md:225 |
| SOT-1216 | date Validation | should | 6_datenschutz_globale_abdeckung_v2_2 | SSID_structure_level3_part3_MAX.md:225 |
| SOT-1217 | deprecated Validation | should | 6_datenschutz_globale_abdeckung_v2_2 | SSID_structure_level3_part3_MAX.md:225 |
| SOT-1218 | regulatory_basis Validation | should | 6_datenschutz_globale_abdeckung_v2_2 | SSID_structure_level3_part3_MAX.md:225 |
| SOT-1219 | classification Validation | should | 6_datenschutz_globale_abdeckung_v2_2 | SSID_structure_level3_part3_MAX.md:225 |
| SOT-122 | governance_fees.proposal_deposits Validation | must | token_economics_distribution | SSID_structure_level3_part1_MAX.md:146 |
| SOT-1220 | ccpa_cpra/.name Validation | should | 6_datenschutz_globale_abdeckung_v2_2 | SSID_structure_level3_part3_MAX.md:225 |
| SOT-1221 | ccpa_cpra/.path Validation | should | 6_datenschutz_globale_abdeckung_v2_2 | SSID_structure_level3_part3_MAX.md:225 |
| SOT-1222 | ccpa_cpra/.deprecated Validation | should | 6_datenschutz_globale_abdeckung_v2_2 | SSID_structure_level3_part3_MAX.md:225 |
| SOT-1223 | ccpa_cpra/.business_priority Validation | should | 6_datenschutz_globale_abdeckung_v2_2 | SSID_structure_level3_part3_MAX.md:225 |
| SOT-1224 | lgpd_br/.name Validation | should | 6_datenschutz_globale_abdeckung_v2_2 | SSID_structure_level3_part3_MAX.md:225 |
| SOT-1225 | lgpd_br/.path Validation | should | 6_datenschutz_globale_abdeckung_v2_2 | SSID_structure_level3_part3_MAX.md:225 |
| SOT-1226 | lgpd_br/.deprecated Validation | should | 6_datenschutz_globale_abdeckung_v2_2 | SSID_structure_level3_part3_MAX.md:225 |
| SOT-1227 | lgpd_br/.business_priority Validation | should | 6_datenschutz_globale_abdeckung_v2_2 | SSID_structure_level3_part3_MAX.md:225 |
| SOT-1228 | pdpa_sg/.name Validation | should | 6_datenschutz_globale_abdeckung_v2_2 | SSID_structure_level3_part3_MAX.md:225 |
| SOT-1229 | pdpa_sg/.path Validation | should | 6_datenschutz_globale_abdeckung_v2_2 | SSID_structure_level3_part3_MAX.md:225 |
| SOT-123 | governance_fees.voting_gas Validation | should | token_economics_distribution | SSID_structure_level3_part1_MAX.md:146 |
| SOT-1230 | pdpa_sg/.deprecated Validation | should | 6_datenschutz_globale_abdeckung_v2_2 | SSID_structure_level3_part3_MAX.md:225 |
| SOT-1231 | pdpa_sg/.business_priority Validation | should | 6_datenschutz_globale_abdeckung_v2_2 | SSID_structure_level3_part3_MAX.md:225 |
| SOT-1232 | appi_jp/.name Validation | should | 6_datenschutz_globale_abdeckung_v2_2 | SSID_structure_level3_part3_MAX.md:225 |
| SOT-1233 | appi_jp/.path Validation | should | 6_datenschutz_globale_abdeckung_v2_2 | SSID_structure_level3_part3_MAX.md:225 |
| SOT-1234 | appi_jp/.deprecated Validation | should | 6_datenschutz_globale_abdeckung_v2_2 | SSID_structure_level3_part3_MAX.md:225 |
| SOT-1235 | appi_jp/.business_priority Validation | should | 6_datenschutz_globale_abdeckung_v2_2 | SSID_structure_level3_part3_MAX.md:225 |
| SOT-1236 | pipl_cn/.name Validation | should | 6_datenschutz_globale_abdeckung_v2_2 | SSID_structure_level3_part3_MAX.md:225 |
| SOT-1237 | pipl_cn/.path Validation | should | 6_datenschutz_globale_abdeckung_v2_2 | SSID_structure_level3_part3_MAX.md:225 |
| SOT-1238 | pipl_cn/.deprecated Validation | should | 6_datenschutz_globale_abdeckung_v2_2 | SSID_structure_level3_part3_MAX.md:225 |
| SOT-1239 | pipl_cn/.business_priority Validation | have | 6_datenschutz_globale_abdeckung_v2_2 | SSID_structure_level3_part3_MAX.md:225 |
| SOT-124 | governance_controls.authority Validation | should | token_economics_distribution | SSID_structure_level3_part1_MAX.md:146 |
| SOT-1240 | popia_za/.name Validation | should | 6_datenschutz_globale_abdeckung_v2_2 | SSID_structure_level3_part3_MAX.md:225 |
| SOT-1241 | popia_za/.path Validation | should | 6_datenschutz_globale_abdeckung_v2_2 | SSID_structure_level3_part3_MAX.md:225 |
| SOT-1242 | popia_za/.deprecated Validation | should | 6_datenschutz_globale_abdeckung_v2_2 | SSID_structure_level3_part3_MAX.md:225 |
| SOT-1243 | popia_za/.business_priority Validation | have | 6_datenschutz_globale_abdeckung_v2_2 | SSID_structure_level3_part3_MAX.md:225 |
| SOT-1244 | pipeda_ca/.name Validation | should | 6_datenschutz_globale_abdeckung_v2_2 | SSID_structure_level3_part3_MAX.md:225 |
| SOT-1245 | pipeda_ca/.path Validation | should | 6_datenschutz_globale_abdeckung_v2_2 | SSID_structure_level3_part3_MAX.md:225 |
| SOT-1246 | pipeda_ca/.deprecated Validation | should | 6_datenschutz_globale_abdeckung_v2_2 | SSID_structure_level3_part3_MAX.md:225 |
| SOT-1247 | pipeda_ca/.business_priority Validation | should | 6_datenschutz_globale_abdeckung_v2_2 | SSID_structure_level3_part3_MAX.md:225 |
| SOT-1248 | dpdp_in/.name Validation | should | 6_datenschutz_globale_abdeckung_v2_2 | SSID_structure_level3_part3_MAX.md:225 |
| SOT-1249 | dpdp_in/.path Validation | should | 6_datenschutz_globale_abdeckung_v2_2 | SSID_structure_level3_part3_MAX.md:225 |
| SOT-125 | governance_controls.reference Validation | should | token_economics_distribution | SSID_structure_level3_part1_MAX.md:146 |
| SOT-1250 | dpdp_in/.deprecated Validation | should | 6_datenschutz_globale_abdeckung_v2_2 | SSID_structure_level3_part3_MAX.md:225 |
| SOT-1251 | dpdp_in/.business_priority Validation | should | 6_datenschutz_globale_abdeckung_v2_2 | SSID_structure_level3_part3_MAX.md:225 |
| SOT-1252 | deprecated_privacy.id Validation | should | 6_datenschutz_globale_abdeckung_v2_2 | SSID_structure_level3_part3_MAX.md:225 |
| SOT-1253 | deprecated_privacy.status Validation | should | 6_datenschutz_globale_abdeckung_v2_2 | SSID_structure_level3_part3_MAX.md:225 |
| SOT-1254 | deprecated_privacy.deprecated Validation | should | 6_datenschutz_globale_abdeckung_v2_2 | SSID_structure_level3_part3_MAX.md:225 |
| SOT-1255 | deprecated_privacy.replaced_by Validation | should | 6_datenschutz_globale_abdeckung_v2_2 | SSID_structure_level3_part3_MAX.md:225 |
| SOT-1256 | deprecated_privacy.deprecation_date Validation | should | 6_datenschutz_globale_abdeckung_v2_2 | SSID_structure_level3_part3_MAX.md:225 |
| SOT-1257 | deprecated_privacy.notes Validation | should | 6_datenschutz_globale_abdeckung_v2_2 | SSID_structure_level3_part3_MAX.md:225 |
| SOT-1258 | version Validation | should | 7_finanzmarkt_sicherheit_resilienz_v1_1 | SSID_structure_level3_part3_MAX.md:291 |
| SOT-1259 | date Validation | should | 7_finanzmarkt_sicherheit_resilienz_v1_1 | SSID_structure_level3_part3_MAX.md:291 |
| SOT-126 | governance_controls.note Validation | should | token_economics_distribution | SSID_structure_level3_part1_MAX.md:146 |
| SOT-1260 | deprecated Validation | should | 7_finanzmarkt_sicherheit_resilienz_v1_1 | SSID_structure_level3_part3_MAX.md:291 |
| SOT-1261 | classification Validation | should | 7_finanzmarkt_sicherheit_resilienz_v1_1 | SSID_structure_level3_part3_MAX.md:291 |
| SOT-1262 | nist_csf_20/.name Validation | should | 7_finanzmarkt_sicherheit_resilienz_v1_1 | SSID_structure_level3_part3_MAX.md:291 |
| SOT-1263 | nist_csf_20/.path Validation | should | 7_finanzmarkt_sicherheit_resilienz_v1_1 | SSID_structure_level3_part3_MAX.md:291 |
| SOT-1264 | nist_csf_20/.deprecated Validation | should | 7_finanzmarkt_sicherheit_resilienz_v1_1 | SSID_structure_level3_part3_MAX.md:291 |
| SOT-1265 | nist_csf_20/.business_priority Validation | should | 7_finanzmarkt_sicherheit_resilienz_v1_1 | SSID_structure_level3_part3_MAX.md:291 |
| SOT-1266 | pqc/.name Validation | should | 7_finanzmarkt_sicherheit_resilienz_v1_1 | SSID_structure_level3_part3_MAX.md:291 |
| SOT-1267 | pqc/.path Validation | should | 7_finanzmarkt_sicherheit_resilienz_v1_1 | SSID_structure_level3_part3_MAX.md:291 |
| SOT-1268 | pqc/.deprecated Validation | should | 7_finanzmarkt_sicherheit_resilienz_v1_1 | SSID_structure_level3_part3_MAX.md:291 |
| SOT-1269 | pqc/.business_priority Validation | should | 7_finanzmarkt_sicherheit_resilienz_v1_1 | SSID_structure_level3_part3_MAX.md:291 |
| SOT-127 | staking_mechanics.minimum_stake Validation | should | token_economics_distribution | SSID_structure_level3_part1_MAX.md:146 |
| SOT-1270 | etsi_trust/.name Validation | should | 7_finanzmarkt_sicherheit_resilienz_v1_1 | SSID_structure_level3_part3_MAX.md:291 |
| SOT-1271 | etsi_trust/.path Validation | should | 7_finanzmarkt_sicherheit_resilienz_v1_1 | SSID_structure_level3_part3_MAX.md:291 |
| SOT-1272 | etsi_trust/.deprecated Validation | should | 7_finanzmarkt_sicherheit_resilienz_v1_1 | SSID_structure_level3_part3_MAX.md:291 |
| SOT-1273 | etsi_trust/.business_priority Validation | should | 7_finanzmarkt_sicherheit_resilienz_v1_1 | SSID_structure_level3_part3_MAX.md:291 |
| SOT-1274 | name Validation | should | internal_issue_templates | SSID_structure_level3_part3_MAX.md:330 |
| SOT-1275 | description Validation | should | internal_issue_templates | SSID_structure_level3_part3_MAX.md:330 |
| SOT-1276 | title Validation | should | internal_issue_templates | SSID_structure_level3_part3_MAX.md:330 |
| SOT-1277 | labels[0] Validation | should | internal_issue_templates | SSID_structure_level3_part3_MAX.md:330 |
| SOT-1278 | labels[1] Validation | should | internal_issue_templates | SSID_structure_level3_part3_MAX.md:330 |
| SOT-1279 | labels[2] Validation | should | internal_issue_templates | SSID_structure_level3_part3_MAX.md:330 |
| SOT-128 | staking_mechanics.maximum_discount Validation | should | token_economics_distribution | SSID_structure_level3_part1_MAX.md:146 |
| SOT-1280 | labels[3] Validation | should | internal_issue_templates | SSID_structure_level3_part3_MAX.md:330 |
| SOT-1281 | body.type Validation | should | internal_issue_templates | SSID_structure_level3_part3_MAX.md:330 |
| SOT-1282 | body.id Validation | should | internal_issue_templates | SSID_structure_level3_part3_MAX.md:330 |
| SOT-1283 | body.attributes.label Validation | should | internal_issue_templates | SSID_structure_level3_part3_MAX.md:330 |
| SOT-1284 | body.attributes.options[0] Validation | should | internal_issue_templates | SSID_structure_level3_part3_MAX.md:330 |
| SOT-1285 | body.attributes.options[1] Validation | should | internal_issue_templates | SSID_structure_level3_part3_MAX.md:330 |
| SOT-1286 | body.attributes.options[2] Validation | should | internal_issue_templates | SSID_structure_level3_part3_MAX.md:330 |
| SOT-1287 | body.attributes.options[3] Validation | should | internal_issue_templates | SSID_structure_level3_part3_MAX.md:330 |
| SOT-1288 | body.attributes.options[4] Validation | should | internal_issue_templates | SSID_structure_level3_part3_MAX.md:330 |
| SOT-1289 | body.validations.required Validation | must | internal_issue_templates | SSID_structure_level3_part3_MAX.md:330 |
| SOT-129 | staking_mechanics.slashing_penalty Validation | should | token_economics_distribution | SSID_structure_level3_part1_MAX.md:146 |
| SOT-1290 | body.type Validation | should | internal_issue_templates | SSID_structure_level3_part3_MAX.md:330 |
| SOT-1291 | body.id Validation | should | internal_issue_templates | SSID_structure_level3_part3_MAX.md:330 |
| SOT-1292 | body.attributes.label Validation | should | internal_issue_templates | SSID_structure_level3_part3_MAX.md:330 |
| SOT-1293 | body.attributes.options[0] Validation | must | internal_issue_templates | SSID_structure_level3_part3_MAX.md:330 |
| SOT-1294 | body.attributes.options[1] Validation | should | internal_issue_templates | SSID_structure_level3_part3_MAX.md:330 |
| SOT-1295 | body.attributes.options[2] Validation | should | internal_issue_templates | SSID_structure_level3_part3_MAX.md:330 |
| SOT-1296 | body.attributes.options[3] Validation | have | internal_issue_templates | SSID_structure_level3_part3_MAX.md:330 |
| SOT-1297 | body.validations.required Validation | must | internal_issue_templates | SSID_structure_level3_part3_MAX.md:330 |
| SOT-1298 | body.type Validation | should | internal_issue_templates | SSID_structure_level3_part3_MAX.md:330 |
| SOT-1299 | body.id Validation | should | internal_issue_templates | SSID_structure_level3_part3_MAX.md:330 |
| SOT-130 | staking_mechanics.unstaking_period Validation | should | token_economics_distribution | SSID_structure_level3_part1_MAX.md:146 |
| SOT-1300 | body.attributes.label Validation | should | internal_issue_templates | SSID_structure_level3_part3_MAX.md:330 |
| SOT-1301 | body.attributes.description Validation | should | internal_issue_templates | SSID_structure_level3_part3_MAX.md:330 |
| SOT-1302 | body.validations.required Validation | must | internal_issue_templates | SSID_structure_level3_part3_MAX.md:330 |
| SOT-1303 | body.type Validation | should | internal_issue_templates | SSID_structure_level3_part3_MAX.md:330 |
| SOT-1304 | body.id Validation | should | internal_issue_templates | SSID_structure_level3_part3_MAX.md:330 |
| SOT-1305 | body.attributes.label Validation | should | internal_issue_templates | SSID_structure_level3_part3_MAX.md:330 |
| SOT-1306 | body.attributes.description Validation | should | internal_issue_templates | SSID_structure_level3_part3_MAX.md:330 |
| SOT-1307 | body.validations.required Validation | must | internal_issue_templates | SSID_structure_level3_part3_MAX.md:330 |
| SOT-1308 | body.type Validation | should | internal_issue_templates | SSID_structure_level3_part3_MAX.md:330 |
| SOT-1309 | body.id Validation | should | internal_issue_templates | SSID_structure_level3_part3_MAX.md:330 |
| SOT-131 | staking_mechanics.discount_applies_to Validation | should | token_economics_distribution | SSID_structure_level3_part1_MAX.md:146 |
| SOT-1310 | body.attributes.label Validation | should | internal_issue_templates | SSID_structure_level3_part3_MAX.md:330 |
| SOT-1311 | body.attributes.options.label Validation | should | internal_issue_templates | SSID_structure_level3_part3_MAX.md:330 |
| SOT-1312 | body.attributes.options.label Validation | should | internal_issue_templates | SSID_structure_level3_part3_MAX.md:330 |
| SOT-1313 | body.attributes.options.label Validation | should | internal_issue_templates | SSID_structure_level3_part3_MAX.md:330 |
| SOT-1314 | body.attributes.options.label Validation | should | internal_issue_templates | SSID_structure_level3_part3_MAX.md:330 |
| SOT-1315 | Business-critical changes escalated to compliance ... | must | review_process_internal | SSID_structure_level3_part3_MAX.md:411 |
| SOT-1316 | version Validation | should | enhanced_evidence_management_enterprise | SSID_structure_level3_part3_MAX.md:425 |
| SOT-1317 | deprecated Validation | should | enhanced_evidence_management_enterprise | SSID_structure_level3_part3_MAX.md:425 |
| SOT-1318 | classification Validation | should | enhanced_evidence_management_enterprise | SSID_structure_level3_part3_MAX.md:425 |
| SOT-1319 | storage_tiers.immutable_store.path Validation | should | enhanced_evidence_management_enterprise | SSID_structure_level3_part3_MAX.md:425 |
| SOT-132 | staking_mechanics.system_fee_invariance Validation | should | token_economics_distribution | SSID_structure_level3_part1_MAX.md:146 |
| SOT-1320 | storage_tiers.immutable_store.retention Validation | should | enhanced_evidence_management_enterprise | SSID_structure_level3_part3_MAX.md:425 |
| SOT-1321 | storage_tiers.immutable_store.integrity Validation | should | enhanced_evidence_management_enterprise | SSID_structure_level3_part3_MAX.md:425 |
| SOT-1322 | storage_tiers.immutable_store.encryption Validatio... | should | enhanced_evidence_management_enterprise | SSID_structure_level3_part3_MAX.md:425 |
| SOT-1323 | storage_tiers.blockchain_anchors.enabled Validatio... | should | enhanced_evidence_management_enterprise | SSID_structure_level3_part3_MAX.md:425 |
| SOT-1324 | storage_tiers.blockchain_anchors.path Validation | should | enhanced_evidence_management_enterprise | SSID_structure_level3_part3_MAX.md:425 |
| SOT-1325 | storage_tiers.blockchain_anchors.service Validatio... | should | enhanced_evidence_management_enterprise | SSID_structure_level3_part3_MAX.md:425 |
| SOT-1326 | storage_tiers.blockchain_anchors.frequency Validat... | should | enhanced_evidence_management_enterprise | SSID_structure_level3_part3_MAX.md:425 |
| SOT-1327 | storage_tiers.blockchain_anchors.classification Va... | should | enhanced_evidence_management_enterprise | SSID_structure_level3_part3_MAX.md:425 |
| SOT-1328 | storage_tiers.evidence_chain.path Validation | should | enhanced_evidence_management_enterprise | SSID_structure_level3_part3_MAX.md:425 |
| SOT-1329 | storage_tiers.evidence_chain.retention Validation | should | enhanced_evidence_management_enterprise | SSID_structure_level3_part3_MAX.md:425 |
| SOT-133 | governance_parameters.proposal_framework.proposal_... | should | token_economics_distribution | SSID_structure_level3_part1_MAX.md:146 |
| SOT-1330 | storage_tiers.evidence_chain.encryption Validation | should | enhanced_evidence_management_enterprise | SSID_structure_level3_part3_MAX.md:425 |
| SOT-1331 | storage_tiers.evidence_chain.backup Validation | should | enhanced_evidence_management_enterprise | SSID_structure_level3_part3_MAX.md:425 |
| SOT-1332 | storage_tiers.internal_review_documentation.path V... | should | enhanced_evidence_management_enterprise | SSID_structure_level3_part3_MAX.md:425 |
| SOT-1333 | storage_tiers.internal_review_documentation.retent... | should | enhanced_evidence_management_enterprise | SSID_structure_level3_part3_MAX.md:425 |
| SOT-1334 | storage_tiers.internal_review_documentation.encryp... | should | enhanced_evidence_management_enterprise | SSID_structure_level3_part3_MAX.md:425 |
| SOT-1335 | storage_tiers.internal_review_documentation.classi... | should | enhanced_evidence_management_enterprise | SSID_structure_level3_part3_MAX.md:425 |
| SOT-1336 | storage_tiers.business_evidence.path Validation | should | enhanced_evidence_management_enterprise | SSID_structure_level3_part3_MAX.md:425 |
| SOT-1337 | storage_tiers.business_evidence.retention Validati... | should | enhanced_evidence_management_enterprise | SSID_structure_level3_part3_MAX.md:425 |
| SOT-1338 | storage_tiers.business_evidence.encryption Validat... | should | enhanced_evidence_management_enterprise | SSID_structure_level3_part3_MAX.md:425 |
| SOT-1339 | storage_tiers.business_evidence.classification Val... | should | enhanced_evidence_management_enterprise | SSID_structure_level3_part3_MAX.md:425 |
| SOT-134 | governance_parameters.proposal_framework.proposal_... | must | token_economics_distribution | SSID_structure_level3_part1_MAX.md:146 |
| SOT-1340 | audit_enhancement.blockchain_anchoring Validation | should | enhanced_evidence_management_enterprise | SSID_structure_level3_part3_MAX.md:425 |
| SOT-1341 | audit_enhancement.opentimestamp_enabled Validation | should | enhanced_evidence_management_enterprise | SSID_structure_level3_part3_MAX.md:425 |
| SOT-1342 | audit_enhancement.evidence_timestamping Validation | should | enhanced_evidence_management_enterprise | SSID_structure_level3_part3_MAX.md:425 |
| SOT-1343 | audit_enhancement.proof_of_existence Validation | should | enhanced_evidence_management_enterprise | SSID_structure_level3_part3_MAX.md:425 |
| SOT-1344 | audit_enhancement.verification_method Validation | should | enhanced_evidence_management_enterprise | SSID_structure_level3_part3_MAX.md:425 |
| SOT-1345 | audit_enhancement.enterprise_controls Validation | should | enhanced_evidence_management_enterprise | SSID_structure_level3_part3_MAX.md:425 |
| SOT-1346 | version Validation | should | quarantine_singleton_framework_enterprise | SSID_structure_level3_part3_MAX.md:473 |
| SOT-1347 | date Validation | should | quarantine_singleton_framework_enterprise | SSID_structure_level3_part3_MAX.md:473 |
| SOT-1348 | deprecated Validation | should | quarantine_singleton_framework_enterprise | SSID_structure_level3_part3_MAX.md:473 |
| SOT-1349 | classification Validation | should | quarantine_singleton_framework_enterprise | SSID_structure_level3_part3_MAX.md:473 |
| SOT-135 | governance_parameters.proposal_framework.proposal_... | should | token_economics_distribution | SSID_structure_level3_part1_MAX.md:146 |
| SOT-1350 | quarantine_singleton.canonical_path Validation | should | quarantine_singleton_framework_enterprise | SSID_structure_level3_part3_MAX.md:473 |
| SOT-1351 | quarantine_singleton.principle Validation | should | quarantine_singleton_framework_enterprise | SSID_structure_level3_part3_MAX.md:473 |
| SOT-1352 | quarantine_singleton.access_control Validation | should | quarantine_singleton_framework_enterprise | SSID_structure_level3_part3_MAX.md:473 |
| SOT-1353 | quarantine_singleton.encryption Validation | should | quarantine_singleton_framework_enterprise | SSID_structure_level3_part3_MAX.md:473 |
| SOT-1354 | quarantine_triggers.compliance_violations[0] Valid... | must | quarantine_singleton_framework_enterprise | SSID_structure_level3_part3_MAX.md:473 |
| SOT-1355 | quarantine_triggers.compliance_violations[1] Valid... | should | quarantine_singleton_framework_enterprise | SSID_structure_level3_part3_MAX.md:473 |
| SOT-1356 | quarantine_triggers.compliance_violations[2] Valid... | should | quarantine_singleton_framework_enterprise | SSID_structure_level3_part3_MAX.md:473 |
| SOT-1357 | quarantine_triggers.compliance_violations[3] Valid... | should | quarantine_singleton_framework_enterprise | SSID_structure_level3_part3_MAX.md:473 |
| SOT-1358 | quarantine_triggers.compliance_violations[4] Valid... | should | quarantine_singleton_framework_enterprise | SSID_structure_level3_part3_MAX.md:473 |
| SOT-1359 | quarantine_triggers.compliance_violations[5] Valid... | should | quarantine_singleton_framework_enterprise | SSID_structure_level3_part3_MAX.md:473 |
| SOT-136 | governance_parameters.proposal_framework.proposal_... | should | token_economics_distribution | SSID_structure_level3_part1_MAX.md:146 |
| SOT-1360 | quarantine_triggers.regulatory_flags[0] Validation | should | quarantine_singleton_framework_enterprise | SSID_structure_level3_part3_MAX.md:473 |
| SOT-1361 | quarantine_triggers.regulatory_flags[1] Validation | should | quarantine_singleton_framework_enterprise | SSID_structure_level3_part3_MAX.md:473 |
| SOT-1362 | quarantine_triggers.regulatory_flags[2] Validation | must | quarantine_singleton_framework_enterprise | SSID_structure_level3_part3_MAX.md:473 |
| SOT-1363 | quarantine_triggers.regulatory_flags[3] Validation | should | quarantine_singleton_framework_enterprise | SSID_structure_level3_part3_MAX.md:473 |
| SOT-1364 | quarantine_triggers.regulatory_flags[4] Validation | should | quarantine_singleton_framework_enterprise | SSID_structure_level3_part3_MAX.md:473 |
| SOT-1365 | quarantine_triggers.technical_violations[0] Valida... | must | quarantine_singleton_framework_enterprise | SSID_structure_level3_part3_MAX.md:473 |
| SOT-1366 | quarantine_triggers.technical_violations[1] Valida... | should | quarantine_singleton_framework_enterprise | SSID_structure_level3_part3_MAX.md:473 |
| SOT-1367 | quarantine_triggers.technical_violations[2] Valida... | should | quarantine_singleton_framework_enterprise | SSID_structure_level3_part3_MAX.md:473 |
| SOT-1368 | quarantine_triggers.technical_violations[3] Valida... | should | quarantine_singleton_framework_enterprise | SSID_structure_level3_part3_MAX.md:473 |
| SOT-1369 | quarantine_triggers.technical_violations[4] Valida... | should | quarantine_singleton_framework_enterprise | SSID_structure_level3_part3_MAX.md:473 |
| SOT-137 | governance_parameters.proposal_framework.proposal_... | should | token_economics_distribution | SSID_structure_level3_part1_MAX.md:146 |
| SOT-1370 | quarantine_processing.intake_processor Validation | should | quarantine_singleton_framework_enterprise | SSID_structure_level3_part3_MAX.md:473 |
| SOT-1371 | quarantine_processing.auto_quarantine Validation | should | quarantine_singleton_framework_enterprise | SSID_structure_level3_part3_MAX.md:473 |
| SOT-1372 | quarantine_processing.manual_override_required Val... | must | quarantine_singleton_framework_enterprise | SSID_structure_level3_part3_MAX.md:473 |
| SOT-1373 | quarantine_processing.escalation_timeline Validati... | must | quarantine_singleton_framework_enterprise | SSID_structure_level3_part3_MAX.md:473 |
| SOT-1374 | quarantine_retention.policies_file Validation | should | quarantine_singleton_framework_enterprise | SSID_structure_level3_part3_MAX.md:473 |
| SOT-1375 | quarantine_retention.retention_periods.compliance_... | should | quarantine_singleton_framework_enterprise | SSID_structure_level3_part3_MAX.md:473 |
| SOT-1376 | quarantine_retention.retention_periods.regulatory_... | should | quarantine_singleton_framework_enterprise | SSID_structure_level3_part3_MAX.md:473 |
| SOT-1377 | quarantine_retention.retention_periods.technical_v... | should | quarantine_singleton_framework_enterprise | SSID_structure_level3_part3_MAX.md:473 |
| SOT-1378 | quarantine_retention.retention_periods.business_cr... | must | quarantine_singleton_framework_enterprise | SSID_structure_level3_part3_MAX.md:473 |
| SOT-1379 | quarantine_retention.retention_periods.legal_hold ... | should | quarantine_singleton_framework_enterprise | SSID_structure_level3_part3_MAX.md:473 |
| SOT-138 | governance_parameters.proposal_framework.proposal_... | should | token_economics_distribution | SSID_structure_level3_part1_MAX.md:146 |
| SOT-1380 | quarantine_retention.purge_automation Validation | should | quarantine_singleton_framework_enterprise | SSID_structure_level3_part3_MAX.md:473 |
| SOT-1381 | quarantine_retention.archive_to_cold_storage Valid... | should | quarantine_singleton_framework_enterprise | SSID_structure_level3_part3_MAX.md:473 |
| SOT-1382 | quarantine_retention.enterprise_backup Validation | should | quarantine_singleton_framework_enterprise | SSID_structure_level3_part3_MAX.md:473 |
| SOT-1383 | hash_ledger_system.ledger_file Validation | should | quarantine_singleton_framework_enterprise | SSID_structure_level3_part3_MAX.md:473 |
| SOT-1384 | hash_ledger_system.hash_algorithm Validation | should | quarantine_singleton_framework_enterprise | SSID_structure_level3_part3_MAX.md:473 |
| SOT-1385 | hash_ledger_system.chain_integrity Validation | should | quarantine_singleton_framework_enterprise | SSID_structure_level3_part3_MAX.md:473 |
| SOT-1386 | hash_ledger_system.immutable_properties Validation | should | quarantine_singleton_framework_enterprise | SSID_structure_level3_part3_MAX.md:473 |
| SOT-1387 | hash_ledger_system.blockchain_anchoring Validation | should | quarantine_singleton_framework_enterprise | SSID_structure_level3_part3_MAX.md:473 |
| SOT-1388 | hash_ledger_system.ledger_structure.entry_id Valid... | should | quarantine_singleton_framework_enterprise | SSID_structure_level3_part3_MAX.md:473 |
| SOT-1389 | hash_ledger_system.ledger_structure.timestamp Vali... | should | quarantine_singleton_framework_enterprise | SSID_structure_level3_part3_MAX.md:473 |
| SOT-139 | governance_parameters.voting_requirements.quorum_s... | should | token_economics_distribution | SSID_structure_level3_part1_MAX.md:146 |
| SOT-1390 | hash_ledger_system.ledger_structure.item_hash Vali... | should | quarantine_singleton_framework_enterprise | SSID_structure_level3_part3_MAX.md:473 |
| SOT-1391 | hash_ledger_system.ledger_structure.trigger_reason... | should | quarantine_singleton_framework_enterprise | SSID_structure_level3_part3_MAX.md:473 |
| SOT-1392 | hash_ledger_system.ledger_structure.quarantine_off... | should | quarantine_singleton_framework_enterprise | SSID_structure_level3_part3_MAX.md:473 |
| SOT-1393 | hash_ledger_system.ledger_structure.business_impac... | should | quarantine_singleton_framework_enterprise | SSID_structure_level3_part3_MAX.md:473 |
| SOT-1394 | hash_ledger_system.ledger_structure.previous_hash ... | should | quarantine_singleton_framework_enterprise | SSID_structure_level3_part3_MAX.md:473 |
| SOT-1395 | hash_ledger_system.ledger_structure.blockchain_anc... | should | quarantine_singleton_framework_enterprise | SSID_structure_level3_part3_MAX.md:473 |
| SOT-1396 | quarantine_governance.review_committee[0] Validati... | should | quarantine_singleton_framework_enterprise | SSID_structure_level3_part3_MAX.md:473 |
| SOT-1397 | quarantine_governance.review_committee[1] Validati... | should | quarantine_singleton_framework_enterprise | SSID_structure_level3_part3_MAX.md:473 |
| SOT-1398 | quarantine_governance.review_committee[2] Validati... | should | quarantine_singleton_framework_enterprise | SSID_structure_level3_part3_MAX.md:473 |
| SOT-1399 | quarantine_governance.review_committee[3] Validati... | should | quarantine_singleton_framework_enterprise | SSID_structure_level3_part3_MAX.md:473 |
| SOT-140 | governance_parameters.voting_requirements.quorum_p... | should | token_economics_distribution | SSID_structure_level3_part1_MAX.md:146 |
| SOT-1400 | quarantine_governance.review_committee[4] Validati... | should | quarantine_singleton_framework_enterprise | SSID_structure_level3_part3_MAX.md:473 |
| SOT-1401 | quarantine_governance.review_schedule.daily Valida... | should | quarantine_singleton_framework_enterprise | SSID_structure_level3_part3_MAX.md:473 |
| SOT-1402 | quarantine_governance.review_schedule.weekly Valid... | should | quarantine_singleton_framework_enterprise | SSID_structure_level3_part3_MAX.md:473 |
| SOT-1403 | quarantine_governance.review_schedule.monthly Vali... | should | quarantine_singleton_framework_enterprise | SSID_structure_level3_part3_MAX.md:473 |
| SOT-1404 | quarantine_governance.review_schedule.quarterly Va... | should | quarantine_singleton_framework_enterprise | SSID_structure_level3_part3_MAX.md:473 |
| SOT-1405 | quarantine_governance.release_criteria.compliance_... | should | quarantine_singleton_framework_enterprise | SSID_structure_level3_part3_MAX.md:473 |
| SOT-1406 | quarantine_governance.release_criteria.legal_clear... | must | quarantine_singleton_framework_enterprise | SSID_structure_level3_part3_MAX.md:473 |
| SOT-1407 | quarantine_governance.release_criteria.business_ap... | should | quarantine_singleton_framework_enterprise | SSID_structure_level3_part3_MAX.md:473 |
| SOT-1408 | quarantine_governance.release_criteria.technical_v... | should | quarantine_singleton_framework_enterprise | SSID_structure_level3_part3_MAX.md:473 |
| SOT-1409 | quarantine_governance.release_criteria.documentati... | should | quarantine_singleton_framework_enterprise | SSID_structure_level3_part3_MAX.md:473 |
| SOT-141 | governance_parameters.voting_requirements.quorum_e... | should | token_economics_distribution | SSID_structure_level3_part1_MAX.md:146 |
| SOT-1410 | quarantine_monitoring.dashboard_integration Valida... | should | quarantine_singleton_framework_enterprise | SSID_structure_level3_part3_MAX.md:473 |
| SOT-1411 | quarantine_monitoring.alert_system Validation | should | quarantine_singleton_framework_enterprise | SSID_structure_level3_part3_MAX.md:473 |
| SOT-1412 | quarantine_monitoring.reporting_integration Valida... | should | quarantine_singleton_framework_enterprise | SSID_structure_level3_part3_MAX.md:473 |
| SOT-1413 | quarantine_monitoring.competitive_intelligence Val... | should | quarantine_singleton_framework_enterprise | SSID_structure_level3_part3_MAX.md:473 |
| SOT-1414 | quarantine_monitoring.quarantine_metrics[0] Valida... | should | quarantine_singleton_framework_enterprise | SSID_structure_level3_part3_MAX.md:473 |
| SOT-1415 | quarantine_monitoring.quarantine_metrics[1] Valida... | should | quarantine_singleton_framework_enterprise | SSID_structure_level3_part3_MAX.md:473 |
| SOT-1416 | quarantine_monitoring.quarantine_metrics[2] Valida... | should | quarantine_singleton_framework_enterprise | SSID_structure_level3_part3_MAX.md:473 |
| SOT-1417 | quarantine_monitoring.quarantine_metrics[3] Valida... | should | quarantine_singleton_framework_enterprise | SSID_structure_level3_part3_MAX.md:473 |
| SOT-1418 | quarantine_monitoring.quarantine_metrics[4] Valida... | should | quarantine_singleton_framework_enterprise | SSID_structure_level3_part3_MAX.md:473 |
| SOT-1419 | quarantine_monitoring.quarantine_metrics[5] Valida... | should | quarantine_singleton_framework_enterprise | SSID_structure_level3_part3_MAX.md:473 |
| SOT-142 | governance_parameters.voting_requirements.simple_m... | should | token_economics_distribution | SSID_structure_level3_part1_MAX.md:146 |
| SOT-1420 | anti_gaming_quarantine.quarantine_gaming_detection... | should | quarantine_singleton_framework_enterprise | SSID_structure_level3_part3_MAX.md:473 |
| SOT-1421 | anti_gaming_quarantine.bypass_attempt_logging Vali... | should | quarantine_singleton_framework_enterprise | SSID_structure_level3_part3_MAX.md:473 |
| SOT-1422 | anti_gaming_quarantine.false_quarantine_prevention... | should | quarantine_singleton_framework_enterprise | SSID_structure_level3_part3_MAX.md:473 |
| SOT-1423 | anti_gaming_quarantine.quarantine_integrity_verifi... | should | quarantine_singleton_framework_enterprise | SSID_structure_level3_part3_MAX.md:473 |
| SOT-1424 | anti_gaming_quarantine.insider_threat_monitoring V... | should | quarantine_singleton_framework_enterprise | SSID_structure_level3_part3_MAX.md:473 |
| SOT-1425 | integration_points.compliance_system Validation | should | quarantine_singleton_framework_enterprise | SSID_structure_level3_part3_MAX.md:473 |
| SOT-1426 | integration_points.audit_logging Validation | should | quarantine_singleton_framework_enterprise | SSID_structure_level3_part3_MAX.md:473 |
| SOT-1427 | integration_points.governance_legal Validation | should | quarantine_singleton_framework_enterprise | SSID_structure_level3_part3_MAX.md:473 |
| SOT-1428 | integration_points.business_intelligence Validatio... | should | quarantine_singleton_framework_enterprise | SSID_structure_level3_part3_MAX.md:473 |
| SOT-1429 | integration_points.enterprise_dashboard Validation | should | quarantine_singleton_framework_enterprise | SSID_structure_level3_part3_MAX.md:473 |
| SOT-143 | governance_parameters.voting_requirements.supermaj... | should | token_economics_distribution | SSID_structure_level3_part1_MAX.md:146 |
| SOT-1430 | version Validation | should | standards_implementierung_enhanced_versioniert | SSID_structure_level3_part3_MAX.md:681 |
| SOT-1431 | date Validation | should | standards_implementierung_enhanced_versioniert | SSID_structure_level3_part3_MAX.md:681 |
| SOT-1432 | deprecated Validation | should | standards_implementierung_enhanced_versioniert | SSID_structure_level3_part3_MAX.md:681 |
| SOT-1433 | classification Validation | should | standards_implementierung_enhanced_versioniert | SSID_structure_level3_part3_MAX.md:681 |
| SOT-1434 | active_standards.W3C_VC_20.name Validation | should | standards_implementierung_enhanced_versioniert | SSID_structure_level3_part3_MAX.md:681 |
| SOT-1435 | active_standards.W3C_VC_20.path Validation | should | standards_implementierung_enhanced_versioniert | SSID_structure_level3_part3_MAX.md:681 |
| SOT-1436 | active_standards.W3C_VC_20.deprecated Validation | should | standards_implementierung_enhanced_versioniert | SSID_structure_level3_part3_MAX.md:681 |
| SOT-1437 | active_standards.W3C_VC_20.business_priority Valid... | should | standards_implementierung_enhanced_versioniert | SSID_structure_level3_part3_MAX.md:681 |
| SOT-1438 | active_standards.OpenID_Connect_4_VC.name Validati... | should | standards_implementierung_enhanced_versioniert | SSID_structure_level3_part3_MAX.md:681 |
| SOT-1439 | active_standards.OpenID_Connect_4_VC.path Validati... | should | standards_implementierung_enhanced_versioniert | SSID_structure_level3_part3_MAX.md:681 |
| SOT-144 | governance_parameters.voting_requirements.emergenc... | should | token_economics_distribution | SSID_structure_level3_part1_MAX.md:146 |
| SOT-1440 | active_standards.OpenID_Connect_4_VC.deprecated Va... | should | standards_implementierung_enhanced_versioniert | SSID_structure_level3_part3_MAX.md:681 |
| SOT-1441 | active_standards.OpenID_Connect_4_VC.business_prio... | should | standards_implementierung_enhanced_versioniert | SSID_structure_level3_part3_MAX.md:681 |
| SOT-1442 | active_standards.ISO_IEC_27001_2022.name Validatio... | should | standards_implementierung_enhanced_versioniert | SSID_structure_level3_part3_MAX.md:681 |
| SOT-1443 | active_standards.ISO_IEC_27001_2022.path Validatio... | should | standards_implementierung_enhanced_versioniert | SSID_structure_level3_part3_MAX.md:681 |
| SOT-1444 | active_standards.ISO_IEC_27001_2022.deprecated Val... | should | standards_implementierung_enhanced_versioniert | SSID_structure_level3_part3_MAX.md:681 |
| SOT-1445 | active_standards.ISO_IEC_27001_2022.business_prior... | must | standards_implementierung_enhanced_versioniert | SSID_structure_level3_part3_MAX.md:681 |
| SOT-1446 | active_standards.NIST_SSDF.name Validation | should | standards_implementierung_enhanced_versioniert | SSID_structure_level3_part3_MAX.md:681 |
| SOT-1447 | active_standards.NIST_SSDF.path Validation | should | standards_implementierung_enhanced_versioniert | SSID_structure_level3_part3_MAX.md:681 |
| SOT-1448 | active_standards.NIST_SSDF.deprecated Validation | should | standards_implementierung_enhanced_versioniert | SSID_structure_level3_part3_MAX.md:681 |
| SOT-1449 | active_standards.NIST_SSDF.business_priority Valid... | should | standards_implementierung_enhanced_versioniert | SSID_structure_level3_part3_MAX.md:681 |
| SOT-145 | governance_parameters.timelock_framework.standard_... | should | token_economics_distribution | SSID_structure_level3_part1_MAX.md:146 |
| SOT-1450 | active_standards.SLSA.name Validation | should | standards_implementierung_enhanced_versioniert | SSID_structure_level3_part3_MAX.md:681 |
| SOT-1451 | active_standards.SLSA.path Validation | should | standards_implementierung_enhanced_versioniert | SSID_structure_level3_part3_MAX.md:681 |
| SOT-1452 | active_standards.SLSA.deprecated Validation | should | standards_implementierung_enhanced_versioniert | SSID_structure_level3_part3_MAX.md:681 |
| SOT-1453 | active_standards.SLSA.business_priority Validation | should | standards_implementierung_enhanced_versioniert | SSID_structure_level3_part3_MAX.md:681 |
| SOT-1454 | deprecated_standards.id Validation | should | standards_implementierung_enhanced_versioniert | SSID_structure_level3_part3_MAX.md:681 |
| SOT-1455 | deprecated_standards.status Validation | should | standards_implementierung_enhanced_versioniert | SSID_structure_level3_part3_MAX.md:681 |
| SOT-1456 | deprecated_standards.deprecated Validation | should | standards_implementierung_enhanced_versioniert | SSID_structure_level3_part3_MAX.md:681 |
| SOT-1457 | deprecated_standards.replaced_by Validation | should | standards_implementierung_enhanced_versioniert | SSID_structure_level3_part3_MAX.md:681 |
| SOT-1458 | deprecated_standards.migration_deadline Validation | should | standards_implementierung_enhanced_versioniert | SSID_structure_level3_part3_MAX.md:681 |
| SOT-1459 | deprecated_standards.business_impact Validation | must | standards_implementierung_enhanced_versioniert | SSID_structure_level3_part3_MAX.md:681 |
| SOT-146 | governance_parameters.timelock_framework.protocol_... | should | token_economics_distribution | SSID_structure_level3_part1_MAX.md:146 |
| SOT-1460 | version Validation | should | internal_review_requirements_enterprise | SSID_structure_level3_part3_MAX.md:731 |
| SOT-1461 | deprecated Validation | should | internal_review_requirements_enterprise | SSID_structure_level3_part3_MAX.md:731 |
| SOT-1462 | classification Validation | should | internal_review_requirements_enterprise | SSID_structure_level3_part3_MAX.md:731 |
| SOT-1463 | internal_reviews.monthly.scope Validation | should | internal_review_requirements_enterprise | SSID_structure_level3_part3_MAX.md:731 |
| SOT-1464 | internal_reviews.monthly.owner Validation | should | internal_review_requirements_enterprise | SSID_structure_level3_part3_MAX.md:731 |
| SOT-1465 | internal_reviews.monthly.deliverable Validation | should | internal_review_requirements_enterprise | SSID_structure_level3_part3_MAX.md:731 |
| SOT-1466 | internal_reviews.monthly.classification Validation | should | internal_review_requirements_enterprise | SSID_structure_level3_part3_MAX.md:731 |
| SOT-1467 | internal_reviews.monthly.business_review Validatio... | should | internal_review_requirements_enterprise | SSID_structure_level3_part3_MAX.md:731 |
| SOT-1468 | internal_reviews.quarterly.scope Validation | should | internal_review_requirements_enterprise | SSID_structure_level3_part3_MAX.md:731 |
| SOT-1469 | internal_reviews.quarterly.owner Validation | should | internal_review_requirements_enterprise | SSID_structure_level3_part3_MAX.md:731 |
| SOT-147 | governance_parameters.timelock_framework.parameter... | should | token_economics_distribution | SSID_structure_level3_part1_MAX.md:146 |
| SOT-1470 | internal_reviews.quarterly.deliverable Validation | should | internal_review_requirements_enterprise | SSID_structure_level3_part3_MAX.md:731 |
| SOT-1471 | internal_reviews.quarterly.classification Validati... | should | internal_review_requirements_enterprise | SSID_structure_level3_part3_MAX.md:731 |
| SOT-1472 | internal_reviews.quarterly.external_validation Val... | have | internal_review_requirements_enterprise | SSID_structure_level3_part3_MAX.md:731 |
| SOT-1473 | internal_reviews.quarterly.board_reporting Validat... | should | internal_review_requirements_enterprise | SSID_structure_level3_part3_MAX.md:731 |
| SOT-1474 | internal_reviews.semi_annual.scope Validation | should | internal_review_requirements_enterprise | SSID_structure_level3_part3_MAX.md:731 |
| SOT-1475 | internal_reviews.semi_annual.owner Validation | should | internal_review_requirements_enterprise | SSID_structure_level3_part3_MAX.md:731 |
| SOT-1476 | internal_reviews.semi_annual.deliverable Validatio... | should | internal_review_requirements_enterprise | SSID_structure_level3_part3_MAX.md:731 |
| SOT-1477 | internal_reviews.semi_annual.classification Valida... | should | internal_review_requirements_enterprise | SSID_structure_level3_part3_MAX.md:731 |
| SOT-1478 | internal_reviews.semi_annual.c_suite_presentation ... | should | internal_review_requirements_enterprise | SSID_structure_level3_part3_MAX.md:731 |
| SOT-1479 | external_reviews.frequency Validation | should | internal_review_requirements_enterprise | SSID_structure_level3_part3_MAX.md:731 |
| SOT-148 | governance_parameters.timelock_framework.emergency... | should | token_economics_distribution | SSID_structure_level3_part1_MAX.md:146 |
| SOT-1480 | external_reviews.mandatory Validation | must | internal_review_requirements_enterprise | SSID_structure_level3_part3_MAX.md:731 |
| SOT-1481 | external_reviews.scope Validation | should | internal_review_requirements_enterprise | SSID_structure_level3_part3_MAX.md:731 |
| SOT-1482 | external_reviews.deliverable Validation | should | internal_review_requirements_enterprise | SSID_structure_level3_part3_MAX.md:731 |
| SOT-1483 | external_reviews.confidentiality_agreement Validat... | must | internal_review_requirements_enterprise | SSID_structure_level3_part3_MAX.md:731 |
| SOT-1484 | external_reviews.clearance_verification Validation | should | internal_review_requirements_enterprise | SSID_structure_level3_part3_MAX.md:731 |
| SOT-1485 | Critical Issues: [Number] | must | executive_summary | SSID_structure_level3_part3_MAX.md:783 |
| SOT-1486 | Business Risks: [High/Medium/Low] | should | executive_summary | SSID_structure_level3_part3_MAX.md:784 |
| SOT-1487 | Business-Critical Markets: | must | compliance_matrix_review_enterprise | SSID_structure_level3_part3_MAX.md:791 |
| SOT-1488 | Required Actions: [List with timelines and busines... | must | regulatory_horizon_scanning_business_focus | SSID_structure_level3_part3_MAX.md:835 |
| SOT-1489 | Investment Decisions Required: [List with amounts] | must | board_reporting_summary | SSID_structure_level3_part3_MAX.md:843 |
| SOT-149 | governance_parameters.timelock_framework.treasury_... | should | token_economics_distribution | SSID_structure_level3_part1_MAX.md:146 |
| SOT-1490 | External Review Required: [Yes/No] | must | next_review | SSID_structure_level3_part3_MAX.md:850 |
| SOT-1491 | MUST/OPTIONAL Compliance (Level 2) | must | ci_gate_implementation_clarification | SSID_structure_level3_part3_MAX.md:871 |
| SOT-1492 | **"Business-Critical"**: Compliance-Status kritisc... | must | compliance_claims_disclaimer_internal | SSID_structure_level3_part3_MAX.md:897 |
| SOT-1493 | version Validation | should | quarantine_framework_canonical | SSID_structure_level3_part3_MAX.md:908 |
| SOT-1494 | date Validation | should | quarantine_framework_canonical | SSID_structure_level3_part3_MAX.md:908 |
| SOT-1495 | deprecated Validation | should | quarantine_framework_canonical | SSID_structure_level3_part3_MAX.md:908 |
| SOT-1496 | classification Validation | should | quarantine_framework_canonical | SSID_structure_level3_part3_MAX.md:908 |
| SOT-1497 | quarantine_structure.canonical_path Validation | should | quarantine_framework_canonical | SSID_structure_level3_part3_MAX.md:908 |
| SOT-1498 | quarantine_structure.subfolders.staging Validation | should | quarantine_framework_canonical | SSID_structure_level3_part3_MAX.md:908 |
| SOT-1499 | quarantine_structure.subfolders.triage Validation | should | quarantine_framework_canonical | SSID_structure_level3_part3_MAX.md:908 |
| SOT-150 | governance_parameters.voting_periods.standard_voti... | should | token_economics_distribution | SSID_structure_level3_part1_MAX.md:146 |
| SOT-1500 | quarantine_structure.subfolders.hash_buckets Valid... | should | quarantine_framework_canonical | SSID_structure_level3_part3_MAX.md:908 |
| SOT-1501 | quarantine_structure.subfolders.quarantined Valida... | should | quarantine_framework_canonical | SSID_structure_level3_part3_MAX.md:908 |
| SOT-1502 | quarantine_structure.processing Validation | should | quarantine_framework_canonical | SSID_structure_level3_part3_MAX.md:908 |
| SOT-1503 | quarantine_structure.retention Validation | should | quarantine_framework_canonical | SSID_structure_level3_part3_MAX.md:908 |
| SOT-1504 | quarantine_structure.hash_ledger Validation | should | quarantine_framework_canonical | SSID_structure_level3_part3_MAX.md:908 |
| SOT-1505 | quarantine_structure.evidence_path Validation | should | quarantine_framework_canonical | SSID_structure_level3_part3_MAX.md:908 |
| SOT-1506 | quarantine_structure.hash_ledger_export Validation | should | quarantine_framework_canonical | SSID_structure_level3_part3_MAX.md:908 |
| SOT-1507 | quarantine_structure.evidence_path_note Validation | should | quarantine_framework_canonical | SSID_structure_level3_part3_MAX.md:908 |
| SOT-1508 | forbidden_locations[0] Validation | should | quarantine_framework_canonical | SSID_structure_level3_part3_MAX.md:908 |
| SOT-1509 | forbidden_locations[1] Validation | should | quarantine_framework_canonical | SSID_structure_level3_part3_MAX.md:908 |
| SOT-151 | governance_parameters.voting_periods.protocol_upgr... | should | token_economics_distribution | SSID_structure_level3_part1_MAX.md:146 |
| SOT-1510 | forbidden_locations[2] Validation | should | quarantine_framework_canonical | SSID_structure_level3_part3_MAX.md:908 |
| SOT-1511 | forbidden_locations[3] Validation | should | quarantine_framework_canonical | SSID_structure_level3_part3_MAX.md:908 |
| SOT-1512 | retention_policy.staging_retention Validation | should | quarantine_framework_canonical | SSID_structure_level3_part3_MAX.md:908 |
| SOT-1513 | retention_policy.triage_retention Validation | should | quarantine_framework_canonical | SSID_structure_level3_part3_MAX.md:908 |
| SOT-1514 | retention_policy.quarantined_retention Validation | should | quarantine_framework_canonical | SSID_structure_level3_part3_MAX.md:908 |
| SOT-1515 | retention_policy.hash_evidence_retention Validatio... | should | quarantine_framework_canonical | SSID_structure_level3_part3_MAX.md:908 |
| SOT-1516 | security_controls.read_only_quarantine Validation | should | quarantine_framework_canonical | SSID_structure_level3_part3_MAX.md:908 |
| SOT-1517 | security_controls.hash_verification Validation | should | quarantine_framework_canonical | SSID_structure_level3_part3_MAX.md:908 |
| SOT-1518 | security_controls.evidence_immutable Validation | should | quarantine_framework_canonical | SSID_structure_level3_part3_MAX.md:908 |
| SOT-1519 | security_controls.worm_compliance Validation | should | quarantine_framework_canonical | SSID_structure_level3_part3_MAX.md:908 |
| SOT-152 | governance_parameters.voting_periods.emergency_vot... | should | token_economics_distribution | SSID_structure_level3_part1_MAX.md:146 |
| SOT-1520 | Healthcare organizations and critical infrastructu... | must | opencore_integration_summary_fully_integrated_feat | SSID_structure_level3_part3_MAX.md:1052 |
| SOT-1521 | `24_meta_orchestration/triggers/ci/gates/structure... | must | maximalstand_addendum_ci_gates_tests_erzwingen_ebe | SSID_structure_level3_part3_MAX.md:1147 |
| SOT-1522 | **FAIL (Exit 24)**, wenn | must | ci_gate_anpassungen_erzwingen_semantik | SSID_structure_level3_part3_MAX.md:1202 |
| SOT-1523 | [Kritische Policies](#kritische-policies) | must | inhaltsverzeichnis | ssid_master_definition_corrected_v1.1.1.md:21 |
| SOT-1524 | metadata.shard_id Validation | should | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:438 |
| SOT-1525 | metadata.version Validation | should | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:438 |
| SOT-1526 | metadata.status Validation | should | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:438 |
| SOT-1527 | capabilities.MUST[0] Validation | must | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:438 |
| SOT-1528 | capabilities.SHOULD[0] Validation | should | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:438 |
| SOT-1529 | capabilities.HAVE[0] Validation | have | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:438 |
| SOT-153 | governance_parameters.voting_periods.parameter_vot... | should | token_economics_distribution | SSID_structure_level3_part1_MAX.md:146 |
| SOT-1530 | constraints.pii_storage Validation | should | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:438 |
| SOT-1531 | constraints.data_policy Validation | should | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:438 |
| SOT-1532 | constraints.custody Validation | should | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:438 |
| SOT-1533 | enforcement.static_analysis[0] Validation | should | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:438 |
| SOT-1534 | enforcement.static_analysis[1] Validation | should | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:438 |
| SOT-1535 | enforcement.runtime_checks[0] Validation | should | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:438 |
| SOT-1536 | enforcement.audit.log_to Validation | should | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:438 |
| SOT-1537 | interfaces.contracts[0] Validation | should | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:438 |
| SOT-1538 | interfaces.data_schemas[0] Validation | should | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:438 |
| SOT-1539 | interfaces.authentication Validation | should | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:438 |
| SOT-154 | governance_parameters.delegation_system.delegation... | should | token_economics_distribution | SSID_structure_level3_part1_MAX.md:146 |
| SOT-1540 | dependencies.required[0] Validation | must | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:438 |
| SOT-1541 | dependencies.optional[0] Validation | have | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:438 |
| SOT-1542 | compatibility.semver Validation | should | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:438 |
| SOT-1543 | compatibility.core_min_version Validation | should | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:438 |
| SOT-1544 | implementations.default Validation | have | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:438 |
| SOT-1545 | implementations.available[0] Validation | have | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:438 |
| SOT-1546 | implementations.available[1] Validation | should | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:438 |
| SOT-1547 | implementations.available[2] Validation | should | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:438 |
| SOT-1548 | conformance.test_framework Validation | should | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:438 |
| SOT-1549 | conformance.contract_tests[0] Validation | should | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:438 |
| SOT-155 | governance_parameters.delegation_system.self_deleg... | should | token_economics_distribution | SSID_structure_level3_part1_MAX.md:146 |
| SOT-1550 | orchestration.workflows[0] Validation | have | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:438 |
| SOT-1551 | documentation.auto_generate[0] Validation | should | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:438 |
| SOT-1552 | documentation.auto_generate[1] Validation | should | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:438 |
| SOT-1553 | documentation.manual[0] Validation | should | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:438 |
| SOT-1554 | observability.logging.pii_redaction Validation | should | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:438 |
| SOT-1555 | evidence.strategy Validation | should | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:438 |
| SOT-1556 | evidence.anchoring.chains[0] Validation | should | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:438 |
| SOT-1557 | evidence.anchoring.chains[1] Validation | should | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:438 |
| SOT-1558 | security.threat_model Validation | should | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:438 |
| SOT-1559 | security.secrets_management Validation | should | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:438 |
| SOT-156 | governance_parameters.delegation_system.delegation... | should | token_economics_distribution | SSID_structure_level3_part1_MAX.md:146 |
| SOT-1560 | deployment.strategy Validation | should | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:438 |
| SOT-1561 | deployment.environments[0] Validation | should | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:438 |
| SOT-1562 | deployment.environments[1] Validation | should | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:438 |
| SOT-1563 | deployment.environments[2] Validation | should | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:438 |
| SOT-1564 | roadmap.upcoming[0] Validation | should | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:438 |
| SOT-1565 | roadmap.upcoming[1] Validation | should | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:438 |
| SOT-1566 | metadata.implementation_id Validation | have | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:533 |
| SOT-1567 | metadata.implementation_version Validation | should | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:533 |
| SOT-1568 | metadata.chart_version Validation | should | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:533 |
| SOT-1569 | metadata.maturity Validation | should | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:533 |
| SOT-157 | governance_parameters.delegation_system.vote_weigh... | should | token_economics_distribution | SSID_structure_level3_part1_MAX.md:146 |
| SOT-1570 | technology_stack.language.name Validation | should | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:533 |
| SOT-1571 | technology_stack.language.version Validation | should | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:533 |
| SOT-1572 | technology_stack.testing[0] Validation | should | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:533 |
| SOT-1573 | technology_stack.testing[1] Validation | should | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:533 |
| SOT-1574 | technology_stack.linting_formatting[0] Validation | should | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:533 |
| SOT-1575 | technology_stack.linting_formatting[1] Validation | should | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:533 |
| SOT-1576 | technology_stack.linting_formatting[2] Validation | should | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:533 |
| SOT-1577 | technology_stack.linting_formatting[3] Validation | should | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:533 |
| SOT-1578 | artifacts.source_code.location Validation | should | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:533 |
| SOT-1579 | artifacts.source_code.structure[0] Validation | should | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:533 |
| SOT-158 | governance_parameters.governance_rewards.voter_par... | should | token_economics_distribution | SSID_structure_level3_part1_MAX.md:146 |
| SOT-1580 | artifacts.source_code.structure[1] Validation | should | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:533 |
| SOT-1581 | artifacts.source_code.structure[2] Validation | should | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:533 |
| SOT-1582 | artifacts.source_code.structure[3] Validation | should | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:533 |
| SOT-1583 | artifacts.source_code.structure[4] Validation | should | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:533 |
| SOT-1584 | artifacts.configuration.location Validation | should | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:533 |
| SOT-1585 | artifacts.configuration.files[0] Validation | should | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:533 |
| SOT-1586 | artifacts.configuration.files[1] Validation | should | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:533 |
| SOT-1587 | artifacts.configuration.files[2] Validation | should | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:533 |
| SOT-1588 | artifacts.models.location Validation | should | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:533 |
| SOT-1589 | artifacts.models.files[0] Validation | should | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:533 |
| SOT-159 | governance_parameters.governance_rewards.proposal_... | should | token_economics_distribution | SSID_structure_level3_part1_MAX.md:146 |
| SOT-1590 | artifacts.models.files[1] Validation | should | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:533 |
| SOT-1591 | artifacts.protocols.location Validation | should | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:533 |
| SOT-1592 | artifacts.tests.location Validation | should | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:533 |
| SOT-1593 | artifacts.documentation.location Validation | should | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:533 |
| SOT-1594 | artifacts.scripts.location Validation | should | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:533 |
| SOT-1595 | artifacts.docker.files[0] Validation | should | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:533 |
| SOT-1596 | artifacts.docker.files[1] Validation | should | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:533 |
| SOT-1597 | dependencies.python_packages Validation | should | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:533 |
| SOT-1598 | dependencies.development_packages Validation | should | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:533 |
| SOT-1599 | dependencies.system_dependencies[0] Validation | should | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:533 |
| SOT-160 | governance_parameters.governance_rewards.delegate_... | should | token_economics_distribution | SSID_structure_level3_part1_MAX.md:146 |
| SOT-1600 | dependencies.system_dependencies[1] Validation | should | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:533 |
| SOT-1601 | dependencies.external_services[0] Validation | should | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:533 |
| SOT-1602 | dependencies.external_services[1] Validation | should | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:533 |
| SOT-1603 | dependencies.external_services[2] Validation | should | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:533 |
| SOT-1604 | deployment.kubernetes.manifests_location Validatio... | should | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:533 |
| SOT-1605 | deployment.helm.chart_location Validation | should | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:533 |
| SOT-1606 | testing.unit_tests.coverage_target Validation | should | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:533 |
| SOT-1607 | observability.metrics.exporter Validation | should | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:533 |
| SOT-1608 | observability.tracing.exporter Validation | should | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:533 |
| SOT-1609 | observability.logging.format Validation | should | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:533 |
| SOT-161 | governance_parameters.governance_rewards.minimum_p... | should | token_economics_distribution | SSID_structure_level3_part1_MAX.md:146 |
| SOT-1610 | observability.logging.pii_redaction Validation | should | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:533 |
| SOT-1611 | performance.baseline_benchmarks[0] Validation | should | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:533 |
| SOT-1612 | performance.optimization_targets[0] Validation | should | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:533 |
| SOT-1613 | changelog.location Validation | should | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:533 |
| SOT-1614 | changelog.latest_versions[0] Validation | should | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:533 |
| SOT-1615 | support.documentation Validation | should | hauptsektionen | ssid_master_definition_corrected_v1.1.1.md:533 |
| SOT-1616 | data_policy.storage_type Validation | should | 2_hash_only_data_policy | ssid_master_definition_corrected_v1.1.1.md:679 |
| SOT-1617 | data_policy.hash_algorithm Validation | should | 2_hash_only_data_policy | ssid_master_definition_corrected_v1.1.1.md:679 |
| SOT-1618 | data_policy.pepper_strategy Validation | should | 2_hash_only_data_policy | ssid_master_definition_corrected_v1.1.1.md:679 |
| SOT-1619 | data_policy.deterministic Validation | should | 2_hash_only_data_policy | ssid_master_definition_corrected_v1.1.1.md:679 |
| SOT-162 | version Validation | should | translation_quality_framework | SSID_structure_level3_part1_MAX.md:353 |
| SOT-1620 | data_policy.raw_data_retention Validation | should | 2_hash_only_data_policy | ssid_master_definition_corrected_v1.1.1.md:679 |
| SOT-1621 | **RFC-Prozess:** Für alle MUST-Capability-Änderung... | must | 7_versioning_breaking_changes | ssid_master_definition_corrected_v1.1.1.md:717 |
| SOT-1622 | Entscheidet über SHOULD/HAVE-Promotions | should | owner_pro_shard | ssid_master_definition_corrected_v1.1.1.md:727 |
| SOT-1623 | RFC erstellen (für MUST-Changes) | must | change_prozess | ssid_master_definition_corrected_v1.1.1.md:748 |
| SOT-1624 | Python-TensorFlow (Production) | have | 3_multi_implementation_support | ssid_master_definition_corrected_v1.1.1.md:817 |
| SOT-1625 | [ ] Workflow-Definitionen (z.B. full_kyc_flow) | have | phase_5_cross_root_orchestration | ssid_master_definition_corrected_v1.1.1.md:919 |
| SOT-1626 | **ML:** TensorFlow, PyTorch, Scikit-Learn | have | tools_frameworks | ssid_master_definition_corrected_v1.1.1.md:950 |
| SOT-1627 | country_specific.uk.ico_uk_gdpr.mandatory Validati... | must | 1_regulatory_matrix_uk_apac_country_specific | ssid_master_definition_corrected_v1.1.1.md:976 |
| SOT-1628 | country_specific.uk.ico_uk_gdpr.requirements.dpa_2... | should | 1_regulatory_matrix_uk_apac_country_specific | ssid_master_definition_corrected_v1.1.1.md:976 |
| SOT-1629 | country_specific.uk.ico_uk_gdpr.requirements.dpo_c... | should | 1_regulatory_matrix_uk_apac_country_specific | ssid_master_definition_corrected_v1.1.1.md:976 |
| SOT-163 | date Validation | should | translation_quality_framework | SSID_structure_level3_part1_MAX.md:353 |
| SOT-1630 | country_specific.singapore.mas_pdpa.mandatory Vali... | must | 1_regulatory_matrix_uk_apac_country_specific | ssid_master_definition_corrected_v1.1.1.md:976 |
| SOT-1631 | country_specific.singapore.mas_pdpa.requirements.d... | should | 1_regulatory_matrix_uk_apac_country_specific | ssid_master_definition_corrected_v1.1.1.md:976 |
| SOT-1632 | country_specific.singapore.mas_pdpa.requirements.c... | should | 1_regulatory_matrix_uk_apac_country_specific | ssid_master_definition_corrected_v1.1.1.md:976 |
| SOT-1633 | country_specific.japan.jfsa_appi.mandatory Validat... | must | 1_regulatory_matrix_uk_apac_country_specific | ssid_master_definition_corrected_v1.1.1.md:976 |
| SOT-1634 | country_specific.japan.jfsa_appi.requirements.cros... | should | 1_regulatory_matrix_uk_apac_country_specific | ssid_master_definition_corrected_v1.1.1.md:976 |
| SOT-1635 | country_specific.australia.au_privacy_act_1988.man... | must | 1_regulatory_matrix_uk_apac_country_specific | ssid_master_definition_corrected_v1.1.1.md:976 |
| SOT-1636 | country_specific.australia.au_privacy_act_1988.req... | should | 1_regulatory_matrix_uk_apac_country_specific | ssid_master_definition_corrected_v1.1.1.md:976 |
| SOT-1637 | True.push.branches[0] Validation | should | 3_ci_workflows_schedules_artifacts | ssid_master_definition_corrected_v1.1.1.md:1009 |
| SOT-1638 | True.push.branches[1] Validation | should | 3_ci_workflows_schedules_artifacts | ssid_master_definition_corrected_v1.1.1.md:1009 |
| SOT-1639 | True.pull_request.branches[0] Validation | should | 3_ci_workflows_schedules_artifacts | ssid_master_definition_corrected_v1.1.1.md:1009 |
| SOT-164 | deprecated Validation | should | translation_quality_framework | SSID_structure_level3_part1_MAX.md:353 |
| SOT-1640 | True.pull_request.branches[1] Validation | should | 3_ci_workflows_schedules_artifacts | ssid_master_definition_corrected_v1.1.1.md:1009 |
| SOT-1641 | True.schedule.cron Validation | should | 3_ci_workflows_schedules_artifacts | ssid_master_definition_corrected_v1.1.1.md:1009 |
| SOT-1642 | True.schedule.cron Validation | should | 3_ci_workflows_schedules_artifacts | ssid_master_definition_corrected_v1.1.1.md:1009 |
| SOT-1643 | **Artifacts:** Einheitlich `actions/upload-artifac... | have | 3_ci_workflows_schedules_artifacts | ssid_master_definition_corrected_v1.1.1.md:1020 |
| SOT-1644 | version Validation | should | 4_sanctions_workflow_entities_freshness | ssid_master_definition_corrected_v1.1.1.md:1032 |
| SOT-1645 | last_updated Validation | should | 4_sanctions_workflow_entities_freshness | ssid_master_definition_corrected_v1.1.1.md:1032 |
| SOT-1646 | sources.ofac_sdn.url Validation | should | 4_sanctions_workflow_entities_freshness | ssid_master_definition_corrected_v1.1.1.md:1032 |
| SOT-1647 | sources.ofac_sdn.sha256 Validation | should | 4_sanctions_workflow_entities_freshness | ssid_master_definition_corrected_v1.1.1.md:1032 |
| SOT-1648 | sources.eu_consolidated.url Validation | should | 4_sanctions_workflow_entities_freshness | ssid_master_definition_corrected_v1.1.1.md:1032 |
| SOT-1649 | sources.eu_consolidated.sha256 Validation | should | 4_sanctions_workflow_entities_freshness | ssid_master_definition_corrected_v1.1.1.md:1032 |
| SOT-165 | quality_standards.accuracy_threshold Validation | should | translation_quality_framework | SSID_structure_level3_part1_MAX.md:353 |
| SOT-1650 | freshness_policy.max_age_hours Validation | should | 4_sanctions_workflow_entities_freshness | ssid_master_definition_corrected_v1.1.1.md:1032 |
| SOT-166 | quality_standards.consistency_score Validation | should | translation_quality_framework | SSID_structure_level3_part1_MAX.md:353 |
| SOT-167 | quality_standards.cultural_appropriateness Validat... | must | translation_quality_framework | SSID_structure_level3_part1_MAX.md:353 |
| SOT-168 | quality_standards.technical_precision Validation | should | translation_quality_framework | SSID_structure_level3_part1_MAX.md:353 |
| SOT-169 | translation_workflow.step_1 Validation | have | translation_quality_framework | SSID_structure_level3_part1_MAX.md:353 |
| SOT-170 | translation_workflow.step_2 Validation | have | translation_quality_framework | SSID_structure_level3_part1_MAX.md:353 |
| SOT-171 | translation_workflow.step_3 Validation | have | translation_quality_framework | SSID_structure_level3_part1_MAX.md:353 |
| SOT-172 | translation_workflow.step_4 Validation | have | translation_quality_framework | SSID_structure_level3_part1_MAX.md:353 |
| SOT-173 | translation_workflow.step_5 Validation | have | translation_quality_framework | SSID_structure_level3_part1_MAX.md:353 |
| SOT-174 | maintenance_schedule.major_updates Validation | should | translation_quality_framework | SSID_structure_level3_part1_MAX.md:353 |
| SOT-175 | maintenance_schedule.minor_updates Validation | should | translation_quality_framework | SSID_structure_level3_part1_MAX.md:353 |
| SOT-176 | maintenance_schedule.urgent_updates Validation | should | translation_quality_framework | SSID_structure_level3_part1_MAX.md:353 |
| SOT-177 | maintenance_schedule.quarterly_review Validation | should | translation_quality_framework | SSID_structure_level3_part1_MAX.md:353 |
| SOT-178 | specialized_terminology.legal_terms Validation | must | translation_quality_framework | SSID_structure_level3_part1_MAX.md:353 |
| SOT-179 | specialized_terminology.regulatory_terms Validatio... | should | translation_quality_framework | SSID_structure_level3_part1_MAX.md:353 |
| SOT-180 | specialized_terminology.technical_terms Validation | should | translation_quality_framework | SSID_structure_level3_part1_MAX.md:353 |
| SOT-181 | specialized_terminology.business_terms Validation | should | translation_quality_framework | SSID_structure_level3_part1_MAX.md:353 |
| SOT-182 | Independent legal review mandatory | must | recommended_use_cases | SSID_structure_level3_part1_MAX.md:423 |
| SOT-183 | Local regulatory validation required | must | recommended_use_cases | SSID_structure_level3_part1_MAX.md:424 |
| SOT-184 | Professional compliance consultation recommended | should | recommended_use_cases | SSID_structure_level3_part1_MAX.md:425 |
| SOT-185 | version Validation | should | stakeholder_investor_protection | SSID_structure_level3_part1_MAX.md:461 |
| SOT-186 | date Validation | should | stakeholder_investor_protection | SSID_structure_level3_part1_MAX.md:461 |
| SOT-187 | deprecated Validation | should | stakeholder_investor_protection | SSID_structure_level3_part1_MAX.md:461 |
| SOT-188 | classification Validation | should | stakeholder_investor_protection | SSID_structure_level3_part1_MAX.md:461 |
| SOT-189 | investment_disclaimers.no_public_offer Validation | should | stakeholder_investor_protection | SSID_structure_level3_part1_MAX.md:461 |
| SOT-190 | investment_disclaimers.no_investment_vehicle Valid... | should | stakeholder_investor_protection | SSID_structure_level3_part1_MAX.md:461 |
| SOT-191 | investment_disclaimers.no_yield_promises Validatio... | should | stakeholder_investor_protection | SSID_structure_level3_part1_MAX.md:461 |
| SOT-192 | investment_disclaimers.no_custody_services Validat... | should | stakeholder_investor_protection | SSID_structure_level3_part1_MAX.md:461 |
| SOT-193 | investment_disclaimers.no_financial_advice Validat... | should | stakeholder_investor_protection | SSID_structure_level3_part1_MAX.md:461 |
| SOT-194 | investment_disclaimers.no_solicitation Validation | should | stakeholder_investor_protection | SSID_structure_level3_part1_MAX.md:461 |
| SOT-195 | legal_position.framework_purpose Validation | should | stakeholder_investor_protection | SSID_structure_level3_part1_MAX.md:461 |
| SOT-196 | legal_position.token_purpose Validation | should | stakeholder_investor_protection | SSID_structure_level3_part1_MAX.md:461 |
| SOT-197 | legal_position.business_model Validation | should | stakeholder_investor_protection | SSID_structure_level3_part1_MAX.md:461 |
| SOT-198 | legal_position.revenue_source Validation | should | stakeholder_investor_protection | SSID_structure_level3_part1_MAX.md:461 |
| SOT-199 | prohibited_representations[0] Validation | should | stakeholder_investor_protection | SSID_structure_level3_part1_MAX.md:461 |
| SOT-200 | prohibited_representations[1] Validation | should | stakeholder_investor_protection | SSID_structure_level3_part1_MAX.md:461 |
| SOT-201 | prohibited_representations[2] Validation | should | stakeholder_investor_protection | SSID_structure_level3_part1_MAX.md:461 |
| SOT-202 | prohibited_representations[3] Validation | should | stakeholder_investor_protection | SSID_structure_level3_part1_MAX.md:461 |
| SOT-203 | prohibited_representations[4] Validation | should | stakeholder_investor_protection | SSID_structure_level3_part1_MAX.md:461 |
| SOT-204 | prohibited_representations[5] Validation | should | stakeholder_investor_protection | SSID_structure_level3_part1_MAX.md:461 |
| SOT-205 | compliance_statements.securities_law Validation | should | stakeholder_investor_protection | SSID_structure_level3_part1_MAX.md:461 |
| SOT-206 | compliance_statements.money_transmission Validatio... | should | stakeholder_investor_protection | SSID_structure_level3_part1_MAX.md:461 |
| SOT-207 | compliance_statements.banking_services Validation | should | stakeholder_investor_protection | SSID_structure_level3_part1_MAX.md:461 |
| SOT-208 | compliance_statements.investment_advice Validation | should | stakeholder_investor_protection | SSID_structure_level3_part1_MAX.md:461 |
| SOT-209 | user_responsibilities.regulatory_compliance Valida... | should | stakeholder_investor_protection | SSID_structure_level3_part1_MAX.md:461 |
| SOT-210 | user_responsibilities.tax_obligations Validation | should | stakeholder_investor_protection | SSID_structure_level3_part1_MAX.md:461 |
| SOT-211 | user_responsibilities.legal_validation Validation | must | stakeholder_investor_protection | SSID_structure_level3_part1_MAX.md:461 |
| SOT-212 | user_responsibilities.risk_assessment Validation | must | stakeholder_investor_protection | SSID_structure_level3_part1_MAX.md:461 |
| SOT-213 | regulatory_safe_harbor.eu_mica_compliance Validati... | should | stakeholder_investor_protection | SSID_structure_level3_part1_MAX.md:461 |
| SOT-214 | regulatory_safe_harbor.us_securities_law Validatio... | should | stakeholder_investor_protection | SSID_structure_level3_part1_MAX.md:461 |
| SOT-215 | regulatory_safe_harbor.uk_fca_compliance Validatio... | should | stakeholder_investor_protection | SSID_structure_level3_part1_MAX.md:461 |
| SOT-216 | regulatory_safe_harbor.singapore_mas Validation | should | stakeholder_investor_protection | SSID_structure_level3_part1_MAX.md:461 |
| SOT-217 | regulatory_safe_harbor.switzerland_finma Validatio... | should | stakeholder_investor_protection | SSID_structure_level3_part1_MAX.md:461 |
| SOT-218 | version Validation | should | enterprise_partnership_framework | SSID_structure_level3_part1_MAX.md:511 |
| SOT-219 | date Validation | should | enterprise_partnership_framework | SSID_structure_level3_part1_MAX.md:511 |
| SOT-220 | deprecated Validation | should | enterprise_partnership_framework | SSID_structure_level3_part1_MAX.md:511 |
| SOT-221 | classification Validation | should | enterprise_partnership_framework | SSID_structure_level3_part1_MAX.md:511 |
| SOT-222 | partnership_tiers.tier_1_strategic.description Val... | should | enterprise_partnership_framework | SSID_structure_level3_part1_MAX.md:511 |
| SOT-223 | partnership_tiers.tier_1_strategic.benefits[0] Val... | should | enterprise_partnership_framework | SSID_structure_level3_part1_MAX.md:511 |
| SOT-224 | partnership_tiers.tier_1_strategic.benefits[1] Val... | should | enterprise_partnership_framework | SSID_structure_level3_part1_MAX.md:511 |
| SOT-225 | partnership_tiers.tier_1_strategic.benefits[2] Val... | should | enterprise_partnership_framework | SSID_structure_level3_part1_MAX.md:511 |
| SOT-226 | partnership_tiers.tier_1_strategic.requirements[0]... | should | enterprise_partnership_framework | SSID_structure_level3_part1_MAX.md:511 |
| SOT-227 | partnership_tiers.tier_1_strategic.requirements[1]... | should | enterprise_partnership_framework | SSID_structure_level3_part1_MAX.md:511 |
| SOT-228 | partnership_tiers.tier_1_strategic.requirements[2]... | should | enterprise_partnership_framework | SSID_structure_level3_part1_MAX.md:511 |
| SOT-229 | partnership_tiers.tier_2_specialized.description V... | should | enterprise_partnership_framework | SSID_structure_level3_part1_MAX.md:511 |
| SOT-230 | partnership_tiers.tier_2_specialized.benefits[0] V... | should | enterprise_partnership_framework | SSID_structure_level3_part1_MAX.md:511 |
| SOT-231 | partnership_tiers.tier_2_specialized.benefits[1] V... | should | enterprise_partnership_framework | SSID_structure_level3_part1_MAX.md:511 |
| SOT-232 | partnership_tiers.tier_2_specialized.benefits[2] V... | should | enterprise_partnership_framework | SSID_structure_level3_part1_MAX.md:511 |
| SOT-233 | partnership_tiers.tier_2_specialized.requirements[... | should | enterprise_partnership_framework | SSID_structure_level3_part1_MAX.md:511 |
| SOT-234 | partnership_tiers.tier_2_specialized.requirements[... | should | enterprise_partnership_framework | SSID_structure_level3_part1_MAX.md:511 |
| SOT-235 | partnership_tiers.tier_3_technology.description Va... | should | enterprise_partnership_framework | SSID_structure_level3_part1_MAX.md:511 |
| SOT-236 | partnership_tiers.tier_3_technology.benefits[0] Va... | should | enterprise_partnership_framework | SSID_structure_level3_part1_MAX.md:511 |
| SOT-237 | partnership_tiers.tier_3_technology.benefits[1] Va... | should | enterprise_partnership_framework | SSID_structure_level3_part1_MAX.md:511 |
| SOT-238 | partnership_tiers.tier_3_technology.benefits[2] Va... | should | enterprise_partnership_framework | SSID_structure_level3_part1_MAX.md:511 |
| SOT-239 | partnership_tiers.tier_3_technology.requirements[0... | should | enterprise_partnership_framework | SSID_structure_level3_part1_MAX.md:511 |
| SOT-240 | partnership_tiers.tier_3_technology.requirements[1... | should | enterprise_partnership_framework | SSID_structure_level3_part1_MAX.md:511 |
| SOT-241 | partnership_benefits.revenue_sharing Validation | should | enterprise_partnership_framework | SSID_structure_level3_part1_MAX.md:511 |
| SOT-242 | partnership_benefits.technical_support Validation | should | enterprise_partnership_framework | SSID_structure_level3_part1_MAX.md:511 |
| SOT-243 | partnership_benefits.marketing_support Validation | should | enterprise_partnership_framework | SSID_structure_level3_part1_MAX.md:511 |
| SOT-244 | partnership_benefits.training_programs Validation | should | enterprise_partnership_framework | SSID_structure_level3_part1_MAX.md:511 |
| SOT-245 | partnership_requirements.legal_compliance Validati... | should | enterprise_partnership_framework | SSID_structure_level3_part1_MAX.md:511 |
| SOT-246 | partnership_requirements.technical_competence Vali... | should | enterprise_partnership_framework | SSID_structure_level3_part1_MAX.md:511 |
| SOT-247 | partnership_requirements.business_ethics Validatio... | should | enterprise_partnership_framework | SSID_structure_level3_part1_MAX.md:511 |
| SOT-248 | partnership_requirements.confidentiality Validatio... | should | enterprise_partnership_framework | SSID_structure_level3_part1_MAX.md:511 |
| SOT-249 | version Validation | should | version_control_deprecation_strategy | SSID_structure_level3_part1_MAX.md:550 |
| SOT-250 | date Validation | should | version_control_deprecation_strategy | SSID_structure_level3_part1_MAX.md:550 |
| SOT-251 | deprecated Validation | should | version_control_deprecation_strategy | SSID_structure_level3_part1_MAX.md:550 |
| SOT-252 | classification Validation | should | version_control_deprecation_strategy | SSID_structure_level3_part1_MAX.md:550 |
| SOT-253 | versioning_scheme.format Validation | should | version_control_deprecation_strategy | SSID_structure_level3_part1_MAX.md:550 |
| SOT-254 | versioning_scheme.major_changes Validation | should | version_control_deprecation_strategy | SSID_structure_level3_part1_MAX.md:550 |
| SOT-255 | versioning_scheme.minor_changes Validation | should | version_control_deprecation_strategy | SSID_structure_level3_part1_MAX.md:550 |
| SOT-256 | versioning_scheme.patch_changes Validation | should | version_control_deprecation_strategy | SSID_structure_level3_part1_MAX.md:550 |
| SOT-257 | current_version.version Validation | should | version_control_deprecation_strategy | SSID_structure_level3_part1_MAX.md:550 |
| SOT-258 | current_version.release_date Validation | should | version_control_deprecation_strategy | SSID_structure_level3_part1_MAX.md:550 |
| SOT-259 | current_version.codename Validation | should | version_control_deprecation_strategy | SSID_structure_level3_part1_MAX.md:550 |
| SOT-260 | current_version.lts_status Validation | should | version_control_deprecation_strategy | SSID_structure_level3_part1_MAX.md:550 |
| SOT-261 | compatibility_matrix.supported_versions[0] Validat... | should | version_control_deprecation_strategy | SSID_structure_level3_part1_MAX.md:550 |
| SOT-262 | compatibility_matrix.supported_versions[1] Validat... | should | version_control_deprecation_strategy | SSID_structure_level3_part1_MAX.md:550 |
| SOT-263 | compatibility_matrix.supported_versions[2] Validat... | should | version_control_deprecation_strategy | SSID_structure_level3_part1_MAX.md:550 |
| SOT-264 | compatibility_matrix.deprecated_versions[0] Valida... | should | version_control_deprecation_strategy | SSID_structure_level3_part1_MAX.md:550 |
| SOT-265 | compatibility_matrix.deprecated_versions[1] Valida... | should | version_control_deprecation_strategy | SSID_structure_level3_part1_MAX.md:550 |
| SOT-266 | compatibility_matrix.end_of_life[0] Validation | should | version_control_deprecation_strategy | SSID_structure_level3_part1_MAX.md:550 |
| SOT-267 | compatibility_matrix.end_of_life[1] Validation | should | version_control_deprecation_strategy | SSID_structure_level3_part1_MAX.md:550 |
| SOT-268 | compatibility_matrix.end_of_life[2] Validation | should | version_control_deprecation_strategy | SSID_structure_level3_part1_MAX.md:550 |
| SOT-269 | deprecation_process.advance_notice Validation | should | version_control_deprecation_strategy | SSID_structure_level3_part1_MAX.md:550 |
| SOT-270 | deprecation_process.migration_guide Validation | should | version_control_deprecation_strategy | SSID_structure_level3_part1_MAX.md:550 |
| SOT-271 | deprecation_process.support_period Validation | should | version_control_deprecation_strategy | SSID_structure_level3_part1_MAX.md:550 |
| SOT-272 | deprecation_process.emergency_patches Validation | must | version_control_deprecation_strategy | SSID_structure_level3_part1_MAX.md:550 |
| SOT-273 | badge_validity.tied_to_version Validation | should | version_control_deprecation_strategy | SSID_structure_level3_part1_MAX.md:550 |
| SOT-274 | badge_validity.expiration_policy Validation | should | version_control_deprecation_strategy | SSID_structure_level3_part1_MAX.md:550 |
| SOT-275 | badge_validity.grace_period Validation | should | version_control_deprecation_strategy | SSID_structure_level3_part1_MAX.md:550 |
| SOT-276 | badge_validity.compatibility_check Validation | should | version_control_deprecation_strategy | SSID_structure_level3_part1_MAX.md:550 |
| SOT-277 | lts_support.lts_versions[0] Validation | should | version_control_deprecation_strategy | SSID_structure_level3_part1_MAX.md:550 |
| SOT-278 | lts_support.lts_versions[1] Validation | should | version_control_deprecation_strategy | SSID_structure_level3_part1_MAX.md:550 |
| SOT-279 | lts_support.support_duration Validation | should | version_control_deprecation_strategy | SSID_structure_level3_part1_MAX.md:550 |
| SOT-280 | lts_support.security_patches Validation | should | version_control_deprecation_strategy | SSID_structure_level3_part1_MAX.md:550 |
| SOT-281 | lts_support.enterprise_support Validation | should | version_control_deprecation_strategy | SSID_structure_level3_part1_MAX.md:550 |
| SOT-282 | version_history.v4_1_0.release_date Validation | should | version_control_deprecation_strategy | SSID_structure_level3_part1_MAX.md:550 |
| SOT-283 | version_history.v4_1_0.features[0] Validation | should | version_control_deprecation_strategy | SSID_structure_level3_part1_MAX.md:550 |
| SOT-284 | version_history.v4_1_0.features[1] Validation | should | version_control_deprecation_strategy | SSID_structure_level3_part1_MAX.md:550 |
| SOT-285 | version_history.v4_1_0.features[2] Validation | should | version_control_deprecation_strategy | SSID_structure_level3_part1_MAX.md:550 |
| SOT-286 | version_history.v4_1_0.status Validation | should | version_control_deprecation_strategy | SSID_structure_level3_part1_MAX.md:550 |
| SOT-287 | version_history.v4_0_0.release_date Validation | should | version_control_deprecation_strategy | SSID_structure_level3_part1_MAX.md:550 |
| SOT-288 | version_history.v4_0_0.features[0] Validation | should | version_control_deprecation_strategy | SSID_structure_level3_part1_MAX.md:550 |
| SOT-289 | version_history.v4_0_0.features[1] Validation | should | version_control_deprecation_strategy | SSID_structure_level3_part1_MAX.md:550 |
| SOT-290 | version_history.v4_0_0.features[2] Validation | should | version_control_deprecation_strategy | SSID_structure_level3_part1_MAX.md:550 |
| SOT-291 | version_history.v4_0_0.status Validation | should | version_control_deprecation_strategy | SSID_structure_level3_part1_MAX.md:550 |
| SOT-292 | version_history.v3_2_0.release_date Validation | should | version_control_deprecation_strategy | SSID_structure_level3_part1_MAX.md:550 |
| SOT-293 | version_history.v3_2_0.features[0] Validation | should | version_control_deprecation_strategy | SSID_structure_level3_part1_MAX.md:550 |
| SOT-294 | version_history.v3_2_0.features[1] Validation | should | version_control_deprecation_strategy | SSID_structure_level3_part1_MAX.md:550 |
| SOT-295 | version_history.v3_2_0.features[2] Validation | should | version_control_deprecation_strategy | SSID_structure_level3_part1_MAX.md:550 |
| SOT-296 | version_history.v3_2_0.status Validation | should | version_control_deprecation_strategy | SSID_structure_level3_part1_MAX.md:550 |
| SOT-297 | version Validation | should | release_management_framework | SSID_structure_level3_part1_MAX.md:610 |
| SOT-298 | date Validation | should | release_management_framework | SSID_structure_level3_part1_MAX.md:610 |
| SOT-299 | deprecated Validation | should | release_management_framework | SSID_structure_level3_part1_MAX.md:610 |
| SOT-300 | release_schedule.major_releases Validation | should | release_management_framework | SSID_structure_level3_part1_MAX.md:610 |
| SOT-301 | release_schedule.minor_releases Validation | should | release_management_framework | SSID_structure_level3_part1_MAX.md:610 |
| SOT-302 | release_schedule.patch_releases Validation | should | release_management_framework | SSID_structure_level3_part1_MAX.md:610 |
| SOT-303 | release_schedule.security_releases Validation | should | release_management_framework | SSID_structure_level3_part1_MAX.md:610 |
| SOT-304 | release_process.development_phase Validation | should | release_management_framework | SSID_structure_level3_part1_MAX.md:610 |
| SOT-305 | release_process.beta_phase Validation | should | release_management_framework | SSID_structure_level3_part1_MAX.md:610 |
| SOT-306 | release_process.release_candidate Validation | should | release_management_framework | SSID_structure_level3_part1_MAX.md:610 |
| SOT-307 | release_process.stable_release Validation | should | release_management_framework | SSID_structure_level3_part1_MAX.md:610 |
| SOT-308 | quality_gates[0] Validation | should | release_management_framework | SSID_structure_level3_part1_MAX.md:610 |
| SOT-309 | quality_gates[1] Validation | should | release_management_framework | SSID_structure_level3_part1_MAX.md:610 |
| SOT-310 | quality_gates[2] Validation | should | release_management_framework | SSID_structure_level3_part1_MAX.md:610 |
| SOT-311 | quality_gates[3] Validation | should | release_management_framework | SSID_structure_level3_part1_MAX.md:610 |
| SOT-312 | quality_gates[4] Validation | should | release_management_framework | SSID_structure_level3_part1_MAX.md:610 |
| SOT-313 | quality_gates[5] Validation | should | release_management_framework | SSID_structure_level3_part1_MAX.md:610 |
| SOT-314 | quality_gates[6] Validation | should | release_management_framework | SSID_structure_level3_part1_MAX.md:610 |
| SOT-315 | quality_gates[7] Validation | should | release_management_framework | SSID_structure_level3_part1_MAX.md:610 |
| SOT-316 | world_market_readiness.regulatory_validation Valid... | should | release_management_framework | SSID_structure_level3_part1_MAX.md:610 |
| SOT-317 | world_market_readiness.translation_completion Vali... | should | release_management_framework | SSID_structure_level3_part1_MAX.md:610 |
| SOT-318 | world_market_readiness.enterprise_testing Validati... | should | release_management_framework | SSID_structure_level3_part1_MAX.md:610 |
| SOT-319 | world_market_readiness.compliance_certification Va... | should | release_management_framework | SSID_structure_level3_part1_MAX.md:610 |
| SOT-320 | world_market_readiness.legal_clearance Validation | should | release_management_framework | SSID_structure_level3_part1_MAX.md:610 |
| SOT-321 | communication_strategy.release_notes Validation | should | release_management_framework | SSID_structure_level3_part1_MAX.md:610 |
| SOT-322 | communication_strategy.migration_guides Validation | should | release_management_framework | SSID_structure_level3_part1_MAX.md:610 |
| SOT-323 | communication_strategy.webinars Validation | should | release_management_framework | SSID_structure_level3_part1_MAX.md:610 |
| SOT-324 | communication_strategy.enterprise_briefings Valida... | should | release_management_framework | SSID_structure_level3_part1_MAX.md:610 |
| SOT-325 | communication_strategy.community_updates Validatio... | should | release_management_framework | SSID_structure_level3_part1_MAX.md:610 |
| SOT-326 | communication_strategy.press_releases Validation | should | release_management_framework | SSID_structure_level3_part1_MAX.md:610 |
| SOT-327 | version Validation | should | deprecation_management | SSID_structure_level3_part1_MAX.md:655 |
| SOT-328 | date Validation | should | deprecation_management | SSID_structure_level3_part1_MAX.md:655 |
| SOT-329 | deprecated Validation | should | deprecation_management | SSID_structure_level3_part1_MAX.md:655 |
| SOT-330 | deprecation_framework.deprecation_notice_period Va... | should | deprecation_management | SSID_structure_level3_part1_MAX.md:655 |
| SOT-331 | deprecation_framework.support_period Validation | should | deprecation_management | SSID_structure_level3_part1_MAX.md:655 |
| SOT-332 | deprecation_framework.security_support Validation | must | deprecation_management | SSID_structure_level3_part1_MAX.md:655 |
| SOT-333 | deprecation_framework.enterprise_support Validatio... | should | deprecation_management | SSID_structure_level3_part1_MAX.md:655 |
| SOT-334 | deprecation_process.phase_1_announcement Validatio... | should | deprecation_management | SSID_structure_level3_part1_MAX.md:655 |
| SOT-335 | deprecation_process.phase_2_warnings Validation | should | deprecation_management | SSID_structure_level3_part1_MAX.md:655 |
| SOT-336 | deprecation_process.phase_3_sunset Validation | should | deprecation_management | SSID_structure_level3_part1_MAX.md:655 |
| SOT-337 | deprecation_process.phase_4_support Validation | should | deprecation_management | SSID_structure_level3_part1_MAX.md:655 |
| SOT-338 | deprecation_process.phase_5_eol Validation | should | deprecation_management | SSID_structure_level3_part1_MAX.md:655 |
| SOT-339 | communication_channels.github_issues Validation | should | deprecation_management | SSID_structure_level3_part1_MAX.md:655 |
| SOT-340 | communication_channels.documentation Validation | should | deprecation_management | SSID_structure_level3_part1_MAX.md:655 |
| SOT-341 | communication_channels.release_notes Validation | should | deprecation_management | SSID_structure_level3_part1_MAX.md:655 |
| SOT-342 | communication_channels.enterprise_notifications Va... | should | deprecation_management | SSID_structure_level3_part1_MAX.md:655 |
| SOT-343 | communication_channels.community_forums Validation | should | deprecation_management | SSID_structure_level3_part1_MAX.md:655 |
| SOT-344 | migration_support.automated_tools Validation | should | deprecation_management | SSID_structure_level3_part1_MAX.md:655 |
| SOT-345 | migration_support.documentation Validation | should | deprecation_management | SSID_structure_level3_part1_MAX.md:655 |
| SOT-346 | migration_support.community_support Validation | should | deprecation_management | SSID_structure_level3_part1_MAX.md:655 |
| SOT-347 | migration_support.enterprise_services Validation | should | deprecation_management | SSID_structure_level3_part1_MAX.md:655 |
| SOT-348 | migration_support.training_materials Validation | should | deprecation_management | SSID_structure_level3_part1_MAX.md:655 |
| SOT-349 | version Validation | should | market_entry_strategy | SSID_structure_level3_part1_MAX.md:821 |
| SOT-350 | date Validation | should | market_entry_strategy | SSID_structure_level3_part1_MAX.md:821 |
| SOT-351 | deprecated Validation | should | market_entry_strategy | SSID_structure_level3_part1_MAX.md:821 |
| SOT-352 | classification Validation | should | market_entry_strategy | SSID_structure_level3_part1_MAX.md:821 |
| SOT-353 | market_prioritization.immediate_focus.jurisdiction... | should | market_entry_strategy | SSID_structure_level3_part1_MAX.md:821 |
| SOT-354 | market_prioritization.immediate_focus.jurisdiction... | should | market_entry_strategy | SSID_structure_level3_part1_MAX.md:821 |
| SOT-355 | market_prioritization.immediate_focus.jurisdiction... | should | market_entry_strategy | SSID_structure_level3_part1_MAX.md:821 |
| SOT-356 | market_prioritization.immediate_focus.jurisdiction... | should | market_entry_strategy | SSID_structure_level3_part1_MAX.md:821 |
| SOT-357 | market_prioritization.immediate_focus.jurisdiction... | should | market_entry_strategy | SSID_structure_level3_part1_MAX.md:821 |
| SOT-358 | market_prioritization.immediate_focus.rationale Va... | should | market_entry_strategy | SSID_structure_level3_part1_MAX.md:821 |
| SOT-359 | market_prioritization.immediate_focus.timeline Val... | should | market_entry_strategy | SSID_structure_level3_part1_MAX.md:821 |
| SOT-360 | market_prioritization.immediate_focus.investment V... | should | market_entry_strategy | SSID_structure_level3_part1_MAX.md:821 |
| SOT-361 | market_prioritization.near_term.jurisdictions[0] V... | should | market_entry_strategy | SSID_structure_level3_part1_MAX.md:821 |
| SOT-362 | market_prioritization.near_term.jurisdictions[1] V... | should | market_entry_strategy | SSID_structure_level3_part1_MAX.md:821 |
| SOT-363 | market_prioritization.near_term.jurisdictions[2] V... | should | market_entry_strategy | SSID_structure_level3_part1_MAX.md:821 |
| SOT-364 | market_prioritization.near_term.jurisdictions[3] V... | should | market_entry_strategy | SSID_structure_level3_part1_MAX.md:821 |
| SOT-365 | market_prioritization.near_term.rationale Validati... | should | market_entry_strategy | SSID_structure_level3_part1_MAX.md:821 |
| SOT-366 | market_prioritization.near_term.timeline Validatio... | should | market_entry_strategy | SSID_structure_level3_part1_MAX.md:821 |
| SOT-367 | market_prioritization.near_term.investment Validat... | should | market_entry_strategy | SSID_structure_level3_part1_MAX.md:821 |
| SOT-368 | market_prioritization.medium_term.jurisdictions[0]... | should | market_entry_strategy | SSID_structure_level3_part1_MAX.md:821 |
| SOT-369 | market_prioritization.medium_term.jurisdictions[1]... | should | market_entry_strategy | SSID_structure_level3_part1_MAX.md:821 |
| SOT-370 | market_prioritization.medium_term.jurisdictions[2]... | should | market_entry_strategy | SSID_structure_level3_part1_MAX.md:821 |
| SOT-371 | market_prioritization.medium_term.jurisdictions[3]... | should | market_entry_strategy | SSID_structure_level3_part1_MAX.md:821 |
| SOT-372 | market_prioritization.medium_term.rationale Valida... | should | market_entry_strategy | SSID_structure_level3_part1_MAX.md:821 |
| SOT-373 | market_prioritization.medium_term.timeline Validat... | should | market_entry_strategy | SSID_structure_level3_part1_MAX.md:821 |
| SOT-374 | market_prioritization.medium_term.investment Valid... | should | market_entry_strategy | SSID_structure_level3_part1_MAX.md:821 |
| SOT-375 | market_prioritization.long_term.jurisdictions[0] V... | should | market_entry_strategy | SSID_structure_level3_part1_MAX.md:821 |
| SOT-376 | market_prioritization.long_term.jurisdictions[1] V... | should | market_entry_strategy | SSID_structure_level3_part1_MAX.md:821 |
| SOT-377 | market_prioritization.long_term.jurisdictions[2] V... | should | market_entry_strategy | SSID_structure_level3_part1_MAX.md:821 |
| SOT-378 | market_prioritization.long_term.jurisdictions[3] V... | should | market_entry_strategy | SSID_structure_level3_part1_MAX.md:821 |
| SOT-379 | market_prioritization.long_term.rationale Validati... | should | market_entry_strategy | SSID_structure_level3_part1_MAX.md:821 |
| SOT-380 | market_prioritization.long_term.timeline Validatio... | should | market_entry_strategy | SSID_structure_level3_part1_MAX.md:821 |
| SOT-381 | market_prioritization.long_term.investment Validat... | should | market_entry_strategy | SSID_structure_level3_part1_MAX.md:821 |
| SOT-382 | entry_requirements.regulatory_assessment.timeline ... | should | market_entry_strategy | SSID_structure_level3_part1_MAX.md:821 |
| SOT-383 | entry_requirements.regulatory_assessment.cost Vali... | should | market_entry_strategy | SSID_structure_level3_part1_MAX.md:821 |
| SOT-384 | entry_requirements.regulatory_assessment.deliverab... | should | market_entry_strategy | SSID_structure_level3_part1_MAX.md:821 |
| SOT-385 | entry_requirements.regulatory_assessment.deliverab... | should | market_entry_strategy | SSID_structure_level3_part1_MAX.md:821 |
| SOT-386 | entry_requirements.regulatory_assessment.deliverab... | should | market_entry_strategy | SSID_structure_level3_part1_MAX.md:821 |
| SOT-387 | entry_requirements.local_legal_counsel.requirement... | must | market_entry_strategy | SSID_structure_level3_part1_MAX.md:821 |
| SOT-388 | entry_requirements.local_legal_counsel.selection_c... | should | market_entry_strategy | SSID_structure_level3_part1_MAX.md:821 |
| SOT-389 | entry_requirements.local_legal_counsel.selection_c... | should | market_entry_strategy | SSID_structure_level3_part1_MAX.md:821 |
| SOT-390 | entry_requirements.local_legal_counsel.selection_c... | should | market_entry_strategy | SSID_structure_level3_part1_MAX.md:821 |
| SOT-391 | entry_requirements.local_legal_counsel.budget Vali... | should | market_entry_strategy | SSID_structure_level3_part1_MAX.md:821 |
| SOT-392 | entry_requirements.compliance_implementation.timel... | should | market_entry_strategy | SSID_structure_level3_part1_MAX.md:821 |
| SOT-393 | entry_requirements.compliance_implementation.resou... | should | market_entry_strategy | SSID_structure_level3_part1_MAX.md:821 |
| SOT-394 | entry_requirements.compliance_implementation.cost ... | should | market_entry_strategy | SSID_structure_level3_part1_MAX.md:821 |
| SOT-395 | entry_requirements.local_partnerships.requirement ... | should | market_entry_strategy | SSID_structure_level3_part1_MAX.md:821 |
| SOT-396 | entry_requirements.local_partnerships.partner_type... | should | market_entry_strategy | SSID_structure_level3_part1_MAX.md:821 |
| SOT-397 | entry_requirements.local_partnerships.partner_type... | should | market_entry_strategy | SSID_structure_level3_part1_MAX.md:821 |
| SOT-398 | entry_requirements.local_partnerships.partner_type... | should | market_entry_strategy | SSID_structure_level3_part1_MAX.md:821 |
| SOT-399 | risk_assessment_framework.regulatory_risk.low Vali... | have | market_entry_strategy | SSID_structure_level3_part1_MAX.md:821 |
| SOT-400 | risk_assessment_framework.regulatory_risk.medium V... | should | market_entry_strategy | SSID_structure_level3_part1_MAX.md:821 |
| SOT-401 | risk_assessment_framework.regulatory_risk.high Val... | should | market_entry_strategy | SSID_structure_level3_part1_MAX.md:821 |
| SOT-402 | risk_assessment_framework.regulatory_risk.prohibit... | should | market_entry_strategy | SSID_structure_level3_part1_MAX.md:821 |
| SOT-403 | risk_assessment_framework.compliance_cost.estimati... | should | market_entry_strategy | SSID_structure_level3_part1_MAX.md:821 |
| SOT-404 | risk_assessment_framework.compliance_cost.estimati... | should | market_entry_strategy | SSID_structure_level3_part1_MAX.md:821 |
| SOT-405 | risk_assessment_framework.compliance_cost.estimati... | should | market_entry_strategy | SSID_structure_level3_part1_MAX.md:821 |
| SOT-406 | risk_assessment_framework.compliance_cost.cost_cat... | should | market_entry_strategy | SSID_structure_level3_part1_MAX.md:821 |
| SOT-407 | risk_assessment_framework.compliance_cost.cost_cat... | should | market_entry_strategy | SSID_structure_level3_part1_MAX.md:821 |
| SOT-408 | risk_assessment_framework.compliance_cost.cost_cat... | should | market_entry_strategy | SSID_structure_level3_part1_MAX.md:821 |
| SOT-409 | risk_assessment_framework.compliance_cost.cost_cat... | should | market_entry_strategy | SSID_structure_level3_part1_MAX.md:821 |
| SOT-410 | risk_assessment_framework.time_to_market.factors[0... | should | market_entry_strategy | SSID_structure_level3_part1_MAX.md:821 |
| SOT-411 | risk_assessment_framework.time_to_market.factors[1... | should | market_entry_strategy | SSID_structure_level3_part1_MAX.md:821 |
| SOT-412 | risk_assessment_framework.time_to_market.factors[2... | should | market_entry_strategy | SSID_structure_level3_part1_MAX.md:821 |
| SOT-413 | risk_assessment_framework.time_to_market.typical_r... | should | market_entry_strategy | SSID_structure_level3_part1_MAX.md:821 |
| SOT-414 | risk_assessment_framework.time_to_market.typical_r... | should | market_entry_strategy | SSID_structure_level3_part1_MAX.md:821 |
| SOT-415 | risk_assessment_framework.business_opportunity.ass... | should | market_entry_strategy | SSID_structure_level3_part1_MAX.md:821 |
| SOT-416 | risk_assessment_framework.business_opportunity.ass... | should | market_entry_strategy | SSID_structure_level3_part1_MAX.md:821 |
| SOT-417 | risk_assessment_framework.business_opportunity.ass... | should | market_entry_strategy | SSID_structure_level3_part1_MAX.md:821 |
| SOT-418 | risk_assessment_framework.business_opportunity.ass... | should | market_entry_strategy | SSID_structure_level3_part1_MAX.md:821 |
| SOT-419 | risk_assessment_framework.business_opportunity.roi... | must | market_entry_strategy | SSID_structure_level3_part1_MAX.md:821 |
| SOT-420 | risk_assessment_framework.competitive_landscape.an... | should | market_entry_strategy | SSID_structure_level3_part1_MAX.md:821 |
| SOT-421 | risk_assessment_framework.competitive_landscape.an... | should | market_entry_strategy | SSID_structure_level3_part1_MAX.md:821 |
| SOT-422 | risk_assessment_framework.competitive_landscape.an... | should | market_entry_strategy | SSID_structure_level3_part1_MAX.md:821 |
| SOT-423 | risk_assessment_framework.competitive_landscape.an... | should | market_entry_strategy | SSID_structure_level3_part1_MAX.md:821 |
| SOT-424 | version Validation | should | regulatory_monitoring_intelligence | SSID_structure_level3_part1_MAX.md:897 |
| SOT-425 | date Validation | should | regulatory_monitoring_intelligence | SSID_structure_level3_part1_MAX.md:897 |
| SOT-426 | deprecated Validation | should | regulatory_monitoring_intelligence | SSID_structure_level3_part1_MAX.md:897 |
| SOT-427 | classification Validation | should | regulatory_monitoring_intelligence | SSID_structure_level3_part1_MAX.md:897 |
| SOT-428 | monitoring_scope.tier_1_markets.monitoring_frequen... | should | regulatory_monitoring_intelligence | SSID_structure_level3_part1_MAX.md:897 |
| SOT-429 | monitoring_scope.tier_1_markets.sources[0] Validat... | should | regulatory_monitoring_intelligence | SSID_structure_level3_part1_MAX.md:897 |
| SOT-430 | monitoring_scope.tier_1_markets.sources[1] Validat... | should | regulatory_monitoring_intelligence | SSID_structure_level3_part1_MAX.md:897 |
| SOT-431 | monitoring_scope.tier_1_markets.sources[2] Validat... | should | regulatory_monitoring_intelligence | SSID_structure_level3_part1_MAX.md:897 |
| SOT-432 | monitoring_scope.tier_1_markets.alert_threshold Va... | should | regulatory_monitoring_intelligence | SSID_structure_level3_part1_MAX.md:897 |
| SOT-433 | monitoring_scope.tier_2_markets.monitoring_frequen... | should | regulatory_monitoring_intelligence | SSID_structure_level3_part1_MAX.md:897 |
| SOT-434 | monitoring_scope.tier_2_markets.sources[0] Validat... | should | regulatory_monitoring_intelligence | SSID_structure_level3_part1_MAX.md:897 |
| SOT-435 | monitoring_scope.tier_2_markets.sources[1] Validat... | should | regulatory_monitoring_intelligence | SSID_structure_level3_part1_MAX.md:897 |
| SOT-436 | monitoring_scope.tier_2_markets.sources[2] Validat... | should | regulatory_monitoring_intelligence | SSID_structure_level3_part1_MAX.md:897 |
| SOT-437 | monitoring_scope.tier_2_markets.alert_threshold Va... | should | regulatory_monitoring_intelligence | SSID_structure_level3_part1_MAX.md:897 |
| SOT-438 | monitoring_scope.tier_3_markets.monitoring_frequen... | should | regulatory_monitoring_intelligence | SSID_structure_level3_part1_MAX.md:897 |
| SOT-439 | monitoring_scope.tier_3_markets.sources[0] Validat... | should | regulatory_monitoring_intelligence | SSID_structure_level3_part1_MAX.md:897 |
| SOT-440 | monitoring_scope.tier_3_markets.sources[1] Validat... | should | regulatory_monitoring_intelligence | SSID_structure_level3_part1_MAX.md:897 |
| SOT-441 | monitoring_scope.tier_3_markets.sources[2] Validat... | should | regulatory_monitoring_intelligence | SSID_structure_level3_part1_MAX.md:897 |
| SOT-442 | monitoring_scope.tier_3_markets.alert_threshold Va... | should | regulatory_monitoring_intelligence | SSID_structure_level3_part1_MAX.md:897 |
| SOT-443 | intelligence_sources.primary_sources[0] Validation | should | regulatory_monitoring_intelligence | SSID_structure_level3_part1_MAX.md:897 |
| SOT-444 | intelligence_sources.primary_sources[1] Validation | should | regulatory_monitoring_intelligence | SSID_structure_level3_part1_MAX.md:897 |
| SOT-445 | intelligence_sources.primary_sources[2] Validation | should | regulatory_monitoring_intelligence | SSID_structure_level3_part1_MAX.md:897 |
| SOT-446 | intelligence_sources.primary_sources[3] Validation | should | regulatory_monitoring_intelligence | SSID_structure_level3_part1_MAX.md:897 |
| SOT-447 | intelligence_sources.secondary_sources[0] Validati... | should | regulatory_monitoring_intelligence | SSID_structure_level3_part1_MAX.md:897 |
| SOT-448 | intelligence_sources.secondary_sources[1] Validati... | should | regulatory_monitoring_intelligence | SSID_structure_level3_part1_MAX.md:897 |
| SOT-449 | intelligence_sources.secondary_sources[2] Validati... | should | regulatory_monitoring_intelligence | SSID_structure_level3_part1_MAX.md:897 |
| SOT-450 | intelligence_sources.secondary_sources[3] Validati... | should | regulatory_monitoring_intelligence | SSID_structure_level3_part1_MAX.md:897 |
| SOT-451 | intelligence_sources.intelligence_partners[0] Vali... | should | regulatory_monitoring_intelligence | SSID_structure_level3_part1_MAX.md:897 |
| SOT-452 | intelligence_sources.intelligence_partners[1] Vali... | should | regulatory_monitoring_intelligence | SSID_structure_level3_part1_MAX.md:897 |
| SOT-453 | intelligence_sources.intelligence_partners[2] Vali... | should | regulatory_monitoring_intelligence | SSID_structure_level3_part1_MAX.md:897 |
| SOT-454 | intelligence_sources.intelligence_partners[3] Vali... | should | regulatory_monitoring_intelligence | SSID_structure_level3_part1_MAX.md:897 |
| SOT-455 | alert_framework.critical_alerts.criteria Validatio... | must | regulatory_monitoring_intelligence | SSID_structure_level3_part1_MAX.md:897 |
| SOT-456 | alert_framework.critical_alerts.response_time Vali... | must | regulatory_monitoring_intelligence | SSID_structure_level3_part1_MAX.md:897 |
| SOT-457 | alert_framework.critical_alerts.escalation Validat... | must | regulatory_monitoring_intelligence | SSID_structure_level3_part1_MAX.md:897 |
| SOT-458 | alert_framework.high_priority.criteria Validation | should | regulatory_monitoring_intelligence | SSID_structure_level3_part1_MAX.md:897 |
| SOT-459 | alert_framework.high_priority.response_time Valida... | should | regulatory_monitoring_intelligence | SSID_structure_level3_part1_MAX.md:897 |
| SOT-460 | alert_framework.high_priority.escalation Validatio... | should | regulatory_monitoring_intelligence | SSID_structure_level3_part1_MAX.md:897 |
| SOT-461 | alert_framework.medium_priority.criteria Validatio... | should | regulatory_monitoring_intelligence | SSID_structure_level3_part1_MAX.md:897 |
| SOT-462 | alert_framework.medium_priority.response_time Vali... | should | regulatory_monitoring_intelligence | SSID_structure_level3_part1_MAX.md:897 |
| SOT-463 | alert_framework.medium_priority.escalation Validat... | should | regulatory_monitoring_intelligence | SSID_structure_level3_part1_MAX.md:897 |
| SOT-464 | alert_framework.low_priority.criteria Validation | have | regulatory_monitoring_intelligence | SSID_structure_level3_part1_MAX.md:897 |
| SOT-465 | alert_framework.low_priority.response_time Validat... | have | regulatory_monitoring_intelligence | SSID_structure_level3_part1_MAX.md:897 |
| SOT-466 | alert_framework.low_priority.escalation Validation | have | regulatory_monitoring_intelligence | SSID_structure_level3_part1_MAX.md:897 |
| SOT-467 | impact_assessment.assessment_criteria[0] Validatio... | should | regulatory_monitoring_intelligence | SSID_structure_level3_part1_MAX.md:897 |
| SOT-468 | impact_assessment.assessment_criteria[1] Validatio... | should | regulatory_monitoring_intelligence | SSID_structure_level3_part1_MAX.md:897 |
| SOT-469 | impact_assessment.assessment_criteria[2] Validatio... | should | regulatory_monitoring_intelligence | SSID_structure_level3_part1_MAX.md:897 |
| SOT-470 | impact_assessment.assessment_criteria[3] Validatio... | should | regulatory_monitoring_intelligence | SSID_structure_level3_part1_MAX.md:897 |
| SOT-471 | impact_assessment.assessment_criteria[4] Validatio... | should | regulatory_monitoring_intelligence | SSID_structure_level3_part1_MAX.md:897 |
| SOT-472 | impact_assessment.response_planning[0] Validation | should | regulatory_monitoring_intelligence | SSID_structure_level3_part1_MAX.md:897 |
| SOT-473 | impact_assessment.response_planning[1] Validation | should | regulatory_monitoring_intelligence | SSID_structure_level3_part1_MAX.md:897 |
| SOT-474 | impact_assessment.response_planning[2] Validation | should | regulatory_monitoring_intelligence | SSID_structure_level3_part1_MAX.md:897 |
| SOT-475 | impact_assessment.response_planning[3] Validation | should | regulatory_monitoring_intelligence | SSID_structure_level3_part1_MAX.md:897 |
| SOT-476 | impact_assessment.response_planning[4] Validation | should | regulatory_monitoring_intelligence | SSID_structure_level3_part1_MAX.md:897 |
| SOT-477 | version Validation | should | ai_ml_ready_compliance_architecture | SSID_structure_level3_part1_MAX.md:979 |
| SOT-478 | date Validation | should | ai_ml_ready_compliance_architecture | SSID_structure_level3_part1_MAX.md:979 |
| SOT-479 | deprecated Validation | should | ai_ml_ready_compliance_architecture | SSID_structure_level3_part1_MAX.md:979 |
| SOT-480 | ai_compatible Validation | should | ai_ml_ready_compliance_architecture | SSID_structure_level3_part1_MAX.md:979 |
| SOT-481 | llm_interpretable Validation | should | ai_ml_ready_compliance_architecture | SSID_structure_level3_part1_MAX.md:979 |
| SOT-482 | classification Validation | should | ai_ml_ready_compliance_architecture | SSID_structure_level3_part1_MAX.md:979 |
| SOT-483 | ai_integration.policy_bots.enabled Validation | should | ai_ml_ready_compliance_architecture | SSID_structure_level3_part1_MAX.md:979 |
| SOT-484 | ai_integration.policy_bots.description Validation | should | ai_ml_ready_compliance_architecture | SSID_structure_level3_part1_MAX.md:979 |
| SOT-485 | ai_integration.policy_bots.compatible_models[0] Va... | should | ai_ml_ready_compliance_architecture | SSID_structure_level3_part1_MAX.md:979 |
| SOT-486 | ai_integration.policy_bots.compatible_models[1] Va... | should | ai_ml_ready_compliance_architecture | SSID_structure_level3_part1_MAX.md:979 |
| SOT-487 | ai_integration.policy_bots.compatible_models[2] Va... | should | ai_ml_ready_compliance_architecture | SSID_structure_level3_part1_MAX.md:979 |
| SOT-488 | ai_integration.policy_bots.compatible_models[3] Va... | should | ai_ml_ready_compliance_architecture | SSID_structure_level3_part1_MAX.md:979 |
| SOT-489 | ai_integration.policy_bots.api_endpoints Validatio... | should | ai_ml_ready_compliance_architecture | SSID_structure_level3_part1_MAX.md:979 |
| SOT-490 | ai_integration.policy_bots.enterprise_models Valid... | should | ai_ml_ready_compliance_architecture | SSID_structure_level3_part1_MAX.md:979 |
| SOT-491 | ai_integration.realtime_checks.enabled Validation | should | ai_ml_ready_compliance_architecture | SSID_structure_level3_part1_MAX.md:979 |
| SOT-492 | ai_integration.realtime_checks.description Validat... | should | ai_ml_ready_compliance_architecture | SSID_structure_level3_part1_MAX.md:979 |
| SOT-493 | ai_integration.realtime_checks.check_frequency Val... | should | ai_ml_ready_compliance_architecture | SSID_structure_level3_part1_MAX.md:979 |
| SOT-494 | ai_integration.realtime_checks.alert_threshold Val... | should | ai_ml_ready_compliance_architecture | SSID_structure_level3_part1_MAX.md:979 |
| SOT-495 | ai_integration.realtime_checks.integration_path Va... | should | ai_ml_ready_compliance_architecture | SSID_structure_level3_part1_MAX.md:979 |
| SOT-496 | ai_integration.realtime_checks.business_escalation... | must | ai_ml_ready_compliance_architecture | SSID_structure_level3_part1_MAX.md:979 |
| SOT-497 | ai_integration.natural_language_queries.enabled Va... | should | ai_ml_ready_compliance_architecture | SSID_structure_level3_part1_MAX.md:979 |
| SOT-498 | ai_integration.natural_language_queries.descriptio... | should | ai_ml_ready_compliance_architecture | SSID_structure_level3_part1_MAX.md:979 |
| SOT-499 | ai_integration.natural_language_queries.examples[0... | should | ai_ml_ready_compliance_architecture | SSID_structure_level3_part1_MAX.md:979 |
| SOT-500 | ai_integration.natural_language_queries.examples[1... | should | ai_ml_ready_compliance_architecture | SSID_structure_level3_part1_MAX.md:979 |
| SOT-501 | ai_integration.natural_language_queries.examples[2... | should | ai_ml_ready_compliance_architecture | SSID_structure_level3_part1_MAX.md:979 |
| SOT-502 | ai_integration.natural_language_queries.examples[3... | should | ai_ml_ready_compliance_architecture | SSID_structure_level3_part1_MAX.md:979 |
| SOT-503 | ai_integration.natural_language_queries.query_proc... | should | ai_ml_ready_compliance_architecture | SSID_structure_level3_part1_MAX.md:979 |
| SOT-504 | ai_integration.natural_language_queries.business_i... | should | ai_ml_ready_compliance_architecture | SSID_structure_level3_part1_MAX.md:979 |
| SOT-505 | ai_integration.machine_readable_comments.format Va... | should | ai_ml_ready_compliance_architecture | SSID_structure_level3_part1_MAX.md:979 |
| SOT-506 | ai_integration.machine_readable_comments.ai_tags[0... | should | ai_ml_ready_compliance_architecture | SSID_structure_level3_part1_MAX.md:979 |
| SOT-507 | ai_integration.machine_readable_comments.ai_tags[1... | should | ai_ml_ready_compliance_architecture | SSID_structure_level3_part1_MAX.md:979 |
| SOT-508 | ai_integration.machine_readable_comments.ai_tags[2... | should | ai_ml_ready_compliance_architecture | SSID_structure_level3_part1_MAX.md:979 |
| SOT-509 | ai_integration.machine_readable_comments.ai_tags[3... | must | ai_ml_ready_compliance_architecture | SSID_structure_level3_part1_MAX.md:979 |
| SOT-510 | ai_integration.machine_readable_comments.schema Va... | should | ai_ml_ready_compliance_architecture | SSID_structure_level3_part1_MAX.md:979 |
| SOT-511 | policy_automation.auto_policy_updates.enabled Vali... | should | ai_ml_ready_compliance_architecture | SSID_structure_level3_part1_MAX.md:979 |
| SOT-512 | policy_automation.auto_policy_updates.description ... | should | ai_ml_ready_compliance_architecture | SSID_structure_level3_part1_MAX.md:979 |
| SOT-513 | policy_automation.auto_policy_updates.human_approv... | must | ai_ml_ready_compliance_architecture | SSID_structure_level3_part1_MAX.md:979 |
| SOT-514 | policy_automation.auto_policy_updates.business_rev... | must | ai_ml_ready_compliance_architecture | SSID_structure_level3_part1_MAX.md:979 |
| SOT-515 | policy_automation.auto_policy_updates.review_thres... | should | ai_ml_ready_compliance_architecture | SSID_structure_level3_part1_MAX.md:979 |
| SOT-516 | policy_automation.compliance_chatbot.enabled Valid... | should | ai_ml_ready_compliance_architecture | SSID_structure_level3_part1_MAX.md:979 |
| SOT-517 | policy_automation.compliance_chatbot.description V... | should | ai_ml_ready_compliance_architecture | SSID_structure_level3_part1_MAX.md:979 |
| SOT-518 | policy_automation.compliance_chatbot.knowledge_bas... | should | ai_ml_ready_compliance_architecture | SSID_structure_level3_part1_MAX.md:979 |
| SOT-519 | policy_automation.compliance_chatbot.update_freque... | should | ai_ml_ready_compliance_architecture | SSID_structure_level3_part1_MAX.md:979 |
| SOT-520 | policy_automation.compliance_chatbot.business_cont... | should | ai_ml_ready_compliance_architecture | SSID_structure_level3_part1_MAX.md:979 |
| SOT-521 | policy_automation.risk_assessment_ai.enabled Valid... | should | ai_ml_ready_compliance_architecture | SSID_structure_level3_part1_MAX.md:979 |
| SOT-522 | policy_automation.risk_assessment_ai.description V... | should | ai_ml_ready_compliance_architecture | SSID_structure_level3_part1_MAX.md:979 |
| SOT-523 | policy_automation.risk_assessment_ai.model_path Va... | should | ai_ml_ready_compliance_architecture | SSID_structure_level3_part1_MAX.md:979 |
| SOT-524 | policy_automation.risk_assessment_ai.confidence_th... | should | ai_ml_ready_compliance_architecture | SSID_structure_level3_part1_MAX.md:979 |
| SOT-525 | policy_automation.risk_assessment_ai.human_review_... | must | ai_ml_ready_compliance_architecture | SSID_structure_level3_part1_MAX.md:979 |
| SOT-526 | policy_automation.risk_assessment_ai.business_impa... | should | ai_ml_ready_compliance_architecture | SSID_structure_level3_part1_MAX.md:979 |
| SOT-527 | version Validation | should | api_data_portability_framework | SSID_structure_level3_part1_MAX.md:1045 |
| SOT-528 | date Validation | should | api_data_portability_framework | SSID_structure_level3_part1_MAX.md:1045 |
| SOT-529 | deprecated Validation | should | api_data_portability_framework | SSID_structure_level3_part1_MAX.md:1045 |
| SOT-530 | classification Validation | should | api_data_portability_framework | SSID_structure_level3_part1_MAX.md:1045 |
| SOT-531 | export_formats.openapi.version Validation | should | api_data_portability_framework | SSID_structure_level3_part1_MAX.md:1045 |
| SOT-532 | export_formats.openapi.endpoint Validation | should | api_data_portability_framework | SSID_structure_level3_part1_MAX.md:1045 |
| SOT-533 | export_formats.openapi.schema_path Validation | should | api_data_portability_framework | SSID_structure_level3_part1_MAX.md:1045 |
| SOT-534 | export_formats.openapi.business_sensitive_fields V... | should | api_data_portability_framework | SSID_structure_level3_part1_MAX.md:1045 |
| SOT-535 | export_formats.json_schema.version Validation | should | api_data_portability_framework | SSID_structure_level3_part1_MAX.md:1045 |
| SOT-536 | export_formats.json_schema.endpoint Validation | should | api_data_portability_framework | SSID_structure_level3_part1_MAX.md:1045 |
| SOT-537 | export_formats.json_schema.schema_path Validation | should | api_data_portability_framework | SSID_structure_level3_part1_MAX.md:1045 |
| SOT-538 | export_formats.json_schema.enterprise_extensions V... | should | api_data_portability_framework | SSID_structure_level3_part1_MAX.md:1045 |
| SOT-539 | export_formats.graphql.enabled Validation | should | api_data_portability_framework | SSID_structure_level3_part1_MAX.md:1045 |
| SOT-540 | export_formats.graphql.endpoint Validation | should | api_data_portability_framework | SSID_structure_level3_part1_MAX.md:1045 |
| SOT-541 | export_formats.graphql.schema_path Validation | should | api_data_portability_framework | SSID_structure_level3_part1_MAX.md:1045 |
| SOT-542 | export_formats.graphql.introspection_enabled Valid... | should | api_data_portability_framework | SSID_structure_level3_part1_MAX.md:1045 |
| SOT-543 | export_formats.graphql.business_rules_layer Valida... | should | api_data_portability_framework | SSID_structure_level3_part1_MAX.md:1045 |
| SOT-544 | export_formats.rdf_turtle.enabled Validation | should | api_data_portability_framework | SSID_structure_level3_part1_MAX.md:1045 |
| SOT-545 | export_formats.rdf_turtle.namespace Validation | should | api_data_portability_framework | SSID_structure_level3_part1_MAX.md:1045 |
| SOT-546 | export_formats.rdf_turtle.endpoint Validation | should | api_data_portability_framework | SSID_structure_level3_part1_MAX.md:1045 |
| SOT-547 | export_formats.rdf_turtle.ontology_path Validation | should | api_data_portability_framework | SSID_structure_level3_part1_MAX.md:1045 |
| SOT-548 | import_capabilities.frameworks_supported[0] Valida... | should | api_data_portability_framework | SSID_structure_level3_part1_MAX.md:1045 |
| SOT-549 | import_capabilities.frameworks_supported[1] Valida... | should | api_data_portability_framework | SSID_structure_level3_part1_MAX.md:1045 |
| SOT-550 | import_capabilities.frameworks_supported[2] Valida... | should | api_data_portability_framework | SSID_structure_level3_part1_MAX.md:1045 |
| SOT-551 | import_capabilities.frameworks_supported[3] Valida... | should | api_data_portability_framework | SSID_structure_level3_part1_MAX.md:1045 |
| SOT-552 | import_capabilities.frameworks_supported[4] Valida... | should | api_data_portability_framework | SSID_structure_level3_part1_MAX.md:1045 |
| SOT-553 | import_capabilities.frameworks_supported[5] Valida... | should | api_data_portability_framework | SSID_structure_level3_part1_MAX.md:1045 |
| SOT-554 | import_capabilities.frameworks_supported[6] Valida... | should | api_data_portability_framework | SSID_structure_level3_part1_MAX.md:1045 |
| SOT-555 | import_capabilities.mapping_engine.path Validation | should | api_data_portability_framework | SSID_structure_level3_part1_MAX.md:1045 |
| SOT-556 | import_capabilities.mapping_engine.ai_assisted Val... | should | api_data_portability_framework | SSID_structure_level3_part1_MAX.md:1045 |
| SOT-557 | import_capabilities.mapping_engine.confidence_scor... | should | api_data_portability_framework | SSID_structure_level3_part1_MAX.md:1045 |
| SOT-558 | import_capabilities.mapping_engine.human_validatio... | must | api_data_portability_framework | SSID_structure_level3_part1_MAX.md:1045 |
| SOT-559 | import_capabilities.mapping_engine.business_rule_v... | should | api_data_portability_framework | SSID_structure_level3_part1_MAX.md:1045 |
| SOT-560 | import_capabilities.bulk_import.enabled Validation | should | api_data_portability_framework | SSID_structure_level3_part1_MAX.md:1045 |
| SOT-561 | import_capabilities.bulk_import.max_file_size Vali... | should | api_data_portability_framework | SSID_structure_level3_part1_MAX.md:1045 |
| SOT-562 | import_capabilities.bulk_import.supported_formats[... | should | api_data_portability_framework | SSID_structure_level3_part1_MAX.md:1045 |
| SOT-563 | import_capabilities.bulk_import.supported_formats[... | should | api_data_portability_framework | SSID_structure_level3_part1_MAX.md:1045 |
| SOT-564 | import_capabilities.bulk_import.supported_formats[... | should | api_data_portability_framework | SSID_structure_level3_part1_MAX.md:1045 |
| SOT-565 | import_capabilities.bulk_import.supported_formats[... | should | api_data_portability_framework | SSID_structure_level3_part1_MAX.md:1045 |
| SOT-566 | import_capabilities.bulk_import.supported_formats[... | should | api_data_portability_framework | SSID_structure_level3_part1_MAX.md:1045 |
| SOT-567 | import_capabilities.bulk_import.validation_require... | must | api_data_portability_framework | SSID_structure_level3_part1_MAX.md:1045 |
| SOT-568 | import_capabilities.bulk_import.enterprise_audit_t... | should | api_data_portability_framework | SSID_structure_level3_part1_MAX.md:1045 |
| SOT-569 | portability_guarantees.no_vendor_lockin Validation | should | api_data_portability_framework | SSID_structure_level3_part1_MAX.md:1045 |
| SOT-570 | portability_guarantees.full_data_export Validation | should | api_data_portability_framework | SSID_structure_level3_part1_MAX.md:1045 |
| SOT-571 | portability_guarantees.schema_versioning Validatio... | should | api_data_portability_framework | SSID_structure_level3_part1_MAX.md:1045 |
| SOT-572 | portability_guarantees.migration_assistance Valida... | should | api_data_portability_framework | SSID_structure_level3_part1_MAX.md:1045 |
| SOT-573 | portability_guarantees.api_stability_promise Valid... | should | api_data_portability_framework | SSID_structure_level3_part1_MAX.md:1045 |
| SOT-574 | portability_guarantees.enterprise_support Validati... | should | api_data_portability_framework | SSID_structure_level3_part1_MAX.md:1045 |
| SOT-575 | version Validation | should | next_generation_audit_chain | SSID_structure_level3_part1_MAX.md:1112 |
| SOT-576 | date Validation | should | next_generation_audit_chain | SSID_structure_level3_part1_MAX.md:1112 |
| SOT-577 | deprecated Validation | should | next_generation_audit_chain | SSID_structure_level3_part1_MAX.md:1112 |
| SOT-578 | experimental Validation | should | next_generation_audit_chain | SSID_structure_level3_part1_MAX.md:1112 |
| SOT-579 | classification Validation | should | next_generation_audit_chain | SSID_structure_level3_part1_MAX.md:1112 |
| SOT-580 | blockchain_anchoring.enabled Validation | should | next_generation_audit_chain | SSID_structure_level3_part1_MAX.md:1112 |
| SOT-581 | blockchain_anchoring.supported_networks.name Valid... | should | next_generation_audit_chain | SSID_structure_level3_part1_MAX.md:1112 |
| SOT-582 | blockchain_anchoring.supported_networks.type Valid... | should | next_generation_audit_chain | SSID_structure_level3_part1_MAX.md:1112 |
| SOT-583 | blockchain_anchoring.supported_networks.cost Valid... | should | next_generation_audit_chain | SSID_structure_level3_part1_MAX.md:1112 |
| SOT-584 | blockchain_anchoring.supported_networks.verificati... | should | next_generation_audit_chain | SSID_structure_level3_part1_MAX.md:1112 |
| SOT-585 | blockchain_anchoring.supported_networks.enterprise... | have | next_generation_audit_chain | SSID_structure_level3_part1_MAX.md:1112 |
| SOT-586 | blockchain_anchoring.supported_networks.name Valid... | should | next_generation_audit_chain | SSID_structure_level3_part1_MAX.md:1112 |
| SOT-587 | blockchain_anchoring.supported_networks.type Valid... | should | next_generation_audit_chain | SSID_structure_level3_part1_MAX.md:1112 |
| SOT-588 | blockchain_anchoring.supported_networks.cost Valid... | should | next_generation_audit_chain | SSID_structure_level3_part1_MAX.md:1112 |
| SOT-589 | blockchain_anchoring.supported_networks.verificati... | should | next_generation_audit_chain | SSID_structure_level3_part1_MAX.md:1112 |
| SOT-590 | blockchain_anchoring.supported_networks.enterprise... | should | next_generation_audit_chain | SSID_structure_level3_part1_MAX.md:1112 |
| SOT-591 | blockchain_anchoring.supported_networks.name Valid... | should | next_generation_audit_chain | SSID_structure_level3_part1_MAX.md:1112 |
| SOT-592 | blockchain_anchoring.supported_networks.type Valid... | should | next_generation_audit_chain | SSID_structure_level3_part1_MAX.md:1112 |
| SOT-593 | blockchain_anchoring.supported_networks.cost Valid... | should | next_generation_audit_chain | SSID_structure_level3_part1_MAX.md:1112 |
| SOT-594 | blockchain_anchoring.supported_networks.verificati... | should | next_generation_audit_chain | SSID_structure_level3_part1_MAX.md:1112 |
| SOT-595 | blockchain_anchoring.supported_networks.enterprise... | should | next_generation_audit_chain | SSID_structure_level3_part1_MAX.md:1112 |
| SOT-596 | blockchain_anchoring.anchor_frequency Validation | should | next_generation_audit_chain | SSID_structure_level3_part1_MAX.md:1112 |
| SOT-597 | blockchain_anchoring.critical_events_immediate Val... | must | next_generation_audit_chain | SSID_structure_level3_part1_MAX.md:1112 |
| SOT-598 | blockchain_anchoring.business_critical_immediate V... | must | next_generation_audit_chain | SSID_structure_level3_part1_MAX.md:1112 |
| SOT-599 | decentralized_identity.did_support Validation | should | next_generation_audit_chain | SSID_structure_level3_part1_MAX.md:1112 |
| SOT-600 | decentralized_identity.supported_methods[0] Valida... | should | next_generation_audit_chain | SSID_structure_level3_part1_MAX.md:1112 |
| SOT-601 | decentralized_identity.supported_methods[1] Valida... | should | next_generation_audit_chain | SSID_structure_level3_part1_MAX.md:1112 |
| SOT-602 | decentralized_identity.supported_methods[2] Valida... | should | next_generation_audit_chain | SSID_structure_level3_part1_MAX.md:1112 |
| SOT-603 | decentralized_identity.supported_methods[3] Valida... | should | next_generation_audit_chain | SSID_structure_level3_part1_MAX.md:1112 |
| SOT-604 | decentralized_identity.supported_methods[4] Valida... | should | next_generation_audit_chain | SSID_structure_level3_part1_MAX.md:1112 |
| SOT-605 | decentralized_identity.verifiable_credentials Vali... | should | next_generation_audit_chain | SSID_structure_level3_part1_MAX.md:1112 |
| SOT-606 | decentralized_identity.credential_schemas Validati... | should | next_generation_audit_chain | SSID_structure_level3_part1_MAX.md:1112 |
| SOT-607 | decentralized_identity.business_credentials Valida... | should | next_generation_audit_chain | SSID_structure_level3_part1_MAX.md:1112 |
| SOT-608 | zero_knowledge_proofs.enabled Validation | should | next_generation_audit_chain | SSID_structure_level3_part1_MAX.md:1112 |
| SOT-609 | zero_knowledge_proofs.use_cases[0] Validation | should | next_generation_audit_chain | SSID_structure_level3_part1_MAX.md:1112 |
| SOT-610 | zero_knowledge_proofs.use_cases[1] Validation | should | next_generation_audit_chain | SSID_structure_level3_part1_MAX.md:1112 |
| SOT-611 | zero_knowledge_proofs.use_cases[2] Validation | should | next_generation_audit_chain | SSID_structure_level3_part1_MAX.md:1112 |
| SOT-612 | zero_knowledge_proofs.use_cases[3] Validation | should | next_generation_audit_chain | SSID_structure_level3_part1_MAX.md:1112 |
| SOT-613 | zero_knowledge_proofs.supported_schemes[0] Validat... | should | next_generation_audit_chain | SSID_structure_level3_part1_MAX.md:1112 |
| SOT-614 | zero_knowledge_proofs.supported_schemes[1] Validat... | should | next_generation_audit_chain | SSID_structure_level3_part1_MAX.md:1112 |
| SOT-615 | zero_knowledge_proofs.supported_schemes[2] Validat... | should | next_generation_audit_chain | SSID_structure_level3_part1_MAX.md:1112 |
| SOT-616 | zero_knowledge_proofs.business_applications Valida... | should | next_generation_audit_chain | SSID_structure_level3_part1_MAX.md:1112 |
| SOT-617 | quantum_resistant.enabled Validation | should | next_generation_audit_chain | SSID_structure_level3_part1_MAX.md:1112 |
| SOT-618 | quantum_resistant.algorithms_supported[0] Validati... | should | next_generation_audit_chain | SSID_structure_level3_part1_MAX.md:1112 |
| SOT-619 | quantum_resistant.algorithms_supported[1] Validati... | should | next_generation_audit_chain | SSID_structure_level3_part1_MAX.md:1112 |
| SOT-620 | quantum_resistant.algorithms_supported[2] Validati... | should | next_generation_audit_chain | SSID_structure_level3_part1_MAX.md:1112 |
| SOT-621 | quantum_resistant.migration_plan Validation | should | next_generation_audit_chain | SSID_structure_level3_part1_MAX.md:1112 |
| SOT-622 | quantum_resistant.timeline Validation | should | next_generation_audit_chain | SSID_structure_level3_part1_MAX.md:1112 |
| SOT-623 | quantum_resistant.business_continuity Validation | should | next_generation_audit_chain | SSID_structure_level3_part1_MAX.md:1112 |
| SOT-624 | **ENFORCED LANGUAGES:** `en-US` (Primär), `de-DE` ... | have | language_policy_override_verbindlich | SSID_structure_level3_part1_MAX.md:1196 |
| SOT-625 | **FAIL (Exit 24)**, wenn | must | ci_gate_anpassungen_erzwingen_semantik | SSID_structure_level3_part1_MAX.md:1249 |
| SOT-626 | version Validation | should | canonical_root_level_exceptions_definition | SSID_structure_level3_part2_MAX.md:27 |
| SOT-627 | date Validation | should | canonical_root_level_exceptions_definition | SSID_structure_level3_part2_MAX.md:27 |
| SOT-628 | deprecated Validation | should | canonical_root_level_exceptions_definition | SSID_structure_level3_part2_MAX.md:27 |
| SOT-629 | classification Validation | should | canonical_root_level_exceptions_definition | SSID_structure_level3_part2_MAX.md:27 |
| SOT-630 | root_level_exceptions.description Validation | should | canonical_root_level_exceptions_definition | SSID_structure_level3_part2_MAX.md:27 |
| SOT-631 | root_level_exceptions.enforcement Validation | should | canonical_root_level_exceptions_definition | SSID_structure_level3_part2_MAX.md:27 |
| SOT-632 | root_level_exceptions.modification_policy Validati... | should | canonical_root_level_exceptions_definition | SSID_structure_level3_part2_MAX.md:27 |
| SOT-633 | allowed_directories.git_infrastructure[0] Validati... | have | canonical_root_level_exceptions_definition | SSID_structure_level3_part2_MAX.md:27 |
| SOT-634 | allowed_directories.git_infrastructure[1] Validati... | have | canonical_root_level_exceptions_definition | SSID_structure_level3_part2_MAX.md:27 |
| SOT-635 | allowed_directories.git_infrastructure[2] Validati... | have | canonical_root_level_exceptions_definition | SSID_structure_level3_part2_MAX.md:27 |
| SOT-636 | allowed_directories.development_environment[0] Val... | have | canonical_root_level_exceptions_definition | SSID_structure_level3_part2_MAX.md:27 |
| SOT-637 | allowed_directories.development_environment[1] Val... | have | canonical_root_level_exceptions_definition | SSID_structure_level3_part2_MAX.md:27 |
| SOT-638 | allowed_directories.testing_artifacts[0] Validatio... | have | canonical_root_level_exceptions_definition | SSID_structure_level3_part2_MAX.md:27 |
| SOT-639 | allowed_files.version_control[0] Validation | have | canonical_root_level_exceptions_definition | SSID_structure_level3_part2_MAX.md:27 |
| SOT-640 | allowed_files.version_control[1] Validation | have | canonical_root_level_exceptions_definition | SSID_structure_level3_part2_MAX.md:27 |
| SOT-641 | allowed_files.version_control[2] Validation | have | canonical_root_level_exceptions_definition | SSID_structure_level3_part2_MAX.md:27 |
| SOT-642 | allowed_files.project_metadata[0] Validation | have | canonical_root_level_exceptions_definition | SSID_structure_level3_part2_MAX.md:27 |
| SOT-643 | allowed_files.project_metadata[1] Validation | have | canonical_root_level_exceptions_definition | SSID_structure_level3_part2_MAX.md:27 |
| SOT-644 | allowed_files.testing_configuration[0] Validation | have | canonical_root_level_exceptions_definition | SSID_structure_level3_part2_MAX.md:27 |
| SOT-645 | guard_enforcement.ci_script Validation | should | canonical_root_level_exceptions_definition | SSID_structure_level3_part2_MAX.md:27 |
| SOT-646 | guard_enforcement.validation_function Validation | should | canonical_root_level_exceptions_definition | SSID_structure_level3_part2_MAX.md:27 |
| SOT-647 | guard_enforcement.enforcement_level Validation | should | canonical_root_level_exceptions_definition | SSID_structure_level3_part2_MAX.md:27 |
| SOT-648 | guard_enforcement.bypass_mechanism Validation | should | canonical_root_level_exceptions_definition | SSID_structure_level3_part2_MAX.md:27 |
| SOT-649 | guard_enforcement.violation_handling.immediate_fai... | must | canonical_root_level_exceptions_definition | SSID_structure_level3_part2_MAX.md:27 |
| SOT-650 | guard_enforcement.violation_handling.exit_code Val... | should | canonical_root_level_exceptions_definition | SSID_structure_level3_part2_MAX.md:27 |
| SOT-651 | guard_enforcement.violation_handling.quarantine_tr... | should | canonical_root_level_exceptions_definition | SSID_structure_level3_part2_MAX.md:27 |
| SOT-652 | guard_enforcement.violation_handling.escalation Va... | should | canonical_root_level_exceptions_definition | SSID_structure_level3_part2_MAX.md:27 |
| SOT-653 | guard_algorithm.step_1 Validation | should | canonical_root_level_exceptions_definition | SSID_structure_level3_part2_MAX.md:27 |
| SOT-654 | guard_algorithm.step_2 Validation | have | canonical_root_level_exceptions_definition | SSID_structure_level3_part2_MAX.md:27 |
| SOT-655 | guard_algorithm.step_3 Validation | should | canonical_root_level_exceptions_definition | SSID_structure_level3_part2_MAX.md:27 |
| SOT-656 | guard_algorithm.step_4 Validation | must | canonical_root_level_exceptions_definition | SSID_structure_level3_part2_MAX.md:27 |
| SOT-657 | guard_algorithm.step_5 Validation | should | canonical_root_level_exceptions_definition | SSID_structure_level3_part2_MAX.md:27 |
| SOT-658 | modification_process.approval_required[0] Validati... | must | canonical_root_level_exceptions_definition | SSID_structure_level3_part2_MAX.md:27 |
| SOT-659 | modification_process.approval_required[1] Validati... | must | canonical_root_level_exceptions_definition | SSID_structure_level3_part2_MAX.md:27 |
| SOT-660 | modification_process.approval_required[2] Validati... | must | canonical_root_level_exceptions_definition | SSID_structure_level3_part2_MAX.md:27 |
| SOT-661 | modification_process.documentation_required[0] Val... | must | canonical_root_level_exceptions_definition | SSID_structure_level3_part2_MAX.md:27 |
| SOT-662 | modification_process.documentation_required[1] Val... | must | canonical_root_level_exceptions_definition | SSID_structure_level3_part2_MAX.md:27 |
| SOT-663 | modification_process.documentation_required[2] Val... | must | canonical_root_level_exceptions_definition | SSID_structure_level3_part2_MAX.md:27 |
| SOT-664 | modification_process.documentation_required[3] Val... | must | canonical_root_level_exceptions_definition | SSID_structure_level3_part2_MAX.md:27 |
| SOT-665 | modification_process.change_procedure.step_1 Valid... | should | canonical_root_level_exceptions_definition | SSID_structure_level3_part2_MAX.md:27 |
| SOT-666 | modification_process.change_procedure.step_2 Valid... | should | canonical_root_level_exceptions_definition | SSID_structure_level3_part2_MAX.md:27 |
| SOT-667 | modification_process.change_procedure.step_3 Valid... | should | canonical_root_level_exceptions_definition | SSID_structure_level3_part2_MAX.md:27 |
| SOT-668 | modification_process.change_procedure.step_4 Valid... | should | canonical_root_level_exceptions_definition | SSID_structure_level3_part2_MAX.md:27 |
| SOT-669 | modification_process.change_procedure.step_5 Valid... | should | canonical_root_level_exceptions_definition | SSID_structure_level3_part2_MAX.md:27 |
| SOT-670 | anti_gaming_measures.no_wildcards Validation | have | canonical_root_level_exceptions_definition | SSID_structure_level3_part2_MAX.md:27 |
| SOT-671 | anti_gaming_measures.no_regex Validation | have | canonical_root_level_exceptions_definition | SSID_structure_level3_part2_MAX.md:27 |
| SOT-672 | anti_gaming_measures.explicit_enumeration Validati... | must | canonical_root_level_exceptions_definition | SSID_structure_level3_part2_MAX.md:27 |
| SOT-673 | anti_gaming_measures.case_sensitive Validation | must | canonical_root_level_exceptions_definition | SSID_structure_level3_part2_MAX.md:27 |
| SOT-674 | anti_gaming_measures.no_symlinks Validation | have | canonical_root_level_exceptions_definition | SSID_structure_level3_part2_MAX.md:27 |
| SOT-675 | anti_gaming_measures.no_hidden_directories Validat... | have | canonical_root_level_exceptions_definition | SSID_structure_level3_part2_MAX.md:27 |
| SOT-676 | integration_points.structure_guard Validation | should | canonical_root_level_exceptions_definition | SSID_structure_level3_part2_MAX.md:27 |
| SOT-677 | integration_points.ci_gates Validation | should | canonical_root_level_exceptions_definition | SSID_structure_level3_part2_MAX.md:27 |
| SOT-678 | integration_points.quarantine_system Validation | should | canonical_root_level_exceptions_definition | SSID_structure_level3_part2_MAX.md:27 |
| SOT-679 | integration_points.compliance_policies Validation | should | canonical_root_level_exceptions_definition | SSID_structure_level3_part2_MAX.md:27 |
| SOT-680 | audit_requirements.change_log Validation | should | canonical_root_level_exceptions_definition | SSID_structure_level3_part2_MAX.md:27 |
| SOT-681 | audit_requirements.review_cycle Validation | should | canonical_root_level_exceptions_definition | SSID_structure_level3_part2_MAX.md:27 |
| SOT-682 | audit_requirements.justification_retention Validat... | should | canonical_root_level_exceptions_definition | SSID_structure_level3_part2_MAX.md:27 |
| SOT-683 | audit_requirements.approval_trail Validation | must | canonical_root_level_exceptions_definition | SSID_structure_level3_part2_MAX.md:27 |
| SOT-684 | version Validation | should | maintainer_definition_backup_structure | SSID_structure_level3_part2_MAX.md:249 |
| SOT-685 | date Validation | should | maintainer_definition_backup_structure | SSID_structure_level3_part2_MAX.md:249 |
| SOT-686 | deprecated Validation | should | maintainer_definition_backup_structure | SSID_structure_level3_part2_MAX.md:249 |
| SOT-687 | classification Validation | should | maintainer_definition_backup_structure | SSID_structure_level3_part2_MAX.md:249 |
| SOT-688 | maintainer_structure.primary_maintainers.name Vali... | should | maintainer_definition_backup_structure | SSID_structure_level3_part2_MAX.md:249 |
| SOT-689 | maintainer_structure.primary_maintainers.role Vali... | should | maintainer_definition_backup_structure | SSID_structure_level3_part2_MAX.md:249 |
| SOT-690 | maintainer_structure.primary_maintainers.email Val... | should | maintainer_definition_backup_structure | SSID_structure_level3_part2_MAX.md:249 |
| SOT-691 | maintainer_structure.primary_maintainers.backup Va... | should | maintainer_definition_backup_structure | SSID_structure_level3_part2_MAX.md:249 |
| SOT-692 | maintainer_structure.primary_maintainers.areas[0] ... | should | maintainer_definition_backup_structure | SSID_structure_level3_part2_MAX.md:249 |
| SOT-693 | maintainer_structure.primary_maintainers.areas[1] ... | should | maintainer_definition_backup_structure | SSID_structure_level3_part2_MAX.md:249 |
| SOT-694 | maintainer_structure.primary_maintainers.areas[2] ... | should | maintainer_definition_backup_structure | SSID_structure_level3_part2_MAX.md:249 |
| SOT-695 | maintainer_structure.primary_maintainers.clearance... | should | maintainer_definition_backup_structure | SSID_structure_level3_part2_MAX.md:249 |
| SOT-696 | maintainer_structure.primary_maintainers.name Vali... | should | maintainer_definition_backup_structure | SSID_structure_level3_part2_MAX.md:249 |
| SOT-697 | maintainer_structure.primary_maintainers.role Vali... | should | maintainer_definition_backup_structure | SSID_structure_level3_part2_MAX.md:249 |
| SOT-698 | maintainer_structure.primary_maintainers.email Val... | should | maintainer_definition_backup_structure | SSID_structure_level3_part2_MAX.md:249 |
| SOT-699 | maintainer_structure.primary_maintainers.backup Va... | should | maintainer_definition_backup_structure | SSID_structure_level3_part2_MAX.md:249 |
| SOT-700 | maintainer_structure.primary_maintainers.areas[0] ... | should | maintainer_definition_backup_structure | SSID_structure_level3_part2_MAX.md:249 |
| SOT-701 | maintainer_structure.primary_maintainers.areas[1] ... | should | maintainer_definition_backup_structure | SSID_structure_level3_part2_MAX.md:249 |
| SOT-702 | maintainer_structure.primary_maintainers.areas[2] ... | should | maintainer_definition_backup_structure | SSID_structure_level3_part2_MAX.md:249 |
| SOT-703 | maintainer_structure.primary_maintainers.clearance... | should | maintainer_definition_backup_structure | SSID_structure_level3_part2_MAX.md:249 |
| SOT-704 | maintainer_structure.backup_escalation.level_1 Val... | should | maintainer_definition_backup_structure | SSID_structure_level3_part2_MAX.md:249 |
| SOT-705 | maintainer_structure.backup_escalation.level_2 Val... | should | maintainer_definition_backup_structure | SSID_structure_level3_part2_MAX.md:249 |
| SOT-706 | maintainer_structure.backup_escalation.level_3 Val... | should | maintainer_definition_backup_structure | SSID_structure_level3_part2_MAX.md:249 |
| SOT-707 | maintainer_structure.backup_escalation.level_4 Val... | should | maintainer_definition_backup_structure | SSID_structure_level3_part2_MAX.md:249 |
| SOT-708 | maintainer_structure.backup_escalation.emergency_c... | should | maintainer_definition_backup_structure | SSID_structure_level3_part2_MAX.md:249 |
| SOT-709 | maintainer_structure.backup_escalation.external_co... | should | maintainer_definition_backup_structure | SSID_structure_level3_part2_MAX.md:249 |
| SOT-710 | maintainer_structure.internal_review_maintainers.m... | should | maintainer_definition_backup_structure | SSID_structure_level3_part2_MAX.md:249 |
| SOT-711 | maintainer_structure.internal_review_maintainers.q... | should | maintainer_definition_backup_structure | SSID_structure_level3_part2_MAX.md:249 |
| SOT-712 | maintainer_structure.internal_review_maintainers.s... | should | maintainer_definition_backup_structure | SSID_structure_level3_part2_MAX.md:249 |
| SOT-713 | maintainer_structure.external_reviewer_pool[0] Val... | should | maintainer_definition_backup_structure | SSID_structure_level3_part2_MAX.md:249 |
| SOT-714 | maintainer_structure.external_reviewer_pool[1] Val... | should | maintainer_definition_backup_structure | SSID_structure_level3_part2_MAX.md:249 |
| SOT-715 | maintainer_structure.external_reviewer_pool[2] Val... | should | maintainer_definition_backup_structure | SSID_structure_level3_part2_MAX.md:249 |
| SOT-716 | maintainer_structure.review_coordinator Validation | should | maintainer_definition_backup_structure | SSID_structure_level3_part2_MAX.md:249 |
| SOT-717 | maintainer_structure.backup_coordinator Validation | should | maintainer_definition_backup_structure | SSID_structure_level3_part2_MAX.md:249 |
| SOT-718 | maintainer_structure.vacation_coverage.minimum_cov... | should | maintainer_definition_backup_structure | SSID_structure_level3_part2_MAX.md:249 |
| SOT-719 | maintainer_structure.vacation_coverage.notificatio... | should | maintainer_definition_backup_structure | SSID_structure_level3_part2_MAX.md:249 |
| SOT-720 | maintainer_structure.vacation_coverage.handover_re... | must | maintainer_definition_backup_structure | SSID_structure_level3_part2_MAX.md:249 |
| SOT-721 | maintainer_structure.vacation_coverage.documentati... | should | maintainer_definition_backup_structure | SSID_structure_level3_part2_MAX.md:249 |
| SOT-722 | maintainer_structure.vacation_coverage.business_co... | must | maintainer_definition_backup_structure | SSID_structure_level3_part2_MAX.md:249 |
| SOT-723 | **Internal Override:** Business-critical modules >... | must | structure_compliance_badge | SSID_structure_level3_part2_MAX.md:312 |
| SOT-724 | **Source:** `pytest.ini:coverage_threshold` + `.gi... | have | test_coverage_badge_tiered | SSID_structure_level3_part2_MAX.md:315 |
| SOT-725 | **Business-Critical:** >= 95% (enforcement via CI ... | must | test_coverage_badge_tiered | SSID_structure_level3_part2_MAX.md:318 |
| SOT-726 | **Formula:** (Implemented Controls / Total Require... | must | compliance_coverage_badge_internal | SSID_structure_level3_part2_MAX.md:324 |
| SOT-727 | version Validation | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-728 | date Validation | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-729 | deprecated Validation | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-730 | classification Validation | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-731 | international_standards.geographic_coverage.region... | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-732 | international_standards.geographic_coverage.standa... | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-733 | international_standards.geographic_coverage.standa... | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-734 | international_standards.geographic_coverage.standa... | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-735 | international_standards.geographic_coverage.standa... | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-736 | international_standards.geographic_coverage.standa... | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-737 | international_standards.geographic_coverage.locali... | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-738 | international_standards.geographic_coverage.busine... | must | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-739 | international_standards.geographic_coverage.region... | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-740 | international_standards.geographic_coverage.standa... | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-741 | international_standards.geographic_coverage.standa... | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-742 | international_standards.geographic_coverage.standa... | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-743 | international_standards.geographic_coverage.standa... | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-744 | international_standards.geographic_coverage.locali... | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-745 | international_standards.geographic_coverage.busine... | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-746 | international_standards.geographic_coverage.region... | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-747 | international_standards.geographic_coverage.standa... | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-748 | international_standards.geographic_coverage.standa... | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-749 | international_standards.geographic_coverage.standa... | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-750 | international_standards.geographic_coverage.standa... | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-751 | international_standards.geographic_coverage.locali... | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-752 | international_standards.geographic_coverage.busine... | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-753 | international_standards.geographic_coverage.region... | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-754 | international_standards.geographic_coverage.standa... | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-755 | international_standards.geographic_coverage.standa... | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-756 | international_standards.geographic_coverage.standa... | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-757 | international_standards.geographic_coverage.locali... | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-758 | international_standards.geographic_coverage.busine... | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-759 | international_standards.geographic_coverage.region... | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-760 | international_standards.geographic_coverage.standa... | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-761 | international_standards.geographic_coverage.standa... | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-762 | international_standards.geographic_coverage.standa... | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-763 | international_standards.geographic_coverage.locali... | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-764 | international_standards.geographic_coverage.busine... | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-765 | accessibility_compliance.wcag_version Validation | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-766 | accessibility_compliance.baseline Validation | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-767 | accessibility_compliance.aaa_scope Validation | must | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-768 | accessibility_compliance.screen_reader_compatible ... | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-769 | accessibility_compliance.keyboard_navigation Valid... | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-770 | accessibility_compliance.color_contrast_ratio Vali... | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-771 | accessibility_compliance.language_support[0] Valid... | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-772 | accessibility_compliance.language_support[1] Valid... | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-773 | accessibility_compliance.language_support[2] Valid... | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-774 | accessibility_compliance.language_support[3] Valid... | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-775 | accessibility_compliance.language_support[4] Valid... | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-776 | accessibility_compliance.language_support[5] Valid... | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-777 | accessibility_compliance.language_support[6] Valid... | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-778 | accessibility_compliance.language_support[7] Valid... | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-779 | accessibility_compliance.rtl_language_support Vali... | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-780 | accessibility_compliance.business_localization Val... | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-781 | accessibility_compliance.wcag_aaa_note Validation | must | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-782 | community_participation.open_contribution Validati... | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-783 | community_participation.translation_program Valida... | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-784 | community_participation.accessibility_review Valid... | must | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-785 | community_participation.diverse_reviewer_pool Vali... | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-786 | community_participation.enterprise_participation V... | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-787 | community_participation.marginalized_communities.s... | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-788 | community_participation.marginalized_communities.a... | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-789 | community_participation.marginalized_communities.t... | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-790 | community_participation.marginalized_communities.t... | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-791 | community_participation.marginalized_communities.o... | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-792 | community_participation.marginalized_communities.b... | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-793 | community_participation.economic_inclusion.low_inc... | have | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-794 | community_participation.economic_inclusion.educati... | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-795 | community_participation.economic_inclusion.develop... | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-796 | community_participation.economic_inclusion.interne... | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-797 | community_participation.economic_inclusion.enterpr... | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-798 | dao_governance_compatibility.governance_models[0] ... | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-799 | dao_governance_compatibility.governance_models[1] ... | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-800 | dao_governance_compatibility.governance_models[2] ... | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-801 | dao_governance_compatibility.governance_models[3] ... | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-802 | dao_governance_compatibility.governance_models[4] ... | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-803 | dao_governance_compatibility.governance_models[5] ... | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-804 | dao_governance_compatibility.governance_models[6] ... | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-805 | dao_governance_compatibility.governance_models[7] ... | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-806 | dao_governance_compatibility.voting_mechanisms[0] ... | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-807 | dao_governance_compatibility.voting_mechanisms[1] ... | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-808 | dao_governance_compatibility.voting_mechanisms[2] ... | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-809 | dao_governance_compatibility.voting_mechanisms[3] ... | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-810 | dao_governance_compatibility.voting_mechanisms[4] ... | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-811 | dao_governance_compatibility.voting_mechanisms[5] ... | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-812 | dao_governance_compatibility.voting_mechanisms[6] ... | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-813 | dao_governance_compatibility.decision_frameworks.c... | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-814 | dao_governance_compatibility.decision_frameworks.c... | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-815 | dao_governance_compatibility.decision_frameworks.c... | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-816 | dao_governance_compatibility.decision_frameworks.c... | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-817 | dao_governance_compatibility.decision_frameworks.q... | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-818 | dao_governance_compatibility.decision_frameworks.p... | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-819 | dao_governance_compatibility.decision_frameworks.v... | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-820 | dao_governance_compatibility.decision_frameworks.b... | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-821 | unbanked_community_support.no_bank_account_require... | must | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-822 | unbanked_community_support.alternative_identity_ve... | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-823 | unbanked_community_support.offline_capability Vali... | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-824 | unbanked_community_support.sms_notifications Valid... | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-825 | unbanked_community_support.ussd_support Validation | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-826 | unbanked_community_support.agent_network_compatibl... | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-827 | unbanked_community_support.enterprise_financial_in... | should | diversity_inclusion_standards | SSID_structure_level3_part2_MAX.md:339 |
| SOT-828 | version Validation | should | esg_sustainability_integration | SSID_structure_level3_part2_MAX.md:444 |
| SOT-829 | date Validation | should | esg_sustainability_integration | SSID_structure_level3_part2_MAX.md:444 |
| SOT-830 | deprecated Validation | should | esg_sustainability_integration | SSID_structure_level3_part2_MAX.md:444 |
| SOT-831 | classification Validation | should | esg_sustainability_integration | SSID_structure_level3_part2_MAX.md:444 |
| SOT-832 | environmental_standards.carbon_footprint.tracking_... | should | esg_sustainability_integration | SSID_structure_level3_part2_MAX.md:444 |
| SOT-833 | environmental_standards.carbon_footprint.reporting... | should | esg_sustainability_integration | SSID_structure_level3_part2_MAX.md:444 |
| SOT-834 | environmental_standards.carbon_footprint.target Va... | should | esg_sustainability_integration | SSID_structure_level3_part2_MAX.md:444 |
| SOT-835 | environmental_standards.carbon_footprint.offset_pr... | should | esg_sustainability_integration | SSID_structure_level3_part2_MAX.md:444 |
| SOT-836 | environmental_standards.carbon_footprint.business_... | should | esg_sustainability_integration | SSID_structure_level3_part2_MAX.md:444 |
| SOT-837 | environmental_standards.energy_efficiency.green_ho... | should | esg_sustainability_integration | SSID_structure_level3_part2_MAX.md:444 |
| SOT-838 | environmental_standards.energy_efficiency.renewabl... | should | esg_sustainability_integration | SSID_structure_level3_part2_MAX.md:444 |
| SOT-839 | environmental_standards.energy_efficiency.energy_m... | should | esg_sustainability_integration | SSID_structure_level3_part2_MAX.md:444 |
| SOT-840 | environmental_standards.energy_efficiency.cost_opt... | should | esg_sustainability_integration | SSID_structure_level3_part2_MAX.md:444 |
| SOT-841 | environmental_standards.circular_economy.code_reus... | should | esg_sustainability_integration | SSID_structure_level3_part2_MAX.md:444 |
| SOT-842 | environmental_standards.circular_economy.resource_... | should | esg_sustainability_integration | SSID_structure_level3_part2_MAX.md:444 |
| SOT-843 | environmental_standards.circular_economy.waste_red... | should | esg_sustainability_integration | SSID_structure_level3_part2_MAX.md:444 |
| SOT-844 | environmental_standards.circular_economy.business_... | should | esg_sustainability_integration | SSID_structure_level3_part2_MAX.md:444 |
| SOT-845 | social_responsibility.un_sdg_mapping.sdg_1 Validat... | should | esg_sustainability_integration | SSID_structure_level3_part2_MAX.md:444 |
| SOT-846 | social_responsibility.un_sdg_mapping.sdg_4 Validat... | should | esg_sustainability_integration | SSID_structure_level3_part2_MAX.md:444 |
| SOT-847 | social_responsibility.un_sdg_mapping.sdg_5 Validat... | should | esg_sustainability_integration | SSID_structure_level3_part2_MAX.md:444 |
| SOT-848 | social_responsibility.un_sdg_mapping.sdg_8 Validat... | should | esg_sustainability_integration | SSID_structure_level3_part2_MAX.md:444 |
| SOT-849 | social_responsibility.un_sdg_mapping.sdg_10 Valida... | should | esg_sustainability_integration | SSID_structure_level3_part2_MAX.md:444 |
| SOT-850 | social_responsibility.un_sdg_mapping.sdg_16 Valida... | should | esg_sustainability_integration | SSID_structure_level3_part2_MAX.md:444 |
| SOT-851 | social_responsibility.un_sdg_mapping.sdg_17 Valida... | should | esg_sustainability_integration | SSID_structure_level3_part2_MAX.md:444 |
| SOT-852 | social_responsibility.social_impact_metrics.access... | should | esg_sustainability_integration | SSID_structure_level3_part2_MAX.md:444 |
| SOT-853 | social_responsibility.social_impact_metrics.inclus... | should | esg_sustainability_integration | SSID_structure_level3_part2_MAX.md:444 |
| SOT-854 | social_responsibility.social_impact_metrics.commun... | should | esg_sustainability_integration | SSID_structure_level3_part2_MAX.md:444 |
| SOT-855 | social_responsibility.social_impact_metrics.contri... | should | esg_sustainability_integration | SSID_structure_level3_part2_MAX.md:444 |
| SOT-856 | social_responsibility.social_impact_metrics.busine... | should | esg_sustainability_integration | SSID_structure_level3_part2_MAX.md:444 |
| SOT-857 | governance_excellence.transparency_requirements[0]... | should | esg_sustainability_integration | SSID_structure_level3_part2_MAX.md:444 |
| SOT-858 | governance_excellence.transparency_requirements[1]... | must | esg_sustainability_integration | SSID_structure_level3_part2_MAX.md:444 |
| SOT-859 | governance_excellence.transparency_requirements[2]... | should | esg_sustainability_integration | SSID_structure_level3_part2_MAX.md:444 |
| SOT-860 | governance_excellence.transparency_requirements[3]... | should | esg_sustainability_integration | SSID_structure_level3_part2_MAX.md:444 |
| SOT-861 | governance_excellence.transparency_requirements[4]... | should | esg_sustainability_integration | SSID_structure_level3_part2_MAX.md:444 |
| SOT-862 | governance_excellence.ethics_framework.code_of_con... | should | esg_sustainability_integration | SSID_structure_level3_part2_MAX.md:444 |
| SOT-863 | governance_excellence.ethics_framework.conflict_of... | should | esg_sustainability_integration | SSID_structure_level3_part2_MAX.md:444 |
| SOT-864 | governance_excellence.ethics_framework.whistleblow... | have | esg_sustainability_integration | SSID_structure_level3_part2_MAX.md:444 |
| SOT-865 | governance_excellence.ethics_framework.business_et... | should | esg_sustainability_integration | SSID_structure_level3_part2_MAX.md:444 |
| SOT-866 | governance_excellence.stakeholder_engagement.user_... | should | esg_sustainability_integration | SSID_structure_level3_part2_MAX.md:444 |
| SOT-867 | governance_excellence.stakeholder_engagement.devel... | should | esg_sustainability_integration | SSID_structure_level3_part2_MAX.md:444 |
| SOT-868 | governance_excellence.stakeholder_engagement.regul... | should | esg_sustainability_integration | SSID_structure_level3_part2_MAX.md:444 |
| SOT-869 | governance_excellence.stakeholder_engagement.commu... | should | esg_sustainability_integration | SSID_structure_level3_part2_MAX.md:444 |
| SOT-870 | governance_excellence.stakeholder_engagement.enter... | should | esg_sustainability_integration | SSID_structure_level3_part2_MAX.md:444 |
| SOT-871 | version Validation | should | multi_sector_compatibility_matrix | SSID_structure_level3_part2_MAX.md:511 |
| SOT-872 | date Validation | should | multi_sector_compatibility_matrix | SSID_structure_level3_part2_MAX.md:511 |
| SOT-873 | deprecated Validation | should | multi_sector_compatibility_matrix | SSID_structure_level3_part2_MAX.md:511 |
| SOT-874 | classification Validation | should | multi_sector_compatibility_matrix | SSID_structure_level3_part2_MAX.md:511 |
| SOT-875 | sector_support.financial_services.regulations[0] V... | should | multi_sector_compatibility_matrix | SSID_structure_level3_part2_MAX.md:511 |
| SOT-876 | sector_support.financial_services.regulations[1] V... | should | multi_sector_compatibility_matrix | SSID_structure_level3_part2_MAX.md:511 |
| SOT-877 | sector_support.financial_services.regulations[2] V... | should | multi_sector_compatibility_matrix | SSID_structure_level3_part2_MAX.md:511 |
| SOT-878 | sector_support.financial_services.regulations[3] V... | should | multi_sector_compatibility_matrix | SSID_structure_level3_part2_MAX.md:511 |
| SOT-879 | sector_support.financial_services.regulations[4] V... | should | multi_sector_compatibility_matrix | SSID_structure_level3_part2_MAX.md:511 |
| SOT-880 | sector_support.financial_services.regulations[5] V... | should | multi_sector_compatibility_matrix | SSID_structure_level3_part2_MAX.md:511 |
| SOT-881 | sector_support.financial_services.risk_level Valid... | should | multi_sector_compatibility_matrix | SSID_structure_level3_part2_MAX.md:511 |
| SOT-882 | sector_support.financial_services.audit_frequency ... | should | multi_sector_compatibility_matrix | SSID_structure_level3_part2_MAX.md:511 |
| SOT-883 | sector_support.financial_services.specialized_cont... | should | multi_sector_compatibility_matrix | SSID_structure_level3_part2_MAX.md:511 |
| SOT-884 | sector_support.financial_services.business_opportu... | should | multi_sector_compatibility_matrix | SSID_structure_level3_part2_MAX.md:511 |
| SOT-885 | sector_support.financial_services.revenue_potentia... | should | multi_sector_compatibility_matrix | SSID_structure_level3_part2_MAX.md:511 |
| SOT-886 | sector_support.healthcare.regulations[0] Validatio... | should | multi_sector_compatibility_matrix | SSID_structure_level3_part2_MAX.md:511 |
| SOT-887 | sector_support.healthcare.regulations[1] Validatio... | should | multi_sector_compatibility_matrix | SSID_structure_level3_part2_MAX.md:511 |
| SOT-888 | sector_support.healthcare.regulations[2] Validatio... | should | multi_sector_compatibility_matrix | SSID_structure_level3_part2_MAX.md:511 |
| SOT-889 | sector_support.healthcare.regulations[3] Validatio... | should | multi_sector_compatibility_matrix | SSID_structure_level3_part2_MAX.md:511 |
| SOT-890 | sector_support.healthcare.regulations[4] Validatio... | should | multi_sector_compatibility_matrix | SSID_structure_level3_part2_MAX.md:511 |
| SOT-891 | sector_support.healthcare.risk_level Validation | must | multi_sector_compatibility_matrix | SSID_structure_level3_part2_MAX.md:511 |
| SOT-892 | sector_support.healthcare.audit_frequency Validati... | should | multi_sector_compatibility_matrix | SSID_structure_level3_part2_MAX.md:511 |
| SOT-893 | sector_support.healthcare.specialized_controls Val... | should | multi_sector_compatibility_matrix | SSID_structure_level3_part2_MAX.md:511 |
| SOT-894 | sector_support.healthcare.business_opportunity Val... | should | multi_sector_compatibility_matrix | SSID_structure_level3_part2_MAX.md:511 |
| SOT-895 | sector_support.healthcare.revenue_potential Valida... | should | multi_sector_compatibility_matrix | SSID_structure_level3_part2_MAX.md:511 |
| SOT-896 | sector_support.government_public_sector.regulation... | should | multi_sector_compatibility_matrix | SSID_structure_level3_part2_MAX.md:511 |
| SOT-897 | sector_support.government_public_sector.regulation... | should | multi_sector_compatibility_matrix | SSID_structure_level3_part2_MAX.md:511 |
| SOT-898 | sector_support.government_public_sector.regulation... | should | multi_sector_compatibility_matrix | SSID_structure_level3_part2_MAX.md:511 |
| SOT-899 | sector_support.government_public_sector.regulation... | should | multi_sector_compatibility_matrix | SSID_structure_level3_part2_MAX.md:511 |
| SOT-900 | sector_support.government_public_sector.risk_level... | must | multi_sector_compatibility_matrix | SSID_structure_level3_part2_MAX.md:511 |
| SOT-901 | sector_support.government_public_sector.audit_freq... | should | multi_sector_compatibility_matrix | SSID_structure_level3_part2_MAX.md:511 |
| SOT-902 | sector_support.government_public_sector.specialize... | should | multi_sector_compatibility_matrix | SSID_structure_level3_part2_MAX.md:511 |
| SOT-903 | sector_support.government_public_sector.business_o... | should | multi_sector_compatibility_matrix | SSID_structure_level3_part2_MAX.md:511 |
| SOT-904 | sector_support.government_public_sector.revenue_po... | should | multi_sector_compatibility_matrix | SSID_structure_level3_part2_MAX.md:511 |
| SOT-905 | sector_support.education.regulations[0] Validation | should | multi_sector_compatibility_matrix | SSID_structure_level3_part2_MAX.md:511 |
| SOT-906 | sector_support.education.regulations[1] Validation | should | multi_sector_compatibility_matrix | SSID_structure_level3_part2_MAX.md:511 |
| SOT-907 | sector_support.education.regulations[2] Validation | should | multi_sector_compatibility_matrix | SSID_structure_level3_part2_MAX.md:511 |
| SOT-908 | sector_support.education.regulations[3] Validation | should | multi_sector_compatibility_matrix | SSID_structure_level3_part2_MAX.md:511 |
| SOT-909 | sector_support.education.risk_level Validation | should | multi_sector_compatibility_matrix | SSID_structure_level3_part2_MAX.md:511 |
| SOT-910 | sector_support.education.audit_frequency Validatio... | should | multi_sector_compatibility_matrix | SSID_structure_level3_part2_MAX.md:511 |
| SOT-911 | sector_support.education.specialized_controls Vali... | should | multi_sector_compatibility_matrix | SSID_structure_level3_part2_MAX.md:511 |
| SOT-912 | sector_support.education.business_opportunity Vali... | should | multi_sector_compatibility_matrix | SSID_structure_level3_part2_MAX.md:511 |
| SOT-913 | sector_support.education.revenue_potential Validat... | should | multi_sector_compatibility_matrix | SSID_structure_level3_part2_MAX.md:511 |
| SOT-914 | sector_support.gaming_entertainment.regulations[0]... | should | multi_sector_compatibility_matrix | SSID_structure_level3_part2_MAX.md:511 |
| SOT-915 | sector_support.gaming_entertainment.regulations[1]... | should | multi_sector_compatibility_matrix | SSID_structure_level3_part2_MAX.md:511 |
| SOT-916 | sector_support.gaming_entertainment.regulations[2]... | should | multi_sector_compatibility_matrix | SSID_structure_level3_part2_MAX.md:511 |
| SOT-917 | sector_support.gaming_entertainment.regulations[3]... | should | multi_sector_compatibility_matrix | SSID_structure_level3_part2_MAX.md:511 |
| SOT-918 | sector_support.gaming_entertainment.risk_level Val... | should | multi_sector_compatibility_matrix | SSID_structure_level3_part2_MAX.md:511 |
| SOT-919 | sector_support.gaming_entertainment.audit_frequenc... | should | multi_sector_compatibility_matrix | SSID_structure_level3_part2_MAX.md:511 |
| SOT-920 | sector_support.gaming_entertainment.specialized_co... | should | multi_sector_compatibility_matrix | SSID_structure_level3_part2_MAX.md:511 |
| SOT-921 | sector_support.gaming_entertainment.business_oppor... | should | multi_sector_compatibility_matrix | SSID_structure_level3_part2_MAX.md:511 |
| SOT-922 | sector_support.gaming_entertainment.revenue_potent... | should | multi_sector_compatibility_matrix | SSID_structure_level3_part2_MAX.md:511 |
| SOT-923 | sector_support.iot_manufacturing.regulations[0] Va... | should | multi_sector_compatibility_matrix | SSID_structure_level3_part2_MAX.md:511 |
| SOT-924 | sector_support.iot_manufacturing.regulations[1] Va... | should | multi_sector_compatibility_matrix | SSID_structure_level3_part2_MAX.md:511 |
| SOT-925 | sector_support.iot_manufacturing.regulations[2] Va... | should | multi_sector_compatibility_matrix | SSID_structure_level3_part2_MAX.md:511 |
| SOT-926 | sector_support.iot_manufacturing.regulations[3] Va... | should | multi_sector_compatibility_matrix | SSID_structure_level3_part2_MAX.md:511 |
| SOT-927 | sector_support.iot_manufacturing.risk_level Valida... | should | multi_sector_compatibility_matrix | SSID_structure_level3_part2_MAX.md:511 |
| SOT-928 | sector_support.iot_manufacturing.audit_frequency V... | should | multi_sector_compatibility_matrix | SSID_structure_level3_part2_MAX.md:511 |
| SOT-929 | sector_support.iot_manufacturing.specialized_contr... | should | multi_sector_compatibility_matrix | SSID_structure_level3_part2_MAX.md:511 |
| SOT-930 | sector_support.iot_manufacturing.business_opportun... | should | multi_sector_compatibility_matrix | SSID_structure_level3_part2_MAX.md:511 |
| SOT-931 | sector_support.iot_manufacturing.revenue_potential... | should | multi_sector_compatibility_matrix | SSID_structure_level3_part2_MAX.md:511 |
| SOT-932 | cross_sector_features.regulatory_change_notificati... | should | multi_sector_compatibility_matrix | SSID_structure_level3_part2_MAX.md:511 |
| SOT-933 | cross_sector_features.sector_specific_templates Va... | should | multi_sector_compatibility_matrix | SSID_structure_level3_part2_MAX.md:511 |
| SOT-934 | cross_sector_features.compliance_gap_analysis Vali... | should | multi_sector_compatibility_matrix | SSID_structure_level3_part2_MAX.md:511 |
| SOT-935 | cross_sector_features.risk_assessment_tools Valida... | should | multi_sector_compatibility_matrix | SSID_structure_level3_part2_MAX.md:511 |
| SOT-936 | cross_sector_features.audit_preparation Validation | should | multi_sector_compatibility_matrix | SSID_structure_level3_part2_MAX.md:511 |
| SOT-937 | cross_sector_features.business_development Validat... | should | multi_sector_compatibility_matrix | SSID_structure_level3_part2_MAX.md:511 |
| SOT-938 | `agents/` → Agenten-Frameworks, Policy- und Workfl... | have | 1_kern_module | SSID_structure_level3_part2_MAX.md:616 |
| SOT-939 | `flows/` → Authentifizierungsflows | have | 1_kern_module | SSID_structure_level3_part2_MAX.md:642 |
| SOT-940 | `ci/blueprints/` → CI-Blueprints, Workflow-Vorlage... | have | 3_tech_module | SSID_structure_level3_part2_MAX.md:670 |
| SOT-941 | version Validation | should | badge_threshold_justification_enhanced | SSID_structure_level3_part2_MAX.md:806 |
| SOT-942 | date Validation | should | badge_threshold_justification_enhanced | SSID_structure_level3_part2_MAX.md:806 |
| SOT-943 | deprecated Validation | should | badge_threshold_justification_enhanced | SSID_structure_level3_part2_MAX.md:806 |
| SOT-944 | classification Validation | should | badge_threshold_justification_enhanced | SSID_structure_level3_part2_MAX.md:806 |
| SOT-945 | last_review Validation | should | badge_threshold_justification_enhanced | SSID_structure_level3_part2_MAX.md:806 |
| SOT-946 | next_review Validation | should | badge_threshold_justification_enhanced | SSID_structure_level3_part2_MAX.md:806 |
| SOT-947 | thresholds.structure_compliance.threshold Validati... | should | badge_threshold_justification_enhanced | SSID_structure_level3_part2_MAX.md:806 |
| SOT-948 | thresholds.structure_compliance.rationale Validati... | should | badge_threshold_justification_enhanced | SSID_structure_level3_part2_MAX.md:806 |
| SOT-949 | thresholds.structure_compliance.business_impact Va... | must | badge_threshold_justification_enhanced | SSID_structure_level3_part2_MAX.md:806 |
| SOT-950 | thresholds.structure_compliance.internal_note Vali... | should | badge_threshold_justification_enhanced | SSID_structure_level3_part2_MAX.md:806 |
| SOT-951 | thresholds.structure_compliance.deprecated Validat... | should | badge_threshold_justification_enhanced | SSID_structure_level3_part2_MAX.md:806 |
| SOT-952 | thresholds.structure_compliance.benchmark_source V... | should | badge_threshold_justification_enhanced | SSID_structure_level3_part2_MAX.md:806 |
| SOT-953 | thresholds.test_coverage.threshold Validation | should | badge_threshold_justification_enhanced | SSID_structure_level3_part2_MAX.md:806 |
| SOT-954 | thresholds.test_coverage.rationale Validation | should | badge_threshold_justification_enhanced | SSID_structure_level3_part2_MAX.md:806 |
| SOT-955 | thresholds.test_coverage.business_impact Validatio... | should | badge_threshold_justification_enhanced | SSID_structure_level3_part2_MAX.md:806 |
| SOT-956 | thresholds.test_coverage.deprecated Validation | should | badge_threshold_justification_enhanced | SSID_structure_level3_part2_MAX.md:806 |
| SOT-957 | thresholds.test_coverage.tiered_requirements.busin... | must | badge_threshold_justification_enhanced | SSID_structure_level3_part2_MAX.md:806 |
| SOT-958 | thresholds.test_coverage.tiered_requirements.secur... | should | badge_threshold_justification_enhanced | SSID_structure_level3_part2_MAX.md:806 |
| SOT-959 | thresholds.test_coverage.tiered_requirements.compl... | should | badge_threshold_justification_enhanced | SSID_structure_level3_part2_MAX.md:806 |
| SOT-960 | thresholds.test_coverage.internal_exception Valida... | must | badge_threshold_justification_enhanced | SSID_structure_level3_part2_MAX.md:806 |
| SOT-961 | thresholds.compliance_coverage.threshold Validatio... | should | badge_threshold_justification_enhanced | SSID_structure_level3_part2_MAX.md:806 |
| SOT-962 | thresholds.compliance_coverage.rationale Validatio... | should | badge_threshold_justification_enhanced | SSID_structure_level3_part2_MAX.md:806 |
| SOT-963 | thresholds.compliance_coverage.business_impact Val... | must | badge_threshold_justification_enhanced | SSID_structure_level3_part2_MAX.md:806 |
| SOT-964 | thresholds.compliance_coverage.deprecated Validati... | should | badge_threshold_justification_enhanced | SSID_structure_level3_part2_MAX.md:806 |
| SOT-965 | thresholds.compliance_coverage.jurisdictional_requ... | should | badge_threshold_justification_enhanced | SSID_structure_level3_part2_MAX.md:806 |
| SOT-966 | thresholds.compliance_coverage.jurisdictional_requ... | should | badge_threshold_justification_enhanced | SSID_structure_level3_part2_MAX.md:806 |
| SOT-967 | thresholds.compliance_coverage.jurisdictional_requ... | should | badge_threshold_justification_enhanced | SSID_structure_level3_part2_MAX.md:806 |
| SOT-968 | thresholds.compliance_coverage.jurisdictional_requ... | should | badge_threshold_justification_enhanced | SSID_structure_level3_part2_MAX.md:806 |
| SOT-969 | thresholds.compliance_coverage.jurisdictions Valid... | should | badge_threshold_justification_enhanced | SSID_structure_level3_part2_MAX.md:806 |
| SOT-970 | thresholds.review_cycle.requirement Validation | should | badge_threshold_justification_enhanced | SSID_structure_level3_part2_MAX.md:806 |
| SOT-971 | thresholds.review_cycle.rationale Validation | should | badge_threshold_justification_enhanced | SSID_structure_level3_part2_MAX.md:806 |
| SOT-972 | thresholds.review_cycle.cost_benefit Validation | should | badge_threshold_justification_enhanced | SSID_structure_level3_part2_MAX.md:806 |
| SOT-973 | thresholds.review_cycle.deprecated Validation | should | badge_threshold_justification_enhanced | SSID_structure_level3_part2_MAX.md:806 |
| SOT-974 | thresholds.review_cycle.escalation_trigger Validat... | should | badge_threshold_justification_enhanced | SSID_structure_level3_part2_MAX.md:806 |
| SOT-975 | **90+ = HIGH** (Release mit Monitoring) | should | badge_threshold_justification_enhanced | SSID_structure_level3_part2_MAX.md:857 |
| SOT-976 | **<70 = LOW** (Sanierung erforderlich) | have | badge_threshold_justification_enhanced | SSID_structure_level3_part2_MAX.md:859 |
| SOT-977 | version Validation | should | badge_integrity_framework_enterprise | SSID_structure_level3_part2_MAX.md:864 |
| SOT-978 | date Validation | should | badge_integrity_framework_enterprise | SSID_structure_level3_part2_MAX.md:864 |
| SOT-979 | deprecated Validation | should | badge_integrity_framework_enterprise | SSID_structure_level3_part2_MAX.md:864 |
| SOT-980 | classification Validation | should | badge_integrity_framework_enterprise | SSID_structure_level3_part2_MAX.md:864 |
| SOT-981 | controls.circular_dependency_check.description Val... | should | badge_integrity_framework_enterprise | SSID_structure_level3_part2_MAX.md:864 |
| SOT-982 | controls.circular_dependency_check.script Validati... | should | badge_integrity_framework_enterprise | SSID_structure_level3_part2_MAX.md:864 |
| SOT-983 | controls.circular_dependency_check.script_deprecat... | should | badge_integrity_framework_enterprise | SSID_structure_level3_part2_MAX.md:864 |
| SOT-984 | controls.circular_dependency_check.frequency Valid... | should | badge_integrity_framework_enterprise | SSID_structure_level3_part2_MAX.md:864 |
| SOT-985 | controls.circular_dependency_check.threshold Valid... | have | badge_integrity_framework_enterprise | SSID_structure_level3_part2_MAX.md:864 |
| SOT-986 | controls.circular_dependency_check.escalation Vali... | should | badge_integrity_framework_enterprise | SSID_structure_level3_part2_MAX.md:864 |
| SOT-987 | controls.circular_dependency_check.dependency_map_... | should | badge_integrity_framework_enterprise | SSID_structure_level3_part2_MAX.md:864 |
| SOT-988 | controls.circular_dependency_check.export_formats[... | should | badge_integrity_framework_enterprise | SSID_structure_level3_part2_MAX.md:864 |
| SOT-989 | controls.circular_dependency_check.export_formats[... | should | badge_integrity_framework_enterprise | SSID_structure_level3_part2_MAX.md:864 |
| SOT-990 | controls.circular_dependency_check.export_formats[... | should | badge_integrity_framework_enterprise | SSID_structure_level3_part2_MAX.md:864 |
| SOT-991 | controls.circular_dependency_check.export_formats[... | should | badge_integrity_framework_enterprise | SSID_structure_level3_part2_MAX.md:864 |
| SOT-992 | controls.business_logic_overfitting.description Va... | should | badge_integrity_framework_enterprise | SSID_structure_level3_part2_MAX.md:864 |
| SOT-993 | controls.business_logic_overfitting.method Validat... | should | badge_integrity_framework_enterprise | SSID_structure_level3_part2_MAX.md:864 |
| SOT-994 | controls.business_logic_overfitting.script Validat... | should | badge_integrity_framework_enterprise | SSID_structure_level3_part2_MAX.md:864 |
| SOT-995 | controls.business_logic_overfitting.script_depreca... | should | badge_integrity_framework_enterprise | SSID_structure_level3_part2_MAX.md:864 |
| SOT-996 | controls.business_logic_overfitting.frequency Vali... | should | badge_integrity_framework_enterprise | SSID_structure_level3_part2_MAX.md:864 |
| SOT-997 | controls.business_logic_overfitting.sample_size Va... | should | badge_integrity_framework_enterprise | SSID_structure_level3_part2_MAX.md:864 |
| SOT-998 | controls.business_logic_overfitting.reviewer_requi... | must | badge_integrity_framework_enterprise | SSID_structure_level3_part2_MAX.md:864 |
| SOT-999 | controls.business_logic_overfitting.internal_audit... | should | badge_integrity_framework_enterprise | SSID_structure_level3_part2_MAX.md:864 |