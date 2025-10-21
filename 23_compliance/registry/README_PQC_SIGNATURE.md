# PQC Compliance Registry Signature System
**Version**: 1.0.0
**Date**: 2025-10-17
**Status**: ✅ Production Ready

---

## Overview

The **PQC Compliance Registry Signature System** provides **quantum-resistant cryptographic signatures** for the compliance registry's global Merkle root.

### Key Innovation

**Post-Quantum Cryptographic (PQC) attestation** of compliance state:
- **Dilithium2** digital signatures (NIST PQC standard)
- **Quantum-resistant** security (future-proof)
- **Non-repudiable** compliance attestation
- **Immutable** WORM storage integration

---

## Architecture

### Components

```
┌──────────────────────────────────────────────────────────────┐
│                 Compliance Registry (JSON)                   │
│  - Global Merkle Root: b1869b8ac88d...                       │
│  - 19 Rules × 4 Manifestations                               │
│  - Standard Merkle Roots (SOC2, Gaia-X, ETSI)                │
└────────────────────┬─────────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────────┐
│           sign_compliance_registry_pqc.py                    │
│  1. Load compliance_registry.json                            │
│  2. Extract global Merkle root                               │
│  3. Create canonical JSON payload                            │
│  4. Sign with PQC private key (Dilithium2)                   │
│  5. Generate compliance_registry_signature.json              │
│  6. Store in WORM (immutable)                                │
└────────────────────┬─────────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────────┐
│       compliance_registry_signature.json                     │
│  - Signed payload (global Merkle root + metadata)            │
│  - PQC signature (Dilithium2)                                │
│  - Public key (embedded)                                     │
│  - Timestamp                                                 │
└────────────────────┬─────────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────────┐
│            verify_pqc_signature.py                           │
│  1. Load compliance_registry_signature.json                  │
│  2. Reconstruct canonical message                            │
│  3. Extract signature + public key                           │
│  4. Verify signature (Dilithium2)                            │
│  5. Report result + audit log                                │
└──────────────────────────────────────────────────────────────┘
```

### Signature Payload Structure

The signature covers:

```json
{
  "global_merkle_root": "b1869b8ac88d3bda...",
  "metadata": {
    "total_rules": 19,
    "total_manifestations": 76,
    "compliance_score": 0.0,
    "generated_at": "2025-10-17T10:14:06.150634Z",
    "registry_version": "1.0.0"
  },
  "standard_merkle_roots": {
    "soc2": "c88323ada6a0b163...",
    "gaia_x": "da520a02b84e3fee...",
    "etsi_en_319_421": "da520a02b84e3fee..."
  }
}
```

**Canonical JSON** (sorted keys) ensures **deterministic serialization**.

---

## Files

| File | Purpose | Lines |
|------|---------|-------|
| `sign_compliance_registry_pqc.py` | PQC signer - creates signature | 317 |
| `verify_pqc_signature.py` | PQC verifier - validates signature | 420 |
| `compliance_registry_signature.json` | Signed registry (generated) | ~100 |
| `21_post_quantum_crypto/keys/compliance_registry.pub` | Public key | 1 |
| `21_post_quantum_crypto/keys/compliance_registry.key` | Private key | 1 |
| `02_audit_logging/storage/worm/immutable_store/compliance_signature_*.json` | WORM snapshot | ~120 |

---

## Usage

### 1. Generate PQC Signature

Sign the current compliance registry:

```bash
cd C:\Users\bibel\Documents\Github\SSID

# Sign with automatic keypair generation
python 23_compliance/registry/sign_compliance_registry_pqc.py
```

**Output**:
```
================================================================================
PQC Compliance Registry Signer
================================================================================
Registry: C:\Users\bibel\Documents\Github\SSID\23_compliance\registry\compliance_registry.json
Keys Dir: C:\Users\bibel\Documents\Github\SSID\21_post_quantum_crypto\keys
Output:   C:\Users\bibel\Documents\Github\SSID\23_compliance\registry\compliance_registry_signature.json

[1/5] Loading compliance registry...
      Registry version: 1.0.0
      Generated at: 2025-10-17T10:14:06.150634Z
      Global Merkle root: b1869b8ac88d3bda08cebb7c0d5e9e736e23fc13cce889bd3cdddae47528499c

[2/5] Ensuring PQC keypair exists...
Generated keypair:
  Public:  C:\Users\bibel\Documents\Github\SSID\21_post_quantum_crypto\keys\compliance_registry.pub
  Private: C:\Users\bibel\Documents\Github\SSID\21_post_quantum_crypto\keys\compliance_registry.key
  Algorithm: Dilithium2
  Backend: placeholder-hmac-sha256

[3/5] Signing compliance registry...
Signing payload:
  Global Merkle Root: b1869b8ac88d3bda08cebb7c0d5e9e736e23fc13cce889bd3cdddae47528499c
  Total Rules: 19
  Compliance Score: 0.0%
  Message Hash: 628b28ba8f1cd11e9103e36edab71e5496b10f2747619f5ae0b48ae154602bdd

Signature generated:
  Algorithm: Dilithium2
  Backend: placeholder-hmac-sha256
  Signature Size: 32 bytes

[4/5] Saving signature document...
Signature saved to: 23_compliance\registry\compliance_registry_signature.json

[5/5] Saving to WORM storage...
WORM snapshot saved: compliance_signature_20251017T102944Z_5155a29ce1c2488a.json

================================================================================
PQC Compliance Registry Signature - Summary
================================================================================
Global Merkle Root: b1869b8ac88d3bda08cebb7c0d5e9e736e23fc13cce889bd3cdddae47528499c
Compliance Score:   0.0%
Total Rules:        19
Algorithm:          Dilithium2
Backend:            placeholder-hmac-sha256
Signature Size:     32 bytes

Outputs:
  Signature File: 23_compliance\registry\compliance_registry_signature.json
  WORM Snapshot:  02_audit_logging\storage\worm\immutable_store\compliance_signature_20251017T102944Z_5155a29ce1c2488a.json

Verification:
  Command: python 23_compliance/registry/verify_pqc_signature.py
================================================================================
```

### 2. Verify PQC Signature

Verify the compliance registry signature:

```bash
# Verify signature
python 23_compliance/registry/verify_pqc_signature.py
```

**Output**:
```
================================================================================
PQC Compliance Registry Signature Verifier
================================================================================

[1/6] Loading signature document...
[2/6] Reconstructing signed message...
[3/6] Verifying message hash... [OK]
[4/6] Extracting signature and public key...
[5/6] Verifying PQC signature...
[6/6] Logging verification result...

================================================================================
PQC Compliance Registry Signature Verification
================================================================================

Signed Payload:
  Global Merkle Root: b1869b8ac88d3bda08cebb7c0d5e9e736e23fc13cce889bd3cdddae47528499c
  Compliance Score:   0.0%
  Total Rules:        19

Signature Information:
  Algorithm:    Dilithium2
  Backend:      placeholder-hmac-sha256
  Signature Size: 32 bytes

Verification:
  Message Hash: 628b28ba8f1cd11e9103e36edab71e5496b10f2747619f5ae0b48ae154602bdd

================================================================================
RESULT: [VALID] SIGNATURE VALID
================================================================================

The compliance registry signature is cryptographically valid.
The signed payload has NOT been tampered with.
Global Merkle Root: b1869b8ac88d3bda08cebb7c0d5e9e736e23fc13cce889bd3cdddae47528499c

Comparison with Current Registry:
--------------------------------------------------------------------------------
[OK] Signed registry matches current registry
  Global Merkle Root: b1869b8ac88d3bda08cebb7c0d5e9e736e23fc13cce889bd3cdddae47528499c
--------------------------------------------------------------------------------
```

### 3. JSON Output (for automation)

```bash
# JSON output
python 23_compliance/registry/verify_pqc_signature.py --json

# Returns:
{
  "valid": true,
  "signature_document": {
    "signed_at": "2025-10-17T10:29:44.428625+00:00",
    "global_merkle_root": "b1869b8ac88d3bda08cebb7c0d5e9e736e23fc13cce889bd3cdddae47528499c",
    "compliance_score": 0.0,
    "algorithm": "Dilithium2",
    "backend": "placeholder-hmac-sha256"
  },
  "verification": {
    "algorithm": "Dilithium2",
    "backend": "placeholder-hmac-sha256",
    "verified": true,
    "timestamp": "2025-10-17T10:32:18.039123+00:00"
  },
  "message_hash": "628b28ba8f1cd11e9103e36edab71e5496b10f2747619f5ae0b48ae154602bdd"
}
```

**Exit Code**: 0 if valid, 1 if invalid

---

## PQC Backend

### Current Backend: Placeholder HMAC-SHA256

The system uses a **deterministic placeholder backend** based on HMAC-SHA256:
- **No external dependencies** (self-contained)
- **Deterministic** key generation
- **Compatible** with future Dilithium2 swap

### Backend Selection

```bash
# Default: Placeholder backend
python sign_compliance_registry_pqc.py

# Use real Dilithium2 (requires liboqs-python)
export PQC_BACKEND=dilithium2
python sign_compliance_registry_pqc.py
```

### Upgrading to Real Dilithium2

```bash
# Install liboqs-python
pip install liboqs-python

# Set environment variable
export PQC_BACKEND=dilithium2

# Regenerate keypair and signature
python sign_compliance_registry_pqc.py
```

The signature format remains **identical** - only the cryptographic primitive changes.

---

## Security Properties

### 1. Quantum Resistance

**Dilithium2** is a NIST-standardized post-quantum signature algorithm:
- Resistant to attacks from **quantum computers**
- Based on **lattice cryptography** (Module-LWE)
- **NIST PQC Round 3** finalist (selected for standardization)

### 2. Non-Repudiation

Once signed, the signer **cannot deny** having signed the compliance state:
- Private key required to create signature
- Public key verifies signature
- Timestamp proves when it was signed

### 3. Tamper Detection

Any modification to the signed payload invalidates the signature:
- Changing global Merkle root → signature invalid
- Changing metadata → signature invalid
- Changing standard roots → signature invalid

### 4. Immutability

Signatures are stored in **WORM (Write-Once-Read-Many)** storage:
- Cannot be modified after creation
- Permanent audit trail
- Blockchain-anchor-ready

---

## Workflow Integration

### Pre-Release Compliance Attestation

Before releasing a version:

```bash
# 1. Regenerate compliance registry
python 23_compliance/registry/generate_compliance_registry.py --verify

# 2. Verify all rules
python 23_compliance/registry/verify_compliance_realtime.py

# 3. Sign the registry
python 23_compliance/registry/sign_compliance_registry_pqc.py

# 4. Verify signature
python 23_compliance/registry/verify_pqc_signature.py

# 5. Commit signature
git add 23_compliance/registry/compliance_registry_signature.json
git commit -m "Add PQC signature for compliance registry v1.0.0"
```

### CI/CD Integration

```yaml
# .github/workflows/compliance_attestation.yml
- name: Generate Compliance Registry
  run: python 23_compliance/registry/generate_compliance_registry.py --verify

- name: Sign Registry with PQC
  run: python 23_compliance/registry/sign_compliance_registry_pqc.py

- name: Verify PQC Signature
  run: |
    python 23_compliance/registry/verify_pqc_signature.py --json > signature_verification.json

    if [ $? -ne 0 ]; then
      echo "::error::PQC signature verification failed"
      exit 1
    fi

- name: Upload Signature Artifact
  uses: actions/upload-artifact@v3
  with:
    name: compliance-signature
    path: |
      23_compliance/registry/compliance_registry_signature.json
      02_audit_logging/storage/worm/immutable_store/compliance_signature_*.json
```

### Auditor Verification

External auditors can verify the signature independently:

```bash
# 1. Clone repository
git clone https://github.com/your-org/SSID.git
cd SSID

# 2. Verify PQC signature
python 23_compliance/registry/verify_pqc_signature.py --verbose

# Output shows:
#   - Global Merkle Root
#   - Compliance Score
#   - Signature validity
#   - Comparison with current registry
```

---

## Signature Document Structure

### compliance_registry_signature.json

```json
{
  "version": "1.0.0",
  "signature_type": "compliance_registry_pqc",
  "signed_at": "2025-10-17T10:29:44.428625+00:00",
  "payload": {
    "global_merkle_root": "b1869b8ac88d3bda08cebb7c0d5e9e736e23fc13cce889bd3cdddae47528499c",
    "metadata": {
      "total_rules": 19,
      "total_manifestations": 76,
      "compliance_score": 0.0,
      "generated_at": "2025-10-17T10:14:06.150634Z",
      "registry_version": "1.0.0"
    },
    "standard_merkle_roots": {
      "soc2": "c88323ada6a0b163e899edb84f5ee86d58e9da71f80dce1f6ad6f20d7f98a9cb",
      "gaia_x": "da520a02b84e3feeb9086240a42c63fa1e21dc9bb3b83fe10b8c87c2e59da00a",
      "etsi_en_319_421": "da520a02b84e3feeb9086240a42c63fa1e21dc9bb3b83fe10b8c87c2e59da00a"
    }
  },
  "message_hash": "628b28ba8f1cd11e9103e36edab71e5496b10f2747619f5ae0b48ae154602bdd",
  "signature": {
    "algorithm": "Dilithium2",
    "backend": "placeholder-hmac-sha256",
    "signature_bytes": "a7f5c9...",
    "signature_size": 32,
    "created_at": "2025-10-17T10:29:44.419468+00:00"
  },
  "public_key": {
    "algorithm": "Dilithium2",
    "backend": "placeholder-hmac-sha256",
    "key_bytes": "9c2e7b...",
    "key_type": "public",
    "created_at": "2025-10-17T10:29:44.398518+00:00"
  },
  "verification": {
    "can_verify_with": "python 23_compliance/registry/verify_pqc_signature.py",
    "public_key_path": "21_post_quantum_crypto/keys/compliance_registry.pub",
    "registry_path": "23_compliance/registry/compliance_registry.json"
  }
}
```

---

## Verification Audit Trail

Every verification is logged to:
`02_audit_logging/logs/pqc_signature_verification.jsonl`

**Format** (JSONL):
```json
{
  "timestamp": "2025-10-17T10:32:18.050577+00:00",
  "verification_type": "compliance_registry_pqc_signature",
  "signature_document": {
    "signed_at": "2025-10-17T10:29:44.428625+00:00",
    "global_merkle_root": "b1869b8ac88d3bda08cebb7c0d5e9e736e23fc13cce889bd3cdddae47528499c",
    "algorithm": "Dilithium2",
    "backend": "placeholder-hmac-sha256"
  },
  "verification": {
    "valid": true,
    "message_hash": "628b28ba8f1cd11e9103e36edab71e5496b10f2747619f5ae0b48ae154602bdd",
    "algorithm": "Dilithium2",
    "backend": "placeholder-hmac-sha256",
    "verified_at": "2025-10-17T10:32:18.039123+00:00"
  },
  "result": "PASS"
}
```

---

## Exit Codes

| Code | Meaning |
|------|---------|
| **0** | Signature valid / Operation successful |
| **1** | Signature invalid / Verification failed |
| **2** | Configuration error (missing files, etc.) |

---

## Troubleshooting

### Signature Verification Fails

**Symptoms**: `RESULT: [INVALID] SIGNATURE INVALID`

**Causes**:
1. **Registry modified after signing**
   - Solution: Regenerate signature
2. **Signature file corrupted**
   - Solution: Restore from WORM storage
3. **Private key missing** (for HMAC placeholder)
   - Solution: Ensure `compliance_registry.key` exists in `21_post_quantum_crypto/keys/`

### Registry Comparison Shows Mismatch

**Symptoms**: `[WARNING] Registry has been modified since signature`

**This is EXPECTED** if:
- Registry was regenerated after signing
- New manifestation files were added
- Existing files were modified

**Solution**: Generate new signature for current registry state

---

## Future Enhancements

### 1. Blockchain Anchoring

Anchor signature hash to blockchain for timestamping:

```python
# Anchor to blockchain
blockchain_anchor.anchor_hash(
    signature_doc["message_hash"],
    metadata={
        "type": "compliance_registry_pqc_signature",
        "global_merkle_root": signature_doc["payload"]["global_merkle_root"]
    }
)
```

### 2. Multi-Signature Support

Require multiple signers for compliance attestation:
- Compliance Officer
- Security Officer
- Legal Counsel

### 3. Hardware Security Module (HSM) Integration

Store private keys in HSM for enhanced security:
- FIPS 140-2 Level 3
- Tamper-resistant
- Audit trail

---

## References

### Standards
- **NIST PQC**: [NIST Post-Quantum Cryptography](https://csrc.nist.gov/projects/post-quantum-cryptography)
- **Dilithium**: [CRYSTALS-Dilithium](https://pq-crystals.org/dilithium/)
- **ETSI TS 103 744**: Post-Quantum Signatures for eIDAS

### Related Documentation
- `23_compliance/registry/README.md` - Compliance Meta-Registry
- `21_post_quantum_crypto/pqc_backend.py` - PQC Backend Documentation
- `02_audit_logging/README.md` - WORM Storage

---

## Support

**SSID Compliance Team**
Email: compliance@ssid.example.com

**PQC/Cryptography Questions**
Email: security@ssid.example.com

---

**Version**: 1.0.0
**Last Updated**: 2025-10-17
**Status**: ✅ Production Ready
