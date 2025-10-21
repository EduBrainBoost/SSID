#!/usr/bin/env python3
"""
PQC Compliance Registry Signature Verifier
============================================

Verifies the PQC signature of compliance_registry_signature.json.

Purpose:
  - Verify cryptographic signature of compliance state
  - Detect tampering of registry or signature
  - Validate quantum-resistant attestation
  - Provide audit trail verification

Verification Steps:
  1. Load compliance_registry_signature.json
  2. Reconstruct canonical message from payload
  3. Extract signature and public key
  4. Verify signature using PQC backend (Dilithium2)
  5. Report verification result

Security Properties:
  - Detects ANY modification to signed payload
  - Verifies quantum-resistant signature
  - Non-repudiable proof of compliance state
  - Timestamped verification audit trail

Exit Codes:
  0 - Signature valid
  1 - Signature invalid or verification failed
  2 - Configuration error (missing files, etc.)

Author: SSID Compliance Team
Version: 1.0.0
Date: 2025-10-17
"""

import sys
import json
import hashlib
import argparse
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Tuple, Optional

# Add parent directories to path for imports
REPO_ROOT = Path(__file__).resolve().parents[2]
PQC_DIR = REPO_ROOT / "21_post_quantum_crypto"
sys.path.insert(0, str(PQC_DIR))

# Import PQC backend
from pqc_backend import get_backend

# Paths
SIGNATURE_PATH = REPO_ROOT / "23_compliance" / "registry" / "compliance_registry_signature.json"
VERIFICATION_LOG = REPO_ROOT / "02_audit_logging" / "logs" / "pqc_signature_verification.jsonl"


def load_signature_document(signature_path: Path) -> Dict:
    """Load signature document."""
    if not signature_path.exists():
        print(f"ERROR: Signature file not found: {signature_path}", file=sys.stderr)
        print("Run: python 23_compliance/registry/sign_compliance_registry_pqc.py", file=sys.stderr)
        sys.exit(2)

    with open(signature_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def reconstruct_signed_message(signature_doc: Dict) -> bytes:
    """
    Reconstruct the exact message that was signed.

    The signer creates a canonical JSON representation of the payload,
    so we must reconstruct it identically.
    """
    payload = signature_doc["payload"]

    # Canonical JSON (sorted keys, no extra whitespace)
    canonical_json = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    message_bytes = canonical_json.encode('utf-8')

    return message_bytes


def verify_message_hash(signature_doc: Dict, message_bytes: bytes) -> Tuple[bool, str]:
    """Verify that reconstructed message matches stored hash."""
    calculated_hash = hashlib.sha256(message_bytes).hexdigest()
    stored_hash = signature_doc["message_hash"]

    if calculated_hash != stored_hash:
        return False, f"Hash mismatch: expected {stored_hash}, got {calculated_hash}"

    return True, calculated_hash


def extract_signature_and_key(signature_doc: Dict) -> Tuple[bytes, Dict]:
    """Extract signature bytes and public key data."""
    # Extract signature
    signature_hex = signature_doc["signature"]["signature_bytes"]
    signature = bytes.fromhex(signature_hex)

    # Extract public key data (keep as dict, not file)
    pub_key_data = signature_doc["public_key"]

    return signature, pub_key_data


def perform_verification(message: bytes, signature: bytes, pub_key_data: Dict) -> Tuple[bool, Dict]:
    """
    Perform PQC signature verification using public key data.

    For HMAC-based placeholder backend, we reconstruct the signature
    directly from the stored public key bytes.
    """
    backend = get_backend()

    # For placeholder-HMAC backend, verify using key bytes directly
    if backend.BACKEND_ID == "placeholder-hmac-sha256":
        try:
            # Extract public key bytes
            public_key_bytes = bytes.fromhex(pub_key_data["key_bytes"])

            # HMAC verification: In placeholder mode, the "public key" is actually
            # SHA256(private_key), so we need to reverse-engineer from the signature
            # For HMAC, verification requires the private key, which we don't have
            # from just the public key. So we reconstruct using the same deterministic
            # key generation.

            # Actually, we need to use the REAL key files if available
            # Fall back to loading from the actual key directory
            name = "compliance_registry"  # Hardcoded for compliance registry
            keys_dir = REPO_ROOT / "21_post_quantum_crypto" / "keys"
            pub_key_path = keys_dir / f"{name}.pub"
            priv_key_path = keys_dir / f"{name}.key"

            if priv_key_path.exists():
                # Recompute signature with private key
                expected_sig = backend.sign(message, priv_key_path)
                valid = (signature == expected_sig)
            else:
                # Cannot verify without private key in HMAC mode
                valid = False

        except Exception as e:
            valid = False
    else:
        # For real Dilithium2 backend, use standard verification
        # Create temp public key file
        temp_dir = REPO_ROOT / "23_compliance" / "registry" / ".temp_keys"
        temp_dir.mkdir(parents=True, exist_ok=True)
        temp_pub_key = temp_dir / "temp_verification.pub"

        with open(temp_pub_key, 'w', encoding='utf-8') as f:
            json.dump(pub_key_data, f, indent=2, ensure_ascii=False)

        try:
            valid = backend.verify(message, signature, temp_pub_key)
        finally:
            if temp_pub_key.exists():
                temp_pub_key.unlink()
            if temp_dir.exists() and not any(temp_dir.iterdir()):
                temp_dir.rmdir()

    verify_metadata = {
        "algorithm": backend.ALG_LABEL,
        "backend": backend.BACKEND_ID,
        "verified": valid,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    return valid, verify_metadata


def log_verification_result(signature_doc: Dict, valid: bool, verify_metadata: Dict,
                            message_hash: str, log_path: Path) -> None:
    """Log verification result to audit trail."""
    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "verification_type": "compliance_registry_pqc_signature",
        "signature_document": {
            "signed_at": signature_doc["signed_at"],
            "global_merkle_root": signature_doc["payload"]["global_merkle_root"],
            "algorithm": signature_doc["signature"]["algorithm"],
            "backend": signature_doc["signature"]["backend"]
        },
        "verification": {
            "valid": valid,
            "message_hash": message_hash,
            "algorithm": verify_metadata["algorithm"],
            "backend": verify_metadata["backend"],
            "verified_at": verify_metadata["timestamp"]
        },
        "result": "PASS" if valid else "FAIL"
    }

    # Append to log file (JSONL format)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    with open(log_path, 'a', encoding='utf-8') as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')


def display_verification_result(signature_doc: Dict, valid: bool, verify_metadata: Dict,
                                message_hash: str, verbose: bool = False) -> None:
    """Display verification result to console."""
    print("\n" + "="*80)
    print("PQC Compliance Registry Signature Verification")
    print("="*80)

    payload = signature_doc["payload"]

    print(f"\nSigned Payload:")
    print(f"  Global Merkle Root: {payload['global_merkle_root']}")
    print(f"  Compliance Score:   {payload['metadata']['compliance_score']:.1%}")
    print(f"  Total Rules:        {payload['metadata']['total_rules']}")
    print(f"  Registry Version:   {payload['metadata']['registry_version']}")
    print(f"  Generated At:       {payload['metadata']['generated_at']}")

    print(f"\nSignature Information:")
    print(f"  Algorithm:    {signature_doc['signature']['algorithm']}")
    print(f"  Backend:      {signature_doc['signature']['backend']}")
    print(f"  Signature Size: {signature_doc['signature']['signature_size']} bytes")
    print(f"  Signed At:    {signature_doc['signed_at']}")

    print(f"\nVerification:")
    print(f"  Message Hash: {message_hash}")
    print(f"  Algorithm:    {verify_metadata['algorithm']}")
    print(f"  Backend:      {verify_metadata['backend']}")
    print(f"  Verified At:  {verify_metadata['timestamp']}")

    if verbose:
        print(f"\nStandard Merkle Roots:")
        for standard, root in payload["standard_merkle_roots"].items():
            print(f"  {standard:20s}: {root}")

    print("\n" + "="*80)

    if valid:
        print("RESULT: [VALID] SIGNATURE VALID")
        print("="*80)
        print("\nThe compliance registry signature is cryptographically valid.")
        print("The signed payload has NOT been tampered with.")
        print(f"Global Merkle Root: {payload['global_merkle_root']}")
    else:
        print("RESULT: [INVALID] SIGNATURE INVALID")
        print("="*80)
        print("\nWARNING: Signature verification FAILED!")
        print("The compliance registry may have been tampered with.")
        print("DO NOT TRUST this compliance attestation.")

    print("="*80 + "\n")


def compare_with_current_registry(signature_doc: Dict, registry_path: Path) -> Optional[Dict]:
    """
    Compare signed registry state with current registry.

    Returns comparison result or None if registry not found.
    """
    if not registry_path.exists():
        return None

    with open(registry_path, 'r', encoding='utf-8') as f:
        current_registry = json.load(f)

    signed_root = signature_doc["payload"]["global_merkle_root"]
    current_root = current_registry["verification"]["global_merkle_root"]

    comparison = {
        "signed_global_merkle_root": signed_root,
        "current_global_merkle_root": current_root,
        "roots_match": signed_root == current_root,
        "signed_at": signature_doc["signed_at"],
        "current_generated_at": current_registry["metadata"]["generated_at"]
    }

    return comparison


def display_registry_comparison(comparison: Optional[Dict]) -> None:
    """Display comparison with current registry."""
    if comparison is None:
        print("\nNote: Current compliance_registry.json not found - cannot compare.")
        return

    print("\nComparison with Current Registry:")
    print("-" * 80)

    if comparison["roots_match"]:
        print("[OK] Signed registry matches current registry")
        print(f"  Global Merkle Root: {comparison['signed_global_merkle_root']}")
    else:
        print("[WARNING] Registry has been modified since signature")
        print(f"  Signed Root:   {comparison['signed_global_merkle_root']}")
        print(f"  Current Root:  {comparison['current_global_merkle_root']}")
        print(f"  Signed At:     {comparison['signed_at']}")
        print(f"  Current State: {comparison['current_generated_at']}")
        print("\n  This is EXPECTED if the registry was regenerated.")
        print("  Consider generating a new signature for the current state.")

    print("-" * 80)


def main():
    parser = argparse.ArgumentParser(
        description="Verify PQC signature of compliance registry",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Verify signature
  python verify_pqc_signature.py

  # Verbose output
  python verify_pqc_signature.py --verbose

  # Custom paths
  python verify_pqc_signature.py --signature ./custom_sig.json

  # Skip logging
  python verify_pqc_signature.py --no-log
        """
    )

    parser.add_argument("--signature", "-s", type=Path, default=SIGNATURE_PATH,
                        help="Path to signature JSON file")
    parser.add_argument("--registry", type=Path,
                        default=REPO_ROOT / "23_compliance" / "registry" / "compliance_registry.json",
                        help="Path to current registry (for comparison)")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Verbose output")
    parser.add_argument("--no-log", action="store_true",
                        help="Skip audit logging")
    parser.add_argument("--json", action="store_true",
                        help="JSON output")

    args = parser.parse_args()

    if not args.json:
        print("="*80)
        print("PQC Compliance Registry Signature Verifier")
        print("="*80)
        print(f"Signature File: {args.signature}")

    # Load signature document
    if not args.json:
        print("\n[1/6] Loading signature document...")
    signature_doc = load_signature_document(args.signature)

    if not args.json:
        print(f"      Signature type: {signature_doc['signature_type']}")
        print(f"      Signed at: {signature_doc['signed_at']}")

    # Reconstruct signed message
    if not args.json:
        print("\n[2/6] Reconstructing signed message...")
    message_bytes = reconstruct_signed_message(signature_doc)

    # Verify message hash
    if not args.json:
        print("\n[3/6] Verifying message hash...")
    hash_valid, message_hash = verify_message_hash(signature_doc, message_bytes)

    if not hash_valid:
        print(f"ERROR: {message_hash}", file=sys.stderr)
        sys.exit(1)

    if not args.json:
        print(f"      Message hash: {message_hash} [OK]")

    # Extract signature and key
    if not args.json:
        print("\n[4/6] Extracting signature and public key...")
    signature, pub_key_data = extract_signature_and_key(signature_doc)

    if not args.json:
        print(f"      Signature size: {len(signature)} bytes")
        print(f"      Algorithm: {signature_doc['signature']['algorithm']}")

    # Perform verification
    if not args.json:
        print("\n[5/6] Verifying PQC signature...")

    valid, verify_metadata = perform_verification(message_bytes, signature, pub_key_data)

    # Log result
    if not args.no_log and not args.json:
        print("\n[6/6] Logging verification result...")
        log_verification_result(signature_doc, valid, verify_metadata, message_hash, VERIFICATION_LOG)
        print(f"      Log: {VERIFICATION_LOG.relative_to(REPO_ROOT)}")
    elif not args.json:
        print("\n[6/6] Skipping audit log (--no-log)")

    # Output results
    if args.json:
        # JSON output
        comparison = compare_with_current_registry(signature_doc, args.registry)
        output = {
            "valid": valid,
            "signature_document": {
                "signed_at": signature_doc["signed_at"],
                "global_merkle_root": signature_doc["payload"]["global_merkle_root"],
                "compliance_score": signature_doc["payload"]["metadata"]["compliance_score"],
                "algorithm": signature_doc["signature"]["algorithm"],
                "backend": signature_doc["signature"]["backend"]
            },
            "verification": verify_metadata,
            "message_hash": message_hash
        }

        if comparison:
            output["registry_comparison"] = comparison

        print(json.dumps(output, indent=2))
    else:
        # Human-readable output
        display_verification_result(signature_doc, valid, verify_metadata, message_hash, args.verbose)

        # Compare with current registry
        comparison = compare_with_current_registry(signature_doc, args.registry)
        display_registry_comparison(comparison)

    # Exit code
    return 0 if valid else 1


if __name__ == "__main__":
    sys.exit(main())
