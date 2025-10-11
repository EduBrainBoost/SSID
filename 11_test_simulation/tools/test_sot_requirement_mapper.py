#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit Tests: SoT Requirement Mapper
Author: SSID Codex Engine ©2025 MIT License
"""

import pytest
import sys
import os
import json
import yaml
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))


def test_sot_mapper_exists():
    """Test that SoT mapper tool exists."""
    tool_path = Path(__file__).parents[2] / "24_meta_orchestration" / "registry" / "tools" / "sot_requirement_mapper.py"
    assert tool_path.exists(), f"Tool not found: {tool_path}"


def test_sot_mapper_executes():
    """Test that SoT mapper executes successfully."""
    import subprocess

    tool_path = Path(__file__).parents[2] / "24_meta_orchestration" / "registry" / "tools" / "sot_requirement_mapper.py"

    result = subprocess.run(
        [sys.executable, str(tool_path)],
        capture_output=True,
        text=True,
        timeout=60
    )

    # Always returns 0 (evidence generation regardless of compliance)
    assert result.returncode == 0, f"Unexpected exit code: {result.returncode}"
    assert "SSID SoT Requirement Mapper" in result.stdout


def test_sot_mapper_generates_manifest():
    """Test that manifest is generated."""
    import subprocess

    tool_path = Path(__file__).parents[2] / "24_meta_orchestration" / "registry" / "tools" / "sot_requirement_mapper.py"
    manifest_path = Path(__file__).parents[2] / "24_meta_orchestration" / "registry" / "manifests" / "sot_requirement_mapping.yaml"

    # Run tool
    result = subprocess.run(
        [sys.executable, str(tool_path)],
        capture_output=True,
        text=True,
        timeout=60
    )

    assert result.returncode == 0

    # Check manifest exists
    assert manifest_path.exists(), "Manifest not generated"

    # Verify manifest structure
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = yaml.safe_load(f)

    assert "version" in manifest
    assert "timestamp" in manifest
    assert "tool" in manifest
    assert manifest["tool"] == "sot_requirement_mapper"
    assert "requirements" in manifest


def test_sot_mapper_generates_score():
    """Test that score report is generated."""
    import subprocess

    tool_path = Path(__file__).parents[2] / "24_meta_orchestration" / "registry" / "tools" / "sot_requirement_mapper.py"
    score_path = Path(__file__).parents[2] / "02_audit_logging" / "scores" / "sot_requirement_score.json"

    # Run tool
    result = subprocess.run(
        [sys.executable, str(tool_path)],
        capture_output=True,
        text=True,
        timeout=60
    )

    assert result.returncode == 0

    # Check score exists
    assert score_path.exists(), "Score not generated"

    # Verify score structure
    with open(score_path, "r", encoding="utf-8") as f:
        score_report = json.load(f)

    assert "timestamp" in score_report
    assert "tool" in score_report
    assert "score" in score_report

    # Check score fields
    score = score_report["score"]
    assert "score" in score
    assert "total" in score
    assert "satisfied" in score
    assert "unsatisfied" in score
    assert "breakdown" in score

    # Score should be 0-100
    assert 0 <= score["score"] <= 100


def test_sot_mapper_generates_report():
    """Test that markdown report is generated."""
    import subprocess

    tool_path = Path(__file__).parents[2] / "24_meta_orchestration" / "registry" / "tools" / "sot_requirement_mapper.py"
    report_path = Path(__file__).parents[2] / "02_audit_logging" / "reports" / "sot_requirement_report.md"

    # Run tool
    result = subprocess.run(
        [sys.executable, str(tool_path)],
        capture_output=True,
        text=True,
        timeout=60
    )

    assert result.returncode == 0

    # Check report exists
    assert report_path.exists(), "Markdown report not generated"

    # Verify report content
    with open(report_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "# SoT Requirement Mapping Report" in content
    assert "Compliance Score" in content
    assert "MUST" in content or "SHOULD" in content or "HAVE" in content


def test_sot_score_breakdown_structure():
    """Test score breakdown has correct structure."""
    score_path = Path(__file__).parents[2] / "02_audit_logging" / "scores" / "sot_requirement_score.json"

    if not score_path.exists():
        pytest.skip("Score not found - run mapper first")

    with open(score_path, "r", encoding="utf-8") as f:
        score_report = json.load(f)

    breakdown = score_report["score"]["breakdown"]

    # Check all requirement types
    assert "MUST" in breakdown
    assert "SHOULD" in breakdown
    assert "HAVE" in breakdown

    # Each type should have total and satisfied
    for req_type in ["MUST", "SHOULD", "HAVE"]:
        assert "total" in breakdown[req_type]
        assert "satisfied" in breakdown[req_type]
        assert breakdown[req_type]["total"] >= 0
        assert breakdown[req_type]["satisfied"] >= 0
        assert breakdown[req_type]["satisfied"] <= breakdown[req_type]["total"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
