# MoSCoW Scorecard Registry

**Purpose:** Time-series storage of MoSCoW Priority Scorecard validation results for trend analysis and compliance reporting.

---

## Directory Structure

```
scorecards/
├── main/                    # Production branch scorecards
│   ├── scorecard_20251017T152536Z_a6e6d2a.json
│   ├── scorecard_20251017T152536Z_a6e6d2a.md
│   └── ...
├── develop/                 # Development branch scorecards
│   └── ...
├── feature-*/              # Feature branch scorecards (optional)
│   └── ...
└── README.md               # This file
```

---

## Naming Convention

**Format:** `scorecard_<ISO8601_TIMESTAMP>_<SHORT_COMMIT_SHA>.<ext>`

**Examples:**
- `scorecard_20251017T152536Z_a6e6d2a.json`
- `scorecard_20251017T152536Z_a6e6d2a.md`

**Timestamp Format:** `YYYYMMDDTHHMMSSZ` (UTC)

---

## File Formats

### JSON Format (`.json`)

Machine-readable format for automation and trending:

```json
{
  "version": "3.2.0",
  "timestamp": "2025-10-17T15:25:36.784617Z",
  "moscow_scorecard": {
    "must_rules": {
      "total": 48,
      "passed": 48,
      "failed": 0,
      "warnings": 0
    },
    "should_rules": {
      "total": 15,
      "passed": 15,
      "failed": 0,
      "warnings": 0
    },
    "have_rules": {
      "total": 6,
      "passed": 6,
      "failed": 0,
      "warnings": 0
    },
    "moscow_score": 81.3,
    "overall_status": "PASS",
    "ci_blocking_failures": 0
  },
  "detailed_results": { /* ... */ }
}
```

### Markdown Format (`.md`)

Human-readable format for reports and documentation. Includes:
- Priority breakdown table
- Score calculation
- Detailed rule-by-rule results
- CI impact assessment

---

## Retention Policy

| Branch | Retention | Rationale |
|--------|-----------|-----------|
| `main` | Permanent | Production compliance audit trail |
| `develop` | 180 days | Development tracking |
| `feature-*` | 30 days | Short-lived branch validation |
| `hotfix-*` | 180 days | Critical fix documentation |

**CI Artifact Retention:** 90 days (configurable in workflow)

---

## Usage

### Automatic Population

Scorecards are automatically generated and stored by the CI MoSCoW Gate workflow:

```yaml
# .github/workflows/ci_moscow_gate.yml
- name: Archive Scorecard to Registry
  run: |
    TIMESTAMP=$(date -u +"%Y%m%dT%H%M%SZ")
    COMMIT_SHA=$(git rev-parse --short HEAD)
    BRANCH_NAME=$(git rev-parse --abbrev-ref HEAD)

    cp scorecard.json \
      02_audit_logging/registry/scorecards/$BRANCH_NAME/scorecard_${TIMESTAMP}_${COMMIT_SHA}.json
```

### Manual Storage

```bash
# Generate scorecard
python 12_tooling/cli/sot_validator.py \
  --scorecard \
  --input 16_codex/contracts/sot/sot_contract.yaml \
  --export

# Move to registry
TIMESTAMP=$(date -u +"%Y%m%dT%H%M%SZ")
COMMIT=$(git rev-parse --short HEAD)
BRANCH=$(git branch --show-current)

mkdir -p 02_audit_logging/registry/scorecards/$BRANCH
cp scorecard_*.json 02_audit_logging/registry/scorecards/$BRANCH/scorecard_${TIMESTAMP}_${COMMIT}.json
cp scorecard_*.md 02_audit_logging/registry/scorecards/$BRANCH/scorecard_${TIMESTAMP}_${COMMIT}.md
```

---

## Trend Analysis

Use the trend analysis script to generate historical reports:

```bash
python 12_tooling/scripts/analyze_scorecard_trends.py \
  --registry 02_audit_logging/registry/scorecards/main \
  --output 02_audit_logging/reports/moscow_trend_report.md
```

**Output includes:**
- Score progression over time
- MUST/SHOULD/HAVE pass rate trends
- Regression detection
- Compliance KPIs

---

## Querying Registry

### Find Latest Scorecard

```bash
# Latest in main branch
ls -t 02_audit_logging/registry/scorecards/main/scorecard_*.json | head -n 1
```

### Extract Score from JSON

```bash
LATEST=$(ls -t 02_audit_logging/registry/scorecards/main/scorecard_*.json | head -n 1)
python -c "import json; print(f'Score: {json.load(open(\"$LATEST\"))[\"moscow_scorecard\"][\"moscow_score\"]}%')"
```

### Compare Two Scorecards

```bash
python 12_tooling/scripts/compare_scorecards.py \
  --old scorecards/main/scorecard_20251001_abc123.json \
  --new scorecards/main/scorecard_20251017_def456.json
```

---

## Integration with Audit Logging

Scorecards are part of the broader SSID audit logging framework:

- **WORM Storage:** Scorecards can be anchored to immutable storage
- **Blockchain Anchoring:** IPFS CID for scorecard JSON
- **Evidence Chain:** Linked to `02_audit_logging/evidence_trails/`
- **Compliance Reports:** Referenced in quarterly compliance bundles

---

## Metrics and KPIs

### Key Metrics Tracked

1. **MoSCoW Score** - Weighted compliance score (0-100%)
2. **MUST Pass Rate** - Critical rule compliance percentage
3. **SHOULD Pass Rate** - Best practice adoption percentage
4. **HAVE Pass Rate** - Optional feature usage percentage
5. **CI Blocking Failures** - Count of MUST rule violations
6. **Score Velocity** - Rate of score change over time

### Dashboard Integration

Scorecards can be ingested into dashboards:
- Grafana (via JSON export)
- Kibana (via Elasticsearch)
- Custom web dashboards (via REST API)

---

## Security and Access Control

- **Read Access:** All team members (audit transparency)
- **Write Access:** CI pipeline only (integrity)
- **Branch Protection:** Main branch requires passing gate

---

## FAQ

**Q: Why store both JSON and Markdown?**
A: JSON for automation/trending, Markdown for human review and reports.

**Q: How long until registry becomes too large?**
A: At 1 commit/day, ~365 files/year. At ~20KB/file = ~7.3MB/year. Retention policies keep this manageable.

**Q: Can I regenerate scorecard for old commit?**
A: Yes, checkout old commit and run CLI manually. However, CI-generated scorecards are preferred for audit trail integrity.

**Q: What if score drops below threshold?**
A: CI fails, preventing merge. Team must fix violations before proceeding.

---

**Version:** 1.0.0
**Last Updated:** 2025-10-17
**Maintained By:** SSID Core Team
