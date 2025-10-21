#!/usr/bin/env python3
"""
Architecture Rules Validator - AR001-AR010
============================================
Implements Master Rules for SSID 24x16 Matrix Architecture.

Coverage Target: Architecture Rules (AR001-AR010) from master_rules.yaml
Priority: CRITICAL - These rules define the foundational structure

References:
- Master Rules: 16_codex/structure/level3/master_rules.yaml
- Master Definition: 16_codex/ssid_master_definition_corrected_v1.1.1.md
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List
import re


@dataclass
class ArchitectureValidationResult:
    """Result of an architecture rule validation."""
    rule_id: str
    rule_text: str
    passed: bool
    evidence: Dict
    violations: List[str]
    severity: str = "CRITICAL"

    def to_dict(self) -> Dict:
        return {
            "rule_id": self.rule_id,
            "rule_text": self.rule_text,
            "passed": self.passed,
            "evidence": self.evidence,
            "violations": self.violations,
            "severity": self.severity
        }


class ArchitectureValidator:
    """
    Validates SSID repository against Architecture Master Rules (AR001-AR010).

    Usage:
        validator = ArchitectureValidator(repo_path=Path("."))
        results = validator.validate_all()

        for result in results:
            if not result.passed:
                print(f"FAIL: {result.rule_id} - {result.rule_text}")
    """

    def __init__(self, repo_path: Path):
        self.repo_path = Path(repo_path)
        self.root_folders = []
        self.shards = {}

    def validate_all(self) -> List[ArchitectureValidationResult]:
        """Validate all Architecture Rules (AR001-AR010)."""
        return [
            self.validate_ar001_24_root_folders(),
            self.validate_ar002_16_shards_per_root(),
            self.validate_ar003_384_charts(),
            self.validate_ar004_root_folder_format(),
            self.validate_ar005_shard_format(),
            self.validate_ar006_chart_yaml_exists(),
            self.validate_ar007_manifest_yaml_exists(),
            self.validate_ar008_path_structure(),
            self.validate_ar009_implementations_path(),
            self.validate_ar010_contracts_folder(),
        ]

    def _scan_root_folders(self):
        """Scan and cache root folders."""
        if not self.root_folders:
            self.root_folders = [
                d for d in self.repo_path.iterdir()
                if d.is_dir() and re.match(r'^\d{2}_', d.name)
            ]

    def _scan_shards(self):
        """Scan and cache shards per root folder."""
        if not self.shards:
            self._scan_root_folders()
            for root in self.root_folders:
                shards_dir = root / "shards"
                if shards_dir.exists():
                    self.shards[root.name] = [
                        s for s in shards_dir.iterdir()
                        if s.is_dir()
                    ]

    def validate_ar001_24_root_folders(self) -> ArchitectureValidationResult:
        """AR001: Das System MUSS aus exakt 24 Root-Ordnern bestehen."""
        self._scan_root_folders()

        passed = len(self.root_folders) == 24
        violations = []

        if not passed:
            violations.append(
                f"Expected 24 root folders, found {len(self.root_folders)}"
            )
            expected_prefixes = [f"{i:02d}_" for i in range(1, 25)]
            actual_prefixes = [f.name[:3] for f in self.root_folders]
            missing = set(expected_prefixes) - set(actual_prefixes)
            if missing:
                violations.append(f"Missing folders with prefixes: {sorted(missing)}")

        return ArchitectureValidationResult(
            rule_id="AR001",
            rule_text="Das System MUSS aus exakt 24 Root-Ordnern bestehen",
            passed=passed,
            evidence={
                "total_root_folders": len(self.root_folders),
                "root_folders": [f.name for f in self.root_folders]
            },
            violations=violations
        )

    def validate_ar002_16_shards_per_root(self) -> ArchitectureValidationResult:
        """AR002: Jeder Root-Ordner MUSS exakt 16 Shards enthalten."""
        self._scan_shards()

        violations = []
        evidence = {}

        for root_name, shard_list in self.shards.items():
            shard_count = len(shard_list)
            evidence[root_name] = {
                "count": shard_count,
                "shards": [s.name for s in shard_list]
            }

            if shard_count != 16:
                violations.append(
                    f"{root_name}: Expected 16 shards, found {shard_count}"
                )

        passed = len(violations) == 0

        return ArchitectureValidationResult(
            rule_id="AR002",
            rule_text="Jeder Root-Ordner MUSS exakt 16 Shards enthalten",
            passed=passed,
            evidence=evidence,
            violations=violations
        )

    def validate_ar003_384_charts(self) -> ArchitectureValidationResult:
        """AR003: Es MUESSEN exakt 384 Chart-Dateien existieren (24x16)."""
        self._scan_shards()

        chart_files = []
        for root_name, shard_list in self.shards.items():
            for shard in shard_list:
                chart_yaml = shard / "chart.yaml"
                if chart_yaml.exists():
                    chart_files.append(str(chart_yaml.relative_to(self.repo_path)))

        passed = len(chart_files) == 384
        violations = []

        if not passed:
            violations.append(
                f"Expected 384 chart.yaml files, found {len(chart_files)}"
            )

        return ArchitectureValidationResult(
            rule_id="AR003",
            rule_text="Es MUESSEN exakt 384 Chart-Dateien existieren (24x16)",
            passed=passed,
            evidence={
                "total_charts": len(chart_files),
                "sample_charts": chart_files[:10]
            },
            violations=violations
        )

    def validate_ar004_root_folder_format(self) -> ArchitectureValidationResult:
        """AR004: Root-Ordner MUESSEN Format '{NR}_{NAME}' haben."""
        self._scan_root_folders()

        pattern = re.compile(r'^\d{2}_[a-z_]+$')
        violations = []

        for folder in self.root_folders:
            if not pattern.match(folder.name):
                violations.append(
                    f"Invalid format: {folder.name} (expected: ##_lowercase_with_underscores)"
                )

        passed = len(violations) == 0

        return ArchitectureValidationResult(
            rule_id="AR004",
            rule_text="Root-Ordner MUESSEN Format '{NR}_{NAME}' haben",
            passed=passed,
            evidence={"root_folders": [f.name for f in self.root_folders]},
            violations=violations
        )

    def validate_ar005_shard_format(self) -> ArchitectureValidationResult:
        """AR005: Shards MUESSEN Format 'Shard_{NR}_{NAME}' haben."""
        self._scan_shards()

        pattern = re.compile(r'^Shard_\d{2}_[A-Za-z_]+$')
        violations = []
        evidence = {}

        for root_name, shard_list in self.shards.items():
            invalid_shards = [
                s.name for s in shard_list
                if not pattern.match(s.name)
            ]

            if invalid_shards:
                evidence[root_name] = {"invalid_shards": invalid_shards}
                for shard_name in invalid_shards:
                    violations.append(
                        f"{root_name}/{shard_name}: Invalid format (expected: Shard_##_Name)"
                    )

        passed = len(violations) == 0

        return ArchitectureValidationResult(
            rule_id="AR005",
            rule_text="Shards MUESSEN Format 'Shard_{NR}_{NAME}' haben",
            passed=passed,
            evidence=evidence,
            violations=violations
        )

    def validate_ar006_chart_yaml_exists(self) -> ArchitectureValidationResult:
        """AR006: Jeder Shard MUSS eine chart.yaml (SoT) enthalten."""
        self._scan_shards()

        violations = []
        missing_count = 0

        for root_name, shard_list in self.shards.items():
            for shard in shard_list:
                chart_yaml = shard / "chart.yaml"
                if not chart_yaml.exists():
                    violations.append(f"{root_name}/{shard.name}/chart.yaml missing")
                    missing_count += 1

        passed = missing_count == 0

        return ArchitectureValidationResult(
            rule_id="AR006",
            rule_text="Jeder Shard MUSS eine chart.yaml (SoT) enthalten",
            passed=passed,
            evidence={"missing_count": missing_count},
            violations=violations[:20]
        )

    def validate_ar007_manifest_yaml_exists(self) -> ArchitectureValidationResult:
        """AR007: Jede Implementierung MUSS eine manifest.yaml enthalten."""
        self._scan_shards()

        violations = []
        impl_count = 0
        missing_count = 0

        for root_name, shard_list in self.shards.items():
            for shard in shard_list:
                impl_dir = shard / "implementations"
                if impl_dir.exists():
                    for impl in impl_dir.iterdir():
                        if impl.is_dir():
                            impl_count += 1
                            manifest = impl / "manifest.yaml"
                            if not manifest.exists():
                                violations.append(
                                    f"{root_name}/{shard.name}/implementations/{impl.name}/manifest.yaml missing"
                                )
                                missing_count += 1

        passed = missing_count == 0

        return ArchitectureValidationResult(
            rule_id="AR007",
            rule_text="Jede Implementierung MUSS eine manifest.yaml enthalten",
            passed=passed,
            evidence={
                "total_implementations": impl_count,
                "missing_manifests": missing_count
            },
            violations=violations[:20]
        )

    def validate_ar008_path_structure(self) -> ArchitectureValidationResult:
        """AR008: Pfadstruktur MUSS sein: {ROOT}/shards/{SHARD}/chart.yaml."""
        self._scan_root_folders()

        violations = []

        for root in self.root_folders:
            shards_dir = root / "shards"
            if not shards_dir.exists():
                violations.append(f"{root.name}/shards/ directory missing")
                continue

            if not shards_dir.is_dir():
                violations.append(f"{root.name}/shards is not a directory")

        passed = len(violations) == 0

        return ArchitectureValidationResult(
            rule_id="AR008",
            rule_text="Pfadstruktur MUSS sein: {ROOT}/shards/{SHARD}/chart.yaml",
            passed=passed,
            evidence={"shards_directories_validated": len(self.root_folders)},
            violations=violations
        )

    def validate_ar009_implementations_path(self) -> ArchitectureValidationResult:
        """AR009: Implementierungen MUESSEN unter implementations/{IMPL_ID}/ liegen."""
        self._scan_shards()

        violations = []
        valid_impls = 0

        for root_name, shard_list in self.shards.items():
            for shard in shard_list:
                impl_dir = shard / "implementations"
                if impl_dir.exists():
                    for impl in impl_dir.iterdir():
                        if impl.is_dir():
                            valid_impls += 1
                        else:
                            violations.append(
                                f"{root_name}/{shard.name}/implementations/{impl.name} is not a directory"
                            )

        passed = len(violations) == 0

        return ArchitectureValidationResult(
            rule_id="AR009",
            rule_text="Implementierungen MUESSEN unter implementations/{IMPL_ID}/ liegen",
            passed=passed,
            evidence={"valid_implementations": valid_impls},
            violations=violations
        )

    def validate_ar010_contracts_folder(self) -> ArchitectureValidationResult:
        """AR010: Contracts MUESSEN in contracts/-Ordner mit OpenAPI/JSON-Schema liegen."""
        self._scan_shards()

        violations = []
        contracts_found = 0
        shards_with_contracts = 0

        for root_name, shard_list in self.shards.items():
            for shard in shard_list:
                contracts_dir = shard / "contracts"
                if contracts_dir.exists() and contracts_dir.is_dir():
                    yaml_files = list(contracts_dir.glob("*.yaml"))
                    json_files = list(contracts_dir.glob("*.json"))

                    if yaml_files or json_files:
                        shards_with_contracts += 1
                        contracts_found += len(yaml_files) + len(json_files)

                    for f in yaml_files + json_files:
                        if f.stat().st_size == 0:
                            violations.append(f"Empty contract file: {f.relative_to(self.repo_path)}")

        passed = len(violations) == 0

        return ArchitectureValidationResult(
            rule_id="AR010",
            rule_text="Contracts MUESSEN in contracts/-Ordner mit OpenAPI/JSON-Schema liegen",
            passed=passed,
            evidence={
                "shards_with_contracts": shards_with_contracts,
                "total_contract_files": contracts_found
            },
            violations=violations
        )


def main():
    """CLI entry point for architecture validation."""
    import sys
    import json

    repo_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")

    print("="*80)
    print("SSID ARCHITECTURE VALIDATOR - AR001-AR010")
    print("="*80)
    print(f"Repository: {repo_path.absolute()}")
    print()

    validator = ArchitectureValidator(repo_path)
    results = validator.validate_all()

    total = len(results)
    passed = sum(1 for r in results if r.passed)
    failed = total - passed

    print(f"Results: {passed}/{total} passed, {failed} failed")
    print()

    for result in results:
        status = "PASS" if result.passed else "FAIL"
        print(f"[{status}] {result.rule_id}: {result.rule_text}")

        if not result.passed:
            for violation in result.violations[:5]:
                print(f"    - {violation}")
            if len(result.violations) > 5:
                print(f"    ... and {len(result.violations) - 5} more violations")
        print()

    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
