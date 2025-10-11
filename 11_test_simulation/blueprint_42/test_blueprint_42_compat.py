#!/usr/bin/env python3
"""
Blueprint 4.2 Compatibility Test Suite
Tests all requirements for Blueprint 4.2 upgrade from 4.1.
"""
from pathlib import Path
import yaml
import json
import hashlib
import pytest


REPO = Path(__file__).resolve().parents[2]


class TestRequiredPaths:
    """Test that all required Blueprint 4.2 paths exist."""

    def test_consortium_registry_exists(self):
        """Consortium registry must exist."""
        path = REPO / "24_meta_orchestration/consortium/consortium_registry.yaml"
        assert path.exists(), f"Missing: {path}"

    def test_consensus_policy_exists(self):
        """Consensus policy must exist."""
        path = REPO / "24_meta_orchestration/consortium/consensus_policy.yaml"
        assert path.exists(), f"Missing: {path}"

    def test_rego_policy_exists(self):
        """OPA/Rego compliance policy must exist."""
        path = REPO / "23_compliance/policy_as_code/rego_policies/ssid_compliance_policy.rego"
        assert path.exists(), f"Missing: {path}"

    def test_snapshot_diff_index_exists(self):
        """Snapshot diff index must exist."""
        path = REPO / "23_compliance/ai_ml_ready/snapshot_diffs/index.json"
        assert path.exists(), f"Missing: {path}"

    def test_technical_dashboard_exists(self):
        """Technical dashboard view must exist."""
        path = REPO / "13_ui_layer/synced_views/technical_dashboard.json"
        assert path.exists(), f"Missing: {path}"

    def test_legal_narrative_exists(self):
        """Legal narrative view must exist."""
        path = REPO / "13_ui_layer/synced_views/legal_narrative.md"
        assert path.exists(), f"Missing: {path}"

    def test_sync_metadata_exists(self):
        """Sync metadata must exist."""
        path = REPO / "13_ui_layer/synced_views/sync_metadata.json"
        assert path.exists(), f"Missing: {path}"

    def test_blueprint_42_manifest_exists(self):
        """Blueprint 4.2 manifest must exist."""
        path = REPO / "24_meta_orchestration/registry/manifests/blueprint_4_2_manifest.yaml"
        assert path.exists(), f"Missing: {path}"

    def test_blueprint_42_rfc_exists(self):
        """Blueprint 4.2 RFC must exist."""
        path = REPO / "23_compliance/governance/blueprint_4_2_rfc.yaml"
        assert path.exists(), f"Missing: {path}"


class TestRegistryLock:
    """Test registry_lock.yaml contains required Blueprint 4.2 fields."""

    @pytest.fixture
    def registry_lock(self):
        """Load registry lock file."""
        path = REPO / "24_meta_orchestration/registry/locks/registry_lock.yaml"
        assert path.exists(), "registry_lock.yaml not found"
        return yaml.safe_load(path.read_text(encoding="utf-8"))

    def test_consortium_status_exists(self, registry_lock):
        """registry_lock.yaml must contain consortium_status."""
        assert "consortium_status" in registry_lock, \
            "Missing consortium_status in registry_lock.yaml"

    def test_compliance_evidence_exists(self, registry_lock):
        """registry_lock.yaml must contain compliance_evidence."""
        assert "compliance_evidence" in registry_lock, \
            "Missing compliance_evidence in registry_lock.yaml"

    def test_consortium_status_structure(self, registry_lock):
        """consortium_status must have proper structure."""
        cs = registry_lock.get("consortium_status", {})
        assert "enabled" in cs, "consortium_status missing 'enabled' field"
        assert isinstance(cs["enabled"], bool), "enabled must be boolean"

    def test_blueprint_version_if_present(self, registry_lock):
        """If blueprint_version exists, verify it's 4.2.0."""
        if "blueprint_version" in registry_lock:
            version = registry_lock["blueprint_version"]
            assert version.startswith("4.2"), \
                f"Expected 4.2.x, got {version}"


class TestSyncIntegrity:
    """Test unified view sync integrity."""

    @pytest.fixture
    def sync_metadata(self):
        """Load sync metadata."""
        path = REPO / "13_ui_layer/synced_views/sync_metadata.json"
        assert path.exists(), "sync_metadata.json not found"
        return json.loads(path.read_text(encoding="utf-8"))

    @pytest.fixture
    def technical_dashboard_content(self):
        """Load technical dashboard content."""
        path = REPO / "13_ui_layer/synced_views/technical_dashboard.json"
        assert path.exists(), "technical_dashboard.json not found"
        return path.read_bytes()

    @pytest.fixture
    def legal_narrative_content(self):
        """Load legal narrative content."""
        path = REPO / "13_ui_layer/synced_views/legal_narrative.md"
        assert path.exists(), "legal_narrative.md not found"
        return path.read_bytes()

    def test_sync_metadata_has_integrity_hash(self, sync_metadata):
        """sync_metadata.json must contain integrity_hash."""
        assert "integrity_hash" in sync_metadata, \
            "Missing integrity_hash in sync_metadata.json"

    def test_integrity_hash_valid(
        self,
        sync_metadata,
        technical_dashboard_content,
        legal_narrative_content
    ):
        """Integrity hash must match combined content hash."""
        stored_hash = sync_metadata["integrity_hash"]
        computed_hash = hashlib.sha256(
            technical_dashboard_content + legal_narrative_content
        ).hexdigest()

        # Check at least first 16 characters match
        assert stored_hash.startswith(computed_hash[:16]), \
            f"Integrity hash mismatch: expected {computed_hash[:16]}..., got {stored_hash[:16]}..."


class TestSnapshotDiffIndex:
    """Test snapshot diff index structure."""

    @pytest.fixture
    def snapshot_index(self):
        """Load snapshot diff index."""
        path = REPO / "23_compliance/ai_ml_ready/snapshot_diffs/index.json"
        assert path.exists(), "snapshot_diffs/index.json not found"
        return json.loads(path.read_text(encoding="utf-8"))

    def test_index_has_snapshots_key(self, snapshot_index):
        """Index must contain 'snapshots' key."""
        assert "snapshots" in snapshot_index, \
            "Missing 'snapshots' key in index.json"

    def test_snapshots_is_list(self, snapshot_index):
        """Snapshots must be a list."""
        snapshots = snapshot_index["snapshots"]
        assert isinstance(snapshots, list), \
            "snapshots must be a list"


class TestConsortiumQuorum:
    """Test consortium BFT quorum requirements."""

    @pytest.fixture
    def consortium_registry(self):
        """Load consortium registry."""
        path = REPO / "24_meta_orchestration/consortium/consortium_registry.yaml"
        assert path.exists(), "consortium_registry.yaml not found"
        return yaml.safe_load(path.read_text(encoding="utf-8"))

    def test_members_exist(self, consortium_registry):
        """Consortium registry must have members."""
        assert "members" in consortium_registry, \
            "Missing 'members' in consortium_registry.yaml"

    def test_quorum_requirements(self, consortium_registry):
        """Test BFT quorum: ≥11 weighted points, ≥5 distinct signers."""
        members = consortium_registry.get("members", [])

        total_weight = 0
        distinct_signers = 0

        for member in members:
            if member.get("status") == "active":
                distinct_signers += 1
                total_weight += member.get("weight", 1)

        assert total_weight >= 11, \
            f"Insufficient weighted quorum: need ≥11, got {total_weight}"

        assert distinct_signers >= 5, \
            f"Insufficient distinct signers: need ≥5, got {distinct_signers}"


class TestBlueprint42Artifacts:
    """Test Blueprint 4.2 specific artifacts."""

    def test_manifest_structure(self):
        """Blueprint 4.2 manifest must be valid."""
        path = REPO / "24_meta_orchestration/registry/manifests/blueprint_4_2_manifest.yaml"
        manifest = yaml.safe_load(path.read_text(encoding="utf-8"))

        assert "meta" in manifest
        assert manifest["meta"]["version"] == "4.2.0"
        assert manifest["meta"]["base_blueprint"] == "4.1.x"
        assert "compatibility" in manifest
        assert manifest["compatibility"]["breaking_changes"] is False

    def test_rfc_structure(self):
        """Blueprint 4.2 RFC must be valid."""
        path = REPO / "23_compliance/governance/blueprint_4_2_rfc.yaml"
        rfc = yaml.safe_load(path.read_text(encoding="utf-8"))

        assert "rfc" in rfc
        assert rfc["rfc"]["id"] == "RFC-BP-4.2"
        assert "criteria" in rfc
        assert "must" in rfc["criteria"]
        assert "must_not" in rfc["criteria"]

    def test_no_new_root_folders(self):
        """Verify no new root folders were created."""
        # Get all top-level directories
        top_levels = [p for p in REPO.iterdir() if p.is_dir() and not p.name.startswith(".")]

        # Expected roots (adjust based on your existing structure)
        expected_roots = {
            "01_source_of_truth",
            "02_audit_logging",
            "03_risk_scoring",
            "04_federation_interop",
            "11_test_simulation",
            "12_cli_tools",
            "13_ui_layer",
            "14_api",
            "15_docs",
            "16_codex",
            "23_compliance",
            "24_meta_orchestration",
        }

        actual_roots = {p.name for p in top_levels}

        # Allow expected roots + common dirs like .git, node_modules, etc.
        unexpected = actual_roots - expected_roots - {
            "node_modules", "__pycache__", ".pytest_cache", "venv", ".venv"
        }

        assert len(unexpected) == 0, \
            f"Unexpected root folders detected: {unexpected}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
