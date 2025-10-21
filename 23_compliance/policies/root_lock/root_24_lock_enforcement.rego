# ROOT-24-LOCK Enforcement Policy
# =================================
#
# Purpose: Protect 24 root structures from unauthorized modifications
# Version: 2.1.0 (Fixed)
# Date: 2025-10-17
# Exit Code: 24 on violation
#
# This policy enforces the immutability of the 24 SSID root directories
# and their critical files. Any modification attempt that violates the
# ROOT-24-LOCK principle will be blocked.

package ssid.root_lock

import future.keywords.if
import future.keywords.in

# ============================================================================
# ROOT-24 CANONICAL STRUCTURE
# ============================================================================

root_directories := {
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

# ============================================================================
# PROTECTED FILES (NEVER OVERWRITE)
# ============================================================================

protected_files := {
    "module.yaml",
    "README.md",
    ".gitkeep",
    "LOCK",
    "ROOT_24_LOCK"
}

# ============================================================================
# APPEND-ONLY PATHS
# ============================================================================

append_only_paths := {
    "02_audit_logging/storage/worm/",
    "02_audit_logging/logs/",
    "02_audit_logging/reports/",
    "23_compliance/evidence/",
    "24_meta_orchestration/registry/locks/"
}

# ============================================================================
# ENFORCEMENT RULES
# ============================================================================

# Default: deny all modifications
default allow_modification = false

# Allow modification if all checks pass
allow_modification if {
    valid_root_structure
    no_protected_file_overwrite
    append_only_compliance
    sha_chain_intact
}

# ============================================================================
# VALIDATION RULES
# ============================================================================

# Check: All 24 roots exist
valid_root_structure if {
    count(existing_roots) == 24
    existing_roots == root_directories
}

# Check: No protected files are being overwritten
no_protected_file_overwrite if {
    not has_protected_file_violation
}

has_protected_file_violation if {
    some file in input.modified_files
    some protected in protected_files
    endswith(file, protected)
    input.operation == "overwrite"
}

# Check: Append-only paths are respected
append_only_compliance if {
    not has_append_only_violation
}

has_append_only_violation if {
    some file in input.modified_files
    some path in append_only_paths
    startswith(file, path)
    input.operation == "overwrite"
}

# Check: SHA-256 chain is intact
sha_chain_intact if {
    input.sha_verification == true
}

# ============================================================================
# VIOLATION REPORTING
# ============================================================================

violations[msg] {
    not valid_root_structure
    msg := "ROOT-24-LOCK VIOLATION: Invalid root structure - expected 24 roots"
}

violations[msg] {
    has_protected_file_violation
    msg := sprintf("ROOT-24-LOCK VIOLATION: Attempt to overwrite protected file: %v", [input.modified_files])
}

violations[msg] {
    has_append_only_violation
    msg := sprintf("ROOT-24-LOCK VIOLATION: Append-only path modification detected: %v", [input.modified_files])
}

violations[msg] {
    not sha_chain_intact
    msg := "ROOT-24-LOCK VIOLATION: SHA-256 chain integrity failed"
}

# ============================================================================
# EXIT CODE ENFORCEMENT
# ============================================================================

exit_code := 0 if allow_modification
exit_code := 24 if not allow_modification

# ============================================================================
# AUDIT TRAIL
# ============================================================================

audit_entry := {
    "timestamp": time.now_ns(),
    "operation": input.operation,
    "files": input.modified_files,
    "allowed": allow_modification,
    "violations": violations,
    "exit_code": exit_code,
    "root_lock_version": "1.0.0"
}
