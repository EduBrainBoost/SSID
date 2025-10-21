#!/usr/bin/env python3
"""
SSID Forensic Integrity Validation - Phase 3: Test Completeness
Validates test coverage across v1-v12: 144 tests, fixtures, no xfail markers
"""

import json
import ast
import re
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime, timezone
from collections import defaultdict

# Expected: 24 roots × 6 test types (policy, policy_stub, readiness, etc.)
ROOT_MODULES = [
    "01_ai_layer", "02_audit_logging", "03_core", "04_deployment",
    "05_documentation", "06_data_pipeline", "07_governance_legal",
    "08_identity_score", "09_meta_identity", "10_interoperability",
    "11_test_simulation", "12_tooling", "13_ui_layer", "14_zero_time_auth",
    "15_infra", "16_codex", "17_observability", "18_data_layer",
    "19_adapters", "20_foundation", "21_post_quantum_crypto", "22_datasets",
    "23_compliance", "24_meta_orchestration"
]

class TestCoverageAuditor:
    """Audits test completeness across all versions"""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.test_dir = repo_root / "11_test_simulation"
        self.tests_found = []
        self.xfail_violations = []
        self.fixture_status = {}
        self.scan_timestamp = datetime.now(timezone.utc).isoformat()

    def find_test_files(self) -> List[Path]:
        """Find all test files"""
        test_files = []

        # Find tests in 11_test_simulation
        if self.test_dir.exists():
            for test_file in self.test_dir.rglob("test_*.py"):
                test_files.append(test_file)

        return test_files

    def analyze_test_file(self, test_path: Path) -> Dict[str, Any]:
        """Analyze a single test file"""
        result = {
            "file": str(test_path.relative_to(self.repo_root)),
            "test_count": 0,
            "has_xfail": False,
            "xfail_locations": [],
            "test_functions": []
        }

        try:
            content = test_path.read_text(encoding='utf-8', errors='ignore')

            # Count test functions
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
                    result["test_functions"].append(node.name)
                    result["test_count"] += 1

                    # Check for xfail markers
                    for decorator in node.decorator_list:
                        dec_name = ""
                        if isinstance(decorator, ast.Name):
                            dec_name = decorator.id
                        elif isinstance(decorator, ast.Attribute):
                            dec_name = decorator.attr
                        elif isinstance(decorator, ast.Call):
                            if isinstance(decorator.func, ast.Attribute):
                                dec_name = decorator.func.attr

                        if 'xfail' in dec_name.lower():
                            result["has_xfail"] = True
                            result["xfail_locations"].append(node.name)

        except Exception as e:
            result["error"] = str(e)

        return result

    def check_fixtures(self) -> Dict[str, Any]:
        """Check for fixture files"""
        fixtures_dir = self.repo_root / "16_codex" / "fixtures"
        fixture_summary = {
            "fixtures_dir_exists": fixtures_dir.exists(),
            "fixture_files": [],
            "total_fixtures": 0
        }

        if fixtures_dir.exists():
            for fixture_file in fixtures_dir.rglob("*.json*"):
                fixture_summary["fixture_files"].append(str(fixture_file.relative_to(self.repo_root)))
                fixture_summary["total_fixtures"] += 1

        return fixture_summary

    def audit_all(self) -> Dict[str, Any]:
        """Run complete test audit"""
        print(f"🧪 PHASE 3: Test Completeness Validation")
        print(f"=" * 80)
        print(f"Auditing test coverage across v1-v12")
        print()

        # Find and analyze all test files
        test_files = self.find_test_files()
        total_test_count = 0
        xfail_count = 0

        for test_path in test_files:
            result = self.analyze_test_file(test_path)
            self.tests_found.append(result)
            total_test_count += result["test_count"]

            if result["has_xfail"]:
                xfail_count += len(result["xfail_locations"])
                self.xfail_violations.extend(result["xfail_locations"])

        # Check fixtures
        fixture_summary = self.check_fixtures()

        # Calculate coverage score
        # Expected: ~144 tests minimum (24 roots × 6 test types)
        expected_test_count = 144
        coverage_percentage = min((total_test_count / expected_test_count) * 100, 100.0)

        # Scoring
        test_score = coverage_percentage
        xfail_penalty = min(xfail_count * 5, 50)  # 5 points per xfail, max -50
        fixture_bonus = 10 if fixture_summary["total_fixtures"] >= 24 else 0

        final_score = max(test_score - xfail_penalty + fixture_bonus, 0)

        status = "PASS" if final_score >= 95 and xfail_count == 0 else "PARTIAL" if final_score >= 70 else "FAIL"

        summary = {
            "scan_phase": "Phase 3: Test Completeness Validation",
            "timestamp": self.scan_timestamp,
            "statistics": {
                "total_test_files": len(test_files),
                "total_test_count": total_test_count,
                "expected_test_count": expected_test_count,
                "coverage_percentage": round(coverage_percentage, 2),
                "xfail_count": xfail_count,
                "fixture_count": fixture_summary["total_fixtures"],
                "test_completeness_score": round(final_score, 2),
                "status": status
            },
            "tests": self.tests_found,
            "xfail_violations": self.xfail_violations,
            "fixtures": fixture_summary
        }

        # Print summary
        print(f"=" * 80)
        print(f"📊 Summary:")
        print(f"   Test Files Found:      {len(test_files)}")
        print(f"   Total Tests:           {total_test_count}")
        print(f"   Expected Minimum:      {expected_test_count}")
        print(f"   Coverage:              {coverage_percentage:.2f}%")
        print(f"   xfail Violations:      {xfail_count}")
        print(f"   Fixtures Available:    {fixture_summary['total_fixtures']}")
        print(f"   📈 Test Score:         {final_score:.2f}/100")
        print(f"   Status:                {status}")
        print()

        if xfail_count > 0:
            print(f"⚠️  {xfail_count} tests marked with xfail (should be removed)")
        else:
            print(f"✅ No xfail markers detected")

        return summary

    def save_report(self, summary: Dict[str, Any]):
        """Save test coverage report"""
        output_dir = self.repo_root / "02_audit_logging" / "reports"
        output_dir.mkdir(parents=True, exist_ok=True)

        output_file = output_dir / "test_coverage_status_v1_v12.json"

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        print(f"💾 Report saved: {output_file}")

        return output_file

def main():
    """Main execution"""
    import sys

    repo_root = Path(__file__).resolve().parents[1]

    auditor = TestCoverageAuditor(repo_root)
    summary = auditor.audit_all()
    auditor.save_report(summary)

    print()
    status = summary['statistics']['status']
    if status == "PASS":
        print(f"✅ Phase 3 Complete: Test coverage is complete")
        return 0
    else:
        print(f"⚠️ Phase 3 Complete: Test coverage needs improvement")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
