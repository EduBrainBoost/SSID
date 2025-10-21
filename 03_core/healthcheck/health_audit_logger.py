#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
health_audit_logger.py – Health Check Audit Integration
Autor: edubrainboost ©2025 MIT License

Logs health check results to audit system with structured JSONL format.
Integrates with 02_audit_logging for compliance tracking.

MIGRATION STATUS: Phase 1 - Event Bus Integration
- Uses new AuditEventEmitter interface
- Legacy file-based logging preserved as fallback
- Backward compatible with existing callers
"""

import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import sys

# Add event bus to path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "02_audit_logging" / "interfaces"))
sys.path.insert(0, str(ROOT / "02_audit_logging" / "event_bus"))

try:
    from audit_event_emitter import (
        AuditEvent,
        EventType,
        EventSeverity,
        get_audit_emitter,
        set_audit_emitter
    )
    from in_memory_bus import InMemoryAuditBus
    EVENT_BUS_AVAILABLE = True
except ImportError:
    EVENT_BUS_AVAILABLE = False
    print("[WARN] Event bus not available, using legacy file logging", file=sys.stderr)

# Legacy fallback (preserved for compatibility)
AUDIT_LOG = ROOT / "02_audit_logging" / "logs" / "health_readiness_log.jsonl"

# Global event bus instance (lazy-initialized)
_audit_bus = None


def _get_audit_bus():
    """Get or initialize audit bus."""
    global _audit_bus

    if not EVENT_BUS_AVAILABLE:
        return None

    if _audit_bus is None:
        try:
            _audit_bus = get_audit_emitter()
        except RuntimeError:
            # Not initialized, create default
            _audit_bus = InMemoryAuditBus(max_queue_size=1000, worker_threads=2)
            set_audit_emitter(_audit_bus)

    return _audit_bus


def log_health_check(
    component: str,
    status: str,
    services_checked: int,
    failed: int,
    details: Dict[str, Any] = None
) -> None:
    """
    Log health check results to audit system.

    NEW: Uses event bus if available, falls back to file logging.

    Args:
        component: Component name (e.g., "health", "readiness")
        status: Check status ("PASS", "FAIL", "WARN")
        services_checked: Total number of services checked
        failed: Number of failed checks
        details: Additional details (optional)
    """
    # Prepare data
    data = {
        "component": component,
        "services_checked": services_checked,
        "failed": failed,
    }

    if details:
        data["details"] = details

    # Try event bus first
    audit_bus = _get_audit_bus()

    if audit_bus is not None:
        try:
            # Map status to severity
            severity = EventSeverity.INFO if status == "PASS" else EventSeverity.ERROR

            # Create audit event
            event = AuditEvent(
                event_id=f"health_{component}_{int(time.time() * 1000)}",
                timestamp=datetime.utcnow(),
                source_module="03_core/healthcheck",
                event_type=EventType.HEALTH_CHECK,
                severity=severity,
                data=data,
                requires_worm=True,
                requires_blockchain=False
            )

            # Emit event (fire-and-forget)
            audit_bus.emit(event)

            return  # Success, no fallback needed

        except Exception as e:
            print(f"[WARN] Event bus emit failed, using fallback: {e}", file=sys.stderr)

    # Fallback to legacy file logging
    _log_health_check_legacy(component, status, services_checked, failed, details)


def _log_health_check_legacy(
    component: str,
    status: str,
    services_checked: int,
    failed: int,
    details: Optional[Dict[str, Any]] = None
) -> None:
    """
    Legacy file-based logging (fallback).

    Preserved for backward compatibility and graceful degradation.
    """
    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)

    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "component": component,
        "status": status,
        "services_checked": services_checked,
        "failed": failed,
    }

    if details:
        entry["details"] = details

    # Append to JSONL
    with AUDIT_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

def log_service_health_batch(results: List[Dict[str, Any]]) -> None:
    """
    Log batch of service health check results.

    Args:
        results: List of readiness check results from HealthChecker.readiness()
    """
    total = len(results)
    failed_count = sum(1 for r in results if not r["status"])
    status = "PASS" if failed_count == 0 else "FAIL"

    # Log summary
    log_health_check(
        component="health_batch",
        status=status,
        services_checked=total,
        failed=failed_count,
        details={
            "success_rate": round((total - failed_count) / total * 100, 2) if total > 0 else 0,
            "failed_services": [r["service"] for r in results if not r["status"]]
        }
    )

def get_audit_summary(limit: int = 100) -> Dict[str, Any]:
    """
    Get summary of recent health check audit logs.

    Args:
        limit: Maximum number of recent entries to analyze

    Returns:
        Dict with summary statistics
    """
    if not AUDIT_LOG.exists():
        return {
            "total_entries": 0,
            "status": "NO_DATA",
            "last_check": None
        }

    entries = []
    with AUDIT_LOG.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

    # Take last N entries
    recent = entries[-limit:] if len(entries) > limit else entries

    if not recent:
        return {
            "total_entries": 0,
            "status": "NO_DATA",
            "last_check": None
        }

    # Calculate statistics
    total_checks = sum(e.get("services_checked", 0) for e in recent)
    total_failures = sum(e.get("failed", 0) for e in recent)
    pass_count = sum(1 for e in recent if e.get("status") == "PASS")

    return {
        "total_entries": len(recent),
        "total_checks": total_checks,
        "total_failures": total_failures,
        "pass_count": pass_count,
        "fail_count": len(recent) - pass_count,
        "success_rate": round(pass_count / len(recent) * 100, 2) if recent else 0,
        "last_check": recent[-1]["timestamp"],
        "overall_status": "HEALTHY" if total_failures == 0 else "DEGRADED"
    }

# CLI interface
if __name__ == "__main__":
    import sys

    # Example: log a test entry
    log_health_check(
        component="health-audit-logger",
        status="PASS",
        services_checked=1,
        failed=0,
        details={"test": True}
    )

    # Display summary
    summary = get_audit_summary()
    print("Health Audit Summary:")
    print(json.dumps(summary, indent=2))

    sys.exit(0)
