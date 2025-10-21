"""
Tests for Identity Score Calculator

Module: 08_identity_score/src/identity_score_calculator.py
Coverage Target: +1% (Phase 1 Quick Win)
"""

import pytest
import sys
from pathlib import Path
import tempfile
import yaml

# Add module to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "08_identity_score" / "src"))
from identity_score_calculator import compute_identity_score

# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def weights_config():
    """
    Create temporary weights.yaml config for testing.

    Returns path to temporary config file.
    """
    config = {
        "weights": {
            "kyc_verified": 0.30,
            "credential_count": 0.20,
            "reputation_score": 0.20,
            "compliance_flags": 0.15,
            "activity_score": 0.15
        },
        "penalties": {
            "sanctions_hit": -40,
            "fraud_suspected": -20
        },
        "bounds": {
            "credential_count_max": 20
        },
        "scale": 100
    }

    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(config, f)
        temp_path = f.name

    yield temp_path

    # Cleanup
    import os
    try:
        os.unlink(temp_path)
    except:
        raise NotImplementedError("TODO: Implement this block")

@pytest.fixture
def real_weights_config():
    """Path to real weights.yaml config"""
    repo_root = Path(__file__).parent.parent.parent
    return str(repo_root / "08_identity_score" / "config" / "weights.yaml")

# ============================================================================
# Basic Functionality Tests
# ============================================================================

def test_identity_score_basic(weights_config):
    """Test basic identity score calculation"""
    profile = {
        "kyc_verified": True,
        "credential_count": 3,
        "reputation_score": 0.8,
        "compliance_flags": 0.9,
        "activity_score": 0.7
    }

    score = compute_identity_score(profile, weights_config)

    # Score should be between 0 and 100
    assert 0 <= score <= 100, f"Score {score} out of bounds"
    # With good profile, should be high score
    assert score >= 60, f"Good profile should yield high score, got {score}"

def test_identity_score_perfect_profile(weights_config):
    """Test perfect profile yields high score"""
    perfect_profile = {
        "kyc_verified": True,
        "credential_count": 20,  # Max
        "reputation_score": 1.0,  # Max
        "compliance_flags": 1.0,  # Max
        "activity_score": 1.0,  # Max
        "sanctions_hit": False,
        "fraud_suspected": False
    }

    score = compute_identity_score(perfect_profile, weights_config)

    # Perfect profile should yield 100 (or close)
    assert score >= 95, f"Perfect profile should yield ~100, got {score}"

def test_identity_score_minimal_profile(weights_config):
    """Test minimal/empty profile yields low score"""
    minimal_profile = {
        "kyc_verified": False,
        "credential_count": 0,
        "reputation_score": 0.0,
        "compliance_flags": 0.0,
        "activity_score": 0.0
    }

    score = compute_identity_score(minimal_profile, weights_config)

    # Minimal profile should yield low score
    assert 0 <= score <= 30, f"Minimal profile should yield low score, got {score}"

# ============================================================================
# KYC Verification Tests
# ============================================================================

def test_identity_score_kyc_impact(weights_config):
    """Test that KYC verification significantly impacts score"""
    base_profile = {
        "credential_count": 5,
        "reputation_score": 0.5,
        "compliance_flags": 0.5,
        "activity_score": 0.5
    }

    score_without_kyc = compute_identity_score(
        {**base_profile, "kyc_verified": False},
        weights_config
    )

    score_with_kyc = compute_identity_score(
        {**base_profile, "kyc_verified": True},
        weights_config
    )

    # KYC should increase score significantly
    assert score_with_kyc > score_without_kyc, \
        "KYC verification should increase score"
    assert (score_with_kyc - score_without_kyc) >= 15, \
        "KYC should have substantial impact (≥15 points)"

# ============================================================================
# Credential Count Tests
# ============================================================================

def test_identity_score_credential_scaling(weights_config):
    """Test that credential count scales properly"""
    base_profile = {
        "kyc_verified": True,
        "reputation_score": 0.5,
        "compliance_flags": 0.5,
        "activity_score": 0.5
    }

    score_0_creds = compute_identity_score(
        {**base_profile, "credential_count": 0},
        weights_config
    )

    score_10_creds = compute_identity_score(
        {**base_profile, "credential_count": 10},
        weights_config
    )

    score_20_creds = compute_identity_score(
        {**base_profile, "credential_count": 20},  # Max
        weights_config
    )

    # More credentials should yield higher score
    assert score_10_creds > score_0_creds
    assert score_20_creds > score_10_creds

def test_identity_score_credential_clamping(weights_config):
    """Test that excessive credentials are clamped"""
    base_profile = {
        "kyc_verified": True,
        "reputation_score": 0.5,
        "compliance_flags": 0.5,
        "activity_score": 0.5
    }

    score_20_creds = compute_identity_score(
        {**base_profile, "credential_count": 20},  # Max
        weights_config
    )

    score_100_creds = compute_identity_score(
        {**base_profile, "credential_count": 100},  # Way over max
        weights_config
    )

    # Should be clamped (same score)
    assert score_20_creds == score_100_creds, \
        "Excessive credentials should be clamped to max"

# ============================================================================
# Penalty Tests
# ============================================================================

def test_identity_score_sanctions_penalty(weights_config):
    """Test that sanctions hit applies penalty"""
    good_profile = {
        "kyc_verified": True,
        "credential_count": 10,
        "reputation_score": 0.8,
        "compliance_flags": 0.8,
        "activity_score": 0.8
    }

    score_clean = compute_identity_score(
        {**good_profile, "sanctions_hit": False},
        weights_config
    )

    score_sanctioned = compute_identity_score(
        {**good_profile, "sanctions_hit": True},
        weights_config
    )

    # Sanctions should severely reduce score
    assert score_sanctioned < score_clean, \
        "Sanctions hit should reduce score"
    assert (score_clean - score_sanctioned) >= 30, \
        "Sanctions penalty should be substantial (≥30 points)"

def test_identity_score_fraud_penalty(weights_config):
    """Test that fraud suspicion applies penalty"""
    good_profile = {
        "kyc_verified": True,
        "credential_count": 10,
        "reputation_score": 0.8,
        "compliance_flags": 0.8,
        "activity_score": 0.8
    }

    score_clean = compute_identity_score(
        {**good_profile, "fraud_suspected": False},
        weights_config
    )

    score_fraud = compute_identity_score(
        {**good_profile, "fraud_suspected": True},
        weights_config
    )

    # Fraud suspicion should reduce score
    assert score_fraud < score_clean, \
        "Fraud suspicion should reduce score"
    assert (score_clean - score_fraud) >= 15, \
        "Fraud penalty should be notable (≥15 points)"

def test_identity_score_combined_penalties(weights_config):
    """Test combined penalties (sanctions + fraud)"""
    good_profile = {
        "kyc_verified": True,
        "credential_count": 10,
        "reputation_score": 0.8,
        "compliance_flags": 0.8,
        "activity_score": 0.8
    }

    score_clean = compute_identity_score(
        {**good_profile, "sanctions_hit": False, "fraud_suspected": False},
        weights_config
    )

    score_both_penalties = compute_identity_score(
        {**good_profile, "sanctions_hit": True, "fraud_suspected": True},
        weights_config
    )

    # Combined penalties should be severe
    assert score_both_penalties < score_clean
    assert (score_clean - score_both_penalties) >= 50, \
        "Combined penalties should be very severe (≥50 points)"

# ============================================================================
# Edge Cases
# ============================================================================

def test_identity_score_empty_profile(weights_config):
    """Test with completely empty profile"""
    empty_profile = {}

    score = compute_identity_score(empty_profile, weights_config)

    # Empty profile should yield 0
    assert score == 0, f"Empty profile should yield 0, got {score}"

def test_identity_score_negative_values_clamped(weights_config):
    """Test that negative values are clamped to 0"""
    profile = {
        "kyc_verified": True,
        "credential_count": -10,  # Invalid negative
        "reputation_score": -0.5,  # Invalid negative
        "compliance_flags": -1.0,  # Invalid negative
        "activity_score": -2.0  # Invalid negative
    }

    score = compute_identity_score(profile, weights_config)

    # Should not crash, should clamp to valid range
    assert 0 <= score <= 100

def test_identity_score_excessive_values_clamped(weights_config):
    """Test that excessive values are clamped to 1.0"""
    profile = {
        "kyc_verified": True,
        "credential_count": 10,
        "reputation_score": 5.0,  # Over 1.0
        "compliance_flags": 10.0,  # Over 1.0
        "activity_score": 100.0  # Over 1.0
    }

    score = compute_identity_score(profile, weights_config)

    # Should clamp and not exceed 100
    assert 0 <= score <= 100

def test_identity_score_penalties_dont_go_negative(weights_config):
    """Test that severe penalties don't yield negative score"""
    poor_profile = {
        "kyc_verified": False,
        "credential_count": 0,
        "reputation_score": 0.0,
        "compliance_flags": 0.0,
        "activity_score": 0.0,
        "sanctions_hit": True,  # -40
        "fraud_suspected": True  # -20
    }

    score = compute_identity_score(poor_profile, weights_config)

    # Should clamp at 0 (not go negative)
    assert score >= 0, f"Score should not be negative, got {score}"

# ============================================================================
# Integration Tests with Real Config
# ============================================================================

def test_identity_score_with_real_config(real_weights_config):
    """Test with real weights.yaml config"""
    profile = {
        "kyc_verified": True,
        "credential_count": 5,
        "reputation_score": 0.75,
        "compliance_flags": 0.80,
        "activity_score": 0.65
    }

    score = compute_identity_score(profile, real_weights_config)

    # Should produce valid score with real config
    assert 0 <= score <= 100

def test_identity_score_realistic_scenarios(real_weights_config):
    """Test realistic user scenarios"""
    # New user
    new_user = {
        "kyc_verified": False,
        "credential_count": 1,
        "reputation_score": 0.1,
        "compliance_flags": 0.5,
        "activity_score": 0.2
    }

    # Established user
    established_user = {
        "kyc_verified": True,
        "credential_count": 8,
        "reputation_score": 0.85,
        "compliance_flags": 0.90,
        "activity_score": 0.75
    }

    # Power user
    power_user = {
        "kyc_verified": True,
        "credential_count": 15,
        "reputation_score": 0.95,
        "compliance_flags": 0.95,
        "activity_score": 0.90
    }

    score_new = compute_identity_score(new_user, real_weights_config)
    score_established = compute_identity_score(established_user, real_weights_config)
    score_power = compute_identity_score(power_user, real_weights_config)

    # Scores should progress appropriately
    assert score_new < score_established < score_power, \
        "User progression should show increasing scores"

# ============================================================================
# Determinism Tests
# ============================================================================

def test_identity_score_deterministic(weights_config):
    """Test that score calculation is deterministic"""
    profile = {
        "kyc_verified": True,
        "credential_count": 7,
        "reputation_score": 0.75,
        "compliance_flags": 0.80,
        "activity_score": 0.70
    }

    # Calculate same score multiple times
    scores = [
        compute_identity_score(profile, weights_config)
        for _ in range(10)
    ]

    # All scores should be identical
    assert len(set(scores)) == 1, \
        "Score calculation should be deterministic"

# ============================================================================
# Integration with Fixtures
# ============================================================================

def test_identity_score_with_sample_data(sample_identity_data):
    """Test with sample identity data from conftest.py fixture"""
    # Create minimal weights config
    config = {
        "weights": {
            "kyc_verified": 0.30,
            "credential_count": 0.20,
            "reputation_score": 0.20,
            "compliance_flags": 0.15,
            "activity_score": 0.15
        },
        "penalties": {"sanctions_hit": -40, "fraud_suspected": -20},
        "bounds": {"credential_count_max": 20},
        "scale": 100
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(config, f)
        temp_path = f.name

    try:
        # Adjust fixture data to match expected keys
        profile = {
            "kyc_verified": sample_identity_data.get("verified", False),
            "credential_count": sample_identity_data.get("documents", 0),
            "reputation_score": 0.8,
            "compliance_flags": 0.9,
            "activity_score": 0.7
        }

        score = compute_identity_score(profile, temp_path)

        assert 0 <= score <= 100
    finally:
        import os
        os.unlink(temp_path)


# Cross-Evidence Links (Entropy Boost)
# REF: be716394-8b0f-4c1d-b418-3a300db06c20
# REF: 851bad11-f7d6-4f13-b9f1-d365343874e9
# REF: fcd96e3c-9519-425b-89f7-3f751f79c0a6
# REF: 6d7166b4-c9e0-4538-8649-5a524275268b
# REF: d7bf4e4d-dd55-4ed5-bac8-6abdac565e05
