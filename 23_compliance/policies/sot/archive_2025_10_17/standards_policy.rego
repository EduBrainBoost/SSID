# Global Standards Policy (SoT Rules 10-12)
# ==========================================
# Lines 61-78 from SSID_structure_level3_part3_MAX.md
#
# Scientific Foundation: FSB, IOSCO, NIST AI standards
# Technical Manifestation: OPA policy enforcement

package ssid.sot.standards

import future.keywords.if

# SoT Rule 10: FSB Stablecoins 2023 Validation
deny contains msg if {
    input.fsb_stablecoins_2023
    not input.fsb_stablecoins_2023.name == "FSB Policy-Matrizen Marktmissbrauch/Transparenz"
    msg := sprintf("[RULE-10] Invalid fsb_stablecoins_2023 name: %v", [input.fsb_stablecoins_2023.name])
}

deny contains msg if {
    input.fsb_stablecoins_2023
    not input.fsb_stablecoins_2023.path == "23_compliance/global/standards/fsb_stablecoins_2023/"
    msg := sprintf("[RULE-10] Invalid fsb_stablecoins_2023 path: %v", [input.fsb_stablecoins_2023.path])
}

deny contains msg if {
    input.fsb_stablecoins_2023
    not input.fsb_stablecoins_2023.deprecated == false
    msg := "[RULE-10] FSB Stablecoins 2023 must not be deprecated"
}

deny contains msg if {
    input.fsb_stablecoins_2023
    not input.fsb_stablecoins_2023.business_priority == "HIGH"
    msg := sprintf("[RULE-10] FSB Stablecoins must have HIGH priority, got: %v", [input.fsb_stablecoins_2023.business_priority])
}

# SoT Rule 11: IOSCO Crypto Markets 2023 Validation
deny contains msg if {
    input.iosco_crypto_markets_2023
    not input.iosco_crypto_markets_2023.name == "IOSCO Policy-Matrizen"
    msg := sprintf("[RULE-11] Invalid iosco_crypto_markets_2023 name: %v", [input.iosco_crypto_markets_2023.name])
}

deny contains msg if {
    input.iosco_crypto_markets_2023
    not input.iosco_crypto_markets_2023.path == "23_compliance/global/standards/iosco_crypto_markets_2023/"
    msg := sprintf("[RULE-11] Invalid iosco_crypto_markets_2023 path: %v", [input.iosco_crypto_markets_2023.path])
}

deny contains msg if {
    input.iosco_crypto_markets_2023
    not input.iosco_crypto_markets_2023.deprecated == false
    msg := "[RULE-11] IOSCO Crypto Markets 2023 must not be deprecated"
}

deny contains msg if {
    input.iosco_crypto_markets_2023
    not input.iosco_crypto_markets_2023.business_priority == "MEDIUM"
    msg := sprintf("[RULE-11] IOSCO must have MEDIUM priority, got: %v", [input.iosco_crypto_markets_2023.business_priority])
}

# SoT Rule 12: NIST AI RMF 1.0 Validation
deny contains msg if {
    input.nist_ai_rmf_1_0
    not input.nist_ai_rmf_1_0.name == "Govern/Map/Measure/Manage Quick-Profiles"
    msg := sprintf("[RULE-12] Invalid nist_ai_rmf_1_0 name: %v", [input.nist_ai_rmf_1_0.name])
}

deny contains msg if {
    input.nist_ai_rmf_1_0
    not input.nist_ai_rmf_1_0.path == "23_compliance/global/standards/nist_ai_rmf_1_0/"
    msg := sprintf("[RULE-12] Invalid nist_ai_rmf_1_0 path: %v", [input.nist_ai_rmf_1_0.path])
}

deny contains msg if {
    input.nist_ai_rmf_1_0
    not input.nist_ai_rmf_1_0.deprecated == false
    msg := "[RULE-12] NIST AI RMF 1.0 must not be deprecated"
}

deny contains msg if {
    input.nist_ai_rmf_1_0
    not input.nist_ai_rmf_1_0.business_priority == "MEDIUM"
    msg := sprintf("[RULE-12] NIST AI RMF must have MEDIUM priority, got: %v", [input.nist_ai_rmf_1_0.business_priority])
}

# Aggregated validation result
standards_rules_valid if {
    input.fsb_stablecoins_2023
    input.fsb_stablecoins_2023.name == "FSB Policy-Matrizen Marktmissbrauch/Transparenz"
    input.fsb_stablecoins_2023.deprecated == false
    input.fsb_stablecoins_2023.business_priority == "HIGH"
    input.iosco_crypto_markets_2023
    input.iosco_crypto_markets_2023.name == "IOSCO Policy-Matrizen"
    input.iosco_crypto_markets_2023.deprecated == false
    input.iosco_crypto_markets_2023.business_priority == "MEDIUM"
    input.nist_ai_rmf_1_0
    input.nist_ai_rmf_1_0.name == "Govern/Map/Measure/Manage Quick-Profiles"
    input.nist_ai_rmf_1_0.deprecated == false
    input.nist_ai_rmf_1_0.business_priority == "MEDIUM"
}
