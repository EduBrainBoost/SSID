#!/usr/bin/env python3
"""
test_verify_hygiene_enforcement.py

Unit tests for verify_hygiene_enforcement.py - Continuous Hygiene Certificate Monitoring

Test Coverage:
--------------
1. File Existence Checks
2. [LOCK] Status Verification
3. Hash Integrity Validation
4. Score Stability Monitoring
5. Temporal Validity Checks
6. Recommendation Generation
7. Integration Tests

Author: SSID Compliance Team
Version: 1.0.0
Created: 2025-10-15
"""

import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Add tools directory to path
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "02_audit_logging" / "tools"))

import verify_hygiene_enforcement as vhe


# --- Test Fixtures ---

@pytest.fixture
def mock_cert_files(tmp_path):
    """Create mock certificate file structure."""
    cert_dir = tmp_path / "02_audit_logging" / "reports"
    cert_dir.mkdir(parents=True)

    registry_dir = tmp_path / "24_meta_orchestration" / "registry"
    registry_dir.mkdir(parents=True)

    badge_dir = tmp_path / "13_ui_layer" / "assets" / "badges"
    badge_dir.mkdir(parents=True)

    log_dir = tmp_path / "02_audit_logging" / "logs"
    log_dir.mkdir(parents=True)

    return {
        "report": cert_dir / "test_hygiene_certificate_v1.md",
        "registry": registry_dir / "test_hygiene_certificate.yaml",
        "badge": badge_dir / "test_hygiene_badge.svg",
        "score_log": log_dir / "test_hygiene_score_log.json",
    }


@pytest.fixture
def valid_certificate_report():
    """Return valid certificate report content."""
    return """
# Test Hygiene Certificate v1.0 [LOCK]

## Certificate Details
Certificate ID: SSID-TH-2025-10-15-001
Valid From: 2025-10-15
Valid To: 2026-10-15
PQC Hash: ef6a26061246349e4a495b71246d33f624dcb8cdb96fe31eb1e12fad7720094e
Algorithm: Dilithium2

## Status: CERTIFIED [LOCK]

This certificate is sealed and immutable.
"""


@pytest.fixture
def valid_registry_yaml():
    """Return valid registry YAML content."""
    return """
certificate:
  id: SSID-TH-2025-10-15-001
  version: "1.0"
  pqc_hash: "ef6a26061246349e4a495b71246d33f624dcb8cdb96fe31eb1e12fad7720094e"
  algorithm: Dilithium2
  status: CERTIFIED
  validity:
    from: "2025-10-15"
    to: "2026-10-15"
"""


@pytest.fixture
def valid_score_log():
    """Return valid score log JSON content."""
    return json.dumps({
        "timestamp": "2025-10-15T12:00:00Z",
        "score": 100,
        "hygiene_score": 100,
        "status": "PASS",
    })


@pytest.fixture
def valid_badge_svg():
    """Return valid badge SVG content."""
    return """
<svg xmlns="http://www.w3.org/2000/svg" width="200" height="40">
  <text x="10" y="25">Test Hygiene: 100/100</text>
</svg>
"""


# --- Test Helper Functions ---

class TestHelperFunctions:
    """Test helper utility functions."""

    def test_read_file_success(self, tmp_path):
        """Test reading file successfully."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content", encoding="utf-8")

        content = vhe.read_file(test_file)
        assert content == "test content"

    def test_read_file_nonexistent(self, tmp_path):
        """Test reading nonexistent file returns empty string."""
        test_file = tmp_path / "nonexistent.txt"
        content = vhe.read_file(test_file)
        assert content == ""

    def test_read_file_permission_error(self, tmp_path):
        """Test reading file with permission error returns empty string."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content", encoding="utf-8")

        with patch("pathlib.Path.read_text", side_effect=PermissionError):
            content = vhe.read_file(test_file)
            assert content == ""


# --- Test Phase 1: File Existence ---

class TestFileExistenceCheck:
    """Test Phase 1: Certificate file existence verification."""

    def test_all_files_exist(self, mock_cert_files, monkeypatch):
        """Test when all certificate files exist and are readable."""
        # Create all files
        for file_path in mock_cert_files.values():
            file_path.write_text("test content", encoding="utf-8")

        # Monkey patch CERTIFICATE_FILES
        monkeypatch.setattr(vhe, "CERTIFICATE_FILES", mock_cert_files)

        results, score = vhe.check_file_existence()

        assert score == 20
        assert len(results) == 4
        for file_result in results.values():
            assert file_result["exists"] is True
            assert file_result["readable"] is True
            assert file_result["status"] == "PASS"

    def test_missing_files(self, mock_cert_files, monkeypatch):
        """Test when certificate files are missing."""
        # Don't create any files
        monkeypatch.setattr(vhe, "CERTIFICATE_FILES", mock_cert_files)

        results, score = vhe.check_file_existence()

        assert score == 0
        for file_result in results.values():
            assert file_result["exists"] is False
            assert file_result["status"] == "FAIL"

    def test_partial_files_exist(self, mock_cert_files, monkeypatch):
        """Test when only some certificate files exist."""
        # Create only report and registry
        mock_cert_files["report"].write_text("content", encoding="utf-8")
        mock_cert_files["registry"].write_text("content", encoding="utf-8")

        monkeypatch.setattr(vhe, "CERTIFICATE_FILES", mock_cert_files)

        results, score = vhe.check_file_existence()

        assert 0 < score < 20  # Partial score
        assert results["report"]["status"] == "PASS"
        assert results["registry"]["status"] == "PASS"
        assert results["badge"]["status"] == "FAIL"
        assert results["score_log"]["status"] == "FAIL"


# --- Test Phase 2: [LOCK] Status ---

class TestLockStatusCheck:
    """Test Phase 2: [LOCK] marker verification."""

    def test_lock_markers_found(self, tmp_path, valid_certificate_report):
        """Test detection of [LOCK] markers in certificate."""
        report_path = tmp_path / "cert.md"
        report_path.write_text(valid_certificate_report, encoding="utf-8")

        results, score = vhe.check_lock_status(report_path)

        assert score == 25
        assert results["lock_count"] >= 1
        assert results["status"] == "PASS"

    def test_no_lock_markers(self, tmp_path):
        """Test when no [LOCK] markers are present."""
        report_path = tmp_path / "cert.md"
        report_path.write_text("Certificate content without lock markers", encoding="utf-8")

        results, score = vhe.check_lock_status(report_path)

        assert score == 0
        assert results["lock_count"] == 0
        assert results["status"] == "FAIL"
        assert "No [LOCK] markers" in results["error"]

    def test_missing_report_file(self, tmp_path):
        """Test when certificate report file is missing."""
        report_path = tmp_path / "nonexistent.md"

        results, score = vhe.check_lock_status(report_path)

        assert score == 0
        assert results["status"] == "FAIL"
        assert "Cannot read" in results["error"]


# --- Test Phase 3: Hash Integrity ---

class TestHashIntegrityCheck:
    """Test Phase 3: PQC hash integrity verification."""

    def test_matching_hashes(self, tmp_path, valid_certificate_report, valid_registry_yaml):
        """Test when hashes match between report and registry."""
        report_path = tmp_path / "cert.md"
        registry_path = tmp_path / "registry.yaml"

        report_path.write_text(valid_certificate_report, encoding="utf-8")
        registry_path.write_text(valid_registry_yaml, encoding="utf-8")

        results, score = vhe.check_hash_integrity(report_path, registry_path)

        assert score == 25
        assert results["hashes_match"] is True
        assert results["status"] == "PASS"
        assert results["report_hash"] == "ef6a26061246349e4a495b71246d33f624dcb8cdb96fe31eb1e12fad7720094e"
        assert results["registry_hash"] == "ef6a26061246349e4a495b71246d33f624dcb8cdb96fe31eb1e12fad7720094e"

    def test_mismatched_hashes(self, tmp_path):
        """Test when hashes do not match."""
        report_content = "PQC Hash: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
        registry_content = "pqc_hash: bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"

        report_path = tmp_path / "cert.md"
        registry_path = tmp_path / "registry.yaml"

        report_path.write_text(report_content, encoding="utf-8")
        registry_path.write_text(registry_content, encoding="utf-8")

        results, score = vhe.check_hash_integrity(report_path, registry_path)

        assert score == 0
        assert results["hashes_match"] is False
        assert results["status"] == "FAIL"
        assert "mismatch" in results["error"]

    def test_missing_hash_in_report(self, tmp_path, valid_registry_yaml):
        """Test when hash is missing from report."""
        report_path = tmp_path / "cert.md"
        registry_path = tmp_path / "registry.yaml"

        report_path.write_text("Certificate without hash", encoding="utf-8")
        registry_path.write_text(valid_registry_yaml, encoding="utf-8")

        results, score = vhe.check_hash_integrity(report_path, registry_path)

        assert score == 0
        assert results["status"] == "FAIL"
        assert results["report_hash"] is None

    def test_missing_hash_in_registry(self, tmp_path, valid_certificate_report):
        """Test when hash is missing from registry."""
        report_path = tmp_path / "cert.md"
        registry_path = tmp_path / "registry.yaml"

        report_path.write_text(valid_certificate_report, encoding="utf-8")
        registry_path.write_text("certificate: {id: test}", encoding="utf-8")

        results, score = vhe.check_hash_integrity(report_path, registry_path)

        assert score == 0
        assert results["status"] == "FAIL"
        assert results["registry_hash"] is None


# --- Test Phase 4: Score Stability ---

class TestScoreStabilityCheck:
    """Test Phase 4: Score log stability verification."""

    def test_perfect_score(self, tmp_path, valid_score_log):
        """Test when score log shows 100/100."""
        score_log_path = tmp_path / "score_log.json"
        score_log_path.write_text(valid_score_log, encoding="utf-8")

        results, score = vhe.check_score_stability(score_log_path)

        assert score == 20
        assert results["latest_score"] == 100
        assert results["score_stable"] is True
        assert results["status"] == "PASS"

    def test_degraded_score(self, tmp_path):
        """Test when score has degraded below 100."""
        degraded_log = json.dumps({"score": 85, "timestamp": "2025-10-15T12:00:00Z"})
        score_log_path = tmp_path / "score_log.json"
        score_log_path.write_text(degraded_log, encoding="utf-8")

        results, score = vhe.check_score_stability(score_log_path)

        assert score < 20  # Proportional to degradation
        assert results["latest_score"] == 85
        assert results["score_stable"] is False
        assert results["status"] == "FAIL"
        assert "degraded" in results["error"]

    def test_multiple_log_entries(self, tmp_path):
        """Test handling of multiple score log entries."""
        log_entries = [
            {"score": 100, "timestamp": "2025-10-14T12:00:00Z"},
            {"score": 100, "timestamp": "2025-10-15T12:00:00Z"},
        ]
        score_log_path = tmp_path / "score_log.json"
        score_log_path.write_text(json.dumps(log_entries), encoding="utf-8")

        results, score = vhe.check_score_stability(score_log_path)

        assert score == 20
        assert results["log_entries"] == 2
        assert results["latest_score"] == 100

    def test_missing_score_log(self, tmp_path):
        """Test when score log file doesn't exist."""
        score_log_path = tmp_path / "nonexistent.json"

        results, score = vhe.check_score_stability(score_log_path)

        assert score == 0
        assert results["status"] == "FAIL"
        assert "does not exist" in results["error"]

    def test_invalid_json(self, tmp_path):
        """Test handling of invalid JSON in score log."""
        score_log_path = tmp_path / "score_log.json"
        score_log_path.write_text("invalid json {{{", encoding="utf-8")

        results, score = vhe.check_score_stability(score_log_path)

        assert score == 0
        assert results["status"] == "FAIL"
        assert "invalid JSON" in results["error"]

    def test_empty_score_log(self, tmp_path):
        """Test when score log is empty array."""
        score_log_path = tmp_path / "score_log.json"
        score_log_path.write_text("[]", encoding="utf-8")

        results, score = vhe.check_score_stability(score_log_path)

        assert score == 0
        assert results["status"] == "FAIL"
        assert "empty" in results["error"]


# --- Test Phase 5: Temporal Validity ---

class TestTemporalValidityCheck:
    """Test Phase 5: Certificate temporal validity verification."""

    def test_valid_certificate(self, tmp_path):
        """Test certificate within valid date range."""
        # Create certificate valid for 1 year from today
        today = datetime.now(timezone.utc).date()
        valid_from = today - timedelta(days=30)
        valid_to = today + timedelta(days=335)

        cert_content = f"""
Certificate
Valid From: {valid_from.isoformat()}
Valid To: {valid_to.isoformat()}
"""
        report_path = tmp_path / "cert.md"
        report_path.write_text(cert_content, encoding="utf-8")

        results, score = vhe.check_temporal_validity(report_path)

        assert score == 10
        assert results["is_valid"] is True
        assert results["status"] == "PASS"

    def test_expired_certificate(self, tmp_path):
        """Test expired certificate."""
        # Create certificate that expired yesterday
        today = datetime.now(timezone.utc).date()
        valid_from = today - timedelta(days=365)
        valid_to = today - timedelta(days=1)

        cert_content = f"""
Certificate
Valid From: {valid_from.isoformat()}
Valid To: {valid_to.isoformat()}
"""
        report_path = tmp_path / "cert.md"
        report_path.write_text(cert_content, encoding="utf-8")

        results, score = vhe.check_temporal_validity(report_path)

        assert score == 0
        assert results["is_valid"] is False
        assert results["status"] == "FAIL"
        assert "expired" in results["error"]

    def test_not_yet_valid_certificate(self, tmp_path):
        """Test certificate not yet valid."""
        # Create certificate valid starting tomorrow
        today = datetime.now(timezone.utc).date()
        valid_from = today + timedelta(days=1)
        valid_to = today + timedelta(days=365)

        cert_content = f"""
Certificate
Valid From: {valid_from.isoformat()}
Valid To: {valid_to.isoformat()}
"""
        report_path = tmp_path / "cert.md"
        report_path.write_text(cert_content, encoding="utf-8")

        results, score = vhe.check_temporal_validity(report_path)

        assert score == 0
        assert results["is_valid"] is False
        assert results["status"] == "FAIL"
        assert "not yet valid" in results["error"]

    def test_missing_validity_dates(self, tmp_path):
        """Test when validity dates are missing."""
        cert_content = "Certificate without validity dates"
        report_path = tmp_path / "cert.md"
        report_path.write_text(cert_content, encoding="utf-8")

        results, score = vhe.check_temporal_validity(report_path)

        assert score == 0
        assert results["status"] == "FAIL"
        assert "extract validity dates" in results["error"]


# --- Test Recommendation Generation ---

class TestRecommendationGeneration:
    """Test recommendation generation based on check results."""

    def test_all_checks_passed(self):
        """Test recommendations when all checks pass."""
        results = {
            "checks": {
                "file_existence": {"results": {
                    "report": {"status": "PASS"},
                    "registry": {"status": "PASS"},
                    "badge": {"status": "PASS"},
                    "score_log": {"status": "PASS"},
                }},
                "lock_status": {"results": {"status": "PASS", "lock_count": 2}},
                "hash_integrity": {"results": {"status": "PASS", "hashes_match": True}},
                "score_stability": {"results": {"status": "PASS", "score_stable": True, "latest_score": 100}},
                "temporal_validity": {"results": {"status": "PASS", "is_valid": True}},
            },
            "summary": {"overall_score": 100},
        }

        recommendations = vhe.generate_recommendations(results)

        assert len(recommendations) == 1
        assert "SUCCESS" in recommendations[0]

    def test_missing_files_recommendation(self):
        """Test recommendations for missing files."""
        results = {
            "checks": {
                "file_existence": {"results": {
                    "report": {"status": "FAIL"},
                    "registry": {"status": "PASS"},
                    "badge": {"status": "PASS"},
                    "score_log": {"status": "PASS"},
                }},
                "lock_status": {"results": {"status": "PASS", "lock_count": 2}},
                "hash_integrity": {"results": {"status": "PASS", "hashes_match": True}},
                "score_stability": {"results": {"status": "PASS", "score_stable": True}},
                "temporal_validity": {"results": {"status": "PASS", "is_valid": True}},
            },
            "summary": {"overall_score": 80},
        }

        recommendations = vhe.generate_recommendations(results)

        assert any("CRITICAL" in rec and "report" in rec for rec in recommendations)

    def test_hash_mismatch_recommendation(self):
        """Test recommendations for hash integrity failure."""
        results = {
            "checks": {
                "file_existence": {"results": {
                    "report": {"status": "PASS"},
                    "registry": {"status": "PASS"},
                    "badge": {"status": "PASS"},
                    "score_log": {"status": "PASS"},
                }},
                "lock_status": {"results": {"status": "PASS", "lock_count": 2}},
                "hash_integrity": {"results": {"status": "FAIL", "hashes_match": False}},
                "score_stability": {"results": {"status": "PASS", "score_stable": True}},
                "temporal_validity": {"results": {"status": "PASS", "is_valid": True}},
            },
            "summary": {"overall_score": 75},
        }

        recommendations = vhe.generate_recommendations(results)

        assert any("hash mismatch" in rec.lower() for rec in recommendations)
        assert any("tampering" in rec.lower() for rec in recommendations)

    def test_score_degradation_recommendation(self):
        """Test recommendations for score degradation."""
        results = {
            "checks": {
                "file_existence": {"results": {
                    "report": {"status": "PASS"},
                    "registry": {"status": "PASS"},
                    "badge": {"status": "PASS"},
                    "score_log": {"status": "PASS"},
                }},
                "lock_status": {"results": {"status": "PASS", "lock_count": 2}},
                "hash_integrity": {"results": {"status": "PASS", "hashes_match": True}},
                "score_stability": {"results": {"status": "FAIL", "score_stable": False, "latest_score": 70}},
                "temporal_validity": {"results": {"status": "PASS", "is_valid": True}},
            },
            "summary": {"overall_score": 80},
        }

        recommendations = vhe.generate_recommendations(results)

        assert any("degraded to 70/100" in rec for rec in recommendations)


# --- Integration Tests ---

class TestIntegration:
    """Integration tests for full verification workflow."""

    def test_run_all_checks_perfect_certificate(
        self, tmp_path, monkeypatch, valid_certificate_report,
        valid_registry_yaml, valid_score_log, valid_badge_svg
    ):
        """Test running all checks on a perfect certificate."""
        # Setup certificate files
        cert_files = {
            "report": tmp_path / "cert.md",
            "registry": tmp_path / "registry.yaml",
            "badge": tmp_path / "badge.svg",
            "score_log": tmp_path / "score_log.json",
        }

        cert_files["report"].write_text(valid_certificate_report, encoding="utf-8")
        cert_files["registry"].write_text(valid_registry_yaml, encoding="utf-8")
        cert_files["badge"].write_text(valid_badge_svg, encoding="utf-8")
        cert_files["score_log"].write_text(valid_score_log, encoding="utf-8")

        monkeypatch.setattr(vhe, "CERTIFICATE_FILES", cert_files)

        results, overall_score = vhe.run_all_checks(verbose=False)

        assert overall_score == 100
        assert results["summary"]["certification_level"] == "PLATINUM"
        assert results["summary"]["certification_status"] == "FULLY_VALID"
        assert results["summary"]["all_checks_passed"] is True

    def test_run_all_checks_degraded_certificate(
        self, tmp_path, monkeypatch, valid_certificate_report,
        valid_registry_yaml, valid_badge_svg
    ):
        """Test running all checks on a degraded certificate."""
        # Setup certificate files with degraded score
        cert_files = {
            "report": tmp_path / "cert.md",
            "registry": tmp_path / "registry.yaml",
            "badge": tmp_path / "badge.svg",
            "score_log": tmp_path / "score_log.json",
        }

        degraded_score = json.dumps({"score": 75})

        cert_files["report"].write_text(valid_certificate_report, encoding="utf-8")
        cert_files["registry"].write_text(valid_registry_yaml, encoding="utf-8")
        cert_files["badge"].write_text(valid_badge_svg, encoding="utf-8")
        cert_files["score_log"].write_text(degraded_score, encoding="utf-8")

        monkeypatch.setattr(vhe, "CERTIFICATE_FILES", cert_files)

        results, overall_score = vhe.run_all_checks(verbose=False)

        assert 70 <= overall_score < 95
        assert results["summary"]["certification_level"] in ["SILVER", "GOLD"]
        assert results["summary"]["all_checks_passed"] is False

    def test_run_all_checks_invalid_certificate(self, tmp_path, monkeypatch):
        """Test running all checks on completely invalid certificate."""
        # Setup missing certificate files
        cert_files = {
            "report": tmp_path / "cert.md",
            "registry": tmp_path / "registry.yaml",
            "badge": tmp_path / "badge.svg",
            "score_log": tmp_path / "score_log.json",
        }

        # Don't create any files
        monkeypatch.setattr(vhe, "CERTIFICATE_FILES", cert_files)

        results, overall_score = vhe.run_all_checks(verbose=False)

        assert overall_score < 50
        assert results["summary"]["certification_level"] == "NONE"
        assert results["summary"]["certification_status"] == "INVALID"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
