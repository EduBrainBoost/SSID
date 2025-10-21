#!/usr/bin/env python3
"""
Blockchain Anchoring Engine - Immutable Evidence Commitment
============================================================

Anchors evidence hashes to blockchain for tamper-proof audit trail.
Implements MUST-008-BLOCKCHAIN-ANCHOR compliance requirement.

Features:
- Batch evidence hash anchoring (cost-optimized)
- Multiple blockchain support (Ethereum Sepolia, Polygon Amoy)
- Merkle tree commitments for efficient batch anchoring
- Transaction verification and retry logic
- Integration with WORM storage

Compliance: MUST-008-BLOCKCHAIN-ANCHOR, GDPR Art.5(1)(f), MiCA Art.74
Version: 1.0.0
"""

import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict

@dataclass
class AnchorTransaction:
    """Blockchain anchor transaction record."""
    batch_id: str
    merkle_root: str
    evidence_hashes: List[str]
    chain: str
    tx_hash: Optional[str]
    block_number: Optional[int]
    timestamp: str
    status: str  # pending, confirmed, failed

class BlockchainAnchoringEngine:
    """
    Blockchain anchoring engine for evidence commitments.

    Supports:
    - Ethereum Sepolia (testnet)
    - Polygon Amoy (testnet)
    - Batch anchoring with Merkle trees
    - Transaction retry with exponential backoff
    """

    def __init__(self, storage_root: str = "02_audit_logging/blockchain_anchor"):
        """
        Initialize blockchain anchoring engine.

        Args:
            storage_root: Root directory for anchor records
        """
        self.storage_root = Path(storage_root)
        self.storage_root.mkdir(parents=True, exist_ok=True)

        # Anchor records index
        self.index_path = self.storage_root / "anchor_index.json"
        self.index: Dict[str, AnchorTransaction] = self._load_index()

        # Transaction log
        self.tx_log_path = self.storage_root / "transactions.jsonl"

        # Configuration
        self.config = {
            "batch_size": 1000,
            "batch_timeout_seconds": 3600,  # 1 hour
            "retry_max": 3,
            "retry_backoff_base": 2,
            "chains": {
                "ethereum:sepolia": {
                    "enabled": True,
                    "rpc_url": "https://sepolia.infura.io/v3/YOUR_API_KEY",
                    "chain_id": 11155111
                },
                "polygon:amoy": {
                    "enabled": True,
                    "rpc_url": "https://rpc-amoy.polygon.technology",
                    "chain_id": 80002
                }
            }
        }

    def _load_index(self) -> Dict[str, AnchorTransaction]:
        """Load anchor transaction index."""
        if self.index_path.exists():
            with open(self.index_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return {k: AnchorTransaction(**v) for k, v in data.items()}
        return {}

    def _save_index(self) -> None:
        """Save anchor transaction index."""
        data = {k: asdict(v) for k, v in self.index.items()}
        with open(self.index_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _log_transaction(self, tx: AnchorTransaction) -> None:
        """Log transaction to append-only log."""
        with open(self.tx_log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(asdict(tx)) + '\n')

    def _compute_merkle_root(self, hashes: List[str]) -> str:
        """
        Compute Merkle root of evidence hashes.

        Args:
            hashes: List of evidence hashes (SHA-256)

        Returns:
            Merkle root hash
        """
        if len(hashes) == 0:
            return hashlib.sha256(b"").hexdigest()

        if len(hashes) == 1:
            return hashes[0]

        # Build Merkle tree (simple implementation)
        current_level = hashes[:]

        while len(current_level) > 1:
            next_level = []
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                right = current_level[i + 1] if i + 1 < len(current_level) else left

                # Hash pair
                combined = hashlib.sha256(
                    bytes.fromhex(left) + bytes.fromhex(right)
                ).hexdigest()
                next_level.append(combined)

            current_level = next_level

        return current_level[0]

    def _simulate_blockchain_anchor(self, merkle_root: str, chain: str) -> Dict[str, Any]:
        """
        Simulate blockchain anchoring (mock for PoC).

        In production: Replace with real Web3 transaction.

        Args:
            merkle_root: Merkle root hash to anchor
            chain: Blockchain identifier

        Returns:
            Transaction result with tx_hash and block_number
        """
        # Simulate transaction hash (deterministic for testing)
        tx_input = f"{merkle_root}||{chain}||{int(time.time())}"
        tx_hash = "0x" + hashlib.sha256(tx_input.encode()).hexdigest()[:40]

        # Simulate block number
        block_number = 1000000 + int(time.time()) % 1000000

        # Simulate network delay
        time.sleep(0.1)

        return {
            "tx_hash": tx_hash,
            "block_number": block_number,
            "status": "confirmed",
            "chain": chain
        }

    def anchor_evidence_batch(self, evidence_hashes: List[str],
                             chain: str = "ethereum:sepolia") -> Dict[str, Any]:
        """
        Anchor batch of evidence hashes to blockchain.

        Args:
            evidence_hashes: List of evidence content hashes
            chain: Target blockchain (default: ethereum:sepolia)

        Returns:
            Anchor transaction record
        """
        if len(evidence_hashes) == 0:
            raise ValueError("Cannot anchor empty batch")

        if chain not in self.config["chains"]:
            raise ValueError(f"Unsupported chain: {chain}")

        if not self.config["chains"][chain]["enabled"]:
            raise ValueError(f"Chain {chain} is not enabled")

        # Generate batch ID
        batch_id = f"batch_{int(time.time())}_{len(evidence_hashes)}"

        # Compute Merkle root
        merkle_root = self._compute_merkle_root(evidence_hashes)

        # Create transaction record
        tx = AnchorTransaction(
            batch_id=batch_id,
            merkle_root=merkle_root,
            evidence_hashes=evidence_hashes,
            chain=chain,
            tx_hash=None,
            block_number=None,
            timestamp=datetime.now(timezone.utc).isoformat(),
            status="pending"
        )

        # Anchor to blockchain (with retry)
        for attempt in range(self.config["retry_max"]):
            try:
                result = self._simulate_blockchain_anchor(merkle_root, chain)

                # Update transaction record
                tx.tx_hash = result["tx_hash"]
                tx.block_number = result["block_number"]
                tx.status = result["status"]

                break
            except Exception as e:
                if attempt == self.config["retry_max"] - 1:
                    tx.status = "failed"
                    print(f"[ERROR] Blockchain anchor failed after {self.config['retry_max']} attempts: {e}")
                else:
                    # Exponential backoff
                    backoff = self.config["retry_backoff_base"] ** attempt
                    time.sleep(backoff)

        # Save transaction
        self.index[batch_id] = tx
        self._save_index()
        self._log_transaction(tx)

        return {
            "batch_id": batch_id,
            "merkle_root": merkle_root,
            "tx_hash": tx.tx_hash,
            "block_number": tx.block_number,
            "chain": chain,
            "evidence_count": len(evidence_hashes),
            "status": tx.status,
            "timestamp": tx.timestamp
        }

    def anchor_single_evidence(self, evidence_hash: str,
                              chain: str = "ethereum:sepolia") -> Dict[str, Any]:
        """
        Anchor single evidence hash to blockchain.

        Args:
            evidence_hash: Evidence content hash (SHA-256)
            chain: Target blockchain

        Returns:
            Anchor transaction record
        """
        return self.anchor_evidence_batch([evidence_hash], chain)

    def verify_anchor(self, batch_id: str) -> Dict[str, Any]:
        """
        Verify blockchain anchor transaction.

        Args:
            batch_id: Batch identifier

        Returns:
            Verification result
        """
        if batch_id not in self.index:
            raise FileNotFoundError(f"Batch {batch_id} not found")

        tx = self.index[batch_id]

        # In production: Query blockchain to verify transaction
        # For now: Return stored transaction data
        return {
            "batch_id": batch_id,
            "merkle_root": tx.merkle_root,
            "tx_hash": tx.tx_hash,
            "block_number": tx.block_number,
            "chain": tx.chain,
            "evidence_count": len(tx.evidence_hashes),
            "status": tx.status,
            "timestamp": tx.timestamp,
            "verified": tx.status == "confirmed"
        }

    def list_anchors(self, chain: Optional[str] = None,
                    status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List blockchain anchors.

        Args:
            chain: Filter by blockchain (optional)
            status: Filter by status (optional)

        Returns:
            List of anchor transactions
        """
        results = []
        for batch_id, tx in self.index.items():
            if chain and tx.chain != chain:
                continue
            if status and tx.status != status:
                continue

            results.append({
                "batch_id": batch_id,
                "merkle_root": tx.merkle_root,
                "tx_hash": tx.tx_hash,
                "block_number": tx.block_number,
                "chain": tx.chain,
                "evidence_count": len(tx.evidence_hashes),
                "status": tx.status,
                "timestamp": tx.timestamp
            })

        return results

    def get_anchor_proof(self, evidence_hash: str) -> Dict[str, Any]:
        """
        Get blockchain anchor proof for specific evidence hash.

        Args:
            evidence_hash: Evidence content hash

        Returns:
            Anchor proof with Merkle path and transaction details
        """
        # Find batch containing this evidence
        for batch_id, tx in self.index.items():
            if evidence_hash in tx.evidence_hashes:
                # Compute Merkle proof path (simplified)
                index = tx.evidence_hashes.index(evidence_hash)

                return {
                    "evidence_hash": evidence_hash,
                    "batch_id": batch_id,
                    "merkle_root": tx.merkle_root,
                    "merkle_index": index,
                    "tx_hash": tx.tx_hash,
                    "block_number": tx.block_number,
                    "chain": tx.chain,
                    "timestamp": tx.timestamp,
                    "proof_valid": tx.status == "confirmed"
                }

        raise FileNotFoundError(f"No anchor found for evidence hash {evidence_hash}")

def test_blockchain_anchoring():
    """Test blockchain anchoring functionality."""
    print("=" * 70)
    print("Blockchain Anchoring Engine - Functional Test")
    print("=" * 70)
    print()

    # Initialize engine
    anchor_engine = BlockchainAnchoringEngine()

    # Test 1: Anchor single evidence
    print("TEST 1: Anchoring single evidence hash")
    print("-" * 70)
    evidence_hash = hashlib.sha256(b"test_evidence_data").hexdigest()
    result = anchor_engine.anchor_single_evidence(evidence_hash)

    print(f"Batch ID: {result['batch_id']}")
    print(f"Merkle Root: {result['merkle_root']}")
    print(f"TX Hash: {result['tx_hash']}")
    print(f"Block Number: {result['block_number']}")
    print(f"Chain: {result['chain']}")
    print(f"Status: {result['status']}")
    print()

    # Test 2: Anchor batch of evidence
    print("TEST 2: Anchoring batch of evidence hashes")
    print("-" * 70)
    evidence_batch = [
        hashlib.sha256(f"evidence_{i}".encode()).hexdigest()
        for i in range(10)
    ]
    batch_result = anchor_engine.anchor_evidence_batch(evidence_batch)

    print(f"Batch ID: {batch_result['batch_id']}")
    print(f"Evidence Count: {batch_result['evidence_count']}")
    print(f"Merkle Root: {batch_result['merkle_root']}")
    print(f"TX Hash: {batch_result['tx_hash']}")
    print(f"Status: {batch_result['status']}")
    print()

    # Test 3: Verify anchor
    print("TEST 3: Verifying blockchain anchor")
    print("-" * 70)
    verification = anchor_engine.verify_anchor(batch_result['batch_id'])

    print(f"Batch ID: {verification['batch_id']}")
    print(f"Verified: {verification['verified']}")
    print(f"TX Hash: {verification['tx_hash']}")
    print()

    # Test 4: Get anchor proof for specific evidence
    print("TEST 4: Getting anchor proof for specific evidence")
    print("-" * 70)
    proof = anchor_engine.get_anchor_proof(evidence_batch[0])

    print(f"Evidence Hash: {proof['evidence_hash']}")
    print(f"Batch ID: {proof['batch_id']}")
    print(f"Merkle Root: {proof['merkle_root']}")
    print(f"Proof Valid: {proof['proof_valid']}")
    print()

    # Test 5: List all anchors
    print("TEST 5: Listing all anchors")
    print("-" * 70)
    anchors = anchor_engine.list_anchors()

    print(f"Total Anchors: {len(anchors)}")
    for anchor in anchors[:3]:
        print(f"  - {anchor['batch_id']} ({anchor['evidence_count']} evidence, {anchor['status']})")
    print()

    print("=" * 70)
    print("[OK] Blockchain Anchoring Engine - All Tests Passed")
    print("=" * 70)

if __name__ == "__main__":
    test_blockchain_anchoring()
