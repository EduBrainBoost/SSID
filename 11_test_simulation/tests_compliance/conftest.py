"""
Pytest configuration for compliance tests.
Sets up import paths for 23_compliance modules.
"""

import sys
from pathlib import Path

# Add 23_compliance to path for anti_gaming imports
repo_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(repo_root / "23_compliance"))

# Fixtures for badge validation tests
import pytest
import hashlib

@pytest.fixture
def sample_valid_badges():
    """Sample of valid badge records."""
    def sha256(text):
        return hashlib.sha256(text.encode()).hexdigest()

    return [
        {
            "id": "valid-001",
            "payload": "user:alice,merit:kyc_verified",
            "sig": sha256("user:alice,merit:kyc_verified")
        },
        {
            "id": "valid-002",
            "payload": "user:bob,merit:high_trust",
            "sig": sha256("user:bob,merit:high_trust")
        },
        {
            "id": "valid-003",
            "payload": "user:charlie,merit:expert",
            "sig": sha256("user:charlie,merit:expert")
        }
    ]

@pytest.fixture
def sample_invalid_badges():
    """Sample of invalid badge records."""
    return [
        {
            "id": "invalid-001",
            "payload": "user:eve,merit:fake",
            "sig": "WRONG_SIGNATURE_123"
        },
        {
            "id": "invalid-002",
            "payload": "user:mallory",
            "sig": ""
        },
        {
            "id": "invalid-003",
            "payload": "tampered_data",
            "sig": "0000000000"
        }
    ]

@pytest.fixture
def sample_mixed_badges(sample_valid_badges, sample_invalid_badges):
    """Sample of mixed valid and invalid badges."""
    return sample_valid_badges + sample_invalid_badges
