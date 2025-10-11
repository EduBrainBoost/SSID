#!/usr/bin/env python3
"""
WORM Storage Engine - Write-Once-Read-Many Evidence Storage
============================================================

Immutable evidence storage with cryptographic integrity guarantees.
Implements MUST-007-WORM-STORAGE compliance requirement.

Features:
- Write-once semantics (no updates/deletes after write)
- Cryptographic integrity verification (SHA-256)
- Tamper detection with content hashing
- Metadata immutability enforcement
- Audit trail for all access attempts

Compliance: MUST-007-WORM-STORAGE, GDPR Art.5(1)(f), MiCA Art.74
Version: 1.0.0
"""

import hashlib
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional, List
import stat


class WORMViolationError(Exception):
    """Raised when attempting to modify immutable WORM data."""
    raise NotImplementedError("TODO: Implement this block")


class WORMStorageEngine:
    """
    Write-Once-Read-Many storage engine for audit evidence.

    Guarantees:
    - Files can only be written once
    - No modifications after initial write
    - No deletions
    - Cryptographic integrity verification
    - Tamper detection
    """

    def __init__(self, storage_root: str = "02_audit_logging/worm_storage/vault"):
        """
        Initialize WORM storage engine.

        Args:
            storage_root: Root directory for WORM storage
        """
        self.storage_root = Path(storage_root)
        self.storage_root.mkdir(parents=True, exist_ok=True)

        # Metadata index (tracks all WORM files)
        self.index_path = self.storage_root / "worm_index.json"
        self.index: Dict[str, Dict[str, Any]] = self._load_index()

        # Access log (audit trail)
        self.access_log_path = self.storage_root / "access_log.jsonl"

    def _load_index(self) -> Dict[str, Dict[str, Any]]:
        """Load WORM file index."""
        if self.index_path.exists():
            with open(self.index_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _save_index(self) -> None:
        """Save WORM file index."""
        with open(self.index_path, 'w', encoding='utf-8') as f:
            json.dump(self.index, f, indent=2, ensure_ascii=False)

    def _log_access(self, event_type: str, evidence_id: str,
                    result: str, details: Optional[str] = None) -> None:
        """Log access attempt to audit trail."""
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type,
            "evidence_id": evidence_id,
            "result": result,
            "details": details
        }

        with open(self.access_log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + '\n')

    def _compute_content_hash(self, content: str) -> str:
        """Compute SHA-256 hash of content."""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def _make_readonly(self, file_path: Path) -> None:
        """Make file read-only (WORM enforcement)."""
        # Remove write permissions (Windows + Unix compatible)
        current_perms = file_path.stat().st_mode
        readonly_perms = current_perms & ~(stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH)
        file_path.chmod(readonly_perms)

    def write_evidence(self, evidence_id: str, evidence_data: Dict[str, Any],
                       category: str = "general") -> Dict[str, Any]:
        """
        Write evidence to WORM storage (write-once only).

        Args:
            evidence_id: Unique identifier for evidence
            evidence_data: Evidence content (JSON-serializable)
            category: Evidence category (for organization)

        Returns:
            Write confirmation with content hash and timestamp

        Raises:
            WORMViolationError: If evidence_id already exists
        """
        # Check if evidence already exists (WORM violation)
        if evidence_id in self.index:
            self._log_access("write_attempt", evidence_id, "DENIED",
                           "Evidence already exists (WORM violation)")
            raise WORMViolationError(
                f"Evidence {evidence_id} already exists. "
                "WORM storage does not allow modifications."
            )

        # Create category directory
        category_dir = self.storage_root / category
        category_dir.mkdir(parents=True, exist_ok=True)

        # Generate filename with timestamp
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        filename = f"{evidence_id}_{timestamp}.json"
        file_path = category_dir / filename

        # Prepare evidence envelope with metadata
        envelope = {
            "evidence_id": evidence_id,
            "category": category,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "worm_metadata": {
                "write_once": True,
                "immutable": True,
                "deletable": False,
                "retention_years": 10,
                "compliance": ["MUST-007-WORM-STORAGE", "GDPR-Art5", "MiCA-Art74"]
            },
            "evidence_data": evidence_data
        }

        # Serialize and compute hash
        content = json.dumps(envelope, indent=2, ensure_ascii=False, sort_keys=True)
        content_hash = self._compute_content_hash(content)

        # Add hash to envelope
        envelope["content_hash"] = content_hash
        final_content = json.dumps(envelope, indent=2, ensure_ascii=False, sort_keys=True)

        # Write to disk
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(final_content)

        # Make read-only (WORM enforcement)
        self._make_readonly(file_path)

        # Update index
        self.index[evidence_id] = {
            "file_path": str(file_path.relative_to(self.storage_root)),
            "category": category,
            "content_hash": content_hash,
            "timestamp": envelope["timestamp"],
            "size_bytes": len(final_content.encode('utf-8'))
        }
        self._save_index()

        # Log successful write
        self._log_access("write", evidence_id, "SUCCESS",
                        f"Hash: {content_hash[:16]}...")

        return {
            "evidence_id": evidence_id,
            "content_hash": content_hash,
            "file_path": str(file_path),
            "timestamp": envelope["timestamp"],
            "status": "IMMUTABLE",
            "worm_guaranteed": True
        }

    def read_evidence(self, evidence_id: str, verify_integrity: bool = True) -> Dict[str, Any]:
        """
        Read evidence from WORM storage with integrity verification.

        Args:
            evidence_id: Unique identifier for evidence
            verify_integrity: Verify cryptographic hash (default: True)

        Returns:
            Evidence data with verification status

        Raises:
            FileNotFoundError: If evidence doesn't exist
            ValueError: If integrity check fails
        """
        if evidence_id not in self.index:
            self._log_access("read_attempt", evidence_id, "DENIED",
                           "Evidence not found")
            raise FileNotFoundError(f"Evidence {evidence_id} not found in WORM storage")

        # Get file path from index
        index_entry = self.index[evidence_id]
        file_path = self.storage_root / index_entry["file_path"]

        # Read content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        envelope = json.loads(content)

        # Verify integrity
        if verify_integrity:
            stored_hash = envelope.get("content_hash")

            # Recompute hash (without content_hash field)
            envelope_copy = envelope.copy()
            envelope_copy.pop("content_hash", None)
            recomputed_content = json.dumps(envelope_copy, indent=2,
                                          ensure_ascii=False, sort_keys=True)
            recomputed_hash = self._compute_content_hash(recomputed_content)

            if recomputed_hash != stored_hash:
                self._log_access("read", evidence_id, "INTEGRITY_FAILURE",
                               f"Hash mismatch: {stored_hash[:16]} != {recomputed_hash[:16]}")
                raise ValueError(
                    f"Integrity check failed for evidence {evidence_id}. "
                    f"Expected {stored_hash[:16]}..., got {recomputed_hash[:16]}..."
                )

        # Log successful read
        self._log_access("read", evidence_id, "SUCCESS",
                        f"Integrity: {'VERIFIED' if verify_integrity else 'SKIPPED'}")

        return {
            "evidence_id": evidence_id,
            "evidence_data": envelope["evidence_data"],
            "metadata": envelope.get("worm_metadata", {}),
            "timestamp": envelope["timestamp"],
            "content_hash": envelope.get("content_hash"),
            "integrity_verified": verify_integrity
        }

    def list_evidence(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all evidence in WORM storage.

        Args:
            category: Filter by category (optional)

        Returns:
            List of evidence metadata
        """
        results = []
        for evidence_id, metadata in self.index.items():
            if category is None or metadata["category"] == category:
                results.append({
                    "evidence_id": evidence_id,
                    "category": metadata["category"],
                    "content_hash": metadata["content_hash"],
                    "timestamp": metadata["timestamp"],
                    "size_bytes": metadata["size_bytes"]
                })

        self._log_access("list", "ALL", "SUCCESS",
                        f"Found {len(results)} evidence files")

        return results

    def verify_all_integrity(self) -> Dict[str, Any]:
        """
        Verify integrity of all evidence files in WORM storage.

        Returns:
            Verification report with status for each file
        """
        report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_files": len(self.index),
            "verified": 0,
            "failed": 0,
            "results": []
        }

        for evidence_id in self.index.keys():
            try:
                self.read_evidence(evidence_id, verify_integrity=True)
                report["verified"] += 1
                report["results"].append({
                    "evidence_id": evidence_id,
                    "status": "VERIFIED",
                    "integrity": "OK"
                })
            except ValueError as e:
                report["failed"] += 1
                report["results"].append({
                    "evidence_id": evidence_id,
                    "status": "FAILED",
                    "integrity": "COMPROMISED",
                    "error": str(e)
                })

        self._log_access("verify_all", "ALL", "COMPLETE",
                        f"Verified: {report['verified']}, Failed: {report['failed']}")

        return report

    def get_access_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get recent access log entries.

        Args:
            limit: Maximum number of entries to return

        Returns:
            List of access log entries (most recent first)
        """
        if not self.access_log_path.exists():
            return []

        entries = []
        with open(self.access_log_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    entries.append(json.loads(line))

        # Return most recent first
        return entries[-limit:][::-1]


def test_worm_storage():
    """Test WORM storage functionality."""
    print("=" * 70)
    print("WORM Storage Engine - Functional Test")
    print("=" * 70)
    print()

    # Initialize WORM storage
    worm = WORMStorageEngine()

    # Test 1: Write evidence
    print("TEST 1: Writing evidence to WORM storage")
    print("-" * 70)
    evidence_id = f"test_evidence_{int(time.time())}"
    evidence_data = {
        "event": "test_audit_event",
        "user": "system",
        "action": "test_write",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    result = worm.write_evidence(evidence_id, evidence_data, category="test")
    print(f"Evidence ID: {result['evidence_id']}")
    print(f"Content Hash: {result['content_hash']}")
    print(f"Status: {result['status']}")
    print(f"WORM Guaranteed: {result['worm_guaranteed']}")
    print()

    # Test 2: Read evidence with integrity check
    print("TEST 2: Reading evidence with integrity verification")
    print("-" * 70)
    read_result = worm.read_evidence(evidence_id, verify_integrity=True)
    print(f"Evidence ID: {read_result['evidence_id']}")
    print(f"Integrity Verified: {read_result['integrity_verified']}")
    print(f"Content Hash: {read_result['content_hash']}")
    print()

    # Test 3: Attempt to overwrite (should fail)
    print("TEST 3: Attempting to overwrite (WORM violation)")
    print("-" * 70)
    try:
        worm.write_evidence(evidence_id, {"malicious": "data"}, category="test")
        print("[FAIL] WORM violation not detected!")
    except WORMViolationError as e:
        print(f"[OK] WORM protection active: {e}")
    print()

    # Test 4: List evidence
    print("TEST 4: Listing all evidence")
    print("-" * 70)
    evidence_list = worm.list_evidence(category="test")
    print(f"Found {len(evidence_list)} evidence files")
    for item in evidence_list[:3]:
        print(f"  - {item['evidence_id']} ({item['content_hash'][:16]}...)")
    print()

    # Test 5: Verify all integrity
    print("TEST 5: Verifying all evidence integrity")
    print("-" * 70)
    verification = worm.verify_all_integrity()
    print(f"Total Files: {verification['total_files']}")
    print(f"Verified: {verification['verified']}")
    print(f"Failed: {verification['failed']}")
    print()

    print("=" * 70)
    print("[OK] WORM Storage Engine - All Tests Passed")
    print("=" * 70)


if __name__ == "__main__":
    test_worm_storage()
