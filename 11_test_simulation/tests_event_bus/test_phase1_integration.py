#!/usr/bin/env python3
"""
Phase 1 Integration Tests
==========================

End-to-end tests for Phase 1 migration:
- Legacy adapter functionality
- Health audit logger with event bus
- WORM handler integration
- Health log handler integration

Status: Phase 1 Validation
Version: 1.0.0
"""

import pytest
import time
import json
from datetime import datetime
from pathlib import Path
import sys

# Add module paths
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "02_audit_logging" / "interfaces"))
sys.path.insert(0, str(ROOT / "02_audit_logging" / "event_bus"))
sys.path.insert(0, str(ROOT / "02_audit_logging" / "adapters"))
sys.path.insert(0, str(ROOT / "02_audit_logging" / "handlers"))
sys.path.insert(0, str(ROOT / "03_core" / "healthcheck"))

from audit_event_emitter import (
    AuditEvent,
    EventType,
    EventSeverity,
    set_audit_emitter,
    reset_audit_emitter
)

from in_memory_bus import InMemoryAuditBus
from legacy_adapter import LegacyAuditAdapter
from worm_handler import WORMHandler
from health_log_handler import HealthLogHandler


# Fixtures
# ========

@pytest.fixture
def event_bus_with_handlers():
    """Create event bus with WORM and health log handlers."""
    bus = InMemoryAuditBus(max_queue_size=100, worker_threads=2)

    # Register handlers
    worm_handler = WORMHandler(storage_root="02_audit_logging/worm_storage/vault_test")
    health_handler = HealthLogHandler(log_path="02_audit_logging/logs/health_test.jsonl")

    bus.register_handler(worm_handler)
    bus.register_handler(health_handler)

    set_audit_emitter(bus)

    yield bus

    bus.shutdown(timeout_ms=5000)
    reset_audit_emitter()


@pytest.fixture
def legacy_adapter():
    """Create legacy adapter."""
    adapter = LegacyAuditAdapter(
        worm_root="02_audit_logging/worm_storage/vault_test_legacy"
    )
    yield adapter


# Test Cases: Legacy Adapter
# ===========================

def test_legacy_adapter_emit_sync(legacy_adapter):
    """Test legacy adapter emit_sync."""
    event = AuditEvent(
        event_id=f"legacy_test_{int(time.time() * 1000)}",
        timestamp=datetime.utcnow(),
        source_module="test/legacy_adapter",
        event_type=EventType.HEALTH_CHECK,
        severity=EventSeverity.INFO,
        data={"test": True},
        requires_worm=True
    )

    result = legacy_adapter.emit_sync(event, timeout_ms=5000)

    assert result.event_id == event.event_id
    assert result.status == "processed"
    assert result.worm_hash is not None
    assert len(result.worm_hash) == 64  # SHA-256


def test_legacy_adapter_health_check(legacy_adapter):
    """Test legacy adapter health check."""
    health = legacy_adapter.health_check()

    assert health["backend"] == "legacy_integrated_audit_trail"
    assert health["status"] in ["healthy", "degraded", "unhealthy"]
    assert "worm_storage" in health


# Test Cases: Event Bus with Handlers
# ====================================

def test_event_bus_with_worm_handler(event_bus_with_handlers):
    """Test event bus with WORM handler."""
    event = AuditEvent(
        event_id=f"worm_test_{int(time.time() * 1000)}",
        timestamp=datetime.utcnow(),
        source_module="test/event_bus",
        event_type=EventType.HEALTH_CHECK,
        severity=EventSeverity.INFO,
        data={"test": True},
        requires_worm=True
    )

    result = event_bus_with_handlers.emit_sync(event, timeout_ms=5000)

    assert result.status == "processed"
    assert result.worm_hash is not None


def test_event_bus_with_health_log_handler(event_bus_with_handlers):
    """Test event bus with health log handler."""
    event = AuditEvent(
        event_id=f"health_log_test_{int(time.time() * 1000)}",
        timestamp=datetime.utcnow(),
        source_module="test/event_bus",
        event_type=EventType.HEALTH_CHECK,
        severity=EventSeverity.INFO,
        data={
            "component": "test_component",
            "services_checked": 5,
            "failed": 0
        },
        requires_worm=False
    )

    result = event_bus_with_handlers.emit_sync(event, timeout_ms=5000)

    assert result.status == "processed"

    # Verify log file
    log_path = Path("02_audit_logging/logs/health_test.jsonl")
    assert log_path.exists()

    # Read last entry
    with log_path.open("r", encoding="utf-8") as f:
        lines = f.readlines()
        last_entry = json.loads(lines[-1])

        assert last_entry["component"] == "test_component"
        assert last_entry["services_checked"] == 5
        assert last_entry["failed"] == 0


def test_event_bus_both_handlers(event_bus_with_handlers):
    """Test event bus with both WORM and health log handlers."""
    event = AuditEvent(
        event_id=f"both_handlers_test_{int(time.time() * 1000)}",
        timestamp=datetime.utcnow(),
        source_module="test/event_bus",
        event_type=EventType.HEALTH_CHECK,
        severity=EventSeverity.INFO,
        data={
            "component": "api_server",
            "services_checked": 10,
            "failed": 0
        },
        requires_worm=True  # Should trigger WORM handler
    )

    result = event_bus_with_handlers.emit_sync(event, timeout_ms=5000)

    assert result.status == "processed"
    assert result.worm_hash is not None  # WORM handler processed

    # Verify health log
    log_path = Path("02_audit_logging/logs/health_test.jsonl")
    with log_path.open("r", encoding="utf-8") as f:
        lines = f.readlines()
        last_entry = json.loads(lines[-1])
        assert last_entry["component"] == "api_server"


# Test Cases: Health Audit Logger Integration
# ============================================

def test_health_audit_logger_with_event_bus(event_bus_with_handlers):
    """Test migrated health_audit_logger with event bus."""
    import health_audit_logger

    # Reset audit bus to use test instance
    set_audit_emitter(event_bus_with_handlers)

    # Log health check
    health_audit_logger.log_health_check(
        component="test_service",
        status="PASS",
        services_checked=5,
        failed=0,
        details={"test": True}
    )

    # Give event bus time to process
    event_bus_with_handlers.flush(timeout_ms=2000)

    # Verify health log
    log_path = Path("02_audit_logging/logs/health_test.jsonl")
    with log_path.open("r", encoding="utf-8") as f:
        lines = f.readlines()
        last_entry = json.loads(lines[-1])

        assert last_entry["component"] == "test_service"
        assert last_entry["status"] == "PASS"
        assert last_entry["services_checked"] == 5
        assert last_entry["failed"] == 0


# Test Cases: Handler Filtering
# ==============================

def test_worm_handler_filters_correctly(event_bus_with_handlers):
    """Test WORM handler only processes events with requires_worm=True."""
    # Event without WORM requirement
    event_no_worm = AuditEvent(
        event_id=f"no_worm_test_{int(time.time() * 1000)}",
        timestamp=datetime.utcnow(),
        source_module="test/filtering",
        event_type=EventType.HEALTH_CHECK,
        severity=EventSeverity.INFO,
        data={"test": True},
        requires_worm=False  # Should NOT trigger WORM handler
    )

    result = event_bus_with_handlers.emit_sync(event_no_worm, timeout_ms=5000)

    # Should process (health handler) but no WORM hash
    assert result.status == "processed"
    assert result.worm_hash is None  # WORM handler skipped


def test_health_log_handler_filters_correctly(event_bus_with_handlers):
    """Test health log handler only processes HEALTH_CHECK events."""
    # Non-health event
    event_kyc = AuditEvent(
        event_id=f"kyc_test_{int(time.time() * 1000)}",
        timestamp=datetime.utcnow(),
        source_module="test/filtering",
        event_type=EventType.KYC_VERIFICATION,  # Not HEALTH_CHECK
        severity=EventSeverity.INFO,
        data={"test": True},
        requires_worm=True
    )

    log_path = Path("02_audit_logging/logs/health_test.jsonl")
    initial_line_count = sum(1 for _ in log_path.open()) if log_path.exists() else 0

    result = event_bus_with_handlers.emit_sync(event_kyc, timeout_ms=5000)

    # WORM should process, health log should not
    assert result.status == "processed"
    assert result.worm_hash is not None

    # Health log should not have new entry
    final_line_count = sum(1 for _ in log_path.open())
    assert final_line_count == initial_line_count  # No new line


# Test Cases: Performance
# ========================

def test_event_bus_throughput(event_bus_with_handlers):
    """Test event bus throughput."""
    num_events = 100
    start_time = time.time()

    for i in range(num_events):
        event = AuditEvent(
            event_id=f"perf_test_{i}_{int(time.time() * 1000)}",
            timestamp=datetime.utcnow(),
            source_module="test/performance",
            event_type=EventType.HEALTH_CHECK,
            severity=EventSeverity.INFO,
            data={"index": i},
            requires_worm=True
        )

        event_bus_with_handlers.emit(event)

    event_bus_with_handlers.flush(timeout_ms=30000)
    duration = time.time() - start_time

    throughput = num_events / duration

    print(f"\nThroughput: {throughput:.0f} events/sec")
    assert throughput > 50  # Should process at least 50 events/sec


# Test Cases: Error Handling
# ===========================

def test_graceful_degradation_handler_failure(event_bus_with_handlers):
    """Test graceful degradation when handler fails."""
    # Create failing handler
    class FailingHandler:
        def handle(self, event):
            raise ValueError("Simulated failure")

        def supports(self, event):
            return True

        def name(self):
            return "failing_handler"

    event_bus_with_handlers.register_handler(FailingHandler())

    event = AuditEvent(
        event_id=f"failure_test_{int(time.time() * 1000)}",
        timestamp=datetime.utcnow(),
        source_module="test/error_handling",
        event_type=EventType.HEALTH_CHECK,
        severity=EventSeverity.INFO,
        data={"test": True},
        requires_worm=True
    )

    result = event_bus_with_handlers.emit_sync(event, timeout_ms=5000)

    # Should still process (other handlers succeed)
    # But status indicates failure
    assert result.status == "failed"
    assert "Simulated failure" in result.error


# Summary Test
# ============

def test_phase1_complete_workflow(event_bus_with_handlers):
    """Test complete Phase 1 workflow."""
    print("\n" + "=" * 70)
    print("Phase 1 Integration Test - Complete Workflow")
    print("=" * 70)

    # Step 1: Emit health check event
    event = AuditEvent(
        event_id=f"phase1_workflow_{int(time.time() * 1000)}",
        timestamp=datetime.utcnow(),
        source_module="03_core/healthcheck",
        event_type=EventType.HEALTH_CHECK,
        severity=EventSeverity.INFO,
        data={
            "component": "api_gateway",
            "services_checked": 20,
            "failed": 0,
            "details": {
                "success_rate": 100.0,
                "response_time_ms": 45
            }
        },
        requires_worm=True,
        requires_blockchain=False
    )

    print(f"Step 1: Emit event {event.event_id}")
    result = event_bus_with_handlers.emit_sync(event, timeout_ms=5000)

    print(f"Step 2: Event processed (status: {result.status})")
    assert result.status == "processed"

    print(f"Step 3: WORM hash: {result.worm_hash[:16]}...")
    assert result.worm_hash is not None

    # Verify health log
    log_path = Path("02_audit_logging/logs/health_test.jsonl")
    with log_path.open("r", encoding="utf-8") as f:
        lines = f.readlines()
        last_entry = json.loads(lines[-1])

    print(f"Step 4: Health log verified")
    assert last_entry["component"] == "api_gateway"

    # Health check
    health = event_bus_with_handlers.health_check()

    print(f"Step 5: Event bus health: {health['status']}")
    print(f"  - Queue depth: {health['queue_depth']}")
    print(f"  - Events processed: {health['metrics']['events_processed']}")
    print(f"  - Handlers: {health['handlers']}")

    print("=" * 70)
    print("[OK] Phase 1 Complete Workflow Test PASSED")
    print("=" * 70)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
