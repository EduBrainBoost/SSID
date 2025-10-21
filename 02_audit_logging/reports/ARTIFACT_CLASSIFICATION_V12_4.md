# SSID Forensic Artifact Classification v12.4

**Status:** READ-ONLY CLASSIFICATION COMPLETE
**Timestamp:** 2025-10-14T01:38:04.775655
**Audit Version:** v12.4

## Executive Summary

- **Total Artifacts:** 52,217
- **Total Size:** 120.05 MB (125,886,337 bytes)
- **Unique Extensions:** 11
- **Unique Root Modules:** 24

## Extension Distribution

| Extension | Count | Percentage | Total Size (MB) | Avg Size (bytes) |
|-----------|-------|------------|-----------------|------------------|
| `.yaml` | 26,603 | 50.95% | 61.41 | 2421 |
| `.py` | 21,729 | 41.61% | 21.08 | 1017 |
| `.md` | 1,854 | 3.55% | 3.26 | 1846 |
| `.json` | 1,200 | 2.3% | 30.58 | 26722 |
| `.rego` | 360 | 0.69% | 1.51 | 4399 |
| `.yml` | 178 | 0.34% | 1.39 | 8197 |
| `.sh` | 168 | 0.32% | 0.51 | 3207 |
| `.sha256` | 49 | 0.09% | 0.01 | 175 |
| `.ts` | 48 | 0.09% | 0.28 | 6132 |
| `.wasm` | 25 | 0.05% | 0.0 | 69 |
| `.tsx` | 3 | 0.01% | 0.01 | 4201 |

## Category Distribution

| Category | Count | Artifact % | Total Size (MB) | Size % |
|----------|-------|------------|-----------------|--------|
| **MODELS** | 27,981 | 53.59% | 93.39 | 77.79% |
| **CODE** | 21,948 | 42.03% | 21.88 | 18.23% |
| **REPORTS** | 1,854 | 3.55% | 3.26 | 2.72% |
| **POLICIES** | 360 | 0.69% | 1.51 | 1.26% |
| **WASM/HASH** | 74 | 0.14% | 0.01 | 0.01% |

## Top 10 Largest Files

| Rank | Path | Size (MB) |
|------|------|-----------|
| 1 | `23_compliance/evidence/structure_validator/2025-10-05/file_hashes.json` | 8.21 |
| 2 | `02_audit_logging/reports/knowledge_map.json` | 4.88 |
| 3 | `23_compliance/evidence/structure_validator/2025-10-06/file_hashes.json` | 2.85 |
| 4 | `23_compliance/evidence/depth_limit/depth_validation_20251009T212551Z.json` | 1.96 |
| 5 | `23_compliance/evidence/depth_limit/depth_validation_20251009T232633Z.json` | 1.96 |
| 6 | `02_audit_logging/evidence/deps/dependency_graph.json` | 1.12 |
| 7 | `02_audit_logging/reports/coverage_advice_20251009_203331.json` | 0.61 |
| 8 | `02_audit_logging/reports/coverage_advice_latest.json` | 0.61 |
| 9 | `02_audit_logging/reports/coverage_advice_20251009_203222.json` | 0.61 |
| 10 | `02_audit_logging/reports/coverage_advice_20251009_203317.json` | 0.61 |

## Root Module Anomalies (>1000 artifacts)

| Root Module | Artifact Count | Total Size (MB) |
|-------------|----------------|-----------------|
| `02_audit_logging` | 37,753 | 79.44 |
| `23_compliance` | 1,318 | 19.06 |

## Pareto Analysis (80/20 Rule)

**2 file types** cause **80%** of all artifacts:

`.yaml`, `.py`

## Generated/Temporary Files Estimate

- **Estimated Count:** 411
- **Percentage:** 0.79%
- **Note:** Estimated based on extensions and path patterns

---

**Audit Version:** `v12.4`
**Status:** `READ_ONLY_CLASSIFICATION_COMPLETE`
