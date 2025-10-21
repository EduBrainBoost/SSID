#!/usr/bin/env python3
"""
SSID KYC Gateway - Callback Handler
License: GPL-3.0-or-later

Handles callbacks from KYC providers:
- Validates provider proof (JWT/VC)
- Enforces replay protection
- Persists proof records (hash-only, no PII)
- Emits structured audit logs

Architecture: Non-custodial, proof-only, WORM logging
"""

import json
import logging
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from proof_verifier import ProofVerifier, ProofVerifierError, create_proof_record

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}',
    datefmt="%Y-%m-%dT%H:%M:%SZ",
)
logger = logging.getLogger(__name__)

class KYCCallbackHandler:
    """
    Handles KYC provider callbacks.

    Responsibilities:
    - Validate callback payload
    - Verify proof signature and claims
    - Enforce PII-free storage
    - Persist proof record (JSONL append)
    - Emit audit logs (JSON structured)
    """

    def __init__(
        self,
        provider_registry_path: str,
        proof_registry_path: str,
        audit_log_path: str,
        expected_audience: str,
    ):
        """
        Initialize callback handler.

        Args:
            provider_registry_path: Path to provider_registry.yaml
            proof_registry_path: Path to proof_registry.jsonl
            audit_log_path: Path to audit log file
            expected_audience: Expected JWT audience claim
        """
        self.provider_registry_path = provider_registry_path
        self.proof_registry_path = proof_registry_path
        self.audit_log_path = audit_log_path
        self.expected_audience = expected_audience

        # Load provider registry
        with open(provider_registry_path, "r", encoding="utf-8") as f:
            self.registry = yaml.safe_load(f)

        # Initialize proof verifier
        self.verifier = ProofVerifier(
            expected_audience=expected_audience,
            max_clock_skew_seconds=60,
            jti_cache_ttl_seconds=3600,
        )

        # Ensure directories exist
        Path(proof_registry_path).parent.mkdir(parents=True, exist_ok=True)
        Path(audit_log_path).parent.mkdir(parents=True, exist_ok=True)

    def handle_callback(
        self,
        session_id: str,
        provider_id: str,
        proof_token: str,
        state: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Handle provider callback with proof token.

        Args:
            session_id: Session UUID
            provider_id: Provider ID from registry
            proof_token: JWT or VC proof token
            state: Optional CSRF state parameter

        Returns:
            Callback response with status, proof_id, digest

        Raises:
            ValueError: On validation errors
        """
        audit_context = {
            "session_id": session_id,
            "provider_id": provider_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        try:
            # Validate provider
            provider = self._get_provider(provider_id)
            if not provider:
                self._log_audit("callback_failed", audit_context, error="PROVIDER_NOT_FOUND")
                raise ValueError(f"Provider not found: {provider_id}")

            # Verify proof token
            claims, digest = self.verifier.verify_jwt(
                token=proof_token,
                provider_id=provider_id,
                expected_issuer=provider["token_issuer"],
                jwk_set_url=provider["jwk_set_url"],
                allowed_algorithms=self.registry["security_requirements"]["allowed_jwt_algorithms"],
            )

            # Generate proof record
            proof_id = str(uuid.uuid4())
            proof_record = create_proof_record(
                proof_id=proof_id,
                provider_id=provider_id,
                digest=digest,
                algorithm="SHA-256",
                policy_version=self.registry["version"],
            )

            # Persist proof record (JSONL append, WORM)
            self._append_proof_record(proof_record)

            # Emit audit log
            audit_context.update({
                "proof_id": proof_id,
                "digest": digest,
                "jti": claims.get("jti"),
            })
            self._log_audit("callback_success", audit_context)

            # Return response
            return {
                "status": "PASS",
                "proof_id": proof_id,
                "digest": digest,
                "algorithm": "SHA-256",
                "timestamp": proof_record["timestamp"],
                "provider_id": provider_id,
            }

        except ProofVerifierError as e:
            audit_context["error"] = str(e)
            self._log_audit("callback_failed", audit_context, error=str(e))
            raise ValueError(f"Proof verification failed: {e}")

        except Exception as e:
            audit_context["error"] = str(e)
            self._log_audit("callback_failed", audit_context, error=str(e))
            raise

    def _get_provider(self, provider_id: str) -> Optional[Dict[str, Any]]:
        """Get provider config from registry"""
        for provider in self.registry.get("providers", []):
            if provider["id"] == provider_id:
                return provider
        return None

    def _append_proof_record(self, proof_record: Dict[str, Any]) -> None:
        """
        Append proof record to JSONL file (WORM).

        Format: One JSON object per line (JSON Lines)
        """
        with open(self.proof_registry_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(proof_record, sort_keys=True, separators=(",", ":")) + "\n")

    def _log_audit(
        self,
        event: str,
        context: Dict[str, Any],
        error: Optional[str] = None,
    ) -> None:
        """
        Emit structured audit log entry.

        Format: JSON per line, UTC timestamps
        """
        log_entry = {
            "event": event,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "context": context,
        }
        if error:
            log_entry["error"] = error

        # Write to audit log file (WORM append)
        with open(self.audit_log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, sort_keys=True, separators=(",", ":")) + "\n")

        # Also log to console
        if error:
            logger.error(json.dumps(log_entry))
        else:
            logger.info(json.dumps(log_entry))

def main():
    """CLI entry point for testing"""
    import argparse

    parser = argparse.ArgumentParser(description="KYC Callback Handler CLI")
    parser.add_argument("--registry", required=True, help="Path to provider_registry.yaml")
    parser.add_argument("--proof-registry", required=True, help="Path to proof_registry.jsonl")
    parser.add_argument("--audit-log", required=True, help="Path to audit log file")
    parser.add_argument("--audience", required=True, help="Expected JWT audience")
    parser.add_argument("--session-id", required=True, help="Session UUID")
    parser.add_argument("--provider-id", required=True, help="Provider ID")
    parser.add_argument("--token", required=True, help="JWT proof token")
    parser.add_argument("--state", help="Optional state parameter")

    args = parser.parse_args()

    handler = KYCCallbackHandler(
        provider_registry_path=args.registry,
        proof_registry_path=args.proof_registry,
        audit_log_path=args.audit_log,
        expected_audience=args.audience,
    )

    try:
        result = handler.handle_callback(
            session_id=args.session_id,
            provider_id=args.provider_id,
            proof_token=args.token,
            state=args.state,
        )
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(json.dumps({"status": "FAIL", "error": str(e)}, indent=2))
        exit(1)

if __name__ == "__main__":
    main()
