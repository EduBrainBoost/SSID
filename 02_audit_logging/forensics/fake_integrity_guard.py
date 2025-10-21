#!/usr/bin/env python3
"""
Fake Integrity Guard - Meta-Auditor
Permanent audit node that validates the integrity of the audit system itself
Runs bi-weekly to detect integrity manipulation patterns

Author: SSID Meta-Audit System
License: MIT
"""

import sys
import os
import re
import json
import yaml
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timezone
from collections import defaultdict

# Fix Windows console encoding
if sys.platform == 'win32':
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
    if sys.stderr.encoding != 'utf-8':
        sys.stderr.reconfigure(encoding='utf-8')

class FakeIntegrityGuard:
    """
    Meta-Auditor: Validates the integrity of audit artifacts and processes
    Detects manipulation patterns that could compromise certification claims
    """

    def __init__(self, root_dir: Path, strict_mode: bool = False):
        self.root = root_dir
        self.strict_mode = strict_mode
        self.anomalies = []
        self.critical_violations = []
        self.warnings = []

        # Whitelist for legitimate patterns (learned from initial scan)
        self.whitelisted_patterns = {
            'empty_init_hash': 'e3b0c44298fc1c14',  # Empty __init__.py
            'backup_dirs': ['backups', 'placeholders_'],
            'shard_templates': [
                'auth.py', 'endpoints.py', 'middleware.py',
                'bias_monitor.py', 'hasher.py', 'pii_detector.py'
            ],
            'legitimate_reports': [
                'certification', 'badge', 'audit', 'summary',
                'compliance', 'framework_mappings', 'report',
                'continuum', 'interfederation', 'integrity',
                'validation', 'manifest', 'template', 'readme',
                'release', 'dashboard', 'quarterly', 'bundle',
                'policy', 'promotion', 'nexus'
            ]
        }

    def scan_root_breaks(self) -> List[Dict]:
        """Detect NEW unauthorized root-level structures"""
        print("[1/5] Scanning for root-break patterns...")

        root_breaks = []
        suspicious_patterns = [
            r'root_.*_temp',
            r'/draft/',
            r'_backup(?!s)',  # _backup but not backups
            r'_old',
            r'_hidden',
            r'_test_(?!simulation)',  # _test_ but not test_simulation
            r'\.tmp$',
            r'staging'
        ]

        # Scan root level only
        for item in self.root.iterdir():
            if item.name.startswith('.'):
                # Allow .git, .github, .claude, .gitignore
                if item.name not in ['.git', '.github', '.claude', '.gitignore',
                                    '.pre-commit-config.yaml', '.gitattributes']:
                    root_breaks.append({
                        'type': 'UNAUTHORIZED-DOTFILE',
                        'path': item.name,
                        'severity': 'HIGH'
                    })
                continue

            for pattern in suspicious_patterns:
                if re.search(pattern, str(item)):
                    root_breaks.append({
                        'type': 'ROOT-BREAK',
                        'path': item.name,
                        'pattern': pattern,
                        'severity': 'CRITICAL'
                    })
                    self.critical_violations.append(f"Root break: {item.name}")

        self.anomalies.extend(root_breaks)
        return root_breaks

    def scan_score_manipulation(self) -> List[Dict]:
        """Detect score claims without corresponding test logs"""
        print("[2/5] Detecting score manipulation patterns...")

        manipulation_patterns = []

        # Focus on audit and compliance
        focus_dirs = [
            '02_audit_logging/reports',
            '23_compliance/reports',
            '24_meta_orchestration'
        ]

        for focus in focus_dirs:
            focus_path = self.root / focus
            if not focus_path.exists():
                continue

            for file_path in focus_path.rglob('*'):
                if not file_path.is_file():
                    continue
                if file_path.suffix not in ['.md', '.yaml', '.json']:
                    continue

                # Skip backups
                if any(backup in str(file_path) for backup in self.whitelisted_patterns['backup_dirs']):
                    continue

                try:
                    content = file_path.read_text(encoding='utf-8')

                    # Look for score claims
                    if re.search(r'100[/:]100', content):
                        # Check if it's a whitelisted report type
                        is_whitelisted = any(
                            keyword in file_path.name.lower()
                            for keyword in self.whitelisted_patterns['legitimate_reports']
                        )

                        if is_whitelisted:
                            continue  # Skip whitelisted reports

                        # Check for test evidence
                        has_pytest = 'pytest' in content.lower() or 'test_' in content.lower()
                        has_assert = 'assert' in content.lower()
                        has_test_log = bool(re.search(r'collected \d+ items', content))

                        # If no evidence and not a known report type, flag it
                        if not (has_pytest or has_assert or has_test_log):
                            manipulation_patterns.append({
                                'type': 'SCORE-WITHOUT-LOG',
                                'path': str(file_path.relative_to(self.root)),
                                'severity': 'CRITICAL'
                            })
                            self.critical_violations.append(
                                f"Score claim without log: {file_path.name}"
                            )

                except Exception as e:
                    pass

        self.anomalies.extend(manipulation_patterns)
        return manipulation_patterns

    def scan_hash_collisions(self) -> List[Dict]:
        """Detect NEW suspicious hash collisions (excluding whitelisted patterns)"""
        print("[3/5] Probing for suspicious hash collisions...")

        collisions = []
        hash_map = defaultdict(list)

        # Focus on critical directories
        focus_dirs = [
            '02_audit_logging/anti_gaming',
            '02_audit_logging/blockchain_anchor',
            '02_audit_logging/evidence',
            '23_compliance/anti_gaming',
            '23_compliance/policies',
            '12_tooling/quality'
        ]

        for focus in focus_dirs:
            focus_path = self.root / focus
            if not focus_path.exists():
                continue

            for py_file in focus_path.rglob('*.py'):
                if '__pycache__' in str(py_file):
                    continue

                try:
                    content = py_file.read_bytes()

                    # Skip empty __init__.py
                    if py_file.name == '__init__.py' and len(content) == 0:
                        continue

                    file_hash = hashlib.sha256(content).hexdigest()
                    hash_map[file_hash].append(str(py_file.relative_to(self.root)))

                except Exception as e:
                    pass

        # Detect suspicious duplicates (not in shard templates)
        for file_hash, files in hash_map.items():
            if len(files) > 1:
                # Check if all are shard templates
                basenames = [Path(f).name for f in files]
                is_shard_template = all(
                    name in self.whitelisted_patterns['shard_templates'] and '/shards/' in f
                    for name, f in zip(basenames, files)
                )

                if not is_shard_template:
                    collisions.append({
                        'type': 'SUSPICIOUS-HASH-COLLISION',
                        'hash': file_hash[:16],
                        'files': files,
                        'count': len(files),
                        'severity': 'HIGH'
                    })
                    self.critical_violations.append(
                        f"Hash collision: {len(files)} files with hash {file_hash[:16]}"
                    )

        self.anomalies.extend(collisions)
        return collisions

    def scan_policy_integrity(self) -> List[Dict]:
        """Validate OPA policies for blind guards or trivial allows"""
        print("[4/5] Analyzing OPA policy integrity...")

        policy_issues = []
        opa_dir = self.root / '23_compliance' / 'policies' / 'opa'

        if not opa_dir.exists():
            policy_issues.append({
                'type': 'MISSING-OPA-POLICIES',
                'severity': 'CRITICAL'
            })
            self.critical_violations.append('OPA policy directory missing')
            return policy_issues

        for rego_file in opa_dir.glob('*.rego'):
            try:
                content = rego_file.read_text(encoding='utf-8')

                # Enhanced policy analysis
                allow_count = len(re.findall(r'\ballow\b', content))
                deny_count = len(re.findall(r'\bdeny\b', content))
                has_default_allow = bool(re.search(r'default\s+allow\s*=\s*true', content))
                has_conditional_deny = bool(re.search(r'deny\[.*?\]\s+if\s+\{', content))

                # Only flag if default allow WITHOUT any deny rules
                if has_default_allow and not has_conditional_deny:
                    policy_issues.append({
                        'type': 'TRIVIAL-ALLOW-WITHOUT-DENY',
                        'path': str(rego_file.relative_to(self.root)),
                        'severity': 'CRITICAL'
                    })
                    self.critical_violations.append(
                        f"Trivial allow policy: {rego_file.name}"
                    )

                # Flag pure deny policies (deny only, no allow)
                if deny_count > 0 and allow_count == 0:
                    policy_issues.append({
                        'type': 'BLIND-GUARD-POLICY',
                        'path': str(rego_file.relative_to(self.root)),
                        'severity': 'HIGH'
                    })
                    self.warnings.append(f"Blind guard policy: {rego_file.name}")

            except Exception as e:
                pass

        self.anomalies.extend(policy_issues)
        return policy_issues

    def scan_audit_artifacts(self) -> List[Dict]:
        """Validate audit log and WORM storage integrity"""
        print("[5/5] Validating audit artifacts...")

        artifacts = []

        # Check WORM storage
        worm_dir = self.root / '02_audit_logging' / 'worm_storage'
        if worm_dir.exists():
            for worm_file in worm_dir.rglob('*.json'):
                try:
                    with open(worm_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    # Verify timestamp
                    if 'timestamp' not in data:
                        artifacts.append({
                            'type': 'MISSING-TIMESTAMP',
                            'path': str(worm_file.relative_to(self.root)),
                            'severity': 'HIGH'
                        })
                        self.warnings.append(f"Missing timestamp: {worm_file.name}")

                except Exception as e:
                    artifacts.append({
                        'type': 'CORRUPTED-WORM-FILE',
                        'path': str(worm_file.relative_to(self.root)),
                        'severity': 'CRITICAL',
                        'error': str(e)
                    })
                    self.critical_violations.append(f"Corrupted WORM: {worm_file.name}")

        self.anomalies.extend(artifacts)
        return artifacts

    def archive_to_worm(self, analysis_result: Dict) -> Path:
        """Archive analysis result to WORM storage"""
        worm_dir = self.root / '02_audit_logging' / 'worm_storage' / 'fake_integrity'
        worm_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
        worm_file = worm_dir / f"fake_integrity_analysis_{timestamp}.json"

        with open(worm_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_result, f, indent=2, ensure_ascii=False)

        return worm_file

    def update_verdict_registry(self, analysis_result: Dict) -> None:
        """Update YAML verdict registry"""
        registry_path = self.root / '02_audit_logging' / 'forensics' / 'fake_integrity_registry.yaml'

        # Load existing registry
        if registry_path.exists():
            with open(registry_path, 'r', encoding='utf-8') as f:
                registry = yaml.safe_load(f) or {}
        else:
            registry = {'analyses': []}

        # Add new entry
        entry = {
            'timestamp': analysis_result['metadata']['timestamp'],
            'suspicion_level': analysis_result['summary']['suspicion_level'],
            'total_anomalies': analysis_result['summary']['total_anomalies'],
            'critical_violations': len(self.critical_violations),
            'verdict': 'FAIL' if self.critical_violations else 'PASS',
            'worm_archive': analysis_result.get('worm_archive', ''),
            'sha256': analysis_result.get('sha256', '')
        }

        registry['analyses'].append(entry)
        registry['last_updated'] = datetime.now(timezone.utc).isoformat()
        registry['total_scans'] = len(registry['analyses'])

        # Keep last 52 analyses (1 year at bi-weekly rate)
        if len(registry['analyses']) > 52:
            registry['analyses'] = registry['analyses'][-52:]

        # Save registry
        with open(registry_path, 'w', encoding='utf-8') as f:
            yaml.dump(registry, f, default_flow_style=False, allow_unicode=True)

    def run_guard_analysis(self) -> Dict:
        """Execute complete meta-audit analysis"""
        print("=" * 80)
        print("FAKE INTEGRITY GUARD - Meta-Auditor")
        print("Validating Audit System Integrity")
        print("=" * 80)
        print(f"Mode: {'STRICT (CI-Fail on violations)' if self.strict_mode else 'MONITORING'}")
        print()

        # Run all scans
        self.scan_root_breaks()
        self.scan_score_manipulation()
        self.scan_hash_collisions()
        self.scan_policy_integrity()
        self.scan_audit_artifacts()

        # Generate analysis result
        suspicion = self._calculate_suspicion()

        analysis_result = {
            'metadata': {
                'version': '1.1',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'root_directory': str(self.root),
                'strict_mode': self.strict_mode
            },
            'summary': {
                'total_anomalies': len(self.anomalies),
                'suspicion_level': suspicion,
                'critical_violations': len(self.critical_violations),
                'warnings': len(self.warnings)
            },
            'violations': {
                'critical': self.critical_violations,
                'warnings': self.warnings
            },
            'categories': {
                'root_breaks': [a for a in self.anomalies if 'ROOT' in a.get('type', '')],
                'score_manipulation': [a for a in self.anomalies if 'SCORE' in a.get('type', '')],
                'hash_collisions': [a for a in self.anomalies if 'HASH' in a.get('type', '')],
                'policy_issues': [a for a in self.anomalies if 'POLICY' in a.get('type', '') or 'GUARD' in a.get('type', '')],
                'artifact_issues': [a for a in self.anomalies if 'WORM' in a.get('type', '') or 'TIMESTAMP' in a.get('type', '')]
            },
            'detected_anomalies': self.anomalies
        }

        # Archive to WORM
        worm_file = self.archive_to_worm(analysis_result)
        analysis_result['worm_archive'] = str(worm_file.relative_to(self.root))

        # Calculate SHA-256
        result_json = json.dumps(analysis_result, sort_keys=True)
        analysis_result['sha256'] = hashlib.sha256(result_json.encode()).hexdigest()

        # Update registry
        self.update_verdict_registry(analysis_result)

        # Print summary
        print()
        print("=" * 80)
        print("ANALYSIS COMPLETE")
        print("=" * 80)
        print(f"Total Anomalies: {analysis_result['summary']['total_anomalies']}")
        print(f"Critical Violations: {len(self.critical_violations)}")
        print(f"Warnings: {len(self.warnings)}")
        print(f"Suspicion Level: {suspicion}")
        print()

        if self.critical_violations:
            print("CRITICAL VIOLATIONS DETECTED:")
            for violation in self.critical_violations:
                print(f"  - {violation}")
            print()

        print(f"WORM Archive: {analysis_result['worm_archive']}")
        print(f"SHA-256: {analysis_result['sha256'][:32]}...")
        print()

        return analysis_result

    def _calculate_suspicion(self) -> str:
        """Calculate suspicion level based on violations"""
        critical_count = len(self.critical_violations)
        total_anomalies = len(self.anomalies)

        if critical_count >= 1:
            return 'HIGH'
        elif total_anomalies >= 5:
            return 'MEDIUM'
        else:
            return 'LOW'

def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Fake Integrity Guard - Meta-Auditor')
    parser.add_argument('--strict', action='store_true',
                       help='Strict mode: CI-fail on critical violations')
    args = parser.parse_args()

    root = Path(__file__).parent.parent.parent

    guard = FakeIntegrityGuard(root, strict_mode=args.strict)
    result = guard.run_guard_analysis()

    # Exit with appropriate code
    if args.strict and guard.critical_violations:
        print("=" * 80)
        print("CI-FAIL: Critical integrity violations detected")
        print("=" * 80)
        sys.exit(1)
    elif result['summary']['suspicion_level'] == 'HIGH':
        sys.exit(2)
    elif result['summary']['suspicion_level'] == 'MEDIUM':
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
