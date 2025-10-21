#!/usr/bin/env python3
"""
SSID Forensic Integrity Validation - Phase 1: Root Structure Integrity
Scans all 24 root modules × versions v1-v12 for structural completeness
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime, timezone

# Expected 24 root modules
ROOT_MODULES = [
    "01_ai_layer", "02_audit_logging", "03_core", "04_deployment",
    "05_documentation", "06_data_pipeline", "07_governance_legal",
    "08_identity_score", "09_meta_identity", "10_interoperability",
    "11_test_simulation", "12_tooling", "13_ui_layer", "14_zero_time_auth",
    "15_infra", "16_codex", "17_observability", "18_data_layer",
    "19_adapters", "20_foundation", "21_post_quantum_crypto", "22_datasets",
    "23_compliance", "24_meta_orchestration"
]

# Expected versions v1.0 through v12.0
EXPECTED_VERSIONS = [f"v{i}.0" for i in range(1, 13)]

class RootStructureScanner:
    """Scans Root-24 structure for version completeness"""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.results = []
        self.total_violations = 0
        self.scan_timestamp = datetime.now(timezone.utc).isoformat()

    def scan_module(self, module_name: str) -> Dict[str, Any]:
        """Scan a single root module for version artifacts"""
        module_path = self.repo_root / module_name

        result = {
            "root_id": module_name,
            "path": str(module_path),
            "exists": module_path.exists(),
            "chart_yaml_present": False,
            "manifest_yaml_present": False,
            "versions_detected": [],
            "missing_files": [],
            "status": "FAIL"
        }

        if not module_path.exists():
            result["missing_files"].append("directory")
            return result

        # Check for chart.yaml
        chart_path = module_path / "chart.yaml"
        result["chart_yaml_present"] = chart_path.exists()
        if not chart_path.exists():
            result["missing_files"].append("chart.yaml")

        # Check for manifest.yaml
        manifest_path = module_path / "manifest.yaml"
        result["manifest_yaml_present"] = manifest_path.exists()
        if not manifest_path.exists():
            result["missing_files"].append("manifest.yaml")

        # Detect versions in documentation/artifacts
        detected_versions = self._detect_versions(module_path)
        result["versions_detected"] = detected_versions

        # Determine status
        if result["chart_yaml_present"] and result["manifest_yaml_present"]:
            result["status"] = "PASS"
        else:
            result["status"] = "PARTIAL" if result["chart_yaml_present"] or result["manifest_yaml_present"] else "FAIL"

        return result

    def _detect_versions(self, module_path: Path) -> List[str]:
        """Detect version references in module artifacts"""
        versions = set()

        # Search for version patterns in key files
        search_patterns = [
            "chart.yaml",
            "manifest.yaml",
            "README.md",
            "CHANGELOG.md"
        ]

        for pattern in search_patterns:
            file_path = module_path / pattern
            if file_path.exists():
                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    # Look for v1.0, v2.0, etc.
                    for version in EXPECTED_VERSIONS:
                        if version in content or version.replace('.', '_') in content:
                            versions.add(version)
                except Exception:
                    pass

        return sorted(list(versions))

    def scan_all(self) -> Dict[str, Any]:
        """Scan all 24 root modules"""
        print(f"🔬 PHASE 1: Root-24 Structure Integrity Scan")
        print(f"=" * 80)
        print(f"Scanning {len(ROOT_MODULES)} root modules for version artifacts v1.0 - v12.0")
        print()

        for module_name in ROOT_MODULES:
            result = self.scan_module(module_name)
            self.results.append(result)

            status_icon = "✅" if result["status"] == "PASS" else "⚠️" if result["status"] == "PARTIAL" else "❌"
            print(f"{status_icon} {module_name:30} | chart.yaml: {result['chart_yaml_present']} | manifest.yaml: {result['manifest_yaml_present']}")

            if result["missing_files"]:
                self.total_violations += len(result["missing_files"])

        # Calculate summary
        passed = sum(1 for r in self.results if r["status"] == "PASS")
        partial = sum(1 for r in self.results if r["status"] == "PARTIAL")
        failed = sum(1 for r in self.results if r["status"] == "FAIL")

        structure_score = (passed / len(ROOT_MODULES)) * 100

        summary = {
            "scan_phase": "Phase 1: Root Structure Integrity",
            "timestamp": self.scan_timestamp,
            "scope": f"{len(ROOT_MODULES)} root modules",
            "expected_versions": EXPECTED_VERSIONS,
            "results": self.results,
            "summary": {
                "total_modules": len(ROOT_MODULES),
                "passed": passed,
                "partial": partial,
                "failed": failed,
                "total_violations": self.total_violations,
                "structure_integrity_score": round(structure_score, 2),
                "status": "PASS" if structure_score == 100.0 else "PARTIAL" if structure_score >= 90.0 else "FAIL"
            }
        }

        print()
        print(f"=" * 80)
        print(f"📊 Summary:")
        print(f"   Total Modules:   {len(ROOT_MODULES)}")
        print(f"   ✅ Passed:       {passed}")
        print(f"   ⚠️ Partial:       {partial}")
        print(f"   ❌ Failed:        {failed}")
        print(f"   🔍 Violations:   {self.total_violations}")
        print(f"   📈 Score:        {structure_score:.2f}/100")
        print(f"   Status:          {summary['summary']['status']}")
        print()

        return summary

    def check_root_24_lock(self) -> bool:
        """Check if any files exist outside the 24 root directories"""
        print(f"🔒 Checking Root-24-LOCK enforcement...")

        violations = []

        # Check for top-level files (some are allowed like README.md, .gitignore)
        # ROOT-24-LOCK: Only 4-FILE-LOCK allowed + temporary test/config files
        allowed_files = {
            "README.md", ".gitignore", ".gitattributes", "LICENSE",
            "pytest.ini", ".github", ".pre-commit-config.yaml"
        }

        for item in self.repo_root.iterdir():
            if item.is_file():
                if item.name not in allowed_files:
                    violations.append(f"Unexpected root file: {item.name}")
            elif item.is_dir():
                if item.name not in ROOT_MODULES and not item.name.startswith('.'):
                    violations.append(f"Unexpected root directory: {item.name}")

        if violations:
            print(f"   ❌ Root-24-LOCK violations detected: {len(violations)}")
            for v in violations[:5]:  # Show first 5
                print(f"      - {v}")
            return False
        else:
            print(f"   ✅ Root-24-LOCK enforced: All files within 24 root modules")
            return True

    def save_report(self, summary: Dict[str, Any]):
        """Save the structure integrity report"""
        output_dir = self.repo_root / "02_audit_logging" / "reports"
        output_dir.mkdir(parents=True, exist_ok=True)

        output_file = output_dir / "root_structure_integrity_v1_v12.json"

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        print(f"💾 Report saved: {output_file}")

        return output_file

def main():
    """Main execution"""
    repo_root = Path(__file__).resolve().parents[2]

    scanner = RootStructureScanner(repo_root)

    # Phase 1a: Scan module structure
    summary = scanner.scan_all()

    # Phase 1b: Check Root-24-LOCK
    lock_enforced = scanner.check_root_24_lock()
    summary["root_24_lock_enforced"] = lock_enforced

    # Save report
    report_path = scanner.save_report(summary)

    # Exit code
    exit_code = 0 if summary["summary"]["status"] == "PASS" and lock_enforced else 1

    print()
    print(f"✅ Phase 1 Complete" if exit_code == 0 else f"⚠️ Phase 1 Complete with Issues")
    print(f"📄 Full report: {report_path}")

    return exit_code

if __name__ == "__main__":
    sys.exit(main())
