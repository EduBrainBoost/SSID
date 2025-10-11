#!/usr/bin/env python3
"""
Phase F-03 Merkle Root Validator & Evidence Chain Verifier
Blueprint v4.1 - Final Production Readiness Verification
"""

import hashlib
import json
from pathlib import Path
from typing import List, Tuple
from datetime import datetime

def sha256_hash(data: str) -> str:
    """Calculate SHA-256 hash of string data."""
    return hashlib.sha256(data.encode('utf-8')).hexdigest()

def build_merkle_tree(hashes: List[str]) -> Tuple[str, int]:
    """
    Build Merkle tree from list of hashes and return root + height.

    Args:
        hashes: List of SHA-256 hash strings

    Returns:
        Tuple of (merkle_root, tree_height)
    """
    if not hashes:
        return "", 0

    if len(hashes) == 1:
        return hashes[0], 1

    # Ensure even number of leaves (duplicate last if odd)
    current_level = hashes.copy()

    height = 1

    while len(current_level) > 1:
        # Ensure even count at each level
        if len(current_level) % 2 == 1:
            current_level.append(current_level[-1])

        next_level = []
        for i in range(0, len(current_level), 2):
            if i + 1 < len(current_level):
                combined = current_level[i] + current_level[i+1]
                parent_hash = sha256_hash(combined)
                next_level.append(parent_hash)
            else:
                # Shouldn't reach here, but safety check
                next_level.append(current_level[i])

        current_level = next_level
        height += 1

    return current_level[0], height

def extract_evidence_hashes(evidence_chain_path: Path) -> List[Tuple[str, str]]:
    """
    Extract all SHA-256 hashes from evidence_chain.json.

    Returns:
        List of (identifier, hash) tuples
    """
    with open(evidence_chain_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    hashes = []

    # Extract from evidence_chain section
    if 'evidence_chain' in data:
        for phase_key, phase_data in data['evidence_chain'].items():
            if 'implementations' in phase_data:
                for impl_name, impl_data in phase_data['implementations'].items():
                    if 'sha256' in impl_data:
                        hashes.append((f"{phase_key}:{impl_name}", impl_data['sha256']))

            if 'report' in phase_data:
                for report_name, report_data in phase_data['report'].items():
                    if 'sha256' in report_data:
                        hashes.append((f"{phase_key}:{report_name}", report_data['sha256']))

            if 'test_evidence' in phase_data:
                for test_name, test_data in phase_data['test_evidence'].items():
                    if 'sha256' in test_data:
                        hashes.append((f"{phase_key}:{test_name}", test_data['sha256']))

    return hashes

def validate_evidence_chain(root_dir: Path) -> dict:
    """
    Complete evidence chain validation for Phase F-03.

    Returns:
        Validation results dictionary
    """
    evidence_chain_path = root_dir / "02_audit_logging" / "reports" / "evidence_chain.json"

    print(f"[F-03] Starting Evidence Chain Validation")
    print(f"[F-03] Evidence Chain: {evidence_chain_path}")

    # Extract all hashes
    evidence_hashes = extract_evidence_hashes(evidence_chain_path)

    print(f"[F-03] Extracted {len(evidence_hashes)} evidence hashes")

    # Add critical registry hashes
    critical_hashes = [
        ("sot_to_repo_matrix", "226405e8d8f3e9ebc10b5636e5ca742c807dd5efee25a8c4aea933d0def83f99"),
        ("evidence_chain", "0a5be64231ee44fefbf9e5004f81d168c14fbc10ee45ad38428afd1b6314e101"),
        ("final_gap_report", "0c2972cc4d6a94eee8d05cc9f5d12e30662c2014e9822ea648e54e50724bfcc6"),
        ("final_coverage", "1e13148c68e53c0d84ea8e9f5e6c0bb37b571a364291cf20530acc6d40d897b4"),
        ("verification_score", "38c7a94aa160f9f1c94eeafb437e4bbd324396c51c96fe27d334b6e60c435c49"),
        ("verification_evidence", "12379b790f727539d7cd5b22513318a380fa5ec8ecfa6ec80356a98e94bc17e3"),
        ("on_chain_proof", "4b712d267c9441b967a031b1a61877ea114c79335c280c286dab9ad5b65b54dd"),
        ("phaseF_manifest", "9dc53d12b23152214dbe59a3f3d1b07cff3cca642052286ab2c4f72568afbcb4"),
        ("final_compliance_confirmation", "b401d9a5628abfc0a659607fc630f7c8d0be599dc370630658d2cb32b49e0b11"),
        ("health_check_template", "253d67537da73b2acc180fee7e82a245eae2aa50db889f386074b3cb82bda884"),
        ("cache_layer", "a27655a19c9c50da633d23326b9b9bd37cbf170068abe4adc2e371028ff14581"),
        ("resilience_tests", "6832495d7aacee14057b0f58864263555956198d8dc2f4f0a665feca923a952d"),
        ("multi_region_config", "161ff7e9a3f669fea526269bbbd853966aeae35d971eba282ca5b8d3036e906f"),
        ("explainability_report", "1725914ba60a7cb1461a5171a7375a036d01100796be10886dd8f89acff96139"),
        ("quantum_crypto", "571865f67e95ef11fed66f16044145fd8ff2e94e38b512c58ca8ae52a42d3a14"),
    ]

    all_hashes = evidence_hashes + critical_hashes

    print(f"[F-03] Total evidence entries (including critical registry): {len(all_hashes)}")

    # Build Merkle tree
    hash_list = [h[1] for h in all_hashes]
    merkle_root, tree_height = build_merkle_tree(hash_list)

    print(f"[F-03] Merkle Tree Height: {tree_height}")
    print(f"[F-03] Merkle Root: {merkle_root}")

    # Validate against expected root
    expected_root = "a51bc3f7b03c54d9e7d3a2b12e447fa9d4f94a6d6b2e00a94a17ed991f22238f"
    root_match = (merkle_root == expected_root)

    print(f"[F-03] Expected Root: {expected_root}")
    print(f"[F-03] Root Match: {'PASS' if root_match else 'FAIL'}")

    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "total_evidence_entries": len(all_hashes),
        "evidence_chain_entries": len(evidence_hashes),
        "critical_registry_entries": len(critical_hashes),
        "merkle_root": merkle_root,
        "expected_root": expected_root,
        "root_match": root_match,
        "tree_height": tree_height,
        "validation_status": "PASS" if root_match else "FAIL",
        "all_hashes": all_hashes
    }

if __name__ == "__main__":
    root = Path(r"C:\Users\bibel\Documents\Github\SSID")
    result = validate_evidence_chain(root)

    print("\n" + "="*80)
    print("FINAL VALIDATION RESULT")
    print("="*80)
    print(f"Total Evidence Entries: {result['total_evidence_entries']}")
    print(f"Merkle Root: {result['merkle_root']}")
    print(f"Validation Status: {result['validation_status']}")
    print("="*80)

    # Save result
    output_path = root / "24_meta_orchestration" / "registry" / "logs" / "merkle_validation_f03.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2)

    print(f"\nValidation result saved to: {output_path}")
