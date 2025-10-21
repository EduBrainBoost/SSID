#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit Tests: Test Coverage Booster
Author: SSID Codex Engine ©2025 MIT License
"""

import pytest
import sys
import os
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

def test_coverage_booster_exists():
    """Test that coverage booster tool exists."""
    tool_path = Path(__file__).parents[2] / "12_tooling" / "quality" / "test_coverage_booster.py"
    assert tool_path.exists(), f"Tool not found: {tool_path}"

def test_coverage_booster_executes():
    """Test that coverage booster executes successfully."""
    import subprocess

    tool_path = Path(__file__).parents[2] / "12_tooling" / "quality" / "test_coverage_booster.py"

    result = subprocess.run(
        [sys.executable, str(tool_path)],
        capture_output=True,
        text=True,
        timeout=60
    )

    # Advisory tool always returns 0
    assert result.returncode == 0, f"Unexpected exit code: {result.returncode}"
    assert "SSID Test Coverage Booster" in result.stdout

def test_coverage_booster_json_output():
    """Test that JSON output mode works."""
    import subprocess

    tool_path = Path(__file__).parents[2] / "12_tooling" / "quality" / "test_coverage_booster.py"

    result = subprocess.run(
        [sys.executable, str(tool_path), "--emit-json"],
        capture_output=True,
        text=True,
        timeout=60
    )

    assert result.returncode == 0

    # Parse JSON output
    report = json.loads(result.stdout)

    assert "timestamp" in report
    assert "tool" in report
    assert report["tool"] == "test_coverage_booster"
    assert "summary" in report
    assert "recommendations" in report

def test_coverage_report_structure():
    """Test coverage report has expected structure."""
    import subprocess

    tool_path = Path(__file__).parents[2] / "12_tooling" / "quality" / "test_coverage_booster.py"

    result = subprocess.run(
        [sys.executable, str(tool_path), "--emit-json"],
        capture_output=True,
        text=True,
        timeout=60
    )

    report = json.loads(result.stdout)

    # Check summary fields
    assert "total_modules" in report["summary"]
    assert "tested_modules" in report["summary"]
    assert "untested_modules" in report["summary"]
    assert "estimated_coverage_percent" in report["summary"]

    # Check recommendations
    assert "priority_modules" in report["recommendations"]
    assert isinstance(report["recommendations"]["priority_modules"], list)

def test_coverage_report_saved():
    """Test that report is saved to file."""
    import subprocess

    tool_path = Path(__file__).parents[2] / "12_tooling" / "quality" / "test_coverage_booster.py"
    report_dir = Path(__file__).parents[2] / "02_audit_logging" / "reports"

    # Run tool
    result = subprocess.run(
        [sys.executable, str(tool_path)],
        capture_output=True,
        text=True,
        timeout=60
    )

    assert result.returncode == 0

    # Check for latest report
    latest_report = report_dir / "coverage_advice_latest.json"
    assert latest_report.exists(), "Latest report not found"

    # Verify report content
    with open(latest_report, "r", encoding="utf-8") as f:
        report = json.load(f)

    assert report["tool"] == "test_coverage_booster"

def test_coverage_booster_pytest_mode():
    """Test coverage booster with pytest collection."""
    import subprocess

    tool_path = Path(__file__).parents[2] / "12_tooling" / "quality" / "test_coverage_booster.py"

    result = subprocess.run(
        [sys.executable, str(tool_path), "--run-pytest", "--emit-json"],
        capture_output=True,
        text=True,
        timeout=90
    )

    assert result.returncode == 0

    report = json.loads(result.stdout)

    # Pytest info should be present
    assert "pytest_info" in report
    assert report["pytest_info"]["executed"] is True

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
