# SSID Operations Guide - Blueprint v4.2

## Overview

This guide outlines the operational procedures for maintaining 100% compliance with Blueprint v4.2 and the Root-24-LOCK standard.

## Regular Maintenance Schedule

### Monthly Compliance Check

**Frequency:** First Monday of each month  
**Duration:** ~5 minutes  
**Command:**
```bash
bash 12_tooling/scripts/structure_guard.sh
```

**What it checks:**
- All 24 root directories are present and unchanged
- Pre-commit hooks are active and properly configured
- No unauthorized structural modifications
- Directory naming conventions are maintained

**Expected Output:**
```
✅ Root-24-LOCK: COMPLIANT (24 roots verified)
```

**Action on Failure:**
1. Review the violation report
2. Identify the structural change
3. Either revert the change or update the blueprint documentation
4. Re-run validation

### Quarterly Compliance Audit

**Frequency:** End of each quarter (Q1: March 31, Q2: June 30, Q3: September 30, Q4: December 31)  
**Duration:** ~10 minutes  
**Command:**
```bash
bash 12_tooling/scripts/run_quarterly_audit.sh
```

**What it generates:**
- Comprehensive compliance report in `05_documentation/reports/YYYY-QX/COMPLIANCE_REPORT.md`
- Updated governance dashboard in `05_documentation/reports/dashboard/SSID_Governance_Dashboard.md`
- Updated dashboard metrics in `05_documentation/reports/dashboard/dashboard_data.csv`
- Commit history analysis
- Test coverage metrics
- Structure validation results
- CI/CD pipeline status

**Post-Audit Actions:**
1. Review the generated report
2. Check the updated governance dashboard
3. Address any identified issues
4. Update README with link to latest report
5. Commit the audit report:
   ```bash
   git add 05_documentation/reports/
   git commit -m "Add quarterly compliance report for YYYY-QX"
   git push origin main
   ```

**Automated Quarterly Audits:**

The quarterly audit can now run automatically via GitHub Actions:

- **Trigger:** Scheduled cron job on 1st of Jan/Apr/Jul/Oct at 08:00 UTC
- **Workflow:** `.github/workflows/quarterly_audit.yml`
- **Manual Trigger:** Available via GitHub Actions UI (workflow_dispatch)

The automated workflow will:
- Run the complete quarterly audit
- Update the governance dashboard
- Generate a pull request with results
- Include proof-anchor for external verification
- Provide options for on-chain/IPFS anchoring

### Release Tag Events

**Frequency:** After each version tag  
**Duration:** ~2 minutes  
**Command:**
```bash
# Get current commit hash
CURRENT_HASH=$(git rev-parse HEAD)

# Emit registry event
bash 12_tooling/scripts/registry_event_trigger.sh \
  --event "release_tagged" \
  --version "vX.Y.Z" \
  --hash "$CURRENT_HASH"
```

**What it does:**
- Emits a tamper-proof registry event
- Logs the release in `24_meta_orchestration/registry/logs/registry_events.log`
- Generates a cryptographic proof-anchor (SHA256)
- Creates an audit trail for the release

**Example:**
```bash
# For release v4.2.1
git tag -a v4.2.1 -m "Release v4.2.1"
bash 12_tooling/scripts/registry_event_trigger.sh \
  --event "release_tagged" \
  --version "v4.2.1" \
  --hash "$(git rev-parse HEAD)"
git push origin v4.2.1
```

## CI/CD Pipeline

### GitHub Actions Workflows

**Structure Guard Workflow:**
- **File:** `.github/workflows/structure_guard.yml`
- **Trigger:** On every push and pull request
- **Validation:** Runs `structure_guard.sh` to verify Root-24-LOCK
- **Badge:** ![Structure Guard](https://github.com/EduBrainBoost/SSID/actions/workflows/structure_guard.yml/badge.svg)

**Quarterly Audit Workflow (NEW):**
- **File:** `.github/workflows/quarterly_audit.yml`
- **Trigger:** Scheduled cron on 1st of Jan/Apr/Jul/Oct at 08:00 UTC
- **Manual Trigger:** Available via workflow_dispatch
- **Actions:**
  - Runs complete quarterly compliance audit
  - Updates governance dashboard with latest metrics
  - Generates proof-anchor for external verification
  - Creates pull request with audit results
  - Provides instructions for on-chain/IPFS anchoring

### Pre-commit Hook

**Location:** `.git/hooks/pre-commit`  
**Source:** `12_tooling/hooks/pre_commit/root24_enforcer.sh`

**What it validates:**
- All 24 root directories exist before commit
- No root directories have been renamed or deleted
- Compliance score remains at 100/100

**Re-install hook (if needed):**
```bash
cp 12_tooling/hooks/pre_commit/root24_enforcer.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

## Branch Protection Setup

### Apply Branch Protection Rules

**Option 1: GitHub CLI**
```bash
gh api repos/EduBrainBoost/SSID/branches/main/protection \
  --method PUT \
  --field required_status_checks='{"strict":true,"contexts":["Structure Guard / guard","Root-24-LOCK Validation"]}' \
  --field enforce_admins=true \
  --field required_pull_request_reviews='{"required_approving_review_count":1,"dismiss_stale_reviews":true}' \
  --field required_signatures=true \
  --field allow_force_pushes=false \
  --field allow_deletions=false \
  --field required_conversation_resolution=true
```

**Option 2: GitHub Web UI**
1. Go to Settings → Branches
2. Add rule for branch name pattern: `main`
3. Enable:
   - ✅ Require pull request reviews before merging (1 approval)
   - ✅ Dismiss stale pull request approvals
   - ✅ Require status checks to pass: "Structure Guard / guard"
   - ✅ Require signed commits
   - ✅ Require conversation resolution
   - ✅ Do not allow bypassing the above settings (include administrators)
   - ✅ Block force pushes
   - ✅ Block deletions

## Monitoring & Alerts

### Key Metrics to Monitor

1. **Compliance Score:** Must remain at 100/100
2. **Root Count:** Must always be exactly 24
3. **CI/CD Status:** All workflows should pass
4. **Pre-commit Hook Status:** Must be active

### Registry Event Log

**Location:** `24_meta_orchestration/registry/logs/registry_events.log`

**Purpose:**
- Tamper-proof audit trail
- Cryptographic proof-anchors for major events
- Compliance verification history

**View recent events:**
```bash
tail -n 20 24_meta_orchestration/registry/logs/registry_events.log
```

## Troubleshooting

### Structure Guard Fails

**Symptoms:** `structure_guard.sh` reports violations

**Solutions:**
1. Check which root directories are missing:
   ```bash
   bash 12_tooling/scripts/structure_guard.sh 2>&1 | grep "MISSING"
   ```
2. Verify directory names match exactly (including leading zeros)
3. Check git history for unauthorized deletions:
   ```bash
   git log --all --full-history --oneline -- "XX_*/"
   ```

### Pre-commit Hook Not Running

**Symptoms:** Commits succeed without validation

**Solutions:**
1. Verify hook exists and is executable:
   ```bash
   ls -l .git/hooks/pre-commit
   ```
2. Re-install hook:
   ```bash
   cp 12_tooling/hooks/pre_commit/root24_enforcer.sh .git/hooks/pre-commit
   chmod +x .git/hooks/pre-commit
   ```
3. Test manually:
   ```bash
   bash .git/hooks/pre-commit
   ```

### GitHub Actions Workflow Failing

**Symptoms:** Red X on commits in GitHub

**Solutions:**
1. Check workflow runs: https://github.com/EduBrainBoost/SSID/actions
2. Review workflow logs for error details
3. Ensure `structure_guard.sh` is executable:
   ```bash
   chmod +x 12_tooling/scripts/structure_guard.sh
   ```
4. Test locally:
   ```bash
   bash 12_tooling/scripts/structure_guard.sh
   ```

## Best Practices

### 1. Never Bypass Validation
- Always let pre-commit hooks run
- Never use `git commit --no-verify`
- Never force push to protected branches

### 2. Regular Audits
- Run monthly structure checks
- Generate quarterly compliance reports
- Review registry event logs periodically

### 3. Documentation Updates
- Keep README.md current with latest compliance status
- Link to most recent quarterly report
- Update registry manifests after major changes

### 4. Version Control
- Tag all releases with semantic versioning
- Emit registry events for each tag
- Maintain detailed commit messages

### 5. Transparency
- Keep all compliance reports public
- Document all structural changes
- Maintain audit trail integrity

## Advanced Features (v4.2.1+)

### Audit Report Comparison

**Purpose:** Analyze score drift between quarters

**Command:**
```bash
python3 12_tooling/scripts/diff_audit_reports.py <quarter1> <quarter2>

# Example
python3 12_tooling/scripts/diff_audit_reports.py 2025-Q4 2026-Q1
```

**Output:**
- Detailed comparison report in `05_documentation/reports/comparisons/`
- Score drift analysis
- Violation trends
- Commit activity comparison
- Recommendations for improvement

**Use Cases:**
- Quarterly performance tracking
- Compliance trend analysis
- Identifying degradation patterns
- Root cause analysis for score changes

### External Proof-Anchoring

**Purpose:** Anchor proof-hashes to external systems for independent verification

**Guide:** `05_documentation/PROOF_ANCHORING_GUIDE.md`

**Quick Commands:**

```bash
# Anchor to IPFS (free)
ipfs add 05_documentation/reports/2026-Q1/COMPLIANCE_REPORT.md

# Anchor to Ethereum/Polygon (requires wallet)
cast send $CONTRACT "anchorProof(bytes32,string,string)" \
  0x<PROOF_ANCHOR> "2026-Q1" "github.com/EduBrainBoost/SSID" \
  --rpc-url $RPC_URL --private-key $PRIVATE_KEY

# Anchor to Arweave (permanent storage)
arweave deploy 05_documentation/reports/2026-Q1/COMPLIANCE_REPORT.md
```

**Supported Methods:**
- IPFS (decentralized, free)
- Ethereum/Polygon (blockchain, $1-5 per anchor)
- Arweave (permanent, ~$0.01/MB one-time)
- Certificate Transparency (timestamping, free)
- Bitcoin OP_RETURN (ultra-permanent, ~$1-10)

### Governance Dashboard

**Location:** `05_documentation/reports/dashboard/SSID_Governance_Dashboard.md`

**Features:**
- Real-time compliance metrics
- Quarterly trend charts (Markdown format)
- Registry proof-anchors table
- Compliance reports overview
- Commit activity visualization
- Evidence-chain status
- Next scheduled audit

**Auto-updates:** Dashboard regenerates automatically during quarterly audits

**Manual Update:**
```bash
python3 12_tooling/scripts/update_governance_dashboard.py
```

## Blueprint v4.4 Functional Expansion Commands (NEW)

### Policy Compiler

**Purpose:** Generate OPA/Rego policies from compliance mappings

```bash
# Compile all policies from mappings
python3 12_tooling/scripts/policy_compiler.py --compile-all

# Validate existing policies only
python3 12_tooling/scripts/policy_compiler.py --validate-only
```

**Output:**
- `23_compliance/policy/*.rego` - Generated policies
- `23_compliance/policy/tests/*_test.rego` - Unit tests
- `02_audit_logging/reports/policy_activation_log.json` - Audit log

### Evidence Proof Emitter

**Purpose:** Generate cryptographic proofs for forensic reports

```bash
# Generate proofs for all forensic files
python3 12_tooling/scripts/evidence_proof_emitter.py --emit

# Generate proofs with IPFS anchoring
python3 12_tooling/scripts/evidence_proof_emitter.py --emit --auto-anchor

# Verify specific file
python3 12_tooling/scripts/evidence_proof_emitter.py \
  --verify-file "05_documentation/reports/2026-Q1/COMPLIANCE_REPORT.md"

# Calculate Merkle root for quarter
python3 12_tooling/scripts/evidence_proof_emitter.py \
  --calculate-merkle-root --quarter "2026-Q1"
```

**Output:**
- `23_compliance/evidence/proof_hashes.json` - All file proofs
- `24_meta_orchestration/registry/events/evidence_emission_event.json` - Registry event
- `02_audit_logging/reports/evidence_emission_log.json` - Audit log

### Review Flow Manager

**Purpose:** Automate governance review and approval workflows

```bash
# Create review item
python3 07_governance_legal/automation/review_flow_manager.py \
  --create-item "blueprint" "Blueprint v4.5 Proposal" "AI-powered governance"

# Submit review (approve/reject)
python3 07_governance_legal/automation/review_flow_manager.py \
  --submit-review "blueprint_abc123" "technical-lead" "approve" "LGTM"

# Quarterly status check
python3 07_governance_legal/automation/review_flow_manager.py --quarterly-check

# Finalize quarter
python3 07_governance_legal/automation/review_flow_manager.py --finalize-quarter
```

**Output:**
- `24_meta_orchestration/registry/review_items/*.json` - Review items
- `24_meta_orchestration/registry/logs/governance_review.log` - Review log
- `24_meta_orchestration/registry/events/governance_review_event.json` - Registry events

## Quick Reference Commands

```bash
# Monthly check
bash 12_tooling/scripts/structure_guard.sh

# Quarterly audit
bash 12_tooling/scripts/run_quarterly_audit.sh

# Compare audit reports
python3 12_tooling/scripts/diff_audit_reports.py 2025-Q4 2026-Q1

# Update dashboard
python3 12_tooling/scripts/update_governance_dashboard.py

# Release event
bash 12_tooling/scripts/registry_event_trigger.sh \
  --event "release_tagged" \
  --version "vX.Y.Z" \
  --hash "$(git rev-parse HEAD)"

# Verify pre-commit hook
bash .git/hooks/pre-commit

# View recent registry events
tail -n 20 24_meta_orchestration/registry/logs/registry_events.log

# View governance dashboard
cat 05_documentation/reports/dashboard/SSID_Governance_Dashboard.md

# Check CI/CD status
gh run list --limit 5

# Trigger automated quarterly audit manually
gh workflow run quarterly_audit.yml

# Anchor proof to IPFS
ipfs add 05_documentation/reports/2026-Q1/COMPLIANCE_REPORT.md

# === NEW: Blueprint v4.4 Functional Expansion === #

# Compile OPA/Rego policies
python3 12_tooling/scripts/policy_compiler.py --compile-all

# Generate evidence proofs
python3 12_tooling/scripts/evidence_proof_emitter.py --emit --auto-anchor

# Quarterly review check
python3 07_governance_legal/automation/review_flow_manager.py --quarterly-check

# Finalize quarterly governance cycle
python3 07_governance_legal/automation/review_flow_manager.py --finalize-quarter
```

## Support & Contact

**Repository:** https://github.com/EduBrainBoost/SSID  
**Blueprint Version:** v4.2.0  
**Maintainer:** EduBrainBoost <EduBrainBoost@fakemail.com>

---

_Blueprint v4.2.0 Operations Guide • Root-24-LOCK Active • 100% Compliance_
