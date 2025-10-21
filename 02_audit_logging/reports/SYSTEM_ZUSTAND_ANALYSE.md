# SYSTEM-ZUSTAND ANALYSE - 2025-10-17

## AKTUELLE REGEL-ZÄHLUNG

### Manifestation 1: Python Validators
**Datei:** `03_core/validators/sot/sot_validator_core.py`
- **Total Regeln:** 69
- **Regel-Range:** SOT-001 bis SOT-081
- **Prioritäten:**
  - MUST: 49
  - SHOULD: 14
  - HAVE: 6

### Manifestation 2: Rego Policy
**Datei:** `23_compliance/policies/sot/sot_policy.rego`
- **Total Regeln:** 69
- **Regel-Range:** SOT-001 bis SOT-081
- **Status:** ✅ Vollständig

### Manifestation 3: YAML Contract
**Datei:** `16_codex/contracts/sot/sot_contract.yaml`
- **Total Regeln:** 33 ❌
- **Regel-IDs:**
  - SOT-001, SOT-002, SOT-003, SOT-004, SOT-005 (Global Foundations)
  - SOT-018, SOT-019 (YAML Markers)
  - SOT-020, SOT-031, SOT-037, SOT-043 (Hierarchy Markers)
  - SOT-021, SOT-026, SOT-032, SOT-038, SOT-044, SOT-049, SOT-054 (Entry Markers)
  - SOT-067 bis SOT-081 (EU Regulatorik - 15 Regeln)

### Manifestation 4: CLI Validator
**Datei:** `12_tooling/cli/sot_validator.py`
- **Total Regeln:** 69 (via dynamischer Import)
- **Status:** ✅ Vollständig

### Manifestation 5: Tests
**Datei:** `11_test_simulation/tests_compliance/test_sot_validator.py`
- **Total Regeln:** 69 (via Parametrisierung)
- **Status:** ✅ Vollständig

---

## FEHLENDE REGELN IM YAML CONTRACT

**YAML hat nur 33 von 69 Regeln!**

### Fehlende Regel-Bereiche (36 Regeln fehlen):

1. **Instance Properties (SOT-022 bis SOT-058) - 37 Regeln fehlen:**
   - SOT-022 bis SOT-025: ivms101_2023 (name, path, deprecated, business_priority)
   - SOT-027 bis SOT-030: fatf_rec16_2025_update (name, path, deprecated, business_priority)
   - SOT-033 bis SOT-036: xml_schema_2025_07 (name, path, deprecated, business_priority)
   - SOT-039 bis SOT-042: iso24165_dti (name, path, deprecated, business_priority)
   - SOT-045 bis SOT-048: fsb_stablecoins_2023 (name, path, deprecated, business_priority)
   - SOT-050 bis SOT-053: iosco_crypto_markets_2023 (name, path, deprecated, business_priority)
   - SOT-055 bis SOT-058: nist_ai_rmf_1_0 (name, path, deprecated, business_priority)

2. **Deprecated List (SOT-059 bis SOT-066) - 8 Regeln fehlen:**
   - SOT-059: deprecated_standards marker
   - SOT-060: deprecated list id validation
   - SOT-061: deprecated list status validation
   - SOT-062: deprecated list deprecated flag
   - SOT-063: deprecated list replaced_by
   - SOT-064: deprecated list deprecation_date
   - SOT-065: deprecated list migration_deadline
   - SOT-066: deprecated list notes

**ABER: SOT-026 ist im YAML vorhanden, nicht SOT-027-030!**
Das bedeutet: Es gibt eine Lücke bei SOT-026!

---

## REGEL-NUMMERIERUNG ANALYSE

### Bestehende Regeln (69 total):
- SOT-001 bis SOT-005: Global Foundations (5)
- **GAP: SOT-006 bis SOT-017 (deprecated)**
- SOT-018, SOT-019: YAML Markers (2)
- SOT-020, SOT-031, SOT-037, SOT-043: Hierarchy Markers (4)
- SOT-021, SOT-026, SOT-032, SOT-038, SOT-044, SOT-049, SOT-054: Entry Markers (7)
- SOT-022 bis SOT-058: Instance Properties (37) ← **Nur in Python/Rego, NICHT in YAML!**
- SOT-059 bis SOT-066: Deprecated List (8) ← **Nur in Python/Rego, NICHT in YAML!**
- SOT-067 bis SOT-081: EU Regulatorik (15)

**Total: 5 + 2 + 4 + 7 + 37 + 8 + 15 = 78 Regeln**
**Mit GAP (12 deprecated): 78 + 12 = 90 Regel-IDs verwendet**
**Aber nur 69 aktive Regeln!**

---

## SOURCE-DOKUMENT ANFORDERUNG

**Datei:** `16_codex/structure/SSID_structure_level3_part3_MAX.md`

### User-Spezifikation:
- **Zeilen 2-20:** 19 Regeln (EU-Regulatorik: soc2, gaia_x, etsi_en_319_421)
- **Zeilen 26-32:** 7 Regeln (Globale Metadaten)
- **Zeilen 34-87:** 54 Regeln (Frameworks)

**User sagt: 19 + 7 + 54 = 80 NEUE Regeln**

### Problem:
EU-Regulatorik (SOT-067 bis SOT-081) sind **NICHT NEU** - sie existieren bereits!

Das bedeutet:
- 15 Regeln (SOT-067 bis SOT-081) sind bereits im System
- **Verbleiben: 80 - 15 = 65 tatsächlich NEUE Regeln**

---

## DISKREPANZ-ANALYSE

### Was der User will:
- 80 neue Regeln aus Zeilen 2-87 des Source-Dokuments

### Was das System hat:
- 69 bestehende Regeln (SOT-001 bis SOT-081 mit Lücken)

### Was fehlt:
1. **36 Regeln fehlen im YAML Contract** (SOT-022 bis SOT-066)
2. **Unklar: Sind die "80 neuen Regeln" zusätzlich zu den 69 oder Teil davon?**

---

## NÄCHSTE SCHRITTE (VORSCHLAG)

### Option A: 36 fehlende Regeln zum YAML hinzufügen
**Ziel:** Erreiche 1:1:1:1:1 Manifestation für alle 69 bestehenden Regeln

**Aktion:**
1. Füge SOT-022 bis SOT-066 zum YAML Contract hinzu
2. Verifiziere alle 5 Manifestationen
3. Erstelle Badge "FULL SOT MATERIALIZATION"

**Ergebnis:** 69 Regeln in allen 5 Manifestationen

---

### Option B: 80 zusätzliche Regeln erstellen
**Ziel:** Erweitere System auf 69 + 80 = 149 Regeln

**Aktion:**
1. Parse Source-Dokument Zeilen 2-87
2. Generiere 80 neue Regeln (SOT-082 bis SOT-161)
3. Füge zu allen 5 Manifestationen hinzu

**Ergebnis:** 149 Regeln in allen 5 Manifestationen

---

### Option C: Nur NEUE Regeln (65 Regeln)
**Ziel:** Füge 65 tatsächlich neue Regeln hinzu (80 minus 15 bestehende EU-Regulatorik)

**Aktion:**
1. Parse Source-Dokument (ohne SOT-067 bis SOT-081)
2. Generiere 65 neue Regeln
3. Füge zu allen 5 Manifestationen hinzu

**Ergebnis:** 69 + 65 = 134 Regeln total

---

## USER-ANWEISUNG ERFORDERLICH

**Frage an User:**
Was ist das EXAKTE Ziel?

1. **Vervollständige die 69 bestehenden Regeln** (füge 36 zu YAML hinzu)?
2. **Erweitere auf 149 Regeln** (69 bestehend + 80 neu)?
3. **Erweitere auf 134 Regeln** (69 bestehend + 65 neu, ohne Duplikate)?

---

## ZUSAMMENFASSUNG

- ✅ **Python:** 69 Regeln
- ✅ **Rego:** 69 Regeln
- ❌ **YAML:** 33 Regeln (36 fehlen!)
- ✅ **CLI:** 69 Regeln (dynamisch)
- ✅ **Tests:** 69 Regeln (parametrisiert)

**STATUS:** 1:1:1:1:1 Manifestation VERLETZT wegen YAML Contract!

**KRITISCH:** User-Klarstellung nötig bevor weitere Generierung!
