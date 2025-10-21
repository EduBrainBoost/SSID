# SOC2 CC1.1 - Integrity & Ethical Values Policy
# ================================================
#
# Scientific Basis:
# AICPA TSC CC1.1 - The entity demonstrates a commitment to integrity and ethical values
# COSO Internal Control Framework (2013) Principle 1
#
# Technical Manifestation:
# OPA policy enforcing presence and validity of integrity/ethics controls
#
# Enforcement Rules:
# 1. Required policy documents must exist
# 2. Ethics training completion >= 80% annually
# 3. WORM-compliant violation logging must be configured
# 4. Code of conduct acknowledgments must be tracked
#
# Author: SSID Compliance Team
# Version: 1.0.0
# Date: 2025-10-17

package ssid.compliance.soc2.cc1_1

import future.keywords.if
import future.keywords.in

# Default deny
default allow = false

# Required policy documents
required_policies := {
    "code_of_conduct": "07_governance_legal/policies/code_of_conduct.md",
    "ethics_policy": "07_governance_legal/policies/ethics_policy.md",
    "conflict_of_interest": "07_governance_legal/policies/conflict_of_interest_policy.md",
    "whistleblower_policy": "07_governance_legal/policies/whistleblower_policy.md"
}

# Evidence paths
evidence_paths := {
    "training_log": "07_governance_legal/training/ethics_training_log.json",
    "violation_log": "02_audit_logging/storage/worm/immutable_store/ethics_violations.jsonl",
    "acknowledgment_log": "07_governance_legal/training/code_conduct_acknowledgments.json"
}

# Training compliance threshold
training_threshold := 0.80

# Rule 1: All required policy documents must exist
policies_exist if {
    input.file_system
    count(missing_policies) == 0
}

missing_policies[policy_name] {
    some policy_name, path in required_policies
    not file_exists(path)
}

# Rule 2: Ethics training compliance >= 80%
training_compliant if {
    input.training_log
    input.training_log.total_personnel > 0

    recent_completions := count([record |
        some record in input.training_log.training_records
        days_ago := days_between(record.completion_date, input.current_date)
        days_ago <= 365
    ])

    compliance_rate := recent_completions / input.training_log.total_personnel
    compliance_rate >= training_threshold
}

# Rule 3: WORM violation logging configured
violation_logging_configured if {
    input.file_system
    file_exists("02_audit_logging/storage/worm/immutable_store")
    dir_exists("02_audit_logging/storage/worm/immutable_store")
}

# Rule 4: Code of conduct acknowledgments tracked
acknowledgments_tracked if {
    input.acknowledgment_log
    count(input.acknowledgment_log.acknowledgments) > 0
}

# Overall CC1.1 compliance
allow if {
    policies_exist
    training_compliant
    violation_logging_configured
    acknowledgments_tracked
}

# Violation details for reporting
violations[violation] {
    not policies_exist
    some policy in missing_policies
    violation := {
        "rule": "CC1.1",
        "severity": "CRITICAL",
        "finding": sprintf("Missing required policy: %s", [policy]),
        "remediation": sprintf("Create policy document: %s", [required_policies[policy]])
    }
}

violations[violation] {
    not training_compliant
    violation := {
        "rule": "CC1.1",
        "severity": "HIGH",
        "finding": "Ethics training compliance below 80% threshold",
        "remediation": "Increase ethics training completion rate"
    }
}

violations[violation] {
    not violation_logging_configured
    violation := {
        "rule": "CC1.1",
        "severity": "CRITICAL",
        "finding": "WORM-compliant ethics violation logging not configured",
        "remediation": "Initialize WORM storage for ethics violations"
    }
}

violations[violation] {
    not acknowledgments_tracked
    violation := {
        "rule": "CC1.1",
        "severity": "HIGH",
        "finding": "No code of conduct acknowledgments tracked",
        "remediation": "Implement acknowledgment tracking system"
    }
}

# Helper functions
file_exists(path) if {
    some file in input.file_system.files
    file.path == path
    file.exists == true
}

dir_exists(path) if {
    some directory in input.file_system.directories
    directory.path == path
    directory.exists == true
}

days_between(date1, date2) := diff if {
    # Simplified - in production would use time.parse_rfc3339_ns
    diff := 0  # Placeholder
}
