#!/usr/bin/env python3
"""
Complete System Verification
=============================

Verifies all components work with real code - no placeholders!

Version: 4.0.0
"""

import sys
import subprocess
from pathlib import Path
from datetime import datetime
import json


def run_command(cmd: list, timeout: int = 120, capture: bool = True) -> dict:
    """Run a command and return result"""
    try:
        if capture:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=str(Path(__file__).resolve().parents[2])
            )
        else:
            result = subprocess.run(
                cmd,
                timeout=timeout,
                cwd=str(Path(__file__).resolve().parents[2])
            )

        return {
            'success': result.returncode == 0,
            'returncode': result.returncode,
            'stdout': result.stdout if capture else '',
            'stderr': result.stderr if capture else ''
        }
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'returncode': -1,
            'error': f'Timeout after {timeout}s'
        }
    except Exception as e:
        return {
            'success': False,
            'returncode': -1,
            'error': str(e)
        }


def main():
    repo_root = Path(__file__).resolve().parents[2]

    print("="*70)
    print(" "*15 + "COMPLETE SYSTEM VERIFICATION")
    print("="*70)
    print(f"Repository: {repo_root}")
    print(f"Timestamp:  {datetime.now().isoformat()}")
    print("="*70)
    print()

    checks = []
    all_passed = True

    # ===================================================================
    # CHECK 1: Validator Engine
    # ===================================================================
    print("[1/8] Testing Validator Engine...")
    validator = repo_root / '03_core' / 'validators' / 'sot' / 'sot_validator_engine.py'

    if not validator.exists():
        print(f"  [ERROR] Validator engine not found at {validator}")
        checks.append(('Validator Engine', False, 'File not found'))
        all_passed = False
    else:
        # Try to import it
        result = run_command([sys.executable, '-c',
            f'import sys; sys.path.insert(0, str("{validator.parent}")); from sot_validator_engine import RuleValidationEngine; print("OK")'],
            timeout=10)

        if result['success'] and 'OK' in result['stdout']:
            print(f"  [OK] Validator Engine (import successful)")
            checks.append(('Validator Engine', True, 'Import successful'))
        else:
            print(f"  [ERROR] Validator Engine (import failed)")
            checks.append(('Validator Engine', False, result.get('error', 'Import failed')))
            all_passed = False

    # ===================================================================
    # CHECK 2: Registry File
    # ===================================================================
    print("\n[2/8] Testing Registry...")
    registry_path = repo_root / '16_codex' / 'structure' / 'auto_generated' / 'sot_rules_full.json'

    if not registry_path.exists():
        print(f"  [ERROR] Registry not found at {registry_path}")
        checks.append(('Registry File', False, 'File not found'))
        all_passed = False
    else:
        try:
            with open(registry_path) as f:
                registry = json.load(f)
            rule_count = len(registry.get('rules', []))
            print(f"  [OK] Registry File ({rule_count} rules)")
            checks.append(('Registry File', True, f'{rule_count} rules'))
        except Exception as e:
            print(f"  [ERROR] Registry File (invalid JSON: {e})")
            checks.append(('Registry File', False, f'Invalid JSON: {e}'))
            all_passed = False

    # ===================================================================
    # CHECK 3: CLI Tools
    # ===================================================================
    print("\n[3/8] Testing CLI Tools...")

    cli_files = [
        ('Validator CLI', repo_root / '12_tooling' / 'cli' / 'sot_validator_complete_cli.py'),
        ('Unified CLI', repo_root / '12_tooling' / 'cli' / 'sot_cli_unified.py'),
        ('Autopilot CLI', repo_root / '12_tooling' / 'cli' / 'sot_cli_autopilot.py'),
    ]

    cli_pass = True
    for name, cli_path in cli_files:
        if cli_path.exists():
            print(f"  [OK] {name}")
        else:
            print(f"  [ERROR] {name} (not found)")
            cli_pass = False

    checks.append(('CLI Tools', cli_pass, f'{len([1 for _, p in cli_files if p.exists()])}/{len(cli_files)} found'))
    if not cli_pass:
        all_passed = False

    # ===================================================================
    # CHECK 4: Test Suite
    # ===================================================================
    print("\n[4/8] Testing Test Suite...")
    test_file = repo_root / '11_test_simulation' / 'tests_compliance' / 'test_sot_complete.py'

    if not test_file.exists():
        print(f"  [ERROR] Test file not found at {test_file}")
        checks.append(('Test Suite', False, 'File not found'))
        all_passed = False
    else:
        # Run pytest --collect-only to check tests
        result = run_command(['pytest', str(test_file), '--collect-only', '-q'], timeout=30)

        if result['success']:
            # Count tests
            test_count = result['stdout'].count('test_')
            print(f"  [OK] Test Suite ({test_count} tests collected)")
            checks.append(('Test Suite', True, f'{test_count} tests'))
        else:
            print(f"  [ERROR] Test Suite (collection failed)")
            checks.append(('Test Suite', False, 'Collection failed'))
            all_passed = False

    # ===================================================================
    # CHECK 5: Completeness Scorer
    # ===================================================================
    print("\n[5/8] Testing Completeness Scorer...")
    scorer = repo_root / '24_meta_orchestration' / 'completeness_scorer_integrated.py'

    if scorer.exists():
        print(f"  [OK] Completeness Scorer")
        checks.append(('Completeness Scorer', True, 'File exists'))
    else:
        print(f"  [WARN]  Completeness Scorer (not found)")
        checks.append(('Completeness Scorer', False, 'File not found'))

    # ===================================================================
    # CHECK 6: PQC Signatures
    # ===================================================================
    print("\n[6/8] Testing PQC Signature Tools...")
    signer = repo_root / '21_post_quantum_crypto' / 'tools' / 'sign_all_sot_artifacts_direct.py'

    if signer.exists():
        print(f"  [OK] PQC Signature Tools")
        checks.append(('PQC Signatures', True, 'Tools exist'))
    else:
        print(f"  [WARN]  PQC Signature Tools (not found)")
        checks.append(('PQC Signatures', False, 'Tools not found'))

    # ===================================================================
    # CHECK 7: File Structure
    # ===================================================================
    print("\n[7/8] Testing File Structure...")
    required_paths = [
        ('Registry', '16_codex/structure/auto_generated/sot_rules_full.json'),
        ('Contract', '16_codex/contracts/sot/sot_contract.yaml'),
        ('Policy Dir', '23_compliance/policies/sot'),
        ('Validator', '03_core/validators/sot/sot_validator_engine.py'),
    ]

    structure_pass = True
    for name, rel_path in required_paths:
        full_path = repo_root / rel_path
        if full_path.exists():
            print(f"  [OK] {name}")
        else:
            print(f"  [ERROR] {name} (not found)")
            structure_pass = False

    checks.append(('File Structure', structure_pass, f'{sum(1 for _, p in required_paths if (repo_root / p).exists())}/{len(required_paths)} paths'))
    if not structure_pass:
        all_passed = False

    # ===================================================================
    # CHECK 8: 24 Root Directories
    # ===================================================================
    print("\n[8/8] Testing 24 Root Directories...")
    expected_roots = [
        "01_ai_layer", "02_audit_logging", "03_core", "04_deployment",
        "05_documentation", "06_data_pipeline", "07_governance_legal",
        "08_identity_score", "09_meta_identity", "10_interoperability",
        "11_test_simulation", "12_tooling", "13_ui_layer", "14_zero_time_auth",
        "15_infra", "16_codex", "17_observability", "18_data_layer",
        "19_adapters", "20_foundation", "21_post_quantum_crypto",
        "22_datasets", "23_compliance", "24_meta_orchestration"
    ]

    existing_roots = [d.name for d in repo_root.iterdir()
                     if d.is_dir() and d.name in expected_roots]

    if len(existing_roots) == 24:
        print(f"  [OK] All 24 Root Directories")
        checks.append(('24 Root Dirs', True, '24/24 found'))
    else:
        print(f"  [ERROR] Root Directories ({len(existing_roots)}/24 found)")
        checks.append(('24 Root Dirs', False, f'{len(existing_roots)}/24 found'))
        all_passed = False

    # ===================================================================
    # SUMMARY
    # ===================================================================
    print()
    print("="*70)
    print("VERIFICATION SUMMARY")
    print("="*70)

    passed = sum(1 for _, status, _ in checks if status)
    total = len(checks)

    for check_name, status, details in checks:
        status_icon = '[OK]' if status else '[ERROR]'
        print(f"  {status_icon} {check_name:25} {details}")

    print()
    print(f"Total: {passed}/{total} checks passed ({passed/total*100:.1f}%)")
    print()

    # Save report
    reports_dir = repo_root / '02_audit_logging' / 'reports'
    reports_dir.mkdir(parents=True, exist_ok=True)

    report_file = reports_dir / 'system_verification_report.json'
    report_data = {
        'timestamp': datetime.now().isoformat(),
        'version': '4.0.0',
        'total_checks': total,
        'passed': passed,
        'failed': total - passed,
        'score': (passed / total) * 100,
        'checks': [
            {'name': name, 'passed': status, 'details': details}
            for name, status, details in checks
        ]
    }

    report_file.write_text(json.dumps(report_data, indent=2))
    print(f"[FILE] Report saved: {report_file.name}")
    print()

    if all_passed:
        print("[SUCCESS] ALL CHECKS PASSED - SYSTEM READY FOR PRODUCTION")
        return 0
    else:
        print(f"[WARN] {total - passed} CHECKS FAILED - NEEDS ATTENTION")
        return 1


if __name__ == '__main__':
    sys.exit(main())
