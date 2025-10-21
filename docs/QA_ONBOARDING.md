# QA Master Suite - Developer Onboarding Guide

**Version:** 1.0.0
**Letzte Aktualisierung:** 2025-10-18
**Zielgruppe:** Neue Entwickler, QA Engineers, Compliance Auditoren

---

## Willkommen im SSID QA-System

Dieser Guide hilft dir, schnell produktiv mit dem SSID QA/Regression-System zu werden.

---

## 🏗️ Architektur-Überblick

Das SSID QA-System folgt einer **DUAL-LAYER Architecture**:

```
┌─────────────────────────────────────────────────────────────┐
│  DUAL-LAYER QA ARCHITECTURE                                 │
└─────────────────────────────────────────────────────────────┘

LAYER 1: Active QA (11_test_simulation/)
├── ✅ Hier arbeitest du täglich
├── Produktive, ausführbare Tests
├── CI/CD Integration
└── pytest, coverage, health checks

LAYER 2: QA Archive (qa_master_suite/)
├── 📦 Konsolidiertes Archiv (853MB+)
├── Historische Tests
├── Regressions-Tests
└── Nur für Reviews/Archivierung

LAYER 3: SoT Governance (5 Artefakte)
├── 🔒 Niemals anfassen (außer mit Approval)
├── Compliance-Regeln
└── Strikte Trennung von QA
```

---

## 🚀 Quick Start (5 Minuten)

### 1. Repository klonen

```bash
git clone https://github.com/your-org/SSID.git
cd SSID
```

### 2. Python-Umgebung einrichten

```bash
# Python 3.11+ erforderlich
python --version  # Sollte ≥3.11 sein

# Virtual Environment erstellen
python -m venv venv
source venv/bin/activate  # Linux/Mac
# oder
venv\Scripts\activate  # Windows

# Dependencies installieren
pip install -r requirements.txt
pip install pytest pytest-cov pytest-mock
```

### 3. Erste Tests ausführen

```bash
# Alle Tests ausführen
pytest 11_test_simulation/

# Nur Compliance-Tests
pytest 11_test_simulation/tests_compliance/

# Mit Coverage
pytest 11_test_simulation/ --cov=03_core --cov-report=term-missing
```

### 4. Pre-Commit Hook testen

```bash
# Hook ist bereits aktiv nach dem Klonen
# Test: Versuche eine Test-Datei außerhalb der erlaubten Orte zu committen
touch test_invalid.py
git add test_invalid.py
git commit -m "Test"
# ❌ Sollte blockiert werden!

# Aufräumen
rm test_invalid.py
```

**✅ Wenn der Pre-Commit Hook blockiert hat, bist du bereit!**

---

## 📁 Verzeichnis-Struktur

### Wo du arbeiten darfst

```bash
11_test_simulation/           # ✅ Hier entwickelst du neue Tests
├── tests/                    # Allgemeine System-Tests
├── tests_compliance/         # Compliance-Tests
├── tests_audit/              # Audit-Tests
├── tests_health/             # Health-Check-Tests
└── health/                   # Monitoring-Tests
```

### Wo du NICHT arbeiten darfst (ohne Approval)

```bash
02_audit_logging/archives/qa_master_suite/  # ❌ Nur Archiv, kein Active Development
16_codex/contracts/sot/sot_contract.yaml    # ❌ SoT Governance
03_core/validators/sot/sot_validator_core.py # ❌ SoT Governance
23_compliance/policies/sot/sot_policy.rego   # ❌ SoT Governance
12_tooling/cli/sot_validator.py             # ❌ SoT Governance
11_test_simulation/tests_compliance/test_sot_validator.py # ❌ SoT Governance
```

---

## ✍️ Einen neuen Test schreiben

### Schritt 1: Test-Datei erstellen

```bash
# Erstelle eine neue Test-Datei im richtigen Verzeichnis
touch 11_test_simulation/tests/test_my_feature.py
```

### Schritt 2: Test implementieren

```python
# 11_test_simulation/tests/test_my_feature.py

import pytest

def test_my_feature_basic():
    """Test basic functionality of my feature."""
    result = my_function(input_data)
    assert result == expected_output

def test_my_feature_edge_cases():
    """Test edge cases."""
    with pytest.raises(ValueError):
        my_function(invalid_input)

@pytest.mark.slow
def test_my_feature_performance():
    """Test performance (marked as slow)."""
    # Performance test logic
    pass
```

### Schritt 3: Test lokal ausführen

```bash
# Einzelnen Test ausführen
pytest 11_test_simulation/tests/test_my_feature.py -v

# Mit Coverage
pytest 11_test_simulation/tests/test_my_feature.py --cov=03_core --cov-report=term
```

### Schritt 4: Commit vorbereiten

```bash
git add 11_test_simulation/tests/test_my_feature.py
git commit -m "feat(tests): Add tests for my_feature"
# ✅ Pre-Commit Hook wird automatisch ausgeführt
```

---

## 🔍 Policy-Enforcement verstehen

### Pre-Commit Hook

Der Pre-Commit Hook (`.git/hooks/pre-commit`) blockiert automatisch:

- ❌ Test-Dateien außerhalb von `11_test_simulation/`
- ❌ Test-Dateien außerhalb von `qa_master_suite/` (Archiv)
- ❌ Änderungen an den 5 SoT Governance-Artefakten (ohne Approval)

**Was passiert bei einem Verstoß:**

```bash
❌ QA/SoT DUAL-LAYER POLICY VIOLATION
The following QA test files are outside the allowed QA corpus:
  ❌ my_tests/test_something.py

POLICY:
  All QA test files (.py, .yaml, .yml, .rego, .json) MUST reside in:
    - 02_audit_logging/archives/qa_master_suite/ (QA Archive)
    - 11_test_simulation/ (Active Test Directory)

ACTION REQUIRED:
  1. Move test files to qa_master_suite/
  2. OR remove from commit (git reset HEAD <file>)
```

### OPA Policy

OPA (Open Policy Agent) wird in CI/CD verwendet für maschinenlesbare Policy-Checks:

```bash
# Lokal OPA Policy testen (optional)
opa eval -i files.json -d 23_compliance/policies/qa/qa_policy_enforcer.rego "data.qa_policy.deny"
```

---

## 📊 Coverage-Anforderungen

### Ziele

- **Minimum:** 75% Coverage (Hard Fail)
- **Ziel:** 80% Coverage (Sprint 2 Requirement)

### Coverage lokal prüfen

```bash
# Coverage für alle Module
pytest 11_test_simulation/ \
  --cov=02_audit_logging \
  --cov=03_core \
  --cov=08_identity_score \
  --cov=23_compliance \
  --cov-report=html \
  --cov-report=term-missing

# HTML-Report öffnen
open htmlcov/index.html  # Mac/Linux
start htmlcov/index.html  # Windows
```

---

## 🔄 Workflow: Vom Test zum Archiv

```
1. ENTWICKLUNG (11_test_simulation/)
   ↓
   Developer schreibt neuen Test
   ↓
2. REVIEW & MERGE
   ↓
   PR wird reviewed und gemerged
   ↓
3. CI/CD EXECUTION
   ↓
   Tests laufen in GitHub Actions
   ↓
4. STABILISIERUNG (nach mehreren Wochen)
   ↓
   Test ist stabil und bewährt
   ↓
5. ARCHIVIERUNG (qa_master_suite/)
   ↓
   Test wird ins konsolidierte Archiv übernommen
   (Nur durch Compliance Team)
```

---

## 🧪 Test-Kategorien

### Unit Tests

```python
@pytest.mark.unit
def test_function_unit():
    """Unit test for a single function."""
    pass
```

### Integration Tests

```python
@pytest.mark.integration
def test_integration():
    """Integration test across modules."""
    pass
```

### Compliance Tests

```python
@pytest.mark.compliance
def test_sot_compliance():
    """Compliance test for SoT enforcement."""
    pass
```

### Slow Tests

```python
@pytest.mark.slow
def test_performance():
    """Performance test (excluded from quick runs)."""
    pass
```

**Tests ausführen nach Kategorie:**

```bash
# Nur Unit Tests
pytest -m unit

# Ohne Slow Tests
pytest -m "not slow"

# Nur Compliance Tests
pytest -m compliance
```

---

## 🚨 Häufige Fehler & Lösungen

### Fehler 1: Pre-Commit Hook blockiert meinen Test

**Problem:**
```
❌ QA/SoT DUAL-LAYER POLICY VIOLATION
  ❌ my_folder/test_something.py
```

**Lösung:**
```bash
# Test in erlaubtes Verzeichnis verschieben
mv my_folder/test_something.py 11_test_simulation/tests/
git add 11_test_simulation/tests/test_something.py
git commit -m "fix: Move test to correct location"
```

---

### Fehler 2: Import-Fehler beim Test-Ausführen

**Problem:**
```
ModuleNotFoundError: No module named 'my_module'
```

**Lösung:**
```bash
# Sicherstellen, dass PYTHONPATH korrekt ist
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Oder pytest.ini ist korrekt konfiguriert (sollte bereits sein)
```

---

### Fehler 3: Coverage unter Minimum

**Problem:**
```
FAILED: Coverage 68% below minimum 75%
```

**Lösung:**
```bash
# Mehr Tests schreiben für nicht-getestete Bereiche
pytest --cov=03_core --cov-report=term-missing
# Zeigt welche Zeilen nicht getestet sind
```

---

## 📚 Wichtige Dokumente

### Pflichtlektüre

1. **Policy README:** `02_audit_logging/archives/qa_master_suite/README.md`
   - DUAL-LAYER Architecture
   - Erlaubte/Verbotene Änderungen
   - Enforcement-Regeln

2. **Registry Policy:** `24_meta_orchestration/registry/qa_corpus_policy.yaml`
   - Machine-readable Policy
   - SHA256 Integrity Hashes
   - Compliance-Level

### Für Fortgeschrittene

3. **Audit Report:** `02_audit_logging/reports/QA_MASTER_SUITE_COMPLIANCE_AUDIT_2025_10_18.md`
   - Vollständiger Compliance-Audit
   - Enforcement-Status
   - KPIs und Metriken

4. **Monitoring Dashboard:** `02_audit_logging/archives/qa_master_suite/MONITORING.md`
   - Live-Status
   - Violations
   - Performance-Metriken

---

## 🛠️ Tooling & Commands

### Pytest

```bash
# Basic run
pytest 11_test_simulation/

# Verbose mit Failures
pytest 11_test_simulation/ -v --tb=short

# Stop on first failure
pytest 11_test_simulation/ -x

# Run specific test
pytest 11_test_simulation/tests/test_my_feature.py::test_my_function

# With coverage
pytest 11_test_simulation/ --cov=03_core --cov-report=term-missing
```

### Git

```bash
# Test Pre-Commit Hook (ohne tatsächlich zu committen)
.git/hooks/pre-commit

# View commit history
git log --oneline --graph

# Check what will be committed
git diff --cached
```

### OPA (Optional, für Policy-Entwicklung)

```bash
# Install OPA
brew install opa  # Mac
# oder download von https://www.openpolicyagent.org/

# Test QA Policy
opa eval -i files.json -d 23_compliance/policies/qa/qa_policy_enforcer.rego "data.qa_policy.report"
```

---

## 🤝 Support & Kontakt

### Bei Fragen

1. **Slack:** `#qa-master-suite` Channel
2. **Email:** qa-policy@ssid-project.internal
3. **Ticket:** JIRA QA-Policy Board
4. **Meeting:** Bi-weekly Thursday 14:00 UTC

### Bei Policy-Violations

1. **Nicht panikieren!** Pre-Commit Hook ist da, um zu helfen
2. **Lesen:** Fehlermeldung zeigt genau, was falsch ist
3. **Fixen:** Test in erlaubtes Verzeichnis verschieben
4. **Fragen:** Bei Unklarheiten Slack/Email nutzen

### Bei Emergencies

**Emergency Contact:** compliance-emergency@ssid-project.internal

---

## 📖 Weiterführende Resources

### CI/CD

- **Coverage Workflow:** `.github/workflows/ci_coverage.yml`
- **Compliance Checks:** `.github/workflows/sot_compliance_validation.yml`

### Policies

- **OPA Policy:** `23_compliance/policies/qa/qa_policy_enforcer.rego`
- **Pre-Commit Hook:** `.git/hooks/pre-commit`

### Externe Links

- [Pytest Documentation](https://docs.pytest.org/)
- [OPA Documentation](https://www.openpolicyagent.org/docs/)
- [pytest-cov Plugin](https://pytest-cov.readthedocs.io/)

---

## ✅ Onboarding Checklist

Stelle sicher, dass du alles erledigt hast:

- [ ] Repository geklont
- [ ] Python 3.11+ installiert
- [ ] Virtual Environment erstellt
- [ ] Dependencies installiert (`pip install -r requirements.txt`)
- [ ] Erste Tests ausgeführt (`pytest 11_test_simulation/`)
- [ ] Pre-Commit Hook getestet
- [ ] Policy README gelesen (`qa_master_suite/README.md`)
- [ ] Slack Channel beigetreten (`#qa-master-suite`)
- [ ] Ersten Test geschrieben und committed
- [ ] Coverage-Report generiert

**Wenn alle Punkte abgehakt sind: Willkommen im Team! 🎉**

---

## 🔄 Changelog

| Version | Datum | Änderung | Autor |
|---------|-------|----------|-------|
| 1.0.0 | 2025-10-18 | Initial Onboarding Guide | Claude (Finalization Agent) |

---

**END OF ONBOARDING GUIDE**

*Feedback willkommen:* qa-policy@ssid-project.internal
