# OpenTimestamps Setup Guide - Blockchain Anchoring

**Version:** 1.0.0
**Datum:** 2025-10-18
**Owner:** SSID Compliance Team
**Status:** READY FOR IMPLEMENTATION
**Deadline:** 2025-11-15

---

## Executive Summary

OpenTimestamps provides free, Bitcoin-based blockchain anchoring for SSID audit artifacts. This guide covers installation, usage, and integration into the QA Master Suite workflow.

**Timeline:** 30 minutes
**Cost:** FREE (Bitcoin-based)
**Benefits:** Tamper-proof timestamping, third-party verification, regulatory compliance

---

## What is OpenTimestamps?

OpenTimestamps (OTS) is an open-source standard for creating blockchain-based timestamps. It:

- **Proves existence:** A file existed at a specific time
- **Uses Bitcoin:** Most secure and decentralized blockchain
- **Is free:** No transaction fees
- **Is verifiable:** Anyone can verify timestamps independently

### How it works:

```
1. File → SHA256 Hash
2. Hash → Submit to OTS Calendars (aggregators)
3. Calendar → Bundle multiple hashes into Merkle tree
4. Merkle Root → Anchor in Bitcoin transaction (OP_RETURN)
5. Bitcoin confirmation → Immutable proof
```

---

## Installation

### Option 1: Python (Recommended)

```bash
# Install via pip
pip install opentimestamps-client

# Verify installation
ots --version
# Should show: OpenTimestamps client 0.x.x

# Test with help
ots --help
```

### Option 2: Docker

```bash
# Pull Docker image
docker pull btccom/opentimestamps-client

# Create alias
alias ots='docker run --rm -v $(pwd):/data btccom/opentimestamps-client'

# Test
ots --version
```

### Option 3: Binary (Linux/macOS)

```bash
# Download binary
wget https://github.com/opentimestamps/opentimestamps-client/releases/download/v0.7.1/ots
chmod +x ots
sudo mv ots /usr/local/bin/

# Verify
ots --version
```

---

## Basic Usage

### 1. Create Timestamp

```bash
# Timestamp a file
ots stamp document.pdf

# Creates: document.pdf.ots (timestamp proof)
```

The `.ots` file contains:
- SHA256 hash of the file
- Calendar server attestations
- Merkle tree path (once confirmed)
- Bitcoin transaction reference (after ~10-60 min)

### 2. Upgrade Timestamp (Wait for Bitcoin Confirmation)

```bash
# Upgrade to include Bitcoin confirmation
ots upgrade document.pdf.ots

# Run periodically until confirmed
# OR let it run automatically:
while ! ots verify document.pdf.ots 2>&1 | grep -q "Success"; do
    sleep 600  # Wait 10 minutes
    ots upgrade document.pdf.ots
done
```

### 3. Verify Timestamp

```bash
# Verify with original file
ots verify document.pdf.ots

# Expected output (after Bitcoin confirmation):
# Success! Bitcoin attests data existed as of Thu Oct 18 16:45:23 2025 UTC
# Complete proof:
#  * File sha256 hash: 173aedef08b3db974b6d4891aa84269f52970d65b5389697ce7dd1811033602f
#  * Bitcoin block 876543
```

### 4. Verify Without Original File

```bash
# If you only have the .ots file and know the hash
echo "173aedef08b3db974b6d4891aa84269f52970d65b5389697ce7dd1811033602f" | \
    xxd -r -p | \
    ots verify /dev/stdin < document.pdf.ots
```

---

## SSID Integration

### Use Cases

| Artifact Type | When to Timestamp | Retention |
|---------------|-------------------|-----------|
| **QA Policy** | Every version change | Forever |
| **Audit Reports** | After finalization | 7 years |
| **Evidence Chains** | Monthly | 5 years |
| **SHA256 Manifests** | Quarterly | 10 years |
| **Compliance Proofs** | As needed | 7 years |

### Workflow Integration

```bash
# Example: Timestamp QA Policy v2.0.0
cd /c/Users/bibel/Documents/Github/SSID

# 1. Create timestamp
ots stamp 24_meta_orchestration/registry/qa_corpus_policy.yaml

# Output:
# Submitting to remote calendar https://alice.btc.calendar.opentimestamps.org
# Submitting to remote calendar https://bob.btc.calendar.opentimestamps.org
# Submitting to remote calendar https://finney.calendar.eternitywall.com

# 2. Commit the .ots file
git add 24_meta_orchestration/registry/qa_corpus_policy.yaml.ots
git commit -m "chore: Add blockchain timestamp for QA Policy v2.0.0"

# 3. Wait for Bitcoin confirmation (10-60 minutes)
# Can continue working, upgrade later

# 4. Upgrade (after ~1 hour)
ots upgrade 24_meta_orchestration/registry/qa_corpus_policy.yaml.ots

# 5. Verify
ots verify 24_meta_orchestration/registry/qa_corpus_policy.yaml.ots

# 6. Update registry with Bitcoin block reference
# (See registry update section below)
```

---

## Automation Script

Create: `tools/timestamp_artifact.sh`

```bash
#!/bin/bash
################################################################################
# SSID OpenTimestamps Automation
################################################################################

set -euo pipefail

FILE="$1"
REGISTRY_FILE="24_meta_orchestration/registry/blockchain_anchor_registry.yaml"

if [ ! -f "$FILE" ]; then
    echo "❌ File not found: $FILE"
    exit 1
fi

echo "⛓️  Creating blockchain timestamp: $FILE"

# 1. Create timestamp
ots stamp "$FILE"

if [ ! -f "${FILE}.ots" ]; then
    echo "❌ Failed to create timestamp"
    exit 1
fi

echo "✅ Timestamp created: ${FILE}.ots"
echo "📝 SHA256: $(sha256sum "$FILE" | awk '{print $1}')"

# 2. Background upgrade task
{
    echo "⏳ Waiting for Bitcoin confirmation..."
    sleep 3600  # Wait 1 hour

    for i in {1..10}; do
        if ots upgrade "${FILE}.ots" 2>/dev/null; then
            if ots verify "${FILE}.ots" 2>&1 | grep -q "Success"; then
                echo "✅ Bitcoin confirmation received!"

                # Extract Bitcoin block
                BLOCK=$(ots verify "${FILE}.ots" 2>&1 | grep -oP 'block \K[0-9]+' | head -1)
                echo "   Bitcoin Block: $BLOCK"

                # Update registry
                echo "   Updating registry: $REGISTRY_FILE"
                # ... (registry update logic)

                break
            fi
        fi
        sleep 600  # Wait 10 more minutes
    done
} &

echo ""
echo "Background upgrade task started (PID: $!)"
echo "Monitor progress with: ots verify ${FILE}.ots"
echo ""
```

Make executable:
```bash
chmod +x tools/timestamp_artifact.sh
```

---

## Registry Integration

### Blockchain Anchor Registry

Create: `24_meta_orchestration/registry/blockchain_anchor_registry.yaml`

```yaml
version: "1.0.0"
created: "2025-10-18T00:00:00Z"
owner: "SSID Compliance Team"

anchors:
  - artifact: "24_meta_orchestration/registry/qa_corpus_policy.yaml"
    version: "2.0.0"
    sha256: "173aedef08b3db974b6d4891aa84269f52970d65b5389697ce7dd1811033602f"
    ots_file: "24_meta_orchestration/registry/qa_corpus_policy.yaml.ots"
    created: "2025-10-18T16:30:00Z"
    bitcoin_block: 876543
    bitcoin_timestamp: "2025-10-18T16:45:23Z"
    verification_status: "confirmed"
    verified_at: "2025-10-18T17:30:00Z"

  - artifact: "02_audit_logging/reports/QA_MASTER_SUITE_COMPLIANCE_AUDIT_2025_10_18.md"
    version: "1.0.0"
    sha256: "a1b2c3d4e5f6..."
    ots_file: "02_audit_logging/reports/QA_MASTER_SUITE_COMPLIANCE_AUDIT_2025_10_18.md.ots"
    created: "2025-10-18T17:00:00Z"
    bitcoin_block: null
    bitcoin_timestamp: null
    verification_status: "pending"
    verified_at: null
```

### Update Script

```python
#!/usr/bin/env python3
# tools/update_blockchain_registry.py

import yaml
import subprocess
import hashlib
from datetime import datetime

def get_sha256(filename):
    sha256_hash = hashlib.sha256()
    with open(filename, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def verify_ots(ots_file):
    """Verify OTS file and extract Bitcoin block if confirmed"""
    try:
        result = subprocess.run(
            ['ots', 'verify', ots_file],
            capture_output=True,
            text=True
        )

        if 'Success!' in result.stdout:
            # Extract Bitcoin block
            for line in result.stdout.split('\n'):
                if 'block' in line:
                    import re
                    match = re.search(r'block (\d+)', line)
                    if match:
                        return {'status': 'confirmed', 'block': int(match.group(1))}

        return {'status': 'pending', 'block': None}
    except Exception as e:
        return {'status': 'error', 'block': None, 'error': str(e)}

def add_to_registry(artifact_path, version="1.0.0"):
    registry_file = "24_meta_orchestration/registry/blockchain_anchor_registry.yaml"

    # Load or create registry
    try:
        with open(registry_file, 'r') as f:
            registry = yaml.safe_load(f) or {'anchors': []}
    except FileNotFoundError:
        registry = {
            'version': '1.0.0',
            'created': datetime.utcnow().isoformat() + 'Z',
            'owner': 'SSID Compliance Team',
            'anchors': []
        }

    # Calculate SHA256
    sha256 = get_sha256(artifact_path)

    # Check OTS file
    ots_file = f"{artifact_path}.ots"
    verification = verify_ots(ots_file)

    # Create entry
    entry = {
        'artifact': artifact_path,
        'version': version,
        'sha256': sha256,
        'ots_file': ots_file,
        'created': datetime.utcnow().isoformat() + 'Z',
        'bitcoin_block': verification.get('block'),
        'bitcoin_timestamp': None,  # TODO: Fetch from blockchain explorer
        'verification_status': verification['status'],
        'verified_at': datetime.utcnow().isoformat() + 'Z' if verification['status'] == 'confirmed' else None
    }

    # Add to registry
    registry['anchors'].append(entry)

    # Save
    with open(registry_file, 'w') as f:
        yaml.dump(registry, f, default_flow_style=False, sort_keys=False)

    print(f"✅ Added to registry: {artifact_path}")
    print(f"   Status: {verification['status']}")
    if verification.get('block'):
        print(f"   Bitcoin Block: {verification['block']}")

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: python update_blockchain_registry.py <artifact_path> [version]")
        sys.exit(1)

    artifact = sys.argv[1]
    version = sys.argv[2] if len(sys.argv) > 2 else "1.0.0"
    add_to_registry(artifact, version)
```

---

## GitHub Actions Integration

Add to `.github/workflows/blockchain_anchoring.yml`:

```yaml
name: Blockchain Anchoring

on:
  workflow_dispatch:
    inputs:
      artifact_path:
        description: 'Path to artifact to timestamp'
        required: true
      artifact_version:
        description: 'Artifact version'
        required: false
        default: '1.0.0'

jobs:
  timestamp:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install OpenTimestamps
        run: pip install opentimestamps-client

      - name: Create timestamp
        run: |
          ots stamp "${{ github.event.inputs.artifact_path }}"

      - name: Commit .ots file
        run: |
          git config user.name "SSID Bot"
          git config user.email "bot@ssid-project.internal"
          git add "${{ github.event.inputs.artifact_path }}.ots"
          git commit -m "chore: Add blockchain timestamp for ${{ github.event.inputs.artifact_path }}"
          git push

      - name: Background upgrade
        run: |
          {
            sleep 3600
            ots upgrade "${{ github.event.inputs.artifact_path }}.ots" || true
          } &
```

---

## Verification for Auditors

Provide auditors with:

1. **Original file** (or SHA256 hash)
2. **`.ots` file**
3. **Instructions:**

```bash
# Install OpenTimestamps
pip install opentimestamps-client

# Verify timestamp
ots verify document.pdf.ots

# Verify with hash only
echo "<sha256_hash>" | xxd -r -p | ots verify /dev/stdin < document.pdf.ots
```

Auditors can independently verify:
- File existed at claimed timestamp
- Proof is anchored in Bitcoin blockchain
- No trust required (publicly verifiable)

---

## Troubleshooting

### Issue: "Pending attestations" forever

**Cause:** Bitcoin confirmation not yet received (can take 10-60 min, sometimes longer)

**Solution:**
```bash
# Manually upgrade
ots upgrade file.ots

# Check status
ots info file.ots
```

### Issue: "Unknown calendar server"

**Cause:** Calendar server temporarily unavailable

**Solution:**
```bash
# Use different calendars
ots stamp --calendar https://alice.btc.calendar.opentimestamps.org file.pdf
```

### Issue: Verification fails

**Cause:** File was modified after timestamping

**Solution:**
```bash
# Check SHA256
sha256sum original_file.pdf
# Compare with hash in .ots file

ots info file.ots  # Shows expected hash
```

---

## Best Practices

1. **Timestamp immediately after finalization**
   - Don't wait for approval - timestamp locks the state

2. **Commit .ots files to Git**
   - Ensures they're not lost
   - Provides additional audit trail

3. **Upgrade within 24 hours**
   - Bitcoin confirmations typically happen within 1 hour
   - Don't wait too long (calendar servers may clean up pending)

4. **Verify before distributing**
   - Ensure timestamp is fully confirmed
   - Provides strongest proof

5. **Store .ots files with artifacts in WORM**
   - Both original and .ots should be immutable

---

## Next Steps

After completing this setup:

1. **Timestamp QA Policy v2.0.0**
2. **Timestamp Audit Reports**
3. **Create monthly Evidence Chain timestamps**
4. **Integrate into CI/CD pipeline**
5. **Train team on verification procedures**

---

## Success Metrics

- ✅ OpenTimestamps installed and working
- ✅ First artifact timestamped
- ✅ Bitcoin confirmation received
- ✅ Registry updated
- ✅ .ots files committed to Git
- ✅ Auditor verification procedure documented

---

## Resources

- **OpenTimestamps Website:** https://opentimestamps.org/
- **GitHub:** https://github.com/opentimestamps/opentimestamps-client
- **Specification:** https://github.com/opentimestamps/opentimestamps-protocol
- **Block Explorer:** https://blockstream.info/ (to verify Bitcoin transactions)

---

## Kontakt & Support

**OpenTimestamps Owner:** SSID Compliance Team
**Lead:** bibel
**Email:** compliance@ssid-project.internal
**Questions:** blockchain-anchoring@ssid-project.internal

---

**END OF SETUP GUIDE**

*Status: READY FOR IMPLEMENTATION*
*Classification: INTERNAL USE ONLY*
*Last Updated: 2025-10-18*
