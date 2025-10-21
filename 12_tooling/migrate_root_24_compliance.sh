#!/bin/bash
# SSID Root-24-LOCK Compliance Migration Script
# Version: 1.0.0
# Purpose: Automated remediation of Root-24 violations
# Cost: $0 (local file operations)

set -e  # Exit on error

echo "=========================================================================="
echo "  SSID Root-24-LOCK Compliance Migration"
echo "=========================================================================="
echo ""
echo "This script will:"
echo "  1. Remove critical violations (.claude/, .pytest_cache/)"
echo "  2. Migrate documentation files to proper locations"
echo "  3. Update .gitignore"
echo "  4. Verify 100/100 compliance"
echo ""
echo "Current Score: 30/100"
echo "Target Score:  100/100"
echo ""
read -p "Continue with migration? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Migration cancelled."
    exit 0
fi

echo ""
echo "=========================================================================="
echo "Phase 1: Removing Critical Violations"
echo "=========================================================================="
echo ""

# Remove .claude/ directory
if [ -d ".claude" ]; then
    echo "  Removing .claude/ ..."
    rm -rf .claude/
    echo "    ✅ Removed .claude/"
else
    echo "    ℹ️ .claude/ not found (already clean)"
fi

# Remove .pytest_cache/ directory
if [ -d ".pytest_cache" ]; then
    echo "  Removing .pytest_cache/ ..."
    rm -rf .pytest_cache/
    echo "    ✅ Removed .pytest_cache/"
else
    echo "    ℹ️ .pytest_cache/ not found (already clean)"
fi

# Update .gitignore
echo "  Updating .gitignore ..."
grep -q "^\.claude/" .gitignore 2>/dev/null || echo ".claude/" >> .gitignore
grep -q "^\.pytest_cache/" .gitignore 2>/dev/null || echo ".pytest_cache/" >> .gitignore
grep -q "^__pycache__/" .gitignore 2>/dev/null || echo "__pycache__/" >> .gitignore
echo "    ✅ .gitignore updated"

echo ""
echo "✅ Phase 1 Complete: Critical violations addressed"
echo ""

echo "=========================================================================="
echo "Phase 2: Migrating Documentation Files"
echo "=========================================================================="
echo ""

# Create target directories
echo "  Creating target directories ..."
mkdir -p 05_documentation/deployment
mkdir -p 05_documentation/transitions
echo "    ✅ Directories created"

# Migrate DEPLOYMENT_*.md files
echo "  Migrating DEPLOYMENT_*.md files ..."
MIGRATED_DEPLOYMENT=0
for file in DEPLOYMENT_*.md; do
    if [ -f "$file" ]; then
        echo "    $file -> 05_documentation/deployment/"
        mv "$file" "05_documentation/deployment/"
        MIGRATED_DEPLOYMENT=$((MIGRATED_DEPLOYMENT + 1))
    fi
done

if [ $MIGRATED_DEPLOYMENT -gt 0 ]; then
    echo "    ✅ Migrated $MIGRATED_DEPLOYMENT deployment file(s)"
else
    echo "    ℹ️ No DEPLOYMENT_*.md files found at root"
fi

# Migrate TRANSITION_*.md files
echo "  Migrating TRANSITION_*.md files ..."
MIGRATED_TRANSITION=0
for file in TRANSITION_*.md; do
    if [ -f "$file" ]; then
        echo "    $file -> 05_documentation/transitions/"
        mv "$file" "05_documentation/transitions/"
        MIGRATED_TRANSITION=$((MIGRATED_TRANSITION + 1))
    fi
done

if [ $MIGRATED_TRANSITION -gt 0 ]; then
    echo "    ✅ Migrated $MIGRATED_TRANSITION transition file(s)"
else
    echo "    ℹ️ No TRANSITION_*.md files found at root"
fi

echo ""
echo "✅ Phase 2 Complete: Documentation migrated"
echo ""

echo "=========================================================================="
echo "Phase 3: Handle .github/ Directory"
echo "=========================================================================="
echo ""

if [ -d ".github" ]; then
    echo "  .github/ directory detected"
    echo ""
    echo "  Options:"
    echo "    A) Add .github/ to policy exceptions (recommended for GitHub projects)"
    echo "    B) Keep as-is (will remain a violation)"
    echo ""
    echo "  Recommendation: Add to policy exceptions"
    echo "  This can be done by updating:"
    echo "    23_compliance/policies/root_24_integrity_policy.yaml"
    echo ""
    echo "  For now, we'll recommend adding .github/ to exceptions."
    echo "  Update the policy file manually or CI will flag this."
    echo ""
    echo "  ⚠️ Manual action required for .github/"
else
    echo "  ℹ️ .github/ not found"
fi

echo ""
echo "=========================================================================="
echo "Phase 4: Verification"
echo "=========================================================================="
echo ""

# Run audit scanner
echo "  Running root structure audit ..."
python 12_tooling/root_structure_audit.py

echo ""
echo "  Checking compliance score ..."

if [ -f "23_compliance/reports/root_structure_score.json" ]; then
    # Use Python to parse JSON
    SCORE=$(python3 -c "
import json
try:
    with open('23_compliance/reports/root_structure_score.json', 'r') as f:
        data = json.load(f)
        print(data.get('overall_score', 0))
except:
    print('ERROR')
" 2>/dev/null || echo "ERROR")

    if [ "$SCORE" == "ERROR" ]; then
        echo "    ⚠️ Could not read score file"
        echo "    Check: 23_compliance/reports/root_structure_score.json"
    else
        echo "    Compliance Score: $SCORE/100"
        echo ""

        if [ "$SCORE" == "100.0" ] || [ "$SCORE" == "100" ]; then
            echo "    ✅ Perfect compliance achieved!"
        elif (( $(echo "$SCORE >= 90" | bc -l) )); then
            echo "    ⚠️ Good compliance (≥90/100)"
            echo "    Review audit report for remaining issues"
        else
            echo "    ⚠️ Additional work needed"
            echo "    See: 02_audit_logging/reports/root_structure_audit_report.md"
        fi
    fi
else
    echo "    ⚠️ Score file not generated"
fi

echo ""
echo "=========================================================================="
echo "Migration Summary"
echo "=========================================================================="
echo ""
echo "Actions Completed:"
echo "  ✅ Removed critical violations (2)"
echo "  ✅ Updated .gitignore"
echo "  ✅ Migrated deployment docs ($MIGRATED_DEPLOYMENT files)"
echo "  ✅ Migrated transition docs ($MIGRATED_TRANSITION files)"
echo "  ✅ Re-ran compliance audit"
echo ""

if [ -d ".github" ]; then
    echo "Manual Actions Required:"
    echo "  ⚠️ Add .github/ to policy exceptions OR migrate"
    echo "     Edit: 23_compliance/policies/root_24_integrity_policy.yaml"
    echo ""
fi

echo "Next Steps:"
echo "  1. Review changes: git status"
echo "  2. Check audit report: 02_audit_logging/reports/root_structure_audit_report.md"
echo "  3. Update references to migrated files (if any)"
echo "  4. Commit changes:"
echo "     git add ."
echo "     git commit -m 'refactor: Root-24-LOCK compliance migration'"
echo ""
echo "=========================================================================="
echo "✅ Migration Complete"
echo "=========================================================================="
echo ""
