# 23_compliance - Shards

## Overview

This directory contains all 16 shards for the **23_compliance** layer (Regeltreue).

## Structure

Each shard follows the SSID Master Definition v1.1.1 structure:

```
23_compliance/shards/
├── 01_identitaet_personen/
├── 02_dokumente_nachweise/
├── 03_zugang_berechtigungen/
├── 04_kommunikation_daten/
├── 05_gesundheit_medizin/
├── 06_bildung_qualifikationen/
├── 07_familie_soziales/
├── 08_mobilitaet_fahrzeuge/
├── 09_arbeit_karriere/
├── 10_finanzen_banking/
├── 11_versicherungen_risiken/
├── 12_immobilien_grundstuecke/
├── 13_unternehmen_gewerbe/
├── 14_vertraege_vereinbarungen/
├── 15_handel_transaktionen/
└── 16_behoerden_verwaltung/
```

## Shard Details

Each shard contains:
- `chart.yaml` - Single Source of Truth (capabilities, policies, interfaces)
- `README.md` - Shard-specific documentation
- `contracts/` - API contracts (OpenAPI, JSON Schema)
- `implementations/` - Concrete implementations (Python, Rust, etc.)
- `conformance/` - Contract tests
- `policies/` - Enforcement rules
- `docs/` - Additional documentation

## Matrix Architecture

This is part of the **24×16 Matrix Architecture** (384 total shards):
- 24 Root Layers (vertical)
- 16 Shards per Layer (horizontal)

## References

- Master Definition: `16_codex/structure/ssid_master_definition_corrected_v1.1.1.md`
- Architecture Guide: `05_documentation/architecture/`
