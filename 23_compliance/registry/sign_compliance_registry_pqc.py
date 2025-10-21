#!/usr/bin/env python3
"""
PQC Compliance Registry Signer
================================

Signs the global Merkle root from compliance_registry.json using
post-quantum cryptography (Dilithium2).

Purpose:
  - Create cryptographically-verifiable signature of compliance state
  - Enable tamper-proof compliance attestation
  - Support quantum-resistant verification
  - Generate immutable proof chain

Architecture:
  1. Load compliance_registry.json
  2. Extract global Merkle root
  3. Sign with PQC private key (Dilithium2)
  4. Generate compliance_registry_signature.json
  5. Store signature in WORM storage

Output Format:
  - compliance_registry_signature.json: Signature + metadata
  - WORM snapshot: Immutable record

Security Properties:
  - Quantum-resistant signature (Dilithium2)
  - Tamper detection via Merkle root
  - Non-repudiable attestation
  - Timestamped proof chain

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
from typing import Dict, Optional

# Add parent directories to path for imports
REPO_ROOT = Path(__file__).resolve().parents[2]
PQC_DIR = REPO_ROOT / "21_post_quantum_crypto"
sys.path.insert(0, str(PQC_DIR))

# Import PQC backend
from pqc_backend import get_backend, sign_message

# Paths
REGISTRY_PATH = REPO_ROOT / "23_compliance" / "registry" / "compliance_registry.json"
SIGNATURE_OUTPUT = REPO_ROOT / "23_compliance" / "registry" / "compliance_registry_signature.json"
KEYS_DIR = REPO_ROOT / "21_post_quantum_crypto" / "keys"
WORM_STORAGE = REPO_ROOT / "02_audit_logging" / "storage" / "worm" / "immutable_store"


def load_registry() -> Dict:
    """Load compliance registry."""
    if not REGISTRY_PATH.exists():
        print(f"ERROR: Registry not found: {REGISTRY_PATH}", file=sys.stderr)
        print("Run: python 23_compliance/registry/generate_compliance_registry.py", file=sys.stderr)
        sys.exit(1)

    with open(REGISTRY_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def ensure_keypair_exists(keys_dir: Path) -> tuple[Path, Path]:
    """Ensure compliance registry keypair exists, generate if missing."""
    pub_path = keys_dir / "compliance_registry.pub"
    priv_path = keys_dir / "compliance_registry.key"

    if pub_path.exists() and priv_path.exists():
        print(f"Using existing keypair: {pub_path.name}, {priv_path.name}")
        return pub_path, priv_path

    # Generate new keypair
    print("Generating new PQC keypair for compliance registry...")
    backend = get_backend()
    pub_path, priv_path = backend.generate_keypair("compliance_registry", keys_dir)

    print(f"Generated keypair:")
    print(f"  Public:  {pub_path}")
    print(f"  Private: {priv_path}")
    print(f"  Algorithm: {backend.ALG_LABEL}")
    print(f"  Backend: {backend.BACKEND_ID}")

    return pub_path, priv_path


def create_signature_payload(registry: Dict) -> Dict:
    """Create payload to be signed."""
    return {
        "global_merkle_root": registry["verification"]["global_merkle_root"],
        "metadata": {
            "total_rules": registry["metadata"]["total_rules"],
            "total_manifestations": registry["metadata"]["total_manifestations"],
            "compliance_score": registry["metadata"]["compliance_score"],
            "generated_at": registry["metadata"]["generated_at"],
            "registry_version": registry["metadata"]["version"]
        },
        "standard_merkle_roots": registry["merkle_roots"]
    }


def sign_registry(registry: Dict, private_key_path: Path, public_key_path: Path) -> Dict:
    """Sign the compliance registry's global Merkle root."""

    # Create signing payload
    payload = create_signature_payload(registry)

    # Canonical JSON for signing (deterministic serialization)
    canonical_json = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    message_bytes = canonical_json.encode('utf-8')

    # Calculate message hash for reference
    message_hash = hashlib.sha256(message_bytes).hexdigest()

    print(f"\nSigning payload:")
    print(f"  Global Merkle Root: {payload['global_merkle_root']}")
    print(f"  Total Rules: {payload['metadata']['total_rules']}")
    print(f"  Compliance Score: {payload['metadata']['compliance_score']:.1%}")
    print(f"  Message Hash: {message_hash}")

    # Sign message
    signature, sign_metadata = sign_message(message_bytes, private_key_path)

    print(f"\nSignature generated:")
    print(f"  Algorithm: {sign_metadata['alg_label']}")
    print(f"  Backend: {sign_metadata['backend']}")
    print(f"  Signature Size: {sign_metadata['signature_bytes']} bytes")
    print(f"  Timestamp: {sign_metadata['timestamp']}")

    # Load public key for embedding
    pub_data = json.loads(public_key_path.read_text(encoding="utf-8"))

    # Create signature document
    signature_doc = {
        "version": "1.0.0",
        "signature_type": "compliance_registry_pqc",
        "signed_at": datetime.now(timezone.utc).isoformat(),
        "payload": payload,
        "message_hash": message_hash,
        "signature": {
            "algorithm": sign_metadata['alg_label'],
            "backend": sign_metadata['backend'],
            "signature_bytes": signature.hex(),
            "signature_size": len(signature),
            "created_at": sign_metadata['timestamp']
        },
        "public_key": {
            "algorithm": pub_data['alg_label'],
            "backend": pub_data['backend'],
            "key_bytes": pub_data['key_bytes'],
            "key_type": pub_data['key_type'],
            "created_at": pub_data['created_at']
        },
        "verification": {
            "can_verify_with": "python 23_compliance/registry/verify_pqc_signature.py",
            "public_key_path": str(public_key_path.relative_to(REPO_ROOT)),
            "registry_path": "23_compliance/registry/compliance_registry.json"
        }
    }

    return signature_doc


def save_signature(signature_doc: Dict, output_path: Path) -> None:
    """Save signature document to file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(signature_doc, f, indent=2, ensure_ascii=False)

    print(f"\nSignature saved to: {output_path}")


def save_to_worm(signature_doc: Dict, worm_dir: Path) -> Path:
    """Save signature to WORM storage for immutability."""
    worm_dir.mkdir(parents=True, exist_ok=True)

    # Generate WORM snapshot ID
    timestamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    merkle_root = signature_doc['payload']['global_merkle_root']
    snapshot_id = hashlib.sha256(f"{timestamp}_{merkle_root}".encode()).hexdigest()[:16]

    worm_snapshot = {
        "snapshot_id": f"compliance_signature_{timestamp}_{snapshot_id}",
        "timestamp": signature_doc["signed_at"],
        "immutable": True,
        "type": "compliance_registry_pqc_signature",
        "signature_document": signature_doc
    }

    snapshot_file = worm_dir / f"{worm_snapshot['snapshot_id']}.json"

    with open(snapshot_file, 'w', encoding='utf-8') as f:
        json.dump(worm_snapshot, f, indent=2, ensure_ascii=False)

    print(f"WORM snapshot saved: {snapshot_file.name}")

    return snapshot_file


def display_summary(signature_doc: Dict, worm_file: Path, signature_output: Path) -> None:
    """Display signature summary."""
    print("\n" + "="*80)
    print("PQC Compliance Registry Signature - Summary")
    print("="*80)
    print(f"Global Merkle Root: {signature_doc['payload']['global_merkle_root']}")
    print(f"Compliance Score:   {signature_doc['payload']['metadata']['compliance_score']:.1%}")
    print(f"Total Rules:        {signature_doc['payload']['metadata']['total_rules']}")
    print(f"Algorithm:          {signature_doc['signature']['algorithm']}")
    print(f"Backend:            {signature_doc['signature']['backend']}")
    print(f"Signature Size:     {signature_doc['signature']['signature_size']} bytes")
    print(f"Signed At:          {signature_doc['signed_at']}")
    print(f"\nOutputs:")
    print(f"  Signature File: {signature_output.relative_to(REPO_ROOT)}")
    if worm_file.exists():
        print(f"  WORM Snapshot:  {worm_file.relative_to(REPO_ROOT)}")
    else:
        print(f"  WORM Snapshot:  (skipped)")
    print(f"\nVerification:")
    print(f"  Command: python 23_compliance/registry/verify_pqc_signature.py")
    print("="*80)


def main():
    parser = argparse.ArgumentParser(
        description="Sign compliance registry with PQC signature",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Sign with automatic keypair generation
  python sign_compliance_registry_pqc.py

  # Specify custom paths
  python sign_compliance_registry_pqc.py --keys-dir ./custom_keys --output ./custom_sig.json

  # Skip WORM storage
  python sign_compliance_registry_pqc.py --no-worm
        """
    )

    parser.add_argument("--keys-dir", type=Path, default=KEYS_DIR,
                        help="Directory for PQC keys (default: 21_post_quantum_crypto/keys)")
    parser.add_argument("--output", "-o", type=Path, default=SIGNATURE_OUTPUT,
                        help="Output path for signature JSON")
    parser.add_argument("--no-worm", action="store_true",
                        help="Skip WORM storage")
    parser.add_argument("--registry", type=Path, default=REGISTRY_PATH,
                        help="Path to compliance registry JSON")

    args = parser.parse_args()

    # Use custom paths if provided
    registry_path = args.registry
    signature_output = args.output

    print("="*80)
    print("PQC Compliance Registry Signer")
    print("="*80)
    print(f"Registry: {registry_path}")
    print(f"Keys Dir: {args.keys_dir}")
    print(f"Output:   {signature_output}")

    # Load registry (update function to use parameter)
    print("\n[1/5] Loading compliance registry...")
    if not registry_path.exists():
        print(f"ERROR: Registry not found: {registry_path}", file=sys.stderr)
        print("Run: python 23_compliance/registry/generate_compliance_registry.py", file=sys.stderr)
        sys.exit(1)

    with open(registry_path, 'r', encoding='utf-8') as f:
        registry = json.load(f)

    print(f"      Registry version: {registry['metadata']['version']}")
    print(f"      Generated at: {registry['metadata']['generated_at']}")
    print(f"      Global Merkle root: {registry['verification']['global_merkle_root']}")

    # Ensure keypair exists
    print("\n[2/5] Ensuring PQC keypair exists...")
    pub_path, priv_path = ensure_keypair_exists(args.keys_dir)

    # Sign registry
    print("\n[3/5] Signing compliance registry...")
    signature_doc = sign_registry(registry, priv_path, pub_path)

    # Save signature
    print("\n[4/5] Saving signature document...")
    save_signature(signature_doc, signature_output)

    # Save to WORM
    worm_file = None
    if not args.no_worm:
        print("\n[5/5] Saving to WORM storage...")
        worm_file = save_to_worm(signature_doc, WORM_STORAGE)
    else:
        print("\n[5/5] Skipping WORM storage (--no-worm)")

    # Display summary
    if worm_file:
        display_summary(signature_doc, worm_file, signature_output)
    else:
        # Create dummy path for display
        worm_file = Path("__WORM_SKIPPED__")
        display_summary(signature_doc, worm_file, signature_output)

    print("\n[OK] Signature generation complete!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
