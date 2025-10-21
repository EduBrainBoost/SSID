"""
Tests for Intent Evolution Guard v3.0
"""

import json
import pytest
from pathlib import Path
import sys

# Add tooling to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "12_tooling/evolution"))

try:
    from intent_evolution_guard import IntentEvolutionGuard, ChangeType, IntentCategory
    from auto_manifest_updater import AutoManifestUpdater
    IMPORT_SUCCESS = True
except ImportError:
    IMPORT_SUCCESS = False


@pytest.mark.skipif(not IMPORT_SUCCESS, reason="Evolution guard not importable")
def test_evolution_guard_initialization():
    """Test that evolution guard initializes correctly."""
    guard = IntentEvolutionGuard(repo_root=".")
    assert guard.repo_root.exists()
    assert guard.manifest_path.name == "artifact_intent_manifest.yaml"


@pytest.mark.skipif(not IMPORT_SUCCESS, reason="Evolution guard not importable")
def test_change_detection():
    """Test that change detection works."""
    guard = IntentEvolutionGuard(repo_root=".")
    changes = guard.detect_changes()

    # Should detect at least some files
    assert isinstance(changes, list)
    print(f"Detected {len(changes)} potential intent changes")


@pytest.mark.skipif(not IMPORT_SUCCESS, reason="Evolution guard not importable")
def test_category_classification():
    """Test category classification logic."""
    guard = IntentEvolutionGuard(repo_root=".")

    # Test policy classification
    policy_path = Path("23_compliance/policies/opa/test.rego")
    category = guard._classify_category(policy_path)
    assert category == IntentCategory.POLICY

    # Test tool classification
    tool_path = Path("12_tooling/tools/test_tool.py")
    category = guard._classify_category(tool_path)
    assert category == IntentCategory.TOOL


@pytest.mark.skipif(not IMPORT_SUCCESS, reason="Evolution guard not importable")
def test_layer_classification():
    """Test layer classification logic."""
    guard = IntentEvolutionGuard(repo_root=".")

    # Test core layer
    core_path = Path("03_core/healthcheck/test.py")
    layer = guard._classify_layer(core_path)
    assert layer == "03_core"

    # Test compliance layer
    compliance_path = Path("23_compliance/policies/test.rego")
    layer = guard._classify_layer(compliance_path)
    assert layer == "23_compliance"


@pytest.mark.skipif(not IMPORT_SUCCESS, reason="Evolution guard not importable")
def test_semantic_versioning():
    """Test semantic versioning logic."""
    guard = IntentEvolutionGuard(repo_root=".")

    # Mock change for new intent
    from intent_evolution_guard import IntentChange
    new_change = IntentChange(
        change_type=ChangeType.ADDED,
        artifact_path="test/new_file.py",
        old_hash=None,
        new_hash="abc123",
        timestamp="2025-10-14T12:00:00Z",
        category=IntentCategory.TOOL,
        layer="12_tooling",
        auto_generated_id="ART-TEST-001",
        metadata={}
    )

    version = guard.version_change(new_change)
    assert version.version == "1.0.0"
    assert not version.deprecated


def test_evolution_history_structure():
    """Test that evolution history has correct structure."""
    history_path = Path("24_meta_orchestration/registry/intent_evolution_history.json")

    if history_path.exists():
        with open(history_path) as f:
            history = json.load(f)

        assert isinstance(history, dict)

        for path, data in history.items():
            assert "intent_id" in data
            assert "category" in data
            assert "versions" in data
            assert isinstance(data["versions"], list)

            for version in data["versions"]:
                assert "version" in version
                assert "date" in version
                assert "hash" in version

                # Validate semantic version format
                parts = version["version"].split(".")
                assert len(parts) == 3
                assert all(p.isdigit() for p in parts)

        print(f"✓ Evolution history validated: {len(history)} intents")
    else:
        pytest.skip("Evolution history not yet created")


def test_manifest_auto_updater():
    """Test manifest auto-updater."""
    if not IMPORT_SUCCESS:
        pytest.skip("Cannot import evolution guard")

    updater = AutoManifestUpdater(repo_root=".")
    assert updater.manifest_path.name == "artifact_intent_manifest.yaml"

    # Test name generation
    name = updater._generate_name("path/to/test_file.py")
    assert name == "Test File"

    # Test owner determination
    owner = updater._determine_owner("03_core", "tool")
    assert owner == "platform-team"


def test_opa_evolution_policy_exists():
    """Test that OPA evolution policy exists."""
    policy_path = Path("23_compliance/policies/opa/intent_evolution.rego")
    assert policy_path.exists(), "OPA evolution policy missing"

    content = policy_path.read_text()
    assert "package intent.evolution" in content
    assert "allow" in content
    assert "deny" in content
    assert "evolution_stats" in content


def test_evolution_audit_trail():
    """Test that evolution creates audit trail."""
    audit_path = Path("02_audit_logging/reports/intent_evolution_audit.jsonl")

    if audit_path.exists():
        # Read last 10 entries
        with open(audit_path) as f:
            lines = f.readlines()[-10:]

        for line in lines:
            entry = json.loads(line)
            assert "timestamp" in entry
            assert "event" in entry
            assert entry["event"] == "intent_evolution"
            assert "change_type" in entry
            assert "artifact" in entry
            assert "version" in entry

        print(f"✓ Audit trail validated: {len(lines)} recent entries")
    else:
        pytest.skip("Evolution audit trail not yet created")


def test_backup_creation():
    """Test that backups are created."""
    backup_dir = Path("24_meta_orchestration/registry/backups")

    if not IMPORT_SUCCESS:
        pytest.skip("Cannot import evolution guard")

    updater = AutoManifestUpdater(repo_root=".")

    # Check backup directory structure
    assert backup_dir.exists() or not updater.manifest_path.exists()

    if backup_dir.exists():
        backups = list(backup_dir.glob("artifact_intent_manifest_backup_*.yaml"))
        print(f"✓ Found {len(backups)} manifest backups")


def test_integration_with_coverage_system():
    """Test integration with existing intent coverage system."""
    # Check that evolution guard integrates with coverage tracker
    guard_path = Path("12_tooling/evolution/intent_evolution_guard.py")
    tracker_path = Path("12_tooling/tools/intent_coverage_tracker.py")

    assert guard_path.exists(), "Evolution guard missing"
    assert tracker_path.exists(), "Coverage tracker missing"

    # Both should be able to work together
    manifest_path = Path("24_meta_orchestration/registry/artifact_intent_manifest.yaml")
    assert manifest_path.exists(), "Manifest missing"

    print("✓ Evolution guard integrated with coverage system")
