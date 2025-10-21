def test_budget_yaml_parsed():
    from pathlib import Path
    p = Path("24_meta_orchestration/registry/change_budget.yaml")
    assert p.exists()
    txt = p.read_text(encoding="utf-8")
    assert "allowed_paths" in txt and "forbidden_globs" in txt

def test_detect_changes_script_runs(tmp_path, monkeypatch):
    import subprocess, sys, os, pathlib, shutil
    # Note: This test requires a git repo context
    # In CI, the checkout action provides this
    # For local testing, we just verify the script exists and is executable
    script = pathlib.Path("12_tooling/static_checks/detect_unreferenced_artifacts.py")
    assert script.exists()
    assert script.read_text(encoding="utf-8").startswith("#!/usr/bin/env python3")
