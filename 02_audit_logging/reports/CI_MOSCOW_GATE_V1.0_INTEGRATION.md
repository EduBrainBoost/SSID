# CI MoSCoW Gate v1.0 - Integration Guide

**Version:** 1.0.0
**Date:** 2025-10-17
**Author:** SSID Core Team
**Status:** ✅ PRODUCTION READY

---

## Executive Summary

The **CI MoSCoW Gate v1.0** is a GitHub Actions workflow that automatically validates MoSCoW Priority compliance on every commit to `main` and `develop` branches, as well as all pull requests. It provides:

- ✅ **Automated Scorecard Generation** - Run on every CI build
- ✅ **Score Threshold Enforcement** - Configurable minimum score (default: 75%)
- ✅ **CI Blocking for MUST Failures** - Exit code 24 prevents merge
- ✅ **Artifact Archival** - 90-day retention of scorecard files
- ✅ **Registry Storage** - Permanent time-series storage for trend analysis
- ✅ **Pull Request Comments** - Inline scorecard display for reviewers
- ✅ **Trend Reporting** - Automated regression detection and KPI tracking
- ✅ **Dynamic Badge Generation** - shields.io badge for README

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     GitHub Actions CI Pipeline                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Checkout Code                                               │
│  2. Setup Python 3.12                                           │
│  3. Generate MoSCoW Scorecard  ──────────────┐                  │
│     └── python sot_validator.py --scorecard  │                  │
│                                               │                  │
│  4. Extract Score from JSON ◄─────────────────┘                 │
│     └── Parse moscow_score & ci_blocking                        │
│                                                                 │
│  5. Archive to Registry                                         │
│     └── 02_audit_logging/registry/scorecards/<branch>/          │
│                                                                 │
│  6. Upload Artifacts (90-day retention)                         │
│                                                                 │
│  7. Comment on PR (if pull_request event)                       │
│                                                                 │
│  8. Evaluate Threshold                                          │
│     ├── Score < MIN_SCORE? ──> EXIT 1 (fail)                    │
│     └── MUST failures > 0? ──> EXIT 24 (ROOT-24-LOCK)           │
│                                                                 │
│  9. Generate Trend Report (main branch only)                    │
│     └── python analyze_scorecard_trends.py                      │
│                                                                 │
│ 10. Commit Registry & Report (main branch only)                 │
│     └── Auto-commit with [skip ci] tag                          │
│                                                                 │
│ 11. Generate Dynamic Badge (main branch only)                   │
│     └── moscow_badge.json for shields.io                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Files and Components

### 1. GitHub Action Workflow

**File:** `.github/workflows/ci_moscow_gate.yml`

**Key Configuration:**

```yaml
env:
  MIN_SCORE: 75.0  # Minimum required MoSCoW score
  PYTHON_VERSION: "3.12"
  CONFIG_FILE: "16_codex/contracts/sot/sot_contract.yaml"
```

**Jobs:**
1. `moscow-validation` - Main validation job (runs on all events)
2. `generate-badge` - Badge generation (runs on main branch only)

**Exit Codes:**
- `0` - All checks passed
- `1` - Score below threshold
- `24` - MUST rule failures (ROOT-24-LOCK)

### 2. Scorecard Registry

**Location:** `02_audit_logging/registry/scorecards/`

**Structure:**
```
scorecards/
├── main/
│   ├── scorecard_20251017T152536Z_a6e6d2a.json
│   └── scorecard_20251017T152536Z_a6e6d2a.md
├── develop/
└── feature-*/
```

**Naming:** `scorecard_<ISO8601_TIMESTAMP>_<SHORT_COMMIT_SHA>.<ext>`

**Retention:**
- `main`: Permanent (audit trail)
- `develop`: 180 days
- `feature-*`: 30 days

### 3. Trend Analysis Script

**File:** `12_tooling/scripts/analyze_scorecard_trends.py`

**Usage:**
```bash
python analyze_scorecard_trends.py \
  --registry 02_audit_logging/registry/scorecards/main \
  --output 02_audit_logging/reports/moscow_trend_report.md
```

**Outputs:**
- Score progression table
- Statistical analysis (avg, min, max, trend)
- Regression detection
- Compliance KPIs
- Recommendations

**Automated Execution:** Runs on every main branch commit

### 4. Dynamic Badge

**File:** `02_audit_logging/reports/moscow_badge.json`

**Format:**
```json
{
  "schemaVersion": 1,
  "label": "MoSCoW Score",
  "message": "81.3%",
  "color": "brightgreen"
}
```

**Badge URL:**
```markdown
![MoSCoW Score](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/<org>/<repo>/main/02_audit_logging/reports/moscow_badge.json)
```

**Color Scale:**
- `brightgreen` - Score ≥ 90%
- `green` - Score 75-89%
- `yellow` - Score 60-74%
- `red` - Score < 60%

---

## Setup Instructions

### Step 1: Enable Workflow

The workflow is already committed to `.github/workflows/ci_moscow_gate.yml`. It will run automatically on:
- Push to `main` or `develop` branches
- Pull requests targeting `main` or `develop`
- Manual trigger via `workflow_dispatch`

**No additional configuration required unless customizing thresholds.**

### Step 2: Configure Minimum Score (Optional)

Edit `.github/workflows/ci_moscow_gate.yml`:

```yaml
env:
  MIN_SCORE: 75.0  # Change to desired threshold (0-100)
```

**Recommendations:**
- **Strict:** 90.0 (All MUST + most SHOULD)
- **Standard:** 75.0 (All MUST + some SHOULD)
- **Lenient:** 60.0 (All MUST minimum)

### Step 3: Set Up Branch Protection (Recommended)

**GitHub Settings → Branches → Branch protection rules for `main`:**

1. ✅ Require status checks to pass before merging
2. ✅ Require branches to be up to date before merging
3. ✅ Status checks that are required:
   - `moscow-validation` ← Add this check

**This ensures MoSCoW Gate must pass before merge.**

### Step 4: Add Badge to README (Optional)

Add to your repository's `README.md`:

```markdown
# SSID Project

![MoSCoW Score](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/<org>/<repo>/main/02_audit_logging/reports/moscow_badge.json)

...
```

Replace `<org>/<repo>` with your GitHub organization and repository name.

---

## Usage

### Automatic Execution

The workflow runs automatically on:
- Every commit to `main` or `develop`
- Every pull request
- Manual trigger via Actions tab

### Manual Trigger

**GitHub Actions Tab:**
1. Click "CI MoSCoW Gate v1.0"
2. Click "Run workflow"
3. Select branch
4. Click "Run workflow" button

### Local Testing (Before Push)

```bash
# Generate scorecard locally
python 12_tooling/cli/sot_validator.py \
  --scorecard \
  --input 16_codex/contracts/sot/sot_contract.yaml \
  --export \
  --verbose

# Check if score meets threshold
SCORE=$(python -c "import json; print(json.load(open('scorecard_*.json'))['moscow_scorecard']['moscow_score'])")
echo "Score: $SCORE%"

if (( $(echo "$SCORE < 75.0" | bc -l) )); then
  echo "❌ Score below threshold"
else
  echo "✅ Score above threshold"
fi
```

---

## Interpreting Results

### Success Scenario

**CI Output:**
```
======================================================================
MoSCoW Priority Scorecard (v3.2.0)
======================================================================

[+] MUST:   48/48 PASS
[!] SHOULD: 14/15 PASS  (1 WARNINGS)
[i] HAVE:   6/6 RECORDED

MoSCoW Score: 79.9%
Overall Status: PASS

[+] All MUST rules passed - CI ready
======================================================================

===================================================
MoSCoW Gate Evaluation
===================================================
Score:             79.9%
Minimum Required:  75.0%
MUST Failures:     0
===================================================
✅ PASS: MoSCoW Gate validation successful
```

**Result:** ✅ CI passes, merge allowed

### Failure Scenario 1: Score Below Threshold

**CI Output:**
```
MoSCoW Score: 72.3%

===================================================
MoSCoW Gate Evaluation
===================================================
Score:             72.3%
Minimum Required:  75.0%
MUST Failures:     0
===================================================
❌ FAIL: Score 72.3% is below minimum 75.0%
```

**Exit Code:** 1
**Result:** ❌ CI fails, merge blocked
**Action:** Improve SHOULD rule compliance to raise score

### Failure Scenario 2: MUST Rule Violations

**CI Output:**
```
[X] MUST:   47/48 PASS  (1 FAILED - CI BLOCKING)
MoSCoW Score: 79.9%

===================================================
MoSCoW Gate Evaluation
===================================================
Score:             79.9%
Minimum Required:  75.0%
MUST Failures:     1
===================================================
❌ FAIL: 1 critical MUST rule failures detected
```

**Exit Code:** 24 (ROOT-24-LOCK)
**Result:** ❌ CI fails, merge blocked
**Action:** Fix critical MUST rule violation immediately

### Pull Request Comment

For pull requests, the full scorecard Markdown is automatically posted as a comment:

```markdown
## 🎯 MoSCoW Priority Scorecard

**Version:** 3.2.0
**Timestamp:** 2025-10-17T15:25:36Z
**Overall Status:** PASS
**MoSCoW Score:** 79.9%

## Priority Breakdown

| Priority | Passed | Total | Status |
|----------|--------|-------|--------|
| ✅ MUST   | 48 | 48 | 0 failed (CI blocking) |
| ⚠️ SHOULD | 14 | 15 | 1 warnings |
| ℹ️ HAVE   | 6 | 6 | Informational only |

...
```

---

## Artifact Management

### CI Artifacts (90-day retention)

**Location:** GitHub Actions → Artifacts

**Contents:**
- `scorecard_<timestamp>.json`
- `scorecard_<timestamp>.md`

**Access:**
1. Go to Actions tab
2. Click on workflow run
3. Scroll to "Artifacts" section
4. Download `moscow-scorecard-<sha>`

### Registry Storage (Permanent)

**Location:** `02_audit_logging/registry/scorecards/<branch>/`

**Committed to Repository:** Yes (auto-commit on main branch)

**Access:**
```bash
# List all scorecards in main branch
ls -lh 02_audit_logging/registry/scorecards/main/

# View latest scorecard
cat $(ls -t 02_audit_logging/registry/scorecards/main/scorecard_*.md | head -n 1)
```

---

## Trend Reporting

### Automatic Trend Report

**Generated:** On every `main` branch commit
**Location:** `02_audit_logging/reports/moscow_trend_report.md`

**Contents:**
- Executive summary with current score
- Score progression table (last 20 commits)
- Statistical analysis (avg, min, max, trend)
- Regression detection
- Compliance KPIs
- Recommendations

### Manual Trend Analysis

```bash
# Generate trend report for main branch
python 12_tooling/scripts/analyze_scorecard_trends.py \
  --registry 02_audit_logging/registry/scorecards/main \
  --output custom_trend_report.md

# Generate trend report for develop branch
python 12_tooling/scripts/analyze_scorecard_trends.py \
  --registry 02_audit_logging/registry/scorecards/develop \
  --output develop_trend_report.md
```

### Interpreting Trends

**Trend Indicators:**
- `improving` - Score increasing over time (slope > 0.5)
- `stable` - Score relatively constant (slope ± 0.5)
- `declining` - Score decreasing over time (slope < -0.5)

**Regression Detection:**
- Flags any score drop > 2% between consecutive commits
- Lists all regressions with commit SHAs and dates

**Example Output:**
```markdown
### Current Status

- **Current Score:** 81.3%
- **Average Score:** 78.5%
- **Score Trend:** IMPROVING
- **MUST Pass Rate:** 100.0%
- **SHOULD Pass Rate:** 93.3%
```

---

## Troubleshooting

### Issue 1: Workflow Fails with "File not found"

**Symptom:**
```
Error: Input file not found: 16_codex/contracts/sot/sot_contract.yaml
```

**Solution:**
- Verify CONFIG_FILE path in workflow YAML
- Ensure file exists in repository
- Check file path is relative to repository root

### Issue 2: Score Below Threshold (Unexpected)

**Symptom:**
```
❌ FAIL: Score 68.2% is below minimum 75.0%
```

**Solution:**
1. Run locally with `--verbose` to see detailed failures
2. Check SHOULD rule violations (they contribute 50% weight)
3. Review recent changes that may have introduced violations
4. Fix violations or temporarily lower threshold if justified

### Issue 3: Exit Code 24 with No Obvious MUST Failures

**Symptom:**
```
❌ FAIL: 1 critical MUST rule failures detected
```
But terminal output shows all passing.

**Solution:**
- Download JSON artifact and search for `"enforcement_status": "FAIL"`
- Check for data type mismatches (e.g., expected string, got dict)
- Verify input YAML structure matches contract schema

### Issue 4: Trend Report Not Generated

**Symptom:**
Trend report file not updated after main branch push.

**Solution:**
- Check workflow logs for errors in "Generate Trend Report" step
- Ensure `analyze_scorecard_trends.py` script is executable
- Verify registry directory exists and contains scorecards
- Check if commit step succeeded (may fail if nothing changed)

### Issue 5: Badge Not Updating

**Symptom:**
Badge shows old score or "invalid" message.

**Solution:**
- Ensure badge JSON file exists: `02_audit_logging/reports/moscow_badge.json`
- Check badge URL uses correct GitHub raw URL
- Verify badge generation step succeeded in workflow
- Clear browser cache (badges are cached by shields.io)

---

## Advanced Configuration

### Custom Scoring Formula

To change the scoring formula, edit `03_core/validators/sot/sot_validator_core.py`:

```python
def evaluate_priorities(validation_results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    # Current formula:
    # moscow_score = (pass_must + 0.5 * pass_should + 0.1 * pass_have) / total * 100

    # Example: Equal weighting
    # moscow_score = (pass_must + pass_should + pass_have) / total * 100

    # Example: MUST-only
    # moscow_score = (pass_must / must_total) * 100
```

**Note:** Changing formula requires updating documentation and tests.

### Per-Branch Thresholds

Currently not supported. To implement:

1. Add branch detection in workflow
2. Set MIN_SCORE conditionally based on branch
3. Example:
   ```yaml
   - name: Set Threshold
     run: |
       if [ "${{ github.ref }}" == "refs/heads/main" ]; then
         echo "MIN_SCORE=90.0" >> $GITHUB_ENV
       else
         echo "MIN_SCORE=75.0" >> $GITHUB_ENV
       fi
   ```

### Multiple Config Files

To validate multiple config files:

1. Duplicate the "Generate MoSCoW Scorecard" step
2. Change `--input` path for each file
3. Aggregate results or require all to pass

### Slack/Email Notifications

Add notification step to workflow:

```yaml
- name: Send Slack Notification
  if: failure()
  uses: slackapi/slack-github-action@v1.24.0
  with:
    payload: |
      {
        "text": "MoSCoW Gate failed: ${{ steps.extract_score.outputs.score }}%"
      }
  env:
    SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
```

---

## Performance Considerations

### Workflow Runtime

**Typical Duration:** 2-3 minutes

**Breakdown:**
- Checkout: ~10s
- Python setup: ~30s
- Scorecard generation: ~10s
- Registry archival: ~5s
- Artifact upload: ~10s
- Trend analysis: ~5s (only on main)
- Total: ~70s + overhead

### Repository Size Impact

**Per Scorecard:**
- JSON: ~20KB
- Markdown: ~10KB
- Total: ~30KB per commit

**Annual Growth (1 commit/day):**
- 365 commits × 30KB = ~10.95MB/year (main branch)

**Mitigation:**
- Retention policies remove old branch scorecards
- Consider LFS for large-scale projects

### CI Resource Usage

**GitHub Actions Minutes:**
- ~3 minutes per workflow run
- Free tier: 2,000 minutes/month
- With 100 commits/month: ~300 minutes used (15% of quota)

---

## Security Considerations

### Permissions

**Workflow requires:**
- `contents: write` - To commit registry updates (main branch only)
- `pull-requests: write` - To comment on PRs

**Already configured** in workflow YAML.

### Secrets

**No secrets required** for basic functionality.

**Optional secrets:**
- `SLACK_WEBHOOK` - For Slack notifications
- `GITHUB_TOKEN` - Automatically provided by Actions

### Branch Protection

**Recommended settings:**
1. Require status checks (moscow-validation)
2. Require branches to be up to date
3. Restrict push access to main
4. Require pull request reviews

### Data Sensitivity

**Scorecards contain:**
- Rule IDs (non-sensitive)
- Pass/fail status (non-sensitive)
- Commit SHAs (non-sensitive)
- Timestamps (non-sensitive)

**No PII or sensitive data** is included in scorecards.

---

## Maintenance

### Regular Tasks

**Monthly:**
- Review trend report for anomalies
- Check badge is updating correctly
- Verify registry size is manageable

**Quarterly:**
- Review MIN_SCORE threshold appropriateness
- Audit RULE_PRIORITIES for classification accuracy
- Clean up old feature branch scorecards

**Annually:**
- Archive old scorecards to separate repository or storage
- Update workflow dependencies (actions versions)

### Upgrading

**To upgrade MoSCoW model (e.g., v3.2.0 → v3.3.0):**

1. Update `03_core/validators/sot/sot_validator_core.py`
2. Update `16_codex/contracts/sot/sot_contract.yaml`
3. Update `23_compliance/policies/sot/sot_policy.rego`
4. Update tests in `11_test_simulation/tests_compliance/test_sot_validator.py`
5. Workflow automatically uses updated validator

**No workflow changes needed** unless CLI interface changes.

---

## Integration with Other Systems

### Grafana Dashboard

Ingest JSON scorecards into time-series database:

```python
import json
from datetime import datetime
from influxdb import InfluxDBClient

client = InfluxDBClient(host='localhost', port=8086, database='ssid_metrics')

with open('scorecard.json') as f:
    data = json.load(f)
    scorecard = data['moscow_scorecard']

    point = {
        "measurement": "moscow_score",
        "time": data['timestamp'],
        "fields": {
            "score": scorecard['moscow_score'],
            "must_passed": scorecard['must_rules']['passed'],
            "must_total": scorecard['must_rules']['total'],
            "should_passed": scorecard['should_rules']['passed'],
            "should_total": scorecard['should_rules']['total']
        }
    }

    client.write_points([point])
```

### JIRA Integration

Create tickets for SHOULD violations:

```python
from jira import JIRA

jira = JIRA(server='https://jira.example.com', basic_auth=('user', 'token'))

# Parse scorecard
should_warnings = scorecard['should_rules']['warnings']

if should_warnings > 0:
    issue = jira.create_issue(
        project='SSID',
        summary=f'{should_warnings} MoSCoW SHOULD Rule Violations',
        description=f'See scorecard for details: {scorecard_url}',
        issuetype={'name': 'Technical Debt'}
    )
```

### Slack Dashboard

Post weekly summary to Slack channel:

```bash
# In workflow or cron job
python 12_tooling/scripts/slack_moscow_summary.py \
  --registry 02_audit_logging/registry/scorecards/main \
  --webhook $SLACK_WEBHOOK_URL \
  --period 7d
```

---

## FAQ

**Q: Can I run the gate only on pull requests, not pushes?**
A: Yes, change workflow trigger:
```yaml
on:
  pull_request:
    branches: [ main, develop ]
```

**Q: Can I exclude certain branches from validation?**
A: Yes, add branch filter:
```yaml
on:
  push:
    branches:
      - main
      - develop
      - '!experimental-*'
```

**Q: What happens if the workflow fails?**
A: Merge is blocked if branch protection is enabled. Developer must fix violations and re-push.

**Q: Can I temporarily bypass the gate for hotfixes?**
A: Not recommended. Instead:
1. Lower MIN_SCORE temporarily in workflow
2. Merge hotfix
3. Create follow-up PR to fix violations
4. Restore MIN_SCORE

**Q: How do I access scorecard for a specific commit?**
A:
```bash
# Find scorecard by commit SHA
find 02_audit_logging/registry/scorecards -name "*_abc123.json"
```

**Q: Can I run validation on non-YAML files (e.g., JSON)?**
A: Yes, CLI supports JSON input:
```yaml
--input config.json
```

---

## Conclusion

The **CI MoSCoW Gate v1.0** provides automated, deterministic enforcement of SoT compliance with:
- Graduated priority model (MUST/SHOULD/HAVE)
- CI/CD integration with blocking capabilities
- Comprehensive artifact and trend management
- Extensible architecture for future enhancements

**Status:** ✅ PRODUCTION READY - Ready for immediate deployment

---

**Document Version:** 1.0.0
**Last Updated:** 2025-10-17
**Next Review:** 2025-11-17

---

*This guide is part of the SSID Project ROOT-24-LOCK compliance framework.*
