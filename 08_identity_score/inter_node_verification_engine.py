#!/usr/bin/env python3
"""
Blueprint v4.8 - Inter-Node Verification Engine

Verifies incoming proof hashes from federated nodes and calculates
federation consistency score (0-100). Alerts on drift > 1 bit.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

AUDIT_LOG_DIR = Path("02_audit_logging/reports")
MAX_DRIFT_BITS = 1

def calculate_bit_drift(hash1: str, hash2: str) -> int:
    """Calculate bit-level drift between two SHA-256 hashes"""
    if hash1 == hash2:
        return 0

    try:
        int1 = int(hash1, 16)
        int2 = int(hash2, 16)
        xor_result = int1 ^ int2
        return bin(xor_result).count('1')
    except:
        return 256  # Maximum drift for invalid hashes

def verify_node_proofs(node_proofs: list) -> dict:
    """Verify proofs from multiple nodes"""
    results = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_nodes": len(node_proofs),
        "consistent_nodes": 0,
        "drift_detected": 0,
        "max_drift_bits": 0,
        "federation_consistency_score": 0,
        "nodes": []
    }

    if len(node_proofs) < 2:
        return results

    # Compare first node against all others
    reference = node_proofs[0]

    for node in node_proofs:
        drift = calculate_bit_drift(reference["layer6_hash"], node["layer6_hash"])

        node_result = {
            "node_id": node["node_id"],
            "layer6_hash": node["layer6_hash"],
            "drift_bits": drift,
            "status": "CONSISTENT" if drift <= MAX_DRIFT_BITS else "DRIFT"
        }

        results["nodes"].append(node_result)

        if drift <= MAX_DRIFT_BITS:
            results["consistent_nodes"] += 1
        else:
            results["drift_detected"] += 1

        if drift > results["max_drift_bits"]:
            results["max_drift_bits"] = drift

    # Calculate consistency score
    results["federation_consistency_score"] = int(
        (results["consistent_nodes"] / results["total_nodes"]) * 100
    )

    return results

def save_consistency_log(results: dict):
    """Save consistency results"""
    AUDIT_LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_path = AUDIT_LOG_DIR / "federation_consistency_log.json"

    if log_path.exists():
        with open(log_path, 'r') as f:
            log_data = json.load(f)
    else:
        log_data = {"log_version": "1.0.0", "entries": []}

    log_data["entries"].append(results)
    log_data["last_updated"] = datetime.now(timezone.utc).isoformat()

    with open(log_path, 'w') as f:
        json.dump(log_data, f, indent=2)

    print(f"[LOG] Saved to {log_path}")

def main():
    print("=== Inter-Node Verification Engine v4.8 ===")

    # Example: Verify 3 nodes
    node_proofs = [
        {"node_id": "node_001", "layer6_hash": "a" * 64},
        {"node_id": "node_002", "layer6_hash": "a" * 64},
        {"node_id": "node_003", "layer6_hash": "a" * 64}
    ]

    results = verify_node_proofs(node_proofs)
    save_consistency_log(results)

    print(f"\nConsistency Score: {results['federation_consistency_score']}/100")
    print(f"Consistent Nodes: {results['consistent_nodes']}/{results['total_nodes']}")
    print(f"Max Drift: {results['max_drift_bits']} bits")

    sys.exit(0 if results['drift_detected'] == 0 else 1)

if __name__ == "__main__":
    main()
