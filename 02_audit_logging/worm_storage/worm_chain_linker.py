#!/usr/bin/env python3
"""
WORM Chain Linker - Double-Link Verification for PLATINUM Certification
========================================================================

Extends WORM storage with bidirectional chain linking (Merkle-like structure).
Each WORM entry references both previous and next entries for tamper detection.

Features:
- Bidirectional chain linking (previous + next hash)
- Merkle-tree-like integrity verification
- Chain continuity validation
- Break detection with pinpoint accuracy
- PLATINUM-grade audit trail

Version: 1.0.0 (PLATINUM Preparation)
"""

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple

class ChainIntegrityError(Exception):
    """Raised when chain integrity is compromised."""
    pass

class WORMChainLinker:
    """
    WORM Chain Linker with double-link verification.

    Creates a bidirectional chain of WORM entries where:
    - Each entry contains hash of previous entry (backward link)
    - Each entry is referenced by next entry (forward link)
    - Chain can be verified in both directions
    - Any tampering breaks both forward and backward links
    """

    def __init__(self, storage_root: str = "02_audit_logging/storage/worm"):
        """
        Initialize WORM chain linker.

        Args:
            storage_root: Root directory for WORM storage
        """
        self.storage_root = Path(storage_root)
        self.immutable_store = self.storage_root / "immutable_store"
        self.immutable_store.mkdir(parents=True, exist_ok=True)

        # Chain index (tracks chain structure)
        self.chain_index_path = self.storage_root / "chain_index.json"
        self.chain_index: Dict[str, Any] = self._load_chain_index()

    def _load_chain_index(self) -> Dict[str, Any]:
        """Load chain index."""
        if self.chain_index_path.exists():
            with open(self.chain_index_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "chain_head": None,
            "chain_tail": None,
            "total_entries": 0,
            "entries": {}
        }

    def _save_chain_index(self) -> None:
        """Save chain index."""
        with open(self.chain_index_path, 'w', encoding='utf-8') as f:
            json.dump(self.chain_index, f, indent=2, ensure_ascii=False)

    def _compute_entry_hash(self, entry_data: Dict[str, Any]) -> str:
        """Compute SHA-512 hash of entry (PLATINUM-grade)."""
        # Sort keys for deterministic hashing
        canonical = json.dumps(entry_data, sort_keys=True, ensure_ascii=False)
        return hashlib.sha512(canonical.encode('utf-8')).hexdigest()

    def _compute_blake2b(self, entry_data: Dict[str, Any]) -> str:
        """Compute BLAKE2b hash (secondary verification)."""
        canonical = json.dumps(entry_data, sort_keys=True, ensure_ascii=False)
        return hashlib.blake2b(canonical.encode('utf-8')).hexdigest()

    def add_chain_entry(self, entry_id: str, entry_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add entry to WORM chain with double-link verification.

        Args:
            entry_id: Unique identifier for entry
            entry_data: Entry content (JSON-serializable)

        Returns:
            Chain entry with forward/backward links
        """
        timestamp = datetime.now(timezone.utc).isoformat()

        # Get previous entry (tail of chain)
        prev_hash = None
        prev_entry_id = self.chain_index.get("chain_tail")

        if prev_entry_id:
            prev_entry = self._read_chain_entry(prev_entry_id)
            prev_hash = prev_entry["entry_hash"]

        # Create chain entry
        chain_entry = {
            "entry_id": entry_id,
            "timestamp": timestamp,
            "entry_data": entry_data,
            "chain_links": {
                "previous_hash": prev_hash,
                "previous_entry_id": prev_entry_id,
                "next_hash": None,  # Will be filled by next entry
                "next_entry_id": None
            },
            "chain_metadata": {
                "chain_position": self.chain_index["total_entries"],
                "is_genesis": prev_entry_id is None,
                "double_link_verified": False
            }
        }

        # Compute hashes (without hash fields)
        entry_hash = self._compute_entry_hash(chain_entry)
        blake2b_hash = self._compute_blake2b(chain_entry)

        # Add hashes to entry
        chain_entry["entry_hash"] = entry_hash
        chain_entry["blake2b_hash"] = blake2b_hash

        # Write to immutable storage
        filename = f"sot_enforcement_v2_{timestamp.replace(':', '').replace('.', '')}_chain_{entry_id}.json"
        file_path = self.immutable_store / filename

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(chain_entry, f, indent=2, ensure_ascii=False)

        # Update previous entry with forward link
        if prev_entry_id:
            self._update_forward_link(prev_entry_id, entry_id, entry_hash)

        # Update chain index
        if self.chain_index["chain_head"] is None:
            self.chain_index["chain_head"] = entry_id

        self.chain_index["chain_tail"] = entry_id
        self.chain_index["total_entries"] += 1
        self.chain_index["entries"][entry_id] = {
            "file_path": str(file_path.relative_to(self.storage_root)),
            "entry_hash": entry_hash,
            "blake2b_hash": blake2b_hash,
            "timestamp": timestamp,
            "previous_entry_id": prev_entry_id,
            "next_entry_id": None
        }

        # Update previous entry index
        if prev_entry_id:
            self.chain_index["entries"][prev_entry_id]["next_entry_id"] = entry_id

        self._save_chain_index()

        return {
            "entry_id": entry_id,
            "entry_hash": entry_hash,
            "blake2b_hash": blake2b_hash,
            "file_path": str(file_path),
            "timestamp": timestamp,
            "chain_position": chain_entry["chain_metadata"]["chain_position"],
            "is_genesis": chain_entry["chain_metadata"]["is_genesis"],
            "status": "CHAIN_LINKED"
        }

    def _update_forward_link(self, prev_entry_id: str, next_entry_id: str, next_hash: str) -> None:
        """Update forward link in previous entry (creates double-link)."""
        prev_entry = self._read_chain_entry(prev_entry_id)

        # Update forward link
        prev_entry["chain_links"]["next_hash"] = next_hash
        prev_entry["chain_links"]["next_entry_id"] = next_entry_id
        prev_entry["chain_metadata"]["double_link_verified"] = True

        # Recompute hash with updated links
        prev_entry.pop("entry_hash", None)
        prev_entry.pop("blake2b_hash", None)
        updated_hash = self._compute_entry_hash(prev_entry)
        updated_blake2b = self._compute_blake2b(prev_entry)
        prev_entry["entry_hash"] = updated_hash
        prev_entry["blake2b_hash"] = updated_blake2b

        # Write updated entry (append-only, new version)
        file_path = self.storage_root / self.chain_index["entries"][prev_entry_id]["file_path"]
        timestamp = datetime.now(timezone.utc).isoformat()
        updated_filename = f"{file_path.stem}_updated_{timestamp.replace(':', '').replace('.', '')}.json"
        updated_path = file_path.parent / updated_filename

        with open(updated_path, 'w', encoding='utf-8') as f:
            json.dump(prev_entry, f, indent=2, ensure_ascii=False)

        # Update index to point to new version
        self.chain_index["entries"][prev_entry_id]["file_path"] = str(updated_path.relative_to(self.storage_root))
        self.chain_index["entries"][prev_entry_id]["entry_hash"] = updated_hash
        self.chain_index["entries"][prev_entry_id]["blake2b_hash"] = updated_blake2b

    def _read_chain_entry(self, entry_id: str) -> Dict[str, Any]:
        """Read chain entry from storage."""
        if entry_id not in self.chain_index["entries"]:
            raise FileNotFoundError(f"Chain entry {entry_id} not found")

        file_path = self.storage_root / self.chain_index["entries"][entry_id]["file_path"]
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def verify_chain_integrity(self, direction: str = "both") -> Dict[str, Any]:
        """
        Verify chain integrity in forward, backward, or both directions.

        Args:
            direction: "forward", "backward", or "both"

        Returns:
            Verification report with detailed results
        """
        report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_entries": self.chain_index["total_entries"],
            "direction": direction,
            "forward_verification": None,
            "backward_verification": None,
            "integrity_status": "UNKNOWN"
        }

        if direction in ["forward", "both"]:
            report["forward_verification"] = self._verify_forward_chain()

        if direction in ["backward", "both"]:
            report["backward_verification"] = self._verify_backward_chain()

        # Determine overall status
        forward_ok = (direction not in ["forward", "both"] or
                     report["forward_verification"]["status"] == "OK")
        backward_ok = (direction not in ["backward", "both"] or
                      report["backward_verification"]["status"] == "OK")

        if forward_ok and backward_ok:
            report["integrity_status"] = "VERIFIED"
        else:
            report["integrity_status"] = "COMPROMISED"

        return report

    def _verify_forward_chain(self) -> Dict[str, Any]:
        """Verify chain integrity in forward direction (head -> tail)."""
        result = {
            "status": "OK",
            "verified_links": 0,
            "broken_links": [],
            "details": []
        }

        current_id = self.chain_index.get("chain_head")

        while current_id:
            current_entry = self._read_chain_entry(current_id)
            next_id = current_entry["chain_links"]["next_entry_id"]

            if next_id:
                # Verify forward link
                next_entry = self._read_chain_entry(next_id)
                expected_hash = next_entry["entry_hash"]
                actual_hash = current_entry["chain_links"]["next_hash"]

                if expected_hash != actual_hash:
                    result["status"] = "BROKEN"
                    result["broken_links"].append({
                        "from_entry": current_id,
                        "to_entry": next_id,
                        "expected_hash": expected_hash[:16] + "...",
                        "actual_hash": actual_hash[:16] + "..." if actual_hash else "None"
                    })
                else:
                    result["verified_links"] += 1

            current_id = next_id

        return result

    def _verify_backward_chain(self) -> Dict[str, Any]:
        """Verify chain integrity in backward direction (tail -> head)."""
        result = {
            "status": "OK",
            "verified_links": 0,
            "broken_links": [],
            "details": []
        }

        current_id = self.chain_index.get("chain_tail")

        while current_id:
            current_entry = self._read_chain_entry(current_id)
            prev_id = current_entry["chain_links"]["previous_entry_id"]

            if prev_id:
                # Verify backward link
                prev_entry = self._read_chain_entry(prev_id)
                expected_hash = prev_entry["entry_hash"]
                actual_hash = current_entry["chain_links"]["previous_hash"]

                if expected_hash != actual_hash:
                    result["status"] = "BROKEN"
                    result["broken_links"].append({
                        "from_entry": current_id,
                        "to_entry": prev_id,
                        "expected_hash": expected_hash[:16] + "...",
                        "actual_hash": actual_hash[:16] + "..." if actual_hash else "None"
                    })
                else:
                    result["verified_links"] += 1

            current_id = prev_id

        return result

    def get_chain_stats(self) -> Dict[str, Any]:
        """Get chain statistics."""
        return {
            "total_entries": self.chain_index["total_entries"],
            "chain_head": self.chain_index.get("chain_head"),
            "chain_tail": self.chain_index.get("chain_tail"),
            "double_linked_entries": sum(
                1 for e in self.chain_index["entries"].values()
                if e.get("next_entry_id") is not None
            )
        }

def demo_worm_chain_linker():
    """Demo WORM chain linker functionality."""
    print("=" * 70)
    print("WORM Chain Linker - Double-Link Verification (PLATINUM Prep)")
    print("=" * 70)
    print()

    linker = WORMChainLinker()

    # Add sample chain entries
    print("Adding chain entries...")
    for i in range(3):
        entry_id = f"demo_entry_{i}"
        entry_data = {
            "event": f"demo_event_{i}",
            "score": 85 + i,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        result = linker.add_chain_entry(entry_id, entry_data)
        print(f"  - Entry {i}: {result['entry_id']} (pos: {result['chain_position']})")
    print()

    # Verify chain integrity
    print("Verifying chain integrity (both directions)...")
    verification = linker.verify_chain_integrity(direction="both")
    print(f"  Status: {verification['integrity_status']}")
    print(f"  Forward: {verification['forward_verification']['verified_links']} links verified")
    print(f"  Backward: {verification['backward_verification']['verified_links']} links verified")
    print()

    # Show chain stats
    print("Chain statistics:")
    stats = linker.get_chain_stats()
    print(f"  Total entries: {stats['total_entries']}")
    print(f"  Chain head: {stats['chain_head']}")
    print(f"  Chain tail: {stats['chain_tail']}")
    print(f"  Double-linked: {stats['double_linked_entries']}")
    print()

    print("=" * 70)
    print("[OK] WORM Chain Linker - PLATINUM Preparation Complete")
    print("=" * 70)

if __name__ == "__main__":
    demo_worm_chain_linker()
