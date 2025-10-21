# Intent Coverage – Final Audit
Timestamp: 2025-10-14T18:21:00.593969Z
Score: 95/100
Created files: []

## Checks
- ✅ present::24_meta_orchestration/registry/artifact_intent_manifest.yaml — required file must exist
- ✅ present::24_meta_orchestration/registry/subscriptions_registry.yaml — required file must exist
- ✅ present::24_meta_orchestration/registry/roadmap_manifest.yaml — required file must exist
- ✅ present::24_meta_orchestration/registry/artifact_index.json — required file must exist
- ✅ present::12_tooling/tools/intent_coverage_tracker.py — required file must exist
- ✅ present::23_compliance/guards/precommit_intent_guard.py — required file must exist
- ✅ present::23_compliance/policies/opa/intent_coverage.rego — required file must exist
- ✅ present::.github/workflows/intent_coverage_gate.yml — required file must exist
- ✅ present::11_test_simulation/tests_governance/test_intent_coverage.py — required file must exist
- ✅ present::02_audit_logging/reports/intent_coverage_report.json — required file must exist
- ✅ present::02_audit_logging/reports/intent_coverage_report.md — required file must exist
- ✅ yaml::artifact_intent_manifest
- ✅ yaml::subscriptions_registry
- ✅ yaml::roadmap_manifest
- ✅ json::artifact_index
- ✅ schema::artifact_intents_complete — missing=[]
- ✅ schema::subscriptions_registry_keys — missing=[]
- ✅ schema::roadmap_entries — first_missing=[]
- ✅ workflow::fail_on_missing_flag
- ❌ policy::intent_coverage_has_deny
- ✅ tests::import_tracker