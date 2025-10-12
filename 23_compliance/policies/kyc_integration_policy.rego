# SSID KYC Integration Policy (OPA/Rego)
# License: GPL-3.0-or-later
# Purpose: Enforce interface separation and PII-free constraints for Layer 14 ↔ Layer 9

package kyc.integration

import future.keywords.if
import future.keywords.in

# Default deny
default allow := false

# RULE 1: Integration allowed if all checks pass
allow if {
    proof_only_mode
    no_pii_fields
    valid_provider
    valid_digest_format
    valid_timestamp
    valid_policy_version
}

# RULE 2: Proof-only mode enforcement
proof_only_mode if {
    input.digest
    input.algorithm
    input.algorithm in ["SHA-256", "BLAKE2b"]
}

# RULE 3: No PII fields in payload
no_pii_fields if {
    not has_pii_in_metadata
}

has_pii_in_metadata if {
    pii_fields := {"name", "given_name", "family_name", "birthdate", "birth_date", "address", "email", "phone_number", "phone", "ssn", "tax_id", "passport", "id_number", "drivers_license", "picture"}
    some field in object.keys(input.metadata)
    lower(field) in pii_fields
}

# RULE 4: Provider in allowlist
valid_provider if {
    allowed_providers := {"didit", "yoti", "idnow", "signicat"}
    input.provider_id in allowed_providers
}

# RULE 5: Digest format validation
valid_digest_format if {
    input.algorithm == "SHA-256"
    regex.match("^[a-f0-9]{64}$", input.digest)
}

valid_digest_format if {
    input.algorithm == "BLAKE2b"
    regex.match("^[a-f0-9]{128}$", input.digest)
}

# RULE 6: Timestamp format validation
valid_timestamp if {
    regex.match("^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(Z|[+-]\\d{2}:\\d{2})$", input.timestamp)
}

# RULE 7: Policy version format
valid_policy_version if {
    regex.match("^\\d+\\.\\d+$", input.policy_version)
}

# RULE 8: Session ID and Proof ID format (UUID)
valid_identifiers if {
    regex.match("^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", input.session_id)
    regex.match("^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", input.proof_id)
}

# RULE 9: Evidence chain validation (optional)
valid_evidence_chain if {
    not input.evidence_chain
}

valid_evidence_chain if {
    is_array(input.evidence_chain)
    count(input.evidence_chain) <= 100
}

# RULE 10: Metadata size limit
valid_metadata_size if {
    count(input.metadata) <= 50
}

# Comprehensive policy check
policy_pass if {
    allow
    valid_identifiers
    valid_evidence_chain
    valid_metadata_size
}

# Layer separation enforcement
layer_separation_ok if {
    # Ensure no direct database access from Layer 14
    not input.direct_db_access
    # Ensure interface-only communication
    input.via_interface == true
}

# Audit requirement
audit_required if {
    input.event in ["digest_emitted", "digest_emission_failed", "digest_emission_error"]
}

# Compliance score calculation
compliance_score := score if {
    checks := [
        allow,
        proof_only_mode,
        no_pii_fields,
        valid_provider,
        valid_digest_format,
        valid_timestamp,
        valid_policy_version,
        valid_identifiers,
        valid_evidence_chain,
        valid_metadata_size,
        layer_separation_ok,
    ]
    passed := count([c | checks[c] == true])
    total := count(checks)
    score := (passed * 100) / total
}
