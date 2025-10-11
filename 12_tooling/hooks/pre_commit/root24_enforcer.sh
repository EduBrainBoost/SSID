#!/bin/bash
# Root-24-LOCK Enforcement Hook
# Prevents commits that violate the canonical 24-root structure
# Version: 1.0.0
# SoT: SSID_structure_level3_part1_MAX.md

set -e

echo "🔒 Root-24-LOCK Enforcement..."

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
cd "$REPO_ROOT"

# Expected 24 root modules
EXPECTED_ROOTS=(
  "01_ai_layer"
  "02_audit_logging"
  "03_core"
  "04_deployment"
  "05_documentation"
  "06_data_pipeline"
  "07_governance_legal"
  "08_identity_score"
  "09_meta_identity"
  "10_interoperability"
  "11_test_simulation"
  "12_tooling"
  "13_ui_layer"
  "14_zero_time_auth"
  "15_infra"
  "16_codex"
  "17_observability"
  "18_data_layer"
  "19_adapters"
  "20_foundation"
  "21_post_quantum_crypto"
  "22_datasets"
  "23_compliance"
  "24_meta_orchestration"
)

# Allowed exceptions (from root_level_exceptions.yaml)
ALLOWED_DIRS=(
  ".git"
  ".github"
  ".githooks"
  ".venv"
  ".continue"
  ".pytest_cache"
  ".claude"
)

ALLOWED_FILES=(
  ".gitattributes"
  ".gitignore"
  ".gitmodules"
  ".pre-commit-config.yaml"
  "LICENSE"
  "README.md"
  "pytest.ini"
)

# Scan root directory
violations=0

# Check for unauthorized directories
for item in $(ls -A1); do
  # Skip if it's an expected root
  is_expected_root=false
  for root in "${EXPECTED_ROOTS[@]}"; do
    if [ "$item" == "$root" ]; then
      is_expected_root=true
      break
    fi
  done
  [ "$is_expected_root" == true ] && continue

  # Skip if it's an allowed directory
  if [ -d "$item" ]; then
    is_allowed=false
    for allowed in "${ALLOWED_DIRS[@]}"; do
      if [ "$item" == "$allowed" ]; then
        is_allowed=true
        break
      fi
    done
    [ "$is_allowed" == true ] && continue

    echo "❌ VIOLATION: Unauthorized directory at root: $item"
    violations=$((violations + 1))
  fi

  # Skip if it's an allowed file
  if [ -f "$item" ]; then
    is_allowed=false
    for allowed in "${ALLOWED_FILES[@]}"; do
      if [ "$item" == "$allowed" ]; then
        is_allowed=true
        break
      fi
    done
    [ "$is_allowed" == true ] && continue

    echo "❌ VIOLATION: Unauthorized file at root: $item"
    violations=$((violations + 1))
  fi
done

# Verify all 24 roots exist
missing_roots=0
for root in "${EXPECTED_ROOTS[@]}"; do
  if [ ! -d "$root" ]; then
    echo "❌ VIOLATION: Missing required root: $root"
    missing_roots=$((missing_roots + 1))
    violations=$((violations + 1))
  fi
done

# Report results
if [ $violations -eq 0 ]; then
  echo "✅ Root-24-LOCK: COMPLIANT (24 roots verified)"
  exit 0
else
  echo ""
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "❌ Root-24-LOCK VIOLATION DETECTED"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  echo "Total violations: $violations"
  echo ""
  echo "The repository root must contain EXACTLY:"
  echo "  - 24 module directories (01_ai_layer through 24_meta_orchestration)"
  echo "  - Allowed files: ${ALLOWED_FILES[*]}"
  echo "  - Allowed hidden dirs: ${ALLOWED_DIRS[*]}"
  echo ""
  echo "Please resolve violations before committing."
  echo "See: 23_compliance/exceptions/root_level_exceptions.yaml"
  echo ""
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  exit 1
fi
