#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
health_check_telemetry.py – Health Check Response Time Telemetry
Autor: edubrainboost ©2025 MIT License

Collects P50/P95/P99 response times for health check endpoints to
objectively measure performance gains from consolidation.

Features:
- Response time collection
- P50/P95/P99 percentile calculation
- Historical trending
- Comparison before/after consolidation
- Quarterly report integration

Usage:
    from observability.health_check_telemetry import HealthCheckTelemetry

    telemetry = HealthCheckTelemetry()
    telemetry.record_health_check("shard_01", response_time_ms=5.2)
    stats = telemetry.get_statistics()
"""

import json
import time
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional
from collections import defaultdict
import statistics


class HealthCheckTelemetry:
    """Collect and analyze health check response time metrics."""

    def __init__(self, root_dir: Optional[Path] = None):
        if root_dir is None:
            root_dir = Path(__file__).resolve().parents[1]

        self.root = root_dir
        self.telemetry_dir = root_dir / "17_observability" / "metrics" / "health_checks"
        self.telemetry_dir.mkdir(parents=True, exist_ok=True)

        self.telemetry_file = self.telemetry_dir / "response_times.jsonl"

        # In-memory storage for current session
        self.measurements: Dict[str, List[float]] = defaultdict(list)

    def record_health_check(
        self,
        shard_id: str,
        response_time_ms: float,
        status: str = "healthy",
        timestamp: Optional[str] = None
    ) -> None:
        """
        Record a health check response time measurement.

        Args:
            shard_id: Shard identifier (e.g., "01_identitaet_personen")
            response_time_ms: Response time in milliseconds
            status: Health check status ("healthy", "degraded", "unhealthy")
            timestamp: ISO8601 timestamp (default: now)
        """
        if timestamp is None:
            timestamp = datetime.now(timezone.utc).isoformat()

        # Add to in-memory storage
        self.measurements[shard_id].append(response_time_ms)

        # Append to JSONL file for persistent storage
        entry = {
            "timestamp": timestamp,
            "shard_id": shard_id,
            "response_time_ms": response_time_ms,
            "status": status
        }

        with open(self.telemetry_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

    def get_percentiles(self, values: List[float]) -> Dict[str, float]:
        """
        Calculate P50, P95, P99 percentiles.

        Args:
            values: List of measurements

        Returns:
            Dict with p50, p95, p99 keys
        """
        if not values:
            return {"p50": 0.0, "p95": 0.0, "p99": 0.0}

        sorted_values = sorted(values)
        n = len(sorted_values)

        def percentile(p: float) -> float:
            k = (n - 1) * p
            f = int(k)
            c = k - f
            if f + 1 < n:
                return sorted_values[f] * (1 - c) + sorted_values[f + 1] * c
            else:
                return sorted_values[f]

        return {
            "p50": percentile(0.50),
            "p95": percentile(0.95),
            "p99": percentile(0.99)
        }

    def get_statistics(self, shard_id: Optional[str] = None) -> Dict:
        """
        Get statistics for health check response times.

        Args:
            shard_id: Specific shard ID (None for all shards)

        Returns:
            Dict with statistics
        """
        if shard_id:
            values = self.measurements.get(shard_id, [])
            shards_data = {shard_id: values}
        else:
            shards_data = self.measurements

        stats = {}

        for shard, values in shards_data.items():
            if not values:
                continue

            percentiles = self.get_percentiles(values)

            stats[shard] = {
                "count": len(values),
                "min": min(values),
                "max": max(values),
                "mean": statistics.mean(values),
                "median": statistics.median(values),
                "stdev": statistics.stdev(values) if len(values) > 1 else 0.0,
                "p50": percentiles["p50"],
                "p95": percentiles["p95"],
                "p99": percentiles["p99"]
            }

        return stats

    def load_historical_data(
        self,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None
    ) -> Dict[str, List[float]]:
        """
        Load historical telemetry data from JSONL file.

        Args:
            since: Start datetime (default: all history)
            until: End datetime (default: now)

        Returns:
            Dict mapping shard_id to list of response times
        """
        if not self.telemetry_file.exists():
            return {}

        historical = defaultdict(list)

        with open(self.telemetry_file, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue

                try:
                    entry = json.loads(line)
                    timestamp = datetime.fromisoformat(entry["timestamp"].replace("Z", "+00:00"))

                    # Filter by time range
                    if since and timestamp < since:
                        continue
                    if until and timestamp > until:
                        continue

                    shard_id = entry["shard_id"]
                    response_time = entry["response_time_ms"]

                    historical[shard_id].append(response_time)

                except (json.JSONDecodeError, KeyError, ValueError):
                    continue

        return dict(historical)

    def compare_periods(
        self,
        before_date: datetime,
        after_date: datetime
    ) -> Dict:
        """
        Compare health check performance before and after a date (e.g., consolidation).

        Args:
            before_date: Cutoff date for "before" period
            after_date: Start date for "after" period

        Returns:
            Dict with comparison statistics
        """
        # Load data for both periods
        before_data = self.load_historical_data(until=before_date)
        after_data = self.load_historical_data(since=after_date)

        comparison = {}

        # Get all unique shards
        all_shards = set(before_data.keys()) | set(after_data.keys())

        for shard in all_shards:
            before_values = before_data.get(shard, [])
            after_values = after_data.get(shard, [])

            if not before_values or not after_values:
                continue

            before_stats = self.get_percentiles(before_values)
            after_stats = self.get_percentiles(after_values)

            # Calculate improvements
            p95_improvement = ((before_stats["p95"] - after_stats["p95"]) / before_stats["p95"] * 100
                              if before_stats["p95"] > 0 else 0)

            comparison[shard] = {
                "before": before_stats,
                "after": after_stats,
                "improvement": {
                    "p50_delta_ms": before_stats["p50"] - after_stats["p50"],
                    "p95_delta_ms": before_stats["p95"] - after_stats["p95"],
                    "p99_delta_ms": before_stats["p99"] - after_stats["p99"],
                    "p95_improvement_pct": p95_improvement
                }
            }

        return comparison

    def generate_quarterly_report(self, quarter: str) -> Dict:
        """
        Generate quarterly telemetry report.

        Args:
            quarter: Quarter identifier (e.g., "2025-Q4")

        Returns:
            Quarterly report dict
        """
        # Load all data
        all_data = self.load_historical_data()

        # Calculate overall statistics
        all_values = []
        for values in all_data.values():
            all_values.extend(values)

        overall_stats = self.get_percentiles(all_values) if all_values else {}

        # Per-shard statistics
        shard_stats = {}
        for shard, values in all_data.items():
            if values:
                shard_stats[shard] = self.get_percentiles(values)

        report = {
            "quarter": quarter,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "overall_statistics": {
                "total_measurements": len(all_values),
                "unique_shards": len(all_data),
                "p50_ms": overall_stats.get("p50", 0),
                "p95_ms": overall_stats.get("p95", 0),
                "p99_ms": overall_stats.get("p99", 0)
            },
            "per_shard_statistics": shard_stats,
            "performance_assessment": self._assess_performance(overall_stats)
        }

        return report

    def _assess_performance(self, stats: Dict) -> str:
        """
        Assess performance based on P95 latency.

        Args:
            stats: Percentile statistics

        Returns:
            Performance rating
        """
        p95 = stats.get("p95", 0)

        if p95 < 5:
            return "EXCELLENT"
        elif p95 < 10:
            return "GOOD"
        elif p95 < 20:
            return "ACCEPTABLE"
        else:
            return "NEEDS_IMPROVEMENT"


# Decorator for automatic telemetry collection
def measure_health_check(telemetry: HealthCheckTelemetry):
    """
    Decorator to automatically measure health check response times.

    Usage:
        telemetry = HealthCheckTelemetry()

        @measure_health_check(telemetry)
        def my_health_check(shard_id: str):
            # ... health check logic
            return {"status": "healthy"}
    """
    def decorator(func):
        def wrapper(shard_id: str, *args, **kwargs):
            start_time = time.perf_counter()

            try:
                result = func(shard_id, *args, **kwargs)
                status = result.get("status", "healthy") if isinstance(result, dict) else "healthy"
            except Exception:
                status = "unhealthy"
                raise
            finally:
                end_time = time.perf_counter()
                response_time_ms = (end_time - start_time) * 1000

                telemetry.record_health_check(
                    shard_id=shard_id,
                    response_time_ms=response_time_ms,
                    status=status
                )

            return result

        return wrapper
    return decorator


def main():
    """Example usage and testing."""
    telemetry = HealthCheckTelemetry()

    print("Health Check Telemetry - Example Usage")
    print("=" * 70)
    print()

    # Simulate some measurements
    shards = ["01_identitaet_personen", "02_dokumente_nachweise", "03_zugang_berechtigungen"]

    print("Recording sample measurements...")
    for shard in shards:
        for _ in range(10):
            # Simulate response times (base class should be faster)
            response_time = 3.0 + (hash(shard) % 10) / 10.0
            telemetry.record_health_check(shard, response_time)

    print()
    print("Statistics:")
    stats = telemetry.get_statistics()

    for shard, shard_stats in stats.items():
        print(f"\n{shard}:")
        print(f"  P50: {shard_stats['p50']:.2f}ms")
        print(f"  P95: {shard_stats['p95']:.2f}ms")
        print(f"  P99: {shard_stats['p99']:.2f}ms")

    print()
    print(f"Telemetry file: {telemetry.telemetry_file}")


if __name__ == "__main__":
    main()
