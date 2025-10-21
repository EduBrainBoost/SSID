#!/usr/bin/env python3
"""
Root-Write Prevention Validator
================================

CI/CD validator that blocks commits containing scripts that write to repository root.
Integrates with pre-commit hooks and GitHub Actions.

Usage:
    python root_write_prevention_validator.py [--staged-only]

Exit Codes:
    0 - No violations found
    1 - Violations detected (blocks commit)

Output:
    02_audit_logging/reports/root_write_prevention_result.json
"""

import re
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Set

# UTF-8 enforcement for Windows
if sys.platform == 'win32':
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')

class RootWritePreventionValidator:
    """Validates that no scripts write to repository root"""

    def __init__(self, repo_root: Path, staged_only: bool = False):
        self.repo_root = repo_root
        self.staged_only = staged_only
        self.violations = []
        self.stats = {
            'files_checked': 0,
            'violations_found': 0,
            'blocked_patterns': {}
        }

        # Patterns that indicate root-writing violations
        self.violation_patterns = [
            {
                'name': 'direct_root_write',
                'regex': r'Path\(["\']([A-Z][A-Za-z_0-9]+\.(?:md|log|zip|json|txt))["\'](?!\s*\)\.exists)',
                'severity': 'HIGH',
                'message': 'Direct Path() construction for root-level file write'
            },
            {
                'name': 'open_root_write',
                'regex': r'open\(["\']([A-Za-z][A-Za-z_0-9]+\.(?:md|log|zip|json|txt))["\'].*["\']w',
                'severity': 'HIGH',
                'message': 'open() with write mode for root-level file'
            },
            {
                'name': 'write_text_root',
                'regex': r'Path\(["\']([A-Za-z][A-Za-z_0-9]+\.(?:md|log|zip|json))["\']\)\.write_text',
                'severity': 'HIGH',
                'message': 'write_text() method for root-level file'
            },
            {
                'name': 'parent_parent_root',
                'regex': r'parent\.parent\s*/\s*["\']([A-Z][A-Za-z_0-9]+\.(?:md|log|zip))["\']',
                'severity': 'CRITICAL',
                'message': 'parent.parent path construction to repository root'
            }
        ]

        # Whitelisted files (scanner itself, examples, documentation)
        self.whitelist = {
            '12_tooling/analysis/scan_root_writers.py',  # Scanner has example patterns
            '23_compliance/validators/root_write_prevention_validator.py',  # This file
        }

    def get_files_to_check(self) -> List[Path]:
        """Get list of Python files to check"""
        if self.staged_only:
            # Check only staged files in git
            try:
                result = subprocess.run(
                    ['git', 'diff', '--cached', '--name-only', '--diff-filter=ACMR'],
                    cwd=self.repo_root,
                    capture_output=True,
                    text=True,
                    check=True
                )
                files = result.stdout.strip().split('\n')
                python_files = [
                    self.repo_root / f
                    for f in files
                    if f.endswith('.py') and Path(self.repo_root / f).exists()
                ]
                return python_files
            except subprocess.CalledProcessError:
                print("Warning: git command failed, checking all files")
                return self._get_all_python_files()
        else:
            return self._get_all_python_files()

    def _get_all_python_files(self) -> List[Path]:
        """Get all Python files in repository"""
        python_files = list(self.repo_root.rglob("*.py"))
        # Filter out git, pycache, backups
        python_files = [
            f for f in python_files
            if '.git' not in str(f)
            and '__pycache__' not in str(f)
            and '/backups/' not in str(f).replace('\\', '/')
        ]
        return python_files

    def check_file(self, file_path: Path) -> List[Dict]:
        """Check a single file for root-write violations"""
        violations = []

        # Skip whitelisted files
        rel_path = str(file_path.relative_to(self.repo_root)).replace('\\', '/')
        if rel_path in self.whitelist:
            return violations

        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            lines = content.split('\n')

            for pattern_def in self.violation_patterns:
                pattern = re.compile(pattern_def['regex'], re.IGNORECASE)

                for line_num, line in enumerate(lines, 1):
                    # Skip comments (simple check)
                    stripped = line.strip()
                    if stripped.startswith('#') or stripped.startswith('"""') or stripped.startswith("'''"):
                        continue

                    matches = pattern.findall(line)
                    for match in matches:
                        # Check if path has directory separator (if yes, skip)
                        if '/' in match or '\\\\' in match:
                            continue

                        violations.append({
                            'file': rel_path,
                            'line': line_num,
                            'pattern': pattern_def['name'],
                            'target_file': match,
                            'severity': pattern_def['severity'],
                            'message': pattern_def['message'],
                            'code_snippet': line.strip()[:100]
                        })

                        # Update stats
                        pattern_name = pattern_def['name']
                        self.stats['blocked_patterns'][pattern_name] = \
                            self.stats['blocked_patterns'].get(pattern_name, 0) + 1

        except Exception as e:
            pass  # Skip files that can't be read

        return violations

    def validate(self) -> Dict:
        """Run validation on all files"""
        print("=" * 80)
        print("ROOT-WRITE PREVENTION VALIDATOR")
        print("=" * 80)
        print()

        files_to_check = self.get_files_to_check()
        print(f"Mode: {'Staged files only' if self.staged_only else 'All Python files'}")
        print(f"Files to check: {len(files_to_check)}")
        print()

        if self.staged_only and not files_to_check:
            print("✅ No Python files staged for commit")
            return self._generate_report(passed=True)

        print("Scanning for root-write violations...")
        print()

        for file_path in files_to_check:
            self.stats['files_checked'] += 1
            file_violations = self.check_file(file_path)
            self.violations.extend(file_violations)

            if file_violations:
                rel_path = file_path.relative_to(self.repo_root)
                print(f"❌ {rel_path}: {len(file_violations)} violation(s)")

        self.stats['violations_found'] = len(self.violations)

        print()
        print("=" * 80)
        print("VALIDATION RESULTS")
        print("=" * 80)
        print()

        if self.violations:
            print(f"❌ FAILED: {len(self.violations)} root-write violation(s) detected")
            print()
            print("Violations by severity:")
            severity_counts = {}
            for v in self.violations:
                severity = v['severity']
                severity_counts[severity] = severity_counts.get(severity, 0) + 1

            for severity in ['CRITICAL', 'HIGH', 'MEDIUM']:
                if severity in severity_counts:
                    print(f"  {severity}: {severity_counts[severity]}")

            print()
            print("Top violations:")
            for i, violation in enumerate(self.violations[:5], 1):
                print(f"  {i}. {violation['file']}:{violation['line']}")
                print(f"     Pattern: {violation['pattern']} ({violation['severity']})")
                print(f"     Target: {violation['target_file']}")
                print()

            return self._generate_report(passed=False)
        else:
            print(f"✅ PASSED: No root-write violations detected")
            print(f"Files checked: {self.stats['files_checked']}")
            print()
            return self._generate_report(passed=True)

    def _generate_report(self, passed: bool) -> Dict:
        """Generate validation report"""
        report = {
            'version': '1.0',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'mode': 'staged_only' if self.staged_only else 'full_scan',
            'passed': passed,
            'statistics': self.stats,
            'violations': self.violations,
            'repository_root': str(self.repo_root)
        }

        # Write report
        output_dir = self.repo_root / '02_audit_logging' / 'reports'
        output_dir.mkdir(parents=True, exist_ok=True)

        output_file = output_dir / 'root_write_prevention_result.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"📄 Report: {output_file}")
        print()

        return report

def main():
    """Main execution"""
    repo_root = Path(__file__).resolve().parents[2]

    # Check if --staged-only flag is present
    staged_only = '--staged-only' in sys.argv

    validator = RootWritePreventionValidator(repo_root, staged_only=staged_only)
    report = validator.validate()

    # Exit with appropriate code
    exit_code = 0 if report['passed'] else 1

    if exit_code == 1:
        print("❌ ROOT-WRITE PREVENTION FAILED")
        print("Please fix the violations above before committing.")
        print()
        print("Guidelines:")
        print("  - Write files to appropriate root directories (01_-24_)")
        print("  - Use proper output paths: 02_audit_logging/reports/, etc.")
        print("  - Never construct paths like Path('REPORT.md') without a directory")
        print()

    sys.exit(exit_code)

if __name__ == "__main__":
    main()
