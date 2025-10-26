#!/usr/bin/env python3
"""
StructureGuard Integration with SoT Validator
==============================================

This module integrates the existing StructureGuard system
(12_tooling/structure/structure_guard.py) with the SoT validation engine.

Features:
- ROOT-24-LOCK enforcement
- Placeholder detection (TODO, FIXME, PLACEHOLDER, STUB, MOCK, XXX)
- SoT artefact presence checking (chart.yaml, manifest.yaml)
- Root violation detection
- Integration with OPA policies (23_compliance/opa/structure_guard_v5.rego)
"""

import re
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class StructureGuardResult:
    """Result from StructureGuard validation"""
    status: str  # 'PASS' or 'FAIL'
    violations: List[Dict[str, Any]]
    files_scanned: int
    placeholder_count: int
    root_violations: int
    sot_missing: int
    timestamp: str


class StructureGuardValidator:
    """
    Unified StructureGuard Validator

    Integrates:
    1. Python StructureGuard (12_tooling/structure/structure_guard.py)
    2. OPA Policy (23_compliance/opa/structure_guard_v5.rego)
    3. SoT validation engine
    """

    # ROOT-24-LOCK: Official 24 root directories
    ALLOWED_ROOTS = [
        "01_ai_layer", "02_audit_logging", "03_core", "04_deployment",
        "05_documentation", "06_data_pipeline", "07_governance_legal",
        "08_identity_score", "09_meta_identity", "10_interoperability",
        "11_test_simulation", "12_tooling", "13_ui_layer", "14_zero_time_auth",
        "15_infra", "16_codex", "17_observability", "18_data_layer",
        "19_adapters", "20_foundation", "21_post_quantum_crypto",
        "22_datasets", "23_compliance", "24_meta_orchestration"
    ]

    # Additional allowed entries (hidden/config files)
    ALLOWED_SPECIAL = [
        ".github", ".git", ".gitattributes", ".gitmodules", ".gitignore",
        "LICENSE", "README.md", ".claude", "ssid_validator", ".pytest",
        ".pytest_cache", ".coverage", "__pycache__", ".venv", "venv",
        "pytest.ini", ".ssid_cache"
    ]

    # Placeholder patterns
    PLACEHOLDER_PATTERNS = re.compile(
        r"\b(TODO|FIXME|PLACEHOLDER|STUB|MOCK|XXX)\b",
        re.IGNORECASE
    )

    # Required SoT artefacts per root
    REQUIRED_SOT_ARTEFACTS = ["chart.yaml", "manifest.yaml"]

    # File extensions to scan for placeholders
    SCANNABLE_EXTENSIONS = {".py", ".rego", ".ts", ".sh", ".yml", ".yaml", ".md", ".json"}

    def __init__(self, repo_root: Path):
        self.repo_root = Path(repo_root).resolve()
        self.structure_guard_script = self.repo_root / "12_tooling/structure/structure_guard.py"
        self.policy_config = self.repo_root / "23_compliance/config/root_24_lock_policy.yaml"
        self.opa_policy = self.repo_root / "23_compliance/opa/structure_guard_v5.rego"

    def validate_all(self) -> StructureGuardResult:
        """
        Run comprehensive structure validation

        Returns:
            StructureGuardResult with all findings
        """
        violations = []
        files_scanned = 0
        placeholder_count = 0

        # 1. Validate ROOT-24-LOCK
        root_violations = self._validate_root_structure()
        violations.extend(root_violations)

        # 2. Scan for placeholders
        placeholder_violations = self._scan_placeholders()
        violations.extend(placeholder_violations)
        placeholder_count = len(placeholder_violations)

        # 3. Check SoT artefact presence
        sot_violations = self._check_sot_artefacts()
        violations.extend(sot_violations)

        # 4. Count scanned files
        files_scanned = self._count_scannable_files()

        status = "PASS" if len(violations) == 0 else "FAIL"

        return StructureGuardResult(
            status=status,
            violations=violations,
            files_scanned=files_scanned,
            placeholder_count=placeholder_count,
            root_violations=len(root_violations),
            sot_missing=len(sot_violations),
            timestamp=datetime.utcnow().isoformat()
        )

    def _validate_root_structure(self) -> List[Dict[str, Any]]:
        """
        Validate ROOT-24-LOCK: No additional root directories allowed

        Returns:
            List of violations
        """
        violations = []
        all_allowed = set(self.ALLOWED_ROOTS) | set(self.ALLOWED_SPECIAL)

        # Check all top-level entries
        for entry in self.repo_root.iterdir():
            # Skip files at root (handled separately)
            if entry.is_file():
                continue

            if entry.name not in all_allowed:
                violations.append({
                    "type": "root_violation",
                    "path": entry.name,
                    "message": f"ROOT-24-LOCK violation: '{entry.name}' not in allowed roots"
                })

        # Verify all 24 numbered roots exist
        existing_roots = {d.name for d in self.repo_root.iterdir()
                         if d.is_dir() and re.match(r'^\d{2}_', d.name)}

        missing_roots = set(self.ALLOWED_ROOTS) - existing_roots
        if missing_roots:
            violations.append({
                "type": "missing_roots",
                "paths": list(missing_roots),
                "message": f"Missing required root directories: {', '.join(sorted(missing_roots))}"
            })

        return violations

    def _scan_placeholders(self) -> List[Dict[str, Any]]:
        """
        Scan all code files for placeholder markers

        Returns:
            List of files containing placeholders
        """
        violations = []

        for file_path in self.repo_root.rglob("*"):
            if not file_path.is_file():
                continue

            # Only scan relevant file types
            if file_path.suffix not in self.SCANNABLE_EXTENSIONS:
                continue

            # Skip archived/backup files
            if any(x in file_path.parts for x in ['99_archives', '__pycache__', '.git', 'node_modules']):
                continue

            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')

                if self.PLACEHOLDER_PATTERNS.search(content):
                    rel_path = file_path.relative_to(self.repo_root).as_posix()

                    # Find specific matches
                    matches = self.PLACEHOLDER_PATTERNS.findall(content)

                    violations.append({
                        "type": "placeholder_detected",
                        "path": rel_path,
                        "markers": list(set(matches)),
                        "message": f"Placeholder markers found: {', '.join(set(matches))}"
                    })
            except Exception as e:
                # Skip files that can't be read
                pass

        return violations

    def _check_sot_artefacts(self) -> List[Dict[str, Any]]:
        """
        Check that each root has required SoT artefacts

        Returns:
            List of missing artefact violations
        """
        violations = []

        for root_name in self.ALLOWED_ROOTS:
            root_dir = self.repo_root / root_name

            if not root_dir.exists() or not root_dir.is_dir():
                continue

            for required_file in self.REQUIRED_SOT_ARTEFACTS:
                artefact_path = root_dir / required_file

                if not artefact_path.exists():
                    violations.append({
                        "type": "sot_missing",
                        "root": root_name,
                        "file": required_file,
                        "message": f"Missing SoT artefact: {root_name}/{required_file}"
                    })

        return violations

    def _count_scannable_files(self) -> int:
        """Count total number of scannable files"""
        count = 0
        for file_path in self.repo_root.rglob("*"):
            if not file_path.is_file():
                continue
            if file_path.suffix in self.SCANNABLE_EXTENSIONS:
                if not any(x in file_path.parts for x in ['99_archives', '__pycache__', '.git']):
                    count += 1
        return count

    def run_legacy_structure_guard(self) -> Dict[str, Any]:
        """
        Run the legacy StructureGuard script

        Returns:
            Dict with results from structure_guard.py
        """
        if not self.structure_guard_script.exists():
            return {
                "status": "ERROR",
                "message": "StructureGuard script not found"
            }

        if not self.policy_config.exists():
            return {
                "status": "ERROR",
                "message": "Policy config not found"
            }

        try:
            # Run structure_guard.py
            report_path = self.repo_root / "02_audit_logging/reports/structure_guard_report.json"

            cmd = [
                sys.executable,
                str(self.structure_guard_script),
                "--policy", str(self.policy_config),
                "--report", str(report_path)
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(self.repo_root)
            )

            # Load report
            if report_path.exists():
                with open(report_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return {
                    "status": "ERROR",
                    "message": "Report file not generated",
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }
        except Exception as e:
            return {
                "status": "ERROR",
                "message": f"Failed to run StructureGuard: {str(e)}"
            }

    def validate_with_opa(self, mutation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a mutation against OPA policy

        Args:
            mutation: Dict describing a file system mutation
                {
                    "action": "write_file" | "create_dir",
                    "path": {
                        "full": "C:/Users/.../file.py",
                        "root": "03_core",
                        "name": "file.py",
                        "depth": 2
                    }
                }

        Returns:
            Dict with allow/deny decision
        """
        if not self.opa_policy.exists():
            return {
                "allow": False,
                "errors": ["OPA policy not found"]
            }

        try:
            # Format input for OPA
            opa_input = {
                "mutation": mutation
            }

            # Run OPA evaluation
            cmd = [
                "opa", "eval",
                "-d", str(self.opa_policy),
                "-i", "-",
                "data.ssid.v5.structure"
            ]

            result = subprocess.run(
                cmd,
                input=json.dumps(opa_input),
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                output = json.loads(result.stdout)
                return output
            else:
                return {
                    "allow": False,
                    "errors": [result.stderr]
                }
        except FileNotFoundError:
            return {
                "allow": False,
                "errors": ["OPA binary not found - install from https://www.openpolicyagent.org/"]
            }
        except Exception as e:
            return {
                "allow": False,
                "errors": [f"OPA evaluation failed: {str(e)}"]
            }

    def generate_report(self, result: StructureGuardResult, output_path: Optional[Path] = None) -> str:
        """
        Generate human-readable report

        Returns:
            Report as string
        """
        lines = []
        lines.append("=" * 80)
        lines.append("STRUCTUREGUARD VALIDATION REPORT")
        lines.append("=" * 80)
        lines.append(f"Status: {result.status}")
        lines.append(f"Timestamp: {result.timestamp}")
        lines.append(f"Files Scanned: {result.files_scanned}")
        lines.append(f"Total Violations: {len(result.violations)}")
        lines.append(f"  - Root Violations: {result.root_violations}")
        lines.append(f"  - Placeholder Files: {result.placeholder_count}")
        lines.append(f"  - Missing SoT Artefacts: {result.sot_missing}")
        lines.append("")

        if result.violations:
            lines.append("VIOLATIONS:")
            lines.append("-" * 80)

            for i, violation in enumerate(result.violations, 1):
                lines.append(f"{i}. [{violation['type']}] {violation['message']}")
                if 'path' in violation:
                    lines.append(f"   Path: {violation['path']}")
                if 'paths' in violation:
                    for path in violation['paths']:
                        lines.append(f"   - {path}")
                lines.append("")
        else:
            lines.append("No violations found. Structure is compliant.")

        lines.append("=" * 80)

        report = "\n".join(lines)

        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(report, encoding='utf-8')

        return report


def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="StructureGuard Validator - ROOT-24-LOCK enforcement"
    )
    parser.add_argument(
        '--repo-root',
        type=Path,
        default=Path.cwd(),
        help='Repository root directory'
    )
    parser.add_argument(
        '--output',
        type=Path,
        help='Output report file (JSON)'
    )
    parser.add_argument(
        '--report',
        type=Path,
        help='Output human-readable report (TXT)'
    )
    parser.add_argument(
        '--legacy',
        action='store_true',
        help='Run legacy StructureGuard script'
    )

    args = parser.parse_args()

    validator = StructureGuardValidator(args.repo_root)

    if args.legacy:
        # Run legacy script
        result = validator.run_legacy_structure_guard()
        print(json.dumps(result, indent=2))
        sys.exit(0 if result.get('status') == 'PASS' else 1)
    else:
        # Run new integrated validator
        result = validator.validate_all()

        # Generate report
        report_text = validator.generate_report(result, args.report)
        print(report_text)

        # Save JSON output
        if args.output:
            output_data = {
                "status": result.status,
                "timestamp": result.timestamp,
                "summary": {
                    "files_scanned": result.files_scanned,
                    "total_violations": len(result.violations),
                    "root_violations": result.root_violations,
                    "placeholder_count": result.placeholder_count,
                    "sot_missing": result.sot_missing
                },
                "violations": result.violations
            }

            args.output.parent.mkdir(parents=True, exist_ok=True)
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)

            print(f"\nJSON output saved to: {args.output}")

        sys.exit(0 if result.status == "PASS" else 1)


if __name__ == '__main__':
    main()
