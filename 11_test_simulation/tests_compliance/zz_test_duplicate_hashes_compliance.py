"""
Tests for Duplicate Identity Hash Detection

Module: 23_compliance/anti_gaming/detect_duplicate_identity_hashes.py
Target Coverage: 30% → 100%
Priority: HIGH (gaming detection critical)
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

from anti_gaming.detect_duplicate_identity_hashes import (
    detect_duplicate_identity_hashes,
    analyze_hash_dataset,
    generate_evidence_report
)

# ============================================================================
# Basic Detection Tests
# ============================================================================

def test_detect_duplicate_identity_hashes_no_duplicates(sample_identity_hashes_clean):
    """Test detection with clean dataset (no duplicates)"""
    duplicates = detect_duplicate_identity_hashes(sample_identity_hashes_clean)

    assert duplicates == [], "Clean dataset should have no duplicates"

def test_detect_duplicate_identity_hashes_with_duplicates(sample_identity_hashes_duplicates):
    """Test detection with duplicates present"""
    duplicates = detect_duplicate_identity_hashes(sample_identity_hashes_duplicates)

    # Should detect duplicates
    assert len(duplicates) > 0, "Should detect duplicates in dataset"

    # From sample: "abc123", "def456", "ghi789" are duplicated
    assert "abc123" in duplicates
    assert "def456" in duplicates
    assert "ghi789" in duplicates

def test_detect_duplicate_identity_hashes_preserves_order():
    """Test that duplicates are returned in first-seen order"""
    hashes = [
        "hash_a",
        "hash_b",
        "hash_a",  # Duplicate of hash_a (should be in result)
        "hash_c",
        "hash_b",  # Duplicate of hash_b (should be in result)
        "hash_d",
        "hash_c"   # Duplicate of hash_c (should be in result)
    ]

    duplicates = detect_duplicate_identity_hashes(hashes)

    # Should have 3 duplicates in order: hash_a, hash_b, hash_c
    assert len(duplicates) == 3
    assert duplicates == ["hash_a", "hash_b", "hash_c"]

def test_detect_duplicate_identity_hashes_only_once_per_duplicate():
    """Test that each duplicate hash appears only once in result"""
    hashes = [
        "hash_x",
        "hash_x",  # First duplicate
        "hash_x",  # Second duplicate (should not add again)
        "hash_x"   # Third duplicate (should not add again)
    ]

    duplicates = detect_duplicate_identity_hashes(hashes)

    # Should only appear once in duplicates list
    assert duplicates == ["hash_x"]
    assert len(duplicates) == 1

# ============================================================================
# Edge Cases
# ============================================================================

def test_detect_duplicate_identity_hashes_empty_list():
    """Test with empty list"""
    duplicates = detect_duplicate_identity_hashes([])

    assert duplicates == [], "Empty list should return no duplicates"

def test_detect_duplicate_identity_hashes_single_item():
    """Test with single item (no duplicates possible)"""
    duplicates = detect_duplicate_identity_hashes(["single_hash"])

    assert duplicates == [], "Single item cannot have duplicates"

def test_detect_duplicate_identity_hashes_all_unique():
    """Test with all unique hashes"""
    hashes = [f"hash_{i}" for i in range(100)]

    duplicates = detect_duplicate_identity_hashes(hashes)

    assert duplicates == [], "All unique hashes should return no duplicates"

def test_detect_duplicate_identity_hashes_all_duplicates():
    """Test with all same hash"""
    hashes = ["same_hash"] * 50

    duplicates = detect_duplicate_identity_hashes(hashes)

    # Should detect as duplicate (appears once in result)
    assert duplicates == ["same_hash"]

# ============================================================================
# Dataset Analysis Tests
# ============================================================================

def test_analyze_hash_dataset_clean(sample_identity_hashes_clean):
    """Test analysis of clean dataset"""
    result = analyze_hash_dataset(sample_identity_hashes_clean)

    assert result["total_hashes"] == len(sample_identity_hashes_clean)
    assert result["unique_hashes"] == len(sample_identity_hashes_clean)
    assert result["duplicate_count"] == 0
    assert result["duplicate_rate"] == 0.0
    assert result["risk_level"] == "NONE"
    assert "timestamp" in result

def test_analyze_hash_dataset_with_duplicates(sample_identity_hashes_duplicates):
    """Test analysis of dataset with duplicates"""
    result = analyze_hash_dataset(sample_identity_hashes_duplicates)

    assert result["total_hashes"] == len(sample_identity_hashes_duplicates)
    assert result["unique_hashes"] < result["total_hashes"]
    assert result["duplicate_count"] > 0
    assert result["duplicate_rate"] > 0
    assert len(result["duplicate_hashes"]) == result["duplicate_count"]

def test_analyze_hash_dataset_empty():
    """Test analysis of empty dataset"""
    result = analyze_hash_dataset([])

    assert result["total_hashes"] == 0
    assert result["unique_hashes"] == 0
    assert result["duplicate_count"] == 0
    assert result["duplicate_rate"] == 0.0
    assert result["risk_level"] == "NONE"

# ============================================================================
# Risk Level Tests
# ============================================================================

def test_analyze_hash_dataset_risk_none():
    """Test risk level NONE (0% duplicates)"""
    hashes = [f"unique_{i}" for i in range(100)]

    result = analyze_hash_dataset(hashes)

    assert result["duplicate_rate"] == 0.0
    assert result["risk_level"] == "NONE"

def test_analyze_hash_dataset_risk_low():
    """Test risk level LOW (<1% duplicates)"""
    # 200 hashes with 1 duplicate = 0.5% (LOW)
    hashes = [f"hash_{i}" for i in range(199)]
    hashes.append("hash_0")  # Duplicate

    result = analyze_hash_dataset(hashes)

    assert result["duplicate_rate"] < 0.01
    assert result["risk_level"] == "LOW"

def test_analyze_hash_dataset_risk_medium():
    """Test risk level MEDIUM (1-5% duplicates)"""
    # 100 hashes with 3 duplicates = 3% (MEDIUM)
    hashes = []

    # 97 unique
    for i in range(97):
        hashes.append(f"unique_{i}")

    # 3 duplicates (add each twice)
    for i in range(3):
        hashes.append(f"duplicate_{i}")
        hashes.append(f"duplicate_{i}")

    result = analyze_hash_dataset(hashes)

    assert 0.01 <= result["duplicate_rate"] < 0.05
    assert result["risk_level"] == "MEDIUM"

def test_analyze_hash_dataset_risk_high():
    """Test risk level HIGH (≥5% duplicates)"""
    # 100 hashes with 10 duplicates = 10% (HIGH)
    hashes = []

    # 90 unique
    for i in range(90):
        hashes.append(f"unique_{i}")

    # 10 duplicates
    for i in range(10):
        hashes.append(f"duplicate_{i}")
        hashes.append(f"duplicate_{i}")

    result = analyze_hash_dataset(hashes)

    assert result["duplicate_rate"] >= 0.05
    assert result["risk_level"] == "HIGH"

# ============================================================================
# Duplicate Rate Calculation Tests
# ============================================================================

def test_analyze_hash_dataset_duplicate_rate_calculation():
    """Test accurate duplicate rate calculation"""
    # 10 hashes: 8 unique, 2 duplicates (1 hash appears 3 times)
    # Duplicate rate = 1 / 10 = 10%
    hashes = [
        "hash_a",
        "hash_b",
        "hash_c",
        "hash_d",
        "hash_e",
        "hash_f",
        "hash_g",
        "hash_a",  # Duplicate
        "hash_h",
        "hash_a"   # Duplicate again
    ]

    result = analyze_hash_dataset(hashes)

    assert result["total_hashes"] == 10
    assert result["unique_hashes"] == 8
    assert result["duplicate_count"] == 1  # Only 1 unique duplicate hash
    assert result["duplicate_rate"] == 0.1  # 1/10 = 10%

def test_analyze_hash_dataset_multiple_duplicates():
    """Test dataset with multiple different duplicated hashes"""
    hashes = [
        "hash_1", "hash_1",  # Duplicate 1
        "hash_2", "hash_2", "hash_2",  # Duplicate 2 (appears 3 times)
        "hash_3",  # Unique
        "hash_4", "hash_4",  # Duplicate 3
        "hash_5"  # Unique
    ]

    result = analyze_hash_dataset(hashes)

    assert result["total_hashes"] == 9
    assert result["duplicate_count"] == 3  # hash_1, hash_2, hash_4
    assert set(result["duplicate_hashes"]) == {"hash_1", "hash_2", "hash_4"}

# ============================================================================
# Evidence Report Generation Tests
# ============================================================================

def test_generate_evidence_report():
    """Test evidence report generation"""
    analysis = {
        "total_hashes": 100,
        "duplicate_count": 5,
        "risk_level": "LOW"
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "evidence" / "hash_analysis.json"

        generate_evidence_report(analysis, output_path)

        # File should exist
        assert output_path.exists()

        # Load and verify
        with open(output_path, "r") as f:
            saved_data = json.load(f)

        # Should have original data plus evidence_hash
        assert "evidence_hash" in saved_data
        assert saved_data["total_hashes"] == 100
        assert saved_data["duplicate_count"] == 5

        # Evidence hash should be SHA-256 (64 hex chars)
        assert len(saved_data["evidence_hash"]) == 64

def test_generate_evidence_report_creates_directories():
    """Test that evidence report creates parent directories"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Nested path that doesn't exist
        output_path = Path(tmpdir) / "deep" / "nested" / "evidence.json"

        analysis = {"test": "data"}
        generate_evidence_report(analysis, output_path)

        # All directories should be created
        assert output_path.exists()
        assert output_path.parent.exists()

def test_generate_evidence_report_hash_deterministic():
    """Test that evidence hash is deterministic"""
    analysis = {
        "total_hashes": 100,
        "duplicate_count": 5,
        "risk_level": "LOW"
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        path1 = Path(tmpdir) / "report1.json"
        path2 = Path(tmpdir) / "report2.json"

        generate_evidence_report(analysis.copy(), path1)
        generate_evidence_report(analysis.copy(), path2)

        with open(path1) as f1, open(path2) as f2:
            data1 = json.load(f1)
            data2 = json.load(f2)

        # Hashes should be identical (same input data)
        assert data1["evidence_hash"] == data2["evidence_hash"]

# ============================================================================
# Integration Tests
# ============================================================================

def test_full_duplicate_detection_workflow(sample_identity_hashes_duplicates):
    """Test complete duplicate detection workflow"""
    # Step 1: Detect duplicates
    duplicates = detect_duplicate_identity_hashes(sample_identity_hashes_duplicates)
    assert len(duplicates) > 0

    # Step 2: Analyze dataset
    analysis = analyze_hash_dataset(sample_identity_hashes_duplicates)
    assert analysis["duplicate_count"] == len(duplicates)

    # Step 3: Generate evidence
    with tempfile.TemporaryDirectory() as tmpdir:
        evidence_path = Path(tmpdir) / "evidence.json"
        generate_evidence_report(analysis, evidence_path)

        assert evidence_path.exists()

        # Verify evidence
        with open(evidence_path) as f:
            evidence = json.load(f)

        assert "evidence_hash" in evidence
        assert evidence["total_hashes"] == len(sample_identity_hashes_duplicates)

def test_realistic_gaming_attack_scenario():
    """Test realistic identity hash gaming attack scenario"""
    # Attacker creates 1000 identities, reuses 50 hashes
    hashes = []

    # 950 legitimate unique hashes
    for i in range(950):
        hashes.append(f"legitimate_hash_{i}")

    # 50 gaming attempts (reuse 10 hashes, 5 times each)
    for i in range(10):
        for _ in range(5):
            hashes.append(f"gaming_hash_{i}")

    # Analyze
    result = analyze_hash_dataset(hashes)

    assert result["total_hashes"] == 1000
    assert result["duplicate_count"] == 10  # 10 unique gaming hashes
    assert result["duplicate_rate"] == 0.01  # 10/1000 = 1%
    assert result["risk_level"] == "MEDIUM"  # 1% is in MEDIUM range

def test_mass_reuse_attack():
    """Test mass identity hash reuse attack"""
    # Extreme attack: same hash used 1000 times
    hashes = ["attacker_hash"] * 1000

    result = analyze_hash_dataset(hashes)

    assert result["total_hashes"] == 1000
    assert result["unique_hashes"] == 1
    assert result["duplicate_count"] == 1
    assert result["duplicate_rate"] == 0.001  # 1/1000
    assert result["risk_level"] == "LOW"  # Rate is low, but this is still suspicious

# ============================================================================
# Real-World Scenario Tests
# ============================================================================

def test_normal_production_dataset():
    """Test analysis of normal production dataset"""
    # Realistic: 10,000 users, no gaming
    hashes = [f"user_hash_{i}" for i in range(10000)]

    result = analyze_hash_dataset(hashes)

    assert result["total_hashes"] == 10000
    assert result["unique_hashes"] == 10000
    assert result["duplicate_count"] == 0
    assert result["risk_level"] == "NONE"

def test_dataset_with_legitimate_collisions():
    """Test dataset with rare legitimate hash collisions"""
    # 10,000 hashes with 5 legitimate collisions (0.05%)
    hashes = [f"hash_{i}" for i in range(9995)]

    # 5 legitimate collisions (extremely rare)
    for i in range(5):
        hashes.append(f"hash_{i}")  # Duplicate first 5 hashes

    result = analyze_hash_dataset(hashes)

    assert result["duplicate_rate"] == 0.0005  # 5/10000 = 0.05%
    assert result["risk_level"] == "LOW"

# ============================================================================
# Performance Tests
# ============================================================================

@pytest.mark.skip(reason="Performance test - run manually")
def test_duplicate_detection_performance():
    """Test detection performance with large dataset"""
    import time

    # Generate 100,000 hashes with 1% duplicates
    hashes = []
    for i in range(99000):
        hashes.append(f"hash_{i}")

    # Add 1000 duplicates
    for i in range(1000):
        hashes.append(f"hash_{i % 100}")  # Reuse first 100 hashes

    start = time.time()
    result = analyze_hash_dataset(hashes)
    elapsed = time.time() - start

    # Should process 100K hashes in <1 second
    assert elapsed < 1.0, f"Detection too slow: {elapsed}s for 100K hashes"
    assert result["total_hashes"] == 100000
