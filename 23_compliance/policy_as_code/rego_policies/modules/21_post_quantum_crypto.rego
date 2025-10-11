# SSID Module Compliance Policy: 21_post_quantum_crypto
# Generated: 2025-10-07T11:40:52.066564

package ssid.modules.21_post_quantum_crypto

import future.keywords.if

# Controls affecting this module
module_controls := {
    "UNI-SR-001": {
        "category": "CC-02",
        "description": "ICT risk management framework",
        "risk_level": "CRITICAL",
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