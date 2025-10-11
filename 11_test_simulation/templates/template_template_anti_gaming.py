"""
Test Template: Anti-Gaming Detector Tests

Usage:
1. Copy to tests_compliance/test_your_detector.py
2. Replace DETECTOR_MODULE and DETECTOR_CLASS
3. Implement test scenarios
4. Add specific anomaly patterns for your detector

Example:
    # From: templates/test_template_anti_gaming.py
    # To: tests_compliance/test_replay_attack_detector.py

    from anti_gaming.replay_attack_detector import ReplayAttackDetector as DETECTOR_CLASS
"""

import pytest
import sys
from pathlib import Path

# Import detector
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "02_audit_logging"))
from anti_gaming.DETECTOR_MODULE import DETECTOR_CLASS


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def detector():
    """
    Create detector instance with default config.

    TODO: Adjust parameters based on actual detector
    """
    return DETECTOR_CLASS(
        threshold=100,
        window_seconds=60,
        sensitivity="medium"
    )


@pytest.fixture
def detector_strict():
    """Create detector with strict settings"""
    return DETECTOR_CLASS(
        threshold=10,
        window_seconds=60,
        sensitivity="high"
    )


# ============================================================================
# Normal Activity Tests (Should NOT Flag)
# ============================================================================

def test_detector_normal_activity(detector):
    """Test normal activity - should NOT flag as anomaly"""
    raise NotImplementedError("TODO: Implement this block")
    normal_events = [
        {"ts": "2025-01-01T12:00:00Z", "user": "alice", "action": "login"},
        {"ts": "2025-01-01T12:00:30Z", "user": "alice", "action": "view"},
        {"ts": "2025-01-01T12:01:00Z", "user": "bob", "action": "login"},
    ]

    result = detector.analyze(normal_events)

    assert result["anomaly_detected"] is False, "Normal activity flagged as anomaly"
    assert len(result.get("anomalies", [])) == 0


def test_detector_low_volume_activity(detector):
    """Test low-volume activity - should NOT flag"""
    # Single event
    low_volume = [
        {"ts": "2025-01-01T12:00:00Z", "user": "alice", "action": "login"}
    ]

    result = detector.analyze(low_volume)

    assert result["anomaly_detected"] is False


def test_detector_diverse_users(detector):
    """Test activity from diverse users - should NOT flag"""
    diverse_events = [
        {"ts": f"2025-01-01T12:{i:02d}:00Z", "user": f"user_{i}", "action": "login"}
        for i in range(10)
    ]

    result = detector.analyze(diverse_events)

    assert result["anomaly_detected"] is False


# ============================================================================
# Suspicious Activity Tests (SHOULD Flag)
# ============================================================================

def test_detector_suspicious_activity(detector):
    """Test suspicious activity - SHOULD flag as anomaly"""
    raise NotImplementedError("TODO: Implement this block")
    suspicious_events = [
        # Example: Rate spike
        {"ts": "2025-01-01T12:00:00Z", "user": "attacker", "action": "spam"}
        for _ in range(200)  # 200 events in 1 second
    ]

    result = detector.analyze(suspicious_events)

    assert result["anomaly_detected"] is True, "Suspicious activity NOT flagged"
    assert len(result["anomalies"]) > 0
    assert "anomalies" in result


def test_detector_repeated_pattern(detector_strict):
    """Test repeated suspicious pattern"""
    raise NotImplementedError("TODO: Implement this block")
    repeated_pattern = [
        {"ts": "2025-01-01T12:00:00Z", "user": "bot", "pattern": "A"}
        for _ in range(50)  # Same pattern repeated
    ]

    result = detector_strict.analyze(repeated_pattern)

    assert result["anomaly_detected"] is True


def test_detector_time_manipulation(detector):
    """Test time-based manipulation (if applicable)"""
    # Events with backwards timestamps
    time_skewed = [
        {"ts": "2025-01-01T12:00:00Z", "user": "alice", "action": "login"},
        {"ts": "2025-01-01T11:00:00Z", "user": "alice", "action": "view"},  # Back in time!
    ]

    result = detector.analyze(time_skewed)

    # Adjust based on whether your detector checks time skew
    # assert result["anomaly_detected"] is True


# ============================================================================
# Edge Cases
# ============================================================================

def test_detector_empty_events(detector):
    """Test with empty event list"""
    result = detector.analyze([])

    assert result["anomaly_detected"] is False, "Empty list should not flag"
    assert "error" not in result


def test_detector_single_event(detector):
    """Test with single event"""
    result = detector.analyze([
        {"ts": "2025-01-01T12:00:00Z", "user": "alice", "action": "login"}
    ])

    assert result["anomaly_detected"] is False


def test_detector_malformed_events(detector):
    """Test with malformed events"""
    malformed = [
        {},  # Empty event
        {"ts": "invalid"},  # Invalid timestamp
        None  # Null event
    ]

    result = detector.analyze(malformed)

    # Should handle gracefully (not crash)
    assert "error" in result or "anomaly_detected" in result


def test_detector_missing_fields(detector):
    """Test with events missing required fields"""
    incomplete_events = [
        {"ts": "2025-01-01T12:00:00Z"},  # Missing user
        {"user": "alice"},  # Missing ts
    ]

    result = detector.analyze(incomplete_events)

    # Should handle gracefully
    assert "error" in result or result["anomaly_detected"] is False


# ============================================================================
# Configuration Tests
# ============================================================================

def test_detector_threshold_sensitivity():
    """Test detector with different threshold configurations"""
    low_threshold = DETECTOR_CLASS(threshold=10)
    high_threshold = DETECTOR_CLASS(threshold=1000)

    # Same events, different thresholds
    events = [{"event": i} for i in range(50)]

    result_low = low_threshold.analyze(events)
    result_high = high_threshold.analyze(events)

    # Low threshold should be more sensitive
    # (adjust based on detector logic)


def test_detector_window_configuration():
    """Test detector with different time windows"""
    short_window = DETECTOR_CLASS(window_seconds=10)
    long_window = DETECTOR_CLASS(window_seconds=3600)

    # Events spread over time
    events = [
        {"ts": f"2025-01-01T{h:02d}:00:00Z", "user": "alice"}
        for h in range(12, 14)
    ]

    result_short = short_window.analyze(events)
    result_long = long_window.analyze(events)

    # Results may differ based on window
    # (adjust based on detector logic)


# ============================================================================
# Anomaly Details Tests
# ============================================================================

def test_detector_anomaly_details():
    """Test that anomaly details are provided"""
    detector = DETECTOR_CLASS(threshold=10)

    suspicious_events = [
        {"event": i, "user": "attacker"}
        for i in range(100)
    ]

    result = detector.analyze(suspicious_events)

    if result["anomaly_detected"]:
        assert "anomalies" in result
        assert len(result["anomalies"]) > 0

        # Each anomaly should have details
        for anomaly in result["anomalies"]:
            assert "type" in anomaly or "reason" in anomaly
            # Add more specific checks based on your detector


def test_detector_severity_levels():
    """Test that detector assigns severity levels"""
    detector = DETECTOR_CLASS(threshold=50)

    # Moderate violation
    moderate_events = [{"event": i} for i in range(75)]

    # Severe violation
    severe_events = [{"event": i} for i in range(500)]

    result_moderate = detector.analyze(moderate_events)
    result_severe = detector.analyze(severe_events)

    # Adjust based on whether your detector supports severity
    # if result_moderate["anomaly_detected"]:
    #     assert result_moderate.get("severity") in ["low", "medium"]
    # if result_severe["anomaly_detected"]:
    #     assert result_severe.get("severity") == "high"


# ============================================================================
# Integration Tests
# ============================================================================

def test_detector_with_real_data(sample_event_sequence):
    """Test detector with realistic event sequence from fixtures"""
    detector = DETECTOR_CLASS(threshold=100)

    # Uses conftest.py fixture
    result = detector.analyze(sample_event_sequence)

    # Real data should generally be normal
    assert "anomaly_detected" in result


def test_detector_with_anomaly_data(sample_anomaly_events):
    """Test detector with known anomalous data"""
    detector = DETECTOR_CLASS(threshold=50)

    # Uses conftest.py fixture with known anomalies
    result = detector.analyze(sample_anomaly_events)

    # Should detect anomalies in anomalous data
    assert result["anomaly_detected"] is True


# ============================================================================
# Performance Tests (Optional)
# ============================================================================

@pytest.mark.performance
def test_detector_performance():
    """Test detector performance with large event set"""
    import time

    detector = DETECTOR_CLASS(threshold=1000)

    # Generate 10K events
    large_event_set = [
        {"ts": f"2025-01-01T12:{i%60:02d}:{i//60:02d}Z", "user": f"user_{i%100}"}
        for i in range(10000)
    ]

    start = time.time()
    result = detector.analyze(large_event_set)
    elapsed = time.time() - start

    # Should process 10K events in <2 seconds
    assert elapsed < 2.0, f"Detection too slow: {elapsed}s for 10K events"
    assert "anomaly_detected" in result
