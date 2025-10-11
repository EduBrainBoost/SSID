#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
time_skew_analyzer.py – Timestamp Skew Detection
Autor: edubrainboost ©2025 MIT License

Detects implausible timestamp skews (backdating, future-dating).
Read-only scan with deterministic JSONL logging.

Exit Codes:
  0 - PASS (skew within threshold)
  2 - FAIL (skew exceeds threshold)
"""

import sys
import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List


ROOT = Path(__file__).resolve().parents[2]
POLICY_PATH = ROOT / "23_compliance" / "policies" / "anti_gaming_policy.yaml"
LOG_PATH = ROOT / "02_audit_logging" / "logs" / "anti_gaming_time_skew.jsonl"


def load_policy() -> Dict:
    """Load anti-gaming policy configuration."""
    if not POLICY_PATH.exists():
        return {
            "rules": {
                "time_skew": {
                    "max_allowed_skew_seconds": 300,
                    "severity": "high"
                }
            }
        }

    with open(POLICY_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def find_jsonl_files() -> List[Path]:
    """Find all JSONL files in audit/evidence directories."""
    jsonl_files = []

    search_dirs = [
        ROOT / "02_audit_logging" / "logs",
        ROOT / "02_audit_logging" / "evidence"
    ]

    for search_dir in search_dirs:
        if search_dir.exists():
            jsonl_files.extend(search_dir.rglob("*.jsonl"))

    return sorted(jsonl_files)


def extract_timestamps(jsonl_file: Path) -> List[Dict]:
    """Extract timestamps from JSONL file."""
    timestamps = []

    if not jsonl_file.exists():
        return timestamps

    try:
        with open(jsonl_file, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                if not line.strip():
                    continue

                try:
                    entry = json.loads(line)
                    # Try common timestamp fields
                    ts_value = entry.get("timestamp") or entry.get("ts")

                    if ts_value:
                        timestamps.append({
                            "file": str(jsonl_file.relative_to(ROOT)),
                            "line": line_num,
                            "timestamp": ts_value
                        })

                except json.JSONDecodeError:
                    raise NotImplementedError("TODO: Implement this block")

    except OSError:
        raise NotImplementedError("TODO: Implement this block")

    return timestamps


def analyze_skew(timestamps: List[Dict], max_skew_seconds: int) -> tuple[int, List[Dict]]:
    """Analyze timestamps for skew violations."""
    if len(timestamps) < 2:
        return 0, []

    # Sort by timestamp
    try:
        timestamps_sorted = sorted(
            timestamps,
            key=lambda x: datetime.fromisoformat(x["timestamp"].replace("Z", "+00:00"))
        )
    except (ValueError, AttributeError):
        return 0, []

    violations = []
    max_skew = 0

    for i in range(len(timestamps_sorted) - 1):
        try:
            ts1_str = timestamps_sorted[i]["timestamp"]
            ts2_str = timestamps_sorted[i + 1]["timestamp"]

            ts1 = datetime.fromisoformat(ts1_str.replace("Z", "+00:00"))
            ts2 = datetime.fromisoformat(ts2_str.replace("Z", "+00:00"))

            skew_seconds = abs((ts2 - ts1).total_seconds())

            if skew_seconds > max_skew:
                max_skew = int(skew_seconds)

            if skew_seconds > max_skew_seconds:
                violations.append({
                    "file1": timestamps_sorted[i]["file"],
                    "line1": timestamps_sorted[i]["line"],
                    "timestamp1": ts1_str,
                    "file2": timestamps_sorted[i + 1]["file"],
                    "line2": timestamps_sorted[i + 1]["line"],
                    "timestamp2": ts2_str,
                    "skew_seconds": int(skew_seconds)
                })

        except (ValueError, AttributeError):
            raise NotImplementedError("TODO: Implement this block")

    return max_skew, violations


def write_audit_log(
    status: str,
    max_skew_seconds: int,
    threshold: int,
    violations: List[Dict],
    policy_version: str
) -> None:
    """Write deterministic audit log entry."""
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    entry = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "component": "anti_gaming",
        "check": "time_skew",
        "status": status,
        "max_skew_seconds": max_skew_seconds,
        "threshold": threshold,
        "violations": len(violations),
        "violation_details": violations[:10],  # Limit to first 10
        "policy_version": policy_version
    }

    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, sort_keys=True) + "\n")


def main() -> int:
    """Main execution."""
    print("SSID Time Skew Analyzer")
    print("=" * 60)

    # Load policy
    policy = load_policy()
    rules = policy.get("rules", {}).get("time_skew", {})
    max_skew_threshold = rules.get("max_allowed_skew_seconds", 300)
    policy_version = policy.get("metadata", {}).get("version", "1.0.0")

    print(f"Policy Version: {policy_version}")
    print(f"Max Skew Threshold: {max_skew_threshold} seconds")
    print()

    # Find JSONL files
    print("Scanning for JSONL files...")
    jsonl_files = find_jsonl_files()
    print(f"Files found: {len(jsonl_files)}")

    # Extract all timestamps
    print("Extracting timestamps...")
    all_timestamps = []
    for jsonl_file in jsonl_files:
        timestamps = extract_timestamps(jsonl_file)
        all_timestamps.extend(timestamps)

    print(f"Timestamps extracted: {len(all_timestamps)}")
    print()

    # Analyze skew
    print("Analyzing time skew...")
    max_skew, violations = analyze_skew(all_timestamps, max_skew_threshold)

    status = "PASS" if len(violations) == 0 else "FAIL"

    # Write audit log
    write_audit_log(status, max_skew, max_skew_threshold, violations, policy_version)

    # Report results
    print()
    print("=" * 60)
    print(f"Status: {status}")
    print(f"Max Skew: {max_skew} seconds")
    print(f"Violations: {len(violations)}")

    if violations:
        print("\nTime Skew Violations (first 5):")
        for v in violations[:5]:
            print(f"  - {v['file1']}:{v['line1']} -> {v['file2']}:{v['line2']}")
            print(f"    Skew: {v['skew_seconds']} seconds")

    print()
    print(f"Audit log: {LOG_PATH}")

    return 0 if status == "PASS" else 2


if __name__ == "__main__":
    sys.exit(main())
