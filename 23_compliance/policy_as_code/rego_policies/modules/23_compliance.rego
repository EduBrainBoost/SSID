# SSID Module Compliance Policy: 23_compliance
# Generated: 2025-10-07T11:40:52.067568

package ssid.modules.23_compliance

import future.keywords.if

# Controls affecting this module
module_controls := {
    "UNI-GV-001": {
        "category": "CC-04",
        "description": "Governance framework and management accountability",
        "risk_level": "MEDIUM",
        "implementation_status": "implemented"
    }
}

# Module compliance check
module_compliant if {
    implemented := [c |
        control := module_controls[c]
        control.implementation_status == "implemented"
    ]
    count(implemented) == count(module_controls)
}

# Critical gaps
critical_gaps := gaps if {
    gaps := [control_id |
        control := module_controls[control_id]
        control.risk_level == "CRITICAL"
        control.implementation_status != "implemented"
    ]
}

# Module risk level
module_risk := "CRITICAL" if {
    count(critical_gaps) > 0
}

module_risk := "OK" if {
    count(critical_gaps) == 0
}