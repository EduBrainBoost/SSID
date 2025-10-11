# SSID Module Compliance Policy: 14_zero_time_auth
# Generated: 2025-10-07T11:40:52.065553

package ssid.modules.14_zero_time_auth

import future.keywords.if

# Controls affecting this module
module_controls := {
    "UNI-FC-001": {
        "category": "CC-03",
        "description": "Customer due diligence (CDD) and KYC",
        "risk_level": "HIGH",
        "implementation_status": "implemented"
    },
    "UNI-CR-001": {
        "category": "CC-06",
        "description": "Encryption and cryptographic key management",
        "risk_level": "CRITICAL",
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