#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Placeholder Removal Tool - SSID Anti-Gaming Suite
Author: SSID Codex Engine ©2025 MIT License

Scans codebase for placeholder patterns and optionally removes them.
Generates deterministic WORM-compatible evidence reports.

Exit Codes:
  0 - PASS (no violations or all fixed)
  1 - FAIL (violations found in dry-run mode)
  2 - ERROR (configuration or I/O error)
"""

import sys
import json
import yaml
import re
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict


ROOT = Path(__file__).resolve().parents[2]
PATTERNS_CONFIG = Path(__file__).parent / "placeholder_patterns.yaml"
REPORT_DIR = ROOT / "02_audit_logging" / "reports"


@dataclass
class Violation:
    """Placeholder violation record."""
    file_path: str
    line_number: int
    pattern: str
    severity: str
    description: str
    matched_text: str
    context_before: List[str]
    context_after: List[str]


class PlaceholderScanner:
    """Scans files for placeholder patterns."""

    def __init__(self, config_path: Path):
        """Initialize scanner with configuration."""
        self.config = self._load_config(config_path)
        self.violations: List[Violation] = []

    def _load_config(self, config_path: Path) -> Dict[str, Any]:
        """Load pattern configuration from YAML."""
        if not config_path.exists():
            print(f"ERROR: Config file not found: {config_path}")
            sys.exit(2)

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"ERROR: Failed to load config: {e}")
            sys.exit(2)

    def _should_exclude(self, file_path: Path) -> bool:
        """Check if file should be excluded from scanning."""
        file_str = str(file_path)
        exclusions = self.config.get("exclusions", {})

        # Check path exclusions
        for pattern in exclusions.get("paths", []):
            if pattern.replace("*", "") in file_str:
                return True

        # Check file pattern exclusions
        for pattern in exclusions.get("patterns", []):
            if file_path.match(pattern.replace("*", "")):
                return True

        return False

    def _get_context_lines(self, lines: List[str], line_idx: int, context: int = 2) -> tuple:
        """Extract context lines around match."""
        before = lines[max(0, line_idx - context):line_idx]
        after = lines[line_idx + 1:line_idx + context + 1]
        return before, after

    def scan_file(self, file_path: Path, file_type: str) -> List[Violation]:
        """Scan a single file for placeholder patterns."""
        if self._should_exclude(file_path):
            return []

        if not file_path.exists() or not file_path.is_file():
            return []

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
        except Exception as e:
            print(f"WARNING: Could not read {file_path}: {e}")
            return []

        violations = []
        patterns = self.config.get("patterns", {}).get(file_type, [])

        for pattern_def in patterns:
            pattern = pattern_def["pattern"]
            severity = pattern_def["severity"]
            description = pattern_def["description"]

            regex = re.compile(pattern, re.IGNORECASE)

            for idx, line in enumerate(lines):
                match = regex.search(line)
                if match:
                    context_before, context_after = self._get_context_lines(lines, idx)

                    violation = Violation(
                        file_path=str(file_path.relative_to(ROOT)),
                        line_number=idx + 1,
                        pattern=pattern,
                        severity=severity,
                        description=description,
                        matched_text=match.group(0),
                        context_before=[l.rstrip() for l in context_before],
                        context_after=[l.rstrip() for l in context_after]
                    )
                    violations.append(violation)

        return violations

    def scan_directory(self, root_dir: Path) -> None:
        """Scan directory recursively for placeholders."""
        # Scan Python files
        for py_file in root_dir.rglob("*.py"):
            violations = self.scan_file(py_file, "python")
            self.violations.extend(violations)

        # Scan Markdown files
        for md_file in root_dir.rglob("*.md"):
            violations = self.scan_file(md_file, "markdown")
            self.violations.extend(violations)

        # Scan YAML files
        for yaml_file in root_dir.rglob("*.yaml"):
            violations = self.scan_file(yaml_file, "yaml")
            self.violations.extend(violations)

        for yml_file in root_dir.rglob("*.yml"):
            violations = self.scan_file(yml_file, "yaml")
            self.violations.extend(violations)


def generate_report(scanner: PlaceholderScanner, mode: str) -> Dict[str, Any]:
    """Generate violation report."""
    report = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "tool": "placeholder_removal_tool",
        "version": scanner.config.get("metadata", {}).get("version", "1.0.0"),
        "mode": mode,
        "summary": {
            "total_violations": len(scanner.violations),
            "by_severity": {
                "high": sum(1 for v in scanner.violations if v.severity == "high"),
                "medium": sum(1 for v in scanner.violations if v.severity == "medium"),
                "low": sum(1 for v in scanner.violations if v.severity == "low"),
            },
            "files_affected": len(set(v.file_path for v in scanner.violations))
        },
        "violations": [asdict(v) for v in scanner.violations]
    }
    return report


def save_report(report: Dict[str, Any]) -> Path:
    """Save report to evidence directory."""
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    report_path = REPORT_DIR / f"placeholder_violations_{timestamp}.json"

    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, sort_keys=True)

    return report_path


def remove_placeholders(violations: List[Violation]) -> int:
    """Remove placeholder violations from files."""
    files_modified = 0
    violations_by_file = {}

    # Group violations by file
    for violation in violations:
        file_path = violation.file_path
        if file_path not in violations_by_file:
            violations_by_file[file_path] = []
        violations_by_file[file_path].append(violation)

    # Process each file
    for file_path, file_violations in violations_by_file.items():
        full_path = ROOT / file_path

        try:
            with open(full_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            # Sort violations by line number (descending) to avoid index shifting
            file_violations.sort(key=lambda v: v.line_number, reverse=True)

            modified = False
            for violation in file_violations:
                line_idx = violation.line_number - 1
                if line_idx < len(lines):
                    # Remove the line containing placeholder
                    lines.pop(line_idx)
                    modified = True

            if modified:
                with open(full_path, "w", encoding="utf-8") as f:
                    f.writelines(lines)
                files_modified += 1
                print(f"  [FIXED] {file_path}")

        except Exception as e:
            print(f"  [ERROR] Failed to fix {file_path}: {e}")

    return files_modified


def main() -> int:
    """Main execution."""
    parser = argparse.ArgumentParser(
        description="SSID Placeholder Removal Tool - Anti-Gaming Suite"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only report violations, do not fix"
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Remove placeholders from files"
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=PATTERNS_CONFIG,
        help="Path to patterns configuration file"
    )

    args = parser.parse_args()

    # Default to dry-run if neither specified
    if not args.dry_run and not args.fix:
        args.dry_run = True

    mode = "dry-run" if args.dry_run else "fix"

    print("SSID Placeholder Removal Tool")
    print("=" * 60)
    print(f"Mode: {mode.upper()}")
    print(f"Config: {args.config}")
    print(f"Root: {ROOT}")
    print()

    # Initialize scanner
    scanner = PlaceholderScanner(args.config)

    # Scan repository
    print("Scanning repository...")
    scanner.scan_directory(ROOT)

    # Generate report
    report = generate_report(scanner, mode)
    report_path = save_report(report)

    # Display summary
    print()
    print("=" * 60)
    print(f"Violations Found: {report['summary']['total_violations']}")
    print(f"  High:   {report['summary']['by_severity']['high']}")
    print(f"  Medium: {report['summary']['by_severity']['medium']}")
    print(f"  Low:    {report['summary']['by_severity']['low']}")
    print(f"Files Affected: {report['summary']['files_affected']}")
    print()

    # Fix mode
    if args.fix:
        print("Removing placeholders...")
        files_modified = remove_placeholders(scanner.violations)
        print(f"Files Modified: {files_modified}")
        print()

    # Report location
    print(f"Report: {report_path}")
    print()

    # Exit code
    if report['summary']['total_violations'] > 0 and args.dry_run:
        print("Status: FAIL (violations found)")
        return 1
    else:
        print("Status: PASS")
        return 0


if __name__ == "__main__":
    sys.exit(main())
