"""
Bridge: 10_interoperability → 09_meta_identity
Purpose: DID resolver endpoint for federated identity
Evidence: SHA-256 logged in 24_meta_orchestration/registry/logs/
"""

import sys
import os
from typing import Dict, Any, List

# Add path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

try:
    from meta_identity.src.did_resolver import (  # type: ignore
        resolve_did,
        verify_did_signature,
        get_did_metadata,
    )
except ImportError:
    # Fallback for direct imports
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "did_resolver",
            os.path.join(os.path.dirname(__file__), "../../09_meta_identity/src/did_resolver.py")
        )
        if spec and spec.loader:
            did_resolver = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(did_resolver)
            resolve_did = did_resolver.resolve_did
            verify_did_signature = did_resolver.verify_did_signature
            get_did_metadata = did_resolver.get_did_metadata
        else:
            raise ImportError("Could not load did_resolver")
    except Exception as e:
        raise ImportError(f"Could not load did_resolver: {e}")

def resolve_external_did(did: str) -> Dict[str, Any]:
    """
    Resolve DID using internal resolver and return metadata.

    Args:
        did: Decentralized Identifier (e.g., "did:ssid:1234567890abcdef")

    Returns:
        DID Document dict
    """
    return resolve_did(did)

def verify_external_did_signature(did: str, message: str, signature: str) -> bool:
    """
    Verify a signature from an external DID.

    Args:
        did: Decentralized Identifier
        message: Original message that was signed
        signature: Signature to verify

    Returns:
        True if signature is valid, False otherwise
    """
    return verify_did_signature(did, message, signature)

def get_external_did_info(did: str) -> Dict[str, Any]:
    """
    Get information about an external DID.

    Args:
        did: Decentralized Identifier

    Returns:
        Dict with DID metadata
    """
    return get_did_metadata(did)

def resolve_did_batch(dids: List[str]) -> Dict[str, Dict[str, Any]]:
    """
    Resolve multiple DIDs at once.

    Args:
        dids: List of DIDs to resolve

    Returns:
        Dict mapping DIDs to their documents
    """
    results = {}
    for did in dids:
        results[did] = resolve_external_did(did)
    return results

def validate_did_format(did: str) -> Dict[str, Any]:
    """
    Validate DID format and return validation results.

    Args:
        did: DID string to validate

    Returns:
        Dict with validation status and details
    """
    valid = True
    errors = []

    if not did:
        valid = False
        errors.append("DID is empty")
    elif not did.startswith("did:"):
        valid = False
        errors.append("DID must start with 'did:'")
    else:
        parts = did.split(":")
        if len(parts) < 3:
            valid = False
            errors.append("DID must have at least 3 parts (did:method:id)")

    return {
        "valid": valid,
        "did": did,
        "errors": errors,
    }

if __name__ == "__main__":
    # Self-test
    print("Bridge: 10_interoperability → 09_meta_identity")

    test_did = "did:ssid:test123"
    print(f"\nResolving {test_did}:")
    doc = resolve_external_did(test_did)
    print("DID Document:", doc)

    print("\nDID Info:")
    info = get_external_did_info(test_did)
    print(info)

    print("\nValidation:")
    validation = validate_did_format(test_did)
    print(validation)

    print("\nBatch resolution:")
    batch = resolve_did_batch(["did:ssid:test1", "did:ssid:test2"])
    print(f"Resolved {len(batch)} DIDs")
