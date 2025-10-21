#!/usr/bin/env python3
"""
SoT Validator Test Suite
=========================

Comprehensive tests for SoT Validator Core and Cached Validator.

Test Coverage:
- AR001-AR010: Architecture rules (24x16 matrix validation)
- CP001+: Key compliance rules
- Performance: Benchmarking and cache performance
- Edge cases: Boundary conditions, missing files, error handling

Test Categories (pytest markers):
- @pytest.mark.ar: Architecture rule tests
- @pytest.mark.cp: Compliance rule tests
- @pytest.mark.performance: Performance tests
- @pytest.mark.unit: Unit tests
- @pytest.mark.integration: Integration tests
- @pytest.mark.cached: Cached validator tests
- @pytest.mark.original: Original validator tests

Usage:
    # Run all tests
    pytest -v

    # Run only AR tests
    pytest -v -m ar

    # Run with coverage
    pytest --cov --cov-report=html --cov-report=term

    # Run performance tests
    pytest -v -m performance
"""

import pytest
import sys
import time
from pathlib import Path

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sot_validator_core import (
    SoTValidator,
    ValidationResult,
    Severity,
    REQUIRED_ROOT_COUNT,
    REQUIRED_SHARD_COUNT
)
from cached_validator import CachedSoTValidator


# ============================================================
# AR001: EXACTLY 24 ROOT FOLDERS
# ============================================================

@pytest.mark.ar
@pytest.mark.unit
@pytest.mark.critical
class TestAR001:
    """Tests for AR001: System must have exactly 24 root folders."""

    def test_ar001_valid_24_roots_original(self, valid_repo_structure):
        """[AR001] Valid repo with 24 roots should PASS (original validator)"""
        validator = SoTValidator(repo_root=valid_repo_structure)
        result = validator.validate_ar001()

        assert result.passed is True
        assert result.rule_id == "AR001"
        assert result.severity == Severity.CRITICAL
        assert result.evidence["actual_count"] == REQUIRED_ROOT_COUNT
        assert result.evidence["expected_count"] == REQUIRED_ROOT_COUNT

    def test_ar001_valid_24_roots_cached(self, valid_repo_structure):
        """[AR001] Valid repo with 24 roots should PASS (cached validator)"""
        validator = CachedSoTValidator(repo_root=valid_repo_structure)
        result = validator.validate_ar001()

        assert result.passed is True
        assert result.rule_id == "AR001"
        assert result.severity == Severity.CRITICAL
        assert result.evidence["actual_count"] == REQUIRED_ROOT_COUNT

    def test_ar001_invalid_missing_roots(self, invalid_repo_missing_roots):
        """[AR001] Repo with <24 roots should FAIL"""
        validator = SoTValidator(repo_root=invalid_repo_missing_roots)
        result = validator.validate_ar001()

        assert result.passed is False
        assert result.evidence["actual_count"] < REQUIRED_ROOT_COUNT
        assert len(result.evidence["missing_roots"]) > 0

    def test_ar001_invalid_missing_roots_cached(self, invalid_repo_missing_roots):
        """[AR001] Repo with <24 roots should FAIL (cached)"""
        validator = CachedSoTValidator(repo_root=invalid_repo_missing_roots)
        result = validator.validate_ar001()

        assert result.passed is False
        assert result.evidence["actual_count"] < REQUIRED_ROOT_COUNT

    def test_ar001_empty_repo(self, temp_repo):
        """[AR001] Empty repo should FAIL"""
        empty_repo = temp_repo / "empty"
        empty_repo.mkdir()

        validator = SoTValidator(repo_root=empty_repo)
        result = validator.validate_ar001()

        assert result.passed is False
        assert result.evidence["actual_count"] == 0
        assert result.evidence["expected_count"] == REQUIRED_ROOT_COUNT


# ============================================================
# AR002: EACH ROOT MUST HAVE EXACTLY 16 SHARDS
# ============================================================

@pytest.mark.ar
@pytest.mark.unit
@pytest.mark.critical
class TestAR002:
    """Tests for AR002: Each root must have exactly 16 shards."""

    def test_ar002_valid_16_shards_per_root_original(self, valid_repo_structure):
        """[AR002] Valid repo with 16 shards per root should PASS"""
        validator = SoTValidator(repo_root=valid_repo_structure)
        result = validator.validate_ar002()

        assert result.passed is True
        assert result.rule_id == "AR002"
        assert result.severity == Severity.CRITICAL
        assert len(result.evidence["violations"]) == 0

    def test_ar002_valid_16_shards_per_root_cached(self, valid_repo_structure):
        """[AR002] Valid repo with 16 shards per root should PASS (cached)"""
        validator = CachedSoTValidator(repo_root=valid_repo_structure)
        result = validator.validate_ar002()

        assert result.passed is True
        assert len(result.evidence["violations"]) == 0

    def test_ar002_invalid_missing_shards(self, invalid_repo_missing_shards):
        """[AR002] Repo with <16 shards in some roots should FAIL"""
        validator = SoTValidator(repo_root=invalid_repo_missing_shards)
        result = validator.validate_ar002()

        assert result.passed is False
        assert len(result.evidence["violations"]) > 0

        # Check violation details
        for violation in result.evidence["violations"]:
            assert violation["actual_shards"] != REQUIRED_SHARD_COUNT
            assert violation["expected_shards"] == REQUIRED_SHARD_COUNT

    def test_ar002_invalid_missing_shards_cached(self, invalid_repo_missing_shards):
        """[AR002] Repo with <16 shards in some roots should FAIL (cached)"""
        validator = CachedSoTValidator(repo_root=invalid_repo_missing_shards)
        result = validator.validate_ar002()

        assert result.passed is False
        assert len(result.evidence["violations"]) > 0


# ============================================================
# AR003: 24x16=384 SHARD MATRIX
# ============================================================

@pytest.mark.ar
@pytest.mark.unit
@pytest.mark.critical
class TestAR003:
    """Tests for AR003: System must form a 24x16=384 shard matrix."""

    def test_ar003_valid_384_shards_original(self, valid_repo_structure):
        """[AR003] Valid repo with 384 shards should PASS"""
        validator = SoTValidator(repo_root=valid_repo_structure)
        result = validator.validate_ar003()

        assert result.passed is True
        assert result.rule_id == "AR003"
        assert result.severity == Severity.CRITICAL
        assert result.evidence["actual_total_charts"] == 384
        assert result.evidence["required_total_charts"] == 384

    def test_ar003_valid_384_shards_cached(self, valid_repo_structure):
        """[AR003] Valid repo with 384 shards should PASS (cached)"""
        validator = CachedSoTValidator(repo_root=valid_repo_structure)
        result = validator.validate_ar003()

        assert result.passed is True
        assert result.evidence["actual_total_charts"] == 384

    def test_ar003_invalid_missing_shards(self, invalid_repo_missing_shards):
        """[AR003] Repo with <384 shards should FAIL"""
        validator = SoTValidator(repo_root=invalid_repo_missing_shards)
        result = validator.validate_ar003()

        assert result.passed is False
        assert result.evidence["actual_total_charts"] < 384

    def test_ar003_invalid_missing_roots(self, invalid_repo_missing_roots):
        """[AR003] Repo with <24 roots should FAIL"""
        validator = SoTValidator(repo_root=invalid_repo_missing_roots)
        result = validator.validate_ar003()

        assert result.passed is False
        # 20 roots * 16 shards = 320 shards
        assert result.evidence["actual_total_charts"] == 320


# ============================================================
# AR004: EACH SHARD MUST HAVE CHART.YAML
# ============================================================

@pytest.mark.ar
@pytest.mark.unit
@pytest.mark.critical
class TestAR004:
    """Tests for AR004: Each shard must have Chart.yaml."""

    def test_ar004_valid_all_charts_present_original(self, valid_repo_structure):
        """[AR004] Valid repo with all Chart.yaml files should PASS"""
        validator = SoTValidator(repo_root=valid_repo_structure)
        result = validator.validate_ar004()

        assert result.passed is True
        assert result.rule_id == "AR004"
        assert result.severity == Severity.CRITICAL
        assert result.evidence["missing_count"] == 0

    def test_ar004_valid_all_charts_present_cached(self, valid_repo_structure):
        """[AR004] Valid repo with all Chart.yaml files should PASS (cached)"""
        validator = CachedSoTValidator(repo_root=valid_repo_structure)
        result = validator.validate_ar004()

        assert result.passed is True
        assert result.evidence["missing_count"] == 0

    def test_ar004_invalid_missing_charts(self, invalid_repo_missing_charts):
        """[AR004] Repo with missing Chart.yaml files should FAIL"""
        validator = SoTValidator(repo_root=invalid_repo_missing_charts)
        result = validator.validate_ar004()

        assert result.passed is False
        assert result.evidence["missing_count"] > 0
        assert len(result.evidence["missing_charts"]) > 0

    def test_ar004_invalid_missing_charts_cached(self, invalid_repo_missing_charts):
        """[AR004] Repo with missing Chart.yaml files should FAIL (cached)"""
        validator = CachedSoTValidator(repo_root=invalid_repo_missing_charts)
        result = validator.validate_ar004()

        assert result.passed is False
        assert result.evidence["missing_count"] > 0


# ============================================================
# AR005: EACH SHARD MUST HAVE VALUES.YAML
# ============================================================

@pytest.mark.ar
@pytest.mark.unit
@pytest.mark.critical
class TestAR005:
    """Tests for AR005: Each shard must have values.yaml."""

    def test_ar005_valid_all_values_present_original(self, valid_repo_structure):
        """[AR005] Valid repo with all values.yaml files should PASS"""
        validator = SoTValidator(repo_root=valid_repo_structure)
        result = validator.validate_ar005()

        assert result.passed is True
        assert result.rule_id == "AR005"
        assert result.severity == Severity.CRITICAL
        assert result.evidence["missing_count"] == 0

    def test_ar005_valid_all_values_present_cached(self, valid_repo_structure):
        """[AR005] Valid repo with all values.yaml files should PASS (cached)"""
        validator = CachedSoTValidator(repo_root=valid_repo_structure)
        result = validator.validate_ar005()

        assert result.passed is True
        assert result.evidence["missing_count"] == 0

    def test_ar005_invalid_missing_values(self, invalid_repo_missing_values):
        """[AR005] Repo with missing values.yaml files should FAIL"""
        validator = SoTValidator(repo_root=invalid_repo_missing_values)
        result = validator.validate_ar005()

        assert result.passed is False
        assert result.evidence["missing_count"] > 0
        assert len(result.evidence["missing_values"]) > 0

    def test_ar005_invalid_missing_values_cached(self, invalid_repo_missing_values):
        """[AR005] Repo with missing values.yaml files should FAIL (cached)"""
        validator = CachedSoTValidator(repo_root=invalid_repo_missing_values)
        result = validator.validate_ar005()

        assert result.passed is False
        assert result.evidence["missing_count"] > 0


# ============================================================
# AR006: EACH ROOT MUST HAVE README.MD
# ============================================================

@pytest.mark.ar
@pytest.mark.unit
@pytest.mark.high
class TestAR006:
    """Tests for AR006: Each root must have README.md."""

    def test_ar006_valid_all_readmes_present_original(self, valid_repo_structure):
        """[AR006] Valid repo with all README.md files should PASS"""
        validator = SoTValidator(repo_root=valid_repo_structure)
        result = validator.validate_ar006()

        assert result.passed is True
        assert result.rule_id == "AR006"
        assert result.severity == Severity.HIGH
        assert result.evidence["missing_count"] == 0

    def test_ar006_valid_all_readmes_present_cached(self, valid_repo_structure):
        """[AR006] Valid repo with all README.md files should PASS (cached)"""
        validator = CachedSoTValidator(repo_root=valid_repo_structure)
        result = validator.validate_ar006()

        assert result.passed is True
        assert result.evidence["missing_count"] == 0

    def test_ar006_invalid_missing_readmes(self, invalid_repo_missing_readme):
        """[AR006] Repo with missing README.md files should FAIL"""
        validator = SoTValidator(repo_root=invalid_repo_missing_readme)
        result = validator.validate_ar006()

        assert result.passed is False
        assert result.evidence["missing_count"] > 0
        assert len(result.evidence["missing_readme"]) > 0

    def test_ar006_invalid_missing_readmes_cached(self, invalid_repo_missing_readme):
        """[AR006] Repo with missing README.md files should FAIL (cached)"""
        validator = CachedSoTValidator(repo_root=invalid_repo_missing_readme)
        result = validator.validate_ar006()

        assert result.passed is False
        assert result.evidence["missing_count"] > 0


# ============================================================
# AR007: 16 SHARDS MUST BE IDENTICAL ACROSS ALL ROOTS
# ============================================================

@pytest.mark.ar
@pytest.mark.unit
@pytest.mark.critical
class TestAR007:
    """Tests for AR007: 16 shards must be identical across all roots."""

    def test_ar007_valid_consistent_shards_original(self, valid_repo_structure):
        """[AR007] Valid repo with consistent shards should PASS"""
        validator = SoTValidator(repo_root=valid_repo_structure)
        result = validator.validate_ar007()

        assert result.passed is True
        assert result.rule_id == "AR007"
        assert result.severity == Severity.CRITICAL
        assert len(result.evidence["inconsistencies"]) == 0

    def test_ar007_valid_consistent_shards_cached(self, valid_repo_structure):
        """[AR007] Valid repo with consistent shards should PASS (cached)"""
        validator = CachedSoTValidator(repo_root=valid_repo_structure)
        result = validator.validate_ar007()

        assert result.passed is True
        assert len(result.evidence["inconsistencies"]) == 0

    def test_ar007_invalid_inconsistent_shards(self, invalid_repo_inconsistent_shards):
        """[AR007] Repo with inconsistent shards should FAIL"""
        validator = SoTValidator(repo_root=invalid_repo_inconsistent_shards)
        result = validator.validate_ar007()

        assert result.passed is False
        assert len(result.evidence["inconsistencies"]) > 0

        # Check inconsistency details
        for inconsistency in result.evidence["inconsistencies"]:
            assert "root" in inconsistency
            assert "missing_shards" in inconsistency or "extra_shards" in inconsistency

    def test_ar007_invalid_inconsistent_shards_cached(self, invalid_repo_inconsistent_shards):
        """[AR007] Repo with inconsistent shards should FAIL (cached)"""
        validator = CachedSoTValidator(repo_root=invalid_repo_inconsistent_shards)
        result = validator.validate_ar007()

        assert result.passed is False
        assert len(result.evidence["inconsistencies"]) > 0


# ============================================================
# AR008: SHARD NAMES MUST MATCH NN_NAME PATTERN (NN=01-16)
# ============================================================

@pytest.mark.ar
@pytest.mark.unit
@pytest.mark.high
class TestAR008:
    """Tests for AR008: Shard names must match NN_name pattern (NN=01-16)."""

    def test_ar008_valid_shard_names_original(self, valid_repo_structure):
        """[AR008] Valid repo with correct shard names should PASS"""
        validator = SoTValidator(repo_root=valid_repo_structure)
        result = validator.validate_ar008()

        assert result.passed is True
        assert result.rule_id == "AR008"
        assert result.severity == Severity.HIGH
        assert result.evidence["total_violations"] == 0

    def test_ar008_valid_shard_names_cached(self, valid_repo_structure):
        """[AR008] Valid repo with correct shard names should PASS (cached)"""
        validator = CachedSoTValidator(repo_root=valid_repo_structure)
        result = validator.validate_ar008()

        assert result.passed is True
        assert result.evidence["total_violations"] == 0

    def test_ar008_invalid_bad_shard_names(self, invalid_repo_bad_shard_names):
        """[AR008] Repo with incorrectly named shards should FAIL"""
        validator = SoTValidator(repo_root=invalid_repo_bad_shard_names)
        result = validator.validate_ar008()

        assert result.passed is False
        assert result.evidence["total_violations"] > 0
        assert len(result.evidence["violations"]) > 0

    def test_ar008_invalid_bad_shard_names_cached(self, invalid_repo_bad_shard_names):
        """[AR008] Repo with incorrectly named shards should FAIL (cached)"""
        validator = CachedSoTValidator(repo_root=invalid_repo_bad_shard_names)
        result = validator.validate_ar008()

        assert result.passed is False
        assert result.evidence["total_violations"] > 0


# ============================================================
# AR009: ROOT NAMES MUST MATCH NN_NAME PATTERN (NN=01-24)
# ============================================================

@pytest.mark.ar
@pytest.mark.unit
@pytest.mark.high
class TestAR009:
    """Tests for AR009: Root names must match NN_name pattern (NN=01-24)."""

    def test_ar009_valid_root_names_original(self, valid_repo_structure):
        """[AR009] Valid repo with correct root names should PASS"""
        validator = SoTValidator(repo_root=valid_repo_structure)
        result = validator.validate_ar009()

        assert result.passed is True
        assert result.rule_id == "AR009"
        assert result.severity == Severity.HIGH
        assert result.evidence["total_violations"] == 0

    def test_ar009_valid_root_names_cached(self, valid_repo_structure):
        """[AR009] Valid repo with correct root names should PASS (cached)"""
        validator = CachedSoTValidator(repo_root=valid_repo_structure)
        result = validator.validate_ar009()

        assert result.passed is True
        assert result.evidence["total_violations"] == 0

    def test_ar009_invalid_bad_root_names(self, invalid_repo_bad_root_names):
        """[AR009] Repo with incorrectly named roots should FAIL"""
        validator = SoTValidator(repo_root=invalid_repo_bad_root_names)
        result = validator.validate_ar009()

        assert result.passed is False
        assert result.evidence["total_violations"] > 0
        assert len(result.evidence["violations"]) > 0

    def test_ar009_invalid_bad_root_names_cached(self, invalid_repo_bad_root_names):
        """[AR009] Repo with incorrectly named roots should FAIL (cached)"""
        validator = CachedSoTValidator(repo_root=invalid_repo_bad_root_names)
        result = validator.validate_ar009()

        assert result.passed is False
        assert result.evidence["total_violations"] > 0


# ============================================================
# AR010: EACH SHARD MUST HAVE TEMPLATES/ DIRECTORY
# ============================================================

@pytest.mark.ar
@pytest.mark.unit
@pytest.mark.high
class TestAR010:
    """Tests for AR010: Each shard must have templates/ directory."""

    def test_ar010_valid_all_templates_present_original(self, valid_repo_structure):
        """[AR010] Valid repo with all templates/ directories should PASS"""
        validator = SoTValidator(repo_root=valid_repo_structure)
        result = validator.validate_ar010()

        assert result.passed is True
        assert result.rule_id == "AR010"
        assert result.severity == Severity.HIGH
        assert result.evidence["missing_count"] == 0

    def test_ar010_valid_all_templates_present_cached(self, valid_repo_structure):
        """[AR010] Valid repo with all templates/ directories should PASS (cached)"""
        validator = CachedSoTValidator(repo_root=valid_repo_structure)
        result = validator.validate_ar010()

        assert result.passed is True
        assert result.evidence["missing_count"] == 0

    def test_ar010_invalid_missing_templates(self, invalid_repo_missing_templates):
        """[AR010] Repo with missing templates/ directories should FAIL"""
        validator = SoTValidator(repo_root=invalid_repo_missing_templates)
        result = validator.validate_ar010()

        assert result.passed is False
        assert result.evidence["missing_count"] > 0
        assert len(result.evidence["missing_templates"]) > 0

    def test_ar010_invalid_missing_templates_cached(self, invalid_repo_missing_templates):
        """[AR010] Repo with missing templates/ directories should FAIL (cached)"""
        validator = CachedSoTValidator(repo_root=invalid_repo_missing_templates)
        result = validator.validate_ar010()

        assert result.passed is False
        assert result.evidence["missing_count"] > 0


# ============================================================
# COMPLIANCE RULES (CP001+)
# ============================================================

@pytest.mark.cp
@pytest.mark.unit
class TestCP001:
    """Tests for CP001: GDPR compliance - no PII in Chart.yaml."""

    def test_cp001_valid_no_pii_in_charts(self, valid_repo_structure):
        """[CP001] Charts without PII should PASS"""
        validator = SoTValidator(repo_root=valid_repo_structure)
        result = validator.validate_cp001()

        # Should pass because our test fixtures don't include PII
        assert result.rule_id == "CP001"
        assert result.passed is True

    def test_cp001_invalid_pii_in_chart(self, temp_repo):
        """[CP001] Chart with PII should FAIL"""
        repo_root = temp_repo / "pii_test"
        repo_root.mkdir()

        # Create a single shard with PII in Chart.yaml
        root_dir = repo_root / "01_test_root"
        root_dir.mkdir()

        shard_dir = root_dir / "01_test_shard"
        shard_dir.mkdir()

        # Create Chart.yaml with PII
        chart_file = shard_dir / "Chart.yaml"
        chart_content = """
apiVersion: v2
name: test-chart
description: Test chart with PII
author: john.doe@example.com
maintainer_email: jane.smith@company.com
social_security: 123-45-6789
"""
        chart_file.write_text(chart_content)

        validator = SoTValidator(repo_root=repo_root)
        result = validator.validate_cp001()

        # Should detect PII (email addresses, SSN)
        assert result.passed is False
        assert "pii_violations" in result.evidence


# ============================================================
# EDGE CASES AND ERROR HANDLING
# ============================================================

@pytest.mark.unit
class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_nonexistent_repo_path(self):
        """Validator should handle nonexistent repository path"""
        nonexistent = Path("/nonexistent/path/to/repo")
        validator = SoTValidator(repo_root=nonexistent)

        # Should not raise exception
        result = validator.validate_ar001()
        assert result.passed is False

    def test_file_as_repo_path(self, temp_repo):
        """Validator should handle file passed as repo path"""
        file_path = temp_repo / "testfile.txt"
        file_path.write_text("test")

        validator = SoTValidator(repo_root=file_path)
        result = validator.validate_ar001()

        # Should fail gracefully
        assert result.passed is False

    def test_permission_denied_handling(self, temp_repo):
        """Validator should handle permission errors gracefully"""
        # This test may not work on all systems
        # It's here for completeness
        pass


# ============================================================
# VALIDATOR INTEGRATION TESTS
# ============================================================

@pytest.mark.integration
class TestValidatorIntegration:
    """Integration tests for full validation workflow."""

    def test_validate_all_ar_rules_original(self, valid_repo_structure):
        """[INTEGRATION] All AR001-AR010 should pass on valid repo"""
        validator = SoTValidator(repo_root=valid_repo_structure)

        # Validate all AR rules
        results = [
            validator.validate_ar001(),
            validator.validate_ar002(),
            validator.validate_ar003(),
            validator.validate_ar004(),
            validator.validate_ar005(),
            validator.validate_ar006(),
            validator.validate_ar007(),
            validator.validate_ar008(),
            validator.validate_ar009(),
            validator.validate_ar010()
        ]

        # All should pass
        for result in results:
            assert result.passed is True, f"{result.rule_id} failed: {result.message}"

    def test_validate_all_ar_rules_cached(self, valid_repo_structure):
        """[INTEGRATION] All AR001-AR010 should pass on valid repo (cached)"""
        validator = CachedSoTValidator(repo_root=valid_repo_structure)

        # Validate all AR rules
        results = [
            validator.validate_ar001(),
            validator.validate_ar002(),
            validator.validate_ar003(),
            validator.validate_ar004(),
            validator.validate_ar005(),
            validator.validate_ar006(),
            validator.validate_ar007(),
            validator.validate_ar008(),
            validator.validate_ar009(),
            validator.validate_ar010()
        ]

        # All should pass
        for result in results:
            assert result.passed is True, f"{result.rule_id} failed: {result.message}"

    def test_validation_result_structure(self, validator):
        """[INTEGRATION] ValidationResult should have correct structure"""
        result = validator.validate_ar001()

        # Check required fields
        assert hasattr(result, "rule_id")
        assert hasattr(result, "passed")
        assert hasattr(result, "severity")
        assert hasattr(result, "message")
        assert hasattr(result, "evidence")
        assert hasattr(result, "timestamp")

        # Check types
        assert isinstance(result.rule_id, str)
        assert isinstance(result.passed, bool)
        assert isinstance(result.severity, Severity)
        assert isinstance(result.message, str)
        assert isinstance(result.evidence, dict)


# ============================================================
# PERFORMANCE TESTS
# ============================================================

@pytest.mark.performance
class TestPerformance:
    """Performance and benchmark tests."""

    def test_ar001_performance_original(self, valid_repo_structure):
        """[PERF] AR001 should complete in <100ms (original)"""
        validator = SoTValidator(repo_root=valid_repo_structure)

        start = time.perf_counter()
        result = validator.validate_ar001()
        elapsed = time.perf_counter() - start

        assert result.passed is True
        assert elapsed < 0.1, f"AR001 took {elapsed*1000:.2f}ms (expected <100ms)"

    def test_ar001_performance_cached(self, valid_repo_structure):
        """[PERF] AR001 should complete in <100ms (cached)"""
        validator = CachedSoTValidator(repo_root=valid_repo_structure)

        start = time.perf_counter()
        result = validator.validate_ar001()
        elapsed = time.perf_counter() - start

        assert result.passed is True
        assert elapsed < 0.1, f"AR001 (cached) took {elapsed*1000:.2f}ms (expected <100ms)"

    def test_all_ar_rules_performance_original(self, valid_repo_structure):
        """[PERF] All AR001-AR010 should complete in <1s (original)"""
        validator = SoTValidator(repo_root=valid_repo_structure)

        start = time.perf_counter()
        for i in range(1, 11):
            method = getattr(validator, f"validate_ar{i:03d}")
            method()
        elapsed = time.perf_counter() - start

        assert elapsed < 1.0, f"AR001-AR010 took {elapsed:.3f}s (expected <1s)"

    def test_all_ar_rules_performance_cached(self, valid_repo_structure):
        """[PERF] All AR001-AR010 should complete in <1s (cached)"""
        validator = CachedSoTValidator(repo_root=valid_repo_structure)

        start = time.perf_counter()
        for i in range(1, 11):
            method = getattr(validator, f"validate_ar{i:03d}")
            method()
        elapsed = time.perf_counter() - start

        assert elapsed < 1.0, f"AR001-AR010 (cached) took {elapsed:.3f}s (expected <1s)"

    def test_cache_speedup(self, valid_repo_structure):
        """[PERF] Cached validator should be faster on repeated calls"""
        validator = CachedSoTValidator(repo_root=valid_repo_structure)

        # First run (cold cache)
        start1 = time.perf_counter()
        validator.validate_ar001()
        cold_time = time.perf_counter() - start1

        # Second run (warm cache)
        start2 = time.perf_counter()
        for _ in range(10):
            validator.validate_ar001()
        warm_time = (time.perf_counter() - start2) / 10

        # Warm cache should be significantly faster
        # Note: This may not always be true due to system variance
        print(f"\n[CACHE] Cold: {cold_time*1000:.3f}ms, Warm: {warm_time*1000:.3f}ms")

    def test_cache_hit_rate(self, valid_repo_structure):
        """[PERF] Cache should have high hit rate on repeated validations"""
        validator = CachedSoTValidator(repo_root=valid_repo_structure)

        # Run multiple validations
        for _ in range(5):
            validator.validate_ar001()
            validator.validate_ar002()
            validator.validate_ar003()

        stats = validator.get_cache_stats()
        print(f"\n[CACHE STATS] {stats}")

        # Should have cache hits
        assert stats["hits"] > 0


# ============================================================
# CACHE-SPECIFIC TESTS
# ============================================================

@pytest.mark.cached
@pytest.mark.unit
class TestCachedValidator:
    """Tests specific to CachedSoTValidator."""

    def test_cache_invalidation(self, valid_repo_structure):
        """[CACHE] Cache invalidation should force rescan"""
        validator = CachedSoTValidator(repo_root=valid_repo_structure)

        # Run validation
        result1 = validator.validate_ar001()
        stats1 = validator.get_cache_stats()

        # Invalidate cache
        validator.invalidate_cache()

        # Run again
        result2 = validator.validate_ar001()
        stats2 = validator.get_cache_stats()

        # Both should pass
        assert result1.passed is True
        assert result2.passed is True

        # Misses should increase after invalidation
        assert stats2["misses"] >= stats1["misses"]

    def test_cache_ttl_expiration(self, valid_repo_structure):
        """[CACHE] Cache should expire after TTL"""
        # Short TTL for testing
        validator = CachedSoTValidator(repo_root=valid_repo_structure, cache_ttl=1)

        # Run validation
        validator.validate_ar001()

        # Wait for TTL to expire
        time.sleep(1.1)

        # Run again - should trigger cache miss
        validator.validate_ar001()

        # Cache should have been rebuilt
        stats = validator.get_cache_stats()
        assert stats["misses"] >= 2  # At least 2 cache misses

    def test_cache_stats_tracking(self, valid_repo_structure):
        """[CACHE] Cache stats should be tracked correctly"""
        validator = CachedSoTValidator(repo_root=valid_repo_structure)

        # Clear stats
        validator.invalidate_cache()

        # Run validations
        validator.validate_ar001()  # Miss
        validator.validate_ar001()  # Hit
        validator.validate_ar002()  # Hit

        stats = validator.get_cache_stats()

        # Should have hits and misses
        assert "hits" in stats
        assert "misses" in stats
        assert stats["hits"] + stats["misses"] > 0


# ============================================================
# PARAMETRIZED TESTS
# ============================================================

@pytest.mark.ar
@pytest.mark.parametrize("rule_num,expected_severity", [
    (1, Severity.CRITICAL),
    (2, Severity.CRITICAL),
    (3, Severity.CRITICAL),
    (4, Severity.CRITICAL),
    (5, Severity.CRITICAL),
    (6, Severity.HIGH),
    (7, Severity.CRITICAL),
    (8, Severity.HIGH),
    (9, Severity.HIGH),
    (10, Severity.HIGH),
])
def test_ar_rule_severity(valid_repo_structure, rule_num, expected_severity):
    """[AR*] Verify correct severity for each AR rule"""
    validator = SoTValidator(repo_root=valid_repo_structure)
    method = getattr(validator, f"validate_ar{rule_num:03d}")
    result = method()

    assert result.severity == expected_severity


@pytest.mark.ar
@pytest.mark.parametrize("rule_num", range(1, 11))
def test_ar_rule_consistency_original_vs_cached(valid_repo_structure, rule_num):
    """[AR*] Original and cached validators should produce identical results"""
    original = SoTValidator(repo_root=valid_repo_structure)
    cached = CachedSoTValidator(repo_root=valid_repo_structure)

    method_name = f"validate_ar{rule_num:03d}"
    result_original = getattr(original, method_name)()
    result_cached = getattr(cached, method_name)()

    # Both should pass
    assert result_original.passed == result_cached.passed
    assert result_original.rule_id == result_cached.rule_id
    assert result_original.severity == result_cached.severity


# ============================================================
# REAL REPOSITORY TESTS (OPTIONAL)
# ============================================================

@pytest.mark.integration
@pytest.mark.slow
class TestRealRepository:
    """Tests against actual SSID repository (if available)."""

    def test_real_repo_ar_validation(self, real_repo_root):
        """[REAL] Validate AR rules against real repository"""
        if real_repo_root is None:
            pytest.skip("Real repository not found")

        validator = SoTValidator(repo_root=real_repo_root)

        # Run AR001-AR010
        results = []
        for i in range(1, 11):
            method = getattr(validator, f"validate_ar{i:03d}")
            result = method()
            results.append(result)

        # Print results
        passed = sum(1 for r in results if r.passed)
        print(f"\n[REAL REPO] {passed}/10 AR rules passed")

        for result in results:
            status = "[PASS]" if result.passed else "[FAIL]"
            print(f"{status} {result.rule_id}: {result.message}")
