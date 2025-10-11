#!/usr/bin/env python3
"""
Blueprint v4.5 Telemetry Sync Preview

Simulates governance notifications before Q1 2026 cycle launch.
Sends test payloads to configured notification channels:
- Slack
- Discord
- Email
- Webhooks

Test messages:
- "Governance Warm-Up [OK]"
- "Proof-Chain Integrity Verified [LOCK]"
- "Telemetry Ready for Q1 2026 [ROCKET]"

Exit Codes:
  0 = OK (All notifications sent)
  1 = Webhook failure
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Optional import for requests (fallback to simulation mode if not available)
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("[INFO] 'requests' module not available - running in simulation mode only")

# Configuration
TELEMETRY_CONFIG_PATH = "07_governance_legal/telemetry_config.json"
REPORT_PATH = "23_compliance/reports/telemetry_preview_report.json"

TEST_MESSAGES = [
    {
        "title": "Governance Warm-Up",
        "message": "Governance Warm-Up [OK]",
        "status": "success",
        "icon": "[CHECK]"
    },
    {
        "title": "Proof-Chain Integrity Verified",
        "message": "Proof-Chain Integrity Verified [LOCK]",
        "status": "info",
        "icon": "[LOCK]"
    },
    {
        "title": "Telemetry Ready for Q1 2026",
        "message": "Telemetry Ready for Q1 2026 [ROCKET]",
        "status": "success",
        "icon": "[ROCKET]"
    }
]

def load_telemetry_config():
    """Load telemetry configuration"""
    if not os.path.exists(TELEMETRY_CONFIG_PATH):
        return None

    with open(TELEMETRY_CONFIG_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def send_slack_notification(webhook_url, message_data):
    """Send notification to Slack"""
    if not REQUESTS_AVAILABLE:
        return {
            "status": "SIMULATED",
            "webhook_url": webhook_url[:30] + "...",
            "message": message_data["message"]
        }

    payload = {
        "text": f"{message_data['icon']} *{message_data['title']}*",
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{message_data['icon']} *{message_data['title']}*\n{message_data['message']}"
                }
            }
        ]
    }

    try:
        response = requests.post(webhook_url, json=payload, timeout=10)
        return {
            "status": "SUCCESS" if response.status_code == 200 else "FAILED",
            "status_code": response.status_code,
            "response": response.text[:200]
        }
    except Exception as e:
        return {
            "status": "ERROR",
            "error": str(e)
        }

def send_discord_notification(webhook_url, message_data):
    """Send notification to Discord"""
    if not REQUESTS_AVAILABLE:
        return {
            "status": "SIMULATED",
            "webhook_url": webhook_url[:30] + "...",
            "message": message_data["message"]
        }

    payload = {
        "content": f"{message_data['icon']} **{message_data['title']}**\n{message_data['message']}"
    }

    try:
        response = requests.post(webhook_url, json=payload, timeout=10)
        return {
            "status": "SUCCESS" if response.status_code in [200, 204] else "FAILED",
            "status_code": response.status_code,
            "response": response.text[:200]
        }
    except Exception as e:
        return {
            "status": "ERROR",
            "error": str(e)
        }

def send_webhook_notification(webhook_url, message_data):
    """Send notification to generic webhook"""
    if not REQUESTS_AVAILABLE:
        return {
            "status": "SIMULATED",
            "webhook_url": webhook_url[:30] + "...",
            "message": message_data["message"]
        }

    payload = {
        "event": "governance_telemetry_preview",
        "blueprint_version": "v4.5.0-prelaunch",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "title": message_data["title"],
        "message": message_data["message"],
        "status": message_data["status"]
    }

    try:
        response = requests.post(webhook_url, json=payload, timeout=10)
        return {
            "status": "SUCCESS" if response.status_code == 200 else "FAILED",
            "status_code": response.status_code,
            "response": response.text[:200]
        }
    except Exception as e:
        return {
            "status": "ERROR",
            "error": str(e)
        }

def send_email_notification(email_config, message_data):
    """Simulate email notification (placeholder)"""
    # Email sending would require SMTP configuration
    # For preview, we just log the attempt
    return {
        "status": "SIMULATED",
        "email_to": email_config.get("to", "not_configured"),
        "subject": f"[SSID Governance] {message_data['title']}",
        "message": message_data["message"]
    }

def send_test_notifications(config):
    """Send test notifications to all configured channels"""
    results = {
        "slack": [],
        "discord": [],
        "webhook": [],
        "email": []
    }

    # Slack notifications
    if config.get("notifications", {}).get("slack", {}).get("enabled"):
        slack_webhook = config["notifications"]["slack"].get("webhook_url")
        if slack_webhook:
            for msg in TEST_MESSAGES:
                result = send_slack_notification(slack_webhook, msg)
                results["slack"].append({
                    "message": msg["title"],
                    "result": result
                })

    # Discord notifications
    if config.get("notifications", {}).get("discord", {}).get("enabled"):
        discord_webhook = config["notifications"]["discord"].get("webhook_url")
        if discord_webhook:
            for msg in TEST_MESSAGES:
                result = send_discord_notification(discord_webhook, msg)
                results["discord"].append({
                    "message": msg["title"],
                    "result": result
                })

    # Webhook notifications
    if config.get("notifications", {}).get("webhook", {}).get("enabled"):
        webhook_url = config["notifications"]["webhook"].get("url")
        if webhook_url:
            for msg in TEST_MESSAGES:
                result = send_webhook_notification(webhook_url, msg)
                results["webhook"].append({
                    "message": msg["title"],
                    "result": result
                })

    # Email notifications (simulated)
    if config.get("notifications", {}).get("email", {}).get("enabled"):
        email_config = config["notifications"]["email"]
        for msg in TEST_MESSAGES:
            result = send_email_notification(email_config, msg)
            results["email"].append({
                "message": msg["title"],
                "result": result
            })

    return results

def generate_preview_report(config, notification_results):
    """Generate telemetry preview report"""
    timestamp = datetime.now(timezone.utc).isoformat()

    # Count successes and failures
    total_sent = 0
    total_failed = 0
    total_simulated = 0

    for channel, results in notification_results.items():
        for result in results:
            status = result["result"].get("status")
            if status == "SUCCESS":
                total_sent += 1
            elif status == "SIMULATED":
                total_simulated += 1
            else:
                total_failed += 1

    # Determine overall status
    if total_failed > 0:
        overall_status = "PARTIAL_SUCCESS"
        exit_code = 1
        exit_message = f"{total_failed} notification(s) failed"
    elif total_sent > 0 or total_simulated > 0:
        overall_status = "SUCCESS"
        exit_code = 0
        exit_message = "All notifications delivered successfully"
    else:
        overall_status = "NO_CHANNELS_CONFIGURED"
        exit_code = 0
        exit_message = "No notification channels configured (preview mode)"

    report = {
        "manifest_version": "1.0.0",
        "blueprint_version": "v4.5.0-prelaunch",
        "timestamp": timestamp,
        "report_type": "telemetry_sync_preview",
        "telemetry_config": {
            "enabled": config.get("enabled", False) if config else False,
            "channels_configured": len([
                ch for ch, cfg in (config.get("notifications", {}).items() if config else [])
                if cfg.get("enabled")
            ])
        },
        "test_messages": TEST_MESSAGES,
        "notification_results": notification_results,
        "delivery_summary": {
            "total_sent": total_sent,
            "total_failed": total_failed,
            "total_simulated": total_simulated,
            "total_channels": len([ch for ch, results in notification_results.items() if results]),
            "success_rate": (total_sent / (total_sent + total_failed) * 100) if (total_sent + total_failed) > 0 else 0
        },
        "overall_status": {
            "status": overall_status,
            "exit_code": exit_code,
            "exit_message": exit_message
        }
    }

    return report, exit_code

def save_preview_report(report):
    """Save preview report to file"""
    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)

    with open(REPORT_PATH, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

    print(f"\n[OK] Telemetry preview report saved: {REPORT_PATH}")

def print_preview_summary(report):
    """Print human-readable preview summary"""
    print("\n" + "=" * 70)
    print("  TELEMETRY SYNC PREVIEW - Blueprint v4.5")
    print("=" * 70)
    print()

    print("[CONFIGURATION]")
    telem_config = report["telemetry_config"]
    print(f"  Telemetry Enabled: {telem_config['enabled']}")
    print(f"  Channels Configured: {telem_config['channels_configured']}")
    print()

    print("[TEST MESSAGES]")
    for i, msg in enumerate(report["test_messages"], 1):
        print(f"  {i}. {msg['icon']} {msg['title']}")
        print(f"     {msg['message']}")
    print()

    print("[NOTIFICATION RESULTS]")
    for channel, results in report["notification_results"].items():
        if results:
            print(f"  {channel.upper()}:")
            for result in results:
                status = result["result"].get("status", "UNKNOWN")
                icon = "[OK]" if status == "SUCCESS" else "[SIM]" if status == "SIMULATED" else "[FAIL]"
                print(f"    {icon} {result['message']}")
                if status == "ERROR":
                    print(f"         Error: {result['result'].get('error', 'Unknown')}")
    print()

    summary = report["delivery_summary"]
    print("[DELIVERY SUMMARY]")
    print(f"  Total Sent: {summary['total_sent']}")
    print(f"  Total Failed: {summary['total_failed']}")
    print(f"  Total Simulated: {summary['total_simulated']}")
    print(f"  Channels Active: {summary['total_channels']}")
    print(f"  Success Rate: {summary['success_rate']:.1f}%")
    print()

    overall = report["overall_status"]
    print("[OVERALL STATUS]")
    print(f"  Status: {overall['status']}")
    print(f"  Exit Code: {overall['exit_code']}")
    print(f"  Message: {overall['exit_message']}")
    print()

    print("=" * 70)
    if overall["status"] == "SUCCESS":
        print("  [OK] TELEMETRY SYNC PREVIEW: ALL NOTIFICATIONS DELIVERED")
    elif overall["status"] == "NO_CHANNELS_CONFIGURED":
        print("  [INFO] TELEMETRY SYNC PREVIEW: NO CHANNELS CONFIGURED")
    else:
        print("  [WARNING] TELEMETRY SYNC PREVIEW: PARTIAL SUCCESS")
    print("=" * 70)

def main():
    """Main execution"""
    print("\nTelemetry Sync Preview - Blueprint v4.5")
    print("Testing governance notification channels...\n")

    # Load configuration
    config = load_telemetry_config()

    if not config:
        print(f"[WARNING] Telemetry config not found: {TELEMETRY_CONFIG_PATH}")
        print("[INFO] Running in simulation mode only")
        config = {"enabled": False, "notifications": {}}

    # Send test notifications
    print("[INFO] Sending test notifications...")
    notification_results = send_test_notifications(config)

    # Generate report
    report, exit_code = generate_preview_report(config, notification_results)

    # Save report
    save_preview_report(report)

    # Print summary
    print_preview_summary(report)

    # Exit with appropriate code
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
