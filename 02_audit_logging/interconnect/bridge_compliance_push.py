"""
Bridge: 02_audit_logging → 23_compliance
Purpose: Push audit evidence to compliance registry
Evidence: SHA-256 logged in 24_meta_orchestration/registry/logs/
"""

import json
import os
import hashlib
import datetime
from typing import Dict, List, Any

def push_evidence_to_compliance(
    hash_chain_path: str = "02_audit_logging/storage/worm/hash_chain.json"
) -> Dict[str, str]:
    """
    Push local audit evidence into compliance evidence registry.

    Args:
        hash_chain_path: Path to the audit hash chain file

    Returns:
        Dict with status and details
    """
    target_dir = "23_compliance/evidence/audit_bridge/"
    os.makedirs(target_dir, exist_ok=True)

    if not os.path.exists(hash_chain_path):
        return {"status": "missing", "message": "Hash chain file not found"}

    try:
        with open(hash_chain_path, "r", encoding="utf-8") as src:
            data = src.read()

        # Create evidence file with timestamp
        timestamp = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        target_file = os.path.join(target_dir, f"audit_chain_{timestamp}.json")

        with open(target_file, "w", encoding="utf-8") as dst:
            dst.write(data)

        # Also update last_chain.json
        last_chain_path = os.path.join(target_dir, "last_chain.json")
        with open(last_chain_path, "w", encoding="utf-8") as dst:
            dst.write(data)

        # Calculate hash of transferred data
        data_hash = hashlib.sha256(data.encode()).hexdigest()

        return {
            "status": "ok",
            "target": target_file,
            "hash": data_hash,
            "timestamp": timestamp,
        }
    except IOError as e:
        return {"status": "error", "message": str(e)}

def create_audit_entry(event: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new audit log entry.

    Args:
        event: Event name/type
        data: Event data

    Returns:
        Audit entry dict with timestamp and hash
    """
    entry = {
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "event": event,
        "data": data,
    }

    # Generate hash
    entry["hash"] = hashlib.sha256(
        json.dumps(entry, sort_keys=True).encode()
    ).hexdigest()

    return entry

def append_to_hash_chain(
    entry: Dict[str, Any],
    hash_chain_path: str = "02_audit_logging/storage/worm/hash_chain.json"
) -> bool:
    """
    Append an audit entry to the hash chain.

    Args:
        entry: Audit entry to append
        hash_chain_path: Path to hash chain file

    Returns:
        True if successful, False otherwise
    """
    os.makedirs(os.path.dirname(hash_chain_path), exist_ok=True)

    try:
        with open(hash_chain_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
        return True
    except IOError:
        return False

def verify_hash_chain(
    hash_chain_path: str = "02_audit_logging/storage/worm/hash_chain.json"
) -> bool:
    """
    Verify the integrity of the audit hash chain.

    Args:
        hash_chain_path: Path to hash chain file

    Returns:
        True if chain is valid, False otherwise
    """
    if not os.path.exists(hash_chain_path):
        return True  # Empty chain is valid

    try:
        with open(hash_chain_path, "r", encoding="utf-8") as f:
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

def get_audit_stats(
    hash_chain_path: str = "02_audit_logging/storage/worm/hash_chain.json"
) -> Dict[str, Any]:
    """
    Get statistics about the audit chain.

    Args:
        hash_chain_path: Path to hash chain file

    Returns:
        Dict with stats (count, size, integrity)
    """
    if not os.path.exists(hash_chain_path):
        return {"count": 0, "size_bytes": 0, "integrity": True}

    try:
        with open(hash_chain_path, "r", encoding="utf-8") as f:
            lines = [line for line in f if line.strip()]

        file_size = os.path.getsize(hash_chain_path)
        integrity = verify_hash_chain(hash_chain_path)

        return {
            "count": len(lines),
            "size_bytes": file_size,
            "integrity": integrity,
        }
    except IOError:
        return {"count": 0, "size_bytes": 0, "integrity": False}

if __name__ == "__main__":
    # Self-test
    print("Bridge: 02_audit_logging → 23_compliance")

    # Create sample entry
    entry = create_audit_entry("test_event", {"key": "value"})
    print("Created entry:", entry)

    # Append to chain
    success = append_to_hash_chain(entry)
    print("Appended to chain:", success)

    # Get stats
    stats = get_audit_stats()
    print("Audit stats:", stats)

    # Push to compliance
    result = push_evidence_to_compliance()
    print("Push result:", result)
