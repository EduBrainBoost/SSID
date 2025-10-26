# SSID 24×16 Shard System - Quick Start Guide

**Version:** 1.0.0
**Date:** 2025-10-24

---

## What is the Shard System?

The SSID project uses a **24×16 Matrix Architecture**:

```
24 Technical Layers  ×  16 Application Domains  =  384 Shards
```

Every piece of functionality lives in exactly one shard, making the system:
- ✅ **Deterministic** - Clear location for every feature
- ✅ **Scalable** - Add features without restructuring
- ✅ **Auditable** - Complete traceability
- ✅ **Maintainable** - Isolated components

---

## Quick Commands

### 1. Verify Shard Matrix

Check that all 384 shards exist:

```bash
python 12_tooling/scripts/verify_shard_matrix.py
```

**Expected Output:**
```
Shard Matrix Verification
================================================================================
Total Expected: 384
Existing: 384
Missing: 0
Incomplete: 0

[OK] All 384 shards are complete!
```

### 2. Analyze Duplicates and Orphans

Find files that should be in shards (dry-run, no changes):

```bash
python 12_tooling/scripts/consolidate_into_shards.py --dry-run
```

**Output:**
- Found duplicate files
- Found orphaned files (outside shard structure)
- Shows where files would be moved

### 3. Consolidate Files (CAREFUL!)

Actually move files into proper shards:

```bash
python 12_tooling/scripts/consolidate_into_shards.py --execute
```

⚠️ **WARNING:** This modifies files. Make sure you have a backup!

### 4. Run Complete Setup

Execute all setup steps in sequence:

```bash
python 12_tooling/scripts/setup_complete_shard_system.py
```

For dry-run only (no consolidation):
```bash
python 12_tooling/scripts/setup_complete_shard_system.py --skip-validation
```

To actually consolidate files:
```bash
python 12_tooling/scripts/setup_complete_shard_system.py --consolidate
```

### 5. Validate Shard-Aware SOT

Run complete SOT validation with shard awareness:

```bash
python 03_core/validators/sot/shard_aware_validator.py
```

---

## Shard Structure

Every shard follows this structure:

```
<layer>/shards/<shard_id>/
├── chart.yaml              # Single Source of Truth
├── README.md              # Documentation
├── contracts/             # API contracts
├── implementations/       # Concrete code
│   ├── python-tensorflow/
│   └── legacy/           # Consolidated old files
├── conformance/          # Contract tests
├── policies/             # Enforcement rules
└── docs/                 # Additional docs
```

### Example Shard Paths

```
01_ai_layer/shards/01_identitaet_personen/
03_core/shards/10_finanzen_banking/
16_codex/shards/16_behoerden_verwaltung/
```

---

## The 24 Layers

| # | Layer | Description |
|---|-------|-------------|
| 01 | ai_layer | AI/ML & Intelligenz |
| 02 | audit_logging | Nachweise & Beweisführung |
| 03 | core | Zentrale Logik |
| 04 | deployment | Auslieferung & Distribution |
| 05 | documentation | Dokumentation & I18N |
| 06 | data_pipeline | Datenfluss & Verarbeitung |
| 07 | governance_legal | Recht & Steuerung |
| 08 | identity_score | Reputation & Scoring |
| 09 | meta_identity | Digitale Identität |
| 10 | interoperability | Kompatibilität |
| 11 | test_simulation | Simulation & QA |
| 12 | tooling | Werkzeuge |
| 13 | ui_layer | Benutzeroberfläche |
| 14 | zero_time_auth | Sofort-Authentifizierung |
| 15 | infra | Infrastruktur |
| 16 | codex | Wissensbasis & Regeln |
| 17 | observability | Monitoring & Insights |
| 18 | data_layer | Datenhaltung |
| 19 | adapters | Anschlüsse & Schnittstellen |
| 20 | foundation | Grundlagen & Tokenomics |
| 21 | post_quantum_crypto | Zukunftskrypto |
| 22 | datasets | Datenbestände |
| 23 | compliance | Regeltreue |
| 24 | meta_orchestration | Zentrale Steuerung |

---

## The 16 Shards (Application Domains)

### Block 1: Identität & Basis (01-04)

| # | Shard | Description |
|---|-------|-------------|
| 01 | identitaet_personen | DIDs, Ausweise, Profile |
| 02 | dokumente_nachweise | Urkunden, Bescheinigungen |
| 03 | zugang_berechtigungen | Rollen, Rechte, Mandanten |
| 04 | kommunikation_daten | Nachrichten, Datenaustausch |

### Block 2: Privatleben (05-08)

| # | Shard | Description |
|---|-------|-------------|
| 05 | gesundheit_medizin | Krankenakte, Rezepte |
| 06 | bildung_qualifikationen | Zeugnisse, Abschlüsse |
| 07 | familie_soziales | Geburt, Heirat |
| 08 | mobilitaet_fahrzeuge | Führerschein, KFZ |

### Block 3: Wirtschaft & Vermögen (09-12)

| # | Shard | Description |
|---|-------|-------------|
| 09 | arbeit_karriere | Arbeitsverträge, Gehalt |
| 10 | finanzen_banking | Konten, Zahlungen, DeFi |
| 11 | versicherungen_risiken | Policen, Claims |
| 12 | immobilien_grundstuecke | Eigentum, Grundbuch |

### Block 4: Geschäft & Öffentlich (13-16)

| # | Shard | Description |
|---|-------|-------------|
| 13 | unternehmen_gewerbe | Firmendaten, B2B |
| 14 | vertraege_vereinbarungen | Smart Contracts |
| 15 | handel_transaktionen | Käufe, Supply Chain |
| 16 | behoerden_verwaltung | Ämter, Steuern |

---

## Working with Shards

### Finding the Right Shard

**Question:** Where should I put code for "AI-based identity verification"?

**Answer:**
1. **Layer:** `01_ai_layer` (it's AI/ML functionality)
2. **Shard:** `01_identitaet_personen` (it's about identity)
3. **Full Path:** `01_ai_layer/shards/01_identitaet_personen/`

### Adding Implementation

1. Navigate to shard:
   ```bash
   cd 01_ai_layer/shards/01_identitaet_personen/
   ```

2. Create implementation directory:
   ```bash
   mkdir -p implementations/python-ml/src
   ```

3. Add your code:
   ```bash
   implementations/python-ml/
   ├── manifest.yaml       # Implementation metadata
   ├── src/
   │   └── identity_verifier.py
   ├── tests/
   │   └── test_identity_verifier.py
   └── requirements.txt
   ```

4. Update chart.yaml:
   ```yaml
   implementations:
     default: "python-ml"
     available: ["python-ml"]
   ```

### Defining Dependencies

In `chart.yaml`, specify cross-shard dependencies:

```yaml
dependencies:
  required:
    - "09_meta_identity/01_identitaet_personen"  # Need DID resolution
    - "02_audit_logging"                          # Need audit logging
  optional:
    - "17_observability/01_identitaet_personen"  # Optional metrics
```

---

## Common Tasks

### Add New Feature

1. Identify layer and shard
2. Navigate to shard directory
3. Add to `implementations/<your-impl>/`
4. Update `chart.yaml` capabilities
5. Add contracts to `contracts/`
6. Add tests to `conformance/`

### Find Existing Code

Use shard structure to navigate:

```bash
# Find all identity-related code
find . -path "*/shards/01_identitaet_personen/*" -name "*.py"

# Find all core implementations
find 03_core/shards/*/implementations -name "*.py"
```

### Review Shard Health

```bash
# Check specific shard
cat 01_ai_layer/shards/01_identitaet_personen/chart.yaml

# List all implementations in shard
ls 01_ai_layer/shards/01_identitaet_personen/implementations/
```

---

## Validation & Compliance

### Automated Checks

The shard system enforces:

✅ **No PII Storage** - Only hashes allowed
✅ **Shard Boundaries** - Code in correct location
✅ **Valid Dependencies** - Cross-shard references valid
✅ **No Duplicates** - Single source of truth
✅ **Complete Structure** - All required files present

### Pre-Commit Hook

Add to `.git/hooks/pre-commit`:

```bash
#!/bin/bash
python 03_core/validators/sot/shard_aware_validator.py
```

---

## Troubleshooting

### Problem: "Shard not found"

**Solution:**
```bash
# Regenerate all shards
python 12_tooling/scripts/create_complete_shard_matrix.py
```

### Problem: "Duplicate files detected"

**Solution:**
```bash
# Analyze duplicates
python 12_tooling/scripts/consolidate_into_shards.py --dry-run

# Fix duplicates (careful!)
python 12_tooling/scripts/consolidate_into_shards.py --execute
```

### Problem: "Invalid cross-shard dependency"

**Solution:**
Check `chart.yaml` dependencies match format:
- Layer reference: `"02_audit_logging"`
- Shard reference: `"02_audit_logging/01_identitaet_personen"`

---

## Reports & Documentation

### View Reports

```bash
# Shard matrix status
cat 02_audit_logging/reports/shard_matrix_generation_report.json

# Consolidation analysis
cat 02_audit_logging/reports/shard_consolidation_report.json

# Validation results
cat 02_audit_logging/reports/shard_validation_report.json

# Complete summary
cat 02_audit_logging/reports/SHARD_SYSTEM_SETUP_SUMMARY.md
```

### Full Documentation

- **Master Definition**: `16_codex/structure/ssid_master_definition_corrected_v1.1.1.md`
- **Complete Report**: `02_audit_logging/reports/SHARD_SYSTEM_COMPLETE_FINAL_REPORT.md`

---

## Getting Help

- **Issues**: https://github.com/ssid/issues
- **Docs**: https://docs.ssid.org/
- **Email**: team@ssid.org

---

## Summary

```bash
# 1. Verify everything is set up
python 12_tooling/scripts/verify_shard_matrix.py

# 2. Find your shard
# Layer = technical domain (AI, Core, UI, etc.)
# Shard = application domain (Identity, Finance, Health, etc.)

# 3. Add your code
cd <layer>/shards/<shard>/implementations/<your-impl>/

# 4. Update chart.yaml
# Add capabilities, dependencies, etc.

# 5. Validate
python 03_core/validators/sot/shard_aware_validator.py
```

**Questions?** Check the full report:
`02_audit_logging/reports/SHARD_SYSTEM_COMPLETE_FINAL_REPORT.md`

---

*SSID 24×16 Shard System v1.0.0*
*Making complexity manageable through deterministic architecture*
