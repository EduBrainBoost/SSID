#!/usr/bin/env python3
"""
SSID Shard-Aware SOT Validator
===============================

Validates SOT compliance while respecting the 24×16 shard matrix architecture.

Key Features:
- Enforces shard boundaries (all content must live in appropriate shards)
- Validates chart.yaml in each shard
- Prevents duplicate files outside shard structure
- Ensures proper cross-shard dependencies

Version: 1.0.0
Author: SSID System
Date: 2025-10-24
"""

import os
import sys
import yaml
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, field
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from sot_validator_core import SOTValidator, ValidationResult


@dataclass
class ShardInfo:
    """Information about a shard"""
    layer: str
    shard_id: str
    path: Path
    chart_exists: bool = False
    chart_valid: bool = False
    readme_exists: bool = False
    has_content: bool = False
    violations: List[str] = field(default_factory=list)


class ShardAwareValidator(SOTValidator):
    """
    Enhanced SOT Validator that enforces shard architecture
    """

    # 24 Root Layers
    ROOT_LAYERS = [
        "01_ai_layer", "02_audit_logging", "03_core", "04_deployment",
        "05_documentation", "06_data_pipeline", "07_governance_legal",
        "08_identity_score", "09_meta_identity", "10_interoperability",
        "11_test_simulation", "12_tooling", "13_ui_layer", "14_zero_time_auth",
        "15_infra", "16_codex", "17_observability", "18_data_layer",
        "19_adapters", "20_foundation", "21_post_quantum_crypto", "22_datasets",
        "23_compliance", "24_meta_orchestration"
    ]

    # 16 Shards
    SHARD_IDS = [
        "01_identitaet_personen", "02_dokumente_nachweise", "03_zugang_berechtigungen",
        "04_kommunikation_daten", "05_gesundheit_medizin", "06_bildung_qualifikationen",
        "07_familie_soziales", "08_mobilitaet_fahrzeuge", "09_arbeit_karriere",
        "10_finanzen_banking", "11_versicherungen_risiken", "12_immobilien_grundstuecke",
        "13_unternehmen_gewerbe", "14_vertraege_vereinbarungen", "15_handel_transaktionen",
        "16_behoerden_verwaltung"
    ]

    def __init__(self, repo_root: Optional[Path] = None):
        """Initialize shard-aware validator"""
        super().__init__(repo_root)
        self.shards: Dict[str, Dict[str, ShardInfo]] = {}
        self.orphaned_files: List[Path] = []
        self.duplicate_files: List[Tuple[Path, Path]] = []

    def scan_shard_matrix(self) -> None:
        """Scan all 384 shards in the matrix"""

        print("\n[SCAN] Scanning 24×16 shard matrix...")

        for layer in self.ROOT_LAYERS:
            layer_path = self.repo_root / layer / "shards"

            if not layer_path.exists():
                print(f"  [WARN] Missing shards directory: {layer}/shards")
                continue

            self.shards[layer] = {}

            for shard_id in self.SHARD_IDS:
                shard_path = layer_path / shard_id

                shard_info = ShardInfo(
                    layer=layer,
                    shard_id=shard_id,
                    path=shard_path
                )

                if shard_path.exists():
                    # Check chart.yaml
                    chart_file = shard_path / "chart.yaml"
                    shard_info.chart_exists = chart_file.exists()

                    if shard_info.chart_exists:
                        try:
                            with open(chart_file, 'r', encoding='utf-8') as f:
                                chart_data = yaml.safe_load(f)
                                shard_info.chart_valid = self._validate_chart_structure(chart_data)
                        except Exception as e:
                            shard_info.violations.append(f"Invalid chart.yaml: {e}")
                            shard_info.chart_valid = False

                    # Check README
                    shard_info.readme_exists = (shard_path / "README.md").exists()

                    # Check for content
                    shard_info.has_content = any(shard_path.iterdir())

                else:
                    shard_info.violations.append("Shard directory does not exist")

                self.shards[layer][shard_id] = shard_info

        print(f"  [OK] Scanned {len(self.ROOT_LAYERS)} layers × {len(self.SHARD_IDS)} shards = {len(self.ROOT_LAYERS) * len(self.SHARD_IDS)} total")

    def _validate_chart_structure(self, chart_data: Dict) -> bool:
        """Validate chart.yaml structure"""

        required_sections = [
            "metadata", "governance", "capabilities", "constraints",
            "enforcement", "interfaces"
        ]

        for section in required_sections:
            if section not in chart_data:
                return False

        # Validate metadata
        metadata = chart_data.get("metadata", {})
        if not all(k in metadata for k in ["shard_id", "root_layer", "version"]):
            return False

        return True

    def find_orphaned_files(self) -> List[Path]:
        """Find files that should be in shards but aren't"""

        print("\n[SCAN] Finding orphaned files...")

        orphaned = []

        for layer in self.ROOT_LAYERS:
            layer_path = self.repo_root / layer

            if not layer_path.exists():
                continue

            # Skip these directories
            skip_dirs = {
                "shards", ".git", "__pycache__", "node_modules",
                ".pytest_cache", ".venv", "venv"
            }

            # Files that are allowed in root layer
            allowed_root_files = {
                "README.md", "CHANGELOG.md", "LICENSE", ".gitignore",
                "requirements.txt", "setup.py", "pyproject.toml",
                "Dockerfile", "docker-compose.yml", ".dockerignore"
            }

            for item in layer_path.rglob("*"):
                if item.is_file():
                    # Check if in shards
                    if "shards" in item.parts:
                        continue

                    # Check if in skip dirs
                    if any(skip in item.parts for skip in skip_dirs):
                        continue

                    # Check if allowed root file
                    rel_path = item.relative_to(layer_path)
                    if rel_path.name in allowed_root_files and len(rel_path.parts) == 1:
                        continue

                    # This file should probably be in a shard
                    orphaned.append(item)

        self.orphaned_files = orphaned
        print(f"  [FOUND] {len(orphaned)} orphaned files")

        return orphaned

    def find_duplicate_files(self) -> List[Tuple[Path, Path]]:
        """Find duplicate files across shards"""

        print("\n[SCAN] Finding duplicate files...")

        file_hashes: Dict[str, List[Path]] = {}
        duplicates = []

        for layer in self.ROOT_LAYERS:
            layer_path = self.repo_root / layer / "shards"

            if not layer_path.exists():
                continue

            for file_path in layer_path.rglob("*"):
                if file_path.is_file() and file_path.suffix in ['.py', '.yaml', '.json', '.md']:
                    try:
                        # Simple content hash
                        content = file_path.read_bytes()
                        import hashlib
                        file_hash = hashlib.sha256(content).hexdigest()

                        if file_hash in file_hashes:
                            # Duplicate found
                            for existing in file_hashes[file_hash]:
                                duplicates.append((existing, file_path))
                        else:
                            file_hashes[file_hash] = []

                        file_hashes[file_hash].append(file_path)

                    except Exception:
                        pass

        self.duplicate_files = duplicates
        print(f"  [FOUND] {len(duplicates)} duplicate file pairs")

        return duplicates

    def validate_shard_boundaries(self) -> List[str]:
        """Validate that cross-shard references are proper"""

        print("\n[VALIDATE] Checking shard boundaries...")

        violations = []

        for layer, shards in self.shards.items():
            for shard_id, shard_info in shards.items():
                chart_file = shard_info.path / "chart.yaml"

                if not chart_file.exists():
                    continue

                try:
                    with open(chart_file, 'r', encoding='utf-8') as f:
                        chart_data = yaml.safe_load(f)

                    # Check dependencies
                    deps = chart_data.get("dependencies", {})
                    required_deps = deps.get("required", [])

                    for dep in required_deps:
                        # Validate dependency format: layer/shard or layer
                        if "/" in dep:
                            dep_layer, dep_shard = dep.split("/", 1)
                            if dep_layer not in self.ROOT_LAYERS:
                                violations.append(
                                    f"{layer}/{shard_id}: Invalid dependency layer '{dep_layer}'"
                                )
                            if dep_shard not in self.SHARD_IDS:
                                violations.append(
                                    f"{layer}/{shard_id}: Invalid dependency shard '{dep_shard}'"
                                )
                        else:
                            if dep not in self.ROOT_LAYERS:
                                violations.append(
                                    f"{layer}/{shard_id}: Invalid dependency '{dep}'"
                                )

                except Exception as e:
                    violations.append(f"{layer}/{shard_id}: Error reading chart.yaml: {e}")

        print(f"  [FOUND] {len(violations)} boundary violations")

        return violations

    def generate_shard_report(self) -> Dict:
        """Generate comprehensive shard validation report"""

        print("\n[REPORT] Generating shard validation report...")

        # Statistics
        total_shards = len(self.ROOT_LAYERS) * len(self.SHARD_IDS)
        existing_shards = 0
        valid_charts = 0
        has_readme = 0
        has_content = 0
        total_violations = 0

        shard_details = []

        for layer, shards in self.shards.items():
            for shard_id, shard_info in shards.items():
                if shard_info.path.exists():
                    existing_shards += 1

                if shard_info.chart_valid:
                    valid_charts += 1

                if shard_info.readme_exists:
                    has_readme += 1

                if shard_info.has_content:
                    has_content += 1

                total_violations += len(shard_info.violations)

                if shard_info.violations:
                    shard_details.append({
                        "layer": layer,
                        "shard": shard_id,
                        "violations": shard_info.violations
                    })

        report = {
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "summary": {
                "total_shards": total_shards,
                "existing_shards": existing_shards,
                "valid_charts": valid_charts,
                "has_readme": has_readme,
                "has_content": has_content,
                "total_violations": total_violations,
                "orphaned_files": len(self.orphaned_files),
                "duplicate_files": len(self.duplicate_files)
            },
            "compliance": {
                "shard_existence": f"{(existing_shards / total_shards) * 100:.1f}%",
                "chart_validity": f"{(valid_charts / existing_shards) * 100:.1f}%" if existing_shards > 0 else "0%",
                "documentation": f"{(has_readme / existing_shards) * 100:.1f}%" if existing_shards > 0 else "0%"
            },
            "issues": {
                "shard_violations": shard_details[:20],  # Top 20
                "orphaned_files": [str(f.relative_to(self.repo_root)) for f in self.orphaned_files[:20]],
                "duplicate_files": [
                    {
                        "file1": str(f1.relative_to(self.repo_root)),
                        "file2": str(f2.relative_to(self.repo_root))
                    }
                    for f1, f2 in self.duplicate_files[:20]
                ]
            }
        }

        print(f"  [OK] Report generated")

        return report

    def validate(self) -> ValidationResult:
        """
        Run complete shard-aware validation
        """

        print("\n" + "=" * 80)
        print("SSID SHARD-AWARE SOT VALIDATION")
        print("=" * 80)

        # 1. Scan shard matrix
        self.scan_shard_matrix()

        # 2. Find orphaned files
        self.find_orphaned_files()

        # 3. Find duplicates
        self.find_duplicate_files()

        # 4. Validate boundaries
        boundary_violations = self.validate_shard_boundaries()

        # 5. Generate report
        report = self.generate_shard_report()

        # 6. Run base SOT validation
        print("\n[VALIDATE] Running base SOT validation...")
        base_result = super().validate()

        # 7. Combine results
        total_violations = (
            report["summary"]["total_violations"] +
            len(self.orphaned_files) +
            len(self.duplicate_files) +
            len(boundary_violations) +
            len(base_result.violations)
        )

        # Save report
        report_path = self.repo_root / "02_audit_logging" / "reports" / "shard_validation_report.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)

        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"\n[REPORT] Saved to: {report_path.relative_to(self.repo_root)}")

        # Print summary
        print("\n" + "=" * 80)
        print("VALIDATION SUMMARY")
        print("=" * 80)
        print(f"Total Shards: {report['summary']['total_shards']}")
        print(f"  Existing: {report['summary']['existing_shards']}")
        print(f"  Valid Charts: {report['summary']['valid_charts']}")
        print(f"  With README: {report['summary']['has_readme']}")
        print(f"\nIssues:")
        print(f"  Shard Violations: {report['summary']['total_violations']}")
        print(f"  Orphaned Files: {len(self.orphaned_files)}")
        print(f"  Duplicate Files: {len(self.duplicate_files)}")
        print(f"  Boundary Violations: {len(boundary_violations)}")
        print(f"  Base SOT Violations: {len(base_result.violations)}")
        print(f"\nTotal Violations: {total_violations}")

        if total_violations == 0:
            print("\n[OK] All validations passed!")
            status = "PASS"
        else:
            print("\n[ERROR] Validation failed!")
            status = "FAIL"

        print("=" * 80)

        # Return combined result
        return ValidationResult(
            status=status,
            violations=base_result.violations + boundary_violations,
            warnings=base_result.warnings,
            metadata={
                **base_result.metadata,
                "shard_report": report
            }
        )


def main():
    """Main entry point"""

    # Get repo root
    repo_root = Path(__file__).parent.parent.parent.parent

    # Create validator
    validator = ShardAwareValidator(repo_root)

    # Run validation
    result = validator.validate()

    # Exit with appropriate code
    sys.exit(0 if result.status == "PASS" else 1)


if __name__ == "__main__":
    main()
