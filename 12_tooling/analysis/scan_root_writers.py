#!/usr/bin/env python3
"""
Root-Writer Scanner
===================

Scans all Python scripts for code that writes files to repository root.
Identifies violations of ROOT-24-LOCK policy.

Usage:
    python scan_root_writers.py

Output:
    02_audit_logging/reports/root_writers_analysis.json
"""

import re
import json
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Set

# UTF-8 enforcement for Windows
if sys.platform == 'win32':
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')

class RootWriterScanner:
    """Scans Python scripts for root-writing violations"""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.violations = []
        self.stats = {
            'scripts_scanned': 0,
            'violations_found': 0,
            'patterns_detected': {}
        }

    def scan_script(self, script_path: Path) -> List[Dict]:
        """Scan a single Python script for root-writing patterns"""
        violations = []

        try:
            content = script_path.read_text(encoding='utf-8', errors='ignore')
            lines = content.split('\n')

            # Pattern 1: Direct root file writes
            # Example: Path("SYSTEM_HEALTH_REPORT.md")
            pattern1 = r'Path\(["\']([A-Z_]+.*\.(?:md|log|zip|json))["\']'
            for i, line in enumerate(lines, 1):
                matches = re.findall(pattern1, line, re.IGNORECASE)
                for match in matches:
                    if not '/' in match and not '\\' in match:
                        violations.append({
                            'file': str(script_path.relative_to(self.repo_root)),
                            'line': i,
                            'pattern': 'direct_root_write',
                            'target_file': match,
                            'code_snippet': line.strip(),
                            'severity': 'HIGH'
                        })

            # Pattern 2: open() with root-level paths
            # Example: open("test_results.log", "w")
            pattern2 = r'open\(["\']([A-Za-z_]+.*\.(?:md|log|zip|json|txt))["\'].*["\']w'
            for i, line in enumerate(lines, 1):
                matches = re.findall(pattern2, line, re.IGNORECASE)
                for match in matches:
                    if not '/' in match and not '\\' in match:
                        violations.append({
                            'file': str(script_path.relative_to(self.repo_root)),
                            'line': i,
                            'pattern': 'open_root_write',
                            'target_file': match,
                            'code_snippet': line.strip(),
                            'severity': 'HIGH'
                        })

            # Pattern 3: write_text() with root paths
            # Example: Path("report.md").write_text(...)
            pattern3 = r'Path\(["\']([A-Za-z_]+.*\.(?:md|log|zip|json))["\']\)\.write_text'
            for i, line in enumerate(lines, 1):
                matches = re.findall(pattern3, line, re.IGNORECASE)
                for match in matches:
                    if not '/' in match and not '\\' in match:
                        violations.append({
                            'file': str(script_path.relative_to(self.repo_root)),
                            'line': i,
                            'pattern': 'write_text_root',
                            'target_file': match,
                            'code_snippet': line.strip(),
                            'severity': 'HIGH'
                        })

            # Pattern 4: Root path construction with parent.parent
            # Example: Path(__file__).parent.parent / "REPORT.md"
            pattern4 = r'parent\.parent\s*/\s*["\']([A-Z_]+.*\.(?:md|log|zip))["\']'
            for i, line in enumerate(lines, 1):
                matches = re.findall(pattern4, line)
                for match in matches:
                    violations.append({
                        'file': str(script_path.relative_to(self.repo_root)),
                        'line': i,
                        'pattern': 'parent_parent_root_write',
                        'target_file': match,
                        'code_snippet': line.strip(),
                        'severity': 'CRITICAL'
                    })

            # Pattern 5: Hardcoded root file references
            # Example: "ROOT_24_LOCK_V5_3_BUNDLE_FINAL.md"
            suspicious_files = [
                'SYSTEM_HEALTH_REPORT',
                'PHASE_3_',
                'MINIMAL_SURFACE',
                'ROOT_24_LOCK.*BUNDLE',
                'test_results',
                '_SUMMARY\.md',
                '_REPORT_.*\.md'
            ]
            for pattern in suspicious_files:
                regex = re.compile(f'["\']({pattern}[^"\']*)["\']', re.IGNORECASE)
                for i, line in enumerate(lines, 1):
                    matches = regex.findall(line)
                    for match in matches:
                        violations.append({
                            'file': str(script_path.relative_to(self.repo_root)),
                            'line': i,
                            'pattern': 'hardcoded_root_file',
                            'target_file': match,
                            'code_snippet': line.strip()[:100],
                            'severity': 'MEDIUM'
                        })

        except Exception as e:
            pass  # Skip files that can't be read

        return violations

    def scan_repository(self) -> None:
        """Scan all Python scripts in repository"""
        print("=" * 80)
        print("ROOT-WRITER SCANNER")
        print("=" * 80)
        print()

        print(f"Scanning repository: {self.repo_root}")
        print()

        # Find all Python scripts
        python_files = list(self.repo_root.rglob("*.py"))
        python_files = [f for f in python_files if '.git' not in str(f) and '__pycache__' not in str(f)]

        print(f"Found {len(python_files)} Python scripts")
        print("Scanning for root-writing patterns...")
        print()

        for script in python_files:
            self.stats['scripts_scanned'] += 1
            violations = self.scan_script(script)
            self.violations.extend(violations)

            if violations:
                print(f"⚠️ {len(violations)} violation(s) in {script.relative_to(self.repo_root)}")

        self.stats['violations_found'] = len(self.violations)

        # Group by pattern
        for v in self.violations:
            pattern = v['pattern']
            self.stats['patterns_detected'][pattern] = self.stats['patterns_detected'].get(pattern, 0) + 1

    def generate_report(self) -> Dict:
        """Generate analysis report"""

        # Group violations by file
        by_file = {}
        for v in self.violations:
            file = v['file']
            if file not in by_file:
                by_file[file] = []
            by_file[file].append(v)

        # Group by target file
        by_target = {}
        for v in self.violations:
            target = v['target_file']
            if target not in by_target:
                by_target[target] = []
            by_target[target].append(v['file'])

        # Top offenders
        top_offenders = sorted(by_file.items(), key=lambda x: len(x[1]), reverse=True)[:20]

        report = {
            'version': '1.0',
            'generated_at': datetime.now(timezone.utc).isoformat(),
            'repository_root': str(self.repo_root),
            'statistics': self.stats,
            'violations': self.violations,
            'by_file': {k: len(v) for k, v in by_file.items()},
            'by_target_file': by_target,
            'top_offenders': [
                {
                    'script': file,
                    'violation_count': len(violations),
                    'violations': violations
                }
                for file, violations in top_offenders
            ]
        }

        return report

    def print_summary(self, report: Dict) -> None:
        """Print summary to console"""
        print()
        print("=" * 80)
        print("SCAN RESULTS")
        print("=" * 80)
        print()

        stats = report['statistics']
        print(f"Scripts scanned:    {stats['scripts_scanned']}")
        print(f"Violations found:   {stats['violations_found']}")
        print()

        print("Violations by pattern:")
        for pattern, count in stats['patterns_detected'].items():
            print(f"  {pattern:30s} {count:3d}")
        print()

        if report['top_offenders']:
            print("Top 10 offending scripts:")
            for i, offender in enumerate(report['top_offenders'][:10], 1):
                print(f"  {i:2d}. {offender['script']:60s} ({offender['violation_count']} violations)")
            print()

        print("Target files being written to root:")
        target_files = set()
        for v in self.violations:
            target_files.add(v['target_file'])
        for target in sorted(target_files)[:20]:
            count = len(report['by_target_file'].get(target, []))
            print(f"  - {target:50s} ({count} scripts)")
        print()

def main():
    """Main execution"""
    repo_root = Path(__file__).parent.parent.parent

    scanner = RootWriterScanner(repo_root)
    scanner.scan_repository()

    report = scanner.generate_report()
    scanner.print_summary(report)

    # Write report
    output_dir = repo_root / '02_audit_logging' / 'reports'
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / 'root_writers_analysis.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"✅ Report written: {output_file}")
    print()

    # Exit with violation count
    sys.exit(1 if report['statistics']['violations_found'] > 0 else 0)

if __name__ == "__main__":
    main()
