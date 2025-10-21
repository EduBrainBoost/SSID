# Core

## Zweck
Core service logic including DID management, proof aggregation, and transaction processing

## Technische Fähigkeiten
- did_lifecycle_management
- verifiable_credential_issuance
- proof_aggregation
- transaction_processing
- smart_contract_integration
- cryptographic_operations

## Governance & Compliance
- **chart.yaml** → Definiert technische Spezifikationen, Abhängigkeiten und Compliance-Anforderungen
- **manifest.yaml** → Implementiert Laufzeitkonfiguration und Deployment-Parameter
- **Policies**: Stub-Status (`ready = false`)
- **Rego-Pfad**: `23_compliance/policies/03_core_policy_stub_v6_0.rego`
- **Tests**: `11_test_simulation/tests/test_03_core_policy_stub_v6_0.py`

## Abhängigkeiten
**Interne Abhängigkeiten:**
- 09_meta_identity
- 14_zero_time_auth
- 02_audit_logging
- 21_post_quantum_crypto

**Externe Abhängigkeiten:**
- {'python': '>=3.11'}
- {'did_resolution_library': '>=1.0'}

## Regulierung & Frameworks
- W3C_STANDARDS: did_core_1_0
- W3C_STANDARDS: vc_data_model_1_1
- MICA: article_60
- MICA: article_74

## Fortschrittsstatus
**Compliance Readiness Index:** 70.84 % → 78.89 % (target)
**Epistemic Certainty:** 0.95 → 0.97 (expected)

---

_Diese Datei wurde automatisch im Honest-Compliance-Modus v6.1 generiert._
