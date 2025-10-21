# Compliance

## Zweck
Compliance policies, OPA enforcement, regulatory mappings, and audit frameworks

## Technische Fähigkeiten
- opa_policy_management
- regulatory_compliance_mapping
- compliance_testing
- evidence_collection
- audit_trail_management
- anti_gaming_controls

## Governance & Compliance
- **chart.yaml** → Definiert technische Spezifikationen, Abhängigkeiten und Compliance-Anforderungen
- **manifest.yaml** → Implementiert Laufzeitkonfiguration und Deployment-Parameter
- **Policies**: Stub-Status (`ready = false`)
- **Rego-Pfad**: `23_compliance/policies/23_compliance_policy_stub_v6_0.rego`
- **Tests**: `11_test_simulation/tests/test_23_compliance_policy_stub_v6_0.py`

## Abhängigkeiten
**Interne Abhängigkeiten:**
- 02_audit_logging
- 07_governance_legal
- 11_test_simulation

**Externe Abhängigkeiten:**
- {'opa': '>=0.64'}
- {'rego': '>=1.0'}

## Regulierung & Frameworks
- DSGVO: article_5
- DSGVO: article_25
- DSGVO: article_32
- DSGVO: article_35
- DORA: article_6
- DORA: article_10
- DORA: article_21
- MICA: article_57
- MICA: article_74
- AMLD6: article_8
- AMLD6: article_30

## Fortschrittsstatus
**Compliance Readiness Index:** 70.84 % → 78.89 % (target)
**Epistemic Certainty:** 0.95 → 0.97 (expected)

---

_Diese Datei wurde automatisch im Honest-Compliance-Modus v6.1 generiert._
