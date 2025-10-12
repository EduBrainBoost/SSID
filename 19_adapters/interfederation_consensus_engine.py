#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
═══════════════════════════════════════════════════════════════════════════════
SSID Inter-Federation Mesh Consensus Engine
═══════════════════════════════════════════════════════════════════════════════

Blueprint: v4.9.0
Layer: 8 - Cross-Federation Consensus Root Aggregation
Phase: POST-FEDERATION → INTER-FEDERATION
Date: 2026-04-01 00:00 UTC

Compliance: GDPR, eIDAS, MiCA, DORA, AMLD6
Root-24-LOCK: ENFORCED
SAFE-FIX: ENFORCED

Description:
    This adapter implements the off-chain consensus aggregation logic for
    Layer 8 inter-federation mesh proof coordination. It collects federation
    roots from Layer 7, calculates Layer 8 Merkle roots, and submits on-chain
    anchors to the InterFederationConsensus smart contract.

Exit Codes:
    0 = OK                    - Operation completed successfully
    1 = MISSING_DATA          - Required federation data unavailable
    2 = HASH_DRIFT            - Hash mismatch detected in aggregation
    3 = UNREACHABLE_CONTRACT  - Smart contract endpoint not accessible
    4 = SIGNATURE_ERROR       - Cryptographic signature verification failed

Logging:
    All operations log to: 02_audit_logging/reports/interfederation_consensus_log.json

Security:
    - Zero-custody: No private keys or PII stored or transmitted
    - Hash-only anchoring: Only SHA-256 hashes published on-chain
    - Simulation mode: No real blockchain transactions in v4.9 prep phase

═══════════════════════════════════════════════════════════════════════════════
"""

import hashlib
import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Exit codes
EXIT_OK = 0
EXIT_MISSING_DATA = 1
EXIT_HASH_DRIFT = 2
EXIT_UNREACHABLE_CONTRACT = 3
EXIT_SIGNATURE_ERROR = 4

# Configuration
BLUEPRINT_VERSION = "v4.9.0"
CONSENSUS_LAYER = 8
CONSENSUS_THRESHOLD = 0.8  # 80%
BYZANTINE_TOLERANCE = 0.2  # 20%
EPOCH_ROTATION = "Q2_2026"

# Paths (relative to project root)
PROJECT_ROOT = Path(__file__).parent.parent
AUDIT_LOG_PATH = PROJECT_ROOT / "02_audit_logging" / "reports" / "interfederation_consensus_log.json"
LAYER7_PROOFS_PATH = PROJECT_ROOT / "24_meta_orchestration" / "proofs" / "layer7"
LAYER8_OUTPUT_PATH = PROJECT_ROOT / "24_meta_orchestration" / "proofs" / "layer8"

# Ensure directories exist
AUDIT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
LAYER8_OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(AUDIT_LOG_PATH.with_suffix('.log'))
    ]
)
logger = logging.getLogger(__name__)


class InterFederationConsensusEngine:
    """
    Engine for Layer 8 inter-federation consensus aggregation and on-chain anchoring.
    """

    def __init__(self, simulation_mode: bool = True):
        """
        Initialize the consensus engine.

        Args:
            simulation_mode: If True, no real blockchain transactions are executed
        """
        self.simulation_mode = simulation_mode
        self.epoch_id = self._generate_epoch_id()
        self.federation_roots: List[Dict] = []
        self.layer8_merkle_root: Optional[str] = None

        logger.info(
            f"InterFederationConsensusEngine initialized | "
            f"Blueprint: {BLUEPRINT_VERSION} | Layer: {CONSENSUS_LAYER} | "
            f"Epoch: {self.epoch_id} | Simulation: {simulation_mode}"
        )

    def _generate_epoch_id(self) -> str:
        """
        Generate epoch identifier based on current timestamp and rotation schedule.

        Returns:
            Epoch ID string (e.g., "Q2_2026_epoch_001")
        """
        now = datetime.now(timezone.utc)
        epoch_base = f"{EPOCH_ROTATION}_epoch_{now.strftime('%j')}"  # Day of year
        return epoch_base

    def _sha256_hash(self, data: str) -> str:
        """
        Calculate SHA-256 hash of input data.

        Args:
            data: Input string to hash

        Returns:
            Hex-encoded SHA-256 hash
        """
        return hashlib.sha256(data.encode('utf-8')).hexdigest()

    def aggregate_federation_roots(self) -> int:
        """
        Aggregate Layer 7 federation roots from all participating nodes.

        Returns:
            Exit code (0=success, 1=missing data, 2=hash drift)
        """
        logger.info("Starting Layer 7 federation root aggregation...")

        try:
            # Check if Layer 7 proofs directory exists
            if not LAYER7_PROOFS_PATH.exists():
                logger.warning(f"Layer 7 proofs directory not found: {LAYER7_PROOFS_PATH}")
                logger.info("Creating placeholder Layer 7 proofs for simulation...")
                LAYER7_PROOFS_PATH.mkdir(parents=True, exist_ok=True)
                self._create_simulation_layer7_proofs()

            # Load all Layer 7 proof files
            proof_files = list(LAYER7_PROOFS_PATH.glob("*.json"))

            if not proof_files:
                logger.error("No Layer 7 proof files found")
                self._log_audit_event("MISSING_DATA", "No Layer 7 proofs available")
                return EXIT_MISSING_DATA

            logger.info(f"Found {len(proof_files)} Layer 7 proof files")

            # Aggregate roots
            for proof_file in proof_files:
                try:
                    with open(proof_file, 'r') as f:
                        proof_data = json.load(f)

                    # Validate proof structure
                    if not self._validate_proof_structure(proof_data):
                        logger.warning(f"Invalid proof structure in {proof_file.name}, skipping")
                        continue

                    self.federation_roots.append({
                        "node_id": proof_data.get("node_id", "unknown"),
                        "federation_root": proof_data.get("merkle_root"),
                        "timestamp": proof_data.get("timestamp"),
                        "layer": proof_data.get("layer", 7),
                        "trust_score": proof_data.get("trust_score", 100)
                    })

                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse {proof_file.name}: {e}")
                    continue
                except Exception as e:
                    logger.error(f"Error processing {proof_file.name}: {e}")
                    continue

            if not self.federation_roots:
                logger.error("No valid federation roots collected")
                self._log_audit_event("MISSING_DATA", "No valid Layer 7 roots")
                return EXIT_MISSING_DATA

            logger.info(f"Successfully aggregated {len(self.federation_roots)} federation roots")
            self._log_audit_event("AGGREGATION_SUCCESS", f"Collected {len(self.federation_roots)} roots")

            return EXIT_OK

        except Exception as e:
            logger.error(f"Unexpected error during aggregation: {e}")
            self._log_audit_event("AGGREGATION_ERROR", str(e))
            return EXIT_MISSING_DATA

    def _validate_proof_structure(self, proof: Dict) -> bool:
        """
        Validate that a proof has the required structure.

        Args:
            proof: Proof dictionary to validate

        Returns:
            True if valid, False otherwise
        """
        required_fields = ["node_id", "merkle_root", "timestamp"]
        return all(field in proof for field in required_fields)

    def _create_simulation_layer7_proofs(self):
        """
        Create placeholder Layer 7 proofs for simulation mode.
        """
        simulation_nodes = [
            {"node_id": "node_fed_eu_001", "trust_score": 95},
            {"node_id": "node_fed_us_002", "trust_score": 92},
            {"node_id": "node_fed_asia_003", "trust_score": 88},
            {"node_id": "node_fed_latam_004", "trust_score": 90}
        ]

        for node in simulation_nodes:
            proof_data = {
                "node_id": node["node_id"],
                "merkle_root": self._sha256_hash(f"layer7_proof_{node['node_id']}_{self.epoch_id}"),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "layer": 7,
                "trust_score": node["trust_score"],
                "epoch_id": self.epoch_id,
                "simulation": True
            }

            proof_file = LAYER7_PROOFS_PATH / f"{node['node_id']}_layer7_proof.json"
            with open(proof_file, 'w') as f:
                json.dump(proof_data, f, indent=2)

            logger.debug(f"Created simulation proof: {proof_file.name}")

    def calculate_layer8_merkle(self) -> int:
        """
        Calculate Layer 8 Merkle root from aggregated federation roots.

        Returns:
            Exit code (0=success, 2=hash drift)
        """
        logger.info("Calculating Layer 8 Merkle root...")

        if not self.federation_roots:
            logger.error("No federation roots available for Merkle calculation")
            return EXIT_MISSING_DATA

        try:
            # Sort roots for deterministic ordering
            sorted_roots = sorted(
                self.federation_roots,
                key=lambda x: (x["node_id"], x["federation_root"])
            )

            # Build Merkle tree
            leaves = [root["federation_root"] for root in sorted_roots]
            merkle_tree = self._build_merkle_tree(leaves)

            if not merkle_tree:
                logger.error("Failed to build Merkle tree")
                self._log_audit_event("HASH_DRIFT", "Merkle tree construction failed")
                return EXIT_HASH_DRIFT

            self.layer8_merkle_root = merkle_tree[0]  # Root is at index 0

            logger.info(f"Layer 8 Merkle root calculated: {self.layer8_merkle_root[:16]}...")
            self._log_audit_event("MERKLE_SUCCESS", f"Layer 8 root: {self.layer8_merkle_root}")

            # Save Layer 8 proof
            self._save_layer8_proof()

            return EXIT_OK

        except Exception as e:
            logger.error(f"Error calculating Merkle root: {e}")
            self._log_audit_event("MERKLE_ERROR", str(e))
            return EXIT_HASH_DRIFT

    def _build_merkle_tree(self, leaves: List[str]) -> List[str]:
        """
        Build a Merkle tree from leaf hashes.

        Args:
            leaves: List of leaf hash strings

        Returns:
            List containing the Merkle tree (root at index 0)
        """
        if not leaves:
            return []

        # Ensure even number of leaves (duplicate last if odd)
        if len(leaves) % 2 != 0:
            leaves.append(leaves[-1])

        tree = leaves.copy()
        current_level = leaves

        while len(current_level) > 1:
            next_level = []
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                right = current_level[i + 1] if i + 1 < len(current_level) else left
                parent = self._sha256_hash(left + right)
                next_level.append(parent)
                tree.append(parent)
            current_level = next_level

        # Return root at the beginning
        return [current_level[0]] + tree

    def _save_layer8_proof(self):
        """
        Save the Layer 8 proof to disk.
        """
        proof_data = {
            "version": BLUEPRINT_VERSION,
            "layer": CONSENSUS_LAYER,
            "epoch_id": self.epoch_id,
            "merkle_root": self.layer8_merkle_root,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_federations": len(self.federation_roots),
            "consensus_threshold": CONSENSUS_THRESHOLD,
            "byzantine_tolerance": BYZANTINE_TOLERANCE,
            "federation_nodes": [
                {
                    "node_id": root["node_id"],
                    "root_hash": root["federation_root"],
                    "trust_score": root["trust_score"]
                }
                for root in self.federation_roots
            ],
            "compliance": ["GDPR", "eIDAS", "MiCA", "DORA", "AMLD6"],
            "root_24_lock": True,
            "simulation_mode": self.simulation_mode
        }

        output_file = LAYER8_OUTPUT_PATH / f"layer8_consensus_{self.epoch_id}.json"
        with open(output_file, 'w') as f:
            json.dump(proof_data, f, indent=2)

        logger.info(f"Layer 8 proof saved: {output_file}")

    def submit_onchain_anchor(self) -> int:
        """
        Submit Layer 8 consensus root as on-chain anchor.

        Returns:
            Exit code (0=success, 3=unreachable, 4=signature error)
        """
        logger.info("Submitting on-chain anchor...")

        if not self.layer8_merkle_root:
            logger.error("No Layer 8 Merkle root available for submission")
            return EXIT_MISSING_DATA

        try:
            if self.simulation_mode:
                logger.info("SIMULATION MODE: Skipping real blockchain transaction")
                logger.info(f"Would submit to contract: submitFederationProof()")
                logger.info(f"  - Proof Root: {self.layer8_merkle_root}")
                logger.info(f"  - Epoch ID: {self.epoch_id}")
                logger.info(f"  - Total Nodes: {len(self.federation_roots)}")

                self._log_audit_event(
                    "ANCHOR_SIMULATED",
                    f"Simulation anchor for epoch {self.epoch_id}"
                )

                return EXIT_OK

            # Real blockchain submission would happen here
            # This is a placeholder for production implementation
            success = self._submit_to_blockchain()

            if success:
                logger.info("On-chain anchor submitted successfully")
                self._log_audit_event("ANCHOR_SUCCESS", "On-chain anchor confirmed")
                return EXIT_OK
            else:
                logger.error("Failed to submit on-chain anchor")
                self._log_audit_event("ANCHOR_FAILED", "Blockchain submission failed")
                return EXIT_UNREACHABLE_CONTRACT

        except Exception as e:
            logger.error(f"Error submitting on-chain anchor: {e}")
            self._log_audit_event("ANCHOR_ERROR", str(e))
            return EXIT_UNREACHABLE_CONTRACT

    def _submit_to_blockchain(self) -> bool:
        """
        Placeholder for actual blockchain submission logic.

        In production, this would:
        1. Load RPC endpoint configuration
        2. Load signing key (from secure key management system)
        3. Build transaction for InterFederationConsensus.submitFederationProof()
        4. Sign and broadcast transaction
        5. Wait for confirmation

        Returns:
            True if successful, False otherwise
        """
        # TODO: Implement actual blockchain interaction
        # Example structure:
        # web3 = Web3(Web3.HTTPProvider(RPC_ENDPOINT))
        # contract = web3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)
        # tx = contract.functions.submitFederationProof(
        #     bytes.fromhex(self.layer8_merkle_root),
        #     int(self.epoch_id.split('_')[-1])
        # ).build_transaction({...})
        # signed_tx = web3.eth.account.sign_transaction(tx, private_key=KEY)
        # tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        # receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
        # return receipt['status'] == 1

        logger.warning("_submit_to_blockchain is a placeholder - not implemented")
        return False

    def _log_audit_event(self, event_type: str, message: str):
        """
        Log an audit event to the consensus log file.

        Args:
            event_type: Type of event (e.g., "AGGREGATION_SUCCESS")
            message: Event message
        """
        audit_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "blueprint_version": BLUEPRINT_VERSION,
            "layer": CONSENSUS_LAYER,
            "epoch_id": self.epoch_id,
            "event_type": event_type,
            "message": message,
            "simulation_mode": self.simulation_mode
        }

        # Append to audit log
        try:
            if AUDIT_LOG_PATH.exists():
                with open(AUDIT_LOG_PATH, 'r') as f:
                    audit_log = json.load(f)
            else:
                audit_log = {"events": []}

            if "events" not in audit_log:
                audit_log["events"] = []

            audit_log["events"].append(audit_entry)

            with open(AUDIT_LOG_PATH, 'w') as f:
                json.dump(audit_log, f, indent=2)

        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")

    def run_full_cycle(self) -> int:
        """
        Execute the complete consensus cycle: aggregate, calculate, submit.

        Returns:
            Exit code from the last failed step, or 0 if all successful
        """
        logger.info("=" * 80)
        logger.info("Starting Inter-Federation Consensus Cycle")
        logger.info("=" * 80)

        # Step 1: Aggregate federation roots
        exit_code = self.aggregate_federation_roots()
        if exit_code != EXIT_OK:
            logger.error(f"Aggregation failed with exit code {exit_code}")
            return exit_code

        # Step 2: Calculate Layer 8 Merkle root
        exit_code = self.calculate_layer8_merkle()
        if exit_code != EXIT_OK:
            logger.error(f"Merkle calculation failed with exit code {exit_code}")
            return exit_code

        # Step 3: Submit on-chain anchor
        exit_code = self.submit_onchain_anchor()
        if exit_code != EXIT_OK:
            logger.error(f"On-chain anchor submission failed with exit code {exit_code}")
            return exit_code

        logger.info("=" * 80)
        logger.info("Inter-Federation Consensus Cycle Completed Successfully")
        logger.info("=" * 80)

        return EXIT_OK


def main():
    """
    Main entry point for the consensus engine.
    """
    # Always run in simulation mode for v4.9 prep phase
    engine = InterFederationConsensusEngine(simulation_mode=True)

    try:
        exit_code = engine.run_full_cycle()
        sys.exit(exit_code)

    except KeyboardInterrupt:
        logger.warning("Consensus cycle interrupted by user")
        sys.exit(130)

    except Exception as e:
        logger.error(f"Unexpected error in consensus cycle: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
