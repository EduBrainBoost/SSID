"""Tests for Shard_05_Gesundheit_Medizin"""
import pytest
from pathlib import Path
import yaml

# Go to project root, then to the actual shard location
SHARD = Path(__file__).parent.parent.parent.parent / "14_zero_time_auth/shards/Shard_05_Gesundheit_Medizin"

def test_shard_exists():
    assert SHARD.exists(), f"Shard not found: {SHARD}"

def test_chart_yaml_exists():
    assert (SHARD / "chart.yaml").exists()

def test_chart_yaml_valid():
    with open(SHARD / "chart.yaml") as f:
        chart = yaml.safe_load(f)
    assert chart["metadata"]["shard_id"] == "Shard_05_Gesundheit_Medizin"
    assert chart["metadata"]["version"] == "2.0.0"
    assert "governance" in chart
    assert "capabilities" in chart

def test_contracts_exist():
    contracts = list((SHARD / "contracts").glob("*.openapi.yaml"))
    assert len(contracts) >= 2, "Expected at least 2 OpenAPI contracts"

def test_schemas_exist():
    schemas = list((SHARD / "contracts/schemas").glob("*.schema.json"))
    assert len(schemas) >= 2, "Expected at least 2 JSON schemas"

def test_policies_exist():
    policies = list((SHARD / "policies").glob("*.yaml"))
    assert len(policies) == 7, f"Expected 7 policies, found {len(policies)}"

def test_implementation_exists():
    impl = SHARD / "implementations/python-tensorflow"
    assert impl.exists()
    assert (impl / "manifest.yaml").exists()
    assert (impl / "src/main.py").exists()
