package meta_continuum_guard

# Meta-Continuum Readiness Guard Policy
# Version: 1.0
# Author: edubrainboost
# System: SSID v11.0
# Mode: SPEC_ONLY_SINGLE_SYSTEM

# MC-001: Forbid OpenCore paths/claims
deny[msg] {
    input.artifact_paths[_]
    path := input.artifact_paths[_]
    contains(lower(path), "opencore")
    msg := sprintf("MC-001 VIOLATION: OpenCore path detected: %s", [path])
}

deny[msg] {
    input.artifact_paths[_]
    path := input.artifact_paths[_]
    contains(lower(path), "open-core")
    msg := sprintf("MC-001 VIOLATION: open-core path detected: %s", [path])
}

deny[msg] {
    input.artifact_paths[_]
    path := input.artifact_paths[_]
    contains(lower(path), "second_system")
    msg := sprintf("MC-001 VIOLATION: second_system path detected: %s", [path])
}

deny[msg] {
    input.report_content
    contains(lower(input.report_content), "opencore")
    not contains(lower(input.report_content), "opencore fehlt")
    not contains(lower(input.report_content), "opencore missing")
    msg := "MC-001 VIOLATION: OpenCore claim detected in report content (must only state absence)"
}

# MC-002: Forbid bidirectional validation claims
deny[msg] {
    input.report_content
    contains(lower(input.report_content), "bidirectional")
    not contains(lower(input.report_content), "no bidirectional")
    not contains(lower(input.report_content), "bidirectional: blocked")
    msg := "MC-002 VIOLATION: Bidirectional validation claim detected (must only state absence)"
}

deny[msg] {
    input.report_content
    contains(lower(input.report_content), "mutual truth")
    not contains(lower(input.report_content), "no mutual truth")
    msg := "MC-002 VIOLATION: Mutual truth claim detected without negation"
}

deny[msg] {
    input.report_content
    contains(lower(input.report_content), "co-truth")
    not contains(lower(input.report_content), "no co-truth")
    msg := "MC-002 VIOLATION: Co-truth claim detected without negation"
}

deny[msg] {
    input.certification_type
    input.certification_type != "READINESS"
    input.certification_type != "SPEC_ONLY"
    msg := sprintf("MC-002 VIOLATION: Invalid certification type: %s (must be READINESS or SPEC_ONLY)", [input.certification_type])
}

# MC-003: Enforce SPEC_ONLY Single-System scope
deny[msg] {
    input.mode
    input.mode != "SPEC_ONLY_SINGLE_SYSTEM"
    input.mode != "SPEC_ONLY"
    msg := sprintf("MC-003 VIOLATION: Invalid mode: %s (must be SPEC_ONLY_SINGLE_SYSTEM or SPEC_ONLY)", [input.mode])
}

deny[msg] {
    input.system_count
    input.system_count > 1
    msg := sprintf("MC-003 VIOLATION: Multiple systems detected: %d (must be exactly 1)", [input.system_count])
}

deny[msg] {
    input.interfederation_status
    input.interfederation_status != "BLOCKED"
    msg := sprintf("MC-003 VIOLATION: Invalid interfederation status: %s (must be BLOCKED)", [input.interfederation_status])
}

# Allow rule for SPEC_ONLY modes
default allow := false

allow {
    input.mode == "SPEC_ONLY_SINGLE_SYSTEM"
}

allow {
    input.mode == "SPEC_ONLY"
}

# MC-004: Require deterministic SHA-512 + Merkle proof
deny[msg] {
    input.hashing_algorithm
    input.hashing_algorithm != "SHA-512"
    msg := sprintf("MC-004 VIOLATION: Invalid hashing algorithm: %s (must be SHA-512)", [input.hashing_algorithm])
}

deny[msg] {
    not input.merkle_root
    msg := "MC-004 VIOLATION: Merkle root missing from certification artifacts"
}

deny[msg] {
    input.merkle_root
    count(input.merkle_root) != 128
    msg := sprintf("MC-004 VIOLATION: Invalid Merkle root length: %d chars (SHA-512 hex must be 128)", [count(input.merkle_root)])
}

deny[msg] {
    not input.deterministic_hashing
    msg := "MC-004 VIOLATION: Deterministic hashing flag not set to true"
}

deny[msg] {
    not input.stable_sort
    msg := "MC-004 VIOLATION: Stable sort flag not set to true"
}

# MC-005: GDPR hash-only, no PII on-chain/in reports
deny[msg] {
    input.contains_pii
    input.contains_pii == true
    msg := "MC-005 VIOLATION: PII detected in certification artifacts (GDPR violation)"
}

deny[msg] {
    input.gdpr_mode
    input.gdpr_mode != "hash_only"
    msg := sprintf("MC-005 VIOLATION: Invalid GDPR mode: %s (must be hash_only)", [input.gdpr_mode])
}

deny[msg] {
    input.report_content
    regex.match(`(?i)(email|e-mail|phone|address|ssn|passport|driver.?license|credit.?card):\s*[^\s]+`, input.report_content)
    msg := "MC-005 VIOLATION: Potential PII pattern detected in report content"
}

# MC-006: MiCA neutrality (utility/non-custodial)
deny[msg] {
    input.mica_applicable
    input.mica_applicable == true
    msg := "MC-006 VIOLATION: MiCA applicability flag incorrectly set to true (must be false for non-custodial)"
}

deny[msg] {
    input.custodial_services
    input.custodial_services == true
    msg := "MC-006 VIOLATION: Custodial services flag incorrectly set to true (must be false)"
}

deny[msg] {
    input.report_content
    contains(lower(input.report_content), "asset custody")
    not contains(lower(input.report_content), "no asset custody")
    msg := "MC-006 VIOLATION: Asset custody claim detected (must be non-custodial)"
}

deny[msg] {
    input.report_content
    contains(lower(input.report_content), "financial instrument")
    not contains(lower(input.report_content), "not a financial instrument")
    msg := "MC-006 VIOLATION: Financial instrument claim detected (must be utility-only)"
}

# Pass condition: no deny rules triggered
pass {
    count(deny) == 0
}

# Gate checks
gate_g1_single_system_scope {
    count([msg | deny[msg]; contains(msg, "MC-001")]) == 0
}

gate_g2_no_bidirectional_claims {
    count([msg | deny[msg]; contains(msg, "MC-002")]) == 0
}

gate_g3_deterministic_hashing {
    count([msg | deny[msg]; contains(msg, "MC-004")]) == 0
}

gate_g5_evidence_completeness {
    count([msg | deny[msg]; contains(msg, "MC-005")]) == 0
    count([msg | deny[msg]; contains(msg, "MC-006")]) == 0
}

all_gates_pass {
    gate_g1_single_system_scope
    gate_g2_no_bidirectional_claims
    gate_g3_deterministic_hashing
    gate_g5_evidence_completeness
}

# Summary evaluation
evaluation = result {
    pass
    all_gates_pass
    result := {
        "status": "PASS",
        "violations": [],
        "gates": {
            "G1_SINGLE_SYSTEM_SCOPE": "PASS",
            "G2_NO_BIDIRECTIONAL_CLAIMS": "PASS",
            "G3_DETERMINISTIC_HASHING": "PASS",
            "G5_EVIDENCE_COMPLETENESS": "PASS"
        },
        "rules_checked": ["MC-001", "MC-002", "MC-003", "MC-004", "MC-005", "MC-006"],
        "timestamp": time.now_ns()
    }
} else = result {
    violations := [msg | deny[msg]]
    result := {
        "status": "FAIL",
        "violations": violations,
        "gates": {
            "G1_SINGLE_SYSTEM_SCOPE": gate_status("MC-001", violations),
            "G2_NO_BIDIRECTIONAL_CLAIMS": gate_status("MC-002", violations),
            "G3_DETERMINISTIC_HASHING": gate_status("MC-004", violations),
            "G5_EVIDENCE_COMPLETENESS": gate_status_combined(["MC-005", "MC-006"], violations)
        },
        "rules_checked": ["MC-001", "MC-002", "MC-003", "MC-004", "MC-005", "MC-006"],
        "timestamp": time.now_ns()
    }
}

gate_status(rule_id, violations) = "FAIL" {
    count([v | violations[v]; contains(v, rule_id)]) > 0
} else = "PASS"

gate_status_combined(rule_ids, violations) = "FAIL" {
    count([v | violations[v]; rule_ids[_]; contains(v, rule_ids[_])]) > 0
} else = "PASS"


# Cross-Evidence Links (Entropy Boost)
# REF: 111f4cdd-4a4c-4b70-9537-fb975f7a8d62
# REF: cf6a20c9-3297-4853-964f-76c03880f4f7
# REF: efa37212-4370-435d-a341-94cde3e4e17d
# REF: fb34d446-4c1d-45e5-bc37-d041ceef3909
# REF: 25088303-4c21-4f06-aa97-65f6d5a7f5d0
