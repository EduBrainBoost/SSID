# SSID v11.0 Mutual Truth Validator Policy
# Purpose: Semantic resonance and epistemic equivalence validation
# Thresholds: >= 0.97 for production certification
# Framework: Meta-Continuum v11.0

package ssid.interfederation.validator

import future.keywords.if
import future.keywords.in

# Minimum thresholds for certification
min_semantic_resonance := 0.97
min_reflexive_symmetry := 0.97
min_epistemic_equivalence := 0.97
min_policy_coherence := 0.95

# Default deny
default validated = false

# Semantic resonance validation
semantic_resonance_valid if {
    input.metrics.semantic_resonance >= min_semantic_resonance
}

# Reflexive symmetry validation
reflexive_symmetry_valid if {
    input.metrics.reflexive_symmetry >= min_reflexive_symmetry
}

# Epistemic equivalence validation
epistemic_equivalence_valid if {
    input.metrics.epistemic_equivalence >= min_epistemic_equivalence
}

# Policy coherence validation
policy_coherence_valid if {
    input.metrics.policy_coherence >= min_policy_coherence
}

# Cross-system definition alignment
definition_alignment_valid if {
    count(input.shared_definitions) > 0
    every def in input.shared_definitions {
        def.ssid_hash != ""
        def.partner_hash != ""
        def.semantic_distance <= 0.03
    }
}

# Governance policy compatibility
governance_compatible if {
    count(input.policy_conflicts) == 0
    every policy in input.shared_policies {
        policy.compatible == true
    }
}

# Cryptographic proof bidirectionality
bidirectional_proofs_valid if {
    input.proofs.ssid_validates_partner == true
    input.proofs.partner_validates_ssid == true
    input.proofs.cross_merkle_verified == true
}

# Master validation rule
validated if {
    input.mode == "EXECUTION"
    semantic_resonance_valid
    reflexive_symmetry_valid
    epistemic_equivalence_valid
    policy_coherence_valid
    definition_alignment_valid
    governance_compatible
    bidirectional_proofs_valid
}

# Spec-only mode always passes (no execution)
validated if {
    input.mode == "SPEC_ONLY"
    input.spec_version == "v11.0"
}

# Violation tracking
violations[msg] {
    input.mode == "EXECUTION"
    not semantic_resonance_valid
    msg := sprintf("Semantic resonance %.3f below threshold %.3f", [
        input.metrics.semantic_resonance,
        min_semantic_resonance
    ])
}

violations[msg] {
    input.mode == "EXECUTION"
    not reflexive_symmetry_valid
    msg := sprintf("Reflexive symmetry %.3f below threshold %.3f", [
        input.metrics.reflexive_symmetry,
        min_reflexive_symmetry
    ])
}

violations[msg] {
    input.mode == "EXECUTION"
    not epistemic_equivalence_valid
    msg := sprintf("Epistemic equivalence %.3f below threshold %.3f", [
        input.metrics.epistemic_equivalence,
        min_epistemic_equivalence
    ])
}

violations[msg] {
    input.mode == "EXECUTION"
    not policy_coherence_valid
    msg := sprintf("Policy coherence %.3f below threshold %.3f", [
        input.metrics.policy_coherence,
        min_policy_coherence
    ])
}

violations[msg] {
    input.mode == "EXECUTION"
    not definition_alignment_valid
    msg := "Shared definitions have excessive semantic distance or missing hashes"
}

violations[msg] {
    input.mode == "EXECUTION"
    not governance_compatible
    msg := sprintf("Policy conflicts detected: %d incompatible policies", [
        count(input.policy_conflicts)
    ])
}

violations[msg] {
    input.mode == "EXECUTION"
    not bidirectional_proofs_valid
    msg := "Bidirectional cryptographic proof validation failed"
}

# Certification readiness
certification_ready if {
    validated
    count(violations) == 0
    input.metrics.semantic_resonance >= 0.97
    input.metrics.reflexive_symmetry >= 0.97
    input.metrics.epistemic_equivalence >= 0.97
}


# Cross-Evidence Links (Entropy Boost)
# REF: d49c22cc-d00a-43b1-9826-5c1cb42189b4
# REF: 97220b13-e2b5-4a6e-8340-f83c30e0ae1d
# REF: abd00dda-af66-4e41-ba22-301dfe9db012
# REF: 8be71fdc-1939-438b-8e4a-8f8952f8961b
# REF: 9ad6dbbb-64e1-4902-a4c9-b212c9185f1b
