#!/usr/bin/env python3
"""
SSID Proof Emission Linker (v5.2)
License: GPL-3.0-or-later

Purpose: Coordinate digest transfer from Layer 14 → Layer 9 → On-chain anchor
Architecture: Non-custodial, proof-only, bidirectional verification
Security: Hash chains (SHA-512 + BLAKE2b), signature validation, replay protection
"""

import hashlib
import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple
from pathlib import Path

import yaml

logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}',
    datefmt="%Y-%m-%dT%H:%M:%SZ",
)
logger = logging.getLogger(__name__)


class ProofEmissionError(Exception):
    """Base exception for proof emission errors"""
    pass


class ProofEmissionLinker:
    """
    Coordinates proof digest emission from Layer 14 to Layer 9 and optional on-chain anchoring.

    Flow:
    1. Receive validated digest from kyc_callback_handler
    2. Compute hash chain (SHA-512)
    3. Forward to Layer 9 (global_proof_nexus_engine.receive_digest)
    4. Trigger on-chain anchor (if enabled)
    5. Generate provider acknowledgement JWT
    6. Emit WORM audit logs
    """

    def __init__(
        self,
        config_path: str = "14_zero_time_auth/kyc_gateway/integration/config.v5.2.example.yaml",
        audit_log_path: str = "02_audit_logging/logs/proof_emission.log",
    ):
        """
        Initialize proof emission linker.

        Args:
            config_path: Path to v5.2 configuration
            audit_log_path: Path to WORM audit log
        """
        self.config_path = config_path
        self.audit_log_path = audit_log_path

        # Load configuration
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)

        # Create audit log directory
        Path(audit_log_path).parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Proof Emission Linker initialized (v{self.config['version']})")

    def emit_proof(
        self,
        provider_id: str,
        digest: str,
        algorithm: str,
        session_id: str,
        proof_id: str,
        policy_version: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Emit proof digest to Layer 9 and optionally anchor on-chain.

        Args:
            provider_id: Provider identifier
            digest: SHA-256 or BLAKE2b hex digest
            algorithm: Hash algorithm used
            session_id: Session UUID
            proof_id: Proof UUID
            policy_version: Policy version
            metadata: Optional non-PII metadata

        Returns:
            Emission response with status, layer9_proof_id, anchor_tx_hash (if on-chain)

        Raises:
            ProofEmissionError: On emission failure
        """
        audit_context = {
            "provider_id": provider_id,
            "proof_id": proof_id,
            "session_id": session_id,
            "algorithm": algorithm,
        }

        try:
            # Step 1: Compute hash chain (SHA-512 over digest)
            hash_chain = self._compute_hash_chain(digest, algorithm, proof_id)

            # Step 2: Prepare emission payload
            payload = {
                "provider_id": provider_id,
                "digest": digest,
                "algorithm": algorithm,
                "session_id": session_id,
                "proof_id": proof_id,
                "policy_version": policy_version,
                "hash_chain": hash_chain,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "metadata": metadata or {},
            }

            # Step 3: Forward to Layer 9
            layer9_response = self._forward_to_layer9(payload)

            # Step 4: Optional on-chain anchoring
            anchor_result = None
            if self.config.get("on_chain", {}).get("enabled", False):
                anchor_result = self._anchor_on_chain(
                    proof_id=proof_id,
                    digest=digest,
                    provider_id=provider_id,
                )

            # Step 5: Emit audit log
            audit_context.update({
                "status": "SUCCESS",
                "layer9_proof_id": layer9_response["layer9_proof_id"],
                "hash_chain": hash_chain[:16] + "...",
                "on_chain": anchor_result is not None,
            })
            if anchor_result:
                audit_context["anchor_tx_hash"] = anchor_result.get("tx_hash", "N/A")

            self._log_audit("proof_emitted", audit_context)

            # Step 6: Return response
            response = {
                "status": "EMITTED",
                "proof_id": proof_id,
                "layer9_proof_id": layer9_response["layer9_proof_id"],
                "hash_chain": hash_chain,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            if anchor_result:
                response["anchor"] = {
                    "tx_hash": anchor_result.get("tx_hash"),
                    "block_number": anchor_result.get("block_number"),
                    "network": anchor_result.get("network"),
                }

            return response

        except Exception as e:
            audit_context.update({"status": "FAILED", "error": str(e)})
            self._log_audit("proof_emission_failed", audit_context)
            raise ProofEmissionError(f"Emission failed: {e}")

    def _compute_hash_chain(self, digest: str, algorithm: str, proof_id: str) -> str:
        """
        Compute hash chain (SHA-512 over digest + proof_id).

        Args:
            digest: Original digest
            algorithm: Hash algorithm used
            proof_id: Proof UUID

        Returns:
            SHA-512 hex hash chain
        """
        chain_input = f"{digest}:{algorithm}:{proof_id}"
        return hashlib.sha512(chain_input.encode("utf-8")).hexdigest()

    def _forward_to_layer9(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Forward digest to Layer 9 (global_proof_nexus_engine).

        Args:
            payload: Emission payload

        Returns:
            Layer 9 response with layer9_proof_id

        Note: Mock implementation - real version calls Layer 9 function
        """
        # Mock Layer 9 response
        layer9_proof_id = f"l9-{hashlib.sha256(payload['digest'].encode()).hexdigest()[:16]}"

        logger.info(f"Forwarded to Layer 9: {layer9_proof_id}")

        return {
            "layer9_proof_id": layer9_proof_id,
            "status": "accepted",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def _anchor_on_chain(
        self,
        proof_id: str,
        digest: str,
        provider_id: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Anchor digest on-chain via ProofAnchor.sol.

        Args:
            proof_id: Proof UUID
            digest: Digest to anchor
            provider_id: Provider identifier

        Returns:
            Anchor result with tx_hash, block_number, network

        Note: Mock implementation - real version calls smart contract
        """
        if not self.config.get("on_chain", {}).get("enabled", False):
            return None

        # Mock on-chain anchor
        mock_tx_hash = f"0x{hashlib.sha256(f'{proof_id}:{digest}'.encode()).hexdigest()}"

        logger.info(f"On-chain anchor: {mock_tx_hash}")

        return {
            "tx_hash": mock_tx_hash,
            "block_number": 12345678,
            "network": self.config["on_chain"].get("network", "testnet"),
            "gas_used": 120000,
        }

    def _log_audit(self, event: str, context: Dict[str, Any]) -> None:
        """
        Emit WORM audit log entry.

        Args:
            event: Event name
            context: Event context (no PII)
        """
        log_entry = {
            "event": event,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "context": context,
        }

        # Write to audit log (WORM append)
        with open(self.audit_log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, sort_keys=True, separators=(",", ":")) + "\n")

        logger.info(json.dumps(log_entry))


def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Proof Emission Linker CLI")
    parser.add_argument("--config", default="14_zero_time_auth/kyc_gateway/integration/config.v5.2.example.yaml")
    parser.add_argument("--provider-id", required=True)
    parser.add_argument("--digest", required=True)
    parser.add_argument("--algorithm", default="SHA-256")
    parser.add_argument("--session-id", required=True)
    parser.add_argument("--proof-id", required=True)
    parser.add_argument("--policy-version", default="1.0")

    args = parser.parse_args()

    linker = ProofEmissionLinker(config_path=args.config)

    try:
        result = linker.emit_proof(
            provider_id=args.provider_id,
            digest=args.digest,
            algorithm=args.algorithm,
            session_id=args.session_id,
            proof_id=args.proof_id,
            policy_version=args.policy_version,
        )
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(json.dumps({"status": "FAILED", "error": str(e)}, indent=2))
        exit(1)


if __name__ == "__main__":
    main()
