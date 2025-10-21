"""
Tests for Badge Signature Validator

Module: 23_compliance/anti_gaming/badge_signature_validator.py
Target Coverage: 31% → 100%
Priority: HIGH (fraud detection critical)
"""

# CRITICAL: Set sys.path BEFORE imports (pytest collection happens before conftest)
import sys
from pathlib import Path
_repo_root = Path(__file__).parent.parent.parent
if str(_repo_root / "23_compliance") not in sys.path:
    sys.path.insert(0, str(_repo_root / "23_compliance"))

# Now safe to import
import pytest
import hashlib
import tempfile
import json

from anti_gaming.badge_signature_validator import (
    verify_badges,
    analyze_badge_batch,
    generate_evidence_report,
    _sha256_text
)

# ============================================================================
# Basic Functionality Tests
# ============================================================================

def test_verify_badges_all_valid(sample_valid_badges):
    """Test verification of all valid badges"""
    invalid = verify_badges(sample_valid_badges)

    assert len(invalid) == 0, "All valid badges should pass verification"

def test_verify_badges_all_invalid(sample_invalid_badges):
    """Test verification detects all invalid badges"""
    invalid = verify_badges(sample_invalid_badges)

    assert len(invalid) == len(sample_invalid_badges), \
        "All invalid badges should be detected"

    # Each invalid badge should have error details
    for inv in invalid:
        assert "id" in inv
        assert "error" in inv

def test_verify_badges_mixed(sample_mixed_badges):
    """Test verification with mix of valid and invalid badges"""
    invalid = verify_badges(sample_mixed_badges)

    # Should detect exactly 3 invalid badges (from sample_invalid_badges)
    assert len(invalid) == 3, f"Expected 3 invalid badges, got {len(invalid)}"

# ============================================================================
# Signature Verification Tests
# ============================================================================

def test_verify_badges_signature_mismatch():
    """Test detection of signature mismatch"""
    badges = [
        {
            "id": "test-001",
            "payload": "correct_payload",
            "sig": _sha256_text("WRONG_payload")  # Wrong hash!
        }
    ]

    invalid = verify_badges(badges)

    assert len(invalid) == 1
    assert invalid[0]["error"] == "invalid-signature"
    assert "expected" in invalid[0]
    assert "actual" in invalid[0]

def test_verify_badges_empty_signature():
    """Test detection of empty signature"""
    badges = [
        {
            "id": "test-002",
            "payload": "some_data",
            "sig": ""  # Empty!
        }
    ]

    invalid = verify_badges(badges)

    assert len(invalid) == 1
    assert invalid[0]["error"] == "invalid-signature"

def test_verify_badges_tampered_payload():
    """Test detection of tampered payload (signature doesn't match)"""
    original_payload = "user:alice,merit:verified"
    tampered_payload = "user:alice,merit:ADMIN"  # Tampered!

    badges = [
        {
            "id": "test-003",
            "payload": tampered_payload,
            "sig": _sha256_text(original_payload)  # Signature for original
        }
    ]

    invalid = verify_badges(badges)

    assert len(invalid) == 1, "Tampered payload should be detected"

# ============================================================================
# Edge Cases
# ============================================================================

def test_verify_badges_empty_list():
    """Test with empty badge list"""
    invalid = verify_badges([])

    assert invalid == [], "Empty list should return no invalids"

def test_verify_badges_non_dict_record():
    """Test handling of non-dict records"""
    badges = [
        "not a dict",
        123,
        None,
        ["list", "instead"],
        {"id": "valid-001", "payload": "data", "sig": _sha256_text("data")}
    ]

    invalid = verify_badges(badges)

    # Should detect 4 non-dict records
    assert len(invalid) == 4

    # Check error types
    assert any(inv["error"] == "not-a-dict" for inv in invalid)

def test_verify_badges_missing_fields():
    """Test handling of missing required fields"""
    badges = [
        {},  # Missing all fields
        {"id": "test"},  # Missing payload and sig
        {"payload": "data"},  # Missing id and sig
        {"sig": "abc123"}  # Missing id and payload
    ]

    invalid = verify_badges(badges)

    # All should be flagged as invalid (empty payload/sig won't match)
    assert len(invalid) > 0

def test_verify_badges_partial_fields():
    """Test badges with some missing fields"""
    badges = [
        {
            "id": "test-004",
            "payload": "data"
            # Missing sig - defaults to ""
        }
    ]

    invalid = verify_badges(badges)

    # Missing sig should cause mismatch
    assert len(invalid) == 1

# ============================================================================
# Batch Analysis Tests
# ============================================================================

def test_analyze_badge_batch_all_valid(sample_valid_badges):
    """Test batch analysis of all valid badges"""
    result = analyze_badge_batch(sample_valid_badges)

    assert result["total_badges"] == len(sample_valid_badges)
    assert result["valid_badges"] == len(sample_valid_badges)
    assert result["invalid_badges"] == 0
    assert result["invalid_rate"] == 0.0
    assert result["risk_level"] == "NONE"
    assert "timestamp" in result

def test_analyze_badge_batch_all_invalid(sample_invalid_badges):
    """Test batch analysis of all invalid badges"""
    result = analyze_badge_batch(sample_invalid_badges)

    assert result["total_badges"] == len(sample_invalid_badges)
    assert result["valid_badges"] == 0
    assert result["invalid_badges"] == len(sample_invalid_badges)
    assert result["invalid_rate"] == 1.0
    assert result["risk_level"] == "HIGH"  # 100% invalid rate

def test_analyze_badge_batch_mixed(sample_mixed_badges):
    """Test batch analysis with mixed valid/invalid badges"""
    result = analyze_badge_batch(sample_mixed_badges)

    assert result["total_badges"] == len(sample_mixed_badges)
    assert result["valid_badges"] == 3  # From sample_valid_badges
    assert result["invalid_badges"] == 3  # From sample_invalid_badges
    assert 0 < result["invalid_rate"] < 1
    assert len(result["invalid_records"]) == 3

# ============================================================================
# Risk Level Tests
# ============================================================================

def test_analyze_badge_batch_risk_none(sample_valid_badges):
    """Test risk level NONE (0% invalid)"""
    result = analyze_badge_batch(sample_valid_badges)
    assert result["risk_level"] == "NONE"

def test_analyze_badge_batch_risk_low():
    """Test risk level LOW (<1% invalid)"""
    # 1 invalid out of 101 badges = 0.99% (LOW)
    def sha256(text):
        return hashlib.sha256(text.encode()).hexdigest()

    # Create 100 valid badges
    badges = []
    for i in range(100):
        payload = f"user:user_{i},merit:test"
        badges.append({
            "id": f"valid-{i}",
            "payload": payload,
            "sig": sha256(payload)
        })

    # Add 1 invalid badge
    badges.append({
        "id": "invalid-001",
        "payload": "data",
        "sig": "wrong_sig"  # 1 invalid
    })

    result = analyze_badge_batch(badges)

    assert result["invalid_rate"] < 0.01
    assert result["risk_level"] == "LOW"

def test_analyze_badge_batch_risk_medium():
    """Test risk level MEDIUM (1-5% invalid)"""
    # 3 invalid out of 100 badges = 3% (MEDIUM)
    badges = []

    def sha256(text):
        return hashlib.sha256(text.encode()).hexdigest()

    # 97 valid
    for i in range(97):
        badges.append({
            "id": f"valid-{i}",
            "payload": f"data-{i}",
            "sig": sha256(f"data-{i}")
        })

    # 3 invalid
    for i in range(3):
        badges.append({
            "id": f"invalid-{i}",
            "payload": f"data-{i}",
            "sig": "wrong"
        })

    result = analyze_badge_batch(badges)

    assert 0.01 <= result["invalid_rate"] < 0.05
    assert result["risk_level"] == "MEDIUM"

def test_analyze_badge_batch_risk_high():
    """Test risk level HIGH (≥5% invalid)"""
    # 10 invalid out of 100 = 10% (HIGH)
    badges = []

    def sha256(text):
        return hashlib.sha256(text.encode()).hexdigest()

    # 90 valid
    for i in range(90):
        badges.append({
            "id": f"valid-{i}",
            "payload": f"data-{i}",
            "sig": sha256(f"data-{i}")
        })

    # 10 invalid
    for i in range(10):
        badges.append({
            "id": f"invalid-{i}",
            "payload": f"data-{i}",
            "sig": "tampered"
        })

    result = analyze_badge_batch(badges)

    assert result["invalid_rate"] >= 0.05
    assert result["risk_level"] == "HIGH"

# ============================================================================
# Evidence Report Generation Tests
# ============================================================================

def test_generate_evidence_report(sample_valid_badges):
    """Test evidence report generation"""
    analysis = analyze_badge_batch(sample_valid_badges)

    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "evidence" / "test_report.json"

        generate_evidence_report(analysis, output_path)

        # File should exist
        assert output_path.exists()

        # Load and verify
        with open(output_path, "r") as f:
            saved_data = json.load(f)

        # Should have all analysis fields plus evidence_hash
        assert "evidence_hash" in saved_data
        assert "total_badges" in saved_data
        assert "risk_level" in saved_data

        # Evidence hash should be SHA-256 (64 hex chars)
        assert len(saved_data["evidence_hash"]) == 64

def test_generate_evidence_report_creates_dirs():
    """Test that evidence report creates parent directories"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Nested path that doesn't exist
        output_path = Path(tmpdir) / "deep" / "nested" / "path" / "report.json"

        analysis = {"test": "data"}
        generate_evidence_report(analysis, output_path)

        # All directories should be created
        assert output_path.exists()
        assert output_path.parent.exists()

# ============================================================================
# Helper Function Tests
# ============================================================================

def test_sha256_text_basic():
    """Test SHA-256 text hashing"""
    result = _sha256_text("test")

    # Should be 64 hex characters
    assert len(result) == 64
    assert all(c in "0123456789abcdef" for c in result)

def test_sha256_text_deterministic():
    """Test that SHA-256 is deterministic"""
    text = "deterministic_test"

    hash1 = _sha256_text(text)
    hash2 = _sha256_text(text)

    assert hash1 == hash2

def test_sha256_text_different_inputs():
    """Test that different inputs produce different hashes"""
    hash1 = _sha256_text("text1")
    hash2 = _sha256_text("text2")

    assert hash1 != hash2

# ============================================================================
# Integration Tests
# ============================================================================

def test_full_validation_workflow(sample_mixed_badges):
    """Test complete validation workflow"""
    # Step 1: Verify badges
    invalid = verify_badges(sample_mixed_badges)
    assert len(invalid) > 0

    # Step 2: Analyze batch
    analysis = analyze_badge_batch(sample_mixed_badges)
    assert analysis["invalid_badges"] == len(invalid)

    # Step 3: Generate evidence
    with tempfile.TemporaryDirectory() as tmpdir:
        evidence_path = Path(tmpdir) / "evidence.json"
        generate_evidence_report(analysis, evidence_path)

        assert evidence_path.exists()

        # Verify evidence is valid JSON
        with open(evidence_path) as f:
            evidence = json.load(f)

        assert "evidence_hash" in evidence
        assert evidence["total_badges"] == len(sample_mixed_badges)

def test_realistic_badge_validation_scenario():
    """Test realistic scenario with real-world badge data"""
    def sha256(text):
        return hashlib.sha256(text.encode()).hexdigest()

    # Realistic badge batch (1000 badges, 2% invalid)
    badges = []

    # 980 valid badges
    for i in range(980):
        payload = f"user:user_{i},merit:contributor,timestamp:2025-01-{i%30+1:02d}"
        badges.append({
            "id": f"badge_{i:04d}",
            "payload": payload,
            "sig": sha256(payload)
        })

    # 20 invalid badges (tampered)
    for i in range(980, 1000):
        payload = f"user:user_{i},merit:contributor"
        badges.append({
            "id": f"badge_{i:04d}",
            "payload": payload,
            "sig": sha256("TAMPERED")  # Wrong signature
        })

    # Analyze
    result = analyze_badge_batch(badges)

    assert result["total_badges"] == 1000
    assert result["invalid_badges"] == 20
    assert result["invalid_rate"] == 0.02  # 2%
    assert result["risk_level"] == "MEDIUM"  # 2% is in MEDIUM range (1-5%)

# ============================================================================
# Performance Tests (Optional)
# ============================================================================

@pytest.mark.skip(reason="Performance test - run manually")
def test_badge_validation_performance():
    """Test validation performance with large batch"""
    import time

    def sha256(text):
        return hashlib.sha256(text.encode()).hexdigest()

    # Generate 10,000 badges
    badges = []
    for i in range(10000):
        payload = f"user:user_{i},merit:test"
        badges.append({
            "id": f"badge_{i}",
            "payload": payload,
            "sig": sha256(payload)
        })

    start = time.time()
    result = analyze_badge_batch(badges)
    elapsed = time.time() - start

    # Should process 10K badges in <1 second
    assert elapsed < 1.0, f"Validation too slow: {elapsed}s for 10K badges"
    assert result["total_badges"] == 10000
