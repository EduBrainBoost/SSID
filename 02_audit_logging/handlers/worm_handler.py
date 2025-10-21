#!/usr/bin/env python3
"""
WORM Handler - Event Bus Integration
=====================================

Processes audit events by writing to WORM storage.
Implements AuditEventHandler protocol.

Features:
- Write-once semantics (immutable evidence)
- SHA-256 content hashing
- Batch writes for performance (optional)
- Filter support (only process events with requires_worm=True)

Status: Phase 1 (Production-Ready)
Version: 1.0.0
"""

import sys
from pathlib import Path
from typing import List
import time

# Add parent paths
sys.path.insert(0, str(Path(__file__).parent.parent / "interfaces"))
sys.path.insert(0, str(Path(__file__).parent.parent / "worm_storage"))

from audit_event_emitter import (
    AuditEvent,
    AuditEventHandler,
    EmitResult
)

from worm_storage_engine import WORMStorageEngine, WORMViolationError


class WORMHandler(AuditEventHandler):
    """
    WORM storage handler for audit events.

    Processes events by writing to immutable WORM storage.
    Returns WORM content hash in EmitResult.
    """

    def __init__(
        self,
        storage_root: str = "02_audit_logging/worm_storage/vault",
        batch_enabled: bool = False,
        batch_size: int = 100,
        flush_interval_ms: int = 5000
    ):
        """
        Initialize WORM handler.

        Args:
            storage_root: WORM storage directory
            batch_enabled: Enable batch writes (future optimization)
            batch_size: Batch size for writes
            flush_interval_ms: Flush interval for batches
        """
        self.storage_root = storage_root
        self.batch_enabled = batch_enabled
        self.batch_size = batch_size
        self.flush_interval_ms = flush_interval_ms

        # Initialize WORM storage engine
        self.worm = WORMStorageEngine(storage_root=storage_root)

        # Batch buffer (if batching enabled)
        self.batch_buffer: List[AuditEvent] = []
        self.last_flush_time = time.time()

        # Statistics
        self.stats = {
            "events_processed": 0,
            "events_failed": 0,
            "worm_violations": 0
        }

    def handle(self, event: AuditEvent) -> EmitResult:
        """
        Process audit event by writing to WORM storage.

        Args:
            event: Audit event to process

        Returns:
            EmitResult with WORM content hash
        """
        try:
            # Convert AuditEvent to evidence data
            evidence_data = event.to_dict()

            # Determine category from source_module
            category = event.source_module.replace("/", "_").replace("\\", "_")

            # Write to WORM storage
            worm_result = self.worm.write_evidence(
                evidence_id=event.event_id,
                evidence_data=evidence_data,
                category=category
            )

            self.stats["events_processed"] += 1

            return EmitResult(
                event_id=event.event_id,
                status="processed",
                worm_hash=worm_result["content_hash"]
            )

        except WORMViolationError as e:
            # Event ID already exists (WORM violation)
            self.stats["worm_violations"] += 1

            return EmitResult(
                event_id=event.event_id,
                status="failed",
                error=f"WORM violation: {e}"
            )

        except Exception as e:
            self.stats["events_failed"] += 1

            return EmitResult(
                event_id=event.event_id,
                status="failed",
                error=f"WORM write failed: {e}"
            )

    def supports(self, event: AuditEvent) -> bool:
        """
        Check if handler supports this event.

        Only processes events with requires_worm=True.

        Args:
            event: Event to check

        Returns:
            True if requires_worm is set
        """
        return event.requires_worm

    def name(self) -> str:
        """Get handler name."""
        return "worm_handler"

    def get_stats(self):
        """Get handler statistics."""
        return {
            "handler": self.name(),
            "storage_root": self.storage_root,
            "stats": self.stats
        }


# Factory function
def create_worm_handler_from_config(config: dict) -> WORMHandler:
    """
    Create WORM handler from configuration.

    Example config:
    {
        "storage_root": "02_audit_logging/worm_storage/vault",
        "batch_size": 100,
        "flush_interval_ms": 5000
    }
    """
    return WORMHandler(
        storage_root=config.get("storage_root", "02_audit_logging/worm_storage/vault"),
        batch_enabled=config.get("batch_enabled", False),
        batch_size=config.get("batch_size", 100),
        flush_interval_ms=config.get("flush_interval_ms", 5000)
    )


# Example usage
if __name__ == "__main__":
    from datetime import datetime

    # Initialize handler
    handler = WORMHandler()

    # Create sample event
    event = AuditEvent(
        event_id=f"worm_test_{int(time.time() * 1000)}",
        timestamp=datetime.utcnow(),
        source_module="test/worm_handler",
        event_type="health_check",
        severity="INFO",
        data={"test": True, "handler": "worm"},
        requires_worm=True,
        requires_blockchain=False
    )

    print("Testing WORM Handler")
    print("=" * 70)

    # Check if handler supports event
    print(f"Supports event: {handler.supports(event)}")

    # Handle event
    result = handler.handle(event)

    print(f"Event ID: {result.event_id}")
    print(f"Status: {result.status}")
    print(f"WORM Hash: {result.worm_hash}")
    print()

    # Stats
    stats = handler.get_stats()
    print("Handler Statistics:")
    print(f"  Events Processed: {stats['stats']['events_processed']}")
    print(f"  Events Failed: {stats['stats']['events_failed']}")
    print(f"  WORM Violations: {stats['stats']['worm_violations']}")
    print()

    print("=" * 70)
    print("[OK] WORM Handler Test Complete")
