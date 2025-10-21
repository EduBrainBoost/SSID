# Global Foundations Policy (SoT Rules 1-5)
# ==========================================
# Lines 26-32 from SSID_structure_level3_part3_MAX.md
#
# Scientific Foundation: ISO 8601, Semantic Versioning 2.0.0
# Technical Manifestation: OPA policy enforcement

package ssid.sot.global_foundations

import future.keywords.if
import future.keywords.in

# SoT Rule 1: Version Format Validation
deny contains msg if {
    not input.version
    msg := "[RULE-1] Missing required field: version"
}

deny contains msg if {
    input.version
    not regex.match(`^\d+\.\d+(\.\d+)?$`, input.version)
    msg := sprintf("[RULE-1] Invalid version format: %v. Must be MAJOR.MINOR or MAJOR.MINOR.PATCH", [input.version])
}

# SoT Rule 2: Date Format Validation (ISO 8601)
deny contains msg if {
    not input.date
    msg := "[RULE-2] Missing required field: date"
}

deny contains msg if {
    input.date
    not regex.match(`^\d{4}-\d{2}-\d{2}$`, input.date)
    msg := sprintf("[RULE-2] Invalid date format: %v. Must be YYYY-MM-DD (ISO 8601)", [input.date])
}

# SoT Rule 3: Deprecated Flag Validation
deny contains msg if {
    not input.deprecated == true
    not input.deprecated == false
    msg := "[RULE-3] Missing or invalid deprecated flag. Must be boolean (true/false)"
}

# SoT Rule 4: Regulatory Basis Validation
deny contains msg if {
    not input.regulatory_basis
    msg := "[RULE-4] Missing required field: regulatory_basis"
}

deny contains msg if {
    input.regulatory_basis
    count(input.regulatory_basis) < 10
    msg := sprintf("[RULE-4] Regulatory basis too short: %v chars. Minimum 10 chars required", [count(input.regulatory_basis)])
}

valid_regulatory_terms := ["FATF", "OECD", "ISO", "NIST", "MiCA", "DORA", "GDPR", "AML", "KYC"]

deny contains msg if {
    input.regulatory_basis
    count([term | term := valid_regulatory_terms[_]; contains(input.regulatory_basis, term)]) == 0
    msg := sprintf("[RULE-4] Regulatory basis should reference known standards: %v", [concat(", ", valid_regulatory_terms)])
}

# SoT Rule 5: Classification Validation
valid_classifications := [
    "PUBLIC",
    "INTERNAL",
    "CONFIDENTIAL",
    "CONFIDENTIAL - Internal Compliance Matrix",
    "RESTRICTED",
    "SECRET"
]

deny contains msg if {
    not input.classification
    msg := "[RULE-5] Missing required field: classification"
}

deny contains msg if {
    input.classification
    not input.classification in valid_classifications
    msg := sprintf("[RULE-5] Invalid classification: %v. Must be one of: %v", [input.classification, concat(", ", valid_classifications)])
}

# Aggregated validation result
global_foundations_valid if {
    input.version
    regex.match(`^\d+\.\d+(\.\d+)?$`, input.version)
    input.date
    regex.match(`^\d{4}-\d{2}-\d{2}$`, input.date)
    # Check deprecated is boolean (either true or false)
    is_boolean(input.deprecated)
    input.regulatory_basis
    count(input.regulatory_basis) >= 10
    input.classification
    input.classification in valid_classifications
}
