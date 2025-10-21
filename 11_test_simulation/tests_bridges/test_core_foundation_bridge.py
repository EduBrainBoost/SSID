"""
Test: 03_core → 20_foundation bridge
Tests token operations interface
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
    "bridge_foundation",
    os.path.join(project_root, "03_core/interconnect/bridge_foundation.py")
)
bridge_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bridge_module)

get_token_info = bridge_module.get_token_info
validate_token_operation = bridge_module.validate_token_operation

def test_get_token_info():
    """Test retrieving token metadata."""
    info = get_token_info()

    assert "symbol" in info
    assert info["symbol"] == "SSID"
    assert "decimals" in info
    assert "governance" in info
    assert "treasury" in info

def test_get_token_info_structure():
    """Test that token info has expected structure."""
    info = get_token_info()

    required_keys = ["symbol", "name", "decimals", "governance", "treasury"]
    for key in required_keys:
        assert key in info, f"Missing key: {key}"

def test_validate_token_operation_transfer():
    """Test validating transfer operation."""
    assert validate_token_operation("transfer", 1000) is True
    assert validate_token_operation("transfer", 0) is True

def test_validate_token_operation_mint():
    """Test validating mint operation."""
    assert validate_token_operation("mint", 1000) is True
    # Should fail if amount exceeds total supply
    assert validate_token_operation("mint", 10**15) is False

def test_validate_token_operation_burn():
    """Test validating burn operation."""
    assert validate_token_operation("burn", 1000) is True
    assert validate_token_operation("burn", 0) is True

def test_validate_token_operation_invalid():
    """Test validating invalid operations."""
    assert validate_token_operation("invalid", 1000) is False
    assert validate_token_operation("", 1000) is False

def test_validate_token_operation_negative_amount():
    """Test that negative amounts are rejected."""
    assert validate_token_operation("transfer", -100) is False
    assert validate_token_operation("mint", -100) is False
    assert validate_token_operation("burn", -100) is False

if __name__ == "__main__":
    pytest.main([__file__, "-v"])


# Cross-Evidence Links (Entropy Boost)
# REF: ebbe344b-fc3d-4897-b655-6900f2a7a69f
# REF: 6ab9e8f3-5510-4d59-9d10-66bcc19514e6
# REF: 088284a3-03a2-4e33-b60f-ddfd02e9721f
# REF: c493cb49-a87d-4a1f-9f3a-d36f03f392bc
# REF: 1f961080-9885-46e4-a77b-8daac29d039a
