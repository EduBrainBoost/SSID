# NÄCHSTE SCHRITTE: Parser-Vereinheitlichung

## 🚨 KRITISCHER STATUS

**Problem:** Es existieren MEHRERE Parser im System, die unterschiedliche Regeln zählen.
**Lösung:** ALLE Parser-Logik in EINEN Master-Parser zusammenführen.
**Basis:** `03_core/validators/sot/sot_rule_parser_v3.py`

---

## ✅ WAS WURDE BEREITS GEMACHT

1. ✅ Alle Parser gefunden und analysiert
2. ✅ Illegalen Parser gelöscht (`16_codex/structure/parser/sot_rule_parser.py`)
3. ✅ Health Monitor implementiert (17_observability/sot_health_monitor.py)
4. ✅ CLI --self-health Flag hinzugefügt
5. ✅ Extractor API erstellt (03_core/validators/sot/sot_extractor.py)
6. ✅ 100% Compliance Report erstellt

---

## 🎯 WAS NOCH ZU TUN IST

### SOFORT (Heute)

#### 1. Parser-Logik von `parse_sot_rules.py` nach `sot_rule_parser_v3.py` übertragen

**Datei zu erweitern:**
```
03_core/validators/sot/sot_rule_parser_v3.py
```

**Zu integrierende Patterns aus:**
```
12_tooling/scripts/parse_sot_rules.py
```

**Spezifische Patterns hinzufügen:**
- `HASH_START_PATTERN`
- `PATH_ANCHOR_PATTERN`
- `MOSCOW_DE_PATTERN` (deutsche MoSCoW-Begriffe)
- `MOSCOW_DE_EXTENDED`
- `MUST_EXIST_PATTERN`
- `SCORE_THRESHOLD_PATTERN`
- `REGIONAL_SCOPE_PATTERN`
- `BOOLEAN_CONTROL_PATTERN`
- `PURPOSE_PATTERN`

**Kommando:**
```python
# Am Ende von sot_rule_parser_v3.py hinzufügen:

# === ADDITIONAL PATTERNS FROM parse_sot_rules.py ===
# (Hier alle fehlenden Patterns einfügen)
```

#### 2. Parser-Logik von `parse_part1_semantic.py` integrieren

**Datei:**
```
16_codex/structure/level3/parse_part1_semantic.py
```

**Zu prüfen:**
- Welche einzigartigen Patterns existieren hier?
- Semantic Rules Extraction Logik
- Part1-specific Handling

#### 3. Mode-System implementieren

**In `sot_rule_parser_v3.py` hinzufügen:**

```python
import argparse

# Am Ende der Datei:
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['explicit', 'comprehensive'],
                        default='explicit',
                        help='explicit: nur RULE-XXXX | comprehensive: inkl. semantische Regeln')
    args = parser.parse_args()

    # ... Parser-Logik mit Mode-Support
```

---

## 📋 DETAILLIERTE ANLEITUNG

### Schritt 1: Backup erstellen

```bash
cd C:\Users\bibel\Documents\Github\SSID
cp 03_core/validators/sot/sot_rule_parser_v3.py \
   03_core/validators/sot/sot_rule_parser_v3.py.backup
```

### Schritt 2: Patterns aus parse_sot_rules.py extrahieren

```bash
# Zeilen 48-150 aus parse_sot_rules.py kopieren
head -150 12_tooling/scripts/parse_sot_rules.py | tail -100 > /tmp/patterns.txt
```

### Schritt 3: In sot_rule_parser_v3.py einfügen

**Position:** Nach Zeile 200 (nach bestehenden Patterns)

**Code-Block einfügen:**
```python
# ============================================================================
# ADDITIONAL PATTERNS - Merged from parse_sot_rules.py
# ============================================================================

# Pattern #1: HASH_START Markers
HASH_START_PATTERN = r'^HASH_START::([A-Z0-9_]+)'

# Pattern #2: Path Anchors in Comments
PATH_ANCHOR_PATTERN = r'^#\s+([\d]{2}_[a-z_]+/[\w/.]+\.(?:yaml|md|py|rego))'

# Pattern #3: German MoSCoW Terms
MOSCOW_DE_PATTERN = r'\b(MUSS|SOLL|EMPFOHLEN|OPTIONAL|DARF NICHT|VERBOTEN)\b'
MOSCOW_DE_EXTENDED = r'\b(hat zu|verpflichtet|ist erforderlich|muss sein|soll sein|kann sein|darf sein)\b'

# Pattern #4: MUST EXIST Blocks
MUST_EXIST_PATTERN = r'\(MUSS EXISTIEREN\)|MUST EXIST'

# Pattern #5: Score Thresholds
SCORE_THRESHOLD_PATTERN = r'(?:Score|Coverage|Requirement|Threshold|Target)\s*(?:≥|>=|≤|<=)\s*(\d+)\s*%?'

# Pattern #6: Regional Scopes
REGIONAL_SCOPE_PATTERN = r'(eu_eea_uk_ch_li|apac|mena|africa|americas|global|jurisdiction)'

# Pattern #7: Boolean Controls
BOOLEAN_CONTROL_PATTERN = r'(immediate_failure|enabled|quarantine_trigger|strict|zero_tolerance):\s*(true|false)'

# Pattern #8: Purpose/Goal Statements
PURPOSE_PATTERN = r'^(Ziel|Purpose|Scope|Objective|Goal|Target):\s*(.+)$'
```

### Schritt 4: Detection-Logik erweitern

**In der `detect()` Methode von `LexicalDetector`:**

```python
def detect(self, file_path: Path) -> Dict[str, List[RuleSource]]:
    # ... bestehender Code ...

    # ADD: Additional pattern detection
    for pattern_name in ['HASH_START', 'PATH_ANCHOR', 'MOSCOW_DE', 'MUST_EXIST',
                         'SCORE_THRESHOLD', 'REGIONAL_SCOPE', 'BOOLEAN_CONTROL', 'PURPOSE']:
        pattern = globals()[f'{pattern_name}_PATTERN']
        for line_num, line in enumerate(lines, start=1):
            matches = re.finditer(pattern, line, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                # Extract or derive rule ID
                rule_id = self._derive_semantic_rule_id(match, pattern_name, line_num)
                if rule_id:
                    detected_rules[rule_id].append(RuleSource(...))
```

### Schritt 5: Semantic Rule ID Generation

**Neue Methode hinzufügen:**

```python
def _derive_semantic_rule_id(self, match, pattern_type, line_num):
    """
    Generate semantic rule IDs for patterns without explicit RULE-XXX

    Format: SEM-{pattern_type}-{hash[:8]}
    """
    if self.mode == 'explicit':
        return None  # Skip semantic rules in explicit mode

    content = match.group(0)
    hash_part = hashlib.sha256(content.encode()).hexdigest()[:8]
    return f"SEM-{pattern_type}-{hash_part}"
```

### Schritt 6: Mode-System testen

```bash
# Explicit Mode (sollte ~4.723 finden)
python 03_core/validators/sot/sot_rule_parser_v3.py --mode explicit

# Comprehensive Mode (sollte ~9.000+ finden)
python 03_core/validators/sot/sot_rule_parser_v3.py --mode comprehensive
```

---

## 🧪 TESTING

### Test 1: Explicit Mode

**Erwartung:** 4.723 Regeln (wie bisher)

```bash
python 03_core/validators/sot/sot_rule_parser_v3.py --mode explicit | grep "total_rules"
# Expected: "total_rules": 4723
```

### Test 2: Comprehensive Mode

**Erwartung:** ~9.000+ Regeln (inkl. semantische)

```bash
python 03_core/validators/sot/sot_rule_parser_v3.py --mode comprehensive | grep "total_rules"
# Expected: "total_rules": 9000+
```

### Test 3: Health Check

```bash
python 12_tooling/cli/sot_validator.py --self-health
# Expected: All checks PASS
```

---

## 📊 SUCCESS CRITERIA

✅ **Parser-Unification erfolgreich, wenn:**

1. **Code:**
   - [ ] Alle Patterns aus `parse_sot_rules.py` integriert
   - [ ] Alle Patterns aus `parse_part1_semantic.py` geprüft und integriert
   - [ ] Mode-System (`--mode explicit|comprehensive`) funktioniert
   - [ ] Keine Code-Duplikation mehr

2. **Funktionalität:**
   - [ ] Explicit Mode findet 4.723 Regeln (wie bisher)
   - [ ] Comprehensive Mode findet 9.000+ Regeln
   - [ ] Deduplication funktioniert
   - [ ] Hash-Integrity erhalten

3. **Testing:**
   - [ ] Alle bestehenden Tests laufen weiter
   - [ ] Neue Tests für Comprehensive Mode
   - [ ] CI/CD Pipeline läuft durch

4. **Cleanup:**
   - [ ] Alte Parser-Dateien als `_legacy` markiert
   - [ ] Nur EIN aktiver Parser im System
   - [ ] Dokumentation aktualisiert

---

## 🗂️ DATEIEN-ÜBERSICHT

### Aktive Dateien (BEHALTEN)

```
✅ 03_core/validators/sot/sot_rule_parser_v3.py     [MASTER PARSER - zu erweitern]
✅ 03_core/validators/sot/sot_extractor.py          [API Wrapper]
✅ 03_core/validators/sot/sot_validator_core.py     [Validator]
✅ 12_tooling/cli/sot_validator.py                  [CLI]
✅ 17_observability/sot_health_monitor.py           [Health Check]
```

### Legacy-Dateien (UMBENENNEN zu *_legacy.py)

```
📦 12_tooling/scripts/parse_sot_rules.py → parse_sot_rules_legacy.py
📦 16_codex/structure/level3/parse_part1_semantic.py → parse_part1_semantic_legacy.py
```

### Gelöschte Dateien (BEREITS ENTFERNT)

```
❌ 16_codex/structure/parser/sot_rule_parser.py     [DELETED]
```

---

## 🚀 DEPLOYMENT

### Nach Fertigstellung:

```bash
# 1. Tests laufen lassen
pytest 11_test_simulation/tests_compliance/ -v

# 2. Health Check
python 12_tooling/cli/sot_validator.py --self-health

# 3. Full Validation
python 12_tooling/cli/sot_validator.py --verify-all --scorecard

# 4. Commit erstellen
git add .
git commit -m "feat(parser): Unified parser with explicit/comprehensive modes

- Merged all parser logic into sot_rule_parser_v3.py
- Added mode system: --mode explicit|comprehensive
- Integrated patterns from parse_sot_rules.py
- Explicit mode: 4.723 rules (backward compatible)
- Comprehensive mode: 9.000+ rules (semantic detection)
- Marked legacy parsers with _legacy suffix
- All tests passing

🔒 ROOT-24-LOCK enforced
Co-Authored-By: Claude <noreply@anthropic.com>"

# 5. Push
git push origin main
```

---

## 📞 SUPPORT

Bei Problemen:
1. Backup wiederherstellen: `cp sot_rule_parser_v3.py.backup sot_rule_parser_v3.py`
2. Legacy-Parser nutzen: `python 12_tooling/scripts/parse_sot_rules_legacy.py`
3. Issue erstellen mit Tag `parser-unification`

---

**Ende der Anleitung**

*Erstellt: 2025-10-24*
*Status: READY FOR IMPLEMENTATION*
*Priorität: KRITISCH*

*Co-Authored-By: Claude <noreply@anthropic.com>*
