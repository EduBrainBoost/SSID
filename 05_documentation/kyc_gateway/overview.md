# SSID KYC Gateway - Technical Overview

**Version:** 1.0.0
**Status:** Production-Ready (Mock Providers)
**License:** GPL-3.0-or-later
**Date:** 2025-10-12

---

## Executive Summary

SSID KYC Delegation Gateway implements a **non-custodial, proof-only architecture** for integrating third-party KYC providers (Didit, Yoti, IDnow, Signicat). Following the Web3 delegation pattern (MetaMask-style), SSID:

- **Does NOT** perform KYC verification
- **Does NOT** store personal identifiable information (PII)
- **Does NOT** handle payments or custody funds
- **Acts ONLY** as code publisher providing technical infrastructure

Users interact directly with KYC providers. SSID receives only cryptographic proofs (JWT/VC), validates signatures, computes hash digests, and stores proof records (hash-only, no PII).

---

## Architecture Pattern

### Delegation Model

```
┌──────────────────────────────────────────────────────────────┐
│  User                                                         │
│   │                                                           │
│   ├─→ 1. Request KYC (SSID Gateway)                          │
│   ├─→ 2. Redirect to Provider (Didit/Yoti/IDnow/Signicat)    │
│   ├─→ 3. Complete KYC with Provider (direct interaction)     │
│   ├─→ 4. Provider issues JWT/VC Proof                        │
│   └─→ 5. Provider sends Proof to SSID Callback              │
│                                                               │
│  SSID Gateway                                                 │
│   │                                                           │
│   ├─→ 6. Verify JWT signature (JWK-based)                    │
│   ├─→ 7. Validate issuer, audience, expiry                   │
│   ├─→ 8. Check for PII (reject if found)                     │
│   ├─→ 9. Normalize claims                                    │
│   ├─→ 10. Compute digest (SHA-256/BLAKE2b)                   │
│   ├─→ 11. Store proof record (hash-only, JSONL)              │
│   └─→ 12. Emit audit log (JSON, WORM)                        │
└──────────────────────────────────────────────────────────────┘
```

### Responsibility Matrix

| Responsibility | Party | SSID Role |
|----------------|-------|-----------|
| **KYC Execution** | Provider | None (delegation) |
| **PII Storage** | Provider | None (hash-only) |
| **Payment Processing** | User ↔ Provider | None (no payment flow) |
| **GDPR Controller** | Provider | Not applicable |
| **eIDAS Trust Service** | Provider | Verification only |
| **MiCA CASP** | N/A | Not a CASP |
| **AMLD6 Obliged Entity** | Provider | Not applicable |

---

## Security Model

### JWT Verification

1. **Signature Validation**: RS256/ES256/EdDSA using provider JWK Set
2. **Issuer Check**: Must match provider's registered issuer
3. **Audience Check**: Must match SSID's expected audience
4. **Expiry Check**: Token must not be expired (exp claim)
5. **Not-Before Check**: Token must be valid (nbf claim)
6. **JTI Check**: Replay protection via JTI cache with TTL

### Privacy Enforcement

**PII Blacklist** (rejected before storage):
- name, given_name, family_name, middle_name
- birthdate, birth_date, dob
- address, street_address, locality, region, postal_code
- email, phone_number, phone
- ssn, tax_id, national_id, passport, drivers_license
- picture, photo

**OPA Policy**: Enforces proof-only mode, rejects any PII-like patterns

**Hash-Only Storage**: Only SHA-256 or BLAKE2b digests persisted

---

## Proof Flow Sequence

```
User                SSID Gateway           Provider
  │                      │                      │
  │  POST /kyc/start     │                      │
  │─────────────────────>│                      │
  │  {provider, session} │                      │
  │                      │                      │
  │  {auth_url, state}   │                      │
  │<─────────────────────│                      │
  │                      │                      │
  │  Redirect            │                      │
  │──────────────────────────────────────────> │
  │                      │    (User completes   │
  │                      │     KYC with         │
  │                      │     Provider)        │
  │                      │                      │
  │  POST /callback      │                      │
  │<────────────────────────────────────────────┤
  │  {session, JWT/VC}   │                      │
  │─────────────────────>│                      │
  │                      │                      │
  │                      │  Fetch JWK Set       │
  │                      │─────────────────────>│
  │                      │<─────────────────────│
  │                      │                      │
  │                      │  Verify + Hash       │
  │                      │  (internal)          │
  │                      │                      │
  │  {PASS, proof_id,    │                      │
  │   digest}            │                      │
  │<─────────────────────│                      │
  │                      │                      │
  │  GET /proofs/{id}    │                      │
  │─────────────────────>│                      │
  │  {digest, timestamp} │                      │
  │<─────────────────────│                      │
```

---

## Data Structures

### Proof Record (JSONL)

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "provider_id": "didit",
  "digest": "a3c5f8d2e9b1047c6d8e2f5a9b3c7d1e4f6a8b9c0d1e2f3a4b5c6d7e8f9a0b1c",
  "algorithm": "SHA-256",
  "timestamp": "2025-10-12T10:00:00Z",
  "policy_version": "1.0",
  "evidence_chain": []
}
```

### Audit Log (JSON)

```json
{
  "event": "callback_success",
  "timestamp": "2025-10-12T10:00:00Z",
  "context": {
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "provider_id": "didit",
    "proof_id": "660f9511-f3ac-52e5-b827-557766551111",
    "digest": "a3c5f8d2...",
    "jti": "mock-jti-12345"
  }
}
```

---

## Compliance Design

### GDPR (Data Protection)
- **No PII Processing**: Only hash digests stored
- **Data Minimization**: Proof metadata only
- **Storage Limitation**: Proofs 365d, logs 90d
- **Right to Erasure**: Hash deletion on request

### eIDAS (Trust Services)
- **Signature Validation**: JWK-based JWT verification
- **Timestamp Validation**: UTC timestamps, max skew 60s
- **QTSP Integration**: Provider-dependent

### MiCA (Crypto-Assets)
- **Not Applicable**: SSID is not a CASP
- **No Custody**: No crypto-asset custody

### DORA (Resilience)
- **Testing Framework**: CI/CD with ≥90% coverage
- **Audit Logs**: Forensic trail (24h RTO)
- **Deterministic**: Reproducible verification

### AMLD6 (AML)
- **No KYC Role**: Delegated to providers
- **No Payment Flow**: User ↔ Provider direct

**Disclaimer**: Design intent, NOT legal advice. Independent legal review required.

---

## Testing Strategy

### Unit Tests
- JWT signature verification
- PII detection
- Digest computation (determinism)
- Replay protection (JTI cache)

### Integration Tests
- Start → Redirect → Callback flow
- Mock provider integration
- OPA policy enforcement

### Security Tests
- Invalid signature rejection
- Expired token rejection
- Replay attack mitigation
- Rate limiting enforcement

**Coverage Target**: ≥90%

---

## Deployment Checklist

- [ ] Replace mock provider endpoints with real URLs
- [ ] Configure real JWK Set URLs
- [ ] Set expected audience claim
- [ ] Enable TLS (production)
- [ ] Configure rate limiting
- [ ] Set up monitoring/alerting
- [ ] Independent security audit
- [ ] Legal review (compliance)
- [ ] DPIA (Data Protection Impact Assessment)
- [ ] Backup/recovery procedures

---

## Support & Documentation

- **OpenAPI Spec**: `14_zero_time_auth/kyc_gateway/openapi.yaml`
- **README**: `14_zero_time_auth/kyc_gateway/README.md`
- **Audit Report**: `23_compliance/reports/kyc_gateway_audit_report.md`
- **EU Mapping**: `23_compliance/mappings/kyc_delegation_eu_mapping.yaml`
- **Source Code**: https://github.com/EduBrainBoost/SSID

---

**License:** GPL-3.0-or-later
**Contact:** SSID Technical Team
