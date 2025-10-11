#!/usr/bin/env python3
"""Bridge: 14_zero_time_auth -> 08_identity_score - Trust Level"""

from typing import Dict


def get_auth_trust_level(profile: Dict) -> int:
    """
    Compute authentication trust level (0-100) based on identity score.

    Args:
        profile: User profile dict with identity attributes

    Returns:
        Trust score 0-100
    """
    if not profile or not isinstance(profile, dict):
        return 0

    # Calculate base trust from profile completeness
    required_fields = ["identity_hash", "did", "verification_level"]
    completeness = sum(1 for field in required_fields if field in profile)
    base_score = (completeness / len(required_fields)) * 100

    # Boost for verified attributes
    verification_level = profile.get("verification_level", "none")
    verification_boost = {
        "none": 0,
        "email": 10,
        "phone": 15,
        "kyc_basic": 25,
        "kyc_enhanced": 40
    }.get(verification_level, 0)

    # Penalty for recent security events
    recent_security_events = profile.get("security_events_30d", 0)
    security_penalty = min(recent_security_events * 5, 30)

    # Final score
    trust_score = base_score + verification_boost - security_penalty

    return max(0, min(100, int(trust_score)))


def require_minimum_trust(min_trust: int = 50) -> callable:
    """Decorator to enforce minimum trust level for auth operations"""
    def decorator(func):
        def wrapper(profile: Dict, *args, **kwargs):
            trust = get_auth_trust_level(profile)
            if trust < min_trust:
                raise PermissionError(f"Insufficient trust level: {trust} < {min_trust}")
            return func(profile, *args, **kwargs)
        return wrapper
    return decorator


if __name__ == "__main__":
    test_profile = {
        "identity_hash": "abc123",
        "did": "did:ssid:test",
        "verification_level": "kyc_basic",
        "security_events_30d": 0
    }
    print("Trust Level:", get_auth_trust_level(test_profile))
