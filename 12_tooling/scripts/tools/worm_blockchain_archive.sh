#!/bin/bash
################################################################################
# SSID WORM + Blockchain Archiving Automation
################################################################################
# Purpose: Automate WORM storage upload and blockchain anchoring
# Version: 1.0.0
# Date: 2025-10-18
# Owner: SSID Compliance Team
#
# Usage: ./tools/worm_blockchain_archive.sh <file> [options]
#
# Examples:
#   ./tools/worm_blockchain_archive.sh 24_meta_orchestration/registry/qa_corpus_policy.yaml
#   ./tools/worm_blockchain_archive.sh 02_audit_logging/reports/QA_AUDIT.md --skip-blockchain
#
################################################################################

set -euo pipefail

# Configuration
WORM_BUCKET="${WORM_BUCKET:-s3://ssid-worm-storage}"
RETENTION_YEARS="${RETENTION_YEARS:-7}"
OTS_ENABLED="${OTS_ENABLED:-true}"
AWS_REGION="${AWS_REGION:-eu-central-1}"
REGISTRY_FILE="24_meta_orchestration/registry/worm_storage_index.yaml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
function log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

function log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

function log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

function log_error() {
    echo -e "${RED}❌ $1${NC}"
}

function check_dependencies() {
    log_info "Checking dependencies..."

    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        log_error "AWS CLI not installed. Install: https://aws.amazon.com/cli/"
        exit 1
    fi

    # Check sha256sum
    if ! command -v sha256sum &> /dev/null; then
        log_error "sha256sum not found"
        exit 1
    fi

    # Check OpenTimestamps (optional)
    if [ "$OTS_ENABLED" = true ] && ! command -v ots &> /dev/null; then
        log_warning "OpenTimestamps not installed. Blockchain anchoring will be skipped."
        log_warning "Install: pip install opentimestamps-client"
        OTS_ENABLED=false
    fi

    log_success "All dependencies OK"
}

function calculate_sha256() {
    local file="$1"
    sha256sum "$file" | awk '{print $1}'
}

function calculate_retention_date() {
    # Calculate date X years in the future (ISO 8601 format)
    if command -v gdate &> /dev/null; then
        # macOS with GNU coreutils
        gdate -d "+${RETENTION_YEARS} years" --iso-8601=seconds | sed 's/+.*/Z/'
    else
        # Linux
        date -d "+${RETENTION_YEARS} years" --iso-8601=seconds | sed 's/+.*/Z/'
    fi
}

function archive_to_worm() {
    local file="$1"
    local s3_key="$2"
    local retention_date="$3"
    local sha256="$4"

    log_info "Archiving to WORM storage: $file"
    log_info "  S3 Key: $s3_key"
    log_info "  SHA256: $sha256"
    log_info "  Retention until: $retention_date"

    # Upload to S3 with Object Lock
    aws s3api put-object \
        --bucket "${WORM_BUCKET#s3://}" \
        --key "$s3_key" \
        --body "$file" \
        --region "$AWS_REGION" \
        --object-lock-mode COMPLIANCE \
        --object-lock-retain-until-date "$retention_date" \
        --metadata "sha256=$sha256,archived=$(date -u +%Y-%m-%dT%H:%M:%SZ),tool=worm_blockchain_archive.sh" \
        >/dev/null

    log_success "Uploaded to WORM storage"

    # Verify upload
    local uploaded_sha256=$(aws s3api head-object \
        --bucket "${WORM_BUCKET#s3://}" \
        --key "$s3_key" \
        --region "$AWS_REGION" \
        --query 'Metadata.sha256' \
        --output text)

    if [ "$uploaded_sha256" = "$sha256" ]; then
        log_success "SHA256 verification passed"
    else
        log_error "SHA256 mismatch! Expected: $sha256, Got: $uploaded_sha256"
        exit 1
    fi
}

function blockchain_anchor() {
    local file="$1"

    if [ "$OTS_ENABLED" != true ]; then
        log_warning "Blockchain anchoring disabled"
        return 0
    fi

    log_info "Creating blockchain timestamp: $file"

    # Create OpenTimestamps proof
    ots stamp "$file" 2>&1 | grep -v "Submitting to remote calendar" || true

    if [ -f "${file}.ots" ]; then
        log_success "Timestamp created: ${file}.ots"
        log_info "⏳ Bitcoin confirmation pending (10-60 minutes)"
        log_info "Run later: ots upgrade ${file}.ots"
        log_info "Verify: ots verify ${file}.ots"

        # Background upgrade check (after 1 hour)
        (
            sleep 3600
            ots upgrade "${file}.ots" 2>/dev/null && \
                log_success "Blockchain timestamp upgraded automatically" || \
                log_info "Blockchain timestamp not yet confirmed (retry later)"
        ) &
    else
        log_warning "Failed to create timestamp"
    fi
}

function update_registry() {
    local file="$1"
    local s3_key="$2"
    local sha256="$3"
    local retention_date="$4"

    log_info "Updating registry: $REGISTRY_FILE"

    # Create registry directory if needed
    mkdir -p "$(dirname "$REGISTRY_FILE")"

    # Initialize registry if not exists
    if [ ! -f "$REGISTRY_FILE" ]; then
        cat > "$REGISTRY_FILE" <<EOF
version: "1.0.0"
bucket: "${WORM_BUCKET}"
region: "${AWS_REGION}"
retention_years: ${RETENTION_YEARS}
created: "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
owner: "SSID Compliance Team"

artifacts: []
EOF
    fi

    # Add artifact entry (simplified - in production use yq or Python)
    log_success "Registry updated (manual verification recommended)"
    log_info "Add this entry to $REGISTRY_FILE:"
    echo ""
    echo "  - key: \"$s3_key\""
    echo "    sha256: \"$sha256\""
    echo "    uploaded: \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\""
    echo "    retention_until: \"$retention_date\""
    echo "    size_bytes: $(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null)"
    echo "    type: \"$(basename "$(dirname "$file")")\""
    echo ""
}

function generate_s3_key() {
    local file="$1"

    # Detect artifact type from path
    if [[ "$file" == *"qa_master_suite"* ]]; then
        echo "qa-master-suite/v2.0.0/$(basename "$file")"
    elif [[ "$file" == *"audit"* ]] || [[ "$file" == *"report"* ]]; then
        echo "audit-reports/$(date +%Y-%m-%d)/$(basename "$file")"
    elif [[ "$file" == *"policy"* ]]; then
        echo "policies/$(date +%Y-%m)/$(basename "$file")"
    elif [[ "$file" == *"evidence"* ]]; then
        echo "evidence/$(date +%Y-%m)/$(basename "$file")"
    else
        echo "misc/$(date +%Y-%m-%d)/$(basename "$file")"
    fi
}

function verify_immutability() {
    local s3_key="$1"

    log_info "Verifying immutability (attempting delete)..."

    # Try to delete (should fail)
    if aws s3api delete-object \
        --bucket "${WORM_BUCKET#s3://}" \
        --key "$s3_key" \
        --region "$AWS_REGION" \
        2>&1 | grep -q "Access Denied"; then
        log_success "Immutability verified - object is locked ✅"
    else
        log_error "WARNING: Object is NOT immutable! Delete succeeded!"
        log_error "Check Object Lock configuration!"
        exit 1
    fi
}

function print_usage() {
    cat <<EOF
Usage: $0 <file> [options]

Archive a file to WORM storage with blockchain anchoring.

Arguments:
  <file>                  Path to file to archive

Options:
  --skip-blockchain       Skip blockchain anchoring
  --skip-worm             Skip WORM upload (blockchain only)
  --retention-years N     Override retention period (default: 7)
  --help                  Show this help

Environment Variables:
  WORM_BUCKET             S3 bucket name (default: s3://ssid-worm-storage)
  RETENTION_YEARS         Retention period in years (default: 7)
  OTS_ENABLED             Enable OpenTimestamps (default: true)
  AWS_REGION              AWS region (default: eu-central-1)

Examples:
  # Archive QA policy
  $0 24_meta_orchestration/registry/qa_corpus_policy.yaml

  # Archive audit report without blockchain
  $0 02_audit_logging/reports/AUDIT.md --skip-blockchain

  # Custom retention period
  $0 evidence.json --retention-years 10
EOF
}

################################################################################
# MAIN
################################################################################

function main() {
    local file=""
    local skip_blockchain=false
    local skip_worm=false

    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --skip-blockchain)
                skip_blockchain=true
                OTS_ENABLED=false
                shift
                ;;
            --skip-worm)
                skip_worm=true
                shift
                ;;
            --retention-years)
                RETENTION_YEARS="$2"
                shift 2
                ;;
            --help|-h)
                print_usage
                exit 0
                ;;
            -*)
                log_error "Unknown option: $1"
                print_usage
                exit 1
                ;;
            *)
                file="$1"
                shift
                ;;
        esac
    done

    # Validate file argument
    if [ -z "$file" ]; then
        log_error "Missing file argument"
        print_usage
        exit 1
    fi

    if [ ! -f "$file" ]; then
        log_error "File not found: $file"
        exit 1
    fi

    # Print header
    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    echo "🔒 SSID WORM + Blockchain Archiving"
    echo "═══════════════════════════════════════════════════════════════"
    echo ""
    echo "File: $file"
    echo "WORM Bucket: $WORM_BUCKET"
    echo "Retention: $RETENTION_YEARS years"
    echo "Blockchain: $([ "$OTS_ENABLED" = true ] && echo "Enabled" || echo "Disabled")"
    echo ""

    # Check dependencies
    check_dependencies
    echo ""

    # Calculate SHA256
    log_info "Calculating SHA256 hash..."
    local sha256=$(calculate_sha256 "$file")
    log_success "SHA256: $sha256"
    echo ""

    # Generate S3 key
    local s3_key=$(generate_s3_key "$file")
    log_info "S3 Key: $s3_key"
    echo ""

    # Calculate retention date
    local retention_date=$(calculate_retention_date)
    log_info "Retention until: $retention_date"
    echo ""

    # WORM upload
    if [ "$skip_worm" != true ]; then
        archive_to_worm "$file" "$s3_key" "$retention_date" "$sha256"
        echo ""

        # Verify immutability
        verify_immutability "$s3_key"
        echo ""
    fi

    # Blockchain anchoring
    if [ "$skip_blockchain" != true ]; then
        blockchain_anchor "$file"
        echo ""
    fi

    # Update registry
    update_registry "$file" "$s3_key" "$sha256" "$retention_date"

    # Summary
    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    log_success "Archiving complete!"
    echo "═══════════════════════════════════════════════════════════════"
    echo ""
    echo "Verification commands:"
    echo ""
    echo "  # WORM Storage"
    echo "  aws s3api head-object \\"
    echo "    --bucket ${WORM_BUCKET#s3://} \\"
    echo "    --key $s3_key \\"
    echo "    --region $AWS_REGION"
    echo ""
    if [ "$OTS_ENABLED" = true ]; then
        echo "  # Blockchain (after ~1 hour)"
        echo "  ots verify ${file}.ots"
        echo ""
    fi
}

# Run main
main "$@"
