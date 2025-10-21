#!/usr/bin/env python3
"""
Unit tests for Strict Score Authenticity Verification (PROMPT 2)
"""
import pytest
import json
import jsonschema
from pathlib import Path
from datetime import datetime
import uuid
import tempfile
import shutil

REPO_ROOT = Path(__file__).resolve().parents[2]

# Import after path is set
import sys
sys.path.insert(0, str(REPO_ROOT / "02_audit_logging/tools"))
from verify_score_authenticity_strict import (
    load_schema,
    find_all_score_manifests,
    validate_manifest,
    check_certification_chain,
    compute_authenticity_rate
)

@pytest.fixture
def schema():
    """Load schema."""
    return load_schema()

@pytest.fixture
def temp_manifest(tmp_path):
    """Create temporary manifest file."""
    def _create(data):
        manifest_file = tmp_path / "test.score.json"
        with open(manifest_file, 'w') as f:
            json.dump(data, f)
        return manifest_file
    return _create

def test_valid_cert_100_manifest(schema, temp_manifest):
    """Test valid 100/100 certification manifest."""
    manifest_data = {
        "id": str(uuid.uuid4()),
        "kind": "cert",
        "scale": {"max": 100, "min": 0},
        "value": 100,
        "status": "actual",
        "source": {
            "file": "test.md",
            "hash": "a" * 128
        },
        "ci": {
            "commit": "abc123",
            "timestamp": datetime.now().isoformat() + "Z"
        },
        "worm": {
            "uuid": str(uuid.uuid4()),
            "signature": "b" * 128,
            "chain_prev": None
        }
    }

    manifest_file = temp_manifest(manifest_data)
    valid, errors = validate_manifest(manifest_file, schema)

    assert valid, f"Expected valid, got errors: {errors}"
    assert len(errors) == 0

def test_invalid_cert_400_scale(schema, temp_manifest):
    """Test that cert kind cannot use 400 scale."""
    manifest_data = {
        "id": str(uuid.uuid4()),
        "kind": "cert",
        "scale": {"max": 400, "min": 0},  # ❌ cert must use 100
        "value": 100,
        "status": "actual",
        "source": {
            "file": "test.md",
            "hash": "a" * 128
        },
        "ci": {
            "commit": "abc123",
            "timestamp": datetime.now().isoformat() + "Z"
        },
        "worm": {
            "uuid": str(uuid.uuid4()),
            "signature": "b" * 128,
            "chain_prev": None
        }
    }

    manifest_file = temp_manifest(manifest_data)
    valid, errors = validate_manifest(manifest_file, schema)

    assert not valid
    assert any("cert kind must use scale.max=100" in e for e in errors)

def test_invalid_evolution_100_scale(schema, temp_manifest):
    """Test that evolution kind cannot use 100 scale."""
    manifest_data = {
        "id": str(uuid.uuid4()),
        "kind": "evolution",
        "scale": {"max": 100, "min": 0},  # ❌ evolution must use 400
        "value": 100,
        "status": "actual",
        "source": {
            "file": "test.md",
            "hash": "a" * 128
        },
        "ci": {
            "commit": "abc123",
            "timestamp": datetime.now().isoformat() + "Z"
        },
        "worm": {
            "uuid": str(uuid.uuid4()),
            "signature": "b" * 128,
            "chain_prev": None
        }
    }

    manifest_file = temp_manifest(manifest_data)
    valid, errors = validate_manifest(manifest_file, schema)

    assert not valid
    assert any("evolution kind must use scale.max=400" in e for e in errors)

def test_value_exceeds_scale(schema, temp_manifest):
    """Test that value > scale.max fails."""
    manifest_data = {
        "id": str(uuid.uuid4()),
        "kind": "cert",
        "scale": {"max": 100, "min": 0},
        "value": 150,  # ❌ exceeds max
        "status": "actual",
        "source": {
            "file": "test.md",
            "hash": "a" * 128
        },
        "ci": {
            "commit": "abc123",
            "timestamp": datetime.now().isoformat() + "Z"
        },
        "worm": {
            "uuid": str(uuid.uuid4()),
            "signature": "b" * 128,
            "chain_prev": None
        }
    }

    manifest_file = temp_manifest(manifest_data)
    valid, errors = validate_manifest(manifest_file, schema)

    assert not valid
    assert any("outside scale" in e for e in errors)

def test_projection_not_counted_as_actual(schema, temp_manifest):
    """Test that projections have status='projection' not 'actual'."""
    manifest_data = {
        "id": str(uuid.uuid4()),
        "kind": "phase",
        "scale": {"max": 100, "min": 0},
        "value": 85,
        "status": "projection",  # ✓ correct
        "source": {
            "file": "roadmap.md",
            "hash": "a" * 128
        },
        "ci": {
            "commit": "abc123",
            "timestamp": datetime.now().isoformat() + "Z"
        },
        "worm": {
            "uuid": str(uuid.uuid4()),
            "signature": "b" * 128,
            "chain_prev": None
        }
    }

    manifest_file = temp_manifest(manifest_data)
    valid, errors = validate_manifest(manifest_file, schema)

    assert valid

def test_certification_chain_consistency():
    """Test that PLATINUM >= GOLD."""
    manifests = [
        {
            "kind": "cert",
            "status": "actual",
            "value": 90,
            "metadata": {"component": "Core", "grade": "GOLD"}
        },
        {
            "kind": "cert",
            "status": "actual",
            "value": 95,
            "metadata": {"component": "Core", "grade": "PLATINUM"}
        }
    ]

    valid, errors = check_certification_chain(manifests)
    assert valid, f"Expected valid chain, got: {errors}"

def test_certification_chain_violation():
    """Test that PLATINUM < GOLD fails."""
    manifests = [
        {
            "kind": "cert",
            "status": "actual",
            "value": 95,
            "metadata": {"component": "Core", "grade": "GOLD"}
        },
        {
            "kind": "cert",
            "status": "actual",
            "value": 85,  # ❌ lower than GOLD
            "metadata": {"component": "Core", "grade": "PLATINUM"}
        }
    ]

    valid, errors = check_certification_chain(manifests)
    assert not valid
    assert len(errors) > 0

def test_authenticity_rate_calculation():
    """Test authenticity rate calculation."""
    results = [
        {"valid": True},
        {"valid": True},
        {"valid": False},
        {"valid": True}
    ]

    rate = compute_authenticity_rate(results)
    assert rate == 0.75

def test_authenticity_rate_perfect():
    """Test 100% authenticity rate."""
    results = [
        {"valid": True},
        {"valid": True},
        {"valid": True}
    ]

    rate = compute_authenticity_rate(results)
    assert rate == 1.0

def test_worm_signature_missing(schema, temp_manifest):
    """Test that missing WORM signature fails."""
    manifest_data = {
        "id": str(uuid.uuid4()),
        "kind": "cert",
        "scale": {"max": 100, "min": 0},
        "value": 100,
        "status": "actual",
        "source": {
            "file": "test.md",
            "hash": "a" * 128
        },
        "ci": {
            "commit": "abc123",
            "timestamp": datetime.now().isoformat() + "Z"
        },
        "worm": {
            "uuid": str(uuid.uuid4()),
            "signature": "",  # ❌ empty
            "chain_prev": None
        }
    }

    manifest_file = temp_manifest(manifest_data)
    valid, errors = validate_manifest(manifest_file, schema)

    assert not valid
    assert any("WORM signature" in e for e in errors)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
