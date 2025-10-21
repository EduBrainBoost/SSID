# Deprecated List Policy
# SOT-059 through SOT-066

package ssid.sot.deprecated_list

import rego.v1

# SOT-059: deprecated_standards marker
deny contains msg if {
    not input.deprecated_standards_marker
    msg := "[SOT-059] Missing 'deprecated_standards_marker' field"
}

deny contains msg if {
    input.deprecated_standards_marker
    input.deprecated_standards_marker != "deprecated_standards:"
    msg := sprintf("[SOT-059] Invalid marker: '%v' (expected 'deprecated_standards:')", [input.deprecated_standards_marker])
}

# SOT-060 through SOT-066: Validate each entry in deprecated list
deny contains msg if {
    input.entries
    some entry in input.entries
    not entry.id
    msg := "[SOT-060] Missing 'id' in deprecated list entry"
}

deny contains msg if {
    input.entries
    some entry in input.entries
    entry.id
    count(entry.id) < 5
    msg := sprintf("[SOT-060] ID too short in deprecated list: '%v'", [entry.id])
}

deny contains msg if {
    input.entries
    some entry in input.entries
    not entry.status
    msg := "[SOT-061] Missing 'status' in deprecated list entry"
}

deny contains msg if {
    input.entries
    some entry in input.entries
    entry.status
    not entry.status in ["deprecated", "superseded", "obsolete", "retired"]
    msg := sprintf("[SOT-061] Invalid status: '%v'", [entry.status])
}

deny contains msg if {
    input.entries
    some entry in input.entries
    not is_boolean(entry.deprecated)
    msg := "[SOT-062] Missing or invalid 'deprecated' boolean in deprecated list entry"
}

deny contains msg if {
    input.entries
    some entry in input.entries
    is_boolean(entry.deprecated)
    entry.deprecated != true
    msg := "[SOT-062] 'deprecated' must be true in deprecated list"
}

deny contains msg if {
    input.entries
    some entry in input.entries
    not entry.replaced_by
    msg := "[SOT-063] Missing 'replaced_by' in deprecated list entry"
}

deny contains msg if {
    input.entries
    some entry in input.entries
    entry.replaced_by
    count(entry.replaced_by) < 5
    msg := sprintf("[SOT-063] 'replaced_by' too short: '%v'", [entry.replaced_by])
}

deny contains msg if {
    input.entries
    some entry in input.entries
    not entry.deprecation_date
    msg := "[SOT-064] Missing 'deprecation_date' in deprecated list entry"
}

deny contains msg if {
    input.entries
    some entry in input.entries
    not entry.migration_deadline
    msg := "[SOT-065] Missing 'migration_deadline' in deprecated list entry"
}

deny contains msg if {
    input.entries
    some entry in input.entries
    not entry.notes
    msg := "[SOT-066] Missing 'notes' in deprecated list entry"
}

deny contains msg if {
    input.entries
    some entry in input.entries
    entry.notes
    count(entry.notes) < 10
    msg := sprintf("[SOT-066] Notes too short: '%v'", [entry.notes])
}
