# SSID Quarterly Governance Release Bundles

**Blueprint v4.2.0 - Automated Release Packaging System**

## Overview

This directory contains quarterly governance release bundles for the SSID project. Each bundle is a comprehensive, tamper-proof archive of all governance artifacts for a specific quarter.

## Release Bundle Structure

Each quarterly release bundle includes:

### Core Governance Documents
- `COMPLIANCE_REPORT.md` - Quarterly compliance audit report
- `SSID_Governance_Dashboard.md` - Real-time governance dashboard
- `README.md` - Repository overview and status

### Registry & Manifests
- `registry_events.log` - Complete event log with proof-anchors
- `integrity_checksums.json` - File integrity checksums (if available)
- `dashboard_manifest.json` - Dashboard metadata

### Governance Rules
- `branch_protection_rules.yaml` - Branch protection configuration
- `promotion_rules.yaml` - Blueprint promotion workflows
- `OPERATIONS_GUIDE.md` - Operational procedures

## Release Naming Convention

Bundles are named: `SSID_Quarterly_Release_YYYY-QX.zip`

Examples:
- `SSID_Quarterly_Release_2026-Q1.zip`
- `SSID_Quarterly_Release_2026-Q2.zip`
- `SSID_Quarterly_Release_2026-Q3.zip`
- `SSID_Quarterly_Release_2026-Q4.zip`

## Verification

Each bundle has a SHA256 hash for integrity verification:

```bash
# Verify bundle integrity
sha256sum SSID_Quarterly_Release_2026-Q1.zip

# Compare with hash from manifest
cat ../../../24_meta_orchestration/registry/manifests/quarterly_release_manifest_2026-Q1.json | grep '"hash"'
```

## Automated Generation

Release bundles are generated automatically:

### Quarterly Audit Integration
When running a quarterly audit, the release bundle is automatically created:

```bash
bash 12_tooling/scripts/run_quarterly_audit.sh
# Automatically generates:
# 1. Compliance report
# 2. Updated dashboard
# 3. Release bundle with all artifacts
```

### Manual Generation
You can also create a release bundle manually:

```bash
# Create bundle for current quarter
python3 12_tooling/scripts/create_quarterly_release_bundle.py

# Create bundle and publish to GitHub Releases
python3 12_tooling/scripts/create_quarterly_release_bundle.py --publish
```

### GitHub Actions Automation
Release bundles are also created automatically via GitHub Actions:

- **Schedule:** 1st of Jan/Apr/Jul/Oct at 09:00 UTC (1 hour after quarterly audit)
- **Workflow:** `.github/workflows/quarterly_release.yml`
- **Manual Trigger:** Available via GitHub Actions UI

## Release Artifacts

For each quarter, the following artifacts are generated:

1. **Release Bundle** (ZIP)
   - Location: `05_documentation/releases/SSID_Quarterly_Release_YYYY-QX.zip`
   - Contains: All governance documents for the quarter

2. **Release Manifest** (JSON)
   - Location: `24_meta_orchestration/registry/manifests/quarterly_release_manifest_YYYY-QX.json`
   - Contains: Bundle metadata, hash, file list, verification info

3. **Registry Event** (JSON)
   - Location: `24_meta_orchestration/registry/events/release_YYYY-QX.json`
   - Contains: Event metadata for proof-anchoring

4. **Registry Log Entry**
   - Location: `24_meta_orchestration/registry/logs/registry_events.log`
   - Contains: Appended event for `governance_release_published`

## External Proof-Anchoring

For maximum tamper-proof verification, anchor bundle hashes to external systems:

### IPFS (Recommended - Free)
```bash
# Add bundle to IPFS
ipfs add SSID_Quarterly_Release_2026-Q1.zip

# Pin to ensure persistence
ipfs pin add <CID_from_above>

# Verify via gateway
# https://ipfs.io/ipfs/<CID>
```

### Blockchain (Ethereum/Polygon)
```bash
# Anchor to Polygon (low cost ~$0.01)
cast send $CONTRACT "anchorProof(bytes32,string,string)" \
  0x<BUNDLE_HASH> "2026-Q1" "github.com/EduBrainBoost/SSID" \
  --rpc-url $POLYGON_RPC_URL --private-key $PRIVATE_KEY
```

### Arweave (Permanent Storage)
```bash
# Deploy to Arweave for 200+ year permanence
arweave deploy SSID_Quarterly_Release_2026-Q1.zip --key-file wallet.json
```

See: `05_documentation/PROOF_ANCHORING_GUIDE.md` for complete instructions.

## GitHub Releases

All quarterly bundles are published to GitHub Releases:

**Format:** `https://github.com/EduBrainBoost/SSID/releases/tag/v4.2.0-Q1-2026`

Each release includes:
- Downloadable ZIP bundle
- SHA256 hash for verification
- Complete release notes
- External anchoring instructions
- Compliance status

## Bundle Contents

Each bundle typically includes:

| File | Description | Required |
|------|-------------|----------|
| COMPLIANCE_REPORT.md | Quarterly compliance audit | ✅ Required |
| SSID_Governance_Dashboard.md | Real-time metrics dashboard | ✅ Required |
| registry_events.log | Complete event log | ✅ Required |
| dashboard_manifest.json | Dashboard metadata | ✅ Required |
| branch_protection_rules.yaml | Branch protection config | ✅ Required |
| OPERATIONS_GUIDE.md | Operations procedures | ✅ Required |
| promotion_rules.yaml | Promotion workflows | ✅ Required |
| README.md | Repository overview | ✅ Required |
| integrity_checksums.json | File checksums | ⚠️ Optional |

## Compliance & Audit Trail

Release bundles provide:
- ✅ Complete governance snapshot for each quarter
- ✅ Tamper-proof proof-anchors (SHA256)
- ✅ Cryptographic verification capability
- ✅ External anchoring to IPFS/blockchain
- ✅ Full audit trail in registry events
- ✅ Reproducible builds (same inputs → same hash)

## Usage Examples

### Download Latest Release
```bash
# Via GitHub CLI
gh release download v4.2.0-Q1-2026 --repo EduBrainBoost/SSID

# Via wget
wget https://github.com/EduBrainBoost/SSID/releases/download/v4.2.0-Q1-2026/SSID_Quarterly_Release_2026-Q1.zip
```

### Extract Bundle
```bash
# Extract to current directory
unzip SSID_Quarterly_Release_2026-Q1.zip

# Extract to specific directory
unzip SSID_Quarterly_Release_2026-Q1.zip -d 2026-Q1-archive/
```

### Verify Integrity
```bash
# Calculate hash
sha256sum SSID_Quarterly_Release_2026-Q1.zip

# Compare with manifest
MANIFEST="24_meta_orchestration/registry/manifests/quarterly_release_manifest_2026-Q1.json"
EXPECTED=$(jq -r '.hash' "$MANIFEST")
ACTUAL=$(sha256sum SSID_Quarterly_Release_2026-Q1.zip | cut -d' ' -f1)

if [ "$EXPECTED" = "$ACTUAL" ]; then
  echo "✅ Verification passed"
else
  echo "❌ Verification failed"
fi
```

## Retention Policy

- **Git-Tracked:** All bundles committed to repository
- **GitHub Releases:** Permanent hosting on GitHub
- **IPFS:** Permanent if pinned (recommended)
- **Blockchain:** Permanent anchoring (optional)

## Metadata

Each bundle has associated metadata in JSON format:

```json
{
  "artifact": "05_documentation/releases/SSID_Quarterly_Release_2026-Q1.zip",
  "version": "v4.2.0-Q1-2026",
  "quarter": "2026-Q1",
  "blueprint": "v4.2.0",
  "compliance_score": "100/100",
  "hash": "<sha256>",
  "created_at": "<timestamp>",
  "status": "READY_FOR_PUBLIC_RELEASE"
}
```

## Troubleshooting

### Bundle Creation Fails
**Symptoms:** Script errors or missing files

**Solutions:**
1. Ensure all required files exist:
   ```bash
   ls -la 05_documentation/reports/2026-Q1/COMPLIANCE_REPORT.md
   ls -la 05_documentation/reports/dashboard/SSID_Governance_Dashboard.md
   ```
2. Run quarterly audit first:
   ```bash
   bash 12_tooling/scripts/run_quarterly_audit.sh
   ```
3. Check Python availability:
   ```bash
   python3 --version
   ```

### Hash Verification Fails
**Symptoms:** Calculated hash doesn't match manifest

**Solutions:**
1. Re-download or re-extract bundle
2. Check for file corruption
3. Verify manifest is for correct quarter
4. Re-generate bundle if necessary

### GitHub Release Not Created
**Symptoms:** Bundle created but no GitHub Release

**Solutions:**
1. Check if `gh` CLI is installed:
   ```bash
   gh --version
   ```
2. Install GitHub CLI: https://cli.github.com/
3. Authenticate: `gh auth login`
4. Run with `--publish` flag:
   ```bash
   python3 12_tooling/scripts/create_quarterly_release_bundle.py --publish
   ```

## Support & Resources

**Script:** `12_tooling/scripts/create_quarterly_release_bundle.py`
**Workflow:** `.github/workflows/quarterly_release.yml`
**Documentation:** `05_documentation/GOVERNANCE_ECOSYSTEM.md`
**Proof-Anchoring Guide:** `05_documentation/PROOF_ANCHORING_GUIDE.md`

**Repository:** https://github.com/EduBrainBoost/SSID
**Releases:** https://github.com/EduBrainBoost/SSID/releases

---

**Blueprint v4.2.0 Quarterly Release System**
_Automated • Tamper-Proof • Cryptographically Verified_
_Generated: 2025-10-11_
