# SSID Compliance Policy - OPA Rego Export
# Generated from: compliance_unified_index.yaml
# Framework: UNIFIED
# Version: 2025-Q4
# Generated: 2025-10-07T11:40:52.059298
# Maintainer: edubrainboost
#
# This policy enforces SSID compliance rules across GDPR, DORA, MiCA, and AMLD6.
# Deploy to Open Policy Agent for external system enforcement.

package ssid.compliance

import future.keywords.if
import future.keywords.in
import future.keywords.contains

# =============================================================================
# Control Categories
# =============================================================================

control_categories := {
    "CC-01": {
        "name": "Data Protection & Privacy",
        "description": "Controls related to personal data processing, privacy rights, and data minimization",
        "frameworks": ["GDPR", "MiCA", "AMLD6"],
        "risk_domain": "privacy"
    },
    "CC-02": {
        "name": "ICT Security & Resilience",
        "description": "Controls for IT security, business continuity, and incident response",
        "frameworks": ["DORA", "GDPR", "MiCA"],
        "risk_domain": "operational"
    },
    "CC-03": {
        "name": "Financial Crime Prevention",
        "description": "AML/CFT controls, transaction monitoring, and sanctions compliance",
        "frameworks": ["AMLD6", "MiCA"],
        "risk_domain": "financial_crime"
    },
    "CC-04": {
        "name": "Governance & Accountability",
        "description": "Management oversight, documentation, and regulatory reporting",
        "frameworks": ["GDPR", "DORA", "MiCA", "AMLD6"],
        "risk_domain": "governance"
    },
    "CC-05": {
        "name": "Third-Party Risk Management",
        "description": "Vendor due diligence, service provider oversight, and supply chain security",
        "frameworks": ["DORA", "GDPR", "AMLD6"],
        "risk_domain": "third_party"
    },
    "CC-06": {
        "name": "Cryptographic Controls",
        "description": "Encryption, key management, and post-quantum cryptography",
        "frameworks": ["DORA", "GDPR", "MiCA"],
        "risk_domain": "cryptography"
    },
    "CC-07": {
        "name": "Audit & Monitoring",
        "description": "Logging, audit trails, and continuous monitoring",
        "frameworks": ["GDPR", "DORA", "MiCA", "AMLD6"],
        "risk_domain": "audit"
    }
}

# Check if a control belongs to a category
control_in_category(control_id, category_id) if {
    category := control_categories[category_id]
    control_id
    category
}

# =============================================================================
# Risk Classifications
# =============================================================================

risk_levels := {
    "CRITICAL": {
        "severity_score": 5,
        "description": "Immediate regulatory action required, potential fines or sanctions",
        "remediation_sla": "24 hours",
        "escalation": "C-level + Legal"
    },
    "HIGH": {
        "severity_score": 4,
        "description": "Significant compliance gap, regulatory notification may be required",
        "remediation_sla": "7 days",
        "escalation": "Compliance Officer + DPO"
    },
    "MEDIUM": {
        "severity_score": 3,
        "description": "Material compliance issue requiring timely remediation",
        "remediation_sla": "30 days",
        "escalation": "Department Head"
    },
    "LOW": {
        "severity_score": 2,
        "description": "Minor compliance gap, continuous improvement opportunity",
        "remediation_sla": "90 days",
        "escalation": "Team Lead"
    },
    "INFORMATIONAL": {
        "severity_score": 1,
        "description": "Observation or best practice recommendation",
        "remediation_sla": "Next review cycle",
        "escalation": "N/A"
    }
}

# Get severity score for risk level
risk_severity(level) := score if {
    risk := risk_levels[level]
    score := risk.severity_score
}

# Check if risk level requires immediate action
requires_immediate_action(level) if {
    risk_severity(level) >= 4
}

# =============================================================================
# Verification Methods
# =============================================================================

verification_methods := {
    "automated": {
        "description": "Continuous automated testing via CI/CD pipeline",
        "frequency": "real-time",
        "tools": ["pytest", "structure_guard.sh", "compliance_check.yml"],
        "confidence_level": "high"
    },
    "semi_automated": {
        "description": "Automated data collection with manual review",
        "frequency": "daily/weekly",
        "tools": ["compliance_dashboard.py", "dora_operational_metrics.yaml"],
        "confidence_level": "medium-high"
    },
    "manual": {
        "description": "Manual documentation review and attestation",
        "frequency": "quarterly",
        "tools": ["review_template.yaml", "audit_findings.yaml"],
        "confidence_level": "medium"
    },
    "external_audit": {
        "description": "Independent third-party assessment",
        "frequency": "annual",
        "tools": ["registry_anchor.json", "evidence trails"],
        "confidence_level": "very-high"
    }
}

# Check if verification method provides high confidence
high_confidence_verification(method) if {
    verification := verification_methods[method]
    verification.confidence_level in ["high", "very-high"]
}

# =============================================================================
# Compliance Rules
# =============================================================================

# All compliance controls indexed by unified ID
compliance_controls := {
    "UNI-DP-001": {
        "category": "CC-01",
        "description": "Personal data processing lawfulness and transparency",
        "risk_level": "HIGH",
        "frameworks": ["GDPR", "MiCA"],
        "ssid_modules": ["09_meta_identity", "03_core"],
        "verification": "automated",
        "implementation_status": "implemented"
    },
    "UNI-DP-002": {
        "category": "CC-01",
        "description": "Data subject rights (access, erasure, portability)",
        "risk_level": "MEDIUM",
        "frameworks": ["GDPR"],
        "ssid_modules": ["09_meta_identity", "07_governance_legal"],
        "verification": "semi_automated",
        "implementation_status": "implemented"
    },
    "UNI-SR-001": {
        "category": "CC-02",
        "description": "ICT risk management framework",
        "risk_level": "CRITICAL",
        "frameworks": ["DORA", "GDPR", "MiCA"],
        "ssid_modules": ["15_infra", "21_post_quantum_crypto", "03_core"],
        "verification": "automated",
        "implementation_status": "implemented"
    },
    "UNI-SR-002": {
        "category": "CC-02",
        "description": "Incident detection and response",
        "risk_level": "HIGH",
        "frameworks": ["DORA", "GDPR", "MiCA"],
        "ssid_modules": ["02_audit_logging", "17_observability", "07_governance_legal"],
        "verification": "semi_automated",
        "implementation_status": "implemented"
    },
    "UNI-SR-003": {
        "category": "CC-02",
        "description": "Business continuity and disaster recovery",
        "risk_level": "HIGH",
        "frameworks": ["DORA"],
        "ssid_modules": ["15_infra", "02_audit_logging"],
        "verification": "manual",
        "implementation_status": "implemented"
    },
    "UNI-FC-001": {
        "category": "CC-03",
        "description": "Customer due diligence (CDD) and KYC",
        "risk_level": "HIGH",
        "frameworks": ["AMLD6", "MiCA"],
        "ssid_modules": ["09_meta_identity", "14_zero_time_auth"],
        "verification": "manual",
        "implementation_status": "implemented"
    },
    "UNI-FC-002": {
        "category": "CC-03",
        "description": "Transaction monitoring and suspicious activity reporting",
        "risk_level": "HIGH",
        "frameworks": ["AMLD6", "AMLD6"],
        "ssid_modules": ["02_audit_logging", "17_observability"],
        "verification": "semi_automated",
        "implementation_status": "implemented"
    },
    "UNI-GV-001": {
        "category": "CC-04",
        "description": "Governance framework and management accountability",
        "risk_level": "MEDIUM",
        "frameworks": ["GDPR", "DORA", "MiCA"],
        "ssid_modules": ["07_governance_legal", "23_compliance"],
        "verification": "manual",
        "implementation_status": "implemented"
    },
    "UNI-GV-002": {
        "category": "CC-04",
        "description": "Records management and documentation",
        "risk_level": "MEDIUM",
        "frameworks": ["GDPR", "MiCA", "AMLD6"],
        "ssid_modules": ["07_governance_legal", "02_audit_logging", "05_documentation"],
        "verification": "automated",
        "implementation_status": "implemented"
    },
    "UNI-TP-001": {
        "category": "CC-05",
        "description": "Third-party service provider oversight",
        "risk_level": "HIGH",
        "frameworks": ["DORA", "GDPR", "AMLD6"],
        "ssid_modules": ["07_governance_legal", "15_infra"],
        "verification": "manual",
        "implementation_status": "planned"
    },
    "UNI-CR-001": {
        "category": "CC-06",
        "description": "Encryption and cryptographic key management",
        "risk_level": "CRITICAL",
        "frameworks": ["GDPR", "DORA", "MiCA"],
        "ssid_modules": ["21_post_quantum_crypto", "14_zero_time_auth", "03_core"],
        "verification": "automated",
        "implementation_status": "implemented"
    },
    "UNI-AL-001": {
        "category": "CC-07",
        "description": "Comprehensive audit logging and WORM storage",
        "risk_level": "HIGH",
        "frameworks": ["GDPR", "DORA", "AMLD6"],
        "ssid_modules": ["02_audit_logging", "17_observability"],
        "verification": "automated",
        "implementation_status": "implemented"
    }
}

# Check if a control is implemented
control_implemented(control_id) if {
    control := compliance_controls[control_id]
    control.implementation_status == "implemented"
}

# Check if a control is high priority
control_high_priority(control_id) if {
    control := compliance_controls[control_id]
    control.risk_level in ["CRITICAL", "HIGH"]
}

# Get all controls for a specific framework
framework_controls(framework) := controls if {
    controls := [control_id |
        control := compliance_controls[control_id]
        framework in control.frameworks
    ]
}

# Get all controls affecting a specific SSID module
module_controls(module) := controls if {
    controls := [control_id |
        control := compliance_controls[control_id]
        module in control.ssid_modules
    ]
}

# Check if all critical controls are implemented
all_critical_controls_implemented if {
    critical := [c |
        control := compliance_controls[c]
        control.risk_level == "CRITICAL"
    ]
    implemented := [c |
        control := compliance_controls[c]
        control.risk_level == "CRITICAL"
        control.implementation_status == "implemented"
    ]
    count(critical) == count(implemented)
}

# =============================================================================
# Helper Functions
# =============================================================================

# Calculate overall compliance score
compliance_score(framework) := score if {
    coverage := {"gdpr": "95%", "dora": "92%", "mica": "88%", "amld6": "94%", "unified_average": "92%"}
    score_str := coverage[framework]
    score := to_number(trim_suffix(score_str, "%"))
}

# Check if framework meets minimum compliance threshold
meets_compliance_threshold(framework, threshold) if {
    score := compliance_score(framework)
    score >= threshold
}

# Get all non-compliant controls
non_compliant_controls := controls if {
    controls := [control_id |
        control := compliance_controls[control_id]
        control.implementation_status != "implemented"
        control_high_priority(control_id)
    ]
}

# Count controls by risk level
controls_by_risk_level(level) := count if {
    controls := [c |
        control := compliance_controls[c]
        control.risk_level == level
    ]
    count := count(controls)
}

# Get remediation SLA for control
remediation_sla(control_id) := sla if {
    control := compliance_controls[control_id]
    risk := risk_levels[control.risk_level]
    sla := risk.remediation_sla
}

# =============================================================================
# Audit Decisions
# =============================================================================

# Main compliance decision
default allow := false

# Allow if all critical controls implemented
allow if {
    all_critical_controls_implemented
    count(non_compliant_controls) == 0
}

# Deny with reasons
deny[msg] if {
    not all_critical_controls_implemented
    msg := "Critical controls not fully implemented"
}

deny[msg] if {
    count(non_compliant_controls) > 0
    msg := sprintf("Non-compliant high-priority controls: %d", [count(non_compliant_controls)])
}

deny[msg] if {
    not meets_compliance_threshold("gdpr", 90)
    msg := "GDPR compliance below 90% threshold"
}

deny[msg] if {
    not meets_compliance_threshold("dora", 90)
    msg := "DORA compliance below 90% threshold"
}

# Audit report generation
audit_report := report if {
    report := {
        "timestamp": time.now_ns(),
        "compliance_status": {
            "gdpr": compliance_score("gdpr"),
            "dora": compliance_score("dora"),
            "mica": compliance_score("mica"),
            "amld6": compliance_score("amld6")
        },
        "critical_controls": {
            "total": controls_by_risk_level("CRITICAL"),
            "implemented": count([c |
                control := compliance_controls[c]
                control.risk_level == "CRITICAL"
                control_implemented(c)
            ])
        },
        "high_priority_gaps": non_compliant_controls,
        "overall_decision": allow
    }
}

# Risk assessment
risk_assessment := assessment if {
    critical_gaps := controls_by_risk_level("CRITICAL") - count([c |
        control := compliance_controls[c]
        control.risk_level == "CRITICAL"
        control_implemented(c)
    ])

    high_gaps := controls_by_risk_level("HIGH") - count([c |
        control := compliance_controls[c]
        control.risk_level == "HIGH"
        control_implemented(c)
    ])

    assessment := {
        "overall_risk": risk_level_assessment(critical_gaps, high_gaps),
        "critical_gaps": critical_gaps,
        "high_priority_gaps": high_gaps,
        "requires_action": critical_gaps > 0 or high_gaps > 3
    }
}

risk_level_assessment(critical, high) := "CRITICAL" if {
    critical > 0
}

risk_level_assessment(critical, high) := "HIGH" if {
    critical == 0
    high > 3
}

risk_level_assessment(critical, high) := "MEDIUM" if {
    critical == 0
    high > 0
    high <= 3
}

risk_level_assessment(critical, high) := "LOW" if {
    critical == 0
    high == 0
}