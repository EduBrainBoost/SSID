#!/usr/bin/env python3
"""
SoT Continuous Monitoring System
Automated health checks and alerting for SoT system

Version: 1.0.0
Status: PRODUCTION
"""

import sys
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Any


class SoTContinuousMonitor:
    """Continuous monitoring daemon for SoT system"""

    def __init__(self, repo_root: Path = None):
        self.repo_root = repo_root or Path(__file__).parents[1]
        self.check_interval = 3600  # 1 hour
        self.alert_threshold = 95.0  # Alert if score drops below this

    def run_health_check(self) -> Dict[str, Any]:
        """Execute health check"""
        health_script = self.repo_root / '17_observability' / 'sot_health_monitor.py'

        if not health_script.exists():
            return {
                'status': 'error',
                'message': 'Health monitor not found'
            }

        try:
            result = subprocess.run(
                [sys.executable, str(health_script)],
                capture_output=True,
                text=True,
                timeout=60
            )

            return {
                'status': 'success' if result.returncode == 0 else 'failed',
                'returncode': result.returncode,
                'output': result.stdout[:500],
                'timestamp': datetime.now().isoformat()
            }
        except subprocess.TimeoutExpired:
            return {
                'status': 'timeout',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def check_completeness(self) -> Dict[str, Any]:
        """Check completeness score"""
        report_file = self.repo_root / '02_audit_logging' / 'reports' / 'completeness_report_integrated.json'

        if not report_file.exists():
            return {
                'status': 'not_found',
                'score': 0
            }

        try:
            with open(report_file, encoding='utf-8') as f:
                data = json.load(f)

            return {
                'status': 'ok',
                'score': data.get('average_completeness', 0),
                'timestamp': data.get('timestamp')
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'score': 0
            }

    def check_signatures(self) -> Dict[str, Any]:
        """Check signature validity"""
        sig_file = self.repo_root / '02_audit_logging' / 'reports' / 'signatures' / 'master_signature_manifest.json'

        if not sig_file.exists():
            return {
                'status': 'not_found',
                'score': 0
            }

        try:
            with open(sig_file, encoding='utf-8') as f:
                data = json.load(f)

            return {
                'status': 'ok',
                'score': data.get('completeness_percentage', 0),
                'timestamp': data.get('timestamp')
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'score': 0
            }

    def generate_alert(self, alert_type: str, message: str, severity: str = 'warning'):
        """Generate alert"""
        alert = {
            'timestamp': datetime.now().isoformat(),
            'type': alert_type,
            'severity': severity,
            'message': message
        }

        # Save alert
        alerts_dir = self.repo_root / '17_observability' / 'alerts'
        alerts_dir.mkdir(parents=True, exist_ok=True)

        alert_file = alerts_dir / f'alert_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        alert_file.write_text(json.dumps(alert, indent=2))

        print(f"[ALERT] {severity.upper()}: {message}")

        return alert

    def run_monitoring_cycle(self) -> Dict[str, Any]:
        """Execute one monitoring cycle"""
        print(f"\n{'='*60}")
        print(f"Monitoring Cycle: {datetime.now().isoformat()}")
        print(f"{'='*60}")

        # Check all components
        completeness = self.check_completeness()
        signatures = self.check_signatures()
        health = self.run_health_check()

        results = {
            'timestamp': datetime.now().isoformat(),
            'completeness': completeness,
            'signatures': signatures,
            'health': health
        }

        # Check for alerts
        if completeness.get('score', 0) < self.alert_threshold:
            self.generate_alert(
                'completeness_drop',
                f"Completeness dropped to {completeness['score']:.1f}%",
                'critical'
            )

        if signatures.get('score', 0) < self.alert_threshold:
            self.generate_alert(
                'signature_issue',
                f"Signature coverage at {signatures['score']:.1f}%",
                'warning'
            )

        # Save monitoring result
        log_file = self.repo_root / '17_observability' / 'monitoring_log.jsonl'
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(results) + '\n')

        # Display summary
        print(f"\nCompleteness: {completeness.get('score', 0):.1f}%")
        print(f"Signatures: {signatures.get('score', 0):.1f}%")
        print(f"Health: {health.get('status', 'unknown')}")

        return results

    def run_daemon(self, cycles: int = None):
        """Run monitoring daemon"""
        print("="*60)
        print("SoT Continuous Monitoring System")
        print("="*60)
        print(f"Check interval: {self.check_interval}s")
        print(f"Alert threshold: {self.alert_threshold}%")
        print()

        cycle_count = 0
        try:
            while True:
                self.run_monitoring_cycle()
                cycle_count += 1

                if cycles and cycle_count >= cycles:
                    print(f"\n[OK] Completed {cycle_count} cycles")
                    break

                if not cycles:
                    print(f"\nNext check in {self.check_interval}s...")
                    time.sleep(self.check_interval)

        except KeyboardInterrupt:
            print("\n[!] Monitoring stopped by user")
        except Exception as e:
            print(f"\n[!] Error: {e}")

    def run_single_check(self):
        """Run single monitoring check"""
        result = self.run_monitoring_cycle()
        return 0 if result['completeness'].get('score', 0) >= self.alert_threshold else 1


def main():
    import argparse

    parser = argparse.ArgumentParser(description='SoT Continuous Monitoring')
    parser.add_argument('--daemon', action='store_true', help='Run as daemon')
    parser.add_argument('--cycles', type=int, help='Number of cycles (for daemon mode)')
    parser.add_argument('--interval', type=int, default=3600, help='Check interval in seconds')

    args = parser.parse_args()

    monitor = SoTContinuousMonitor()

    if args.interval:
        monitor.check_interval = args.interval

    if args.daemon:
        monitor.run_daemon(cycles=args.cycles)
        return 0
    else:
        return monitor.run_single_check()


if __name__ == '__main__':
    sys.exit(main())
