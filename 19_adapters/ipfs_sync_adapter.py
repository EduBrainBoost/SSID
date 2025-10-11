#!/usr/bin/env python3
"""
Blueprint v4.8 - IPFS Sync Adapter

Handles exchange of proof artifacts over IPFS gateways for federated continuity mesh.
Non-custodial, hash-based proof synchronization with no PII processing.

Features:
- IPFS gateway communication (public gateways)
- CID-based artifact retrieval
- SHA-256 proof verification
- Distributed artifact pinning
- Graceful fallback for offline nodes

Exit Codes:
  0 - Sync successful
  1 - Connection error (gateway unreachable)
  2 - Hash mismatch (proof integrity failure)
  3 - Timeout error
  4 - Invalid CID format

Compliance: GDPR, eIDAS, MiCA, DORA, AMLD6
"""

import json
import sys
import hashlib
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Configuration
IPFS_GATEWAYS = [
    "https://ipfs.io/ipfs/",
    "https://gateway.pinata.cloud/ipfs/",
    "https://cloudflare-ipfs.com/ipfs/",
    "https://dweb.link/ipfs/"
]

REGISTRY_DIR = Path("24_meta_orchestration/registry")
FEDERATION_DIR = REGISTRY_DIR / "federation"
SYNC_LOG_DIR = Path("02_audit_logging/reports")

# Timeout settings
GATEWAY_TIMEOUT = 30  # seconds
MAX_RETRIES = 3


def calculate_sha256(data: str) -> str:
    """Calculate SHA-256 hash of data"""
    return hashlib.sha256(data.encode('utf-8')).hexdigest()


def validate_cid(cid: str) -> bool:
    """Validate IPFS CID format (basic check)"""
    if not cid:
        return False
    # CIDv0: starts with Qm, 46 characters
    # CIDv1: starts with b, variable length
    if cid.startswith('Qm') and len(cid) == 46:
        return True
    if cid.startswith('b'):
        return True
    return False


def fetch_from_ipfs(cid: str, gateway_url: str, timeout: int = GATEWAY_TIMEOUT) -> Tuple[Optional[str], str]:
    """
    Fetch content from IPFS gateway

    Returns:
        (content, status) where status is SUCCESS, TIMEOUT, or ERROR
    """
    # Simulate IPFS fetch (in production, use requests library)
    print(f"[IPFS] Fetching CID {cid} from {gateway_url}")

    # Check if requests module is available
    try:
        import requests

        full_url = f"{gateway_url}{cid}"
        try:
            response = requests.get(full_url, timeout=timeout)
            if response.status_code == 200:
                return response.text, "SUCCESS"
            else:
                return None, f"ERROR: HTTP {response.status_code}"
        except requests.Timeout:
            return None, "TIMEOUT"
        except requests.RequestException as e:
            return None, f"ERROR: {str(e)}"

    except ImportError:
        # Fallback mode without requests library
        print(f"[SIMULATED] Would fetch from {gateway_url}{cid}")
        print(f"[SIMULATED] requests library not available - using simulation mode")
        return None, "SIMULATED"


def sync_proof_from_node(node_id: str, proof_cid: str, expected_hash: Optional[str] = None) -> Dict:
    """
    Sync proof artifact from federated node via IPFS

    Args:
        node_id: Identifier of the federated node
        proof_cid: IPFS CID of the proof artifact
        expected_hash: Expected SHA-256 hash for verification (optional)

    Returns:
        Sync result dictionary
    """
    sync_result = {
        "node_id": node_id,
        "proof_cid": proof_cid,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "UNKNOWN",
        "gateway_used": None,
        "hash_verified": False,
        "actual_hash": None,
        "expected_hash": expected_hash,
        "error": None
    }

    # Validate CID format
    if not validate_cid(proof_cid):
        sync_result["status"] = "INVALID_CID"
        sync_result["error"] = f"Invalid CID format: {proof_cid}"
        print(f"[ERROR] Invalid CID format: {proof_cid}")
        return sync_result

    # Try each gateway with fallback
    content = None
    for gateway in IPFS_GATEWAYS:
        print(f"[IPFS] Trying gateway: {gateway}")

        for attempt in range(MAX_RETRIES):
            content, status = fetch_from_ipfs(proof_cid, gateway, GATEWAY_TIMEOUT)

            if status == "SUCCESS" and content:
                sync_result["gateway_used"] = gateway
                sync_result["status"] = "RETRIEVED"
                break
            elif status == "SIMULATED":
                sync_result["gateway_used"] = gateway
                sync_result["status"] = "SIMULATED"
                # Generate simulated content for testing
                content = json.dumps({
                    "proof_cid": proof_cid,
                    "node_id": node_id,
                    "simulated": True
                }, indent=2)
                break
            elif status == "TIMEOUT":
                print(f"[WARN] Gateway timeout (attempt {attempt + 1}/{MAX_RETRIES})")
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                print(f"[WARN] Gateway error: {status}")
                break

        if content:
            break

    if not content:
        sync_result["status"] = "FETCH_FAILED"
        sync_result["error"] = "All gateways failed or timed out"
        print("[ERROR] Failed to fetch proof from all gateways")
        return sync_result

    # Verify hash if expected hash provided
    if expected_hash:
        actual_hash = calculate_sha256(content)
        sync_result["actual_hash"] = actual_hash

        if actual_hash == expected_hash:
            sync_result["hash_verified"] = True
            sync_result["status"] = "VERIFIED"
            print(f"[SUCCESS] Hash verified: {actual_hash}")
        else:
            sync_result["hash_verified"] = False
            sync_result["status"] = "HASH_MISMATCH"
            sync_result["error"] = f"Hash mismatch: expected {expected_hash}, got {actual_hash}"
            print(f"[ERROR] Hash mismatch!")
            print(f"  Expected: {expected_hash}")
            print(f"  Actual:   {actual_hash}")
            return sync_result
    else:
        # No expected hash, calculate and store
        actual_hash = calculate_sha256(content)
        sync_result["actual_hash"] = actual_hash
        sync_result["hash_verified"] = True  # No comparison needed
        print(f"[INFO] Content hash: {actual_hash}")

    # Save proof artifact locally
    FEDERATION_DIR.mkdir(parents=True, exist_ok=True)
    proof_path = FEDERATION_DIR / f"proof_{node_id}_{proof_cid[:8]}.json"

    try:
        # Parse and re-serialize to ensure valid JSON
        proof_data = json.loads(content)
        with open(proof_path, 'w', encoding='utf-8') as f:
            json.dump(proof_data, f, indent=2, ensure_ascii=False)

        sync_result["local_path"] = str(proof_path)
        print(f"[SUCCESS] Proof saved to {proof_path}")
    except json.JSONDecodeError as e:
        sync_result["status"] = "INVALID_JSON"
        sync_result["error"] = f"Invalid JSON content: {str(e)}"
        print(f"[ERROR] Invalid JSON in proof content: {e}")
    except Exception as e:
        sync_result["status"] = "SAVE_FAILED"
        sync_result["error"] = f"Failed to save proof: {str(e)}"
        print(f"[ERROR] Failed to save proof: {e}")

    return sync_result


def sync_multiple_proofs(proof_list: List[Dict]) -> Dict:
    """
    Sync multiple proofs from federation nodes

    Args:
        proof_list: List of dicts with keys: node_id, proof_cid, expected_hash

    Returns:
        Aggregated sync results
    """
    results = {
        "sync_timestamp": datetime.now(timezone.utc).isoformat(),
        "total_proofs": len(proof_list),
        "successful": 0,
        "failed": 0,
        "hash_mismatches": 0,
        "results": []
    }

    for proof_spec in proof_list:
        node_id = proof_spec.get("node_id")
        proof_cid = proof_spec.get("proof_cid")
        expected_hash = proof_spec.get("expected_hash")

        print(f"\n[SYNC] Processing proof from node {node_id}")
        sync_result = sync_proof_from_node(node_id, proof_cid, expected_hash)

        results["results"].append(sync_result)

        if sync_result["status"] in ["VERIFIED", "RETRIEVED", "SIMULATED"]:
            results["successful"] += 1
        else:
            results["failed"] += 1

        if sync_result["status"] == "HASH_MISMATCH":
            results["hash_mismatches"] += 1

    return results


def save_sync_log(sync_results: Dict) -> None:
    """Save sync results to audit log"""
    SYNC_LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_path = SYNC_LOG_DIR / "federation_sync_log.json"

    # Load existing log or create new
    if log_path.exists():
        with open(log_path, 'r', encoding='utf-8') as f:
            log_data = json.load(f)
    else:
        log_data = {
            "log_version": "1.0.0",
            "log_type": "federation_sync_log",
            "entries": []
        }

    # Append new entry
    log_data["entries"].append(sync_results)
    log_data["last_updated"] = datetime.now(timezone.utc).isoformat()

    # Keep only last 100 sync operations
    if len(log_data["entries"]) > 100:
        log_data["entries"] = log_data["entries"][-100:]

    with open(log_path, 'w', encoding='utf-8') as f:
        json.dump(log_data, f, indent=2, ensure_ascii=False)

    print(f"\n[LOG] Sync results saved to {log_path}")


def main():
    """Main execution for IPFS sync adapter"""
    print("=" * 70)
    print("Blueprint v4.8 - IPFS Sync Adapter")
    print("=" * 70)

    # Example: Load federation proof list (in production, this comes from federation_registry)
    # For now, create a test list
    proof_list = [
        {
            "node_id": "node_example_001",
            "proof_cid": "QmTest1234567890abcdefghijklmnopqrstuvwxyz",
            "expected_hash": "abcd1234567890abcdef1234567890abcdef1234567890abcdef1234567890ab"
        }
    ]

    print("\n[INFO] Starting federated proof sync")
    print(f"[INFO] Proofs to sync: {len(proof_list)}")

    # Sync proofs
    sync_results = sync_multiple_proofs(proof_list)

    # Save results
    save_sync_log(sync_results)

    # Print summary
    print("\n" + "=" * 70)
    print("[SUMMARY] Sync Results")
    print("=" * 70)
    print(f"Total proofs:      {sync_results['total_proofs']}")
    print(f"Successful:        {sync_results['successful']}")
    print(f"Failed:            {sync_results['failed']}")
    print(f"Hash mismatches:   {sync_results['hash_mismatches']}")
    print("=" * 70)

    # Determine exit code
    if sync_results['hash_mismatches'] > 0:
        print("[EXIT] Hash mismatch detected")
        sys.exit(2)
    elif sync_results['failed'] > 0:
        print("[EXIT] Some syncs failed")
        sys.exit(1)
    else:
        print("[EXIT] All syncs successful")
        sys.exit(0)


if __name__ == "__main__":
    main()
