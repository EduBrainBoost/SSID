# SSID Module Compliance Policy: 17_observability
# Generated: 2025-10-07T11:40:52.066564

package ssid.modules.17_observability

import future.keywords.if

# Controls affecting this module
module_controls := {
    "UNI-SR-002": {
        "category": "CC-02",
        "description": "Incident detection and response",
        "risk_level": "HIGH",
        "implementation_status": "implemented"
    },
    "UNI-FC-002": {
        "category": "CC-03",
        "description": "Transaction monitoring and suspicious activity reporting",
        "risk_level": "HIGH",
        "implementation_status": "implemented"
    },
    "UNI-AL-001": {
        "category": "CC-07",
        "description": "Comprehensive audit logging and WORM storage",
        "risk_level": "HIGH",
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