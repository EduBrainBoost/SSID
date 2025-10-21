# root_of_trust_bridging.rego
# Root-of-Trust Bridging Policy - Manifest ↔ Blockchain Verification
# Autor: edubrainboost ©2025 MIT License
#
# Purpose: Verify that on-chain RootAnchored events match off-chain
#          forensic manifest merkle roots, closing the trust gap between
#          CI/audit and blockchain.
#
# Evaluation: opa eval -d root_of_trust_bridging.rego -i verification.json "data.bridge.allow"

package bridge

import future.keywords.if
import future.keywords.in

# Default deny - explicit allow required
default allow = false

# Allow if manifest-blockchain hash match is verified
allow if {
    manifest_valid
    blockchain_event_valid
    hashes_match
    temporal_consistency
}

# Check: Manifest data is valid
manifest_valid if {
    input.manifest.merkle_root
    input.manifest.generated_at
    input.manifest.total_files > 0
    string.length(input.manifest.merkle_root) == 64
}

# Check: Blockchain event data is valid
blockchain_event_valid if {
    input.blockchain.root_hash
    input.blockchain.block_number
    input.blockchain.timestamp
    input.blockchain.event_type == "RootAnchored"
    string.length(input.blockchain.root_hash) == 64
}

# Check: Merkle roots match between manifest and blockchain
hashes_match if {
    input.manifest.merkle_root == input.blockchain.root_hash
}

# Check: Temporal consistency (manifest should precede blockchain event)
temporal_consistency if {
    manifest_time := time.parse_rfc3339_ns(input.manifest.generated_at)
    blockchain_time := input.blockchain.timestamp * 1000000000  # Convert to ns

    # Manifest must be generated before blockchain anchoring
    manifest_time <= blockchain_time

    # But not too long before (max 1 hour gap)
    time_gap_hours := (blockchain_time - manifest_time) / 1000000000 / 3600
    time_gap_hours <= 1
}

# Denial reasons for debugging
deny[msg] if {
    not manifest_valid
    msg := "Manifest data is invalid or incomplete"
}

deny[msg] if {
    not blockchain_event_valid
    msg := "Blockchain event data is invalid or incomplete"
}

deny[msg] if {
    not hashes_match
    msg := sprintf("Hash mismatch: manifest=%s, blockchain=%s", [
        substring(input.manifest.merkle_root, 0, 16),
        substring(input.blockchain.root_hash, 0, 16)
    ])
}

deny[msg] if {
    not temporal_consistency
    manifest_time := time.parse_rfc3339_ns(input.manifest.generated_at)
    blockchain_time := input.blockchain.timestamp * 1000000000

    manifest_time > blockchain_time
    msg := "Temporal inconsistency: manifest generated after blockchain event"
}

deny[msg] if {
    manifest_time := time.parse_rfc3339_ns(input.manifest.generated_at)
    blockchain_time := input.blockchain.timestamp * 1000000000
    time_gap_hours := (blockchain_time - manifest_time) / 1000000000 / 3600

    time_gap_hours > 1
    msg := sprintf("Temporal gap too large: %d hours between manifest and blockchain event", [time_gap_hours])
}

# Additional validation: Chain ID verification (if provided)
chain_id_valid if {
    not input.blockchain.chain_id  # Optional field
}

chain_id_valid if {
    input.blockchain.chain_id
    # Expected chain IDs: 1 (mainnet), 137 (polygon), 5 (goerli), etc.
    allowed_chains := {1, 137, 5, 80001, 11155111}
    input.blockchain.chain_id in allowed_chains
}

deny[msg] if {
    input.blockchain.chain_id
    not chain_id_valid
    msg := sprintf("Invalid chain ID: %d (must be mainnet, polygon, or testnet)", [input.blockchain.chain_id])
}

# Verification metadata for reporting
verification_metadata := {
    "manifest_merkle_root": input.manifest.merkle_root,
    "blockchain_root_hash": input.blockchain.root_hash,
    "hashes_match": hashes_match,
    "manifest_timestamp": input.manifest.generated_at,
    "blockchain_block": input.blockchain.block_number,
    "blockchain_timestamp": input.blockchain.timestamp,
    "chain_id": object.get(input.blockchain, "chain_id", null),
    "verification_result": allow
}

# Full verification report
verification_report := {
    "policy": "root_of_trust_bridging",
    "version": "1.0.0",
    "decision": allow,
    "checks": {
        "manifest_valid": manifest_valid,
        "blockchain_event_valid": blockchain_event_valid,
        "hashes_match": hashes_match,
        "temporal_consistency": temporal_consistency,
        "chain_id_valid": chain_id_valid
    },
    "metadata": verification_metadata,
    "denial_reasons": deny,
    "recommendation": recommendation,
    "trust_level": trust_level
}

recommendation := "TRUST_ESTABLISHED" if allow
recommendation := "TRUST_BREACH_DETECTED" if not allow

trust_level := "HIGH" if {
    allow
    input.blockchain.chain_id == 1  # Mainnet
}

trust_level := "MEDIUM" if {
    allow
    input.blockchain.chain_id != 1
    input.blockchain.chain_id != null
}

trust_level := "NONE" if not allow
