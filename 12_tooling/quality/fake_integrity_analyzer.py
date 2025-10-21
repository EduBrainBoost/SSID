#!/usr/bin/env python3
"""
FAKE-INTEGRITY-ANALYSIS v1.0
Counter-verification tool to detect integrity manipulation patterns
Defensive security validation for 100/100 certification claims
"""

import sys
import os
import re
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime
from collections import defaultdict

# Fix Windows console encoding
if sys.platform == 'win32':
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
    if sys.stderr.encoding != 'utf-8':
        sys.stderr.reconfigure(encoding='utf-8')

class FakeIntegrityAnalyzer:
    """Detects potential integrity manipulation in certification claims"""

    def __init__(self, root_dir: Path, scan_depth: int = 3):
        self.root = root_dir
        self.scan_depth = scan_depth
        self.anomalies = []
        self.hash_map = {}
        self.score_patterns = []
        self.self_references = []
        self.policy_issues = []

        # Exclusions for legitimate files
        self.legitimate_whitelist = {
            '.git', '__pycache__', '.pytest_cache', '.mypy_cache',
            'node_modules', '.venv', 'venv', 'dist', 'build'
        }

    def scan_root_breaks(self) -> List[Dict]:
        """Detect unauthorized root-level structures"""
        print("[1/5] Scanning for root-break patterns...")

        root_breaks = []
        suspicious_patterns = [
            r'root_.*_temp',
            r'/draft/',
            r'_backup',
            r'_old',
            r'_hidden'
        ]

        # Scan root level
        for item in self.root.iterdir():
            if item.name in self.legitimate_whitelist:
                continue

            # Check for suspicious patterns
            for pattern in suspicious_patterns:
                if re.search(pattern, str(item)):
                    root_breaks.append({
                        'type': 'ROOT-BREAK',
                        'path': str(item.relative_to(self.root)),
                        'pattern': pattern,
                        'severity': 'HIGH'
                    })

        # Check .claude directory legitimacy
        claude_dir = self.root / '.claude'
        if claude_dir.exists():
            # .claude is legitimate for Claude Code config
            # Check if it contains unauthorized artifacts
            for item in claude_dir.rglob('*'):
                if item.is_file() and item.suffix in ['.json', '.yaml', '.md']:
                    size = item.stat().st_size
                    if size > 100000:  # > 100KB suspicious for config
                        root_breaks.append({
                            'type': 'CLAUDE-DIR-BLOAT',
                            'path': str(item.relative_to(self.root)),
                            'size': size,
                            'severity': 'MEDIUM'
                        })

        self.anomalies.extend(root_breaks)
        return root_breaks

    def scan_score_manipulation(self) -> List[Dict]:
        """Detect score manipulation heuristics"""
        print("[2/5] Detecting score manipulation patterns...")

        manipulation_patterns = []

        # Focus on audit, compliance, and orchestration
        focus_dirs = [
            '02_audit_logging',
            '23_compliance',
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
                if file_path.name.startswith('.'):
                    continue

                try:
                    content = file_path.read_text(encoding='utf-8')

                    # Pattern 1: 100/100 without test evidence
                    if re.search(r'100[/:]100', content):
                        # Check if there's actual test evidence
                        has_pytest = 'pytest' in content.lower() or 'test_' in content.lower()
                        has_assert = 'assert' in content.lower()
                        has_validation = any(x in content.lower() for x in ['validation', 'verified', 'checked'])

                        # If it's just reporting 100/100 without evidence
                        if not (has_pytest or has_assert) and 'score' in content.lower():
                            manipulation_patterns.append({
                                'type': 'SCORE-WITHOUT-EVIDENCE',
                                'path': str(file_path.relative_to(self.root)),
                                'pattern': '100/100 score claim without test evidence',
                                'severity': 'MEDIUM',
                                'has_validation': has_validation
                            })

                    # Pattern 2: Status checkmarks without assertions
                    status_matches = re.findall(r'Status:\s*✅', content)
                    if status_matches:
                        has_assert = 'assert' in content.lower()
                        has_test = re.search(r'def test_', content)
                        has_validation = 'validated' in content.lower() or 'verified' in content.lower()

                        if not (has_assert or has_test) and len(status_matches) > 3:
                            manipulation_patterns.append({
                                'type': 'STATUS-CHECKMARK-SPAM',
                                'path': str(file_path.relative_to(self.root)),
                                'count': len(status_matches),
                                'severity': 'LOW',
                                'has_validation_text': has_validation
                            })

                    # Pattern 3: "PASSED" without actual test results
                    passed_matches = re.findall(r'\[PASS\]|\bPASSED\b', content)
                    if len(passed_matches) > 5:
                        has_pytest_output = 'collected' in content and 'items' in content
                        has_test_function = re.search(r'def test_', content)

                        if not (has_pytest_output or has_test_function):
                            manipulation_patterns.append({
                                'type': 'PASSED-CLAIM-WITHOUT-TEST',
                                'path': str(file_path.relative_to(self.root)),
                                'count': len(passed_matches),
                                'severity': 'MEDIUM'
                            })

                except Exception as e:
                    # Skip files that can't be read
                    pass

        self.score_patterns = manipulation_patterns
        self.anomalies.extend(manipulation_patterns)
        return manipulation_patterns

    def scan_evidence_loops(self) -> List[Dict]:
        """Detect self-referencing evidence (circular validation)"""
        print("[3/5] Checking for evidence self-reference loops...")

        loops = []
        audit_dir = self.root / '02_audit_logging'

        if not audit_dir.exists():
            return loops

        for report_file in audit_dir.rglob('*.md'):
            if 'report' not in report_file.name.lower():
                continue

            try:
                content = report_file.read_text(encoding='utf-8')

                # Check for verification claims
                verification_claims = re.findall(r'verified|validated|certified|approved', content, re.IGNORECASE)

                if len(verification_claims) > 5:
                    # Check for external/independent references
                    has_external = any(x in content.lower() for x in [
                        'external audit', 'independent', 'third-party',
                        'external verifier', 'independent committee'
                    ])

                    has_test_output = 'pytest' in content.lower() or re.search(r'collected \d+ items', content)

                    if not (has_external or has_test_output):
                        loops.append({
                            'type': 'SELF-REFERENCE-LOOP',
                            'path': str(report_file.relative_to(self.root)),
                            'claim_count': len(verification_claims),
                            'has_external_ref': has_external,
                            'severity': 'MEDIUM'
                        })

                # Check if report references itself as evidence
                report_name = report_file.stem
                if report_name in content and content.count(report_name) > 2:
                    loops.append({
                        'type': 'CIRCULAR-SELF-CITATION',
                        'path': str(report_file.relative_to(self.root)),
                        'self_references': content.count(report_name),
                        'severity': 'LOW'
                    })

            except Exception as e:
                pass

        self.self_references = loops
        self.anomalies.extend(loops)
        return loops

    def scan_policy_shields(self) -> List[Dict]:
        """Analyze OPA policies for blind guard patterns"""
        print("[4/5] Analyzing OPA policies for blind guards...")

        policy_issues = []
        opa_dir = self.root / '23_compliance' / 'policies' / 'opa'

        if not opa_dir.exists():
            policy_issues.append({
                'type': 'MISSING-OPA-POLICIES',
                'severity': 'HIGH',
                'note': 'No OPA policy directory found'
            })
            self.anomalies.extend(policy_issues)
            return policy_issues

        for rego_file in opa_dir.glob('*.rego'):
            try:
                content = rego_file.read_text(encoding='utf-8')

                # Count allow vs deny rules
                allow_count = len(re.findall(r'\ballow\b', content))
                deny_count = len(re.findall(r'\bdeny\b', content))

                # Check for blind guard (deny only, no allow logic)
                if deny_count > 0 and allow_count == 0:
                    policy_issues.append({
                        'type': 'BLIND-GUARD-POLICY',
                        'path': str(rego_file.relative_to(self.root)),
                        'deny_count': deny_count,
                        'allow_count': allow_count,
                        'severity': 'HIGH'
                    })

                # Check for trivial allow (always true)
                trivial_allow = re.search(r'default\s+allow\s*=\s*true', content)
                if trivial_allow:
                    policy_issues.append({
                        'type': 'TRIVIAL-ALLOW-POLICY',
                        'path': str(rego_file.relative_to(self.root)),
                        'severity': 'HIGH',
                        'note': 'Policy defaults to allow=true without conditions'
                    })

                # Check for missing validation logic
                has_conditions = bool(re.search(r'if\s+\{', content))
                has_comparisons = bool(re.search(r'[=<>!]=', content))

                if allow_count > 0 and not (has_conditions and has_comparisons):
                    policy_issues.append({
                        'type': 'UNCONDITIONAL-ALLOW',
                        'path': str(rego_file.relative_to(self.root)),
                        'severity': 'MEDIUM',
                        'note': 'Allow rules without validation conditions'
                    })

            except Exception as e:
                pass

        self.policy_issues = policy_issues
        self.anomalies.extend(policy_issues)
        return policy_issues

    def scan_hash_inconsistencies(self) -> List[Dict]:
        """Probe for duplicate hashes and code mirroring"""
        print("[5/5] Probing for hash inconsistencies...")

        duplicates = []
        self.hash_map = defaultdict(list)

        # Focus on Python files in critical directories
        focus_dirs = [
            '02_audit_logging',
            '23_compliance',
            '24_meta_orchestration',
            '12_tooling'
        ]

        for focus in focus_dirs:
            focus_path = self.root / focus
            if not focus_path.exists():
                continue

            for py_file in focus_path.rglob('*.py'):
                if py_file.name.startswith('.'):
                    continue
                if '__pycache__' in str(py_file):
                    continue

                try:
                    content = py_file.read_bytes()
                    file_hash = hashlib.sha256(content).hexdigest()

                    self.hash_map[file_hash].append(str(py_file.relative_to(self.root)))

                except Exception as e:
                    pass

        # Detect duplicates
        for file_hash, files in self.hash_map.items():
            if len(files) > 1:
                # Check if duplicates are legitimate (e.g., __init__.py)
                basenames = [Path(f).name for f in files]
                if all(name == '__init__.py' for name in basenames):
                    # Legitimate: empty __init__.py files
                    continue

                duplicates.append({
                    'type': 'DUPLICATE-HASH-CODE',
                    'hash': file_hash[:16],
                    'files': files,
                    'count': len(files),
                    'severity': 'MEDIUM'
                })

        self.anomalies.extend(duplicates)
        return duplicates

    def calculate_suspicion_level(self) -> str:
        """Calculate overall suspicion level"""
        high_severity = sum(1 for a in self.anomalies if a.get('severity') == 'HIGH')
        medium_severity = sum(1 for a in self.anomalies if a.get('severity') == 'MEDIUM')
        total = len(self.anomalies)

        if high_severity >= 3 or total >= 10:
            return 'HIGH'
        elif medium_severity >= 5 or total >= 5:
            return 'MEDIUM'
        else:
            return 'LOW'

    def generate_report(self) -> Dict:
        """Generate comprehensive fake-integrity analysis report"""
        suspicion = self.calculate_suspicion_level()

        report = {
            'metadata': {
                'analysis_version': '1.0',
                'timestamp': datetime.utcnow().isoformat(),
                'root_directory': str(self.root),
                'scan_depth': self.scan_depth
            },
            'summary': {
                'total_anomalies': len(self.anomalies),
                'suspicion_level': suspicion,
                'high_severity_count': sum(1 for a in self.anomalies if a.get('severity') == 'HIGH'),
                'medium_severity_count': sum(1 for a in self.anomalies if a.get('severity') == 'MEDIUM'),
                'low_severity_count': sum(1 for a in self.anomalies if a.get('severity') == 'LOW')
            },
            'categories': {
                'root_breaks': [a for a in self.anomalies if a.get('type', '').startswith('ROOT-BREAK')],
                'score_manipulation': [a for a in self.anomalies if 'SCORE' in a.get('type', '')],
                'evidence_loops': [a for a in self.anomalies if 'REFERENCE' in a.get('type', '')],
                'policy_shields': [a for a in self.anomalies if 'POLICY' in a.get('type', '') or 'GUARD' in a.get('type', '')],
                'hash_duplicates': [a for a in self.anomalies if 'HASH' in a.get('type', '')]
            },
            'detected_anomalies': self.anomalies,
            'interpretation': self._interpret_results(suspicion)
        }

        return report

    def _interpret_results(self, suspicion: str) -> Dict:
        """Interpret suspicion level"""
        interpretations = {
            'HIGH': {
                'risk': 'CRITICAL',
                'message': 'Possible integrity manipulation detected. Reports or policies may be masking actual errors.',
                'recommendations': [
                    'Conduct manual code review of flagged files',
                    'Verify OPA policies with external security audit',
                    'Re-run tests with independent validation',
                    'Review score calculation methodology'
                ]
            },
            'MEDIUM': {
                'risk': 'MODERATE',
                'message': 'CI/OPA may be enforcing scores without complete validation. Some patterns require investigation.',
                'recommendations': [
                    'Review flagged anomalies for false positives',
                    'Validate test coverage independently',
                    'Check policy logic for completeness',
                    'Monitor for pattern recurrence'
                ]
            },
            'LOW': {
                'risk': 'MINIMAL',
                'message': 'No significant integrity manipulation detected. System appears legitimate.',
                'recommendations': [
                    'Continue periodic integrity scans',
                    'Monitor for new anomaly patterns',
                    'Maintain current validation practices'
                ]
            }
        }

        return interpretations[suspicion]

    def run_full_scan(self) -> Dict:
        """Execute complete fake-integrity analysis"""
        print("=" * 80)
        print("FAKE-INTEGRITY-ANALYSIS v1.0")
        print("Counter-Verification of 100/100 Certification Claims")
        print("=" * 80)
        print()

        # Run all scans
        self.scan_root_breaks()
        self.scan_score_manipulation()
        self.scan_evidence_loops()
        self.scan_policy_shields()
        self.scan_hash_inconsistencies()

        # Generate report
        report = self.generate_report()

        print()
        print("=" * 80)
        print("ANALYSIS COMPLETE")
        print("=" * 80)
        print(f"Total Anomalies: {report['summary']['total_anomalies']}")
        print(f"Suspicion Level: {report['summary']['suspicion_level']}")
        print(f"Risk: {report['interpretation']['risk']}")
        print()
        print(f"Message: {report['interpretation']['message']}")
        print()

        return report

def main():
    """Main entry point"""
    root = Path(__file__).parent.parent.parent

    analyzer = FakeIntegrityAnalyzer(root, scan_depth=3)
    report = analyzer.run_full_scan()

    # Save JSON report
    json_path = root / '02_audit_logging' / 'reports' / 'fake_integrity_analysis_report.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"JSON Report: {json_path.relative_to(root)}")

    # Calculate hash
    report_hash = hashlib.sha256(json.dumps(report, sort_keys=True).encode()).hexdigest()
    print(f"Report SHA-256: {report_hash[:32]}...")
    print()

    # Exit with appropriate code
    suspicion = report['summary']['suspicion_level']
    if suspicion == 'HIGH':
        sys.exit(2)
    elif suspicion == 'MEDIUM':
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
