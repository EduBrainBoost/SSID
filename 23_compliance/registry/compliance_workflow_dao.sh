#!/bin/bash
# Compliance Registry Workflow with DAO Governance
# ==================================================
#
# Complete workflow with DAO governance integration:
# 1. Generate registry
# 2. Verify all rules
# 3. Sign with PQC
# 4. Verify signature
# 5. Create DAO proposal for lineage update
# 6. [Manual] Vote on proposal
# 7. [Manual] Tally votes and execute
#
# Usage:
#   ./compliance_workflow_dao.sh [--skip-verify] [--auto-approve]
#
# Author: SSID Compliance Team
# Version: 2.0.0
# Date: 2025-10-17

set -e  # Exit on error

# Colors (if terminal supports)
if [ -t 1 ]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    BLUE='\033[0;34m'
    NC='\033[0m' # No Color
else
    RED=''
    GREEN=''
    YELLOW=''
    BLUE=''
    NC=''
fi

# Parse arguments
SKIP_VERIFY=0
AUTO_APPROVE=0

for arg in "$@"; do
    case $arg in
        --skip-verify)
            SKIP_VERIFY=1
            shift
            ;;
        --auto-approve)
            AUTO_APPROVE=1
            shift
            ;;
        --help)
            echo "Usage: $0 [--skip-verify] [--auto-approve]"
            echo ""
            echo "Options:"
            echo "  --skip-verify   Skip rule verification (faster)"
            echo "  --auto-approve  Auto-approve proposal (for testing)"
            echo "  --help          Show this help"
            exit 0
            ;;
    esac
done

echo "================================================================================"
echo "Compliance Registry Workflow with DAO Governance"
echo "================================================================================"
echo ""

# Step 1: Generate Registry
echo "[1/7] Generating compliance registry..."
python 23_compliance/registry/generate_compliance_registry.py --pretty

if [ $? -ne 0 ]; then
    echo -e "${RED}ERROR: Registry generation failed${NC}"
    exit 1
fi

echo -e "${GREEN}[OK]${NC} Registry generated"
echo ""

# Step 2: Verify All Rules (optional)
if [ $SKIP_VERIFY -eq 0 ]; then
    echo "[2/7] Verifying all compliance rules..."
    python 23_compliance/registry/verify_compliance_realtime.py

    if [ $? -ne 0 ]; then
        echo -e "${RED}ERROR: Compliance verification failed${NC}"
        exit 1
    fi

    echo -e "${GREEN}[OK]${NC} All rules verified"
    echo ""
else
    echo "[2/7] Skipping rule verification (--skip-verify)"
    echo ""
fi

# Step 3: Sign with PQC
echo "[3/7] Signing registry with PQC..."
python 23_compliance/registry/sign_compliance_registry_pqc.py

if [ $? -ne 0 ]; then
    echo -e "${RED}ERROR: PQC signing failed${NC}"
    exit 1
fi

echo -e "${GREEN}[OK]${NC} Registry signed"
echo ""

# Step 4: Verify PQC Signature
echo "[4/7] Verifying PQC signature..."
python 23_compliance/registry/verify_pqc_signature.py --json > /dev/null

if [ $? -ne 0 ]; then
    echo -e "${RED}ERROR: Signature verification failed${NC}"
    exit 1
fi

echo -e "${GREEN}[OK]${NC} Signature verified"
echo ""

# Step 5: Create DAO Proposal
echo "[5/7] Creating DAO governance proposal..."
python 23_compliance/registry/create_lineage_proposal.py

if [ $? -ne 0 ]; then
    echo -e "${RED}ERROR: Proposal creation failed${NC}"
    exit 1
fi

echo -e "${GREEN}[OK]${NC} DAO proposal created"
echo ""

# Extract proposal ID from latest proposal
PROPOSAL_ID=$(ls -t 24_meta_orchestration/proposals/lineage-update-*.yaml 2>/dev/null | head -1 | xargs basename | sed 's/.yaml$//')

if [ -z "$PROPOSAL_ID" ]; then
    echo -e "${RED}ERROR: Could not find proposal ID${NC}"
    exit 1
fi

echo -e "${BLUE}Proposal ID: $PROPOSAL_ID${NC}"
echo ""

# Step 6: Start Voting
echo "[6/7] Starting DAO voting period..."
python 24_meta_orchestration/proposals/start_voting.py "$PROPOSAL_ID"

if [ $? -ne 0 ]; then
    echo -e "${RED}ERROR: Failed to start voting${NC}"
    exit 1
fi

echo -e "${GREEN}[OK]${NC} Voting started"
echo ""

# Auto-approve if requested (for testing)
if [ $AUTO_APPROVE -eq 1 ]; then
    echo "[7/7] Auto-approving proposal (testing mode)..."

    # Cast 3 yes votes
    python 24_meta_orchestration/proposals/cast_vote.py "$PROPOSAL_ID" --vote yes --validator validator-1
    python 24_meta_orchestration/proposals/cast_vote.py "$PROPOSAL_ID" --vote yes --validator validator-2
    python 24_meta_orchestration/proposals/cast_vote.py "$PROPOSAL_ID" --vote yes --validator validator-3

    # Tally votes and execute
    python 24_meta_orchestration/proposals/tally_votes.py "$PROPOSAL_ID" --force

    if [ $? -ne 0 ]; then
        echo -e "${RED}ERROR: Proposal execution failed${NC}"
        exit 1
    fi

    echo -e "${GREEN}[OK]${NC} Proposal approved and executed"
    echo ""
else
    echo "[7/7] Awaiting DAO votes..."
    echo ""
    echo -e "${YELLOW}MANUAL STEPS REQUIRED:${NC}"
    echo ""
    echo "  1. Cast votes:"
    echo "     python 24_meta_orchestration/proposals/cast_vote.py $PROPOSAL_ID --vote yes --validator validator-1"
    echo "     python 24_meta_orchestration/proposals/cast_vote.py $PROPOSAL_ID --vote yes --validator validator-2"
    echo "     python 24_meta_orchestration/proposals/cast_vote.py $PROPOSAL_ID --vote yes --validator validator-3"
    echo ""
    echo "  2. Tally votes and execute:"
    echo "     python 24_meta_orchestration/proposals/tally_votes.py $PROPOSAL_ID"
    echo ""
fi

# Summary
echo "================================================================================"
echo "Workflow Status"
echo "================================================================================"
echo ""
echo "Completed steps:"
echo "  [OK] Registry generated"
if [ $SKIP_VERIFY -eq 0 ]; then
    echo "  [OK] Rules verified"
fi
echo "  [OK] PQC signature created"
echo "  [OK] Signature verified"
echo "  [OK] DAO proposal created"
echo "  [OK] Voting started"

if [ $AUTO_APPROVE -eq 1 ]; then
    echo "  [OK] Proposal approved and executed"
else
    echo "  [PENDING] Awaiting DAO votes"
fi

echo ""

if [ $AUTO_APPROVE -eq 0 ]; then
    echo -e "${YELLOW}Governance process active - manual voting required${NC}"
    echo ""
    echo "Verify lineage after approval:"
    echo "  python 23_compliance/registry/verify_lineage_integrity.py --verify-signatures"
    echo ""
fi

echo "================================================================================"

exit 0
