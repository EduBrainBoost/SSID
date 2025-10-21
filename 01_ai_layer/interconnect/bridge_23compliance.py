#!/usr/bin/env python3
"""Bridge: 01_ai_layer -> 23_compliance - Policy Validation"""

from typing import Dict, Any
from pathlib import Path

def validate_ai_decision(decision: Dict[str, Any], policy_name: str = "AI_ETHICS") -> bool:
    """
    Validate AI decision against compliance policies.

    Args:
        decision: AI decision dict with keys: model, score, confidence, features
        policy_name: Policy to validate against

    Returns:
        True if compliant, False otherwise
    """
    # Basic validation rules
    if not isinstance(decision, dict):
        return False

    # Check required fields
    required_fields = ["model", "score", "confidence"]
    if not all(field in decision for field in required_fields):
        return False

    # Confidence must be >= 0.7 for production use
    if decision.get("confidence", 0) < 0.7:
        return False

    # Score must be within valid range
    score = decision.get("score", 0)
    if not (0 <= score <= 100):
        return False

    return True

def check_bias_constraints(features: Dict[str, Any]) -> bool:
    """
    Check if feature set violates bias constraints.

    Args:
        features: Feature dictionary from AI model

    Returns:
        True if no bias violations, False otherwise
    """
    # Prohibited features that could introduce bias
    prohibited = ["race", "religion", "political_affiliation", "sexual_orientation"]

    for feature_name in features.keys():
        if any(prohibited_term in feature_name.lower() for prohibited_term in prohibited):
            return False

    return True

def log_ai_compliance_check(decision: Dict, result: bool) -> None:
    """Log compliance check to evidence trail"""
    repo_root = Path(__file__).resolve().parents[2]
    log_path = repo_root / "23_compliance" / "evidence" / "ai_decisions" / "compliance_checks.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)

    import json
    from datetime import datetime, timezone

    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "decision_id": decision.get("id", "unknown"),
        "compliant": result
    }

    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")

if __name__ == "__main__":
    test_decision = {"model": "identity_scorer", "score": 75, "confidence": 0.85, "id": "test-001"}
    print("Valid:", validate_ai_decision(test_decision))
