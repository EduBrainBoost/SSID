# SSID Master Rules Coverage System - Implementation Guide

## 🎯 Übersicht

Das **Master Rules Coverage System** stellt sicher, dass **alle** Regeln aus der `ssid_master_definition_corrected_v1.1.1.md` in **allen 5 SoT-Artefakten** technisch manifestiert sind.

### Die 5 SoT-Artefakte

1. **Contract Definitions** (OpenAPI + JSON-Schema)
2. **Core Logic** (Python/Rust Implementierungen)
3. **Policy Enforcement** (OPA Rego + Semgrep)
4. **CLI Validation** (Struktur-Checks)
5. **Test Suites** (Unit/Integration/Contract Tests)

### Governance-Prinzip

**100% Coverage ist Pflicht:**
- Jede Master-Regel MUSS in allen 5 Artefakten nachweisbar sein
- Keine Ausnahmen
- Automatische CI/CD-Blockierung bei Lücken

---

## 📦 Deliverables

### 1. Extrahierte Regeln (`master_rules.yaml`)

**87 Regeln in 10 Kategorien:**
- Architecture Rules (10)
- Critical Policies (12)
- Versioning & Governance (8)
- Chart Structure (11)
- Manifest Structure (6)
- Core Principles (10)
- Consolidated Extensions (8)
- Technology Standards (5)
- Deployment & CI/CD (4)
- Matrix & Registry (3)

**Location:** Repository-Root  
**Format:** YAML mit eindeutigen Rule-IDs (AR001, CP001, etc.)

### 2. Coverage Checker (`coverage_checker.py`)

**Features:**
- ✅ Lädt alle Master-Regeln aus YAML
- ✅ Scannt Repository nach Implementierungen
- ✅ Prüft Coverage in allen 5 Artefakten
- ✅ Generiert Console + JSON Reports
- ✅ SHA256-Hashing der Reports
- ✅ Exit Code 0 nur bei 100% Coverage

**Dependencies:** `pyyaml`

### 3. CI/CD Workflow (`.github/workflows/master-rules-coverage.yml`)

**Trigger:**
- Push/PR auf main/develop
- Täglich um 02:00 UTC (scheduled)
- Manuell (workflow_dispatch)

**Features:**
- ✅ Automatische Coverage-Prüfung
- ✅ PR-Kommentare mit Coverage-Report
- ✅ Artifact-Upload (90 Tage Retention)
- ✅ Audit-Logging in `02_audit_logging/reports/`
- ✅ Badge-Update in README
- ✅ Pre-Commit Hook Generation

---

## 🚀 Setup-Anleitung

### Schritt 1: Dateien ins Repository kopieren

```bash
# Root-Level
cp master_rules.yaml /path/to/ssid/
cp coverage_checker.py /path/to/ssid/

# CI/CD Workflow
mkdir -p /path/to/ssid/.github/workflows/
cp master-rules-coverage.yml /path/to/ssid/.github/workflows/
```

### Schritt 2: Dependencies installieren

```bash
pip install pyyaml
```

### Schritt 3: Lokaler Coverage-Check

```bash
cd /path/to/ssid/

python coverage_checker.py \
  --rules master_rules.yaml \
  --repo . \
  --output coverage_report.json \
  --fail-under 100.0
```

**Expected Output:**
```
🔍 Checking coverage for 87 rules...
[1/87] AR001: Das System MUSS aus exakt 24 Root-Ordnern bestehen...
[2/87] AR002: Jeder Root-Ordner MUSS exakt 16 Shards enthalten...
...

================================================================================
SSID MASTER RULES COVERAGE REPORT
================================================================================
Timestamp: 2025-10-19T15:30:00.123456
Total Rules: 87

✅ Full Coverage:     42 (48.3%)
⚠️  Partial Coverage: 30 (34.5%)
❌ No Coverage:       15 (17.2%)

📊 Overall Coverage: 65.7%
================================================================================

📋 DETAILED RESULTS:

🔴 AR001 - Coverage: 80%
   Rule: Das System MUSS aus exakt 24 Root-Ordnern bestehen
   Contract:  ❌
   Core:      ✅
   Policy:    ✅
   CLI:       ✅
   Test:      ✅
...

❌ FAIL: Coverage 65.7% below threshold 100.0%
```

### Schritt 4: Coverage-Lücken schließen

Für jede Regel mit `< 100% Coverage`:

1. **Contract Coverage fehlt?**
   → Füge OpenAPI-Spec oder JSON-Schema in `contracts/` hinzu

2. **Core Coverage fehlt?**
   → Implementiere Logik in `implementations/*/src/`

3. **Policy Coverage fehlt?**
   → Erstelle OPA-Policy in `23_compliance/opa/*.rego`
   → Oder Semgrep-Rule in `*.semgrep.yaml`

4. **CLI Coverage fehlt?**
   → Ergänze Validator in `12_tooling/cli/`

5. **Test Coverage fehlt?**
   → Schreibe Tests in `tests/` oder `conformance/`

### Schritt 5: Re-Check

```bash
python coverage_checker.py \
  --rules master_rules.yaml \
  --repo . \
  --output coverage_report.json \
  --fail-under 100.0
```

Wiederhole Schritt 4-5, bis:
```
✅ PASS: Coverage 100.0% meets threshold 100.0%
```

### Schritt 6: CI/CD aktivieren

```bash
git add .github/workflows/master-rules-coverage.yml
git commit -m "ci: Add Master Rules Coverage Check"
git push
```

**GitHub Actions wird jetzt automatisch:**
- Bei jedem Push/PR Coverage prüfen
- Täglich um 02:00 UTC Coverage-Report erstellen
- Reports in `02_audit_logging/reports/` archivieren
- Badge in README aktualisieren

---

## 📊 Coverage-Report-Struktur

### Console Output

```
================================================================================
SSID MASTER RULES COVERAGE REPORT
================================================================================
Timestamp: 2025-10-19T15:30:00.123456
Total Rules: 87

✅ Full Coverage:     87 (100.0%)
⚠️  Partial Coverage:  0 (0.0%)
❌ No Coverage:        0 (0.0%)

📊 Overall Coverage: 100.0%
================================================================================

✅ PASS: Coverage 100.0% meets threshold 100.0%
```

### JSON Report (`coverage_report.json`)

```json
{
  "timestamp": "2025-10-19T15:30:00.123456",
  "summary": {
    "total_rules": 87,
    "full_coverage": 87,
    "partial_coverage": 0,
    "no_coverage": 0,
    "overall_percentage": 100.0
  },
  "warnings": [],
  "missing_artifacts": [],
  "results": [
    {
      "rule_id": "AR001",
      "rule_text": "Das System MUSS aus exakt 24 Root-Ordnern bestehen",
      "coverage_percentage": 100.0,
      "full_coverage": true,
      "artifacts": {
        "contract": {
          "covered": true,
          "evidence": ["Contract: structure_validation.openapi.yaml"]
        },
        "core": {
          "covered": true,
          "evidence": ["Source: 12_tooling/cli/validators/structure.py"]
        },
        "policy": {
          "covered": true,
          "evidence": ["Policy: 23_compliance/opa/structure_rules.rego"]
        },
        "cli": {
          "covered": true,
          "evidence": ["CLI: 12_tooling/cli/commands/validate.py"]
        },
        "test": {
          "covered": true,
          "evidence": ["Test: tests/test_structure_validation.py"]
        }
      }
    }
    // ... weitere 86 Regeln
  ]
}
```

### SHA256-Hash (`coverage_report.json.sha256`)

```
a3f5e9d8c7b6a5e4f3d2c1b0a9e8d7c6b5a4f3e2d1c0b9a8e7f6d5c4b3a2f1e0  coverage_report.json
```

---

## 🔧 Erweiterte Nutzung

### Custom Fail-Under Threshold

Für schrittweise Migration (nicht empfohlen für Production):

```bash
python coverage_checker.py \
  --rules master_rules.yaml \
  --repo . \
  --fail-under 80.0  # Akzeptiert 80% Coverage
```

**⚠️ Warnung:** Production MUSS immer 100% Coverage haben!

### Filtern nach Kategorie

Wenn Coverage-Report zu groß wird, kann man gezielt prüfen:

```python
# Modifiziere RuleLoader.load() in coverage_checker.py
def load(yaml_path: Path, categories: List[str] = None) -> List[Rule]:
    ...
    for category_key in categories or [all_categories]:
        ...
```

```bash
python coverage_checker.py \
  --rules master_rules.yaml \
  --repo . \
  --categories critical_policies,architecture_rules
```

### Pre-Commit Hook (lokal)

```bash
# Installation
mkdir -p .git/hooks
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
python coverage_checker.py \
  --rules master_rules.yaml \
  --repo . \
  --fail-under 100.0
EOF
chmod +x .git/hooks/pre-commit

# Test
git commit -m "test: Coverage check"
# → Blockiert bei < 100% Coverage
```

### Coverage-Badge im README

Füge zu `README.md` hinzu:

```markdown
# SSID Project

<!-- COVERAGE_BADGE --> ![Coverage](https://img.shields.io/badge/Master%20Rules%20Coverage-100%25-brightgreen)

...
```

CI/CD aktualisiert Badge automatisch.

---

## 📈 Coverage-Evolutionstracking

### Audit-Log-Struktur

```
02_audit_logging/reports/master_rules_coverage/
├── coverage_20251019_150000.json
├── coverage_20251019_150000.json.sha256
├── coverage_20251020_020000.json
├── coverage_20251020_020000.json.sha256
└── ...
```

### Trend-Analyse

```python
import json
import glob

reports = sorted(glob.glob("02_audit_logging/reports/master_rules_coverage/*.json"))

for report_path in reports:
    with open(report_path) as f:
        data = json.load(f)
        timestamp = data['timestamp']
        coverage = data['summary']['overall_percentage']
        print(f"{timestamp}: {coverage:.1f}%")
```

**Output:**
```
2025-10-19T15:00:00: 65.7%
2025-10-19T18:30:00: 72.3%
2025-10-20T02:00:00: 85.4%
2025-10-20T14:45:00: 100.0%
```

---

## 🚨 Troubleshooting

### Problem: "No coverage for rule XYZ"

**Lösung:**
1. Prüfe, ob Keyword-Matching funktioniert
2. Passe `_extract_keywords()` in entsprechendem Analyzer an
3. Oder füge explizite Evidence-Marker in Code ein:

```python
# In Python-Code:
# COVERAGE: AR001 - Root-Count-Validierung
def validate_root_count(roots: List[Path]) -> bool:
    return len(roots) == 24
```

### Problem: "False Positives"

Wenn Coverage fälschlicherweise als "vorhanden" gemeldet wird:

1. Verfeinere Keyword-Matching
2. Füge negative Keywords hinzu:

```python
def _extract_keywords(self, rule: Rule) -> List[str]:
    keywords = [...]
    negative_keywords = [...]  # Diese DÜRFEN NICHT vorkommen
    return keywords, negative_keywords
```

### Problem: "CI/CD blockiert, aber lokal funktioniert"

**Lösung:**
- Prüfe, ob alle Dateien committed sind
- Checke `.gitignore` (keine Artefakte ausschließen)
- Vergleiche `git ls-files` mit lokalem Filesystem

---

## ✅ Success Criteria

Das System ist **vollständig compliant**, wenn:

1. ✅ `python coverage_checker.py` → Exit Code 0
2. ✅ Coverage Report zeigt 100% Overall Coverage
3. ✅ CI/CD Pipeline ist grün (alle Jobs passed)
4. ✅ Alle 87 Regeln haben Full Coverage (5/5 Artifacts)
5. ✅ Reports in `02_audit_logging/` sind SHA256-gehasht
6. ✅ Pre-Commit Hook blockiert unvollständige Änderungen

---

## 📚 Referenzen

- **Master Definition:** `ssid_master_definition_corrected_v1.1.1.md`
- **Extrahierte Regeln:** `master_rules.yaml`
- **Coverage Checker:** `coverage_checker.py`
- **CI/CD Workflow:** `.github/workflows/master-rules-coverage.yml`
- **Audit Reports:** `02_audit_logging/reports/master_rules_coverage/`

---

## 🎯 Next Steps

1. **Initiale Coverage-Baseline erstellen**
   ```bash
   python coverage_checker.py --rules master_rules.yaml --repo . --output baseline.json
   ```

2. **Coverage-Lücken priorisieren**
   - Zuerst: CRITICAL Policies (CP001-CP012)
   - Dann: Architecture Rules (AR001-AR010)
   - Dann: Restliche Kategorien

3. **Schrittweise Coverage erhöhen**
   - Täglich 5-10 Regeln abschließen
   - Pull Requests nur mit Coverage-Improvement

4. **100% Coverage erreichen**
   - Target: Innerhalb von 2-4 Wochen
   - Danach: Maintenance-Modus (Coverage halten)

5. **Governance etablieren**
   - Architecture Board übernimmt Review
   - Quarterly Audits der Coverage-Reports
   - Continuous Improvement

---

**Version:** 1.0  
**Erstellt:** 2025-10-19  
**Autor:** SSID Coverage Team  
**Status:** Production-Ready
