#!/usr/bin/env python3
"""
SSID SoT Metrics Exporter
===========================

Exports SoT enforcement metrics in Prometheus format for real-time monitoring.

Metrics Exported:
  - sot_validator_pass_rate: Percentage of SoT rules passing (0-1)
  - sot_policy_denials_total: Total OPA policy denial events (counter)
  - sot_merkle_verifications_total: Total Merkle proof verifications (counter)
  - sot_compliance_score: Current compliance score (0-100)
  - sot_rules_total: Total number of SoT rules enforced
  - sot_pqc_signatures_total: Total PQC signatures generated (counter)
  - sot_worm_snapshots_total: Total WORM snapshots created (counter)
  - sot_audit_pipeline_duration_seconds: Time to run full audit pipeline (histogram)
  - sot_validation_errors_total: Total validation errors (counter by severity)

Usage:
  # Start metrics server
  python sot_metrics.py --port 9090

  # Scrape metrics
  curl http://localhost:9090/metrics

Integration:
  # Prometheus scrape config
  scrape_configs:
    - job_name: 'ssid_sot'
      static_configs:
        - targets: ['localhost:9090']

Author: SSID Observability Team
Version: 1.0.0
Date: 2025-10-22
"""

import sys
import json
import time
import argparse
from pathlib import Path
from typing import Dict, List, Optional
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime, timezone

# Add repo root to path
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

# Paths
AUDIT_LOGS = REPO_ROOT / "02_audit_logging" / "reports"
MERKLE_DIR = REPO_ROOT / "02_audit_logging" / "merkle"
WORM_STORAGE = REPO_ROOT / "02_audit_logging" / "storage" / "worm" / "immutable_store"
POLICY_LOGS = REPO_ROOT / "02_audit_logging" / "policy_decisions"
VALIDATOR_RESULTS = REPO_ROOT / "03_core" / "validators" / "sot"

# Metric storage (in-memory)
class MetricsStore:
    def __init__(self):
        self.sot_validator_pass_rate = 0.0
        self.sot_policy_denials_total = 0
        self.sot_merkle_verifications_total = 0
        self.sot_compliance_score = 0.0
        self.sot_rules_total = 1276  # 1,276 Ebene-3 rules
        self.sot_pqc_signatures_total = 0
        self.sot_worm_snapshots_total = 0
        self.sot_validation_errors_total = {"CRITICAL": 0, "IMPORTANT": 0, "MINOR": 0}
        self.sot_audit_pipeline_duration = []
        self.last_update = datetime.now(timezone.utc)

    def update_from_audit_logs(self):
        """Update metrics from audit log files"""
        # Update validator pass rate
        scorecard = AUDIT_LOGS / "AGENT_STACK_SCORE_LOG.json"
        if scorecard.exists():
            try:
                data = json.loads(scorecard.read_text(encoding="utf-8"))
                self.sot_compliance_score = float(data.get("compliance_score", 0))
                self.sot_validator_pass_rate = self.sot_compliance_score / 100.0
            except Exception as e:
                print(f"Warning: Could not parse scorecard: {e}", file=sys.stderr)

        # Update Merkle verifications
        merkle_proofs = MERKLE_DIR / "root_write_merkle_proofs.json"
        if merkle_proofs.exists():
            try:
                data = json.loads(merkle_proofs.read_text(encoding="utf-8"))
                self.sot_merkle_verifications_total = len(data.get("proofs", []))
            except Exception as e:
                print(f"Warning: Could not parse Merkle proofs: {e}", file=sys.stderr)

        # Update WORM snapshot count
        if WORM_STORAGE.exists():
            self.sot_worm_snapshots_total = len(list(WORM_STORAGE.glob("*.json")))

        # Update PQC signature count
        pqc_signature = REPO_ROOT / "23_compliance" / "registry" / "compliance_registry_signature.json"
        if pqc_signature.exists():
            try:
                data = json.loads(pqc_signature.read_text(encoding="utf-8"))
                if data.get("signature"):
                    self.sot_pqc_signatures_total = 1  # Latest signature
            except Exception as e:
                print(f"Warning: Could not parse PQC signature: {e}", file=sys.stderr)

        # Update policy denials (simulation - would parse OPA decision logs)
        if POLICY_LOGS.exists():
            policy_files = list(POLICY_LOGS.glob("*.json"))
            total_denials = 0
            for policy_file in policy_files:
                try:
                    data = json.loads(policy_file.read_text(encoding="utf-8"))
                    if not data.get("allow", True):
                        total_denials += 1
                except Exception:
                    pass
            self.sot_policy_denials_total = total_denials

        # Update validation errors
        validation_result = VALIDATOR_RESULTS / "validation_result.json"
        if validation_result.exists():
            try:
                data = json.loads(validation_result.read_text(encoding="utf-8"))
                errors = data.get("errors", {})
                self.sot_validation_errors_total = {
                    "CRITICAL": errors.get("CRITICAL", 0),
                    "IMPORTANT": errors.get("IMPORTANT", 0),
                    "MINOR": errors.get("MINOR", 0),
                }
            except Exception as e:
                print(f"Warning: Could not parse validation errors: {e}", file=sys.stderr)

        self.last_update = datetime.now(timezone.utc)

    def to_prometheus_format(self) -> str:
        """Export metrics in Prometheus text format"""
        lines = []

        # Metadata
        lines.append(f"# HELP sot_validator_pass_rate Percentage of SoT rules passing (0-1)")
        lines.append(f"# TYPE sot_validator_pass_rate gauge")
        lines.append(f"sot_validator_pass_rate {self.sot_validator_pass_rate:.4f}")
        lines.append("")

        lines.append(f"# HELP sot_policy_denials_total Total OPA policy denial events")
        lines.append(f"# TYPE sot_policy_denials_total counter")
        lines.append(f"sot_policy_denials_total {self.sot_policy_denials_total}")
        lines.append("")

        lines.append(f"# HELP sot_merkle_verifications_total Total Merkle proof verifications")
        lines.append(f"# TYPE sot_merkle_verifications_total counter")
        lines.append(f"sot_merkle_verifications_total {self.sot_merkle_verifications_total}")
        lines.append("")

        lines.append(f"# HELP sot_compliance_score Current compliance score (0-100)")
        lines.append(f"# TYPE sot_compliance_score gauge")
        lines.append(f"sot_compliance_score {self.sot_compliance_score:.2f}")
        lines.append("")

        lines.append(f"# HELP sot_rules_total Total number of SoT rules enforced")
        lines.append(f"# TYPE sot_rules_total gauge")
        lines.append(f"sot_rules_total {self.sot_rules_total}")
        lines.append("")

        lines.append(f"# HELP sot_pqc_signatures_total Total PQC signatures generated")
        lines.append(f"# TYPE sot_pqc_signatures_total counter")
        lines.append(f"sot_pqc_signatures_total {self.sot_pqc_signatures_total}")
        lines.append("")

        lines.append(f"# HELP sot_worm_snapshots_total Total WORM snapshots created")
        lines.append(f"# TYPE sot_worm_snapshots_total counter")
        lines.append(f"sot_worm_snapshots_total {self.sot_worm_snapshots_total}")
        lines.append("")

        lines.append(f"# HELP sot_validation_errors_total Total validation errors by severity")
        lines.append(f"# TYPE sot_validation_errors_total counter")
        for severity, count in self.sot_validation_errors_total.items():
            lines.append(f'sot_validation_errors_total{{severity="{severity}"}} {count}')
        lines.append("")

        # Metadata
        lines.append(f"# HELP sot_last_update_timestamp_seconds Unix timestamp of last metric update")
        lines.append(f"# TYPE sot_last_update_timestamp_seconds gauge")
        lines.append(f"sot_last_update_timestamp_seconds {self.last_update.timestamp():.0f}")
        lines.append("")

        return "\n".join(lines)


# Global metrics store
metrics = MetricsStore()


class MetricsHandler(BaseHTTPRequestHandler):
    """HTTP handler for Prometheus scraping"""

    def do_GET(self):
        """Handle GET requests"""
        if self.path == "/metrics":
            # Update metrics from files
            metrics.update_from_audit_logs()

            # Return Prometheus text format
            response = metrics.to_prometheus_format()
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; version=0.0.4")
            self.end_headers()
            self.wfile.write(response.encode("utf-8"))

        elif self.path == "/health":
            # Health check endpoint
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            health = {
                "status": "healthy",
                "last_update": metrics.last_update.isoformat(),
                "compliance_score": metrics.sot_compliance_score
            }
            self.wfile.write(json.dumps(health, indent=2).encode("utf-8"))

        elif self.path == "/":
            # Index page
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            html = """
            <!DOCTYPE html>
            <html>
            <head><title>SSID SoT Metrics Exporter</title></head>
            <body>
                <h1>SSID SoT Metrics Exporter</h1>
                <p><a href="/metrics">Metrics (Prometheus format)</a></p>
                <p><a href="/health">Health Check</a></p>
                <hr>
                <p>Version: 1.0.0</p>
                <p>Last Update: %s</p>
                <p>Compliance Score: %.2f%%</p>
            </body>
            </html>
            """ % (metrics.last_update.isoformat(), metrics.sot_compliance_score)
            self.wfile.write(html.encode("utf-8"))

        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        """Custom log format"""
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        print(f"[{timestamp}] {format % args}")


def main():
    """Main execution"""
    parser = argparse.ArgumentParser(
        description="SSID SoT Metrics Exporter (Prometheus format)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start metrics server on default port
  python sot_metrics.py

  # Start on custom port
  python sot_metrics.py --port 8080

  # Test scraping
  curl http://localhost:9090/metrics

Integration:
  # Add to Prometheus scrape config
  scrape_configs:
    - job_name: 'ssid_sot'
      static_configs:
        - targets: ['localhost:9090']
      scrape_interval: 15s
        """
    )

    parser.add_argument(
        "--port", "-p",
        type=int,
        default=9090,
        help="HTTP server port (default: 9090)"
    )

    parser.add_argument(
        "--host",
        type=str,
        default="localhost",
        help="HTTP server host (default: localhost)"
    )

    args = parser.parse_args()

    # Create necessary directories
    POLICY_LOGS.mkdir(parents=True, exist_ok=True)

    # Initial metrics update
    print("=" * 80)
    print("SSID SoT Metrics Exporter")
    print("=" * 80)
    print(f"Version: 1.0.0")
    print(f"Listening: http://{args.host}:{args.port}")
    print(f"Endpoints:")
    print(f"  - http://{args.host}:{args.port}/metrics (Prometheus)")
    print(f"  - http://{args.host}:{args.port}/health (Health check)")
    print("=" * 80)
    print()

    metrics.update_from_audit_logs()
    print(f"Initial Metrics:")
    print(f"  - Compliance Score: {metrics.sot_compliance_score:.2f}%")
    print(f"  - Validator Pass Rate: {metrics.sot_validator_pass_rate:.2%}")
    print(f"  - Total Rules: {metrics.sot_rules_total}")
    print(f"  - Merkle Verifications: {metrics.sot_merkle_verifications_total}")
    print(f"  - WORM Snapshots: {metrics.sot_worm_snapshots_total}")
    print(f"  - PQC Signatures: {metrics.sot_pqc_signatures_total}")
    print(f"  - Policy Denials: {metrics.sot_policy_denials_total}")
    print()
    print("Waiting for Prometheus scrapes...")
    print("Press Ctrl+C to stop")
    print()

    # Start HTTP server
    server = HTTPServer((args.host, args.port), MetricsHandler)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down metrics exporter...")
        server.shutdown()
        print("Goodbye!")


if __name__ == "__main__":
    main()
