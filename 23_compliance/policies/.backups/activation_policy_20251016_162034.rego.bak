# SSID Root-24-LOCK Activation Policy
# Purpose: Prevent file creation outside authorized Root-24 modules
# Version: 2.0.0 (Forensic Edition)
# Mode: ENFORCEMENT
# Cost: $0 (local policy evaluation)

package ssid.root24.activation

import future.keywords.if
import future.keywords.in

# ========================================================================
# CONFIGURATION
# ========================================================================

# Official Root-24 modules (IMMUTABLE)
authorized_root_modules := {
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

# Authorized root-level files (exceptions)
authorized_root_files := {
    "README.md",
    "LICENSE",
    ".gitignore",
    ".gitattributes",
    ".pre-commit-config.yaml",
    "pytest.ini"
}

# Authorized root-level directories (exceptions)
authorized_root_dirs := {
    ".git",
    ".github"  # GitHub workflows and config
}

# Prohibited patterns (never allowed)
prohibited_patterns := [
    ".claude",
    "__pycache__",
    ".pytest_cache",
    "node_modules",
    "venv",
    ".venv",
    "dist",
    "build",
    ".DS_Store",
    "Thumbs.db",
    "desktop.ini"
}

# Migration mappings (wrong location → correct location)
migration_mappings := {
    "DEPLOYMENT_v5.2.md": "05_documentation/deployment/DEPLOYMENT_v5.2.md",
    "DEPLOYMENT_v5.4_Federation.md": "05_documentation/deployment/DEPLOYMENT_v5.4_Federation.md",
    "DEPLOYMENT_v6.0_Planetary_Continuum.md": "05_documentation/deployment/DEPLOYMENT_v6.0_Planetary_Continuum.md",
    "DEPLOYMENT_v8.0_Continuum_Ignition.md": "05_documentation/deployment/DEPLOYMENT_v8.0_Continuum_Ignition.md",
    "TRANSITION_v6_to_v7_DORMANT.md": "05_documentation/transitions/TRANSITION_v6_to_v7_DORMANT.md",
    "ROOT_24_LOCK_COMPLIANCE_SUMMARY.md": "05_documentation/compliance/ROOT_24_LOCK_COMPLIANCE_SUMMARY.md"
}

# ========================================================================
# CORE POLICY RULES
# ========================================================================

# Default: deny all operations not explicitly allowed
default allow := false
default enforce_root_lock := true

# RULE 1: Block creation of files at root level (except authorized)
deny[msg] {
    input.operation == "create_file"
    input.path_depth == 0  # Root level
    filename := input.filename

    # Not in authorized list
    not filename in authorized_root_files

    # Not already a known migration candidate
    not filename in migration_mappings

    msg := sprintf("CRITICAL: Unauthorized file creation at root: '%s' - violates Root-24-LOCK. All files must be within authorized Root-24 modules.", [filename])
}

# RULE 2: Block creation of directories at root level (except authorized)
deny[msg] {
    input.operation == "create_directory"
    input.path_depth == 0  # Root level
    dirname := input.dirname

    # Not in authorized roots
    not dirname in authorized_root_modules

    # Not in authorized exceptions
    not dirname in authorized_root_dirs

    msg := sprintf("CRITICAL: Unauthorized directory creation at root: '%s' - violates Root-24-LOCK. Only 24 authorized root modules permitted.", [dirname])
}

# RULE 3: Block prohibited patterns anywhere in tree
deny[msg] {
    input.operation in ["create_file", "create_directory"]
    some pattern
    pattern := prohibited_patterns[_]
    contains(input.full_path, pattern)

    msg := sprintf("CRITICAL: Prohibited pattern '%s' detected in path '%s' - cache/build artifacts not allowed in repository.", [pattern, input.full_path])
}

# RULE 4: Detect migration candidates and warn
deny[msg] {
    input.operation == "create_file"
    input.path_depth == 0
    filename := input.filename
    filename in migration_mappings

    target := migration_mappings[filename]

    msg := sprintf("WARNING: File '%s' should be created at '%s' according to Root-24-LOCK migration policy.", [filename, target])
}

# RULE 5: Block writes to root-level files (except git operations)
deny[msg] {
    input.operation == "write_file"
    input.path_depth == 0
    filename := input.filename

    # Not an authorized exception
    not filename in authorized_root_files

    # Not git-related
    not startswith(filename, ".git")

    msg := sprintf("CRITICAL: Write operation to root file '%s' blocked - Root-24-LOCK enforcement.", [filename])
}

# RULE 6: Enforce Root-24 module boundary
deny[msg] {
    input.operation in ["create_file", "create_directory"]
    input.path_depth > 0

    path_parts := split(input.full_path, "/")
    root_module := path_parts[0]

    # Check if first path component is authorized
    not root_module in authorized_root_modules
    not root_module in authorized_root_dirs

    msg := sprintf("CRITICAL: Operation in unauthorized module '%s' - path '%s' violates Root-24-LOCK.", [root_module, input.full_path])
}

# ========================================================================
# ALLOW RULES
# ========================================================================

# Allow reads anywhere
allow if {
    input.operation == "read"
}

# Allow operations within authorized Root-24 modules
allow if {
    input.operation in ["create_file", "create_directory", "write_file", "delete"]
    input.path_depth > 0

    path_parts := split(input.full_path, "/")
    root_module := path_parts[0]

    root_module in authorized_root_modules
}

# Allow operations on authorized root files
allow if {
    input.operation in ["read", "write_file"]
    input.path_depth == 0
    input.filename in authorized_root_files
}

# Allow git operations
allow if {
    input.operation in ["create_file", "write_file", "delete"]
    startswith(input.full_path, ".git/")
}

# Allow .github operations (CI/CD)
allow if {
    input.operation in ["create_file", "write_file", "delete"]
    startswith(input.full_path, ".github/")
}

# ========================================================================
# COMPLIANCE CHECKING
# ========================================================================

# Check if all 24 root modules exist
all_roots_present if {
    # Count existing roots from input
    existing_roots := {root |
        some root
        root := input.existing_roots[_]
        root in authorized_root_modules
    }

    count(existing_roots) == 24
}

# Check for critical violations
has_critical_violations if {
    some msg
    deny[msg]
    contains(msg, "CRITICAL")
}

# Check for warnings
has_warnings if {
    some msg
    deny[msg]
    contains(msg, "WARNING")
}

# Calculate compliance score
compliance_score := score if {
    base_score := 100

    # Count violations
    critical_count := count([msg | msg := deny[_]; contains(msg, "CRITICAL")])
    warning_count := count([msg | msg := deny[_]; contains(msg, "WARNING")])

    # Deductions
    critical_deduction := critical_count * 20
    warning_deduction := warning_count * 5

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
# FORENSIC ANALYSIS
# ========================================================================

# Collect all violations
all_violations := violations if {
    violations := [
        {
            "message": msg,
            "severity": severity,
            "operation": input.operation,
            "path": input.full_path
        } |
        msg := deny[_]
        severity := "CRITICAL" if contains(msg, "CRITICAL") else "WARNING"
    ]
}

# Generate migration recommendations
migration_recommendations := recommendations if {
    recommendations := [
        {
            "current_path": filename,
            "target_path": target,
            "action": "MOVE",
            "reason": "Root-24-LOCK compliance"
        } |
        filename := migration_mappings[_]
        target := migration_mappings[filename]
    ]
}

# ========================================================================
# AUDIT REPORT
# ========================================================================

audit_report := {
    "policy_version": "2.0.0",
    "framework": "Root-24-LOCK",
    "timestamp": time.now_ns(),
    "compliance_score": compliance_score,
    "compliance_status": compliance_status,
    "all_roots_present": all_roots_present,
    "has_critical_violations": has_critical_violations,
    "has_warnings": has_warnings,
    "violations": all_violations,
    "migration_recommendations": migration_recommendations,
    "enforcement_level": "STRICT",
    "cost_usd": 0
}

# ========================================================================
# HELPER FUNCTIONS
# ========================================================================

# Check if path is within Root-24 module
is_within_root24_module(path) if {
    path_parts := split(path, "/")
    count(path_parts) > 0
    root_module := path_parts[0]
    root_module in authorized_root_modules
}

# Check if filename matches prohibited pattern
matches_prohibited_pattern(filename) if {
    some pattern
    pattern := prohibited_patterns[_]
    contains(filename, pattern)
}

# Get recommended target path for file
get_target_path(filename) := target if {
    filename in migration_mappings
    target := migration_mappings[filename]
} else := "unknown"

# ========================================================================
# POLICY METADATA
# ========================================================================

policy_metadata := {
    "name": "SSID Root-24-LOCK Activation Policy",
    "version": "2.0.0",
    "mode": "ENFORCEMENT",
    "framework": "Root-24-LOCK",
    "authorized_roots_count": count(authorized_root_modules),
    "authorized_exceptions_count": count(authorized_root_files) + count(authorized_root_dirs),
    "prohibited_patterns_count": count(prohibited_patterns),
    "migration_mappings_count": count(migration_mappings),
    "cost_usd": 0,
    "created": "2025-10-12"
}
