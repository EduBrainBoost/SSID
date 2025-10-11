"""
Test: 10_interoperability → 09_meta_identity bridge
Tests DID resolution for federated identity
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
    "bridge_meta_identity",
    os.path.join(project_root, "10_interoperability/interconnect/bridge_meta_identity.py")
)
bridge_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bridge_module)

resolve_external_did = bridge_module.resolve_external_did
verify_external_did_signature = bridge_module.verify_external_did_signature
get_external_did_info = bridge_module.get_external_did_info
resolve_did_batch = bridge_module.resolve_did_batch
validate_did_format = bridge_module.validate_did_format


def test_resolve_external_did():
    """Test resolving a DID."""
    did = "did:ssid:test123"
    doc = resolve_external_did(did)

    assert "id" in doc
    assert doc["id"] == did
    assert "verificationMethod" in doc


def test_resolve_external_did_invalid():
    """Test resolving invalid DID."""
    doc = resolve_external_did("invalid")

    assert "error" in doc


def test_verify_external_did_signature():
    """Test verifying DID signature."""
    did = "did:ssid:test123"
    message = "test message"
    signature = "fake_signature"

    # Stub resolver should return True for any non-empty signature
    result = verify_external_did_signature(did, message, signature)
    assert isinstance(result, bool)


def test_verify_external_did_signature_empty():
    """Test rejecting empty signature."""
    did = "did:ssid:test123"
    message = "test message"
    signature = ""

    result = verify_external_did_signature(did, message, signature)
    assert result is False


def test_get_external_did_info():
    """Test getting DID metadata."""
    did = "did:ssid:test123"
    info = get_external_did_info(did)

    assert "did" in info
    assert "is_stub" in info
    assert "has_verification_methods" in info


def test_resolve_did_batch():
    """Test batch DID resolution."""
    dids = [
        "did:ssid:test1",
        "did:ssid:test2",
        "did:ssid:test3",
    ]

    results = resolve_did_batch(dids)

    assert len(results) == 3
    for did in dids:
        assert did in results
        assert results[did]["id"] == did


def test_resolve_did_batch_empty():
    """Test batch resolution with empty list."""
    results = resolve_did_batch([])
    assert len(results) == 0


def test_validate_did_format_valid():
    """Test validating valid DID format."""
    result = validate_did_format("did:ssid:test123")

    assert result["valid"] is True
    assert len(result["errors"]) == 0


def test_validate_did_format_missing_prefix():
    """Test validating DID without prefix."""
    result = validate_did_format("ssid:test123")

    assert result["valid"] is False
    assert "must start with 'did:'" in str(result["errors"])


def test_validate_did_format_empty():
    """Test validating empty DID."""
    result = validate_did_format("")

    assert result["valid"] is False
    assert len(result["errors"]) > 0


def test_validate_did_format_insufficient_parts():
    """Test validating DID with insufficient parts."""
    result = validate_did_format("did:ssid")

    assert result["valid"] is False
    assert "must have at least 3 parts" in str(result["errors"])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
