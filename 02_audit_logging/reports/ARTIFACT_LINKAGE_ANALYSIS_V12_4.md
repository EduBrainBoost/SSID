# SSID Artifact Linkage Analysis Report v12.4

**Generated:** 2025-10-13T21:37:50.747290Z  
**Source:** global_artifact_inventory.json  
**Min Links Filter:** 1  

---

## Executive Summary

- **Total Artifacts:** 52,217
- **Artifacts with Links:** 403 (0.8%)
- **Isolated Artifacts:** 51,814 (99.2%)
- **Hub Artifacts (>=1 links):** 403
- **Cross-Module Links:** 1,439

---

## Hub Artifacts (Top 50)

Artifacts with the most outgoing links:

| Rank | File Path | Links | Root Module |
|------|-----------|-------|-------------|
| 1 | `02_audit_logging/backups/placeholders_20251013_192628/07_governance_legal/automation/review_flow_manager.py` | 10 | 02_audit_logging |
| 2 | `02_audit_logging/backups/placeholders_20251013_192628/12_tooling/performance/cache_layer.py` | 10 | 02_audit_logging |
| 3 | `02_audit_logging/backups/placeholders_20251013_192628/23_compliance/federated_evidence/federation_node.py` | 10 | 02_audit_logging |
| 4 | `02_audit_logging/backups/placeholders_20251013_192748/07_governance_legal/automation/review_flow_manager.py` | 10 | 02_audit_logging |
| 5 | `02_audit_logging/backups/placeholders_20251013_192748/12_tooling/performance/cache_layer.py` | 10 | 02_audit_logging |
| 6 | `02_audit_logging/backups/placeholders_20251013_192748/23_compliance/federated_evidence/federation_node.py` | 10 | 02_audit_logging |
| 7 | `02_audit_logging/backups/placeholders_20251013_200559/07_governance_legal/automation/review_flow_manager.py` | 10 | 02_audit_logging |
| 8 | `02_audit_logging/backups/placeholders_20251013_192628/12_tooling/scripts/create_quarterly_release_bundle.py` | 9 | 02_audit_logging |
| 9 | `02_audit_logging/backups/placeholders_20251013_192748/12_tooling/scripts/create_quarterly_release_bundle.py` | 9 | 02_audit_logging |
| 10 | `02_audit_logging/backups/placeholders_20251013_200559/12_tooling/scripts/consensus_validator.py` | 9 | 02_audit_logging |
| 11 | `02_audit_logging/reports/artifact_inventory_builder.py` | 9 | 02_audit_logging |
| 12 | `02_audit_logging/backups/placeholders_20251013_192628/02_audit_logging/anti_gaming/circular_dependency_validator.py` | 8 | 02_audit_logging |
| 13 | `02_audit_logging/backups/placeholders_20251013_192628/02_audit_logging/shards/15_handel_transaktionen/implementations/python-tensorflow/src/main.py` | 8 | 02_audit_logging |
| 14 | `02_audit_logging/backups/placeholders_20251013_192628/03_core/shards/16_behoerden_verwaltung/implementations/python-tensorflow/src/main.py` | 8 | 02_audit_logging |
| 15 | `02_audit_logging/backups/placeholders_20251013_192628/04_deployment/shards/16_behoerden_verwaltung/implementations/python-tensorflow/src/main.py` | 8 | 02_audit_logging |
| 16 | `02_audit_logging/backups/placeholders_20251013_192628/05_documentation/shards/15_handel_transaktionen/implementations/python-tensorflow/src/main.py` | 8 | 02_audit_logging |
| 17 | `02_audit_logging/backups/placeholders_20251013_192628/06_data_pipeline/shards/12_immobilien_grundstuecke/implementations/python-tensorflow/src/main.py` | 8 | 02_audit_logging |
| 18 | `02_audit_logging/backups/placeholders_20251013_192628/07_governance_legal/shards/07_familie_soziales/implementations/python-tensorflow/src/main.py` | 8 | 02_audit_logging |
| 19 | `02_audit_logging/backups/placeholders_20251013_192628/08_identity_score/shards/01_identitaet_personen/implementations/python-tensorflow/src/main.py` | 8 | 02_audit_logging |
| 20 | `02_audit_logging/backups/placeholders_20251013_192628/09_meta_identity/shards/15_handel_transaktionen/implementations/python-tensorflow/src/main.py` | 8 | 02_audit_logging |
| 21 | `02_audit_logging/backups/placeholders_20251013_192628/10_interoperability/shards/13_unternehmen_gewerbe/implementations/python-tensorflow/src/main.py` | 8 | 02_audit_logging |
| 22 | `02_audit_logging/backups/placeholders_20251013_192628/12_tooling/shards/04_kommunikation_daten/implementations/python-tensorflow/src/main.py` | 8 | 02_audit_logging |
| 23 | `02_audit_logging/backups/placeholders_20251013_192628/13_ui_layer/shards/16_behoerden_verwaltung/implementations/python-tensorflow/src/main.py` | 8 | 02_audit_logging |
| 24 | `02_audit_logging/backups/placeholders_20251013_192628/15_infra/shards/14_vertraege_vereinbarungen/implementations/python-tensorflow/src/main.py` | 8 | 02_audit_logging |
| 25 | `02_audit_logging/backups/placeholders_20251013_192628/16_codex/shards/13_unternehmen_gewerbe/implementations/python-tensorflow/src/main.py` | 8 | 02_audit_logging |
| 26 | `02_audit_logging/backups/placeholders_20251013_192628/17_observability/shards/05_gesundheit_medizin/implementations/python-tensorflow/src/main.py` | 8 | 02_audit_logging |
| 27 | `02_audit_logging/backups/placeholders_20251013_192628/18_data_layer/shards/15_handel_transaktionen/implementations/python-tensorflow/src/main.py` | 8 | 02_audit_logging |
| 28 | `02_audit_logging/backups/placeholders_20251013_192628/19_adapters/shards/09_arbeit_karriere/implementations/python-tensorflow/src/main.py` | 8 | 02_audit_logging |
| 29 | `02_audit_logging/backups/placeholders_20251013_192628/20_foundation/shards/14_vertraege_vereinbarungen/implementations/python-tensorflow/src/main.py` | 8 | 02_audit_logging |
| 30 | `02_audit_logging/backups/placeholders_20251013_192628/21_post_quantum_crypto/shards/08_mobilitaet_fahrzeuge/implementations/python-tensorflow/src/main.py` | 8 | 02_audit_logging |
| 31 | `02_audit_logging/backups/placeholders_20251013_192628/22_datasets/shards/05_gesundheit_medizin/implementations/python-tensorflow/src/main.py` | 8 | 02_audit_logging |
| 32 | `02_audit_logging/backups/placeholders_20251013_192628/23_compliance/policy_as_code/opa_exporter.py` | 8 | 02_audit_logging |
| 33 | `02_audit_logging/backups/placeholders_20251013_192628/24_meta_orchestration/shards/09_arbeit_karriere/implementations/python-tensorflow/src/main.py` | 8 | 02_audit_logging |
| 34 | `02_audit_logging/backups/placeholders_20251013_192748/02_audit_logging/anti_gaming/circular_dependency_validator.py` | 8 | 02_audit_logging |
| 35 | `02_audit_logging/backups/placeholders_20251013_192748/02_audit_logging/shards/15_handel_transaktionen/implementations/python-tensorflow/src/main.py` | 8 | 02_audit_logging |
| 36 | `02_audit_logging/backups/placeholders_20251013_192748/03_core/shards/16_behoerden_verwaltung/implementations/python-tensorflow/src/main.py` | 8 | 02_audit_logging |
| 37 | `02_audit_logging/backups/placeholders_20251013_192748/04_deployment/shards/16_behoerden_verwaltung/implementations/python-tensorflow/src/main.py` | 8 | 02_audit_logging |
| 38 | `02_audit_logging/backups/placeholders_20251013_192748/05_documentation/shards/15_handel_transaktionen/implementations/python-tensorflow/src/main.py` | 8 | 02_audit_logging |
| 39 | `02_audit_logging/backups/placeholders_20251013_192748/06_data_pipeline/shards/12_immobilien_grundstuecke/implementations/python-tensorflow/src/main.py` | 8 | 02_audit_logging |
| 40 | `02_audit_logging/backups/placeholders_20251013_192748/07_governance_legal/shards/07_familie_soziales/implementations/python-tensorflow/src/main.py` | 8 | 02_audit_logging |
| 41 | `02_audit_logging/backups/placeholders_20251013_192748/08_identity_score/shards/01_identitaet_personen/implementations/python-tensorflow/src/main.py` | 8 | 02_audit_logging |
| 42 | `02_audit_logging/backups/placeholders_20251013_192748/09_meta_identity/shards/15_handel_transaktionen/implementations/python-tensorflow/src/main.py` | 8 | 02_audit_logging |
| 43 | `02_audit_logging/backups/placeholders_20251013_192748/10_interoperability/shards/13_unternehmen_gewerbe/implementations/python-tensorflow/src/main.py` | 8 | 02_audit_logging |
| 44 | `02_audit_logging/backups/placeholders_20251013_192748/12_tooling/shards/04_kommunikation_daten/implementations/python-tensorflow/src/main.py` | 8 | 02_audit_logging |
| 45 | `02_audit_logging/backups/placeholders_20251013_192748/13_ui_layer/shards/16_behoerden_verwaltung/implementations/python-tensorflow/src/main.py` | 8 | 02_audit_logging |
| 46 | `02_audit_logging/backups/placeholders_20251013_192748/15_infra/shards/14_vertraege_vereinbarungen/implementations/python-tensorflow/src/main.py` | 8 | 02_audit_logging |
| 47 | `02_audit_logging/backups/placeholders_20251013_192748/16_codex/shards/13_unternehmen_gewerbe/implementations/python-tensorflow/src/main.py` | 8 | 02_audit_logging |
| 48 | `02_audit_logging/backups/placeholders_20251013_192748/17_observability/shards/05_gesundheit_medizin/implementations/python-tensorflow/src/main.py` | 8 | 02_audit_logging |
| 49 | `02_audit_logging/backups/placeholders_20251013_192748/18_data_layer/shards/15_handel_transaktionen/implementations/python-tensorflow/src/main.py` | 8 | 02_audit_logging |
| 50 | `02_audit_logging/backups/placeholders_20251013_192748/19_adapters/shards/09_arbeit_karriere/implementations/python-tensorflow/src/main.py` | 8 | 02_audit_logging |

---

## Most Referenced Artifacts (Top 20)

Artifacts that are referenced by other artifacts (incoming links):

| Rank | File Path | Referenced By | Root Module |
|------|-----------|---------------|-------------|
| 1 | `typing` | 177 | unknown |
| 2 | `fastapi` | 148 | unknown |
| 3 | `hashlib` | 97 | unknown |
| 4 | `pathlib` | 95 | unknown |
| 5 | `sys` | 85 | unknown |
| 6 | `src.config` | 77 | unknown |
| 7 | `src.api.health` | 77 | unknown |
| 8 | `src.utils.hasher` | 77 | unknown |
| 9 | `uvicorn` | 77 | unknown |
| 10 | `fastapi.middleware.cors` | 77 | unknown |
| 11 | `src.api.endpoints` | 77 | unknown |
| 12 | `src.api.middleware` | 77 | unknown |
| 13 | `re` | 70 | unknown |
| 14 | `healthcheck.health_check_core` | 63 | unknown |
| 15 | `json` | 36 | unknown |
| 16 | `datetime` | 33 | unknown |
| 17 | `yaml` | 10 | unknown |
| 18 | `dataclasses` | 10 | unknown |
| 19 | `collections` | 9 | unknown |
| 20 | `enum` | 8 | unknown |

---

## Cross-Module Linkage (Top 20)

Artifacts linking between different root modules:

| Rank | Link Pattern | Count |
|------|--------------|-------|
| 1 | 02_audit_logging → unknown | 1149 |
| 2 | 03_core → unknown | 40 |
| 3 | 05_documentation → unknown | 40 |
| 4 | 06_data_pipeline → unknown | 40 |
| 5 | 14_zero_time_auth → unknown | 40 |
| 6 | 12_tooling → unknown | 37 |
| 7 | 19_adapters → unknown | 15 |
| 8 | 09_meta_identity → unknown | 12 |
| 9 | 23_compliance → unknown | 11 |
| 10 | 08_identity_score → unknown | 8 |
| 11 | 15_infra → unknown | 8 |
| 12 | 17_observability → unknown | 8 |
| 13 | 21_post_quantum_crypto → unknown | 8 |
| 14 | 10_interoperability → unknown | 5 |
| 15 | 04_deployment → unknown | 4 |
| 16 | 07_governance_legal → unknown | 4 |
| 17 | 18_data_layer → unknown | 4 |
| 18 | 22_datasets → unknown | 4 |
| 19 | 13_ui_layer → . | 1 |
| 20 | 13_ui_layer → unknown | 1 |

---

## Linkage by Artifact Type

| Artifact Type | With Links | Isolated | Total | Link Rate |
|---------------|------------|----------|-------|-----------|
| Bridge | 4 | 68 | 72 | 5.6% |
| Config | 0 | 25999 | 25999 | 0.0% |
| Doc | 0 | 782 | 782 | 0.0% |
| Hash | 0 | 1 | 1 | 0.0% |
| Other | 0 | 627 | 627 | 0.0% |
| Policy | 0 | 360 | 360 | 0.0% |
| Report | 0 | 370 | 370 | 0.0% |
| Schema | 0 | 747 | 747 | 0.0% |
| Script | 327 | 18104 | 18431 | 1.8% |
| Shell | 0 | 148 | 148 | 0.0% |
| Test | 0 | 3028 | 3028 | 0.0% |
| UI | 1 | 30 | 31 | 3.2% |
| Validator | 71 | 1477 | 1548 | 4.6% |
| WASM | 0 | 73 | 73 | 0.0% |

---

## Isolated Artifacts Sample (First 100)

Artifacts with no outgoing links:

| File Path | Type | Size (KB) | Root Module |
|-----------|------|-----------|-------------|
| `01_ai_layer/chart.yaml` | Config | 1.60 | 01_ai_layer |
| `01_ai_layer/manifest.yaml` | Config | 1.12 | 01_ai_layer |
| `01_ai_layer/module.yaml` | Config | 0.03 | 01_ai_layer |
| `01_ai_layer/predictive_compliance_ai.py` | Script | 16.08 | 01_ai_layer |
| `01_ai_layer/README.md` | Doc | 1.26 | 01_ai_layer |
| `01_ai_layer/__init__.py` | Script | 0.03 | 01_ai_layer |
| `01_ai_layer/evidence/eval_metrics.json` | Config | 0.03 | 01_ai_layer |
| `01_ai_layer/evidence/train_metrics.json` | Config | 0.03 | 01_ai_layer |
| `01_ai_layer/interconnect/bridge_23compliance.py` | Bridge | 2.45 | 01_ai_layer |
| `01_ai_layer/interconnect/bridge_compliance.py` | Bridge | 3.37 | 01_ai_layer |
| `01_ai_layer/interconnect/__init__.py` | Bridge | 0.27 | 01_ai_layer |
| `01_ai_layer/shards/01_identitaet_personen/CHANGELOG.md` | Report | 0.07 | 01_ai_layer |
| `01_ai_layer/shards/01_identitaet_personen/chart.yaml` | Config | 7.88 | 01_ai_layer |
| `01_ai_layer/shards/01_identitaet_personen/README.md` | Doc | 0.11 | 01_ai_layer |
| `01_ai_layer/shards/01_identitaet_personen/contracts/identity_matching.openapi.yaml` | Config | 3.29 | 01_ai_layer |
| `01_ai_layer/shards/01_identitaet_personen/contracts/identity_risk_scoring.openapi.yaml` | Config | 9.00 | 01_ai_layer |
| `01_ai_layer/shards/01_identitaet_personen/contracts/schemas/identity_document.schema.json` | Schema | 1.66 | 01_ai_layer |
| `01_ai_layer/shards/01_identitaet_personen/contracts/schemas/identity_evidence.schema.json` | Schema | 2.77 | 01_ai_layer |
| `01_ai_layer/shards/01_identitaet_personen/docs/security/threat_model.md` | Other | 0.20 | 01_ai_layer |
| `01_ai_layer/shards/01_identitaet_personen/implementations/python-tensorflow/manifest.yaml` | Config | 7.84 | 01_ai_layer |
| `01_ai_layer/shards/01_identitaet_personen/implementations/python-tensorflow/helm/Chart.yaml` | Config | 0.26 | 01_ai_layer |
| `01_ai_layer/shards/01_identitaet_personen/implementations/python-tensorflow/helm/values.yaml` | Config | 0.70 | 01_ai_layer |
| `01_ai_layer/shards/01_identitaet_personen/implementations/python-tensorflow/k8s/deployment.yaml` | Config | 1.39 | 01_ai_layer |
| `01_ai_layer/shards/01_identitaet_personen/implementations/python-tensorflow/k8s/hpa.yaml` | Config | 0.51 | 01_ai_layer |
| `01_ai_layer/shards/01_identitaet_personen/implementations/python-tensorflow/k8s/service.yaml` | Config | 0.27 | 01_ai_layer |
| `01_ai_layer/shards/01_identitaet_personen/implementations/python-tensorflow/src/main.py` | Script | 1.26 | 01_ai_layer |
| `01_ai_layer/shards/01_identitaet_personen/implementations/python-tensorflow/src/api/auth.py` | Script | 0.02 | 01_ai_layer |
| `01_ai_layer/shards/01_identitaet_personen/implementations/python-tensorflow/src/api/endpoints.py` | Script | 0.07 | 01_ai_layer |
| `01_ai_layer/shards/01_identitaet_personen/implementations/python-tensorflow/src/api/health.py` | Script | 1.23 | 01_ai_layer |
| `01_ai_layer/shards/01_identitaet_personen/implementations/python-tensorflow/src/api/middleware.py` | Script | 0.13 | 01_ai_layer |
| `01_ai_layer/shards/01_identitaet_personen/implementations/python-tensorflow/src/api/__init__.py` | Script | 0.00 | 01_ai_layer |
| `01_ai_layer/shards/01_identitaet_personen/implementations/python-tensorflow/src/services/identity_matcher.py` | Script | 0.02 | 01_ai_layer |
| `01_ai_layer/shards/01_identitaet_personen/implementations/python-tensorflow/src/services/identity_risk_scorer.py` | Script | 0.02 | 01_ai_layer |
| `01_ai_layer/shards/01_identitaet_personen/implementations/python-tensorflow/src/services/__init__.py` | Script | 0.00 | 01_ai_layer |
| `01_ai_layer/shards/01_identitaet_personen/implementations/python-tensorflow/src/utils/bias_monitor.py` | Script | 0.02 | 01_ai_layer |
| `01_ai_layer/shards/01_identitaet_personen/implementations/python-tensorflow/src/utils/hasher.py` | Script | 0.95 | 01_ai_layer |
| `01_ai_layer/shards/01_identitaet_personen/implementations/python-tensorflow/src/utils/pii_detector.py` | Validator | 1.11 | 01_ai_layer |
| `01_ai_layer/shards/01_identitaet_personen/implementations/python-tensorflow/src/utils/__init__.py` | Script | 0.00 | 01_ai_layer |
| `01_ai_layer/shards/01_identitaet_personen/implementations/rust-burn/README.md` | Doc | 0.08 | 01_ai_layer |
| `01_ai_layer/shards/01_identitaet_personen/policies.migrated/bias_fairness.yaml` | Config | 0.94 | 01_ai_layer |
| `01_ai_layer/shards/01_identitaet_personen/policies.migrated/evidence_audit.yaml` | Config | 0.92 | 01_ai_layer |
| `01_ai_layer/shards/01_identitaet_personen/policies.migrated/gdpr_compliance.yaml` | Config | 1.22 | 01_ai_layer |
| `01_ai_layer/shards/01_identitaet_personen/policies.migrated/hash_only_enforcement.yaml` | Config | 0.68 | 01_ai_layer |
| `01_ai_layer/shards/01_identitaet_personen/policies.migrated/no_pii_storage.yaml` | Config | 0.91 | 01_ai_layer |
| `01_ai_layer/shards/01_identitaet_personen/policies.migrated/secrets_management.yaml` | Config | 0.80 | 01_ai_layer |
| `01_ai_layer/shards/01_identitaet_personen/policies.migrated/versioning_policy.yaml` | Config | 1.02 | 01_ai_layer |
| `01_ai_layer/shards/02_dokumente_nachweise/CHANGELOG.md` | Report | 0.07 | 01_ai_layer |
| `01_ai_layer/shards/02_dokumente_nachweise/chart.yaml` | Config | 7.86 | 01_ai_layer |
| `01_ai_layer/shards/02_dokumente_nachweise/README.md` | Doc | 0.10 | 01_ai_layer |
| `01_ai_layer/shards/02_dokumente_nachweise/contracts/documents_matching.openapi.yaml` | Config | 3.29 | 01_ai_layer |
| `01_ai_layer/shards/02_dokumente_nachweise/contracts/documents_risk_scoring.openapi.yaml` | Config | 8.99 | 01_ai_layer |
| `01_ai_layer/shards/02_dokumente_nachweise/contracts/schemas/documents_document.schema.json` | Schema | 1.66 | 01_ai_layer |
| `01_ai_layer/shards/02_dokumente_nachweise/contracts/schemas/documents_evidence.schema.json` | Schema | 2.77 | 01_ai_layer |
| `01_ai_layer/shards/02_dokumente_nachweise/docs/security/threat_model.md` | Other | 0.19 | 01_ai_layer |
| `01_ai_layer/shards/02_dokumente_nachweise/implementations/python-tensorflow/manifest.yaml` | Config | 7.84 | 01_ai_layer |
| `01_ai_layer/shards/02_dokumente_nachweise/implementations/python-tensorflow/helm/Chart.yaml` | Config | 0.26 | 01_ai_layer |
| `01_ai_layer/shards/02_dokumente_nachweise/implementations/python-tensorflow/helm/values.yaml` | Config | 0.70 | 01_ai_layer |
| `01_ai_layer/shards/02_dokumente_nachweise/implementations/python-tensorflow/k8s/deployment.yaml` | Config | 1.40 | 01_ai_layer |
| `01_ai_layer/shards/02_dokumente_nachweise/implementations/python-tensorflow/k8s/hpa.yaml` | Config | 0.51 | 01_ai_layer |
| `01_ai_layer/shards/02_dokumente_nachweise/implementations/python-tensorflow/k8s/service.yaml` | Config | 0.27 | 01_ai_layer |
| `01_ai_layer/shards/02_dokumente_nachweise/implementations/python-tensorflow/src/main.py` | Script | 1.26 | 01_ai_layer |
| `01_ai_layer/shards/02_dokumente_nachweise/implementations/python-tensorflow/src/api/auth.py` | Script | 0.02 | 01_ai_layer |
| `01_ai_layer/shards/02_dokumente_nachweise/implementations/python-tensorflow/src/api/endpoints.py` | Script | 0.07 | 01_ai_layer |
| `01_ai_layer/shards/02_dokumente_nachweise/implementations/python-tensorflow/src/api/health.py` | Script | 1.23 | 01_ai_layer |
| `01_ai_layer/shards/02_dokumente_nachweise/implementations/python-tensorflow/src/api/middleware.py` | Script | 0.13 | 01_ai_layer |
| `01_ai_layer/shards/02_dokumente_nachweise/implementations/python-tensorflow/src/api/__init__.py` | Script | 0.00 | 01_ai_layer |
| `01_ai_layer/shards/02_dokumente_nachweise/implementations/python-tensorflow/src/services/documents_matcher.py` | Script | 0.02 | 01_ai_layer |
| `01_ai_layer/shards/02_dokumente_nachweise/implementations/python-tensorflow/src/services/documents_risk_scorer.py` | Script | 0.03 | 01_ai_layer |
| `01_ai_layer/shards/02_dokumente_nachweise/implementations/python-tensorflow/src/services/__init__.py` | Script | 0.00 | 01_ai_layer |
| `01_ai_layer/shards/02_dokumente_nachweise/implementations/python-tensorflow/src/utils/bias_monitor.py` | Script | 0.02 | 01_ai_layer |
| `01_ai_layer/shards/02_dokumente_nachweise/implementations/python-tensorflow/src/utils/hasher.py` | Script | 0.95 | 01_ai_layer |
| `01_ai_layer/shards/02_dokumente_nachweise/implementations/python-tensorflow/src/utils/pii_detector.py` | Validator | 1.11 | 01_ai_layer |
| `01_ai_layer/shards/02_dokumente_nachweise/implementations/python-tensorflow/src/utils/__init__.py` | Script | 0.00 | 01_ai_layer |
| `01_ai_layer/shards/02_dokumente_nachweise/implementations/rust-burn/README.md` | Doc | 0.08 | 01_ai_layer |
| `01_ai_layer/shards/02_dokumente_nachweise/policies.migrated/bias_fairness.yaml` | Config | 0.94 | 01_ai_layer |
| `01_ai_layer/shards/02_dokumente_nachweise/policies.migrated/evidence_audit.yaml` | Config | 0.92 | 01_ai_layer |
| `01_ai_layer/shards/02_dokumente_nachweise/policies.migrated/gdpr_compliance.yaml` | Config | 1.22 | 01_ai_layer |
| `01_ai_layer/shards/02_dokumente_nachweise/policies.migrated/hash_only_enforcement.yaml` | Config | 0.68 | 01_ai_layer |
| `01_ai_layer/shards/02_dokumente_nachweise/policies.migrated/no_pii_storage.yaml` | Config | 0.91 | 01_ai_layer |
| `01_ai_layer/shards/02_dokumente_nachweise/policies.migrated/secrets_management.yaml` | Config | 0.80 | 01_ai_layer |
| `01_ai_layer/shards/02_dokumente_nachweise/policies.migrated/versioning_policy.yaml` | Config | 1.02 | 01_ai_layer |
| `01_ai_layer/shards/03_zugang_berechtigungen/CHANGELOG.md` | Report | 0.07 | 01_ai_layer |
| `01_ai_layer/shards/03_zugang_berechtigungen/chart.yaml` | Config | 7.83 | 01_ai_layer |
| `01_ai_layer/shards/03_zugang_berechtigungen/README.md` | Doc | 0.10 | 01_ai_layer |
| `01_ai_layer/shards/03_zugang_berechtigungen/contracts/access_matching.openapi.yaml` | Config | 3.28 | 01_ai_layer |
| `01_ai_layer/shards/03_zugang_berechtigungen/contracts/access_risk_scoring.openapi.yaml` | Config | 8.97 | 01_ai_layer |
| `01_ai_layer/shards/03_zugang_berechtigungen/contracts/schemas/access_document.schema.json` | Schema | 1.65 | 01_ai_layer |
| `01_ai_layer/shards/03_zugang_berechtigungen/contracts/schemas/access_evidence.schema.json` | Schema | 2.75 | 01_ai_layer |
| `01_ai_layer/shards/03_zugang_berechtigungen/docs/security/threat_model.md` | Other | 0.19 | 01_ai_layer |
| `01_ai_layer/shards/03_zugang_berechtigungen/implementations/python-tensorflow/manifest.yaml` | Config | 7.83 | 01_ai_layer |
| `01_ai_layer/shards/03_zugang_berechtigungen/implementations/python-tensorflow/helm/Chart.yaml` | Config | 0.25 | 01_ai_layer |
| `01_ai_layer/shards/03_zugang_berechtigungen/implementations/python-tensorflow/helm/values.yaml` | Config | 0.70 | 01_ai_layer |
| `01_ai_layer/shards/03_zugang_berechtigungen/implementations/python-tensorflow/k8s/deployment.yaml` | Config | 1.38 | 01_ai_layer |
| `01_ai_layer/shards/03_zugang_berechtigungen/implementations/python-tensorflow/k8s/hpa.yaml` | Config | 0.51 | 01_ai_layer |
| `01_ai_layer/shards/03_zugang_berechtigungen/implementations/python-tensorflow/k8s/service.yaml` | Config | 0.26 | 01_ai_layer |
| `01_ai_layer/shards/03_zugang_berechtigungen/implementations/python-tensorflow/src/main.py` | Script | 1.25 | 01_ai_layer |
| `01_ai_layer/shards/03_zugang_berechtigungen/implementations/python-tensorflow/src/api/auth.py` | Script | 0.02 | 01_ai_layer |
| `01_ai_layer/shards/03_zugang_berechtigungen/implementations/python-tensorflow/src/api/endpoints.py` | Script | 0.07 | 01_ai_layer |
| `01_ai_layer/shards/03_zugang_berechtigungen/implementations/python-tensorflow/src/api/health.py` | Script | 1.24 | 01_ai_layer |
| `01_ai_layer/shards/03_zugang_berechtigungen/implementations/python-tensorflow/src/api/middleware.py` | Script | 0.13 | 01_ai_layer |
| ... | ... | ... | ... |
| *51,714 more isolated artifacts* | | | |

---

## Analysis Notes

- **Hub Artifacts:** High-degree nodes that link to many other artifacts
- **Most Referenced:** Critical artifacts that many others depend on
- **Cross-Module Links:** Inter-layer dependencies (important for architecture)
- **Isolated Artifacts:** May be standalone, deprecated, or require linkage analysis

---

## Audit Signature

```json
{
  "audit_version": "v12.4",
  "analysis_type": "artifact_linkage",
  "status": "ANALYSIS_COMPLETE",
  "timestamp_utc": "2025-10-13T21:37:50.747290Z",
  "total_artifacts_analyzed": 52217,
  "artifacts_with_links": 403,
  "hub_artifacts": 403
}
```

*Generated by SSID Artifact Linkage Analyzer v12.4*