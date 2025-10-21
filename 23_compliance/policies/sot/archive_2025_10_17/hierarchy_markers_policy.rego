# Hierarchy Markers Policy
# SOT-020, SOT-031, SOT-037, SOT-043

package ssid.sot.hierarchy_markers

import rego.v1

# SOT-020: FATF Travel Rule Hierarchy
deny contains msg if {
    not input.hierarchy_marker_fatf
    msg := "[SOT-020] Missing 'hierarchy_marker_fatf' field"
}

deny contains msg if {
    input.hierarchy_marker_fatf
    input.hierarchy_marker_fatf != "fatf/travel_rule/"
    msg := sprintf("[SOT-020] Invalid hierarchy marker: '%v' (expected 'fatf/travel_rule/')", [input.hierarchy_marker_fatf])
}

# SOT-031: OECD CARF Hierarchy
deny contains msg if {
    not input.hierarchy_marker_oecd
    msg := "[SOT-031] Missing 'hierarchy_marker_oecd' field"
}

deny contains msg if {
    input.hierarchy_marker_oecd
    input.hierarchy_marker_oecd != "oecd_carf/"
    msg := sprintf("[SOT-031] Invalid hierarchy marker: '%v' (expected 'oecd_carf/')", [input.hierarchy_marker_oecd])
}

# SOT-037: ISO Hierarchy
deny contains msg if {
    not input.hierarchy_marker_iso
    msg := "[SOT-037] Missing 'hierarchy_marker_iso' field"
}

deny contains msg if {
    input.hierarchy_marker_iso
    input.hierarchy_marker_iso != "iso/"
    msg := sprintf("[SOT-037] Invalid hierarchy marker: '%v' (expected 'iso/')", [input.hierarchy_marker_iso])
}

# SOT-043: Standards Hierarchy
deny contains msg if {
    not input.hierarchy_marker_standards
    msg := "[SOT-043] Missing 'hierarchy_marker_standards' field"
}

deny contains msg if {
    input.hierarchy_marker_standards
    input.hierarchy_marker_standards != "standards/"
    msg := sprintf("[SOT-043] Invalid hierarchy marker: '%v' (expected 'standards/')", [input.hierarchy_marker_standards])
}
