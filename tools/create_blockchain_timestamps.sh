#!/bin/bash
################################################################################
# SSID Blockchain Timestamp Creation - Batch Script
################################################################################
# Purpose: Create blockchain timestamps for critical artifacts
# Version: 1.0.0
# Date: 2025-10-18
# Owner: SSID Compliance Team
#
# Usage: ./tools/create_blockchain_timestamps.sh [--auto-upgrade]
#
################################################################################

set -euo pipefail

# Configuration
REGISTRY_FILE="24_meta_orchestration/registry/blockchain_anchor_registry.yaml"
AUTO_UPGRADE=false

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

function log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
function log_success() { echo -e "${GREEN}✅ $1${NC}"; }
function log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
function log_error() { echo -e "${RED}❌ $1${NC}"; }

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --auto-upgrade)
            AUTO_UPGRADE=true
            shift
            ;;
        --help|-h)
            cat <<EOF
Usage: $0 [--auto-upgrade]

Create blockchain timestamps for critical SSID artifacts.

Options:
  --auto-upgrade    Automatically upgrade timestamps after 1 hour
  --help            Show this help

Critical artifacts timestamped:
  - QA Policy (qa_master_suite/README.md)
  - Audit Reports
  - SHA256 Manifests
  - Enforcement Policies

EOF
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "⛓️  SSID Blockchain Timestamp Creation"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Check OpenTimestamps
log_info "Checking OpenTimestamps installation..."
if ! command -v ots &> /dev/null; then
    log_error "OpenTimestamps not installed"
    log_info "Install with: pip install opentimestamps-client"
    echo ""
    log_info "Alternative installation methods:"
    echo "  - Docker: docker pull btccom/opentimestamps-client"
    echo "  - Binary: https://github.com/opentimestamps/opentimestamps-client/releases"
    exit 1
fi

OTS_VERSION=$(ots --version 2>&1 || echo "unknown")
log_success "OpenTimestamps installed: $OTS_VERSION"
echo ""

# Define critical artifacts to timestamp
declare -a ARTIFACTS=(
    "02_audit_logging/archives/qa_master_suite/README.md"
    "02_audit_logging/archives/qa_master_suite/qa_master_suite_hashes.json"
    "23_compliance/policies/qa/qa_policy_enforcer.rego"
    ".git/hooks/pre-commit"
)

log_info "Critical artifacts to timestamp: ${#ARTIFACTS[@]}"
echo ""

# Initialize registry if needed
if [ ! -f "$REGISTRY_FILE" ]; then
    log_info "Creating blockchain anchor registry..."
    mkdir -p "$(dirname "$REGISTRY_FILE")"

    cat > "$REGISTRY_FILE" <<'EOF'
version: "1.0.0"
created: "TIMESTAMP_PLACEHOLDER"
owner: "SSID Compliance Team"
description: "Blockchain-anchored timestamps for audit artifacts"

anchors: []
EOF

    # Update timestamp
    CREATED_TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)
    sed -i "s/TIMESTAMP_PLACEHOLDER/$CREATED_TS/" "$REGISTRY_FILE"

    log_success "Registry created: $REGISTRY_FILE"
fi

# Process each artifact
TIMESTAMP_COUNT=0
SKIPPED_COUNT=0

for artifact in "${ARTIFACTS[@]}"; do
    echo "───────────────────────────────────────────────────────────────"
    log_info "Processing: $artifact"

    if [ ! -f "$artifact" ]; then
        log_warning "File not found - skipping"
        ((SKIPPED_COUNT++))
        continue
    fi

    # Check if already timestamped
    if [ -f "${artifact}.ots" ]; then
        log_warning "Timestamp already exists: ${artifact}.ots"

        # Try to verify
        log_info "Verifying existing timestamp..."
        if ots verify "${artifact}.ots" 2>&1 | grep -q "Success"; then
            log_success "Timestamp verified successfully"
            ots verify "${artifact}.ots" | grep -E "(Success|Bitcoin block)" || true
        else
            log_info "Timestamp pending Bitcoin confirmation"
            log_info "Run: ots upgrade ${artifact}.ots"
        fi

        ((SKIPPED_COUNT++))
        continue
    fi

    # Calculate SHA256
    SHA256=$(sha256sum "$artifact" | awk '{print $1}')
    SIZE=$(stat -c%s "$artifact" 2>/dev/null || stat -f%z "$artifact" 2>/dev/null)

    log_info "  SHA256: $SHA256"
    log_info "  Size: $SIZE bytes"

    # Create timestamp
    log_info "Creating blockchain timestamp..."

    if ots stamp "$artifact" 2>&1 | tee /tmp/ots_output.txt; then
        log_success "Timestamp created: ${artifact}.ots"

        # Show calendar servers used
        grep "Submitting to" /tmp/ots_output.txt | while read -r line; do
            log_info "  $line"
        done

        ((TIMESTAMP_COUNT++))

        # Add to registry
        log_info "Adding to registry..."
        # Note: This is simplified - in production use yq or Python
        cat >> "$REGISTRY_FILE" <<EOF

  - artifact: "$artifact"
    sha256: "$SHA256"
    size_bytes: $SIZE
    ots_file: "${artifact}.ots"
    created: "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    bitcoin_block: null
    verification_status: "pending"
    verified_at: null
EOF

        log_success "Added to registry"

        # Schedule auto-upgrade if requested
        if [ "$AUTO_UPGRADE" = true ]; then
            log_info "Scheduling auto-upgrade in 1 hour..."
            {
                sleep 3600
                log_info "Auto-upgrading: ${artifact}.ots"
                if ots upgrade "${artifact}.ots" 2>/dev/null; then
                    log_success "Timestamp upgraded successfully"

                    # Verify
                    if ots verify "${artifact}.ots" 2>&1 | grep -q "Success"; then
                        BLOCK=$(ots verify "${artifact}.ots" 2>&1 | grep -oP 'block \K[0-9]+' | head -1)
                        log_success "Bitcoin confirmation: Block $BLOCK"

                        # Update registry (simplified)
                        log_info "Registry update: Set bitcoin_block=$BLOCK for $artifact"
                    fi
                else
                    log_info "Upgrade failed - Bitcoin confirmation not yet available"
                fi
            } &
        fi

    else
        log_error "Failed to create timestamp"
        ((SKIPPED_COUNT++))
    fi

    echo ""
done

rm -f /tmp/ots_output.txt

# Summary
echo "═══════════════════════════════════════════════════════════════"
echo "📊 SUMMARY"
echo "═══════════════════════════════════════════════════════════════"
echo ""
log_success "Timestamps created: $TIMESTAMP_COUNT"
log_info "Skipped (already timestamped): $SKIPPED_COUNT"
echo ""

if [ $TIMESTAMP_COUNT -gt 0 ]; then
    log_info "Next steps:"
    echo "  1. Commit .ots files to Git:"
    echo "     git add **/*.ots"
    echo "     git commit -m \"chore: Add blockchain timestamps for QA artifacts\""
    echo ""
    echo "  2. Wait ~10-60 minutes for Bitcoin confirmation"
    echo ""
    echo "  3. Upgrade timestamps:"
    echo "     ots upgrade 02_audit_logging/archives/qa_master_suite/README.md.ots"
    echo ""
    echo "  4. Verify timestamps:"
    echo "     ots verify 02_audit_logging/archives/qa_master_suite/README.md.ots"
    echo ""
    echo "  5. Update registry with Bitcoin block numbers"
fi

if [ "$AUTO_UPGRADE" = true ]; then
    log_info "Auto-upgrade tasks running in background (check logs in 1 hour)"
fi

echo ""
log_info "Registry: $REGISTRY_FILE"
log_info "Documentation: 02_audit_logging/procedures/OPENTIMESTAMPS_SETUP_GUIDE.md"
echo ""
echo "═══════════════════════════════════════════════════════════════"
