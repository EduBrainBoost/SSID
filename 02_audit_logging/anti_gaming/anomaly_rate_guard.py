#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
anomaly_rate_guard.py – Rate Limiting & Anomaly Detection
Autor: edubrainboost ©2025 MIT License

Detects rate limit violations (botting/spam) in identity events.
Read-only scan with deterministic JSONL logging.

Exit Codes:
  0 - PASS (no rate violations)
  2 - FAIL (rate limits exceeded)
"""

import sys
import json
import yaml
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List
from collections import defaultdict


ROOT = Path(__file__).resolve().parents[2]
POLICY_PATH = ROOT / "23_compliance" / "policies" / "anti_gaming_policy.yaml"
EVENTS_PATH = ROOT / "02_audit_logging" / "evidence" / "identity_events.jsonl"
LOG_PATH = ROOT / "02_audit_logging" / "logs" / "anti_gaming_anomaly_rate.jsonl"


def load_policy() -> Dict:
    """Load anti-gaming policy configuration."""
    if not POLICY_PATH.exists():
        return {
            "rules": {
                "anomaly_rate": {
                    "rate_limits": {
                        "events_per_minute_per_did": 10,
                        "events_per_hour_per_did": 500
                    },
                    "burst_limits": {"per_5s": 5},
                    "severity": "high"
                }
            }
        }

    with open(POLICY_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_identity_events() -> List[Dict]:
    """Load identity events from JSONL."""
    if not EVENTS_PATH.exists():
        return []

    events = []
    with open(EVENTS_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    raise NotImplementedError("TODO: Implement this block")

    return events


def detect_rate_violations(
    events: List[Dict],
    events_per_minute: int,
    events_per_hour: int,
    burst_per_5s: int
) -> List[Dict]:
    """Detect rate limit violations per DID."""
    # Group events by DID
    did_events = defaultdict(list)

    for event in events:
        did = event.get("did")
        timestamp = event.get("ts") or event.get("timestamp")

        if did and timestamp:
            try:
                ts = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                did_events[did].append(ts)
            except (ValueError, AttributeError):
                raise NotImplementedError("TODO: Implement this block")

    # Check rate limits
    violations = []

    for did, timestamps in did_events.items():
        if len(timestamps) < 2:
            continue

        timestamps.sort()

        # Check burst (5 second window)
        for i in range(len(timestamps) - burst_per_5s + 1):
            window_end = timestamps[i] + timedelta(seconds=5)
            events_in_burst = sum(1 for ts in timestamps[i:] if ts <= window_end)

            if events_in_burst > burst_per_5s:
                violations.append({
                    "did": did,
                    "type": "burst",
                    "window": "5s",
                    "events": events_in_burst,
                    "limit": burst_per_5s,
                    "start_time": timestamps[i].isoformat()
                })
                break  # One violation per DID per check

        # Check per-minute rate
        for i in range(len(timestamps) - events_per_minute + 1):
            window_end = timestamps[i] + timedelta(minutes=1)
            events_in_minute = sum(1 for ts in timestamps[i:] if ts <= window_end)

            if events_in_minute > events_per_minute:
                violations.append({
                    "did": did,
                    "type": "per_minute",
                    "window": "1m",
                    "events": events_in_minute,
                    "limit": events_per_minute,
                    "start_time": timestamps[i].isoformat()
                })
                break

        # Check per-hour rate
        for i in range(len(timestamps) - events_per_hour + 1):
            window_end = timestamps[i] + timedelta(hours=1)
            events_in_hour = sum(1 for ts in timestamps[i:] if ts <= window_end)

            if events_in_hour > events_per_hour:
                violations.append({
                    "did": did,
                    "type": "per_hour",
                    "window": "1h",
                    "events": events_in_hour,
                    "limit": events_per_hour,
                    "start_time": timestamps[i].isoformat()
                })
                break

    return violations


def write_audit_log(
    status: str,
    offenders: List[Dict],
    limits: Dict,
    policy_version: str
) -> None:
    """Write deterministic audit log entry."""
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    entry = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "component": "anti_gaming",
        "check": "anomaly_rate",
        "status": status,
        "offenders": len(offenders),
        "violations": offenders,
        "limits": limits,
        "policy_version": policy_version
    }

    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, sort_keys=True) + "\n")


def main() -> int:
    """Main execution."""
    print("SSID Anomaly Rate Guard")
    print("=" * 60)

    # Load policy
    policy = load_policy()
    rules = policy.get("rules", {}).get("anomaly_rate", {})
    rate_limits = rules.get("rate_limits", {"events_per_minute_per_did": 10})
    burst_limits = rules.get("burst_limits", {"per_5s": 5})
    policy_version = policy.get("metadata", {}).get("version", "1.0.0")

    print(f"Policy Version: {policy_version}")
    print(f"Rate Limits: {rate_limits}")
    print(f"Burst Limits: {burst_limits}")
    print()

    # Load events
    print("Loading identity events...")
    events = load_identity_events()
    print(f"Events loaded: {len(events)}")

    if len(events) == 0:
        print("No events found - creating placeholder...")
        EVENTS_PATH.parent.mkdir(parents=True, exist_ok=True)
        sample_events = [
            {"did": "did:ssid:test1", "ts": datetime.utcnow().isoformat() + "Z"},
            {"did": "did:ssid:test2", "ts": datetime.utcnow().isoformat() + "Z"}
        ]
        with open(EVENTS_PATH, "w", encoding="utf-8") as f:
            for event in sample_events:
                f.write(json.dumps(event) + "\n")
        events = sample_events

    print()

    # Detect violations
    print("Analyzing rate limits...")
    violations = detect_rate_violations(
        events,
        rate_limits.get("events_per_minute_per_did", 10),
        rate_limits.get("events_per_hour_per_did", 500),
        burst_limits.get("per_5s", 5)
    )

    status = "PASS" if len(violations) == 0 else "FAIL"

    # Write audit log
    write_audit_log(
        status,
        violations,
        {"rate_limits": rate_limits, "burst_limits": burst_limits},
        policy_version
    )

    # Report results
    print()
    print("=" * 60)
    print(f"Status: {status}")
    print(f"Violations: {len(violations)}")

    if violations:
        print("\nRate Limit Violations:")
        for v in violations:
            print(f"  - DID: {v['did']}")
            print(f"    Type: {v['type']} ({v['window']})")
            print(f"    Events: {v['events']} (limit: {v['limit']})")

    print()
    print(f"Audit log: {LOG_PATH}")

    return 0 if status == "PASS" else 2


if __name__ == "__main__":
    sys.exit(main())
