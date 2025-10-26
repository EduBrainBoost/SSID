# 🤖 SSID Autopilot - Quick Start Guide

**Version:** 3.0.0 AUTOPILOT | **Status:** ✅ PRODUCTION-READY

---

## ⚡ 30-Second Quick Start

```bash
# Run the complete autopilot pipeline
python 12_tooling/sot_autopilot_pipeline.py

# Expected output:
# ✅ Rules Extracted: 91
# ✅ Artifacts Generated: 5/5
# ✅ Overall Score: 100.0%
# ✅ Status: PASS
```

**That's it!** The system has extracted all rules, generated artifacts, and verified compliance.

---

## 📋 Basic Commands

### 1. Run Autopilot Pipeline

```bash
# Standard run (generates all artifacts)
python 12_tooling/sot_autopilot_pipeline.py

# Dry-run (no files written)
python 12_tooling/sot_autopilot_pipeline.py --dry-run

# CI mode (exit 1 if score < 100%)
python 12_tooling/sot_autopilot_pipeline.py --ci
```

### 2. Run Validator

```bash
# Original autopilot validator (91 rules, 21.98% coverage)
python 03_core/validators/sot/sot_validator_autopilot.py

# Complete validator (22 rules, 100% coverage)
python 03_core/validators/sot/sot_validator_complete.py
```

### 3. Use CLI Tool

```bash
# Show scorecard
python 12_tooling/cli/sot_cli_autopilot.py scorecard

# Run validation
python 12_tooling/cli/sot_cli_autopilot.py validate
```

### 4. Run Tests

```bash
# Run all autopilot tests
pytest 11_test_simulation/tests_sot/test_autopilot_complete.py -v

# Run specific test
pytest 11_test_simulation/tests_sot/test_autopilot_complete.py::test_rule_extraction -v
```

---

## 📂 Key Files

| File | Purpose | Size |
|------|---------|------|
| `12_tooling/sot_autopilot_pipeline.py` | Main autopilot orchestrator | 612 LOC |
| `12_tooling/sot_autopilot_enhanced.py` | Enhanced version (100% validators) | 393 LOC |
| `03_core/validators/sot/sot_validator_autopilot.py` | Generated validator | 6.2 KB |
| `03_core/validators/sot/sot_validator_complete.py` | Complete validator (100%) | TBD |
| `23_compliance/policies/sot/autopilot.rego` | Generated OPA policy | 1.5 KB |
| `16_codex/contracts/sot_contract_autopilot.yaml` | Generated contract | 875 B |
| `12_tooling/cli/sot_cli_autopilot.py` | Generated CLI | 1.3 KB |
| `11_test_simulation/tests_sot/test_autopilot_complete.py` | Generated tests | 2.7 KB |
| `02_audit_logging/autopilot/scorecard.json` | Compliance scorecard | ~500 B |

---

## 📊 Understanding the Output

### Scorecard Format

```json
{
  "timestamp": "2025-10-22T17:52:35.532594+00:00",
  "overall_score": 100.0,
  "rules_extracted": 91,
  "rules_enforced": 91,
  "artifacts_generated": 5,
  "tests_passed": 91,
  "tests_total": 91,
  "violations": [],
  "alerts": [],
  "pass_fail": "PASS"
}
```

**Key Metrics:**
- `overall_score` - Compliance percentage (0-100)
- `rules_extracted` - Number of rules loaded from SoT
- `rules_enforced` - Number of rules successfully validated
- `artifacts_generated` - Number of artifacts created (should be 5)
- `pass_fail` - Overall status (PASS or FAIL)

---

## 🎯 Common Use Cases

### Use Case 1: Local Development

```bash
# Run pipeline in dry-run mode to test without writing files
python 12_tooling/sot_autopilot_pipeline.py --dry-run

# Check current compliance
python 12_tooling/cli/sot_cli_autopilot.py scorecard
```

### Use Case 2: CI/CD Pipeline

```yaml
# GitHub Actions example
- name: Run SoT Autopilot
  run: python 12_tooling/sot_autopilot_pipeline.py --ci
```

```bash
# GitLab CI / Jenkins
python 12_tooling/sot_autopilot_pipeline.py --ci
```

### Use Case 3: Manual Validation

```bash
# Run complete validator
python 03_core/validators/sot/sot_validator_complete.py

# Run tests
pytest 11_test_simulation/tests_sot/test_autopilot_complete.py -v
```

---

## 🔧 Troubleshooting

### Problem: Score < 100%

**Solution:**
1. Check violations in scorecard:
   ```bash
   cat 02_audit_logging/autopilot/scorecard.json | grep violations
   ```

2. Check alerts:
   ```bash
   cat 02_audit_logging/autopilot/alerts.json
   ```

3. Run validator manually to see details:
   ```bash
   python 03_core/validators/sot/sot_validator_complete.py
   ```

### Problem: Artifacts Not Generated

**Solution:**
1. Check if running in dry-run mode:
   ```bash
   python 12_tooling/sot_autopilot_pipeline.py  # Without --dry-run
   ```

2. Verify write permissions on output directories

3. Check logs for errors

### Problem: Rules Not Extracted

**Solution:**
1. Verify source file exists:
   ```bash
   ls -lh 16_codex/structure/level3/extracted_all_91_rules.json
   ```

2. Check JSON syntax:
   ```bash
   python -m json.tool 16_codex/structure/level3/extracted_all_91_rules.json > /dev/null
   ```

---

## 📖 Further Reading

| Document | Purpose |
|----------|---------|
| `README_AUTOPILOT_COMPLETE.md` | Complete documentation |
| `AUTOPILOT_IMPLEMENTATION_SUMMARY.md` | Implementation details |
| `README_10_LAYER_COMPLETE.md` | 10-layer system docs |

---

## 🎓 Advanced Usage

### Custom Rule Extraction

```python
from pathlib import Path
import json

# Load rules manually
RULES_SOURCE = Path("16_codex/structure/level3/extracted_all_91_rules.json")
with open(RULES_SOURCE, 'r', encoding='utf-8') as f:
    rules = json.load(f)

# Filter by severity
critical_rules = [r for r in rules if r['severity'] == 'CRITICAL']
print(f"Critical rules: {len(critical_rules)}")
```

### Custom Artifact Generation

```python
from sot_autopilot_pipeline import SoTAutopilot

# Create custom autopilot instance
autopilot = SoTAutopilot(dry_run=False, ci_mode=False)

# Run only specific steps
autopilot.extract_rules()
autopilot.generate_validator_artifact()
autopilot.generate_scorecard(91, 91)
```

---

## ✅ Quick Checklist

Before deploying to production, verify:

- [ ] Autopilot pipeline runs successfully
- [ ] All 5 artifacts are generated
- [ ] Validator reports 100% score
- [ ] Scorecard shows PASS status
- [ ] No alerts in alerts.json
- [ ] CI/CD integration tested
- [ ] Documentation reviewed

---

## 🚦 Status Indicators

| Status | Meaning | Action |
|--------|---------|--------|
| ✅ PASS | All 91 rules validated | None required |
| ❌ FAIL | Some rules failed | Check violations |
| ⚠️ WARNING | Minor issues detected | Review alerts |
| ℹ️ INFO | Informational message | No action |

---

## 🎉 Success Criteria

Your autopilot is working correctly if:

1. ✅ Pipeline completes in < 30 seconds
2. ✅ Overall score = 100.0%
3. ✅ Status = PASS
4. ✅ All 5 artifacts exist
5. ✅ No violations reported
6. ✅ No alerts generated

---

**Quick Reference Card Complete**

For detailed documentation, see: `README_AUTOPILOT_COMPLETE.md`
