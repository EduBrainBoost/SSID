"""
Bridge: 20_foundation → 24_meta_orchestration
Purpose: Registry lock updates for token registry sync
Evidence: SHA-256 logged in 24_meta_orchestration/registry/logs/
"""

import json
import hashlib
import datetime
import os
from typing import Dict

def record_registry_lock(
    lock_path: str = "24_meta_orchestration/registry/locks/bridge_lock.json"
) -> Dict[str, str]:
    """
    Append a timestamp + hash entry for token registry sync.

    Args:
        lock_path: Path to the lock file

    Returns:
        Dict with timestamp, event, and hash
    """
    # Ensure directory exists
    os.makedirs(os.path.dirname(lock_path), exist_ok=True)

    # Create entry
    entry = {
        "ts": datetime.datetime.utcnow().isoformat() + "Z",
        "event": "foundation→meta_orchestration sync",
        "source": "20_foundation",
        "target": "24_meta_orchestration",
    }

    # Generate hash
    entry["hash"] = hashlib.sha256(json.dumps(entry, sort_keys=True).encode()).hexdigest()

    # Append to lock file
    try:
        with open(lock_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except IOError as e:
        return {"status": "error", "message": str(e)}

    return entry

def get_last_sync_timestamp(
    lock_path: str = "24_meta_orchestration/registry/locks/bridge_lock.json"
) -> str:
    """
    Retrieve the timestamp of the last sync event.

    Args:
        lock_path: Path to the lock file

    Returns:
        ISO timestamp string or empty string if no sync found
    """
    if not os.path.exists(lock_path):
        return ""

    try:
        with open(lock_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            if not lines:
                return ""

            # Get last line
            last_entry = json.loads(lines[-1])
            return last_entry.get("ts", "")
    except (IOError, json.JSONDecodeError):
        return ""

def verify_lock_integrity(
    lock_path: str = "24_meta_orchestration/registry/locks/bridge_lock.json"
) -> bool:
    """
    Verify the integrity of all lock entries by checking hashes.

    Args:
        lock_path: Path to the lock file

    Returns:
        True if all entries are valid, False otherwise
    """
    if not os.path.exists(lock_path):
        return True  # Empty file is valid

    try:
        with open(lock_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue

                entry = json.loads(line)
                stored_hash = entry.pop("hash", None)

                # Recompute hash
                computed_hash = hashlib.sha256(
                    json.dumps(entry, sort_keys=True).encode()
                ).hexdigest()

                if stored_hash != computed_hash:
                    return False

        return True
    except (IOError, json.JSONDecodeError):
        return False

if __name__ == "__main__":
    # Self-test
    print("Bridge: 20_foundation → 24_meta_orchestration")
    result = record_registry_lock()
    print("Lock recorded:", result)
    print("Last sync:", get_last_sync_timestamp())
    print("Integrity check:", verify_lock_integrity())
