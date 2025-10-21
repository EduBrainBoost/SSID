# forensic_manifest_integrity.rego
# OPA Policy for Forensic Manifest Integrity Validation
# Autor: edubrainboost ©2025 MIT License
#
# Purpose: Validate forensic evidence manifest for completeness,
#          freshness, and integrity before allowing builds to proceed.
#
# Evaluation: opa eval -d forensic_manifest_integrity.rego -i manifest.yaml "data.forensic.allow"

package forensic

import future.keywords.if
import future.keywords.in

# Default deny - must explicitly allow
default allow = false

# Allow if all integrity checks pass
allow if {
    manifest_exists
    manifest_fresh
    manifest_complete
    hashes_valid
    merkle_root_valid
}

# Check: Manifest exists and has required fields
manifest_exists if {
    input.version
    input.generated_at
    input.merkle_root
    input.evidence
}

# Check: Manifest is less than 24 hours old
manifest_fresh if {
    # Parse ISO 8601 timestamp
    manifest_time := time.parse_rfc3339_ns(input.generated_at)
    current_time := time.now_ns()

    # Calculate age in hours
    age_ns := current_time - manifest_time
    age_hours := age_ns / 1000000000 / 3600

    # Must be less than 24 hours old
    age_hours < 24
}

# Check: Manifest is complete (all expected files present)
manifest_complete if {
    # At least one evidence file must be present
    count(input.evidence) > 0

    # Total files count must match evidence array length
    input.total_files == count(input.evidence)

    # All evidence entries must have required fields
    all_entries_valid
}

all_entries_valid if {
    every entry in input.evidence {
        entry.path
        entry.sha256
        entry.size_bytes
    }
}

# Check: All hashes are valid (no ERROR_HASH_FAILED)
hashes_valid if {
    every entry in input.evidence {
        entry.sha256 != "ERROR_HASH_FAILED"
        string.length(entry.sha256) == 64  # SHA-256 is 64 hex chars
    }
}

# Check: Merkle root is valid
merkle_root_valid if {
    input.merkle_root != "EMPTY_NO_EVIDENCE"
    string.length(input.merkle_root) == 64  # SHA-256 is 64 hex chars
}

# Denial reasons for debugging
deny[msg] if {
    not manifest_exists
    msg := "Manifest is missing required fields (version, generated_at, merkle_root, evidence)"
}

deny[msg] if {
    not manifest_fresh
    msg := "Manifest is older than 24 hours - regeneration required"
}

deny[msg] if {
    count(input.evidence) == 0
    msg := "Manifest contains no evidence files"
}

deny[msg] if {
    input.total_files != count(input.evidence)
    msg := sprintf("Manifest total_files (%d) does not match evidence count (%d)", [input.total_files, count(input.evidence)])
}

deny[msg] if {
    some entry in input.evidence
    entry.sha256 == "ERROR_HASH_FAILED"
    msg := sprintf("Hash computation failed for file: %s", [entry.path])
}

deny[msg] if {
    input.merkle_root == "EMPTY_NO_EVIDENCE"
    msg := "Merkle root is empty - no evidence to validate"
}

# Additional validation: Check for duplicate hashes (collision detection)
deny[msg] if {
    # Collect all hashes
    hashes := {hash | some entry in input.evidence; hash := entry.sha256}

    # If set size is smaller than array length, there are duplicates
    count(hashes) < count(input.evidence)

    msg := "Duplicate SHA-256 hashes detected - possible hash collision or duplicate files"
}

# Additional validation: Evidence directory path must match expected location
deny[msg] if {
    input.evidence_directory != "02_audit_logging/evidence/import_resolution"
    msg := sprintf("Evidence directory mismatch: expected '02_audit_logging/evidence/import_resolution', got '%s'", [input.evidence_directory])
}

# Validation summary for reporting
validation_summary := {
    "allow": allow,
    "checks": {
        "manifest_exists": manifest_exists,
        "manifest_fresh": manifest_fresh,
        "manifest_complete": manifest_complete,
        "hashes_valid": hashes_valid,
        "merkle_root_valid": merkle_root_valid
    },
    "denial_reasons": deny,
    "evidence_count": count(input.evidence),
    "merkle_root": input.merkle_root
}

# Compliance report generation
compliance_report := {
    "policy": "forensic_manifest_integrity",
    "version": "1.0.0",
    "evaluated_at": time.now_ns(),
    "decision": allow,
    "validation_summary": validation_summary,
    "recommendation": recommendation
}

recommendation := "ALLOW_DEPLOYMENT" if allow
recommendation := "DENY_DEPLOYMENT" if not allow
