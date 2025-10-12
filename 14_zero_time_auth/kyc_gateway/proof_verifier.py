#!/usr/bin/env python3
"""
SSID KYC Gateway - Proof Verifier
License: GPL-3.0-or-later

Verifies JWT/VC proofs from KYC providers:
- JWK signature validation
- Issuer/audience/expiry checks
- Claim normalization and hashing
- No PII storage (hash-only)

Security: Strict validation, replay protection, deterministic digest computation
Privacy: PII filtering enforced before hashing
"""

import hashlib
import json
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple
from urllib.parse import urljoin
from urllib.request import urlopen

try:
    import jwt
    from jwt import PyJWK
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.backends import default_backend
except ImportError:
    raise ImportError("Install dependencies: pip install PyJWT cryptography")


class ProofVerifierError(Exception):
    """Base exception for proof verification errors"""
    pass


class InvalidSignatureError(ProofVerifierError):
    """JWT signature validation failed"""
    pass


class InvalidIssuerError(ProofVerifierError):
    """Issuer claim mismatch"""
    pass


class InvalidAudienceError(ProofVerifierError):
    """Audience claim mismatch"""
    pass


class ExpiredTokenError(ProofVerifierError):
    """Token expired"""
    pass


class PIIDetectedError(ProofVerifierError):
    """PII detected in claims (not allowed)"""
    pass


# PII field blacklist (enforce no-PII policy)
PII_FORBIDDEN_FIELDS: Set[str] = {
    "name", "given_name", "family_name", "middle_name",
    "birthdate", "birth_date", "dob",
    "address", "street_address", "locality", "region", "postal_code", "country",
    "email", "email_verified",
    "phone_number", "phone", "phone_verified",
    "ssn", "tax_id", "national_id",
    "passport", "passport_number",
    "drivers_license", "id_number", "document_number",
    "picture", "photo",
}


class ProofVerifier:
    """
    Verifies cryptographic proofs (JWT/VC) from KYC providers.

    Features:
    - JWK-based signature verification
    - Issuer/audience/expiry validation
    - Deterministic claim normalization
    - SHA-256 or BLAKE2b digest computation
    - PII detection and rejection
    - Replay protection (jti tracking)
    """

    def __init__(
        self,
        expected_audience: str,
        max_clock_skew_seconds: int = 60,
        jti_cache_ttl_seconds: int = 3600,
    ):
        """
        Initialize proof verifier.

        Args:
            expected_audience: Expected 'aud' claim value
            max_clock_skew_seconds: Maximum allowed clock skew for exp/nbf
            jti_cache_ttl_seconds: TTL for jti replay cache
        """
        self.expected_audience = expected_audience
        self.max_clock_skew = max_clock_skew_seconds
        self.jti_cache_ttl = jti_cache_ttl_seconds
        self._jti_cache: Dict[str, float] = {}  # jti -> timestamp
        self._jwk_cache: Dict[str, Any] = {}  # jwk_url -> keys

    def verify_jwt(
        self,
        token: str,
        provider_id: str,
        expected_issuer: str,
        jwk_set_url: str,
        allowed_algorithms: Optional[List[str]] = None,
    ) -> Tuple[Dict[str, Any], str]:
        """
        Verify JWT proof from provider.

        Args:
            token: JWT string
            provider_id: Provider identifier
            expected_issuer: Expected 'iss' claim
            jwk_set_url: Provider's JWK Set URL
            allowed_algorithms: Allowed signature algorithms

        Returns:
            Tuple of (validated_claims, digest)

        Raises:
            ProofVerifierError: On validation failure
        """
        if allowed_algorithms is None:
            allowed_algorithms = ["RS256", "RS384", "RS512", "ES256", "ES384", "ES512", "EdDSA"]

        # Fetch JWK Set (with caching)
        jwk_set = self._fetch_jwk_set(jwk_set_url)

        # Decode JWT header to get kid
        try:
            unverified_header = jwt.get_unverified_header(token)
            kid = unverified_header.get("kid")
        except Exception as e:
            raise ProofVerifierError(f"Invalid JWT header: {e}")

        # Find matching JWK
        jwk_data = self._find_jwk(jwk_set, kid)
        if not jwk_data:
            raise InvalidSignatureError(f"JWK kid={kid} not found in provider JWK Set")

        # Verify signature and decode
        try:
            public_key = PyJWK.from_dict(jwk_data).key
            claims = jwt.decode(
                token,
                public_key,
                algorithms=allowed_algorithms,
                audience=self.expected_audience,
                issuer=expected_issuer,
                options={
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_nbf": True,
                    "verify_aud": True,
                    "verify_iss": True,
                    "require": ["exp", "iat", "iss", "aud", "jti"],
                },
                leeway=self.max_clock_skew,
            )
        except jwt.ExpiredSignatureError as e:
            raise ExpiredTokenError(f"Token expired: {e}")
        except jwt.InvalidAudienceError as e:
            raise InvalidAudienceError(f"Invalid audience: {e}")
        except jwt.InvalidIssuerError as e:
            raise InvalidIssuerError(f"Invalid issuer: {e}")
        except jwt.InvalidSignatureError as e:
            raise InvalidSignatureError(f"Signature verification failed: {e}")
        except Exception as e:
            raise ProofVerifierError(f"JWT verification failed: {e}")

        # Replay protection: Check jti
        jti = claims.get("jti")
        if not jti:
            raise ProofVerifierError("Missing required 'jti' claim")

        if self._is_jti_seen(jti):
            raise ProofVerifierError(f"Replay detected: jti={jti} already seen")

        self._mark_jti_seen(jti)

        # PII filtering: Ensure no forbidden fields
        self._check_pii(claims)

        # Normalize claims and compute digest
        normalized = self._normalize_claims(claims)
        digest = self._compute_digest(normalized, algorithm="SHA-256")

        return claims, digest

    def _fetch_jwk_set(self, jwk_set_url: str) -> Dict[str, Any]:
        """Fetch JWK Set from provider URL (with caching)"""
        if jwk_set_url in self._jwk_cache:
            return self._jwk_cache[jwk_set_url]

        try:
            with urlopen(jwk_set_url, timeout=5) as response:
                jwk_set = json.loads(response.read().decode("utf-8"))
                self._jwk_cache[jwk_set_url] = jwk_set
                return jwk_set
        except Exception as e:
            raise ProofVerifierError(f"Failed to fetch JWK Set from {jwk_set_url}: {e}")

    def _find_jwk(self, jwk_set: Dict[str, Any], kid: Optional[str]) -> Optional[Dict[str, Any]]:
        """Find JWK by kid in JWK Set"""
        keys = jwk_set.get("keys", [])
        if not kid:
            return keys[0] if keys else None

        for key in keys:
            if key.get("kid") == kid:
                return key
        return None

    def _check_pii(self, claims: Dict[str, Any]) -> None:
        """
        Check claims for forbidden PII fields.

        Raises:
            PIIDetectedError: If PII field detected
        """
        forbidden_found = []
        for key in claims.keys():
            if key.lower() in PII_FORBIDDEN_FIELDS:
                forbidden_found.append(key)

        if forbidden_found:
            raise PIIDetectedError(f"PII fields detected (not allowed): {forbidden_found}")

    def _normalize_claims(self, claims: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize claims for deterministic hashing.

        - Remove standard JWT fields (iss, aud, exp, nbf, iat, jti)
        - Sort keys alphabetically
        - Serialize to canonical JSON
        """
        # Remove standard JWT metadata
        excluded = {"iss", "aud", "exp", "nbf", "iat", "jti", "sub"}
        normalized = {k: v for k, v in claims.items() if k not in excluded}

        # Sort keys for determinism
        return dict(sorted(normalized.items()))

    def _compute_digest(self, data: Dict[str, Any], algorithm: str = "SHA-256") -> str:
        """
        Compute cryptographic digest of normalized claims.

        Args:
            data: Normalized claims dictionary
            algorithm: Hash algorithm (SHA-256 or BLAKE2b)

        Returns:
            Hex-encoded digest string
        """
        # Serialize to canonical JSON (sorted keys, no whitespace)
        canonical_json = json.dumps(data, sort_keys=True, separators=(",", ":"))

        if algorithm == "SHA-256":
            digest = hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()
        elif algorithm == "BLAKE2b":
            digest = hashlib.blake2b(canonical_json.encode("utf-8")).hexdigest()
        else:
            raise ValueError(f"Unsupported hash algorithm: {algorithm}")

        return digest

    def _is_jti_seen(self, jti: str) -> bool:
        """Check if jti has been seen (replay protection)"""
        # Clean expired entries
        now = time.time()
        self._jti_cache = {
            k: v for k, v in self._jti_cache.items()
            if now - v < self.jti_cache_ttl
        }

        return jti in self._jti_cache

    def _mark_jti_seen(self, jti: str) -> None:
        """Mark jti as seen (replay protection)"""
        self._jti_cache[jti] = time.time()


def create_proof_record(
    proof_id: str,
    provider_id: str,
    digest: str,
    algorithm: str,
    policy_version: str = "1.0",
    evidence_chain: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Create proof record for persistence (JSONL format).

    Args:
        proof_id: Unique proof UUID
        provider_id: Provider identifier
        digest: Proof digest (hex)
        algorithm: Hash algorithm used
        policy_version: Policy version at time of creation
        evidence_chain: Optional evidence hash chain

    Returns:
        Proof record dictionary (ready for JSONL append)
    """
    return {
        "id": proof_id,
        "provider_id": provider_id,
        "digest": digest,
        "algorithm": algorithm,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "policy_version": policy_version,
        "evidence_chain": evidence_chain or [],
    }
