# Instance-Specific Properties Policy
# SOT-022 through SOT-058

package ssid.sot.instance_properties

import rego.v1

# Helper: Valid business priorities
valid_priorities := {"CRITICAL", "HIGH", "MEDIUM", "LOW"}

# ivms101_2023 (SOT-022 through SOT-025)
deny contains msg if {
    not input.ivms101_2023.name
    msg := "[SOT-022] Missing 'name' in ivms101_2023"
}

deny contains msg if {
    not input.ivms101_2023.path
    msg := "[SOT-023] Missing 'path' in ivms101_2023"
}

deny contains msg if {
    not is_boolean(input.ivms101_2023.deprecated)
    msg := "[SOT-024] Missing or invalid 'deprecated' in ivms101_2023"
}

deny contains msg if {
    not input.ivms101_2023.business_priority
    msg := "[SOT-025] Missing 'business_priority' in ivms101_2023"
}

deny contains msg if {
    input.ivms101_2023.business_priority
    not valid_priorities[input.ivms101_2023.business_priority]
    msg := sprintf("[SOT-025] Invalid business_priority in ivms101_2023: '%v'", [input.ivms101_2023.business_priority])
}

# fatf_rec16_2025_update (SOT-027 through SOT-030)
deny contains msg if {
    not input.fatf_rec16_2025_update.name
    msg := "[SOT-027] Missing 'name' in fatf_rec16_2025_update"
}

deny contains msg if {
    not input.fatf_rec16_2025_update.path
    msg := "[SOT-028] Missing 'path' in fatf_rec16_2025_update"
}

deny contains msg if {
    not is_boolean(input.fatf_rec16_2025_update.deprecated)
    msg := "[SOT-029] Missing or invalid 'deprecated' in fatf_rec16_2025_update"
}

deny contains msg if {
    not input.fatf_rec16_2025_update.business_priority
    msg := "[SOT-030] Missing 'business_priority' in fatf_rec16_2025_update"
}

deny contains msg if {
    input.fatf_rec16_2025_update.business_priority
    not valid_priorities[input.fatf_rec16_2025_update.business_priority]
    msg := sprintf("[SOT-030] Invalid business_priority in fatf_rec16_2025_update: '%v'", [input.fatf_rec16_2025_update.business_priority])
}

# xml_schema_2025_07 (SOT-033 through SOT-036)
deny contains msg if {
    not input.xml_schema_2025_07.name
    msg := "[SOT-033] Missing 'name' in xml_schema_2025_07"
}

deny contains msg if {
    not input.xml_schema_2025_07.path
    msg := "[SOT-034] Missing 'path' in xml_schema_2025_07"
}

deny contains msg if {
    not is_boolean(input.xml_schema_2025_07.deprecated)
    msg := "[SOT-035] Missing or invalid 'deprecated' in xml_schema_2025_07"
}

deny contains msg if {
    not input.xml_schema_2025_07.business_priority
    msg := "[SOT-036] Missing 'business_priority' in xml_schema_2025_07"
}

deny contains msg if {
    input.xml_schema_2025_07.business_priority
    not valid_priorities[input.xml_schema_2025_07.business_priority]
    msg := sprintf("[SOT-036] Invalid business_priority in xml_schema_2025_07: '%v'", [input.xml_schema_2025_07.business_priority])
}

# iso24165_dti (SOT-039 through SOT-042)
deny contains msg if {
    not input.iso24165_dti.name
    msg := "[SOT-039] Missing 'name' in iso24165_dti"
}

deny contains msg if {
    not input.iso24165_dti.path
    msg := "[SOT-040] Missing 'path' in iso24165_dti"
}

deny contains msg if {
    not is_boolean(input.iso24165_dti.deprecated)
    msg := "[SOT-041] Missing or invalid 'deprecated' in iso24165_dti"
}

deny contains msg if {
    not input.iso24165_dti.business_priority
    msg := "[SOT-042] Missing 'business_priority' in iso24165_dti"
}

deny contains msg if {
    input.iso24165_dti.business_priority
    not valid_priorities[input.iso24165_dti.business_priority]
    msg := sprintf("[SOT-042] Invalid business_priority in iso24165_dti: '%v'", [input.iso24165_dti.business_priority])
}

# fsb_stablecoins_2023 (SOT-045 through SOT-048)
deny contains msg if {
    not input.fsb_stablecoins_2023.name
    msg := "[SOT-045] Missing 'name' in fsb_stablecoins_2023"
}

deny contains msg if {
    not input.fsb_stablecoins_2023.path
    msg := "[SOT-046] Missing 'path' in fsb_stablecoins_2023"
}

deny contains msg if {
    not is_boolean(input.fsb_stablecoins_2023.deprecated)
    msg := "[SOT-047] Missing or invalid 'deprecated' in fsb_stablecoins_2023"
}

deny contains msg if {
    not input.fsb_stablecoins_2023.business_priority
    msg := "[SOT-048] Missing 'business_priority' in fsb_stablecoins_2023"
}

deny contains msg if {
    input.fsb_stablecoins_2023.business_priority
    not valid_priorities[input.fsb_stablecoins_2023.business_priority]
    msg := sprintf("[SOT-048] Invalid business_priority in fsb_stablecoins_2023: '%v'", [input.fsb_stablecoins_2023.business_priority])
}

# iosco_crypto_markets_2023 (SOT-050 through SOT-053)
deny contains msg if {
    not input.iosco_crypto_markets_2023.name
    msg := "[SOT-050] Missing 'name' in iosco_crypto_markets_2023"
}

deny contains msg if {
    not input.iosco_crypto_markets_2023.path
    msg := "[SOT-051] Missing 'path' in iosco_crypto_markets_2023"
}

deny contains msg if {
    not is_boolean(input.iosco_crypto_markets_2023.deprecated)
    msg := "[SOT-052] Missing or invalid 'deprecated' in iosco_crypto_markets_2023"
}

deny contains msg if {
    not input.iosco_crypto_markets_2023.business_priority
    msg := "[SOT-053] Missing 'business_priority' in iosco_crypto_markets_2023"
}

deny contains msg if {
    input.iosco_crypto_markets_2023.business_priority
    not valid_priorities[input.iosco_crypto_markets_2023.business_priority]
    msg := sprintf("[SOT-053] Invalid business_priority in iosco_crypto_markets_2023: '%v'", [input.iosco_crypto_markets_2023.business_priority])
}

# nist_ai_rmf_1_0 (SOT-055 through SOT-058)
deny contains msg if {
    not input.nist_ai_rmf_1_0.name
    msg := "[SOT-055] Missing 'name' in nist_ai_rmf_1_0"
}

deny contains msg if {
    not input.nist_ai_rmf_1_0.path
    msg := "[SOT-056] Missing 'path' in nist_ai_rmf_1_0"
}

deny contains msg if {
    not is_boolean(input.nist_ai_rmf_1_0.deprecated)
    msg := "[SOT-057] Missing or invalid 'deprecated' in nist_ai_rmf_1_0"
}

deny contains msg if {
    not input.nist_ai_rmf_1_0.business_priority
    msg := "[SOT-058] Missing 'business_priority' in nist_ai_rmf_1_0"
}

deny contains msg if {
    input.nist_ai_rmf_1_0.business_priority
    not valid_priorities[input.nist_ai_rmf_1_0.business_priority]
    msg := sprintf("[SOT-058] Invalid business_priority in nist_ai_rmf_1_0: '%v'", [input.nist_ai_rmf_1_0.business_priority])
}
