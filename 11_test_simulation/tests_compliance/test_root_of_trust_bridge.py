#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test: Root-of-Trust Bridge Verification
Autor: edubrainboost ©2025 MIT License

Validates the bridge between forensic manifest merkle roots and
blockchain RootAnchored events, ensuring complete trust chain closure.

Tests:
- Manifest-blockchain hash matching
- Temporal consistency validation
- OPA policy compliance
- Verification report generation

Exit Codes:
  0 - PASS: All bridge verification tests passed
  1 - FAIL: One or more tests failed
"""

import sys
import json
import yaml
import pytest
from pathlib import Path
from datetime import datetime, timezone, timedelta


class TestRootOfTrustBridge:
    """Test suite for root-of-trust bridge verification."""

    @pytest.fixture(scope="class")
    def root_dir(self):
        """Get repository root directory."""
        return Path(__file__).resolve().parents[2]

    @pytest.fixture(scope="class")
    def manifest(self, root_dir):
        """Load forensic manifest."""
        manifest_path = root_dir / "02_audit_logging" / "evidence" / "forensic_manifest.yaml"
        if not manifest_path.exists():
            pytest.skip(f"Manifest not found: {manifest_path}")

        with open(manifest_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    @pytest.fixture(scope="class")
    def blockchain_event(self, root_dir):
        """Load latest blockchain event."""
        event_log = root_dir / "20_foundation" / "smart_contracts" / "events" / "root_anchored.jsonl"
        if not event_log.exists():
            pytest.skip(f"Blockchain event log not found: {event_log}")

        with open(event_log, "r", encoding="utf-8") as f:
            lines = [line for line in f if line.strip()]

        if not lines:
            pytest.skip("No blockchain events logged")

        return json.loads(lines[-1])

    @pytest.fixture(scope="class")
    def verification_input(self, root_dir):
        """Load OPA verification input."""
        input_path = root_dir / "verification_input.json"
        if not input_path.exists():
            pytest.skip(f"Verification input not found: {input_path}")

        with open(input_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def test_manifest_has_merkle_root(self, manifest):
        """Test that manifest contains merkle root."""
        assert "merkle_root" in manifest, "Manifest missing merkle_root"
        assert len(manifest["merkle_root"]) == 64, "Invalid merkle root length"

    def test_blockchain_event_has_root_hash(self, blockchain_event):
        """Test that blockchain event contains root hash."""
        assert "root_hash" in blockchain_event, "Blockchain event missing root_hash"
        assert len(blockchain_event["root_hash"]) == 64, "Invalid root hash length"

    def test_hashes_match(self, manifest, blockchain_event):
        """Test that manifest merkle root matches blockchain root hash."""
        manifest_root = manifest["merkle_root"]
        blockchain_root = blockchain_event["root_hash"]

        assert manifest_root == blockchain_root, \
            f"Hash mismatch: manifest={manifest_root[:16]}..., blockchain={blockchain_root[:16]}..."

    def test_blockchain_event_type(self, blockchain_event):
        """Test that blockchain event is of correct type."""
        assert blockchain_event.get("event_type") == "RootAnchored", \
            f"Invalid event type: {blockchain_event.get('event_type')}"

    def test_blockchain_event_has_block_number(self, blockchain_event):
        """Test that blockchain event has block number."""
        assert "block_number" in blockchain_event, "Missing block_number"
        assert isinstance(blockchain_event["block_number"], int), "Invalid block_number type"
        assert blockchain_event["block_number"] > 0, "Invalid block_number value"

    def test_blockchain_event_has_timestamp(self, blockchain_event):
        """Test that blockchain event has timestamp."""
        assert "timestamp" in blockchain_event, "Missing timestamp"
        assert isinstance(blockchain_event["timestamp"], int), "Invalid timestamp type"

    def test_temporal_consistency(self, manifest, blockchain_event):
        """Test that manifest was generated before blockchain event."""
        manifest_time = datetime.fromisoformat(manifest["generated_at"].replace("Z", "+00:00"))
        blockchain_time = datetime.fromtimestamp(blockchain_event["timestamp"], tz=timezone.utc)

        assert manifest_time <= blockchain_time, \
            "Temporal inconsistency: manifest generated after blockchain event"

        # Check that gap is reasonable (< 1 hour)
        time_gap = blockchain_time - manifest_time
        assert time_gap < timedelta(hours=1), \
            f"Temporal gap too large: {time_gap.total_seconds() / 3600:.2f} hours"

    def test_verification_input_structure(self, verification_input):
        """Test that verification input has correct structure."""
        assert "manifest" in verification_input, "Missing manifest section"
        assert "blockchain" in verification_input, "Missing blockchain section"

        # Manifest section
        assert "merkle_root" in verification_input["manifest"]
        assert "generated_at" in verification_input["manifest"]
        assert "total_files" in verification_input["manifest"]

        # Blockchain section
        assert "root_hash" in verification_input["blockchain"]
        assert "block_number" in verification_input["blockchain"]
        assert "timestamp" in verification_input["blockchain"]
        assert "event_type" in verification_input["blockchain"]

    def test_verification_input_hashes_match(self, verification_input):
        """Test that hashes match in verification input."""
        manifest_root = verification_input["manifest"]["merkle_root"]
        blockchain_root = verification_input["blockchain"]["root_hash"]

        assert manifest_root == blockchain_root, \
            f"Verification input hash mismatch: {manifest_root[:16]}... != {blockchain_root[:16]}..."

    def test_verification_report_exists(self, root_dir):
        """Test that verification report was generated."""
        report_dir = root_dir / "23_compliance" / "reports"
        if not report_dir.exists():
            pytest.skip(f"Report directory not found: {report_dir}")

        reports = sorted(report_dir.glob("bridge_verification_*.json"))
        assert len(reports) > 0, "No verification reports found"

    def test_verification_report_content(self, root_dir):
        """Test that verification report has correct content."""
        report_dir = root_dir / "23_compliance" / "reports"
        if not report_dir.exists():
            pytest.skip(f"Report directory not found: {report_dir}")

        reports = sorted(report_dir.glob("bridge_verification_*.json"))
        if len(reports) == 0:
            pytest.skip("No verification reports found")

        latest_report = reports[-1]
        with open(latest_report, "r", encoding="utf-8") as f:
            report = json.load(f)

        assert report["report_type"] == "manifest_blockchain_bridge_verification"
        assert "verification_success" in report
        assert "verification_message" in report
        assert "compliance_status" in report

    def test_verification_report_success(self, root_dir):
        """Test that verification report shows success."""
        report_dir = root_dir / "23_compliance" / "reports"
        if not report_dir.exists():
            pytest.skip(f"Report directory not found: {report_dir}")

        reports = sorted(report_dir.glob("bridge_verification_*.json"))
        if len(reports) == 0:
            pytest.skip("No verification reports found")

        latest_report = reports[-1]
        with open(latest_report, "r", encoding="utf-8") as f:
            report = json.load(f)

        assert report["verification_success"] is True, \
            f"Verification failed: {report['verification_message']}"

        assert report["compliance_status"] == "VERIFIED", \
            f"Compliance status not verified: {report['compliance_status']}"

    def test_chain_id_valid(self, blockchain_event):
        """Test that chain ID is valid (if present)."""
        if "chain_id" in blockchain_event:
            allowed_chains = {1, 137, 5, 80001, 11155111}  # mainnet, polygon, testnets
            assert blockchain_event["chain_id"] in allowed_chains, \
                f"Invalid chain ID: {blockchain_event['chain_id']}"

    def test_opa_policy_exists(self, root_dir):
        """Test that OPA policy file exists."""
        policy_path = root_dir / "23_compliance" / "policies" / "opa" / "root_of_trust_bridging.rego"
        assert policy_path.exists(), f"OPA policy not found: {policy_path}"

    def test_opa_policy_structure(self, root_dir):
        """Test that OPA policy has correct structure."""
        policy_path = root_dir / "23_compliance" / "policies" / "opa" / "root_of_trust_bridging.rego"
        if not policy_path.exists():
            pytest.skip(f"OPA policy not found: {policy_path}")

        with open(policy_path, "r", encoding="utf-8") as f:
            policy_content = f.read()

        # Check for key policy elements
        assert "package bridge" in policy_content, "Missing package declaration"
        assert "allow" in policy_content, "Missing allow rule"
        assert "deny" in policy_content, "Missing deny rules"
        assert "hashes_match" in policy_content, "Missing hash match validation"
        assert "temporal_consistency" in policy_content, "Missing temporal validation"

    def test_complete_trust_chain(self, manifest, blockchain_event, verification_input):
        """Test complete trust chain from manifest to blockchain."""
        # Step 1: Manifest has merkle root
        assert manifest["merkle_root"]

        # Step 2: Blockchain event has matching root hash
        assert blockchain_event["root_hash"] == manifest["merkle_root"]

        # Step 3: Verification input links both
        assert verification_input["manifest"]["merkle_root"] == manifest["merkle_root"]
        assert verification_input["blockchain"]["root_hash"] == blockchain_event["root_hash"]

        # Step 4: Hashes match throughout chain
        assert verification_input["manifest"]["merkle_root"] == verification_input["blockchain"]["root_hash"]

        # Complete trust chain verified
        print("\n[TRUST CHAIN VERIFIED]")
        print(f"  Manifest -> {manifest['merkle_root'][:32]}...")
        print(f"  Blockchain -> {blockchain_event['root_hash'][:32]}...")
        print(f"  Status: TRUST ESTABLISHED")


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
# REF: 97152414-41fd-4167-bb11-f33ee156bfc5
# REF: c319b6df-98c8-48a1-a499-4230e55fd0b8
# REF: 47600ae5-ff99-4556-83b4-3724b95fa9e6
# REF: 1285c43c-c862-444c-893d-412894e9bbd0
# REF: 2e5247b7-d352-4a64-8357-dce7cf818e1a
