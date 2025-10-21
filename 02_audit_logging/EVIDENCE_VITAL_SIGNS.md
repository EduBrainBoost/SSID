# Evidence Vital Signs - Memory EKG

**Date**: 2025-10-14
**Status**: ✅ Production Ready
**Purpose**: Monthly health monitoring for evidence storage (Gedächtnis-EKG)

---

## Overview

Evidence Vital Signs provides a **monthly health snapshot** of evidence storage, analogous to YAML Vital Signs. It's a "Memory EKG" - tracking the health of the audit evidence system through 5 simple metrics.

**Philosophy**: Minimalist monitoring as a byproduct of Rolling Window cleanup, not a heavyweight observability system.

---

## 5 Key Metrics

### 1. Active Evidence Count
**What**: Number of files in active window (last 14 days)
**Threshold**: ≤ 500 files
**Status**:
- **HEALTHY**: < 250 files
- **STABLE**: 250-400 files
- **NEEDS_ATTENTION**: 400-500 files
- **CRITICAL**: > 500 files

**Why it matters**: Unbounded active evidence growth indicates retention policy failure.

---

### 2. Archive Size
**What**: Total size of WORM archives and count
**Tracked**:
- Archive count (number of `.tar.gz` files)
- Total size (MB)
- Average size per archive (MB)

**Why it matters**: Archive growth indicates rolling window is functioning, but exponential growth may signal data explosion.

---

### 3. Verify Success Rate
**What**: Percentage of archives with valid SHA-256 checksums
**Threshold**: ≥ 95%
**Status**:
- **HEALTHY**: ≥ 98%
- **CRITICAL**: < 95%

**Why it matters**: Verification failures indicate storage corruption or archiving bugs.

---

### 4. Integrity Errors
**What**: Count of checksum mismatches detected in archives
**Threshold**: 0 (zero tolerance)
**Status**:
- **HEALTHY**: 0 errors
- **CRITICAL**: > 0 errors

**Why it matters**: Any integrity error is a forensic red flag requiring immediate investigation.

---

### 5. OPA Deny Events (Last 30d)
**What**: Number of times OPA policy denied cleanup due to violations
**Threshold**: ≤ 2 denies/month
**Status**:
- **HEALTHY**: 0-2 denies
- **NEEDS_ATTENTION**: > 2 denies

**Why it matters**: Repeated denies indicate policy misconfiguration or evidence accumulation exceeding cleanup rate.

---

## Output Format

### Markdown Snapshot
**File**: `12_tooling/quality/vital_signs/evidence_vital_signs_YYYY-MM.md`

Example:
```markdown
# Evidence Vital Signs - 2025-10

**Generated**: 2025-10-14
**Overall Health**: HEALTHY ✅

## 5 Key Metrics

### 1. Active Evidence Count
- **Files**: 41
- **Size**: 4.36 MB
- **Threshold**: ≤ 500 files
- **Status**: HEALTHY

### 2. Archive Size
- **Archives**: 0
- **Total Size**: 0.0 MB
- **Avg Size**: 0.0 MB/archive
- **Status**: HEALTHY

...

## Interpretation

**Evidence storage is healthy:**
- Active evidence well within limits
- No integrity errors
- Archives verified successfully
- No policy violations

**Recommendation**: Continue monitoring monthly.
```

### JSON Report
**File**: `12_tooling/quality/vital_signs/evidence_vital_signs_YYYY-MM.json`

Machine-readable format for trend analysis and automation:
```json
{
  "month": "2025-10",
  "generated_at": "2025-10-14T12:00:00Z",
  "vital_signs": {
    "1_active_evidence": {
      "count": 41,
      "size_mb": 4.36,
      "threshold": 500,
      "status": "HEALTHY"
    },
    "2_archive_size": {...},
    "3_verify_success": {...},
    "4_integrity_errors": {...},
    "5_opa_denies": {...}
  },
  "overall_health": "HEALTHY"
}
```

---

## Historical Trend Analysis

**Script**: `evidence_vital_signs_trend.py`

Analyzes trends across multiple monthly reports (requires ≥2 months):
- Active evidence growth/decline rate
- Archive accumulation pattern
- Verify success rate stability
- Integrity error frequency
- OPA deny trends

**Output**: `evidence_vital_signs_trends.json`

Example:
```json
{
  "trend_available": true,
  "period": {
    "start": "2025-10",
    "end": "2025-12",
    "months": 3
  },
  "metrics": {
    "active_evidence": {
      "start": 41,
      "end": 35,
      "change": -6,
      "change_pct": -14.6,
      "trend": "IMPROVING",
      "interpretation": "Moderate decrease - evidence cleanup active"
    },
    ...
  },
  "overall_assessment": "STABLE"
}
```

---

## Integration with Rolling Window

Evidence Vital Signs are **automatically generated** as a byproduct of Rolling Window cleanup:

```python
# evidence_rolling_window.py
def main():
    manager = EvidenceRollingWindowManager(policy_path=args.policy)
    manager.cleanup_evidence(dry_run=dry_run)

    # Generate vital signs (monthly health check)
    if not dry_run:
        manager.generate_vital_signs()
```

**Execution**:
```bash
# Cleanup + vital signs generation
python 12_tooling/scripts/evidence_rolling_window.py \
  --policy 24_meta_orchestration/registry/evidence_retention_policy.yaml \
  --execute
```

**Output**:
```
======================================================================
Evidence Rolling Window Cleanup
======================================================================
...
Cleanup complete!

======================================================================
Evidence Vital Signs (Monthly Health Check)
======================================================================

Overall Health: HEALTHY
Markdown: evidence_vital_signs_2025-10.md
JSON:     evidence_vital_signs_2025-10.json
```

---

## Usage

### Manual Generation
```bash
# Generate current month's vital signs
python 12_tooling/quality/evidence_vital_signs_generator.py

# Generate for specific month
python 12_tooling/quality/evidence_vital_signs_generator.py --month 2025-10
```

### Trend Analysis
```bash
# Analyze historical trends (requires ≥2 months of data)
python 12_tooling/quality/evidence_vital_signs_trend.py
```

### Viewing Reports
```bash
# View latest markdown snapshot
cat 12_tooling/quality/vital_signs/evidence_vital_signs_2025-10.md

# Query JSON programmatically
jq '.overall_health' 12_tooling/quality/vital_signs/evidence_vital_signs_2025-10.json
```

---

## Comparison to YAML Vital Signs

| Feature | YAML Vital Signs | Evidence Vital Signs |
|---------|------------------|---------------------|
| **Purpose** | Monitor YAML ecology health | Monitor evidence storage health |
| **Frequency** | Quarterly | Monthly |
| **Metrics** | 5 (count, backup ratio, dedup, OPA denies, retention) | 5 (active count, archive size, verify success, integrity, OPA denies) |
| **Trigger** | Manual / CI quarterly | Auto-generated during cleanup |
| **Output** | Markdown + JSON | Markdown + JSON |
| **Trend Analysis** | ✅ | ✅ |

**Commonality**: Both provide **minimalist, P95-style health metrics** as Markdown snapshots with historical trend tracking.

---

## Benefits

### 1. Lightweight Monitoring
- **< 10 KB per monthly report**
- No heavyweight observability infrastructure
- Markdown-readable, JSON-queryable

### 2. Forensic Early Warning
- Detects integrity errors immediately
- Tracks verification success rate trends
- Identifies policy compliance issues

### 3. Autophagy Validation
- Confirms rolling window is functioning
- Validates active evidence stays bounded
- Tracks archive accumulation patterns

### 4. Historical Context
- Month-over-month trend analysis
- Identifies degradation patterns early
- Provides evidence for capacity planning

---

## Health Status Matrix

| Overall Health | Active Count | Integrity Errors | Verify Success | OPA Denies |
|---------------|--------------|------------------|----------------|------------|
| **HEALTHY** | < 250 | 0 | ≥ 98% | 0-1 |
| **STABLE** | 250-400 | 0 | ≥ 98% | 0-2 |
| **NEEDS_ATTENTION** | 400-500 | 0 | 95-98% | 2-5 |
| **CRITICAL** | > 500 | > 0 | < 95% | > 5 |

---

## Quarterly Review Checklist

**Review Questions** (Every 3 months):

1. **Active Evidence Trend**
   - Is active count growing or shrinking?
   - Is cleanup frequency adequate?

2. **Archive Health**
   - Are archives being created regularly?
   - Is verify success rate stable at ≥95%?
   - Any integrity errors detected?

3. **Policy Compliance**
   - Are OPA denies increasing?
   - Root cause of denies identified?

4. **Storage Capacity**
   - Is archive growth linear or exponential?
   - Will we exceed capacity in next 6 months?

5. **Trend Assessment**
   - Overall trend: IMPROVING, STABLE, or DEGRADING?
   - Any corrective actions needed?

---

## Example: Interpreting Vital Signs

### Scenario 1: Healthy System
```
Active Evidence: 45 files (4.2 MB) - HEALTHY
Archive Size: 3 archives (12.5 MB) - HEALTHY
Verify Success: 100% (3/3) - HEALTHY
Integrity Errors: 0 - HEALTHY
OPA Denies: 0 - HEALTHY

Overall: HEALTHY ✅
```

**Interpretation**: System is operating normally. Rolling window functioning, no issues detected.

**Action**: Continue monthly monitoring.

---

### Scenario 2: Approaching Limits
```
Active Evidence: 425 files (85.3 MB) - NEEDS_ATTENTION
Archive Size: 12 archives (45.2 MB) - HEALTHY
Verify Success: 96.5% (11/12) - HEALTHY
Integrity Errors: 0 - HEALTHY
OPA Denies: 3 - NEEDS_ATTENTION

Overall: NEEDS_ATTENTION ⚠️
```

**Interpretation**: Active evidence approaching limit (500 files). Cleanup frequency may be insufficient.

**Action**:
1. Execute rolling window cleanup immediately
2. Review retention policy (consider shortening active window 14→10 days)
3. Investigate OPA deny root causes

---

### Scenario 3: Critical Issue
```
Active Evidence: 520 files (105.2 MB) - CRITICAL
Archive Size: 8 archives (38.1 MB) - HEALTHY
Verify Success: 87.5% (7/8) - CRITICAL
Integrity Errors: 1 - CRITICAL
OPA Denies: 8 - CRITICAL

Overall: CRITICAL 🔴
```

**Interpretation**: Multiple critical issues - active evidence exceeded limit, verification failing, integrity error detected.

**Action**:
1. **IMMEDIATE**: Investigate integrity error (checksum mismatch indicates corruption)
2. **URGENT**: Verify archive storage health
3. Force cleanup run with manual verification
4. Review OPA deny logs for pattern
5. Consider emergency retention policy adjustment

---

## Success Criteria

Evidence Vital Signs implementation is successful if:

1. **Monthly snapshots generated** automatically during cleanup
2. **All 5 metrics tracked** with clear thresholds
3. **Overall health status** accurately reflects system state
4. **Historical trends available** after 2+ months
5. **Markdown readable** without tools
6. **JSON queryable** for automation
7. **< 10 KB overhead** per monthly report

---

## Files Created

### Scripts
- `12_tooling/quality/evidence_vital_signs_generator.py` - Main generator (185 LOC)
- `12_tooling/quality/evidence_vital_signs_trend.py` - Trend analyzer (200 LOC)

### Reports (Auto-generated)
- `12_tooling/quality/vital_signs/evidence_vital_signs_YYYY-MM.md` - Monthly snapshot
- `12_tooling/quality/vital_signs/evidence_vital_signs_YYYY-MM.json` - Machine-readable report
- `12_tooling/quality/vital_signs/evidence_vital_signs_trends.json` - Historical trends

### Documentation
- `02_audit_logging/EVIDENCE_VITAL_SIGNS.md` - This file

---

## Future Enhancements (Optional)

**Not required, but could be added later**:

1. **Alerting Integration**
   - Email/Slack notifications for CRITICAL status
   - Automated ticket creation for integrity errors

2. **Visual Dashboard**
   - Line charts for metric trends
   - Heat map for monthly health status

3. **Predictive Analysis**
   - Forecast when active evidence will exceed limit
   - Recommend cleanup frequency adjustments

4. **CI Integration**
   - GitHub Actions badge showing current health
   - PR comments with health status changes

---

## Comparison to Traditional Monitoring

| Traditional Monitoring | Evidence Vital Signs |
|----------------------|---------------------|
| Real-time metrics | Monthly snapshots |
| Time-series database | JSON files |
| Grafana dashboards | Markdown reports |
| Prometheus alerts | Status thresholds |
| Complex infrastructure | ~400 LOC total |
| Continuous overhead | Zero runtime cost between cleanups |

**Philosophy**: Evidence Vital Signs prioritizes **simplicity and sustainability** over real-time observability. It's a "good enough" solution for audit evidence monitoring that doesn't require dedicated infrastructure.

---

## Status

✅ **Production Ready**

**Implemented**:
- 5-metric health monitoring
- Markdown + JSON output formats
- Historical trend analysis
- Auto-generation during cleanup
- Complete documentation

**Tested**:
- Generated initial report (2025-10)
- All 5 metrics tracked correctly
- Overall health: HEALTHY
- Integration with rolling window verified

**Next Action**: Accumulate 2+ months of data for trend analysis validation.

---

**Maintained by**: Automated (generated during rolling window cleanup)
**Review Frequency**: Monthly (during cleanup) + Quarterly (trend review)
**Last Updated**: 2025-10-14
