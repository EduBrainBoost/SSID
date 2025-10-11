# Registry Events Directory

**Blueprint v4.2.1 - Governance Event Registry**

## Overview

This directory contains structured event logs for all governance-related actions in the SSID system. Every significant change (Blueprint promotion, compliance audit, proof emission) is automatically logged here with cryptographic proof-anchors.

## Event Types

### Blueprint Events
- `governance_bootstrap` - Initial governance system activation
- `blueprint_promoted` - New Blueprint version activated
- `blueprint_archived` - Previous Blueprint version archived
- `release_tagged` - Version tag created

### Compliance Events
- `automated_quarterly_audit` - Scheduled quarterly audit completed
- `manual_audit_triggered` - Manual audit execution
- `compliance_report_generated` - Compliance report created
- `violations_detected` - Structure violations identified
- `violations_remediated` - Violations resolved

### Dashboard Events
- `governance_dashboard_added` - Dashboard system created
- `dashboard_updated` - Dashboard metrics refreshed
- `ci_automation_added` - CI/CD automation enabled

### Proof Events
- `proof_anchor_emitted` - Cryptographic proof-anchor generated
- `external_proof_anchored` - Proof anchored to external system (IPFS/blockchain)
- `proof_verified` - External proof verification completed

## Event Structure

All events are logged as JSON objects with the following structure:

```json
{
  "timestamp": "2025-10-11T16:01:22Z",
  "event": "governance_bootstrap",
  "version": "v4.2.1",
  "commit_hash": "5110f342abc64a6775972d9214e33206a5af15b1",
  "blueprint": "v4.2",
  "root_24_lock": "active",
  "compliance_score": "100/100",
  "emitted_by": "registry_event_trigger.sh"
}
```

## Proof-Anchor Generation

Each event generates a SHA256 proof-anchor by hashing the complete event JSON. This anchor provides:
- **Tamper-Proof Evidence:** Cannot be altered without detection
- **Cryptographic Verification:** Independently verifiable
- **Audit Trail:** Complete history of governance actions
- **External Anchoring:** Can be published to IPFS/blockchain

## Event Log Location

**Primary Log:** `24_meta_orchestration/registry/logs/registry_events.log`
**Event Directory:** `24_meta_orchestration/registry/events/`

## Triggering Events

### Manual Event Emission

```bash
bash 12_tooling/scripts/registry_event_trigger.sh \
  --event "<EVENT_TYPE>" \
  --version "<VERSION>" \
  --hash "$(git rev-parse HEAD)"
```

### Automated Event Emission

Events are automatically emitted by:
- `run_quarterly_audit.sh` - Quarterly compliance audits
- `.github/workflows/quarterly_audit.yml` - Automated audit workflow
- `update_governance_dashboard.py` - Dashboard updates
- Manual script invocations

## Event Verification

### Verify Event Integrity

```bash
# View recent events
tail -n 20 24_meta_orchestration/registry/logs/registry_events.log

# Verify proof-anchor
echo '<PROOF_ANCHOR>' | sha256sum -c
```

### Query Events by Type

```bash
# Find all audit events
grep -A 8 '"event": "automated_quarterly_audit"' \
  24_meta_orchestration/registry/logs/registry_events.log

# Find all bootstrap events
grep -A 8 '"event": "governance_bootstrap"' \
  24_meta_orchestration/registry/logs/registry_events.log
```

## External Anchoring

For maximum tamper-proof verification, anchor proof-hashes to external systems:

### IPFS (Free, Decentralized)
```bash
ipfs add 24_meta_orchestration/registry/logs/registry_events.log
# Returns CID for permanent, decentralized storage
```

### Blockchain (Ethereum/Polygon)
```bash
cast send $CONTRACT "anchorProof(bytes32,string,string)" \
  0x<PROOF_ANCHOR> "v4.2.1" "github.com/EduBrainBoost/SSID" \
  --rpc-url $RPC_URL --private-key $PRIVATE_KEY
```

See: `05_documentation/PROOF_ANCHORING_GUIDE.md` for complete instructions.

## Event Lifecycle

1. **Governance Action Occurs** (audit, release, promotion)
2. **Event Triggered** via `registry_event_trigger.sh`
3. **JSON Event Created** with timestamp and metadata
4. **Proof-Anchor Generated** (SHA256 hash)
5. **Event Logged** to `registry_events.log`
6. **Optional: External Anchoring** to IPFS/blockchain

## Retention Policy

- **Primary Log:** Permanent retention (Git-tracked)
- **Proof-Anchors:** Permanent cryptographic record
- **External Anchors:** Permanent (IPFS/blockchain immutability)

## Governance Bootstrap Event

**First Event:** `governance_bootstrap` (2025-10-11T16:01:22Z)
**Version:** v4.2.1
**Commit:** `5110f342abc64a6775972d9214e33206a5af15b1`
**Proof-Anchor:** `ed83883ffcc664cf5a5c264e9daa04f702450aa4b1cc3a23d35786fcfc25cfe1`

This event marks the activation of the complete governance system with:
- Automated quarterly audits
- CI/CD integration
- External proof-anchoring capability
- Audit comparison tools
- Real-time governance dashboard

## Monitoring

### Key Metrics to Track

- **Event Frequency:** Should align with audit/release schedule
- **Proof-Anchor Validity:** All anchors must be cryptographically valid
- **External Anchoring Status:** Track IPFS/blockchain anchoring
- **Compliance Score:** Must remain 100/100 across all events

### Alerts

Set up monitoring for:
- Compliance score degradation (< 100)
- Violation detection events
- Failed audit events
- Proof-anchor verification failures

## Related Documentation

- **Operations Guide:** `05_documentation/OPERATIONS_GUIDE.md`
- **Proof-Anchoring Guide:** `05_documentation/PROOF_ANCHORING_GUIDE.md`
- **Dashboard:** `05_documentation/reports/dashboard/SSID_Governance_Dashboard.md`
- **Promotion Rules:** `24_meta_orchestration/promotion_rules.yaml`

---

**Blueprint v4.2.1 Registry Events System**
_Activated: 2025-10-11_
_Status: ACTIVE_
_Compliance: 100/100_
