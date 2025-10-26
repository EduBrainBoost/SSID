# UTF-8 Encoding Fix für SSID Agent v1.1

## Problem

Ollama gibt UTF-8 aus, aber Windows-Terminals (PowerShell, CMD) erwarten standardmäßig Windows-1252 (CP1252).
Dadurch entstehen falsche Zeichen:
- `ü` → `�`
- `ä` → `�`
- `ö` → `�`

## Lösung

### 1. Code-Fix (bereits implementiert ✅)

In `agent_cli.py` Zeile 143-149:

```python
result = subprocess.run(
    ["ollama", "run", model, prompt],
    capture_output=True,
    text=True,
    encoding="utf-8",    # ← UTF-8 erzwingen
    errors="ignore"      # ← ungültige Zeichen überspringen
)
```

### 2. Terminal-Fix (nur für PowerShell/CMD)

**Für PowerShell:**
```powershell
chcp 65001
$OutputEncoding = [Console]::OutputEncoding = [Text.UTF8Encoding]::UTF8
```

**Für Git Bash/MINGW64:**
Kein Fix nötig - Git Bash nutzt bereits UTF-8 (`LC_CTYPE="de_DE.UTF-8"`).

### 3. Permanente Lösung (optional)

Füge zu deinem PowerShell-Profil hinzu:
```powershell
notepad $PROFILE
```

Ergänze:
```powershell
chcp 65001 > $null
$OutputEncoding = [Console]::OutputEncoding = [Text.UTF8Encoding]::UTF8
```

## Status

✅ Code-Fix implementiert in `agent_cli.py`
✅ Git Bash: UTF-8 bereits aktiv
⚠️ PowerShell/CMD: Manueller `chcp 65001`-Befehl nötig

## Test

```bash
python 12_tooling/agent/agent_cli.py llm "Schreibe pytest für validate_all_sot_rules()"
```

Erwartete Ausgabe:
- **Vorher:** `m�ssen`, `k�nnten`, `f�r`
- **Nachher:** `müssen`, `könnten`, `für`

## Technische Details

- **Ollama-Output:** UTF-8 (Standard)
- **subprocess.run:** Nutzt jetzt `encoding="utf-8"` statt System-Default
- **Git Bash Locale:** `de_DE.UTF-8` (bereits korrekt)
- **PowerShell/CMD:** Nutzt `cp1252` → muss manuell auf UTF-8 umgestellt werden

---

**Version:** v1.1
**Datum:** 2025-10-22
**Status:** ✅ Production-Ready
