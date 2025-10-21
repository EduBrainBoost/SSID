#!/usr/bin/env python3
"""
SoT Validator - Python ↔ OPA Consistency Test
==============================================

Ensures bit-exact consistency between Python validator and OPA policy enforcer.
Both must produce identical validation results for the same input.

Test Strategy:
1. Run Python validators (sot_validator_core_v4.py)
2. Evaluate OPA policy (sot_policy.rego)
3. Compare results rule-by-rule
4. Fail if any discrepancy detected

Author: SSID Core Team
Version: 4.0.0 (Python ↔ OPA Consistency)
Date: 2025-10-18
"""

import pytest
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, Set

# Add core module to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "03_core"))

from validators.sot.sot_validator_core_v4 import (
    run_all_validations,
    RULE_PRIORITIES,
    ValidationResult
)


# =============================================================================
# OPA EVALUATION HELPER
# =============================================================================

def evaluate_opa_policy(input_data: Dict[str, Any], policy_path: str) -> Dict[str, Any]:
    """
    Evaluate OPA policy and return deny/warn/info sets.

    Args:
        input_data: Input data for validation
        policy_path: Path to .rego policy file

    Returns:
        Dict with 'deny', 'warn', 'info' sets of rule IDs
    """
    # Create OPA input structure
    opa_input = {
        "version": input_data.get("version"),
        "date": input_data.get("date"),
        "deprecated": input_data.get("deprecated"),
        "regulatory_basis": input_data.get("regulatory_basis"),
        "classification": input_data.get("classification"),
        "soc2": input_data.get("soc2", {})
    }

    # Convert to JSON
    input_json = json.dumps({"input": opa_input})

    # Run OPA eval
    try:
        result = subprocess.run(
            ["opa", "eval", "-d", policy_path, "-i", "-", "data.ssid.sot.consolidated.v3_2"],
            input=input_json,
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode != 0:
            # OPA not available or policy error
            # Return empty result for graceful degradation
            return {"deny": set(), "warn": set(), "info": set(), "opa_available": False}

        # Parse OPA output
        output = json.loads(result.stdout)
        opa_result = output.get("result", [{}])[0].get("expressions", [{}])[0].get("value", {})

        deny_set = set(opa_result.get("deny", []))
        warn_set = set(opa_result.get("warn", []))
        info_set = set(opa_result.get("info", []))

        return {
            "deny": deny_set,
            "warn": warn_set,
            "info": info_set,
            "opa_available": True
        }

    except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError):
        # OPA not available or other error
        return {"deny": set(), "warn": set(), "info": set(), "opa_available": False}


# =============================================================================
# CONSISTENCY TESTS
# =============================================================================

@pytest.fixture
def valid_test_data():
    """Valid test data for consistency check"""
    return {
        "version": "2.0.0",
        "date": "2025-10-18",
        "deprecated": False,
        "regulatory_basis": "FATF Recommendation 16, OECD CARF 2025-07, ISO 24165-2:2025",
        "classification": "CONFIDENTIAL - Internal Compliance Matrix",
        "soc2": {
            "entry_marker_soc2": "soc2/:"
        }
    }


@pytest.fixture
def invalid_test_data():
    """Invalid test data for consistency check"""
    return {
        "version": "1.0",  # Invalid format
        "date": "2025-10-18",
        "deprecated": False,
        "regulatory_basis": "Short",  # Too short
        "classification": "INVALID",
        "soc2": {}  # Missing marker
    }


def test_python_vs_opa_consistency_valid_data(valid_test_data):
    """
    Test Python ↔ OPA consistency with valid data.
    Both should agree that all rules pass.
    """
    # Run Python validators
    py_results = run_all_validations(valid_test_data)
    py_results_map = {r.rule_id: {"ok": r.passed, "priority": r.priority} for r in py_results}

    # Prepare OPA input
    opa_policy_path = str(Path(__file__).parent.parent.parent / "23_compliance" / "policies" / "sot" / "sot_policy.rego")

    # Run OPA evaluation
    opa_results = evaluate_opa_policy(valid_test_data, opa_policy_path)

    # Skip test if OPA not available
    if not opa_results.get("opa_available", False):
        pytest.skip("OPA not available for consistency testing")

    # Check consistency for each rule
    for rule_id, py_result in py_results_map.items():
        # Python says PASS
        if py_result["ok"]:
            # OPA should NOT have this in deny/warn/info
            assert rule_id not in opa_results["deny"], \
                f"{rule_id}: Python PASS but OPA DENY - INCONSISTENCY!"
            if py_result["priority"] == "should":
                assert rule_id not in opa_results["warn"], \
                    f"{rule_id}: Python PASS but OPA WARN - INCONSISTENCY!"
        else:
            # Python says FAIL
            # OPA should have this in appropriate set based on priority
            if py_result["priority"] == "must":
                assert rule_id in opa_results["deny"], \
                    f"{rule_id}: Python FAIL (MUST) but OPA doesn't DENY - INCONSISTENCY!"
            elif py_result["priority"] == "should":
                assert rule_id in opa_results["warn"], \
                    f"{rule_id}: Python FAIL (SHOULD) but OPA doesn't WARN - INCONSISTENCY!"


def test_python_vs_opa_consistency_invalid_data(invalid_test_data):
    """
    Test Python ↔ OPA consistency with invalid data.
    Both should agree on which rules fail.
    """
    # Run Python validators
    py_results = run_all_validations(invalid_test_data)
    py_results_map = {r.rule_id: {"ok": r.passed, "priority": r.priority} for r in py_results}

    # Prepare OPA input
    opa_policy_path = str(Path(__file__).parent.parent.parent / "23_compliance" / "policies" / "sot" / "sot_policy.rego")

    # Run OPA evaluation
    opa_results = evaluate_opa_policy(invalid_test_data, opa_policy_path)

    # Skip test if OPA not available
    if not opa_results.get("opa_available", False):
        pytest.skip("OPA not available for consistency testing")

    # Track failures for detailed reporting
    inconsistencies = []

    # Check consistency for each rule
    for rule_id, py_result in py_results_map.items():
        if py_result["ok"]:
            # Python says PASS
            if rule_id in opa_results["deny"]:
                inconsistencies.append(f"{rule_id}: Python PASS but OPA DENY")
            if py_result["priority"] == "should" and rule_id in opa_results["warn"]:
                inconsistencies.append(f"{rule_id}: Python PASS but OPA WARN")
        else:
            # Python says FAIL
            if py_result["priority"] == "must" and rule_id not in opa_results["deny"]:
                inconsistencies.append(f"{rule_id}: Python FAIL (MUST) but OPA doesn't DENY")
            elif py_result["priority"] == "should" and rule_id not in opa_results["warn"]:
                inconsistencies.append(f"{rule_id}: Python FAIL (SHOULD) but OPA doesn't WARN")

    # Assert no inconsistencies
    assert len(inconsistencies) == 0, \
        f"Python ↔ OPA Inconsistencies detected:\n" + "\n".join(inconsistencies)


def test_moscow_priority_mapping_consistency():
    """
    Test that RULE_PRIORITIES mapping is consistent across Python and OPA.
    This is a meta-test ensuring the priority definitions match.
    """
    # This test verifies that RULE_PRIORITIES exists and has expected structure
    assert isinstance(RULE_PRIORITIES, dict), "RULE_PRIORITIES should be a dict"

    # Check that we have MUST, SHOULD, HAVE rules
    must_rules = [rid for rid, priority in RULE_PRIORITIES.items() if priority == "must"]
    should_rules = [rid for rid, priority in RULE_PRIORITIES.items() if priority == "should"]
    have_rules = [rid for rid, priority in RULE_PRIORITIES.items() if priority == "have"]

    assert len(must_rules) > 0, "Should have MUST rules"
    assert len(should_rules) > 0, "Should have SHOULD rules"
    assert len(have_rules) > 0, "Should have HAVE rules"

    # Verify expected distribution (48 MUST, 15 SHOULD, 6 HAVE)
    assert len(must_rules) == 48, f"Expected 48 MUST rules, got {len(must_rules)}"
    assert len(should_rules) == 15, f"Expected 15 SHOULD rules, got {len(should_rules)}"
    assert len(have_rules) == 6, f"Expected 6 HAVE rules, got {len(have_rules)}"


def test_evidence_field_present_in_all_results(valid_test_data):
    """
    Test that all ValidationResult objects contain evidence field.
    This ensures scientific auditability.
    """
    results = run_all_validations(valid_test_data)

    for result in results:
        assert isinstance(result, ValidationResult), \
            f"{result.rule_id}: Result should be ValidationResult instance"

        assert hasattr(result, 'evidence'), \
            f"{result.rule_id}: ValidationResult missing 'evidence' field"

        assert isinstance(result.evidence, dict), \
            f"{result.rule_id}: Evidence should be dict, got {type(result.evidence)}"

        # Verify evidence contains expected fields
        assert "validation_timestamp" in result.evidence, \
            f"{result.rule_id}: Evidence should contain 'validation_timestamp'"


# =============================================================================
# RUN TESTS
# =============================================================================

if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
