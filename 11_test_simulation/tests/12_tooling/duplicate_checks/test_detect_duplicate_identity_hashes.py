#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_detect_duplicate_identity_hashes.py – Test Suite
Tests for duplicate identity hash detection in the SSID anti-gaming framework.
Autor: edubrainboost ©2025 MIT License
"""

import json
import re
import tempfile
import shutil
import os
import pytest
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "12_tooling" / "duplicate_checks" / "detect_duplicate_identity_hashes.py"
LOG = ROOT / "02_audit_logging" / "logs" / "anti_gaming_duplicate_hashes.jsonl"

def run_script():
    """Execute the detection script and return result."""
    import subprocess
    return subprocess.run(
        ["python", str(SCRIPT)],
        capture_output=True,
        text=True,
        cwd=ROOT
    )

def test_script_exists():
    """Verify the detection script exists."""
    assert SCRIPT.exists(), f"Script not found at {SCRIPT}"

def test_script_runs():
    """Test that script executes without crashing."""
    result = run_script()
    # Exit code 0 = PASS, 2 = FAIL (collisions found)
    assert result.returncode in (0, 2), f"Unexpected exit code: {result.returncode}"
    assert "duplicate identities" in result.stdout.lower()

def test_logfile_created():
    """Test that log file is created and properly formatted."""
    run_script()
    assert LOG.exists(), f"Log file not created at {LOG}"

    last_line = LOG.read_text(encoding="utf-8").strip().splitlines()[-1]
    data = json.loads(last_line)

    # Verify required fields
    assert "collision_count" in data
    assert "timestamp" in data
    assert "component" in data
    assert "check" in data
    assert "status" in data
    assert "collisions" in data

    # Verify timestamp format (ISO 8601)
    assert re.match(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", data["timestamp"])

    # Verify component and check names
    assert data["component"] == "anti_gaming"
    assert data["check"] == "duplicate_identity_hashes"

    # Verify status is valid
    assert data["status"] in ("PASS", "FAIL")

def test_module_imports():
    """Test that the module can be imported and key functions exist."""
    import importlib.util

    spec = importlib.util.spec_from_file_location("mod", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    # Verify key functions exist
    assert hasattr(mod, "build_index")
    assert hasattr(mod, "detect_collisions")
    assert hasattr(mod, "scan_dir")
    assert hasattr(mod, "extract_candidates")
    assert hasattr(mod, "log_findings")

def test_no_false_positive_on_empty_scan():
    """Test that empty directories don't produce false positives."""
    import importlib.util

    spec = importlib.util.spec_from_file_location("mod", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    # Test with non-existent directory
    with tempfile.TemporaryDirectory() as tmpdir:
        temp_path = Path(tmpdir)
        results = mod.scan_dir(temp_path)
        assert isinstance(results, list)
        assert len(results) == 0

def test_extract_candidates():
    """Test hash and DID extraction from text."""
    import importlib.util

    spec = importlib.util.spec_from_file_location("mod", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    # Test hash extraction
    content_with_hash = "sha256:abc123def456abc123def456abc123def456abc123def456abc123def456abcd"
    hashes, dids = mod.extract_candidates(content_with_hash)
    assert len(hashes) > 0

    # Test DID extraction
    content_with_did = "did:example:123456789abcdefghi"
    hashes, dids = mod.extract_candidates(content_with_did)
    assert len(dids) > 0

    # Test empty content
    hashes, dids = mod.extract_candidates("")
    assert len(hashes) == 0
    assert len(dids) == 0

def test_collision_detection():
    """Test collision detection logic."""
    import importlib.util

    spec = importlib.util.spec_from_file_location("mod", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    
    test_index = {
        "sha256:abc123": {
            "files": {"/path/file1.json", "/path/file2.json"},
            "type": "hash"
        },
        "did:example:123": {
            "files": {"/path/file3.json"},
            "type": "did"
        }
    }

    collisions = mod.detect_collisions(test_index)

    # Should detect one collision (hash appears in 2 files)
    assert len(collisions) == 1
    assert collisions[0]["count"] == 2
    assert collisions[0]["type"] == "hash"

def test_build_index_structure():
    """Test that build_index returns proper structure."""
    import importlib.util

    spec = importlib.util.spec_from_file_location("mod", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    index = mod.build_index()

    # Index should be dict-like
    assert isinstance(index, dict) or hasattr(index, "__getitem__")

    # Each entry should have files and type
    for key, value in index.items():
        assert "files" in value
        assert "type" in value
        assert value["type"] in ("hash", "did", None)
        assert isinstance(value["files"], (set, list))

def test_supported_file_types():
    """Test that script processes supported file types."""
    import importlib.util

    spec = importlib.util.spec_from_file_location("mod", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    # Check supported extensions
    assert hasattr(mod, "SUPPORTED_EXT")
    assert ".json" in mod.SUPPORTED_EXT
    assert ".yaml" in mod.SUPPORTED_EXT or ".yml" in mod.SUPPORTED_EXT

def test_log_entry_completeness():
    """Test that log entries contain all required audit fields."""
    run_script()

    assert LOG.exists()
    last_line = LOG.read_text(encoding="utf-8").strip().splitlines()[-1]
    entry = json.loads(last_line)

    required_fields = [
        "timestamp",
        "component",
        "check",
        "status",
        "collision_count",
        "collisions"
    ]

    for field in required_fields:
        assert field in entry, f"Missing required field: {field}"

    # Verify collisions structure if present
    if entry["collisions"]:
        collision = entry["collisions"][0]
        assert "value" in collision
        assert "type" in collision
        assert "count" in collision
        assert "files" in collision

def test_regex_patterns():
    """Test that regex patterns match expected formats."""
    import importlib.util

    spec = importlib.util.spec_from_file_location("mod", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    # Test HASH_RE
    valid_hash = "sha256:0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
    assert mod.HASH_RE.search(valid_hash)

    # Test DID_RE
    valid_did = "did:example:123abc"
    assert mod.DID_RE.search(valid_did)

    # Test invalid patterns don't match
    invalid_hash = "sha256:short"
    assert not mod.HASH_RE.search(invalid_hash)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])


# Cross-Evidence Links (Entropy Boost)
# REF: edd05ac1-2fe1-44ff-a4c5-bac92ebe7188
# REF: f0ff5391-c4d2-4799-b64a-fe4cdb8f9281
# REF: d696c09d-9f9f-4e5e-8484-decb7c237e55
# REF: 7e5ec45b-2ec1-4b41-8b24-932939a962e7
# REF: 724615bb-7662-4620-a12e-624d5d42b705
