# SSID v11.0 Interfederation Guard Policy
# Purpose: Precondition validation for interfederation execution
# Mode: SPEC_ONLY enforcement until prerequisites met
# Framework: Root-24-LOCK v1.0 + Meta-Continuum v11.0

package ssid.interfederation.guard

import future.keywords.if
import future.keywords.in

# Default deny
default allow = false

# Execution mode validation
valid_modes := {"SPEC_ONLY", "EXECUTION_READY", "CERTIFIED"}

# Precondition: Two distinct certified systems required
preconditions_met if {
    input.mode == "SPEC_ONLY"
    input.spec_complete == true
}

preconditions_met if {
    input.mode == "EXECUTION_READY"
    input.systems_count >= 2
    all_systems_certified
    distinct_pqc_keys
    distinct_merkle_roots
    sot_definitions_present
}

# All systems must have valid certifications
all_systems_certified if {
    count(input.systems) >= 2
    every system in input.systems {
        system.certified == true
        system.root_24_lock_score >= 95
        system.pqc_proof_verified == true
    }
}

# Each system must have distinct PQC keys
distinct_pqc_keys if {
    count({key | some system in input.systems; key := system.pqc_public_key}) == count(input.systems)
}

# Each system must have distinct Merkle roots
distinct_merkle_roots if {
    count({root | some system in input.systems; root := system.merkle_root}) == count(input.systems)
}

# SoT definitions must be present for all systems
sot_definitions_present if {
    every system in input.systems {
        system.sot_path != ""
        system.codex_loaded == true
    }
}

# Allow only in SPEC_ONLY mode or when all preconditions met
allow if {
    input.mode in valid_modes
    preconditions_met
}

# Violation tracking
violations[msg] {
    input.mode == "EXECUTION_READY"
    count(input.systems) < 2
    msg := "Interfederation requires at least 2 certified systems"
}

violations[msg] {
    input.mode == "EXECUTION_READY"
    not all_systems_certified
    msg := "All systems must be certified with Root-24-LOCK >= 95"
}

violations[msg] {
    input.mode == "EXECUTION_READY"
    not distinct_pqc_keys
    msg := "Each system must have distinct PQC key pair"
}

violations[msg] {
    input.mode == "EXECUTION_READY"
    not distinct_merkle_roots
    msg := "Each system must have distinct Merkle root"
}

violations[msg] {
    input.mode == "EXECUTION_READY"
    not sot_definitions_present
    msg := "All systems must have loaded SoT definitions"
}

# Execution gate
execution_allowed if {
    allow
    input.mode == "EXECUTION_READY"
    count(violations) == 0
}

# Spec-only gate (always passes when spec is complete)
spec_only_allowed if {
    allow
    input.mode == "SPEC_ONLY"
}
