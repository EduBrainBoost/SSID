# GitHub Branch Protection Setup Guide

**Version:** 1.0.0
**Datum:** 2025-10-18
**Owner:** SSID DevOps Team
**Status:** READY FOR IMPLEMENTATION

---

## Executive Summary

This guide provides step-by-step instructions to configure GitHub Branch Protection Rules to enforce OPA Policy Checks and ensure code quality standards.

**Timeline:** 15-30 minutes
**Prerequisites:** Repository admin access
**Impact:** All PRs must pass OPA checks before merging

---

## Why Branch Protection?

Branch Protection ensures:
- ✅ All code changes pass QA Policy checks
- ✅ OPA violations block merges
- ✅ Compliance is enforced at GitHub level
- ✅ No bypassing of pre-commit hooks via web UI

---

## Prerequisites

1. **Admin Access:** You must be a repository administrator
2. **Workflow Active:** `.github/workflows/qa_policy_check.yml` must exist
3. **Test Run:** Workflow has run at least once successfully

**Verify:**
```bash
# Check if workflow exists
ls .github/workflows/qa_policy_check.yml

# Check recent workflow runs
gh run list --workflow=qa_policy_check.yml --limit 5
```

---

## Step-by-Step Setup

### Method 1: GitHub Web UI (Recommended)

#### 1. Navigate to Repository Settings

```
GitHub Repository → Settings → Branches
```

#### 2. Add Branch Protection Rule

Click **"Add rule"** or **"Add branch protection rule"**

#### 3. Configure Rule for `main` Branch

**Branch name pattern:** `main`

**Enable the following settings:**

##### ✅ Require a pull request before merging
- [x] **Require a pull request before merging**
- [x] Require approvals: **1** (or more based on policy)
- [x] Dismiss stale pull request approvals when new commits are pushed
- [ ] Require review from Code Owners (optional)

##### ✅ Require status checks to pass before merging
- [x] **Require status checks to pass before merging**
- [x] Require branches to be up to date before merging

**Status checks that are required:**
- [x] `QA Policy Enforcement Check` (from `qa_policy_check.yml`)
- [x] `qa-policy-enforcement` (job name)

**How to find status check names:**
1. Go to a recent Pull Request
2. Scroll to "Checks" section
3. Copy the exact names of checks you want to require

##### ⚠️ Additional Recommended Settings
- [x] Require conversation resolution before merging
- [x] Require signed commits (if using GPG)
- [x] Include administrators (enforce rules even for admins)
- [x] Restrict who can push to matching branches (optional, for production)

##### ❌ Settings to AVOID
- [ ] Allow force pushes (should be DISABLED)
- [ ] Allow deletions (should be DISABLED)

#### 4. Save Changes

Click **"Create"** or **"Save changes"**

---

### Method 2: GitHub CLI (`gh`)

```bash
# Navigate to repository
cd /c/Users/bibel/Documents/Github/SSID

# Create branch protection rule
gh api repos/{owner}/{repo}/branches/main/protection \
  --method PUT \
  --input - <<'EOF'
{
  "required_status_checks": {
    "strict": true,
    "contexts": [
      "QA Policy Enforcement Check",
      "qa-policy-enforcement"
    ]
  },
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": false,
    "required_approving_review_count": 1
  },
  "restrictions": null,
  "required_linear_history": false,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "required_conversation_resolution": true
}
EOF
```

**Replace `{owner}` and `{repo}` with your values:**
```bash
# Get owner and repo
gh repo view --json owner,name
```

---

### Method 3: Terraform (Infrastructure as Code)

Create file: `infrastructure/github_branch_protection.tf`

```hcl
terraform {
  required_providers {
    github = {
      source  = "integrations/github"
      version = "~> 5.0"
    }
  }
}

provider "github" {
  token = var.github_token
  owner = var.github_owner
}

resource "github_branch_protection" "main" {
  repository_id = var.repository_name

  pattern = "main"

  required_status_checks {
    strict   = true
    contexts = [
      "QA Policy Enforcement Check",
      "qa-policy-enforcement"
    ]
  }

  required_pull_request_reviews {
    dismiss_stale_reviews      = true
    require_code_owner_reviews = false
    required_approving_review_count = 1
  }

  enforce_admins              = true
  require_conversation_resolution = true
  require_signed_commits      = false

  allows_force_pushes = false
  allows_deletions    = false
}

output "branch_protection_url" {
  value = "https://github.com/${var.github_owner}/${var.repository_name}/settings/branches"
}
```

**Apply:**
```bash
terraform init
terraform plan
terraform apply
```

---

## Verification

### 1. Check Branch Protection is Active

**Web UI:**
```
Repository → Settings → Branches → Branch protection rules
```

Should show rule for `main` with required checks.

**CLI:**
```bash
gh api repos/{owner}/{repo}/branches/main/protection | jq '.required_status_checks.contexts'
```

**Expected output:**
```json
[
  "QA Policy Enforcement Check",
  "qa-policy-enforcement"
]
```

### 2. Test with a Violating PR

Create a test PR that violates QA policy:

```bash
# Create test branch
git checkout -b test-branch-protection

# Add a violating file
echo "test" > 01_ai_layer/test_violation.py
git add 01_ai_layer/test_violation.py
git commit -m "test: Add violating test file"
git push origin test-branch-protection

# Create PR
gh pr create --title "Test: Branch Protection" --body "Testing OPA enforcement"
```

**Expected Behavior:**
1. OPA workflow runs
2. Detects violation (`01_ai_layer/test_violation.py`)
3. Check fails with red ❌
4. **Merge button is disabled**
5. Message shows: "Required status checks must pass before merging"

**Screenshot what you should see:**
```
❌ QA Policy Enforcement Check — Failed
   - 1 file violates QA policy
   - Details: test_violation.py is outside allowed directories

⚠️ Merging is blocked
   Required status checks must pass before merging
```

### 3. Test with a Compliant PR

Fix the violation:

```bash
# Move file to allowed directory
git mv 01_ai_layer/test_violation.py 11_test_simulation/test_example.py
git commit -m "fix: Move test to allowed directory"
git push
```

**Expected Behavior:**
1. OPA workflow re-runs
2. No violations detected
3. Check passes with green ✅
4. **Merge button is enabled**

---

## Troubleshooting

### Issue: "Required checks not found"

**Cause:** Workflow hasn't run yet or check name mismatch

**Solution:**
1. Trigger workflow manually:
   ```bash
   gh workflow run qa_policy_check.yml
   ```
2. Wait for completion
3. Check exact status check name in PR
4. Update branch protection rule with correct name

---

### Issue: "Merge button still enabled despite failures"

**Cause:** Branch protection not properly configured

**Solution:**
1. Verify "Require status checks to pass" is checked
2. Verify correct check names are listed
3. Verify "Require branches to be up to date" is checked (if desired)
4. Save and wait ~1 minute for changes to propagate

---

### Issue: "Administrators can still bypass"

**Cause:** "Include administrators" not enabled

**Solution:**
1. Settings → Branches → Edit rule
2. Check "Include administrators"
3. Save
4. Test again (admins should now be blocked too)

---

### Issue: "Check runs but doesn't appear as required"

**Cause:** Check name in branch protection doesn't match workflow

**Solution:**
```bash
# Get exact check name from recent PR
gh pr checks <PR_NUMBER>

# Look for "QA Policy Enforcement Check" or similar
# Copy exact name to branch protection settings
```

---

## Rollback Procedure

If branch protection causes issues:

### Disable Rule Temporarily

**Web UI:**
```
Settings → Branches → Edit rule → Uncheck "Require status checks"
```

**CLI:**
```bash
gh api repos/{owner}/{repo}/branches/main/protection \
  --method DELETE
```

### Re-enable After Fix

Follow setup steps again.

---

## Advanced Configuration

### Multiple Branches

Protect `develop` branch in addition to `main`:

```bash
# Add rule for develop
gh api repos/{owner}/{repo}/branches/develop/protection \
  --method PUT \
  --input - <<'EOF'
{
  "required_status_checks": {
    "strict": false,
    "contexts": ["qa-policy-enforcement"]
  },
  "enforce_admins": false,
  "required_pull_request_reviews": null,
  "restrictions": null
}
EOF
```

### Custom Status Check Names

If you rename the workflow or job:

1. Update `.github/workflows/qa_policy_check.yml`:
   ```yaml
   name: My Custom Check Name
   jobs:
     my-custom-job:
       name: My Custom Job
   ```

2. Update branch protection to use:
   - `My Custom Check Name`
   - `my-custom-job`

---

## Monitoring & Alerts

### Track Blocked Merges

Create dashboard query:
```sql
-- GitHub Events API
SELECT
  created_at,
  pr_number,
  blocked_by_check
FROM github_events
WHERE event_type = 'pull_request'
  AND action = 'blocked'
  AND check_name LIKE '%QA Policy%'
```

### Alert on Bypasses

Set up alert if anyone force-pushes to `main`:

```yaml
# .github/workflows/force_push_alert.yml
name: Alert on Force Push

on:
  push:
    branches: [main]

jobs:
  check-force-push:
    runs-on: ubuntu-latest
    steps:
      - name: Check for force push
        run: |
          if [ "${{ github.event.forced }}" = "true" ]; then
            echo "::error::Force push detected on main branch!"
            # Send alert to Slack, email, etc.
          fi
```

---

## Documentation for Developers

Add to `CONTRIBUTING.md`:

```markdown
## Branch Protection

The `main` branch is protected. All changes must:

1. **Pass OPA Policy Check:** All test files must be in approved locations
2. **Get 1 approval:** From a team member
3. **Resolve conversations:** All review comments must be resolved

### If your PR is blocked:

1. Check the "Checks" tab
2. Look for "QA Policy Enforcement Check"
3. If it failed, review the error message
4. Move offending files to allowed directories:
   - `02_audit_logging/archives/qa_master_suite/`
   - `11_test_simulation/`
5. Push changes to re-trigger check

### Policy Documentation:
- [QA Policy README](02_audit_logging/archives/qa_master_suite/README.md)
- [OPA Policy](23_compliance/policies/qa/qa_policy_enforcer.rego)
```

---

## Next Steps

After enabling branch protection:

1. **Communicate to team:**
   - Announce in Slack/Email
   - Link to this guide
   - Explain new workflow requirements

2. **Monitor for issues:**
   - First week: Watch for confusion
   - Provide support
   - Update docs based on feedback

3. **Train team:**
   - Hold training session (see `TEAM_TRAINING_GUIDE.md`)
   - Demo blocked PR → fix → merge
   - Answer questions

4. **Quarterly review:**
   - Review effectiveness
   - Check for bypasses
   - Update as needed

---

## Success Criteria

Branch protection is successfully configured when:

- ✅ PR with violations cannot be merged
- ✅ PR without violations can be merged
- ✅ Administrators are also blocked (if configured)
- ✅ Team understands new workflow
- ✅ No increase in force-pushes or bypasses

---

## Support

**Branch Protection Owner:** SSID DevOps Team
**Questions:** devops@ssid-project.internal
**Issues:** Create GitHub issue with label `branch-protection`
**Emergency:** devops-oncall@ssid-project.internal

---

**END OF SETUP GUIDE**

*Status: READY FOR IMPLEMENTATION*
*Last Updated: 2025-10-18*
*Classification: INTERNAL USE ONLY*
