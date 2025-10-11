#!/usr/bin/env python3
"""Bridge: 10_interoperability -> 09_meta_identity - DID Resolver"""

from typing import Dict, Optional


def resolve_external_did(did: str) -> Dict:
    """
    Resolve Decentralized Identifier (DID) using internal resolver.

    Args:
        did: DID string (e.g., "did:ssid:123abc")

    Returns:
        Dict with DID document or error
    """
    # Validate DID format
    if not did or not isinstance(did, str):
        return {"error": "Invalid DID format", "did": did}

    if not did.startswith("did:"):
        return {"error": "DID must start with 'did:'", "did": did}

    parts = did.split(":")
    if len(parts) < 3:
        return {"error": "Invalid DID structure", "did": did}

    method = parts[1]
    identifier = parts[2]

    # Mock resolution (would call 09_meta_identity in production)
    return {
        "did": did,
        "method": method,
        "identifier": identifier,
        "document": {
            "@context": "https://www.w3.org/ns/did/v1",
            "id": did,
            "verificationMethod": [],
            "authentication": [],
            "service": []
        },
        "metadata": {
            "resolved": True,
            "resolver": "ssid_meta_identity_bridge"
        }
    }


def validate_did_format(did: str) -> bool:
    """Validate DID format according to W3C spec"""
    if not did or not isinstance(did, str):
        return False

    if not did.startswith("did:"):
        return False

    parts = did.split(":")
    return len(parts) >= 3


if __name__ == "__main__":
    test_did = "did:ssid:abc123"
    print("DID Resolution:", resolve_external_did(test_did))
    print("Valid Format:", validate_did_format(test_did))
