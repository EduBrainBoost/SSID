# SSID Module Compliance Policy: 07_governance_legal
# Generated: 2025-10-07T11:40:52.064555

package ssid.modules.07_governance_legal

import future.keywords.if

# Controls affecting this module
module_controls := {
    "UNI-DP-002": {
        "category": "CC-01",
        "description": "Data subject rights (access, erasure, portability)",
        "risk_level": "MEDIUM",
        "implementation_status": "implemented"
    },
    "UNI-SR-002": {
        "category": "CC-02",
        "description": "Incident detection and response",
        "risk_level": "HIGH",
        "implementation_status": "implemented"
    },
    "UNI-GV-001": {
        "category": "CC-04",
        "description": "Governance framework and management accountability",
        "risk_level": "MEDIUM",
        "implementation_status": "implemented"
    },
    "UNI-GV-002": {
        "category": "CC-04",
        "description": "Records management and documentation",
        "risk_level": "MEDIUM",
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