#!/usr/bin/env python3
"""
SSID Shard Matrix Validator
Validates the complete 24×16 shard structure (384 combinations)

Requirements from ssid_master_definition_corrected_v1.1.1.md:
- All 24 root directories MUST exist
- Each root MUST contain 16 shards
- Each shard MUST have required structure:
  - chart.yaml (SoT definition)
  - implementations/ directory
  - contracts/ directory
  - policies/ directory
  - docs/ directory
"""

import json
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import yaml


# EXACT definitions from SoT Master Definition v1.1.1
ROOT_DIRECTORIES = [
    "01_ai_layer",
    "02_audit_logging",
    "03_core",
    "04_deployment",
    "05_documentation",
    "06_data_pipeline",
    "07_governance_legal",
    "08_identity_score",
    "09_meta_identity",
    "10_interoperability",
    "11_test_simulation",
    "12_tooling",
    "13_ui_layer",
    "14_zero_time_auth",
    "15_infra",
    "16_codex",
    "17_observability",
    "18_data_layer",
    "19_adapters",
    "20_foundation",
    "21_post_quantum_crypto",
    "22_datasets",
    "23_compliance",
    "24_meta_orchestration",
]

# 16 Shards - EXACT names from SoT
SHARD_DEFINITIONS = [
    # Block 1: Identity & Basis (01-04)
    ("01", "identitaet_personen", "Identität & Personen"),
    ("02", "dokumente_nachweise", "Dokumente & Nachweise"),
    ("03", "zugang_berechtigungen", "Zugang & Berechtigungen"),
    ("04", "kommunikation_daten", "Kommunikation & Daten"),
    # Block 2: Private Life (05-08)
    ("05", "gesundheit_medizin", "Gesundheit & Medizin"),
    ("06", "bildung_qualifikationen", "Bildung & Qualifikationen"),
    ("07", "familie_soziales", "Familie & Soziales"),
    ("08", "mobilitaet_fahrzeuge", "Mobilität & Fahrzeuge"),
    # Block 3: Economy & Assets (09-12)
    ("09", "arbeit_karriere", "Arbeit & Karriere"),
    ("10", "finanzen_banking", "Finanzen & Banking"),
    ("11", "versicherungen_risiken", "Versicherungen & Risiken"),
    ("12", "immobilien_grundstuecke", "Immobilien & Grundstücke"),
    # Block 4: Business & Public (13-16)
    ("13", "unternehmen_gewerbe", "Unternehmen & Gewerbe"),
    ("14", "vertraege_vereinbarungen", "Verträge & Vereinbarungen"),
    ("15", "handel_transaktionen", "Handel & Transaktionen"),
    ("16", "behoerden_verwaltung", "Behörden & Verwaltung"),
]

# Required directories in each shard (from SoT)
REQUIRED_SHARD_DIRS = [
    "implementations",
    "contracts",
    "policies",
    "docs",
]

# Required file in each shard
REQUIRED_SHARD_FILES = [
    "chart.yaml",
]


@dataclass
class ShardStatus:
    """Status of a single shard"""
    root: str
    shard_number: str
    shard_name: str
    exists: bool
    path: Optional[Path] = None
    has_chart_yaml: bool = False
    has_implementations: bool = False
    has_contracts: bool = False
    has_policies: bool = False
    has_docs: bool = False
    chart_valid: bool = False
    chart_errors: List[str] = field(default_factory=list)
    implementation_count: int = 0
    missing_dirs: List[str] = field(default_factory=list)
    missing_files: List[str] = field(default_factory=list)

    @property
    def is_complete(self) -> bool:
        """Check if shard meets all requirements"""
        return (
            self.exists
            and self.has_chart_yaml
            and self.has_implementations
            and self.has_contracts
            and self.has_policies
            and self.has_docs
            and self.chart_valid
            and len(self.missing_dirs) == 0
            and len(self.missing_files) == 0
        )

    @property
    def completion_percentage(self) -> float:
        """Calculate completion percentage"""
        total_checks = 7  # exists, chart, 4 dirs, chart_valid
        passed_checks = sum([
            self.exists,
            self.has_chart_yaml,
            self.has_implementations,
            self.has_contracts,
            self.has_policies,
            self.has_docs,
            self.chart_valid,
        ])
        return (passed_checks / total_checks) * 100


@dataclass
class MatrixStatus:
    """Overall matrix status"""
    total_shards: int = 384  # 24 × 16
    existing_shards: int = 0
    complete_shards: int = 0
    incomplete_shards: int = 0
    missing_shards: int = 0
    shards: List[ShardStatus] = field(default_factory=list)
    root_completeness: Dict[str, float] = field(default_factory=dict)
    shard_completeness: Dict[str, float] = field(default_factory=dict)

    @property
    def overall_completion(self) -> float:
        """Overall completion percentage"""
        if self.total_shards == 0:
            return 0.0
        return (self.complete_shards / self.total_shards) * 100

    @property
    def existence_percentage(self) -> float:
        """Percentage of shards that exist"""
        if self.total_shards == 0:
            return 0.0
        return (self.existing_shards / self.total_shards) * 100


class ShardMatrixValidator:
    """Validates the complete 24×16 shard matrix"""

    def __init__(self, repo_root: Path):
        self.repo_root = Path(repo_root)
        self.matrix_status = MatrixStatus()

    def validate_all(self) -> MatrixStatus:
        """Validate entire 24×16 matrix"""
        print("=" * 80)
        print("SSID SHARD MATRIX VALIDATOR")
        print("=" * 80)
        print(f"Repository Root: {self.repo_root}")
        print(f"Expected Structure: 24 Roots × 16 Shards = 384 Total")
        print()

        # Validate roots first
        self._validate_roots()

        # Validate all 384 shard combinations
        for root_dir in ROOT_DIRECTORIES:
            for shard_num, shard_name, shard_title in SHARD_DEFINITIONS:
                status = self._validate_shard(root_dir, shard_num, shard_name, shard_title)
                self.matrix_status.shards.append(status)

        # Calculate statistics
        self._calculate_statistics()

        return self.matrix_status

    def _validate_roots(self):
        """Validate that all 24 roots exist"""
        print("Validating 24 Root Directories...")
        missing_roots = []

        for root_dir in ROOT_DIRECTORIES:
            root_path = self.repo_root / root_dir
            if root_path.exists() and root_path.is_dir():
                print(f"  ✓ {root_dir}")
            else:
                print(f"  ✗ {root_dir} - MISSING!")
                missing_roots.append(root_dir)

        if missing_roots:
            print(f"\n⚠️  WARNING: {len(missing_roots)} root directories missing!")
            for root in missing_roots:
                print(f"    - {root}")
        else:
            print(f"\n✓ All 24 root directories exist!")
        print()

    def _validate_shard(
        self,
        root_dir: str,
        shard_num: str,
        shard_name: str,
        shard_title: str
    ) -> ShardStatus:
        """Validate a single shard"""
        # Try both naming conventions
        shard_dir_pascal = f"Shard_{shard_num}_{shard_name.replace('_', '_').title().replace('_', '_')}"
        shard_dir_lower = f"{shard_num}_{shard_name}"

        root_path = self.repo_root / root_dir / "shards"
        shard_path_pascal = root_path / shard_dir_pascal
        shard_path_lower = root_path / shard_dir_lower

        # Determine which naming convention is used
        shard_path = None
        if shard_path_pascal.exists():
            shard_path = shard_path_pascal
        elif shard_path_lower.exists():
            shard_path = shard_path_lower

        status = ShardStatus(
            root=root_dir,
            shard_number=shard_num,
            shard_name=shard_name,
            exists=shard_path is not None,
            path=shard_path,
        )

        if not status.exists:
            status.missing_dirs = REQUIRED_SHARD_DIRS.copy()
            status.missing_files = REQUIRED_SHARD_FILES.copy()
            return status

        # Check required files
        chart_path = shard_path / "chart.yaml"
        status.has_chart_yaml = chart_path.exists()
        if not status.has_chart_yaml:
            status.missing_files.append("chart.yaml")
        else:
            # Validate chart.yaml
            status.chart_valid, errors = self._validate_chart_yaml(chart_path)
            status.chart_errors = errors

        # Check required directories
        for dir_name in REQUIRED_SHARD_DIRS:
            dir_path = shard_path / dir_name
            exists = dir_path.exists() and dir_path.is_dir()

            if dir_name == "implementations":
                status.has_implementations = exists
                if exists:
                    # Count implementations
                    status.implementation_count = len([
                        d for d in dir_path.iterdir()
                        if d.is_dir() and (d / "manifest.yaml").exists()
                    ])
            elif dir_name == "contracts":
                status.has_contracts = exists
            elif dir_name == "policies":
                status.has_policies = exists
            elif dir_name == "docs":
                status.has_docs = exists

            if not exists:
                status.missing_dirs.append(dir_name)

        return status

    def _validate_chart_yaml(self, chart_path: Path) -> Tuple[bool, List[str]]:
        """Validate chart.yaml structure"""
        errors = []

        try:
            with open(chart_path, 'r', encoding='utf-8') as f:
                chart = yaml.safe_load(f)

            if not chart:
                errors.append("Empty chart.yaml")
                return False, errors

            # Check required top-level sections
            required_sections = [
                "metadata",
                "governance",
                "capabilities",
                "constraints",
                "interfaces",
            ]

            for section in required_sections:
                if section not in chart:
                    errors.append(f"Missing required section: {section}")

            # Check metadata
            if "metadata" in chart:
                metadata = chart["metadata"]
                if "shard_id" not in metadata:
                    errors.append("metadata.shard_id missing")
                if "version" not in metadata:
                    errors.append("metadata.version missing")

            return len(errors) == 0, errors

        except yaml.YAMLError as e:
            errors.append(f"YAML parsing error: {e}")
            return False, errors
        except Exception as e:
            errors.append(f"Error reading chart.yaml: {e}")
            return False, errors

    def _calculate_statistics(self):
        """Calculate matrix statistics"""
        self.matrix_status.existing_shards = sum(1 for s in self.matrix_status.shards if s.exists)
        self.matrix_status.complete_shards = sum(1 for s in self.matrix_status.shards if s.is_complete)
        self.matrix_status.incomplete_shards = sum(
            1 for s in self.matrix_status.shards
            if s.exists and not s.is_complete
        )
        self.matrix_status.missing_shards = sum(1 for s in self.matrix_status.shards if not s.exists)

        # Calculate per-root completeness
        for root_dir in ROOT_DIRECTORIES:
            root_shards = [s for s in self.matrix_status.shards if s.root == root_dir]
            if root_shards:
                avg_completion = sum(s.completion_percentage for s in root_shards) / len(root_shards)
                self.matrix_status.root_completeness[root_dir] = avg_completion

        # Calculate per-shard-type completeness
        for shard_num, shard_name, _ in SHARD_DEFINITIONS:
            shard_instances = [
                s for s in self.matrix_status.shards
                if s.shard_number == shard_num
            ]
            if shard_instances:
                avg_completion = sum(s.completion_percentage for s in shard_instances) / len(shard_instances)
                self.matrix_status.shard_completeness[f"{shard_num}_{shard_name}"] = avg_completion

    def print_report(self):
        """Print detailed validation report"""
        print("=" * 80)
        print("MATRIX VALIDATION REPORT")
        print("=" * 80)
        print()

        # Overall statistics
        print("OVERALL STATISTICS:")
        print(f"  Total Expected:      {self.matrix_status.total_shards:4d}")
        print(f"  Existing:           {self.matrix_status.existing_shards:4d} ({self.matrix_status.existence_percentage:6.2f}%)")
        print(f"  Complete:           {self.matrix_status.complete_shards:4d} ({self.matrix_status.overall_completion:6.2f}%)")
        print(f"  Incomplete:         {self.matrix_status.incomplete_shards:4d}")
        print(f"  Missing:            {self.matrix_status.missing_shards:4d}")
        print()

        # Per-root statistics
        print("PER-ROOT COMPLETENESS:")
        for root_dir in ROOT_DIRECTORIES:
            completion = self.matrix_status.root_completeness.get(root_dir, 0.0)
            root_shards = [s for s in self.matrix_status.shards if s.root == root_dir]
            existing_count = sum(1 for s in root_shards if s.exists)
            complete_count = sum(1 for s in root_shards if s.is_complete)

            status_symbol = "✓" if completion == 100.0 else "○" if completion > 0 else "✗"
            print(f"  {status_symbol} {root_dir:30s} {existing_count:2d}/16 exist, {complete_count:2d}/16 complete ({completion:6.2f}%)")
        print()

        # Per-shard-type statistics
        print("PER-SHARD-TYPE COMPLETENESS:")
        for shard_num, shard_name, shard_title in SHARD_DEFINITIONS:
            shard_key = f"{shard_num}_{shard_name}"
            completion = self.matrix_status.shard_completeness.get(shard_key, 0.0)
            shard_instances = [
                s for s in self.matrix_status.shards
                if s.shard_number == shard_num
            ]
            existing_count = sum(1 for s in shard_instances if s.exists)
            complete_count = sum(1 for s in shard_instances if s.is_complete)

            status_symbol = "✓" if completion == 100.0 else "○" if completion > 0 else "✗"
            print(f"  {status_symbol} {shard_num} {shard_name:30s} {existing_count:2d}/24 exist, {complete_count:2d}/24 complete ({completion:6.2f}%)")
        print()

        # Missing shards summary
        missing = [s for s in self.matrix_status.shards if not s.exists]
        if missing:
            print(f"MISSING SHARDS ({len(missing)}):")
            for shard in missing[:20]:  # Show first 20
                print(f"  - {shard.root}/shards/{shard.shard_number}_{shard.shard_name}")
            if len(missing) > 20:
                print(f"  ... and {len(missing) - 20} more")
            print()

        # Incomplete shards summary
        incomplete = [s for s in self.matrix_status.shards if s.exists and not s.is_complete]
        if incomplete:
            print(f"INCOMPLETE SHARDS ({len(incomplete)}):")
            for shard in incomplete[:20]:  # Show first 20
                issues = []
                if not shard.has_chart_yaml:
                    issues.append("no chart.yaml")
                if not shard.chart_valid:
                    issues.append("invalid chart.yaml")
                if shard.missing_dirs:
                    issues.append(f"missing dirs: {', '.join(shard.missing_dirs)}")
                if shard.implementation_count == 0:
                    issues.append("no implementations")

                print(f"  - {shard.root}/shards/{shard.shard_number}_{shard.shard_name}")
                print(f"    Issues: {', '.join(issues)}")
            if len(incomplete) > 20:
                print(f"  ... and {len(incomplete) - 20} more")
            print()

        # Success message
        if self.matrix_status.complete_shards == self.matrix_status.total_shards:
            print("🎉 SUCCESS! All 384 shards are complete!")
        elif self.matrix_status.existing_shards == self.matrix_status.total_shards:
            print("✓ All 384 shards exist, but some are incomplete.")
        else:
            print(f"⚠️  {self.matrix_status.missing_shards} shards still need to be created.")
        print()

    def export_json(self, output_path: Path):
        """Export matrix status to JSON"""
        data = {
            "timestamp": "2025-10-24T00:00:00Z",
            "summary": {
                "total_shards": self.matrix_status.total_shards,
                "existing_shards": self.matrix_status.existing_shards,
                "complete_shards": self.matrix_status.complete_shards,
                "incomplete_shards": self.matrix_status.incomplete_shards,
                "missing_shards": self.matrix_status.missing_shards,
                "existence_percentage": self.matrix_status.existence_percentage,
                "completion_percentage": self.matrix_status.overall_completion,
            },
            "root_completeness": self.matrix_status.root_completeness,
            "shard_type_completeness": self.matrix_status.shard_completeness,
            "shards": [
                {
                    "root": s.root,
                    "shard_number": s.shard_number,
                    "shard_name": s.shard_name,
                    "exists": s.exists,
                    "is_complete": s.is_complete,
                    "completion_percentage": s.completion_percentage,
                    "has_chart_yaml": s.has_chart_yaml,
                    "chart_valid": s.chart_valid,
                    "has_implementations": s.has_implementations,
                    "has_contracts": s.has_contracts,
                    "has_policies": s.has_policies,
                    "has_docs": s.has_docs,
                    "implementation_count": s.implementation_count,
                    "missing_dirs": s.missing_dirs,
                    "missing_files": s.missing_files,
                    "chart_errors": s.chart_errors,
                }
                for s in self.matrix_status.shards
            ],
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"✓ Matrix status exported to: {output_path}")


def main():
    """Main entry point"""
    # Determine repository root
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent.parent.parent  # Go up from 03_core/validators/structure/

    # Override with environment variable if set
    if "SSID_ROOT" in os.environ:
        repo_root = Path(os.environ["SSID_ROOT"])

    # Validate
    validator = ShardMatrixValidator(repo_root)
    matrix_status = validator.validate_all()

    # Print report
    validator.print_report()

    # Export JSON
    output_path = repo_root / "24_meta_orchestration" / "registry" / "shard_matrix_status.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    validator.export_json(output_path)

    # Exit code
    if matrix_status.complete_shards == matrix_status.total_shards:
        sys.exit(0)  # Success
    elif matrix_status.existing_shards == matrix_status.total_shards:
        sys.exit(1)  # All exist but some incomplete
    else:
        sys.exit(2)  # Some missing


if __name__ == "__main__":
    main()
