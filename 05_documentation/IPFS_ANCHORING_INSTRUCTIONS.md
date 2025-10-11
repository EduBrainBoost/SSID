# IPFS Proof-Anchoring Instructions

**Blueprint v4.2.1 - External Verification Setup**
**Created:** 2025-10-11
**Status:** Ready for anchoring

## Overview

This guide provides step-by-step instructions for anchoring the SSID governance proof-anchors to IPFS for permanent, decentralized verification.

## Prerequisites

### Install IPFS

**Option 1: IPFS Desktop (Recommended for beginners)**
- Download: https://docs.ipfs.tech/install/ipfs-desktop/
- Install and launch
- IPFS daemon will start automatically

**Option 2: IPFS CLI (kubo)**
```bash
# Linux/Mac
wget https://dist.ipfs.tech/kubo/v0.24.0/kubo_v0.24.0_linux-amd64.tar.gz
tar -xvzf kubo_v0.24.0_linux-amd64.tar.gz
cd kubo
sudo bash install.sh

# Windows (via Chocolatey)
choco install ipfs

# Initialize IPFS
ipfs init
ipfs daemon
```

## Step 1: Anchor Registry Events Log

### Command:
```bash
cd C:/Users/bibel/Documents/Github/SSID
ipfs add 24_meta_orchestration/registry/logs/registry_events.log
```

### Expected Output:
```
added QmXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX registry_events.log
 X.XX KiB / X.XX KiB [====================================] 100.00%
```

### Save the CID:
The `QmXXX...` string is your **Content Identifier (CID)**. Save this!

Example CID: `QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG`

## Step 2: Verify Upload

### Via IPFS Gateway:
```
https://ipfs.io/ipfs/QmYOUR_CID_HERE
```

### Via Local Node:
```bash
ipfs cat QmYOUR_CID_HERE
```

### Via Cloudflare Gateway:
```
https://cloudflare-ipfs.com/ipfs/QmYOUR_CID_HERE
```

## Step 3: Pin to Ensure Persistence

### Local Pin:
```bash
ipfs pin add QmYOUR_CID_HERE
```

### Remote Pinning Services (Recommended):

#### Web3.Storage (Free, Unlimited)
```bash
# Install w3 CLI
npm install -g @web3-storage/w3cli

# Create account
w3 login YOUR_EMAIL@example.com

# Upload file
w3 put 24_meta_orchestration/registry/logs/registry_events.log
```

#### Pinata (Free tier: 1GB)
1. Sign up: https://app.pinata.cloud/
2. Get API key
3. Upload via web interface or API:
```bash
curl -X POST "https://api.pinata.cloud/pinning/pinFileToIPFS" \
  -H "Authorization: Bearer YOUR_JWT" \
  -F "file=@24_meta_orchestration/registry/logs/registry_events.log"
```

#### NFT.Storage (Free, Unlimited)
```bash
# Install NFT.Storage CLI
npm install -g nft.storage

# Create account and get API token
# https://nft.storage/

# Upload
nft-storage upload 24_meta_orchestration/registry/logs/registry_events.log
```

## Step 4: Update README with CID

### Add to README Footer:

```markdown
## External Proof-Anchoring

**Registry Events Log (IPFS):**
- **CID:** `QmYOUR_CID_HERE`
- **Gateway:** https://ipfs.io/ipfs/QmYOUR_CID_HERE
- **Pinned:** ✅ Yes (Web3.Storage)
- **Date:** 2025-10-11

**Verification:**
```bash
# Via IPFS
ipfs cat QmYOUR_CID_HERE

# Via HTTP gateway
curl https://ipfs.io/ipfs/QmYOUR_CID_HERE
```
```

### Add to Governance Dashboard:

In `05_documentation/reports/dashboard/SSID_Governance_Dashboard.md`, add:

```markdown
### External Proof-Anchors

**IPFS:**
- Registry Events: [QmYOUR_CID_HERE](https://ipfs.io/ipfs/QmYOUR_CID_HERE)
- Pinned: Web3.Storage (permanent)
- Uploaded: 2025-10-11
```

## Step 5: Anchor Quarterly Release Bundles

After generating first release bundle:

```bash
# Add release bundle to IPFS
ipfs add 05_documentation/releases/SSID_Quarterly_Release_2026-Q1.zip

# Pin to remote service
w3 put 05_documentation/releases/SSID_Quarterly_Release_2026-Q1.zip

# Update manifest with CID
# Edit: 24_meta_orchestration/registry/manifests/quarterly_release_manifest_2026-Q1.json
# Add IPFS CID to "external_anchors" section
```

## Complete Anchoring Checklist

### Initial Setup (One-Time)
- [ ] Install IPFS Desktop or kubo CLI
- [ ] Create account on Web3.Storage or Pinata
- [ ] Verify IPFS daemon is running
- [ ] Test upload with small file

### Registry Events Log (Now)
- [ ] Upload `registry_events.log` to IPFS
- [ ] Save CID from output
- [ ] Pin to remote service (Web3.Storage recommended)
- [ ] Verify via gateway (https://ipfs.io/ipfs/CID)
- [ ] Update README with CID
- [ ] Update governance dashboard with CID
- [ ] Commit and push changes

### Quarterly Release Bundles (After First Audit)
- [ ] Upload release ZIP to IPFS
- [ ] Save CID
- [ ] Pin to remote service
- [ ] Update release manifest with CID
- [ ] Add CID to GitHub Release notes
- [ ] Commit manifest changes

### Quarterly Maintenance
- [ ] Upload new registry_events.log each quarter
- [ ] Upload new release bundle each quarter
- [ ] Update manifests with new CIDs
- [ ] Maintain pinning service subscription

## Verification Commands

### Verify File on IPFS:
```bash
# Calculate local hash
sha256sum 24_meta_orchestration/registry/logs/registry_events.log

# Download from IPFS
ipfs cat QmYOUR_CID_HERE > /tmp/registry_events_ipfs.log

# Calculate IPFS file hash
sha256sum /tmp/registry_events_ipfs.log

# Hashes should match
```

### Check Pin Status:
```bash
# Local pins
ipfs pin ls --type=recursive | grep QmYOUR_CID_HERE

# Remote pin status (Web3.Storage)
w3 ls
```

## Cost Analysis

| Service | Free Tier | Paid Plans | Permanence |
|---------|-----------|------------|------------|
| **Web3.Storage** | Unlimited | Free | Permanent |
| **NFT.Storage** | Unlimited | Free | Permanent |
| **Pinata** | 1 GB | $20/mo (100GB) | Permanent (while pinned) |
| **Fleek** | 50 GB | $9/mo | Permanent (while pinned) |
| **Local Node** | Storage limit only | Free | Requires node uptime |

**Recommendation:** Web3.Storage (unlimited, free, permanent)

## Automation (Future Enhancement)

### Add to GitHub Actions Workflow:

```yaml
- name: Upload to IPFS
  run: |
    npm install -g @web3-storage/w3cli
    echo "${{ secrets.WEB3_STORAGE_TOKEN }}" | w3 token
    w3 put 24_meta_orchestration/registry/logs/registry_events.log

    # Capture CID
    CID=$(w3 ls | grep registry_events.log | awk '{print $2}')
    echo "ipfs_cid=${CID}" >> $GITHUB_OUTPUT
```

## Troubleshooting

### IPFS Daemon Not Running
**Symptoms:** `Error: api not running`

**Solutions:**
```bash
# Start daemon
ipfs daemon

# Or use IPFS Desktop (starts automatically)
```

### File Not Found on Gateway
**Symptoms:** Gateway returns 404

**Solutions:**
1. Wait 1-2 minutes for DHT propagation
2. Try different gateway (Cloudflare, Pinata)
3. Verify CID is correct
4. Ensure file is pinned

### Upload Fails
**Symptoms:** Timeout or connection error

**Solutions:**
1. Check internet connection
2. Restart IPFS daemon
3. Try smaller file first
4. Use remote pinning service instead

## Support & Resources

**IPFS Documentation:** https://docs.ipfs.tech/
**Web3.Storage:** https://web3.storage/docs/
**Pinata Docs:** https://docs.pinata.cloud/
**NFT.Storage:** https://nft.storage/docs/

**IPFS Gateways List:** https://ipfs.github.io/public-gateway-checker/

---

## Quick Start Summary

**1. Install IPFS:**
```bash
# Via IPFS Desktop (easiest)
# Download from: https://docs.ipfs.tech/install/ipfs-desktop/
```

**2. Upload Registry Log:**
```bash
ipfs add 24_meta_orchestration/registry/logs/registry_events.log
# Save the QmXXX... CID
```

**3. Pin to Web3.Storage:**
```bash
npm install -g @web3-storage/w3cli
w3 login YOUR_EMAIL
w3 put 24_meta_orchestration/registry/logs/registry_events.log
```

**4. Update README:**
```markdown
**IPFS CID:** QmYOUR_CID_HERE
**Gateway:** https://ipfs.io/ipfs/QmYOUR_CID_HERE
```

**5. Commit & Push:**
```bash
git add README.md
git commit -m "Add IPFS proof-anchor for registry events"
git push origin main
```

---

**Blueprint v4.2.1 IPFS Anchoring Instructions**
_Permanent • Decentralized • Verifiable_
_Last Updated: 2025-10-11_
