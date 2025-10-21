#!/bin/bash
################################################################################
# SSID WORM S3 Setup - Dry Run & Verification
################################################################################
# Purpose: Simulate and verify WORM S3 setup without actual AWS execution
# Version: 1.0.0
# Date: 2025-10-18
# Owner: SSID Compliance Team
#
# Usage: ./tools/worm_s3_dry_run.sh [--execute]
#
# Modes:
#   - Default (Dry Run): Shows what would be executed
#   - --execute: Actually executes AWS commands (requires AWS access)
#
################################################################################

set -euo pipefail

# Configuration
BUCKET_NAME="${WORM_BUCKET_NAME:-ssid-worm-storage}"
AWS_REGION="${AWS_REGION:-eu-central-1}"
RETENTION_YEARS="${RETENTION_YEARS:-7}"
DRY_RUN=true

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
function log_command() { echo -e "${YELLOW}🔧 $1${NC}"; }

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --execute)
            DRY_RUN=false
            shift
            ;;
        --help|-h)
            cat <<EOF
Usage: $0 [--execute]

Dry run and verification script for WORM S3 setup.

Options:
  --execute    Actually execute AWS commands (requires AWS access)
  --help       Show this help

Without --execute, this script simulates the setup and checks prerequisites.

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
echo "🔒 SSID WORM S3 Setup - $([ "$DRY_RUN" = true ] && echo "DRY RUN" || echo "EXECUTION MODE")"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "Configuration:"
echo "  Bucket: $BUCKET_NAME"
echo "  Region: $AWS_REGION"
echo "  Retention: $RETENTION_YEARS years"
echo "  Mode: $([ "$DRY_RUN" = true ] && echo "Simulation" || echo "Live Execution")"
echo ""

# Step 1: Check Prerequisites
echo "═══════════════════════════════════════════════════════════════"
echo "📋 STEP 1: Prerequisites Check"
echo "═══════════════════════════════════════════════════════════════"
echo ""

log_info "Checking AWS CLI..."
if command -v aws &> /dev/null; then
    AWS_VERSION=$(aws --version 2>&1 | head -1)
    log_success "AWS CLI installed: $AWS_VERSION"
else
    log_error "AWS CLI not installed"
    log_info "Install: https://aws.amazon.com/cli/"
    exit 1
fi

log_info "Checking AWS credentials..."
if [ "$DRY_RUN" = false ]; then
    if aws sts get-caller-identity &> /dev/null; then
        ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
        USER_ARN=$(aws sts get-caller-identity --query Arn --output text)
        log_success "AWS credentials valid"
        log_info "  Account: $ACCOUNT_ID"
        log_info "  User: $USER_ARN"
    else
        log_error "AWS credentials not configured"
        log_info "Run: aws configure"
        exit 1
    fi
else
    log_warning "Skipping credential check (dry run mode)"
fi

log_info "Checking required tools..."
for tool in sha256sum jq; do
    if command -v $tool &> /dev/null; then
        log_success "$tool installed"
    else
        log_warning "$tool not installed (recommended)"
    fi
done

echo ""

# Step 2: Check if bucket exists
echo "═══════════════════════════════════════════════════════════════"
echo "📦 STEP 2: Bucket Status Check"
echo "═══════════════════════════════════════════════════════════════"
echo ""

if [ "$DRY_RUN" = false ]; then
    log_info "Checking if bucket exists..."
    if aws s3api head-bucket --bucket "$BUCKET_NAME" 2>/dev/null; then
        log_warning "Bucket already exists: $BUCKET_NAME"

        # Check Object Lock status
        if aws s3api get-object-lock-configuration --bucket "$BUCKET_NAME" &> /dev/null; then
            log_success "Object Lock is enabled"
            aws s3api get-object-lock-configuration --bucket "$BUCKET_NAME"
        else
            log_error "Object Lock is NOT enabled"
            log_info "Object Lock cannot be enabled on existing buckets without it"
            log_info "You must create a new bucket with Object Lock enabled"
        fi
    else
        log_info "Bucket does not exist (will be created)"
    fi
else
    log_command "aws s3api head-bucket --bucket $BUCKET_NAME"
    log_info "Would check if bucket exists"
fi

echo ""

# Step 3: Create Bucket (or simulate)
echo "═══════════════════════════════════════════════════════════════"
echo "🏗️  STEP 3: Create S3 Bucket with Object Lock"
echo "═══════════════════════════════════════════════════════════════"
echo ""

CREATE_BUCKET_CMD="aws s3api create-bucket \
  --bucket $BUCKET_NAME \
  --region $AWS_REGION \
  --create-bucket-configuration LocationConstraint=$AWS_REGION \
  --object-lock-enabled-for-bucket"

log_command "$CREATE_BUCKET_CMD"

if [ "$DRY_RUN" = false ]; then
    log_info "Creating bucket..."
    if eval "$CREATE_BUCKET_CMD"; then
        log_success "Bucket created successfully"
    else
        log_error "Failed to create bucket"
        log_info "This may fail if bucket already exists or name is taken"
    fi
else
    log_info "Would create bucket with Object Lock enabled"
fi

echo ""

# Step 4: Configure Object Lock
echo "═══════════════════════════════════════════════════════════════"
echo "🔐 STEP 4: Configure Object Lock Retention Policy"
echo "═══════════════════════════════════════════════════════════════"
echo ""

LOCK_CONFIG='{
  "ObjectLockEnabled": "Enabled",
  "Rule": {
    "DefaultRetention": {
      "Mode": "COMPLIANCE",
      "Years": '${RETENTION_YEARS}'
    }
  }
}'

PUT_LOCK_CMD="aws s3api put-object-lock-configuration \
  --bucket $BUCKET_NAME \
  --object-lock-configuration '$LOCK_CONFIG'"

log_command "$PUT_LOCK_CMD"
echo ""
echo "Object Lock Configuration:"
echo "$LOCK_CONFIG" | jq '.'
echo ""

if [ "$DRY_RUN" = false ]; then
    log_info "Configuring Object Lock..."
    echo "$LOCK_CONFIG" > /tmp/lock-config.json
    if aws s3api put-object-lock-configuration \
        --bucket "$BUCKET_NAME" \
        --object-lock-configuration file:///tmp/lock-config.json; then
        log_success "Object Lock configured"
        rm /tmp/lock-config.json
    else
        log_error "Failed to configure Object Lock"
    fi
else
    log_info "Would set $RETENTION_YEARS year COMPLIANCE retention policy"
fi

echo ""

# Step 5: Create IAM Policies
echo "═══════════════════════════════════════════════════════════════"
echo "👤 STEP 5: IAM Policy Creation"
echo "═══════════════════════════════════════════════════════════════"
echo ""

log_info "Creating IAM policy files..."

# Uploader Policy
UPLOADER_POLICY_FILE="iam_policy_worm_uploader.json"
cat > "$UPLOADER_POLICY_FILE" <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowWORMUpload",
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:PutObjectRetention",
        "s3:PutObjectLegalHold"
      ],
      "Resource": "arn:aws:s3:::${BUCKET_NAME}/*"
    },
    {
      "Sid": "AllowListBucket",
      "Effect": "Allow",
      "Action": [
        "s3:ListBucket",
        "s3:GetBucketLocation",
        "s3:GetBucketVersioning"
      ],
      "Resource": "arn:aws:s3:::${BUCKET_NAME}"
    },
    {
      "Sid": "DenyDeletion",
      "Effect": "Deny",
      "Action": [
        "s3:DeleteObject",
        "s3:DeleteObjectVersion",
        "s3:PutLifecycleConfiguration"
      ],
      "Resource": "arn:aws:s3:::${BUCKET_NAME}/*"
    }
  ]
}
EOF

log_success "Created: $UPLOADER_POLICY_FILE"

# Auditor Policy
AUDITOR_POLICY_FILE="iam_policy_worm_auditor.json"
cat > "$AUDITOR_POLICY_FILE" <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowReadOnly",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:GetObjectVersion",
        "s3:GetObjectRetention",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::${BUCKET_NAME}",
        "arn:aws:s3:::${BUCKET_NAME}/*"
      ]
    }
  ]
}
EOF

log_success "Created: $AUDITOR_POLICY_FILE"

if [ "$DRY_RUN" = false ]; then
    log_info "Creating IAM policies..."

    # Uploader
    CREATE_UPLOADER_CMD="aws iam create-policy \
      --policy-name SSID-WORM-Uploader \
      --policy-document file://$UPLOADER_POLICY_FILE"

    log_command "$CREATE_UPLOADER_CMD"
    if eval "$CREATE_UPLOADER_CMD" 2>/dev/null; then
        log_success "Uploader policy created"
    else
        log_warning "Uploader policy may already exist"
    fi

    # Auditor
    CREATE_AUDITOR_CMD="aws iam create-policy \
      --policy-name SSID-WORM-Auditor \
      --policy-document file://$AUDITOR_POLICY_FILE"

    log_command "$CREATE_AUDITOR_CMD"
    if eval "$CREATE_AUDITOR_CMD" 2>/dev/null; then
        log_success "Auditor policy created"
    else
        log_warning "Auditor policy may already exist"
    fi
else
    log_info "Would create IAM policies:"
    log_info "  - SSID-WORM-Uploader"
    log_info "  - SSID-WORM-Auditor"
fi

echo ""

# Step 6: Test Upload
echo "═══════════════════════════════════════════════════════════════"
echo "🧪 STEP 6: Test Upload & Verification"
echo "═══════════════════════════════════════════════════════════════"
echo ""

TEST_FILE="test_worm_artifact_$(date +%s).txt"
echo "SSID WORM Storage Test - $(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$TEST_FILE"
TEST_SHA256=$(sha256sum "$TEST_FILE" | awk '{print $1}')

log_info "Created test file: $TEST_FILE"
log_info "  SHA256: $TEST_SHA256"

if [ "$DRY_RUN" = false ]; then
    RETENTION_DATE=$(date -d "+${RETENTION_YEARS} years" --iso-8601=seconds | sed 's/+.*/Z/')

    log_info "Uploading test file with Object Lock..."
    log_info "  Retention until: $RETENTION_DATE"

    UPLOAD_CMD="aws s3api put-object \
      --bucket $BUCKET_NAME \
      --key test-uploads/$TEST_FILE \
      --body $TEST_FILE \
      --object-lock-mode COMPLIANCE \
      --object-lock-retain-until-date $RETENTION_DATE \
      --metadata sha256=$TEST_SHA256,uploaded=$(date -u +%Y-%m-%dT%H:%M:%SZ)"

    log_command "$UPLOAD_CMD"

    if eval "$UPLOAD_CMD"; then
        log_success "Test file uploaded successfully"

        # Verify Object Lock
        log_info "Verifying Object Lock settings..."
        aws s3api head-object \
            --bucket "$BUCKET_NAME" \
            --key "test-uploads/$TEST_FILE" | jq '{ObjectLockMode, ObjectLockRetainUntilDate, Metadata}'

        # Try to delete (should fail)
        log_info "Testing immutability (attempting delete)..."
        if aws s3api delete-object \
            --bucket "$BUCKET_NAME" \
            --key "test-uploads/$TEST_FILE" 2>&1 | grep -q "Access Denied"; then
            log_success "✅ IMMUTABILITY VERIFIED - Delete blocked!"
        else
            log_error "⚠️  WARNING - Delete succeeded! Object Lock may not be working!"
        fi
    else
        log_error "Failed to upload test file"
    fi

    rm "$TEST_FILE"
else
    log_command "aws s3api put-object --bucket $BUCKET_NAME --key test-uploads/$TEST_FILE ..."
    log_info "Would upload test file with COMPLIANCE lock"
    log_info "Would verify immutability with delete attempt"
    rm "$TEST_FILE"
fi

echo ""

# Step 7: Summary & Next Steps
echo "═══════════════════════════════════════════════════════════════"
echo "📊 SUMMARY"
echo "═══════════════════════════════════════════════════════════════"
echo ""

if [ "$DRY_RUN" = true ]; then
    log_warning "DRY RUN MODE - No actual changes made"
    echo ""
    log_info "To execute for real, run:"
    echo "  $0 --execute"
    echo ""
    log_info "Next steps:"
    echo "  1. Review IAM policy files created"
    echo "  2. Ensure AWS credentials are configured"
    echo "  3. Run with --execute flag"
    echo "  4. Attach IAM policies to appropriate users/roles"
    echo "  5. Begin archiving production artifacts"
else
    log_success "WORM S3 Setup Complete!"
    echo ""
    log_info "Verification checklist:"
    echo "  [ ] Bucket created with Object Lock"
    echo "  [ ] Default retention policy set"
    echo "  [ ] IAM policies created"
    echo "  [ ] Test file uploaded successfully"
    echo "  [ ] Immutability verified (delete blocked)"
    echo ""
    log_info "Next steps:"
    echo "  1. Attach IAM policies to users:"
    echo "     aws iam attach-user-policy --user-name USER --policy-arn arn:aws:iam::ACCOUNT:policy/SSID-WORM-Uploader"
    echo "  2. Update registry with WORM bucket info"
    echo "  3. Begin archiving production artifacts with tools/worm_blockchain_archive.sh"
    echo "  4. Set up monitoring and alerts"
fi

echo ""
echo "Documentation:"
echo "  - Setup Guide: 02_audit_logging/procedures/AWS_S3_WORM_SETUP_GUIDE.md"
echo "  - Archiving Script: tools/worm_blockchain_archive.sh"
echo ""
echo "═══════════════════════════════════════════════════════════════"
