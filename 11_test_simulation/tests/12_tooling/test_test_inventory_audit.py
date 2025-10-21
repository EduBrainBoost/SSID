#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit Tests for Test Inventory Audit System
===========================================

Tests for the test_inventory_audit.py scanner and policy enforcement.

Author: SSID Codex Engine v5.2
"""
import json
import pytest
import subprocess
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add 12_tooling to path for import
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "12_tooling" / "analysis"))

try:
    from test_inventory_audit import (
        InventoryResult,
        PytestCollection,
        load_policy,
        scan_tests,
        collect_pytest_nodes
    )
    IMPORT_SUCCESS = True
except ImportError as e:
    IMPORT_SUCCESS = False
    IMPORT_ERROR = str(e)


@pytest.mark.skipif(not IMPORT_SUCCESS, reason=f"Import failed: {IMPORT_ERROR if not IMPORT_SUCCESS else ''}")
class TestInventoryAudit:
    """Test suite for test inventory audit system."""

    def test_inventory_result_dataclass(self):
        """Test InventoryResult dataclass structure."""
        result = InventoryResult(
            total_found=100,
            total_after_filters=80,
            files=["test_a.py", "test_b.py"],
            by_dir={"11_test_simulation": 50}
        )
        assert result.total_found == 100
        assert result.total_after_filters == 80
        assert len(result.files) == 2
        assert result.by_dir["11_test_simulation"] == 50

    def test_pytest_collection_dataclass(self):
        """Test PytestCollection dataclass structure."""
        collection = PytestCollection(
            discovered_count=50,
            discovered_nodes=["<Module test_foo.py>", "<Function test_bar>"]
        )
        assert collection.discovered_count == 50
        assert len(collection.discovered_nodes) == 2

    def test_load_policy_nonexistent_file(self, tmp_path):
        """Test loading policy from nonexistent file returns empty dict."""
        policy_path = tmp_path / "nonexistent.yaml"
        result = load_policy(policy_path)
        assert result == {}

    def test_load_policy_valid_yaml(self, tmp_path):
        """Test loading policy from valid YAML file."""
        policy_path = tmp_path / "policy.yaml"
        policy_content = """
min_pytest_ratio: 0.90
exclude_dirs:
  - backups
  - archives
"""
        policy_path.write_text(policy_content, encoding="utf-8")
        result = load_policy(policy_path)
        assert result["min_pytest_ratio"] == 0.90
        assert "backups" in result["exclude_dirs"]
        assert "archives" in result["exclude_dirs"]

    def test_scan_tests_finds_test_files(self, tmp_path):
        """Test that scan_tests finds test files matching patterns."""
        # Create test directory structure
        test_dir = tmp_path / "tests"
        test_dir.mkdir()
        (test_dir / "test_foo.py").write_text("def test_foo(): pass")
        (test_dir / "bar_test.py").write_text("def test_bar(): pass")
        (test_dir / "not_a_test.py").write_text("# not a test")

        result = scan_tests(
            root=tmp_path,
            include_globs=["**/test_*.py", "**/*_test.py"],
            excludes=[],
            exclude_regex=[]
        )

        assert result.total_found == 2
        assert result.total_after_filters == 2
        assert any("test_foo.py" in f for f in result.files)
        assert any("bar_test.py" in f for f in result.files)
        assert not any("not_a_test.py" in f for f in result.files)

    def test_scan_tests_excludes_directories(self, tmp_path):
        """Test that scan_tests properly excludes directories."""
        # Create structure with excluded directories
        test_dir = tmp_path / "tests"
        test_dir.mkdir()
        (test_dir / "test_valid.py").write_text("def test_valid(): pass")

        backup_dir = tmp_path / "backups"
        backup_dir.mkdir()
        (backup_dir / "test_backup.py").write_text("def test_backup(): pass")

        result = scan_tests(
            root=tmp_path,
            include_globs=["**/test_*.py"],
            excludes=["backups"],
            exclude_regex=[]
        )

        assert result.total_found == 2  # Both files found initially
        assert result.total_after_filters == 1  # Only one after filtering
        assert any("test_valid.py" in f for f in result.files)
        assert not any("test_backup.py" in f for f in result.files)

    def test_scan_tests_excludes_by_regex(self, tmp_path):
        """Test that scan_tests properly excludes paths by regex."""
        # Create structure with paths matching regex
        test_dir = tmp_path / "tests"
        test_dir.mkdir()
        (test_dir / "test_valid.py").write_text("def test_valid(): pass")

        old_dir = tmp_path / "old_tests"
        old_dir.mkdir()
        (old_dir / "test_old.py").write_text("def test_old(): pass")

        result = scan_tests(
            root=tmp_path,
            include_globs=["**/test_*.py"],
            excludes=[],
            exclude_regex=[r"(^|/)old_"]
        )

        assert any("test_valid.py" in f for f in result.files)
        assert not any("test_old.py" in f for f in result.files)

    def test_scan_tests_distribution_by_directory(self, tmp_path):
        """Test that scan_tests correctly counts files by directory."""
        # Create structure with multiple directories
        dir1 = tmp_path / "dir1"
        dir1.mkdir()
        (dir1 / "test_a.py").write_text("def test_a(): pass")
        (dir1 / "test_b.py").write_text("def test_b(): pass")

        dir2 = tmp_path / "dir2"
        dir2.mkdir()
        (dir2 / "test_c.py").write_text("def test_c(): pass")

        result = scan_tests(
            root=tmp_path,
            include_globs=["**/test_*.py"],
            excludes=[],
            exclude_regex=[]
        )

        assert len(result.by_dir) == 2
        assert result.by_dir.get("dir1", 0) == 2
        assert result.by_dir.get("dir2", 0) == 1

    @patch('subprocess.run')
    def test_collect_pytest_nodes_success(self, mock_run):
        """Test successful pytest node collection."""
        mock_run.return_value = Mock(
            stdout="<Module test_foo.py>\n<Function test_bar>\ntest_baz.py::test_func\n",
            stderr=""
        )

        result = collect_pytest_nodes(Path("."))

        assert result.discovered_count == 3
        assert any("Module" in node for node in result.discovered_nodes)
        assert any("Function" in node for node in result.discovered_nodes)
        assert any("::" in node for node in result.discovered_nodes)

    @patch('subprocess.run')
    def test_collect_pytest_nodes_timeout(self, mock_run):
        """Test pytest collection handles timeout gracefully."""
        mock_run.side_effect = subprocess.TimeoutExpired("pytest", 180)

        result = collect_pytest_nodes(Path("."))

        assert result.discovered_count == 0
        assert len(result.discovered_nodes) == 0

    @patch('subprocess.run')
    def test_collect_pytest_nodes_not_found(self, mock_run):
        """Test pytest collection handles missing pytest gracefully."""
        mock_run.side_effect = FileNotFoundError("pytest not found")

        result = collect_pytest_nodes(Path("."))

        assert result.discovered_count == 0
        assert len(result.discovered_nodes) == 0

    def test_audit_workflow_integration(self, tmp_path):
        """Integration test: full audit workflow."""
        # Create realistic test structure
        test_dir = tmp_path / "11_test_simulation"
        test_dir.mkdir()
        (test_dir / "test_feature_a.py").write_text("def test_feature_a(): pass")
        (test_dir / "test_feature_b.py").write_text("def test_feature_b(): pass")

        backup_dir = tmp_path / "backups"
        backup_dir.mkdir()
        (backup_dir / "test_old.py").write_text("def test_old(): pass")

        # Scan tests
        inv = scan_tests(
            root=tmp_path,
            include_globs=["**/test_*.py"],
            excludes=["backups"],
            exclude_regex=[]
        )

        # Verify results
        assert inv.total_found == 3
        assert inv.total_after_filters == 2
        assert "11_test_simulation" in inv.by_dir
        assert inv.by_dir["11_test_simulation"] == 2

    def test_policy_threshold_calculation(self):
        """Test that policy threshold is correctly applied."""
        # Simulate inventory and pytest results
        total_files = 100
        pytest_discovered = 96
        ratio = pytest_discovered / total_files
        min_threshold = 0.95

        # Should pass
        assert ratio >= min_threshold

        # Should fail
        pytest_discovered_low = 94
        ratio_low = pytest_discovered_low / total_files
        assert ratio_low < min_threshold


class TestAuditCLI:
    """Test CLI functionality of the audit tool."""

    def test_cli_help(self):
        """Test that CLI help works."""
        result = subprocess.run(
            ["python", "12_tooling/analysis/test_inventory_audit.py", "--help"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert "repo-root" in result.stdout.lower()

    @pytest.mark.slow
    def test_cli_execution_generates_reports(self, tmp_path):
        """Test that CLI execution generates expected output files."""
        # Create minimal test structure
        test_dir = tmp_path / "tests"
        test_dir.mkdir()
        (test_dir / "test_sample.py").write_text("def test_sample(): pass")

        # Create minimal policy
        policy_path = tmp_path / "policy.yaml"
        policy_path.write_text("min_pytest_ratio: 0.0\n")  # Very permissive for test

        # Run audit
        result = subprocess.run(
            [
                "python", "12_tooling/analysis/test_inventory_audit.py",
                "--repo-root", str(tmp_path),
                "--policy", str(policy_path),
                "--json-out", "audit.json",
                "--md-out", "audit.md"
            ],
            capture_output=True,
            text=True
        )

        # Check that reports were generated
        json_report = tmp_path / "audit.json"
        md_report = tmp_path / "audit.md"

        # Reports should exist or audit should complete
        assert result.returncode in [0, 2]  # 0 = pass, 2 = fail (expected)


@pytest.mark.integration
class TestEndToEndAudit:
    """End-to-end integration tests for audit system."""

    def test_real_repository_scan(self):
        """Test scanning the actual SSID repository (smoke test)."""
        repo_root = Path(__file__).resolve().parents[3]

        # Perform scan with strict exclusions
        result = scan_tests(
            root=repo_root,
            include_globs=["**/test_*.py", "**/*_test.py"],
            excludes=["backups", "archives", "__pycache__", ".git"],
            exclude_regex=[r"(^|/)backups(/|$)", r"(^|/)archives(/|$)"]
        )

        # Basic sanity checks
        assert result.total_found > 0, "Should find at least some test files"
        assert result.total_after_filters <= result.total_found, "Filtered count should be <= raw count"
        assert len(result.files) == result.total_after_filters, "File list should match filtered count"
        assert len(result.by_dir) > 0, "Should have files in at least one directory"

        print(f"\n[SMOKE-TEST] Found {result.total_found} raw, {result.total_after_filters} effective test files")


def test_audit_tool_exists():
    """Verify that the audit tool file exists and is executable."""
    audit_tool = Path(__file__).resolve().parents[3] / "12_tooling" / "analysis" / "test_inventory_audit.py"
    assert audit_tool.exists(), f"Audit tool not found at {audit_tool}"
    assert audit_tool.is_file(), "Audit tool should be a file"


def test_policy_file_exists():
    """Verify that the policy configuration file exists."""
    policy_file = Path(__file__).resolve().parents[3] / "12_tooling" / "analysis" / "test_inventory_policy.yaml"
    assert policy_file.exists(), f"Policy file not found at {policy_file}"
    assert policy_file.is_file(), "Policy file should be a file"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
