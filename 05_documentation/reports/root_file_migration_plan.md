# SSID Root File Migration Plan

**Version:** 1.0.0
**Date:** 2025-10-12
**Policy:** Root-24-LOCK
**Status:** PENDING EXECUTION
**Cost:** $0 (local file operations)

---

## Executive Summary

This document provides a comprehensive migration plan to achieve **100% Root-24-LOCK compliance** by relocating unauthorized root-level files to their proper locations within the authorized 24-module structure.

### Current Status

- **Compliance Score:** 30/100 (FAIL)
- **Critical Violations:** 3
- **Warning Violations:** 5
- **Target Score:** 100/100 (PASS)

---

## Violations Summary

### Critical Violations (3)

These items must be removed immediately:

| Item | Type | Impact | Action |
|------|------|--------|--------|
| `.claude/` | Directory | CRITICAL | Remove (IDE-specific, add to .gitignore) |
| `.github/` | Directory | CRITICAL | Evaluate: Add to policy exceptions OR migrate to 04_deployment/ |
| `.pytest_cache/` | Directory | CRITICAL | Remove (test cache, add to .gitignore) |

### Warning Violations (5)

These files should be migrated to maintain clean structure:

| Current Location | Target Location | Type |
|------------------|-----------------|------|
| `DEPLOYMENT_v5.2.md` | `05_documentation/deployment/` | Deployment doc |
| `DEPLOYMENT_v5.4_Federation.md` | `05_documentation/deployment/` | Deployment doc |
| `DEPLOYMENT_v6.0_Planetary_Continuum.md` | `05_documentation/deployment/` | Deployment doc |
| `DEPLOYMENT_v8.0_Continuum_Ignition.md` | `05_documentation/deployment/` | Deployment doc |
| `TRANSITION_v6_to_v7_DORMANT.md` | `05_documentation/transitions/` | Transition doc |

---

## Migration Steps

### Phase 1: Critical Violations (IMMEDIATE)

#### Step 1.1: Remove .claude/ directory

```bash
# Verify it's safe to remove (check if it contains any critical data)
ls -la .claude/

# Remove the directory
rm -rf .claude/

# Add to .gitignore to prevent re-creation
echo ".claude/" >> .gitignore
```

**Rationale:** `.claude/` is IDE/tool-specific configuration and should not be in version control.

---

#### Step 1.2: Remove .pytest_cache/ directory

```bash
# Remove pytest cache
rm -rf .pytest_cache/

# Ensure it's in .gitignore
grep -q ".pytest_cache" .gitignore || echo ".pytest_cache/" >> .gitignore
```

**Rationale:** Test caches are temporary and should be excluded from version control.

---

#### Step 1.3: Handle .github/ directory

**Option A: Add to Policy Exceptions (Recommended)**

If `.github/` contains CI/CD workflows and GitHub-specific metadata:

```yaml
# Update: 23_compliance/policies/root_24_integrity_policy.yaml
# Add to authorized_exceptions.directories:

directories:
  - name: ".github"
    purpose: "GitHub-specific configuration (workflows, issue templates)"
    required: false
    note: "Contains CI/CD workflows and GitHub metadata only"
```

**Option B: Migrate to 04_deployment/**

If you want stricter compliance:

```bash
# Create deployment CI directory
mkdir -p 04_deployment/ci/github_workflows

# Move workflows
mv .github/workflows/* 04_deployment/ci/github_workflows/

# Create symlink (if needed for GitHub to find them)
ln -s ../04_deployment/ci/github_workflows .github/workflows

# OR: Update workflow paths in repository settings
```

**Recommendation:** Use **Option A** - GitHub expects `.github/` at root, and it's a common convention.

---

### Phase 2: Warning Violations (SHORT-TERM)

#### Step 2.1: Migrate Deployment Documentation

```bash
# Create deployment documentation directory
mkdir -p 05_documentation/deployment

# Migrate all DEPLOYMENT_*.md files
mv DEPLOYMENT_v5.2.md 05_documentation/deployment/
mv DEPLOYMENT_v5.4_Federation.md 05_documentation/deployment/
mv DEPLOYMENT_v6.0_Planetary_Continuum.md 05_documentation/deployment/
mv DEPLOYMENT_v8.0_Continuum_Ignition.md 05_documentation/deployment/

# Verify migration
ls -la 05_documentation/deployment/
```

**Expected Result:**
```
05_documentation/deployment/
├── DEPLOYMENT_v5.2.md
├── DEPLOYMENT_v5.4_Federation.md
├── DEPLOYMENT_v6.0_Planetary_Continuum.md
└── DEPLOYMENT_v8.0_Continuum_Ignition.md
```

---

#### Step 2.2: Migrate Transition Documentation

```bash
# Create transitions documentation directory
mkdir -p 05_documentation/transitions

# Migrate TRANSITION_*.md files
mv TRANSITION_v6_to_v7_DORMANT.md 05_documentation/transitions/

# Verify migration
ls -la 05_documentation/transitions/
```

**Expected Result:**
```
05_documentation/transitions/
└── TRANSITION_v6_to_v7_DORMANT.md
```

---

#### Step 2.3: Update Internal References

After migration, update any references to the moved files:

```bash
# Search for references to old paths
grep -r "DEPLOYMENT_v5.2.md" . --exclude-dir=.git
grep -r "DEPLOYMENT_v5.4_Federation.md" . --exclude-dir=.git
grep -r "DEPLOYMENT_v6.0_Planetary_Continuum.md" . --exclude-dir=.git
grep -r "DEPLOYMENT_v8.0_Continuum_Ignition.md" . --exclude-dir=.git
grep -r "TRANSITION_v6_to_v7_DORMANT.md" . --exclude-dir=.git

# Update README.md if it references these files
# Update any navigation docs in 05_documentation/
```

**Common references to update:**
- `README.md` - Update links to deployment docs
- `05_documentation/index.md` - Update documentation index
- Any internal navigation or table of contents

---

### Phase 3: .gitignore Updates

Update `.gitignore` to prevent future violations:

```bash
# Add to .gitignore
cat >> .gitignore << 'EOF'

# Root-24-LOCK - Prevent root violations
# IDE/Tool specific
.claude/
.vscode/
.idea/
.eclipse/

# Python
__pycache__/
*.py[cod]
*.egg-info/
.pytest_cache/
.tox/
.coverage
htmlcov/

# Virtual environments
venv/
.venv/
env/
ENV/

# Build artifacts
dist/
build/
*.egg

# OS specific
.DS_Store
Thumbs.db
desktop.ini

# Node
node_modules/
npm-debug.log

EOF
```

---

### Phase 4: Verification

After completing migration, verify compliance:

```bash
# Run root structure audit
python 12_tooling/root_structure_audit.py

# Check the score
cat 23_compliance/reports/root_structure_score.json | grep "overall_score"

# Expected: "overall_score": 100.0
```

---

## Complete Migration Script

For automated execution:

```bash
#!/bin/bash
# SSID Root-24-LOCK Migration Script
# Version: 1.0.0

set -e  # Exit on error

echo "=========================================="
echo "SSID Root-24-LOCK Migration"
echo "=========================================="
echo ""

# Phase 1: Critical Violations
echo "Phase 1: Removing critical violations..."

# Remove .claude/
if [ -d ".claude" ]; then
    echo "  Removing .claude/..."
    rm -rf .claude/
fi

# Remove .pytest_cache/
if [ -d ".pytest_cache" ]; then
    echo "  Removing .pytest_cache/..."
    rm -rf .pytest_cache/
fi

# Update .gitignore
echo "  Updating .gitignore..."
grep -q ".claude/" .gitignore || echo ".claude/" >> .gitignore
grep -q ".pytest_cache/" .gitignore || echo ".pytest_cache/" >> .gitignore

echo "  ✅ Critical violations addressed"
echo ""

# Phase 2: Warning Violations
echo "Phase 2: Migrating documentation..."

# Create target directories
mkdir -p 05_documentation/deployment
mkdir -p 05_documentation/transitions

# Migrate deployment docs
echo "  Migrating DEPLOYMENT_*.md files..."
for file in DEPLOYMENT_*.md; do
    if [ -f "$file" ]; then
        echo "    $file -> 05_documentation/deployment/"
        mv "$file" 05_documentation/deployment/
    fi
done

# Migrate transition docs
echo "  Migrating TRANSITION_*.md files..."
for file in TRANSITION_*.md; do
    if [ -f "$file" ]; then
        echo "    $file -> 05_documentation/transitions/"
        mv "$file" 05_documentation/transitions/
    fi
done

echo "  ✅ Documentation migrated"
echo ""

# Phase 3: Verification
echo "Phase 3: Verification..."

# Run audit
echo "  Running root structure audit..."
python 12_tooling/root_structure_audit.py

# Check score
SCORE=$(python3 -c "import json; print(json.load(open('23_compliance/reports/root_structure_score.json'))['overall_score'])")
echo "  Compliance Score: $SCORE/100"

if [ "$SCORE" == "100.0" ] || [ "$SCORE" == "100" ]; then
    echo "  ✅ Full Root-24-LOCK compliance achieved!"
else
    echo "  ⚠️ Score: $SCORE/100 - review audit report for remaining issues"
fi

echo ""
echo "=========================================="
echo "Migration Complete"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Review changes: git status"
echo "  2. Update references to migrated files"
echo "  3. Commit changes: git add . && git commit -m 'refactor: Root-24-LOCK compliance migration'"
echo ""
```

**Save as:** `12_tooling/migrate_root_24_compliance.sh`

**Usage:**
```bash
chmod +x 12_tooling/migrate_root_24_compliance.sh
./12_tooling/migrate_root_24_compliance.sh
```

---

## Post-Migration Tasks

### 1. Update Documentation Index

Create or update `05_documentation/README.md`:

```markdown
# SSID Documentation

## Deployment Guides

- [v5.2 Deployment](deployment/DEPLOYMENT_v5.2.md)
- [v5.4 Federation Activation](deployment/DEPLOYMENT_v5.4_Federation.md)
- [v6.0 Planetary Continuum](deployment/DEPLOYMENT_v6.0_Planetary_Continuum.md)
- [v8.0 Continuum Ignition](deployment/DEPLOYMENT_v8.0_Continuum_Ignition.md)

## Version Transitions

- [v6 → v7 Dormant Transition](transitions/TRANSITION_v6_to_v7_DORMANT.md)
```

### 2. Update README.md

Update project root `README.md` to reference new paths:

```markdown
## Documentation

For deployment guides, see [05_documentation/deployment/](05_documentation/deployment/)

For version transitions, see [05_documentation/transitions/](05_documentation/transitions/)
```

### 3. Enable CI Structure Guard

```bash
# Ensure CI workflow is executable
chmod +x .github/workflows/ci_structure_guard.yml

# Commit and push to trigger CI
git add .github/workflows/ci_structure_guard.yml
git commit -m "ci: enable Root-24-LOCK structure guard"
git push
```

### 4. Enable Pre-commit Hooks (Optional)

Add root structure check to `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: root-structure-check
        name: Root-24-LOCK Structure Check
        entry: python 12_tooling/root_structure_audit.py
        language: system
        pass_filenames: false
        always_run: true
```

---

## Expected Outcomes

### Before Migration

```
Root Structure Score: 30/100 (FAIL)
- Critical Violations: 3
- Warnings: 5
- Unauthorized Items: 8
```

### After Migration

```
Root Structure Score: 100/100 (PASS)
- Critical Violations: 0
- Warnings: 0
- Unauthorized Items: 0
- Full Root-24-LOCK Compliance ✅
```

---

## Rollback Plan

If migration causes issues:

```bash
# Restore from git
git checkout -- .

# Or restore specific files
git checkout -- DEPLOYMENT_v*.md
git checkout -- TRANSITION_v*.md

# Re-create directories if needed
git checkout -- .claude/
git checkout -- .pytest_cache/
```

**Note:** Only rollback if critical functionality breaks. The migration is recommended for long-term structural integrity.

---

## Timeline

| Phase | Duration | Priority |
|-------|----------|----------|
| Phase 1 (Critical) | 1 hour | IMMEDIATE |
| Phase 2 (Warnings) | 2 hours | HIGH |
| Phase 3 (Verification) | 30 minutes | HIGH |
| Post-Migration Tasks | 1 hour | MEDIUM |
| **Total** | **~4.5 hours** | - |

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Broken references | Medium | Medium | Search and update all references |
| CI pipeline breaks | Low | High | Test CI before merging |
| Lost file access | Very Low | High | Files are moved, not deleted |
| Git history issues | Low | Low | All changes are tracked in git |

---

## Success Criteria

✅ **Root-24-LOCK Compliance:** Score 100/100
✅ **Zero Critical Violations**
✅ **Zero Warning Violations**
✅ **CI Structure Guard:** Enabled and passing
✅ **All References Updated:** No broken links
✅ **Documentation:** Migration documented

---

## Support & References

- **Root-24-LOCK Policy:** `23_compliance/policies/root_24_integrity_policy.yaml`
- **OPA Guard:** `23_compliance/policies/activation_guard.rego`
- **Audit Scanner:** `12_tooling/root_structure_audit.py`
- **Audit Report:** `02_audit_logging/reports/root_structure_audit_report.md`
- **Score Report:** `23_compliance/reports/root_structure_score.json`

---

**END OF MIGRATION PLAN**

*Execute this plan to achieve 100% Root-24-LOCK compliance with zero cost and minimal risk.*
