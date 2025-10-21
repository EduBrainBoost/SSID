#!/usr/bin/env python3
"""
Federation Node Ranking - Performance-Based Governance
=======================================================

Ranks federation nodes based on proof throughput, validation accuracy,
and consensus participation. Used for Proof Credit Allocation and
Governance Weight determination.

Features:
- Real-time node performance tracking
- Throughput ranking (proof_rate_per_sec)
- Validation accuracy scoring
- Governance weight calculation
- MiCA-compliant (utility-based, non-custodial)

Status: Phase 1.5+ (AMP Integration)
Version: 1.0.0
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class FederationNodeMetrics:
    """
    Performance metrics for a single federation node.
    """
    node_id: str
    region: str
    federation_zone: str

    # Proof stream metrics
    proofs_processed: int
    proof_rate_per_sec: float
    total_latency_ms: float
    avg_latency_ms: float

    # Validation metrics
    validation_accuracy: float  # 0.0-1.0
    validations_performed: int
    false_positives: int
    false_negatives: int

    # Consensus metrics
    consensus_participation: float  # 0.0-1.0
    consensus_rounds: int
    consensus_agreements: int

    # Storage metrics
    storage_contribution_gb: float

    # Availability
    uptime_percent: float
    last_seen: float  # timestamp

    # Ranking score (computed)
    performance_score: float = 0.0
    rank: int = 0


@dataclass
class FederationRanking:
    """
    Ranking of all federation nodes.
    """
    timestamp: str
    total_nodes: int
    nodes: List[FederationNodeMetrics]

    # Aggregated statistics
    avg_proof_rate: float
    total_proofs_processed: int
    highest_performer: str  # node_id
    lowest_performer: str   # node_id


class FederationNodeRanker:
    """
    Ranks federation nodes based on performance metrics.

    Ranking formula:
    performance_score = (
        proof_rate_per_sec * 0.30 +
        validation_accuracy * 100 * 0.25 +
        consensus_participation * 100 * 0.20 +
        uptime_percent * 0.15 +
        (1 - (avg_latency_ms / 1000)) * 100 * 0.10
    )
    """

    def __init__(
        self,
        telemetry_sink=None,
        ranking_output_path: str = "17_observability/federation_ranking.json"
    ):
        """
        Initialize federation node ranker.

        Args:
            telemetry_sink: AuditTelemetrySink instance (for live metrics)
            ranking_output_path: Path to ranking output (JSON)
        """
        self.telemetry_sink = telemetry_sink
        self.ranking_output_path = Path(ranking_output_path)
        self.ranking_output_path.parent.mkdir(parents=True, exist_ok=True)

        # Node registry
        self.nodes: Dict[str, FederationNodeMetrics] = {}

    def update_node_metrics(
        self,
        node_id: str,
        metrics: Dict[str, Any]
    ) -> None:
        """
        Update metrics for a specific node.

        Args:
            node_id: Node identifier
            metrics: Metrics dict from telemetry
        """
        if node_id not in self.nodes:
            # Initialize new node
            self.nodes[node_id] = FederationNodeMetrics(
                node_id=node_id,
                region=metrics.get("region", "unknown"),
                federation_zone=metrics.get("federation_zone", "unknown"),
                proofs_processed=0,
                proof_rate_per_sec=0.0,
                total_latency_ms=0.0,
                avg_latency_ms=0.0,
                validation_accuracy=1.0,
                validations_performed=0,
                false_positives=0,
                false_negatives=0,
                consensus_participation=0.0,
                consensus_rounds=0,
                consensus_agreements=0,
                storage_contribution_gb=0.0,
                uptime_percent=100.0,
                last_seen=time.time()
            )

        node = self.nodes[node_id]

        # Update metrics
        node.proofs_processed = metrics.get("events_processed", node.proofs_processed)
        node.total_latency_ms = metrics.get("total_latency_ms", node.total_latency_ms)

        if node.proofs_processed > 0:
            node.avg_latency_ms = node.total_latency_ms / node.proofs_processed

        # Proof rate (from telemetry)
        uptime = time.time() - node.last_seen
        if uptime > 0:
            node.proof_rate_per_sec = node.proofs_processed / uptime

        node.last_seen = time.time()

        # Update validation/consensus metrics (if provided)
        if "validation_accuracy" in metrics:
            node.validation_accuracy = metrics["validation_accuracy"]
        if "consensus_participation" in metrics:
            node.consensus_participation = metrics["consensus_participation"]
        if "storage_contribution_gb" in metrics:
            node.storage_contribution_gb = metrics["storage_contribution_gb"]

        # Compute performance score
        node.performance_score = self._compute_performance_score(node)

    def _compute_performance_score(self, node: FederationNodeMetrics) -> float:
        """
        Compute performance score for a node.

        Formula:
        score = (
            proof_rate * 0.30 +
            validation_accuracy * 100 * 0.25 +
            consensus_participation * 100 * 0.20 +
            uptime_percent * 0.15 +
            (1 - (avg_latency_ms / 1000)) * 100 * 0.10
        )
        """
        # Normalize latency (cap at 1000ms)
        latency_score = max(0, 1 - (node.avg_latency_ms / 1000))

        score = (
            node.proof_rate_per_sec * 0.30 +
            node.validation_accuracy * 100 * 0.25 +
            node.consensus_participation * 100 * 0.20 +
            node.uptime_percent * 0.15 +
            latency_score * 100 * 0.10
        )

        return round(score, 2)

    def compute_ranking(self) -> FederationRanking:
        """
        Compute ranking of all federation nodes.

        Returns:
            FederationRanking with sorted nodes
        """
        # Sort nodes by performance score
        sorted_nodes = sorted(
            self.nodes.values(),
            key=lambda n: n.performance_score,
            reverse=True
        )

        # Assign ranks
        for rank, node in enumerate(sorted_nodes, start=1):
            node.rank = rank

        # Compute aggregated statistics
        total_proofs = sum(n.proofs_processed for n in sorted_nodes)
        avg_proof_rate = sum(n.proof_rate_per_sec for n in sorted_nodes) / len(sorted_nodes) if sorted_nodes else 0

        highest_performer = sorted_nodes[0].node_id if sorted_nodes else "none"
        lowest_performer = sorted_nodes[-1].node_id if sorted_nodes else "none"

        ranking = FederationRanking(
            timestamp=datetime.utcnow().isoformat() + "Z",
            total_nodes=len(sorted_nodes),
            nodes=sorted_nodes,
            avg_proof_rate=round(avg_proof_rate, 2),
            total_proofs_processed=total_proofs,
            highest_performer=highest_performer,
            lowest_performer=lowest_performer
        )

        return ranking

    def publish_ranking(self) -> None:
        """Publish ranking to JSON file."""
        ranking = self.compute_ranking()

        # Convert to dict
        ranking_dict = {
            "timestamp": ranking.timestamp,
            "total_nodes": ranking.total_nodes,
            "avg_proof_rate": ranking.avg_proof_rate,
            "total_proofs_processed": ranking.total_proofs_processed,
            "highest_performer": ranking.highest_performer,
            "lowest_performer": ranking.lowest_performer,
            "nodes": [asdict(node) for node in ranking.nodes]
        }

        # Write to file
        with self.ranking_output_path.open("w", encoding="utf-8") as f:
            json.dump(ranking_dict, f, indent=2)

    def get_governance_weights(self) -> Dict[str, float]:
        """
        Get governance weights for all nodes.

        Governance weight = performance_score / max_performance_score
        (Capped at 1.0)

        Returns:
            Dict of node_id → governance_weight
        """
        ranking = self.compute_ranking()

        if not ranking.nodes:
            return {}

        max_score = ranking.nodes[0].performance_score  # Highest performer

        weights = {}
        for node in ranking.nodes:
            weight = min(node.performance_score / max_score, 1.0) if max_score > 0 else 0.0
            weights[node.node_id] = round(weight, 4)

        return weights


# Example usage
if __name__ == "__main__":
    print("Federation Node Ranking - Test")
    print("=" * 70)

    # Create ranker
    ranker = FederationNodeRanker()

    # Simulate metrics for 3 nodes
    ranker.update_node_metrics("eu-node-001", {
        "region": "eu-west-1",
        "federation_zone": "eu",
        "events_processed": 10000,
        "total_latency_ms": 150000.0,
        "validation_accuracy": 0.98,
        "consensus_participation": 0.95,
        "storage_contribution_gb": 500.0
    })

    ranker.update_node_metrics("us-node-002", {
        "region": "us-east-1",
        "federation_zone": "us",
        "events_processed": 8000,
        "total_latency_ms": 120000.0,
        "validation_accuracy": 0.96,
        "consensus_participation": 0.90,
        "storage_contribution_gb": 450.0
    })

    ranker.update_node_metrics("apac-node-003", {
        "region": "ap-southeast-1",
        "federation_zone": "apac",
        "events_processed": 5000,
        "total_latency_ms": 100000.0,
        "validation_accuracy": 0.94,
        "consensus_participation": 0.85,
        "storage_contribution_gb": 300.0
    })

    # Compute ranking
    ranking = ranker.compute_ranking()

    print(f"Timestamp: {ranking.timestamp}")
    print(f"Total Nodes: {ranking.total_nodes}")
    print(f"Avg Proof Rate: {ranking.avg_proof_rate} proofs/sec")
    print(f"Total Proofs: {ranking.total_proofs_processed}")
    print()

    print("Node Rankings:")
    for node in ranking.nodes:
        print(f"  Rank {node.rank}: {node.node_id}")
        print(f"    Performance Score: {node.performance_score}")
        print(f"    Proof Rate: {node.proof_rate_per_sec:.2f} proofs/sec")
        print(f"    Validation Accuracy: {node.validation_accuracy:.2%}")
        print(f"    Consensus Participation: {node.consensus_participation:.2%}")
        print()

    # Governance weights
    weights = ranker.get_governance_weights()

    print("Governance Weights:")
    for node_id, weight in weights.items():
        print(f"  {node_id}: {weight:.4f}")

    # Publish ranking
    ranker.publish_ranking()

    print("=" * 70)
    print("[OK] Federation Ranking Test Complete")
    print(f"Ranking published to: {ranker.ranking_output_path}")
