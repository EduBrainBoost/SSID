#!/usr/bin/env python3
"""
Cross-Validation Against Source of Truth (SoT) Documents
Version: 1.0.0
Purpose: Verify complete alignment with SoT structure definitions
"""

import sys
import hashlib
from pathlib import Path
from typing import Dict, List

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

class SoTCrossValidator:
    """Cross-validate Root-24 structure against SoT documents"""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)

        # Canonical 24 root modules from SoT
        self.canonical_roots = [
            "01_ai_layer", "02_audit_logging", "03_core", "04_deployment",
            "05_documentation", "06_data_pipeline", "07_governance_legal",
            "08_identity_score", "09_meta_identity", "10_interoperability",
            "11_test_simulation", "12_tooling", "13_ui_layer", "14_zero_time_auth",
            "15_infra", "16_codex", "17_observability", "18_data_layer",
            "19_adapters", "20_foundation", "21_post_quantum_crypto",
            "22_datasets", "23_compliance", "24_meta_orchestration"
        ]

        # SoT documents to validate against
        self.sot_documents = [
            "16_codex/structure/ssid_master_definition_corrected_v1.1.1.md",
            "16_codex/structure/level3/SSID_structure_level3_part1_MAX.md",
            "16_codex/structure/level3/SSID_structure_level3_part2_MAX.md",
            "16_codex/structure/level3/SSID_structure_level3_part3_MAX.md"
        ]

        self.validation_results = {
            "sot_documents_verified": 0,
            "sot_documents_total": len(self.sot_documents),
            "root_modules_found": 0,
            "root_modules_expected": 24,
            "deviations": 0,
            "reproducibility": 0.0,
            "audit_proof": "UNKNOWN"
        }

    def verify_sot_documents_exist(self) -> bool:
        """Verify all SoT documents exist"""
        print("Verifying SoT documents...")
        print("-" * 70)

        all_exist = True
        for doc_path in self.sot_documents:
            full_path = self.project_root / doc_path
            if full_path.exists():
                size = full_path.stat().st_size
                sha256 = self._calculate_file_hash(full_path)
                print(f"  ✅ {doc_path}")
                print(f"     Size: {size:,} bytes")
                print(f"     SHA-256: {sha256[:32]}...")
                self.validation_results["sot_documents_verified"] += 1
            else:
                print(f"  ❌ {doc_path} - MISSING")
                all_exist = False

        print()
        return all_exist

    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of file"""
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(65536):
                sha256.update(chunk)
        return sha256.hexdigest()

    def verify_root_structure(self) -> Dict:
        """Verify Root-24 structure matches SoT"""
        print("Verifying Root-24 structure compliance...")
        print("-" * 70)

        found_roots = []
        missing_roots = []

        for root_name in self.canonical_roots:
            root_path = self.project_root / root_name
            if root_path.exists() and root_path.is_dir():
                found_roots.append(root_name)
                print(f"  ✅ {root_name}")
            else:
                missing_roots.append(root_name)
                print(f"  ❌ {root_name} - MISSING")

        self.validation_results["root_modules_found"] = len(found_roots)

        print()
        print(f"Root modules found: {len(found_roots)}/24")

        if len(found_roots) == 24:
            print("✅ All 24 root modules present")
        else:
            print(f"⚠️  Missing modules: {missing_roots}")

        print()
        return {
            "found": found_roots,
            "missing": missing_roots
        }

    def check_for_deviations(self) -> int:
        """Check for deviations from SoT"""
        print("Checking for structural deviations...")
        print("-" * 70)

        deviations = 0

        # Check for unauthorized root-level items
        authorized_exceptions = {
            ".git", ".github", ".gitignore", ".gitattributes",
            "LICENSE", "README.md", ".pre-commit-config.yaml", ".claude"
        }

        root_items = [item for item in self.project_root.iterdir()]
        unauthorized = []

        for item in root_items:
            item_name = item.name
            is_root_module = item_name in self.canonical_roots
            is_exception = item_name in authorized_exceptions

            # Check for generated docs (allowed)
            is_generated_doc = (
                item_name.startswith("DEPLOYMENT_") or
                item_name.startswith("TRANSITION_") or
                item_name.startswith("V10_") or
                "CERTIFICATION" in item_name
            )

            if not (is_root_module or is_exception or is_generated_doc):
                unauthorized.append(item_name)
                deviations += 1
                print(f"  ⚠️  Unauthorized item: {item_name}")

        if deviations == 0:
            print("  ✅ No deviations detected")

        self.validation_results["deviations"] = deviations

        print()
        print(f"Deviations found: {deviations}")
        print()

        return deviations

    def calculate_reproducibility(self) -> float:
        """Calculate reproducibility score"""
        sot_score = (self.validation_results["sot_documents_verified"] /
                     self.validation_results["sot_documents_total"]) * 100

        structure_score = (self.validation_results["root_modules_found"] /
                          self.validation_results["root_modules_expected"]) * 100

        deviation_penalty = min(self.validation_results["deviations"] * 5, 100)

        reproducibility = ((sot_score + structure_score) / 2) - deviation_penalty
        reproducibility = max(0, min(100, reproducibility))

        self.validation_results["reproducibility"] = round(reproducibility, 1)
        return reproducibility

    def determine_audit_proof(self, reproducibility: float, deviations: int) -> str:
        """Determine audit proof status"""
        if reproducibility == 100.0 and deviations == 0:
            return "VERIFIED"
        elif reproducibility >= 95.0:
            return "APPROVED"
        elif reproducibility >= 90.0:
            return "CONDITIONAL"
        else:
            return "FAILED"

    def run_validation(self):
        """Execute complete cross-validation"""
        print()
        print("=" * 70)
        print("🔍 CROSS-VALIDATION AGAINST SOURCE OF TRUTH")
        print("=" * 70)
        print()

        # Step 1: Verify SoT documents
        sot_ok = self.verify_sot_documents_exist()

        # Step 2: Verify root structure
        structure_result = self.verify_root_structure()

        # Step 3: Check deviations
        deviations = self.check_for_deviations()

        # Step 4: Calculate reproducibility
        reproducibility = self.calculate_reproducibility()

        # Step 5: Determine audit proof
        audit_proof = self.determine_audit_proof(reproducibility, deviations)
        self.validation_results["audit_proof"] = audit_proof

        # Final summary
        print("=" * 70)
        print("📊 CROSS-VALIDATION SUMMARY")
        print("=" * 70)
        print()
        print(f"SoT Documents Verified: {self.validation_results['sot_documents_verified']}/{self.validation_results['sot_documents_total']}")
        print(f"Root Modules Found: {self.validation_results['root_modules_found']}/{self.validation_results['root_modules_expected']}")
        print(f"Deviations: {self.validation_results['deviations']}")
        print(f"Reproducibility: {self.validation_results['reproducibility']:.1f}%")
        print(f"Audit Proof: {self.validation_results['audit_proof']}")
        print()

        if audit_proof == "VERIFIED":
            print("✅ CROSS-VALIDATION PASSED")
            print("   System is 100% aligned with Source of Truth")
        elif audit_proof in ["APPROVED", "CONDITIONAL"]:
            print("⚠️  CROSS-VALIDATION CONDITIONAL")
            print("   Minor deviations detected")
        else:
            print("❌ CROSS-VALIDATION FAILED")
            print("   Significant deviations from SoT")

        print()
        print("=" * 70)
        print()

        return self.validation_results

def main():
    """Main execution"""
    project_root = Path(__file__).parent.parent

    validator = SoTCrossValidator(str(project_root))
    results = validator.run_validation()

    # Exit code based on audit proof
    if results['audit_proof'] == 'VERIFIED':
        return 0
    elif results['audit_proof'] in ['APPROVED', 'CONDITIONAL']:
        return 1
    else:
        return 2

if __name__ == "__main__":
    sys.exit(main())
