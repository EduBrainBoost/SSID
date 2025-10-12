# SSID KYC Delegation Gateway

**Version:** 1.0.0
**License:** GPL-3.0-or-later
**Status:** Production-ready (mock providers)

## Overview

Non-custodial KYC delegation gateway following Web3 delegation pattern (MetaMask-style). SSID does not perform KYC, does not store PII, and does not handle payments. Users interact directly with third-party KYC providers (Didit, Yoti, IDnow, Signicat). SSID receives only cryptographic proofs (JWT/VC), validates them, and stores hash-based proof records.

## Architecture

```
User → SSID Gateway → KYC Provider (Didit/Yoti/IDnow/Signicat)
                ↓
        Proof (JWT/VC) →  SSID Verification
                ↓
        Hash Digest → Proof Registry (JSONL)
                ↓
        Audit Log (JSON, WORM)
```

### Flow Diagram

```
┌──────┐                 ┌──────────┐                 ┌──────────┐
│ User │                 │   SSID   │                 │ Provider │
└──┬───┘                 └────┬─────┘                 └────┬─────┘
   │                          │                            │
   │  1. POST /kyc/start      │                            │
   │─────────────────────────>│                            │
   │  {provider_id, session}  │                            │
   │                          │                            │
   │  2. {auth_url, state}    │                            │
   │<─────────────────────────│                            │
   │                          │                            │
   │  3. Redirect to Provider                              │
   │──────────────────────────────────────────────────────>│
   │                          │        (User completes KYC)│
   │                          │                            │
   │  4. POST /kyc/callback   │                            │
   │<─────────────────────────────────────────────────────┤
   │  {session_id, JWT/VC}    │                            │
   │                          │                            │
   │  5. Verify + Hash        │                            │
   │                          │──> JWK Fetch               │
   │                          │<── Public Keys             │
   │                          │                            │
   │  6. {PASS, proof_id}     │                            │
   │<─────────────────────────│                            │
   │                          │                            │
   │  7. GET /kyc/proofs/{id} │                            │
   │─────────────────────────>│                            │
   │  {digest, timestamp...}  │                            │
   │<─────────────────────────│                            │
```

## Features

- **Non-Custodial**: Zero PII storage, hash-only proofs
- **Delegation**: User ↔ Provider direct interaction
- **Security**: JWT signature verification, replay protection, rate limiting
- **Privacy**: PII filter enforced via OPA policy
- **Compliance**: GDPR/eIDAS/MiCA/DORA/AMLD6 design intent
- **Deterministic**: Reproducible digest computation
- **WORM Logging**: Write-Once-Read-Many audit trail
- **Root-24-LOCK**: Compliant file structure

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/kyc/providers` | GET | List available KYC providers |
| `/kyc/start` | POST | Start KYC session (returns auth_url) |
| `/kyc/callback` | POST | Handle provider callback (verify proof) |
| `/kyc/status/{session_id}` | GET | Get session status |
| `/kyc/proofs/{proof_id}` | GET | Get proof metadata (no PII) |

See `openapi.yaml` for full API specification.

## Setup

### Dependencies

```bash
pip install PyJWT cryptography pyyaml
```

### Configuration

Copy `config.example.yaml` and update:

```yaml
security:
  expected_audience: "ssid:kyc:gateway"
paths:
  provider_registry: "14_zero_time_auth/kyc_gateway/provider_registry.yaml"
  proof_registry: "14_zero_time_auth/kyc_gateway/proof_registry.jsonl"
  audit_log: "02_audit_logging/logs/kyc_gateway/kyc_gateway_audit.log"
```

### Usage

**Start Session:**

```bash
curl -X POST http://localhost:8080/api/v1/kyc/start \
  -H "Content-Type: application/json" \
  -d '{"provider_id": "didit", "session_id": "uuid", "scopes": ["kyc:basic"]}'
```

**Handle Callback:**

```python
from kyc_callback_handler import KYCCallbackHandler

handler = KYCCallbackHandler(
    provider_registry_path="provider_registry.yaml",
    proof_registry_path="proof_registry.jsonl",
    audit_log_path="kyc_gateway_audit.log",
    expected_audience="ssid:kyc:gateway",
)

result = handler.handle_callback(
    session_id="uuid",
    provider_id="didit",
    proof_token="<JWT_TOKEN>",
)
print(result)  # {"status": "PASS", "proof_id": "...", "digest": "..."}
```

## Security

- **JWT Verification**: RS256/ES256/EdDSA signature validation
- **Replay Protection**: JTI cache with TTL
- **PII Filter**: OPA policy rejects forbidden fields
- **Rate Limiting**: Max 10 sessions/IP/hour
- **CORS**: Strict origin control
- **TLS**: Required (production)

## Privacy

**No PII Storage**: Enforced via:
1. PII field blacklist (name, birthdate, address, email, phone, ssn, passport, etc.)
2. OPA policy check before persistence
3. Hash-only proof registry (SHA-256/BLAKE2b)
4. Audit logs contain only metadata (no PII)

**Data Retention**:
- Proofs: 365 days
- Logs: 90 days

## Testing

```bash
pytest 14_zero_time_auth/kyc_gateway/tests/ -v --cov=14_zero_time_auth/kyc_gateway --cov-fail-under=90
```

## Compliance

**Design Intent** (not legal advice):
- **GDPR**: No PII processing, hash-only storage
- **eIDAS**: Signature validation, timestamp checks
- **MiCA**: No custody, no CASP role
- **DORA**: Resilience via testing, audit logs
- **AMLD6**: No AML role (delegated to providers)

Independent legal review required.

## Threat Model (STRIDE)

| Threat | Mitigation |
|--------|------------|
| **Spoofing** | JWT signature verification, JWK-based trust |
| **Tampering** | WORM logs, deterministic digests |
| **Repudiation** | Audit logs with timestamps, JTI tracking |
| **Information Disclosure** | No PII storage, hash-only proofs |
| **Denial of Service** | Rate limiting, max concurrent verifications |
| **Elevation of Privilege** | OPA policy enforcement, provider allowlist |

## Providers

**Mock Providers** (testing only):
- Didit (redirect flow, JWT)
- Yoti (SDK flow, VC)
- IDnow (redirect flow, JWT)
- Signicat (redirect flow, JWT)

**Production**: Replace with real provider credentials in `provider_registry.yaml`.

## Files

- `provider_registry.yaml` - Provider metadata
- `openapi.yaml` - API specification (OpenAPI 3.1)
- `proof_verifier.py` - JWT/VC verification
- `kyc_callback_handler.py` - Callback processing
- `config.example.yaml` - Configuration template
- `proof_registry.jsonl` - Proof records (WORM)
- `tests/` - Test suite (≥90% coverage)

## License

GPL-3.0-or-later

## Contact

SSID Technical Team - https://github.com/EduBrainBoost/SSID
