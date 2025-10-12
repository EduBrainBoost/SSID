#!/usr/bin/env python3
"""
SSID KYC Proof Interface (Layer 3)
License: GPL-3.0-or-later

Purpose: Receive and validate KYC proof digests from Layer 14 (KYC Gateway)
         Forward normalized digests to Layer 9 (Global Proof Nexus)

Architecture: Non-custodial, proof-only, zero PII
Security: OPA policy enforcement, hash-only validation
"""

import hashlib
import json
import logging
import re
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple

import yaml

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}',
    datefmt="%Y-%m-%dT%H:%M:%SZ",
)
logger = logging.getLogger(__name__)


class KYCProofInterfaceError(Exception):
    """Base exception for KYC proof interface errors"""
    pass


class InvalidDigestError(KYCProofInterfaceError):
    """Digest validation failed"""
    pass


class PIIDetectedError(KYCProofInterfaceError):
    """PII detected in payload (not allowed)"""
    pass


class OPAPolicyError(KYCProofInterfaceError):
    """OPA policy check failed"""
    pass


class KYCProofInterface:
    """
    Interface for receiving KYC proof digests from Layer 14.

    Responsibilities:
    - Validate digest format (SHA-256/BLAKE2b hex)
    - Enforce OPA policy (no PII, proof-only mode)
    - Normalize payload structure
    - Forward to Layer 9 (global_proof_nexus_engine)
    - Emit WORM audit logs
    """

    def __init__(
        self,
        config_path: str = "14_zero_time_auth/kyc_gateway/integration/kyc_layer9_link.yaml",
        audit_log_path: str = "02_audit_logging/logs/kyc_proof_emit.log",
    ):
        """
        Initialize KYC proof interface.

        Args:
            config_path: Path to integration configuration
            audit_log_path: Path to WORM audit log
        """
        self.config_path = config_path
        self.audit_log_path = audit_log_path

        # Load configuration
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)

        logger.info(f"KYC Proof Interface initialized (version {self.config['version']})")

    def emit_digest(
        self,
        provider_id: str,
        digest: str,
        algorithm: str,
        timestamp: str,
        policy_version: str,
        session_id: str,
        proof_id: str,
        evidence_chain: Optional[list] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Receive and process KYC proof digest from Layer 14.

        Args:
            provider_id: Provider identifier (didit, yoti, idnow, signicat)
            digest: SHA-256 or BLAKE2b hex digest
            algorithm: Hash algorithm used (SHA-256, BLAKE2b)
            timestamp: ISO 8601 UTC timestamp
            policy_version: Policy version at time of proof creation
            session_id: Session UUID
            proof_id: Proof UUID
            evidence_chain: Optional evidence hash chain
            metadata: Optional non-PII metadata

        Returns:
            Response with status, layer9_proof_id, timestamp

        Raises:
            KYCProofInterfaceError: On validation failure
        """
        audit_context = {
            "provider_id": provider_id,
            "proof_id": proof_id,
            "session_id": session_id,
            "timestamp": timestamp,
        }

        try:
            # Step 1: Validate digest format
            self.validate_digest(digest, algorithm)

            # Step 2: Construct payload
            payload = {
                "provider_id": provider_id,
                "digest": digest,
                "algorithm": algorithm,
                "timestamp": timestamp,
                "policy_version": policy_version,
                "session_id": session_id,
                "proof_id": proof_id,
                "evidence_chain": evidence_chain or [],
                "metadata": metadata or {},
            }

            # Step 3: OPA policy check
            self.check_opa_policy(payload)

            # Step 4: Normalize payload
            normalized = self.normalize_payload(payload)

            # Step 5: Forward to Layer 9
            layer9_response = self.forward_to_layer9(normalized)

            # Step 6: Emit audit log
            audit_context.update({
                "status": "SUCCESS",
                "layer9_proof_id": layer9_response["layer9_proof_id"],
            })
            self._log_audit("digest_emitted", audit_context)

            # Step 7: Return response
            return {
                "status": "ACCEPTED",
                "layer9_proof_id": layer9_response["layer9_proof_id"],
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        except KYCProofInterfaceError as e:
            audit_context.update({"status": "FAILED", "error": str(e)})
            self._log_audit("digest_emission_failed", audit_context)
            raise

        except Exception as e:
            audit_context.update({"status": "ERROR", "error": str(e)})
            self._log_audit("digest_emission_error", audit_context)
            raise KYCProofInterfaceError(f"Unexpected error: {e}")

    def validate_digest(self, digest: str, algorithm: str) -> None:
        """
        Validate digest format.

        Args:
            digest: Hex-encoded digest string
            algorithm: Hash algorithm (SHA-256 or BLAKE2b)

        Raises:
            InvalidDigestError: If digest format is invalid
        """
        if algorithm == "SHA-256":
            # SHA-256 produces 64-character hex string
            if not re.match(r"^[a-f0-9]{64}$", digest):
                raise InvalidDigestError(f"Invalid SHA-256 digest format: {digest}")
        elif algorithm == "BLAKE2b":
            # BLAKE2b produces 128-character hex string
            if not re.match(r"^[a-f0-9]{128}$", digest):
                raise InvalidDigestError(f"Invalid BLAKE2b digest format: {digest}")
        else:
            raise InvalidDigestError(f"Unsupported algorithm: {algorithm}")

    def check_opa_policy(self, payload: Dict[str, Any]) -> None:
        """
        Check OPA policy for proof-only mode and PII-free enforcement.

        Args:
            payload: Payload to validate

        Raises:
            OPAPolicyError: If OPA policy check fails
            PIIDetectedError: If PII detected
        """
        # OPA policy check (simplified - real implementation would use OPA REST API)
        # For now, basic checks:

        # Check 1: Provider allowlist
        allowed_providers = ["didit", "yoti", "idnow", "signicat"]
        if payload["provider_id"] not in allowed_providers:
            raise OPAPolicyError(f"Provider not in allowlist: {payload['provider_id']}")

        # Check 2: PII detection (forbidden fields)
        forbidden_fields = {
            "name", "given_name", "family_name", "birthdate", "birth_date",
            "address", "email", "phone_number", "phone", "ssn", "tax_id",
            "passport", "id_number", "drivers_license", "picture",
        }

        for field in payload.get("metadata", {}).keys():
            if field.lower() in forbidden_fields:
                raise PIIDetectedError(f"PII field detected in metadata: {field}")

        # Check 3: Proof-only mode
        if not payload.get("digest"):
            raise OPAPolicyError("Digest missing (proof-only mode required)")

        # Check 4: Digest format validation (already done in validate_digest)
        # Pass

    def normalize_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize payload structure for Layer 9 forwarding.

        Args:
            payload: Raw payload

        Returns:
            Normalized payload (sorted keys, consistent structure)
        """
        return {
            "provider_id": payload["provider_id"],
            "digest": payload["digest"],
            "algorithm": payload["algorithm"],
            "timestamp": payload["timestamp"],
            "policy_version": payload["policy_version"],
            "session_id": payload["session_id"],
            "proof_id": payload["proof_id"],
            "evidence_chain": payload.get("evidence_chain", []),
            "metadata": dict(sorted(payload.get("metadata", {}).items())),
        }

    def forward_to_layer9(self, normalized_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Forward normalized digest to Layer 9 (Global Proof Nexus).

        Args:
            normalized_payload: Normalized payload

        Returns:
            Layer 9 response with layer9_proof_id

        Note: In real implementation, this would call
              global_proof_nexus_engine.receive_kyc_digest()
        """
        # Mock implementation - real version would call Layer 9 function
        layer9_proof_id = f"l9-{hashlib.sha256(normalized_payload['digest'].encode()).hexdigest()[:16]}"

        logger.info(f"Forwarded digest to Layer 9: {layer9_proof_id}")

        return {
            "layer9_proof_id": layer9_proof_id,
            "status": "accepted",
            "timestamp": datetime.now(timezone.utc).isoformat(),
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

        # Also log to console
        logger.info(json.dumps(log_entry))


def main():
    """CLI entry point for testing"""
    import argparse

    parser = argparse.ArgumentParser(description="KYC Proof Interface CLI")
    parser.add_argument("--config", default="14_zero_time_auth/kyc_gateway/integration/kyc_layer9_link.yaml")
    parser.add_argument("--audit-log", default="02_audit_logging/logs/kyc_proof_emit.log")
    parser.add_argument("--provider-id", required=True)
    parser.add_argument("--digest", required=True)
    parser.add_argument("--algorithm", default="SHA-256")
    parser.add_argument("--timestamp", default=datetime.now(timezone.utc).isoformat())
    parser.add_argument("--policy-version", default="1.0")
    parser.add_argument("--session-id", required=True)
    parser.add_argument("--proof-id", required=True)

    args = parser.parse_args()

    interface = KYCProofInterface(
        config_path=args.config,
        audit_log_path=args.audit_log,
    )

    try:
        result = interface.emit_digest(
            provider_id=args.provider_id,
            digest=args.digest,
            algorithm=args.algorithm,
            timestamp=args.timestamp,
            policy_version=args.policy_version,
            session_id=args.session_id,
            proof_id=args.proof_id,
        )
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(json.dumps({"status": "FAILED", "error": str(e)}, indent=2))
        exit(1)


if __name__ == "__main__":
    main()
