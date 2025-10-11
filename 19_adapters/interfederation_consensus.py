#!/usr/bin/env python3
"""
Blueprint v4.9 - Inter-Federation Mesh Consensus Adapter

Aggregates Layer 7 federation proofs from multiple meshes into Layer 8 consensus proof.
Implements hash-majority voting (≥80% threshold) with Byzantine tolerance (≤20%).

Layer 8 Merkle Root = SHA256(
    Σ Hashes(Layer 7 own mesh) +
    Σ Hashes(Layer 7 foreign meshes - validated) +
    consensus_vote_tally
)

CRITICAL: Non-interactive, deterministic execution only.
Time-gated: Blocks execution before epoch activation (2026-04-15 10:00 UTC).

Exit Codes:
    0: SUCCESS - Consensus achieved, Layer 8 proof generated
    1: EARLY - Epoch not reached (expected state)
    2: PREREQ_MISSING - Layer 7 proofs not available
    3: FAILED - Execution error or validation failure
    4: THRESHOLD_FAIL - Consensus threshold not met (<80%)
"""

import json
import sys
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# ============================================================================
# CONFIGURATION
# ============================================================================

# Time gate - prevents execution before epoch activation
EPOCH_ACTIVATION_DATE = datetime(2026, 4, 15, 10, 0, 0, tzinfo=timezone.utc)
EPOCH_ID = "Q2_2026"

# Paths (Root-24-LOCK compliant)
L7_LOCAL_DIR = Path("24_meta_orchestration/registry/manifests/layer7_local")
MESH_INBOX_DIR = Path("24_meta_orchestration/federation/inbox")
CONSENSUS_OUTPUT_DIR = Path("24_meta_orchestration/consensus")

# Consensus parameters
CONSENSUS_THRESHOLD = 0.80  # 80% hash-majority required
BYZANTINE_TOLERANCE = 0.20  # Max 20% malicious/faulty nodes
MAX_TIMESTAMP_DRIFT_HOURS = 48
MIN_TRUST_SCORE = 60

# Trust adaptation parameters
TRUST_INCREMENT_AGREE = 1
TRUST_DECREMENT_DISAGREE = 3
TRUST_MIN = 0
TRUST_MAX = 100

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def calculate_sha256(data) -> str:
    """Calculate SHA-256 hash of data"""
    if isinstance(data, dict):
        data = json.dumps(data, sort_keys=True)
    return hashlib.sha256(data.encode('utf-8')).hexdigest()

def check_time_gate() -> bool:
    """Check if current time has passed epoch activation"""
    now = datetime.now(timezone.utc)
    return now >= EPOCH_ACTIVATION_DATE

def validate_timestamp(timestamp_str: str) -> bool:
    """Validate timestamp is within acceptable drift window"""
    try:
        ts = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        now = datetime.now(timezone.utc)
        drift_hours = abs((now - ts).total_seconds()) / 3600
        return drift_hours <= MAX_TIMESTAMP_DRIFT_HOURS
    except:
        return False

def validate_signature_stub(sig_data: Dict) -> bool:
    """
    Stub signature validation (format check only, no real cryptography)
    In production: Replace with real Ed25519/ECDSA/PGP verification
    """
    required_fields = ["key_id", "signature_hex", "algorithm"]
    if not all(field in sig_data for field in required_fields):
        return False

    # Format validation only
    if sig_data["algorithm"] not in ["ed25519", "ecdsa", "pgp"]:
        return False

    if not isinstance(sig_data["signature_hex"], str):
        return False

    if len(sig_data["signature_hex"]) < 64:  # Minimum signature length
        return False

    return True

# ============================================================================
# LAYER 7 PROOF COLLECTION
# ============================================================================

def collect_layer7_proofs() -> Tuple[List[Dict], int]:
    """
    Collect local Layer 7 federation proofs

    Returns:
        Tuple of (proofs_list, exit_code)
    """
    print("=== Collecting Local Layer 7 Proofs ===")

    if not L7_LOCAL_DIR.exists():
        print(f"[ERROR] Local Layer 7 directory not found: {L7_LOCAL_DIR}")
        return [], 2

    proofs = []
    for proof_file in L7_LOCAL_DIR.glob("*.json"):
        try:
            with open(proof_file, 'r') as f:
                proof = json.load(f)

            # Validate structure
            if "proof_chain_layer_7" not in proof:
                print(f"[WARN] Invalid Layer 7 proof: {proof_file.name}")
                continue

            proofs.append({
                "source": "local",
                "node_id": proof.get("node_id", "local_node"),
                "layer7_hash": proof["proof_chain_layer_7"]["merkle_root"],
                "timestamp": proof.get("timestamp", ""),
                "epoch_id": proof.get("epoch", EPOCH_ID),
                "proof_data": proof
            })

            print(f"[OK] Loaded local proof: {proof_file.name}")

        except Exception as e:
            print(f"[ERROR] Failed to load {proof_file.name}: {e}")
            continue

    if not proofs:
        print("[ERROR] No valid local Layer 7 proofs found")
        return [], 2

    print(f"[SUCCESS] Collected {len(proofs)} local Layer 7 proof(s)")
    return proofs, 0

def simulate_mesh_inbox() -> Tuple[List[Dict], int]:
    """
    Load foreign Layer 7 proofs from mesh inbox

    Returns:
        Tuple of (foreign_proofs_list, exit_code)
    """
    print("\n=== Simulating Mesh Inbox (Foreign Layer 7 Proofs) ===")

    if not MESH_INBOX_DIR.exists():
        print(f"[WARN] Mesh inbox directory not found: {MESH_INBOX_DIR}")
        print("[INFO] Creating inbox directory (empty for now)")
        MESH_INBOX_DIR.mkdir(parents=True, exist_ok=True)
        return [], 0

    foreign_proofs = []
    for proof_file in MESH_INBOX_DIR.glob("*.json"):
        try:
            with open(proof_file, 'r') as f:
                proof = json.load(f)

            foreign_proofs.append(proof)
            print(f"[OK] Loaded foreign proof: {proof_file.name}")

        except Exception as e:
            print(f"[ERROR] Failed to load {proof_file.name}: {e}")
            continue

    if not foreign_proofs:
        print("[INFO] No foreign proofs in inbox (acceptable for initial run)")
    else:
        print(f"[SUCCESS] Loaded {len(foreign_proofs)} foreign proof(s)")

    return foreign_proofs, 0

# ============================================================================
# FOREIGN PROOF VALIDATION
# ============================================================================

def validate_foreign_proof(proof: Dict) -> Tuple[bool, str]:
    """
    Validate foreign Layer 7 proof

    Checks:
        - Required fields present
        - Timestamp within drift window
        - Signature stub format valid
        - Hash format valid (64 hex chars)
        - Epoch ID matches

    Returns:
        Tuple of (is_valid, reason)
    """
    # Required fields
    required = ["node_id", "layer7_hash", "timestamp_utc", "epoch_id", "signature"]
    missing = [f for f in required if f not in proof]
    if missing:
        return False, f"Missing fields: {missing}"

    # Epoch validation
    if proof["epoch_id"] != EPOCH_ID:
        return False, f"Epoch mismatch: {proof['epoch_id']} != {EPOCH_ID}"

    # Timestamp validation
    if not validate_timestamp(proof["timestamp_utc"]):
        return False, f"Timestamp drift >48h or invalid format"

    # Hash format validation
    layer7_hash = proof["layer7_hash"]
    if not isinstance(layer7_hash, str) or len(layer7_hash) != 64:
        return False, "Invalid hash format (expected 64 hex chars)"

    try:
        int(layer7_hash, 16)
    except ValueError:
        return False, "Hash is not valid hexadecimal"

    # Signature stub validation
    if not validate_signature_stub(proof["signature"]):
        return False, "Invalid signature stub format"

    return True, "Valid"

# ============================================================================
# LAYER 8 CONSENSUS COMPUTATION
# ============================================================================

def vote_and_tally(all_proofs: List[Dict]) -> Dict:
    """
    Perform hash-majority voting and calculate consensus

    Algorithm:
        1. Group proofs by Layer 7 hash
        2. Calculate vote percentage for each hash
        3. Determine majority hash (≥80% threshold)
        4. Classify nodes as agree/disagree

    Returns:
        Vote tally dictionary with results
    """
    print("\n=== Hash-Majority Voting ===")

    total_nodes = len(all_proofs)
    if total_nodes == 0:
        return {
            "total_nodes": 0,
            "consensus_achieved": False,
            "reason": "No proofs to vote on"
        }

    # Count votes per hash
    vote_counts = {}
    for proof in all_proofs:
        layer7_hash = proof["layer7_hash"]
        if layer7_hash not in vote_counts:
            vote_counts[layer7_hash] = []
        vote_counts[layer7_hash].append(proof["node_id"])

    print(f"[INFO] Total nodes: {total_nodes}")
    print(f"[INFO] Unique hashes: {len(vote_counts)}")

    # Find majority hash
    majority_hash = None
    majority_count = 0
    majority_percentage = 0.0

    for hash_val, nodes in vote_counts.items():
        count = len(nodes)
        percentage = count / total_nodes

        print(f"[VOTE] Hash {hash_val[:16]}... : {count}/{total_nodes} ({percentage*100:.1f}%)")

        if percentage >= CONSENSUS_THRESHOLD:
            majority_hash = hash_val
            majority_count = count
            majority_percentage = percentage

    # Classify nodes
    agree_nodes = []
    disagree_nodes = []

    if majority_hash:
        for proof in all_proofs:
            if proof["layer7_hash"] == majority_hash:
                agree_nodes.append(proof["node_id"])
            else:
                disagree_nodes.append(proof["node_id"])

    consensus_achieved = majority_hash is not None and majority_percentage >= CONSENSUS_THRESHOLD
    byzantine_percentage = len(disagree_nodes) / total_nodes if total_nodes > 0 else 0

    tally = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "epoch_id": EPOCH_ID,
        "total_nodes": total_nodes,
        "consensus_achieved": consensus_achieved,
        "consensus_threshold": CONSENSUS_THRESHOLD,
        "byzantine_tolerance": BYZANTINE_TOLERANCE,
        "majority_hash": majority_hash,
        "majority_count": majority_count,
        "majority_percentage": majority_percentage,
        "byzantine_count": len(disagree_nodes),
        "byzantine_percentage": byzantine_percentage,
        "agree_nodes": agree_nodes,
        "disagree_nodes": disagree_nodes,
        "vote_distribution": {h: len(nodes) for h, nodes in vote_counts.items()}
    }

    if consensus_achieved:
        print(f"[SUCCESS] Consensus achieved: {majority_percentage*100:.1f}% agreement")
        print(f"[INFO] Byzantine nodes: {byzantine_percentage*100:.1f}% (tolerance: {BYZANTINE_TOLERANCE*100:.1f}%)")
    else:
        print(f"[FAIL] Consensus NOT achieved: {majority_percentage*100:.1f}% < {CONSENSUS_THRESHOLD*100:.1f}% threshold")

    return tally

def compute_layer8_root(local_proofs: List[Dict], foreign_proofs_valid: List[Dict], tally: Dict) -> str:
    """
    Compute Layer 8 consensus merkle root

    Layer 8 = SHA256(
        Σ local_L7_hashes (sorted) +
        Σ foreign_L7_hashes_valid (sorted) +
        tally_hash
    )
    """
    print("\n=== Computing Layer 8 Merkle Root ===")

    # Aggregate local Layer 7 hashes
    local_hashes = sorted([p["layer7_hash"] for p in local_proofs])
    local_aggregate = "".join(local_hashes)
    local_hash = hashlib.sha256(local_aggregate.encode()).hexdigest()

    # Aggregate foreign Layer 7 hashes
    foreign_hashes = sorted([p["layer7_hash"] for p in foreign_proofs_valid])
    foreign_aggregate = "".join(foreign_hashes)
    foreign_hash = hashlib.sha256(foreign_aggregate.encode()).hexdigest()

    # Tally hash
    tally_hash = calculate_sha256(tally)

    # Compute Layer 8 root
    layer8_input = local_hash + foreign_hash + tally_hash
    layer8_root = hashlib.sha256(layer8_input.encode()).hexdigest()

    print(f"[INFO] Local L7 aggregate: {local_hash[:16]}...")
    print(f"[INFO] Foreign L7 aggregate: {foreign_hash[:16]}...")
    print(f"[INFO] Tally hash: {tally_hash[:16]}...")
    print(f"[SUCCESS] Layer 8 root: {layer8_root}")

    return layer8_root

# ============================================================================
# TRUST SCORE ADAPTATION
# ============================================================================

def adjust_trust(tally: Dict, current_trust_scores: Dict[str, int]) -> Dict[str, int]:
    """
    Adjust trust scores based on consensus participation

    Rules:
        - Agree with majority: +1 (up to max 100)
        - Disagree with majority: -3 (down to min 0)
    """
    print("\n=== Adjusting Trust Scores ===")

    updated_scores = current_trust_scores.copy()
    deltas = {}

    for node_id in tally["agree_nodes"]:
        current = updated_scores.get(node_id, 75)  # Default trust: 75
        new_score = min(current + TRUST_INCREMENT_AGREE, TRUST_MAX)
        updated_scores[node_id] = new_score
        deltas[node_id] = {
            "previous": current,
            "delta": TRUST_INCREMENT_AGREE,
            "new": new_score,
            "action": "AGREE"
        }
        print(f"[+] {node_id}: {current} → {new_score} (+{TRUST_INCREMENT_AGREE})")

    for node_id in tally["disagree_nodes"]:
        current = updated_scores.get(node_id, 75)
        new_score = max(current - TRUST_DECREMENT_DISAGREE, TRUST_MIN)
        updated_scores[node_id] = new_score
        deltas[node_id] = {
            "previous": current,
            "delta": -TRUST_DECREMENT_DISAGREE,
            "new": new_score,
            "action": "DISAGREE"
        }
        print(f"[-] {node_id}: {current} → {new_score} (-{TRUST_DECREMENT_DISAGREE})")

    trust_delta = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "epoch_id": EPOCH_ID,
        "trust_parameters": {
            "increment_agree": TRUST_INCREMENT_AGREE,
            "decrement_disagree": TRUST_DECREMENT_DISAGREE,
            "min": TRUST_MIN,
            "max": TRUST_MAX
        },
        "deltas": deltas,
        "updated_scores": updated_scores
    }

    return trust_delta

# ============================================================================
# OUTPUT GENERATION
# ============================================================================

def save_outputs(tally: Dict, layer8_proof: Dict, trust_delta: Dict):
    """Save consensus outputs to JSON files"""
    print("\n=== Saving Outputs ===")

    CONSENSUS_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Vote tally
    tally_path = CONSENSUS_OUTPUT_DIR / "intermesh_vote_tally.json"
    with open(tally_path, 'w') as f:
        json.dump(tally, f, indent=2)
    print(f"[SAVED] {tally_path}")

    # Layer 8 proof
    layer8_path = CONSENSUS_OUTPUT_DIR / "layer8_consensus_proof.json"
    with open(layer8_path, 'w') as f:
        json.dump(layer8_proof, f, indent=2)
    print(f"[SAVED] {layer8_path}")

    # Trust delta
    trust_path = CONSENSUS_OUTPUT_DIR / "consensus_trust_delta.json"
    with open(trust_path, 'w') as f:
        json.dump(trust_delta, f, indent=2)
    print(f"[SAVED] {trust_path}")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    print("=" * 70)
    print("Blueprint v4.9 - Inter-Federation Mesh Consensus Adapter")
    print("=" * 70)
    print(f"Epoch: {EPOCH_ID}")
    print(f"Consensus Threshold: {CONSENSUS_THRESHOLD*100:.0f}%")
    print(f"Byzantine Tolerance: {BYZANTINE_TOLERANCE*100:.0f}%")
    print(f"Activation Gate: {EPOCH_ACTIVATION_DATE.isoformat()}")
    print("=" * 70)

    # Time gate check
    if not check_time_gate():
        print("\n[EARLY] Epoch activation date not reached")
        print(f"Current time: {datetime.now(timezone.utc).isoformat()}")
        print(f"Activation: {EPOCH_ACTIVATION_DATE.isoformat()}")
        print("[EXIT 1] Time gate not passed - expected state")
        sys.exit(1)

    # Collect local Layer 7 proofs
    local_proofs, exit_code = collect_layer7_proofs()
    if exit_code != 0:
        print("[EXIT 2] Prerequisites missing - local Layer 7 proofs not found")
        sys.exit(2)

    # Load foreign proofs from mesh inbox
    foreign_proofs_raw, _ = simulate_mesh_inbox()

    # Validate foreign proofs
    print("\n=== Validating Foreign Proofs ===")
    foreign_proofs_valid = []
    for proof in foreign_proofs_raw:
        is_valid, reason = validate_foreign_proof(proof)
        if is_valid:
            foreign_proofs_valid.append(proof)
            print(f"[OK] {proof['node_id']}: {reason}")
        else:
            print(f"[REJECT] {proof.get('node_id', 'unknown')}: {reason}")

    print(f"[INFO] Valid foreign proofs: {len(foreign_proofs_valid)}/{len(foreign_proofs_raw)}")

    # Combine all proofs for voting
    all_proofs = local_proofs + foreign_proofs_valid

    if len(all_proofs) == 0:
        print("[EXIT 2] No proofs available for consensus")
        sys.exit(2)

    # Perform voting and tally
    tally = vote_and_tally(all_proofs)

    if not tally["consensus_achieved"]:
        print(f"[EXIT 4] Consensus threshold not met: {tally['majority_percentage']*100:.1f}% < {CONSENSUS_THRESHOLD*100:.0f}%")
        sys.exit(4)

    # Compute Layer 8 root
    layer8_root = compute_layer8_root(local_proofs, foreign_proofs_valid, tally)

    # Build Layer 8 proof structure
    layer8_proof = {
        "manifest_version": "1.0.0",
        "blueprint_version": "v4.9.0-interfederation",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "epoch_id": EPOCH_ID,
        "proof_chain_layer_8": {
            "layer_id": "layer_8_intermesh_consensus",
            "description": "Inter-Federation Mesh Consensus Proof",
            "merkle_root": layer8_root,
            "local_mesh_count": len(local_proofs),
            "foreign_mesh_count": len(foreign_proofs_valid),
            "total_participants": len(all_proofs),
            "consensus_percentage": tally["majority_percentage"],
            "byzantine_percentage": tally["byzantine_percentage"]
        },
        "proof_status": "FINALIZED",
        "consensus_achieved": True
    }

    layer8_proof["proof_anchor"] = calculate_sha256(layer8_proof)

    # Adjust trust scores
    current_trust = {p["node_id"]: 75 for p in all_proofs}  # Initialize with default
    trust_delta = adjust_trust(tally, current_trust)

    # Save all outputs
    save_outputs(tally, layer8_proof, trust_delta)

    print("\n" + "=" * 70)
    print("[SUCCESS] Inter-Federation Consensus Complete")
    print(f"Layer 8 Root: {layer8_root}")
    print(f"Consensus: {tally['majority_percentage']*100:.1f}%")
    print(f"Byzantine: {tally['byzantine_percentage']*100:.1f}%")
    print("=" * 70)

    sys.exit(0)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n[FATAL ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(3)
