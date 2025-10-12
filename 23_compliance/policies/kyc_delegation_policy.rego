# SSID KYC Delegation Policy (OPA/Rego)
# License: GPL-3.0-or-later
# Purpose: Enforce proof-only, no-PII, provider allowlist policies

package kyc.delegation

# Default deny
default allow = false

# RULE 1: Proof-only mode enforcement
allow {
    input.mode == "proof_only"
    not has_pii_fields
    valid_provider
    valid_digest
    valid_signature
}

# RULE 2: No PII fields allowed in stored data
has_pii_fields {
    pii_fields := {"name", "given_name", "family_name", "birthdate", "birth_date", "address", "email", "phone_number", "phone", "ssn", "tax_id", "passport", "id_number", "drivers_license", "picture"}
    some field
    input.claims[field]
    pii_fields[field]
}

# RULE 3: Provider must be in allowed list
valid_provider {
    count(input.allowed_providers) == 0  # Empty list = all allowed
}

valid_provider {
    count(input.allowed_providers) > 0
    input.provider_id == input.allowed_providers[_]
}

# RULE 4: Digest must be valid SHA-256 or BLAKE2b hex
valid_digest {
    regex.match("^[a-f0-9]{64}$", input.digest)  # SHA-256
}

valid_digest {
    regex.match("^[a-f0-9]{128}$", input.digest)  # BLAKE2b
}

# RULE 5: Signature algorithm must be allowed
valid_signature {
    allowed_algos := {"RS256", "RS384", "RS512", "ES256", "ES384", "ES512", "EdDSA"}
    allowed_algos[input.signature_algorithm]
}

# RULE 6: Claims size limit
valid_claims_size {
    input.claims_size <= input.max_claim_size_bytes
}

# RULE 7: No forbidden operations in non-custody mode
no_custody_violation {
    input.no_custody_mode == true
    input.operation != "store_pii"
    input.operation != "process_payment"
    input.operation != "hold_funds"
}

# Comprehensive policy check
policy_pass {
    allow
    valid_claims_size
    no_custody_violation
}

# Audit log requirement
audit_required {
    input.operation == "callback_received"
}

audit_required {
    input.operation == "proof_verified"
}

audit_required {
    input.operation == "proof_stored"
}

# Score calculation (0-100)
compliance_score = score {
    checks := [
        allow,
        not has_pii_fields,
        valid_provider,
        valid_digest,
        valid_signature,
        valid_claims_size,
        no_custody_violation,
    ]
    passed := count([c | checks[c] == true])
    total := count(checks)
    score := (passed * 100) / total
}
