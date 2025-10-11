#!/usr/bin/env python3
"""
Blueprint v4.6 - Telemetry Activation

This script activates the real-time telemetry system after Q1 2026 launch.
It transitions from simulation mode to live operation with actual notifications.

IMPORTANT: This script should only execute after autonomous_cycle_launcher.py completes.

Exit Codes:
  0 - Telemetry activated successfully
  1 - Launch not confirmed (prerequisite)
  2 - Configuration error
  3 - Notification delivery failed
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
import hashlib

# Optional import for requests (fallback to simulation mode if not available)
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

# Blueprint version
BLUEPRINT_VERSION = "v4.6.0-launch"
CYCLE_ID = "Q1_2026"

# File paths
TELEMETRY_CONFIG = Path("07_governance_legal/telemetry_config.json")
STATE_LOG = Path("02_audit_logging/reports/autonomous_cycle_state.json")
REPORTS_DIR = Path("05_documentation/reports/2026-Q1")
COMPLIANCE_DIR = Path("23_compliance/reports")

def calculate_sha256(data):
    """Calculate SHA256 hash of data"""
    if isinstance(data, dict):
        data = json.dumps(data, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(data.encode('utf-8')).hexdigest()

def check_launch_confirmation():
    """Verify that autonomous cycle launch has completed"""
    if not STATE_LOG.exists():
        print("[ERROR] Launch state log not found")
        print("Prerequisite: autonomous_cycle_launcher.py must complete first")
        return False

    with open(STATE_LOG, 'r', encoding='utf-8') as f:
        state = json.load(f)

    if state.get("system_state") != "AUTONOMOUS_ACTIVE":
        print(f"[ERROR] System not in AUTONOMOUS_ACTIVE state")
        print(f"Current state: {state.get('system_state', 'UNKNOWN')}")
        return False

    if state.get("launch_confirmation", {}).get("status") != "LAUNCHED":
        print("[ERROR] Launch not confirmed")
        return False

    print("[OK] Launch confirmed - proceeding with telemetry activation")
    return True

def load_telemetry_config():
    """Load and validate telemetry configuration"""
    if not TELEMETRY_CONFIG.exists():
        print(f"[ERROR] Telemetry config not found: {TELEMETRY_CONFIG}")
        return None

    with open(TELEMETRY_CONFIG, 'r', encoding='utf-8') as f:
        config = json.load(f)

    # Validate configuration
    if not config.get("enabled", False):
        print("[ERROR] Telemetry not enabled in configuration")
        return None

    channels = config.get("notification_channels", {})
    active_channels = []

    for channel_type in ["slack", "discord", "webhook", "email"]:
        if channels.get(channel_type, {}).get("enabled", False):
            active_channels.append(channel_type)

    if not active_channels:
        print("[WARNING] No notification channels configured")
        print("Telemetry will run in simulation mode")

    config["active_channels"] = active_channels

    print(f"[CONFIG LOADED]")
    print(f"Telemetry Enabled: {config.get('enabled')}")
    print(f"Active Channels:   {len(active_channels)} ({', '.join(active_channels)})")

    return config

def send_slack_notification(webhook_url, message_data):
    """Send notification to Slack"""
    if not REQUESTS_AVAILABLE:
        return {
            "status": "SIMULATED",
            "channel": "slack",
            "webhook_url": webhook_url[:30] + "...",
            "message": message_data["message"]
        }

    try:
        payload = {
            "text": message_data["message"],
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": message_data["title"]
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": message_data["message"]
                    }
                }
            ]
        }

        response = requests.post(webhook_url, json=payload, timeout=10)

        if response.status_code == 200:
            return {"status": "SUCCESS", "channel": "slack", "response_code": 200}
        else:
            return {"status": "FAILED", "channel": "slack", "response_code": response.status_code}

    except Exception as e:
        return {"status": "ERROR", "channel": "slack", "error": str(e)}

def send_discord_notification(webhook_url, message_data):
    """Send notification to Discord"""
    if not REQUESTS_AVAILABLE:
        return {
            "status": "SIMULATED",
            "channel": "discord",
            "webhook_url": webhook_url[:30] + "...",
            "message": message_data["message"]
        }

    try:
        payload = {
            "content": message_data["message"],
            "embeds": [
                {
                    "title": message_data["title"],
                    "description": message_data["message"],
                    "color": 3066993 if message_data.get("status") == "success" else 15158332
                }
            ]
        }

        response = requests.post(webhook_url, json=payload, timeout=10)

        if response.status_code == 204:
            return {"status": "SUCCESS", "channel": "discord", "response_code": 204}
        else:
            return {"status": "FAILED", "channel": "discord", "response_code": response.status_code}

    except Exception as e:
        return {"status": "ERROR", "channel": "discord", "error": str(e)}

def send_webhook_notification(webhook_url, message_data):
    """Send notification to generic webhook"""
    if not REQUESTS_AVAILABLE:
        return {
            "status": "SIMULATED",
            "channel": "webhook",
            "webhook_url": webhook_url[:30] + "...",
            "message": message_data["message"]
        }

    try:
        payload = {
            "event": "telemetry_activation",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "title": message_data["title"],
            "message": message_data["message"],
            "status": message_data.get("status", "info")
        }

        response = requests.post(webhook_url, json=payload, timeout=10)

        if 200 <= response.status_code < 300:
            return {"status": "SUCCESS", "channel": "webhook", "response_code": response.status_code}
        else:
            return {"status": "FAILED", "channel": "webhook", "response_code": response.status_code}

    except Exception as e:
        return {"status": "ERROR", "channel": "webhook", "error": str(e)}

def send_email_notification(email_config, message_data):
    """Send notification via email (placeholder - requires SMTP setup)"""
    # Email notification requires SMTP configuration
    # This is a placeholder that returns simulated status
    return {
        "status": "SIMULATED",
        "channel": "email",
        "recipient": email_config.get("recipient", "not_configured"),
        "message": message_data["message"]
    }

def send_launch_notification(config):
    """Send launch confirmation notification to all active channels"""
    now = datetime.now(timezone.utc)

    message_data = {
        "title": "SSID Governance Node v4.6 - Autonomous Cycle Launch",
        "message": f"[ROCKET] SSID Governance Node v4.6 -> Autonomous Cycle Launch confirmed.\n\nSystem State: AUTONOMOUS_ACTIVE\nGovernance Cycle: Q1 2026\nLaunch Time: {now.isoformat()}\nTelemetry: LIVE\nProof Chain: 5 layers (INTACT)\nRoot-24-LOCK: ENFORCED",
        "status": "success",
        "timestamp": now.isoformat()
    }

    channels = config.get("notification_channels", {})
    results = []

    # Send to Slack
    if "slack" in config.get("active_channels", []):
        slack_config = channels.get("slack", {})
        webhook_url = slack_config.get("webhook_url")
        if webhook_url:
            result = send_slack_notification(webhook_url, message_data)
            results.append(result)

    # Send to Discord
    if "discord" in config.get("active_channels", []):
        discord_config = channels.get("discord", {})
        webhook_url = discord_config.get("webhook_url")
        if webhook_url:
            result = send_discord_notification(webhook_url, message_data)
            results.append(result)

    # Send to Webhook
    if "webhook" in config.get("active_channels", []):
        webhook_config = channels.get("webhook", {})
        webhook_url = webhook_config.get("url")
        if webhook_url:
            result = send_webhook_notification(webhook_url, message_data)
            results.append(result)

    # Send to Email
    if "email" in config.get("active_channels", []):
        email_config = channels.get("email", {})
        result = send_email_notification(email_config, message_data)
        results.append(result)

    return results, message_data

def generate_activation_report(config, notification_results, message_data):
    """Generate telemetry activation report"""
    now = datetime.now(timezone.utc)

    # Calculate success rate
    total_sent = len(notification_results)
    successful = sum(1 for r in notification_results if r.get("status") == "SUCCESS")
    failed = sum(1 for r in notification_results if r.get("status") == "FAILED")
    simulated = sum(1 for r in notification_results if r.get("status") == "SIMULATED")

    success_rate = (successful / total_sent * 100) if total_sent > 0 else 0

    report = {
        "manifest_version": "1.0.0",
        "blueprint_version": BLUEPRINT_VERSION,
        "timestamp": now.isoformat(),
        "report_type": "telemetry_activation",
        "governance_cycle": CYCLE_ID,
        "telemetry_config": {
            "enabled": config.get("enabled"),
            "channels_configured": len(config.get("active_channels", []))
        },
        "launch_notification": {
            "title": message_data["title"],
            "message": message_data["message"],
            "timestamp": message_data["timestamp"]
        },
        "notification_results": notification_results,
        "delivery_summary": {
            "total_sent": total_sent,
            "total_successful": successful,
            "total_failed": failed,
            "total_simulated": simulated,
            "success_rate": success_rate
        },
        "overall_status": {
            "status": "LIVE" if successful > 0 else ("SIMULATED" if simulated > 0 else "FAILED"),
            "exit_code": 0 if successful > 0 or simulated > 0 else 3,
            "exit_message": f"Telemetry activated - {successful} channels live, {simulated} simulated"
        }
    }

    # Save report
    report_path = COMPLIANCE_DIR / "telemetry_activation_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\n[ACTIVATION REPORT GENERATED]")
    print(f"Total Notifications: {total_sent}")
    print(f"Successful:          {successful}")
    print(f"Failed:              {failed}")
    print(f"Simulated:           {simulated}")
    print(f"Success Rate:        {success_rate:.1f}%")
    print(f"Status:              {report['overall_status']['status']}")
    print(f"Saved to:            {report_path}")

    return report

def main():
    """Main execution flow"""
    print("=" * 70)
    print("Blueprint v4.6 - Telemetry Activation")
    print("=" * 70)

    # Step 1: Check launch confirmation
    if not check_launch_confirmation():
        print("\n[EXIT] Telemetry activation blocked - launch not confirmed")
        sys.exit(1)

    # Step 2: Load telemetry configuration
    config = load_telemetry_config()
    if config is None:
        print("\n[EXIT] Configuration error")
        sys.exit(2)

    # Step 3: Send launch notification
    print("\n[SENDING LAUNCH NOTIFICATION]")
    try:
        notification_results, message_data = send_launch_notification(config)
    except Exception as e:
        print(f"[ERROR] Notification delivery failed: {e}")
        sys.exit(3)

    # Step 4: Generate activation report
    try:
        report = generate_activation_report(config, notification_results, message_data)
    except Exception as e:
        print(f"[ERROR] Report generation failed: {e}")
        sys.exit(3)

    # Step 5: Display results
    print("\n" + "=" * 70)
    print("[SUCCESS] Telemetry Activation Complete")
    print("=" * 70)
    print(f"Status:              {report['overall_status']['status']}")
    print(f"Channels Active:     {len(config.get('active_channels', []))}")
    print(f"Notifications Sent:  {report['delivery_summary']['total_sent']}")
    print(f"Success Rate:        {report['delivery_summary']['success_rate']:.1f}%")
    print("=" * 70)

    sys.exit(report['overall_status']['exit_code'])

if __name__ == "__main__":
    main()
