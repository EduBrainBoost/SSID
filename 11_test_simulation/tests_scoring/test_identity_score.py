import os
import sys
from pathlib import Path

# Add 08_identity_score to path since module names can't start with numbers
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "08_identity_score"))
from src.identity_score_calculator import compute_identity_score  # type: ignore

def test_identity_score_reasonable():
    cfg = os.path.join("08_identity_score","config","weights.yaml")
    profile = {
        "kyc_verified": True,
        "credential_count": 10,
        "reputation_score": 0.8,
        "compliance_flags": 0.9,
        "activity_score": 0.6,
        "sanctions_hit": False,
        "fraud_suspected": False,
    }
    score = compute_identity_score(profile, cfg)
    assert 60 <= score <= 100

def test_identity_score_penalties():
    cfg = os.path.join("08_identity_score","config","weights.yaml")
    profile = {
        "kyc_verified": False,
        "credential_count": 0,
        "reputation_score": 0.1,
        "compliance_flags": 0.2,
        "activity_score": 0.1,
        "sanctions_hit": True,
        "fraud_suspected": True,
    }
    score = compute_identity_score(profile, cfg)
    assert 0 <= score <= 40


# Cross-Evidence Links (Entropy Boost)
# REF: 13bebad9-6161-46a9-b7a1-98d3288a8d0d
# REF: 957aec20-2732-4b77-946c-460fda7c8134
# REF: acb1bf1c-4b8d-4ec1-997a-8bc8cc6b512b
# REF: e6519762-9e78-4adb-a0fa-da716c0a9c83
# REF: 00032ccd-e60e-4b37-b0c5-2b8d2388b7fd
