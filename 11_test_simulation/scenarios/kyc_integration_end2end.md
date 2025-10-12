# KYC Integration End-to-End Test Scenarios

**Version:** 1.0
**License:** GPL-3.0-or-later
**Purpose:** Deterministic E2E test scenarios for Layer 14 ↔ Layer 9 integration

---

## Scenario 1: Happy Path (Didit)

**Flow:** User → Didit → JWT → Layer 14 → Digest → Layer 3 → Layer 9

1. User completes KYC with Didit
2. Didit issues JWT (mock)
3. `proof_verifier.py` validates JWT
4. `kyc_callback_handler.py` computes digest
5. Webhook to `kyc_proof_interface.py`
6. OPA policy check: PASS
7. Forward to Layer 9
8. Audit logs emitted (WORM)

**Expected:** Status = ACCEPTED, layer9_proof_id generated

---

## Scenario 2: Invalid Signature

**Flow:** Provider manipulation → Signature failure

1. Attacker modifies JWT payload
2. `proof_verifier.py` detects invalid signature
3. Reject at Layer 14
4. No digest emission
5. Audit log: verification_failed

**Expected:** Status = FAILED, error = "Invalid signature"

---

## Scenario 3: Replay Attack

**Flow:** Duplicate digest → OPA reject

1. Valid digest emitted once
2. Attacker replays same digest
3. JTI cache detects duplicate
4. Reject at Layer 14 or Layer 3
5. Audit log: replay_detected

**Expected:** Status = FAILED, error = "Replay detected"

---

## Scenario 4: PII Injection

**Flow:** Payload contains forbidden fields

1. Attacker injects metadata: {"email": "test@example.com"}
2. `kyc_proof_interface.py` detects PII
3. OPA policy check: FAIL
4. Reject before Layer 9
5. Audit log: pii_detected

**Expected:** Status = FAILED, error = "PII detected"

---

## Scenario 5: Layer 9 Unavailable

**Flow:** Emit failure → Retry → Graceful degrade

1. Valid digest emitted
2. Layer 9 endpoint down
3. Retry 3 times (exponential backoff)
4. Store in pending_digests.jsonl
5. Audit log: emit_failed_retry

**Expected:** Status = RETRY, pending queue created

---

## Scenario 6: On-Chain Anchoring (Optional)

**Flow:** Digest → ProofAnchor.sol

1. Valid digest emitted and forwarded to Layer 9
2. On-chain emitter enabled (testnet)
3. `anchorProof()` called on Mumbai
4. Transaction confirmed
5. Audit log: on_chain_anchored

**Expected:** Transaction hash generated, gas used logged

---

## Test Execution

```bash
# Scenario 1: Happy Path
python 03_core/interfaces/kyc_proof_interface.py \
  --provider-id didit \
  --digest a3c5f8d2e9b1047c6d8e2f5a9b3c7d1e4f6a8b9c0d1e2f3a4b5c6d7e8f9a0b1c \
  --algorithm SHA-256 \
  --session-id 550e8400-e29b-41d4-a716-446655440000 \
  --proof-id 660f9511-f3ac-52e5-b827-557766551111

# Expected output:
# {"status": "ACCEPTED", "layer9_proof_id": "l9-a3c5f8d2...", "timestamp": "..."}
```

---

## Assertions

- Digest format: 64-char hex (SHA-256)
- OPA policy: PASS
- Audit logs: JSON structured, no PII
- Layer separation: No direct DB access
- Retry logic: 3 attempts with backoff
- Graceful degradation: Pending queue on failure
