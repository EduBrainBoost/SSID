# SSID Architecture Master Rules - OPA Tests
# Test Suite for AR001-AR010 Policy Enforcement
#
# Run tests with: opa test . -v
#
# Version: 1.0.0

package ssid.architecture.rules

import future.keywords.if

# =============================================================================
# AR001 Tests: 24 Root Folders
# =============================================================================

test_ar001_pass_with_24_root_folders if {
    allow with input as {
        "validation_result": {
            "rule_id": "AR001",
            "passed": true,
            "evidence": {"total_root_folders": 24}
        }
    }
}

test_ar001_deny_with_23_root_folders if {
    count(deny) > 0 with input as {
        "validation_result": {
            "rule_id": "AR001",
            "passed": false,
            "evidence": {"total_root_folders": 23}
        }
    }
}

test_ar001_deny_create_unauthorized_root if {
    count(deny_ar001) > 0 with input as {
        "action": "create_directory",
        "path_depth": 0,
        "folder_name": "99_unauthorized"
    }
}

test_ar001_allow_create_authorized_root if {
    count(deny_ar001) == 0 with input as {
        "action": "create_directory",
        "path_depth": 0,
        "folder_name": "01_ai_layer"
    }
}

test_ar001_deny_delete_required_root if {
    count(deny_ar001) > 0 with input as {
        "action": "delete_directory",
        "path_depth": 0,
        "folder_name": "01_ai_layer"
    }
}

# =============================================================================
# AR002 Tests: 16 Shards per Root
# =============================================================================

test_ar002_pass_with_16_shards if {
    allow with input as {
        "validation_result": {
            "rule_id": "AR002",
            "passed": true,
            "evidence": {"01_ai_layer": {"count": 16}}
        }
    }
}

test_ar002_deny_with_15_shards if {
    count(deny) > 0 with input as {
        "validation_result": {
            "rule_id": "AR002",
            "passed": false,
            "violations": ["01_ai_layer: Expected 16 shards, found 15"]
        }
    }
}

test_ar002_deny_create_17th_shard if {
    count(deny_ar002) > 0 with input as {
        "action": "create_directory",
        "path_depth": 2,
        "parent_folder": "shards",
        "root_folder": "01_ai_layer",
        "existing_shards": [
            "Shard_01_A", "Shard_02_B", "Shard_03_C", "Shard_04_D",
            "Shard_05_E", "Shard_06_F", "Shard_07_G", "Shard_08_H",
            "Shard_09_I", "Shard_10_J", "Shard_11_K", "Shard_12_L",
            "Shard_13_M", "Shard_14_N", "Shard_15_O", "Shard_16_P"
        ]
    }
}

# =============================================================================
# AR003 Tests: 384 Charts
# =============================================================================

test_ar003_pass_with_384_charts if {
    allow with input as {
        "validation_result": {
            "rule_id": "AR003",
            "passed": true,
            "evidence": {"total_charts": 384}
        }
    }
}

test_ar003_deny_with_383_charts if {
    count(deny) > 0 with input as {
        "validation_result": {
            "rule_id": "AR003",
            "passed": false,
            "evidence": {"total_charts": 383}
        }
    }
}

test_ar003_deny_delete_chart_yaml if {
    count(deny_ar003) > 0 with input as {
        "action": "delete_file",
        "file_path": "01_ai_layer/shards/Shard_01_Identity/chart.yaml"
    }
}

# =============================================================================
# AR004 Tests: Root Folder Format
# =============================================================================

test_ar004_allow_valid_root_format if {
    count(deny_ar004) == 0 with input as {
        "action": "create_directory",
        "path_depth": 0,
        "folder_name": "01_ai_layer"
    }
}

test_ar004_deny_invalid_root_format_no_number if {
    count(deny_ar004) > 0 with input as {
        "action": "create_directory",
        "path_depth": 0,
        "folder_name": "ai_layer"
    }
}

test_ar004_deny_invalid_root_format_uppercase if {
    count(deny_ar004) > 0 with input as {
        "action": "create_directory",
        "path_depth": 0,
        "folder_name": "01_AI_Layer"
    }
}

test_ar004_deny_invalid_root_format_spaces if {
    count(deny_ar004) > 0 with input as {
        "action": "create_directory",
        "path_depth": 0,
        "folder_name": "01 ai layer"
    }
}

# =============================================================================
# AR005 Tests: Shard Format
# =============================================================================

test_ar005_allow_valid_shard_format if {
    count(deny_ar005) == 0 with input as {
        "action": "create_directory",
        "path_depth": 2,
        "parent_folder": "shards",
        "folder_name": "Shard_01_Identity"
    }
}

test_ar005_allow_shard_with_mixed_case if {
    count(deny_ar005) == 0 with input as {
        "action": "create_directory",
        "path_depth": 2,
        "parent_folder": "shards",
        "folder_name": "Shard_01_MyComponent"
    }
}

test_ar005_deny_lowercase_shard_prefix if {
    count(deny_ar005) > 0 with input as {
        "action": "create_directory",
        "path_depth": 2,
        "parent_folder": "shards",
        "folder_name": "shard_01_identity"
    }
}

test_ar005_deny_shard_without_number if {
    count(deny_ar005) > 0 with input as {
        "action": "create_directory",
        "path_depth": 2,
        "parent_folder": "shards",
        "folder_name": "Shard_Identity"
    }
}

test_ar005_deny_old_format_shard if {
    count(deny_ar005) > 0 with input as {
        "action": "create_directory",
        "path_depth": 2,
        "parent_folder": "shards",
        "folder_name": "01_identity"
    }
}

# =============================================================================
# AR006 Tests: chart.yaml Exists
# =============================================================================

test_ar006_pass_no_missing_charts if {
    allow with input as {
        "validation_result": {
            "rule_id": "AR006",
            "passed": true,
            "evidence": {"missing_count": 0}
        }
    }
}

test_ar006_deny_missing_charts if {
    count(deny) > 0 with input as {
        "validation_result": {
            "rule_id": "AR006",
            "passed": false,
            "evidence": {"missing_count": 5}
        }
    }
}

test_ar006_deny_create_shard_without_chart if {
    count(deny_ar006) > 0 with input as {
        "action": "create_directory",
        "path_depth": 2,
        "parent_folder": "shards",
        "folder_name": "Shard_01_New",
        "contains_chart_yaml": false
    }
}

test_ar006_allow_create_shard_with_chart if {
    count(deny_ar006) == 0 with input as {
        "action": "create_directory",
        "path_depth": 2,
        "parent_folder": "shards",
        "folder_name": "Shard_01_New",
        "contains_chart_yaml": true
    }
}

# =============================================================================
# AR007 Tests: manifest.yaml Exists
# =============================================================================

test_ar007_pass_no_missing_manifests if {
    allow with input as {
        "validation_result": {
            "rule_id": "AR007",
            "passed": true,
            "evidence": {"missing_manifests": 0}
        }
    }
}

test_ar007_deny_missing_manifests if {
    count(deny) > 0 with input as {
        "validation_result": {
            "rule_id": "AR007",
            "passed": false,
            "evidence": {"missing_manifests": 3}
        }
    }
}

test_ar007_deny_create_impl_without_manifest if {
    count(deny_ar007) > 0 with input as {
        "action": "create_directory",
        "parent_folder": "implementations",
        "folder_name": "python-fastapi",
        "contains_manifest_yaml": false
    }
}

# =============================================================================
# AR008 Tests: Path Structure
# =============================================================================

test_ar008_pass_correct_path_structure if {
    allow with input as {
        "validation_result": {
            "rule_id": "AR008",
            "passed": true,
            "violations": []
        }
    }
}

test_ar008_deny_chart_outside_shards if {
    count(deny_ar008) > 0 with input as {
        "action": "create_file",
        "file_name": "chart.yaml",
        "file_path": "01_ai_layer/chart.yaml"
    }
}

test_ar008_allow_chart_in_correct_path if {
    count(deny_ar008) == 0 with input as {
        "action": "create_file",
        "file_name": "chart.yaml",
        "file_path": "01_ai_layer/shards/Shard_01_Identity/chart.yaml"
    }
}

# =============================================================================
# AR009 Tests: Implementations Path
# =============================================================================

test_ar009_pass_implementations_in_correct_path if {
    allow with input as {
        "validation_result": {
            "rule_id": "AR009",
            "passed": true,
            "violations": []
        }
    }
}

test_ar009_deny_impl_outside_implementations_folder if {
    count(deny_ar009) > 0 with input as {
        "action": "create_directory",
        "is_implementation_dir": true,
        "dir_path": "01_ai_layer/shards/Shard_01/python-impl"
    }
}

test_ar009_allow_impl_in_implementations_folder if {
    count(deny_ar009) == 0 with input as {
        "action": "create_directory",
        "is_implementation_dir": true,
        "dir_path": "01_ai_layer/shards/Shard_01/implementations/python-impl"
    }
}

# =============================================================================
# AR010 Tests: Contracts Folder
# =============================================================================

test_ar010_pass_contracts_in_correct_folder if {
    allow with input as {
        "validation_result": {
            "rule_id": "AR010",
            "passed": true,
            "violations": []
        }
    }
}

test_ar010_deny_contract_outside_contracts_folder if {
    count(deny_ar010) > 0 with input as {
        "action": "create_file",
        "is_contract_file": true,
        "file_path": "01_ai_layer/api_spec.yaml"
    }
}

test_ar010_allow_contract_in_contracts_folder if {
    count(deny_ar010) == 0 with input as {
        "action": "create_file",
        "is_contract_file": true,
        "file_path": "01_ai_layer/contracts/api_spec.yaml",
        "file_extension": "yaml"
    }
}

test_ar010_deny_invalid_contract_extension if {
    count(deny_ar010) > 0 with input as {
        "action": "create_file",
        "file_path": "01_ai_layer/contracts/spec.txt",
        "file_extension": "txt"
    }
}

test_ar010_allow_yaml_contract if {
    count(deny_ar010) == 0 with input as {
        "action": "create_file",
        "is_contract_file": true,
        "file_path": "01_ai_layer/contracts/api.yaml",
        "file_extension": "yaml"
    }
}

test_ar010_allow_json_contract if {
    count(deny_ar010) == 0 with input as {
        "action": "create_file",
        "is_contract_file": true,
        "file_path": "01_ai_layer/contracts/schema.json",
        "file_extension": "json"
    }
}

# =============================================================================
# Integration Tests
# =============================================================================

test_all_rules_pass if {
    allow with input as {
        "validation_results": [
            {"rule_id": "AR001", "passed": true, "violations": []},
            {"rule_id": "AR002", "passed": true, "violations": []},
            {"rule_id": "AR003", "passed": true, "violations": []},
            {"rule_id": "AR004", "passed": true, "violations": []},
            {"rule_id": "AR005", "passed": true, "violations": []},
            {"rule_id": "AR006", "passed": true, "violations": []},
            {"rule_id": "AR007", "passed": true, "violations": []},
            {"rule_id": "AR008", "passed": true, "violations": []},
            {"rule_id": "AR009", "passed": true, "violations": []},
            {"rule_id": "AR010", "passed": true, "violations": []}
        ]
    }
}

test_one_rule_fails if {
    not allow with input as {
        "validation_results": [
            {"rule_id": "AR001", "passed": false, "violations": ["Test violation"]},
            {"rule_id": "AR002", "passed": true, "violations": []}
        ]
    }
}

test_compliance_report_structure if {
    report := compliance_report with input as {
        "validation_results": [
            {"rule_id": "AR001", "passed": true, "violations": []},
            {"rule_id": "AR002", "passed": false, "violations": ["Error 1", "Error 2"]}
        ]
    }

    report.total_rules_checked == 2
    report.rules_passed == 1
    report.rules_failed == 1
}

test_audit_trail_contains_timestamp if {
    trail := audit_trail with input as {
        "validation_results": [
            {"rule_id": "AR001", "passed": true, "violations": []}
        ]
    }

    trail.timestamp > 0
    trail.policy_version == "1.0.0"
    trail.policy_package == "ssid.architecture.rules"
}

# =============================================================================
# Edge Cases
# =============================================================================

test_empty_validation_results if {
    allow with input as {
        "validation_results": []
    }
}

test_null_input if {
    count(deny) == 0 with input as {}
}

test_malformed_validation_result if {
    count(deny) == 0 with input as {
        "validation_result": {
            "rule_id": "AR999"
        }
    }
}
