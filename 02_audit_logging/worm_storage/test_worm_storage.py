#!/usr/bin/env python3
"""
Unit Tests for WORM Storage Engine
====================================

Compliance: MUST-007-WORM-STORAGE
Version: 1.0.0
"""

import pytest
import json
import os
import tempfile
import shutil
from pathlib import Path
from worm_storage_engine import WORMStorageEngine, WORMViolationError

@pytest.fixture
def temp_worm_storage():
    """Create temporary WORM storage for testing."""
    import stat
    temp_dir = tempfile.mkdtemp()
    storage_root = Path(temp_dir) / "worm_vault"
    worm = WORMStorageEngine(str(storage_root))
    yield worm
    # Cleanup: Make files writable before deletion (test cleanup only)
    def make_writable(path):
        """Make all files in path writable (for test cleanup)."""
        for root, dirs, files in os.walk(path):
            for filename in files:
                filepath = Path(root) / filename
                filepath.chmod(filepath.stat().st_mode | stat.S_IWUSR)
    make_writable(temp_dir)
    shutil.rmtree(temp_dir)

def test_write_evidence_success(temp_worm_storage):
    """Test writing evidence to WORM storage."""
    evidence_id = "test_001"
    evidence_data = {"event": "test_event", "value": 42}

    result = temp_worm_storage.write_evidence(evidence_id, evidence_data)

    assert result["evidence_id"] == evidence_id
    assert "content_hash" in result
    assert result["status"] == "IMMUTABLE"
    assert result["worm_guaranteed"] is True

def test_write_once_enforcement(temp_worm_storage):
    """Test WORM write-once enforcement."""
    evidence_id = "test_002"
    evidence_data = {"event": "first_write"}

    # First write succeeds
    temp_worm_storage.write_evidence(evidence_id, evidence_data)

    # Second write fails
    with pytest.raises(WORMViolationError):
        temp_worm_storage.write_evidence(evidence_id, {"event": "second_write"})

def test_read_evidence_success(temp_worm_storage):
    """Test reading evidence from WORM storage."""
    evidence_id = "test_003"
    evidence_data = {"event": "read_test", "value": 123}

    temp_worm_storage.write_evidence(evidence_id, evidence_data)
    result = temp_worm_storage.read_evidence(evidence_id)

    assert result["evidence_id"] == evidence_id
    assert result["evidence_data"] == evidence_data
    assert result["integrity_verified"] is True

def test_integrity_verification(temp_worm_storage):
    """Test cryptographic integrity verification."""
    evidence_id = "test_004"
    evidence_data = {"event": "integrity_test"}

    write_result = temp_worm_storage.write_evidence(evidence_id, evidence_data)
    read_result = temp_worm_storage.read_evidence(evidence_id, verify_integrity=True)

    assert write_result["content_hash"] == read_result["content_hash"]

def test_list_evidence(temp_worm_storage):
    """Test listing evidence files."""
    # Write multiple evidence files
    for i in range(3):
        temp_worm_storage.write_evidence(f"test_00{i+5}", {"value": i})

    evidence_list = temp_worm_storage.list_evidence()
    assert len(evidence_list) >= 3

def test_category_filtering(temp_worm_storage):
    """Test evidence categorization."""
    temp_worm_storage.write_evidence("cat_001", {"data": 1}, category="category_a")
    temp_worm_storage.write_evidence("cat_002", {"data": 2}, category="category_b")

    cat_a_list = temp_worm_storage.list_evidence(category="category_a")
    assert len(cat_a_list) == 1
    assert cat_a_list[0]["category"] == "category_a"

def test_verify_all_integrity(temp_worm_storage):
    """Test bulk integrity verification."""
    # Write multiple evidence files
    for i in range(3):
        temp_worm_storage.write_evidence(f"verify_00{i}", {"value": i})

    verification = temp_worm_storage.verify_all_integrity()

    assert verification["total_files"] >= 3
    assert verification["verified"] >= 3
    assert verification["failed"] == 0

def test_access_log(temp_worm_storage):
    """Test access logging."""
    evidence_id = "test_log_001"
    temp_worm_storage.write_evidence(evidence_id, {"data": "test"})
    temp_worm_storage.read_evidence(evidence_id)

    access_log = temp_worm_storage.get_access_log(limit=10)

    assert len(access_log) >= 2
    assert any(entry["event_type"] == "write" for entry in access_log)
    assert any(entry["event_type"] == "read" for entry in access_log)

def test_readonly_file_protection(temp_worm_storage):
    """Test that written files are read-only."""
    import stat

    evidence_id = "test_readonly"
    result = temp_worm_storage.write_evidence(evidence_id, {"data": "test"})

    file_path = Path(result["file_path"])
    file_stat = file_path.stat()

    # Check that file is read-only (no write permissions)
    assert not (file_stat.st_mode & stat.S_IWUSR)
    assert not (file_stat.st_mode & stat.S_IWGRP)
    assert not (file_stat.st_mode & stat.S_IWOTH)

def test_metadata_immutability(temp_worm_storage):
    """Test that WORM metadata is correctly set."""
    evidence_id = "test_metadata"
    temp_worm_storage.write_evidence(evidence_id, {"data": "test"})

    result = temp_worm_storage.read_evidence(evidence_id)
    metadata = result["metadata"]

    assert metadata["write_once"] is True
    assert metadata["immutable"] is True
    assert metadata["deletable"] is False
    assert metadata["retention_years"] == 10

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
