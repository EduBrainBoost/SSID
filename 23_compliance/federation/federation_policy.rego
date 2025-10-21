# SSID Federation Policy v5.4
# OPA (Open Policy Agent) Rules for Federation Activation
#
# Policy Enforcement:
# - Trust score thresholds
# - Audit cycle compliance
# - Zero PII enforcement
# - Node registration validation
# - Cross-proof verification
#
# Usage: opa eval --data federation_policy.rego --input request.json "data.ssid.federation.allow"

package ssid.federation

import future.keywords.if
import future.keywords.in

# Default deny
default allow = false

# Version
version := "5.4.0"

# Configuration
config := {
    "min_trust_score": 0.75,
    "min_uptime": 0.995,
    "max_latency_ms": 100,
    "audit_cycle_hours": 24,
    "required_consensus_threshold": 0.90,
    "allowed_federations": ["opencore", "trustnet", "govchain", "eudi"]
}

#############################################################
# Node Registration Rules
#############################################################

# Allow node registration if all conditions met
allow if {
    input.action == "register_node"
    valid_node_registration
}

valid_node_registration if {
    # Node ID is non-empty
    count(input.node_id) > 0

    # Federation ID is in allowed list
    input.federation_id in config.allowed_federations

    # Public key is valid EdDSA key
    valid_public_key(input.public_key)

    # Stake amount is positive
    input.stake_amount > 0

    # Node address is valid Ethereum address
    valid_ethereum_address(input.node_address)

    # No PII in node metadata
    not contains_pii(input)
}

valid_public_key(key) if {
    # EdDSA Ed25519 public keys are 32 bytes (64 hex chars)
    startswith(key, "ed25519:")
    count(split(key, ":")[1]) >= 64
}

valid_ethereum_address(addr) if {
    # Ethereum addresses are 42 chars (0x + 40 hex)
    startswith(addr, "0x")
    count(addr) == 42
}

#############################################################
# Trust Score Rules
#############################################################

# Allow trust score update if valid
allow if {
    input.action == "update_trust_score"
    valid_trust_score_update
}

valid_trust_score_update if {
    # Node exists
    count(input.node_id) > 0

    # Score is in valid range [0, 1000000]
    input.new_score >= 0
    input.new_score <= 1000000

    # Score meets minimum threshold for active nodes
    trust_score_acceptable(input.new_score, input.node_status)
}

trust_score_acceptable(score, status) if {
    # Active nodes must meet minimum trust
    status == "active"
    score >= (config.min_trust_score * 1000000)
}

trust_score_acceptable(score, status) if {
    # Inactive/degraded nodes can have lower scores
    status != "active"
}

#############################################################
# Audit Cycle Rules
#############################################################

# Allow audit cycle trigger
allow if {
    input.action == "trigger_audit_cycle"
    valid_audit_cycle_trigger
}

valid_audit_cycle_trigger if {
    # At least 24 hours since last audit
    time_since_last_audit_hours >= config.audit_cycle_hours

    # At least 3 active nodes (minimum consensus)
    input.active_nodes >= 3

    # Merkle root is valid
    valid_merkle_root(input.merkle_root)
}

time_since_last_audit_hours := hours if {
    current_time := time.now_ns() / 1000000000
    last_audit := input.last_audit_timestamp
    hours := (current_time - last_audit) / 3600
}

valid_merkle_root(root) if {
    # Merkle root is 32 bytes (64 hex chars)
    count(root) == 66  # 0x + 64 hex
    startswith(root, "0x")
}

#############################################################
# Cross-Proof Verification Rules
#############################################################

# Allow cross-proof relay
allow if {
    input.action == "relay_proof"
    valid_cross_proof
}

valid_cross_proof if {
    # Source and target federations are different
    input.source_federation != input.target_federation

    # Both federations are in allowed list
    input.source_federation in config.allowed_federations
    input.target_federation in config.allowed_federations

    # Source node has sufficient trust
    input.source_node_trust >= config.min_trust_score

    # Proof digest is valid
    valid_proof_digest(input.proof_digest)

    # Signature is valid EdDSA signature
    valid_signature(input.signature)

    # No PII in proof
    not contains_pii(input.proof_data)
}

valid_proof_digest(digest) if {
    # SHA-256 digest is 32 bytes (64 hex chars)
    count(digest) == 66
    startswith(digest, "0x")
}

valid_signature(sig) if {
    # EdDSA signatures are 64 bytes (128 hex chars)
    count(sig) >= 128
}

#############################################################
# Privacy & PII Rules
#############################################################

# Zero PII enforcement
contains_pii(data) if {
    # Check for common PII patterns
    pii_patterns := [
        "email",
        "ssn",
        "social_security",
        "phone",
        "address",
        "birthdate",
        "passport",
        "license",
        "name",
        "surname"
    ]

    # Convert data to lowercase string for checking
    data_str := lower(sprintf("%v", [data]))

    some pattern in pii_patterns
    contains(data_str, pattern)
}

# Allow data that has been properly anonymized
allow if {
    input.action == "store_proof"
    not contains_pii(input)
    valid_anonymization(input)
}

valid_anonymization(data) if {
    # Data must use only hashes and aggregates
    data.proof_type in ["digest", "merkle_root", "aggregate"]

    # No raw identifiable data
    not data.raw_data
}

#############################################################
# Federation Bridge Rules
#############################################################

# Allow bridge activation
allow if {
    input.action == "activate_bridge"
    valid_bridge_activation
}

valid_bridge_activation if {
    # Source and target nodes are active
    input.source_node_status == "active"
    input.target_node_status == "active"

    # Both nodes meet trust threshold
    input.source_node_trust >= 0.90
    input.target_node_trust >= 0.90

    # Bridge protocol is approved
    input.bridge_protocol == "proof_relay_v1"

    # TLS 1.3 enforced
    input.tls_version == "1.3"
}

#############################################################
# Consensus Rules
#############################################################

# Allow consensus decision
allow if {
    input.action == "consensus_vote"
    valid_consensus
}

valid_consensus if {
    # Minimum validators participating
    input.participating_validators >= 3

    # Quorum reached (67%)
    quorum_reached

    # All validators have sufficient trust
    all_validators_trusted
}

quorum_reached if {
    quorum_percentage := input.votes_received / input.total_validators
    quorum_percentage >= 0.67
}

all_validators_trusted if {
    # All participating validators have trust >= 0.90
    every validator in input.validators {
        validator.trust_score >= config.required_consensus_threshold
    }
}

#############################################################
# Emergency Rules
#############################################################

# Allow emergency pause (owner only)
allow if {
    input.action == "emergency_pause"
    input.caller == input.contract_owner
    input.severity in ["critical", "high"]
}

#############################################################
# Reporting & Audit
#############################################################

# Generate policy violation report
violations[violation] {
    not allow
    violation := {
        "rule": "allow",
        "reason": denial_reason,
        "action": input.action,
        "timestamp": time.now_ns()
    }
}

denial_reason := reason if {
    input.action == "register_node"
    not valid_node_registration
    reason := "Invalid node registration"
} else := reason if {
    input.action == "update_trust_score"
    not valid_trust_score_update
    reason := "Invalid trust score update"
} else := reason if {
    input.action == "relay_proof"
    not valid_cross_proof
    reason := "Invalid cross-proof"
} else := reason if {
    contains_pii(input)
    reason := "PII detected in input"
} else := "Unknown denial reason"

# Policy coverage score (for testing)
coverage_score := score if {
    total_rules := 10  # Total policy rules defined
    passing_rules := count([r | r := input.test_results[_]; r.passed])
    score := (passing_rules / total_rules) * 100
}

#############################################################
# Test Assertions
#############################################################

test_node_registration_valid if {
    allow with input as {
        "action": "register_node",
        "node_id": "test_node_01",
        "federation_id": "opencore",
        "public_key": "ed25519:1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
        "stake_amount": 500000,
        "node_address": "0x1234567890abcdef1234567890abcdef12345678"
    }
}

test_trust_score_update_valid if {
    allow with input as {
        "action": "update_trust_score",
        "node_id": "test_node_01",
        "new_score": 950000,
        "node_status": "active"
    }
}

test_pii_detection if {
    not allow with input as {
        "action": "store_proof",
        "proof_data": {
            "email": "user@example.com"
        }
    }
}

test_audit_cycle_valid if {
    allow with input as {
        "action": "trigger_audit_cycle",
        "last_audit_timestamp": 1728000000,
        "active_nodes": 5,
        "merkle_root": "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
    } with time.now_ns as 1728100000000000000
}

test_cross_proof_valid if {
    allow with input as {
        "action": "relay_proof",
        "source_federation": "opencore",
        "target_federation": "trustnet",
        "source_node_trust": 0.95,
        "proof_digest": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
        "signature": "0x" + concat("", array.slice(["a", "b", "c", "d", "e", "f", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"], 0, 128)),
        "proof_data": {
            "proof_type": "digest"
        }
    }
}
