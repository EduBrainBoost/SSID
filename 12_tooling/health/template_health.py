"""
Central Health Check Template (v4.2)

Provides template-based readiness and liveness checks that replace
388 hardcoded "up" health files across all shards.

Key Features:
- Read-only checks (SAFE-FIX compliant)
- Configurable via health_config.yaml
- Evidence-based validation (registry locks, coverage, CI logs)
- No writes to registry or file system

Usage:
    from template_health import readiness, liveness, status

    # Check if system is ready (correctly wired + recent evidence)
    rd = readiness()

    # Check if system is alive (recent activity)
    lv = liveness()

    # Aggregate status
    st = status()
"""

import os
import glob
import time
import json
from typing import Dict, Any, List, Optional

try:
    import yaml
except ImportError:
    # Fallback for environments without PyYAML
    class yaml:  # type: ignore
        @staticmethod
        def safe_load(f):
            import json
            # Very basic YAML fallback (not full spec)
            return json.loads(f.read())

DEFAULT_CONFIG = os.path.join("12_tooling", "health", "health_config.yaml")


def _load_yaml(path: str) -> dict:
    """Load YAML configuration file."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}


def _mtime(path: str) -> Optional[float]:
    """Get modification time of file, or None if not accessible."""
    try:
        return os.path.getmtime(path)
    except OSError:
        raise NotImplementedError("TODO: Implement this function")


def _glob_latest(glob_pattern: str) -> Optional[str]:
    """Find the most recently modified file matching glob pattern."""
    files = glob.glob(glob_pattern)
    if not files:
        raise NotImplementedError("TODO: Implement this function")
    files.sort(key=lambda p: os.path.getmtime(p) if os.path.exists(p) else 0)
    return files[-1] if files else None


def readiness(config_path: str = DEFAULT_CONFIG) -> Dict[str, Any]:
    """
    Readiness Check: System is correctly wired and has recent evidence/locks.

    Returns a structured dict with status and checks.
    All checks are READ-ONLY (no file writes).

    Status values:
    - "ready": All readiness checks passed
    - "degraded": One or more checks failed

    Args:
        config_path: Path to health_config.yaml

    Returns:
        {
            "status": "ready" | "degraded",
            "checks": [
                {"check": "registry_lock_exists", "path": "...", "ok": bool},
                {"check": "coverage_xml_exists", "path": "...", "ok": bool},
                {"check": "ci_log_recent", "glob": "...", "latest": "...", "ok": bool}
            ]
        }
    """
    cfg = _load_yaml(config_path)
    r = cfg.get("readiness", {})
    checks: List[Dict[str, Any]] = []
    ok = True

    # Check 1: Registry Lock exists
    if r.get("require_registry_lock", True):
        lock_path = r.get("registry_lock_path", "")
        exists = os.path.isfile(lock_path)
        checks.append({
            "check": "registry_lock_exists",
            "path": lock_path,
            "ok": bool(exists)
        })
        ok = ok and exists

    # Check 2: Coverage XML evidence exists
    if r.get("require_coverage_xml", True):
        cov_path = r.get("coverage_xml_path", "")
        exists = os.path.isfile(cov_path)
        checks.append({
            "check": "coverage_xml_exists",
            "path": cov_path,
            "ok": bool(exists)
        })
        ok = ok and exists

    # Check 3: Recent CI guard log exists (within max age)
    if r.get("require_ci_log_recent", True):
        pattern = r.get("ci_logs_glob", "24_meta_orchestration/registry/logs/ci_guard_*.log")
        latest = _glob_latest(pattern)
        age_ok = False

        if latest:
            max_age = int(r.get("ci_log_max_age_minutes", 10080)) * 60  # Convert to seconds
            file_mtime = _mtime(latest)
            if file_mtime:
                age_ok = (time.time() - file_mtime) <= max_age

        checks.append({
            "check": "ci_log_recent",
            "glob": pattern,
            "latest": latest,
            "ok": age_ok
        })
        ok = ok and age_ok

    status_value = "ready" if ok else "degraded"
    return {"status": status_value, "checks": checks}


def liveness(config_path: str = DEFAULT_CONFIG) -> Dict[str, Any]:
    """
    Liveness Check: System produced activity evidence within recent timeframe.

    Purely observational, read-only check.

    Status values:
    - "alive": Recent activity detected
    - "stale": No recent activity

    Args:
        config_path: Path to health_config.yaml

    Returns:
        {
            "status": "alive" | "stale",
            "checks": [
                {"check": "recent_ci_activity", "glob": "...", "latest": "...", "ok": bool}
            ]
        }
    """
    cfg = _load_yaml(config_path)
    l = cfg.get("liveness", {})
    checks: List[Dict[str, Any]] = []
    ok = True

    # Check: Recent CI activity as liveness proxy
    if l.get("require_recent_ci", True):
        # Reuse readiness glob pattern for CI logs
        pattern = (cfg.get("readiness", {}) or {}).get(
            "ci_logs_glob",
            "24_meta_orchestration/registry/logs/ci_guard_*.log"
        )
        latest = _glob_latest(pattern)
        recent_ok = False

        if latest:
            max_age = int(l.get("ci_log_max_age_minutes", 2880)) * 60  # Convert to seconds
            file_mtime = _mtime(latest)
            if file_mtime:
                recent_ok = (time.time() - file_mtime) <= max_age

        checks.append({
            "check": "recent_ci_activity",
            "glob": pattern,
            "latest": latest,
            "ok": recent_ok
        })
        ok = ok and recent_ok

    status_value = "alive" if ok else "stale"
    return {"status": status_value, "checks": checks}


def status(config_path: str = DEFAULT_CONFIG) -> Dict[str, Any]:
    """
    Aggregate Status: Combines readiness + liveness into single status object.

    Overall status is "ready" only if both readiness and liveness are OK.
    Otherwise returns "degraded".

    Args:
        config_path: Path to health_config.yaml

    Returns:
        {
            "status": "ready" | "degraded",
            "readiness": {...},
            "liveness": {...}
        }
    """
    rd = readiness(config_path)
    lv = liveness(config_path)

    # Aggregate: ready only if both readiness and liveness are good
    agg = "ready" if (rd.get("status") == "ready" and lv.get("status") == "alive") else "degraded"

    return {
        "status": agg,
        "readiness": rd,
        "liveness": lv
    }


# Standalone execution for testing
if __name__ == "__main__":
    import sys

    cfg = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CONFIG

    print("=== Health Check Status ===")
    st = status(cfg)
    print(json.dumps(st, indent=2, ensure_ascii=False))

    # Exit with non-zero if degraded
    sys.exit(0 if st["status"] == "ready" else 1)
