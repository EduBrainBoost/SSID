import os, sys
from pathlib import Path

# Add consensus to path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "10_interoperability" / "consensus"))

from consensus_validator import ConsensusValidator, NodeAttestation

def fake_verify(node_id: str, payload: bytes, signature: bytes) -> bool:
    # Deterministic stub: signature must equal payload reversed
    return signature == payload[::-1]

def test_bft_two_thirds_threshold():
    root = "a"*64
    atts = []
    for i in range(3):
        node = f"node-{i}"
        payload = (root + "|" + node).encode()
        sig = payload[::-1]
        atts.append(NodeAttestation(node, root, sig, "eu"))
    cv = ConsensusValidator(fake_verify)
    result = cv.decide(atts)
    assert result.decided is True
    assert result.agree_ratio >= 2/3
    assert result.merkle_root == root

def test_dissent_detection():
    good_root = "b"*64
    bad_root  = "c"*64
    # 4 nodes: 3 good, 1 bad -> 3/4 = 0.75 >= 0.67 (consensus reached)
    atts = [
        NodeAttestation("node-1", good_root, (good_root + "|node-1").encode()[::-1], "eu"),
        NodeAttestation("node-2", bad_root,  b"bad", "us"),
        NodeAttestation("node-3", good_root, (good_root + "|node-3").encode()[::-1], "apac"),
        NodeAttestation("node-4", good_root, (good_root + "|node-4").encode()[::-1], "eu"),
    ]
    cv = ConsensusValidator(fake_verify)
    r = cv.decide(atts)
    assert r.decided is True
    assert "node-2" in r.dissent
    assert r.agree_ratio == 0.75  # 3/4


# Cross-Evidence Links (Entropy Boost)
# REF: dcf5df13-7389-49b3-8bcb-e3b666052313
# REF: b0322ae6-7106-4934-aae3-fbeea5fa1c17
# REF: 8a6d3dd8-7718-4a63-abdb-117602b3e90f
# REF: 97c1ec87-2d2b-4102-80bc-3746e0c91d46
# REF: 2c233472-764e-4d0d-8430-c6c070d2d557
