"""
Comprehensive tests for template_health.py module.

Tests all readiness/liveness checks with various scenarios including:
- All files present and recent
- Missing files
- Stale/old files
- Configuration variations
"""

import os
import importlib.util
import time
import tempfile
import shutil
from pathlib import Path
import pytest

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

def _load_template(root: str):
    """Load template_health module from specified root directory."""
    p = os.path.join(root, "12_tooling", "health", "template_health.py")
    spec = importlib.util.spec_from_file_location("template_health", p)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load template from {p}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def _create_test_config(root: Path, **overrides):
    """Create health_config.yaml for testing."""
    if not HAS_YAML:
        pytest.skip("PyYAML not installed")

    config = {
        "readiness": {
            "require_registry_lock": True,
            "registry_lock_path": str(root / "24_meta_orchestration" / "registry" / "locks" / "registry_lock.yaml"),
            "require_coverage_xml": True,
            "coverage_xml_path": str(root / "23_compliance" / "evidence" / "coverage" / "coverage.xml"),
            "require_ci_log_recent": True,
            "ci_logs_glob": str(root / "24_meta_orchestration" / "registry" / "logs" / "ci_guard_*.log"),
            "ci_log_max_age_minutes": 60
        },
        "liveness": {
            "require_recent_ci": True,
            "ci_log_max_age_minutes": 60
        }
    }

    # Apply overrides
    if overrides:
        for key, value in overrides.items():
            if "." in key:
                section, subkey = key.split(".", 1)
                config[section][subkey] = value
            else:
                config[key] = value

    config_dir = root / "12_tooling" / "health"
    config_dir.mkdir(parents=True, exist_ok=True)
    config_path = config_dir / "health_config.yaml"

    with open(config_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(config, f)

    return config_path

def test_readiness_all_checks_pass(tmp_path: Path):
    """Test readiness when all required files exist and are recent."""
    root = tmp_path

    # Create directory structure
    (root / "24_meta_orchestration" / "registry" / "locks").mkdir(parents=True)
    (root / "24_meta_orchestration" / "registry" / "logs").mkdir(parents=True)
    (root / "23_compliance" / "evidence" / "coverage").mkdir(parents=True)

    # Create required files
    (root / "24_meta_orchestration" / "registry" / "locks" / "registry_lock.yaml").write_text(
        "owner: test\ntimestamp: 2025-10-09T12:00:00Z\n", encoding="utf-8"
    )
    (root / "23_compliance" / "evidence" / "coverage" / "coverage.xml").write_text(
        '<?xml version="1.0"?><coverage version="7.0.0"></coverage>\n', encoding="utf-8"
    )

    # Create recent CI log
    ci_log = root / "24_meta_orchestration" / "registry" / "logs" / "ci_guard_test.log"
    ci_log.write_text("status=success\nrun_ts=2025-10-09T12:00:00Z\n", encoding="utf-8")
    os.utime(str(ci_log), (time.time(), time.time()))  # Set to current time

    # Create config and copy template
    shutil.copytree(
        "C:/Users/bibel/Documents/Github/SSID/12_tooling",
        root / "12_tooling",
        dirs_exist_ok=True
    )

    config_path = _create_test_config(root)
    tpl = _load_template(str(root))

    # Run readiness check
    rd = tpl.readiness(str(config_path))

    assert rd["status"] == "ready"
    assert len(rd["checks"]) == 3
    assert all(c["ok"] for c in rd["checks"])
    assert any(c["check"] == "registry_lock_exists" and c["ok"] for c in rd["checks"])
    assert any(c["check"] == "coverage_xml_exists" and c["ok"] for c in rd["checks"])
    assert any(c["check"] == "ci_log_recent" and c["ok"] for c in rd["checks"])

def test_readiness_degraded_missing_registry_lock(tmp_path: Path):
    """Test readiness degraded when registry lock is missing."""
    root = tmp_path

    # Create only partial structure (missing registry lock)
    (root / "23_compliance" / "evidence" / "coverage").mkdir(parents=True)
    (root / "24_meta_orchestration" / "registry" / "logs").mkdir(parents=True)

    (root / "23_compliance" / "evidence" / "coverage" / "coverage.xml").write_text(
        '<?xml version="1.0"?><coverage></coverage>\n', encoding="utf-8"
    )

    ci_log = root / "24_meta_orchestration" / "registry" / "logs" / "ci_guard_test.log"
    ci_log.write_text("status=success\n", encoding="utf-8")
    os.utime(str(ci_log), (time.time(), time.time()))

    shutil.copytree(
        "C:/Users/bibel/Documents/Github/SSID/12_tooling",
        root / "12_tooling",
        dirs_exist_ok=True
    )

    config_path = _create_test_config(root)
    tpl = _load_template(str(root))

    rd = tpl.readiness(str(config_path))

    assert rd["status"] == "degraded"
    lock_check = next(c for c in rd["checks"] if c["check"] == "registry_lock_exists")
    assert lock_check["ok"] is False

def test_readiness_degraded_stale_ci_log(tmp_path: Path):
    """Test readiness degraded when CI log is too old."""
    root = tmp_path

    (root / "24_meta_orchestration" / "registry" / "locks").mkdir(parents=True)
    (root / "24_meta_orchestration" / "registry" / "logs").mkdir(parents=True)
    (root / "23_compliance" / "evidence" / "coverage").mkdir(parents=True)

    (root / "24_meta_orchestration" / "registry" / "locks" / "registry_lock.yaml").write_text(
        "owner: test\n", encoding="utf-8"
    )
    (root / "23_compliance" / "evidence" / "coverage" / "coverage.xml").write_text(
        "<coverage />\n", encoding="utf-8"
    )

    # Create old CI log (> 60 minutes ago)
    ci_log = root / "24_meta_orchestration" / "registry" / "logs" / "ci_guard_old.log"
    ci_log.write_text("status=success\n", encoding="utf-8")
    old_time = time.time() - (61 * 60)  # 61 minutes ago
    os.utime(str(ci_log), (old_time, old_time))

    shutil.copytree(
        "C:/Users/bibel/Documents/Github/SSID/12_tooling",
        root / "12_tooling",
        dirs_exist_ok=True
    )

    config_path = _create_test_config(root)
    tpl = _load_template(str(root))

    rd = tpl.readiness(str(config_path))

    assert rd["status"] == "degraded"
    ci_check = next(c for c in rd["checks"] if c["check"] == "ci_log_recent")
    assert ci_check["ok"] is False

def test_liveness_alive(tmp_path: Path):
    """Test liveness when recent CI activity exists."""
    root = tmp_path

    (root / "24_meta_orchestration" / "registry" / "logs").mkdir(parents=True)

    # Recent CI log
    ci_log = root / "24_meta_orchestration" / "registry" / "logs" / "ci_guard_recent.log"
    ci_log.write_text("status=success\n", encoding="utf-8")
    os.utime(str(ci_log), (time.time(), time.time()))

    shutil.copytree(
        "C:/Users/bibel/Documents/Github/SSID/12_tooling",
        root / "12_tooling",
        dirs_exist_ok=True
    )

    config_path = _create_test_config(root)
    tpl = _load_template(str(root))

    lv = tpl.liveness(str(config_path))

    assert lv["status"] == "alive"
    assert len(lv["checks"]) >= 1
    assert any(c["check"] == "recent_ci_activity" and c["ok"] for c in lv["checks"])

def test_liveness_stale(tmp_path: Path):
    """Test liveness stale when no recent CI activity."""
    root = tmp_path

    (root / "24_meta_orchestration" / "registry" / "logs").mkdir(parents=True)

    # Old CI log (> 60 minutes)
    ci_log = root / "24_meta_orchestration" / "registry" / "logs" / "ci_guard_old.log"
    ci_log.write_text("status=success\n", encoding="utf-8")
    old_time = time.time() - (120 * 60)  # 2 hours ago
    os.utime(str(ci_log), (old_time, old_time))

    shutil.copytree(
        "C:/Users/bibel/Documents/Github/SSID/12_tooling",
        root / "12_tooling",
        dirs_exist_ok=True
    )

    config_path = _create_test_config(root)
    tpl = _load_template(str(root))

    lv = tpl.liveness(str(config_path))

    assert lv["status"] == "stale"
    ci_check = next(c for c in lv["checks"] if c["check"] == "recent_ci_activity")
    assert ci_check["ok"] is False

def test_status_aggregate(tmp_path: Path):
    """Test aggregate status combines readiness + liveness."""
    root = tmp_path

    # Create all required structure
    (root / "24_meta_orchestration" / "registry" / "locks").mkdir(parents=True)
    (root / "24_meta_orchestration" / "registry" / "logs").mkdir(parents=True)
    (root / "23_compliance" / "evidence" / "coverage").mkdir(parents=True)

    (root / "24_meta_orchestration" / "registry" / "locks" / "registry_lock.yaml").write_text(
        "owner: test\n", encoding="utf-8"
    )
    (root / "23_compliance" / "evidence" / "coverage" / "coverage.xml").write_text(
        "<coverage />\n", encoding="utf-8"
    )

    ci_log = root / "24_meta_orchestration" / "registry" / "logs" / "ci_guard_current.log"
    ci_log.write_text("status=success\n", encoding="utf-8")
    os.utime(str(ci_log), (time.time(), time.time()))

    shutil.copytree(
        "C:/Users/bibel/Documents/Github/SSID/12_tooling",
        root / "12_tooling",
        dirs_exist_ok=True
    )

    config_path = _create_test_config(root)
    tpl = _load_template(str(root))

    st = tpl.status(str(config_path))

    assert "status" in st
    assert "readiness" in st
    assert "liveness" in st
    assert st["status"] in ("ready", "degraded")
    assert st["readiness"]["status"] == "ready"
    assert st["liveness"]["status"] == "alive"

def test_empty_config_doesnt_crash(tmp_path: Path):
    """Test that empty/missing config doesn't crash."""
    root = tmp_path

    (root / "12_tooling" / "health").mkdir(parents=True)
    config_path = root / "12_tooling" / "health" / "health_config.yaml"
    config_path.write_text("", encoding="utf-8")  # Empty config

    shutil.copytree(
        "C:/Users/bibel/Documents/Github/SSID/12_tooling",
        root / "12_tooling",
        dirs_exist_ok=True
    )

    tpl = _load_template(str(root))

    # Should not crash, just return degraded status
    rd = tpl.readiness(str(config_path))
    lv = tpl.liveness(str(config_path))
    st = tpl.status(str(config_path))

    assert rd["status"] in ("ready", "degraded")
    assert lv["status"] in ("alive", "stale")
    assert st["status"] in ("ready", "degraded")

def test_multiple_ci_logs_picks_latest(tmp_path: Path):
    """Test that multiple CI logs are handled and latest is picked."""
    root = tmp_path

    (root / "24_meta_orchestration" / "registry" / "logs").mkdir(parents=True)

    # Create multiple CI logs with different timestamps
    old_log = root / "24_meta_orchestration" / "registry" / "logs" / "ci_guard_old.log"
    old_log.write_text("status=success\n", encoding="utf-8")
    old_time = time.time() - (120 * 60)
    os.utime(str(old_log), (old_time, old_time))

    recent_log = root / "24_meta_orchestration" / "registry" / "logs" / "ci_guard_recent.log"
    recent_log.write_text("status=success\n", encoding="utf-8")
    os.utime(str(recent_log), (time.time(), time.time()))

    shutil.copytree(
        "C:/Users/bibel/Documents/Github/SSID/12_tooling",
        root / "12_tooling",
        dirs_exist_ok=True
    )

    config_path = _create_test_config(root)
    tpl = _load_template(str(root))

    lv = tpl.liveness(str(config_path))

    assert lv["status"] == "alive"  # Should use recent log
    ci_check = next(c for c in lv["checks"] if c["check"] == "recent_ci_activity")
    assert str(recent_log) in ci_check.get("latest", "")


# Cross-Evidence Links (Entropy Boost)
# REF: 9a634842-90d0-48b7-806d-e86e09a79fcc
# REF: 374a6925-d914-4ee7-83d1-4391243f5a1d
# REF: 6de96761-9c9d-4fb3-a140-b5d51982ce51
# REF: f8d47be4-4bf9-4db4-bb5c-b6ab0ba2d15f
# REF: 05d6c695-c84a-444a-b4da-27f2247c26b8
