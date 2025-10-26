#!/usr/bin/env python3
"""
Unified SoT CLI - Single Entry Point for All Operations

Version: 3.2.1
Status: PRODUCTION

Commands:
  verify-all    - Run complete verification pipeline
  completeness  - Check artifact completeness
  sign          - Apply PQC signatures
  orchestrate   - Run master orchestrator
  health        - System health check
  report        - Generate comprehensive report
  scorecard     - Display current scorecard
"""

import sys
import subprocess
import json
import argparse
from pathlib import Path
from datetime import datetime


class SoTCLI:
    """Unified CLI for SoT operations"""

    def __init__(self):
        self.repo_root = Path(__file__).parents[2]
        self.scripts = {
            'completeness': self.repo_root / '24_meta_orchestration' / 'completeness_scorer_integrated.py',
            'sign': self.repo_root / '21_post_quantum_crypto' / 'tools' / 'sign_all_sot_artifacts_direct.py',
            'orchestrate': self.repo_root / '24_meta_orchestration' / 'sot_master_orchestrator.py',
            'health': self.repo_root / '17_observability' / 'sot_health_monitor.py',
        }

    def run_script(self, script_name: str, timeout: int = 120) -> dict:
        """Execute a script and return result"""
        script_path = self.scripts.get(script_name)

        if not script_path or not script_path.exists():
            return {
                'status': 'not_found',
                'script': script_name,
                'error': f"Script not found: {script_path}"
            }

        try:
            result = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True,
                timeout=timeout
            )

            return {
                'status': 'success' if result.returncode == 0 else 'failed',
                'script': script_name,
                'returncode': result.returncode,
                'output': result.stdout,
                'errors': result.stderr if result.returncode != 0 else None
            }
        except subprocess.TimeoutExpired:
            return {
                'status': 'timeout',
                'script': script_name,
                'error': f'Script timed out after {timeout}s'
            }
        except Exception as e:
            return {
                'status': 'error',
                'script': script_name,
                'error': str(e)
            }

    def cmd_verify_all(self):
        """Run complete verification pipeline"""
        print("="*60)
        print("COMPLETE SoT VERIFICATION PIPELINE")
        print("="*60)
        print()

        # Step 1: Run validator
        print("[1/4] Running SoT Validator...")
        validator_cli = self.repo_root / '12_tooling' / 'cli' / 'sot_validator_complete_cli.py'
        if validator_cli.exists():
            result = subprocess.run(
                [sys.executable, str(validator_cli), '--verify-all'],
                capture_output=True,
                text=True,
                timeout=120
            )
            print(f"  {'✅' if result.returncode == 0 else '❌'} Validation")
        else:
            print(f"  ⚠️  Validator CLI not found")

        steps = [
            ('Completeness Analysis', 'completeness', 120),
            ('PQC Signatures', 'sign', 60),
            ('Health Check', 'health', 60),
        ]

        results = []
        for i, (step_name, script_name, timeout) in enumerate(steps, 2):
            print(f"[{i}/4] Running: {step_name}...")
            result = self.run_script(script_name, timeout)
            results.append(result)

            if result['status'] == 'success':
                print(f"  ✅ {step_name} completed")
            elif result['status'] == 'not_found':
                print(f"  ⚠️  {step_name} (script not found)")
            else:
                print(f"  ❌ {step_name} {result['status']}")
            print()

        # Summary
        print("="*60)
        print("VERIFICATION SUMMARY")
        print("="*60)
        successful = sum(1 for r in results if r['status'] == 'success')
        print(f"Total Steps: {len(results) + 1}")
        print(f"Successful: {successful}")
        print(f"Failed/Skipped: {len(results) + 1 - successful}")

        return 0 if successful == len(results) else 1

    def cmd_completeness(self):
        """Check artifact completeness"""
        print("Running Completeness Analysis...")
        result = self.run_script('completeness')
        print(result['output'] if result.get('output') else f"Status: {result['status']}")
        return result['returncode'] if 'returncode' in result else 1

    def cmd_sign(self):
        """Apply PQC signatures"""
        print("Applying PQC Signatures...")
        result = self.run_script('sign')
        print(result['output'] if result.get('output') else f"Status: {result['status']}")
        return result['returncode'] if 'returncode' in result else 1

    def cmd_orchestrate(self):
        """Run master orchestrator"""
        print("Running Master Orchestrator...")
        result = self.run_script('orchestrate', timeout=300)
        print(result['output'] if result.get('output') else f"Status: {result['status']}")
        return result['returncode'] if 'returncode' in result else 1

    def cmd_health(self):
        """System health check"""
        print("Running Health Check...")
        result = self.run_script('health')
        print(result['output'] if result.get('output') else f"Status: {result['status']}")
        return result['returncode'] if 'returncode' in result else 1

    def cmd_report(self, format='json'):
        """Generate comprehensive report"""
        print("="*60)
        print("COMPREHENSIVE SoT SYSTEM REPORT")
        print("="*60)
        print()

        # Collect all reports
        reports_dir = self.repo_root / '02_audit_logging' / 'reports'

        report_files = {
            'completeness': reports_dir / 'completeness_report_integrated.json',
            'signatures': reports_dir / 'signatures' / 'master_signature_manifest.json',
            'orchestration': reports_dir / 'orchestration_results.json',
        }

        report_data = {}
        for report_name, report_file in report_files.items():
            if report_file.exists():
                try:
                    with open(report_file, encoding='utf-8') as f:
                        report_data[report_name] = json.load(f)
                    print(f"[OK] Loaded {report_name}")
                except Exception as e:
                    print(f"[!] Could not load {report_name}: {e}")
                    report_data[report_name] = {'error': str(e)}
            else:
                print(f"[-] {report_name} not found")
                report_data[report_name] = {'error': 'Not found'}

        # Generate consolidated report
        consolidated = {
            'version': '3.2.1',
            'timestamp': datetime.now().isoformat(),
            'reports': report_data,
            'summary': self._generate_summary(report_data)
        }

        # Save consolidated report
        output_file = reports_dir / f'sot_consolidated_report.{format}'
        output_file.parent.mkdir(parents=True, exist_ok=True)

        if format == 'json':
            output_file.write_text(json.dumps(consolidated, indent=2, ensure_ascii=False))
        else:
            output_file.write_text(self._generate_markdown_report(consolidated))

        print()
        print(f"[OK] Report saved: {output_file.name}")

        return 0

    def cmd_scorecard(self):
        """Display current scorecard"""
        print("="*60)
        print("SoT SYSTEM SCORECARD")
        print("="*60)
        print()

        # Load latest reports
        reports_dir = self.repo_root / '02_audit_logging' / 'reports'

        # Completeness
        completeness_file = reports_dir / 'completeness_report_integrated.json'
        if completeness_file.exists():
            with open(completeness_file, encoding='utf-8') as f:
                completeness = json.load(f)
            print(f"Completeness: {completeness.get('average_completeness', 0):.1f}%")
        else:
            print("Completeness: N/A")

        # Signatures
        sig_file = reports_dir / 'signatures' / 'master_signature_manifest.json'
        if sig_file.exists():
            with open(sig_file, encoding='utf-8') as f:
                signatures = json.load(f)
            print(f"PQC Signatures: {signatures.get('completeness_percentage', 0):.1f}%")
        else:
            print("PQC Signatures: N/A")

        # Orchestration
        orch_file = reports_dir / 'orchestration_results.json'
        if orch_file.exists():
            with open(orch_file, encoding='utf-8') as f:
                orch = json.load(f)
            summary = orch.get('summary', {})
            print(f"Integration: {summary.get('success_rate', 0):.1f}%")
        else:
            print("Integration: N/A")

        print()
        return 0

    def _generate_summary(self, report_data: dict) -> dict:
        """Generate summary from reports"""
        summary = {
            'completeness': 0,
            'signatures': 0,
            'integration': 0,
            'overall_score': 0
        }

        # Completeness
        if 'completeness' in report_data and 'average_completeness' in report_data['completeness']:
            summary['completeness'] = report_data['completeness']['average_completeness']

        # Signatures
        if 'signatures' in report_data and 'completeness_percentage' in report_data['signatures']:
            summary['signatures'] = report_data['signatures']['completeness_percentage']

        # Integration
        if 'orchestration' in report_data and 'summary' in report_data['orchestration']:
            summary['integration'] = report_data['orchestration']['summary'].get('success_rate', 0)

        # Overall score (weighted average)
        summary['overall_score'] = (
            summary['completeness'] * 0.4 +
            summary['signatures'] * 0.3 +
            summary['integration'] * 0.3
        )

        return summary

    def _generate_markdown_report(self, consolidated: dict) -> str:
        """Generate markdown report"""
        summary = consolidated['summary']

        status_msg = "PRODUCTION READY - All systems operational" if summary['overall_score'] >= 95 else "PARTIAL - Some components need attention"

        md = f"""# SoT System Consolidated Report

**Version:** {consolidated['version']}
**Timestamp:** {consolidated['timestamp']}

## Overall Score: {summary['overall_score']:.1f}/100

## Component Scores

- **Completeness:** {summary['completeness']:.1f}%
- **PQC Signatures:** {summary['signatures']:.1f}%
- **Integration:** {summary['integration']:.1f}%

## Status

{status_msg}

---

*Generated by SoT Unified CLI v3.2.1*
"""
        return md


def main():
    parser = argparse.ArgumentParser(
        description='Unified SoT CLI - Single Entry Point',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('command', choices=[
        'verify-all',
        'completeness',
        'sign',
        'orchestrate',
        'health',
        'report',
        'scorecard'
    ], help='Command to execute')

    parser.add_argument('--format', choices=['json', 'md'], default='json',
                        help='Report format (for report command)')

    args = parser.parse_args()

    cli = SoTCLI()

    # Route to command
    command_map = {
        'verify-all': cli.cmd_verify_all,
        'completeness': cli.cmd_completeness,
        'sign': cli.cmd_sign,
        'orchestrate': cli.cmd_orchestrate,
        'health': cli.cmd_health,
        'report': lambda: cli.cmd_report(args.format),
        'scorecard': cli.cmd_scorecard,
    }

    try:
        exit_code = command_map[args.command]()
        return exit_code
    except KeyboardInterrupt:
        print("\n[!] Interrupted by user")
        return 130
    except Exception as e:
        print(f"\n[!] Error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
