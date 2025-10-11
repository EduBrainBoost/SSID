#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
health_audit_logger.py – Health Check Audit Integration
Autor: edubrainboost ©2025 MIT License

Logs health check results to audit system with structured JSONL format.
Integrates with 02_audit_logging for compliance tracking.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any


ROOT = Path(__file__).resolve().parents[2]
AUDIT_LOG = ROOT / "02_audit_logging" / "logs" / "health_readiness_log.jsonl"


def log_health_check(
    component: str,
    status: str,
    services_checked: int,
    failed: int,
    details: Dict[str, Any] = None
) -> None:
    """
    Log health check results to audit system.

    Args:
        component: Component name (e.g., "health", "readiness")
        status: Check status ("PASS", "FAIL", "WARN")
        services_checked: Total number of services checked
        failed: Number of failed checks
        details: Additional details (optional)
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
