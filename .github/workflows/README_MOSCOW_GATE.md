# CI MoSCoW Gate v1.0 - Quick Start

> **Status:** ✅ PRODUCTION READY
> **Version:** 1.0.0
> **Date:** 2025-10-17

---

## 🎯 What is CI MoSCoW Gate?

Automated GitHub Actions workflow that validates **MoSCoW Priority** compliance on every commit:

- **MUST Rules (48)** → Hard fail, blocks CI (exit 24)
- **SHOULD Rules (15)** → Warnings only
- **HAVE Rules (6)** → Informational logging

**Score Formula:** `(pass_must + 0.5×pass_should + 0.1×pass_have) / total × 100`

---

## ⚡ Quick Start (5 Minutes)

### 1. Workflow is Already Enabled

The workflow at `.github/workflows/ci_moscow_gate.yml` runs automatically on:
- ✅ Push to `main` or `develop`
- ✅ Pull requests
- ✅ Manual trigger

**No setup required!**

### 2. Set Branch Protection (Recommended)

**GitHub Settings → Branches → `main` branch:**
1. ✅ Require status checks: `moscow-validation`
2. ✅ Require branches to be up to date

This **blocks merge** if scorecard fails.

### 3. Add Badge to README (Optional)

```markdown
![MoSCoW Score](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/<org>/<repo>/main/02_audit_logging/reports/moscow_badge.json)
```

Replace `<org>/<repo>` with your GitHub org/repo.

---

## 📊 What You Get

### 1. Automated Scorecard in CI

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
```

### 2. Artifacts (90-day retention)

- `scorecard_<timestamp>.json` - Machine-readable
- `scorecard_<timestamp>.md` - Human-readable report

### 3. Registry Storage (Permanent)

**Location:** `02_audit_logging/registry/scorecards/<branch>/`

**Format:** `scorecard_20251017T152536Z_a6e6d2a.json`

### 4. Trend Report (Main Branch)

**Auto-generated on every main commit:**
- `02_audit_logging/reports/moscow_trend_report.md`
- Score progression
- Regression detection
- Compliance KPIs

### 5. Dynamic Badge

**Auto-updated badge JSON:**
- `02_audit_logging/reports/moscow_badge.json`
- Color: Green (≥75%), Yellow (60-74%), Red (<60%)

---

## 🔧 Configuration

### Change Minimum Score Threshold

**File:** `.github/workflows/ci_moscow_gate.yml`

```yaml
env:
  MIN_SCORE: 75.0  # Default: 75% (change to 60-100)
```

**Recommendations:**
- **90.0** - Strict (all MUST + most SHOULD)
- **75.0** - Standard (all MUST + some SHOULD) ← Default
- **60.0** - Lenient (all MUST minimum)

---

## 🚦 Exit Codes

| Code | Meaning | Action |
|------|---------|--------|
| 0 | All checks passed | ✅ Merge allowed |
| 1 | Score below threshold | ❌ Fix SHOULD rules |
| 24 | MUST rule violations | ❌ Fix critical violations |

**Exit 24 = ROOT-24-LOCK** (Critical SoT breach)

---

## 🧪 Test Locally Before Push

```bash
# Generate scorecard
cd 12_tooling/cli
python sot_validator.py \
  --scorecard \
  --input ../../16_codex/contracts/sot/sot_contract.yaml \
  --export

# Check score
python -c "import json; print(f\"Score: {json.load(open('scorecard_*.json'))['moscow_scorecard']['moscow_score']:.1f}%\")"
```

**If score ≥ 75% and no MUST failures → Push will succeed!**

---

## 📈 View Trend Report

```bash
# Generate trend report for main branch
python 12_tooling/scripts/analyze_scorecard_trends.py \
  --registry 02_audit_logging/registry/scorecards/main \
  --output trend_report.md
```

**Auto-generated on main branch commits.**

---

## 🔍 What Happens in CI

1. **Generate Scorecard** - Run MoSCoW validation
2. **Extract Score** - Parse JSON for score & MUST failures
3. **Archive to Registry** - Store in `02_audit_logging/registry/scorecards/`
4. **Upload Artifacts** - 90-day retention in GitHub Actions
5. **Comment on PR** - Post full scorecard to pull request
6. **Evaluate Threshold**:
   - Score < 75%? → EXIT 1
   - MUST failures? → EXIT 24
7. **Generate Trend** - Create historical analysis (main only)
8. **Generate Badge** - Update dynamic badge (main only)

---

## 🆘 Troubleshooting

### CI Fails with "Score below threshold"

```bash
❌ FAIL: Score 72.3% is below minimum 75.0%
```

**Solution:**
1. Run locally with `--verbose` to see failures
2. Fix SHOULD rule violations (they count 50% weight)
3. Or temporarily lower MIN_SCORE if justified

### CI Fails with "MUST rule failures"

```bash
❌ FAIL: 1 critical MUST rule failures detected
```

**Solution:**
1. Download artifact to see which MUST rule failed
2. Fix the critical violation immediately
3. MUST failures always block merge (by design)

### Badge Not Updating

**Solution:**
- Verify `02_audit_logging/reports/moscow_badge.json` exists
- Check badge URL uses correct GitHub raw URL
- Clear browser cache (shields.io caches badges)

---

## 📚 Documentation

**Full Integration Guide:**
`02_audit_logging/reports/CI_MOSCOW_GATE_V1.0_INTEGRATION.md`

**Scorecard Registry Guide:**
`02_audit_logging/registry/scorecards/README.md`

**MoSCoW Enforcement Report:**
`02_audit_logging/reports/SOT_MOSCOW_ENFORCEMENT_V3.2.0.md`

---

## 🎓 Key Concepts

### MoSCoW Priority Model

| Priority | Rules | CI Impact | Weight |
|----------|-------|-----------|--------|
| MUST | 48 | ❌ Blocks | 100% |
| SHOULD | 15 | ⚠️ Warns | 50% |
| HAVE | 6 | ℹ️ Logs | 10% |

### Score Interpretation

- **90-100%** - Grade A+ (Excellent)
- **75-89%** - Grade A (Good) ← Threshold
- **60-74%** - Grade B (Fair)
- **<60%** - Grade C/F (Poor)

**Note:** Any MUST failure = CI blocked (regardless of score)

---

## 🚀 Advanced Usage

### Manual Workflow Trigger

**GitHub Actions Tab:**
1. Select "CI MoSCoW Gate v1.0"
2. Click "Run workflow"
3. Choose branch
4. Run

### Compare Scorecards

```bash
# Find two scorecards
OLD=$(ls 02_audit_logging/registry/scorecards/main/scorecard_*.json | head -n 1)
NEW=$(ls 02_audit_logging/registry/scorecards/main/scorecard_*.json | tail -n 1)

# Compare scores
python -c "import json; old=json.load(open('$OLD')); new=json.load(open('$NEW')); print(f\"Score change: {old['moscow_scorecard']['moscow_score']:.1f}% → {new['moscow_scorecard']['moscow_score']:.1f}%\")"
```

### Query Registry

```bash
# Latest scorecard in main
ls -t 02_audit_logging/registry/scorecards/main/scorecard_*.json | head -n 1

# Count scorecards
ls 02_audit_logging/registry/scorecards/main/*.json | wc -l

# Find scorecard by commit
find 02_audit_logging/registry/scorecards -name "*_a6e6d2a.json"
```

---

## 🎯 Success Criteria

✅ **CI MoSCoW Gate is Working When:**
1. Workflow runs on every push to main/develop
2. Pull requests get scorecard comments
3. Merge is blocked when MUST failures or score < 75%
4. Registry accumulates scorecards over time
5. Trend report updates on main branch
6. Badge shows current score

---

## 🔗 Related Components

- **Python Validator:** `03_core/validators/sot/sot_validator_core.py`
- **CLI Tool:** `12_tooling/cli/sot_validator.py`
- **Rego Policy:** `23_compliance/policies/sot/sot_policy.rego`
- **Contract:** `16_codex/contracts/sot/sot_contract.yaml`
- **Tests:** `11_test_simulation/tests_compliance/test_sot_validator.py`

---

## 📊 Metrics

**Workflow Performance:**
- Runtime: ~2-3 minutes
- Storage/commit: ~30KB
- GitHub Actions usage: ~3 minutes/run

**Retention:**
- CI Artifacts: 90 days
- Registry (main): Permanent
- Registry (develop): 180 days
- Registry (feature): 30 days

---

## ✅ Checklist

Before enabling in production:

- [ ] Workflow file committed to `.github/workflows/`
- [ ] Branch protection enabled with status check
- [ ] MIN_SCORE threshold configured
- [ ] Badge added to README (optional)
- [ ] Team notified of new CI gate
- [ ] Documentation reviewed

---

**Need Help?** See full integration guide: `02_audit_logging/reports/CI_MOSCOW_GATE_V1.0_INTEGRATION.md`

**Version:** 1.0.0 | **Status:** ✅ PRODUCTION READY | **Date:** 2025-10-17
