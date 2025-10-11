# SSID Module Compliance Policy: 05_documentation
# Generated: 2025-10-07T11:40:52.063549

package ssid.modules.05_documentation

import future.keywords.if

# Controls affecting this module
module_controls := {
    "UNI-GV-002": {
        "category": "CC-04",
        "description": "Records management and documentation",
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