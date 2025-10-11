#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_readiness_health.py – Comprehensive Health Check Test Suite
Autor: edubrainboost ©2025 MIT License

Tests for SSID Unified Readiness Framework:
- Core HealthChecker functionality
- Registry operations
- All 384 health wrapper modules
- Integration with CI/CD gates
"""

import sys
import importlib.util
import yaml
from pathlib import Path
from unittest.mock import patch, MagicMock


ROOT = Path(__file__).resolve().parents[2]
CORE = ROOT / "03_core" / "healthcheck" / "health_check_core.py"
REGISTRY = ROOT / "24_meta_orchestration" / "registry" / "locks" / "service_health_registry.yaml"


def test_health_core_module_exists():
    """Test that core health check module exists."""
    assert CORE.exists(), f"Core module not found at {CORE}"
    print("[PASS] Core module exists")


def test_health_core_importable():
    """Test that core module can be imported."""
    spec = importlib.util.spec_from_file_location("health_check_core", CORE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    assert hasattr(mod, "HealthChecker"), "HealthChecker class not found"
    assert hasattr(mod, "update_registry"), "update_registry function not found"
    assert hasattr(mod, "run_checks"), "run_checks function not found"

    print("[PASS] Core module importable with required exports")


def test_health_checker_class():
    """Test HealthChecker class structure."""
    spec = importlib.util.spec_from_file_location("health_check_core", CORE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    checker = mod.HealthChecker("test-service", port=8080, endpoint="/health")

    assert hasattr(checker, "port_check"), "Missing port_check method"
    assert hasattr(checker, "http_check"), "Missing http_check method"
    assert hasattr(checker, "registry_check"), "Missing registry_check method"
    assert hasattr(checker, "readiness"), "Missing readiness method"

    assert callable(checker.port_check)
    assert callable(checker.http_check)
    assert callable(checker.registry_check)
    assert callable(checker.readiness)

    print("[PASS] HealthChecker class structure valid")


def test_registry_file_exists():
    """Test that service health registry exists."""
    assert REGISTRY.exists(), f"Registry not found at {REGISTRY}"
    print("[PASS] Service health registry exists")


def test_registry_structure():
    """Test that registry has correct YAML structure."""
    data = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))

    assert "meta" in data, "Missing 'meta' section"
    assert "services" in data, "Missing 'services' section"
    assert "summary" in data, "Missing 'summary' section"

    assert isinstance(data["services"], dict), "services must be a dict"
    assert isinstance(data["summary"], dict), "summary must be a dict"

    print("[PASS] Registry structure valid")


def test_health_wrappers_count():
    """Test that all 384 health wrappers were generated."""
    health_files = list(ROOT.glob("**/health.py"))
    impl_health_files = [
        f for f in health_files
        if "implementations" in f.parts and "api" in f.parts
    ]

    assert len(impl_health_files) >= 384, f"Expected 384+ wrappers, found {len(impl_health_files)}"
    print(f"[PASS] Found {len(impl_health_files)} health wrappers")


def test_health_wrapper_structure():
    """Test that health wrappers have correct structure."""
    health_files = list(ROOT.glob("**/health.py"))
    impl_health_files = [
        f for f in health_files
        if "implementations" in f.parts and "api" in f.parts
    ][:5]  # Test first 5

    for health_file in impl_health_files:
        content = health_file.read_text(encoding="utf-8")

        assert "HealthChecker" in content, f"{health_file}: Missing HealthChecker import"
        assert "run_checks" in content, f"{health_file}: Missing run_checks import"
        assert "check_health" in content, f"{health_file}: Missing check_health function"
        assert 'name="' in content, f"{health_file}: Missing service name"
        assert "port=" in content, f"{health_file}: Missing port configuration"

    print("[PASS] Health wrapper structure valid")


def test_health_checker_readiness_format():
    """Test that readiness() returns correct format."""
    spec = importlib.util.spec_from_file_location("health_check_core", CORE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    checker = mod.HealthChecker("test-service")
    result = checker.readiness()

    assert "timestamp" in result, "Missing timestamp"
    assert "service" in result, "Missing service"
    assert "checks" in result, "Missing checks"
    assert "status" in result, "Missing status"

    assert isinstance(result["checks"], dict), "checks must be dict"
    assert "port" in result["checks"], "Missing port check"
    assert "http" in result["checks"], "Missing http check"
    assert "registry" in result["checks"], "Missing registry check"

    assert isinstance(result["status"], bool), "status must be bool"

    print("[PASS] Readiness format valid")


def test_update_registry_function():
    """Test that update_registry creates/updates registry correctly."""
    spec = importlib.util.spec_from_file_location("health_check_core", CORE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    # Create test data
    test_statuses = [
        {
            "timestamp": "2025-10-07T10:00:00Z",
            "service": "test-service-1",
            "port": 8080,
            "endpoint": "/health",
            "checks": {"port": True, "http": True, "registry": True},
            "status": True
        },
        {
            "timestamp": "2025-10-07T10:00:00Z",
            "service": "test-service-2",
            "port": 8081,
            "endpoint": "/health",
            "checks": {"port": False, "http": False, "registry": False},
            "status": False
        }
    ]

    # Backup existing registry
    backup = None
    if REGISTRY.exists():
        backup = REGISTRY.read_text(encoding="utf-8")

    try:
        # Update registry
        mod.update_registry(test_statuses)

        # Verify
        data = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))

        assert "test-service-1" in data["services"]
        assert "test-service-2" in data["services"]
        assert data["services"]["test-service-1"]["status"] == "up"
        assert data["services"]["test-service-2"]["status"] == "down"

        assert data["summary"]["total"] == 2
        assert data["summary"]["healthy"] == 1
        assert data["summary"]["percentage"] == 50.0

        print("[PASS] update_registry function works correctly")

    finally:
        # Restore backup
        if backup:
            REGISTRY.write_text(backup, encoding="utf-8")


def test_port_check_no_port():
    """Test port_check returns True when no port configured."""
    spec = importlib.util.spec_from_file_location("health_check_core", CORE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    checker = mod.HealthChecker("test-service", port=None)
    assert checker.port_check() is True

    print("[PASS] port_check with no port returns True")


def test_http_check_no_endpoint():
    """Test http_check returns True when no endpoint configured."""
    spec = importlib.util.spec_from_file_location("health_check_core", CORE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    checker = mod.HealthChecker("test-service", port=8080, endpoint=None)
    assert checker.http_check() is True

    print("[PASS] http_check with no endpoint returns True")


def main():
    """Run all tests."""
    print("=" * 70)
    print("SSID Health Check Test Suite")
    print("=" * 70)
    print()

    tests = [
        test_health_core_module_exists,
        test_health_core_importable,
        test_health_checker_class,
        test_registry_file_exists,
        test_registry_structure,
        test_health_wrappers_count,
        test_health_wrapper_structure,
        test_health_checker_readiness_format,
        test_update_registry_function,
        test_port_check_no_port,
        test_http_check_no_endpoint,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"[FAIL] {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"[ERROR] {test.__name__}: {e}")
            failed += 1

    print()
    print("=" * 70)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 70)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
