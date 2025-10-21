"""
Compliance Alert Monitor

Automatic anomaly detection and alerting for compliance violations.
Triggers alerts when AI layer detects risk increases or framework scores drop below thresholds.

Version: 2025-Q4
Last Updated: 2025-10-07
Maintainer: edubrainboost
Classification: OPERATIONAL - Alert Management
"""

import json
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

class ComplianceAlertMonitor:
    """
    Monitors compliance metrics and triggers alerts on anomalies.

    Alert Triggers:
    - Framework score drops below 90%
    - AI risk level increases to HIGH or CRITICAL
    - Module risk score exceeds threshold
    - Incident rate spike detected
    """

    def __init__(self, repo_root: Optional[Path] = None):
        """Initialize alert monitor."""
        self.repo_root = repo_root or Path(__file__).parent.parent
        self.dashboard_path = self.repo_root / "13_ui_layer/compliance_dashboard_output.json"
        self.ai_prediction_path = self.repo_root / "01_ai_layer/compliance_risk_prediction.json"
        self.alerts_log_path = self.repo_root / "17_observability/logs/compliance_alerts.jsonl"
        self.config_path = self.repo_root / "17_observability/config/alert_config.yaml"

        # Ensure logs directory exists
        self.alerts_log_path.parent.mkdir(parents=True, exist_ok=True)

        # Load configuration
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load alert configuration."""
        if not self.config_path.exists():
            # Return default configuration
            return {
                "thresholds": {
                    "framework_score_critical": 80,
                    "framework_score_warning": 90,
                    "module_risk_score_critical": 50,
                    "module_risk_score_warning": 25,
                    "ai_risk_level_warning": ["HIGH"],
                    "ai_risk_level_critical": ["CRITICAL"]
                },
                "notifications": {
                    "enabled": True,
                    "email": {
                        "enabled": False,  # Disabled by default
                        "smtp_server": "smtp.example.com",
                        "smtp_port": 587,
                        "from_addr": "compliance-alerts@ssid.local",
                        "to_addrs": ["compliance-team@ssid.local"],
                        "use_tls": True
                    },
                    "webhook": {
                        "enabled": False,
                        "url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
                    },
                    "console": {
                        "enabled": True
                    }
                }
            }

        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def check_framework_scores(self) -> List[Dict[str, Any]]:
        """Check framework compliance scores against thresholds."""
        alerts = []

        if not self.dashboard_path.exists():
            return alerts

        with open(self.dashboard_path, 'r', encoding='utf-8') as f:
            dashboard_data = json.load(f)

        frameworks = dashboard_data.get("frameworks", {})

        for framework_name, framework_data in frameworks.items():
            coverage_str = framework_data.get("coverage", "0%")
            try:
                coverage = int(coverage_str.rstrip("%"))
            except (ValueError, AttributeError):
                coverage = 0

            # Check critical threshold
            if coverage < self.config["thresholds"]["framework_score_critical"]:
                alerts.append({
                    "alert_type": "framework_score_critical",
                    "severity": "CRITICAL",
                    "framework": framework_name,
                    "current_score": coverage,
                    "threshold": self.config["thresholds"]["framework_score_critical"],
                    "message": f"{framework_name} compliance score dropped to {coverage}% (threshold: {self.config['thresholds']['framework_score_critical']}%)",
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                })

            # Check warning threshold
            elif coverage < self.config["thresholds"]["framework_score_warning"]:
                alerts.append({
                    "alert_type": "framework_score_warning",
                    "severity": "WARNING",
                    "framework": framework_name,
                    "current_score": coverage,
                    "threshold": self.config["thresholds"]["framework_score_warning"],
                    "message": f"{framework_name} compliance score at {coverage}% (threshold: {self.config['thresholds']['framework_score_warning']}%)",
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                })

        return alerts

    def check_ai_risk_predictions(self) -> List[Dict[str, Any]]:
        """Check AI-predicted risk levels."""
        alerts = []

        if not self.ai_prediction_path.exists():
            return alerts

        with open(self.ai_prediction_path, 'r', encoding='utf-8') as f:
            ai_data = json.load(f)

        # Check overall risk level
        risk_level = ai_data.get("risk_level", "UNKNOWN")

        if risk_level in self.config["thresholds"]["ai_risk_level_critical"]:
            alerts.append({
                "alert_type": "ai_risk_critical",
                "severity": "CRITICAL",
                "risk_level": risk_level,
                "risk_score": ai_data.get("overall_risk_score", 0),
                "message": f"AI detected CRITICAL compliance risk level: {risk_level}",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "recommendations": ai_data.get("recommendations", [])[:3]  # Top 3
            })

        elif risk_level in self.config["thresholds"]["ai_risk_level_warning"]:
            alerts.append({
                "alert_type": "ai_risk_warning",
                "severity": "WARNING",
                "risk_level": risk_level,
                "risk_score": ai_data.get("overall_risk_score", 0),
                "message": f"AI detected HIGH compliance risk level: {risk_level}",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "recommendations": ai_data.get("recommendations", [])[:3]
            })

        # Check high-risk modules
        high_risk_modules = ai_data.get("high_risk_modules", [])

        for module_data in high_risk_modules:
            risk_score = module_data.get("risk_score", 0)

            if risk_score >= self.config["thresholds"]["module_risk_score_critical"]:
                alerts.append({
                    "alert_type": "module_risk_critical",
                    "severity": "CRITICAL",
                    "module": module_data["module"],
                    "risk_score": risk_score,
                    "threshold": self.config["thresholds"]["module_risk_score_critical"],
                    "total_findings": module_data.get("total_findings", 0),
                    "message": f"Module {module_data['module']} has CRITICAL risk score: {risk_score}",
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                })

            elif risk_score >= self.config["thresholds"]["module_risk_score_warning"]:
                alerts.append({
                    "alert_type": "module_risk_warning",
                    "severity": "WARNING",
                    "module": module_data["module"],
                    "risk_score": risk_score,
                    "threshold": self.config["thresholds"]["module_risk_score_warning"],
                    "total_findings": module_data.get("total_findings", 0),
                    "message": f"Module {module_data['module']} has elevated risk score: {risk_score}",
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                })

        return alerts

    def log_alert(self, alert: Dict[str, Any]) -> None:
        """Log alert to JSONL file."""
        with open(self.alerts_log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(alert) + "\n")

    def send_console_notification(self, alert: Dict[str, Any]) -> None:
        """Print alert to console."""
        severity_emoji = {
            "CRITICAL": "🔴",
            "WARNING": "🟡",
            "INFO": "🔵"
        }

        emoji = severity_emoji.get(alert["severity"], "⚪")

        print(f"\n{emoji} COMPLIANCE ALERT [{alert['severity']}]")
        print(f"Type: {alert['alert_type']}")
        print(f"Message: {alert['message']}")
        print(f"Timestamp: {alert['timestamp']}")

        if "recommendations" in alert:
            print("Recommendations:")
            for i, rec in enumerate(alert["recommendations"], 1):
                print(f"  {i}. {rec.get('module', 'N/A')}: {rec.get('recommended_action', 'N/A')}")

        print()

    def send_email_notification(self, alerts: List[Dict[str, Any]]) -> None:
        """Send email notification for alerts."""
        if not self.config["notifications"]["email"]["enabled"]:
            return

        if not alerts:
            return

        email_config = self.config["notifications"]["email"]

        # Build email content
        subject = f"[SSID Compliance Alert] {len(alerts)} Alert(s) Detected"

        body = f"""
SSID Compliance Monitoring Alert

{len(alerts)} compliance alert(s) detected at {datetime.utcnow().isoformat()}Z

"""

        for i, alert in enumerate(alerts, 1):
            body += f"\n{i}. [{alert['severity']}] {alert['message']}\n"
            body += f"   Type: {alert['alert_type']}\n"
            body += f"   Timestamp: {alert['timestamp']}\n"

        body += "\n\nPlease review the compliance dashboard for details."

        # Send email
        try:
            msg = MIMEMultipart()
            msg['From'] = email_config['from_addr']
            msg['To'] = ', '.join(email_config['to_addrs'])
            msg['Subject'] = subject

            msg.attach(MIMEText(body, 'plain'))

            with smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port']) as server:
                if email_config.get('use_tls', True):
                    server.starttls()

                # Note: In production, credentials should be loaded from secure storage
                # server.login(username, password)

                server.send_message(msg)

            print(f"✅ Email notification sent to {', '.join(email_config['to_addrs'])}")

        except Exception as e:
            print(f"❌ Failed to send email notification: {e}")

    def run_monitoring_cycle(self) -> Dict[str, Any]:
        """Run a complete monitoring cycle and return results."""
        print("\n" + "=" * 80)
        print("COMPLIANCE ALERT MONITORING CYCLE".center(80))
        print("=" * 80)
        print(f"Started: {datetime.utcnow().isoformat()}Z\n")

        all_alerts = []

        # Check framework scores
        print("Checking framework scores...")
        framework_alerts = self.check_framework_scores()
        all_alerts.extend(framework_alerts)
        print(f"  Found {len(framework_alerts)} alert(s)")

        # Check AI predictions
        print("Checking AI risk predictions...")
        ai_alerts = self.check_ai_risk_predictions()
        all_alerts.extend(ai_alerts)
        print(f"  Found {len(ai_alerts)} alert(s)")

        # Log all alerts
        for alert in all_alerts:
            self.log_alert(alert)

        # Send notifications
        if all_alerts and self.config["notifications"]["enabled"]:
            print("\nSending notifications...")

            if self.config["notifications"]["console"]["enabled"]:
                for alert in all_alerts:
                    self.send_console_notification(alert)

            if self.config["notifications"]["email"]["enabled"]:
                self.send_email_notification(all_alerts)

        print(f"\nCompleted: {datetime.utcnow().isoformat()}Z")
        print(f"Total Alerts: {len(all_alerts)}")
        print("=" * 80 + "\n")

        return {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "total_alerts": len(all_alerts),
            "alerts_by_severity": {
                "CRITICAL": sum(1 for a in all_alerts if a["severity"] == "CRITICAL"),
                "WARNING": sum(1 for a in all_alerts if a["severity"] == "WARNING"),
                "INFO": sum(1 for a in all_alerts if a["severity"] == "INFO")
            },
            "alerts": all_alerts
        }

def main():
    """Main entry point for compliance alert monitoring."""
    monitor = ComplianceAlertMonitor()

    # Run monitoring cycle
    results = monitor.run_monitoring_cycle()

    # Save results
    results_path = Path(__file__).parent / "logs" / "latest_monitoring_results.json"
    results_path.parent.mkdir(parents=True, exist_ok=True)

    with open(results_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"📊 Results saved to: {results_path}\n")

if __name__ == "__main__":
    main()
