package intent.evolution

import future.keywords.contains
import future.keywords.if
import future.keywords.in

# Intent Evolution Policy v3.0
# =============================
# Governs automatic intent evolution, versioning, and validation

default allow := false
default deny := true

# Computed sets
new_intents := {change |
    change := input.changes[_]
    change.change_type == "added"
}

modified_intents := {change |
    change := input.changes[_]
    change.change_type == "modified"
}

deprecated_intents := {change |
    change := input.changes[_]
    change.change_type == "removed"
}

breaking_changes := {change |
    change := input.changes[_]
    change.metadata.breaking == true
}

# Allow automatic evolution if all conditions met
allow if {
    # No breaking changes without approval
    count(breaking_changes) == 0

    # All changes have valid versions
    all_changes_versioned

    # No conflicts detected
    no_conflicts

    # Audit trail is complete
    audit_complete
}

# Deny rules with descriptive messages
deny[msg] if {
    count(breaking_changes) > 0
    not input.approval.breaking_changes_approved
    msg := sprintf("FAIL: %d breaking changes require manual approval", [count(breaking_changes)])
}

deny[msg] if {
    not all_changes_versioned
    msg := "FAIL: Not all changes have valid semantic versions"
}

deny[msg] if {
    not no_conflicts
    msg := "FAIL: Conflicts detected in intent evolution"
}

deny[msg] if {
    not audit_complete
    msg := "FAIL: Audit trail incomplete - missing required metadata"
}

deny[msg] if {
    input.changes == []
    msg := "FAIL: No changes detected - evolution guard not running"
}

# Helper rules
all_changes_versioned if {
    every change in input.changes {
        change.version != ""
        valid_semver(change.version)
    }
}

valid_semver(version) if {
    # Check format: X.Y.Z
    parts := split(version, ".")
    count(parts) == 3
    to_number(parts[0]) >= 0
    to_number(parts[1]) >= 0
    to_number(parts[2]) >= 0
}

no_conflicts if {
    # Check for duplicate intent IDs
    intent_ids := {change.intent_id | change := input.changes[_]}
    count(intent_ids) == count(input.changes)

    # Check for path conflicts
    paths := {change.artifact_path | change := input.changes[_]}
    count(paths) == count(input.changes)
}

audit_complete if {
    every change in input.changes {
        change.timestamp != ""
        change.hash != ""
        change.category != ""
    }
}

# Evolution statistics
evolution_stats := {
    "total_changes": count(input.changes),
    "new_intents": count(new_intents),
    "modified_intents": count(modified_intents),
    "deprecated_intents": count(deprecated_intents),
    "breaking_changes": count(breaking_changes),
    "version_increments": version_increments
}

version_increments := {increment: count |
    increment := ["major", "minor", "patch"][_]
    count := count_version_type(increment)
}

count_version_type(increment) := count if {
    changes_of_type := {change |
        change := input.changes[_]
        change.version_increment == increment
    }
    count := count(changes_of_type)
}

# Category distribution
category_distribution := {category: count |
    category := ["policy", "report", "tool", "test", "workflow", "registry", "bridge", "guard"][_]
    category_changes := {c |
        c := input.changes[_]
        c.category == category
    }
    count := count(category_changes)
}

# Layer coverage
layer_coverage := {layer: count |
    layer := input.changes[_].layer
    layer != null
    layer_changes := {c |
        c := input.changes[_]
        c.layer == layer
    }
    count := count(layer_changes)
}

# Risk assessment
risk_level := level if {
    score := risk_score
    score < 30 := level := "LOW"
    score >= 30 and score < 70 := level := "MEDIUM"
    score >= 70 := level := "HIGH"
}

risk_score := score if {
    breaking_score := count(breaking_changes) * 50
    new_score := count(new_intents) * 5
    modified_score := count(modified_intents) * 10
    deprecated_score := count(deprecated_intents) * 20

    score := breaking_score + new_score + modified_score + deprecated_score
}

# Rollback policy
allow_rollback if {
    input.rollback_request.target_version != ""
    input.rollback_request.reason != ""
    input.rollback_request.approved_by != ""

    # Can only rollback to previous version
    valid_rollback_target(input.rollback_request.target_version)
}

valid_rollback_target(target) if {
    # Simplified - check that target exists in history
    target != ""
}

# Policy metadata
policy_info := {
    "name": "Intent Evolution Policy",
    "version": "3.0.0",
    "description": "Governs automatic intent evolution, versioning, and validation",
    "enforcement": "ADAPTIVE",
    "integration": "intent_evolution_guard.py",
    "capabilities": [
        "automatic_discovery",
        "semantic_versioning",
        "conflict_detection",
        "audit_integration",
        "rollback_support"
    ],
    "epistemic_certainty": 1.0
}
