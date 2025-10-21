# SoT (Single Source of Truth) Validator System

## Überblick

Das SoT-Validator-System implementiert das **Single Source of Truth Principle** für alle Compliance-Regeln aus `SSID_structure_level3_part3_MAX.md` (Zeilen 23-88).

### SoT-Prinzip

```
JEDE REGEL = WISSENSCHAFTLICHE GRUNDLAGE + TECHNISCHE MANIFESTATION
```

Für **jede der 13 SoT-Regeln** existieren:

1. **Python-Modul** (`03_core/validators/sot/`)
2. **Rego-Policy** (`23_compliance/policies/sot/`)
3. **YAML-Contract** (`16_codex/contracts/sot/`)
4. **CLI-Command** (`12_tooling/cli/sot_validator.py`)
5. **Test-Coverage** (`11_test_simulation/tests_compliance/test_sot_rules.py`)

## 13 SoT-Regeln

### Globale Grundsteine (Regeln 1-5)

| Regel-ID | Name | Wissenschaftliche Grundlage | Technische Manifestation |
|----------|------|------------------------------|--------------------------|
| SOT-001 | Version Format | Semantic Versioning 2.0.0 | `validate_version_format()` |
| SOT-002 | Date Format | ISO 8601:2004 | `validate_date_format()` |
| SOT-003 | Deprecated Flag | Boolean Logic | `validate_deprecated_flag()` |
| SOT-004 | Regulatory Basis | Regulatory Provenance Tracking | `validate_regulatory_basis()` |
| SOT-005 | Classification | ISO/IEC 27001:2022 | `validate_classification()` |

### FATF Travel Rule (Regeln 6-7)

| Regel-ID | Name | Wissenschaftliche Grundlage | Technische Manifestation |
|----------|------|------------------------------|--------------------------|
| SOT-006 | IVMS101-2023 | FATF R.16 + IVMS101 (2023) | `validate_ivms101_2023()` |
| SOT-007 | FATF R.16 2025 Update | FATF R.16 (June 2025) | `validate_fatf_rec16_2025_update()` |

### OECD CARF (Regel 8)

| Regel-ID | Name | Wissenschaftliche Grundlage | Technische Manifestation |
|----------|------|------------------------------|--------------------------|
| SOT-008 | OECD CARF XML Schema | OECD CARF User Guide (July 2025) | `validate_xml_schema_2025_07()` |

### ISO Standards (Regel 9)

| Regel-ID | Name | Wissenschaftliche Grundlage | Technische Manifestation |
|----------|------|------------------------------|--------------------------|
| SOT-009 | ISO 24165 DTI | ISO 24165-2:2025 | `validate_iso24165_dti()` |

### Global Standards (Regeln 10-12)

| Regel-ID | Name | Wissenschaftliche Grundlage | Technische Manifestation |
|----------|------|------------------------------|--------------------------|
| SOT-010 | FSB Stablecoins 2023 | FSB Stablecoin Regulations | `validate_fsb_stablecoins_2023()` |
| SOT-011 | IOSCO Crypto Markets | IOSCO Crypto-Asset Policies | `validate_iosco_crypto_markets_2023()` |
| SOT-012 | NIST AI RMF 1.0 | NIST AI RMF 1.0 | `validate_nist_ai_rmf_1_0()` |

### Deprecation Tracking (Regel 13)

| Regel-ID | Name | Wissenschaftliche Grundlage | Technische Manifestation |
|----------|------|------------------------------|--------------------------|
| SOT-013 | Deprecated Standards | Software Lifecycle Management | `validate_deprecated_standards_tracking()` |

## Verwendung

### 1. Python API

```python
from validators.sot.global_foundations_validators import validate_version_format

# Validiere Version
valid, msg = validate_version_format("2.0")
if valid:
    print("✅ Version valid")
else:
    print(f"❌ Version invalid: {msg}")
```

### 2. CLI Tool

```bash
# Liste alle Regeln
python 12_tooling/cli/sot_validator.py --list

# Validiere einzelne Regel
python 12_tooling/cli/sot_validator.py \
  --rule version-format \
  --input config.yaml

# Validiere alle Regeln
python 12_tooling/cli/sot_validator.py \
  --all \
  --input config.yaml \
  --verbose
```

### 3. Master Orchestrator

```bash
# Vollständige Validierung (Python + OPA + YAML)
python 24_meta_orchestration/sot_enforcement/sot_master_orchestrator.py \
  --config config.yaml \
  --output evidence.json \
  --verbose
```

### 4. OPA Policies

```bash
# Teste OPA Policy
opa test 23_compliance/policies/sot/global_foundations_policy.rego

# Evaluiere Policy
opa eval -i input.json \
  -d 23_compliance/policies/sot/global_foundations_policy.rego \
  'data.ssid.sot.global_foundations.global_foundations_valid'
```

### 5. Pytest

```bash
# Alle SoT-Tests ausführen
pytest 11_test_simulation/tests_compliance/test_sot_rules.py -v

# Einzelne Test-Klasse
pytest 11_test_simulation/tests_compliance/test_sot_rules.py::TestVersionFormat -v

# Mit Coverage
pytest 11_test_simulation/tests_compliance/test_sot_rules.py \
  --cov=03_core/validators/sot \
  --cov-report=term-missing
```

## CI/CD Integration

Das SoT-Enforcement ist vollständig in CI/CD integriert:

```yaml
# .github/workflows/ci_sot_enforcement.yml
- name: SoT Enforcement Gate
  run: |
    python 24_meta_orchestration/sot_enforcement/sot_master_orchestrator.py \
      --config config.yaml \
      --output evidence.json \
      || exit 24  # ROOT-24-LOCK violation
```

**Exit Codes:**
- `0`: Alle SoT-Regeln validiert ✅
- `24`: ROOT-24-LOCK Violation - SoT-Prinzip verletzt ❌

## Architektur

```
┌─────────────────────────────────────────────────────────────┐
│                    SoT Master Orchestrator                   │
│              24_meta_orchestration/sot_enforcement/          │
└───────────┬──────────────────────┬────────────────┬─────────┘
            │                      │                │
    ┌───────▼───────┐      ┌──────▼──────┐  ┌─────▼──────┐
    │  Python       │      │  OPA        │  │  YAML      │
    │  Validators   │      │  Policies   │  │  Contracts │
    │               │      │             │  │            │
    │  03_core/     │      │  23_comp/   │  │  16_codex/ │
    │  validators/  │      │  policies/  │  │  contracts/│
    │  sot/         │      │  sot/       │  │  sot/      │
    └───────┬───────┘      └──────┬──────┘  └─────┬──────┘
            │                     │               │
            └─────────────────────┴───────────────┘
                            │
                    ┌───────▼────────┐
                    │   CLI Tool     │
                    │   12_tooling/  │
                    │   cli/         │
                    └───────┬────────┘
                            │
                    ┌───────▼────────┐
                    │  Test Suite    │
                    │  11_test_sim/  │
                    │  tests_comp/   │
                    └────────────────┘
```

## Evidenz & Audit Trail

Alle Validierungen erzeugen WORM-konforme Evidenz:

- **Python Results**: JSON-Format mit Timestamps
- **OPA Results**: Policy-Evaluation-Logs
- **YAML Validation**: Schema-Validation-Reports
- **CI Evidence**: Workflow-Run-Artifacts

Speicherorte:
- `02_audit_logging/reports/sot_enforcement_evidence.json`
- `02_audit_logging/reports/ci_sot_enforcement_summary.json`
- `23_compliance/evidence/sot_validation/`

## Wartung & Updates

### Neue SoT-Regel hinzufügen

1. **Python Validator** erstellen:
   ```python
   # 03_core/validators/sot/new_category_validators.py
   def validate_new_rule(data: Dict[str, Any]) -> Tuple[bool, str]:
       # Implementation
       pass
   ```

2. **Rego Policy** erstellen:
   ```rego
   # 23_compliance/policies/sot/new_category_policy.rego
   package ssid.sot.new_category

   deny[msg] {
       # Rule implementation
   }
   ```

3. **YAML Contract** erstellen:
   ```yaml
   # 16_codex/contracts/sot/new_category.yaml
   sot_rule_0XX_name:
     rule_id: "SOT-0XX"
     scientific_foundation: ...
     technical_manifestation: ...
   ```

4. **CLI Integration** hinzufügen:
   ```python
   # 12_tooling/cli/sot_validator.py
   RULE_REGISTRY["new-rule"] = {
       "rule_id": "SOT-0XX",
       "validator": validate_new_rule,
       "description": "...",
       "category": "new_category"
   }
   ```

5. **Tests schreiben**:
   ```python
   # 11_test_simulation/tests_compliance/test_sot_rules.py
   class TestNewRule:
       def test_valid_new_rule(self):
           # Test implementation
           pass
   ```

## Compliance & Zertifizierung

Dieses SoT-System erfüllt:

- ✅ **ISO/IEC 27001:2022**: Information Security Management
- ✅ **NIST CSF 2.0**: Cybersecurity Framework
- ✅ **SOC 2 Type II**: Trust Services Criteria
- ✅ **GDPR Art. 25**: Privacy by Design
- ✅ **ROOT-24-LOCK**: Interne Governance-Anforderung

## Support & Kontakt

- **Issues**: GitHub Issues verwenden
- **Dokumentation**: `05_documentation/sot_system/`
- **Compliance-Team**: compliance@ssid-project.org

---

**Version**: 1.0.0
**Datum**: 2025-10-17
**Status**: ✅ PRODUCTION-READY
**Root-24-Lock**: ✅ ENFORCED
