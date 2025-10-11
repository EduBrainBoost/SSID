"""
Comprehensive tests for adoption_guard.py module.

Tests enforcement of template-based health check adoption including:
- Detection of missing template imports
- Detection of hardcoded "up" status
- Handling of malformed files
- Correct scanning of repository structure
"""

import os
import json
import tempfile
import shutil
from pathlib import Path
import importlib.util
import pytest


def _load_guard(root: str):
    """Load adoption_guard module from specified root directory."""
    p = os.path.join(root, "12_tooling", "health", "adoption_guard.py")
    spec = importlib.util.spec_from_file_location("adoption_guard", p)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load guard from {p}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_adoption_guard_detects_missing_import(tmp_path: Path):
    """Test that guard detects health files without template import."""
    # Create shard health.py without template import
    hp = tmp_path / "01_ai_layer" / "shards" / "shard_01" / "health.py"
    hp.parent.mkdir(parents=True)
    hp.write_text(
        "def readiness():\n    return {'status':'up'}\n",
        encoding="utf-8"
    )

    # Copy guard module
    (tmp_path / "12_tooling" / "health").mkdir(parents=True)
    shutil.copy(
        "C:/Users/bibel/Documents/Github/SSID/12_tooling/health/adoption_guard.py",
        tmp_path / "12_tooling" / "health" / "adoption_guard.py"
    )

    guard = _load_guard(str(tmp_path))
    res = guard.scan_repo_for_adoption(str(tmp_path))

    assert res["files_scanned"] == 1
    assert len(res["violations"]) >= 1
    assert any(
        v["error"] in ("missing-template-import", "hardcoded-up-status")
        for v in res["violations"]
    )


def test_adoption_guard_detects_hardcoded_up(tmp_path: Path):
    """Test that guard detects hardcoded 'up' status even with template import."""
    hp = tmp_path / "02_audit_logging" / "shards" / "shard_02" / "health.py"
    hp.parent.mkdir(parents=True)

    # Has template import but also hardcoded "up"
    hp.write_text(
        'import template_health\ndef readiness():\n    return {"status": "up"}\n',
        encoding="utf-8"
    )

    (tmp_path / "12_tooling" / "health").mkdir(parents=True)
    shutil.copy(
        "C:/Users/bibel/Documents/Github/SSID/12_tooling/health/adoption_guard.py",
        tmp_path / "12_tooling" / "health" / "adoption_guard.py"
    )

    guard = _load_guard(str(tmp_path))
    res = guard.scan_repo_for_adoption(str(tmp_path))

    assert res["files_scanned"] == 1
    assert len(res["violations"]) == 1
    assert res["violations"][0]["error"] == "hardcoded-up-status"


def test_adoption_guard_accepts_compliant_file(tmp_path: Path):
    """Test that guard accepts properly formatted health file with template import."""
    hp = tmp_path / "03_core" / "shards" / "shard_03" / "health.py"
    hp.parent.mkdir(parents=True)

    # Compliant: has template import, no hardcoded "up"
    hp.write_text(
        '''import os, importlib.util
def _load():
    p = os.path.join(os.path.dirname(__file__), "../../../12_tooling/health/template_health.py")
    spec = importlib.util.spec_from_file_location("template_health", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod
def readiness(): return _load().readiness()
def liveness(): return _load().liveness()
def status(): return _load().status()
''',
        encoding="utf-8"
    )

    (tmp_path / "12_tooling" / "health").mkdir(parents=True)
    shutil.copy(
        "C:/Users/bibel/Documents/Github/SSID/12_tooling/health/adoption_guard.py",
        tmp_path / "12_tooling" / "health" / "adoption_guard.py"
    )

    guard = _load_guard(str(tmp_path))
    res = guard.scan_repo_for_adoption(str(tmp_path))

    assert res["files_scanned"] == 1
    assert len(res["violations"]) == 0


def test_adoption_guard_handles_read_errors(tmp_path: Path):
    """Test that guard handles file read errors gracefully."""
    hp = tmp_path / "04_blockchain" / "shards" / "shard_04" / "health.py"
    hp.parent.mkdir(parents=True)
    hp.write_text("dummy", encoding="utf-8")

    # Make file unreadable (if possible on platform)
    try:
        hp.chmod(0o000)
        file_made_unreadable = True
    except Exception:
        file_made_unreadable = False
        pytest.skip("Cannot make file unreadable on this platform")

    (tmp_path / "12_tooling" / "health").mkdir(parents=True)
    shutil.copy(
        "C:/Users/bibel/Documents/Github/SSID/12_tooling/health/adoption_guard.py",
        tmp_path / "12_tooling" / "health" / "adoption_guard.py"
    )

    guard = _load_guard(str(tmp_path))

    try:
        res = guard.scan_repo_for_adoption(str(tmp_path))

        if file_made_unreadable:
            assert res["files_scanned"] == 1
            assert len(res["violations"]) == 1
            assert "read-failed" in res["violations"][0]["error"]
    finally:
        # Restore permissions for cleanup
        try:
            hp.chmod(0o644)
        except Exception:
            raise NotImplementedError("TODO: Implement this block")


def test_adoption_guard_scans_multiple_shards(tmp_path: Path):
    """Test that guard scans multiple shard health files correctly."""
    # Create multiple shards across different roots
    shards = [
        ("01_ai_layer", "shard_01", "compliant"),
        ("02_audit_logging", "shard_02", "missing-import"),
        ("03_core", "shard_03", "hardcoded-up"),
        ("04_blockchain", "shard_04", "compliant"),
    ]

    for root_name, shard_name, violation_type in shards:
        hp = tmp_path / root_name / "shards" / shard_name / "health.py"
        hp.parent.mkdir(parents=True)

        if violation_type == "compliant":
            hp.write_text(
                'from template_health import readiness\ndef status(): return {"status": "ready"}',
                encoding="utf-8"
            )
        elif violation_type == "missing-import":
            hp.write_text(
                'def readiness(): return {"status":"ready"}',
                encoding="utf-8"
            )
        elif violation_type == "hardcoded-up":
            hp.write_text(
                'import template_health\ndef readiness(): return {"status":"up"}',
                encoding="utf-8"
            )

    (tmp_path / "12_tooling" / "health").mkdir(parents=True)
    shutil.copy(
        "C:/Users/bibel/Documents/Github/SSID/12_tooling/health/adoption_guard.py",
        tmp_path / "12_tooling" / "health" / "adoption_guard.py"
    )

    guard = _load_guard(str(tmp_path))
    res = guard.scan_repo_for_adoption(str(tmp_path))

    assert res["files_scanned"] == 4
    assert len(res["violations"]) == 2  # missing-import and hardcoded-up


def test_adoption_guard_empty_repository(tmp_path: Path):
    """Test guard with empty repository (no shard health files)."""
    (tmp_path / "12_tooling" / "health").mkdir(parents=True)
    shutil.copy(
        "C:/Users/bibel/Documents/Github/SSID/12_tooling/health/adoption_guard.py",
        tmp_path / "12_tooling" / "health" / "adoption_guard.py"
    )

    guard = _load_guard(str(tmp_path))
    res = guard.scan_repo_for_adoption(str(tmp_path))

    assert res["files_scanned"] == 0
    assert len(res["violations"]) == 0


def test_adoption_guard_various_hardcoded_patterns(tmp_path: Path):
    """Test guard detects various hardcoded 'up' status patterns."""
    patterns = [
        ('return "up"', True),
        ("return 'up'", True),
        ('{"status": "up"}', True),
        ("{'status':'up'}", True),
        ('return {"status": "up"}', True),
        ('status = "ready"', False),  # Not a violation
        ('# return "up" commented out', False),  # Comment should be OK
    ]

    for idx, (code, should_violate) in enumerate(patterns):
        hp = tmp_path / f"test_root_{idx}" / "shards" / "shard" / "health.py"
        hp.parent.mkdir(parents=True, exist_ok=True)

        # Add template import to focus test on hardcoded pattern
        full_code = f'import template_health\n{code}\n'
        hp.write_text(full_code, encoding="utf-8")

    (tmp_path / "12_tooling" / "health").mkdir(parents=True)
    shutil.copy(
        "C:/Users/bibel/Documents/Github/SSID/12_tooling/health/adoption_guard.py",
        tmp_path / "12_tooling" / "health" / "adoption_guard.py"
    )

    guard = _load_guard(str(tmp_path))
    res = guard.scan_repo_for_adoption(str(tmp_path))

    violations_found = len(res["violations"])
    expected_violations = sum(1 for _, should_violate in patterns if should_violate)

    # Should detect all hardcoded "up" patterns
    assert violations_found >= expected_violations


def test_adoption_guard_json_output(tmp_path: Path):
    """Test that guard produces valid JSON output."""
    hp = tmp_path / "test_root" / "shards" / "shard" / "health.py"
    hp.parent.mkdir(parents=True)
    hp.write_text('def status(): return "up"', encoding="utf-8")

    (tmp_path / "12_tooling" / "health").mkdir(parents=True)
    shutil.copy(
        "C:/Users/bibel/Documents/Github/SSID/12_tooling/health/adoption_guard.py",
        tmp_path / "12_tooling" / "health" / "adoption_guard.py"
    )

    guard = _load_guard(str(tmp_path))
    res = guard.scan_repo_for_adoption(str(tmp_path))

    # Should be valid JSON-serializable
    json_str = json.dumps(res)
    parsed = json.loads(json_str)

    assert "files_scanned" in parsed
    assert "violations" in parsed
    assert isinstance(parsed["files_scanned"], int)
    assert isinstance(parsed["violations"], list)


def test_adoption_guard_deep_nested_shards(tmp_path: Path):
    """Test guard finds health files in deeply nested structures."""
    # Create deeply nested shard
    deep_path = tmp_path / "01_ai_layer" / "sub" / "nested" / "shards" / "shard_deep" / "health.py"
    deep_path.parent.mkdir(parents=True)
    deep_path.write_text('def status(): return "up"', encoding="utf-8")

    # Create normal shard
    normal_path = tmp_path / "02_audit" / "shards" / "shard_normal" / "health.py"
    normal_path.parent.mkdir(parents=True)
    normal_path.write_text('import template_health\ndef status(): return template_health.status()', encoding="utf-8")

    (tmp_path / "12_tooling" / "health").mkdir(parents=True)
    shutil.copy(
        "C:/Users/bibel/Documents/Github/SSID/12_tooling/health/adoption_guard.py",
        tmp_path / "12_tooling" / "health" / "adoption_guard.py"
    )

    guard = _load_guard(str(tmp_path))
    res = guard.scan_repo_for_adoption(str(tmp_path))

    # Should find both files
    assert res["files_scanned"] == 2
    # Deep path should have violation, normal should not
    assert len(res["violations"]) >= 1
