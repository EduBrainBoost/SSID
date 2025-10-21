# ISO Standards Policy (SoT Rule 9)
# ==================================
# Lines 54-59 from SSID_structure_level3_part3_MAX.md
#
# Scientific Foundation: ISO 24165-2:2025 Digital Token Identifier
# Technical Manifestation: OPA policy enforcement

package ssid.sot.iso

import future.keywords.if

# SoT Rule 9: ISO 24165 DTI Validation
deny contains msg if {
    input.iso24165_dti
    not input.iso24165_dti.name == "ISO 24165-2:2025 Registry-Flows, DTIF-RA-Hinweise"
    msg := sprintf("[RULE-9] Invalid iso24165_dti name: %v", [input.iso24165_dti.name])
}

deny contains msg if {
    input.iso24165_dti
    not input.iso24165_dti.path == "23_compliance/global/iso/iso24165_dti/"
    msg := sprintf("[RULE-9] Invalid iso24165_dti path: %v", [input.iso24165_dti.path])
}

deny contains msg if {
    input.iso24165_dti
    not input.iso24165_dti.deprecated == false
    msg := "[RULE-9] ISO 24165 DTI must not be deprecated (current standard)"
}

deny contains msg if {
    input.iso24165_dti
    not input.iso24165_dti.business_priority == "MEDIUM"
    msg := sprintf("[RULE-9] ISO 24165 DTI must have MEDIUM priority, got: %v", [input.iso24165_dti.business_priority])
}

# Aggregated validation result
iso_rules_valid if {
    input.iso24165_dti
    input.iso24165_dti.name == "ISO 24165-2:2025 Registry-Flows, DTIF-RA-Hinweise"
    input.iso24165_dti.path == "23_compliance/global/iso/iso24165_dti/"
    input.iso24165_dti.deprecated == false
    input.iso24165_dti.business_priority == "MEDIUM"
}
