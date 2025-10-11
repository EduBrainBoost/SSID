"""
Shard Health Adapter Snippet (v4.2)

COPY THIS CONTENT INTO EACH <root>/shards/*/health.py FILE

This adapter loads the central template via importlib, which works correctly
with numeric root folder names (e.g., 01_ai_layer, 02_audit_logging, etc.).

Purpose:
- Replace 388 hardcoded "up" health files with template-based checks
- Provides readiness(), liveness(), and status() functions
- All checks are read-only (SAFE-FIX compliant)

Usage:
    1. Copy this entire file content
    2. Replace the content of each <root>/shards/<shard_name>/health.py
    3. No modifications needed - adapter auto-locates template

Example Paths:
- 01_ai_layer/shards/shard_01_core/health.py
- 02_audit_logging/shards/shard_01_collector/health.py
- ...
- 24_meta_orchestration/shards/shard_16_timeline/health.py

The adapter calculates the relative path to template_health.py automatically.
"""

import os
import importlib.util
from typing import Dict, Any


def _load_template():
    """
    Load the central health template module using importlib.

    This approach works with numeric root folder names that can't be
    imported directly as Python modules.

    Returns:
        Loaded template_health module with readiness(), liveness(), status()
    """
    # Calculate path to template: <root>/shards/<shard>/health.py
    # Need to go: ../../../12_tooling/health/template_health.py
    current_file = os.path.abspath(__file__)
    shard_dir = os.path.dirname(current_file)  # <root>/shards/<shard>
    shards_dir = os.path.dirname(shard_dir)    # <root>/shards
    root_dir = os.path.dirname(shards_dir)      # <root>
    repo_root = os.path.dirname(root_dir)       # Repository root

    template_path = os.path.join(
        repo_root,
        "12_tooling",
        "health",
        "template_health.py"
    )
    template_path = os.path.normpath(template_path)

    # Load module from file path
    spec = importlib.util.spec_from_file_location("template_health", template_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load template from {template_path}")

    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def readiness() -> Dict[str, Any]:
    """
    Check if system is ready (correctly wired + recent evidence).

    Returns:
        {
            "status": "ready" | "degraded",
            "checks": [...]
        }
    """
    return _load_template().readiness()


def liveness() -> Dict[str, Any]:
    """
    Check if system is alive (recent activity detected).

    Returns:
        {
            "status": "alive" | "stale",
            "checks": [...]
        }
    """
    return _load_template().liveness()


def status() -> Dict[str, Any]:
    """
    Aggregate readiness + liveness status.

    Returns:
        {
            "status": "ready" | "degraded",
            "readiness": {...},
            "liveness": {...}
        }
    """
    return _load_template().status()


# Standalone execution for testing
if __name__ == "__main__":
    import json

    print("=== Shard Health Check ===")
    st = status()
    print(json.dumps(st, indent=2, ensure_ascii=False))
