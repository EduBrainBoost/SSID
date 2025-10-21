from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Any

BFT_THRESHOLD = 0.67  # >= 2/3

@dataclass
class NodeAttestation:
    node_id: str
    merkle_root: str
    signature: bytes  # PQC-ready; upstream module handles Dilithium verify
    region: str

@dataclass
class ConsensusResult:
    merkle_root: str
    agree_ratio: float
    participants: int
    decided: bool
    dissent: List[str]

class ConsensusValidator:
    def __init__(self, verify_signature):
        """
        verify_signature(node_id:str, payload:bytes, signature:bytes) -> bool
        Dependency-injected PQC verifier (Dilithium).
        """
        self.verify_signature = verify_signature

    def decide(self, attestations: List[NodeAttestation]) -> ConsensusResult:
        if not attestations:
            return ConsensusResult("", 0.0, 0, False, [])
        # majority root
        counts: Dict[str,int] = {}
        for a in attestations:
            counts[a.merkle_root] = counts.get(a.merkle_root, 0) + 1
        root = max(counts.items(), key=lambda kv: kv[1])[0]
        ok_nodes = []
        for a in attestations:
            # payload = root || node_id (domain-separated)
            payload = (root + "|" + a.node_id).encode("utf-8")
            if a.merkle_root == root and self.verify_signature(a.node_id, payload, a.signature):
                ok_nodes.append(a.node_id)
        ratio = len(ok_nodes) / max(1, len(attestations))
        decided = ratio >= BFT_THRESHOLD
        dissent = [a.node_id for a in attestations if a.node_id not in ok_nodes]
        return ConsensusResult(root, ratio, len(attestations), decided, dissent)
