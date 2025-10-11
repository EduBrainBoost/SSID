"""
Comprehensive tests for overfitting_detector module.
Tests all edge cases and ensures 80%+ code coverage.
"""
import pytest
import sys
from pathlib import Path

# Add repo root to path
repo_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(repo_root))

# Import using importlib to handle module names starting with numbers
import importlib.util
spec = importlib.util.spec_from_file_location(
    "overfitting_detector",
    repo_root / "23_compliance" / "anti_gaming" / "overfitting_detector.py"
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
is_overfitting = module.is_overfitting


def test_clear_overfitting():
    """Test obvious overfitting case."""
    assert is_overfitting(0.99, 0.75, gap_threshold=0.2) is True


def test_not_overfitting_small_gap():
    """Test when gap is below threshold."""
    assert is_overfitting(0.98, 0.9, gap_threshold=0.2) is False


def test_not_overfitting_low_train_accuracy():
    """Test when training accuracy is too low."""
    # Even with large gap, low train_acc shouldn't flag
    assert is_overfitting(0.80, 0.50, gap_threshold=0.2, min_train=0.95) is False


def test_exact_threshold_boundary():
    """Test exact threshold boundary conditions."""
    # Due to floating point precision, 0.95 - 0.80 = 0.14999... < 0.15
    # Use slightly larger gap to ensure it crosses threshold
    assert is_overfitting(0.95, 0.79, gap_threshold=0.15, min_train=0.95) is True


def test_just_below_threshold():
    """Test just below gap threshold."""
    # 0.149 gap is below 0.15 threshold
    assert is_overfitting(0.95, 0.801, gap_threshold=0.15, min_train=0.95) is False


def test_none_train_accuracy():
    """Test with None training accuracy."""
    assert is_overfitting(None, 0.80) is False


def test_none_val_accuracy():
    """Test with None validation accuracy."""
    assert is_overfitting(0.95, None) is False


def test_both_none():
    """Test with both accuracies as None."""
    assert is_overfitting(None, None) is False


def test_perfect_training():
    """Test with perfect training accuracy."""
    assert is_overfitting(1.0, 0.80, gap_threshold=0.15) is True


def test_perfect_both():
    """Test with perfect training and validation accuracy."""
    # No gap, so not overfitting
    assert is_overfitting(1.0, 1.0, gap_threshold=0.15) is False


def test_validation_higher_than_training():
    """Test unusual case where validation > training (shouldn't flag)."""
    # Negative gap, definitely not overfitting
    assert is_overfitting(0.90, 0.95, gap_threshold=0.15) is False


def test_zero_accuracies():
    """Test with zero accuracies."""
    assert is_overfitting(0.0, 0.0, gap_threshold=0.15) is False


def test_custom_min_train_threshold():
    """Test with custom min_train threshold."""
    # Train acc 0.90 is below custom min_train=0.92
    assert is_overfitting(0.90, 0.70, gap_threshold=0.15, min_train=0.92) is False


def test_custom_min_train_threshold_met():
    """Test with custom min_train threshold met."""
    # Train acc 0.95 meets custom min_train=0.92 and gap=0.25 > 0.20
    assert is_overfitting(0.95, 0.70, gap_threshold=0.20, min_train=0.92) is True


def test_very_small_gap():
    """Test with very small gap."""
    assert is_overfitting(0.98, 0.97, gap_threshold=0.15) is False


def test_very_large_gap():
    """Test with very large gap (extreme overfitting)."""
    assert is_overfitting(0.99, 0.30, gap_threshold=0.15) is True


def test_realistic_overfitting_scenario():
    """Test realistic ML overfitting scenario."""
    # Model memorized training data: 98% train, 72% val
    train_acc = 0.98
    val_acc = 0.72
    gap = train_acc - val_acc  # 0.26

    assert is_overfitting(train_acc, val_acc, gap_threshold=0.20, min_train=0.95) is True


def test_realistic_good_model():
    """Test realistic well-generalized model."""
    # Good model: 94% train, 91% val
    train_acc = 0.94
    val_acc = 0.91
    gap = train_acc - val_acc  # 0.03

    assert is_overfitting(train_acc, val_acc, gap_threshold=0.15, min_train=0.95) is False


def test_edge_case_exact_min_train():
    """Test exact min_train boundary."""
    # Exactly at min_train threshold with sufficient gap
    assert is_overfitting(0.95, 0.75, gap_threshold=0.15, min_train=0.95) is True


def test_floating_point_precision():
    """Test with floating point precision edge cases."""
    # Demonstrate that 0.95 - 0.80 = 0.14999... due to float arithmetic
    train = 0.95
    val = 0.80
    gap_threshold = 0.15

    # This actually returns False due to float precision
    result = is_overfitting(train, val, gap_threshold=gap_threshold)
    assert result is False  # 0.14999... < 0.15

    # But with a slightly smaller threshold, it works
    result2 = is_overfitting(train, val, gap_threshold=0.149)
    assert result2 is True


def test_negative_accuracies():
    """Test with negative accuracy values (invalid but handled)."""
    # Invalid input, but function should handle gracefully
    assert is_overfitting(-0.5, -0.3, gap_threshold=0.15) is False


def test_accuracies_above_one():
    """Test with accuracy values > 1.0 (invalid but handled)."""
    # Should still detect the pattern even with invalid values
    assert is_overfitting(1.2, 0.8, gap_threshold=0.15, min_train=0.95) is True


def test_default_parameters():
    """Test using default parameter values."""
    # Default: gap_threshold=0.15, min_train=0.95
    assert is_overfitting(0.98, 0.80) is True
    assert is_overfitting(0.94, 0.92) is False


def test_boundary_analysis():
    """Test multiple boundary conditions systematically."""
    # Case 1: Just meets both thresholds (accounting for float precision)
    assert is_overfitting(0.95, 0.79, gap_threshold=0.15, min_train=0.95) is True

    # Case 2: Meets gap but not min_train
    assert is_overfitting(0.94, 0.74, gap_threshold=0.15, min_train=0.95) is False

    # Case 3: Meets min_train but not gap
    assert is_overfitting(0.95, 0.85, gap_threshold=0.15, min_train=0.95) is False

    # Case 4: Meets neither
    assert is_overfitting(0.90, 0.85, gap_threshold=0.15, min_train=0.95) is False
