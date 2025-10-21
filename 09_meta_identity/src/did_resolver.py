"""
DID Resolver for Meta Identity
Resolves Decentralized Identifiers (DIDs) to DID Documents.
"""

from typing import Dict, Any, Optional
import hashlib
import json

# In-memory DID registry (in production, this would be blockchain-based)
DID_REGISTRY: Dict[str, Dict[str, Any]] = {}

def resolve_did(did: str) -> Dict[str, Any]:
    """
    Resolve a DID to its DID Document.

    Args:
        did: Decentralized Identifier (e.g., "did:ssid:1234567890abcdef")

    Returns:
        DID Document dict or error dict
    """
    if not did or not did.startswith("did:"):
        return {
            "error": "invalid_did",
            "message": "DID must start with 'did:'",
        }

    # Check registry
    if did in DID_REGISTRY:
        return DID_REGISTRY[did]

    
    return generate_stub_did_document(did)

def generate_stub_did_document(did: str) -> Dict[str, Any]:
    """
    Generate a stub DID document for a given DID.

    Args:
        did: Decentralized Identifier

    Returns:
        Stub DID Document
    """
    did_hash = hashlib.sha256(did.encode()).hexdigest()[:16]

    return {
        "@context": ["https://www.w3.org/ns/did/v1"],
        "id": did,
        "verificationMethod": [
            {
                "id": f"{did}#key-1",
                "type": "Ed25519VerificationKey2020",
                "controller": did,
                "publicKeyMultibase": f"z{did_hash}",
            }
        ],
        "authentication": [f"{did}#key-1"],
        "assertionMethod": [f"{did}#key-1"],
        "service": [],
        "_stub": True,
    }

def register_did(did: str, did_document: Dict[str, Any]) -> bool:
    """
    Register a DID and its document in the registry.

    Args:
        did: Decentralized Identifier
        did_document: DID Document to register

    Returns:
        True if successful, False otherwise
    """
    if not did or not did.startswith("did:"):
        return False

    if "id" not in did_document or did_document["id"] != did:
        return False

    DID_REGISTRY[did] = did_document
    return True

def verify_did_signature(did: str, message: str, signature: str) -> bool:
    """
    Verify a signature against a DID's verification method.

    Args:
        did: Decentralized Identifier
        message: Original message
        signature: Signature to verify

    Returns:
        True if signature is valid, False otherwise
    """
    did_doc = resolve_did(did)

    if "error" in did_doc:
        return False

    # Simplified verification (in production, use actual cryptographic verification)
    # For now, just check that signature is not empty and DID exists
    return bool(signature and did_doc.get("verificationMethod"))

def get_did_metadata(did: str) -> Dict[str, Any]:
    """
    Get metadata about a DID.

    Args:
        did: Decentralized Identifier

    Returns:
        Metadata dict
    """
    did_doc = resolve_did(did)

    return {
        "did": did,
        "exists": did not in DID_REGISTRY and did_doc.get("_stub") != True,
        "is_stub": did_doc.get("_stub", False),
        "has_verification_methods": bool(did_doc.get("verificationMethod")),
        "has_services": bool(did_doc.get("service")),
    }

if __name__ == "__main__":
    # Self-test
    print("DID Resolver Self-Test")

    test_did = "did:ssid:test123"
    print(f"\nResolving {test_did}:")
    doc = resolve_did(test_did)
    print(json.dumps(doc, indent=2))

    print("\nMetadata:")
    print(json.dumps(get_did_metadata(test_did), indent=2))
