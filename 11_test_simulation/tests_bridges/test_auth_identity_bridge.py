"""
Test: 14_zero_time_auth → 08_identity_score bridge
Tests authentication trust score calculation
"""

import pytest
import sys
import os

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, project_root)

# Load module with importlib since module names starting with numbers are invalid
import importlib.util
spec = importlib.util.spec_from_file_location(
    "bridge_identity_score",
    os.path.join(project_root, "14_zero_time_auth/interconnect/bridge_identity_score.py")
)
bridge_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bridge_module)

auth_trust_level = bridge_module.auth_trust_level
check_auth_threshold = bridge_module.check_auth_threshold
classify_auth_risk = bridge_module.classify_auth_risk
recommend_auth_method = bridge_module.recommend_auth_method

@pytest.fixture
def high_trust_profile():
    """Profile with high trust score."""
    return {
        "kyc_verified": True,
        "credential_count": 10,
        "reputation_score": 0.9,
        "compliance_flags": 0.95,
        "activity_score": 0.8,
        "sanctions_hit": False,
        "fraud_suspected": False,
    }

@pytest.fixture
def low_trust_profile():
    """Profile with low trust score."""
    return {
        "kyc_verified": False,
        "credential_count": 1,
        "reputation_score": 0.3,
        "compliance_flags": 0.5,
        "activity_score": 0.2,
        "sanctions_hit": True,
        "fraud_suspected": False,
    }

def test_auth_trust_level_high(high_trust_profile):
    """Test trust level calculation for high trust profile."""
    score = auth_trust_level(high_trust_profile)

    assert isinstance(score, int)
    assert 0 <= score <= 100
    assert score >= 70  # High trust should score well

def test_auth_trust_level_low(low_trust_profile):
    """Test trust level calculation for low trust profile."""
    score = auth_trust_level(low_trust_profile)

    assert isinstance(score, int)
    assert 0 <= score <= 100
    assert score < 50  # Low trust with sanctions hit

def test_check_auth_threshold_pass(high_trust_profile):
    """Test authentication threshold check - passing."""
    result = check_auth_threshold(high_trust_profile, threshold=70)

    assert "score" in result
    assert "threshold" in result
    assert "authorized" in result
    assert result["authorized"] is True
    assert result["margin"] >= 0

def test_check_auth_threshold_fail(low_trust_profile):
    """Test authentication threshold check - failing."""
    result = check_auth_threshold(low_trust_profile, threshold=70)

    assert result["authorized"] is False
    assert result["margin"] < 0

def test_classify_auth_risk_low(high_trust_profile):
    """Test risk classification for low risk profile."""
    risk = classify_auth_risk(high_trust_profile)

    assert risk in ["low", "medium", "high", "critical"]
    assert risk in ["low", "medium"]  # High trust = low/medium risk

def test_classify_auth_risk_critical(low_trust_profile):
    """Test risk classification for critical risk profile."""
    risk = classify_auth_risk(low_trust_profile)

    assert risk in ["low", "medium", "high", "critical"]
    assert risk in ["high", "critical"]  # Low trust = high/critical risk

def test_recommend_auth_method_high_trust(high_trust_profile):
    """Test auth method recommendation for high trust."""
    rec = recommend_auth_method(high_trust_profile)

    assert "method" in rec
    assert "risk_level" in rec
    assert "score" in rec
    assert rec["method"] != "deny"

def test_recommend_auth_method_low_trust(low_trust_profile):
    """Test auth method recommendation for low trust."""
    rec = recommend_auth_method(low_trust_profile)

    assert "method" in rec
    assert "risk_level" in rec
    assert rec["risk_level"] in ["high", "critical"]
    # Low trust should require more security
    assert rec.get("require_mfa") is True or rec["method"] == "deny"

def test_recommend_auth_method_structure():
    """Test recommendation structure."""
    profile = {
        "kyc_verified": True,
        "credential_count": 5,
        "reputation_score": 0.7,
        "compliance_flags": 0.8,
        "activity_score": 0.6,
        "sanctions_hit": False,
        "fraud_suspected": False,
    }

    rec = recommend_auth_method(profile)

    required_keys = ["method", "score", "risk_level", "session_duration_minutes"]
    for key in required_keys:
        assert key in rec, f"Missing key: {key}"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
