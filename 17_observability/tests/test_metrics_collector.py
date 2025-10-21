"""Tests for PII-protected metrics collector."""
import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from metrics_collector import MetricsCollector

def test_inc_and_gauge_without_pii():
    """Test basic metric operations without PII."""
    mc = MetricsCollector()

    # Test counter
    val = mc.inc("events_processed", 2, {"component": "sim"})
    assert val == 2

    val = mc.inc("events_processed", 3, {"component": "sim"})
    assert val == 5

    # Test gauge
    val = mc.set_gauge("queue_depth", 3.5, {"component": "sim"})
    assert val == 3.5

    # Check snapshot
    snap = mc.snapshot()
    assert "counters" in snap
    assert "gauges" in snap
    assert any("events_processed" in k for k in snap["counters"].keys())
    assert any("queue_depth" in k for k in snap["gauges"].keys())

def test_reject_pii_labels_in_counter():
    """Test that PII labels are rejected in counters."""
    mc = MetricsCollector()

    with pytest.raises(ValueError, match="PII labels forbidden"):
        mc.inc("test_metric", 1, {"user_email": "test@example.com"})

    with pytest.raises(ValueError, match="PII labels forbidden"):
        mc.inc("test_metric", 1, {"ssn": "123-45-6789"})

    with pytest.raises(ValueError, match="PII labels forbidden"):
        mc.inc("test_metric", 1, {"iban": "DE89370400440532013000"})

def test_reject_pii_labels_in_gauge():
    """Test that PII labels are rejected in gauges."""
    mc = MetricsCollector()

    with pytest.raises(ValueError, match="PII labels forbidden"):
        mc.set_gauge("test_gauge", 1.0, {"user_name": "john_doe"})

    with pytest.raises(ValueError, match="PII labels forbidden"):
        mc.set_gauge("test_gauge", 1.0, {"phone": "+1234567890"})

def test_multiple_labels_without_pii():
    """Test metrics with multiple safe labels."""
    mc = MetricsCollector()

    mc.inc("requests", 1, {"component": "api", "status": "200", "method": "GET"})
    mc.inc("requests", 1, {"component": "api", "status": "404", "method": "GET"})

    snap = mc.snapshot()
    assert len(snap["counters"]) == 2

def test_reset():
    """Test metrics reset functionality."""
    mc = MetricsCollector()

    mc.inc("test", 5)
    mc.set_gauge("test_gauge", 10.0)

    snap1 = mc.snapshot()
    assert len(snap1["counters"]) > 0
    assert len(snap1["gauges"]) > 0

    mc.reset()

    snap2 = mc.snapshot()
    assert len(snap2["counters"]) == 0
    assert len(snap2["gauges"]) == 0

def test_label_independence():
    """Test that metrics with different labels are independent."""
    mc = MetricsCollector()

    mc.inc("requests", 5, {"service": "A"})
    mc.inc("requests", 10, {"service": "B"})

    snap = mc.snapshot()
    counters = snap["counters"]

    # Should have 2 separate counter entries
    assert len(counters) == 2
