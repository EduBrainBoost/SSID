# SSID Module Compliance Policy: 15_infra
# Generated: 2025-10-07T11:40:52.065553

package ssid.modules.15_infra

import future.keywords.if

# Controls affecting this module
module_controls := {
    "UNI-SR-001": {
        "category": "CC-02",
        "description": "ICT risk management framework",
        "risk_level": "CRITICAL",
        "implementation_status": "implemented"
    },
    "UNI-SR-003": {
        "category": "CC-02",
        "description": "Business continuity and disaster recovery",
        "risk_level": "HIGH",
        "implementation_status": "implemented"
    },
    "UNI-TP-001": {
        "category": "CC-05",
        "description": "Third-party service provider oversight",
        "risk_level": "HIGH",
        "implementation_status": "planned"
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