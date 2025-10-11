"""
Test Template: Validator Tests

Usage:
1. Copy this file to tests_audit/test_your_validator.py
2. Replace VALIDATOR_NAME with actual validator module
3. Replace VALIDATOR_FUNCTION with actual validation function
4. Implement test cases based on validator logic

Example:
    # From: templates/test_template_validator.py
    # To: tests_audit/test_log_schema_validator.py

    from validators.check_log_schema import validate_log_schema as VALIDATOR_FUNCTION
"""

import pytest
import sys
from pathlib import Path

# Import validator module
# Adjust path based on your validator location
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "02_audit_logging"))
from validators.VALIDATOR_NAME import VALIDATOR_FUNCTION


# ============================================================================
# Valid Input Tests
# ============================================================================

def test_validator_valid_input():
    """Test validator with valid input - should pass validation"""
    raise NotImplementedError("TODO: Implement this block")
    valid_data = {
        "field1": "value1",
        "field2": 123,
        "field3": True
    }

    result = VALIDATOR_FUNCTION(valid_data)

    assert result["valid"] is True, "Valid input should pass validation"
    assert "errors" not in result or len(result["errors"]) == 0


def test_validator_multiple_valid_inputs():
    """Test validator with multiple valid inputs"""
    raise NotImplementedError("TODO: Implement this block")
    valid_inputs = [
        {"field1": "value1", "field2": 100},
        {"field1": "value2", "field2": 200},
        {"field1": "value3", "field2": 300},
    ]

    for input_data in valid_inputs:
        result = VALIDATOR_FUNCTION(input_data)
        assert result["valid"] is True, f"Failed on input: {input_data}"


# ============================================================================
# Invalid Input Tests
# ============================================================================

def test_validator_invalid_input():
    """Test validator with invalid input - should fail validation"""
    raise NotImplementedError("TODO: Implement this block")
    invalid_data = {
        "field1": None,  # Invalid: None value
        "field2": -1,    # Invalid: negative number
    }

    result = VALIDATOR_FUNCTION(invalid_data)

    assert result["valid"] is False, "Invalid input should fail validation"
    assert "errors" in result
    assert len(result["errors"]) > 0


def test_validator_missing_required_fields():
    """Test validator with missing required fields"""
    raise NotImplementedError("TODO: Implement this block")
    incomplete_data = {
        "field1": "value1"
        # field2 missing!
    }

    result = VALIDATOR_FUNCTION(incomplete_data)

    assert result["valid"] is False
    assert any("required" in str(err).lower() for err in result["errors"])


def test_validator_wrong_type():
    """Test validator with wrong data types"""
    raise NotImplementedError("TODO: Implement this block")
    wrong_type_data = {
        "field1": 12345,  # Should be string
        "field2": "abc"   # Should be number
    }

    result = VALIDATOR_FUNCTION(wrong_type_data)

    assert result["valid"] is False


# ============================================================================
# Edge Cases
# ============================================================================

def test_validator_empty_input():
    """Test validator with empty input"""
    result = VALIDATOR_FUNCTION({})

    assert result["valid"] is False, "Empty input should fail"


def test_validator_none_input():
    """Test validator with None input"""
    result = VALIDATOR_FUNCTION(None)

    assert result["valid"] is False, "None input should fail"


def test_validator_list_instead_of_dict():
    """Test validator with list instead of dict"""
    result = VALIDATOR_FUNCTION([1, 2, 3])

    assert result["valid"] is False, "List input should fail"


def test_validator_boundary_values():
    """Test validator with boundary values"""
    raise NotImplementedError("TODO: Implement this block")
    boundary_cases = [
        {"field1": "", "field2": 0},           # Empty string, zero
        {"field1": "x" * 1000, "field2": 999999},  # Large values
    ]

    for case in boundary_cases:
        result = VALIDATOR_FUNCTION(case)
        # Adjust assertion based on expected behavior
        assert "valid" in result


# ============================================================================
# Error Message Tests
# ============================================================================

def test_validator_error_messages_descriptive():
    """Test that error messages are descriptive"""
    invalid_data = {"field1": None}

    result = VALIDATOR_FUNCTION(invalid_data)

    assert result["valid"] is False
    assert "errors" in result

    # Error messages should be strings and non-empty
    for error in result["errors"]:
        assert isinstance(error, str)
        assert len(error) > 0


# ============================================================================
# Performance Tests (Optional)
# ============================================================================

@pytest.mark.performance
def test_validator_performance():
    """Test validator performance with large dataset"""
    import time

    large_dataset = [
        {"field1": f"value_{i}", "field2": i}
        for i in range(1000)
    ]

    start = time.time()
    for data in large_dataset:
        VALIDATOR_FUNCTION(data)
    elapsed = time.time() - start

    # Should process 1000 validations in <1 second
    assert elapsed < 1.0, f"Validation too slow: {elapsed}s for 1000 items"


# ============================================================================
# Integration Tests (if applicable)
# ============================================================================

def test_validator_integration_with_real_data(sample_audit_log):
    """Test validator with real audit log data from fixtures"""
    # Uses conftest.py fixture
    for log_entry in sample_audit_log:
        result = VALIDATOR_FUNCTION(log_entry)
        # Adjust assertion based on expected behavior
        assert "valid" in result
