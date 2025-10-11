#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit Tests for Quarterly Review Framework Validator
Author: edubrainboost ©2025 MIT License
"""
import json, pathlib, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
CHECKER = ROOT / "23_compliance" / "tools" / "validate_quarterly_review.py"
SCORE = ROOT / "23_compliance" / "reports" / "review_framework_score.json"

def test_checker_exists():
    assert CHECKER.exists(), f"Validator script not found at {CHECKER}"

def test_run_checker_and_score_written():
    rc = subprocess.run([sys.executable, str(CHECKER)], cwd=str(ROOT))
    assert rc.returncode in (0,2), f"Unexpected return code: {rc.returncode}"
    assert SCORE.exists(), f"Score file not created at {SCORE}"
    data = json.loads(SCORE.read_text(encoding="utf-8"))
    assert data.get("component") == "quarterly_review_framework"
    assert "status" in data and "score" in data and "results" in data

if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
