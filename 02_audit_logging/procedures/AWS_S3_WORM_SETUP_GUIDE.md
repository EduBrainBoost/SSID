# AWS S3 WORM Storage - Setup Guide

**Version:** 1.0.0
**Datum:** 2025-10-18
**Owner:** SSID Compliance Team
**Status:** READY FOR IMPLEMENTATION
**Deadline:** 2025-11-08

---

## Executive Summary

This guide provides step-by-step instructions to set up AWS S3 WORM (Write-Once-Read-Many) storage for SSID audit artifacts with Object Lock compliance mode.

**Timeline:** 1-2 hours
**Cost:** ~$20/year for 853MB QA Archive
**Compliance:** SOC 2, ISO 27001, SEC 17a-4

---

## Prerequisites

### 1. AWS Account Requirements

- [ ] AWS Account with administrative access
- [ ] AWS CLI installed and configured
- [ ] IAM permissions to create S3 buckets and policies
- [ ] Budget approval for storage costs

**Verify AWS CLI:**
```bash
aws --version
# Should show: aws-cli/2.x.x or higher

aws sts get-caller-identity
# Should show your AWS account ID
```

### 2. Cost Estimation

| Component | Size | Cost/Month | Cost/Year |
|-----------|------|------------|-----------|
| QA Master Suite (853MB) | 853 MB | $0.02 | $0.24 |
| Audit Reports (~100 MB/year) | 100 MB | $0.002 | $0.024 |
| Evidence & Logs (~500 MB) | 500 MB | $0.01 | $0.12 |
| **TOTAL** | ~1.5 GB | **$0.03** | **$0.40** |

**Note:** Actual costs may vary based on region and data transfer.

---

## Step 1: Create S3 Bucket with Object Lock

### 1.1 Create Bucket

```bash
# Set variables
export BUCKET_NAME="ssid-worm-storage"
export AWS_REGION="eu-central-1"  # Frankfurt (GDPR-compliant)
export RETENTION_YEARS=7

# Create bucket with Object Lock enabled
aws s3api create-bucket \
  --bucket ${BUCKET_NAME} \
  --region ${AWS_REGION} \
  --create-bucket-configuration LocationConstraint=${AWS_REGION} \
  --object-lock-enabled-for-bucket

# Verify bucket creation
aws s3api get-bucket-versioning --bucket ${BUCKET_NAME}
# Should show: "Status": "Enabled"
```

### 1.2 Configure Object Lock Retention Policy

```bash
# Set default retention to 7 years (COMPLIANCE mode)
aws s3api put-object-lock-configuration \
  --bucket ${BUCKET_NAME} \
  --object-lock-configuration '{
    "ObjectLockEnabled": "Enabled",
    "Rule": {
      "DefaultRetention": {
        "Mode": "COMPLIANCE",
        "Years": '${RETENTION_YEARS}'
      }
    }
  }'

# Verify configuration
aws s3api get-object-lock-configuration --bucket ${BUCKET_NAME}
```

**Expected Output:**
```json
{
  "ObjectLockConfiguration": {
    "ObjectLockEnabled": "Enabled",
    "Rule": {
      "DefaultRetention": {
        "Mode": "COMPLIANCE",
        "Years": 7
      }
    }
  }
}
```

---

## Step 2: Configure IAM Policies

### 2.1 Create IAM Policy for WORM Uploads

Create file: `iam_policy_worm_uploader.json`

```json
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
      "Resource": "arn:aws:s3:::ssid-worm-storage/*"
    },
    {
      "Sid": "AllowListBucket",
      "Effect": "Allow",
      "Action": [
        "s3:ListBucket",
        "s3:GetBucketLocation",
        "s3:GetBucketVersioning"
      ],
      "Resource": "arn:aws:s3:::ssid-worm-storage"
    },
    {
      "Sid": "DenyDeletion",
      "Effect": "Deny",
      "Action": [
        "s3:DeleteObject",
        "s3:DeleteObjectVersion",
        "s3:PutLifecycleConfiguration"
      ],
      "Resource": "arn:aws:s3:::ssid-worm-storage/*"
    }
  ]
}
```

**Apply IAM Policy:**
```bash
aws iam create-policy \
  --policy-name SSID-WORM-Uploader \
  --policy-document file://iam_policy_worm_uploader.json

# Attach to compliance team user/role
aws iam attach-user-policy \
  --user-name compliance-team \
  --policy-arn arn:aws:iam::ACCOUNT_ID:policy/SSID-WORM-Uploader
```

### 2.2 Create IAM Policy for Read-Only Auditors

Create file: `iam_policy_worm_auditor.json`

```json
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
        "arn:aws:s3:::ssid-worm-storage",
        "arn:aws:s3:::ssid-worm-storage/*"
      ]
    }
  ]
}
```

**Apply:**
```bash
aws iam create-policy \
  --policy-name SSID-WORM-Auditor \
  --policy-document file://iam_policy_worm_auditor.json
```

---

## Step 3: Initial Test Upload

### 3.1 Create Test File

```bash
# Create test file
echo "SSID WORM Storage Test - $(date)" > test_worm_artifact.txt

# Calculate SHA256
sha256sum test_worm_artifact.txt > test_worm_artifact.txt.sha256
```

### 3.2 Upload with Object Lock

```bash
# Calculate retention date (7 years from now)
RETENTION_DATE=$(date -d "+7 years" --iso-8601=seconds | sed 's/+.*/Z/')

# Upload with COMPLIANCE mode
aws s3api put-object \
  --bucket ${BUCKET_NAME} \
  --key test-uploads/test_worm_artifact.txt \
  --body test_worm_artifact.txt \
  --object-lock-mode COMPLIANCE \
  --object-lock-retain-until-date ${RETENTION_DATE} \
  --metadata "sha256=$(cat test_worm_artifact.txt.sha256 | awk '{print $1}'),uploaded=$(date -u +%Y-%m-%dT%H:%M:%SZ)"

echo "✅ Test file uploaded successfully"
```

### 3.3 Verify Immutability

```bash
# 1. Verify Object Lock settings
aws s3api head-object \
  --bucket ${BUCKET_NAME} \
  --key test-uploads/test_worm_artifact.txt

# Should show:
#   "ObjectLockMode": "COMPLIANCE"
#   "ObjectLockRetainUntilDate": "2032-10-18T..."

# 2. Try to delete (should fail!)
aws s3api delete-object \
  --bucket ${BUCKET_NAME} \
  --key test-uploads/test_worm_artifact.txt

# Expected error:
# An error occurred (AccessDenied) when calling the DeleteObject operation:
# Access Denied
```

**If deletion succeeds, Object Lock is NOT properly configured! ⚠️**

---

## Step 4: Upload Real Artifacts

### 4.1 QA Master Suite Policy

```bash
# 1. Calculate retention date
RETENTION_DATE=$(date -d "+7 years" --iso-8601=seconds | sed 's/+.*/Z/')

# 2. Calculate SHA256
sha256sum 02_audit_logging/archives/qa_master_suite/README.md

# 3. Upload
aws s3api put-object \
  --bucket ${BUCKET_NAME} \
  --key qa-master-suite/v2.0.0/README.md \
  --body 02_audit_logging/archives/qa_master_suite/README.md \
  --object-lock-mode COMPLIANCE \
  --object-lock-retain-until-date ${RETENTION_DATE} \
  --metadata "version=2.0.0,archived=$(date -u +%Y-%m-%dT%H:%M:%SZ)"

echo "✅ QA Master Suite README archived"
```

### 4.2 Audit Report

```bash
# Find latest audit report
AUDIT_REPORT=$(ls -t 02_audit_logging/reports/QA_MASTER_SUITE_*.md | head -1)

aws s3api put-object \
  --bucket ${BUCKET_NAME} \
  --key audit-reports/$(date +%Y-%m-%d)/$(basename ${AUDIT_REPORT}) \
  --body ${AUDIT_REPORT} \
  --object-lock-mode COMPLIANCE \
  --object-lock-retain-until-date ${RETENTION_DATE}

echo "✅ Audit Report archived: ${AUDIT_REPORT}"
```

### 4.3 SHA256 Hashes

```bash
aws s3api put-object \
  --bucket ${BUCKET_NAME} \
  --key qa-master-suite/v2.0.0/qa_master_suite_hashes.json \
  --body 02_audit_logging/archives/qa_master_suite/qa_master_suite_hashes.json \
  --object-lock-mode COMPLIANCE \
  --object-lock-retain-until-date ${RETENTION_DATE}

echo "✅ SHA256 hashes archived"
```

---

## Step 5: Update Registry

### 5.1 Create WORM Storage Index

Create file: `24_meta_orchestration/registry/worm_storage_index.yaml`

```yaml
version: "1.0.0"
bucket: "ssid-worm-storage"
region: "eu-central-1"
retention_years: 7
created: "2025-10-18T00:00:00Z"
owner: "SSID Compliance Team"

artifacts:
  - key: "qa-master-suite/v2.0.0/README.md"
    sha256: "<calculated_hash>"
    uploaded: "2025-10-18T16:30:00Z"
    retention_until: "2032-10-18T16:30:00Z"
    size_bytes: 4321
    type: "qa_policy"

  - key: "audit-reports/2025-10-18/QA_MASTER_SUITE_COMPLIANCE_AUDIT.md"
    sha256: "<calculated_hash>"
    uploaded: "2025-10-18T16:31:00Z"
    retention_until: "2032-10-18T16:31:00Z"
    size_bytes: 12345
    type: "audit_report"

  - key: "qa-master-suite/v2.0.0/qa_master_suite_hashes.json"
    sha256: "<calculated_hash>"
    uploaded: "2025-10-18T16:32:00Z"
    retention_until: "2032-10-18T16:32:00Z"
    size_bytes: 1234
    type: "integrity_hashes"
```

---

## Step 6: Monitoring & Alerts

### 6.1 Enable S3 Event Notifications

```bash
# Create SNS topic for alerts
aws sns create-topic --name ssid-worm-storage-alerts

# Subscribe compliance team
aws sns subscribe \
  --topic-arn arn:aws:sns:${AWS_REGION}:ACCOUNT_ID:ssid-worm-storage-alerts \
  --protocol email \
  --notification-endpoint compliance@ssid-project.internal

# Configure S3 notifications
aws s3api put-bucket-notification-configuration \
  --bucket ${BUCKET_NAME} \
  --notification-configuration '{
    "TopicConfigurations": [
      {
        "TopicArn": "arn:aws:sns:'${AWS_REGION}':ACCOUNT_ID:ssid-worm-storage-alerts",
        "Events": ["s3:ObjectCreated:*", "s3:ObjectRemoved:*"]
      }
    ]
  }'
```

### 6.2 CloudWatch Alarms

```bash
# Monitor failed delete attempts (should be > 0 for WORM)
aws cloudwatch put-metric-alarm \
  --alarm-name ssid-worm-delete-attempts \
  --alarm-description "Alert on WORM delete attempts" \
  --metric-name 4xxErrors \
  --namespace AWS/S3 \
  --statistic Sum \
  --period 3600 \
  --evaluation-periods 1 \
  --threshold 1 \
  --comparison-operator GreaterThanThreshold \
  --dimensions Name=BucketName,Value=${BUCKET_NAME}
```

---

## Step 7: Documentation & Handoff

### 7.1 Create SOP (Standard Operating Procedure)

File: `02_audit_logging/procedures/SOP_WORM_UPLOAD.md`

**Content:**
- Who can upload to WORM storage
- Approval process for uploads
- Naming conventions
- Metadata requirements
- Verification steps

### 7.2 Team Training

- [ ] Schedule training session (30 min)
- [ ] Demo upload process
- [ ] Demo verification process
- [ ] Review incident response procedures

---

## Verification Checklist

Before marking this task as complete, verify:

- [ ] S3 bucket created with Object Lock enabled
- [ ] Default retention policy set to 7 years COMPLIANCE mode
- [ ] IAM policies created and attached
- [ ] Test file uploaded successfully
- [ ] Test file deletion fails with Access Denied
- [ ] QA Master Suite artifacts uploaded
- [ ] Audit reports uploaded
- [ ] SHA256 hashes uploaded
- [ ] WORM storage index created in registry
- [ ] SNS alerts configured
- [ ] CloudWatch alarms set up
- [ ] Team trained on procedures

---

## Troubleshooting

### Issue: Delete succeeds (Object Lock not working)

**Solution:**
```bash
# Check if Object Lock is enabled on bucket
aws s3api get-object-lock-configuration --bucket ${BUCKET_NAME}

# If not enabled, recreate bucket (Object Lock cannot be enabled post-creation)
# OR create new bucket and migrate
```

### Issue: Access Denied when uploading

**Solution:**
```bash
# Verify IAM permissions
aws iam get-user-policy --user-name compliance-team --policy-name SSID-WORM-Uploader

# Ensure user has s3:PutObject and s3:PutObjectRetention
```

### Issue: Retention date in the past

**Solution:**
```bash
# Recalculate retention date
RETENTION_DATE=$(date -d "+7 years" --iso-8601=seconds | sed 's/+.*/Z/')
echo $RETENTION_DATE  # Should be 2032-XX-XX
```

---

## Next Steps

After completing this setup:

1. **Blockchain Anchoring:** Proceed to OpenTimestamps setup
2. **Automation:** Implement `tools/worm_blockchain_archive.sh`
3. **CI/CD Integration:** Add WORM upload to GitHub Actions
4. **Quarterly Review:** Schedule first review for 2026-01-18

---

## Success Metrics

- ✅ WORM storage operational
- ✅ All critical artifacts archived
- ✅ Immutability verified (delete fails)
- ✅ Team trained
- ✅ Monitoring active
- ✅ Cost within budget (<$1/month)

---

## Kontakt & Support

**AWS WORM Owner:** SSID Compliance Team
**Lead:** bibel
**Email:** compliance@ssid-project.internal
**AWS Account ID:** `<to be filled>`
**Bucket ARN:** `arn:aws:s3:::ssid-worm-storage`

---

**END OF SETUP GUIDE**

*Status: READY FOR IMPLEMENTATION*
*Classification: INTERNAL USE ONLY*
*Last Updated: 2025-10-18*
