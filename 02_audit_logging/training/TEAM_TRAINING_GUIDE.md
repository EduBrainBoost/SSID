# QA Master Suite - Team Training Guide

**Version:** 1.0.0
**Datum:** 2025-10-18
**Owner:** SSID Compliance Team
**Target Audience:** All developers, QA engineers, DevOps
**Duration:** 90 minutes (2-hour session with Q&A)

---

## Training Overview

### Objectives

By the end of this training, participants will:

1. ✅ Understand the DUAL-LAYER QA Architecture
2. ✅ Know where to place test files
3. ✅ Understand policy enforcement mechanisms
4. ✅ Be able to resolve policy violations
5. ✅ Know how to use WORM storage and blockchain anchoring
6. ✅ Understand quarterly review process

### Prerequisites

- Basic Git knowledge
- Access to SSID repository
- Local development environment set up

---

## Training Agenda

### Module 1: Introduction (10 min)

#### 1.1 Why QA Master Suite?

**Problem we're solving:**
- Test chaos: Tests scattered across 20+ directories
- Compliance gaps: No clear governance/test separation
- Audit challenges: Hard to prove test integrity

**Solution:**
- **DUAL-LAYER Architecture:** Clear separation
- **Automated enforcement:** Pre-commit + OPA + CI/CD
- **Audit trail:** WORM storage + blockchain timestamps

#### 1.2 Key Concepts

**DUAL-LAYER Architecture:**

```
┌─────────────────────────────────────────────────┐
│ Layer 1: ACTIVE QA                              │
│ Location: 11_test_simulation/                   │
│ Purpose: Development, CI/CD, active testing     │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│ Layer 2: QA ARCHIVE                             │
│ Location: 02_audit_logging/archives/qa_master_suite/ │
│ Purpose: Historical tests, regression, 853MB corpus │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│ Layer 3: SoT GOVERNANCE (5 files only)          │
│ Purpose: Compliance rules, NOT tests            │
│ Exempt from QA policy                           │
└─────────────────────────────────────────────────┘
```

---

### Module 2: Policy Rules (15 min)

#### 2.1 The Golden Rules

**✅ ALLOWED:**

```bash
# Active tests
11_test_simulation/tests/test_example.py
11_test_simulation/shards/01_*/tests/

# QA Archive
02_audit_logging/archives/qa_master_suite/qa_master_suite.py
02_audit_logging/archives/qa_master_suite/*.yaml
```

**❌ FORBIDDEN:**

```bash
# Tests outside allowed directories
01_ai_layer/test_something.py          # ❌ VIOLATION
03_core/tests/test_core.py             # ❌ VIOLATION
23_compliance/test_policy.yaml         # ❌ VIOLATION
```

**🔓 EXCEPTIONS (5 SoT Governance Files):**

```bash
16_codex/contracts/sot/sot_contract.yaml
03_core/validators/sot/sot_validator_core.py
23_compliance/policies/sot/sot_policy.rego
12_tooling/cli/sot_validator.py
11_test_simulation/tests_compliance/test_sot_validator.py
```

#### 2.2 File Extensions Covered

Policy applies to:
- `.py` (Python)
- `.yaml`, `.yml` (YAML)
- `.rego` (OPA)
- `.json` (JSON)

---

### Module 3: Enforcement Mechanisms (20 min)

#### 3.1 Pre-Commit Hook

**How it works:**
```bash
git commit -m "Add new test"
↓
Pre-commit hook runs
↓
Checks staged files
↓
If violation → ❌ BLOCKED
If compliant → ✅ ALLOWED
```

**Demo:**

```bash
# Create violation
echo "test" > 01_ai_layer/test_bad.py
git add 01_ai_layer/test_bad.py
git commit -m "test"

# Expected output:
# ❌ QA/SoT DUAL-LAYER POLICY VIOLATION
# The following QA test files are outside the allowed QA corpus:
#   ❌ 01_ai_layer/test_bad.py
# [Commit blocked]

# Fix violation
git reset HEAD 01_ai_layer/test_bad.py
mkdir -p 11_test_simulation/tests
mv 01_ai_layer/test_bad.py 11_test_simulation/tests/test_good.py
git add 11_test_simulation/tests/test_good.py
git commit -m "test: Add test in correct location"

# ✅ All pre-commit checks passed
```

#### 3.2 OPA CI/CD Check

**GitHub Actions workflow:**
- Runs on every PR
- Evaluates all changed files
- Posts comment on PR
- Blocks merge if violations

**Demo:** Show live PR with violation

#### 3.3 Branch Protection

**Enforcement:**
- PR cannot be merged if OPA check fails
- Even admins are blocked
- Forces compliance

---

### Module 4: Hands-On: Fixing Violations (25 min)

#### Exercise 1: Identify Violations

**Task:** Given these files, which violate policy?

```
1. 01_ai_layer/test_model.py
2. 11_test_simulation/test_sim.py
3. 02_audit_logging/archives/qa_master_suite/tests.py
4. 03_core/utils/test_utils.yaml
5. 16_codex/contracts/sot/sot_contract.yaml
```

**Answers:**
- ❌ #1 - Violation (outside allowed dirs)
- ✅ #2 - Compliant (in 11_test_simulation/)
- ✅ #3 - Compliant (in qa_master_suite/)
- ❌ #4 - Violation (outside allowed dirs)
- ✅ #5 - Compliant (SoT exemption)

#### Exercise 2: Fix a Violation

**Scenario:** You've added tests in the wrong location.

**Starting state:**
```bash
03_core/nlp/test_nlp.py          # ❌ Violation
03_core/security/test_auth.yaml  # ❌ Violation
```

**Task:** Move to correct location

**Solution:**
```bash
# Option 1: Move to 11_test_simulation
mkdir -p 11_test_simulation/core/nlp
mkdir -p 11_test_simulation/core/security

git mv 03_core/nlp/test_nlp.py 11_test_simulation/core/nlp/
git mv 03_core/security/test_auth.yaml 11_test_simulation/core/security/

git commit -m "fix: Move tests to allowed directory"
```

#### Exercise 3: Dealing with Pre-Commit Block

**Scenario:** Pre-commit hook blocks your commit

**Steps:**
1. Read the error message
2. Identify violating files
3. Move files to allowed directory OR remove from commit
4. Re-commit

**Demo:** Live demonstration

---

### Module 5: WORM Storage & Blockchain (15 min)

#### 5.1 What is WORM Storage?

**Write-Once-Read-Many:**
- Uploaded files cannot be modified or deleted
- Used for audit artifacts, policies, reports
- 7-year retention
- AWS S3 Object Lock

**When to use:**
- Finalizing audit reports
- Archiving policy versions
- Storing evidence for regulators

**Demo:** Show AWS S3 console (if available)

#### 5.2 Blockchain Anchoring

**OpenTimestamps:**
- Free Bitcoin-based timestamping
- Proves file existed at specific time
- Tamper-proof
- Third-party verifiable

**Workflow:**
```bash
# 1. Create timestamp
ots stamp policy.yaml

# 2. Wait for Bitcoin confirmation (~10-60 min)

# 3. Verify
ots verify policy.yaml.ots
# Success! Bitcoin attests data existed as of...
```

**When to use:**
- QA Policy changes
- Audit reports
- Evidence chains
- SHA256 manifests

---

### Module 6: Daily Workflow (10 min)

#### Developer Workflow

```
┌─────────────────────────────────────────┐
│ 1. Write code + tests                   │
│    ↓                                    │
│ 2. Place tests in 11_test_simulation/  │
│    ↓                                    │
│ 3. git add + git commit                 │
│    ↓                                    │
│ 4. Pre-commit hook validates            │
│    ↓                                    │
│ 5. If blocked → Fix location            │
│    ↓                                    │
│ 6. git push                             │
│    ↓                                    │
│ 7. PR created                           │
│    ↓                                    │
│ 8. OPA CI/CD runs                       │
│    ↓                                    │
│ 9. If violations → Fix                  │
│    ↓                                    │
│ 10. PR approved & merged                │
└─────────────────────────────────────────┘
```

#### QA Engineer Workflow

```
┌─────────────────────────────────────────┐
│ 1. Develop tests in 11_test_simulation/│
│ 2. Run tests locally                    │
│ 3. Stabilize tests                      │
│ 4. After X months → Archive to          │
│    qa_master_suite/ (if needed)         │
│ 5. Update SHA256 manifest               │
└─────────────────────────────────────────┘
```

---

### Module 7: Monitoring & Quarterly Reviews (10 min)

#### 7.1 Monitoring Dashboard

**Location:** `02_audit_logging/archives/qa_master_suite/MONITORING.md`

**Metrics tracked:**
- QA Archive size
- Policy violations (30d)
- Test coverage
- WORM storage status
- Blockchain anchoring status

**Auto-updated:** Daily via GitHub Actions

**How to use:**
```bash
# View dashboard
cat 02_audit_logging/archives/qa_master_suite/MONITORING.md

# Manual update
python tools/update_monitoring_dashboard.py
```

#### 7.2 Quarterly Reviews

**Schedule:** Quarterly (Jan, Apr, Jul, Oct)
**Duration:** 2 hours
**Participants:** Compliance, DevOps, QA, Architecture

**Agenda:**
1. Review metrics
2. Policy violations analysis
3. Process improvements
4. Budget & resources
5. Risks & issues
6. Next quarter priorities

**Template:** `02_audit_logging/templates/QUARTERLY_REVIEW_TEMPLATE.md`

---

### Module 8: Q&A & Troubleshooting (15 min)

#### Common Questions

**Q: What if I need to add a test outside allowed directories?**
A: You can't. If you have a special case, discuss with Compliance Team.

**Q: Can I disable the pre-commit hook?**
A: Technically yes (not recommended). But PR will still be blocked by OPA CI/CD.

**Q: What happens to old tests outside allowed dirs?**
A: They stay (grandfathered). New files must comply.

**Q: How do I know if a file is exempt (SoT governance)?**
A: Check the 5-file list in README.md or ask Compliance Team.

**Q: What if pre-commit hook has a bug?**
A: Report to Compliance Team immediately. Emergency bypass procedure exists.

#### Common Issues

**Issue:** Pre-commit hook doesn't run
**Solution:**
```bash
# Reinstall hook
cp .git/hooks/pre-commit.sample .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

**Issue:** False positive violation
**Solution:**
1. Check file extension (only .py, .yaml, .yml, .rego, .json)
2. Check exact path (case-sensitive)
3. If still blocked, contact Compliance Team

**Issue:** Can't push to remote
**Solution:**
- Check branch protection
- Ensure OPA check passed
- Get PR approval

---

### Module 9: Resources & Support (5 min)

#### Documentation

| Document | Location | Purpose |
|----------|----------|---------|
| **Policy README** | `02_audit_logging/archives/qa_master_suite/README.md` | Main policy doc |
| **Next Steps** | `02_audit_logging/archives/qa_master_suite/NEXT_STEPS.md` | Phase 2 roadmap |
| **Monitoring** | `02_audit_logging/archives/qa_master_suite/MONITORING.md` | Metrics dashboard |
| **OPA Policy** | `23_compliance/policies/qa/qa_policy_enforcer.rego` | Enforcement rules |
| **WORM Setup** | `02_audit_logging/procedures/AWS_S3_WORM_SETUP_GUIDE.md` | WORM storage guide |
| **Blockchain** | `02_audit_logging/procedures/OPENTIMESTAMPS_SETUP_GUIDE.md` | Timestamping guide |

#### Support Channels

- **Email:** qa-policy@ssid-project.internal
- **Slack:** #qa-master-suite
- **Issues:** GitHub Issues with label `qa-policy`
- **Meeting:** Bi-weekly Thursday 14:00 UTC
- **Emergency:** compliance-emergency@ssid-project.internal

#### Quick Reference Card

```
╔═══════════════════════════════════════════════════════════╗
║ QA MASTER SUITE - QUICK REFERENCE                         ║
╠═══════════════════════════════════════════════════════════╣
║ WHERE TO PUT TESTS:                                       ║
║   ✅ 11_test_simulation/                                  ║
║   ✅ 02_audit_logging/archives/qa_master_suite/           ║
║                                                           ║
║ ENFORCEMENT:                                              ║
║   🔒 Pre-commit hook                                      ║
║   🔒 OPA CI/CD (GitHub Actions)                           ║
║   🔒 Branch Protection                                    ║
║                                                           ║
║ IF BLOCKED:                                               ║
║   1. Read error message                                   ║
║   2. Move file to allowed directory                       ║
║   3. Commit & push again                                  ║
║                                                           ║
║ HELP:                                                     ║
║   📧 qa-policy@ssid-project.internal                     ║
║   💬 #qa-master-suite (Slack)                            ║
║   📖 02_audit_logging/archives/qa_master_suite/README.md ║
╚═══════════════════════════════════════════════════════════╝
```

---

## Post-Training Actions

### For Participants

- [ ] Read policy README
- [ ] Test pre-commit hook locally
- [ ] Create test PR (practice)
- [ ] Bookmark monitoring dashboard
- [ ] Join #qa-master-suite Slack channel

### For Trainers

- [ ] Distribute training materials
- [ ] Share recording (if recorded)
- [ ] Collect feedback survey
- [ ] Update docs based on questions
- [ ] Schedule follow-up Q&A (1 week later)

---

## Training Feedback Survey

Please complete after training:

```
1. How well did you understand the DUAL-LAYER architecture?
   [ ] Very well [ ] Somewhat [ ] Not well

2. Do you know where to place test files now?
   [ ] Yes, confident [ ] Mostly [ ] Still confused

3. What was most helpful?
   ________________________________________________

4. What needs more clarification?
   ________________________________________________

5. Suggestions for improvement:
   ________________________________________________

6. Overall rating (1-5): ___
```

---

## Appendix: Training Slides Outline

### Slide 1: Title
- QA Master Suite - Team Training
- Date, Facilitator

### Slide 2: Agenda
- 9 modules, 90 minutes
- Interactive exercises

### Slide 3: The Problem
- Test chaos diagram
- Before: 20+ scattered test dirs
- Compliance gaps

### Slide 4: The Solution
- DUAL-LAYER architecture diagram
- 3 layers: Active QA, Archive, SoT Governance

### Slide 5: Policy Rules
- ✅ Allowed locations
- ❌ Forbidden locations
- 🔓 5 SoT exceptions

### Slide 6: Enforcement Stack
- Pre-commit hook
- OPA CI/CD
- Branch Protection
- All layers diagram

### Slide 7: Demo - Violation
- Screen recording: commit blocked
- Error message
- Fix process

### Slide 8: Demo - Compliant
- Screen recording: commit successful
- PR passes OPA
- Merge approved

### Slide 9: Hands-On Exercise
- Exercise 1, 2, 3 (as above)

### Slide 10: WORM & Blockchain
- What, Why, When
- Quick demo

### Slide 11: Daily Workflow
- Developer workflow diagram
- QA Engineer workflow diagram

### Slide 12: Monitoring
- Dashboard screenshot
- Key metrics

### Slide 13: Quarterly Reviews
- Schedule
- Template

### Slide 14: Q&A
- Common questions & answers

### Slide 15: Resources
- Documentation links
- Support channels
- Quick reference card

### Slide 16: Next Steps
- Post-training checklist
- Practice assignments

### Slide 17: Thank You
- Feedback survey link
- Contact info

---

**END OF TRAINING GUIDE**

*Version: 1.0.0*
*Last Updated: 2025-10-18*
*Next Training: TBD (schedule after Phase 2 completion)*
