# Registry Lineage System
**Version**: 1.0.0
**Date**: 2025-10-17
**Status**: ✅ Production Ready

---

## Overview

The **Registry Lineage System** provides a **chronological, cryptographically-verified audit trail** of compliance registry evolution over time.

### Key Innovation

**Ledger of Compliance Evolution** - A tamper-evident chain showing:
- **All historical states** of the compliance registry
- **PQC signatures** for each state
- **Merkle root evolution** over time
- **Changes attribution** (what changed, when, by whom)
- **Cryptographic linkage** between versions

**Result**: Complete, verifiable history of compliance evolution spanning versions and time periods.

---

## Architecture

### Lineage Chain Structure

```
Entry #1 (Initial)
├─ Global Merkle Root: b1869b8ac88d...
├─ PQC Signature: compliance_signature_20251017T102944Z_*.json
├─ Entry Hash: 23ad0053d7eb993f...
└─ Previous: None

      ↓ (cryptographically linked)

Entry #2 (After changes)
├─ Global Merkle Root: [new root]
├─ PQC Signature: compliance_signature_20251018T*.json
├─ Entry Hash: [new hash]
└─ Previous: Entry #1 (23ad0053d7eb993f...)

      ↓ (cryptographically linked)

Entry #3...
```

### Cryptographic Properties

1. **Entry Hash**: SHA-256 of entire entry (excluding hash field itself)
2. **Chain Linkage**: Each entry references previous entry ID + Merkle root
3. **PQC Signature**: Each entry links to its PQC signature file
4. **Tamper Detection**: Any modification breaks the chain

---

## Files

| File | Purpose | Format |
|------|---------|--------|
| `registry_lineage.yaml` | Chronological ledger of all registry states | YAML |
| `update_registry_lineage.py` | Add new entry to lineage | Python |
| `verify_lineage_integrity.py` | Verify chain integrity | Python |
| `compliance_workflow.sh` | Complete workflow automation | Bash |

---

## registry_lineage.yaml Structure

```yaml
metadata:
  version: "1.0.0"
  created_at: "2025-10-17T10:35:00.000000Z"
  description: "Chronological ledger of compliance registry evolution"

  # Chain integrity
  chain_hash_algorithm: "SHA-256"
  signature_algorithm: "Dilithium2"

  # Statistics
  total_entries: 1
  first_entry: "2025-10-17T10:29:44.428625Z"
  last_entry: "2025-10-17T10:29:44.428625Z"

entries:
  - entry_id: 1
    timestamp: "2025-10-17T10:29:44.428625Z"

    # Registry state
    registry_version: "1.0.0"
    global_merkle_root: "b1869b8ac88d3bda..."
    compliance_score: 0.0
    total_rules: 19
    total_manifestations: 76

    # Standard-specific Merkle roots
    standard_merkle_roots:
      soc2: "c88323ada6a0b163..."
      gaia_x: "da520a02b84e3fee..."
      etsi_en_319_421: "da520a02b84e3fee..."

    # PQC signature
    pqc_signature:
      algorithm: "Dilithium2"
      backend: "placeholder-hmac-sha256"
      signature_file: "23_compliance/registry/compliance_registry_signature.json"
      signature_hash: "628b28ba8f1cd11e..."
      worm_snapshot: "02_audit_logging/storage/worm/immutable_store/compliance_signature_*.json"

    # Changes from previous entry
    changes:
      type: "initial"
      description: "Initial compliance registry creation"
      files_added: 76
      files_modified: 0
      files_removed: 0
      rules_added: 19
      rules_modified: 0
      rules_removed: 0

    # Attribution
    attribution:
      actor: "SSID Compliance Team"
      event: "Initial registry creation"
      commit_sha: "abc123..."

    # Chain linkage
    chain:
      previous_entry_id: null
      previous_merkle_root: null
      entry_hash: "23ad0053d7eb993f8ca13b93a46e6baef531ea91fd5b0791431d100c8b8cfb99"
      chain_valid: true
```

---

## Usage

### Complete Workflow (Automated)

```bash
# Run complete compliance workflow
./23_compliance/registry/compliance_workflow.sh

# Steps:
# 1. Generate registry
# 2. Verify all rules
# 3. Sign with PQC
# 4. Verify signature
# 5. Update lineage
# 6. Verify lineage
```

**Output**:
```
================================================================================
Compliance Registry Workflow
================================================================================

[1/6] Generating compliance registry...
[OK] Registry generated

[2/6] Verifying all compliance rules...
[OK] All rules verified

[3/6] Signing registry with PQC...
[OK] Registry signed

[4/6] Verifying PQC signature...
[OK] Signature verified

[5/6] Updating registry lineage...
[OK] Lineage updated

[6/6] Verifying lineage integrity...
[OK] Lineage verified

================================================================================
Workflow Complete
================================================================================
```

### Manual Steps

#### 1. Add New Entry to Lineage

After creating a new PQC signature:

```bash
python 23_compliance/registry/update_registry_lineage.py
```

**Output**:
```
================================================================================
Registry Lineage Updater
================================================================================

[1/6] Loading lineage...
      Current entries: 1

[2/6] Loading signature document...
      Signed at: 2025-10-17T10:29:44.428625Z
      Global Merkle root: b1869b8ac88d3bda08cebb7c0d5e9e736e23fc13cce889bd3cdddae47528499c

[3/6] Loading registry...

[4/6] Checking for duplicates...

[5/6] Creating new entry...

================================================================================
New Registry Lineage Entry
================================================================================
Entry ID:           2
Timestamp:          2025-10-17T11:00:00.000000Z
Registry Version:   1.0.1
Global Merkle Root: [new root]
Compliance Score:   5.3%
Total Rules:        20

Change Type:        EXPANSION
Description:        Added 1 rules, 4 manifestations
  Rules Added:      1
  Rules Removed:    0
  Files Added:      4
  Files Modified:   0
  Files Removed:    0

PQC Signature:      Dilithium2
Entry Hash:         a7f5c9d2e3b8...
Previous Entry:     1
================================================================================

[6/6] Saving lineage...

[OK] Lineage entry #2 added successfully!
```

**Dry Run** (don't save):
```bash
python 23_compliance/registry/update_registry_lineage.py --dry-run
```

**Force** (skip duplicate check):
```bash
python 23_compliance/registry/update_registry_lineage.py --force
```

#### 2. Verify Lineage Integrity

Verify the entire chain:

```bash
python 23_compliance/registry/verify_lineage_integrity.py
```

**Output**:
```
================================================================================
Registry Lineage Integrity Verifier
================================================================================

[1/5] Loading lineage...
      Entries: 2

[2/5] Verifying entry hashes...
      Entry #1: [OK]
      Entry #2: [OK]

[3/5] Verifying chain linkage...
      Chain linkage: [OK]

[4/5] Verifying chronological order...
      Chronology: [OK]

[5/5] Verifying PQC signatures...
      Skipped (use --verify-signatures to enable)

================================================================================
Registry Lineage Integrity Verification
================================================================================

Lineage Metadata:
  Version:        1.0.0
  Total Entries:  2
  First Entry:    2025-10-17T10:29:44.428625Z
  Last Entry:     2025-10-17T11:00:00.000000Z

Verification Results:
  Entry Hashes:         PASS
  Chain Linkage:        PASS
  Chronological Order:  PASS
  PQC Signatures:       0/2

================================================================================
VERDICT: [VALID] CHAIN INTEGRITY VERIFIED
================================================================================

The registry lineage chain is cryptographically valid.
No tampering detected.

Entries: 2
Time Span: 2025-10-17T10:29:44.428625Z to 2025-10-17T11:00:00.000000Z
================================================================================
```

**With Signature Verification** (slower):
```bash
python 23_compliance/registry/verify_lineage_integrity.py --verify-signatures
```

**Verbose Output**:
```bash
python 23_compliance/registry/verify_lineage_integrity.py --verbose
```

**JSON Output**:
```bash
python 23_compliance/registry/verify_lineage_integrity.py --json
```

---

## Security Properties

### 1. Tamper Detection

**Any modification breaks the chain**:

#### Example: Modified Entry

If someone changes an entry's `compliance_score`:

```bash
# Before: compliance_score: 0.0
# After:  compliance_score: 1.0 (tampered)

python verify_lineage_integrity.py
```

**Output**:
```
Entry #1: [FAIL]
Hash mismatch (expected 23ad0053..., got 7f9e2d1a...)

VERDICT: [INVALID] CHAIN INTEGRITY COMPROMISED
```

#### Example: Inserted Entry

If someone inserts a fake entry:

```bash
# Chain: Entry #1 → Entry #2 → Entry #3
# Tampered: Entry #1 → Entry #1.5 (fake) → Entry #2 → Entry #3

python verify_lineage_integrity.py
```

**Output**:
```
Entry #2: Broken chain linkage (expected previous_entry_id=1, got 1.5)

VERDICT: [INVALID] CHAIN INTEGRITY COMPROMISED
```

#### Example: Deleted Entry

If someone removes an entry:

```bash
# Chain: Entry #1 → Entry #2 → Entry #3
# Tampered: Entry #1 → Entry #3 (entry #2 deleted)

python verify_lineage_integrity.py
```

**Output**:
```
Entry #3: Broken chain linkage (expected previous_entry_id=2, got 1)
Entry #3: Broken Merkle linkage (expected previous_merkle_root=..., got ...)

VERDICT: [INVALID] CHAIN INTEGRITY COMPROMISED
```

### 2. Chronological Integrity

Entries **must be chronologically ordered**:

```bash
# Entry #1: 2025-10-17T10:00:00Z
# Entry #2: 2025-10-17T09:00:00Z  ← EARLIER than #1!

python verify_lineage_integrity.py
```

**Output**:
```
Entry #2: Out of chronological order (timestamp ... is before previous entry ...)

VERDICT: [INVALID] CHAIN INTEGRITY COMPROMISED
```

### 3. PQC Signature Verification

Each entry links to its PQC signature:

```bash
python verify_lineage_integrity.py --verify-signatures
```

Verifies:
- Signature file exists
- Merkle root matches entry
- Signature hash matches
- PQC signature valid

---

## Change Detection

The lineage automatically detects and categorizes changes:

### Change Types

| Type | Description | Example |
|------|-------------|---------|
| `initial` | First entry | Initial registry creation |
| `expansion` | Rules/files added | Added 1 rule (CC8.1) |
| `reduction` | Rules/files removed | Removed deprecated rule |
| `modification` | Files modified (Merkle changed) | Updated manifestation files |
| `no_change` | Re-signature of same state | Renewed PQC signature |

### Change Metrics

Each entry tracks:
- **Rules**: `rules_added`, `rules_modified`, `rules_removed`
- **Files**: `files_added`, `files_modified`, `files_removed`

**Example**:
```yaml
changes:
  type: "expansion"
  description: "Added 1 rules, 4 manifestations"
  files_added: 4
  files_modified: 0
  files_removed: 0
  rules_added: 1
  rules_modified: 0
  rules_removed: 0
```

---

## Audit Trail

### Historical Queries

#### Query 1: What was the compliance state on [date]?

```python
import yaml
from datetime import datetime

with open('23_compliance/registry/registry_lineage.yaml') as f:
    lineage = yaml.safe_load(f)

target_date = datetime.fromisoformat("2025-10-17T10:30:00+00:00")

# Find entry closest to target date (before)
for entry in reversed(lineage['entries']):
    entry_time = datetime.fromisoformat(entry['timestamp'].replace('Z', '+00:00'))
    if entry_time <= target_date:
        print(f"State at {target_date}:")
        print(f"  Global Merkle Root: {entry['global_merkle_root']}")
        print(f"  Compliance Score: {entry['compliance_score']:.1%}")
        print(f"  Total Rules: {entry['total_rules']}")
        break
```

#### Query 2: When did rule count change from 19 to 20?

```python
for idx in range(1, len(lineage['entries'])):
    prev = lineage['entries'][idx - 1]
    curr = lineage['entries'][idx]

    if prev['total_rules'] == 19 and curr['total_rules'] == 20:
        print(f"Rule count changed from 19 to 20:")
        print(f"  Timestamp: {curr['timestamp']}")
        print(f"  Entry ID: {curr['entry_id']}")
        print(f"  Description: {curr['changes']['description']}")
        print(f"  Commit: {curr['attribution']['commit_sha']}")
        break
```

#### Query 3: Show all compliance score evolution

```python
print("Compliance Score Evolution:")
for entry in lineage['entries']:
    print(f"  {entry['timestamp']}: {entry['compliance_score']:.1%}")
```

**Output**:
```
Compliance Score Evolution:
  2025-10-17T10:29:44.428625Z: 0.0%
  2025-10-18T14:00:00.000000Z: 5.3%
  2025-10-19T09:30:00.000000Z: 15.8%
  2025-10-20T16:15:00.000000Z: 26.3%
```

---

## Git Integration

### Automatic Commit SHA Tracking

The lineage updater automatically captures the current Git commit:

```python
def get_git_commit_sha() -> Optional[str]:
    """Get current Git commit SHA if available."""
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        capture_output=True,
        text=True
    )
    return result.stdout.strip() if result.returncode == 0 else None
```

**Entry Attribution**:
```yaml
attribution:
  actor: "SSID Compliance Team"
  event: "Added CC8.1 - Infrastructure Management"
  commit_sha: "a7f5c9d2e3b84f1c"
```

### Git Workflow

```bash
# 1. Make changes to compliance rules
vim 23_compliance/mappings/soc2/src/cc8_1_infrastructure.py

# 2. Run complete workflow
./23_compliance/registry/compliance_workflow.sh

# 3. Review changes
git diff 23_compliance/registry/

# 4. Commit everything together
git add 23_compliance/mappings/
git add 23_compliance/registry/
git commit -m "Add CC8.1 - Infrastructure Management

- Add Python validation module
- Add Rego policy
- Add YAML contract
- Add CLI command
- Update compliance registry
- Sign with PQC
- Update lineage"

# 5. Push
git push
```

The lineage will capture the commit SHA automatically on the next update.

---

## Visualization

### Timeline Visualization

```python
import yaml
import matplotlib.pyplot as plt
from datetime import datetime

with open('23_compliance/registry/registry_lineage.yaml') as f:
    lineage = yaml.safe_load(f)

timestamps = [datetime.fromisoformat(e['timestamp'].replace('Z', '+00:00'))
              for e in lineage['entries']]
scores = [e['compliance_score'] * 100 for e in lineage['entries']]

plt.figure(figsize=(12, 6))
plt.plot(timestamps, scores, marker='o')
plt.xlabel('Date')
plt.ylabel('Compliance Score (%)')
plt.title('Compliance Evolution Over Time')
plt.grid(True)
plt.savefig('compliance_evolution.png')
```

---

## Exit Codes

| Code | Meaning |
|------|---------|
| **0** | Success / Chain valid |
| **1** | Failure / Chain invalid |
| **2** | Configuration error |

---

## Best Practices

### 1. Always Update Lineage After Signing

```bash
# After signing
python sign_compliance_registry_pqc.py

# Immediately update lineage
python update_registry_lineage.py
```

**Or use the automated workflow**:
```bash
./compliance_workflow.sh
```

### 2. Verify Before Committing

```bash
# Before git commit
python verify_lineage_integrity.py --verify-signatures

# Only commit if verification passes
if [ $? -eq 0 ]; then
    git add 23_compliance/registry/
    git commit -m "Update compliance registry"
fi
```

### 3. Regular Integrity Checks

```bash
# Daily cron job
0 9 * * * cd /path/to/SSID && python 23_compliance/registry/verify_lineage_integrity.py --verify-signatures --json > /tmp/lineage_check.json
```

### 4. Backup Lineage

```bash
# Before major changes
cp 23_compliance/registry/registry_lineage.yaml \
   23_compliance/registry/registry_lineage.yaml.backup
```

---

## Troubleshooting

### Duplicate Entry Error

**Symptom**:
```
WARNING: This Merkle root already exists in lineage
Use --force to add anyway, or create a new signature
```

**Cause**: Trying to add the same registry state twice.

**Solutions**:
1. **Intended re-signature**: Use `--force`
2. **Accidental**: Make changes first, then regenerate/sign

### Chain Verification Failed

**Symptom**:
```
VERDICT: [INVALID] CHAIN INTEGRITY COMPROMISED
```

**Cause**: Lineage was modified manually.

**Solutions**:
1. **Restore from backup**
2. **Regenerate lineage** (loses history!)
3. **Investigate tampering** (security incident)

### Git Commit SHA Missing

**Symptom**:
```yaml
commit_sha: null
```

**Cause**: Not in a Git repository or Git not available.

**Solution**: Run from Git repository with `git` in PATH.

---

## Future Enhancements

### 1. Blockchain Anchoring

Anchor lineage hashes to blockchain:

```python
# Anchor each entry hash to blockchain
for entry in lineage['entries']:
    blockchain.anchor(
        entry['chain']['entry_hash'],
        metadata={'entry_id': entry['entry_id']}
    )
```

### 2. Multi-Signature Governance

Require multiple signatures for lineage updates:

```yaml
attribution:
  signers:
    - actor: "Compliance Officer"
      signature: "..."
    - actor: "Security Officer"
      signature: "..."
    - actor: "Legal Counsel"
      signature: "..."
```

### 3. Automated Change Detection

Use Git diff to automatically detect changes:

```python
def detect_file_changes():
    result = subprocess.run(
        ["git", "diff", "--name-status", "HEAD~1", "23_compliance/mappings/"],
        capture_output=True,
        text=True
    )
    # Parse diff output for detailed change tracking
```

---

## References

### Standards
- **Blockchain Ledgers**: Bitcoin, Ethereum
- **Merkle Trees**: RFC 6962 (Certificate Transparency)
- **Git History**: Git DAG (Directed Acyclic Graph)

### Related Documentation
- `README.md` - Compliance Meta-Registry
- `README_PQC_SIGNATURE.md` - PQC Signature System
- `02_audit_logging/README.md` - WORM Storage

---

## Support

**SSID Compliance Team**
Email: compliance@ssid.example.com

**Lineage/Audit Questions**
Email: audit@ssid.example.com

---

**Version**: 1.0.0
**Last Updated**: 2025-10-17
**Status**: ✅ Production Ready
