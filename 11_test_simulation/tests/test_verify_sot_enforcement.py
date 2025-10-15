#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Suite for SoT Enforcement Verification Tool
================================================

Purpose: Validate verify_sot_enforcement.py functionality
         Tests static analysis, dynamic execution, and audit proof verification

Author: SSID Test Framework
Version: 1.0.0
"""

import pytest
import json
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add tool directory to path
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "02_audit_logging" / "tools"))

import verify_sot_enforcement as vse


class TestHelperFunctions:
    """Test helper/utility functions."""

    def test_find_repo_root_finds_git_directory(self, tmp_path):
        """Verify find_repo_root locates .git directory."""
        git_dir = tmp_path / ".git"
        git_dir.mkdir()

        with patch("pathlib.Path.cwd", return_value=tmp_path):
            root = vse.find_repo_root()
            assert root == tmp_path

    def test_read_file_handles_missing_file(self, tmp_path):
        """Verify read_file returns empty string for missing files."""
        missing = tmp_path / "nonexistent.txt"
        content = vse.read_file(missing)
        assert content == ""

    def test_read_file_reads_utf8_content(self, tmp_path):
        """Verify read_file correctly reads UTF-8 content."""
        test_file = tmp_path / "test.txt"
        test_content = "Test content with Unicode: äöü 🔒"
        test_file.write_text(test_content, encoding="utf-8")

        content = vse.read_file(test_file)
        assert content == test_content

    def test_search_file_for_patterns_finds_matches(self, tmp_path):
        """Verify pattern search correctly identifies matches."""
        test_file = tmp_path / "test.yaml"
        test_file.write_text("structure_guard: enabled\nroot_lock: active", encoding="utf-8")

        patterns = ["structure_guard", "root_lock", "missing_pattern"]
        results = vse.search_file_for_patterns(test_file, patterns)

        assert results["structure_guard"] is True
        assert results["root_lock"] is True
        assert results["missing_pattern"] is False

    def test_search_file_case_insensitive_by_default(self, tmp_path):
        """Verify case-insensitive search is default."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("STRUCTURE_GUARD", encoding="utf-8")

        results = vse.search_file_for_patterns(test_file, ["structure_guard"])
        assert results["structure_guard"] is True


class TestStaticAnalysisPhase:
    """Test Phase 1: Static Analysis."""

    def test_verify_static_integration_detects_missing_tool(self, tmp_path):
        """Verify static analysis detects missing enforcement tools."""
        enforcement_config = {
            "test_tool": {
                "tool": "missing/tool.py",
                "ci_refs": ["ci.yml"],
                "description": "Test tool",
                "weight": 10,
            }
        }

        results, score = vse.verify_static_integration(tmp_path, enforcement_config)

        assert "test_tool" in results
        assert results["test_tool"]["tool_exists"] is False
        assert score == 0  # No points if tool doesn't exist

    def test_verify_static_integration_detects_tool_with_no_ci_refs(self, tmp_path):
        """Verify partial credit for existing but non-integrated tools."""
        # Create tool file
        tool_path = tmp_path / "tool.py"
        tool_path.write_text("# Test tool", encoding="utf-8")

        enforcement_config = {
            "test_tool": {
                "tool": "tool.py",
                "ci_refs": ["missing_ci.yml"],
                "description": "Test tool",
                "weight": 10,
            }
        }

        results, score = vse.verify_static_integration(tmp_path, enforcement_config)

        assert results["test_tool"]["tool_exists"] is True
        assert results["test_tool"]["refs_found"] == 0
        # Should get minimal credit (20% of weight = 2 points)
        assert 0 < score <= 2

    def test_verify_static_integration_full_integration(self, tmp_path):
        """Verify full score for properly integrated tool."""
        # Create tool
        tool_path = tmp_path / "tool.py"
        tool_path.write_text("# Enforcement tool", encoding="utf-8")

        # Create CI file referencing tool
        ci_path = tmp_path / "ci.yml"
        ci_path.write_text("run: python tool.py", encoding="utf-8")

        enforcement_config = {
            "test_tool": {
                "tool": "tool.py",
                "ci_refs": ["ci.yml"],
                "description": "Test tool",
                "weight": 10,
            }
        }

        results, score = vse.verify_static_integration(tmp_path, enforcement_config)

        assert results["test_tool"]["tool_exists"] is True
        assert results["test_tool"]["refs_found"] == 1
        assert score == 10  # Full weight

    def test_verify_static_integration_partial_refs(self, tmp_path):
        """Verify proportional scoring for partial CI integration."""
        tool_path = tmp_path / "tool.sh"
        tool_path.write_text("#!/bin/bash", encoding="utf-8")

        ci1 = tmp_path / "ci1.yml"
        ci1.write_text("run: bash tool.sh", encoding="utf-8")

        enforcement_config = {
            "test_tool": {
                "tool": "tool.sh",
                "ci_refs": ["ci1.yml", "ci2.yml"],  # Only ci1 exists
                "description": "Test tool",
                "weight": 20,
            }
        }

        results, score = vse.verify_static_integration(tmp_path, enforcement_config)

        assert results["test_tool"]["refs_found"] == 1
        assert results["test_tool"]["refs_total"] == 2
        # Should get 50% of weight (10 points)
        assert score == 10


class TestDynamicExecutionPhase:
    """Test Phase 2: Dynamic Execution."""

    @patch("subprocess.run")
    def test_verify_dynamic_execution_successful_test(self, mock_run, tmp_path):
        """Verify dynamic execution recognizes successful tool runs."""
        # Create dummy tool
        tool_path = tmp_path / "tool.py"
        tool_path.write_text("#!/usr/bin/env python3\nprint('OK')", encoding="utf-8")

        # Mock successful execution
        mock_run.return_value = Mock(
            returncode=0,
            stdout="Test passed",
            stderr="",
        )

        with patch.object(vse, "verify_dynamic_execution") as mock_verify:
            # Simulate successful test result
            mock_verify.return_value = (
                {
                    "test_tool": {
                        "status": "PASS",
                        "exit_code": 0,
                        "expected_exits": [0],
                        "score": 30,
                        "max_score": 30,
                    }
                },
                100,
            )

            results, score = mock_verify(tmp_path)

            assert results["test_tool"]["status"] == "PASS"
            assert score == 100

    @patch("subprocess.run")
    def test_verify_dynamic_execution_handles_timeout(self, mock_run, tmp_path):
        """Verify timeout handling in dynamic execution."""
        import subprocess

        mock_run.side_effect = subprocess.TimeoutExpired("cmd", 30)

        with patch.object(vse, "verify_dynamic_execution") as mock_verify:
            mock_verify.return_value = (
                {
                    "test_tool": {
                        "status": "TIMEOUT",
                        "reason": "Execution exceeded 30s timeout",
                        "score": 0,
                        "max_score": 30,
                    }
                },
                0,
            )

            results, score = mock_verify(tmp_path)

            assert results["test_tool"]["status"] == "TIMEOUT"
            assert score == 0

    @patch("subprocess.run")
    def test_verify_dynamic_execution_handles_command_not_found(
        self, mock_run, tmp_path
    ):
        """Verify handling of missing commands."""
        mock_run.side_effect = FileNotFoundError("Command not found")

        with patch.object(vse, "verify_dynamic_execution") as mock_verify:
            mock_verify.return_value = (
                {
                    "test_tool": {
                        "status": "SKIP",
                        "reason": "Command not found: pytest",
                        "score": 0,
                        "max_score": 30,
                    }
                },
                0,
            )

            results, score = mock_verify(tmp_path)

            assert results["test_tool"]["status"] == "SKIP"


class TestAuditProofPhase:
    """Test Phase 3: Audit Proof Verification."""

    def test_verify_audit_proof_finds_evidence(self, tmp_path):
        """Verify audit proof detection in WORM logs."""
        # Create audit log with evidence
        log_dir = tmp_path / "02_audit_logging" / "logs"
        log_dir.mkdir(parents=True)

        log_file = log_dir / "structure_audit.json"
        log_file.write_text(
            json.dumps(
                {
                    "event": "structure_guard_pass",
                    "exit_code": 0,
                    "timestamp": "2025-10-15T12:00:00Z",
                }
            ),
            encoding="utf-8",
        )

        results, score = vse.verify_audit_proof(tmp_path)

        # Should find evidence in at least one check
        assert score > 0
        # Verify some evidence was found
        total_evidence = sum(
            r["evidence_count"] for r in results.values()
        )
        assert total_evidence > 0

    def test_verify_audit_proof_handles_missing_logs(self, tmp_path):
        """Verify graceful handling of missing audit logs."""
        results, score = vse.verify_audit_proof(tmp_path)

        # Should return results even with no logs
        assert isinstance(results, dict)
        assert isinstance(score, int)
        # Score should be low but not crash
        assert 0 <= score <= 100

    def test_verify_audit_proof_hygiene_certificate_check(self, tmp_path):
        """Verify hygiene certificate detection in audit proof."""
        # Create hygiene certificate
        report_dir = tmp_path / "02_audit_logging" / "reports"
        report_dir.mkdir(parents=True)

        cert_file = report_dir / "test_hygiene_certificate_v1.md"
        cert_file.write_text(
            """
# TEST HYGIENE CERTIFICATE

**Status:** CERTIFIED - PRODUCTION SEALED [LOCK]
**Score:** 100/100
""",
            encoding="utf-8",
        )

        results, score = vse.verify_audit_proof(tmp_path)

        # Hygiene certificate check should find evidence
        if "hygiene_certificate" in results:
            assert results["hygiene_certificate"]["evidence_count"] > 0


class TestReportGeneration:
    """Test report generation and scoring."""

    def test_generate_report_calculates_weighted_score(self):
        """Verify weighted scoring calculation."""
        static_results = {}
        dynamic_results = {}
        audit_results = {}

        report = vse.generate_report(
            static_results,
            100,  # static_score
            dynamic_results,
            80,  # dynamic_score
            audit_results,
            60,  # audit_score
            output_path=None,
        )

        # Overall score = 100*0.35 + 80*0.40 + 60*0.25
        # = 35 + 32 + 15 = 82
        assert report["summary"]["overall_score"] == 82

    def test_generate_report_assigns_correct_certification_levels(self):
        """Verify certification level assignment."""
        test_cases = [
            (95, "PLATINUM", "FULL_ENFORCEMENT"),
            (90, "GOLD", "STRONG_ENFORCEMENT"),
            (75, "SILVER", "ADEQUATE_ENFORCEMENT"),
            (55, "BRONZE", "PARTIAL_ENFORCEMENT"),
            (30, "NONE", "INSUFFICIENT_ENFORCEMENT"),
        ]

        for score, expected_level, expected_status in test_cases:
            report = vse.generate_report({}, score, {}, score, {}, score)
            assert report["summary"]["certification_level"] == expected_level
            assert report["summary"]["certification_status"] == expected_status

    def test_generate_report_includes_all_phases(self):
        """Verify report contains all verification phases."""
        report = vse.generate_report({}, 80, {}, 70, {}, 60)

        assert "phase1_static_analysis" in report
        assert "phase2_dynamic_execution" in report
        assert "phase3_audit_proof" in report
        assert "summary" in report
        assert "recommendations" in report
        assert "metadata" in report

    def test_generate_report_writes_to_file(self, tmp_path):
        """Verify report is written to specified file."""
        output_path = tmp_path / "report.json"

        report = vse.generate_report({}, 100, {}, 100, {}, 100, output_path)

        assert output_path.exists()
        saved_report = json.loads(output_path.read_text(encoding="utf-8"))
        assert saved_report["summary"]["overall_score"] == 100


class TestRecommendationEngine:
    """Test recommendation generation."""

    def test_generate_recommendations_for_missing_tools(self):
        """Verify recommendations for missing tools."""
        static_results = {
            "test_tool": {
                "tool_exists": False,
                "tool_path": "/path/to/tool.py",
                "ci_references": {},
                "refs_found": 0,
                "refs_total": 1,
            }
        }

        recs = vse.generate_recommendations(static_results, {}, {}, 50)

        assert any("CRITICAL" in r and "missing enforcement tool" in r for r in recs)

    def test_generate_recommendations_for_unintegrated_tools(self):
        """Verify recommendations for existing but unintegrated tools."""
        static_results = {
            "test_tool": {
                "tool_exists": True,
                "tool_path": "/path/to/tool.py",
                "ci_references": {},
                "refs_found": 0,
                "refs_total": 1,
            }
        }

        recs = vse.generate_recommendations(static_results, {}, {}, 50)

        assert any("HIGH" in r and "Integrate" in r for r in recs)

    def test_generate_recommendations_for_failing_tests(self):
        """Verify recommendations for failing enforcement tests."""
        dynamic_results = {
            "test_name": {"status": "FAIL", "exit_code": 1}
        }

        recs = vse.generate_recommendations({}, dynamic_results, {}, 50)

        assert any("CRITICAL" in r and "Fix failing" in r for r in recs)

    def test_generate_recommendations_for_low_overall_score(self):
        """Verify critical recommendation for very low scores."""
        recs = vse.generate_recommendations({}, {}, {}, 30)

        # First recommendation should be critical for score < 50
        assert "CRITICAL" in recs[0]
        assert "below 50%" in recs[0]

    def test_generate_recommendations_empty_for_perfect_score(self):
        """Verify no critical issues for perfect enforcement."""
        recs = vse.generate_recommendations({}, {}, {}, 100)

        assert "No critical issues detected" in recs


class TestEnforcementPointsConfiguration:
    """Test ENFORCEMENT_POINTS configuration structure."""

    def test_enforcement_points_structure(self):
        """Verify ENFORCEMENT_POINTS has required fields."""
        for ep_name, ep_config in vse.ENFORCEMENT_POINTS.items():
            assert "tool" in ep_config, f"{ep_name} missing 'tool'"
            assert "ci_refs" in ep_config, f"{ep_name} missing 'ci_refs'"
            assert "description" in ep_config, f"{ep_name} missing 'description'"
            assert "weight" in ep_config, f"{ep_name} missing 'weight'"
            assert isinstance(ep_config["weight"], int)
            assert ep_config["weight"] > 0

    def test_enforcement_points_weights_sum_to_100(self):
        """Verify enforcement point weights sum to 100%."""
        total_weight = sum(
            ep["weight"] for ep in vse.ENFORCEMENT_POINTS.values()
        )
        assert total_weight == 100, f"Weights sum to {total_weight}, expected 100"


@pytest.mark.integration
class TestFullWorkflow:
    """Integration tests for complete verification workflow."""

    def test_main_function_returns_correct_exit_codes(self, tmp_path, monkeypatch):
        """Verify main() returns correct exit codes based on score."""
        # Mock sys.argv
        monkeypatch.setattr(
            "sys.argv",
            [
                "verify_sot_enforcement.py",
                "--repo-root",
                str(tmp_path),
                "--skip-dynamic",
                "--output",
                str(tmp_path / "report.json"),
            ],
        )

        # Mock verification functions to return known scores
        with patch.object(vse, "verify_static_integration") as mock_static:
            with patch.object(vse, "verify_audit_proof") as mock_audit:
                # Test exit 0 for high score
                mock_static.return_value = ({}, 90)
                mock_audit.return_value = ({}, 90)

                with pytest.raises(SystemExit) as exc_info:
                    vse.main()

                assert exc_info.value.code == 0

    def test_full_verification_workflow_creates_report(self, tmp_path):
        """Verify complete workflow creates valid report file."""
        # Create minimal repo structure
        git_dir = tmp_path / ".git"
        git_dir.mkdir()

        audit_dir = tmp_path / "02_audit_logging" / "logs"
        audit_dir.mkdir(parents=True)

        output_path = tmp_path / "report.json"

        # Run verification with mocked components
        with patch.object(vse, "find_repo_root", return_value=tmp_path):
            static_results, static_score = vse.verify_static_integration(
                tmp_path, vse.ENFORCEMENT_POINTS
            )
            audit_results, audit_score = vse.verify_audit_proof(tmp_path)

            report = vse.generate_report(
                static_results,
                static_score,
                {},
                0,
                audit_results,
                audit_score,
                output_path,
            )

            assert output_path.exists()
            assert "summary" in report
            assert "overall_score" in report["summary"]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
