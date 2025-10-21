# FATF Travel Rule Policy (SoT Rules 6-7)
# =========================================
# Lines 34-45 from SSID_structure_level3_part3_MAX.md
#
# Scientific Foundation: FATF Recommendation 16, IVMS101 Standard
# Technical Manifestation: OPA policy enforcement

package ssid.sot.fatf

import future.keywords.if
import future.keywords.in

# SoT Rule 6: IVMS101-2023 Validation
deny contains msg if {
    input.ivms101_2023
    not input.ivms101_2023.name == "IVMS101-2023 Datenmodell & Mapping-Templates"
    msg := sprintf("[RULE-6] Invalid ivms101_2023 name: %v", [input.ivms101_2023.name])
}

deny contains msg if {
    input.ivms101_2023
    not input.ivms101_2023.path == "23_compliance/global/fatf/travel_rule/ivms101_2023/"
    msg := sprintf("[RULE-6] Invalid ivms101_2023 path: %v. Expected: 23_compliance/global/fatf/travel_rule/ivms101_2023/", [input.ivms101_2023.path])
}

deny contains msg if {
    input.ivms101_2023
    not input.ivms101_2023.deprecated == false
    msg := "[RULE-6] IVMS101-2023 must not be deprecated (current standard)"
}

deny contains msg if {
    input.ivms101_2023
    not input.ivms101_2023.business_priority == "CRITICAL"
    msg := sprintf("[RULE-6] IVMS101-2023 must have CRITICAL priority, got: %v", [input.ivms101_2023.business_priority])
}

# SoT Rule 7: FATF R.16 2025 Update Validation
deny contains msg if {
    input.fatf_rec16_2025_update
    not input.fatf_rec16_2025_update.name == "R.16-Änderungen Juni 2025 Gap-Analyse"
    msg := sprintf("[RULE-7] Invalid fatf_rec16_2025_update name: %v", [input.fatf_rec16_2025_update.name])
}

deny contains msg if {
    input.fatf_rec16_2025_update
    not input.fatf_rec16_2025_update.path == "23_compliance/global/fatf/travel_rule/fatf_rec16_2025_update/"
    msg := sprintf("[RULE-7] Invalid fatf_rec16_2025_update path: %v", [input.fatf_rec16_2025_update.path])
}

deny contains msg if {
    input.fatf_rec16_2025_update
    not input.fatf_rec16_2025_update.deprecated == false
    msg := "[RULE-7] FATF R.16 2025 Update must not be deprecated (current standard)"
}

deny contains msg if {
    input.fatf_rec16_2025_update
    not input.fatf_rec16_2025_update.business_priority == "HIGH"
    msg := sprintf("[RULE-7] FATF R.16 2025 Update must have HIGH priority, got: %v", [input.fatf_rec16_2025_update.business_priority])
}

# Aggregated validation result
fatf_rules_valid if {
    input.ivms101_2023
    input.ivms101_2023.name == "IVMS101-2023 Datenmodell & Mapping-Templates"
    input.ivms101_2023.path == "23_compliance/global/fatf/travel_rule/ivms101_2023/"
    input.ivms101_2023.deprecated == false
    input.ivms101_2023.business_priority == "CRITICAL"
    input.fatf_rec16_2025_update
    input.fatf_rec16_2025_update.name == "R.16-Änderungen Juni 2025 Gap-Analyse"
    input.fatf_rec16_2025_update.path == "23_compliance/global/fatf/travel_rule/fatf_rec16_2025_update/"
    input.fatf_rec16_2025_update.deprecated == false
    input.fatf_rec16_2025_update.business_priority == "HIGH"
}
