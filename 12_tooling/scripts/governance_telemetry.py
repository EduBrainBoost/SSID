#!/usr/bin/env python3
"""
governance_telemetry.py - SSID Governance Telemetry & Notification System
Blueprint v4.3 - Auto-Anchoring & Telemetry Layer

This script monitors governance metrics and sends notifications when significant
events occur, such as compliance score changes, violations, or quarterly releases.

Features:
- Real-time monitoring of governance dashboard metrics
- Configurable notification thresholds
- Multi-channel notifications (Slack, Discord, Webhooks)
- Score drift analysis and trend detection
- Violation alerting
- GDPR/eIDAS/MiCA compliant (no PII, only metadata)

Usage:
    python3 governance_telemetry.py                # Check current metrics
    python3 governance_telemetry.py --watch        # Continuous monitoring
    python3 governance_telemetry.py --test         # Test notifications
"""

import json
import csv
import sys
import argparse
import time
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import urllib.request
import urllib.error


# ===========================================================================
# Configuration
# ===========================================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_FILE = PROJECT_ROOT / "07_governance_legal/telemetry_config.json"
DASHBOARD_CSV = PROJECT_ROOT / "07_governance_legal/dashboard_data.csv"
REGISTRY_LOG = PROJECT_ROOT / "24_meta_orchestration/registry/logs/registry_events.log"
TELEMETRY_STATE = PROJECT_ROOT / "24_meta_orchestration/registry/logs/telemetry_state.json"

# Colors for terminal output
class Colors:
    GREEN = '\033[0;32m'
    BLUE = '\033[0;34m'
    YELLOW = '\033[1;33m'
    RED = '\033[0;31m'
    CYAN = '\033[0;36m'
    MAGENTA = '\033[0;35m'
    NC = '\033[0m'  # No Color


# ===========================================================================
# Configuration Management
# ===========================================================================

def load_config() -> Dict:
    """Load telemetry configuration or return defaults."""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)

    # Default configuration
    default_config = {
        "enabled": True,
        "check_interval_seconds": 300,
        "thresholds": {
            "compliance_score_min": 95,
            "compliance_score_critical": 90,
            "score_drop_warning": 5,
            "score_drop_critical": 10,
            "max_violations": 0
        },
        "notifications": {
            "slack": {
                "enabled": False,
                "webhook_url": "",
                "channel": "#ssid-governance",
                "username": "SSID Governance Bot"
            },
            "discord": {
                "enabled": False,
                "webhook_url": "",
                "username": "SSID Governance"
            },
            "webhook": {
                "enabled": False,
                "url": "",
                "method": "POST",
                "headers": {
                    "Content-Type": "application/json"
                }
            },
            "email": {
                "enabled": False,
                "smtp_server": "",
                "smtp_port": 587,
                "from_address": "",
                "to_addresses": [],
                "use_tls": True
            }
        },
        "event_filters": {
            "notify_on_release": True,
            "notify_on_score_change": True,
            "notify_on_violation": True,
            "notify_on_quarterly_report": True
        }
    }

    return default_config


def load_telemetry_state() -> Dict:
    """Load last telemetry state or create new one."""
    if TELEMETRY_STATE.exists():
        with open(TELEMETRY_STATE, 'r', encoding='utf-8') as f:
            return json.load(f)

    return {
        "last_check": None,
        "last_compliance_score": None,
        "last_notification_sent": None,
        "processed_events": []
    }


def save_telemetry_state(state: Dict):
    """Save current telemetry state."""
    state["last_check"] = datetime.now(timezone.utc).isoformat()

    TELEMETRY_STATE.parent.mkdir(parents=True, exist_ok=True)

    with open(TELEMETRY_STATE, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


# ===========================================================================
# Metrics Collection
# ===========================================================================

def load_dashboard_metrics() -> Optional[Dict]:
    """Load latest metrics from governance dashboard CSV."""
    if not DASHBOARD_CSV.exists():
        return None

    try:
        with open(DASHBOARD_CSV, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

            if not rows:
                return None

            # Get the most recent entry
            latest = rows[-1]

            return {
                "timestamp": latest.get("timestamp"),
                "quarter": latest.get("quarter"),
                "compliance_score": int(latest.get("compliance_score", 0)),
                "total_roots": int(latest.get("total_roots", 0)),
                "verified_roots": int(latest.get("verified_roots", 0)),
                "violations": int(latest.get("violations", 0)),
                "blueprint_version": latest.get("blueprint_version"),
                "root_24_lock": latest.get("root_24_lock"),
                "safe_fix_status": latest.get("safe_fix_status")
            }

    except Exception as e:
        print(f"{Colors.RED}X Error loading dashboard metrics: {e}{Colors.NC}")
        return None


def load_registry_events() -> List[Dict]:
    """Load recent events from registry log."""
    events = []

    if not REGISTRY_LOG.exists():
        return events

    with open(REGISTRY_LOG, 'r', encoding='utf-8') as f:
        current_event = {}
        for line in f:
            line = line.strip()

            if not line or line == "Registry events initialized.":
                continue

            if line == "{":
                current_event = {"_raw": "{"}
            elif line == "}":
                if current_event:
                    current_event["_raw"] += "}"
                    try:
                        event = json.loads(current_event["_raw"])
                        events.append(event)
                    except json.JSONDecodeError:
                        pass
                current_event = {}
            elif current_event:
                current_event["_raw"] += line

    return events


def analyze_score_trend(metrics: Dict, state: Dict) -> Dict[str, Any]:
    """
    Analyze compliance score trends and detect anomalies.

    Args:
        metrics: Current metrics
        state: Previous state

    Returns:
        Analysis dictionary with trend information
    """
    current_score = metrics.get("compliance_score", 0)
    previous_score = state.get("last_compliance_score")

    analysis = {
        "current_score": current_score,
        "previous_score": previous_score,
        "score_change": 0,
        "trend": "stable",
        "alert_level": "info"
    }

    if previous_score is not None:
        score_change = current_score - previous_score
        analysis["score_change"] = score_change

        if score_change < 0:
            analysis["trend"] = "declining"

            if abs(score_change) >= 10:
                analysis["alert_level"] = "critical"
            elif abs(score_change) >= 5:
                analysis["alert_level"] = "warning"
        elif score_change > 0:
            analysis["trend"] = "improving"
            analysis["alert_level"] = "success"

    return analysis


# ===========================================================================
# Notification Senders
# ===========================================================================

def send_slack_notification(webhook_url: str, message: Dict, config: Dict) -> bool:
    """Send notification to Slack via webhook."""
    try:
        payload = {
            "channel": config.get("channel", "#ssid-governance"),
            "username": config.get("username", "SSID Governance Bot"),
            "text": message.get("text", ""),
            "attachments": message.get("attachments", [])
        }

        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            webhook_url,
            data=data,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )

        with urllib.request.urlopen(req, timeout=10) as response:
            return response.status == 200

    except Exception as e:
        print(f"{Colors.RED}X Slack notification failed: {e}{Colors.NC}")
        return False


def send_discord_notification(webhook_url: str, message: Dict, config: Dict) -> bool:
    """Send notification to Discord via webhook."""
    try:
        payload = {
            "username": config.get("username", "SSID Governance"),
            "content": message.get("text", ""),
            "embeds": message.get("embeds", [])
        }

        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            webhook_url,
            data=data,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )

        with urllib.request.urlopen(req, timeout=10) as response:
            return response.status in (200, 204)

    except Exception as e:
        print(f"{Colors.RED}X Discord notification failed: {e}{Colors.NC}")
        return False


def send_webhook_notification(url: str, message: Dict, config: Dict) -> bool:
    """Send notification to custom webhook."""
    try:
        headers = config.get("headers", {"Content-Type": "application/json"})
        method = config.get("method", "POST")

        data = json.dumps(message).encode('utf-8')
        req = urllib.request.Request(
            url,
            data=data,
            headers=headers,
            method=method
        )

        with urllib.request.urlopen(req, timeout=10) as response:
            return response.status in (200, 201, 202, 204)

    except Exception as e:
        print(f"{Colors.RED}X Webhook notification failed: {e}{Colors.NC}")
        return False


def format_notification_message(event_type: str, metrics: Dict, analysis: Dict) -> Dict:
    """
    Format a notification message for various platforms.

    Args:
        event_type: Type of event triggering notification
        metrics: Current metrics
        analysis: Score trend analysis

    Returns:
        Formatted message dictionary
    """
    alert_level = analysis.get("alert_level", "info")
    current_score = metrics.get("compliance_score", 0)

    # Determine emoji and color based on alert level
    emoji_map = {
        "critical": "!!",
        "warning": "!",
        "success": "[OK]",
        "info": "[i]"
    }

    color_map = {
        "critical": "#ff0000",
        "warning": "#ff9900",
        "success": "#00ff00",
        "info": "#0099ff"
    }

    emoji = emoji_map.get(alert_level, "[i]")
    color = color_map.get(alert_level, "#0099ff")

    # Build message text
    if event_type == "score_change":
        title = f"{emoji} SSID Governance Score Changed"
        description = f"Compliance score: **{current_score}/100** ({analysis.get('trend', 'stable')})"

        if analysis.get("score_change"):
            change = analysis["score_change"]
            sign = "+" if change > 0 else ""
            description += f"\nChange: {sign}{change}"

    elif event_type == "violation":
        title = f"!! SSID Governance Violation Detected"
        description = f"Violations: **{metrics.get('violations', 0)}**\nCompliance score: {current_score}/100"

    elif event_type == "release":
        title = f"[RELEASE] SSID Quarterly Release"
        description = f"Quarter: **{metrics.get('quarter')}**\nCompliance score: {current_score}/100"

    elif event_type == "test":
        title = f"[TEST] SSID Telemetry Test"
        description = f"Test notification from governance telemetry system\nCompliance score: {current_score}/100"

    else:
        title = f"{emoji} SSID Governance Update"
        description = f"Compliance score: {current_score}/100"

    # Build message for different platforms
    message = {
        "text": f"{title}\n{description}",
        "attachments": [{
            "color": color,
            "title": title,
            "text": description,
            "fields": [
                {"title": "Compliance Score", "value": f"{current_score}/100", "short": True},
                {"title": "Blueprint Version", "value": metrics.get("blueprint_version", "v4.3"), "short": True},
                {"title": "Root-24-LOCK", "value": metrics.get("root_24_lock", "active"), "short": True},
                {"title": "Violations", "value": str(metrics.get("violations", 0)), "short": True}
            ],
            "footer": "SSID Governance Telemetry",
            "ts": int(datetime.now(timezone.utc).timestamp())
        }],
        "embeds": [{
            "title": title,
            "description": description,
            "color": int(color.replace("#", ""), 16),
            "fields": [
                {"name": "Compliance Score", "value": f"{current_score}/100", "inline": True},
                {"name": "Blueprint Version", "value": metrics.get("blueprint_version", "v4.3"), "inline": True},
                {"name": "Root-24-LOCK", "value": metrics.get("root_24_lock", "active"), "inline": True},
                {"name": "Violations", "value": str(metrics.get("violations", 0)), "inline": True}
            ],
            "footer": {"text": "SSID Governance Telemetry"},
            "timestamp": datetime.now(timezone.utc).isoformat()
        }]
    }

    return message


def send_notifications(event_type: str, metrics: Dict, analysis: Dict, config: Dict) -> int:
    """
    Send notifications to all configured channels.

    Args:
        event_type: Type of event triggering notification
        metrics: Current metrics
        analysis: Score trend analysis
        config: Telemetry configuration

    Returns:
        Number of successful notifications sent
    """
    message = format_notification_message(event_type, metrics, analysis)
    notifications_config = config.get("notifications", {})

    sent_count = 0

    # Slack
    if notifications_config.get("slack", {}).get("enabled"):
        webhook_url = notifications_config["slack"].get("webhook_url")
        if webhook_url and send_slack_notification(webhook_url, message, notifications_config["slack"]):
            print(f"{Colors.GREEN}OK Slack notification sent{Colors.NC}")
            sent_count += 1

    # Discord
    if notifications_config.get("discord", {}).get("enabled"):
        webhook_url = notifications_config["discord"].get("webhook_url")
        if webhook_url and send_discord_notification(webhook_url, message, notifications_config["discord"]):
            print(f"{Colors.GREEN}OK Discord notification sent{Colors.NC}")
            sent_count += 1

    # Custom Webhook
    if notifications_config.get("webhook", {}).get("enabled"):
        webhook_url = notifications_config["webhook"].get("url")
        if webhook_url and send_webhook_notification(webhook_url, message, notifications_config["webhook"]):
            print(f"{Colors.GREEN}OK Webhook notification sent{Colors.NC}")
            sent_count += 1

    return sent_count


# ===========================================================================
# Main Monitoring Logic
# ===========================================================================

def check_metrics(config: Dict, test_mode: bool = False):
    """
    Check current governance metrics and send notifications if needed.

    Args:
        config: Telemetry configuration
        test_mode: If True, always send test notification
    """
    print(f"{Colors.CYAN}[CHECK] Checking governance metrics...{Colors.NC}")

    # Load current state
    state = load_telemetry_state()
    metrics = load_dashboard_metrics()

    if not metrics:
        print(f"{Colors.YELLOW}! No metrics available{Colors.NC}")
        return

    # Analyze trends
    analysis = analyze_score_trend(metrics, state)

    print(f"  Compliance Score: {Colors.CYAN}{metrics['compliance_score']}/100{Colors.NC}")
    print(f"  Violations: {Colors.CYAN}{metrics['violations']}{Colors.NC}")
    print(f"  Root-24-LOCK: {Colors.CYAN}{metrics['root_24_lock']}{Colors.NC}")

    if analysis.get("score_change"):
        change = analysis["score_change"]
        sign = "+" if change > 0 else ""
        color = Colors.GREEN if change > 0 else Colors.RED
        print(f"  Score Change: {color}{sign}{change}{Colors.NC}")

    # Determine if notification should be sent
    should_notify = False
    event_type = "info"

    thresholds = config.get("thresholds", {})
    filters = config.get("event_filters", {})

    if test_mode:
        should_notify = True
        event_type = "test"
        print(f"{Colors.YELLOW}[NOTIFY] Test mode: Sending test notification{Colors.NC}")

    elif metrics["violations"] > thresholds.get("max_violations", 0):
        should_notify = filters.get("notify_on_violation", True)
        event_type = "violation"
        print(f"{Colors.RED}!! Violations detected!{Colors.NC}")

    elif analysis.get("alert_level") in ("warning", "critical"):
        should_notify = filters.get("notify_on_score_change", True)
        event_type = "score_change"
        print(f"{Colors.YELLOW}! Score change alert!{Colors.NC}")

    # Send notifications if needed
    if should_notify:
        sent_count = send_notifications(event_type, metrics, analysis, config)

        if sent_count > 0:
            print(f"{Colors.GREEN}OK Sent {sent_count} notification(s){Colors.NC}")
        else:
            print(f"{Colors.YELLOW}! No notifications configured or all failed{Colors.NC}")

    # Update state
    state["last_compliance_score"] = metrics["compliance_score"]
    if should_notify:
        state["last_notification_sent"] = datetime.now(timezone.utc).isoformat()

    save_telemetry_state(state)

    print()


def watch_mode(config: Dict):
    """
    Continuous monitoring mode - check metrics at configured intervals.

    Args:
        config: Telemetry configuration
    """
    interval = config.get("check_interval_seconds", 300)

    print(f"{Colors.BLUE}{'=' * 70}{Colors.NC}")
    print(f"{Colors.BLUE}  SSID Governance Telemetry - Watch Mode{Colors.NC}")
    print(f"{Colors.BLUE}  Check interval: {interval}s{Colors.NC}")
    print(f"{Colors.BLUE}{'=' * 70}{Colors.NC}")
    print()

    try:
        while True:
            check_metrics(config)
            print(f"{Colors.CYAN}[WAIT] Next check in {interval}s... (Ctrl+C to stop){Colors.NC}")
            print()
            time.sleep(interval)

    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}! Monitoring stopped{Colors.NC}")


# ===========================================================================
# CLI Interface
# ===========================================================================

def main():
    """Main entry point for telemetry script."""
    parser = argparse.ArgumentParser(
        description="SSID Governance Telemetry & Notification System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 governance_telemetry.py           # Check metrics once
  python3 governance_telemetry.py --watch   # Continuous monitoring
  python3 governance_telemetry.py --test    # Send test notification
        """
    )

    parser.add_argument(
        "--watch",
        action="store_true",
        help="Continuous monitoring mode"
    )

    parser.add_argument(
        "--test",
        action="store_true",
        help="Send test notification"
    )

    args = parser.parse_args()

    try:
        config = load_config()

        if not config.get("enabled", True):
            print(f"{Colors.YELLOW}! Telemetry is disabled in configuration{Colors.NC}")
            sys.exit(0)

        if args.watch:
            watch_mode(config)
        else:
            check_metrics(config, test_mode=args.test)

        sys.exit(0)

    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}! Interrupted by user{Colors.NC}")
        sys.exit(130)
    except Exception as e:
        print(f"{Colors.RED}X Error: {e}{Colors.NC}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
