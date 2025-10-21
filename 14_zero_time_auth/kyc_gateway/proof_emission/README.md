# Proof Emission & Provider Linking (v5.2)

**Layer 14 → Layer 9 Bidirectional Proof Flow**

## Overview

This subsystem implements secure, privacy-preserving proof emission from Layer 14 (Zero-Time-Auth) to Layer 9 (Global Proof Nexus), with bidirectional provider acknowledgement and on-chain anchoring.

**Key Features:**
- Zero PII emission (hash-only)
- Dual cryptographic hashing (SHA-512 + BLAKE2b)
- On-chain digest anchoring via ProofEmitter.sol
- Bidirectional JWT-based provider ACKs
- 100% OPA policy coverage
- WORM audit logging
- Replay protection

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ Layer 14: Zero-Time-Auth KYC Gateway                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────┐ │
│  │ KYC Event    │─────▶│ Proof        │─────▶│ Digest   │ │
│  │ (Raw Data)   │      │ Emission     │      │ Validator│ │
│  └──────────────┘      │ Engine       │      └──────────┘ │
│                        └──────┬───────┘                    │
│                               │                             │
└───────────────────────────────┼─────────────────────────────┘
                                │ Digest (Hash-Only)
                                ▼
┌─────────────────────────────────────────────────────────────┐
│ Layer 9: Global Proof Nexus                                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────┐ │
│  │ Proof Nexus  │─────▶│ ProofEmitter │─────▶│ Blockchain│ │
│  │ Engine       │      │ .sol         │      │ (Anchor)  │ │
│  └──────┬───────┘      └──────────────┘      └──────────┘ │
│         │                                                   │
└─────────┼───────────────────────────────────────────────────┘
          │ TX Hash
          ▼
┌─────────────────────────────────────────────────────────────┐
│ Provider ACK Flow (Bidirectional)                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────┐ │
│  │ ACK Linker   │◀────▶│ Provider API │─────▶│ JWT      │ │
│  │ (Layer 14)   │ JWT  │              │      │ Validator│ │
│  └──────────────┘      └──────────────┘      └──────────┘ │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Flow Sequence

```
┌────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│ KYC    │     │ Emission │     │ Layer 9  │     │ Blockchain│     │ Provider │
│ Event  │     │ Engine   │     │ Nexus    │     │          │     │          │
└───┬────┘     └────┬─────┘     └────┬─────┘     └────┬─────┘     └────┬─────┘
    │               │                │                │                │
    │ Raw Data      │                │                │                │
    ├──────────────▶│                │                │                │
    │               │                │                │                │
    │               │ PII Filter     │                │                │
    │               │ + Hash         │                │                │
    │               │                │                │                │
    │               │ emit_proof()   │                │                │
    │               ├───────────────▶│                │                │
    │               │                │                │                │
    │               │                │ anchor()       │                │
    │               │                ├───────────────▶│                │
    │               │                │                │                │
    │               │                │   TX Hash      │                │
    │               │                │◀───────────────┤                │
    │               │                │                │                │
    │               │   TX Hash      │                │                │
    │               │◀───────────────┤                │                │
    │               │                │                │                │
    │               │ send_ack()     │                │                │
    │               ├───────────────────────────────────────────────────▶│
    │               │                │                │                │
    │               │                │                │    ACK JWT     │
    │               │◀───────────────────────────────────────────────────┤
    │               │                │                │                │
    │               │ verify_ack()   │                │                │
    │               ├───────────────▶│                │                │
    │               │                │                │                │
    │               │   Verified     │                │                │
    │               │◀───────────────┤                │                │
    │               │                │                │                │
    │               │ WORM Log       │                │                │
    │               │                │                │                │
```

---

## Components

### 1. Proof Emission Engine (`proof_emission_engine.py`)

**Purpose:** Orchestrates digest generation, Layer 9 submission, and ACK coordination.

**Key Methods:**
- `generate_digest(raw_data)` → `ProofDigest`
- `emit_proof(digest, provider_id)` → `EmissionRecord`
- `retry_emission(record)` → `EmissionRecord`

**Security Features:**
- PII filtering via strict allow-list
- Nonce-based replay protection
- HMAC digest ID generation
- Timestamp validation (±1 hour)

### 2. Provider ACK Linker (`provider_ack_linker.py`)

**Purpose:** Manages bidirectional JWT-based acknowledgements with providers.

**Key Methods:**
- `send_ack_request(digest, provider_id)` → `ACKRequest`
- `verify_ack_signature(ack_jwt)` → `bool`
- `retry_ack(request)` → `ACKResponse`

**ACK JWT Structure:**
```json
{
  "iss": "provider_id",
  "sub": "digest_id",
  "iat": 1234567890,
  "exp": 1234568190,
  "ack": {
    "digest_hash": "sha512...",
    "anchor_tx": "0x...",
    "status": "acknowledged"
  },
  "sig": "EdDSA..."
}
```

### 3. Digest Validator (`digest_validator.py`)

**Purpose:** Cross-layer verification and integrity checks.

**Key Methods:**
- `validate_digest(digest)` → `ValidationResult`
- `verify_against_layer9(digest_id)` → `bool`
- `check_replay(nonce)` → `bool`

---

## Cryptographic Specifications

### Hash Algorithms

| Purpose | Algorithm | Output Size | Usage |
|---------|-----------|-------------|-------|
| Content Hash | SHA-512 | 128 hex chars | Primary digest |
| Merkle Root | BLAKE2b | 64 hex chars | Future tree expansion |
| Digest ID | HMAC-SHA256 | 64 hex chars | Unique identifier |

### Signature Schemes

| Context | Algorithm | Key Size | Format |
|---------|-----------|----------|--------|
| Provider ACK | EdDSA (Ed25519) | 256-bit | JWS Compact |
| Digest ID | HMAC-SHA256 | 256-bit | Hex |

### Replay Protection

- **Nonce:** 128-bit cryptographic random (16 bytes hex)
- **Timestamp:** Unix epoch, validated ±1 hour
- **Digest ID:** `HMAC(content_hash || timestamp || nonce)`

---

## OPA Policy Enforcement

All emissions must pass 100% of OPA policies before anchoring:

```rego
# 23_compliance/policies/proof_linking_policy.rego

package ssid.proof_linking

default allow = false

allow {
    input.digest.content_hash != ""
    input.digest.merkle_root != ""
    no_pii_detected(input.digest)
    valid_signature(input.ack)
    timestamp_within_range(input.digest.timestamp)
}

no_pii_detected(digest) {
    # Ensure no PII fields in metadata
    pii_fields := {"name", "ssn", "address", "email", "phone"}
    count({k | digest.metadata[k]; pii_fields[k]}) == 0
}
```

---

## Configuration

See `config.v5.2.example.yaml` for full configuration schema.

**Critical Settings:**
```yaml
# HMAC Secret (256-bit minimum)
crypto:
  hmac_secret: "${PROOF_EMISSION_HMAC_SECRET}"

# Layer 9 Endpoint
layer9:
  endpoint: "http://localhost:8009"
  api_key: "${LAYER9_API_KEY}"

# Blockchain Anchoring
blockchain:
  enabled: true
  contract_address: "${PROOF_EMITTER_CONTRACT_ADDRESS}"
```

---

## Usage Example

```python
from proof_emission_engine import create_engine

# Initialize engine
engine = create_engine(config_path="config.v5.2.yaml")

# KYC event (contains PII)
kyc_event = {
    'event_type': 'kyc_completion',
    'event_id': 'evt_12345',
    'timestamp': 1234567890,
    'provider_type': 'tier1_bank',
    'verification_level': 'enhanced',
    'user_name': 'John Doe',  # Will be filtered
    'document_id': 'AB123456'  # Will be filtered
}

# Generate digest (PII-filtered)
digest = engine.generate_digest(kyc_event)
# digest.content_hash = sha512(filtered_data)
# digest.merkle_root = blake2b(content_hash)

# Emit to Layer 9
record = engine.emit_proof(digest, provider_id="provider_001")

# Check status
if record.status == EmissionStatus.ANCHORED:
    print(f"Anchored: {record.anchor_tx_hash}")
elif record.status == EmissionStatus.RETRY:
    record = engine.retry_emission(record)

# Export for audit
audit_log = engine.export_audit_record(record)
```

---

## Testing

Run comprehensive test suite:

```bash
pytest 14_zero_time_auth/kyc_gateway/tests/test_proof_linking.py \
  --cov=proof_emission \
  --cov-report=html \
  --cov-fail-under=95
```

**Test Coverage Targets:**
- Unit tests: 100%
- Integration tests: 95%
- E2E scenarios: 8 critical paths

**Test Scenarios:**
1. Valid digest → anchor → ACK → PASS
2. Tampered ACK → reject + audit
3. Replay attack → OPA deny
4. Hash mismatch → fail
5. Missing ACK → retry queue
6. Provider offline → graceful degrade
7. Digest re-sync → PASS
8. PII injection → reject + log

---

## Security Considerations

### PII Protection
- **Allow-list filtering:** Only 7 metadata fields permitted
- **Hash-only emission:** No raw data leaves Layer 14
- **Zero-knowledge proofs:** Future expansion planned

### Replay Protection
- **Nonce:** 128-bit random per emission
- **Timestamp validation:** ±1 hour window
- **Digest ID:** HMAC prevents forgery

### Signature Verification
- **EdDSA (Ed25519):** Provider ACK signatures
- **JWK validation:** Public key registry
- **Expiry enforcement:** 5-minute ACK window

### Audit Trail
- **WORM logging:** Immutable audit records
- **Blockchain anchoring:** On-chain proof of existence
- **Multi-layer verification:** Layer 9 ↔ Layer 14 sync

---

## Compliance

### Legal Matrix
See `23_compliance/mappings/proof_linking_legal_matrix.yaml`

**SSID Role:** Code Publisher (Non-Controller)
**Provider Role:** Data Controller
**User Role:** Data Subject

### GDPR/Privacy
- No PII processing by SSID
- Provider-managed consent
- Right to erasure (hash persistence only)

### Audit Requirements
- 100% OPA policy coverage
- ≥95% test coverage
- Zero high/critical vulnerabilities
- Score 100/100 across all categories

---

## Performance

### Throughput
- **Max emissions/min:** 100 (configurable)
- **Concurrent emissions:** 10 (default)
- **Queue size:** 1000

### Latency
- **Digest generation:** <10ms
- **Layer 9 anchor:** <500ms (on-chain) / <50ms (off-chain)
- **ACK round-trip:** <2s (typical)

### Retry Policy
- **Max retries:** 3
- **Backoff:** Exponential (5s, 10s, 20s)
- **Timeout:** 60s per operation

---

## Integration Points

### Layer 9 API
```python
# 20_foundation/global_proof_nexus_engine.py
nexus.emit_proof_anchor(
    digest_id=str,
    content_hash=str,
    merkle_root=str,
    timestamp=int
) → {'success': bool, 'tx_hash': str}
```

### Provider API
```http
POST /api/v1/ack
Content-Type: application/json
Authorization: Bearer {provider_jwt}

{
  "digest_id": "abc123...",
  "content_hash": "sha512...",
  "anchor_tx": "0x..."
}

Response:
{
  "ack_jwt": "eyJ..."
}
```

---

## Monitoring

### Metrics (Prometheus)
- `proof_emissions_total{status}`
- `proof_emission_duration_seconds`
- `layer9_anchor_failures_total`
- `provider_ack_timeouts_total`

### Alerts
- Emission failure rate >5%
- Layer 9 unavailable >30s
- ACK timeout >60s
- OPA policy denial

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| v5.2 | 2025-10 | Initial release - Bidirectional proof flow |
| v5.1.1 | 2025-09 | KYC Gateway integration |
| v5.0 | 2025-08 | Foundation blueprint |

---

## License

See project root LICENSE file.

**SSID Legal Status:** Non-Controller, Code Publisher Only
**Liability:** Delegated to Provider (Data Controller)

---

## Support

- **Documentation:** https://docs.ssid.example/proof-emission
- **Issues:** https://github.com/ssid/ssid/issues
- **Security:** security@ssid.example (PGP key required)
