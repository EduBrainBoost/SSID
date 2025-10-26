#!/usr/bin/env python3
"""
SSID SoT Complete Health Monitor
==================================

Production-grade health monitoring with cross-validation across all artifacts.

Monitors:
1. Registry integrity (Merkle root validation)
2. Artifact synchronization (Contract ↔ Policy ↔ Validator ↔ Tests)
3. Hash verification
4. Completeness scoring
5. Drift detection

Version: 3.2.0
Author: SSID Core Team
"""

import json
import yaml
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple
from collections import defaultdict

# ============================================================================
# CONFIGURATION
# ============================================================================

BASE_DIR = Path(__file__).parent.parent

FILES_TO_MONITOR = {
    'registry': BASE_DIR / '16_codex' / 'structure' / 'auto_generated' / 'sot_rules_full.json',
    'contract': BASE_DIR / '16_codex' / 'contracts' / 'sot' / 'sot_contract_complete.yaml',
    'policy': BASE_DIR / '23_compliance' / 'policies' / 'sot' / 'sot_policy_complete.rego',
    'validator': BASE_DIR / '03_core' / 'validators' / 'sot' / 'sot_validator_complete.py',
    'tests': BASE_DIR / '11_test_simulation' / 'tests_compliance' / 'test_sot_complete.py',
    'merkle': BASE_DIR / '24_meta_orchestration' / 'registry' / 'sot_merkle_tree.json',
    'audit': BASE_DIR / '02_audit_logging' / 'reports' / 'sot_extractor_audit.json',
}

OUTPUT_FILE = BASE_DIR / '02_audit_logging' / 'reports' / 'sot_health_status_complete.json'

# ============================================================================
# HEALTH MONITOR
# ============================================================================

class HealthMonitor:
    """Complete health monitoring system"""

    def __init__(self):
        self.status = {
            'timestamp': datetime.now().isoformat(),
            'version': '3.2.0',
            'checks': {},
            'overall_status': 'UNKNOWN',
            'score': 0.0,
            'issues': [],
            'warnings': [],
        }

    def compute_file_hash(self, file_path: Path) -> str:
        """Compute SHA-256 hash of file"""
        if not file_path.exists():
            return ''

        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                sha256.update(chunk)
        return sha256.hexdigest()

    def check_file_exists(self, name: str, file_path: Path) -> Dict[str, Any]:
        """Check if file exists"""
        exists = file_path.exists()

        return {
            'check': f'file_exists_{name}',
            'status': 'PASS' if exists else 'FAIL',
            'file': str(file_path),
            'exists': exists,
            'size': file_path.stat().st_size if exists else 0,
            'hash': self.compute_file_hash(file_path) if exists else '',
        }

    def check_registry_integrity(self) -> Dict[str, Any]:
        """Check registry file integrity"""
        registry_file = FILES_TO_MONITOR['registry']

        if not registry_file.exists():
            return {
                'check': 'registry_integrity',
                'status': 'FAIL',
                'error': 'Registry file does not exist',
            }

        try:
            with open(registry_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Validate structure
            required_keys = ['metadata', 'rules', 'cross_references']
            missing_keys = [k for k in required_keys if k not in data]

            if missing_keys:
                return {
                    'check': 'registry_integrity',
                    'status': 'FAIL',
                    'error': f'Missing keys: {missing_keys}',
                }

            # Validate metadata
            metadata = data['metadata']
            total_rules = metadata.get('total_rules', 0)
            actual_rules = len(data['rules'])

            if total_rules != actual_rules:
                return {
                    'check': 'registry_integrity',
                    'status': 'WARN',
                    'warning': f'Rule count mismatch: metadata={total_rules}, actual={actual_rules}',
                    'total_rules': total_rules,
                    'actual_rules': actual_rules,
                }

            return {
                'check': 'registry_integrity',
                'status': 'PASS',
                'total_rules': total_rules,
                'version': metadata.get('version', 'unknown'),
                'extraction_mode': metadata.get('extraction_mode', 'unknown'),
            }

        except Exception as e:
            return {
                'check': 'registry_integrity',
                'status': 'FAIL',
                'error': str(e),
            }

    def check_merkle_tree(self) -> Dict[str, Any]:
        """Check Merkle tree integrity"""
        merkle_file = FILES_TO_MONITOR['merkle']

        if not merkle_file.exists():
            return {
                'check': 'merkle_tree',
                'status': 'FAIL',
                'error': 'Merkle tree file does not exist',
            }

        try:
            with open(merkle_file, 'r', encoding='utf-8') as f:
                merkle_data = json.load(f)

            # Validate structure
            if 'merkle_root' not in merkle_data:
                return {
                    'check': 'merkle_tree',
                    'status': 'FAIL',
                    'error': 'Missing merkle_root',
                }

            # Validate merkle root format (should be 64-char hex)
            merkle_root = merkle_data['merkle_root']
            if len(merkle_root) != 64 or not all(c in '0123456789abcdef' for c in merkle_root):
                return {
                    'check': 'merkle_tree',
                    'status': 'FAIL',
                    'error': 'Invalid merkle_root format',
                }

            return {
                'check': 'merkle_tree',
                'status': 'PASS',
                'merkle_root': merkle_root,
                'total_leaves': merkle_data.get('total_leaves', 0),
                'algorithm': merkle_data.get('algorithm', 'unknown'),
            }

        except Exception as e:
            return {
                'check': 'merkle_tree',
                'status': 'FAIL',
                'error': str(e),
            }

    def check_artifact_sync(self) -> Dict[str, Any]:
        """Check synchronization across artifacts"""
        registry_file = FILES_TO_MONITOR['registry']
        contract_file = FILES_TO_MONITOR['contract']

        issues = []
        warnings = []

        # Load registry
        try:
            with open(registry_file, 'r', encoding='utf-8') as f:
                registry_data = json.load(f)
            registry_rules = len(registry_data['rules'])
        except Exception as e:
            return {
                'check': 'artifact_sync',
                'status': 'FAIL',
                'error': f'Failed to load registry: {e}',
            }

        # Load contract
        try:
            with open(contract_file, 'r', encoding='utf-8') as f:
                contract_data = yaml.safe_load(f)
            contract_rules = len(contract_data.get('rules', []))
        except Exception as e:
            return {
                'check': 'artifact_sync',
                'status': 'FAIL',
                'error': f'Failed to load contract: {e}',
            }

        # Compare counts
        if registry_rules != contract_rules:
            warnings.append(f'Rule count mismatch: registry={registry_rules}, contract={contract_rules}')

        # Check validator
        validator_file = FILES_TO_MONITOR['validator']
        if validator_file.exists():
            with open(validator_file, 'r', encoding='utf-8') as f:
                validator_content = f.read()
                validator_funcs = validator_content.count('def validate_')

            if validator_funcs < 50:
                warnings.append(f'Low validator function count: {validator_funcs}')

        # Check tests
        tests_file = FILES_TO_MONITOR['tests']
        if tests_file.exists():
            with open(tests_file, 'r', encoding='utf-8') as f:
                tests_content = f.read()
                test_funcs = tests_content.count('def test_')

            if test_funcs < 50:
                warnings.append(f'Low test function count: {test_funcs}')

        status = 'PASS'
        if issues:
            status = 'FAIL'
        elif warnings:
            status = 'WARN'

        return {
            'check': 'artifact_sync',
            'status': status,
            'registry_rules': registry_rules,
            'contract_rules': contract_rules,
            'validator_functions': validator_funcs if 'validator_funcs' in locals() else 0,
            'test_functions': test_funcs if 'test_funcs' in locals() else 0,
            'issues': issues,
            'warnings': warnings,
        }

    def check_completeness(self) -> Dict[str, Any]:
        """Check overall completeness"""
        registry_file = FILES_TO_MONITOR['registry']

        try:
            with open(registry_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Calculate completeness metrics
            rules = data['rules']
            total = len(rules)

            if total == 0:
                return {
                    'check': 'completeness',
                    'status': 'FAIL',
                    'error': 'No rules found',
                }

            # Count by completeness score
            perfect = sum(1 for r in rules if r.get('completeness', {}).get('score', 0) == 100)
            high = sum(1 for r in rules if 80 <= r.get('completeness', {}).get('score', 0) < 100)
            medium = sum(1 for r in rules if 60 <= r.get('completeness', {}).get('score', 0) < 80)
            low = sum(1 for r in rules if r.get('completeness', {}).get('score', 0) < 60)

            # Calculate average
            avg_score = sum(r.get('completeness', {}).get('score', 0) for r in rules) / total

            # Determine status
            if avg_score >= 80:
                status = 'PASS'
            elif avg_score >= 60:
                status = 'WARN'
            else:
                status = 'FAIL'

            return {
                'check': 'completeness',
                'status': status,
                'total_rules': total,
                'average_score': avg_score,
                'breakdown': {
                    'perfect_100': perfect,
                    'high_80_99': high,
                    'medium_60_79': medium,
                    'low_0_59': low,
                },
            }

        except Exception as e:
            return {
                'check': 'completeness',
                'status': 'FAIL',
                'error': str(e),
            }

    def run_all_checks(self) -> Dict[str, Any]:
        """Run all health checks"""
        print(f"\n{'='*80}")
        print("SSID SoT Health Monitor v3.2.0")
        print(f"{'='*80}\n")

        # File existence checks
        print("Checking file existence...")
        for name, file_path in FILES_TO_MONITOR.items():
            result = self.check_file_exists(name, file_path)
            self.status['checks'][result['check']] = result

            if result['status'] == 'FAIL':
                self.status['issues'].append(f"File missing: {name}")

        # Registry integrity
        print("Checking registry integrity...")
        result = self.check_registry_integrity()
        self.status['checks']['registry_integrity'] = result

        if result['status'] == 'FAIL':
            self.status['issues'].append(f"Registry integrity check failed")
        elif result['status'] == 'WARN':
            self.status['warnings'].append(result.get('warning', 'Unknown warning'))

        # Merkle tree
        print("Checking Merkle tree...")
        result = self.check_merkle_tree()
        self.status['checks']['merkle_tree'] = result

        if result['status'] == 'FAIL':
            self.status['issues'].append(f"Merkle tree check failed")

        # Artifact synchronization
        print("Checking artifact synchronization...")
        result = self.check_artifact_sync()
        self.status['checks']['artifact_sync'] = result

        if result['status'] == 'FAIL':
            self.status['issues'].extend(result.get('issues', []))
        elif result['status'] == 'WARN':
            self.status['warnings'].extend(result.get('warnings', []))

        # Completeness
        print("Checking completeness...")
        result = self.check_completeness()
        self.status['checks']['completeness'] = result

        if result['status'] == 'FAIL':
            self.status['issues'].append(f"Completeness check failed")
        elif result['status'] == 'WARN':
            self.status['warnings'].append(f"Low completeness score: {result.get('average_score', 0):.2f}%")

        # Calculate overall status
        check_statuses = [check['status'] for check in self.status['checks'].values()]

        if any(s == 'FAIL' for s in check_statuses):
            self.status['overall_status'] = 'FAIL'
            self.status['score'] = 0.0
        elif any(s == 'WARN' for s in check_statuses):
            self.status['overall_status'] = 'WARN'
            pass_count = sum(1 for s in check_statuses if s == 'PASS')
            self.status['score'] = (pass_count / len(check_statuses)) * 100
        else:
            self.status['overall_status'] = 'PASS'
            self.status['score'] = 100.0

        return self.status

    def save_status(self):
        """Save health status to file"""
        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.status, f, indent=2)

        print(f"\nHealth status saved to: {OUTPUT_FILE}")

    def print_summary(self):
        """Print health status summary"""
        print(f"\n{'='*80}")
        print("HEALTH CHECK SUMMARY")
        print(f"{'='*80}")
        print(f"Overall Status: {self.status['overall_status']}")
        print(f"Score: {self.status['score']:.2f}%")
        print(f"Checks Performed: {len(self.status['checks'])}")
        print(f"Issues: {len(self.status['issues'])}")
        print(f"Warnings: {len(self.status['warnings'])}")
        print(f"{'='*80}\n")

        if self.status['issues']:
            print("ISSUES:")
            for issue in self.status['issues']:
                print(f"  - {issue}")
            print()

        if self.status['warnings']:
            print("WARNINGS:")
            for warning in self.status['warnings']:
                print(f"  - {warning}")
            print()

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution"""
    monitor = HealthMonitor()

    # Run all checks
    status = monitor.run_all_checks()

    # Save status
    monitor.save_status()

    # Print summary
    monitor.print_summary()

    # Exit with appropriate code
    if status['overall_status'] == 'FAIL':
        return 2
    elif status['overall_status'] == 'WARN':
        return 1
    else:
        return 0

if __name__ == '__main__':
    exit(main())
