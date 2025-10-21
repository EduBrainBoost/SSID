"""
Bridge: 01_ai_layer → 23_compliance
Purpose: Policy validation for AI decisions
Evidence: SHA-256 logged in 24_meta_orchestration/registry/logs/
"""

import sys
import os
from typing import Dict, Any

# Add path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

try:
    from compliance.policies.policy_engine import evaluate_policy, get_policy  # type: ignore
except ImportError:
    # Fallback for direct imports
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "policy_engine",
            os.path.join(os.path.dirname(__file__), "../../23_compliance/policies/policy_engine.py")
        )
        if spec and spec.loader:
            policy_engine = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(policy_engine)
            evaluate_policy = policy_engine.evaluate_policy
            get_policy = policy_engine.get_policy
        else:
            raise ImportError("Could not load policy_engine")
    except Exception as e:
        raise ImportError(f"Could not load policy_engine: {e}")

def validate_ai_decision(decision: Dict[str, Any], policy: str = "AI_DECISION_POLICY") -> bool:
    """
    Validate an AI decision against compliance policies.

    Args:
        decision: Dict containing AI decision metadata
            - confidence: float (0-1)
            - explanation: str (optional)
            - bias_score: float (0-1)
            - human_reviewed: bool (optional)
        policy: Policy name to evaluate against

    Returns:
        True if decision complies with policy, False otherwise
    """
    return evaluate_policy(policy, decision)

def get_ai_policy_requirements(policy: str = "AI_DECISION_POLICY") -> Dict[str, Any]:
    """
    Retrieve the requirements for AI decision policy.

    Args:
        policy: Policy name to retrieve

    Returns:
        Policy definition dict
    """
    return get_policy(policy)

def validate_ai_batch(decisions: list, policy: str = "AI_DECISION_POLICY") -> Dict[str, Any]:
    """
    Validate a batch of AI decisions.

    Args:
        decisions: List of decision dicts
        policy: Policy name to evaluate against

    Returns:
        Dict with validation results:
            - total: int
            - passed: int
            - failed: int
            - pass_rate: float
    """
    total = len(decisions)
    passed = sum(1 for d in decisions if validate_ai_decision(d, policy))
    failed = total - passed

    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "pass_rate": passed / total if total > 0 else 0.0,
    }

if __name__ == "__main__":
    # Self-test
    print("Bridge: 01_ai_layer → 23_compliance")

    test_decision = {
        "confidence": 0.85,
        "explanation": "Test decision with high confidence",
        "bias_score": 0.2,
    }

    print("Valid decision:", validate_ai_decision(test_decision))
    print("Policy requirements:", get_ai_policy_requirements())

    batch = [
        {"confidence": 0.9, "explanation": "Good", "bias_score": 0.1},
        {"confidence": 0.5, "explanation": "Bad", "bias_score": 0.5},
        {"confidence": 0.8, "explanation": "Good", "bias_score": 0.2},
    ]
    print("Batch validation:", validate_ai_batch(batch))
