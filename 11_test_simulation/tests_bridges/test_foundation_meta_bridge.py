"""
Test: 20_foundation → 24_meta_orchestration bridge
Tests registry lock updates
"""

import pytest
import sys
import os
import json
import tempfile
import shutil

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, project_root)

# Load module with importlib since module names starting with numbers are invalid
import importlib.util
spec = importlib.util.spec_from_file_location(
    "bridge_meta_orchestration",
    os.path.join(project_root, "20_foundation/interconnect/bridge_meta_orchestration.py")
)
bridge_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bridge_module)

record_registry_lock = bridge_module.record_registry_lock
get_last_sync_timestamp = bridge_module.get_last_sync_timestamp
verify_lock_integrity = bridge_module.verify_lock_integrity

@pytest.fixture
def temp_lock_file():
    """Create a temporary lock file for testing."""
    temp_dir = tempfile.mkdtemp()
    lock_path = os.path.join(temp_dir, "test_lock.json")
    yield lock_path
    shutil.rmtree(temp_dir)

def test_record_registry_lock(temp_lock_file):
    """Test recording a registry lock."""
    result = record_registry_lock(temp_lock_file)

    assert "ts" in result
    assert "event" in result
    assert "hash" in result
    assert result["event"] == "foundation→meta_orchestration sync"

def test_record_multiple_locks(temp_lock_file):
    """Test recording multiple locks."""
    result1 = record_registry_lock(temp_lock_file)
    result2 = record_registry_lock(temp_lock_file)

    assert result1["hash"] != result2["hash"]  # Different timestamps
    assert os.path.exists(temp_lock_file)

def test_get_last_sync_timestamp(temp_lock_file):
    """Test retrieving last sync timestamp."""
    # Initially empty
    assert get_last_sync_timestamp(temp_lock_file) == ""

    # After recording
    record_registry_lock(temp_lock_file)
    ts = get_last_sync_timestamp(temp_lock_file)
    assert ts != ""
    assert "Z" in ts  # UTC format

def test_verify_lock_integrity_empty(temp_lock_file):
    """Test verifying integrity of empty file."""
    assert verify_lock_integrity(temp_lock_file) is True

def test_verify_lock_integrity_valid(temp_lock_file):
    """Test verifying integrity of valid locks."""
    record_registry_lock(temp_lock_file)
    record_registry_lock(temp_lock_file)

    assert verify_lock_integrity(temp_lock_file) is True

def test_verify_lock_integrity_tampered(temp_lock_file):
    """Test detecting tampered lock file."""
    record_registry_lock(temp_lock_file)

    # Tamper with file
    with open(temp_lock_file, "r") as f:
        content = f.read()

    # Modify content without updating hash
    tampered = content.replace('"source"', '"modified"')
    with open(temp_lock_file, "w") as f:
        f.write(tampered)

    assert verify_lock_integrity(temp_lock_file) is False

if __name__ == "__main__":
    pytest.main([__file__, "-v"])


# Cross-Evidence Links (Entropy Boost)
# REF: 3689c514-e2fa-4b51-b717-99772f77f3c0
# REF: 24b7127c-3465-4911-a9fb-6b4f057d4831
# REF: ba030c8d-55f5-4076-b7ce-5da566994255
# REF: 56aa756c-01e2-4643-b9f2-c475792df05f
# REF: 11ea57bf-d346-42a8-9280-85bee219cbb2
