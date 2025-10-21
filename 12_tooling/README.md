# Tooling

## Zweck
Development tools, scripts, CLI utilities, and automation helpers

## Technische Fähigkeiten
- cli_tools
- automation_scripts
- code_generation
- migration_tools
- debugging_utilities
- performance_profiling

## Governance & Compliance
- **chart.yaml** → Definiert technische Spezifikationen, Abhängigkeiten und Compliance-Anforderungen
- **manifest.yaml** → Implementiert Laufzeitkonfiguration und Deployment-Parameter
- **Policies**: Stub-Status (`ready = false`)
- **Rego-Pfad**: `23_compliance/policies/12_tooling_policy_stub_v6_0.rego`
- **Tests**: `11_test_simulation/tests/test_12_tooling_policy_stub_v6_0.py`

## Abhängigkeiten
**Interne Abhängigkeiten:**
- 16_codex
- 23_compliance

**Externe Abhängigkeiten:**
- {'python': '>=3.11'}
- {'bash': '>=5.0'}
- {'jq': '>=1.6'}
- {'yq': '>=4.35'}

## Regulierung & Frameworks
- ISO_27001: control_a12_4_3

## Fortschrittsstatus
**Compliance Readiness Index:** 70.84 % → 78.89 % (target)
**Epistemic Certainty:** 0.95 → 0.97 (expected)

---

_Diese Datei wurde automatisch im Honest-Compliance-Modus v6.1 generiert._
