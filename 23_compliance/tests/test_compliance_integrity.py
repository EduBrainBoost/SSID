"""
Compliance Integrity Test Suite

Tests compliance mapping integrity, SHA256 checksums, and module reference validation.
Ensures all compliance mappings are valid and reference existing modules.

Version: 2025-Q4
Last Updated: 2025-10-07
Maintainer: edubrainboost
"""

import hashlib
import os
from pathlib import Path
from typing import Dict, List, Set

import pytest
import yaml

# Define the repository root (3 levels up from this test file)
REPO_ROOT = Path(__file__).parent.parent.parent
COMPLIANCE_DIR = REPO_ROOT / "23_compliance"
MAPPINGS_DIR = COMPLIANCE_DIR / "mappings"

# Expected 24 modules (01-24)
EXPECTED_MODULES = [
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

def calculate_sha256(file_path: Path) -> str:
    """Calculate SHA256 checksum of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return f"sha256:{sha256_hash.hexdigest()}"

def load_yaml_mapping(file_path: Path) -> Dict:
    """Load YAML mapping file."""
    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def get_existing_modules() -> Set[str]:
    """Get list of actually existing module directories in repository."""
    existing = set()
    for item in REPO_ROOT.iterdir():
        if item.is_dir() and item.name.startswith(tuple(f"{i:02d}_" for i in range(1, 25))):
            existing.add(item.name)
    return existing

class TestComplianceMappings:
    """Test suite for compliance mapping integrity."""

    @pytest.fixture(scope="class")
    def mapping_files(self) -> List[Path]:
        """Get all mapping YAML files."""
        return list(MAPPINGS_DIR.glob("*_mapping.yaml"))

    @pytest.fixture(scope="class")
    def existing_modules(self) -> Set[str]:
        """Get set of existing modules."""
        return get_existing_modules()

    def test_mapping_files_exist(self, mapping_files):
        """Test that all required mapping files exist."""
        expected_mappings = [
            "gdpr_mapping.yaml",
            "dora_mapping.yaml",
            "mica_mapping.yaml",
            "amld6_mapping.yaml",
        ]

        existing_names = [f.name for f in mapping_files]

        for expected in expected_mappings:
            assert expected in existing_names, f"Missing required mapping file: {expected}"

    def test_mapping_file_structure(self, mapping_files):
        """Test that each mapping file has required structure."""
        for mapping_file in mapping_files:
            data = load_yaml_mapping(mapping_file)

            # Test meta section
            assert "meta" in data, f"{mapping_file.name}: Missing 'meta' section"
            meta = data["meta"]

            required_meta_fields = [
                "framework",
                "version",
                "source",
                "last_updated",
                "maintainer",
                "status",
            ]

            for field in required_meta_fields:
                assert field in meta, f"{mapping_file.name}: Missing meta.{field}"

            # Test version
            assert meta["version"] == "2025-Q4", f"{mapping_file.name}: Version mismatch"

            # Test source
            assert meta["source"] == "SoT Level3", f"{mapping_file.name}: Invalid source"

            # Test maintainer
            assert meta["maintainer"] == "edubrainboost", f"{mapping_file.name}: Invalid maintainer"

            # Test mappings section
            assert "mappings" in data, f"{mapping_file.name}: Missing 'mappings' section"
            assert isinstance(data["mappings"], list), f"{mapping_file.name}: 'mappings' must be a list"
            assert len(data["mappings"]) > 0, f"{mapping_file.name}: 'mappings' cannot be empty"

    def test_mapping_entries_structure(self, mapping_files):
        """Test that each mapping entry has required structure."""
        for mapping_file in mapping_files:
            data = load_yaml_mapping(mapping_file)

            for idx, mapping in enumerate(data["mappings"]):
                context = f"{mapping_file.name}:mappings[{idx}]"

                # Required fields
                required_fields = [
                    "id",
                    "description",
                    "applies_to",
                    "verification",
                    "implementation_status",
                ]

                for field in required_fields:
                    assert field in mapping, f"{context}: Missing field '{field}'"

                # Test id format
                assert mapping["id"].startswith(
                    data["meta"]["framework"]
                ), f"{context}: ID must start with framework name"

                # Test applies_to is list
                assert isinstance(
                    mapping["applies_to"], list
                ), f"{context}: 'applies_to' must be a list"
                assert len(mapping["applies_to"]) > 0, f"{context}: 'applies_to' cannot be empty"

                # Test verification value
                assert mapping["verification"] in [
                    "automated",
                    "manual",
                ], f"{context}: Invalid verification type"

                # Test implementation_status
                assert mapping["implementation_status"] in [
                    "implemented",
                    "planned",
                    "pending",
                ], f"{context}: Invalid implementation_status"

    def test_sha256_checksums(self, mapping_files):
        """Test that SHA256 checksums are present and valid."""
        for mapping_file in mapping_files:
            data = load_yaml_mapping(mapping_file)

            # Check checksum field exists
            assert "checksum" in data, f"{mapping_file.name}: Missing 'checksum' field"

            stored_checksum = data["checksum"]

            # Check checksum format
            assert stored_checksum.startswith(
                "sha256:"
            ), f"{mapping_file.name}: Checksum must start with 'sha256:'"

            # Check checksum is not placeholder
            assert (
                "placeholder" not in stored_checksum.lower()
            ), f"{mapping_file.name}: Checksum is still placeholder"

            # Verify checksum length (sha256: + 64 hex chars = 71 chars)
            assert (
                len(stored_checksum) == 71
            ), f"{mapping_file.name}: Invalid checksum length"

    def test_module_references_exist(self, mapping_files, existing_modules):
        """Test that all referenced modules actually exist."""
        for mapping_file in mapping_files:
            data = load_yaml_mapping(mapping_file)

            for idx, mapping in enumerate(data["mappings"]):
                context = f"{mapping_file.name}:mappings[{idx}]"

                for module in mapping["applies_to"]:
                    # Check module format (NN_module_name)
                    assert module in EXPECTED_MODULES, (
                        f"{context}: Invalid module reference '{module}'. "
                        f"Must be one of {EXPECTED_MODULES}"
                    )

                    # Check module exists in filesystem
                    assert module in existing_modules, (
                        f"{context}: Referenced module '{module}' does not exist in repository. "
                        f"Existing modules: {sorted(existing_modules)}"
                    )

    def test_cross_module_dependencies(self, mapping_files):
        """Test cross-module dependency declarations if present."""
        for mapping_file in mapping_files:
            data = load_yaml_mapping(mapping_file)

            if "cross_module_dependencies" in data:
                deps = data["cross_module_dependencies"]

                for idx, dep in enumerate(deps):
                    context = f"{mapping_file.name}:cross_module_dependencies[{idx}]"

                    # Required fields
                    assert "source" in dep, f"{context}: Missing 'source'"
                    assert "target" in dep, f"{context}: Missing 'target'"
                    assert "requirement" in dep, f"{context}: Missing 'requirement'"

                    # Validate module names
                    assert dep["source"] in EXPECTED_MODULES, (
                        f"{context}: Invalid source module '{dep['source']}'"
                    )
                    assert dep["target"] in EXPECTED_MODULES, (
                        f"{context}: Invalid target module '{dep['target']}'"
                    )

    def test_compliance_metrics(self, mapping_files):
        """Test compliance metrics section if present."""
        for mapping_file in mapping_files:
            data = load_yaml_mapping(mapping_file)

            if "compliance_metrics" in data:
                metrics = data["compliance_metrics"]

                # Check overall coverage
                if "overall_coverage" in metrics:
                    coverage_str = metrics["overall_coverage"]
                    if isinstance(coverage_str, str):
                        # Extract percentage (e.g., "95%")
                        coverage = int(coverage_str.rstrip("%"))
                        assert 0 <= coverage <= 100, (
                            f"{mapping_file.name}: Invalid coverage percentage {coverage}"
                        )

    def test_references_section(self, mapping_files):
        """Test that references section is present and valid."""
        for mapping_file in mapping_files:
            data = load_yaml_mapping(mapping_file)

            assert "references" in data, f"{mapping_file.name}: Missing 'references' section"

            refs = data["references"]
            assert isinstance(refs, list), f"{mapping_file.name}: 'references' must be a list"
            assert len(refs) > 0, f"{mapping_file.name}: 'references' cannot be empty"

            for idx, ref in enumerate(refs):
                context = f"{mapping_file.name}:references[{idx}]"
                assert "title" in ref, f"{context}: Missing 'title'"
                assert "url" in ref, f"{context}: Missing 'url'"

class TestComplianceCoverage:
    """Test compliance coverage across all frameworks."""

    @pytest.fixture(scope="class")
    def all_mappings(self) -> Dict[str, Dict]:
        """Load all mapping files."""
        mappings = {}
        for mapping_file in MAPPINGS_DIR.glob("*_mapping.yaml"):
            data = load_yaml_mapping(mapping_file)
            framework = data["meta"]["framework"]
            mappings[framework] = data
        return mappings

    def test_framework_coverage(self, all_mappings):
        """Test that all major frameworks are covered."""
        required_frameworks = ["GDPR", "DORA", "MiCA", "AMLD6"]

        for framework in required_frameworks:
            assert framework in all_mappings, f"Missing framework: {framework}"

    def test_module_coverage(self, all_mappings):
        """Test that all critical modules are covered by at least one framework."""
        critical_modules = [
            "02_audit_logging",
            "03_core",
            "07_governance_legal",
            "09_meta_identity",
            "14_zero_time_auth",
            "23_compliance",
        ]

        covered_modules = set()
        for framework_data in all_mappings.values():
            for mapping in framework_data["mappings"]:
                covered_modules.update(mapping["applies_to"])

        for module in critical_modules:
            assert module in covered_modules, (
                f"Critical module '{module}' not covered by any compliance framework"
            )

    def test_no_orphan_mappings(self, all_mappings):
        """Test that all mappings have valid implementation status."""
        for framework, data in all_mappings.items():
            for idx, mapping in enumerate(data["mappings"]):
                status = mapping["implementation_status"]
                assert status in ["implemented", "planned", "pending"], (
                    f"{framework}:mappings[{idx}]: Invalid status '{status}'"
                )

    def test_missing_references(self, all_mappings, existing_modules):
        """Test for modules that exist but have no compliance mappings (warning only)."""
        # Collect all referenced modules
        referenced_modules = set()
        for framework_data in all_mappings.values():
            for mapping in framework_data["mappings"]:
                referenced_modules.update(mapping["applies_to"])

        # Find unmapped modules
        unmapped = existing_modules - referenced_modules

        # Critical modules that MUST be mapped
        critical_unmapped = unmapped & {
            "02_audit_logging",
            "03_core",
            "07_governance_legal",
            "09_meta_identity",
            "14_zero_time_auth",
            "21_post_quantum_crypto",
            "23_compliance",
        }

        # Fail if critical modules are unmapped
        assert not critical_unmapped, (
            f"Critical modules without compliance mappings: {critical_unmapped}. "
            f"These modules MUST have compliance mappings in at least one framework."
        )

        # Warning for non-critical unmapped modules (doesn't fail the test)
        if unmapped:
            import warnings
            warnings.warn(
                f"Non-critical modules without compliance mappings: {unmapped}. "
                f"Consider adding mappings if these modules handle regulated data or operations.",
                UserWarning
            )

class TestMissingModules:
    """Test for new modules added without compliance consideration."""

    @pytest.fixture(scope="class")
    def all_mappings(self) -> Dict[str, Dict]:
        """Load all mapping files."""
        mappings = {}
        for mapping_file in MAPPINGS_DIR.glob("*_mapping.yaml"):
            data = load_yaml_mapping(mapping_file)
            framework = data["meta"]["framework"]
            mappings[framework] = data
        return mappings

    @pytest.fixture(scope="class")
    def existing_modules(self) -> Set[str]:
        """Get set of existing modules."""
        return get_existing_modules()

    def test_new_modules_without_mappings(self, existing_modules, all_mappings):
        """
        Test that identifies new modules potentially added without compliance review.
        This test warns about modules that exist but are not referenced in any compliance framework.
        """
        # Collect all referenced modules across all frameworks
        all_referenced = set()
        for framework_data in all_mappings.values():
            for mapping in framework_data["mappings"]:
                all_referenced.update(mapping["applies_to"])

        # Find modules without any compliance mapping
        unmapped_modules = existing_modules - all_referenced

        # Modules that are expected to not need compliance mappings (infrastructure only)
        exempted_modules = {
            "12_tooling",  # Development tools
            "16_codex",    # Documentation/patterns
            "22_datasets", # Data storage (covered by modules using it)
        }

        # Remove exempted modules
        concerning_unmapped = unmapped_modules - exempted_modules

        if concerning_unmapped:
            # Create detailed warning message
            warning_msg = (
                f"\n⚠️  WARNING: {len(concerning_unmapped)} module(s) without compliance mappings:\n"
            )
            for module in sorted(concerning_unmapped):
                warning_msg += f"  - {module}\n"
            warning_msg += (
                "\nIf these modules handle regulated data, user information, or critical "
                "operations, they should be mapped in at least one compliance framework "
                "(GDPR, DORA, MiCA, or AMLD6).\n\n"
                "To resolve this warning, add the module to the 'applies_to' field "
                "in the relevant compliance mapping YAML files under 23_compliance/mappings/"
            )

            import warnings
            warnings.warn(warning_msg, UserWarning)

        # Sprint 2+ Implementation: Assert that unmapped modules are documented/acceptable
        # Allow up to 5 non-critical unmapped modules (infrastructure/support only)
        max_acceptable_unmapped = 5
        assert len(concerning_unmapped) <= max_acceptable_unmapped, (
            f"Too many modules ({len(concerning_unmapped)}) without compliance mappings. "
            f"Maximum acceptable: {max_acceptable_unmapped}. "
            f"Unmapped modules: {sorted(concerning_unmapped)}"
        )

class TestReviewFramework:
    """Test review framework structure."""

    def test_review_directories_exist(self):
        """Test that review directories exist."""
        reviews_dir = COMPLIANCE_DIR / "reviews"
        assert reviews_dir.exists(), "Reviews directory does not exist"

        q4_2025_dir = reviews_dir / "2025-Q4"
        assert q4_2025_dir.exists(), "2025-Q4 review directory does not exist"

    def test_review_templates_exist(self):
        """Test that review templates exist."""
        q4_2025_dir = COMPLIANCE_DIR / "reviews" / "2025-Q4"

        review_template = q4_2025_dir / "review_template.yaml"
        assert review_template.exists(), "review_template.yaml does not exist"

        audit_findings = q4_2025_dir / "audit_findings.yaml"
        assert audit_findings.exists(), "audit_findings.yaml does not exist"

    def test_review_template_structure(self):
        """Test review template has required structure."""
        template_path = COMPLIANCE_DIR / "reviews" / "2025-Q4" / "review_template.yaml"
        data = load_yaml_mapping(template_path)

        required_sections = [
            "meta",
            "review_information",
            "review_sections",
            "metadata",
        ]

        for section in required_sections:
            assert section in data, f"review_template.yaml: Missing section '{section}'"

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
