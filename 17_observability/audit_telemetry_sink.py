#!/usr/bin/env python3
"""
Audit Telemetry Sink - Real-Time Event Metrics
===============================================

Receives metrics callbacks from event bus and publishes to observability layer.
Enables real-time monitoring of audit event processing.

Features:
- Real-time event metrics streaming
- Latency histograms (P50, P95, P99)
- Queue depth monitoring
- Alert thresholds for degradation
- Federation-ready (node_id tagging)

Status: Phase 2 (Observability Hook)
Version: 1.0.0
"""

import json
import time
from pathlib import Path
from typing import Dict, Any, List
from collections import deque
from datetime import datetime

class AuditTelemetrySink:
    """
    Telemetry sink for audit event bus metrics.

    Receives callbacks from InMemoryAuditBus and publishes to observability.
    """

    def __init__(
        self,
        telemetry_path: str = "17_observability/audit_metrics.jsonl",
        window_size: int = 1000,
        alert_threshold_queue_depth: int = 8000,
        alert_threshold_latency_ms: float = 100.0
    ):
        """
        Initialize telemetry sink.

        Args:
            telemetry_path: Path to metrics log (JSONL)
            window_size: Rolling window size for statistics
            alert_threshold_queue_depth: Alert if queue exceeds this depth
            alert_threshold_latency_ms: Alert if P95 latency exceeds this
        """
        self.telemetry_path = Path(telemetry_path)
        self.telemetry_path.parent.mkdir(parents=True, exist_ok=True)

        self.window_size = window_size
        self.alert_threshold_queue_depth = alert_threshold_queue_depth
        self.alert_threshold_latency_ms = alert_threshold_latency_ms

        # Rolling window for statistics
        self.latency_window: deque = deque(maxlen=window_size)
        self.queue_depth_window: deque = deque(maxlen=window_size)

        # Counters
        self.total_events = 0
        self.failed_events = 0
        self.start_time = time.time()

        # Alerts
        self.alerts_fired = []

        # Federation tracking (Phase 1.5+)
        self.federation_metrics = {}  # node_id → metrics
        self.proof_stream_start = time.time()

    def on_event_processed(self, event, metrics: Dict[str, Any]) -> None:
        """
        Callback invoked by event bus after processing each event.

        Args:
            event: AuditEvent that was processed
            metrics: Metrics snapshot from worker loop
        """
        # Update counters
        self.total_events += 1
        if metrics.get("status") == "failed":
            self.failed_events += 1

        # Update rolling windows
        processing_time = metrics.get("processing_time_ms", 0)
        queue_depth = metrics.get("queue_depth", 0)

        self.latency_window.append(processing_time)
        self.queue_depth_window.append(queue_depth)

        # Track federation metrics (Phase 1.5+)
        federation_node = event.federation_context.get("node_id", "local")
        if federation_node not in self.federation_metrics:
            self.federation_metrics[federation_node] = {
                "events_processed": 0,
                "total_latency_ms": 0.0,
                "failures": 0,
                "last_seen": time.time()
            }

        node_metrics = self.federation_metrics[federation_node]
        node_metrics["events_processed"] += 1
        node_metrics["total_latency_ms"] += processing_time
        node_metrics["last_seen"] = time.time()

        if metrics.get("status") == "failed":
            node_metrics["failures"] += 1

        # Compute statistics
        stats = self._compute_statistics()

        # Check alerts
        alerts = self._check_alerts(stats)

        # Publish telemetry
        telemetry_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "event_id": metrics.get("event_id"),
            "processing_time_ms": processing_time,
            "queue_depth": queue_depth,
            "handler_count": metrics.get("handler_count"),
            "status": metrics.get("status"),
            # Federation context (if available)
            "federation_node": event.federation_context.get("node_id", "local"),
            "federation_region": event.federation_context.get("region", "default"),
            # Rolling statistics
            "stats": stats,
            # Alerts
            "alerts": alerts
        }

        # Write to JSONL
        with self.telemetry_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(telemetry_entry) + "\n")

    def _compute_statistics(self) -> Dict[str, Any]:
        """Compute rolling window statistics."""
        if len(self.latency_window) == 0:
            return {}

        # Latency percentiles
        sorted_latencies = sorted(self.latency_window)
        p50_idx = int(len(sorted_latencies) * 0.50)
        p95_idx = int(len(sorted_latencies) * 0.95)
        p99_idx = int(len(sorted_latencies) * 0.99)

        # Queue depth statistics
        avg_queue_depth = sum(self.queue_depth_window) / len(self.queue_depth_window)
        max_queue_depth = max(self.queue_depth_window)

        # Throughput
        uptime = time.time() - self.start_time
        throughput = self.total_events / uptime if uptime > 0 else 0

        # Proof rate (Phase 1.5+)
        proof_stream_duration = time.time() - self.proof_stream_start
        proof_rate_per_sec = self.total_events / proof_stream_duration if proof_stream_duration > 0 else 0

        return {
            "latency_p50_ms": round(sorted_latencies[p50_idx], 2),
            "latency_p95_ms": round(sorted_latencies[p95_idx], 2),
            "latency_p99_ms": round(sorted_latencies[p99_idx], 2),
            "avg_queue_depth": round(avg_queue_depth, 2),
            "max_queue_depth": max_queue_depth,
            "throughput_events_per_sec": round(throughput, 2),
            "proof_rate_per_sec": round(proof_rate_per_sec, 2),  # NEW: Proof stream rate
            "failure_rate_percent": round(self.failed_events / self.total_events * 100, 2) if self.total_events > 0 else 0
        }

    def _check_alerts(self, stats: Dict[str, Any]) -> List[str]:
        """Check alert thresholds."""
        alerts = []

        # Alert: High queue depth
        if stats.get("max_queue_depth", 0) > self.alert_threshold_queue_depth:
            alert = f"HIGH_QUEUE_DEPTH: {stats['max_queue_depth']} > {self.alert_threshold_queue_depth}"
            if alert not in self.alerts_fired:
                alerts.append(alert)
                self.alerts_fired.append(alert)

        # Alert: High latency
        if stats.get("latency_p95_ms", 0) > self.alert_threshold_latency_ms:
            alert = f"HIGH_LATENCY_P95: {stats['latency_p95_ms']}ms > {self.alert_threshold_latency_ms}ms"
            if alert not in self.alerts_fired:
                alerts.append(alert)
                self.alerts_fired.append(alert)

        # Alert: High failure rate
        if stats.get("failure_rate_percent", 0) > 5.0:
            alert = f"HIGH_FAILURE_RATE: {stats['failure_rate_percent']}% > 5%"
            if alert not in self.alerts_fired:
                alerts.append(alert)
                self.alerts_fired.append(alert)

        return alerts

    def get_summary(self) -> Dict[str, Any]:
        """Get telemetry summary."""
        stats = self._compute_statistics()

        return {
            "total_events": self.total_events,
            "failed_events": self.failed_events,
            "uptime_sec": round(time.time() - self.start_time, 2),
            "statistics": stats,
            "alerts_fired": self.alerts_fired
        }


# Example usage
if __name__ == "__main__":
    import sys
    from pathlib import Path

    # Add event bus to path
    ROOT = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(ROOT / "02_audit_logging" / "interfaces"))
    sys.path.insert(0, str(ROOT / "02_audit_logging" / "event_bus"))

    from audit_event_emitter import AuditEvent, EventType, EventSeverity
    from in_memory_bus import InMemoryAuditBus

    print("Testing Audit Telemetry Sink")
    print("=" * 70)

    # Create telemetry sink
    telemetry = AuditTelemetrySink()

    # Create event bus with metrics callback
    bus = InMemoryAuditBus(
        max_queue_size=1000,
        worker_threads=2,
        metrics_callback=telemetry.on_event_processed
    )

    # Emit test events
    for i in range(10):
        event = AuditEvent(
            event_id=f"telemetry_test_{i}",
            timestamp=datetime.utcnow(),
            source_module="test/telemetry",
            event_type=EventType.HEALTH_CHECK,
            severity=EventSeverity.INFO,
            data={"index": i},
            requires_worm=False,
            federation_context={
                "node_id": "node_001",
                "region": "eu-west-1"
            }
        )

        bus.emit(event)

    # Flush
    bus.flush(timeout_ms=5000)

    # Get summary
    summary = telemetry.get_summary()

    print(f"Total Events: {summary['total_events']}")
    print(f"Failed Events: {summary['failed_events']}")
    print(f"Uptime: {summary['uptime_sec']} sec")
    print()
    print("Statistics:")
    for key, value in summary['statistics'].items():
        print(f"  {key}: {value}")
    print()
    print(f"Alerts Fired: {len(summary['alerts_fired'])}")

    print("=" * 70)
    print("[OK] Telemetry Sink Test Complete")

    # Shutdown
    bus.shutdown(timeout_ms=5000)
