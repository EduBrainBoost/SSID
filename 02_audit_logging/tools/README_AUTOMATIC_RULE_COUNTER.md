# Automatic Rule Counter v2.0 - Dokumentation

## Überblick

Das Automatic Rule Counter System ist ein automatisches Zählungssystem, das **die gleichen Ergebnisse wie manuelle Zählung liefert**. Es zählt alle 384 Regeln über die 5 SoT-Artefakte und erstellt detaillierte Reports.

## 384 Regeln-Architektur (24×16 Matrix Alignment)

### Aufschlüsselung

**Original Rules (280):**
- AR001-AR010: Architecture Rules (10)
- CP001-CP012: Critical Policies (12)
- JURIS_BL_001-007: Blacklisted Jurisdictions (7)
- VG001-VG008: Versioning & Governance (8)
- SOT-V2-0001 to SOT-V2-0189: SOT Contract v2 Rules (189)
- **Lifted List Rules (54):**
  - PROP_TYPE_001-007: Proposal Types (7)
  - JURIS_T1_001-007: Tier 1 Markets (7)
  - REWARD_POOL_001-005: Reward Pools (5)
  - NETWORK_001-006: Blockchain Networks (6)
  - AUTH_METHOD_001-006: Authentication Methods (6)
  - PII_CAT_001-010: PII Categories (10)
  - HASH_ALG_001-004: Hash Algorithms (4)
  - RETENTION_001-005: Retention Periods (5)
  - DID_METHOD_001-004: DID Methods (4)

**Master Rules (47):**
- CS001-CS011: Chart Structure (11)
- MS001-MS006: Manifest Structure (6)
- KP001-KP010: Core Principles (10)
- CE001-CE008: Consolidated Extensions (8)
- TS001-TS005: Technology Standards (5)
- DC001-DC004: Deployment & CI/CD (4)
- MR001-MR003: Matrix & Registry (3)

**Master-Definition Rules (57 NEW):**
- MD-STRUCT-009/010: Structure Paths (2)
- MD-CHART-024/029/045/048/050: Chart Fields (5)
- MD-MANIFEST-004 to MD-MANIFEST-050: Manifest Fields (28)
- MD-POLICY-009/012/023/027/028: Critical Policies (5)
- MD-PRINC-007/009/013/018-020: Principles (6)
- MD-GOV-005 to MD-GOV-011: Governance (7)
- MD-EXT-012/014-015/018: Extensions v1.1.1 (4)

**Total:** 280 + 47 + 57 = **384 Rules** ✅

## Die 5 SoT-Artefakte

1. **Python Core Validator** (`03_core/validators/sot/sot_validator_core.py`)
   - Zählt: `def validate_*()` Funktionen
   - Patterns: `validate_ar001`, `validate_md_struct_009`, etc.

2. **OPA Policy** (`23_compliance/policies/sot/sot_policy.rego`)
   - Zählt: `deny[msg] {` Rules mit Kommentaren
   - Patterns: `# AR001:`, `# MD-STRUCT-009:`, etc.

3. **Contract YAML** (`16_codex/contracts/sot/sot_contract.yaml`)
   - Zählt: `rule_id:` Einträge
   - Patterns: `rule_id: AR001`, `rule_id: MD-STRUCT-009`, etc.

4. **Test Suite** (`11_test_simulation/tests_compliance/test_sot_validator.py`)
   - Zählt: `def test_*()` Funktionen
   - Patterns: `test_ar001`, `test_md_struct_009`, etc.

5. **CLI Tool** (`12_tooling/cli/sot_validator.py`)
   - Prüft: Integration mit Python Validator via `validate_all()`
   - Auto-kompatibel wenn Integration vorhanden

## Usage

### Basis-Verwendung

```bash
# Im Repository Root ausführen
python 02_audit_logging/tools/automatic_rule_counter.py --repo .
```

### Mit Output-Datei

```bash
python 02_audit_logging/tools/automatic_rule_counter.py \
    --repo . \
    --output coverage_report.json
```

### Strict Mode (100% erforderlich)

```bash
python 02_audit_logging/tools/automatic_rule_counter.py \
    --repo . \
    --strict
```

### Custom Threshold

```bash
python 02_audit_logging/tools/automatic_rule_counter.py \
    --repo . \
    --fail-under 95.0
```

## Output-Format

### Console Output

```
================================================================================
SSID AUTOMATIC RULE COUNT REPORT
================================================================================
Timestamp: 2025-10-20T19:58:53.627195
Total Rules: 384 (24x16 Matrix Alignment)
Overall Coverage: 66.1%
Status: [FAIL] INCOMPLETE
================================================================================

[OK] Python Core Validator:
   Total: 200/384 (52.1%)

[FAIL] OPA Policy:
   Total: 180/384 (46.9%)
   Missing Categories:
      - SOT-V2: 50/189 (139 missing)
      - MD-CHART: 3/5 (2 missing)

... (detailed breakdown for each artefact) ...

================================================================================
DETAILED CATEGORY BREAKDOWN
================================================================================

AR: 10 rules
------------------------------------------------------------
  [OK]   Python Core Validator           10/ 10
  [OK]   OPA Policy                      10/ 10
  [OK]   Contract YAML                   10/ 10
  [FAIL] Test Suite                       0/ 10
  [OK]   CLI Tool                        10/ 10

... (complete breakdown for all 28 categories) ...

================================================================================
RULE CATEGORIES LEGEND (384 Total)
================================================================================
... (full legend) ...
```

### JSON Output

```json
{
  "timestamp": "2025-10-20T19:58:53.627195",
  "total_rules": 384,
  "overall_percentage": 66.1,
  "all_complete": false,
  "artefacts": [
    {
      "name": "Python Core Validator",
      "total_expected": 384,
      "total_found": 200,
      "percentage": 52.1,
      "complete": false,
      "categories": [
        {
          "category": "AR",
          "expected": 10,
          "found": 10,
          "missing": 0,
          "complete": true,
          "percentage": 100.0,
          "evidence": ["def validate_ar001(", "def validate_ar002(", ...]
        },
        ...
      ]
    },
    ...
  ]
}
```

## Exit Codes

- **0**: Success (Coverage >= threshold)
- **1**: Failure (Coverage < threshold OR strict mode incomplete)
- **2**: Validation error (Repository not found, etc.)

## Verwendung in CI/CD

### GitHub Actions Workflow

```yaml
name: Rule Coverage Check

on: [push, pull_request]

jobs:
  coverage:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Run Rule Counter
        run: |
          python 02_audit_logging/tools/automatic_rule_counter.py \
            --repo . \
            --output coverage_report.json \
            --fail-under 100.0

      - name: Upload Report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: coverage-report
          path: coverage_report.json
```

## Fehlerdiagnose

### Häufige Probleme

1. **Unicode Encoding Errors (Windows)**
   - **Symptom:** `UnicodeEncodeError: 'charmap' codec`
   - **Lösung:** Tool verwendet jetzt ASCII-Zeichen ([OK]/[FAIL] statt ✅/❌)

2. **Falsche Zählungen**
   - **Prüfen:** Regex-Patterns in `_get_pattern()` Methoden
   - **Debug:** Einzelne Kategorie manuell zählen mit `grep`

3. **Kategorie nicht gefunden**
   - **Prüfen:** Naming-Konvention (z.B. `validate_ar001` statt `validate_AR001`)
   - **Prüfen:** Regex-Pattern für Kategorie

### Manual Verification Commands

```bash
# Python Core Validator
grep -c "def validate_ar" 03_core/validators/sot/sot_validator_core.py
grep -c "def validate_md_" 03_core/validators/sot/sot_validator_core.py

# OPA Policy
grep -c "# AR[0-9]" 23_compliance/policies/sot/sot_policy.rego
grep -c "# MD-" 23_compliance/policies/sot/sot_policy.rego

# Contract YAML
grep -c "rule_id: AR" 16_codex/contracts/sot/sot_contract.yaml
grep -c "rule_id: MD-" 16_codex/contracts/sot/sot_contract.yaml

# Test Suite
grep -c "def test_ar" 11_test_simulation/tests_compliance/test_sot_validator.py
grep -c "def test_md_" 11_test_simulation/tests_compliance/test_sot_validator.py
```

## Vergleich: Automatisch vs. Manuell

Das Tool ist so konfiguriert, dass es **die gleichen Ergebnisse wie manuelle Zählung liefert**:

| Methode | AR Rules | MD-* Rules | Total |
|---------|----------|------------|-------|
| Manuell | `grep -c "def validate_ar" ...` → 10 | `grep -c "def validate_md_" ...` → 57 | 384 |
| Automatisch | Counter findet 10 | Counter findet 57 | 384 |
| **Match** | ✅ | ✅ | ✅ |

## Regex-Patterns Referenz

### Python Core Validator Patterns

```python
"AR"         → r'def validate_ar(\d{3})\('
"CP"         → r'def validate_cp(\d{3})\('
"VG"         → r'def validate_vg_?(\d{3})\('
"SOT-V2"     → r'def validate_sot_v2_(\d{4})\('
"MD-STRUCT"  → r'def validate_md_struct_(\d+)\('
"MD-CHART"   → r'def validate_md_chart_(\d+)\('
...
```

### OPA Policy Patterns

```python
"AR"         → r'# AR(\d{3}):'
"CP"         → r'# CP(\d{3}):'
"MD-STRUCT"  → r'# MD-STRUCT-(\d+):'
"MD-CHART"   → r'# MD-CHART-(\d+):'
...
```

### Contract YAML Patterns

```python
"AR"         → r'rule_id: AR(\d{3})'
"CP"         → r'rule_id: CP(\d{3})'
"MD-STRUCT"  → r'rule_id: MD-STRUCT-(\d+)'
"MD-CHART"   → r'rule_id: MD-CHART-(\d+)'
...
```

### Test Suite Patterns

```python
"AR"         → r'def test_ar(\d{3})\('
"CP"         → r'def test_cp(\d{3})\('
"MD-STRUCT"  → r'def test_md_struct_(\d+)\('
"MD-CHART"   → r'def test_md_chart_(\d+)\('
...
```

## Erweiterung

### Neue Kategorie hinzufügen

1. **EXPECTED_COUNTS aktualisieren:**
   ```python
   EXPECTED_COUNTS = {
       ...
       "NEW_CAT": 10,  # NEW_CAT_001-010: Description
   }
   ```

2. **Pattern in allen 4 Counters hinzufügen:**
   ```python
   elif category == "NEW_CAT":
       return r'def validate_new_cat_(\d{3})\('
   ```

3. **Legend aktualisieren:**
   ```python
   print(f"  NEW_CAT: New Category (10)")
   ```

## Support

Bei Problemen:
1. Manuelle Verifikation durchführen (siehe oben)
2. JSON-Report prüfen für detaillierte Evidence
3. Issue in Repository erstellen mit:
   - Output des Tools
   - Manuelle Zählung
   - Erwartete vs. tatsächliche Zählungen

## Version History

- **v2.0** (2025-10-20): Vollständige 384-Regel-Unterstützung
  - Alle 28 Kategorien integriert
  - Windows-kompatibel (ASCII statt Unicode)
  - Detaillierte JSON-Reports
  - Strict Mode und Custom Thresholds

- **v1.0** (2025-10-19): Initial Release
  - 280 Regel-Unterstützung
  - 5 Artefakt-Zählung

---

**Author:** SSID Core Team
**Date:** 2025-10-20
**Version:** 2.0.0
**Status:** Production Ready
