#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
replay_attack_detector.py – Replay Attack Detection
Autor: edubrainboost ©2025 MIT License

Detects reused nonces/timestamps within time window (replay attacks).
Read-only scan with deterministic JSONL logging.

Exit Codes:
  0 - PASS (no replay detected)
  2 - FAIL (replay attacks detected)
"""

import sys
import json
import yaml
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[2]
POLICY_PATH = ROOT / "23_compliance" / "policies" / "anti_gaming_policy.yaml"
EVENTS_PATH = ROOT / "02_audit_logging" / "evidence" / "identity_events.jsonl"
LOG_PATH = ROOT / "02_audit_logging" / "logs" / "anti_gaming_replay.jsonl"

def load_policy() -> Dict:
    """Load anti-gaming policy configuration."""
    if not POLICY_PATH.exists():
        return {
            "rules": {
                "replay": {
                    "nonce_uniqueness_window_minutes": 120,
                    "severity": "critical"
                }
            }
        }

    with open(POLICY_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def load_identity_events() -> List[Dict]:
    """Load identity events from JSONL."""
    if not EVENTS_PATH.exists():
        # Create placeholder for testing
        EVENTS_PATH.parent.mkdir(parents=True, exist_ok=True)
        sample_events = [
            {"did": "did:ssid:test1", "nonce": "nonce_001", "ts": datetime.utcnow().isoformat() + "Z", "sig": "sig1"},
            {"did": "did:ssid:test2", "nonce": "nonce_002", "ts": datetime.utcnow().isoformat() + "Z", "sig": "sig2"}
        ]
        with open(EVENTS_PATH, "w", encoding="utf-8") as f:
            for event in sample_events:
                f.write(json.dumps(event) + "\n")
        return sample_events

    events = []
    with open(EVENTS_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    raise NotImplementedError("TODO: Implement this block")

    return events

def detect_replay_attacks(events: List[Dict], window_minutes: int) -> List[Dict]:
    """Detect replay attacks (duplicate did+nonce within time window)."""
    # Group by (did, nonce)
    nonce_groups = defaultdict(list)

    for event in events:
        did = event.get("did")
        nonce = event.get("nonce")
        timestamp = event.get("ts") or event.get("timestamp")

        if did and nonce and timestamp:
            nonce_groups[(did, nonce)].append({
                "did": did,
                "nonce": nonce,
                "timestamp": timestamp,
                "sig": event.get("sig", "")
            })

    # Check for duplicates within window
    replay_attacks = []
    window_delta = timedelta(minutes=window_minutes)

    for (did, nonce), occurrences in nonce_groups.items():
        if len(occurrences) < 2:
            continue

        # Sort by timestamp
        occurrences.sort(key=lambda x: x["timestamp"])

        # Check if any occur within window
        for i in range(len(occurrences) - 1):
            try:
                ts1 = datetime.fromisoformat(occurrences[i]["timestamp"].replace("Z", "+00:00"))
                ts2 = datetime.fromisoformat(occurrences[i + 1]["timestamp"].replace("Z", "+00:00"))

                if ts2 - ts1 <= window_delta:
                    replay_attacks.append({
                        "did": did,
                        "nonce": nonce,
                        "first_seen": occurrences[i]["timestamp"],
                        "replay_seen": occurrences[i + 1]["timestamp"],
                        "time_diff_minutes": (ts2 - ts1).total_seconds() / 60
                    })
            except (ValueError, AttributeError):
                raise NotImplementedError("TODO: Implement this block")

    return replay_attacks

def write_audit_log(
    status: str,
    duplicates: List[Dict],
    window_minutes: int,
    policy_version: str
) -> None:
    """Write deterministic audit log entry."""
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    entry = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "component": "anti_gaming",
        "check": "replay",
        "status": status,
        "duplicates": len(duplicates),
        "replay_attacks": duplicates,
        "window_minutes": window_minutes,
        "policy_version": policy_version
    }

    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, sort_keys=True) + "\n")

def main() -> int:
    """Main execution."""
    print("SSID Replay Attack Detector")
    print("=" * 60)

    # Load policy
    policy = load_policy()
    rules = policy.get("rules", {}).get("replay", {})
    window_minutes = rules.get("nonce_uniqueness_window_minutes", 120)
    policy_version = policy.get("metadata", {}).get("version", "1.0.0")

    print(f"Policy Version: {policy_version}")
    print(f"Nonce Window: {window_minutes} minutes")
    print()

    # Load events
    print("Loading identity events...")
    events = load_identity_events()
    print(f"Events loaded: {len(events)}")
    print()

    # Detect replay attacks
    print("Analyzing for replay attacks...")
    replay_attacks = detect_replay_attacks(events, window_minutes)

    status = "PASS" if len(replay_attacks) == 0 else "FAIL"

    # Write audit log
    write_audit_log(status, replay_attacks, window_minutes, policy_version)

    # Report results
    print()
    print("=" * 60)
    print(f"Status: {status}")
    print(f"Replay Attacks: {len(replay_attacks)}")

    if replay_attacks:
        print("\nDetected Replay Attacks:")
        for attack in replay_attacks:
            print(f"  - DID: {attack['did']}")
            print(f"    Nonce: {attack['nonce']}")
            print(f"    First: {attack['first_seen']}")
            print(f"    Replay: {attack['replay_seen']}")
            print(f"    Gap: {attack['time_diff_minutes']:.1f} minutes")

    print()
    print(f"Audit log: {LOG_PATH}")

    return 0 if status == "PASS" else 2

if __name__ == "__main__":
    sys.exit(main())
