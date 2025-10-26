# Mapping Tables

**Generated:** 2025-10-23T20:12:37.625361
**Total Table Rows:** 56

---

## From: ssid_master_definition_corrected_v1.1.1.md

- L312: Root | Shard 01 | Shard 02 | ... | Shard 16
- L314: 01_ai_layer | AI für Identity | AI für Dokumente | ... | AI für Behörden
- L315: 02_audit_logging | Audit Identity | Audit Dokumente | ... | Audit Behörden
- L316: 03_core | Core Identity | Core Dokumente | ... | Core Behörden
- L317: ... | ... | ... | ... | ...
- L318: 24_meta_orchestration | Orch. Identity | Orch. Dokumente | ... | Orch. Behörden
- L345: Aspekt | chart.yaml (SoT) | manifest.yaml (Impl.)
- L347: Ebene | Abstrakt | Konkret
- L348: Inhalt | Capabilities, Policies, Interfaces | Dateien, Dependencies, Artefakte
- L349: Änderungsrate | Langsam | Häufiger

... and 3 more rows

## From: SSID_structure_level3_part1_MAX.md

- L4: **Datum:** 2025-09-15 | **Status:** ROOT-24-LOCK | **Ziel:** Alle grünen Haken ✅ + Anti-Gaming Ready
- L8: **24 Root-Ordner (FIX)** | **Common MUST** | **Zentral** | **Create-on-Use** | **100-Score-Ready** |

## From: SSID_structure_level3_part2_MAX.md

- L11: Funktion | Zentraler Pfad | Zweck
- L13: **Registry** | `24_meta_orchestration/registry/` | Kanonische Modulverwaltung
- L14: **Policies** | `23_compliance/policies/` | Struktur-Policies zentral
- L15: **Evidence** | `23_compliance/evidence/` | Audit-Evidence gesammelt
- L16: **Exceptions** | `23_compliance/exceptions/` | Struktur-Ausnahmen zentral
- L17: **Risk** | `07_governance_legal/risk/` | Risk Register zentral
- L18: **CI/CD** | `.github/workflows/` + `24_meta_orchestration/triggers/ci/` | Pipeline-Logik
- L135: local REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null | pwd)
- L140: local ALLOWED_DIRS=$(yq -r '.root_level_exceptions.allowed_directories.*[]' "$EXCEPTIONS_FILE" 2>/de
- L141: local ALLOWED_FILES=$(yq -r '.root_level_exceptions.allowed_files.*[]' "$EXCEPTIONS_FILE" 2>/dev/nul

... and 31 more rows

