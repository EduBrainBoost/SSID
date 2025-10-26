"""
Comprehensive test suite for all 384 shards (24 roots × 16 shards)

Tests each shard for:
1. Directory existence
2. chart.yaml validity
3. Implementation presence
4. manifest.yaml in implementation
5. contracts/ directory
6. policies/ directory
7. docs/ directory
8. README.md

Total: 384 shards × 8 tests = 3,072 tests
"""

import pytest
import yaml
from pathlib import Path
from typing import Tuple, List

# 24 Root directories
ROOTS = [
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
    "24_meta_orchestration"
]

# 16 Shards per root
SHARDS = [
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
    "13_unternehmen_gewerbe",
    "14_vertraege_vereinbarungen",
    "15_handel_transaktionen",
    "16_behoerden_verwaltung"
]

# Generate all 384 combinations
ALL_SHARDS: List[Tuple[str, str]] = [(root, shard) for root in ROOTS for shard in SHARDS]


def get_repo_root() -> Path:
    """Get repository root path"""
    return Path(__file__).parents[2]


def get_shard_path(root: str, shard: str) -> Path:
    """Get path to specific shard"""
    return get_repo_root() / root / "shards" / shard


# Test 1: Shard Directory Exists (384 tests)
@pytest.mark.parametrize("root,shard", ALL_SHARDS)
def test_shard_directory_exists(root: str, shard: str):
    """Test that shard directory exists"""
    shard_path = get_shard_path(root, shard)
    assert shard_path.exists(), f"Shard directory missing: {root}/shards/{shard}"
    assert shard_path.is_dir(), f"Shard path is not a directory: {root}/shards/{shard}"


# Test 2: chart.yaml Exists and Valid (384 tests)
@pytest.mark.parametrize("root,shard", ALL_SHARDS)
def test_chart_yaml_exists_and_valid(root: str, shard: str):
    """Test that chart.yaml exists and contains valid YAML"""
    chart_path = get_shard_path(root, shard) / "chart.yaml"
    assert chart_path.exists(), f"chart.yaml missing in {root}/shards/{shard}"

    # Validate YAML syntax
    try:
        with open(chart_path, 'r', encoding='utf-8') as f:
            chart_data = yaml.safe_load(f)
        assert chart_data is not None, f"chart.yaml is empty in {root}/shards/{shard}"
        assert isinstance(chart_data, dict), f"chart.yaml is not a valid dict in {root}/shards/{shard}"
    except yaml.YAMLError as e:
        pytest.fail(f"Invalid YAML in {root}/shards/{shard}/chart.yaml: {e}")


# Test 3: Implementation Directory Exists with Content (384 tests)
@pytest.mark.parametrize("root,shard", ALL_SHARDS)
def test_implementation_exists(root: str, shard: str):
    """Test that implementations directory exists and contains at least one implementation"""
    impl_dir = get_shard_path(root, shard) / "implementations"
    assert impl_dir.exists(), f"implementations/ directory missing in {root}/shards/{shard}"
    assert impl_dir.is_dir(), f"implementations/ is not a directory in {root}/shards/{shard}"

    # Check for at least one implementation
    impls = list(impl_dir.iterdir())
    assert len(impls) > 0, f"No implementations found in {root}/shards/{shard}/implementations"


# Test 4: manifest.yaml in Implementation (384 tests)
@pytest.mark.parametrize("root,shard", ALL_SHARDS)
def test_manifest_yaml_exists(root: str, shard: str):
    """Test that at least one implementation contains manifest.yaml"""
    impl_dir = get_shard_path(root, shard) / "implementations"

    if not impl_dir.exists():
        pytest.skip(f"implementations/ directory missing in {root}/shards/{shard}")

    impls = list(impl_dir.iterdir())
    if len(impls) == 0:
        pytest.skip(f"No implementations in {root}/shards/{shard}")

    # Check first implementation for manifest.yaml
    first_impl = impls[0]
    manifest_path = first_impl / "manifest.yaml"
    assert manifest_path.exists(), f"manifest.yaml missing in {root}/shards/{shard}/implementations/{first_impl.name}"


# Test 5: contracts/ Directory Exists (384 tests)
@pytest.mark.parametrize("root,shard", ALL_SHARDS)
def test_contracts_directory_exists(root: str, shard: str):
    """Test that contracts/ directory exists"""
    contracts_dir = get_shard_path(root, shard) / "contracts"
    assert contracts_dir.exists(), f"contracts/ directory missing in {root}/shards/{shard}"
    assert contracts_dir.is_dir(), f"contracts/ is not a directory in {root}/shards/{shard}"


# Test 6: policies/ Directory Exists (384 tests)
@pytest.mark.parametrize("root,shard", ALL_SHARDS)
def test_policies_directory_exists(root: str, shard: str):
    """Test that policies/ directory exists"""
    policies_dir = get_shard_path(root, shard) / "policies"
    assert policies_dir.exists(), f"policies/ directory missing in {root}/shards/{shard}"
    assert policies_dir.is_dir(), f"policies/ is not a directory in {root}/shards/{shard}"


# Test 7: docs/ Directory Exists (384 tests)
@pytest.mark.parametrize("root,shard", ALL_SHARDS)
def test_docs_directory_exists(root: str, shard: str):
    """Test that docs/ directory exists"""
    docs_dir = get_shard_path(root, shard) / "docs"
    assert docs_dir.exists(), f"docs/ directory missing in {root}/shards/{shard}"
    assert docs_dir.is_dir(), f"docs/ is not a directory in {root}/shards/{shard}"


# Test 8: README.md Exists (384 tests)
@pytest.mark.parametrize("root,shard", ALL_SHARDS)
def test_readme_exists(root: str, shard: str):
    """Test that README.md exists"""
    readme_path = get_shard_path(root, shard) / "README.md"
    assert readme_path.exists(), f"README.md missing in {root}/shards/{shard}"
    assert readme_path.is_file(), f"README.md is not a file in {root}/shards/{shard}"


# Summary test to count expected vs actual
def test_shard_count_summary():
    """Verify we have exactly 384 shard combinations"""
    assert len(ROOTS) == 24, f"Expected 24 roots, found {len(ROOTS)}"
    assert len(SHARDS) == 16, f"Expected 16 shards, found {len(SHARDS)}"
    assert len(ALL_SHARDS) == 384, f"Expected 384 combinations, found {len(ALL_SHARDS)}"


# Utility test to list all missing shards
def test_list_missing_shards():
    """Generate list of all missing shards for reporting"""
    missing = []
    repo_root = get_repo_root()

    for root, shard in ALL_SHARDS:
        shard_path = repo_root / root / "shards" / shard
        if not shard_path.exists():
            missing.append(f"{root}/shards/{shard}")

    if missing:
        print(f"\n\nMISSING SHARDS ({len(missing)}/384):")
        for shard in missing:
            print(f"  - {shard}")
    else:
        print(f"\n\nALL 384 SHARDS EXIST!")

    # This test always passes but provides useful output
    assert True
