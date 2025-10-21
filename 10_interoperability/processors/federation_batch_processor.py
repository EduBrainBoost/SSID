from __future__ import annotations
import time, hashlib, json
from dataclasses import dataclass, field
from typing import Iterable, List, Dict, Any, Tuple

@dataclass(frozen=True)
class ProofItem:
    event_id: str
    payload_hash: str  # hex sha256 of canonical json
    node_id: str
    region: str
    ts: float

def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def canonical_json(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")

def build_merkle_root(items: List[ProofItem]) -> Tuple[str, List[Tuple[str,str]]]:
    """Returns (root_hex, list of (left,right) pair hashes for audit)."""
    if not items:
        return _sha256_hex(b""), []
    level = [bytes.fromhex(x.payload_hash) for x in items]
    audit_pairs: List[Tuple[str,str]] = []
    while len(level) > 1:
        nxt = []
        for i in range(0, len(level), 2):
            left = level[i]
            right = level[i+1] if i+1 < len(level) else left
            pair = left + right
            h = hashlib.sha256(pair).digest()
            nxt.append(h)
            audit_pairs.append((left.hex(), right.hex()))
        level = nxt
    return level[0].hex(), audit_pairs

@dataclass
class BatchResult:
    merkle_root: str
    count: int
    audit_pairs: List[Tuple[str,str]]
    duration_ms: int
    batch_id: str

class FederationBatchProcessor:
    def __init__(self, max_batch_size: int = 1000):
        self.max_batch_size = max_batch_size

    def process(self, events: Iterable[Dict[str, Any]], batch_id: str) -> BatchResult:
        t0 = time.perf_counter()
        items: List[ProofItem] = []
        for ev in events:
            payload = ev.get("payload", {})
            federation = ev.get("federation_context", {})
            ph = _sha256_hex(canonical_json(payload))
            items.append(ProofItem(
                event_id=ev.get("event_id",""),
                payload_hash=ph,
                node_id=federation.get("node_id",""),
                region=federation.get("region",""),
                ts=ev.get("ts", time.time()),
            ))
            if len(items) >= self.max_batch_size:
                break
        root, pairs = build_merkle_root(items)
        dt = int((time.perf_counter() - t0) * 1000)
        return BatchResult(root, len(items), pairs, dt, batch_id)
