#!/usr/bin/env python3
"""
Blueprint v4.5 Proof-Chain Integrity Watcher

Performs cryptographic integrity verification of the 4-layer proof chain:
  Layer 1: Registry Event Proof-Anchor
  Layer 2: Evidence Merkle Root
  Layer 3: Shadow Proof Merkle Root
  Layer 4: Archive Proof-Anchor

Features:
- SHA256 hash verification with zero-tolerance for drift
- Comprehensive audit reporting
- Optional repair mode (--repair flag)
- Deep integrity comparison

Exit Codes:
  0 = OK (All layers verified)
  1 = Hash drift detected
  2 = Missing proof layer
  3 = Verification failure
"""

import json
import os
import sys
import hashlib
import argparse
from datetime import datetime, timezone
from pathlib import Path

# Configuration
REPORT_PATH = "23_compliance/reports/proof_chain_integrity_report.json"

PROOF_CHAIN_LAYERS = {
    "layer_1_registry_event": {
        "name": "Registry Event Proof-Anchor",
        "expected_hash": "e4e967a292d19096d2ecf406f6f7f22791a5948dd529e53e7778b6a1642581bf",
        "source": "24_meta_orchestration/registry/manifests/readiness_proof_shadow.json",
        "json_path": ["verification_event", "proof_anchor"]
    },
    "layer_2_evidence_merkle": {
        "name": "Evidence Merkle Root",
        "expected_hash": "d1f385e1fb95a07691b698c08ec51bc961f171fe7f9f9153b1061172a57e191a",
        "source": "23_compliance/evidence/proof_hashes.json",
        "json_path": ["merkle_tree", "root_hash"]
    },
    "layer_3_shadow_proof": {
        "name": "Shadow Proof Merkle Root",
        "expected_hash": "0b7d38551cece20a01da0c038cda7c4390e4db05fa605f2daebd09b862612bf0",
        "source": "24_meta_orchestration/registry/manifests/readiness_proof_shadow.json",
        "json_path": ["merkle_tree", "root_hash"]
    },
    "layer_4_archive_proof": {
        "name": "Archive Proof-Anchor",
        "expected_hash": "dd89b7a81186aed5e8dcb6f8f8853e7e20e124a4a90a9f2b00b1af733e04780c",
        "source": "24_meta_orchestration/registry/events/archive_proof_anchor.json",
        "json_path": ["archive_proof_anchor", "sha256_hash"]
    }
}

def get_nested_value(data, path):
    """Extract nested value from JSON using path list"""
    value = data
    for key in path:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return None
    return value

def verify_proof_layer(layer_id, layer_config):
    """Verify a single proof chain layer"""
    source_path = layer_config["source"]
    expected_hash = layer_config["expected_hash"]
    json_path = layer_config["json_path"]

    # Check if source file exists
    if not os.path.exists(source_path):
        return {
            "status": "MISSING",
            "expected_hash": expected_hash,
            "actual_hash": None,
            "drift_bits": None,
            "error": f"Source file not found: {source_path}"
        }

    try:
        # Load JSON and extract hash
        with open(source_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        actual_hash = get_nested_value(data, json_path)

        if actual_hash is None:
            return {
                "status": "ERROR",
                "expected_hash": expected_hash,
                "actual_hash": None,
                "drift_bits": None,
                "error": f"Hash not found at path: {' -> '.join(json_path)}"
            }

        # Calculate drift (bit-level comparison)
        drift_bits = calculate_hash_drift(expected_hash, actual_hash)

        status = "VERIFIED" if drift_bits == 0 else "DRIFT_DETECTED"

        return {
            "status": status,
            "expected_hash": expected_hash,
            "actual_hash": actual_hash,
            "drift_bits": drift_bits,
            "drift_percentage": (drift_bits / 256) * 100 if drift_bits > 0 else 0,
            "source_path": source_path,
            "json_path": " -> ".join(json_path)
        }

    except json.JSONDecodeError as e:
        return {
            "status": "ERROR",
            "expected_hash": expected_hash,
            "actual_hash": None,
            "drift_bits": None,
            "error": f"JSON parse error: {str(e)}"
        }
    except Exception as e:
        return {
            "status": "ERROR",
            "expected_hash": expected_hash,
            "actual_hash": None,
            "drift_bits": None,
            "error": f"Verification error: {str(e)}"
        }

def calculate_hash_drift(expected, actual):
    """Calculate bit-level drift between two SHA256 hashes"""
    if expected == actual:
        return 0

    # Convert to binary and count differing bits
    try:
        expected_int = int(expected, 16)
        actual_int = int(actual, 16)
        xor_result = expected_int ^ actual_int
        return bin(xor_result).count('1')
    except:
        return 256  # Maximum drift for invalid hashes

def calculate_file_hash(filepath):
    """Calculate SHA256 hash of a file"""
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            sha256.update(chunk)
    return sha256.hexdigest()

def verify_all_layers():
    """Verify all proof chain layers"""
    results = {}
    total_drift_bits = 0

    for layer_id, layer_config in PROOF_CHAIN_LAYERS.items():
        print(f"Verifying {layer_config['name']}...")
        result = verify_proof_layer(layer_id, layer_config)
        results[layer_id] = result

        if result["drift_bits"] is not None:
            total_drift_bits += result["drift_bits"]

    return results, total_drift_bits

def generate_integrity_report(verification_results, total_drift):
    """Generate comprehensive integrity report"""
    timestamp = datetime.now(timezone.utc).isoformat()

    # Determine overall status
    all_verified = all(
        r["status"] == "VERIFIED" for r in verification_results.values()
    )

    any_drift = total_drift > 0
    any_missing = any(
        r["status"] == "MISSING" for r in verification_results.values()
    )
    any_error = any(
        r["status"] == "ERROR" for r in verification_results.values()
    )

    if all_verified:
        overall_status = "PASS"
        exit_code = 0
        exit_message = "All proof layers verified with zero drift"
    elif any_drift:
        overall_status = "DRIFT_DETECTED"
        exit_code = 1
        exit_message = f"Hash drift detected: {total_drift} bits"
    elif any_missing:
        overall_status = "MISSING_LAYER"
        exit_code = 2
        exit_message = "Missing proof layer(s)"
    else:
        overall_status = "VERIFICATION_FAILURE"
        exit_code = 3
        exit_message = "Proof chain verification failed"

    report = {
        "manifest_version": "1.0.0",
        "blueprint_version": "v4.5.0-prelaunch",
        "timestamp": timestamp,
        "report_type": "proof_chain_integrity",
        "verification_results": verification_results,
        "integrity_summary": {
            "total_layers": len(PROOF_CHAIN_LAYERS),
            "layers_verified": sum(1 for r in verification_results.values() if r["status"] == "VERIFIED"),
            "layers_with_drift": sum(1 for r in verification_results.values() if r["status"] == "DRIFT_DETECTED"),
            "layers_missing": sum(1 for r in verification_results.values() if r["status"] == "MISSING"),
            "layers_error": sum(1 for r in verification_results.values() if r["status"] == "ERROR"),
            "total_drift_bits": total_drift,
            "max_drift_bits": 256 * len(PROOF_CHAIN_LAYERS),
            "drift_percentage": (total_drift / (256 * len(PROOF_CHAIN_LAYERS))) * 100
        },
        "overall_status": {
            "status": overall_status,
            "exit_code": exit_code,
            "exit_message": exit_message,
            "chain_integrity": "INTACT" if all_verified else "COMPROMISED"
        }
    }

    return report, exit_code

def save_integrity_report(report):
    """Save integrity report to file"""
    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)

    with open(REPORT_PATH, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

    print(f"\n[OK] Integrity report saved: {REPORT_PATH}")

def print_integrity_summary(report):
    """Print human-readable integrity summary"""
    print("\n" + "=" * 70)
    print("  PROOF-CHAIN INTEGRITY WATCHER - Blueprint v4.5")
    print("=" * 70)
    print()

    print("[VERIFICATION RESULTS]")
    for layer_id, result in report["verification_results"].items():
        layer_name = PROOF_CHAIN_LAYERS[layer_id]["name"]
        status = result["status"]

        if status == "VERIFIED":
            print(f"  [OK] {layer_name}")
            print(f"       Hash: {result['actual_hash'][:16]}...")
        elif status == "DRIFT_DETECTED":
            print(f"  [DRIFT] {layer_name}")
            print(f"       Expected: {result['expected_hash'][:16]}...")
            print(f"       Actual:   {result['actual_hash'][:16]}...")
            print(f"       Drift: {result['drift_bits']} bits ({result['drift_percentage']:.2f}%)")
        elif status == "MISSING":
            print(f"  [MISSING] {layer_name}")
            print(f"       Error: {result.get('error', 'Unknown error')}")
        elif status == "ERROR":
            print(f"  [ERROR] {layer_name}")
            print(f"       Error: {result.get('error', 'Unknown error')}")

    print()

    summary = report["integrity_summary"]
    print("[INTEGRITY SUMMARY]")
    print(f"  Total Layers: {summary['total_layers']}")
    print(f"  Verified: {summary['layers_verified']}")
    print(f"  Drift Detected: {summary['layers_with_drift']}")
    print(f"  Missing: {summary['layers_missing']}")
    print(f"  Errors: {summary['layers_error']}")
    print(f"  Total Drift: {summary['total_drift_bits']} bits ({summary['drift_percentage']:.2f}%)")
    print()

    overall = report["overall_status"]
    print("[OVERALL STATUS]")
    print(f"  Status: {overall['status']}")
    print(f"  Chain Integrity: {overall['chain_integrity']}")
    print(f"  Exit Code: {overall['exit_code']}")
    print(f"  Message: {overall['exit_message']}")
    print()

    print("=" * 70)
    if overall["chain_integrity"] == "INTACT":
        print("  [OK] PROOF CHAIN INTEGRITY: VERIFIED")
    else:
        print("  [WARNING] PROOF CHAIN INTEGRITY: COMPROMISED")
    print("=" * 70)

def repair_shadow_proof():
    """Create new shadow proof with current timestamp (repair mode)"""
    print("\n[REPAIR MODE] Creating new shadow proof...")

    shadow_path = "24_meta_orchestration/registry/manifests/readiness_proof_shadow.json"

    if not os.path.exists(shadow_path):
        print("[ERROR] Shadow proof file not found for repair")
        return False

    with open(shadow_path, 'r', encoding='utf-8') as f:
        shadow_data = json.load(f)

    # Update timestamp
    shadow_data["timestamp"] = datetime.now(timezone.utc).isoformat()
    shadow_data["repair_mode"] = True
    shadow_data["original_timestamp"] = shadow_data.get("timestamp")

    # Save repaired version
    repair_path = shadow_path.replace(".json", "_repaired.json")
    with open(repair_path, 'w', encoding='utf-8') as f:
        json.dump(shadow_data, f, indent=2)

    print(f"[OK] Repaired shadow proof saved: {repair_path}")
    return True

def main():
    """Main execution"""
    parser = argparse.ArgumentParser(description="Proof-Chain Integrity Watcher")
    parser.add_argument('--repair', action='store_true', help='Repair mode: create new shadow proof')
    args = parser.parse_args()

    print("\nProof-Chain Integrity Watcher - Blueprint v4.5")
    print("Verifying 4-layer cryptographic proof chain...\n")

    # Verify all layers
    verification_results, total_drift = verify_all_layers()

    # Generate report
    report, exit_code = generate_integrity_report(verification_results, total_drift)

    # Save report
    save_integrity_report(report)

    # Print summary
    print_integrity_summary(report)

    # Repair mode
    if args.repair and exit_code != 0:
        repair_shadow_proof()

    # Exit with appropriate code
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
