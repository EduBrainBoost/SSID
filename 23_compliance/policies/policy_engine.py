"""
Policy Engine for Compliance
Evaluates decisions and actions against defined compliance policies.
"""

from typing import Dict, Any
import os
import json

# Policy definitions
POLICIES = {
    "AI_DECISION_POLICY": {
        "description": "Policy for AI decision-making compliance",
        "rules": {
            "min_confidence": 0.7,
            "require_explainability": True,
            "max_bias_score": 0.3,
            "require_human_review": False,
        },
    },
    "DATA_PRIVACY_POLICY": {
        "description": "Data privacy and protection policy",
        "rules": {
            "anonymize_pii": True,
            "require_consent": True,
            "data_retention_days": 90,
        },
    },
    "SECURITY_POLICY": {
        "description": "Security and access control policy",
        "rules": {
            "min_password_length": 12,
            "require_mfa": True,
            "session_timeout_minutes": 30,
        },
    },
}

def evaluate_policy(policy_name: str, decision: Dict[str, Any]) -> bool:
    """
    Evaluate a decision against a named policy.

    Args:
        policy_name: Name of the policy to evaluate against
        decision: Decision dictionary containing relevant fields

    Returns:
        True if decision complies with policy, False otherwise
    """
    if policy_name not in POLICIES:
        # Unknown policy - fail closed
        return False

    policy = POLICIES[policy_name]
    rules = policy["rules"]

    # AI Decision Policy
    if policy_name == "AI_DECISION_POLICY":
        confidence = decision.get("confidence", 0.0)
        if confidence < rules["min_confidence"]:
            return False

        if rules["require_explainability"] and not decision.get("explanation"):
            return False

        bias_score = decision.get("bias_score", 1.0)
        if bias_score > rules["max_bias_score"]:
            return False

        if rules["require_human_review"] and not decision.get("human_reviewed"):
            return False

    # Data Privacy Policy
    elif policy_name == "DATA_PRIVACY_POLICY":
        if rules["anonymize_pii"] and not decision.get("pii_anonymized"):
            return False

        if rules["require_consent"] and not decision.get("user_consent"):
            return False

    # Security Policy
    elif policy_name == "SECURITY_POLICY":
        password_length = decision.get("password_length", 0)
        if password_length < rules["min_password_length"]:
            return False

        if rules["require_mfa"] and not decision.get("mfa_enabled"):
            return False

    return True

def get_policy(policy_name: str) -> Dict[str, Any]:
    """
    Retrieve policy definition by name.

    Args:
        policy_name: Name of the policy

    Returns:
        Policy definition dict or empty dict if not found
    """
    return POLICIES.get(policy_name, {})

def list_policies() -> list:
    """
    List all available policy names.

    Returns:
        List of policy names
    """
    return list(POLICIES.keys())

if __name__ == "__main__":
    # Self-test
    print("Available policies:", list_policies())

    # Test AI decision policy
    good_decision = {
        "confidence": 0.85,
        "explanation": "High confidence based on multiple factors",
        "bias_score": 0.15,
    }
    print("Good AI decision passes:", evaluate_policy("AI_DECISION_POLICY", good_decision))

    bad_decision = {
        "confidence": 0.5,
        "bias_score": 0.5,
    }
    print("Bad AI decision fails:", not evaluate_policy("AI_DECISION_POLICY", bad_decision))
