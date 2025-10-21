import time, json, sys
from pathlib import Path

# Add processor to path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "10_interoperability" / "processors"))

from federation_batch_processor import FederationBatchProcessor, canonical_json

def test_merkle_root_stability_small_batch():
    evs = []
    for i in range(5):
        evs.append({
            "event_id": f"e{i}",
            "payload": {"x": i, "y": i*i},
            "federation_context": {"node_id":"eu-node-001","region":"eu-west-1"},
            "ts": time.time()
        })
    bp = FederationBatchProcessor(max_batch_size=1000)
    res = bp.process(evs, batch_id="b1")
    assert res.count == 5
    assert len(res.merkle_root) == 64  # SHA-256 hex
    # Re-run with SAME order -> deterministic root
    res2 = bp.process(evs, batch_id="b1")
    assert res.merkle_root == res2.merkle_root
    # Different order -> different root (Merkle trees are order-dependent)
    evs_reversed = list(reversed(evs))
    res3 = bp.process(evs_reversed, batch_id="b1")
    assert res.merkle_root != res3.merkle_root  # Order matters
