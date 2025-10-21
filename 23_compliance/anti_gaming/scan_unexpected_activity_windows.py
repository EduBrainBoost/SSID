#!/usr/bin/env python3
"""
scan_unexpected_activity_windows.py

Anti-Gaming Tool: Detect off-hours batch activity and bot-like behavior
Analyzes audit logs for suspicious activity patterns including:
- Batch operations during off-hours (3am local time)
- Superhuman operation speed (milliseconds between actions)
- Weekend/holiday batch processing
- Anomalous activity patterns using statistical methods

MUST-002-ANTI-GAMING compliance requirement
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from collections import defaultdict
import statistics

class ActivityWindowScanner:
    """Scans audit logs for unexpected activity patterns indicating automation/gaming."""

    def __init__(self, audit_log_dir: str = "02_audit_logging/logs"):
        """
        Initialize scanner with audit log directory.

        Args:
            audit_log_dir: Path to directory containing audit logs
        """
        self.audit_log_dir = Path(audit_log_dir)
        self.violations: List[Dict[str, Any]] = []

        # Thresholds for anomaly detection
        self.off_hours_start = 0  # 12am
        self.off_hours_end = 6    # 6am
        self.min_action_interval_ms = 100  # Minimum human reaction time
        self.max_ops_per_hour_normal = 500  # Normal user activity ceiling
        self.suspicious_batch_size = 10  # Consecutive identical actions

    def scan_all_logs(self) -> tuple[bool, List[Dict[str, Any]]]:
        """
        Scan all audit logs for suspicious activity patterns.

        Returns:
            Tuple of (is_suspicious, violations_list)
        """
        if not self.audit_log_dir.exists():
            return False, []

        # Find all audit log files
        log_files = list(self.audit_log_dir.glob("**/*.json"))
        if not log_files:
            log_files = list(self.audit_log_dir.glob("**/*.jsonl"))

        # Group events by identity/tenant
        activity_by_entity = defaultdict(list)

        for log_file in log_files:
            events = self._load_log_file(log_file)
            for event in events:
                entity_id = event.get("user_id") or event.get("identity_id") or event.get("tenant_id") or "unknown"
                activity_by_entity[entity_id].append(event)

        # Analyze each entity's activity patterns
        for entity_id, events in activity_by_entity.items():
            self._analyze_entity_activity(entity_id, events)

        return len(self.violations) > 0, self.violations

    def _load_log_file(self, log_file: Path) -> List[Dict[str, Any]]:
        """Load events from a log file (JSON or JSONL format)."""
        events = []
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content:
                    return []

                # Try JSON array first
                try:
                    data = json.loads(content)
                    if isinstance(data, list):
                        events = data
                    elif isinstance(data, dict):
                        events = [data]
                except json.JSONDecodeError:
                    # Try JSONL format (one JSON object per line)
                    for line in content.split('\n'):
                        if line.strip():
                            try:
                                events.append(json.loads(line))
                            except json.JSONDecodeError:
                                continue
        except Exception:
            raise NotImplementedError("TODO: Implement this block")

        return events

    def _analyze_entity_activity(self, entity_id: str, events: List[Dict[str, Any]]) -> None:
        """Analyze activity patterns for a single entity."""
        if len(events) < 2:
            return

        # Sort events by timestamp
        sorted_events = sorted(events, key=lambda e: self._parse_timestamp(e.get("timestamp", "")))

        # Check 1: Off-hours activity
        self._check_off_hours_activity(entity_id, sorted_events)

        # Check 2: Superhuman speed
        self._check_superhuman_speed(entity_id, sorted_events)

        # Check 3: Batch operations
        self._check_batch_operations(entity_id, sorted_events)

        # Check 4: Unusual activity rate
        self._check_activity_rate(entity_id, sorted_events)

    def _parse_timestamp(self, timestamp_str: str) -> datetime:
        """Parse ISO 8601 timestamp string, always returning timezone-naive datetime."""
        if not timestamp_str:
            return datetime.min

        try:
            # Handle various ISO formats
            if 'T' in timestamp_str:
                # Remove timezone info to avoid comparison issues
                timestamp_str = timestamp_str.replace('Z', '').split('+')[0].split('-00:00')[0]
                try:
                    return datetime.fromisoformat(timestamp_str)
                except:
                    raise NotImplementedError("TODO: Implement this block")

            # Try simple ISO format
            try:
                dt = datetime.fromisoformat(timestamp_str)
                # Strip timezone if present
                if dt.tzinfo is not None:
                    dt = dt.replace(tzinfo=None)
                return dt
            except:
                return datetime.min
        except:
            return datetime.min

    def _check_off_hours_activity(self, entity_id: str, events: List[Dict[str, Any]]) -> None:
        """Detect batch operations during off-hours (12am-6am)."""
        off_hours_events = []

        for event in events:
            timestamp = self._parse_timestamp(event.get("timestamp", ""))
            if timestamp == datetime.min:
                continue

            hour = timestamp.hour
            if self.off_hours_start <= hour < self.off_hours_end:
                off_hours_events.append(event)

        # If >20% of activity is in off-hours, flag it
        if len(off_hours_events) > len(events) * 0.2:
            self.violations.append({
                "entity_id": entity_id,
                "violation_type": "off_hours_activity",
                "severity": "high",
                "description": f"{len(off_hours_events)}/{len(events)} events occurred during off-hours (12am-6am)",
                "evidence": {
                    "total_events": len(events),
                    "off_hours_events": len(off_hours_events),
                    "percentage": round(len(off_hours_events) / len(events) * 100, 2)
                }
            })

    def _check_superhuman_speed(self, entity_id: str, events: List[Dict[str, Any]]) -> None:
        """Detect operations happening faster than human reaction time."""
        suspicious_pairs = []

        for i in range(len(events) - 1):
            t1 = self._parse_timestamp(events[i].get("timestamp", ""))
            t2 = self._parse_timestamp(events[i + 1].get("timestamp", ""))

            if t1 == datetime.min or t2 == datetime.min:
                continue

            interval_ms = (t2 - t1).total_seconds() * 1000

            if 0 < interval_ms < self.min_action_interval_ms:
                suspicious_pairs.append({
                    "event1": events[i].get("action", "unknown"),
                    "event2": events[i + 1].get("action", "unknown"),
                    "interval_ms": round(interval_ms, 2)
                })

        if len(suspicious_pairs) > 3:  # Multiple superhuman-speed actions
            self.violations.append({
                "entity_id": entity_id,
                "violation_type": "superhuman_speed",
                "severity": "critical",
                "description": f"Detected {len(suspicious_pairs)} actions faster than human reaction time (<{self.min_action_interval_ms}ms)",
                "evidence": {
                    "suspicious_pairs": suspicious_pairs[:5]  # Show first 5 examples
                }
            })

    def _check_batch_operations(self, entity_id: str, events: List[Dict[str, Any]]) -> None:
        """Detect repetitive batch operations (same action repeated rapidly)."""
        consecutive_actions = []
        current_action = None
        current_count = 0

        for event in events:
            action = event.get("action") or event.get("event_type") or event.get("type")

            if action == current_action:
                current_count += 1
            else:
                if current_count >= self.suspicious_batch_size:
                    consecutive_actions.append({
                        "action": current_action,
                        "count": current_count
                    })
                current_action = action
                current_count = 1

        # Check last sequence
        if current_count >= self.suspicious_batch_size:
            consecutive_actions.append({
                "action": current_action,
                "count": current_count
            })

        if consecutive_actions:
            self.violations.append({
                "entity_id": entity_id,
                "violation_type": "batch_operations",
                "severity": "medium",
                "description": f"Detected {len(consecutive_actions)} sequences of repetitive actions",
                "evidence": {
                    "sequences": consecutive_actions
                }
            })

    def _check_activity_rate(self, entity_id: str, events: List[Dict[str, Any]]) -> None:
        """Detect unusually high activity rates (ops per hour)."""
        if len(events) < 10:
            return

        # Calculate activity rate in 1-hour windows
        hourly_rates = []

        events_with_time = [
            (e, self._parse_timestamp(e.get("timestamp", "")))
            for e in events
        ]
        events_with_time = [
            (e, t) for e, t in events_with_time
            if t != datetime.min
        ]

        if not events_with_time:
            return

        events_with_time.sort(key=lambda x: x[1])

        for i, (event, timestamp) in enumerate(events_with_time):
            window_end = timestamp + timedelta(hours=1)
            ops_in_window = sum(
                1 for e, t in events_with_time[i:]
                if t <= window_end
            )
            hourly_rates.append(ops_in_window)

        if not hourly_rates:
            return

        max_rate = max(hourly_rates)
        avg_rate = statistics.mean(hourly_rates)

        if max_rate > self.max_ops_per_hour_normal:
            self.violations.append({
                "entity_id": entity_id,
                "violation_type": "high_activity_rate",
                "severity": "high",
                "description": f"Abnormally high activity rate detected",
                "evidence": {
                    "max_ops_per_hour": max_rate,
                    "avg_ops_per_hour": round(avg_rate, 2),
                    "threshold": self.max_ops_per_hour_normal
                }
            })

    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive report of findings."""
        violations_by_severity = defaultdict(list)
        for v in self.violations:
            violations_by_severity[v["severity"]].append(v)

        return {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "tool": "scan_unexpected_activity_windows",
            "version": "1.0.0",
            "status": "FAIL" if self.violations else "PASS",
            "summary": {
                "total_violations": len(self.violations),
                "critical": len(violations_by_severity["critical"]),
                "high": len(violations_by_severity["high"]),
                "medium": len(violations_by_severity["medium"]),
                "low": len(violations_by_severity["low"])
            },
            "violations": self.violations,
            "thresholds": {
                "off_hours_window": f"{self.off_hours_start}:00-{self.off_hours_end}:00",
                "min_action_interval_ms": self.min_action_interval_ms,
                "max_ops_per_hour_normal": self.max_ops_per_hour_normal,
                "suspicious_batch_size": self.suspicious_batch_size
            }
        }

def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Scan audit logs for unexpected activity windows (bot detection)"
    )
    parser.add_argument(
        "--audit-dir",
        default="02_audit_logging/logs",
        help="Directory containing audit logs"
    )
    parser.add_argument(
        "--output",
        help="Output file for report (default: stdout)"
    )

    args = parser.parse_args()

    scanner = ActivityWindowScanner(audit_log_dir=args.audit_dir)
    is_suspicious, violations = scanner.scan_all_logs()

    report = scanner.generate_report()

    # Output report
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"Report written to {args.output}")
    else:
        print(json.dumps(report, indent=2))

    # Exit with appropriate code
    sys.exit(1 if is_suspicious else 0)

if __name__ == "__main__":
    main()
