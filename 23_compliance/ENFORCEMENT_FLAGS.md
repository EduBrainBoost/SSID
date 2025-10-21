# SSID Enforcement Flags - Quick Reference

**Purpose:** These flags should be included in all future prompts when working with the SSID project to ensure structural compliance.

---

## 🚩 Required Enforcement Flags

When creating prompts or instructions for AI assistants working on SSID, **ALWAYS** include these flags:

```yaml
root_24_lock: true
enforce_structure_guard: true
```

---

## 📋 What These Flags Mean

### `root_24_lock: true`

**Enforces:**
- Only 24 authorized root modules (01_ai_layer through 24_meta_orchestration)
- Authorized exceptions only (LICENSE, README.md, .gitignore, .gitattributes, .pre-commit-config.yaml, .git, .github)
- No unauthorized root files or directories
- All files must be placed in appropriate modules

**Assistant Behavior:**
- Never create files at root level (except authorized exceptions)
- Always place files in appropriate Root-24 modules
- Recommend migration for misplaced files
- Run audit after structural changes

---

### `enforce_structure_guard: true`

**Enforces:**
- CI/CD validation on every push/PR
- Forensic audit with SHA-256 verification
- OPA policy runtime enforcement
- Automatic violation detection

**Assistant Behavior:**
- Verify CI/CD workflow exists and is active
- Update SHA-256 checksums after file changes
- Run structure audit before completing tasks
- Document all structural changes

---

## 🛠️ Example Prompt Usage

### ❌ Bad (No Flags)
```
"Create a new deployment guide for v9.0"
```
**Risk:** File might be created at root level, violating Root-24-LOCK

### ✅ Good (With Flags)
```yaml
root_24_lock: true
enforce_structure_guard: true
---
"Create a new deployment guide for v9.0"
```
**Result:** File correctly placed at `05_documentation/deployment/DEPLOYMENT_v9.0.md`

---

## 📁 Correct File Placement Guide

When `root_24_lock: true`, follow these placement rules:

| File Type | Correct Location | Example |
|-----------|------------------|---------|
| Deployment docs | `05_documentation/deployment/` | DEPLOYMENT_v9.0.md |
| Transition docs | `05_documentation/transitions/` | TRANSITION_v8_to_v9.md |
| Compliance reports | `23_compliance/reports/` | activation_audit.md |
| Audit reports | `02_audit_logging/reports/` | forensic_audit.md |
| Test configs | `11_test_simulation/config/` | pytest.ini |
| CI/CD workflows | `.github/workflows/` | ci_test.yml |
| OPA policies | `23_compliance/policies/` | guard.rego |
| Python tools | `12_tooling/` | validator.py |
| Test scripts | `11_test_simulation/scenarios/` | test_*.py |

---

## 🔍 Verification Commands

When `enforce_structure_guard: true`, run these after changes:

### Standard Audit
```bash
python 12_tooling/root_structure_audit.py
```

### Forensic Audit (with SHA-256)
```bash
python 12_tooling/root_forensic_audit.py
```

### Auto-Fix (if violations detected)
```bash
python 11_test_simulation/tools/root_structure_auto_fix.py
```

---

## 🚨 CI/CD Enforcement

With `enforce_structure_guard: true`, CI/CD will:

✅ **PASS if:**
- All 24 root modules present
- No unauthorized root items
- SHA-256 hashes match baseline
- No prohibited patterns (.pytest_cache, __pycache__, etc.)

❌ **FAIL if:**
- Unauthorized root files/directories
- Missing root modules
- Hash mismatches (file tampering)
- Prohibited patterns detected

**Workflow:** `.github/workflows/ci_structure_guard.yml` v2.0.0

---

## 📊 Current Compliance Status

**Root-24-LOCK:** ✅ 96/100 (Operational)
- 24/24 modules present ✅
- 6 authorized exceptions ✅
- 1 violation (.claude, mitigated via .gitignore) ⚠️

**v8.0 Continuum:** ✅ 100/100 CERTIFIED
- 13/13 components validated
- 61 tests passing (100% coverage)
- Dormant mode verified (cost=$0)

**CI/CD Guard:** ✅ Active (v2.0.0)

---

## 📚 Reference Documents

- **Policy:** `23_compliance/policies/root_24_forensic_integrity_policy.yaml`
- **SoT:** `05_documentation/ssid_master_definition_corrected_v1.1.1.md`
- **Compliance Summary:** `02_audit_logging/reports/ROOT_24_LOCK_FINAL_COMPLIANCE_SUMMARY.md`
- **CI/CD Workflow:** `.github/workflows/ci_structure_guard.yml`

---

## 🎯 Quick Checklist

Before submitting code/docs, verify:

- [ ] `root_24_lock: true` flag used in prompt
- [ ] `enforce_structure_guard: true` flag used in prompt
- [ ] No files created at root level (except authorized)
- [ ] All files in appropriate Root-24 modules
- [ ] Structure audit run and passed
- [ ] SHA-256 checksums updated (if applicable)
- [ ] CI/CD will pass (no violations)

---

## ⚙️ Integration Examples

### Python Script Template
```python
"""
SSID Module: [Module Name]
Location: [Root Module]/{subpath}
Compliance: root_24_lock=true, enforce_structure_guard=true
"""
```

### Markdown Document Template
```markdown
# [Document Title]

**Location:** `[Root Module]/[subpath]/[filename].md`
**Compliance:** root_24_lock=true, enforce_structure_guard=true
```

### CI/CD Workflow Template
```yaml
name: [Workflow Name]
# Compliance: root_24_lock=true, enforce_structure_guard=true

on:
  push:
    branches: ["main", "develop"]
  pull_request:
    branches: ["main"]

jobs:
  # ... workflow jobs
```

---

## 🔒 Enforcement Philosophy

**Root-24-LOCK is non-negotiable.**

The SSID project maintains strict structural discipline:
- **24 root modules** - no more, no less
- **Authorized exceptions only** - documented and justified
- **No root files** - everything belongs in a module
- **Forensic validation** - SHA-256 integrity checks
- **Automated enforcement** - CI/CD blocks violations

**Why:**
- Predictable structure for automation
- Clear ownership and organization
- Easier navigation and maintenance
- Prevents structural drift
- Enforces architectural discipline

---

**Last Updated:** 2025-10-12
**Policy Version:** Root-24-LOCK v1.0
**Framework:** SSID Master Definition v1.1.1

---

**END OF ENFORCEMENT FLAGS REFERENCE**
