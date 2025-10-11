#!/usr/bin/env python3
"""
test_onchain_emit_sim.py — Simulation tests for on-chain proof emission

Tests DRY_RUN mode without requiring network connectivity or blockchain secrets.
Verifies that proof_emitter.py creates proper audit logs and returns correct structure.
"""
import os
import json
from pathlib import Path
import importlib.util
import pytest


ROOT = Path(__file__).resolve().parents[2]
EMIT_PATH = ROOT / "20_foundation" / "smart_contracts" / "proof_emitter.py"
LOG_PATH = ROOT / "02_audit_logging" / "evidence" / "blockchain" / "emits" / "blueprint42_proof.jsonl"


def load_emitter_module():
    """Dynamically load proof_emitter.py as module."""
    spec = importlib.util.spec_from_file_location("proof_emitter", EMIT_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestOnchainEmitDryRun:
    """Test on-chain proof emission in DRY_RUN mode."""

    @pytest.fixture(autouse=True)
    def setup_dry_run_env(self, monkeypatch):
        """Set DRY_RUN=1 for all tests."""
        monkeypatch.setenv("DRY_RUN", "1")

    @pytest.fixture
    def emitter(self):
        """Load emitter module."""
        return load_emitter_module()

    def test_dry_run_emit_creates_log(self, emitter):
        """Test that DRY_RUN mode creates audit log."""
        # Clean previous test logs if any
        if LOG_PATH.exists():
            existing_lines = len(LOG_PATH.read_text(encoding="utf-8").strip().splitlines())
        else:
            existing_lines = 0

        # Run emit in DRY_RUN mode
        result = emitter.emit(
            proof_type="BLUEPRINT_4_2_ACTIVATION",
            metadata_uri="ipfs://blueprint42/manifest.json"
        )

        # Verify result structure
        assert result["status"] == "SIMULATED"
        assert result["tx"] is None
        assert "registry_hash" in result
        assert result["registry_hash"].startswith("0x")
        assert len(result["registry_hash"]) == 66  # 0x + 64 hex chars

        # Verify audit log was created
        assert LOG_PATH.exists(), "Audit log not created"

        # Verify new log entry
        log_content = LOG_PATH.read_text(encoding="utf-8").strip()
        log_lines = log_content.splitlines()
        assert len(log_lines) > existing_lines, "No new log entry created"

        # Parse last log entry
        last_entry = json.loads(log_lines[-1])

        assert last_entry["component"] == "onchain_proof"
        assert last_entry["network"] == "polygon-mumbai"
        assert last_entry["proof_type"] == "BLUEPRINT_4_2_ACTIVATION"
        assert last_entry["mode"] == "DRY_RUN"
        assert last_entry["status"] == "SIMULATED"
        assert last_entry["tx"] is None
        assert last_entry["registry_hash"].startswith("0x")

    def test_registry_hash_is_deterministic(self, emitter):
        """Test that registry hash is deterministic for same file."""
        result1 = emitter.emit("TEST_1", "ipfs://test1")
        result2 = emitter.emit("TEST_2", "ipfs://test2")

        # Registry hash should be same (based on registry_lock.yaml content)
        assert result1["registry_hash"] == result2["registry_hash"]

    def test_registry_hash_format(self, emitter):
        """Test that registry hash is valid bytes32 hex."""
        hash_val = emitter.load_registry_hash()

        # Should start with 0x
        assert hash_val.startswith("0x")

        # Should be 66 chars total (0x + 64 hex)
        assert len(hash_val) == 66

        # Should be valid hex
        try:
            int(hash_val, 16)
        except ValueError:
            pytest.fail("Registry hash is not valid hex")

    def test_different_proof_types(self, emitter):
        """Test emission with different proof types."""
        proof_types = [
            "BLUEPRINT_4_2_ACTIVATION",
            "COMPLIANCE_UPDATE",
            "GOVERNANCE_DECISION",
            "RISK_ASSESSMENT"
        ]

        for proof_type in proof_types:
            result = emitter.emit(proof_type, "ipfs://test")
            assert result["status"] == "SIMULATED"
            assert result["registry_hash"].startswith("0x")

        # Verify all logged
        log_content = LOG_PATH.read_text(encoding="utf-8")
        for proof_type in proof_types:
            assert proof_type in log_content

    def test_metadata_uri_variations(self, emitter):
        """Test emission with different metadata URI schemes."""
        uris = [
            "ipfs://Qm...",
            "https://example.com/metadata.json",
            "ar://arweave-tx-id",
            "data:application/json;base64,eyJ..."
        ]

        for uri in uris:
            result = emitter.emit("TEST_PROOF", uri)
            assert result["status"] == "SIMULATED"


class TestEmitterModuleFunctions:
    """Test individual emitter module functions."""

    @pytest.fixture
    def emitter(self):
        """Load emitter module."""
        return load_emitter_module()

    def test_load_registry_hash_exists(self, emitter):
        """Test that load_registry_hash returns valid hash."""
        hash_val = emitter.load_registry_hash()
        assert isinstance(hash_val, str)
        assert hash_val.startswith("0x")
        assert len(hash_val) == 66

    def test_log_emit_creates_directory(self, emitter, tmp_path, monkeypatch):
        """Test that log_emit creates directory if not exists."""
        # Temporarily redirect EVID_DIR
        temp_evid = tmp_path / "evidence" / "blockchain" / "emits"
        monkeypatch.setattr(emitter, "EVID_DIR", temp_evid)

        # Log should create directory
        emitter.log_emit({"test": "data"})

        assert temp_evid.exists()
        assert (temp_evid / "blueprint42_proof.jsonl").exists()


class TestEmitterCLI:
    """Test command-line interface of emitter."""

    def test_cli_dry_run_mode(self, monkeypatch):
        """Test CLI in DRY_RUN mode."""
        import subprocess
        import sys

        monkeypatch.setenv("DRY_RUN", "1")

        result = subprocess.run(
            [sys.executable, str(EMIT_PATH)],
            capture_output=True,
            text=True,
            env={**os.environ, "DRY_RUN": "1"}
        )

        assert result.returncode == 0

        # Parse JSON output
        output = json.loads(result.stdout)
        assert output["status"] == "SIMULATED"
        assert output["tx"] is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
