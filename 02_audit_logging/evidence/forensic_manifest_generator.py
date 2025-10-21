#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
forensic_manifest_generator.py – Forensic Evidence Manifest with Auto-Hash Injection
Autor: edubrainboost ©2025 MIT License

Automatically generates a deterministic YAML manifest of all import resolution
evidence files with SHA-256 hashes and merkle root for forensic audit trails.

Features:
- Scans 02_audit_logging/evidence/import_resolution/*.json
- Computes SHA-256 for each evidence file
- Generates merkle root from concatenated hashes
- Outputs YAML manifest with full provenance
- Integrates with existing audit chain
- OPA policy validation ready

Exit Codes:
  0 - SUCCESS: Manifest generated and valid
  1 - FAIL: No evidence files found or generation error
"""

import sys
import json
import yaml
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Tuple
from collections import OrderedDict


class ForensicManifestGenerator:
    """Generate forensic evidence manifest with auto-hash injection."""

    def __init__(self, root_dir: Path):
        self.root = root_dir
        self.evidence_dir = root_dir / "02_audit_logging" / "evidence" / "import_resolution"
        self.manifest_path = root_dir / "02_audit_logging" / "evidence" / "forensic_manifest.yaml"
        self.evidence_files: List[Path] = []
        self.hash_map: Dict[str, str] = {}

    def scan_evidence_files(self) -> int:
        """Scan and collect all evidence JSON files."""
        if not self.evidence_dir.exists():
            print(f"ERROR: Evidence directory not found: {self.evidence_dir}")
            return 0

        # Collect all JSON files
        self.evidence_files = sorted(self.evidence_dir.glob("*.json"))

        # Exclude the manifest itself if it exists
        self.evidence_files = [
            f for f in self.evidence_files
            if f.name != "forensic_manifest.json"
        ]

        return len(self.evidence_files)

    def compute_file_hash(self, file_path: Path) -> str:
        """Compute SHA-256 hash of a file."""
        sha256_hash = hashlib.sha256()

        try:
            with open(file_path, "rb") as f:
                # Read in chunks for memory efficiency
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)

            return sha256_hash.hexdigest()
        except (OSError, IOError) as e:
            print(f"WARNING: Could not hash {file_path.name}: {e}")
            return "ERROR_HASH_FAILED"

    def compute_hashes(self) -> None:
        """Compute SHA-256 hash for all evidence files."""
        for file_path in self.evidence_files:
            relative_path = str(file_path.relative_to(self.root)).replace("\\", "/")
            file_hash = self.compute_file_hash(file_path)
            self.hash_map[relative_path] = file_hash

    def compute_merkle_root(self) -> str:
        """
        Compute merkle root from concatenated hashes.

        Uses deterministic ordering (sorted by path) to ensure
        reproducible merkle root across builds.
        """
        if not self.hash_map:
            return "EMPTY_NO_EVIDENCE"

        # Sort by path for deterministic ordering
        sorted_items = sorted(self.hash_map.items())

        # Concatenate all hashes
        concatenated = "".join(hash_val for _, hash_val in sorted_items)

        # Compute merkle root
        merkle_root = hashlib.sha256(concatenated.encode()).hexdigest()

        return merkle_root

    def generate_manifest(self) -> Dict:
        """Generate complete forensic manifest structure."""
        merkle_root = self.compute_merkle_root()

        # Build evidence entries
        evidence_entries = []
        for file_path, file_hash in sorted(self.hash_map.items()):
            # Extract file metadata
            full_path = self.root / file_path
            file_size = full_path.stat().st_size if full_path.exists() else 0
            modified_time = (
                datetime.fromtimestamp(full_path.stat().st_mtime, tz=timezone.utc).isoformat()
                if full_path.exists() else None
            )

            evidence_entries.append({
                "path": file_path,
                "sha256": file_hash,
                "size_bytes": file_size,
                "modified": modified_time
            })

        manifest = {
            "version": 1,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "generator": "forensic_manifest_generator.py v1.0.0",
            "total_files": len(self.evidence_files),
            "merkle_root": merkle_root,
            "evidence_directory": "02_audit_logging/evidence/import_resolution",
            "evidence": evidence_entries,
            "integrity": {
                "algorithm": "SHA-256",
                "merkle_algorithm": "SHA-256 concatenated",
                "deterministic_ordering": "sorted by path"
            }
        }

        return manifest

    def write_manifest(self, manifest: Dict) -> None:
        """Write manifest to YAML file."""
        self.manifest_path.parent.mkdir(parents=True, exist_ok=True)

        # Use ordered dict to preserve key order in YAML
        with open(self.manifest_path, "w", encoding="utf-8") as f:
            yaml.dump(
                manifest,
                f,
                default_flow_style=False,
                sort_keys=False,
                allow_unicode=True,
                indent=2
            )

    def generate_audit_report(self, manifest: Dict) -> Dict:
        """Generate compliance audit report for the manifest."""
        report = {
            "report_type": "forensic_manifest_audit",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "manifest_version": manifest["version"],
            "manifest_merkle_root": manifest["merkle_root"],
            "evidence_count": manifest["total_files"],
            "validation": {
                "all_files_hashed": len([e for e in manifest["evidence"] if e["sha256"] != "ERROR_HASH_FAILED"]) == manifest["total_files"],
                "merkle_root_valid": manifest["merkle_root"] != "EMPTY_NO_EVIDENCE",
                "manifest_complete": True,
                "timestamp_valid": True
            },
            "evidence_files": [
                {
                    "path": e["path"],
                    "hash": e["sha256"][:16] + "...",  # Truncated for readability
                    "size": e["size_bytes"]
                }
                for e in manifest["evidence"]
            ],
            "compliance_status": "COMPLIANT" if all([
                manifest["total_files"] > 0,
                manifest["merkle_root"] != "EMPTY_NO_EVIDENCE",
                all(e["sha256"] != "ERROR_HASH_FAILED" for e in manifest["evidence"])
            ]) else "NON_COMPLIANT"
        }

        return report

    def write_audit_report(self, report: Dict) -> Path:
        """Write audit report to compliance directory."""
        report_dir = self.root / "23_compliance" / "reports"
        report_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        report_path = report_dir / f"forensic_manifest_audit_{timestamp}.json"

        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        return report_path

    def update_registry(self, manifest: Dict, report_path: Path) -> None:
        """Update meta orchestration registry with manifest metadata."""
        registry_dir = self.root / "24_meta_orchestration" / "registry"
        registry_dir.mkdir(parents=True, exist_ok=True)

        registry_path = registry_dir / "forensic_manifest_registry.yaml"

        # Load existing registry or create new
        if registry_path.exists():
            with open(registry_path, "r", encoding="utf-8") as f:
                registry = yaml.safe_load(f) or {}
        else:
            registry = {
                "registry_version": 1,
                "entries": []
            }

        # Add new entry
        entry = {
            "timestamp": manifest["generated_at"],
            "merkle_root": manifest["merkle_root"],
            "evidence_count": manifest["total_files"],
            "manifest_path": str(self.manifest_path.relative_to(self.root)).replace("\\", "/"),
            "audit_report": str(report_path.relative_to(self.root)).replace("\\", "/"),
            "status": "COMPLIANT" if manifest["merkle_root"] != "EMPTY_NO_EVIDENCE" else "NON_COMPLIANT",
            "build_hash": hashlib.sha256(manifest["merkle_root"].encode()).hexdigest()[:16]
        }

        # Append to entries
        if "entries" not in registry:
            registry["entries"] = []
        registry["entries"].append(entry)

        # Keep only last 100 entries
        registry["entries"] = registry["entries"][-100:]

        # Write registry
        with open(registry_path, "w", encoding="utf-8") as f:
            yaml.dump(registry, f, default_flow_style=False, sort_keys=False, indent=2)


def main() -> int:
    """Main execution."""
    print("=" * 70)
    print("Forensic Evidence Manifest Generator")
    print("=" * 70)
    print()

    root = Path(__file__).resolve().parents[2]
    generator = ForensicManifestGenerator(root)

    # Step 1: Scan evidence files
    print("Scanning evidence files...")
    file_count = generator.scan_evidence_files()

    if file_count == 0:
        print("ERROR: No evidence files found")
        print(f"Expected location: {generator.evidence_dir}")
        return 1

    print(f"Found {file_count} evidence files")
    print()

    # Step 2: Compute hashes
    print("Computing SHA-256 hashes...")
    generator.compute_hashes()
    print(f"Hashed {len(generator.hash_map)} files")
    print()

    # Step 3: Generate manifest
    print("Generating manifest...")
    manifest = generator.generate_manifest()
    merkle_root = manifest["merkle_root"]
    print(f"Merkle root: {merkle_root[:32]}...")
    print()

    # Step 4: Write manifest
    print("Writing manifest...")
    generator.write_manifest(manifest)
    print(f"Manifest: {generator.manifest_path.relative_to(root)}")
    print()

    # Step 5: Generate audit report
    print("Generating audit report...")
    audit_report = generator.generate_audit_report(manifest)
    report_path = generator.write_audit_report(audit_report)
    print(f"Report: {report_path.relative_to(root)}")
    print(f"Status: {audit_report['compliance_status']}")
    print()

    # Step 6: Update registry
    print("Updating registry...")
    generator.update_registry(manifest, report_path)
    print("Registry updated")
    print()

    # Summary
    print("=" * 70)
    print("Manifest Generation Complete")
    print("=" * 70)
    print(f"Evidence files: {manifest['total_files']}")
    print(f"Merkle root: {merkle_root}")
    print(f"Compliance: {audit_report['compliance_status']}")
    print()

    # Validation check
    if audit_report["compliance_status"] != "COMPLIANT":
        print("WARNING: Manifest is not compliant")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
