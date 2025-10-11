# Sprint 2 - Coverage Gap Matrix
**Datum:** 2025-10-09
**Baseline Coverage:** 6.80%
**Ziel Coverage:** 80%
**Gap:** 73.20 Prozentpunkte

---

## Zusammenfassung

Diese Gap-Matrix identifiziert alle Coverage-Lücken und priorisiert die Test-Implementierung nach Impact und Aufwand.

### Gesamt-Metriken
- **Gesamte Statements:** 1,852
- **Abgedeckt:** 126 (6.80%)
- **Fehlend:** 1,726 (93.20%)
- **Geschätzte Tests benötigt:** ~172
- **Geschätzter Aufwand:** 86 Stunden (10.8 Tage)

---

## Module Coverage-Übersicht

| Modul | Statements | Abgedeckt | Fehlend | Coverage | Gap zu 80% | Priorität |
|-------|------------|-----------|---------|----------|------------|-----------|
| **23_compliance** | 713 | 91 | 622 | 12.76% | 67.24% | HOCH |
| **02_audit_logging** | 776 | 35 | 741 | 4.51% | 75.49% | KRITISCH |
| **03_core** | 229 | 0 | 229 | 0.00% | 80.00% | KRITISCH |
| **24_meta_orchestration** | 113 | 0 | 113 | 0.00% | 80.00% | MITTEL |
| **08_identity_score** | 21 | 0 | 21 | 0.00% | 80.00% | NIEDRIG |
| **GESAMT** | **1,852** | **126** | **1,726** | **6.80%** | **73.20%** | - |

---

## Detaillierte Gap-Matrix nach Datei

### 02_audit_logging (4.51% Coverage - KRITISCH)

| Datei | Stmts | Miss | Cov% | Priorität | Aufwand | Status |
|-------|-------|------|------|-----------|---------|--------|
| **validators/check_hash_chain.py** | 21 | 3 | 86% | P1 | 0.5h | IN BEARBEITUNG |
| **validators/check_log_schema.py** | 8 | 0 | 100% | P1 | 0h | KOMPLETT |
| **validators/check_worm_storage.py** | 9 | 0 | 100% | P1 | 0h | KOMPLETT |
| **anti_gaming/circular_dependency_validator.py** | 116 | 116 | 0% | P1 | 6h | TODO |
| **anti_gaming/anomaly_rate_guard.py** | 111 | 111 | 0% | P1 | 5h | TODO |
| **anti_gaming/time_skew_analyzer.py** | 107 | 107 | 0% | P1 | 5h | TODO |
| **anti_gaming/replay_attack_detector.py** | 96 | 96 | 0% | P1 | 5h | TODO |
| **anti_gaming/dependency_graph_generator.py** | 95 | 95 | 0% | P1 | 5h | TODO |
| **anti_gaming/overfitting_detector.py** | 95 | 95 | 0% | P1 | 5h | TODO |
| **interconnect/bridge_compliance_push.py** | 73 | 73 | 0% | P2 | 4h | TODO |
| **interconnect/bridge_23compliance.py** | 36 | 36 | 0% | P2 | 2h | TODO |
| **anti_gaming/__init__.py** | 7 | 7 | 0% | P3 | 0.5h | TODO |
| **interconnect/__init__.py** | 2 | 2 | 0% | P3 | 0.25h | TODO |
| **SUBTOTAL** | **776** | **741** | **4.51%** | - | **38.25h** | - |

**Impact auf Gesamt-Coverage:** +40% möglich (741 Statements)

---

### 03_core (0.00% Coverage - KRITISCH)

| Datei | Stmts | Miss | Cov% | Priorität | Aufwand | Status |
|-------|-------|------|------|-----------|---------|--------|
| **healthcheck/health_check_core.py** | 85 | 85 | 0% | P1 | 4h | TODO |
| **healthcheck/generate_health_wrappers.py** | 65 | 65 | 0% | P2 | 3h | TODO |
| **healthcheck/health_audit_logger.py** | 43 | 43 | 0% | P2 | 2h | TODO |
| **interconnect/bridge_foundation.py** | 32 | 32 | 0% | P2 | 2h | TODO |
| **healthcheck/__init__.py** | 2 | 2 | 0% | P3 | 0.25h | TODO |
| **interconnect/__init__.py** | 2 | 2 | 0% | P3 | 0.25h | TODO |
| **SUBTOTAL** | **229** | **229** | **0.00%** | - | **11.5h** | - |

**Impact auf Gesamt-Coverage:** +12% möglich (229 Statements)

---

### 23_compliance (12.76% Coverage - HOCH)

| Datei | Stmts | Miss | Cov% | Priorität | Aufwand | Status |
|-------|-------|------|------|-----------|---------|--------|
| **anti_gaming/dependency_graph_generator.py** | 216 | 216 | 0% | P1 | 8h | TODO |
| **anti_gaming/badge_integrity_checker.py** | 168 | 168 | 0% | P1 | 6h | TODO |
| **anti_gaming/overfitting_detector.py** | 73 | 60 | 18% | P1 | 3h | IN BEARBEITUNG |
| **anti_gaming/detect_circular_dependencies.py** | 88 | 48 | 45% | P1 | 2h | IN BEARBEITUNG |
| **anti_gaming/detect_duplicate_identity_hashes.py** | 56 | 39 | 30% | P1 | 2h | IN BEARBEITUNG |
| **anti_gaming/badge_signature_validator.py** | 67 | 46 | 31% | P2 | 2h | IN BEARBEITUNG |
| **policies/policy_engine.py** | 42 | 42 | 0% | P2 | 2h | TODO |
| **anti_gaming/circular_dependency_validator.py** | 1 | 1 | 0% | P3 | 0.25h | TODO |
| **anti_gaming/detect_proof_reuse_patterns.py** | 0 | 0 | 100% | - | 0h | KOMPLETT |
| **anti_gaming/scan_unexpected_activity_windows.py** | 0 | 0 | 100% | - | 0h | KOMPLETT |
| **policies/__init__.py** | 2 | 2 | 0% | P3 | 0.25h | TODO |
| **SUBTOTAL** | **713** | **622** | **12.76%** | - | **25.5h** | - |

**Impact auf Gesamt-Coverage:** +33% möglich (622 Statements)

---

### 24_meta_orchestration (0.00% Coverage - MITTEL)

| Datei | Stmts | Miss | Cov% | Priorität | Aufwand | Status |
|-------|-------|------|------|-----------|---------|--------|
| **compliance_chain_trigger.py** | 113 | 113 | 0% | P2 | 6h | TODO |
| **SUBTOTAL** | **113** | **113** | **0.00%** | - | **6h** | - |

**Impact auf Gesamt-Coverage:** +6% möglich (113 Statements)

---

### 08_identity_score (0.00% Coverage - NIEDRIG)

| Datei | Stmts | Miss | Cov% | Priorität | Aufwand | Status |
|-------|-------|------|------|-----------|---------|--------|
| **src/identity_score_calculator.py** | 21 | 21 | 0% | P2 | 2h | TODO |
| **__init__.py** | 0 | 0 | 100% | - | 0h | KOMPLETT |
| **src/__init__.py** | 0 | 0 | 100% | - | 0h | KOMPLETT |
| **SUBTOTAL** | **21** | **21** | **0.00%** | - | **2h** | - |

**Impact auf Gesamt-Coverage:** +1% möglich (21 Statements)

---

## Prioritisierungsmatrix

### P1 - KRITISCH (Sofort umsetzen)

**Kriterien:** Hoher Impact + Kritische Funktionalität

| Modul | Dateien | Statements | Aufwand | Coverage-Gewinn |
|-------|---------|------------|---------|-----------------|
| 02_audit_logging | 6 Anti-Gaming Module | 625 | 31h | +34% |
| 03_core | Health Check Core | 85 | 4h | +5% |
| 23_compliance | 3 Anti-Gaming Module | 332 | 13h | +18% |
| **GESAMT P1** | **10 Dateien** | **1,042** | **48h** | **+57%** |

**Ziel:** Mit P1 allein 63.8% Coverage erreichen (6.8% + 57%)

---

### P2 - HOCH (Innerhalb Sprint 2)

**Kriterien:** Mittlerer Impact + Wichtige Funktionalität

| Modul | Dateien | Statements | Aufwand | Coverage-Gewinn |
|-------|---------|------------|---------|-----------------|
| 02_audit_logging | 2 Bridges | 109 | 6h | +6% |
| 03_core | Health Wrappers, Audit Logger, Bridge | 140 | 7h | +8% |
| 23_compliance | Policy Engine, Badge Validator | 88 | 4h | +5% |
| 24_meta_orchestration | Compliance Chain | 113 | 6h | +6% |
| 08_identity_score | Score Calculator | 21 | 2h | +1% |
| **GESAMT P2** | **8 Dateien** | **471** | **25h** | **+26%** |

**Ziel:** Mit P1+P2 gesamt 89.8% Coverage erreichen (63.8% + 26%)

---

### P3 - NIEDRIG (Sprint 3+)

**Kriterien:** Niedriger Impact (meist __init__.py)

| Modul | Dateien | Statements | Aufwand | Coverage-Gewinn |
|-------|---------|------------|---------|-----------------|
| Alle Module | __init__.py Dateien | 13 | 1.25h | +0.7% |
| **GESAMT P3** | **5 Dateien** | **13** | **1.25h** | **+0.7%** |

**Ziel:** Mit P1+P2+P3 gesamt 90.5% Coverage erreichen

---

## Test-Strategie nach Priorität

### Phase 1: Quick Wins (P1 Validator + Identity Score) - Tage 1-2

**Ziel:** 6.8% → 10% Coverage

| Aufgabe | Datei | Aufwand | Coverage-Gewinn |
|---------|-------|---------|-----------------|
| Hash Chain Edge Cases | check_hash_chain.py | 0.5h | +0.2% |
| Identity Score Tests | identity_score_calculator.py | 2h | +1% |
| **GESAMT** | **2 Dateien** | **2.5h** | **+1.2%** |

**Ergebnis:** 8% Coverage nach Phase 1

---

### Phase 2: Health Check System (P1 Core) - Tage 3-5

**Ziel:** 8% → 13% Coverage

| Aufgabe | Datei | Aufwand | Coverage-Gewinn |
|---------|-------|---------|-----------------|
| Health Check Core | health_check_core.py | 4h | +5% |
| **GESAMT** | **1 Datei** | **4h** | **+5%** |

**Ergebnis:** 13% Coverage nach Phase 2

---

### Phase 3: Anti-Gaming Core (P1) - Tage 6-12

**Ziel:** 13% → 63% Coverage

| Aufgabe | Dateien | Aufwand | Coverage-Gewinn |
|---------|---------|---------|-----------------|
| 02_audit_logging Anti-Gaming | 6 Module | 31h | +34% |
| 23_compliance Anti-Gaming | 3 Module | 13h | +18% |
| **GESAMT** | **9 Dateien** | **44h** | **+52%** |

**Ergebnis:** 65% Coverage nach Phase 3

---

### Phase 4: Bridges & Policy (P2) - Tage 13-18

**Ziel:** 65% → 85% Coverage

| Aufgabe | Dateien | Aufwand | Coverage-Gewinn |
|---------|---------|---------|-----------------|
| Health Subsystem | 3 Module | 7h | +8% |
| Bridges | 3 Module | 8h | +7% |
| Policy & Orchestration | 2 Module | 10h | +11% |
| **GESAMT** | **8 Dateien** | **25h** | **+26%** |

**Ergebnis:** 91% Coverage nach Phase 4

---

## Risiko-Analyse nach Modul

### 02_audit_logging - HÖCHSTES RISIKO

**Risiken:**
- Größtes Modul (776 Statements)
- Komplexe Anti-Gaming-Logik
- Externe Abhängigkeiten (Zeitstempel, Hashing)

**Mitigation:**
- Mocking für Zeit-basierte Tests (freezegun)
- Fixtures für Hash-Chains
- Isolierte Tests pro Modul
- Start mit Validators (einfach) vor Anti-Gaming (komplex)

**Zeitschätzung Unsicherheit:** ±20% (31h ± 6h)

---

### 03_core - MITTLERES RISIKO

**Risiken:**
- Health Checks benötigen HTTP-Mocking
- Port-Checking komplex
- Registry-Integration

**Mitigation:**
- requests-mock für HTTP
- socket-mocking für Ports
- In-Memory Registry für Tests

**Zeitschätzung Unsicherheit:** ±15% (11.5h ± 1.7h)

---

### 23_compliance - MITTLERES RISIKO

**Risiken:**
- Dependency Graph Generator (216 Stmts - größte Datei!)
- Graph-Algorithmen komplex
- Badge-Integrität benötigt Kryptografie

**Mitigation:**
- networkx für Graph-Tests (falls vorhanden)
- Vereinfachte Badge-Fixtures
- Start mit detect_* Modulen (schon teilweise getestet)

**Zeitschätzung Unsicherheit:** ±25% (25.5h ± 6.4h)

---

## Realistische Zeitleiste

### Sprint 2 Week 5-6 (10 Arbeitstage)

**Tag 1-2:** Phase 1 - Quick Wins
- **Ziel:** 8% Coverage
- **Aufwand:** 2.5h
- **Status:** MACHBAR

**Tag 3-5:** Phase 2 - Health Check System
- **Ziel:** 13% Coverage
- **Aufwand:** 4h
- **Status:** MACHBAR

**Tag 6-12:** Phase 3 - Anti-Gaming Core
- **Ziel:** 65% Coverage
- **Aufwand:** 44h (über 7 Tage = 6.3h/Tag)
- **Status:** HERAUSFORDERND - Benötigt fokussierte Arbeit

**Tag 13-18:** Phase 4 - Bridges & Policy
- **Ziel:** 85%+ Coverage
- **Aufwand:** 25h (über 6 Tage = 4.2h/Tag)
- **Status:** MACHBAR

**GESAMT:** 75.5h über 18 Tage = 4.2h/Tag Durchschnitt

---

## Alternative Strategie: "80% Minimum"

Falls Zeitbeschränkungen, fokus auf P1+P2 mit Ausnahmen:

**Pflicht für 80%:**
1. Alle Validators (✅ DONE)
2. Health Check Core (P1)
3. Top 5 Anti-Gaming Module (P1)
4. 2 Bridges (P2)
5. Policy Engine (P2)

**Kann verschoben werden:**
- Dependency Graph Generators (zu komplex, niedrig impact)
- Badge Integrity (benötigt Krypto-Setup)
- Meta-Orchestration (wenig genutzt)

**Realistische Zielerreichung:** 75-78% Coverage in Sprint 2

---

## Test-Infrastruktur Anforderungen

### Benötigte Tools
```python
# Bereits installiert
pytest==7.4.3
pytest-cov==7.0.0

# Möglicherweise benötigt
pytest-mock==3.12.0         # Mocking
freezegun==1.4.0            # Zeit-Mocking
requests-mock==1.11.0       # HTTP-Mocking
```

### Fixtures erstellen
**Datei:** `11_test_simulation/conftest.py`

**Benötigte Fixtures:**
1. `sample_audit_log()` - Audit Log Entries
2. `sample_hash_chain()` - Hash Chain Validator
3. `mock_health_endpoint()` - HTTP Health Endpoint
4. `mock_port_check()` - Port Socket Checks
5. `sample_dependency_graph()` - Graph für Tests
6. `sample_badge_data()` - Badge Fixtures

### Test Templates
**Ordner:** `11_test_simulation/templates/`

1. `test_template_validator.py`
2. `test_template_bridge.py`
3. `test_template_health.py`
4. `test_template_anti_gaming.py`

---

## Coverage CI Enforcement

### Strategie: Gestufte Thresholds

**Week 5 (Tag 1-5):**
```yaml
minimum_coverage: 10%
target_coverage: 15%
```

**Week 5 (Tag 6-10):**
```yaml
minimum_coverage: 30%
target_coverage: 40%
```

**Week 6 (Tag 11-15):**
```yaml
minimum_coverage: 60%
target_coverage: 70%
```

**Week 6 (Tag 16-18):**
```yaml
minimum_coverage: 75%
target_coverage: 80%
```

**Nach Sprint 2:**
```yaml
minimum_coverage: 80%
target_coverage: 85%
fail_under: 75%  # Hard fail
```

---

## Erfolgsmetriken

### Coverage Ziele
- [x] Baseline etabliert: 6.8%
- [ ] Phase 1 komplett: 8%
- [ ] Phase 2 komplett: 13%
- [ ] Phase 3 komplett: 65%
- [ ] Phase 4 komplett: 85%+
- [ ] **SPRINT 2 ZIEL:** 80%

### Qualitätsmetriken
- [ ] Alle Tests bestehen
- [ ] Keine flaky Tests
- [ ] Test-Ausführungszeit <5 Minuten
- [ ] Coverage-Report generiert
- [ ] CI-Integration aktiv

---

## Nächste Schritte (SOFORT)

1. **Fixtures erstellen** (1h)
   - `conftest.py` mit Common Fixtures
   - Import-Helper für Number-Prefixed Modules

2. **Test Templates erstellen** (1h)
   - 4 Templates für gängige Patterns

3. **Phase 1 starten** (2h)
   - Edge Cases für hash_chain.py
   - Tests für identity_score_calculator.py

4. **Coverage Run** (15min)
   - Verify 8% Coverage erreicht
   - HTML-Report generieren

**Start JETZT mit Fixtures!**

---

**Erstellt:** 2025-10-09
**Status:** BEREIT FÜR UMSETZUNG
**Nächstes Update:** Nach Phase 1 (Tag 2)
