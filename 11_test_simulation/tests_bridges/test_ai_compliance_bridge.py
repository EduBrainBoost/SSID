"""
Test: 01_ai_layer → 23_compliance bridge
Tests AI decision policy validation
"""

import pytest
import sys
import os

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, project_root)

# Load module with importlib since module names starting with numbers are invalid
import importlib.util
spec = importlib.util.spec_from_file_location(
    "bridge_compliance",
    os.path.join(project_root, "01_ai_layer/interconnect/bridge_compliance.py")
)
bridge_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bridge_module)

validate_ai_decision = bridge_module.validate_ai_decision
get_ai_policy_requirements = bridge_module.get_ai_policy_requirements
validate_ai_batch = bridge_module.validate_ai_batch


def test_validate_ai_decision_pass():
    """Test validating a compliant AI decision."""
    decision = {
        "confidence": 0.85,
        "explanation": "High confidence decision",
        "bias_score": 0.2,
    }

    assert validate_ai_decision(decision) is True


def test_validate_ai_decision_fail_confidence():
    """Test rejecting low confidence decision."""
    decision = {
        "confidence": 0.5,  # Below threshold
        "explanation": "Low confidence",
        "bias_score": 0.2,
    }

    assert validate_ai_decision(decision) is False


def test_validate_ai_decision_fail_bias():
    """Test rejecting high bias decision."""
    decision = {
        "confidence": 0.9,
        "explanation": "High bias decision",
        "bias_score": 0.5,  # Above threshold
    }

    assert validate_ai_decision(decision) is False


def test_validate_ai_decision_fail_missing_explanation():
    """Test rejecting decision without explanation."""
    decision = {
        "confidence": 0.9,
        "bias_score": 0.2,
        # Missing explanation
    }

    assert validate_ai_decision(decision) is False


def test_get_ai_policy_requirements():
    """Test retrieving policy requirements."""
    policy = get_ai_policy_requirements()

    assert "rules" in policy
    assert "description" in policy
    assert policy["rules"]["min_confidence"] == 0.7


def test_validate_ai_batch():
    """Test batch validation of decisions."""
    decisions = [
        {"confidence": 0.9, "explanation": "Good", "bias_score": 0.1},
        {"confidence": 0.5, "explanation": "Bad", "bias_score": 0.5},
        {"confidence": 0.8, "explanation": "Good", "bias_score": 0.2},
    ]

    result = validate_ai_batch(decisions)

    assert result["total"] == 3
    assert result["passed"] == 2
    assert result["failed"] == 1
    assert abs(result["pass_rate"] - 0.667) < 0.01


def test_validate_ai_batch_empty():
    """Test batch validation with empty list."""
    result = validate_ai_batch([])

    assert result["total"] == 0
    assert result["passed"] == 0
    assert result["failed"] == 0
    assert result["pass_rate"] == 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
