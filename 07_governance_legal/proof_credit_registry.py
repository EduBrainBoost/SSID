#!/usr/bin/env python3
"""
Proof Credit Registry - MiCA-Compliant Utility Rewards
=======================================================

Manages proof credit allocation for federation nodes based on
performance metrics. Credits are utility tokens for governance weight
calculation, NOT monetary payments (non-custodial, MiCA Art.74).

Features:
- Performance-based credit allocation
- Governance weight calculation
- On-chain anchoring (audit trail)
- Non-custodial (no payment system)
- Integration with 17_observability/federation_ranking

Status: Blueprint v5.3 Foundation
Version: 1.0.0
"""

import json
import time
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class ProofCreditAllocation:
    """
    MiCA-compliant proof credit allocation.

    Credits are utility tokens for governance weight, NOT payments.
    """
    node_id: str
    region: str
    federation_zone: str
    allocation_timestamp: str

    # Metrics-based allocation
    proofs_validated: int
    validation_accuracy: float          # 0.0-1.0
    storage_contribution_gb: float
    consensus_participation: float      # 0.0-1.0

    # Derived scores
    credit_score: float                 # Utility score (non-monetary)
    governance_weight: float            # Voting power (0.0-1.0)

    # Audit trail
    allocation_hash: str                # SHA-256 of allocation data
    blockchain_anchor_tx: Optional[str] = None  # On-chain proof

    # Metadata
    allocation_round: int = 0
    previous_allocation_hash: Optional[str] = None


@dataclass
class CreditAllocationHistory:
    """
    Historical credit allocations for audit trail.
    """
    node_id: str
    allocations: List[ProofCreditAllocation]
    total_credits_earned: float
    current_governance_weight: float


class ProofCreditRegistry:
    """
    Registry for proof credit allocations.

    Integrates with:
    - 17_observability/federation_ranking.py (performance metrics)
    - 02_audit_logging/blockchain_anchor (on-chain anchoring)
    """

    def __init__(
        self,
        registry_path: str = "07_governance_legal/registries/proof_credits.jsonl",
        blockchain_anchor_enabled: bool = True
    ):
        """
        Initialize proof credit registry.

        Args:
            registry_path: Path to credit allocation log (JSONL)
            blockchain_anchor_enabled: Enable on-chain anchoring
        """
        self.registry_path = Path(registry_path)
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)

        self.blockchain_anchor_enabled = blockchain_anchor_enabled

        # Credit allocation formula weights
        self.formula_weights = {
            "proofs_validated": 0.4,
            "validation_accuracy": 0.3,
            "storage_contribution": 0.2,
            "consensus_participation": 0.1
        }

        # Allocation round counter
        self.allocation_round = self._load_latest_round()

    def _load_latest_round(self) -> int:
        """Load latest allocation round from registry."""
        if not self.registry_path.exists():
            return 0

        with self.registry_path.open("r", encoding="utf-8") as f:
            lines = f.readlines()
            if not lines:
                return 0

            # Parse last line
            last_entry = json.loads(lines[-1])
            return last_entry.get("allocation_round", 0)

    def allocate_credits(
        self,
        node_id: str,
        region: str,
        federation_zone: str,
        metrics: Dict[str, Any]
    ) -> ProofCreditAllocation:
        """
        Allocate proof credits based on node performance metrics.

        Args:
            node_id: Node identifier
            region: Geographic region
            federation_zone: Federation zone
            metrics: Performance metrics from federation_ranking

        Returns:
            ProofCreditAllocation with credit score and governance weight
        """
        # Extract metrics
        proofs_validated = metrics.get("proofs_validated", 0)
        validation_accuracy = metrics.get("validation_accuracy", 0.0)
        storage_contribution_gb = metrics.get("storage_contribution_gb", 0.0)
        consensus_participation = metrics.get("consensus_participation", 0.0)

        # Compute credit score
        credit_score = self._compute_credit_score(
            proofs_validated,
            validation_accuracy,
            storage_contribution_gb,
            consensus_participation
        )

        # Compute governance weight (normalized to max performer)
        max_credit_score = metrics.get("max_credit_score", credit_score)
        governance_weight = self._compute_governance_weight(credit_score, max_credit_score)

        # Get previous allocation hash (for chain)
        previous_hash = self._get_previous_allocation_hash(node_id)

        # Create allocation
        allocation = ProofCreditAllocation(
            node_id=node_id,
            region=region,
            federation_zone=federation_zone,
            allocation_timestamp=datetime.utcnow().isoformat() + "Z",
            proofs_validated=proofs_validated,
            validation_accuracy=validation_accuracy,
            storage_contribution_gb=storage_contribution_gb,
            consensus_participation=consensus_participation,
            credit_score=credit_score,
            governance_weight=governance_weight,
            allocation_hash="",  # Computed below
            blockchain_anchor_tx=None,
            allocation_round=self.allocation_round + 1,
            previous_allocation_hash=previous_hash
        )

        # Compute allocation hash
        allocation.allocation_hash = self._compute_allocation_hash(allocation)

        # Anchor to blockchain (if enabled)
        if self.blockchain_anchor_enabled:
            allocation.blockchain_anchor_tx = self._anchor_to_blockchain(allocation)

        # Record allocation
        self._record_allocation(allocation)

        # Increment allocation round
        self.allocation_round += 1

        return allocation

    def _compute_credit_score(
        self,
        proofs_validated: int,
        validation_accuracy: float,
        storage_contribution_gb: float,
        consensus_participation: float
    ) -> float:
        """
        Compute credit score from performance metrics.

        Formula:
        credit_score = (
            proofs_validated * 0.4 +
            validation_accuracy * 1000 * 0.3 +
            storage_contribution_gb * 0.2 +
            consensus_participation * 1000 * 0.1
        )

        Args:
            proofs_validated: Number of proofs validated
            validation_accuracy: Validation accuracy (0.0-1.0)
            storage_contribution_gb: Storage contribution (GB)
            consensus_participation: Consensus participation (0.0-1.0)

        Returns:
            Credit score (utility-based, non-monetary)
        """
        score = (
            proofs_validated * self.formula_weights["proofs_validated"] +
            validation_accuracy * 1000 * self.formula_weights["validation_accuracy"] +
            storage_contribution_gb * self.formula_weights["storage_contribution"] +
            consensus_participation * 1000 * self.formula_weights["consensus_participation"]
        )

        return round(score, 2)

    def _compute_governance_weight(
        self,
        credit_score: float,
        max_credit_score: float
    ) -> float:
        """
        Compute governance weight from credit score.

        Governance weight determines voting power in governance proposals.
        Normalized to highest performer (max_credit_score).

        Args:
            credit_score: Node's credit score
            max_credit_score: Maximum credit score across all nodes

        Returns:
            Governance weight (0.0-1.0)
        """
        if max_credit_score <= 0:
            return 0.0

        weight = credit_score / max_credit_score
        return min(round(weight, 4), 1.0)

    def _compute_allocation_hash(self, allocation: ProofCreditAllocation) -> str:
        """
        Compute SHA-256 hash of allocation data (audit trail).

        Args:
            allocation: ProofCreditAllocation to hash

        Returns:
            SHA-256 hash (hex)
        """
        # Create deterministic representation
        allocation_dict = {
            "node_id": allocation.node_id,
            "region": allocation.region,
            "federation_zone": allocation.federation_zone,
            "allocation_timestamp": allocation.allocation_timestamp,
            "proofs_validated": allocation.proofs_validated,
            "validation_accuracy": allocation.validation_accuracy,
            "storage_contribution_gb": allocation.storage_contribution_gb,
            "consensus_participation": allocation.consensus_participation,
            "credit_score": allocation.credit_score,
            "governance_weight": allocation.governance_weight,
            "allocation_round": allocation.allocation_round,
            "previous_allocation_hash": allocation.previous_allocation_hash
        }

        # Serialize with sorted keys
        allocation_json = json.dumps(allocation_dict, sort_keys=True)

        # Compute SHA-256
        return hashlib.sha256(allocation_json.encode()).hexdigest()

    def _anchor_to_blockchain(self, allocation: ProofCreditAllocation) -> Optional[str]:
        """
        Anchor credit allocation to blockchain (on-chain proof).

        NOTE: This is a placeholder for blockchain integration.
        In production, integrate with 02_audit_logging/blockchain_anchor.

        Args:
            allocation: ProofCreditAllocation to anchor

        Returns:
            Transaction hash (if anchoring successful)
        """
        # TODO: Integrate with blockchain anchoring engine
        # from blockchain_anchoring_engine import BlockchainAnchoringEngine
        # anchor = BlockchainAnchoringEngine()
        # tx_hash = anchor.anchor_proof(allocation.allocation_hash)
        # return tx_hash

        # Placeholder (simulated tx hash)
        return f"0x{allocation.allocation_hash[:64]}"

    def _get_previous_allocation_hash(self, node_id: str) -> Optional[str]:
        """
        Get previous allocation hash for node (chain linkage).

        Args:
            node_id: Node identifier

        Returns:
            Previous allocation hash (or None if first allocation)
        """
        if not self.registry_path.exists():
            return None

        # Read registry in reverse to find latest allocation for node
        with self.registry_path.open("r", encoding="utf-8") as f:
            lines = f.readlines()

        for line in reversed(lines):
            if not line.strip():
                continue

            entry = json.loads(line)
            if entry.get("node_id") == node_id:
                return entry.get("allocation_hash")

        return None

    def _record_allocation(self, allocation: ProofCreditAllocation) -> None:
        """
        Record allocation to registry (JSONL append).

        Args:
            allocation: ProofCreditAllocation to record
        """
        allocation_dict = asdict(allocation)

        with self.registry_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(allocation_dict) + "\n")

    def get_allocation_history(self, node_id: str) -> CreditAllocationHistory:
        """
        Get credit allocation history for node.

        Args:
            node_id: Node identifier

        Returns:
            CreditAllocationHistory with all allocations
        """
        if not self.registry_path.exists():
            return CreditAllocationHistory(
                node_id=node_id,
                allocations=[],
                total_credits_earned=0.0,
                current_governance_weight=0.0
            )

        allocations = []
        total_credits = 0.0

        with self.registry_path.open("r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue

                entry = json.loads(line)
                if entry.get("node_id") == node_id:
                    allocation = ProofCreditAllocation(**entry)
                    allocations.append(allocation)
                    total_credits += allocation.credit_score

        current_weight = allocations[-1].governance_weight if allocations else 0.0

        return CreditAllocationHistory(
            node_id=node_id,
            allocations=allocations,
            total_credits_earned=total_credits,
            current_governance_weight=current_weight
        )

    def get_all_governance_weights(self) -> Dict[str, float]:
        """
        Get current governance weights for all nodes.

        Returns:
            Dict of node_id → governance_weight
        """
        if not self.registry_path.exists():
            return {}

        # Get latest allocation for each node
        latest_allocations = {}

        with self.registry_path.open("r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue

                entry = json.loads(line)
                node_id = entry.get("node_id")
                allocation_round = entry.get("allocation_round", 0)

                # Keep only latest allocation
                if node_id not in latest_allocations or \
                   allocation_round > latest_allocations[node_id]["allocation_round"]:
                    latest_allocations[node_id] = entry

        # Extract governance weights
        weights = {
            node_id: entry.get("governance_weight", 0.0)
            for node_id, entry in latest_allocations.items()
        }

        return weights

    def verify_allocation_chain(self, node_id: str) -> bool:
        """
        Verify allocation chain integrity for node.

        Args:
            node_id: Node identifier

        Returns:
            True if allocation chain is valid (no tampering)
        """
        history = self.get_allocation_history(node_id)

        for i, allocation in enumerate(history.allocations):
            # Verify allocation hash
            computed_hash = self._compute_allocation_hash(allocation)
            if computed_hash != allocation.allocation_hash:
                return False

            # Verify chain linkage (previous_allocation_hash)
            if i > 0:
                expected_previous = history.allocations[i - 1].allocation_hash
                if allocation.previous_allocation_hash != expected_previous:
                    return False

        return True


# Example usage
if __name__ == "__main__":
    print("Proof Credit Registry - MiCA-Compliant Utility Rewards")
    print("=" * 70)

    # Create registry
    registry = ProofCreditRegistry(
        registry_path="07_governance_legal/registries/proof_credits_test.jsonl",
        blockchain_anchor_enabled=True
    )

    # Simulate credit allocation for 3 nodes
    nodes_metrics = [
        {
            "node_id": "eu-node-001",
            "region": "eu-west-1",
            "federation_zone": "eu",
            "proofs_validated": 10000,
            "validation_accuracy": 0.98,
            "storage_contribution_gb": 500.0,
            "consensus_participation": 0.95,
            "max_credit_score": 5000.0
        },
        {
            "node_id": "us-node-002",
            "region": "us-east-1",
            "federation_zone": "us",
            "proofs_validated": 8000,
            "validation_accuracy": 0.96,
            "storage_contribution_gb": 450.0,
            "consensus_participation": 0.90,
            "max_credit_score": 5000.0
        },
        {
            "node_id": "apac-node-003",
            "region": "ap-southeast-1",
            "federation_zone": "apac",
            "proofs_validated": 5000,
            "validation_accuracy": 0.94,
            "storage_contribution_gb": 300.0,
            "consensus_participation": 0.85,
            "max_credit_score": 5000.0
        }
    ]

    for node_metrics in nodes_metrics:
        allocation = registry.allocate_credits(
            node_id=node_metrics["node_id"],
            region=node_metrics["region"],
            federation_zone=node_metrics["federation_zone"],
            metrics=node_metrics
        )

        print(f"\nNode: {allocation.node_id}")
        print(f"  Region: {allocation.region}")
        print(f"  Proofs Validated: {allocation.proofs_validated}")
        print(f"  Validation Accuracy: {allocation.validation_accuracy:.2%}")
        print(f"  Credit Score: {allocation.credit_score}")
        print(f"  Governance Weight: {allocation.governance_weight:.4f}")
        print(f"  Allocation Hash: {allocation.allocation_hash[:32]}...")
        print(f"  Blockchain TX: {allocation.blockchain_anchor_tx[:32]}...")

    # Get governance weights
    print()
    print("Current Governance Weights:")
    weights = registry.get_all_governance_weights()
    for node_id, weight in weights.items():
        print(f"  {node_id}: {weight:.4f}")

    # Verify allocation chain
    print()
    print("Allocation Chain Verification:")
    for node_id in ["eu-node-001", "us-node-002", "apac-node-003"]:
        is_valid = registry.verify_allocation_chain(node_id)
        status = "[VALID]" if is_valid else "[INVALID]"
        print(f"  {node_id}: {status}")

    print()
    print("=" * 70)
    print("[OK] Proof Credit Registry Test Complete")
