# OECD CARF Policy (SoT Rule 8)
# ==============================
# Lines 47-52 from SSID_structure_level3_part3_MAX.md
#
# Scientific Foundation: OECD Common Reporting Framework for Crypto-Assets (CARF)
# Technical Manifestation: OPA policy enforcement

package ssid.sot.oecd

import future.keywords.if

# SoT Rule 8: OECD CARF XML Schema 2025-07 Validation
deny contains msg if {
    input.xml_schema_2025_07
    not input.xml_schema_2025_07.name == "User Guide + Feldprüfung, Testfälle"
    msg := sprintf("[RULE-8] Invalid xml_schema_2025_07 name: %v", [input.xml_schema_2025_07.name])
}

deny contains msg if {
    input.xml_schema_2025_07
    not input.xml_schema_2025_07.path == "23_compliance/global/oecd_carf/xml_schema_2025_07/"
    msg := sprintf("[RULE-8] Invalid xml_schema_2025_07 path: %v", [input.xml_schema_2025_07.path])
}

deny contains msg if {
    input.xml_schema_2025_07
    not input.xml_schema_2025_07.deprecated == false
    msg := "[RULE-8] OECD CARF XML Schema 2025-07 must not be deprecated (current standard)"
}

deny contains msg if {
    input.xml_schema_2025_07
    not input.xml_schema_2025_07.business_priority == "HIGH"
    msg := sprintf("[RULE-8] OECD CARF must have HIGH priority, got: %v", [input.xml_schema_2025_07.business_priority])
}

# Aggregated validation result
oecd_rules_valid if {
    input.xml_schema_2025_07
    input.xml_schema_2025_07.name == "User Guide + Feldprüfung, Testfälle"
    input.xml_schema_2025_07.path == "23_compliance/global/oecd_carf/xml_schema_2025_07/"
    input.xml_schema_2025_07.deprecated == false
    input.xml_schema_2025_07.business_priority == "HIGH"
}
