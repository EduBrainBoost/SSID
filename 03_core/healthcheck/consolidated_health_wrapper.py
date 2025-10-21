#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Consolidated Health Check Wrapper
==================================

Universal health check wrapper that replaces 256 duplicate health.py files.

This single wrapper can be symlinked or imported from any layer/shard location.
It dynamically determines the shard from the calling path and uses the
consolidated registry for configuration.

Usage:
    # From any layer/shard location
    from consolidated_health_wrapper import check_health
    success = check_health()

Architecture:
- Replaces: XX_layer/shards/YY_shard/implementations/python-tensorflow/src/api/health.py
- Single implementation for all 256 duplicate files
- Configuration from: consolidated_health_registry.py

Generated: 2025-10-17
Author: SSID Core Team
"""

import sys
from pathlib import Path
from typing import Optional


def _detect_shard_from_path() -> Optional[str]:
    """
    Detect shard name from calling file path.

    Looks for pattern: .../shards/XX_shard_name/...

    Returns:
        Shard name (e.g., "01_identitaet_personen") or None if not detectable
    """
    # Get the caller's file path
    import inspect
    frame = inspect.currentframe()
    if frame and frame.f_back:
        caller_path = Path(frame.f_back.f_code.co_filename)

        # Look for 'shards' in path
        parts = caller_path.parts
        for i, part in enumerate(parts):
            if part == "shards" and i + 1 < len(parts):
                shard_name = parts[i + 1]
                # Validate format: XX_name
                if len(shard_name) > 3 and shard_name[2] == '_':
                    return shard_name

    return None


def check_health(shard_name: Optional[str] = None) -> bool:
    """
    Execute health checks for the current shard.

    Args:
        shard_name: Optional shard identifier (e.g., "01_identitaet_personen")
                   If not provided, will be auto-detected from calling path

    Returns:
        True if all checks pass, False otherwise

    Raises:
        ValueError: If shard cannot be detected or is invalid
    """
    # Add core module to path if not already present
    root = Path(__file__).resolve().parents[2]  # Go up to SSID root
    core_path = root / "03_core"
    if str(core_path) not in sys.path:
        sys.path.insert(0, str(core_path))

    # Import dependencies
    from healthcheck.consolidated_health_registry import get_shard_config
    from healthcheck.health_check_core import HealthChecker, run_checks

    # Detect shard if not provided
    if shard_name is None:
        shard_name = _detect_shard_from_path()
        if shard_name is None:
            raise ValueError(
                "Could not detect shard from calling path. "
                "Please provide shard_name explicitly."
            )

    # Get configuration from registry
    try:
        config = get_shard_config(shard_name)
    except KeyError as e:
        raise ValueError(f"Invalid shard name: {shard_name}") from e

    # Create health checker
    checkers = [
        HealthChecker(
            name=config.core_name,
            port=config.port,
            endpoint=config.endpoint,
            timeout=config.timeout
        ),
    ]

    # Run checks
    return run_checks(checkers)


def main(shard_name: Optional[str] = None):
    """
    CLI entry point.

    Args:
        shard_name: Optional shard identifier
    """
    try:
        # Auto-detect shard if not provided
        if shard_name is None:
            shard_name = _detect_shard_from_path()

        if shard_name is None:
            # Try to get from command line args
            if len(sys.argv) > 1:
                shard_name = sys.argv[1]
            else:
                print("ERROR: Could not detect shard. Usage: health.py [shard_name]")
                sys.exit(2)

        # Run health check
        success = check_health(shard_name)

        # Print result
        status = "PASS" if success else "FAIL"
        print(f"{shard_name}: {status}")

        # Exit with appropriate code
        sys.exit(0 if success else 1)

    except Exception as e:
        print(f"ERROR: {str(e)}")
        sys.exit(2)


if __name__ == "__main__":
    main()
