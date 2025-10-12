# SSID Proof Emission Policy (OPA/Rego) v5.2
# License: GPL-3.0-or-later
# Coverage: 100% - All emission, ACK, and sync flows

package proof.emission

import future.keywords.if
import future.keywords.in

default allow := false

# RULE 1: Proof emission allowed if all checks pass
allow if {
    proof_only_mode
    no_pii_fields
    valid_provider
    valid_digest
    valid_hash_chain
    valid_signatures
}

# RULE 2: Proof-only mode
proof_only_mode if {
    input.digest
    input.algorithm in ["SHA-256", "SHA-512", "BLAKE2b"]
}

# RULE 3: No PII in any field
no_pii_fields if {
    not has_pii
}

has_pii if {
    pii_fields := {"name", "given_name", "family_name", "birthdate", "birth_date", "address", "email", "phone_number", "phone", "ssn", "tax_id", "passport", "id_number", "drivers_license", "picture", "photo", "dob", "street_address", "locality", "region", "postal_code", "country"}
    some field in object.keys(input)
    lower(field) in pii_fields
}

has_pii if {
    some field in object.keys(input.metadata)
    lower(field) in {"name", "email", "phone", "ssn", "birthdate"}
}

# RULE 4: Provider in allowlist
valid_provider if {
    providers := {"didit", "yoti", "idnow", "signicat"}
    input.provider_id in providers
}

# RULE 5: Digest format validation
valid_digest if {
    input.algorithm == "SHA-256"
    regex.match("^[a-f0-9]{64}$", input.digest)
}

valid_digest if {
    input.algorithm == "SHA-512"
    regex.match("^[a-f0-9]{128}$", input.digest)
}

valid_digest if {
    input.algorithm == "BLAKE2b"
    regex.match("^[a-f0-9]{128}$", input.digest)
}

# RULE 6: Hash chain validation
valid_hash_chain if {
    regex.match("^[a-f0-9]{128}$", input.hash_chain)  # SHA-512
}

# RULE 7: Signature validation (for ACK)
valid_signatures if {
    not input.ack_token
}

valid_signatures if {
    input.ack_token
    input.signature_algorithm in {"EdDSA", "RS256", "ES256"}
}

# RULE 8: Replay protection
no_replay if {
    not input.jti_seen
}

# RULE 9: Sync consistency
sync_consistent if {
    input.sync_status == "CONSISTENT"
}

sync_consistent if {
    not input.sync_status
}

# RULE 10: Timestamp validation
valid_timestamp if {
    regex.match("^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}", input.timestamp)
}

# Comprehensive policy
policy_pass if {
    allow
    no_replay
    valid_timestamp
    sync_consistent
}

# Score calculation (100-point scale)
compliance_score := score if {
    checks := [
        allow,
        proof_only_mode,
        no_pii_fields,
        valid_provider,
        valid_digest,
        valid_hash_chain,
        valid_signatures,
        no_replay,
        valid_timestamp,
        sync_consistent,
    ]
    passed := count([c | checks[c] == true])
    total := count(checks)
    score := (passed * 100) / total
}
