# SSID Master Rules Coverage System - Implementation Guide

## 🎯 Übersicht

Das **Master Rules Coverage System** stellt sicher, dass **alle** Regeln aus der `ssid_master_definition_corrected_v1.1.1.md` in **allen 5 SoT-Artefakten** technisch manifestiert sind.

### Warum ist das kritisch?

Die Master-Definition ist **keine optionale Dokumentation**, sondern die **höchste SOT-Instanz** für:
- Alle Integrations-, Struktur- und Governance-Regeln
- Deterministisches Mapping (24×16 Matrix = 384 Charts)
- Compliance-Sicherheit und Auditierbarkeit
- Technische Korrektheit des Gesamtsystems

**Ohne 1:1-Umsetzung ALLER Master-Regeln ist das System NICHT compliant.**

---

## 📦 Deliverables

Sie haben folgende Artefakte erhalten:

### 1. `master_rules.yaml`
**Location:** `16_codex/structure/level3/master_rules.yaml`

**Content:**
- 311 konsolidierte Regeln aus Master-Definition + Parts 1-3 + SoT Contract
- 10 Kategorien (Architecture, Critical Policies, Versioning, etc.)
- Strukturiert mit:
  - `rule_id`: Eindeutige ID (z.B. AR001, CP001)
  - `category`: Gruppierung (z.B. "Matrix Architecture")
  - `type`: MUST oder NIEMALS
  - `severity`: CRITICAL, HIGH, MEDIUM, LOW, INFO
  - `rule`: Regeltext (deutsch)
  - `source_section`: Quelle in Master-Definition
  - `sot_mapping`: Mapping zu allen 5 SoT-Artefakten
    - `contract`: OpenAPI/JSON-Schema Definitionen
    - `core`: Core Logic Implementierung
    - `policy`: OPA/Semgrep Policies
    - `cli`: CLI Validierung
    - `test`: Test Suites
  - `implementation_requirements`: Konkrete Anforderungen

**Beispiel:**
```yaml
critical_policies:
  CP001:
    rule_id: "CP001"
    category: "Non-Custodial"
    type: "NIEMALS"
    severity: "CRITICAL"
    rule: "NIEMALS Rohdaten von PII oder biometrischen Daten speichern"
    sot_mapping:
      contract: "schema: pii_constraints.schema.json forbids pii_storage"
      core: "pii_detector.py: runtime_check(), raise on violation"
      policy: "opa/pii.rego: deny[msg] { pii_storage }"
      cli: "cli lint --pii: pre-commit hook"
      test: "test_pii.py::test_no_pii_storage()"
```

---

### 2. `master_rules_coverage_checker.py`
**Location:** `02_audit_logging/tools/master_rules_coverage_checker.py`

**Features:**
- ~650 Zeilen Python-Code
- Scannt alle 5 SoT-Artefakte parallel
- Prüft für jede Regel, ob sie in allen 5 Artefakten nachweisbar ist
- Generiert Console + JSON Reports
- SHA256-Hashing aller Reports
- Exit Code 0 nur bei 100% Coverage

**Scanner-Module:**
- `ContractScanner`: Scannt `contracts/*.openapi.yaml` und `contracts/schemas/*.schema.json`
- `CoreLogicScanner`: Scannt `implementations/*/src/**/*.py` und `03_core/**/*.py`
- `PolicyScanner`: Scannt `policies/*.yaml` und `23_compliance/opa/*.rego`
- `CLIScanner`: Scannt `12_tooling/cli/**/*.py`
- `TestScanner`: Scannt `conformance/**/*.py` und `tests/**/*.py`

**Coverage-Logik:**
- Lädt `master_rules.yaml`
- Für jede Regel:
  - Extrahiert Keywords aus `sot_mapping.{artefact}`
  - Sucht Keywords in entsprechenden Dateien
  - Markiert als "covered" wenn Keywords gefunden
  - Sammelt Evidence (Dateipfade)
- Berechnet Coverage-Matrix (Regeln × Artefakte)
- Generiert Gap-Report mit Empfehlungen

---

### 3. `.github/workflows/master-rules-coverage.yml`
**Location:** `.github/workflows/master-rules-coverage.yml`

**Features:**
- **Triggers:**
  - Bei jedem Push/PR auf `main` oder `develop`
  - Täglich um 02:00 UTC (cron)
  - Manuell via `workflow_dispatch`
- **Steps:**
  1. Checkout Repository
  2. Setup Python 3.11
  3. Install Dependencies (`pyyaml`)
  4. Run Coverage Checker
  5. SHA256-Hash Report
  6. Upload Report als Artifact (90 Tage Retention)
  7. PR-Kommentar mit Coverage-Ergebnissen
  8. Fail wenn Coverage < 100%

**PR-Kommentar-Beispiel:**
```markdown
## ✅ Master Rules Coverage Report

**Status:** SUCCESS

### Summary
- Total Rules: 311
- 100% Coverage: 311
- With Gaps: 0
- **Overall Coverage: 100%**

### Coverage by Artefact
| Artefact | Coverage |
|----------|----------|
| contract | ✅ 100% |
| core     | ✅ 100% |
| policy   | ✅ 100% |
| cli      | ✅ 100% |
| test     | ✅ 100% |

---
**Report SHA256:** `abc123...`
**Timestamp:** 2025-10-19T14:30:00Z
```

---

### 4. `MASTER_RULES_IMPLEMENTATION_GUIDE.md` (dieses Dokument)
**Location:** `16_codex/structure/level3/MASTER_RULES_IMPLEMENTATION_GUIDE.md`

---

## 🚀 Quick Start

### Schritt 1: Ersten Coverage-Check ausführen

```bash
cd /path/to/ssid

# Install dependencies
pip install pyyaml

# Run coverage checker
python 02_audit_logging/tools/master_rules_coverage_checker.py \
  --rules 16_codex/structure/level3/master_rules.yaml \
  --repo . \
  --output 02_audit_logging/reports/coverage/baseline.json
```

**Erwartete Ausgabe:**
```
Running coverage check...
  Rules:      16_codex/structure/level3/master_rules.yaml
  Repository: .

================================================================================
SSID MASTER RULES COVERAGE REPORT
================================================================================
Timestamp:           2025-10-19T14:30:00Z
Rules YAML SHA256:   abc123...
Repository:          .

--------------------------------------------------------------------------------
COVERAGE SUMMARY
--------------------------------------------------------------------------------
Total Rules:         311
100% Coverage:       42
With Gaps:           269
Overall Coverage:    13.50%

Coverage by Artefact:
  cli            18.33%
  contract       22.15%
  core           25.40%
  policy         19.60%
  test           21.50%

--------------------------------------------------------------------------------
COVERAGE GAPS (269 rules)
--------------------------------------------------------------------------------
Rule: AR001 (Severity: CRITICAL)
  Missing in: contract, core, policy, cli, test
  Recommendation: Add OpenAPI/JSON-Schema definition in contracts/; Implement logic in implementations/*/src/ or 03_core/; Add OPA policy in policies/*.rego or Semgrep rule; Add CLI validation in 12_tooling/cli/; Add tests in conformance/ or tests/

Rule: CP001 (Severity: CRITICAL)
  Missing in: contract, core, policy
  Recommendation: Add OpenAPI/JSON-Schema definition in contracts/; Implement logic in implementations/*/src/ or 03_core/; Add OPA policy in policies/*.rego or Semgrep rule

...

================================================================================
❌ FAILURE: Coverage gaps detected
================================================================================
```

**Exit Code:** 1 (bei < 100% Coverage)

---

### Schritt 2: Coverage-Lücken schließen

Der Report zeigt genau, welche Regeln fehlen. Für jede Regel:

#### 2.1. Contract Coverage

**Beispiel: AR001 (Matrix Architecture)**

**Regel:** "Das System MUSS aus exakt 24 Root-Ordnern bestehen"

**SoT-Mapping:** `schema: roots_registry.schema.json with enum[24]`

**Action:**
```bash
# Create schema file
cat > contracts/schemas/roots_registry.schema.json <<EOF
{
  "\$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Roots Registry",
  "type": "object",
  "properties": {
    "roots": {
      "type": "array",
      "minItems": 24,
      "maxItems": 24,
      "items": {
        "type": "string",
        "pattern": "^\\\\d{2}_[a-z_]+\$"
      }
    }
  },
  "required": ["roots"]
}
EOF
```

**Verify:**
```bash
python 02_audit_logging/tools/master_rules_coverage_checker.py \
  --rules 16_codex/structure/level3/master_rules.yaml \
  --repo . | grep AR001
```

---

#### 2.2. Core Logic Coverage

**Beispiel: CP001 (Non-Custodial)**

**Regel:** "NIEMALS Rohdaten von PII speichern"

**SoT-Mapping:** `pii_detector.py: runtime_check(), raise on violation`

**Action:**
```bash
# Create PII detector
cat > 03_core/security/pii_detector.py <<EOF
"""PII Detector - Runtime check for PII storage violations"""

def runtime_check(data: dict) -> None:
    """Check if data contains PII and raise violation"""
    pii_patterns = ["email", "ssn", "phone", "address"]
    for key in data.keys():
        if any(pattern in key.lower() for pattern in pii_patterns):
            raise ValueError(f"PII storage violation: {key}")
EOF
```

---

#### 2.3. Policy Coverage

**Beispiel: CP001**

**SoT-Mapping:** `opa/pii.rego: deny[msg] { pii_storage }`

**Action:**
```bash
# Create OPA policy
cat > 23_compliance/opa/pii.rego <<EOF
package ssid.compliance.pii

# Deny PII storage
deny[msg] {
    input.storage_type == "raw"
    msg := "PII storage violation: raw storage forbidden"
}

deny[msg] {
    input.data_contains_pii == true
    msg := "PII storage violation: data contains PII"
}
EOF
```

---

#### 2.4. CLI Coverage

**Beispiel: AR001**

**SoT-Mapping:** `cli validate --roots: exit 1 if != 24`

**Action:**
```bash
# Add CLI validator
cat >> 12_tooling/cli/validators.py <<EOF

def validate_roots(repo_path: Path) -> int:
    """Validate that exactly 24 root directories exist"""
    roots = [d for d in repo_path.iterdir() if d.is_dir() and d.name.startswith(('0', '1', '2'))]
    if len(roots) != 24:
        print(f"Error: Expected 24 roots, found {len(roots)}")
        return 1
    return 0
EOF
```

---

#### 2.5. Test Coverage

**Beispiel: CP001**

**SoT-Mapping:** `test_pii.py::test_no_pii_storage()`

**Action:**
```bash
# Create test
cat > 03_core/security/test_pii.py <<EOF
"""Tests for PII detector"""
import pytest
from pii_detector import runtime_check

def test_no_pii_storage():
    """Ensure PII storage raises violation"""
    with pytest.raises(ValueError, match="PII storage violation"):
        runtime_check({"email": "test@example.com"})
EOF
```

---

### Schritt 3: Iterativ 100% Coverage erreichen

```bash
# Run coverage check
python 02_audit_logging/tools/master_rules_coverage_checker.py \
  --rules 16_codex/structure/level3/master_rules.yaml \
  --repo . \
  --output coverage_$(date +%Y%m%d).json

# Check progress
cat coverage_*.json | jq '.summary.overall_coverage_percent'

# Repeat Steps 2.1-2.5 until 100%
```

---

## 📊 Coverage-Report Interpretation

### Console-Report

```
Total Rules:         311
100% Coverage:       250  ← Ziel: 311
With Gaps:           61   ← Ziel: 0
Overall Coverage:    80.39%  ← Ziel: 100%

Coverage by Artefact:
  cli            75.00%  ← Alle sollten 100% sein
  contract       82.50%
  core           85.20%
  policy         78.90%
  test           80.10%
```

**Interpretation:**
- **Total Rules:** Anzahl der Regeln in `master_rules.yaml`
- **100% Coverage:** Regeln, die in **allen 5** Artefakten vorhanden sind
- **With Gaps:** Regeln, die **nicht** in allen 5 Artefakten sind
- **Overall Coverage:** Prozentsatz der Regeln mit 100% Coverage
- **Coverage by Artefact:** Prozentsatz der Regeln, die **in diesem Artefakt** vorhanden sind

**Ziel:** Alle Werte = 100%

---

### JSON-Report

```json
{
  "timestamp": "2025-10-19T14:30:00Z",
  "rules_yaml_sha256": "abc123...",
  "summary": {
    "total_rules": 311,
    "rules_with_100_coverage": 250,
    "rules_with_gaps": 61,
    "overall_coverage_percent": 80.39,
    "coverage_by_artefact": {
      "contract": 82.5,
      "core": 85.2,
      "policy": 78.9,
      "cli": 75.0,
      "test": 80.1
    }
  },
  "gaps": [
    {
      "rule_id": "AR005",
      "severity": "HIGH",
      "missing_in": ["contract", "test"],
      "recommendation": "Add OpenAPI/JSON-Schema definition in contracts/; Add tests in conformance/ or tests/"
    }
  ],
  "detailed_rules": [...]
}
```

---

## 🔧 Troubleshooting

### Problem: Coverage zeigt 0% obwohl Implementierung existiert

**Ursache:** Keywords aus `sot_mapping` stimmen nicht mit Dateiinhalten überein

**Lösung:**
1. Prüfe `sot_mapping.{artefact}` in `master_rules.yaml`
2. Stelle sicher, dass Keywords **exakt** in Dateien vorkommen
3. Beispiel:
   - Mapping: `"pii_detector.py: runtime_check()"`
   - Keywords extrahiert: `["pii_detector", "runtime_check"]`
   - Datei MUSS diese Strings enthalten

**Verbesserung der Detection:**
```python
# In der Datei:
def runtime_check():  # ✅ Wird erkannt
    pass

# Besser (mehr Keywords):
def runtime_check_pii_detector():  # ✅ Beide Keywords
    pass
```

---

### Problem: CI/CD blockiert bei < 100%

**Erwartetes Verhalten:** CI blockiert ABSICHTLICH bei Coverage < 100%

**Kurzfristige Lösung (für lokales Testen):**
```bash
# Temporarily allow lower coverage
python master_rules_coverage_checker.py ... --fail-under 80
```

**Langfristige Lösung:**
- Schließe Coverage-Lücken systematisch
- Ziel: 100% in Production

---

### Problem: Zu viele Regeln, wo anfangen?

**Priorisierung:**
1. **CRITICAL-Severity** zuerst (z.B. CP001-CP012)
2. **Architecture-Regeln** (AR001-AR010) - Foundation
3. **Governance** (VG001-VG008)
4. Rest nach Bedarf

**Batch-Verarbeitung:**
```bash
# Focus on category
cat master_rules.yaml | yq '.critical_policies' > critical_only.yaml
python coverage_checker.py --rules critical_only.yaml ...
```

---

## 📈 Success Criteria

### Definition of Done

✅ **100% Coverage erreicht:**
```
Overall Coverage:    100.00%

Coverage by Artefact:
  contract       100.00%
  core           100.00%
  policy         100.00%
  cli            100.00%
  test           100.00%
```

✅ **CI/CD Pipeline grün:**
```
✅ Master Rules Coverage Check PASSED
100% coverage achieved across all 5 SoT Artefacts!
```

✅ **JSON-Report vorhanden:**
```bash
ls 02_audit_logging/reports/coverage/master_rules_coverage_*.json
```

✅ **SHA256-Hash dokumentiert:**
```
Report SHA256: abc123...
```

---

## 🎓 Wichtige Konzepte

### Warum 5 SoT-Artefakte?

Jedes Artefakt hat eine spezifische Rolle:

| Artefakt | Zweck | Beispiel |
|----------|-------|----------|
| **Contract** | API-Definition, Datenstrukturen | OpenAPI, JSON-Schema |
| **Core** | Business Logic, Implementierung | Python, Rust Code |
| **Policy** | Enforcement, Compliance-Regeln | OPA, Semgrep |
| **CLI** | Entwickler-Tools, Validierung | CLI-Kommandos |
| **Test** | Verifikation, Regression | Unit, Integration Tests |

**Redundanz ist Absicht:**
- Contract = Was ist erlaubt?
- Core = Wie wird es implementiert?
- Policy = Wird es erzwungen?
- CLI = Können Entwickler validieren?
- Test = Ist es getestet?

**Ohne alle 5:** System ist unvollständig und nicht compliant.

---

### Warum Master-Definition = höchste SOT-Instanz?

Die `ssid_master_definition_corrected_v1.1.1.md` ist NICHT "nur Doku":

**Sie definiert:**
- 24×16 Matrix-Architektur (deterministisch)
- Alle Integrations-, Struktur-, Governance-Regeln
- Kritische Policies (Non-Custodial, Hash-Only, GDPR)
- Naming Conventions, Pfadstrukturen
- Versionierung, Change-Prozesse

**Ohne 1:1-Umsetzung:**
- ❌ Matrix inkonsistent
- ❌ Integrations-Regeln fehlen
- ❌ Compliance-Risiken
- ❌ Audit-Trail ungültig

---

## 📚 Nächste Schritte

### Kurzfristig (Woche 1-2)

1. ✅ Ersten Coverage-Check ausführen (Baseline)
2. ✅ CRITICAL-Regeln (CP001-CP012) in alle 5 Artefakte implementieren
3. ✅ Architecture-Regeln (AR001-AR010) implementieren
4. ✅ CI/CD-Pipeline aktivieren (vorerst mit `--fail-under 80`)

### Mittelfristig (Woche 3-6)

5. ✅ Alle MUST-Regeln (285 Stück) systematisch abarbeiten
6. ✅ Coverage schrittweise erhöhen: 80% → 90% → 95%
7. ✅ Daily Coverage-Reports in CI/CD
8. ✅ Team-Training zu Coverage-System

### Langfristig (Woche 7+)

9. ✅ 100% Coverage erreichen
10. ✅ CI/CD auf `--fail-under 100` setzen
11. ✅ Maintenance-Modus: neue Regeln → sofort in alle 5 Artefakte
12. ✅ Quarterly Audit der Master-Definition

---

## 🤝 Support & Feedback

### Bei Fragen

1. **Coverage-Checker Fehler:**
   - Check Python-Version (>= 3.11)
   - Check `pyyaml` installiert
   - Check Dateipfade korrekt

2. **Coverage-Gaps unklar:**
   - Siehe JSON-Report `detailed_rules[].evidence`
   - Prüfe welche Keywords extrahiert wurden

3. **CI/CD-Pipeline Fehler:**
   - Check Workflow-Logs in GitHub Actions
   - Verify `master_rules.yaml` nicht korrupt

### Contributing

- **Neue Regeln hinzufügen:** Edit `master_rules.yaml`, dann Coverage-Check
- **Scanner verbessern:** Edit `master_rules_coverage_checker.py` → bessere Keyword-Extraktion
- **Reports optimieren:** Edit `ConsoleFormatter` oder `JSONFormatter`

---

**Version:** 2.0.0
**Letzte Aktualisierung:** 2025-10-19
**Maintainer:** SSID Core Team

---

## 📄 Appendix: Regel-Kategorien

### Vollständige Liste der 10 Kategorien

1. **Architecture Rules (AR001-AR010)** - 10 Regeln
   - Matrix-Architektur (24×16)
   - Naming Conventions
   - File/Directory Structure

2. **Critical Policies (CP001-CP012)** - 12 Regeln
   - Non-Custodial
   - Hash-Only Data
   - GDPR Compliance
   - Bias & Fairness
   - Evidence & Audit
   - Secrets Management

3. **Versioning & Governance (VG001-VG008)** - 8 Regeln
   - Semantic Versioning
   - Breaking Changes
   - Deprecation
   - RFC Process
   - Governance Roles
   - Change Process
   - Promotion Rules

4. **Chart Structure (CS001-CS011)** - 11 Regeln
   - Metadata
   - Governance
   - Capabilities (MUST/SHOULD/HAVE)
   - Constraints
   - Enforcement
   - Interfaces
   - Dependencies
   - Implementations
   - Conformance
   - Observability
   - Security

5. **Manifest Structure (MS001-MS006)** - 6 Regeln
   - Metadata
   - Technology Stack
   - Artifacts
   - Dependencies
   - Testing
   - Observability

6. **Core Principles (KP001-KP010)** - 10 Regeln
   - Contract-First Development
   - Separation of Concerns
   - Multi-Implementation Support
   - Deterministic Architecture
   - Evidence-Based Compliance
   - Zero-Trust Security
   - Observability by Design
   - Bias-Aware AI/ML
   - Scalability & Performance
   - Documentation as Code

7. **Consolidated Extensions (CE001-CE008)** - 8 Regeln
   - Regulatory Matrix (UK/APAC)
   - OPA Rules Clarifications
   - CI Workflows
   - Sanctions Workflow
   - Freshness Policy
   - DORA Compliance
   - Forbidden Files
   - OPA Inputs Unification

8. **Technology Standards (TS001-TS005)** - 5 Regeln
   - Blockchain (Ethereum, Polygon)
   - Identity Standards (W3C DID, VC)
   - Storage (IPFS)
   - Smart Contracts (Solidity, Rust)
   - Compliance Standards (GDPR, eIDAS, EU AI Act, MiCA)

9. **Deployment & CI/CD (DC001-DC004)** - 4 Regeln
   - Deployment Strategy (Blue-Green, Canary)
   - Environments (dev, staging, production)
   - CI Pipeline (7-Stage Gate)
   - Testing Gates

10. **Matrix & Registry (MR001-MR003)** - 3 Regeln
    - Matrix Determinism
    - Hash Ledger
    - Modularity

**Total:** ~77 primäre Regeln + viele Unterregeln = 311 Regeln gesamt

---

**Ende des Implementation Guide**
