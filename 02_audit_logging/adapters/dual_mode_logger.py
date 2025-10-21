#!/usr/bin/env python3
"""
Dual-Mode Audit Logger - Migration Validation
==============================================

Runs both legacy (IntegratedAuditTrail) and new (Event Bus) systems in parallel.
Compares WORM hashes to ensure consistency during migration.

Purpose:
- Validate new event bus produces identical WORM hashes as legacy system
- Detect regressions during migration (Phase 2)
- Provide rollback confidence (hash mismatch → abort migration)

Usage:
    # Phase 2: Enable dual-mode in manifest.yaml
    dual_mode:
      enabled: true
      hash_comparison: true
      alert_on_mismatch: true

    # The adapter routes events to BOTH systems
    dual_logger = DualModeAuditLogger()
    result = dual_logger.emit_sync(event)
    # → result.legacy_hash == result.new_hash (validated)

Status: Migration Phase 2
Version: 1.0.0
"""

import hashlib
import json
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

import sys
from pathlib import Path

# Add parent paths
sys.path.insert(0, str(Path(__file__).parent.parent / "interfaces"))
sys.path.insert(0, str(Path(__file__).parent.parent / "evidence_trails"))
sys.path.insert(0, str(Path(__file__).parent.parent / "event_bus"))

from audit_event_emitter import (
    AuditEvent,
    AuditEventEmitter,
    EmitResult,
    EventSeverity
)


@dataclass
class DualModeResult:
    """Result of dual-mode logging with hash comparison."""
    event_id: str
    legacy_hash: Optional[str]
    new_hash: Optional[str]
    hashes_match: bool
    legacy_error: Optional[str] = None
    new_error: Optional[str] = None
    legacy_time_ms: Optional[float] = None
    new_time_ms: Optional[float] = None
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat() + "Z"


class DualModeAuditLogger:
    """
    Dual-mode logger for migration validation.

    Architecture:
    1. Receive AuditEvent
    2. Convert to legacy format → IntegratedAuditTrail.record_evidence()
    3. Convert to new format → EventBus.emit_sync()
    4. Compare WORM hashes (SHA-256)
    5. Log mismatches to validation report

    Modes:
    - alert_on_mismatch=True → Raise exception on mismatch (fail-fast)
    - alert_on_mismatch=False → Log warning only (continuous monitoring)
    """

    def __init__(
        self,
        legacy_enabled: bool = True,
        new_enabled: bool = True,
        hash_comparison: bool = True,
        alert_on_mismatch: bool = True,
        report_path: str = "02_audit_logging/validation/dual_mode_report.jsonl"
    ):
        """
        Initialize dual-mode logger.

        Args:
            legacy_enabled: Run legacy IntegratedAuditTrail
            new_enabled: Run new EventBus
            hash_comparison: Compare WORM hashes
            alert_on_mismatch: Raise exception on hash mismatch
            report_path: Path to validation report (JSONL)
        """
        self.legacy_enabled = legacy_enabled
        self.new_enabled = new_enabled
        self.hash_comparison = hash_comparison
        self.alert_on_mismatch = alert_on_mismatch
        self.report_path = Path(report_path)
        self.report_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize legacy system (if enabled)
        self.legacy_trail = None
        if self.legacy_enabled:
            try:
                from integrated_audit_trail import IntegratedAuditTrail
                self.legacy_trail = IntegratedAuditTrail()
            except ImportError:
                print("[WARN] Legacy IntegratedAuditTrail not available", file=sys.stderr)
                self.legacy_enabled = False

        # Initialize new system (if enabled)
        self.new_bus = None
        if self.new_enabled:
            try:
                from in_memory_bus import InMemoryAuditBus
                self.new_bus = InMemoryAuditBus()
            except ImportError:
                print("[WARN] New InMemoryAuditBus not available", file=sys.stderr)
                self.new_enabled = False

        # Validation statistics
        self.stats = {
            "total_events": 0,
            "hashes_matched": 0,
            "hashes_mismatched": 0,
            "legacy_errors": 0,
            "new_errors": 0
        }

    def emit_sync(self, event: AuditEvent, timeout_ms: int = 5000) -> DualModeResult:
        """
        Emit event to both legacy and new systems (blocking).

        Returns:
            DualModeResult with hash comparison
        """
        self.stats["total_events"] += 1

        result = DualModeResult(
            event_id=event.event_id,
            legacy_hash=None,
            new_hash=None,
            hashes_match=False
        )

        # Legacy system
        if self.legacy_enabled:
            try:
                start_time = time.time()
                legacy_result = self._emit_legacy(event)
                result.legacy_time_ms = (time.time() - start_time) * 1000
                result.legacy_hash = legacy_result.get("worm_storage", {}).get("content_hash")
            except Exception as e:
                result.legacy_error = str(e)
                self.stats["legacy_errors"] += 1

        # New system
        if self.new_enabled:
            try:
                start_time = time.time()
                new_result = self.new_bus.emit_sync(event, timeout_ms=timeout_ms)
                result.new_time_ms = (time.time() - start_time) * 1000
                result.new_hash = new_result.worm_hash
            except Exception as e:
                result.new_error = str(e)
                self.stats["new_errors"] += 1

        # Hash comparison
        if self.hash_comparison and result.legacy_hash and result.new_hash:
            result.hashes_match = (result.legacy_hash == result.new_hash)

            if result.hashes_match:
                self.stats["hashes_matched"] += 1
            else:
                self.stats["hashes_mismatched"] += 1
                self._handle_hash_mismatch(result, event)

        # Log to validation report
        self._write_validation_report(result)

        return result

    def _emit_legacy(self, event: AuditEvent) -> Dict[str, Any]:
        """
        Emit event to legacy IntegratedAuditTrail.

        Converts AuditEvent → legacy format.
        """
        if not self.legacy_trail:
            raise RuntimeError("Legacy trail not initialized")

        # Convert AuditEvent to legacy format
        evidence_data = {
            "event_type": event.event_type.value if hasattr(event.event_type, 'value') else event.event_type,
            "severity": event.severity.value if hasattr(event.severity, 'value') else event.severity,
            "timestamp": event.timestamp.isoformat() if isinstance(event.timestamp, datetime) else event.timestamp,
            "correlation_id": event.correlation_id,
            "tags": event.tags,
            **event.data
        }

        # Record in legacy system
        return self.legacy_trail.record_evidence(
            evidence_id=event.event_id,
            evidence_data=evidence_data,
            category=event.source_module.replace("/", "_"),
            immediate_anchor=event.requires_blockchain
        )

    def _handle_hash_mismatch(self, result: DualModeResult, event: AuditEvent) -> None:
        """
        Handle hash mismatch between legacy and new systems.

        Args:
            result: Dual-mode result with mismatch
            event: Original audit event
        """
        error_msg = (
            f"[CRITICAL] Hash mismatch detected during dual-mode validation!\n"
            f"Event ID: {event.event_id}\n"
            f"Legacy Hash: {result.legacy_hash}\n"
            f"New Hash: {result.new_hash}\n"
            f"Event Type: {event.event_type}\n"
            f"Source: {event.source_module}\n"
            f"---\n"
            f"This indicates the new event bus is NOT producing identical WORM hashes.\n"
            f"Migration should be PAUSED until this is resolved.\n"
        )

        print(error_msg, file=sys.stderr)

        if self.alert_on_mismatch:
            raise ValueError(error_msg)

    def _write_validation_report(self, result: DualModeResult) -> None:
        """Write validation result to JSONL report."""
        with self.report_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps({
                "event_id": result.event_id,
                "timestamp": result.timestamp,
                "legacy_hash": result.legacy_hash,
                "new_hash": result.new_hash,
                "hashes_match": result.hashes_match,
                "legacy_error": result.legacy_error,
                "new_error": result.new_error,
                "legacy_time_ms": result.legacy_time_ms,
                "new_time_ms": result.new_time_ms
            }) + "\n")

    def get_validation_summary(self) -> Dict[str, Any]:
        """
        Get validation summary statistics.

        Returns:
            Dict with validation metrics
        """
        total = self.stats["total_events"]
        matched = self.stats["hashes_matched"]
        mismatched = self.stats["hashes_mismatched"]

        return {
            "total_events": total,
            "hashes_matched": matched,
            "hashes_mismatched": mismatched,
            "match_rate": round(matched / total * 100, 2) if total > 0 else 0,
            "legacy_errors": self.stats["legacy_errors"],
            "new_errors": self.stats["new_errors"],
            "status": "PASS" if mismatched == 0 else "FAIL",
            "migration_ready": mismatched == 0 and self.stats["new_errors"] == 0
        }

    def analyze_report(self, limit: int = 1000) -> Dict[str, Any]:
        """
        Analyze validation report for patterns.

        Args:
            limit: Maximum entries to analyze

        Returns:
            Dict with analysis results
        """
        if not self.report_path.exists():
            return {"status": "NO_DATA", "entries": 0}

        entries = []
        with self.report_path.open("r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    entries.append(json.loads(line))
                if len(entries) >= limit:
                    break

        if not entries:
            return {"status": "NO_DATA", "entries": 0}

        # Statistics
        total = len(entries)
        matched = sum(1 for e in entries if e.get("hashes_match"))
        mismatched = total - matched

        # Performance comparison
        legacy_times = [e["legacy_time_ms"] for e in entries if e.get("legacy_time_ms")]
        new_times = [e["new_time_ms"] for e in entries if e.get("new_time_ms")]

        avg_legacy = sum(legacy_times) / len(legacy_times) if legacy_times else 0
        avg_new = sum(new_times) / len(new_times) if new_times else 0

        # Mismatch patterns
        mismatched_events = [e for e in entries if not e.get("hashes_match")]

        return {
            "entries_analyzed": total,
            "hashes_matched": matched,
            "hashes_mismatched": mismatched,
            "match_rate_percent": round(matched / total * 100, 2),
            "performance": {
                "avg_legacy_ms": round(avg_legacy, 2),
                "avg_new_ms": round(avg_new, 2),
                "speedup_factor": round(avg_legacy / avg_new, 2) if avg_new > 0 else 0
            },
            "status": "PASS" if mismatched == 0 else "FAIL",
            "migration_recommendation": (
                "PROCEED" if mismatched == 0 else
                "BLOCK - Hash mismatches detected"
            ),
            "sample_mismatches": mismatched_events[:5]  # First 5 mismatches
        }


# CLI interface for validation reporting
def main():
    """CLI for dual-mode validation analysis."""
    import argparse

    parser = argparse.ArgumentParser(description="Dual-Mode Audit Logger Validation")
    parser.add_argument("--report", default="02_audit_logging/validation/dual_mode_report.jsonl",
                       help="Path to validation report")
    parser.add_argument("--limit", type=int, default=1000,
                       help="Max entries to analyze")

    args = parser.parse_args()

    # Analyze report
    logger = DualModeAuditLogger(
        legacy_enabled=False,  # Analysis only
        new_enabled=False,
        report_path=args.report
    )

    analysis = logger.analyze_report(limit=args.limit)

    # Print summary
    print("=" * 70)
    print("Dual-Mode Validation Analysis")
    print("=" * 70)
    print(f"Entries Analyzed: {analysis['entries_analyzed']}")
    print(f"Hashes Matched: {analysis['hashes_matched']}")
    print(f"Hashes Mismatched: {analysis['hashes_mismatched']}")
    print(f"Match Rate: {analysis['match_rate_percent']}%")
    print()
    print("Performance Comparison:")
    print(f"  Legacy Avg: {analysis['performance']['avg_legacy_ms']} ms")
    print(f"  New Avg: {analysis['performance']['avg_new_ms']} ms")
    print(f"  Speedup: {analysis['performance']['speedup_factor']}x")
    print()
    print(f"Status: {analysis['status']}")
    print(f"Migration Recommendation: {analysis['migration_recommendation']}")
    print("=" * 70)

    # Exit code
    sys.exit(0 if analysis['status'] == "PASS" else 1)


if __name__ == "__main__":
    main()
