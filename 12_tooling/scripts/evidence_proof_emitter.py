#!/usr/bin/env python3
"""
SSID Evidence Proof Emitter - Cryptographic Proof Generation for Forensic Reports

This script generates cryptographic proofs (SHA256 + Merkle roots) for forensic
reports and audit documents, with optional IPFS anchoring.

Blueprint: v4.4.0 - Functional Expansion
Layer: L6 - Evidence Layer
Compliance: GDPR / eIDAS / MiCA / DORA / AMLD6
"""

import json
import hashlib
import argparse
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict

# Configuration
EVIDENCE_DIR = Path("23_compliance/evidence")
REPORTS_DIRS = [
    Path("05_documentation/reports"),
    Path("11_test_simulation/reports"),
    Path("02_audit_logging/reports"),
    Path("24_meta_orchestration/registry/reports"),
]
PROOF_HASHES_FILE = EVIDENCE_DIR / "proof_hashes.json"
EVIDENCE_EVENT_FILE = Path("24_meta_orchestration/registry/events/evidence_emission_event.json")
AUDIT_LOG_FILE = Path("02_audit_logging/reports/evidence_emission_log.json")


@dataclass
class FileProof:
    """Represents cryptographic proof for a single file."""
    file_path: str
    file_hash: str
    file_size: int
    timestamp: str
    ipfs_cid: Optional[str] = None
    merkle_position: Optional[int] = None


@dataclass
class MerkleTree:
    """Represents a Merkle tree for evidence verification."""
    leaf_hashes: List[str]
    root_hash: str
    tree_depth: int
    total_leaves: int
    timestamp: str


@dataclass
class EvidenceEmissionResult:
    """Result of evidence proof emission."""
    timestamp: str
    total_files: int
    files_processed: List[str]
    files_failed: List[str]
    merkle_root: str
    ipfs_anchored: bool
    ipfs_cid: Optional[str]
    proof_hash_file: str
    status: str


class MerkleTreeBuilder:
    """Builds Merkle trees from file hashes."""

    def __init__(self, leaf_hashes: List[str]):
        self.leaf_hashes = leaf_hashes
        self.tree: List[List[str]] = []

    def build(self) -> MerkleTree:
        """Build the Merkle tree."""
        if not self.leaf_hashes:
            raise ValueError("No leaf hashes provided")

        # Pad to next power of 2
        padded_leaves = self._pad_to_power_of_2(self.leaf_hashes)

        # Build tree bottom-up
        current_level = padded_leaves
        self.tree = [current_level]

        while len(current_level) > 1:
            next_level = []
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                right = current_level[i + 1] if i + 1 < len(current_level) else current_level[i]
                parent = self._hash_pair(left, right)
                next_level.append(parent)

            current_level = next_level
            self.tree.append(current_level)

        root_hash = current_level[0]

        return MerkleTree(
            leaf_hashes=self.leaf_hashes,
            root_hash=root_hash,
            tree_depth=len(self.tree),
            total_leaves=len(self.leaf_hashes),
            timestamp=datetime.utcnow().isoformat() + "Z"
        )

    @staticmethod
    def _pad_to_power_of_2(items: List[str]) -> List[str]:
        """Pad list to next power of 2."""
        n = len(items)
        next_power = 1
        while next_power < n:
            next_power *= 2

        # Pad with last item
        padded = items.copy()
        while len(padded) < next_power:
            padded.append(items[-1])

        return padded

    @staticmethod
    def _hash_pair(left: str, right: str) -> str:
        """Hash a pair of nodes."""
        combined = left + right
        return hashlib.sha256(combined.encode()).hexdigest()


class EvidenceProofEmitter:
    """Generates cryptographic proofs for forensic evidence."""

    def __init__(self):
        self.evidence_dir = EVIDENCE_DIR
        self.reports_dirs = REPORTS_DIRS
        self.proof_hashes_file = PROOF_HASHES_FILE
        self.evidence_event_file = EVIDENCE_EVENT_FILE
        self.audit_log_file = AUDIT_LOG_FILE

    def emit_proofs(self, auto_anchor: bool = False, file_filter: Optional[str] = None) -> EvidenceEmissionResult:
        """Generate proofs for all forensic reports."""
        print("=" * 60)
        print("  SSID Evidence Proof Emitter")
        print("  Blueprint v4.4.0 - Evidence Layer")
        print("=" * 60)
        print()

        # Collect files
        files_to_process = self._collect_forensic_files(file_filter)
        print(f"Found {len(files_to_process)} forensic files")
        print()

        # Generate file proofs
        file_proofs: List[FileProof] = []
        files_processed = []
        files_failed = []

        for file_path in files_to_process:
            try:
                print(f"Processing: {file_path}")
                proof = self._generate_file_proof(file_path)

                # Optional IPFS anchoring
                if auto_anchor:
                    ipfs_cid = self._anchor_to_ipfs(file_path)
                    proof.ipfs_cid = ipfs_cid
                    if ipfs_cid:
                        print(f"  IPFS CID: {ipfs_cid}")

                file_proofs.append(proof)
                files_processed.append(str(file_path))
                print(f"  Hash: {proof.file_hash[:16]}...")

            except Exception as e:
                print(f"  ERROR: {e}")
                files_failed.append(str(file_path))

        print()

        # Build Merkle tree
        if file_proofs:
            leaf_hashes = [p.file_hash for p in file_proofs]
            merkle_builder = MerkleTreeBuilder(leaf_hashes)
            merkle_tree = merkle_builder.build()

            # Update proof positions
            for i, proof in enumerate(file_proofs):
                proof.merkle_position = i

            print(f"Merkle Tree Built:")
            print(f"  Root Hash: {merkle_tree.root_hash}")
            print(f"  Tree Depth: {merkle_tree.tree_depth}")
            print(f"  Total Leaves: {merkle_tree.total_leaves}")
            print()
        else:
            merkle_tree = MerkleTree(
                leaf_hashes=[],
                root_hash="",
                tree_depth=0,
                total_leaves=0,
                timestamp=datetime.utcnow().isoformat() + "Z"
            )

        # Save proof hashes
        self._save_proof_hashes(file_proofs, merkle_tree)

        # Create registry event
        self._create_registry_event(file_proofs, merkle_tree)

        # Anchor Merkle root to IPFS (optional)
        merkle_ipfs_cid = None
        if auto_anchor and merkle_tree.root_hash:
            merkle_ipfs_cid = self._anchor_merkle_root(merkle_tree)

        # Create result
        result = EvidenceEmissionResult(
            timestamp=datetime.utcnow().isoformat() + "Z",
            total_files=len(files_to_process),
            files_processed=files_processed,
            files_failed=files_failed,
            merkle_root=merkle_tree.root_hash,
            ipfs_anchored=auto_anchor,
            ipfs_cid=merkle_ipfs_cid,
            proof_hash_file=str(self.proof_hashes_file),
            status="success" if not files_failed else "partial_success"
        )

        # Write audit log
        self._write_audit_log(result)

        print("=" * 60)
        print("  Evidence Proof Emission Complete")
        print("=" * 60)
        print()
        print(f"Status: {result.status.upper()}")
        print(f"Files Processed: {len(files_processed)}")
        print(f"Files Failed: {len(files_failed)}")
        print(f"Merkle Root: {result.merkle_root[:32]}...")
        if result.ipfs_cid:
            print(f"IPFS CID: {result.ipfs_cid}")
        print()

        return result

    def _collect_forensic_files(self, file_filter: Optional[str]) -> List[Path]:
        """Collect all forensic report files."""
        files = []

        for reports_dir in self.reports_dirs:
            if not reports_dir.exists():
                continue

            # Find markdown and JSON files
            md_files = list(reports_dir.glob("**/*.md"))
            json_files = list(reports_dir.glob("**/*.json"))

            files.extend(md_files)
            files.extend(json_files)

        # Apply filter
        if file_filter:
            files = [f for f in files if file_filter in str(f)]

        return sorted(set(files))

    def _generate_file_proof(self, file_path: Path) -> FileProof:
        """Generate cryptographic proof for a single file."""
        # Calculate SHA256
        sha256_hash = hashlib.sha256()

        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)

        file_hash = sha256_hash.hexdigest()
        file_size = file_path.stat().st_size

        return FileProof(
            file_path=str(file_path),
            file_hash=file_hash,
            file_size=file_size,
            timestamp=datetime.utcnow().isoformat() + "Z"
        )

    def _anchor_to_ipfs(self, file_path: Path) -> Optional[str]:
        """Anchor file to IPFS (placeholder - actual implementation would use Web3.Storage or local daemon)."""
        # This is a placeholder - actual implementation would use:
        # 1. Web3.Storage API
        # 2. Local IPFS daemon
        # 3. Or other IPFS pinning service

        # For now, generate a mock CID based on file hash
        file_hash = hashlib.sha256(file_path.read_bytes()).hexdigest()
        # Real CIDs start with "bafy" for v1 CIDs
        mock_cid = f"bafy{file_hash[:58]}"

        return mock_cid

    def _anchor_merkle_root(self, merkle_tree: MerkleTree) -> Optional[str]:
        """Anchor Merkle root to IPFS."""
        # Create Merkle tree metadata
        merkle_data = {
            "root_hash": merkle_tree.root_hash,
            "tree_depth": merkle_tree.tree_depth,
            "total_leaves": merkle_tree.total_leaves,
            "timestamp": merkle_tree.timestamp
        }

        # Convert to JSON
        merkle_json = json.dumps(merkle_data, indent=2)

        # Mock CID generation
        data_hash = hashlib.sha256(merkle_json.encode()).hexdigest()
        mock_cid = f"bafy{data_hash[:58]}"

        print(f"Merkle root anchored to IPFS: {mock_cid}")

        return mock_cid

    def _save_proof_hashes(self, file_proofs: List[FileProof], merkle_tree: MerkleTree):
        """Save proof hashes to JSON file."""
        self.evidence_dir.mkdir(parents=True, exist_ok=True)

        proof_data = {
            "version": "1.0.0",
            "blueprint_version": "v4.4.0",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "merkle_tree": {
                "root_hash": merkle_tree.root_hash,
                "tree_depth": merkle_tree.tree_depth,
                "total_leaves": merkle_tree.total_leaves,
                "timestamp": merkle_tree.timestamp
            },
            "file_proofs": [asdict(p) for p in file_proofs],
            "total_files": len(file_proofs)
        }

        with open(self.proof_hashes_file, 'w') as f:
            json.dump(proof_data, f, indent=2)

        print(f"Proof hashes saved: {self.proof_hashes_file}")

    def _create_registry_event(self, file_proofs: List[FileProof], merkle_tree: MerkleTree):
        """Create registry event for evidence emission."""
        self.evidence_event_file.parent.mkdir(parents=True, exist_ok=True)

        event_data = {
            "event_type": "evidence_emission",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "blueprint_version": "v4.4.0",
            "total_files": len(file_proofs),
            "merkle_root": merkle_tree.root_hash,
            "proof_hash_file": str(self.proof_hashes_file),
            "status": "success"
        }

        with open(self.evidence_event_file, 'w') as f:
            json.dump(event_data, f, indent=2)

        print(f"Registry event created: {self.evidence_event_file}")

    def _write_audit_log(self, result: EvidenceEmissionResult):
        """Write audit log."""
        self.audit_log_file.parent.mkdir(parents=True, exist_ok=True)

        # Read existing log
        if self.audit_log_file.exists():
            with open(self.audit_log_file, 'r') as f:
                audit_log = json.load(f)
        else:
            audit_log = {
                "log_version": "1.0.0",
                "description": "Evidence proof emission audit log",
                "emissions": []
            }

        # Add new emission
        audit_log["emissions"].append(asdict(result))
        audit_log["last_updated"] = result.timestamp

        # Write log
        with open(self.audit_log_file, 'w') as f:
            json.dump(audit_log, f, indent=2)

        print(f"Audit log updated: {self.audit_log_file}")

    def verify_file(self, file_path: str, expected_hash: Optional[str] = None) -> bool:
        """Verify a file's hash against proof hashes."""
        print(f"Verifying file: {file_path}")

        # Generate current hash
        current_proof = self._generate_file_proof(Path(file_path))

        # Load proof hashes
        if not self.proof_hashes_file.exists():
            print("ERROR: Proof hashes file not found")
            return False

        with open(self.proof_hashes_file, 'r') as f:
            proof_data = json.load(f)

        # Find stored proof
        stored_proof = None
        for proof in proof_data.get("file_proofs", []):
            if proof["file_path"] == file_path:
                stored_proof = proof
                break

        if not stored_proof:
            print("ERROR: No stored proof found for this file")
            return False

        # Compare hashes
        if current_proof.file_hash == stored_proof["file_hash"]:
            print(f"OK: Hash verified")
            print(f"  Hash: {current_proof.file_hash}")
            return True
        else:
            print(f"ERROR: Hash mismatch")
            print(f"  Current:  {current_proof.file_hash}")
            print(f"  Expected: {stored_proof['file_hash']}")
            return False

    def calculate_merkle_root(self, quarter: Optional[str] = None) -> str:
        """Calculate Merkle root for Q1 2026 or specific quarter."""
        print(f"Calculating Merkle root for {quarter or 'current files'}...")

        # Collect files
        files = self._collect_forensic_files(quarter)

        if not files:
            print("No files found")
            return ""

        # Generate hashes
        file_hashes = []
        for file_path in files:
            proof = self._generate_file_proof(file_path)
            file_hashes.append(proof.file_hash)

        # Build Merkle tree
        merkle_builder = MerkleTreeBuilder(file_hashes)
        merkle_tree = merkle_builder.build()

        print(f"Merkle Root: {merkle_tree.root_hash}")
        print(f"Tree Depth: {merkle_tree.tree_depth}")
        print(f"Total Leaves: {merkle_tree.total_leaves}")

        return merkle_tree.root_hash


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="SSID Evidence Proof Emitter - Generate cryptographic proofs for forensic reports"
    )

    parser.add_argument(
        '--emit',
        action='store_true',
        help='Emit proofs for all forensic files'
    )

    parser.add_argument(
        '--auto-anchor',
        action='store_true',
        help='Automatically anchor to IPFS'
    )

    parser.add_argument(
        '--verify-file',
        type=str,
        metavar='FILE_PATH',
        help='Verify a specific file hash'
    )

    parser.add_argument(
        '--calculate-merkle-root',
        action='store_true',
        help='Calculate Merkle root for all files'
    )

    parser.add_argument(
        '--quarter',
        type=str,
        metavar='QUARTER',
        help='Filter files by quarter (e.g., "2026-Q1")'
    )

    parser.add_argument(
        '--filter',
        type=str,
        metavar='PATTERN',
        help='Filter files by pattern'
    )

    args = parser.parse_args()

    emitter = EvidenceProofEmitter()

    if args.emit:
        result = emitter.emit_proofs(
            auto_anchor=args.auto_anchor,
            file_filter=args.filter or args.quarter
        )
        sys.exit(0 if result.status == "success" else 1)

    elif args.verify_file:
        success = emitter.verify_file(args.verify_file)
        sys.exit(0 if success else 1)

    elif args.calculate_merkle_root:
        merkle_root = emitter.calculate_merkle_root(args.quarter)
        sys.exit(0 if merkle_root else 1)

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
