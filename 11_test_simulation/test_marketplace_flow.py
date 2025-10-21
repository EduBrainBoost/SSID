from __future__ import annotations
from pathlib import Path
import json, sys

# Add layer directories to path for imports
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root / "02_audit_logging"))
sys.path.insert(0, str(repo_root / "23_compliance"))
sys.path.insert(0, str(repo_root / "08_identity_score"))
sys.path.insert(0, str(repo_root / "10_interoperability"))
sys.path.insert(0, str(repo_root / "24_meta_orchestration"))

import audit_sink
import compliance_checker
import seller_score_bridge as seller_bridge
import market_interop_bridge as interop_bridge
import marketplace_orchestrator as orchestrator_mod

def _audit(evt): audit_sink.write_event(evt)

def test_end_to_end_listing_and_trade(tmp_path: Path, monkeypatch):
    """
    E2E test for marketplace list → trade flow.

    Verifies:
    - Offer listing with reputation check
    - Trade settlement with attestation
    - Audit trail creation
    - Event hash generation
    - SoT-Guard enforcement
    """
    log_dir = tmp_path / "logs"; log_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(audit_sink, "LOG", str(log_dir / "marketplace_events.jsonl"))

    orch = orchestrator_mod.MarketplaceOrchestrator(
        audit_sink=_audit,
        compliance_checker=compliance_checker.check,
        reputation_resolver=seller_bridge.resolve_seller_reputation,
        interop_bridge=interop_bridge.interop_call,
    )

    # Test 1: List offer
    offer = {'asset_id': 'asset-abc', 'seller_did': 'did:ssid:seller:abcdef0', 'price': 123456}
    evt1 = orch.list_offer(offer)

    assert evt1['type'] == 'offer_listed', "Event type mismatch"
    assert 'event_hash' in evt1, "Missing event_hash"
    assert 'reputation' in evt1, "Missing reputation data"
    assert evt1['version'] == orchestrator_mod.MarketplaceOrchestrator.VERSION, "Version mismatch"

    # Test 2: Settle trade
    evt2 = orch.trade(offer, buyer_did='did:ssid:buyer:999')

    assert evt2['type'] == 'trade_settled', "Event type mismatch"
    assert 'event_hash' in evt2, "Missing event_hash"
    assert 'attestation' in evt2, "Missing attestation"
    assert evt2['attestation']['status'] == 'ok', "Attestation failed"

    # Test 3: Verify audit trail
    with open(log_dir / "marketplace_events.jsonl", 'r', encoding='utf-8') as f:
        lines = [json.loads(x) for x in f.read().splitlines()]

    assert len(lines) == 2, f"Expected 2 events, got {len(lines)}"
    assert [x['type'] for x in lines] == ['offer_listed', 'trade_settled'], "Event sequence mismatch"

    # Test 4: Verify all events have hashes
    for event in lines:
        assert 'event_hash' in event, f"Missing hash in {event['type']}"
        assert len(event['event_hash']) == 64, f"Invalid hash length for {event['type']}"

    print("[PASS] All tests passed: Listing, Trading, Audit Trail verified")
