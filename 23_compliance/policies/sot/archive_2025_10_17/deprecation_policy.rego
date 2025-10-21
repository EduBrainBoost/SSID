# Deprecation Tracking Policy (SoT Rule 13)
# ===========================================
# Lines 80-87 from SSID_structure_level3_part3_MAX.md
#
# Scientific Foundation: Software lifecycle management, regulatory migration tracking
# Technical Manifestation: OPA policy enforcement

package ssid.sot.deprecation

import future.keywords.if
import future.keywords.in

# SoT Rule 13: Deprecated Standards Tracking Validation
required_fields := ["id", "status", "deprecated", "replaced_by", "deprecation_date", "migration_deadline", "notes"]

deny contains msg if {
    input.deprecated_standards
    some item in input.deprecated_standards
    some field in required_fields
    not object.get(item, field, null)
    msg := sprintf("[RULE-13] Deprecated item missing required field: %v", [field])
}

deny contains msg if {
    input.deprecated_standards
    some item in input.deprecated_standards
    not item.status == "deprecated"
    msg := sprintf("[RULE-13] Deprecated item status must be 'deprecated', got: %v", [item.status])
}

deny contains msg if {
    input.deprecated_standards
    some item in input.deprecated_standards
    not item.deprecated == true
    msg := sprintf("[RULE-13] Deprecated item 'deprecated' flag must be true for item: %v", [item.id])
}

deny contains msg if {
    input.deprecated_standards
    some item in input.deprecated_standards
    not regex.match(`^\d{4}-\d{2}-\d{2}$`, item.deprecation_date)
    msg := sprintf("[RULE-13] Invalid deprecation_date format for %v: %v. Must be YYYY-MM-DD", [item.id, item.deprecation_date])
}

deny contains msg if {
    input.deprecated_standards
    some item in input.deprecated_standards
    not regex.match(`^\d{4}-\d{2}-\d{2}$`, item.migration_deadline)
    msg := sprintf("[RULE-13] Invalid migration_deadline format for %v: %v. Must be YYYY-MM-DD", [item.id, item.migration_deadline])
}

deny contains msg if {
    input.deprecated_standards
    some item in input.deprecated_standards
    item.migration_deadline <= item.deprecation_date
    msg := sprintf("[RULE-13] Migration deadline (%v) must be after deprecation date (%v) for item: %v", [item.migration_deadline, item.deprecation_date, item.id])
}

deny contains msg if {
    input.deprecated_standards
    some item in input.deprecated_standards
    count(item.replaced_by) == 0
    msg := sprintf("[RULE-13] 'replaced_by' must be non-empty for item: %v", [item.id])
}

deny contains msg if {
    input.deprecated_standards
    some item in input.deprecated_standards
    count(item.notes) == 0
    msg := sprintf("[RULE-13] 'notes' must be non-empty for item: %v", [item.id])
}

# Aggregated validation result
deprecation_rules_valid if {
    input.deprecated_standards
    count(input.deprecated_standards) > 0
    # All items have required fields
    all_items_valid
}

all_items_valid if {
    every item in input.deprecated_standards {
        item.status == "deprecated"
        item.deprecated == true
        regex.match(`^\d{4}-\d{2}-\d{2}$`, item.deprecation_date)
        regex.match(`^\d{4}-\d{2}-\d{2}$`, item.migration_deadline)
        item.migration_deadline > item.deprecation_date
        count(item.replaced_by) > 0
        count(item.notes) > 0
    }
}
