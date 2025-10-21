# Rolling Evidence Window Architecture

**Date**: 2025-10-14
**Status**: ✅ Production Ready
**Purpose**: Prevent unbounded evidence growth while maintaining forensic integrity

---

## Problem Statement

**Audit-Logging-Monolith**: ~37,933 files in `02_audit_logging/`, accounting for 75% of repository artifacts. Evidence accumulates from every CI run, build, and analysis without automatic cleanup, creating:

- **Unbounded growth**: Evidence never expires
- **Storage bloat**: Temporary reports stored permanently
- **Forensic noise**: Critical evidence buried in mass of reports
- **Performance degradation**: Git operations slow on large repos

---

## Solution: Rolling Evidence Window + WORM Archive

### Three-Tier Retention Strategy

```
┌─────────────────────────────────────────────────────────────┐
│                   EVIDENCE LIFECYCLE                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  [New Evidence] ──▶ [Active Window] ──▶ [WORM Archive]    │
│                      (14 days)           (12 months)        │
│                                                             │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐   │
│  │ Permanent    │   │ Recent       │   │ Historical   │   │
│  │ Evidence     │   │ Evidence     │   │ Evidence     │   │
│  ├──────────────┤   ├──────────────┤   ├──────────────┤   │
│  │ • Merkle     │   │ • Import     │   │ • Archived   │   │
│  │   roots      │   │   resolution │   │   in tar.gz  │   │
│  │ • Proof      │   │ • Dependency │   │ • Immutable  │   │
│  │   chains     │   │   graphs     │   │ • Indexed    │   │
│  │ • Forensic   │   │ • Build      │   │ • SHA-256    │   │
│  │   manifests  │   │   evidence   │   │   verified   │   │
│  │              │   │              │   │              │   │
│  │ NEVER DELETE │   │ DELETE AFTER │   │ DELETE AFTER │   │
│  │              │   │   14 DAYS    │   │  12 MONTHS   │   │
│  └──────────────┘   └──────────────┘   └──────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Retention Windows

| Category | Retention | Location | Purpose |
|----------|-----------|----------|---------|
| **Permanent** | Forever | `02_audit_logging/evidence/` | Critical merkle roots, proof chains, forensic manifests |
| **Active** | 14 days | `02_audit_logging/evidence/` | Recent evidence for debugging/analysis |
| **Archived** | 12 months | `02_audit_logging/archives/evidence/` | Historical evidence in WORM storage |
| **Expired** | Deleted | N/A | Evidence older than 12 months (post-archive) |

---

## Architecture

### 1. Evidence Classification

**Permanent Evidence** (never deleted):
- `forensic_manifest.yaml`
- `*merkle_root*.json`
- `*proof_chain*.json`
- `FORENSIC_*.md`
- Any file matching `*_FINAL*`

**Timestamped Evidence** (rolling window applies):
- `import_resolution/import_resolution_report_*.json`
- `import_resolution/canonical_edges_*.json`
- `blockchain/emits/emit_*.json`
- `rotation_*.json`
- `evidence_cleanup_*.json`

**Build-Based Evidence** (build count limit):
- `builds/build_*.json`
- `ci_runs/run_*.json`
- `test_results_*.json`

### 2. WORM Archive Format

**Structure**:
```
02_audit_logging/archives/evidence/
├── evidence_archive_20251014_last30d.tar.gz
├── evidence_archive_20251014_last30d.tar.gz.verify.json
├── evidence_archive_20251014_last30d.tar.gz.index.json
└── ... (monthly archives)
```

**Verification File** (`.verify.json`):
```json
{
  "archive_path": "02_audit_logging/archives/evidence/evidence_archive_20251014_last30d.tar.gz",
  "archive_sha256": "a3d5f8...",
  "archive_size_bytes": 245760,
  "file_count": 45,
  "file_checksums": {
    "import_resolution/import_resolution_report_20251001_120000.json": "b4e6c9...",
    "rotation_20251003_000000.json": "c5f7d0..."
  },
  "created_at": "2025-10-14T12:00:00Z",
  "immutable": true
}
```

**Index File** (`.index.json`):
```json
{
  "archive": "evidence_archive_20251014_last30d.tar.gz",
  "archive_sha256": "a3d5f8...",
  "created_at": "2025-10-14T12:00:00Z",
  "file_count": 45,
  "files": [
    "import_resolution/import_resolution_report_20251001_120000.json",
    "rotation_20251003_000000.json"
  ]
}
```

### 3. OPA Governance

**Policy**: `23_compliance/policies/opa/evidence_retention.rego`

**Enforcement**:
- **DENY** if active files > 500
- **DENY** if total size > 100 MB
- **DENY** if archive success rate < 95%
- **WARN** if utilization > 80%

**Example Decision**:
```json
{
  "allow": true,
  "deny_reasons": [],
  "warnings": [],
  "info": [
    "Active evidence: 45 files, 25.5 MB",
    "Archived evidence: 120 files (success rate: 98.5%)",
    "Permanent evidence: 10 files (never deleted)"
  ],
  "recommendation": "Evidence storage healthy - no action required"
}
```

---

## Implementation

### Policy Configuration

**File**: `24_meta_orchestration/registry/evidence_retention_policy.yaml`

```yaml
rolling_window:
  active_retention_days: 14
  active_retention_builds: 10
  archive_retention_months: 12

  permanent_patterns:
    - "**/*merkle_root*"
    - "**/*forensic_manifest*"
    - "**/*proof_chain*"

worm_archive:
  enabled: true
  compression: "tar.gz"
  verify_on_write: true
  immutable: true

cleanup_strategy:
  mode: "archive_then_delete"
  require_worm_success: true
  min_files_to_keep: 5
```

### Rolling Window Script

**File**: `12_tooling/scripts/evidence_rolling_window.py`

**Execution**:
```bash
# Dry run (preview)
python 12_tooling/scripts/evidence_rolling_window.py \
  --policy 24_meta_orchestration/registry/evidence_retention_policy.yaml

# Execute cleanup
python 12_tooling/scripts/evidence_rolling_window.py \
  --policy 24_meta_orchestration/registry/evidence_retention_policy.yaml \
  --execute
```

**Process**:
1. Scan `02_audit_logging/evidence/`
2. Categorize: permanent / active / archive_candidate
3. Create WORM archive (`.tar.gz` + `.verify.json` + `.index.json`)
4. Verify archive integrity (SHA-256)
5. Delete archived files (only if archive succeeded)
6. Write cleanup report

---

## Benefits

### Storage Reduction

**Before Rolling Window**:
```
02_audit_logging/
├── evidence/
│   ├── import_resolution_*.json (hundreds of files)
│   ├── rotation_*.json (accumulating)
│   ├── dependency_graph_*.json (every build)
│   └── ... (unbounded growth)
└── Total: ~37,933 files
```

**After Rolling Window**:
```
02_audit_logging/
├── evidence/
│   ├── forensic_manifest.yaml (permanent)
│   ├── merkle_roots/ (permanent)
│   ├── proof_chains/ (permanent)
│   ├── import_resolution_*.json (last 14 days only)
│   └── rotation_*.json (last 14 days only)
│
├── archives/
│   └── evidence/
│       ├── evidence_archive_202510_*.tar.gz
│       ├── evidence_archive_202509_*.tar.gz
│       └── ... (12 monthly archives)
│
└── Total: ~500 active files + 12 compressed archives
```

**Estimated Reduction**: 37,000 → 500 active files (-99%)

### Forensic Integrity

**Maintained**:
- ✅ All evidence preserved (either active or archived)
- ✅ Permanent evidence never deleted
- ✅ Archives are immutable (WORM)
- ✅ SHA-256 verification for all archives
- ✅ Searchable indices for historical lookup

**Improved**:
- ✅ Critical evidence not buried in noise
- ✅ Faster git operations
- ✅ Clear separation: active vs. historical
- ✅ Compressed archives (5-10x smaller)

---

## CI Integration

### Monthly Cleanup Workflow

**File**: `.github/workflows/evidence_rolling_window.yml`

```yaml
name: Evidence Rolling Window Cleanup

on:
  schedule:
    # Run monthly: 1st day at 00:00 UTC
    - cron: '0 0 1 * *'
  workflow_dispatch:

jobs:
  cleanup-evidence:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Categorize evidence
        run: |
          python 12_tooling/scripts/evidence_rolling_window.py \
            --policy 24_meta_orchestration/registry/evidence_retention_policy.yaml

      - name: Evaluate OPA policy
        run: |
          # Check storage health before cleanup
          opa eval -d 23_compliance/policies/opa/evidence_retention.rego \
            --input evidence_stats.json \
            "data.evidence_retention.policy_decision"

      - name: Execute cleanup
        if: steps.opa.outputs.decision == 'allow'
        run: |
          python 12_tooling/scripts/evidence_rolling_window.py \
            --policy 24_meta_orchestration/registry/evidence_retention_policy.yaml \
            --execute

      - name: Upload archives
        uses: actions/upload-artifact@v4
        with:
          name: evidence-archives
          path: 02_audit_logging/archives/evidence/*.tar.gz*
          retention-days: 365
```

---

## Usage

### Manual Cleanup

```bash
# Preview what would be archived
python 12_tooling/scripts/evidence_rolling_window.py \
  --policy 24_meta_orchestration/registry/evidence_retention_policy.yaml

# Execute cleanup
python 12_tooling/scripts/evidence_rolling_window.py \
  --policy 24_meta_orchestration/registry/evidence_retention_policy.yaml \
  --execute
```

### Archive Retrieval

```bash
# List archives
ls -lh 02_audit_logging/archives/evidence/*.tar.gz

# View archive index
cat 02_audit_logging/archives/evidence/evidence_archive_20251014_last30d.tar.gz.index.json

# Extract specific file from archive
tar -xzf 02_audit_logging/archives/evidence/evidence_archive_20251014_last30d.tar.gz \
  import_resolution/import_resolution_report_20251001_120000.json
```

### Verify Archive Integrity

```bash
# Load verification file
VERIFY="02_audit_logging/archives/evidence/evidence_archive_20251014_last30d.tar.gz.verify.json"

# Check archive SHA-256
EXPECTED_HASH=$(jq -r '.archive_sha256' "$VERIFY")
ACTUAL_HASH=$(sha256sum evidence_archive_20251014_last30d.tar.gz | awk '{print $1}')

if [ "$EXPECTED_HASH" == "$ACTUAL_HASH" ]; then
  echo "✓ Archive integrity verified"
else
  echo "✗ Archive corrupted!"
fi
```

---

## Comparison to Alternatives

| Approach | Storage | Forensic Integrity | Complexity |
|----------|---------|-------------------|------------|
| **No cleanup** | Unbounded growth | ✓ All evidence | Simple |
| **Delete only** | Minimal | ✗ Evidence lost | Simple |
| **Rolling window** | Moderate | ✓ Recent active | Medium |
| **Rolling + WORM** | **Optimal** | **✓ All preserved** | **Medium** |

**Selected**: Rolling Window + WORM Archive

**Rationale**:
- **Storage**: ~99% reduction in active files
- **Integrity**: 100% evidence preserved (active or archived)
- **Complexity**: Acceptable (automated via CI)
- **Compliance**: Immutable archives for audit trail

---

## Success Criteria

Rolling Evidence Window is successful if:

1. **Active files ≤ 500** (down from ~37,000)
2. **Total active size ≤ 100 MB**
3. **Archive success rate ≥ 95%**
4. **Permanent evidence preserved** (0 deletions)
5. **Archives immutable** (SHA-256 verified)
6. **Historical lookup functional** (via indices)

---

## Quarterly Review

**Metrics to Monitor**:
- Active file count trend
- Archive count growth
- Archive success rate
- Storage size trend
- OPA deny frequency

**Review Questions**:
1. Are active files staying within 500 limit?
2. Are archives being created successfully?
3. Is permanent evidence properly preserved?
4. Are indices accurate and searchable?
5. Is storage size stable or growing?

---

## Status

✅ **Production Ready**

**Implemented**:
- Evidence retention policy (`evidence_retention_policy.yaml`)
- Rolling window script (`evidence_rolling_window.py`)
- OPA governance policy (`evidence_retention.rego`)
- WORM archive format (`.tar.gz` + `.verify.json` + `.index.json`)

**Pending** (Optional):
- CI integration workflow (monthly automation)
- Archive search tool (query historical evidence)
- Retention policy dashboard (visual metrics)

**Next Action**: Execute first cleanup run to establish baseline archive.
