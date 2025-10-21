#!/usr/bin/env python3
"""
Pytest Configuration and Shared Fixtures
=========================================

This module provides shared fixtures and configuration for SoT Validator tests.

Key Fixtures:
- valid_repo_structure: Creates a valid 24x16 repository structure
- invalid_repo_structure: Creates various invalid structures for negative testing
- temp_repo: Provides a temporary directory for test repositories
- validator: Creates SoTValidator instances
- cached_validator: Creates CachedSoTValidator instances
"""

import pytest
import sys
import shutil
from pathlib import Path
from typing import Dict, List, Any
import yaml

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sot_validator_core import SoTValidator, REQUIRED_ROOT_COUNT, REQUIRED_SHARD_COUNT
from cached_validator import CachedSoTValidator


# ============================================================
# CONSTANTS
# ============================================================

# Standard shard names (01-16)
STANDARD_SHARDS = [
    "01_identitaet_personen",
    "02_dokumente_nachweise",
    "03_zugang_berechtigungen",
    "04_kommunikation_daten",
    "05_gesundheit_medizin",
    "06_bildung_qualifikationen",
    "07_familie_soziales",
    "08_mobilitaet_fahrzeuge",
    "09_arbeit_karriere",
    "10_finanzen_banking",
    "11_versicherungen_risiken",
    "12_immobilien_grundstuecke",
    "13_recht_verwaltung",
    "14_umwelt_energie",
    "15_kultur_medien",
    "16_forschung_innovation"
]

# Standard root names (01-24)
STANDARD_ROOTS = [
    "01_ai_layer",
    "02_blockchain_layer",
    "03_core",
    "04_federation",
    "05_governance",
    "06_identity",
    "07_interop",
    "08_legal",
    "09_lifecycle",
    "10_monitoring",
    "11_orchestration",
    "12_policy",
    "13_privacy",
    "14_registry",
    "15_security",
    "16_shard_contracts",
    "17_storage",
    "18_testing",
    "19_tooling",
    "20_ui_layer",
    "21_validation",
    "22_workflows",
    "23_zero_knowledge",
    "24_external_adapters"
]


# ============================================================
# DIRECTORY FIXTURES
# ============================================================

@pytest.fixture(scope="function")
def temp_repo(tmp_path):
    """
    Provides a temporary directory for creating test repositories.

    Cleanup is automatic via pytest's tmp_path fixture.

    Returns:
        Path: Temporary directory path
    """
    return tmp_path


@pytest.fixture(scope="function")
def valid_repo_structure(temp_repo):
    """
    Creates a valid 24x16 repository structure with all required files.

    Structure:
    - 24 root directories (01_ai_layer through 24_external_adapters)
    - 16 shards per root (01_identitaet_personen through 16_forschung_innovation)
    - Chart.yaml in each shard
    - values.yaml in each shard
    - templates/ directory in each shard
    - README.md in each root

    Returns:
        Path: Path to valid repository structure
    """
    repo_root = temp_repo / "valid_repo"
    repo_root.mkdir()

    # Create all 24 roots
    for root_name in STANDARD_ROOTS:
        root_dir = repo_root / root_name
        root_dir.mkdir()

        # Create README.md in root
        readme = root_dir / "README.md"
        readme.write_text(f"# {root_name}\n\nTest README for {root_name}")

        # Create all 16 shards in this root
        for shard_name in STANDARD_SHARDS:
            shard_dir = root_dir / shard_name
            shard_dir.mkdir()

            # Create Chart.yaml
            chart_yaml = shard_dir / "Chart.yaml"
            chart_data = {
                "apiVersion": "v2",
                "name": f"{root_name}-{shard_name}",
                "description": f"Test chart for {shard_name}",
                "version": "1.0.0",
                "type": "application"
            }
            chart_yaml.write_text(yaml.dump(chart_data))

            # Create values.yaml
            values_yaml = shard_dir / "values.yaml"
            values_data = {
                "replicaCount": 1,
                "image": {
                    "repository": "test/repo",
                    "tag": "1.0.0"
                }
            }
            values_yaml.write_text(yaml.dump(values_data))

            # Create templates directory
            templates_dir = shard_dir / "templates"
            templates_dir.mkdir()

            # Create a dummy template file
            deployment = templates_dir / "deployment.yaml"
            deployment.write_text("apiVersion: apps/v1\nkind: Deployment\n")

    return repo_root


@pytest.fixture(scope="function")
def invalid_repo_missing_roots(temp_repo):
    """
    Creates repository with only 20 roots (missing 4).

    Tests: AR001 (must have exactly 24 roots)
    """
    repo_root = temp_repo / "invalid_missing_roots"
    repo_root.mkdir()

    # Create only first 20 roots
    for root_name in STANDARD_ROOTS[:20]:
        root_dir = repo_root / root_name
        root_dir.mkdir()

        # Create minimal structure
        for shard_name in STANDARD_SHARDS:
            shard_dir = root_dir / shard_name
            shard_dir.mkdir()

    return repo_root


@pytest.fixture(scope="function")
def invalid_repo_missing_shards(temp_repo):
    """
    Creates repository where some roots have only 12 shards (missing 4).

    Tests: AR002 (each root must have exactly 16 shards)
    """
    repo_root = temp_repo / "invalid_missing_shards"
    repo_root.mkdir()

    # Create all 24 roots
    for i, root_name in enumerate(STANDARD_ROOTS):
        root_dir = repo_root / root_name
        root_dir.mkdir()

        # First 10 roots: only 12 shards
        # Remaining roots: all 16 shards
        shard_count = 12 if i < 10 else 16

        for shard_name in STANDARD_SHARDS[:shard_count]:
            shard_dir = root_dir / shard_name
            shard_dir.mkdir()

    return repo_root


@pytest.fixture(scope="function")
def invalid_repo_missing_charts(temp_repo):
    """
    Creates repository where some shards are missing Chart.yaml.

    Tests: AR004 (each shard must have Chart.yaml)
    """
    repo_root = temp_repo / "invalid_missing_charts"
    repo_root.mkdir()

    count = 0

    # Create all 24 roots
    for root_name in STANDARD_ROOTS:
        root_dir = repo_root / root_name
        root_dir.mkdir()

        # Create all 16 shards
        for shard_name in STANDARD_SHARDS:
            shard_dir = root_dir / shard_name
            shard_dir.mkdir()

            # Only create Chart.yaml for 75% of shards
            if count % 4 != 0:  # Skip every 4th shard
                chart_yaml = shard_dir / "Chart.yaml"
                chart_yaml.write_text("apiVersion: v2\nname: test\n")

            count += 1

    return repo_root


@pytest.fixture(scope="function")
def invalid_repo_missing_values(temp_repo):
    """
    Creates repository where some shards are missing values.yaml.

    Tests: AR005 (each shard must have values.yaml)
    """
    repo_root = temp_repo / "invalid_missing_values"
    repo_root.mkdir()

    count = 0

    # Create all 24 roots
    for root_name in STANDARD_ROOTS:
        root_dir = repo_root / root_name
        root_dir.mkdir()

        # Create all 16 shards
        for shard_name in STANDARD_SHARDS:
            shard_dir = root_dir / shard_name
            shard_dir.mkdir()

            # Only create values.yaml for 80% of shards
            if count % 5 != 0:  # Skip every 5th shard
                values_yaml = shard_dir / "values.yaml"
                values_yaml.write_text("replicaCount: 1\n")

            count += 1

    return repo_root


@pytest.fixture(scope="function")
def invalid_repo_missing_readme(temp_repo):
    """
    Creates repository where some roots are missing README.md.

    Tests: AR006 (each root must have README.md)
    """
    repo_root = temp_repo / "invalid_missing_readme"
    repo_root.mkdir()

    # Create all 24 roots
    for i, root_name in enumerate(STANDARD_ROOTS):
        root_dir = repo_root / root_name
        root_dir.mkdir()

        # Only create README for 75% of roots
        if i % 4 != 0:
            readme = root_dir / "README.md"
            readme.write_text(f"# {root_name}\n")

        # Create minimal shards
        for shard_name in STANDARD_SHARDS:
            shard_dir = root_dir / shard_name
            shard_dir.mkdir()

    return repo_root


@pytest.fixture(scope="function")
def invalid_repo_inconsistent_shards(temp_repo):
    """
    Creates repository where shards are not consistent across roots.

    Tests: AR007 (16 shards must be identical across all roots)
    """
    repo_root = temp_repo / "invalid_inconsistent_shards"
    repo_root.mkdir()

    # Create first 12 roots with standard shards
    for root_name in STANDARD_ROOTS[:12]:
        root_dir = repo_root / root_name
        root_dir.mkdir()

        for shard_name in STANDARD_SHARDS:
            shard_dir = root_dir / shard_name
            shard_dir.mkdir()

    # Create remaining roots with different shard names
    alternate_shards = [
        "01_alternative_shard",
        "02_different_name",
        "03_wrong_shard"
    ] + STANDARD_SHARDS[3:]  # Mix in some standard ones

    for root_name in STANDARD_ROOTS[12:]:
        root_dir = repo_root / root_name
        root_dir.mkdir()

        for shard_name in alternate_shards:
            shard_dir = root_dir / shard_name
            shard_dir.mkdir()

    return repo_root


@pytest.fixture(scope="function")
def invalid_repo_bad_shard_names(temp_repo):
    """
    Creates repository with incorrectly named shards.

    Tests: AR008 (shard names must match NN_name pattern with NN=01-16)
    """
    repo_root = temp_repo / "invalid_bad_shard_names"
    repo_root.mkdir()

    bad_shard_names = [
        "1_bad_name",           # Single digit
        "17_out_of_range",      # Number too high
        "00_zero_index",        # Number too low
        "01-wrong-separator",   # Wrong separator
        "01_UPPERCASE",         # Uppercase letters
        "01 with spaces",       # Spaces
        "notanumber_name"       # Missing number
    ] + STANDARD_SHARDS[7:]  # Fill rest with valid names

    # Create few roots with bad shard names
    for root_name in STANDARD_ROOTS[:3]:
        root_dir = repo_root / root_name
        root_dir.mkdir()

        for shard_name in bad_shard_names:
            shard_dir = root_dir / shard_name
            shard_dir.mkdir()

    # Rest are valid
    for root_name in STANDARD_ROOTS[3:]:
        root_dir = repo_root / root_name
        root_dir.mkdir()

        for shard_name in STANDARD_SHARDS:
            shard_dir = root_dir / shard_name
            shard_dir.mkdir()

    return repo_root


@pytest.fixture(scope="function")
def invalid_repo_bad_root_names(temp_repo):
    """
    Creates repository with incorrectly named roots.

    Tests: AR009 (root names must match NN_name pattern with NN=01-24)
    """
    repo_root = temp_repo / "invalid_bad_root_names"
    repo_root.mkdir()

    bad_root_names = [
        "1_bad_name",           # Single digit
        "25_out_of_range",      # Number too high
        "00_zero_index",        # Number too low
        "01-wrong-separator",   # Wrong separator
        "01_UPPERCASE",         # Uppercase letters
    ] + STANDARD_ROOTS[5:]  # Fill rest with valid names

    for root_name in bad_root_names:
        root_dir = repo_root / root_name
        root_dir.mkdir()

        # Create minimal shards
        for shard_name in STANDARD_SHARDS:
            shard_dir = root_dir / shard_name
            shard_dir.mkdir()

    return repo_root


@pytest.fixture(scope="function")
def invalid_repo_missing_templates(temp_repo):
    """
    Creates repository where some shards are missing templates/ directory.

    Tests: AR010 (each shard must have templates/ directory)
    """
    repo_root = temp_repo / "invalid_missing_templates"
    repo_root.mkdir()

    count = 0

    # Create all 24 roots
    for root_name in STANDARD_ROOTS:
        root_dir = repo_root / root_name
        root_dir.mkdir()

        # Create all 16 shards
        for shard_name in STANDARD_SHARDS:
            shard_dir = root_dir / shard_name
            shard_dir.mkdir()

            # Only create templates/ for 70% of shards
            if count % 10 < 7:
                templates_dir = shard_dir / "templates"
                templates_dir.mkdir()

            count += 1

    return repo_root


# ============================================================
# VALIDATOR FIXTURES
# ============================================================

@pytest.fixture(scope="function")
def validator(valid_repo_structure):
    """
    Creates SoTValidator instance with valid repository.

    Returns:
        SoTValidator: Validator instance
    """
    return SoTValidator(repo_root=valid_repo_structure)


@pytest.fixture(scope="function")
def cached_validator(valid_repo_structure):
    """
    Creates CachedSoTValidator instance with valid repository.

    Returns:
        CachedSoTValidator: Cached validator instance
    """
    return CachedSoTValidator(repo_root=valid_repo_structure, cache_ttl=60)


# ============================================================
# HELPER FIXTURES
# ============================================================

@pytest.fixture(scope="session")
def real_repo_root():
    """
    Provides path to actual SSID repository for integration tests.

    Returns:
        Path: Path to real repository (or None if not found)
    """
    # Try to find real repo
    test_dir = Path(__file__).parent
    validator_dir = test_dir.parent
    core_dir = validator_dir.parent.parent
    repo_root = core_dir.parent

    # Validate it's actually the SSID repo
    if (repo_root / "01_ai_layer").exists() and (repo_root / "03_core").exists():
        return repo_root

    return None


@pytest.fixture(scope="function")
def performance_timer():
    """
    Provides a timer for performance testing.

    Usage:
        with performance_timer() as timer:
            # code to time
        assert timer.elapsed < 0.1  # 100ms
    """
    import time

    class Timer:
        def __init__(self):
            self.start = None
            self.end = None
            self.elapsed = None

        def __enter__(self):
            self.start = time.perf_counter()
            return self

        def __exit__(self, *args):
            self.end = time.perf_counter()
            self.elapsed = self.end - self.start

    return Timer


# ============================================================
# PYTEST CONFIGURATION
# ============================================================

def pytest_configure(config):
    """Configure pytest with custom markers and settings."""
    config.addinivalue_line(
        "markers", "ar: Architecture rule tests (AR001-AR010)"
    )
    config.addinivalue_line(
        "markers", "cp: Compliance rule tests (CP001+)"
    )
    config.addinivalue_line(
        "markers", "performance: Performance and benchmark tests"
    )
    config.addinivalue_line(
        "markers", "slow: Tests that take more than 1 second"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically."""
    for item in items:
        # Auto-mark AR tests
        if "ar001" in item.nodeid.lower() or "ar_" in item.nodeid.lower():
            item.add_marker(pytest.mark.ar)

        # Auto-mark CP tests
        if "cp001" in item.nodeid.lower() or "cp_" in item.nodeid.lower():
            item.add_marker(pytest.mark.cp)

        # Auto-mark performance tests
        if "performance" in item.nodeid.lower() or "benchmark" in item.nodeid.lower():
            item.add_marker(pytest.mark.performance)
