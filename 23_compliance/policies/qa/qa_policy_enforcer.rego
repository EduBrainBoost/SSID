# SSID QA/SoT Dual-Layer Policy Enforcer (OPA)
# ==============================================
# Version: 1.0.0
# Date: 2025-10-18
# Author: SSID Core Team
#
# PURPOSE:
# Enforce that QA test files are only added to the unified QA corpus,
# preventing governance pollution and test chaos.
#
# POLICY:
# - All QA test files (.py, .yaml, .yml, .rego, .json) MUST reside in:
#   02_audit_logging/archives/qa_master_suite/
#   OR
#   11_test_simulation/ (active test directory)
#
# EXCEPTIONS:
# - SoT governance artifacts (5 files only):
#   * 16_codex/contracts/sot/sot_contract.yaml
#   * 03_core/validators/sot/sot_validator_core.py
#   * 23_compliance/policies/sot/sot_policy.rego
#   * 12_tooling/cli/sot_validator.py
#   * 11_test_simulation/tests_compliance/test_sot_validator.py
#
# INPUT SCHEMA:
# {
#   "files": [
#     {"path": "path/to/file.py", "action": "add"},
#     ...
#   ]
# }
#
# USAGE:
# opa eval -i files.json -d qa_policy_enforcer.rego "data.qa_policy.deny"
# opa eval -i files.json -d qa_policy_enforcer.rego "data.qa_policy.report"

package qa_policy

import rego.v1

# ==============================================================================
# CONFIGURATION
# ==============================================================================

# Allowed directories for QA test files
allowed_qa_dirs := [
    "02_audit_logging/archives/qa_master_suite/",
    "11_test_simulation/"
]

# SoT governance artifacts (exempt from QA policy)
sot_governance_files := {
    "16_codex/contracts/sot/sot_contract.yaml",
    "03_core/validators/sot/sot_validator_core.py",
    "23_compliance/policies/sot/sot_policy.rego",
    "12_tooling/cli/sot_validator.py",
    "11_test_simulation/tests_compliance/test_sot_validator.py"
}

# QA test file extensions
qa_test_extensions := {".py", ".yaml", ".yml", ".rego", ".json"}

# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

# Check if file has QA test extension
is_qa_test_file(filepath) if {
    some ext in qa_test_extensions
    endswith(filepath, ext)
}

# Check if file is a SoT governance artifact
is_sot_governance_file(filepath) if {
    filepath in sot_governance_files
}

# Check if file is in allowed QA directory
is_in_allowed_qa_dir(filepath) if {
    some allowed_dir in allowed_qa_dirs
    startswith(filepath, allowed_dir)
}

# ==============================================================================
# POLICY RULES
# ==============================================================================

# DENY: QA test files outside allowed directories
deny contains filepath if {
    some file in input.files
    filepath := file.path

    # Must be a QA test file
    is_qa_test_file(filepath)

    # Must NOT be a SoT governance file
    not is_sot_governance_file(filepath)

    # Must NOT be in allowed QA directory
    not is_in_allowed_qa_dir(filepath)
}

# ==============================================================================
# REPORTING
# ==============================================================================

# Count total files checked
total_files := count(input.files)

# Count QA test files
qa_test_files := count([f | some f in input.files; is_qa_test_file(f.path)])

# Count violations
violation_count := count(deny)

# Overall compliance status
compliance_status := "PASS" if {
    violation_count == 0
} else := "FAIL"

# Detailed report
report := {
    "version": "1.0.0",
    "timestamp": time.now_ns(),
    "policy": "QA/SoT Dual-Layer Enforcement",
    "total_files": total_files,
    "qa_test_files": qa_test_files,
    "violations": violation_count,
    "status": compliance_status,
    "denied_files": deny,
    "policy_document": "02_audit_logging/archives/qa_master_suite/README.md"
}

# ==============================================================================
# ASSERTIONS (for testing)
# ==============================================================================

# Assert: No violations for compliant input
test_no_violations if {
    compliance_status == "PASS"
    violation_count == 0
}

# Assert: SoT governance files are always allowed
test_sot_files_allowed if {
    every filepath in sot_governance_files {
        is_sot_governance_file(filepath)
    }
}

# Assert: Files in allowed dirs are permitted
test_allowed_dirs if {
    every allowed_dir in allowed_qa_dirs {
        test_file := concat("", [allowed_dir, "test.py"])
        is_in_allowed_qa_dir(test_file)
    }
}
