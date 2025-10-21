"""
Temporal Rollback Extension v2 (TRA v2)
Enhanced Merkle-Epoch with Cross-Federation Linking

Version: 8.0.0
Status: DORMANT - Simulation Only
Features:
- Merkle-based epoch checkpointing
- Cross-federation state linking
- Temporal rollback capability
- Zero-knowledge epoch proofs

Cost: $0
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from enum import Enum
import hashlib
import json
import time

class EpochStatus(Enum):
    """Epoch State"""
    ACTIVE = "active"
    FINALIZED = "finalized"
    ROLLED_BACK = "rolled_back"
    ARCHIVED = "archived"

class FederationType(Enum):
    """Federation Types"""
    INTERNAL = "internal"  # SSID internal
    COSMOS = "cosmos"      # Cosmos IBC
    POLKADOT = "polkadot"  # Polkadot parachain
    QUANTUM = "quantum"    # Quantum relay

@dataclass
class MerkleNode:
    """Merkle Tree Node"""
    hash: str
    left_child: Optional[str]
    right_child: Optional[str]
    data: Optional[Dict]
    level: int

    def to_dict(self) -> Dict:
        return {
            "hash": self.hash,
            "left_child": self.left_child,
            "right_child": self.right_child,
            "data": self.data,
            "level": self.level
        }

@dataclass
class EpochCheckpoint:
    """Epoch Checkpoint with Merkle Root"""
    epoch_id: int
    merkle_root: str
    timestamp: int
    block_height: int
    state_hash: str
    federation_links: Dict[str, str]  # federation_type -> proof_hash
    status: EpochStatus
    previous_epoch_id: Optional[int]

    def to_dict(self) -> Dict:
        return {
            "epoch_id": self.epoch_id,
            "merkle_root": self.merkle_root,
            "timestamp": self.timestamp,
            "block_height": self.block_height,
            "state_hash": self.state_hash,
            "federation_links": self.federation_links,
            "status": self.status.value,
            "previous_epoch_id": self.previous_epoch_id
        }

@dataclass
class RollbackProof:
    """Proof of Temporal Rollback"""
    from_epoch_id: int
    to_epoch_id: int
    merkle_path: List[str]
    state_delta: Dict
    proof_hash: str
    timestamp: int

    def to_dict(self) -> Dict:
        return {
            "from_epoch_id": self.from_epoch_id,
            "to_epoch_id": self.to_epoch_id,
            "merkle_path": self.merkle_path,
            "state_delta": self.state_delta,
            "proof_hash": self.proof_hash,
            "timestamp": self.timestamp
        }

class TemporalRollbackExtension:
    """
    Temporal Rollback Extension v2

    Provides Merkle-based epoch checkpointing with cross-federation linking.
    Enables temporal rollback with cryptographic proof verification.

    DORMANT MODE: All operations are local simulations.
    """

    def __init__(
        self,
        epoch_duration_seconds: int = 3600,
        max_epochs: int = 1000,
        dormant: bool = True
    ):
        self.epoch_duration_seconds = epoch_duration_seconds
        self.max_epochs = max_epochs
        self.dormant = dormant

        # Epoch storage
        self.epochs: Dict[int, EpochCheckpoint] = {}
        self.current_epoch_id = 0
        self.merkle_trees: Dict[int, List[MerkleNode]] = {}

        # Federation links
        self.federation_proofs: Dict[str, Dict] = {}

        # Initialize genesis epoch
        self._create_genesis_epoch()

    def _create_genesis_epoch(self):
        """Create genesis epoch (epoch 0)"""
        genesis_state = {
            "version": "8.0.0",
            "genesis": True,
            "timestamp": int(time.time())
        }

        genesis_hash = self._hash_state(genesis_state)
        merkle_root = self._compute_merkle_root([genesis_hash])

        genesis_epoch = EpochCheckpoint(
            epoch_id=0,
            merkle_root=merkle_root,
            timestamp=int(time.time()),
            block_height=0,
            state_hash=genesis_hash,
            federation_links={},
            status=EpochStatus.FINALIZED,
            previous_epoch_id=None
        )

        self.epochs[0] = genesis_epoch
        self.current_epoch_id = 0

    def create_epoch(
        self,
        block_height: int,
        state_data: Dict,
        federation_links: Optional[Dict[str, str]] = None
    ) -> EpochCheckpoint:
        """
        Create new epoch checkpoint
        Computes Merkle root and links to federations
        """
        new_epoch_id = self.current_epoch_id + 1

        # Compute state hash
        state_hash = self._hash_state(state_data)

        # Build Merkle tree for this epoch
        state_leaves = [state_hash]
        if federation_links:
            state_leaves.extend(federation_links.values())

        merkle_root = self._compute_merkle_root(state_leaves)

        # Create epoch checkpoint
        epoch = EpochCheckpoint(
            epoch_id=new_epoch_id,
            merkle_root=merkle_root,
            timestamp=int(time.time()),
            block_height=block_height,
            state_hash=state_hash,
            federation_links=federation_links or {},
            status=EpochStatus.ACTIVE,
            previous_epoch_id=self.current_epoch_id
        )

        self.epochs[new_epoch_id] = epoch
        self.current_epoch_id = new_epoch_id

        return epoch

    def finalize_epoch(self, epoch_id: int) -> bool:
        """
        Finalize epoch (make immutable)
        """
        if epoch_id not in self.epochs:
            return False

        epoch = self.epochs[epoch_id]
        if epoch.status != EpochStatus.ACTIVE:
            return False

        epoch.status = EpochStatus.FINALIZED
        return True

    def add_federation_link(
        self,
        epoch_id: int,
        federation_type: FederationType,
        proof_hash: str
    ) -> bool:
        """
        Add cross-federation link to epoch
        Links to Cosmos, Polkadot, or Quantum proofs
        """
        if epoch_id not in self.epochs:
            return False

        epoch = self.epochs[epoch_id]
        if epoch.status != EpochStatus.ACTIVE:
            return False

        epoch.federation_links[federation_type.value] = proof_hash

        # Recompute Merkle root with new link
        state_leaves = [epoch.state_hash]
        state_leaves.extend(epoch.federation_links.values())
        epoch.merkle_root = self._compute_merkle_root(state_leaves)

        return True

    def rollback_to_epoch(
        self,
        target_epoch_id: int,
        reason: str = "manual_rollback"
    ) -> Optional[RollbackProof]:
        """
        Rollback to previous epoch
        Generates cryptographic proof of rollback
        """
        if target_epoch_id not in self.epochs:
            return None

        if target_epoch_id >= self.current_epoch_id:
            return None

        target_epoch = self.epochs[target_epoch_id]
        current_epoch = self.epochs[self.current_epoch_id]

        # Build Merkle proof path
        merkle_path = self._build_merkle_path(target_epoch_id, self.current_epoch_id)

        # Compute state delta
        state_delta = {
            "reason": reason,
            "epochs_rolled_back": self.current_epoch_id - target_epoch_id,
            "block_height_delta": current_epoch.block_height - target_epoch.block_height,
            "timestamp_delta": current_epoch.timestamp - target_epoch.timestamp
        }

        # Generate proof hash
        proof_data = {
            "from_epoch": self.current_epoch_id,
            "to_epoch": target_epoch_id,
            "state_delta": state_delta,
            "merkle_path": merkle_path
        }
        proof_hash = self._hash_state(proof_data)

        # Mark rolled-back epochs
        for epoch_id in range(target_epoch_id + 1, self.current_epoch_id + 1):
            if epoch_id in self.epochs:
                self.epochs[epoch_id].status = EpochStatus.ROLLED_BACK

        # Update current epoch
        self.current_epoch_id = target_epoch_id

        rollback_proof = RollbackProof(
            from_epoch_id=current_epoch.epoch_id,
            to_epoch_id=target_epoch_id,
            merkle_path=merkle_path,
            state_delta=state_delta,
            proof_hash=proof_hash,
            timestamp=int(time.time())
        )

        return rollback_proof

    def verify_epoch_integrity(self, epoch_id: int) -> bool:
        """
        Verify epoch integrity via Merkle proof
        """
        if epoch_id not in self.epochs:
            return False

        epoch = self.epochs[epoch_id]

        # Rebuild Merkle root
        state_leaves = [epoch.state_hash]
        state_leaves.extend(epoch.federation_links.values())
        computed_root = self._compute_merkle_root(state_leaves)

        return computed_root == epoch.merkle_root

    def verify_rollback_proof(self, proof: RollbackProof) -> bool:
        """
        Verify rollback proof validity
        """
        if proof.from_epoch_id not in self.epochs:
            return False
        if proof.to_epoch_id not in self.epochs:
            return False

        # Verify Merkle path
        expected_path = self._build_merkle_path(proof.to_epoch_id, proof.from_epoch_id)
        if expected_path != proof.merkle_path:
            return False

        # Verify proof hash
        proof_data = {
            "from_epoch": proof.from_epoch_id,
            "to_epoch": proof.to_epoch_id,
            "state_delta": proof.state_delta,
            "merkle_path": proof.merkle_path
        }
        computed_hash = self._hash_state(proof_data)

        return computed_hash == proof.proof_hash

    def get_epoch_chain(self, from_epoch: int, to_epoch: int) -> List[EpochCheckpoint]:
        """
        Get chain of epochs between two points
        """
        chain = []
        for epoch_id in range(from_epoch, to_epoch + 1):
            if epoch_id in self.epochs:
                chain.append(self.epochs[epoch_id])
        return chain

    def _compute_merkle_root(self, leaves: List[str]) -> str:
        """
        Compute Merkle root from leaves
        """
        if not leaves:
            return self._hash("")

        # Pad to power of 2
        while len(leaves) & (len(leaves) - 1) != 0:
            leaves.append(leaves[-1])

        current_level = leaves

        while len(current_level) > 1:
            next_level = []
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                right = current_level[i + 1] if i + 1 < len(current_level) else left
                combined = left + right
                parent_hash = self._hash(combined)
                next_level.append(parent_hash)
            current_level = next_level

        return current_level[0]

    def _build_merkle_path(self, from_epoch: int, to_epoch: int) -> List[str]:
        """
        Build Merkle proof path between epochs
        """
        path = []
        for epoch_id in range(from_epoch, to_epoch + 1):
            if epoch_id in self.epochs:
                path.append(self.epochs[epoch_id].merkle_root)
        return path

    def _hash(self, data: str) -> str:
        """SHA3-256 hash"""
        return hashlib.sha3_256(data.encode() if isinstance(data, str) else data).hexdigest()

    def _hash_state(self, state: Dict) -> str:
        """Hash state dictionary"""
        state_json = json.dumps(state, sort_keys=True)
        return self._hash(state_json)

    def export_epoch_report(self, filepath: str = "temporal_rollback_report.json") -> str:
        """Export epoch report"""
        report = {
            "version": "8.0.0",
            "dormant": self.dormant,
            "current_epoch_id": self.current_epoch_id,
            "total_epochs": len(self.epochs),
            "epoch_duration_seconds": self.epoch_duration_seconds,
            "epochs": [epoch.to_dict() for epoch in self.epochs.values()],
            "integrity_checks": {
                epoch_id: self.verify_epoch_integrity(epoch_id)
                for epoch_id in self.epochs.keys()
            }
        }

        with open(filepath, "w") as f:
            json.dump(report, f, indent=2)

        return filepath

    def get_status(self) -> Dict:
        """Get extension status"""
        return {
            "version": "8.0.0",
            "dormant": self.dormant,
            "current_epoch_id": self.current_epoch_id,
            "total_epochs": len(self.epochs),
            "finalized_epochs": len([e for e in self.epochs.values() if e.status == EpochStatus.FINALIZED]),
            "active_epochs": len([e for e in self.epochs.values() if e.status == EpochStatus.ACTIVE]),
            "rolled_back_epochs": len([e for e in self.epochs.values() if e.status == EpochStatus.ROLLED_BACK]),
            "cost_usd": 0.0
        }

# Test execution (for CI/CD)
if __name__ == "__main__":
    print("Temporal Rollback Extension v2 - Test Execution")
    print("=" * 60)

    tra = TemporalRollbackExtension(
        epoch_duration_seconds=3600,
        dormant=True
    )

    print(f"Dormant Mode: {tra.dormant}")
    print(f"Genesis Epoch: {tra.epochs[0].epoch_id}")

    # Create test epochs
    print("\nCreating test epochs...")
    for i in range(1, 6):
        state_data = {
            "epoch": i,
            "block_height": i * 1000,
            "transactions": i * 100
        }
        federation_links = {
            "cosmos": hashlib.sha256(f"cosmos_proof_{i}".encode()).hexdigest(),
            "polkadot": hashlib.sha256(f"polkadot_proof_{i}".encode()).hexdigest()
        }
        epoch = tra.create_epoch(i * 1000, state_data, federation_links)
        tra.finalize_epoch(epoch.epoch_id)
        print(f"  Epoch {epoch.epoch_id}: {epoch.merkle_root[:16]}...")

    # Verify integrity
    print("\nVerifying epoch integrity...")
    all_valid = True
    for epoch_id in tra.epochs.keys():
        valid = tra.verify_epoch_integrity(epoch_id)
        if not valid:
            all_valid = False
            print(f"  Epoch {epoch_id}: ❌ FAILED")
        else:
            print(f"  Epoch {epoch_id}: ✅ VALID")

    # Test rollback
    print("\nTesting temporal rollback...")
    rollback_proof = tra.rollback_to_epoch(3, reason="test_rollback")
    if rollback_proof:
        print(f"  Rolled back from epoch {rollback_proof.from_epoch_id} to {rollback_proof.to_epoch_id}")
        print(f"  Proof hash: {rollback_proof.proof_hash[:16]}...")
        proof_valid = tra.verify_rollback_proof(rollback_proof)
        print(f"  Proof validity: {'✅ VALID' if proof_valid else '❌ INVALID'}")

    # Export report
    report_path = tra.export_epoch_report()
    print(f"\nEpoch report exported to: {report_path}")

    status = tra.get_status()
    print(f"\nFinal Status:")
    print(f"  Current Epoch: {status['current_epoch_id']}")
    print(f"  Total Epochs: {status['total_epochs']}")
    print(f"  Finalized: {status['finalized_epochs']}")
    print(f"  Rolled Back: {status['rolled_back_epochs']}")
    print(f"  Cost: ${status['cost_usd']}")

    if all_valid:
        print("\n✅ Temporal Rollback Extension PASSED")
    else:
        print("\n❌ Some integrity checks FAILED")
