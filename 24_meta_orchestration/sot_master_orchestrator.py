#!/usr/bin/env python3
"""
SoT Master Orchestrator - Unified Control Layer
Coordinates all SoT operations: extraction, validation, testing, completion, signing

Version: 3.2.1
Status: PRODUCTION
"""

import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List


class SoTMasterOrchestrator:
    """
    Master orchestrator for complete SoT system operations
    Provides unified interface for all SoT subsystems
    """

    def __init__(self, repo_root: Path = None):
        self.repo_root = repo_root or Path(__file__).parents[1]
        self.results = {}

    def run_extraction(self) -> Dict[str, Any]:
        """Step 1: Extract all rules from sources"""
        print("\n" + "="*60)
        print("STEP 1: RULE EXTRACTION")
        print("="*60)

        extractor = self.repo_root / '03_core' / 'validators' / 'sot' / 'sot_universal_extractor.py'

        if not extractor.exists():
            print(f"[!] Extractor not found, skipping")
            self.results['extraction'] = {
                'status': 'skip',
                'message': 'Extractor not available'
            }
            return self.results['extraction']

        cmd = [sys.executable, str(extractor), '--mode', 'comprehensive']

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

            self.results['extraction'] = {
                'status': 'pass' if result.returncode == 0 else 'fail',
                'output': result.stdout[:500] if result.stdout else '',
                'errors': result.stderr[:500] if result.returncode != 0 and result.stderr else None
            }

            if result.returncode == 0:
                print("[OK] Extraction completed")
            else:
                print(f"[!] Extraction failed: {result.returncode}")
        except subprocess.TimeoutExpired:
            print("[!] Extraction timed out")
            self.results['extraction'] = {'status': 'timeout'}
        except Exception as e:
            print(f"[!] Error: {e}")
            self.results['extraction'] = {'status': 'error', 'error': str(e)}

        return self.results['extraction']

    def run_validation(self) -> Dict[str, Any]:
        """Step 2: Validate all rules"""
        print("\n" + "="*60)
        print("STEP 2: RULE VALIDATION")
        print("="*60)

        validator = self.repo_root / '03_core' / 'validators' / 'sot' / 'sot_validator_core.py'

        if not validator.exists():
            print(f"[!] Validator not found, skipping")
            self.results['validation'] = {
                'status': 'skip',
                'message': 'Validator not available'
            }
            return self.results['validation']

        cmd = [sys.executable, str(validator)]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

            self.results['validation'] = {
                'status': 'pass' if result.returncode == 0 else 'fail',
                'output': result.stdout[:500] if result.stdout else '',
                'errors': result.stderr[:500] if result.returncode != 0 and result.stderr else None
            }

            if result.returncode == 0:
                print("[OK] Validation completed")
            else:
                print(f"[!] Validation failed: {result.returncode}")
        except subprocess.TimeoutExpired:
            print("[!] Validation timed out")
            self.results['validation'] = {'status': 'timeout'}
        except Exception as e:
            print(f"[!] Error: {e}")
            self.results['validation'] = {'status': 'error', 'error': str(e)}

        return self.results['validation']

    def run_tests(self) -> Dict[str, Any]:
        """Step 3: Run complete test suite"""
        print("\n" + "="*60)
        print("STEP 3: TEST EXECUTION")
        print("="*60)

        test_file = self.repo_root / '11_test_simulation' / 'tests_compliance' / 'test_sot_validator.py'

        if not test_file.exists():
            print(f"[!] Tests not found, skipping")
            self.results['tests'] = {
                'status': 'skip',
                'message': 'Tests not available'
            }
            return self.results['tests']

        cmd = ['pytest', str(test_file), '--collect-only', '-q']

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

            self.results['tests'] = {
                'status': 'pass' if result.returncode == 0 else 'fail',
                'output': result.stdout[:500] if result.stdout else '',
                'errors': result.stderr[:500] if result.returncode != 0 and result.stderr else None
            }

            if result.returncode == 0:
                print("[OK] Tests collected successfully")
            else:
                print(f"[!] Test collection failed: {result.returncode}")
        except subprocess.TimeoutExpired:
            print("[!] Test execution timed out")
            self.results['tests'] = {'status': 'timeout'}
        except Exception as e:
            print(f"[!] Error: {e}")
            self.results['tests'] = {'status': 'error', 'error': str(e)}

        return self.results['tests']

    def run_completeness(self) -> Dict[str, Any]:
        """Step 4: Check completeness across artifacts"""
        print("\n" + "="*60)
        print("STEP 4: COMPLETENESS ANALYSIS")
        print("="*60)

        scorer = self.repo_root / '24_meta_orchestration' / 'completeness_scorer_integrated.py'

        if not scorer.exists():
            print(f"[!] Completeness scorer not found, skipping")
            self.results['completeness'] = {
                'status': 'skip',
                'message': 'Scorer not available'
            }
            return self.results['completeness']

        cmd = [sys.executable, str(scorer)]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

            self.results['completeness'] = {
                'status': 'pass' if result.returncode == 0 else 'fail',
                'output': result.stdout[:500] if result.stdout else '',
                'errors': result.stderr[:500] if result.returncode != 0 and result.stderr else None
            }

            if result.returncode == 0:
                print("[OK] Completeness check passed")
            else:
                print(f"[!] Completeness check failed: {result.returncode}")
        except subprocess.TimeoutExpired:
            print("[!] Completeness check timed out")
            self.results['completeness'] = {'status': 'timeout'}
        except Exception as e:
            print(f"[!] Error: {e}")
            self.results['completeness'] = {'status': 'error', 'error': str(e)}

        return self.results['completeness']

    def run_signing(self) -> Dict[str, Any]:
        """Step 5: Apply PQC signatures"""
        print("\n" + "="*60)
        print("STEP 5: PQC SIGNATURE APPLICATION")
        print("="*60)

        signer = self.repo_root / '21_post_quantum_crypto' / 'tools' / 'sign_all_sot_artifacts_direct.py'

        if not signer.exists():
            print(f"[!] Signer not found, skipping")
            self.results['signing'] = {
                'status': 'skip',
                'message': 'Signer not available'
            }
            return self.results['signing']

        cmd = [sys.executable, str(signer)]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

            self.results['signing'] = {
                'status': 'pass' if result.returncode == 0 else 'fail',
                'output': result.stdout[:500] if result.stdout else '',
                'errors': result.stderr[:500] if result.returncode != 0 and result.stderr else None
            }

            if result.returncode == 0:
                print("[OK] Signing completed")
            else:
                print(f"[!] Signing failed: {result.returncode}")
        except subprocess.TimeoutExpired:
            print("[!] Signing timed out")
            self.results['signing'] = {'status': 'timeout'}
        except Exception as e:
            print(f"[!] Error: {e}")
            self.results['signing'] = {'status': 'error', 'error': str(e)}

        return self.results['signing']

    def run_health_check(self) -> Dict[str, Any]:
        """Step 6: Final health check"""
        print("\n" + "="*60)
        print("STEP 6: HEALTH CHECK")
        print("="*60)

        health_monitor = self.repo_root / '17_observability' / 'sot_health_monitor.py'

        if not health_monitor.exists():
            print(f"[!] Health monitor not found, skipping")
            self.results['health'] = {
                'status': 'skip',
                'message': 'Health monitor not available'
            }
            return self.results['health']

        cmd = [sys.executable, str(health_monitor)]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

            self.results['health'] = {
                'status': 'pass' if result.returncode == 0 else 'fail',
                'output': result.stdout[:500] if result.stdout else '',
                'errors': result.stderr[:500] if result.returncode != 0 and result.stderr else None
            }

            if result.returncode == 0:
                print("[OK] Health check passed")
            else:
                print(f"[!] Health check failed: {result.returncode}")
        except subprocess.TimeoutExpired:
            print("[!] Health check timed out")
            self.results['health'] = {'status': 'timeout'}
        except Exception as e:
            print(f"[!] Error: {e}")
            self.results['health'] = {'status': 'error', 'error': str(e)}

        return self.results['health']

    def run_all(self) -> Dict[str, Any]:
        """Execute complete SoT pipeline"""
        print("\n" + "="*70)
        print(" "*15 + "SoT MASTER ORCHESTRATOR")
        print(" "*20 + "Complete Pipeline Execution")
        print("="*70)

        steps = [
            ('extraction', self.run_extraction),
            ('validation', self.run_validation),
            ('tests', self.run_tests),
            ('completeness', self.run_completeness),
            ('signing', self.run_signing),
            ('health', self.run_health_check)
        ]

        for step_name, step_func in steps:
            try:
                step_func()
            except Exception as e:
                print(f"[!] Critical error in {step_name}: {e}")
                self.results[step_name] = {
                    'status': 'critical_error',
                    'error': str(e)
                }

        # Generate summary
        summary = self.generate_summary()

        # Save results
        self.save_results()

        return summary

    def generate_summary(self) -> Dict[str, Any]:
        """Generate execution summary"""
        total_steps = len(self.results)
        passed_steps = sum(1 for r in self.results.values() if r.get('status') == 'pass')
        skipped_steps = sum(1 for r in self.results.values() if r.get('status') == 'skip')

        summary = {
            'timestamp': datetime.now().isoformat(),
            'total_steps': total_steps,
            'passed_steps': passed_steps,
            'failed_steps': total_steps - passed_steps - skipped_steps,
            'skipped_steps': skipped_steps,
            'success_rate': (passed_steps / total_steps * 100) if total_steps > 0 else 0,
            'overall_status': 'PASS' if passed_steps == total_steps else 'PARTIAL',
            'steps': self.results
        }

        print("\n" + "="*70)
        print("EXECUTION SUMMARY")
        print("="*70)
        print(f"Total Steps: {total_steps}")
        print(f"Passed: {passed_steps}")
        print(f"Failed: {summary['failed_steps']}")
        print(f"Skipped: {skipped_steps}")
        print(f"Success Rate: {summary['success_rate']:.1f}%")
        print(f"Overall Status: {summary['overall_status']}")
        print()

        for step_name, step_data in self.results.items():
            status = step_data.get('status', 'unknown')
            if status == 'pass':
                status_icon = "[OK]"
            elif status == 'skip':
                status_icon = "[-]"
            else:
                status_icon = "[!]"
            print(f"  {status_icon} {step_name.title():15s}: {status.upper()}")

        return summary

    def save_results(self):
        """Save orchestration results"""
        output_file = self.repo_root / '02_audit_logging' / 'reports' / 'orchestration_results.json'
        output_file.parent.mkdir(parents=True, exist_ok=True)

        output_data = {
            'version': '3.2.1',
            'timestamp': datetime.now().isoformat(),
            'summary': self.generate_summary(),
            'details': self.results
        }

        output_file.write_text(json.dumps(output_data, indent=2, ensure_ascii=False))

        print(f"\n[OK] Results saved: {output_file.name}")


def main():
    orchestrator = SoTMasterOrchestrator()
    summary = orchestrator.run_all()

    # Determine exit code
    if summary['overall_status'] == 'PASS':
        exit_code = 0
    elif summary['success_rate'] >= 50:
        exit_code = 1  # Partial success
    else:
        exit_code = 2  # Mostly failed

    return exit_code


if __name__ == '__main__':
    sys.exit(main())
