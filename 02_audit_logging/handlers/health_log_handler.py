#!/usr/bin/env python3
"""
Health Log Handler - Event Bus Integration
===========================================

Processes health check events by writing to JSONL log file.
Implements AuditEventHandler protocol.

Features:
- Structured JSONL logging
- Filter support (only HEALTH_CHECK events)
- Log rotation (size and age-based)
- Backward compatible with legacy health_readiness_log.jsonl

Status: Phase 1 (Production-Ready)
Version: 1.0.0
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

# Add parent paths
sys.path.insert(0, str(Path(__file__).parent.parent / "interfaces"))

from audit_event_emitter import (
    AuditEvent,
    AuditEventHandler,
    EmitResult,
    EventType
)


class HealthLogHandler(AuditEventHandler):
    """
    Health check log handler for audit events.

    Processes HEALTH_CHECK events by writing to JSONL log file.
    Compatible with legacy health_readiness_log.jsonl format.
    """

    def __init__(
        self,
        log_path: str = "02_audit_logging/logs/health_readiness_log.jsonl",
        max_size_mb: int = 100,
        max_age_days: int = 90
    ):
        """
        Initialize health log handler.

        Args:
            log_path: Path to JSONL log file
            max_size_mb: Max log file size before rotation (MB)
            max_age_days: Max log file age before rotation (days)
        """
        self.log_path = Path(log_path)
        self.max_size_mb = max_size_mb
        self.max_age_days = max_age_days

        # Ensure log directory exists
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

        # Statistics
        self.stats = {
            "events_processed": 0,
            "events_failed": 0,
            "rotations": 0
        }

    def handle(self, event: AuditEvent) -> EmitResult:
        """
        Process health check event by writing to JSONL log.

        Args:
            event: Audit event to process

        Returns:
            EmitResult with processing status
        """
        try:
            # Check if rotation needed
            self._check_rotation()

            # Convert event to legacy JSONL format for compatibility
            log_entry = self._event_to_log_entry(event)

            # Write to JSONL
            with self.log_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")

            self.stats["events_processed"] += 1

            return EmitResult(
                event_id=event.event_id,
                status="processed"
            )

        except Exception as e:
            self.stats["events_failed"] += 1

            return EmitResult(
                event_id=event.event_id,
                status="failed",
                error=f"Health log write failed: {e}"
            )

    def supports(self, event: AuditEvent) -> bool:
        """
        Check if handler supports this event.

        Only processes HEALTH_CHECK events.

        Args:
            event: Event to check

        Returns:
            True if event_type is HEALTH_CHECK
        """
        return (
            event.event_type == EventType.HEALTH_CHECK or
            event.event_type == "health_check"  # String backward compat
        )

    def name(self) -> str:
        """Get handler name."""
        return "health_log_handler"

    def _event_to_log_entry(self, event: AuditEvent) -> dict:
        """
        Convert AuditEvent to legacy JSONL log format.

        Ensures backward compatibility with existing log parsers.

        Args:
            event: Audit event

        Returns:
            Log entry dict (legacy format)
        """
        # Extract fields from event.data
        data = event.data

        return {
            "timestamp": event.timestamp.isoformat() + "Z" if isinstance(event.timestamp, datetime) else event.timestamp,
            "component": data.get("component", "unknown"),
            "status": self._map_severity_to_status(event.severity),
            "services_checked": data.get("services_checked", 0),
            "failed": data.get("failed", 0),
            "details": data.get("details", {}),
            # NEW: Add event metadata for enhanced logging
            "event_id": event.event_id,
            "source_module": event.source_module,
            "correlation_id": event.correlation_id
        }

    def _map_severity_to_status(self, severity) -> str:
        """
        Map EventSeverity to legacy status string.

        Args:
            severity: EventSeverity or string

        Returns:
            "PASS", "FAIL", or "WARN"
        """
        severity_str = severity.value if hasattr(severity, 'value') else str(severity)

        if severity_str in ["INFO", "DEBUG"]:
            return "PASS"
        elif severity_str in ["ERROR", "CRITICAL"]:
            return "FAIL"
        else:
            return "WARN"

    def _check_rotation(self) -> None:
        """
        Check if log rotation is needed.

        Rotates log file if:
        - Size exceeds max_size_mb
        - Age exceeds max_age_days
        """
        if not self.log_path.exists():
            return

        # Check size
        size_mb = self.log_path.stat().st_size / (1024 * 1024)

        if size_mb > self.max_size_mb:
            self._rotate_log("size")
            return

        # Check age
        from datetime import datetime, timezone
        mtime = datetime.fromtimestamp(self.log_path.stat().st_mtime, tz=timezone.utc)
        age_days = (datetime.now(timezone.utc) - mtime).days

        if age_days > self.max_age_days:
            self._rotate_log("age")

    def _rotate_log(self, reason: str) -> None:
        """
        Rotate log file.

        Args:
            reason: Rotation reason ("size" or "age")
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        rotated_path = self.log_path.with_suffix(f".{timestamp}.jsonl")

        # Rename current log
        self.log_path.rename(rotated_path)

        self.stats["rotations"] += 1

        print(
            f"[INFO] Health log rotated (reason: {reason}): {rotated_path}",
            file=sys.stderr
        )

    def get_stats(self):
        """Get handler statistics."""
        return {
            "handler": self.name(),
            "log_path": str(self.log_path),
            "log_size_mb": round(self.log_path.stat().st_size / (1024 * 1024), 2) if self.log_path.exists() else 0,
            "stats": self.stats
        }


# Factory function
def create_health_log_handler_from_config(config: dict) -> HealthLogHandler:
    """
    Create health log handler from configuration.

    Example config:
    {
        "log_path": "02_audit_logging/logs/health_readiness_log.jsonl",
        "max_size_mb": 100,
        "max_age_days": 90
    }
    """
    return HealthLogHandler(
        log_path=config.get("log_path", "02_audit_logging/logs/health_readiness_log.jsonl"),
        max_size_mb=config.get("max_size_mb", 100),
        max_age_days=config.get("max_age_days", 90)
    )


# Example usage
if __name__ == "__main__":
    import time

    # Initialize handler
    handler = HealthLogHandler()

    # Create sample health check event
    event = AuditEvent(
        event_id=f"health_test_{int(time.time() * 1000)}",
        timestamp=datetime.utcnow(),
        source_module="test/health_log_handler",
        event_type=EventType.HEALTH_CHECK,
        severity="INFO",
        data={
            "component": "api_server",
            "services_checked": 5,
            "failed": 0,
            "details": {
                "success_rate": 100.0,
                "failed_services": []
            }
        },
        requires_worm=False
    )

    print("Testing Health Log Handler")
    print("=" * 70)

    # Check if handler supports event
    print(f"Supports event: {handler.supports(event)}")

    # Handle event
    result = handler.handle(event)

    print(f"Event ID: {result.event_id}")
    print(f"Status: {result.status}")
    print()

    # Stats
    stats = handler.get_stats()
    print("Handler Statistics:")
    print(f"  Events Processed: {stats['stats']['events_processed']}")
    print(f"  Events Failed: {stats['stats']['events_failed']}")
    print(f"  Log Rotations: {stats['stats']['rotations']}")
    print(f"  Log Size: {stats['log_size_mb']} MB")
    print()

    # Verify log entry
    if handler.log_path.exists():
        with handler.log_path.open("r", encoding="utf-8") as f:
            lines = f.readlines()
            last_entry = json.loads(lines[-1])
            print("Last Log Entry:")
            print(json.dumps(last_entry, indent=2))

    print("=" * 70)
    print("[OK] Health Log Handler Test Complete")
