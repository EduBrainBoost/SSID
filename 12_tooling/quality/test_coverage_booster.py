#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Coverage Booster - SSID Quality Suite
Author: SSID Codex Engine ©2025 MIT License

Analyzes codebase for missing test coverage and provides recommendations.
Advisory tool - does not fail on low coverage, provides actionable insights.

Exit Codes:
  0 - PASS (always, advisory only)
"""

import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Set
from dataclasses import dataclass, asdict

ROOT = Path(__file__).resolve().parents[2]
TEST_DIR = ROOT / "11_test_simulation"
REPORT_DIR = ROOT / "02_audit_logging" / "reports"

# Roots to scan for production code
PRODUCTION_ROOTS = [
    "01_ai_layer",
    "02_audit_logging",
    "03_core",
    "08_identity_score",
    "09_meta_identity",
    "10_interoperability",
    "14_zero_time_auth",
    "20_foundation",
    "23_compliance",
    "24_meta_orchestration",
]

@dataclass
class ModuleInfo:
    """Production module information."""
    module_path: str
    module_name: str
    root: str
    has_test: bool
    test_paths: List[str]
    line_count: int

class CoverageAnalyzer:
    """Analyzes test coverage heuristically."""

    def __init__(self):
        """Initialize analyzer."""
        self.production_modules: List[ModuleInfo] = []
        self.test_files: Set[str] = set()

    def _count_lines(self, file_path: Path) -> int:
        """Count non-empty, non-comment lines in Python file."""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()

            count = 0
            for line in lines:
                stripped = line.strip()
                # Skip empty lines and pure comments
                if stripped and not stripped.startswith("#"):
                    count += 1
            return count
        except Exception:
            return 0

    def _find_test_files(self) -> None:
        """Index all test files."""
        if not TEST_DIR.exists():
            return

        for test_file in TEST_DIR.rglob("test_*.py"):
            self.test_files.add(str(test_file.relative_to(ROOT)))

    def _find_matching_tests(self, module_name: str, root: str) -> List[str]:
        """Find tests that likely cover this module (heuristic)."""
        matching_tests = []

        # Extract module name without extension
        clean_name = module_name.replace(".py", "").replace("/", "_")
        root_name = root.split("_", 1)[1] if "_" in root else root

        for test_path in self.test_files:
            test_path_lower = test_path.lower()

            # Check if test name contains module name or root name
            if clean_name.lower() in test_path_lower or root_name.lower() in test_path_lower:
                matching_tests.append(test_path)

        return matching_tests

    def scan_production_code(self) -> None:
        """Scan production roots for Python modules."""
        self._find_test_files()

        for root in PRODUCTION_ROOTS:
            root_path = ROOT / root
            if not root_path.exists():
                continue

            # Find all Python files (excluding tests, __pycache__, etc.)
            for py_file in root_path.rglob("*.py"):
                # Skip test files, __init__.py, and special dirs
                if (
                    "test_" in py_file.name
                    or py_file.name == "__init__.py"
                    or "__pycache__" in str(py_file)
                    or "venv" in str(py_file)
                ):
                    continue

                rel_path = py_file.relative_to(ROOT)
                module_name = py_file.stem

                # Find matching tests
                test_paths = self._find_matching_tests(str(rel_path), root)
                has_test = len(test_paths) > 0

                # Count lines
                line_count = self._count_lines(py_file)

                module_info = ModuleInfo(
                    module_path=str(rel_path),
                    module_name=module_name,
                    root=root,
                    has_test=has_test,
                    test_paths=test_paths,
                    line_count=line_count
                )
                self.production_modules.append(module_info)

    def run_pytest(self) -> Dict[str, Any]:
        """Run pytest to get actual coverage (advisory only)."""
        pytest_result = {
            "executed": False,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "total": 0,
            "error": None
        }

        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "--collect-only", "-q"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                timeout=30
            )

            pytest_result["executed"] = True

            # Parse output for test count
            output = result.stdout + result.stderr
            for line in output.split("\n"):
                if "collected" in line.lower():
                    # Extract number from "285 tests collected"
                    parts = line.split()
                    for part in parts:
                        if part.isdigit():
                            pytest_result["total"] = int(part)
                            break

        except Exception as e:
            pytest_result["error"] = str(e)

        return pytest_result

def generate_report(analyzer: CoverageAnalyzer, pytest_result: Dict[str, Any]) -> Dict[str, Any]:
    """Generate coverage analysis report."""
    untested_modules = [m for m in analyzer.production_modules if not m.has_test]
    tested_modules = [m for m in analyzer.production_modules if m.has_test]

    total_lines = sum(m.line_count for m in analyzer.production_modules)
    untested_lines = sum(m.line_count for m in untested_modules)

    coverage_estimate = (
        ((total_lines - untested_lines) / total_lines * 100)
        if total_lines > 0
        else 0.0
    )

    report = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "tool": "test_coverage_booster",
        "version": "1.0.0",
        "summary": {
            "total_modules": len(analyzer.production_modules),
            "tested_modules": len(tested_modules),
            "untested_modules": len(untested_modules),
            "total_lines": total_lines,
            "untested_lines": untested_lines,
            "estimated_coverage_percent": round(coverage_estimate, 2),
        },
        "pytest_info": pytest_result,
        "recommendations": {
            "priority_modules": [
                {
                    "module": m.module_path,
                    "root": m.root,
                    "lines": m.line_count,
                    "reason": "High line count, no tests"
                }
                for m in sorted(untested_modules, key=lambda x: x.line_count, reverse=True)[:10]
            ]
        },
        "untested_modules": [asdict(m) for m in untested_modules],
        "tested_modules": [
            {
                "module": m.module_path,
                "root": m.root,
                "test_count": len(m.test_paths),
                "tests": m.test_paths
            }
            for m in tested_modules
        ]
    }

    return report

def save_report(report: Dict[str, Any], emit_json: bool) -> Path:
    """Save report to evidence directory."""
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    report_path = REPORT_DIR / f"coverage_advice_{timestamp}.json"

    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, sort_keys=True)

    # Also save as latest
    latest_path = REPORT_DIR / "coverage_advice_latest.json"
    with open(latest_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, sort_keys=True)

    if emit_json:
        print(json.dumps(report, indent=2))

    return report_path

def main() -> int:
    """Main execution."""
    import argparse

    parser = argparse.ArgumentParser(
        description="SSID Test Coverage Booster - Quality Advisory Tool"
    )
    parser.add_argument(
        "--emit-json",
        action="store_true",
        help="Emit full JSON report to stdout"
    )
    parser.add_argument(
        "--run-pytest",
        action="store_true",
        help="Run pytest collection (slower)"
    )

    args = parser.parse_args()

    if not args.emit_json:
        print("SSID Test Coverage Booster")
        print("=" * 60)
        print(f"Root: {ROOT}")
        print()

    # Initialize analyzer
    analyzer = CoverageAnalyzer()

    # Scan production code
    if not args.emit_json:
        print("Scanning production modules...")
    analyzer.scan_production_code()

    # Run pytest if requested
    pytest_result = {"executed": False}
    if args.run_pytest:
        if not args.emit_json:
            print("Running pytest collection...")
        pytest_result = analyzer.run_pytest()

    # Generate report
    report = generate_report(analyzer, pytest_result)
    report_path = save_report(report, args.emit_json)

    # Display summary
    if not args.emit_json:
        print()
        print("=" * 60)
        print(f"Total Modules: {report['summary']['total_modules']}")
        print(f"Tested: {report['summary']['tested_modules']}")
        print(f"Untested: {report['summary']['untested_modules']}")
        print(f"Estimated Coverage: {report['summary']['estimated_coverage_percent']}%")
        print()

        if report['recommendations']['priority_modules']:
            print("Top Priority Modules (high LOC, no tests):")
            for i, mod in enumerate(report['recommendations']['priority_modules'][:5], 1):
                print(f"  {i}. {mod['module']} ({mod['lines']} lines)")
            print()

        if pytest_result["executed"]:
            print(f"Pytest Tests Collected: {pytest_result.get('total', 0)}")
            print()

        print(f"Report: {report_path}")
        print()
        print("Status: PASS (advisory only)")

    return 0

if __name__ == "__main__":
    sys.exit(main())
