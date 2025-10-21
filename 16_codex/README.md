# Codex

## Zweck
Structure definitions, schemas, registry manifests, and source-of-truth specifications

## Technische Fähigkeiten
- schema_registry
- structure_definitions
- manifest_registry
- version_control
- json_schema_validation
- openapi_specs

## Governance & Compliance
- **chart.yaml** → Definiert technische Spezifikationen, Abhängigkeiten und Compliance-Anforderungen
- **manifest.yaml** → Implementiert Laufzeitkonfiguration und Deployment-Parameter
- **Policies**: Stub-Status (`ready = false`)
- **Rego-Pfad**: `23_compliance/policies/16_codex_policy_stub_v6_0.rego`
- **Tests**: `11_test_simulation/tests/test_16_codex_policy_stub_v6_0.py`

## Abhängigkeiten
**Interne Abhängigkeiten:**
- 05_documentation
- 23_compliance

**Externe Abhängigkeiten:**
- {'json_schema': 'draft_2020_12'}
- {'openapi': '3.0'}

## Regulierung & Frameworks
- ISO_27001: control_a8_1_1

## Fortschrittsstatus
**Compliance Readiness Index:** 70.84 % → 78.89 % (target)
**Epistemic Certainty:** 0.95 → 0.97 (expected)

---

_Diese Datei wurde automatisch im Honest-Compliance-Modus v6.1 generiert._
