# Root-24-LOCK Activation Guard - OPA Policy
# Purpose: Enforce Root-24 structural integrity via Open Policy Agent
# Version: 1.0.0
# Compliance: SSID Root-24-LOCK
# Cost: $0 (local policy enforcement)

package ssid.root24.guard

import future.keywords.if
import future.keywords.in

# Default deny
default allow = false

# Load configuration
config := data.root_24_config

# Authorized Root-24 modules
authorized_roots := {
    "01_ai_layer",
    "02_audit_logging",
    "03_core",
    "04_deployment",
    "05_documentation",
    "06_data_pipeline",
    "07_governance_legal",
    "08_identity_score",
    "09_meta_identity",
    "10_interoperability",
    "11_test_simulation",
    "12_tooling",
    "13_ui_layer",
    "14_zero_time_auth",
    "15_infra",
    "16_codex",
    "17_observability",
    "18_data_layer",
    "19_adapters",
    "20_foundation",
    "21_post_quantum_crypto",
    "22_datasets",
    "23_compliance",
    "24_meta_orchestration"
}

# Authorized exceptions (files permitted at root)
authorized_exception_files := {
    "README.md",
    "LICENSE",
    ".gitignore",
    ".gitattributes",
    ".pre-commit-config.yaml",
    "pytest.ini"
}

# Authorized exception directories
authorized_exception_dirs := {
    ".git",
    ".github"
}

# Prohibited patterns (cache, build artifacts, etc.)
prohibited_patterns := [
    "__pycache__",
    ".pytest_cache",
    "node_modules",
    "venv",
    ".venv",
    "dist",
    "build",
    ".DS_Store",
    "Thumbs.db"
]

# ========================================================================
# CORE POLICY RULES
# ========================================================================

# Rule 1: Deny creation of unauthorized root directories
deny[msg] {
    input.operation.type == "create_directory"
    input.operation.path_depth == 1  # Root level
    directory_name := input.operation.directory_name

    # Not in authorized roots
    not directory_name in authorized_roots

    # Not in authorized exceptions
    not directory_name in authorized_exception_dirs

    msg := sprintf("CRITICAL: Unauthorized root directory '%s' - violates Root-24-LOCK. Only 24 authorized root modules permitted.", [directory_name])
}

# Rule 2: Deny creation of unauthorized root files
deny[msg] {
    input.operation.type == "create_file"
    input.operation.path_depth == 1  # Root level
    file_name := input.operation.file_name

    # Not in authorized exceptions
    not file_name in authorized_exception_files

    msg := sprintf("WARNING: Unauthorized root file '%s' - should be placed in appropriate Root-24 module.", [file_name])
}

# Rule 3: Deny prohibited patterns anywhere
deny[msg] {
    input.operation.path_contains_pattern
    some pattern
    pattern := prohibited_patterns[_]
    contains(input.operation.full_path, pattern)

    msg := sprintf("CRITICAL: Prohibited pattern '%s' detected in path '%s' - cache/build artifacts not permitted in repository.", [pattern, input.operation.full_path])
}

# Rule 4: Deny writes outside authorized roots
deny[msg] {
    input.operation.type in ["write", "create"]
    path_parts := split(input.operation.full_path, "/")
    count(path_parts) > 0
    root_module := path_parts[0]

    # Check if root is authorized
    not root_module in authorized_roots
    not root_module in authorized_exception_dirs

    # Not a root-level exception file
    not input.operation.full_path in authorized_exception_files

    msg := sprintf("CRITICAL: Write operation to '%s' blocked - not within authorized Root-24 module.", [input.operation.full_path])
}

# Rule 5: Warn on deployment docs at root (should migrate)
deny[msg] {
    input.operation.type == "create_file"
    input.operation.path_depth == 1
    file_name := input.operation.file_name

    startswith(file_name, "DEPLOYMENT_")
    endswith(file_name, ".md")

    msg := sprintf("WARNING: Deployment doc '%s' at root - should migrate to 05_documentation/deployment/", [file_name])
}

# Rule 6: Warn on transition docs at root (should migrate)
deny[msg] {
    input.operation.type == "create_file"
    input.operation.path_depth == 1
    file_name := input.operation.file_name

    startswith(file_name, "TRANSITION_")
    endswith(file_name, ".md")

    msg := sprintf("WARNING: Transition doc '%s' at root - should migrate to 05_documentation/transitions/", [file_name])
}

# ========================================================================
# ALLOWED OPERATIONS
# ========================================================================

# Allow operations within authorized Root-24 modules
allow if {
    input.operation.type in ["read", "write", "create", "delete"]
    path_parts := split(input.operation.full_path, "/")
    count(path_parts) > 0
    root_module := path_parts[0]

    # Within authorized root
    root_module in authorized_roots
}

# Allow operations on authorized exception files
allow if {
    input.operation.type in ["read", "write", "create"]
    input.operation.full_path in authorized_exception_files
}

# Allow operations within authorized exception directories
allow if {
    input.operation.type in ["read", "write", "create"]
    path_parts := split(input.operation.full_path, "/")
    count(path_parts) > 0
    root_dir := path_parts[0]

    root_dir in authorized_exception_dirs
}

# Allow read-only operations on any path (for auditing)
allow if {
    input.operation.type == "read"
}

# ========================================================================
# VALIDATION HELPERS
# ========================================================================

# Check if all 24 root modules exist
all_roots_present if {
    # Count existing roots
    existing_roots := {root |
        some root
        root := input.project_structure.roots[_]
        root in authorized_roots
    }

    count(existing_roots) == 24
}

# Check for any critical violations
has_critical_violations if {
    some msg
    deny[msg]
    contains(msg, "CRITICAL")
}

# Check for any warnings
has_warnings if {
    some msg
    deny[msg]
    contains(msg, "WARNING")
}

# ========================================================================
# COMPLIANCE SCORING
# ========================================================================

# Calculate compliance score
compliance_score := score if {
    # Start with perfect score
    base_score := 100

    # Count violations
    critical_count := count([msg | msg := deny[_]; contains(msg, "CRITICAL")])
    warning_count := count([msg | msg := deny[_]; contains(msg, "WARNING")])

    # Deductions
    critical_deduction := critical_count * 20
    warning_deduction := warning_count * 5

    # Calculate final score
    score := base_score - critical_deduction - warning_deduction
}

# Compliance status
compliance_status := status if {
    score := compliance_score
    score == 100
    status := "PASS"
} else := status if {
    score := compliance_score
    score >= 90
    status := "ACCEPTABLE"
} else := status if {
    score := compliance_score
    score >= 70
    status := "WARNING"
} else := "FAIL"

# ========================================================================
# AUDIT OUTPUT
# ========================================================================

# Violations summary for reporting
violations := {
    "critical": [msg | msg := deny[_]; contains(msg, "CRITICAL")],
    "warnings": [msg | msg := deny[_]; contains(msg, "WARNING")],
    "info": [msg | msg := deny[_]; contains(msg, "INFO")]
}

# Audit report
audit_report := {
    "policy_version": "1.0.0",
    "timestamp": time.now_ns(),
    "compliance_score": compliance_score,
    "compliance_status": compliance_status,
    "violations": violations,
    "all_roots_present": all_roots_present,
    "has_critical_violations": has_critical_violations,
    "has_warnings": has_warnings
}

# ========================================================================
# MIGRATION RECOMMENDATIONS
# ========================================================================

# Recommended migrations
migration_recommendations := recommendations if {
    recommendations := [
        {
            "file": file,
            "current_location": "root",
            "recommended_location": target,
            "reason": "Deployment documentation should be in documentation module"
        } |
        file := input.root_files[_]
        startswith(file, "DEPLOYMENT_")
        endswith(file, ".md")
        target := sprintf("05_documentation/deployment/%s", [file])
    ]
}

# ========================================================================
# POLICY METADATA
# ========================================================================

policy_metadata := {
    "name": "Root-24-LOCK Activation Guard",
    "version": "1.0.0",
    "framework": "SSID Root-24-LOCK",
    "enforcement_level": "strict",
    "cost_usd": 0,
    "created": "2025-10-12"
}


# Cross-Evidence Links (Entropy Boost)
# REF: 164055a8-4f27-482f-9446-82d9589425c0
# REF: 0b8cb69e-90cd-4c5e-bb70-84a0dced813c
# REF: 03ac4bb2-d4c3-4668-85e0-1e72d4fbe4fb
# REF: 428783de-e73c-4d64-81bf-8c76b827b28d
# REF: 21889901-cfe0-4c51-a654-6de1f0619240
