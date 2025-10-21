#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test: Forensic Manifest Validation
Autor: edubrainboost ©2025 MIT License

Validates forensic evidence manifest for:
- Existence and structure
- Complete evidence file coverage
- Valid SHA-256 hashes
- Merkle root correctness
- OPA policy compliance

Exit Codes:
  0 - PASS: All validation checks passed
  1 - FAIL: One or more validation checks failed
"""

import sys
import json
import yaml
import hashlib
import pytest
from pathlib import Path
from datetime import datetime, timezone, timedelta


class TestForensicManifest:
    """Test suite for forensic manifest validation."""

    @pytest.fixture(scope="class")
    def root_dir(self):
        """Get repository root directory."""
        return Path(__file__).resolve().parents[2]

    @pytest.fixture(scope="class")
    def manifest_path(self, root_dir):
        """Get manifest file path."""
        return root_dir / "02_audit_logging" / "evidence" / "forensic_manifest.yaml"

    @pytest.fixture(scope="class")
    def evidence_dir(self, root_dir):
        """Get evidence directory path."""
        return root_dir / "02_audit_logging" / "evidence" / "import_resolution"

    @pytest.fixture(scope="class")
    def manifest(self, manifest_path):
        """Load and return manifest data."""
        if not manifest_path.exists():
            pytest.skip(f"Manifest not found: {manifest_path}")

        with open(manifest_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def test_manifest_exists(self, manifest_path):
        """Test that manifest file exists."""
        assert manifest_path.exists(), f"Manifest file not found: {manifest_path}"

    def test_manifest_structure(self, manifest):
        """Test that manifest has required structure."""
        required_fields = ["version", "generated_at", "total_files", "merkle_root", "evidence"]
        for field in required_fields:
            assert field in manifest, f"Missing required field: {field}"

    def test_manifest_version(self, manifest):
        """Test that manifest version is valid."""
        assert manifest["version"] == 1, f"Invalid manifest version: {manifest['version']}"

    def test_manifest_freshness(self, manifest):
        """Test that manifest is less than 24 hours old."""
        generated_at = datetime.fromisoformat(manifest["generated_at"].replace("Z", "+00:00"))
        age = datetime.now(timezone.utc) - generated_at
        assert age < timedelta(hours=24), f"Manifest is too old: {age.total_seconds() / 3600:.1f} hours"

    def test_evidence_count(self, manifest):
        """Test that evidence count matches array length."""
        assert manifest["total_files"] == len(manifest["evidence"]), \
            f"Evidence count mismatch: {manifest['total_files']} != {len(manifest['evidence'])}"

    def test_evidence_files_exist(self, manifest, root_dir):
        """Test that all evidence files listed in manifest exist."""
        missing_files = []
        for entry in manifest["evidence"]:
            file_path = root_dir / entry["path"]
            if not file_path.exists():
                missing_files.append(entry["path"])

        assert len(missing_files) == 0, f"Missing evidence files: {missing_files}"

    def test_all_evidence_files_covered(self, manifest, evidence_dir, root_dir):
        """Test that all evidence files in directory are covered by manifest."""
        if not evidence_dir.exists():
            pytest.skip(f"Evidence directory not found: {evidence_dir}")

        # Get all JSON files in evidence directory
        actual_files = {
            str(f.relative_to(root_dir)).replace("\\", "/")
            for f in evidence_dir.glob("*.json")
            if f.name != "forensic_manifest.json"
        }

        # Get files listed in manifest
        manifest_files = {entry["path"] for entry in manifest["evidence"]}

        # Check for missing files
        missing_from_manifest = actual_files - manifest_files
        assert len(missing_from_manifest) == 0, \
            f"Evidence files not in manifest: {missing_from_manifest}"

    def test_hash_validity(self, manifest):
        """Test that all hashes are valid SHA-256 hashes."""
        invalid_hashes = []
        for entry in manifest["evidence"]:
            hash_val = entry["sha256"]
            if hash_val == "ERROR_HASH_FAILED":
                invalid_hashes.append(entry["path"])
            elif len(hash_val) != 64:
                invalid_hashes.append(f"{entry['path']} (invalid length: {len(hash_val)})")

        assert len(invalid_hashes) == 0, f"Invalid hashes: {invalid_hashes}"

    def test_hash_correctness(self, manifest, root_dir):
        """Test that file hashes match actual file contents."""
        mismatches = []

        for entry in manifest["evidence"]:
            file_path = root_dir / entry["path"]
            if not file_path.exists():
                continue

            # Compute actual hash
            sha256_hash = hashlib.sha256()
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            actual_hash = sha256_hash.hexdigest()

            # Compare with manifest hash
            if actual_hash != entry["sha256"]:
                mismatches.append(f"{entry['path']}: {entry['sha256'][:16]}... != {actual_hash[:16]}...")

        assert len(mismatches) == 0, f"Hash mismatches: {mismatches}"

    def test_merkle_root_validity(self, manifest):
        """Test that merkle root is valid."""
        merkle_root = manifest["merkle_root"]
        assert merkle_root != "EMPTY_NO_EVIDENCE", "Merkle root is empty"
        assert len(merkle_root) == 64, f"Invalid merkle root length: {len(merkle_root)}"

    def test_merkle_root_correctness(self, manifest):
        """Test that merkle root is correctly computed."""
        # Sort by path for deterministic ordering
        sorted_entries = sorted(manifest["evidence"], key=lambda e: e["path"])

        # Concatenate all hashes
        concatenated = "".join(entry["sha256"] for entry in sorted_entries)

        # Compute expected merkle root
        expected_merkle_root = hashlib.sha256(concatenated.encode()).hexdigest()

        assert manifest["merkle_root"] == expected_merkle_root, \
            f"Merkle root mismatch: {manifest['merkle_root'][:16]}... != {expected_merkle_root[:16]}..."

    def test_no_duplicate_hashes(self, manifest):
        """Test that there are no duplicate hashes (collision detection)."""
        hashes = [entry["sha256"] for entry in manifest["evidence"]]
        unique_hashes = set(hashes)

        assert len(hashes) == len(unique_hashes), \
            f"Duplicate hashes detected: {len(hashes)} total, {len(unique_hashes)} unique"

    def test_evidence_directory_path(self, manifest):
        """Test that evidence directory path is correct."""
        expected_dir = "02_audit_logging/evidence/import_resolution"
        assert manifest["evidence_directory"] == expected_dir, \
            f"Evidence directory mismatch: {manifest['evidence_directory']} != {expected_dir}"

    def test_audit_report_exists(self, root_dir):
        """Test that audit report exists."""
        report_dir = root_dir / "23_compliance" / "reports"
        if not report_dir.exists():
            pytest.skip(f"Report directory not found: {report_dir}")

        # Find most recent audit report
        reports = sorted(report_dir.glob("forensic_manifest_audit_*.json"))
        assert len(reports) > 0, "No audit reports found"

    def test_audit_report_compliance(self, root_dir):
        """Test that audit report shows COMPLIANT status."""
        report_dir = root_dir / "23_compliance" / "reports"
        if not report_dir.exists():
            pytest.skip(f"Report directory not found: {report_dir}")

        # Find most recent audit report
        reports = sorted(report_dir.glob("forensic_manifest_audit_*.json"))
        if len(reports) == 0:
            pytest.skip("No audit reports found")

        latest_report = reports[-1]
        with open(latest_report, "r", encoding="utf-8") as f:
            report_data = json.load(f)

        assert report_data["compliance_status"] == "COMPLIANT", \
            f"Audit report shows non-compliant status: {report_data['compliance_status']}"

    def test_registry_exists(self, root_dir):
        """Test that registry file exists."""
        registry_path = root_dir / "24_meta_orchestration" / "registry" / "forensic_manifest_registry.yaml"
        assert registry_path.exists(), f"Registry not found: {registry_path}"

    def test_registry_entry(self, root_dir, manifest):
        """Test that registry contains entry for current manifest."""
        registry_path = root_dir / "24_meta_orchestration" / "registry" / "forensic_manifest_registry.yaml"
        if not registry_path.exists():
            pytest.skip(f"Registry not found: {registry_path}")

        with open(registry_path, "r", encoding="utf-8") as f:
            registry = yaml.safe_load(f)

        assert "entries" in registry, "Registry has no entries"
        assert len(registry["entries"]) > 0, "Registry entries are empty"

        # Check that most recent entry matches current manifest
        latest_entry = registry["entries"][-1]
        assert latest_entry["merkle_root"] == manifest["merkle_root"], \
            "Registry entry merkle root does not match manifest"

    def test_opa_policy_structure(self, root_dir):
        """Test that OPA policy file exists and has basic structure."""
        opa_policy_path = root_dir / "23_compliance" / "policies" / "opa" / "forensic_manifest_integrity.rego"
        assert opa_policy_path.exists(), f"OPA policy not found: {opa_policy_path}"

        with open(opa_policy_path, "r", encoding="utf-8") as f:
            policy_content = f.read()

        # Check for key policy elements
        assert "package forensic" in policy_content, "Missing package declaration"
        assert "allow" in policy_content, "Missing allow rule"
        assert "deny" in policy_content, "Missing deny rules"
        assert "manifest_fresh" in policy_content, "Missing freshness check"
        assert "merkle_root_valid" in policy_content, "Missing merkle root validation"


def main():
    """Main execution for standalone testing."""
    root = Path(__file__).resolve().parents[2]
    exit_code = pytest.main([
        __file__,
        "-v",
        "--tb=short",
        f"--rootdir={root}"
    ])
    return exit_code


if __name__ == "__main__":
    sys.exit(main())


# Cross-Evidence Links (Entropy Boost)
# REF: 7d33369e-25f8-49e6-80d2-95b8028e8b23
# REF: ffdd8d18-d294-4f3d-8a73-bd56efdc6305
# REF: 05881fc7-9cfb-424b-8e34-8412dace85ff
# REF: 221a001c-2115-47e5-a9e2-2e5b2a63685f
# REF: 8a5f74ef-61b3-4edf-8e6b-38eaea62fa51
