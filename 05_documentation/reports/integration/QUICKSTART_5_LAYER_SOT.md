# 🚀 SSID 5-Layer SoT Enforcement - Quick Start Guide

**Version:** 1.0.0
**Last Updated:** 2025-10-22

---

## What is the 5-Layer SoT Enforcement?

The SSID (Sovereign Self-Sovereign Identity) system uses a **5-layer defense-in-depth architecture** to ensure that all 1,367 Source of Truth (SoT) rules are:

1. **Cryptographically sealed** (tamper-proof)
2. **Policy-enforced** (runtime validation)
3. **Trust-anchored** (verifiable origin)
4. **Observable** (auditable execution)
5. **Governance-compliant** (legally binding)

This guide helps you get started in **5 minutes**.

---

## Prerequisites

- Python 3.10+
- Git
- (Optional) OPA CLI for policy testing
- (Optional) Prometheus for metrics

---

## Quick Start (5 Minutes)

### Step 1: Run the Full Audit Pipeline

```bash
python 02_audit_logging/pipeline/run_audit_pipeline.py
```

**Expected Output:**
```
===============================================================================
SSID SoT Audit Pipeline - Full Execution
===============================================================================

[Layer 1/5] Cryptographic Security
  ✅ Merkle Lock passed
  ✅ PQC Signing passed

[Layer 2/5] Policy Enforcement
  ✅ OPA Policy Test passed
  ✅ SoT Validator passed

[Layer 3/5] Trust Boundary
  ✅ DID Verification simulated
  ✅ ZTA proof simulated

[Layer 4/5] Observability
  ✅ Compliance score: 100.00%

[Layer 5/5] Governance
  ✅ Registry update simulated
  ✅ Dual review simulated

===============================================================================
AUDIT PIPELINE COMPLETE
===============================================================================
Overall Result: ✅ PASS
Duration: 45.23 seconds
```

**Output Files:**
- `02_audit_logging/reports/audit_pipeline_result.json`
- `02_audit_logging/reports/audit_pipeline_report.md`
- `02_audit_logging/reports/AGENT_STACK_SCORE_LOG.json`

---

### Step 2: View Compliance Score

```bash
cat 02_audit_logging/reports/AGENT_STACK_SCORE_LOG.json
```

**Expected:**
```json
{
  "timestamp": "2025-10-22T14:00:00Z",
  "compliance_score": 100.0,
  "total_rules": 1276,
  "passed_rules": 1276,
  "failed_rules": 0
}
```

---

### Step 3: Run Integration Tests

```bash
pytest 11_test_simulation/tests_sot/test_5_layer_integration.py -v
```

**Expected Output:**
```
========================== 25 passed in 120.45s ==========================
```

---

### Step 4: Start Metrics Exporter (Optional)

```bash
python 17_observability/sot_metrics.py --port 9090
```

**Access Metrics:**
- Prometheus format: `http://localhost:9090/metrics`
- Health check: `http://localhost:9090/health`
- Dashboard: `http://localhost:9090/`

**Example Metrics:**
```
sot_validator_pass_rate 1.0000
sot_compliance_score 100.00
sot_rules_total 1276
sot_merkle_verifications_total 3
sot_worm_snapshots_total 5
```

---

## Layer-by-Layer Quick Reference

### Layer 1: Cryptographic Security

**Purpose:** Ensure no SoT rule can be manipulated.

**Quick Test:**
```bash
# Generate Merkle lock
python 23_compliance/merkle/root_write_merkle_lock.py

# View Merkle certificate
cat 02_audit_logging/merkle/root_write_merkle_certificate.md

# Generate PQC signature
python 23_compliance/registry/sign_compliance_registry_pqc.py --no-worm

# Verify PQC signature
python 23_compliance/registry/verify_pqc_signature.py
```

**Key Files:**
- Merkle proofs: `02_audit_logging/merkle/root_write_merkle_proofs.json`
- PQC signature: `23_compliance/registry/compliance_registry_signature.json`
- WORM storage: `02_audit_logging/storage/worm/immutable_store/*.json`

---

### Layer 2: Policy Enforcement

**Purpose:** Verify cryptographically sealed rules are enforced.

**Quick Test:**
```bash
# Test OPA policies
opa test 23_compliance/policies/sot/ -v

# Run SoT validator
python 03_core/validators/sot/sot_validator_core.py
```

**Key Files:**
- SoT policy: `23_compliance/policies/sot/sot_policy.rego` (384 rules)
- Agent sandbox: `23_compliance/policies/agent_sandbox.rego`
- Validator: `03_core/validators/sot/sot_validator_core.py`

---

### Layer 3: Trust Boundary

**Purpose:** Prevent unauthorized entities from modifying SoT.

**Quick Test:**
```bash
# Test DID format validation
pytest 11_test_simulation/tests_sot/test_5_layer_integration.py::TestLayer3TrustBoundary -v

# Run Zero-Time-Auth tests
pytest 11_test_simulation/zero_time_auth/Shard_01_*/test_*.py -v
```

**Key Files:**
- DID resolver: `09_meta_identity/src/did_resolver.py`
- ZTA tests: `11_test_simulation/zero_time_auth/Shard_*/test_*.py`

---

### Layer 4: Observability

**Purpose:** Prove SoT rules are actively enforced.

**Quick Test:**
```bash
# Start metrics server
python 17_observability/sot_metrics.py &

# Scrape metrics
curl http://localhost:9090/metrics

# Run audit pipeline
python 02_audit_logging/pipeline/run_audit_pipeline.py

# View scorecard
cat 02_audit_logging/reports/AGENT_STACK_SCORE_LOG.json
```

**Key Files:**
- Metrics exporter: `17_observability/sot_metrics.py`
- Audit pipeline: `02_audit_logging/pipeline/run_audit_pipeline.py`
- Scorecard: `02_audit_logging/reports/AGENT_STACK_SCORE_LOG.json`

---

### Layer 5: Governance

**Purpose:** Ensure technical security is legally binding.

**Quick Test:**
```bash
# View registry
cat 24_meta_orchestration/registry/agent_stack.yaml

# Check git history (append-only)
git log 24_meta_orchestration/registry/agent_stack.yaml

# View compliance report
cat 05_documentation/compliance/5_LAYER_ENFORCEMENT_COMPLIANCE_REPORT.md
```

**Key Files:**
- Registry: `24_meta_orchestration/registry/agent_stack.yaml`
- Compliance report: `05_documentation/compliance/5_LAYER_ENFORCEMENT_COMPLIANCE_REPORT.md`
- Architecture doc: `23_compliance/architecture/5_LAYER_SOT_ENFORCEMENT.md`

---

## Common Commands

### Run Everything

```bash
# Full audit pipeline (all 5 layers)
python 02_audit_logging/pipeline/run_audit_pipeline.py

# All integration tests
pytest 11_test_simulation/tests_sot/test_5_layer_integration.py -v

# Metrics server
python 17_observability/sot_metrics.py
```

### Run Specific Layer

```bash
# Layer 1 only
python 02_audit_logging/pipeline/run_audit_pipeline.py --layer 1

# Layer 2 only
python 02_audit_logging/pipeline/run_audit_pipeline.py --layer 2

# etc.
```

### CI Mode

```bash
# Fail if compliance < 95%
python 02_audit_logging/pipeline/run_audit_pipeline.py --ci
```

---

## Troubleshooting

### Issue: OPA not found

```bash
# Install OPA
wget https://openpolicyagent.org/downloads/latest/opa_linux_amd64
chmod +x opa_linux_amd64
sudo mv opa_linux_amd64 /usr/local/bin/opa
```

### Issue: Merkle lock fails

**Cause:** Validation results missing

**Fix:**
```bash
# Run SoT validator first
python 03_core/validators/sot/sot_validator_core.py

# Then run Merkle lock
python 23_compliance/merkle/root_write_merkle_lock.py
```

### Issue: Compliance score < 100%

**Check:**
```bash
# View detailed errors
cat 02_audit_logging/reports/audit_pipeline_result.json | jq '.errors'

# Re-run validator
python 03_core/validators/sot/sot_validator_core.py
```

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│              Layer 5: Governance                        │
│  Registry + Dual Review + Legal Anchoring              │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│            Layer 4: Observability                       │
│  Telemetry + Audit Pipeline + Scorecard                │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│            Layer 3: Trust Boundary                      │
│  DID + Zero-Time-Auth + Non-Custodial Proofs           │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│          Layer 2: Policy Enforcement                    │
│  OPA/Rego + SoT Validator + CI/CD Hooks                │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│        Layer 1: Cryptographic Security                  │
│  Merkle Tree + PQC Signatures + WORM Logging           │
└─────────────────────────────────────────────────────────┘
```

---

## Next Steps

1. **Read Full Architecture:** `23_compliance/architecture/5_LAYER_SOT_ENFORCEMENT.md`
2. **View Compliance Report:** `05_documentation/compliance/5_LAYER_ENFORCEMENT_COMPLIANCE_REPORT.md`
3. **Set Up CI/CD:** Configure `.github/workflows/sot_auto_verify.yml`
4. **Deploy Metrics:** Set up Prometheus + Grafana for monitoring

---

## Support

- **Documentation:** `05_documentation/`
- **Tests:** `11_test_simulation/tests_sot/`
- **Issues:** GitHub Issues (repository)

---

**Happy Enforcing! 🔒**
