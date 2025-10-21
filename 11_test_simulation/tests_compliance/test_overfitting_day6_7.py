"""
Day 6-7: Overfitting Detector Comprehensive Tests
Sprint 2 Anti-Gaming Coverage

Tests:
- overfitting_detector.py (35 comprehensive tests)
  - is_overfitting() function (15 tests)
  - analyze_model_metrics() function (10 tests)
  - batch_analyze_models() function (7 tests)
  - generate_evidence_report() function (3 tests)

Total: 35 comprehensive tests
"""

import pytest
import sys
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone

# Add modules to path
repo_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(repo_root / "23_compliance" / "anti_gaming"))

from overfitting_detector import (
    is_overfitting,
    analyze_model_metrics,
    batch_analyze_models,
    generate_evidence_report
)

# ============================================================================
# PART 1: is_overfitting() Tests (15 tests)
# ============================================================================

def test_is_overfitting_clear_case():
    """Test obvious overfitting case"""
    assert is_overfitting(0.99, 0.75, gap_threshold=0.15) is True

def test_is_overfitting_no_overfitting_small_gap():
    """Test when gap is below threshold"""
    assert is_overfitting(0.98, 0.90, gap_threshold=0.15) is False

def test_is_overfitting_low_train_accuracy():
    """Test when training accuracy is too low"""
    assert is_overfitting(0.80, 0.50, gap_threshold=0.15, min_train=0.95) is False

def test_is_overfitting_exact_threshold():
    """Test exact threshold boundary"""
    assert is_overfitting(0.95, 0.79, gap_threshold=0.15, min_train=0.95) is True

def test_is_overfitting_just_below_threshold():
    """Test just below gap threshold"""
    assert is_overfitting(0.95, 0.801, gap_threshold=0.15, min_train=0.95) is False

def test_is_overfitting_none_train_accuracy():
    """Test with None training accuracy"""
    assert is_overfitting(None, 0.80) is False

def test_is_overfitting_none_val_accuracy():
    """Test with None validation accuracy"""
    assert is_overfitting(0.95, None) is False

def test_is_overfitting_both_none():
    """Test with both accuracies as None"""
    assert is_overfitting(None, None) is False

def test_is_overfitting_perfect_training():
    """Test with perfect training accuracy"""
    assert is_overfitting(1.0, 0.80, gap_threshold=0.15) is True

def test_is_overfitting_perfect_both():
    """Test with perfect training and validation"""
    assert is_overfitting(1.0, 1.0, gap_threshold=0.15) is False

def test_is_overfitting_validation_higher():
    """Test validation > training (shouldn't flag)"""
    assert is_overfitting(0.90, 0.95, gap_threshold=0.15) is False

def test_is_overfitting_custom_min_train():
    """Test with custom min_train threshold"""
    assert is_overfitting(0.90, 0.70, gap_threshold=0.15, min_train=0.92) is False

def test_is_overfitting_realistic_scenario():
    """Test realistic ML overfitting scenario"""
    train_acc = 0.98
    val_acc = 0.72
    assert is_overfitting(train_acc, val_acc, gap_threshold=0.20, min_train=0.95) is True

def test_is_overfitting_realistic_good_model():
    """Test realistic well-generalized model"""
    train_acc = 0.94
    val_acc = 0.91
    assert is_overfitting(train_acc, val_acc, gap_threshold=0.15, min_train=0.95) is False

def test_is_overfitting_default_parameters():
    """Test using default parameter values"""
    assert is_overfitting(0.98, 0.80) is True
    assert is_overfitting(0.94, 0.92) is False

# ============================================================================
# PART 2: analyze_model_metrics() Tests (10 tests)
# ============================================================================

def test_analyze_model_metrics_no_overfitting():
    """Test analysis of well-generalized model"""
    result = analyze_model_metrics(
        model_id="test_model_1",
        train_acc=0.94,
        val_acc=0.91,
        test_acc=0.90
    )

    assert result["model_id"] == "test_model_1"
    assert result["overfitting_detected"] is False
    assert result["risk_level"] == "NONE"
    assert result["accuracy_gap"] == round(0.94 - 0.91, 4)
    assert "timestamp" in result

def test_analyze_model_metrics_medium_risk():
    """Test analysis with medium risk overfitting"""
    result = analyze_model_metrics(
        model_id="test_model_2",
        train_acc=0.97,
        val_acc=0.80,  # Gap = 0.17
        test_acc=0.79
    )

    assert result["overfitting_detected"] is True
    assert result["risk_level"] == "MEDIUM"
    assert result["accuracy_gap"] == round(0.97 - 0.80, 4)

def test_analyze_model_metrics_high_risk():
    """Test analysis with high risk overfitting"""
    result = analyze_model_metrics(
        model_id="test_model_3",
        train_acc=0.98,
        val_acc=0.75,  # Gap = 0.23
        test_acc=0.74
    )

    assert result["overfitting_detected"] is True
    assert result["risk_level"] == "HIGH"

def test_analyze_model_metrics_critical_risk():
    """Test analysis with critical risk overfitting"""
    result = analyze_model_metrics(
        model_id="test_model_4",
        train_acc=0.99,
        val_acc=0.65,  # Gap = 0.34
        test_acc=0.63
    )

    assert result["overfitting_detected"] is True
    assert result["risk_level"] == "CRITICAL"

def test_analyze_model_metrics_warning_high_train():
    """Test warning for suspiciously high training accuracy"""
    result = analyze_model_metrics(
        model_id="test_model_5",
        train_acc=0.995,  # >= 0.99
        val_acc=0.80,
        test_acc=0.79
    )

    assert "warnings" in result
    assert any("suspiciously high" in w for w in result["warnings"])

def test_analyze_model_metrics_warning_low_val():
    """Test warning for critically low validation accuracy"""
    result = analyze_model_metrics(
        model_id="test_model_6",
        train_acc=0.96,
        val_acc=0.45,  # < 0.50
        test_acc=0.47
    )

    assert "warnings" in result
    assert any("critically low" in w for w in result["warnings"])

def test_analyze_model_metrics_warning_test_val_mismatch():
    """Test warning for test/validation mismatch"""
    result = analyze_model_metrics(
        model_id="test_model_7",
        train_acc=0.95,
        val_acc=0.85,
        test_acc=0.70  # Gap with val = 0.15
    )

    assert "warnings" in result
    assert any("mismatch" in w for w in result["warnings"])

def test_analyze_model_metrics_no_test_accuracy():
    """Test analysis without test accuracy"""
    result = analyze_model_metrics(
        model_id="test_model_8",
        train_acc=0.95,
        val_acc=0.92,
        test_acc=None
    )

    assert result["test_accuracy"] is None
    assert result["overfitting_detected"] is False

def test_analyze_model_metrics_threshold_config():
    """Test threshold configuration in output"""
    result = analyze_model_metrics(
        model_id="test_model_9",
        train_acc=0.96,
        val_acc=0.90,
        gap_threshold=0.10,
        min_train=0.92
    )

    assert result["threshold_config"]["gap_threshold"] == 0.10
    assert result["threshold_config"]["min_train"] == 0.92

def test_analyze_model_metrics_multiple_warnings():
    """Test model triggering multiple warnings"""
    result = analyze_model_metrics(
        model_id="test_model_10",
        train_acc=0.995,  # High train warning
        val_acc=0.45,     # Low val warning
        test_acc=0.60     # Test/val mismatch
    )

    assert "warnings" in result
    assert len(result["warnings"]) >= 2

# ============================================================================
# PART 3: batch_analyze_models() Tests (7 tests)
# ============================================================================

def test_batch_analyze_empty_list():
    """Test batch analysis with empty list"""
    result = batch_analyze_models([])

    assert result["total_models"] == 0
    assert result["overfitting_count"] == 0
    assert result["high_risk_count"] == 0
    assert result["overfitting_rate"] == 0.0
    assert result["results"] == []

def test_batch_analyze_single_model():
    """Test batch analysis with single model"""
    models = [
        {
            "model_id": "single_model",
            "train_acc": 0.95,
            "val_acc": 0.92,
            "test_acc": 0.91
        }
    ]

    result = batch_analyze_models(models)

    assert result["total_models"] == 1
    assert result["overfitting_count"] == 0
    assert result["overfitting_rate"] == 0.0
    assert len(result["results"]) == 1

def test_batch_analyze_all_overfitting():
    """Test batch analysis with all models overfitting"""
    models = [
        {"model_id": "model_1", "train_acc": 0.98, "val_acc": 0.75, "test_acc": 0.74},
        {"model_id": "model_2", "train_acc": 0.99, "val_acc": 0.70, "test_acc": 0.69},
        {"model_id": "model_3", "train_acc": 0.97, "val_acc": 0.78, "test_acc": 0.77}
    ]

    result = batch_analyze_models(models)

    assert result["total_models"] == 3
    assert result["overfitting_count"] == 3
    assert result["overfitting_rate"] == 1.0

def test_batch_analyze_mixed_models():
    """Test batch analysis with mixed overfitting/non-overfitting"""
    models = [
        {"model_id": "good_model", "train_acc": 0.94, "val_acc": 0.91, "test_acc": 0.90},
        {"model_id": "overfit_model", "train_acc": 0.98, "val_acc": 0.75, "test_acc": 0.74},
        {"model_id": "another_good", "train_acc": 0.92, "val_acc": 0.89, "test_acc": 0.88}
    ]

    result = batch_analyze_models(models)

    assert result["total_models"] == 3
    assert result["overfitting_count"] == 1
    assert result["overfitting_rate"] == round(1 / 3, 4)

def test_batch_analyze_high_risk_count():
    """Test high risk count calculation"""
    models = [
        {"model_id": "model_1", "train_acc": 0.98, "val_acc": 0.70, "test_acc": 0.69},  # HIGH
        {"model_id": "model_2", "train_acc": 0.99, "val_acc": 0.60, "test_acc": 0.59},  # CRITICAL
        {"model_id": "model_3", "train_acc": 0.97, "val_acc": 0.80, "test_acc": 0.79}   # MEDIUM
    ]

    result = batch_analyze_models(models)

    assert result["overfitting_count"] == 3
    assert result["high_risk_count"] == 2  # HIGH + CRITICAL

def test_batch_analyze_missing_model_id():
    """Test batch analysis with missing model_id"""
    models = [
        {"train_acc": 0.95, "val_acc": 0.92, "test_acc": 0.91}
    ]

    result = batch_analyze_models(models)

    assert result["results"][0]["model_id"] == "unknown"

def test_batch_analyze_timestamp():
    """Test that batch analysis includes timestamp"""
    models = [
        {"model_id": "test", "train_acc": 0.95, "val_acc": 0.92}
    ]

    result = batch_analyze_models(models)

    assert "timestamp" in result
    # Validate ISO format
    datetime.fromisoformat(result["timestamp"].replace('Z', '+00:00'))

# ============================================================================
# PART 4: generate_evidence_report() Tests (3 tests)
# ============================================================================

def test_generate_evidence_report_creates_file(tmp_path):
    """Test evidence report file creation"""
    analysis = {
        "model_id": "test_model",
        "train_accuracy": 0.95,
        "val_accuracy": 0.92,
        "overfitting_detected": False,
        "risk_level": "NONE"
    }

    output_path = tmp_path / "evidence" / "overfitting_evidence.json"
    generate_evidence_report(analysis, output_path)

    assert output_path.exists()

def test_generate_evidence_report_adds_hash(tmp_path):
    """Test that evidence hash is added"""
    analysis = {
        "model_id": "test_model",
        "train_accuracy": 0.95,
        "val_accuracy": 0.92,
        "overfitting_detected": False
    }

    output_path = tmp_path / "evidence.json"
    generate_evidence_report(analysis, output_path)

    with open(output_path) as f:
        loaded = json.load(f)

    assert "evidence_hash" in loaded
    assert len(loaded["evidence_hash"]) == 64  # SHA-256 hex length

def test_generate_evidence_report_hash_consistency(tmp_path):
    """Test that evidence hash is deterministic"""
    analysis = {
        "model_id": "test_model",
        "train_accuracy": 0.95,
        "val_accuracy": 0.92,
        "overfitting_detected": False,
        "risk_level": "NONE"
    }

    file1 = tmp_path / "evidence1.json"
    file2 = tmp_path / "evidence2.json"

    generate_evidence_report(analysis.copy(), file1)
    generate_evidence_report(analysis.copy(), file2)

    with open(file1) as f:
        data1 = json.load(f)
    with open(file2) as f:
        data2 = json.load(f)

    assert data1["evidence_hash"] == data2["evidence_hash"]
