#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
anti_gaming_alert_hook.py – SSID Realtime Anti-Gaming Alert System
Monitors anti-gaming duplicate identity check results and triggers realtime notifications
Integrates with Slack/Teams/PagerDuty for immediate incident response

Author: edubrainboost ©2025 MIT License
Version: 1.0.0

SSID Policy Flags:
- hash_only: true
- no_pii: true
- non_custodial: true
- SAFE_FIX: read_only

Compliance Notes:
- GDPR Art. 25: Privacy by design (no PII in alerts)
- eIDAS Art. 24: Secure notification mechanisms
- MiCA Art. 76: Operational resilience via automated alerting
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional
import urllib.request
import urllib.parse

# Root path resolution
ROOT = Path(__file__).resolve().parents[1]
POLICY_FILE = ROOT / "23_compliance" / "policies" / "anti_gaming_policy.yaml"
LOG_FILE = ROOT / "02_audit_logging" / "logs" / "anti_gaming_duplicate_hashes.jsonl"
REGISTRY_LOCK = ROOT / "24_meta_orchestration" / "registry" / "locks" / "registry_lock.yaml"

# Environment variables for webhook URLs (best practice: store in secrets)
SLACK_WEBHOOK = os.getenv("SLACK_COMPLIANCE_WEBHOOK", "")
TEAMS_WEBHOOK = os.getenv("TEAMS_COMPLIANCE_WEBHOOK", "")
PAGERDUTY_KEY = os.getenv("PAGERDUTY_INTEGRATION_KEY", "")


class AntiGamingAlertHook:
    """Monitors anti-gaming check results and dispatches realtime alerts."""

    def __init__(self, log_file: Path, policy_file: Path):
        self.log_file = log_file
        self.policy_file = policy_file
        self.policy = self._load_policy()

    def _load_policy(self) -> Dict:
        """Load policy configuration from YAML file."""
        try:
            import yaml
            with open(self.policy_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"[WARNING] Policy file not found: {self.policy_file}")
            # Fallback to default thresholds
            return {
                "thresholds": {
                    "pass": {"collision_count_max": 0},
                    "warn": {"collision_count_min": 1, "collision_count_max": 2},
                    "fail": {"collision_count_min": 3},
                    "critical": {"collision_count_min": 10}
                }
            }
        except Exception as e:
            print(f"[ERROR] Failed to load policy: {e}")
            return {}

    def get_latest_entry(self) -> Optional[Dict]:
        """Retrieve the latest log entry from the JSONL file."""
        if not self.log_file.exists():
            print(f"[ERROR] Log file not found: {self.log_file}")
            raise NotImplementedError("TODO: Implement this function")

        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if not lines:
                    raise NotImplementedError("TODO: Implement this function")
                # Get last non-empty line
                for line in reversed(lines):
                    line = line.strip()
                    if line:
                        return json.loads(line)
        except Exception as e:
            print(f"[ERROR] Failed to read log file: {e}")
            raise NotImplementedError("TODO: Implement this function")

    def determine_threshold_level(self, collision_count: int) -> str:
        """Determine threshold level based on collision count."""
        thresholds = self.policy.get("thresholds", {})

        if collision_count <= thresholds.get("pass", {}).get("collision_count_max", 0):
            return "PASS"
        elif collision_count <= thresholds.get("warn", {}).get("collision_count_max", 2):
            return "WARN"
        elif collision_count < thresholds.get("critical", {}).get("collision_count_min", 10):
            return "FAIL"
        else:
            return "CRITICAL"

    def send_slack_alert(self, entry: Dict, threshold_level: str):
        """Send alert to Slack via webhook."""
        if not SLACK_WEBHOOK:
            print("[INFO] Slack webhook not configured (set SLACK_COMPLIANCE_WEBHOOK)")
            return

        collision_count = entry.get("collision_count", 0)
        timestamp = entry.get("timestamp", "unknown")
        status = entry.get("status", "UNKNOWN")
        collisions = entry.get("collisions", [])

        # Color coding
        color_map = {
            "PASS": "#36a64f",  # Green
            "WARN": "#ff9900",  # Orange
            "FAIL": "#ff0000",  # Red
            "CRITICAL": "#8b0000"  # Dark Red
        }
        color = color_map.get(threshold_level, "#cccccc")

        # Mention mapping
        mention_map = {
            "PASS": "",
            "WARN": "",
            "FAIL": "<!channel>",  # @channel in Slack
            "CRITICAL": "<!here>"  # @here in Slack
        }
        mention = mention_map.get(threshold_level, "")

        # Build collision summary
        collision_summary = ""
        if collisions:
            collision_summary = f"\n*Top Collisions:*\n"
            for c in collisions[:3]:  # Show top 3
                collision_summary += f"• {c.get('type', 'unknown').upper()}: `{c.get('value', 'N/A')[:50]}...` ({c.get('count', 0)} files)\n"

        payload = {
            "text": f"{mention} *SSID Anti-Gaming Alert*",
            "attachments": [
                {
                    "color": color,
                    "title": f"[{threshold_level}] Duplicate Identity Check",
                    "fields": [
                        {"title": "Status", "value": status, "short": True},
                        {"title": "Collision Count", "value": str(collision_count), "short": True},
                        {"title": "Threshold Level", "value": threshold_level, "short": True},
                        {"title": "Timestamp", "value": timestamp, "short": True}
                    ],
                    "text": collision_summary if collision_summary else "No collisions detected.",
                    "footer": "SSID Compliance Monitor - Anti-Gaming",
                    "footer_icon": "https://ssid.org/icon.png",
                    "ts": int(datetime.now(timezone.utc).timestamp())
                }
            ]
        }

        try:
            req = urllib.request.Request(
                SLACK_WEBHOOK,
                data=json.dumps(payload).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    print(f"[SUCCESS] Slack alert sent ({threshold_level})")
                else:
                    print(f"[ERROR] Slack webhook returned status {response.status}")
        except Exception as e:
            print(f"[ERROR] Failed to send Slack alert: {e}")

    def send_teams_alert(self, entry: Dict, threshold_level: str):
        """Send alert to Microsoft Teams via webhook."""
        if not TEAMS_WEBHOOK:
            print("[INFO] Teams webhook not configured (set TEAMS_COMPLIANCE_WEBHOOK)")
            return

        collision_count = entry.get("collision_count", 0)
        timestamp = entry.get("timestamp", "unknown")
        status = entry.get("status", "UNKNOWN")
        collisions = entry.get("collisions", [])

        # Theme color coding (hex without #)
        color_map = {
            "PASS": "28a745",  # Green
            "WARN": "ffc107",  # Orange
            "FAIL": "dc3545",  # Red
            "CRITICAL": "8b0000"  # Dark Red
        }
        theme_color = color_map.get(threshold_level, "cccccc")

        # Build collision list
        collision_text = ""
        if collisions:
            collision_text = "\n\nTop Collisions:\n"
            for c in collisions[:3]:
                collision_text += f"- {c.get('type', 'unknown').upper()}: {c.get('value', 'N/A')[:50]}... ({c.get('count', 0)} files)\n"

        payload = {
            "@type": "MessageCard",
            "@context": "https://schema.org/extensions",
            "summary": f"SSID Anti-Gaming Alert: {threshold_level}",
            "themeColor": theme_color,
            "title": f"[{threshold_level}] SSID Anti-Gaming Alert",
            "sections": [
                {
                    "activityTitle": "Duplicate Identity Check",
                    "activitySubtitle": "SSID Compliance Monitor",
                    "facts": [
                        {"name": "Status", "value": status},
                        {"name": "Collision Count", "value": str(collision_count)},
                        {"name": "Threshold Level", "value": threshold_level},
                        {"name": "Timestamp", "value": timestamp}
                    ],
                    "text": collision_text if collision_text else "No collisions detected."
                }
            ],
            "potentialAction": [
                {
                    "@type": "OpenUri",
                    "name": "View Audit Log",
                    "targets": [
                        {"os": "default", "uri": "https://ssid.org/audit/anti-gaming"}
                    ]
                }
            ]
        }

        try:
            req = urllib.request.Request(
                TEAMS_WEBHOOK,
                data=json.dumps(payload).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    print(f"[SUCCESS] Teams alert sent ({threshold_level})")
                else:
                    print(f"[ERROR] Teams webhook returned status {response.status}")
        except Exception as e:
            print(f"[ERROR] Failed to send Teams alert: {e}")

    def send_pagerduty_alert(self, entry: Dict, threshold_level: str):
        """Send alert to PagerDuty (only for FAIL/CRITICAL)."""
        if threshold_level not in ["FAIL", "CRITICAL"]:
            return  # Only alert on failures

        if not PAGERDUTY_KEY:
            print("[INFO] PagerDuty not configured (set PAGERDUTY_INTEGRATION_KEY)")
            return

        collision_count = entry.get("collision_count", 0)
        timestamp = entry.get("timestamp", "unknown")
        collisions = entry.get("collisions", [])

        severity_map = {
            "FAIL": "error",
            "CRITICAL": "critical"
        }
        severity = severity_map.get(threshold_level, "error")

        # Build custom details
        custom_details = {
            "collision_count": collision_count,
            "threshold_level": threshold_level,
            "check": "duplicate_identity_hashes",
            "component": "anti_gaming",
            "top_collisions": []
        }

        for c in collisions[:5]:  # Include top 5 in details
            custom_details["top_collisions"].append({
                "type": c.get("type", "unknown"),
                "value": c.get("value", "N/A")[:100],
                "count": c.get("count", 0),
                "files": c.get("files", [])[:3]  # First 3 files
            })

        payload = {
            "routing_key": PAGERDUTY_KEY,
            "event_action": "trigger",
            "payload": {
                "summary": f"SSID Anti-Gaming: {collision_count} duplicate identities detected",
                "severity": severity,
                "source": "ssid-anti-gaming-monitor",
                "timestamp": timestamp,
                "custom_details": custom_details
            }
        }

        try:
            req = urllib.request.Request(
                "https://events.pagerduty.com/v2/enqueue",
                data=json.dumps(payload).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 202:
                    print(f"[SUCCESS] PagerDuty alert sent ({threshold_level})")
                else:
                    print(f"[ERROR] PagerDuty API returned status {response.status}")
        except Exception as e:
            print(f"[ERROR] Failed to send PagerDuty alert: {e}")

    def monitor(self):
        """Main monitoring function - check latest entry and dispatch alerts."""
        print("[INFO] Starting anti-gaming alert hook...")

        entry = self.get_latest_entry()
        if not entry:
            print("[WARNING] No log entries found")
            return

        collision_count = entry.get("collision_count", 0)
        status = entry.get("status", "UNKNOWN")
        threshold_level = self.determine_threshold_level(collision_count)

        print(f"[INFO] Latest check: status={status}, collisions={collision_count}, level={threshold_level}")

        # Dispatch alerts based on threshold level
        if threshold_level in ["WARN", "FAIL", "CRITICAL"]:
            print(f"[ALERT] Threshold {threshold_level} triggered, dispatching notifications...")
            self.send_slack_alert(entry, threshold_level)
            self.send_teams_alert(entry, threshold_level)
            if threshold_level in ["FAIL", "CRITICAL"]:
                self.send_pagerduty_alert(entry, threshold_level)
        else:
            print(f"[OK] Status {threshold_level}, no alerts needed")


def main():
    """Entry point for the anti-gaming alert hook."""
    monitor = AntiGamingAlertHook(LOG_FILE, POLICY_FILE)
    monitor.monitor()


if __name__ == "__main__":
    main()
