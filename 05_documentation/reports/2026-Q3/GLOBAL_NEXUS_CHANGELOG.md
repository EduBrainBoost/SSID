# Global Proof Nexus – Changelog (v5.0)

## Blueprint v5.0 → v4.9 Comparison

### Major Changes

#### 1. New Layer: Layer 9 – Global Proof Nexus

**What Changed:**
- **v4.9:** Maximum layer was Layer 8 (Inter-Federation Mesh Consensus)
- **v5.0:** Introduced Layer 9 (Global Proof Nexus) for cross-ecosystem aggregation

**Impact:**
- Extends proof chain from federated to planetary scale
- Enables verification across independent identity ecosystems (SSID, EUDI, TrustNet, etc.)
- Establishes first cross-boundary consensus mechanism

#### 2. Consensus Threshold Adjustment

**What Changed:**
- **v4.9:** 80% consensus threshold (Layer 8)
- **v5.0:** 85% consensus threshold (Layer 9)

**Rationale:**
- Higher threshold for cross-ecosystem consensus ensures stronger agreement
- Maintains Byzantine fault tolerance at 20% (conservative limit)
- Aligns with BFT research for practical systems

#### 3. Trust Redistribution Algorithm

**What Changed:**
- **v4.9:** No formal trust scoring system
- **v5.0:** Asymmetric +1/-3 trust adjustment algorithm

**Details:**
```
TRUST_INCREMENT = +1  (for valid proof submission)
TRUST_DECREMENT = -3  (for invalid/missing proof)
TRUST_FLOOR = 0
TRUST_CEILING = 100
```

**Impact:**
- Statistical convergence to reliable ecosystems (trust ≥ 85)
- Game-theoretic incentive for cooperation
- Penalizes deviation/downtime

#### 4. Time-Gated Activation

**What Changed:**
- **v4.9:** Immediate activation on deployment
- **v5.0:** Time-gated activation at 2026-07-15T10:00:00Z

**Implementation:**
- CI/CD exits with code 1 (EARLY) before activation date
- Only "prep" commits and tags created during preparation phase
- Full "verified" tags issued after activation

**Benefits:**
- Allows extensive testing in simulation mode
- Gradual rollout with external ecosystems
- Reduces risk of premature production deployment

#### 5. Exit Code Standardization

**What Changed:**
- **v4.9:** 3 exit codes (SUCCESS, FAILED, INSUFFICIENT_PROOFS)
- **v5.0:** 5 exit codes with specific CI/CD actions

**New Exit Codes:**
```
0 = SUCCESS    → commit + tag (verified)
1 = EARLY      → commit only (prep)
2 = PREREQ     → block + create issue
3 = FAILED     → block + high-priority alert
4 = THRESHOLD  → block + manual review
```

**Impact:**
- More granular error handling in CI/CD
- Automated issue creation for blockers
- Clear separation of preparation vs. production phases

#### 6. Smart Contract Introduction

**What Changed:**
- **v4.9:** No on-chain anchoring
- **v5.0:** Solidity smart contract (`global_proof_nexus.sol`) for zero-custody proof anchoring

**Features:**
- `anchorGlobalProof()` – Publish Layer-9 root on-chain
- `registerEcosystem()` – DAO-based ecosystem registration
- `finalizeEpoch()` – Quarterly epoch rotation
- Events for full audit trail

**Blockchain:**
- Target: Ethereum mainnet (L1)
- Future: L2 solutions (Arbitrum, Optimism) for lower gas costs

#### 7. Manifest-Driven Configuration

**What Changed:**
- **v4.9:** Hardcoded parameters in Python scripts
- **v5.0:** Centralized manifest (`global_proof_manifest_v5.0.json`)

**Benefits:**
- Single source of truth for all configuration
- Easier parameter tuning without code changes
- Compliance markers (GDPR, eIDAS, MiCA, DORA, AMLD6) embedded in manifest

#### 8. Foreign Ecosystem Proof Schema

**What Changed:**
- **v4.9:** Only SSID-internal proofs supported
- **v5.0:** JSON schema for foreign Layer-8 proofs (`foreign_layer8_example.json`)

**Required Fields:**
```json
{
  "ecosystem_id": "eudi",
  "layer": 8,
  "proof_hash": "a3c5f8d2e9...",
  "epoch_id": "2026-Q3-001",
  "timestamp": "2026-07-15T10:00:00Z",
  "trust_weight": 95,
  "signature": { ... }
}
```

**Supported Ecosystems:**
- SSID (primary)
- EUDI (European Digital Identity)
- TrustNet (trust network protocol)
- OpenCore (open-source identity framework)
- Custom (experimental ecosystems)

---

## Migration Guide (v4.9 → v5.0)

### For SSID Internal Systems

1. **Update Layer-8 Outputs:**
   - Ensure Layer-8 proofs are written to `24_meta_orchestration/consensus/`
   - Include all required fields: `epoch_id`, `trust_weight`, `signature`

2. **Run Engine in Simulation Mode:**
   ```bash
   python 20_foundation/global_proof_nexus_engine.py
   ```
   - Verify exit code 1 (EARLY) before 2026-07-15
   - Check logs in `02_audit_logging/reports/global_proof_nexus_log.json`

3. **Review CI/CD Workflow:**
   - Workflow runs daily at 00:00 UTC (`.github/workflows/global_proof_nexus.yml`)
   - Verify artifacts retention (proofs: 365d, logs: 90d)

### For External Ecosystems (EUDI, TrustNet, etc.)

1. **Register Ecosystem:**
   - Submit DAO governance proposal with:
     - Ecosystem name
     - Authorized address (for proof submission)
     - Initial trust score (suggested: 80-90)

2. **Implement Proof Submission:**
   - Generate Layer-8 proofs according to `foreign_layer8_example.json` schema
   - Submit to SSID inbox: `24_meta_orchestration/federation/inbox/<ecosystem_id>.json`
   - Alternatively: Direct API submission (roadmap for Q4 2026)

3. **Monitor Trust Scores:**
   - Check `GLOBAL_NEXUS_SUMMARY.md` for trust deltas
   - Maintain ≥85% uptime to avoid trust score decay
   - Trust floor is 0 (requires DAO re-approval to restore)

---

## Deprecated Features

### Removed in v5.0:

1. **Layer-8 Direct On-Chain Anchoring:**
   - **Reason:** Layer 9 now handles all on-chain anchoring
   - **Migration:** Layer-8 proofs remain off-chain, only Layer-9 root goes on-chain

2. **Manual Consensus Triggers:**
   - **Reason:** Automated daily CI/CD execution
   - **Migration:** Use `workflow_dispatch` for manual triggers if needed

3. **Hardcoded Ecosystem List:**
   - **Reason:** Replaced with manifest-driven ecosystem registry
   - **Migration:** Update `ecosystems.registered` in manifest instead of code

---

## Known Issues & Workarounds

### Issue 1: Simulation Mode Limitations

**Problem:** No real cryptographic signature verification before 2026-07-01

**Workaround:** Manual signature verification using external tools (OpenSSL, GPG)

**Resolution:** Full cryptographic verification enabled in production (post-activation)

### Issue 2: Single CI/CD Runner

**Problem:** GitHub Actions runner is single point of failure

**Workaround:** Manual backup execution of `global_proof_nexus_engine.py`

**Resolution:** Multi-region runners deployment planned for Q3 2026

### Issue 3: Gas Cost Uncertainty

**Problem:** Ethereum mainnet gas costs vary (estimated $0.30-$1.00 per anchor)

**Workaround:** Monitor gas prices, execute during low-traffic periods

**Resolution:** L2 deployment (Arbitrum/Optimism) planned for H2 2026

---

## Compliance Changes

### New in v5.0:

1. **eIDAS Compliance:**
   - Optional QTSP (Qualified Timestamp Service Provider) integration
   - Signature algorithm validation (ed25519, ECDSA, RSA, PGP)

2. **MiCA Compliance:**
   - DAO-based governance for ecosystem registration
   - Full transparency via on-chain anchoring

3. **DORA Compliance:**
   - Resilience testing framework (BFT simulations)
   - 24-hour RTO (Recovery Time Objective)

4. **AMLD6 Compliance:**
   - Cross-border audit trail across all ecosystems
   - No reporting threshold (all transactions logged)

---

## Performance Metrics

| Metric | v4.9 (Layer 8) | v5.0 (Layer 9) | Change |
|--------|----------------|----------------|--------|
| **Consensus Cycle** | 24 hours | 24 hours | No change |
| **Max Ecosystems** | N/A (single ecosystem) | 50 | New |
| **Byzantine Tolerance** | 20% | 20% | No change |
| **Consensus Threshold** | 80% | 85% | +5% |
| **Proof Retention** | 90 days | 365 days | +275 days |
| **Log Retention** | 30 days | 90 days | +60 days |
| **On-Chain Gas Cost** | N/A | ~$0.30 (estimated) | New |

---

## Breaking Changes

### API/Interface Changes:

1. **Proof Format:**
   - **v4.9:** `merkle_root` field
   - **v5.0:** `proof_hash` field (standardized across ecosystems)
   - **Migration:** Rename field in Layer-8 output generators

2. **Epoch ID Format:**
   - **v4.9:** `2026_Q3_001`
   - **v5.0:** `2026-Q3-001` (hyphen-separated)
   - **Migration:** Update epoch ID generators to use hyphens

3. **Trust Weight Addition:**
   - **v4.9:** No trust weight field
   - **v5.0:** Required `trust_weight` field (0-100)
   - **Migration:** Calculate trust weight from consensus history (suggested: start at 85)

---

## Roadmap Preview (v5.1+)

### Planned for v5.1 (Q4 2026):

- [ ] Multi-region CI/CD runners (US, EU, Asia)
- [ ] IPFS pinning for redundant proof storage
- [ ] Reduce aggregation cycle to 12 hours (twice-daily)
- [ ] API endpoints for direct proof submission

### Planned for v5.2 (Q1 2027):

- [ ] Zero-knowledge proofs for privacy-preserving verification
- [ ] Quantum-resistant signature algorithms
- [ ] Real-time consensus (streaming state machines)

### Planned for v6.0 (Q2 2027):

- [ ] Self-amending protocol via on-chain governance
- [ ] Dynamic consensus threshold adjustment
- [ ] Integration with national digital identity systems

---

## FAQ

**Q: Do I need to migrate from v4.9 immediately?**
A: No. v4.9 (Layer 8) continues to operate independently. v5.0 (Layer 9) is additive, not replacement.

**Q: What happens if my ecosystem misses a proof submission?**
A: Trust score decreases by -3. No immediate penalty, but repeated misses will eventually drop trust to 0 (requires DAO re-approval).

**Q: Can I test Layer 9 before activation?**
A: Yes. Run `global_proof_nexus_engine.py` in simulation mode (exit code 1 until 2026-07-15).

**Q: How do I join as a new ecosystem?**
A: Submit DAO governance proposal with ecosystem details. Approval requires 67% quorum (2/3 majority).

**Q: What is the gas cost for on-chain anchoring?**
A: Estimated ~$0.30 at 50 gwei on Ethereum mainnet. Significantly lower on L2 solutions.

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 5.0.0 | 2025-01-15 | SSID Technical Team | Initial Layer-9 changelog |
| 5.0.1 | TBD | TBD | Post-activation updates |

---

**License:** GPL-3.0-or-later
**Contact:** For questions, open an issue at https://github.com/ssid-consortium/ssid
