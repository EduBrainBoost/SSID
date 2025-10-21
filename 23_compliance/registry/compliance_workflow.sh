#!/bin/bash
# Compliance Registry Workflow
# =============================
#
# Complete workflow for compliance registry management:
# 1. Generate registry
# 2. Verify all rules
# 3. Sign with PQC
# 4. Verify signature
# 5. Update lineage
# 6. Verify lineage
#
# Usage:
#   ./compliance_workflow.sh [--skip-verify] [--dry-run]
#
# Author: SSID Compliance Team
# Version: 1.0.0
# Date: 2025-10-17

set -e  # Exit on error

# Colors (if terminal supports)
if [ -t 1 ]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    NC='\033[0m' # No Color
else
    RED=''
    GREEN=''
    YELLOW=''
    NC=''
fi

# Parse arguments
SKIP_VERIFY=0
DRY_RUN=0

for arg in "$@"; do
    case $arg in
        --skip-verify)
            SKIP_VERIFY=1
            shift
            ;;
        --dry-run)
            DRY_RUN=1
            shift
            ;;
        --help)
            echo "Usage: $0 [--skip-verify] [--dry-run]"
            echo ""
            echo "Options:"
            echo "  --skip-verify  Skip rule verification (faster)"
            echo "  --dry-run      Don't modify files"
            echo "  --help         Show this help"
            exit 0
            ;;
    esac
done

echo "================================================================================"
echo "Compliance Registry Workflow"
echo "================================================================================"
echo ""

# Step 1: Generate Registry
echo "[1/6] Generating compliance registry..."
python 23_compliance/registry/generate_compliance_registry.py --pretty

if [ $? -ne 0 ]; then
    echo -e "${RED}ERROR: Registry generation failed${NC}"
    exit 1
fi

echo -e "${GREEN}[OK]${NC} Registry generated"
echo ""

# Step 2: Verify All Rules (optional)
if [ $SKIP_VERIFY -eq 0 ]; then
    echo "[2/6] Verifying all compliance rules..."
    python 23_compliance/registry/verify_compliance_realtime.py

    if [ $? -ne 0 ]; then
        echo -e "${RED}ERROR: Compliance verification failed${NC}"
        exit 1
    fi

    echo -e "${GREEN}[OK]${NC} All rules verified"
    echo ""
else
    echo "[2/6] Skipping rule verification (--skip-verify)"
    echo ""
fi

# Step 3: Sign with PQC
echo "[3/6] Signing registry with PQC..."
if [ $DRY_RUN -eq 1 ]; then
    echo -e "${YELLOW}[DRY RUN]${NC} Would sign registry"
else
    python 23_compliance/registry/sign_compliance_registry_pqc.py

    if [ $? -ne 0 ]; then
        echo -e "${RED}ERROR: PQC signing failed${NC}"
        exit 1
    fi

    echo -e "${GREEN}[OK]${NC} Registry signed"
fi
echo ""

# Step 4: Verify PQC Signature
echo "[4/6] Verifying PQC signature..."
python 23_compliance/registry/verify_pqc_signature.py --json > /dev/null

if [ $? -ne 0 ]; then
    echo -e "${RED}ERROR: Signature verification failed${NC}"
    exit 1
fi

echo -e "${GREEN}[OK]${NC} Signature verified"
echo ""

# Step 5: Update Lineage
echo "[5/6] Updating registry lineage..."
if [ $DRY_RUN -eq 1 ]; then
    python 23_compliance/registry/update_registry_lineage.py --dry-run
else
    # Check if this would be a duplicate
    python 23_compliance/registry/update_registry_lineage.py 2>&1 | grep -q "already exists"

    if [ $? -eq 0 ]; then
        echo -e "${YELLOW}WARNING:${NC} This Merkle root already exists in lineage"
        echo "This is expected if registry hasn't changed since last signature."
        echo "Skipping lineage update."
    else
        python 23_compliance/registry/update_registry_lineage.py

        if [ $? -ne 0 ]; then
            echo -e "${RED}ERROR: Lineage update failed${NC}"
            exit 1
        fi

        echo -e "${GREEN}[OK]${NC} Lineage updated"
    fi
fi
echo ""

# Step 6: Verify Lineage Integrity
echo "[6/6] Verifying lineage integrity..."
python 23_compliance/registry/verify_lineage_integrity.py --verify-signatures --json > /dev/null

if [ $? -ne 0 ]; then
    echo -e "${RED}ERROR: Lineage verification failed${NC}"
    exit 1
fi

echo -e "${GREEN}[OK]${NC} Lineage verified"
echo ""

# Summary
echo "================================================================================"
echo "Workflow Complete"
echo "================================================================================"
echo ""
echo "All steps completed successfully:"
echo "  [OK] Registry generated"
if [ $SKIP_VERIFY -eq 0 ]; then
    echo "  [OK] Rules verified"
fi
echo "  [OK] PQC signature created"
echo "  [OK] Signature verified"
if [ $DRY_RUN -eq 0 ]; then
    echo "  [OK] Lineage updated"
fi
echo "  [OK] Lineage integrity verified"
echo ""

if [ $DRY_RUN -eq 1 ]; then
    echo -e "${YELLOW}NOTE: Dry run mode - no files were modified${NC}"
    echo ""
fi

echo "Next steps:"
echo "  1. Review changes: git diff"
echo "  2. Commit: git add 23_compliance/registry/ && git commit -m \"Update compliance registry\""
echo "  3. Push: git push"
echo ""
echo "================================================================================"

exit 0
