#!/usr/bin/env python3
"""
SSID Federated Evidence Node
Peer-to-Peer Audit Network Implementation

Enables SSID instances to mutually verify and cross-sign compliance anchors
in a decentralized network without central oversight.
"""

import hashlib
import json
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set
import hmac
import secrets

class NodeRole(Enum):
    """Node roles in federation network"""
    VALIDATOR = "validator"
    OBSERVER = "observer"
    AUDITOR = "auditor"

class VerificationResult(Enum):
    """Anchor verification results"""
    PASS = "PASS"
    FAIL = "FAIL"
    PENDING = "PENDING"

@dataclass
class PeerNode:
    """Represents a peer node in the federation"""
    node_id: str
    public_key: str
    endpoint: str
    role: NodeRole
    last_seen: datetime
    reputation_score: float = 1.0
    total_verifications: int = 0
    successful_verifications: int = 0

@dataclass
class ComplianceAnchor:
    """Compliance anchor to be verified"""
    anchor_hash: str
    timestamp: datetime
    node_id: str
    evidence_summary: Dict
    signature: str
    merkle_root: str

@dataclass
class CrossSignature:
    """Cross-signature from validator peer"""
    signer_node_id: str
    anchor_hash: str
    verification_result: VerificationResult
    timestamp: datetime
    signature: str
    verification_details: Dict = field(default_factory=dict)

@dataclass
class FederatedAnchor:
    """Anchor with federation metadata"""
    anchor: ComplianceAnchor
    cross_signatures: List[CrossSignature] = field(default_factory=list)
    consensus_reached: bool = False
    consensus_timestamp: Optional[datetime] = None
    distributed_hash: Optional[str] = None

class FederationNode:
    """
    Federated Evidence Node Implementation

    Manages peer connections, anchor verification, and cross-signing
    in the decentralized audit network.
    """

    def __init__(
        self,
        node_id: str,
        private_key: str,
        public_key: str,
        role: NodeRole = NodeRole.VALIDATOR,
        data_dir: Path = Path("./federation_data")
    ):
        self.node_id = node_id
        self.private_key = private_key
        self.public_key = public_key
        self.role = role
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Network state
        self.peers: Dict[str, PeerNode] = {}
        self.pending_anchors: Dict[str, FederatedAnchor] = {}
        self.verified_anchors: Dict[str, FederatedAnchor] = {}

        # Configuration
        self.min_peer_signatures = 3
        self.consensus_threshold = 0.66
        self.heartbeat_interval = 300  # seconds
        self.max_anchors_per_hour = 10
        self.sync_interval = 3600  # seconds

        # Rate limiting
        self.anchor_proposals: List[datetime] = []

        # Metrics
        self.metrics = {
            "total_anchors_proposed": 0,
            "total_anchors_verified": 0,
            "total_cross_signatures": 0,
            "consensus_achieved": 0,
            "byzantine_detections": 0
        }

    def add_peer(self, peer: PeerNode) -> bool:
        """Add peer to federation network"""
        if peer.node_id == self.node_id:
            return False

        self.peers[peer.node_id] = peer
        print(f"[Federation] Added peer: {peer.node_id} ({peer.role.value})")
        return True

    def remove_peer(self, node_id: str) -> bool:
        """Remove peer from network"""
        if node_id in self.peers:
            del self.peers[node_id]
            print(f"[Federation] Removed peer: {node_id}")
            return True
        return False

    def announce_anchor(self, anchor: ComplianceAnchor) -> bool:
        """
        Announce new compliance anchor to network

        Implements rate limiting and broadcasts to all validator peers
        """
        # Check rate limit
        if not self._check_rate_limit():
            print(f"[Federation] Rate limit exceeded for anchor proposals")
            return False

        # Create federated anchor
        fed_anchor = FederatedAnchor(anchor=anchor)
        self.pending_anchors[anchor.anchor_hash] = fed_anchor

        # Record proposal
        self.anchor_proposals.append(datetime.now())
        self.metrics["total_anchors_proposed"] += 1

        # Broadcast to validator peers
        validators = [p for p in self.peers.values() if p.role == NodeRole.VALIDATOR]
        print(f"[Federation] Broadcasting anchor {anchor.anchor_hash[:16]}... to {len(validators)} validators")

        # In production, this would make HTTP requests to peer endpoints
        # For now, simulate announcement
        for peer in validators:
            self._send_anchor_announcement(peer, anchor)

        return True

    def verify_anchor(self, anchor: ComplianceAnchor) -> VerificationResult:
        """
        Independently verify compliance anchor

        Performs cryptographic and policy validation
        """
        checks = {
            "signature_valid": False,
            "merkle_root_valid": False,
            "timestamp_valid": False,
            "evidence_complete": False,
            "policy_compliant": False
        }

        try:
            # 1. Signature verification
            checks["signature_valid"] = self._verify_signature(
                anchor.anchor_hash,
                anchor.signature,
                anchor.node_id
            )

            # 2. Merkle root validation
            checks["merkle_root_valid"] = self._verify_merkle_root(
                anchor.evidence_summary,
                anchor.merkle_root
            )

            # 3. Timestamp validity (not too far in future/past)
            now = datetime.now()
            time_diff = abs((anchor.timestamp - now).total_seconds())
            checks["timestamp_valid"] = time_diff < 300  # 5 minutes tolerance

            # 4. Evidence completeness
            required_fields = ["compliance_controls", "framework_coverage", "risk_assessment"]
            checks["evidence_complete"] = all(
                field in anchor.evidence_summary for field in required_fields
            )

            # 5. Policy compliance
            checks["policy_compliant"] = self._verify_policy_compliance(
                anchor.evidence_summary
            )

            # All checks must pass
            all_passed = all(checks.values())

            print(f"[Federation] Verification for {anchor.anchor_hash[:16]}...")
            for check, result in checks.items():
                print(f"  - {check}: {'✓' if result else '✗'}")

            return VerificationResult.PASS if all_passed else VerificationResult.FAIL

        except Exception as e:
            print(f"[Federation] Verification error: {e}")
            return VerificationResult.FAIL

    def cross_sign_anchor(self, anchor_hash: str) -> Optional[CrossSignature]:
        """
        Generate cross-signature for verified anchor

        Only validators can cross-sign
        """
        if self.role != NodeRole.VALIDATOR:
            print(f"[Federation] Only validators can cross-sign anchors")
            raise NotImplementedError("TODO: Implement this function")

        if anchor_hash not in self.pending_anchors:
            print(f"[Federation] Anchor {anchor_hash[:16]}... not found")
            raise NotImplementedError("TODO: Implement this function")

        fed_anchor = self.pending_anchors[anchor_hash]

        # Perform verification
        result = self.verify_anchor(fed_anchor.anchor)

        # Create cross-signature
        cross_sig = CrossSignature(
            signer_node_id=self.node_id,
            anchor_hash=anchor_hash,
            verification_result=result,
            timestamp=datetime.now(),
            signature=self._sign_data(anchor_hash),
            verification_details={
                "node_role": self.role.value,
                "verification_timestamp": datetime.now().isoformat()
            }
        )

        # Add to federated anchor
        fed_anchor.cross_signatures.append(cross_sig)

        self.metrics["total_cross_signatures"] += 1

        print(f"[Federation] Cross-signed anchor {anchor_hash[:16]}... with result: {result.value}")

        # Check for consensus
        self._check_consensus(anchor_hash)

        return cross_sig

    def receive_cross_signature(self, anchor_hash: str, cross_sig: CrossSignature) -> bool:
        """
        Receive and validate cross-signature from peer
        """
        if anchor_hash not in self.pending_anchors:
            print(f"[Federation] Anchor {anchor_hash[:16]}... not found for cross-signature")
            return False

        # Verify signature authenticity
        if not self._verify_cross_signature(cross_sig):
            print(f"[Federation] Invalid cross-signature from {cross_sig.signer_node_id[:16]}...")
            self._flag_byzantine_node(cross_sig.signer_node_id)
            return False

        # Add to anchor
        fed_anchor = self.pending_anchors[anchor_hash]
        fed_anchor.cross_signatures.append(cross_sig)

        print(f"[Federation] Received valid cross-signature from {cross_sig.signer_node_id[:16]}...")

        # Check for consensus
        self._check_consensus(anchor_hash)

        return True

    def _check_consensus(self, anchor_hash: str) -> bool:
        """
        Check if threshold consensus reached for anchor
        """
        if anchor_hash not in self.pending_anchors:
            return False

        fed_anchor = self.pending_anchors[anchor_hash]

        # Count PASS signatures
        pass_count = sum(
            1 for sig in fed_anchor.cross_signatures
            if sig.verification_result == VerificationResult.PASS
        )

        # Check threshold
        if pass_count >= self.min_peer_signatures:
            fed_anchor.consensus_reached = True
            fed_anchor.consensus_timestamp = datetime.now()
            fed_anchor.distributed_hash = self._compute_distributed_hash(fed_anchor)

            # Move to verified
            self.verified_anchors[anchor_hash] = fed_anchor
            del self.pending_anchors[anchor_hash]

            self.metrics["consensus_achieved"] += 1
            self.metrics["total_anchors_verified"] += 1

            print(f"[Federation] ✓ CONSENSUS REACHED for anchor {anchor_hash[:16]}...")
            print(f"  - Signatures: {pass_count}/{len(fed_anchor.cross_signatures)}")
            print(f"  - Distributed hash: {fed_anchor.distributed_hash[:16]}...")

            return True

        return False

    def get_federation_status(self) -> Dict:
        """Get federation network status"""
        validator_count = sum(1 for p in self.peers.values() if p.role == NodeRole.VALIDATOR)

        return {
            "node_id": self.node_id[:16] + "...",
            "role": self.role.value,
            "peer_count": len(self.peers),
            "validator_count": validator_count,
            "pending_anchors": len(self.pending_anchors),
            "verified_anchors": len(self.verified_anchors),
            "metrics": self.metrics,
            "network_health": self._compute_network_health()
        }

    def export_federated_anchor(self, anchor_hash: str, output_path: Path) -> bool:
        """Export federated anchor with all cross-signatures"""
        if anchor_hash not in self.verified_anchors:
            print(f"[Federation] Anchor {anchor_hash[:16]}... not verified")
            return False

        fed_anchor = self.verified_anchors[anchor_hash]

        export_data = {
            "anchor": {
                "hash": fed_anchor.anchor.anchor_hash,
                "timestamp": fed_anchor.anchor.timestamp.isoformat(),
                "node_id": fed_anchor.anchor.node_id,
                "merkle_root": fed_anchor.anchor.merkle_root,
                "evidence_summary": fed_anchor.anchor.evidence_summary
            },
            "federation": {
                "cross_signatures": [
                    {
                        "signer": sig.signer_node_id,
                        "result": sig.verification_result.value,
                        "timestamp": sig.timestamp.isoformat(),
                        "signature": sig.signature
                    }
                    for sig in fed_anchor.cross_signatures
                ],
                "consensus_reached": fed_anchor.consensus_reached,
                "consensus_timestamp": fed_anchor.consensus_timestamp.isoformat() if fed_anchor.consensus_timestamp else None,
                "distributed_hash": fed_anchor.distributed_hash
            },
            "metadata": {
                "exported_at": datetime.now().isoformat(),
                "exported_by": self.node_id,
                "protocol_version": "1.0.0"
            }
        }

        output_path.write_text(json.dumps(export_data, indent=2))
        print(f"[Federation] Exported federated anchor to {output_path}")
        return True

    # Private helper methods

    def _check_rate_limit(self) -> bool:
        """Check anchor proposal rate limit"""
        cutoff = datetime.now() - timedelta(hours=1)
        self.anchor_proposals = [t for t in self.anchor_proposals if t > cutoff]
        return len(self.anchor_proposals) < self.max_anchors_per_hour

    def _send_anchor_announcement(self, peer: PeerNode, anchor: ComplianceAnchor):
        """Send anchor announcement to peer (mock)"""
        # In production: HTTP POST to peer.endpoint/api/v1/federation/announce
        raise NotImplementedError("TODO: Implement this block")

    def _verify_signature(self, data: str, signature: str, signer_id: str) -> bool:
        """Verify Ed25519 signature (mock)"""
        # In production: Use ed25519 library
        return True

    def _verify_merkle_root(self, evidence: Dict, merkle_root: str) -> bool:
        """Verify merkle root matches evidence (mock)"""
        # In production: Reconstruct merkle tree and compare roots
        computed_root = hashlib.sha256(json.dumps(evidence, sort_keys=True).encode()).hexdigest()
        return computed_root[:32] == merkle_root[:32]  # Simplified check

    def _verify_policy_compliance(self, evidence: Dict) -> bool:
        """Verify evidence meets policy requirements"""
        # Check minimum compliance coverage
        if "framework_coverage" in evidence:
            coverage = evidence["framework_coverage"]
            return all(float(v.strip('%')) >= 80 for v in coverage.values() if isinstance(v, str))
        return False

    def _sign_data(self, data: str) -> str:
        """Sign data with node's private key (mock)"""
        # In production: Use ed25519 signature
        return hmac.new(
            self.private_key.encode(),
            data.encode(),
            hashlib.sha256
        ).hexdigest()

    def _verify_cross_signature(self, cross_sig: CrossSignature) -> bool:
        """Verify cross-signature authenticity"""
        # In production: Verify Ed25519 signature
        if cross_sig.signer_node_id not in self.peers:
            return False
        return True

    def _flag_byzantine_node(self, node_id: str):
        """Flag potentially malicious node"""
        if node_id in self.peers:
            self.peers[node_id].reputation_score *= 0.5
            self.metrics["byzantine_detections"] += 1
            print(f"[Federation] ⚠️  Flagged Byzantine node: {node_id[:16]}...")

    def _compute_distributed_hash(self, fed_anchor: FederatedAnchor) -> str:
        """Compute distributed hash including all cross-signatures"""
        sig_data = "".join(sorted([
            sig.signature for sig in fed_anchor.cross_signatures
        ]))
        combined = fed_anchor.anchor.anchor_hash + sig_data
        return hashlib.sha256(combined.encode()).hexdigest()

    def _compute_network_health(self) -> str:
        """Compute overall network health"""
        if len(self.peers) < 3:
            return "DEGRADED"

        validator_count = sum(1 for p in self.peers.values() if p.role == NodeRole.VALIDATOR)
        if validator_count < 3:
            return "DEGRADED"

        avg_reputation = sum(p.reputation_score for p in self.peers.values()) / len(self.peers)
        if avg_reputation < 0.7:
            return "UNHEALTHY"

        return "HEALTHY"

def demo_federation_network():
    """Demonstrate federated evidence network"""
    print("=== SSID Federated Evidence Network Demo ===\n")

    # Create 4 validator nodes
    nodes = []
    for i in range(4):
        node = FederationNode(
            node_id=f"node_{i}_{secrets.token_hex(8)}",
            private_key=secrets.token_hex(32),
            public_key=secrets.token_hex(32),
            role=NodeRole.VALIDATOR
        )
        nodes.append(node)

    # Connect nodes as peers
    print("1. Building peer network...")
    for node in nodes:
        for other in nodes:
            if node != other:
                peer = PeerNode(
                    node_id=other.node_id,
                    public_key=other.public_key,
                    endpoint=f"https://node-{other.node_id[:8]}.example.com",
                    role=other.role,
                    last_seen=datetime.now()
                )
                node.add_peer(peer)
    print(f"   Network established with {len(nodes)} nodes\n")

    # Node 0 proposes an anchor
    print("2. Node 0 proposes compliance anchor...")
    anchor = ComplianceAnchor(
        anchor_hash=hashlib.sha256(secrets.token_bytes(32)).hexdigest(),
        timestamp=datetime.now(),
        node_id=nodes[0].node_id,
        evidence_summary={
            "compliance_controls": ["UNI-SR-001", "UNI-CR-001", "UNI-AL-001"],
            "framework_coverage": {"gdpr": "95%", "dora": "92%", "mica": "88%"},
            "risk_assessment": {"critical": 0, "high": 2, "medium": 5}
        },
        signature=nodes[0]._sign_data("anchor_data"),
        merkle_root=hashlib.sha256(b"evidence_tree").hexdigest()
    )
    nodes[0].announce_anchor(anchor)
    print()

    # Other nodes cross-sign
    print("3. Validators cross-signing anchor...")
    for i, node in enumerate(nodes[1:], 1):
        # Simulate receiving anchor
        node.pending_anchors[anchor.anchor_hash] = FederatedAnchor(anchor=anchor)

        # Cross-sign
        cross_sig = node.cross_sign_anchor(anchor.anchor_hash)

        # Send back to proposer
        if cross_sig:
            nodes[0].receive_cross_signature(anchor.anchor_hash, cross_sig)

        time.sleep(0.1)
    print()

    # Check status
    print("4. Federation Status:")
    for i, node in enumerate(nodes):
        status = node.get_federation_status()
        print(f"\n   Node {i}:")
        print(f"   - Role: {status['role']}")
        print(f"   - Peers: {status['peer_count']}")
        print(f"   - Verified anchors: {status['verified_anchors']}")
        print(f"   - Consensus achieved: {status['metrics']['consensus_achieved']}")
        print(f"   - Network health: {status['network_health']}")

    # Export federated anchor
    print("\n5. Exporting federated anchor...")
    export_path = Path("./federated_anchor_export.json")
    if nodes[0].export_federated_anchor(anchor.anchor_hash, export_path):
        print(f"   ✓ Exported to {export_path}")

    print("\n=== Demo Complete ===")

if __name__ == "__main__":
    demo_federation_network()
