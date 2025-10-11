"""
Bridge: 14_zero_time_auth → 08_identity_score
Purpose: Trust score verification for authentication flow
Evidence: SHA-256 logged in 24_meta_orchestration/registry/logs/
"""

import sys
import os
from typing import Dict, Any

# Add path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

try:
    from identity_score.src.identity_score_calculator import compute_identity_score  # type: ignore
except ImportError:
    # Fallback for direct imports
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "identity_score_calculator",
            os.path.join(
                os.path.dirname(__file__),
                "../../08_identity_score/src/identity_score_calculator.py"
            )
        )
        if spec and spec.loader:
            calc_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(calc_module)
            compute_identity_score = calc_module.compute_identity_score
        else:
            raise ImportError("Could not load identity_score_calculator")
    except Exception as e:
        raise ImportError(f"Could not load identity_score_calculator: {e}")


def auth_trust_level(profile: Dict[str, Any], config_path: str = None) -> int:
    """
    Compute trust level (0-100) for authentication flow.

    Args:
        profile: User profile dict with identity attributes
        config_path: Optional path to weights config (defaults to standard location)

    Returns:
        Trust score (0-100)
    """
    if config_path is None:
        config_path = os.path.join(
            os.path.dirname(__file__),
            "../../08_identity_score/config/weights.yaml"
        )

    return compute_identity_score(profile, config_path)


def check_auth_threshold(profile: Dict[str, Any], threshold: int = 70) -> Dict[str, Any]:
    """
    Check if a profile meets the authentication threshold.

    Args:
        profile: User profile dict
        threshold: Minimum score required for authentication

    Returns:
        Dict with authentication decision and details
    """
    score = auth_trust_level(profile)

    return {
        "score": score,
        "threshold": threshold,
        "authorized": score >= threshold,
        "margin": score - threshold,
    }


def classify_auth_risk(profile: Dict[str, Any]) -> str:
    """
    Classify authentication risk level based on identity score.

    Args:
        profile: User profile dict

    Returns:
        Risk level string: "low", "medium", "high", "critical"
    """
    score = auth_trust_level(profile)

    if score >= 80:
        return "low"
    elif score >= 60:
        return "medium"
    elif score >= 40:
        return "high"
    else:
        return "critical"


def recommend_auth_method(profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recommend authentication method based on identity score.

    Args:
        profile: User profile dict

    Returns:
        Dict with recommended auth method and requirements
    """
    score = auth_trust_level(profile)
    risk = classify_auth_risk(profile)

    recommendations = {
        "low": {
            "method": "single_factor",
            "require_mfa": False,
            "session_duration_minutes": 60,
        },
        "medium": {
            "method": "two_factor",
            "require_mfa": True,
            "session_duration_minutes": 30,
        },
        "high": {
            "method": "two_factor_plus",
            "require_mfa": True,
            "require_biometric": True,
            "session_duration_minutes": 15,
        },
        "critical": {
            "method": "deny",
            "require_manual_review": True,
            "session_duration_minutes": 0,
        },
    }

    result = recommendations[risk].copy()
    result["score"] = score
    result["risk_level"] = risk

    return result


if __name__ == "__main__":
    # Self-test
    print("Bridge: 14_zero_time_auth → 08_identity_score")

    # Test profiles
    high_trust_profile = {
        "kyc_verified": True,
        "credential_count": 10,
        "reputation_score": 0.9,
        "compliance_flags": 0.95,
        "activity_score": 0.8,
        "sanctions_hit": False,
        "fraud_suspected": False,
    }

    low_trust_profile = {
        "kyc_verified": False,
        "credential_count": 1,
        "reputation_score": 0.3,
        "compliance_flags": 0.5,
        "activity_score": 0.2,
        "sanctions_hit": True,
        "fraud_suspected": False,
    }

    print("\nHigh Trust Profile:")
    print("  Score:", auth_trust_level(high_trust_profile))
    print("  Auth Check:", check_auth_threshold(high_trust_profile))
    print("  Risk:", classify_auth_risk(high_trust_profile))
    print("  Recommendation:", recommend_auth_method(high_trust_profile))

    print("\nLow Trust Profile:")
    print("  Score:", auth_trust_level(low_trust_profile))
    print("  Auth Check:", check_auth_threshold(low_trust_profile))
    print("  Risk:", classify_auth_risk(low_trust_profile))
    print("  Recommendation:", recommend_auth_method(low_trust_profile))
