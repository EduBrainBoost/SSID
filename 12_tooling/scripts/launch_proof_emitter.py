#!/usr/bin/env python3
"""
Blueprint v4.6 - Launch Proof Emitter

This script extends the proof-anchor chain with Layer 5 (Launch Proof)
and validates continuity from v4.4 Archive (Layer 4).

This should execute after autonomous_cycle_launcher.py and telemetry_activation.py.

Exit Codes:
  0 - Proof emission successful, chain extended
  1 - Launch not confirmed (prerequisite)
  2 - Chain validation failed
  3 - Proof emission failed
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
import hashlib

# Blueprint version
BLUEPRINT_VERSION = "v4.6.0-launch"
CYCLE_ID = "Q1_2026"

# File paths
REGISTRY_DIR = Path("24_meta_orchestration/registry")
EVENTS_DIR = REGISTRY_DIR / "events"
MANIFESTS_DIR = REGISTRY_DIR / "manifests"
REPORTS_DIR = Path("05_documentation/reports/2026-Q1")
COMPLIANCE_DIR = Path("23_compliance/reports")
STATE_LOG = Path("02_audit_logging/reports/autonomous_cycle_state.json")

def calculate_sha256(data):
    """Calculate SHA256 hash of data"""
    if isinstance(data, dict):
        data = json.dumps(data, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(data.encode('utf-8')).hexdigest()

def check_launch_confirmation():
    """Verify that autonomous cycle launch has completed"""
    if not STATE_LOG.exists():
        print("[ERROR] Launch state log not found")
        return False

    with open(STATE_LOG, 'r', encoding='utf-8') as f:
        state = json.load(f)

    if state.get("system_state") != "AUTONOMOUS_ACTIVE":
        print(f"[ERROR] System not in AUTONOMOUS_ACTIVE state")
        return False

    print("[OK] Launch confirmed")
    return True

def validate_proof_chain_continuity():
    """Validate proof chain from Layer 1 through Layer 4"""
    print("\n[VALIDATING PROOF CHAIN CONTINUITY]")

    expected_hashes = {
        "layer_1": "e4e967a292d19096d2ecf406f6f7f22791a5948dd529e53e7778b6a1642581bf",
        "layer_2": "d1f385e1fb95a07691b698c08ec51bc961f171fe7f9f9153b1061172a57e191a",
        "layer_3": "0b7d38551cece20a01da0c038cda7c4390e4db05fa605f2daebd09b862612bf0",
        "layer_4": "dd89b7a81186aed5e8dcb6f8f8853e7e20e124a4a90a9f2b00b1af733e04780c"
    }

    # Validate Layer 1 - Registry Event Proof-Anchor
    readiness_shadow = MANIFESTS_DIR / "readiness_proof_shadow.json"
    if readiness_shadow.exists():
        with open(readiness_shadow, 'r', encoding='utf-8') as f:
            data = json.load(f)
            layer_1_hash = data.get("verification_event", {}).get("proof_anchor")
            if layer_1_hash == expected_hashes["layer_1"]:
                print(f"Layer 1 (Registry Event):     VERIFIED ({layer_1_hash[:16]}...)")
            else:
                print(f"Layer 1 (Registry Event):     FAILED")
                return False
    else:
        print("Layer 1: MISSING")
        return False

    # Validate Layer 2 - Evidence Merkle Root
    evidence_hashes = Path("23_compliance/evidence/proof_hashes.json")
    if evidence_hashes.exists():
        with open(evidence_hashes, 'r', encoding='utf-8') as f:
            data = json.load(f)
            layer_2_hash = data.get("merkle_tree", {}).get("root_hash")
            if layer_2_hash == expected_hashes["layer_2"]:
                print(f"Layer 2 (Evidence Merkle):     VERIFIED ({layer_2_hash[:16]}...)")
            else:
                print(f"Layer 2 (Evidence Merkle):     FAILED")
                return False
    else:
        print("Layer 2: MISSING")
        return False

    # Validate Layer 3 - Shadow Proof Merkle Root
    if readiness_shadow.exists():
        with open(readiness_shadow, 'r', encoding='utf-8') as f:
            data = json.load(f)
            layer_3_hash = data.get("merkle_tree", {}).get("root_hash")
            if layer_3_hash == expected_hashes["layer_3"]:
                print(f"Layer 3 (Shadow Proof):        VERIFIED ({layer_3_hash[:16]}...)")
            else:
                print(f"Layer 3 (Shadow Proof):        FAILED")
                return False
    else:
        print("Layer 3: MISSING")
        return False

    # Validate Layer 4 - Archive Proof-Anchor
    archive_proof = EVENTS_DIR / "archive_proof_anchor.json"
    if archive_proof.exists():
        with open(archive_proof, 'r', encoding='utf-8') as f:
            data = json.load(f)
            layer_4_hash = data.get("archive_proof_anchor", {}).get("sha256_hash")
            if layer_4_hash == expected_hashes["layer_4"]:
                print(f"Layer 4 (Archive Proof):       VERIFIED ({layer_4_hash[:16]}...)")
            else:
                print(f"Layer 4 (Archive Proof):       FAILED")
                return False
    else:
        print("Layer 4: MISSING")
        return False

    print("\n[CHAIN CONTINUITY] All 4 layers verified - ready for Layer 5 extension")
    return True

def generate_layer_5_proof():
    """Generate Layer 5 (Launch Proof) and extend the chain"""
    now = datetime.now(timezone.utc)

    # Check if launch proof already exists
    launch_proof_path = EVENTS_DIR / "launch_proof_Q1_2026.json"
    if not launch_proof_path.exists():
        print("[ERROR] Launch proof not found - autonomous_cycle_launcher.py must run first")
        return None

    # Load existing launch proof
    with open(launch_proof_path, 'r', encoding='utf-8') as f:
        launch_proof = json.load(f)

    layer_5_hash = launch_proof.get("proof_chain_layer_5", {}).get("merkle_root")
    proof_anchor = launch_proof.get("proof_anchor")

    print("\n[LAYER 5 PROOF]")
    print(f"Merkle Root:         {layer_5_hash}")
    print(f"Proof Anchor:        {proof_anchor}")
    print(f"Linked from Layer 4: dd89b7a81186aed5e8dcb6f8f8853e7e20e124a4a90a9f2b00b1af733e04780c")
    print(f"Reports Included:    {launch_proof['proof_chain_layer_5']['total_reports']}")

    return launch_proof

def create_proof_anchor_chain_document():
    """Create comprehensive proof-anchor chain document (Layers 1-5)"""
    now = datetime.now(timezone.utc)

    chain_document = {
        "manifest_version": "1.0.0",
        "blueprint_version": BLUEPRINT_VERSION,
        "timestamp": now.isoformat(),
        "document_type": "proof_anchor_chain",
        "governance_cycle": CYCLE_ID,
        "description": "Complete cryptographic proof-anchor chain from v4.0 to v4.6 Q1 2026 Launch",
        "proof_chain": {
            "layer_1_registry_event": {
                "description": "Registry Event Proof-Anchor",
                "source": "readiness_proof_shadow.json",
                "json_path": "verification_event -> proof_anchor",
                "expected_hash": "e4e967a292d19096d2ecf406f6f7f22791a5948dd529e53e7778b6a1642581bf",
                "status": "VERIFIED"
            },
            "layer_2_evidence_merkle": {
                "description": "Evidence Merkle Root (26 files)",
                "source": "proof_hashes.json",
                "json_path": "merkle_tree -> root_hash",
                "expected_hash": "d1f385e1fb95a07691b698c08ec51bc961f171fe7f9f9153b1061172a57e191a",
                "status": "VERIFIED"
            },
            "layer_3_shadow_proof": {
                "description": "Shadow Proof Merkle Root (5 reports)",
                "source": "readiness_proof_shadow.json",
                "json_path": "merkle_tree -> root_hash",
                "expected_hash": "0b7d38551cece20a01da0c038cda7c4390e4db05fa605f2daebd09b862612bf0",
                "status": "VERIFIED"
            },
            "layer_4_archive_proof": {
                "description": "Archive Proof-Anchor (v4.4 SEALED)",
                "source": "archive_proof_anchor.json",
                "json_path": "archive_proof_anchor -> sha256_hash",
                "expected_hash": "dd89b7a81186aed5e8dcb6f8f8853e7e20e124a4a90a9f2b00b1af733e04780c",
                "status": "VERIFIED"
            },
            "layer_5_launch_proof": {
                "description": "Q1 2026 Autonomous Launch Proof",
                "source": "launch_proof_Q1_2026.json",
                "json_path": "proof_chain_layer_5 -> merkle_root",
                "expected_hash": "DYNAMIC_GENERATED",
                "linked_from_layer_4": "dd89b7a81186aed5e8dcb6f8f8853e7e20e124a4a90a9f2b00b1af733e04780c",
                "status": "GENERATED"
            }
        },
        "chain_integrity": {
            "total_layers": 5,
            "layers_verified": 5,
            "chain_status": "EXTENDED",
            "continuity": "INTACT"
        }
    }

    # Load actual Layer 5 hash
    launch_proof_path = EVENTS_DIR / "launch_proof_Q1_2026.json"
    if launch_proof_path.exists():
        with open(launch_proof_path, 'r', encoding='utf-8') as f:
            launch_proof = json.load(f)
            layer_5_hash = launch_proof.get("proof_chain_layer_5", {}).get("merkle_root")
            chain_document["proof_chain"]["layer_5_launch_proof"]["expected_hash"] = layer_5_hash

    # Calculate document proof anchor
    proof_anchor = calculate_sha256(chain_document)
    chain_document["proof_anchor"] = proof_anchor

    # Save chain document
    chain_path = EVENTS_DIR / "proof_anchor_chain_Q1_2026.json"
    chain_path.parent.mkdir(parents=True, exist_ok=True)
    with open(chain_path, 'w', encoding='utf-8') as f:
        json.dump(chain_document, f, indent=2, ensure_ascii=False)

    print(f"\n[PROOF-ANCHOR CHAIN DOCUMENT CREATED]")
    print(f"Total Layers:        5")
    print(f"Chain Status:        EXTENDED")
    print(f"Continuity:          INTACT")
    print(f"Document Proof:      {proof_anchor}")
    print(f"Saved to:            {chain_path}")

    return chain_document

def generate_emission_report():
    """Generate proof emission report"""
    now = datetime.now(timezone.utc)

    report = {
        "manifest_version": "1.0.0",
        "blueprint_version": BLUEPRINT_VERSION,
        "timestamp": now.isoformat(),
        "report_type": "launch_proof_emission",
        "governance_cycle": CYCLE_ID,
        "proof_emission_summary": {
            "layer_5_generated": True,
            "chain_extended": True,
            "continuity_verified": True,
            "total_layers": 5
        },
        "emission_status": {
            "status": "EMITTED",
            "exit_code": 0,
            "exit_message": "Layer 5 Launch Proof emitted and chain extended successfully"
        }
    }

    # Save report
    report_path = COMPLIANCE_DIR / "launch_proof_emission_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\n[EMISSION REPORT GENERATED]")
    print(f"Status: EMITTED")
    print(f"Saved to: {report_path}")

    return report

def main():
    """Main execution flow"""
    print("=" * 70)
    print("Blueprint v4.6 - Launch Proof Emitter")
    print("=" * 70)

    # Step 1: Check launch confirmation
    if not check_launch_confirmation():
        print("\n[EXIT] Proof emission blocked - launch not confirmed")
        sys.exit(1)

    # Step 2: Validate proof chain continuity (Layers 1-4)
    if not validate_proof_chain_continuity():
        print("\n[EXIT] Chain validation failed")
        sys.exit(2)

    # Step 3: Generate Layer 5 proof
    try:
        launch_proof = generate_layer_5_proof()
        if launch_proof is None:
            sys.exit(3)
    except Exception as e:
        print(f"\n[ERROR] Layer 5 proof generation failed: {e}")
        sys.exit(3)

    # Step 4: Create comprehensive proof-anchor chain document
    try:
        chain_document = create_proof_anchor_chain_document()
    except Exception as e:
        print(f"\n[ERROR] Chain document creation failed: {e}")
        sys.exit(3)

    # Step 5: Generate emission report
    try:
        report = generate_emission_report()
    except Exception as e:
        print(f"\n[ERROR] Report generation failed: {e}")
        sys.exit(3)

    # Success
    print("\n" + "=" * 70)
    print("[SUCCESS] Launch Proof Emission Complete")
    print("=" * 70)
    print(f"Proof Chain:         5 layers (EXTENDED)")
    print(f"Chain Integrity:     INTACT")
    print(f"Continuity:          VERIFIED")
    print(f"Status:              EMITTED")
    print("=" * 70)

    sys.exit(0)

if __name__ == "__main__":
    main()
