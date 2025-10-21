# SSID Architecture Master Rules (AR001-AR010)
# OPA Policy Enforcement for 24x16 Matrix Architecture
#
# References:
# - Master Rules: 16_codex/structure/level3/master_rules.yaml
# - Validator: 03_core/validators/architecture_validator.py
# - Contracts: 03_core/contracts/architecture_validation_api.yaml
# - Tests: tests/test_architecture_rules.py
#
# Version: 1.0.0
# Status: Production-Ready

package ssid.architecture.rules

import future.keywords.if
import future.keywords.in

# =============================================================================
# AR001: Das System MUSS aus exakt 24 Root-Ordnern bestehen
# =============================================================================

# List of required 24 root folders
required_root_folders := {
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
    "11_privacy_consent",
    "12_reputation_trust",
    "13_token_economy",
    "14_zero_knowledge",
    "15_federation",
    "16_codex",
    "17_oracle",
    "18_dispute",
    "19_recovery",
    "20_versioning",
    "21_analytics",
    "22_marketplace",
    "23_compliance",
    "24_emergency"
}

# AR001: Deny if not exactly 24 root folders
deny_ar001[msg] if {
    input.validation_result.rule_id == "AR001"
    not input.validation_result.passed
    msg := sprintf(
        "AR001 VIOLATION: Expected 24 root folders, found %d",
        [input.validation_result.evidence.total_root_folders]
    )
}

# AR001: Deny if unknown root folder is created
deny_ar001[msg] if {
    input.action == "create_directory"
    input.path_depth == 0
    folder_name := input.folder_name
    not folder_name in required_root_folders
    msg := sprintf(
        "AR001 VIOLATION: Attempt to create unauthorized root folder '%s'",
        [folder_name]
    )
}

# AR001: Deny if root folder is deleted
deny_ar001[msg] if {
    input.action == "delete_directory"
    input.path_depth == 0
    folder_name := input.folder_name
    folder_name in required_root_folders
    msg := sprintf(
        "AR001 VIOLATION: Attempt to delete required root folder '%s'",
        [folder_name]
    )
}

# =============================================================================
# AR002: Jeder Root-Ordner MUSS exakt 16 Shards enthalten
# =============================================================================

required_shard_count := 16

# AR002: Deny if root folder does not have exactly 16 shards
deny_ar002[msg] if {
    input.validation_result.rule_id == "AR002"
    not input.validation_result.passed
    some violation in input.validation_result.violations
    msg := sprintf("AR002 VIOLATION: %s", [violation])
}

# AR002: Deny if attempting to create more than 16 shards
deny_ar002[msg] if {
    input.action == "create_directory"
    input.path_depth == 2  # root/shards/shard_name
    input.parent_folder == "shards"
    count(input.existing_shards) >= required_shard_count
    msg := sprintf(
        "AR002 VIOLATION: Root folder '%s' already has %d shards (max: 16)",
        [input.root_folder, count(input.existing_shards)]
    )
}

# =============================================================================
# AR003: Es MUESSEN exakt 384 Chart-Dateien existieren (24x16)
# =============================================================================

required_chart_count := 384

# AR003: Deny if not exactly 384 charts
deny_ar003[msg] if {
    input.validation_result.rule_id == "AR003"
    not input.validation_result.passed
    total_charts := input.validation_result.evidence.total_charts
    msg := sprintf(
        "AR003 VIOLATION: Expected 384 chart.yaml files, found %d",
        [total_charts]
    )
}

# AR003: Deny if attempting to delete chart.yaml
deny_ar003[msg] if {
    input.action == "delete_file"
    endswith(input.file_path, "chart.yaml")
    msg := sprintf(
        "AR003 VIOLATION: Attempt to delete chart.yaml at '%s'",
        [input.file_path]
    )
}

# =============================================================================
# AR004: Root-Ordner MUESSEN Format '{NR}_{NAME}' haben
# =============================================================================

# AR004: Deny if root folder format is invalid
deny_ar004[msg] if {
    input.action == "create_directory"
    input.path_depth == 0
    folder_name := input.folder_name
    not regex.match(`^\d{2}_[a-z_]+$`, folder_name)
    msg := sprintf(
        "AR004 VIOLATION: Invalid root folder format '%s' (expected: ##_lowercase_with_underscores)",
        [folder_name]
    )
}

# AR004: Deny based on validation result
deny_ar004[msg] if {
    input.validation_result.rule_id == "AR004"
    not input.validation_result.passed
    some violation in input.validation_result.violations
    msg := sprintf("AR004 VIOLATION: %s", [violation])
}

# =============================================================================
# AR005: Shards MUESSEN Format 'Shard_{NR}_{NAME}' haben
# =============================================================================

# AR005: Deny if shard format is invalid
deny_ar005[msg] if {
    input.action == "create_directory"
    input.path_depth == 2  # root/shards/shard_name
    input.parent_folder == "shards"
    shard_name := input.folder_name
    not regex.match(`^Shard_\d{2}_[A-Za-z_]+$`, shard_name)
    msg := sprintf(
        "AR005 VIOLATION: Invalid shard format '%s' (expected: Shard_##_Name)",
        [shard_name]
    )
}

# AR005: Deny based on validation result
deny_ar005[msg] if {
    input.validation_result.rule_id == "AR005"
    not input.validation_result.passed
    count(input.validation_result.violations) > 0
    msg := sprintf(
        "AR005 VIOLATION: %d shards with invalid format detected",
        [count(input.validation_result.violations)]
    )
}

# =============================================================================
# AR006: Jeder Shard MUSS eine chart.yaml (SoT) enthalten
# =============================================================================

# AR006: Deny if chart.yaml is missing
deny_ar006[msg] if {
    input.validation_result.rule_id == "AR006"
    not input.validation_result.passed
    missing_count := input.validation_result.evidence.missing_count
    missing_count > 0
    msg := sprintf(
        "AR006 VIOLATION: %d shards missing chart.yaml",
        [missing_count]
    )
}

# AR006: Deny if creating shard directory without chart.yaml
deny_ar006[msg] if {
    input.action == "create_directory"
    input.path_depth == 2
    input.parent_folder == "shards"
    not input.contains_chart_yaml
    msg := sprintf(
        "AR006 VIOLATION: New shard '%s' must contain chart.yaml",
        [input.folder_name]
    )
}

# =============================================================================
# AR007: Jede Implementierung MUSS eine manifest.yaml enthalten
# =============================================================================

# AR007: Deny if manifest.yaml is missing
deny_ar007[msg] if {
    input.validation_result.rule_id == "AR007"
    not input.validation_result.passed
    missing_manifests := input.validation_result.evidence.missing_manifests
    missing_manifests > 0
    msg := sprintf(
        "AR007 VIOLATION: %d implementations missing manifest.yaml",
        [missing_manifests]
    )
}

# AR007: Deny if creating implementation without manifest.yaml
deny_ar007[msg] if {
    input.action == "create_directory"
    input.parent_folder == "implementations"
    not input.contains_manifest_yaml
    msg := sprintf(
        "AR007 VIOLATION: Implementation '%s' must contain manifest.yaml",
        [input.folder_name]
    )
}

# =============================================================================
# AR008: Pfadstruktur MUSS sein: {ROOT}/shards/{SHARD}/chart.yaml
# =============================================================================

# AR008: Deny if shards directory is missing
deny_ar008[msg] if {
    input.validation_result.rule_id == "AR008"
    not input.validation_result.passed
    some violation in input.validation_result.violations
    msg := sprintf("AR008 VIOLATION: %s", [violation])
}

# AR008: Deny if creating chart.yaml outside correct path
deny_ar008[msg] if {
    input.action == "create_file"
    input.file_name == "chart.yaml"
    not regex.match(`^.+/shards/.+/chart\.yaml$`, input.file_path)
    msg := sprintf(
        "AR008 VIOLATION: chart.yaml must be in {ROOT}/shards/{SHARD}/ path (attempted: '%s')",
        [input.file_path]
    )
}

# =============================================================================
# AR009: Implementierungen MUESSEN unter implementations/{IMPL_ID}/ liegen
# =============================================================================

# AR009: Deny based on validation result
deny_ar009[msg] if {
    input.validation_result.rule_id == "AR009"
    not input.validation_result.passed
    some violation in input.validation_result.violations
    msg := sprintf("AR009 VIOLATION: %s", [violation])
}

# AR009: Deny if creating implementation outside correct path
deny_ar009[msg] if {
    input.action == "create_directory"
    input.is_implementation_dir
    not regex.match(`.+/implementations/.+$`, input.dir_path)
    msg := sprintf(
        "AR009 VIOLATION: Implementations must be under implementations/{IMPL_ID}/ (attempted: '%s')",
        [input.dir_path]
    )
}

# =============================================================================
# AR010: Contracts MUESSEN in contracts/-Ordner mit OpenAPI/JSON-Schema liegen
# =============================================================================

# AR010: Deny based on validation result
deny_ar010[msg] if {
    input.validation_result.rule_id == "AR010"
    not input.validation_result.passed
    some violation in input.validation_result.violations
    msg := sprintf("AR010 VIOLATION: %s", [violation])
}

# AR010: Deny if creating contract file outside contracts/ folder
deny_ar010[msg] if {
    input.action == "create_file"
    input.is_contract_file
    not regex.match(`.*/contracts/.*`, input.file_path)
    msg := sprintf(
        "AR010 VIOLATION: Contract files must be in contracts/ folder (attempted: '%s')",
        [input.file_path]
    )
}

# AR010: Deny if contract file has invalid extension
deny_ar010[msg] if {
    input.action == "create_file"
    regex.match(`.*/contracts/.*`, input.file_path)
    file_ext := lower(input.file_extension)
    not file_ext in {"yaml", "yml", "json"}
    msg := sprintf(
        "AR010 VIOLATION: Contract files must be .yaml or .json (attempted: '%s')",
        [input.file_path]
    )
}

# =============================================================================
# Combined Deny Rules
# =============================================================================

# Collect all deny messages
deny[msg] if {
    msg := deny_ar001[_]
}

deny[msg] if {
    msg := deny_ar002[_]
}

deny[msg] if {
    msg := deny_ar003[_]
}

deny[msg] if {
    msg := deny_ar004[_]
}

deny[msg] if {
    msg := deny_ar005[_]
}

deny[msg] if {
    msg := deny_ar006[_]
}

deny[msg] if {
    msg := deny_ar007[_]
}

deny[msg] if {
    msg := deny_ar008[_]
}

deny[msg] if {
    msg := deny_ar009[_]
}

deny[msg] if {
    msg := deny_ar010[_]
}

# =============================================================================
# Allow Rule
# =============================================================================

# Default: allow if no deny rules triggered
default allow := false

allow if {
    count(deny) == 0
}

# =============================================================================
# Helper Functions
# =============================================================================

# Check if all validation results passed
all_validations_passed if {
    input.validation_results
    every result in input.validation_results {
        result.passed == true
    }
}

# Count total violations across all rules
total_violations := count if {
    count := sum([count(result.violations) |
        some result in input.validation_results
    ])
}

# Get severity level for a rule
rule_severity(rule_id) := severity if {
    some result in input.validation_results
    result.rule_id == rule_id
    severity := result.severity
}

# Check if specific rule passed
rule_passed(rule_id) if {
    some result in input.validation_results
    result.rule_id == rule_id
    result.passed == true
}

# =============================================================================
# Compliance Report
# =============================================================================

compliance_report := {
    "overall_compliance": allow,
    "total_rules_checked": count([r | some r in input.validation_results]),
    "rules_passed": count([r | some r in input.validation_results; r.passed]),
    "rules_failed": count([r | some r in input.validation_results; not r.passed]),
    "total_violations": total_violations,
    "all_deny_messages": deny
}

# =============================================================================
# Audit Trail
# =============================================================================

audit_trail := {
    "timestamp": time.now_ns(),
    "policy_version": "1.0.0",
    "policy_package": "ssid.architecture.rules",
    "decision": allow,
    "violations": deny,
    "compliance_report": compliance_report
}
