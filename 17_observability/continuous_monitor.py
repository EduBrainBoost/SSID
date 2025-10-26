#!/usr/bin/env python3
"""
SSID Continuous Monitor
=======================

Continuously monitors system health, detects drift, and identifies issues.

Monitors:
- File integrity and completeness
- Test coverage and pass rates
- Performance metrics and degradation
- Configuration drift
- Security violations
- Dependency health

Author: SSID Autonomous System
Version: 1.0.0
License: ROOT-LOCKED
"""

import hashlib
import json
import logging
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "24_meta_orchestration"))

from autonomous_controller import (
    HealthReport, Issue, IssueType, SystemStatus
)

logger = logging.getLogger('ContinuousMonitor')


class ContinuousMonitor:
    """
    Continuous monitoring system for health checks and drift detection
    """

    def __init__(self, base_dir: Path):
        self.base_dir = Path(base_dir)
        self.cache_dir = self.base_dir / ".ssid_cache"
        self.cache_dir.mkdir(exist_ok=True)

        # Load reference hashes
        self.reference_hashes = self._load_reference_hashes()

        # Critical files that must exist
        self.critical_files = [
            "16_codex/contracts/sot/sot_contract.yaml",
            "03_core/validators/sot/sot_validator_core.py",
            "23_compliance/policies/sot/sot_policy.rego",
            "11_test_simulation/tests_compliance/test_sot_validator.py"
        ]

        # Performance thresholds
        self.performance_thresholds = {
            "test_execution_time_ms": 5000,
            "validation_time_ms": 1000,
            "memory_usage_mb": 512,
            "cpu_usage_percent": 80
        }

        logger.info("Continuous Monitor initialized")

    def check_health(self) -> HealthReport:
        """
        Comprehensive health check of the entire system
        """
        logger.info("Starting comprehensive health check...")

        issues = []
        metrics = {}

        # 1. File integrity checks
        file_issues = self._check_file_integrity()
        issues.extend(file_issues)
        metrics["file_integrity_issues"] = len(file_issues)

        # 2. Test health checks
        test_issues, test_metrics = self._check_test_health()
        issues.extend(test_issues)
        metrics.update(test_metrics)

        # 3. Validation health
        validation_issues, validation_metrics = self._check_validation_health()
        issues.extend(validation_issues)
        metrics.update(validation_metrics)

        # 4. Performance monitoring
        perf_issues, perf_metrics = self._check_performance()
        issues.extend(perf_issues)
        metrics.update(perf_metrics)

        # 5. Configuration drift detection
        drift_issues = self._check_configuration_drift()
        issues.extend(drift_issues)
        metrics["configuration_drift_count"] = len(drift_issues)

        # 6. Security checks
        security_issues = self._check_security()
        issues.extend(security_issues)
        metrics["security_violations"] = len(security_issues)

        # 7. Dependency health
        dep_issues = self._check_dependencies()
        issues.extend(dep_issues)
        metrics["dependency_issues"] = len(dep_issues)

        # Determine overall status
        status = self._determine_status(issues)

        # Generate recommendations
        recommendations = self._generate_recommendations(issues, metrics)

        report = HealthReport(
            status=status,
            timestamp=datetime.now().isoformat(),
            issues=issues,
            metrics=metrics,
            recommendations=recommendations
        )

        logger.info(f"Health check complete: {status.value}, {len(issues)} issues detected")

        return report

    def _check_file_integrity(self) -> List[Issue]:
        """Check that critical files exist and haven't been corrupted"""
        issues = []

        for file_path in self.critical_files:
            full_path = self.base_dir / file_path

            if not full_path.exists():
                issues.append(Issue(
                    type=IssueType.MISSING_FILE,
                    severity="CRITICAL",
                    description=f"Critical file missing: {file_path}",
                    component="file_system",
                    timestamp=datetime.now().isoformat(),
                    metadata={"file": file_path},
                    auto_fixable=True
                ))
                continue

            # Check file hash against reference
            if file_path in self.reference_hashes:
                current_hash = self._compute_file_hash(full_path)
                expected_hash = self.reference_hashes[file_path]

                if current_hash != expected_hash:
                    # File modified - check if it's a legitimate update
                    issues.append(Issue(
                        type=IssueType.CONFIGURATION_DRIFT,
                        severity="MEDIUM",
                        description=f"File modified: {file_path}",
                        component="file_system",
                        timestamp=datetime.now().isoformat(),
                        metadata={
                            "file": file_path,
                            "expected_hash": expected_hash,
                            "current_hash": current_hash
                        },
                        auto_fixable=False  # Manual review needed
                    ))

        return issues

    def _check_test_health(self) -> tuple[List[Issue], Dict[str, Any]]:
        """Check test suite health and coverage"""
        issues = []
        metrics = {
            "test_files_found": 0,
            "total_tests": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "test_coverage_percent": 0.0
        }

        # Find all test files
        test_dirs = [
            self.base_dir / "11_test_simulation" / "tests_compliance",
            self.base_dir / "11_test_simulation" / "tests_sot",
            self.base_dir / "11_test_simulation" / "tests_complete"
        ]

        test_files = []
        for test_dir in test_dirs:
            if test_dir.exists():
                test_files.extend(test_dir.glob("test_*.py"))

        metrics["test_files_found"] = len(test_files)

        if len(test_files) == 0:
            issues.append(Issue(
                type=IssueType.TEST_FAILURE,
                severity="HIGH",
                description="No test files found",
                component="testing",
                timestamp=datetime.now().isoformat(),
                metadata={},
                auto_fixable=False
            ))

        # Check for coverage report
        coverage_file = self.base_dir / "23_compliance" / "evidence" / "coverage" / "coverage.xml"
        if coverage_file.exists():
            coverage = self._parse_coverage_report(coverage_file)
            metrics["test_coverage_percent"] = coverage

            if coverage < 80:
                issues.append(Issue(
                    type=IssueType.TEST_FAILURE,
                    severity="MEDIUM",
                    description=f"Test coverage below threshold: {coverage:.1f}%",
                    component="testing",
                    timestamp=datetime.now().isoformat(),
                    metadata={"coverage": coverage, "threshold": 80},
                    auto_fixable=True
                ))

        return issues, metrics

    def _check_validation_health(self) -> tuple[List[Issue], Dict[str, Any]]:
        """Check validation system health"""
        issues = []
        metrics = {
            "validators_found": 0,
            "validation_rules": 0,
            "validation_errors": 0
        }

        # Check for validator files
        validator_dir = self.base_dir / "03_core" / "validators" / "sot"
        if not validator_dir.exists():
            issues.append(Issue(
                type=IssueType.MISSING_FILE,
                severity="CRITICAL",
                description="Validator directory missing",
                component="validators",
                timestamp=datetime.now().isoformat(),
                metadata={"directory": str(validator_dir)},
                auto_fixable=True
            ))
            return issues, metrics

        validator_files = list(validator_dir.glob("*.py"))
        metrics["validators_found"] = len(validator_files)

        # Check SOT contract
        contract_file = self.base_dir / "16_codex" / "contracts" / "sot" / "sot_contract.yaml"
        if contract_file.exists():
            try:
                import yaml
                with open(contract_file, 'r', encoding='utf-8') as f:
                    contract = yaml.safe_load(f)

                # Count rules in contract
                rules_count = 0
                if isinstance(contract, dict):
                    for section, content in contract.items():
                        if isinstance(content, dict) and 'rules' in content:
                            rules_count += len(content['rules'])
                        elif isinstance(content, list):
                            rules_count += len(content)

                metrics["validation_rules"] = rules_count

                if rules_count == 0:
                    issues.append(Issue(
                        type=IssueType.VALIDATION_ERROR,
                        severity="HIGH",
                        description="No validation rules found in contract",
                        component="validators",
                        timestamp=datetime.now().isoformat(),
                        metadata={},
                        auto_fixable=False
                    ))

            except Exception as e:
                issues.append(Issue(
                    type=IssueType.VALIDATION_ERROR,
                    severity="HIGH",
                    description=f"Failed to parse SOT contract: {str(e)}",
                    component="validators",
                    timestamp=datetime.now().isoformat(),
                    metadata={"error": str(e)},
                    auto_fixable=False
                ))

        return issues, metrics

    def _check_performance(self) -> tuple[List[Issue], Dict[str, Any]]:
        """Monitor system performance metrics"""
        issues = []
        metrics = {
            "memory_usage_mb": 0,
            "cpu_usage_percent": 0,
            "disk_usage_percent": 0
        }

        try:
            import psutil

            # Memory usage
            memory = psutil.virtual_memory()
            metrics["memory_usage_mb"] = memory.used / (1024 * 1024)

            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            metrics["cpu_usage_percent"] = cpu_percent

            # Disk usage
            disk = psutil.disk_usage(str(self.base_dir))
            metrics["disk_usage_percent"] = disk.percent

            # Check thresholds
            if metrics["memory_usage_mb"] > self.performance_thresholds["memory_usage_mb"]:
                issues.append(Issue(
                    type=IssueType.PERFORMANCE_DEGRADATION,
                    severity="MEDIUM",
                    description=f"High memory usage: {metrics['memory_usage_mb']:.0f}MB",
                    component="performance",
                    timestamp=datetime.now().isoformat(),
                    metadata={"value": metrics["memory_usage_mb"], "threshold": self.performance_thresholds["memory_usage_mb"]},
                    auto_fixable=True
                ))

            if cpu_percent > self.performance_thresholds["cpu_usage_percent"]:
                issues.append(Issue(
                    type=IssueType.PERFORMANCE_DEGRADATION,
                    severity="MEDIUM",
                    description=f"High CPU usage: {cpu_percent:.1f}%",
                    component="performance",
                    timestamp=datetime.now().isoformat(),
                    metadata={"value": cpu_percent, "threshold": self.performance_thresholds["cpu_usage_percent"]},
                    auto_fixable=True
                ))

        except ImportError:
            logger.warning("psutil not available, skipping performance monitoring")
        except Exception as e:
            logger.error(f"Performance monitoring error: {e}")

        return issues, metrics

    def _check_configuration_drift(self) -> List[Issue]:
        """Detect configuration drift from expected state"""
        issues = []

        # Check for expected directory structure
        expected_dirs = [
            "01_ai_layer",
            "02_audit_logging",
            "03_core/validators/sot",
            "11_test_simulation",
            "16_codex/contracts/sot",
            "23_compliance/policies/sot",
            "24_meta_orchestration"
        ]

        for dir_path in expected_dirs:
            full_path = self.base_dir / dir_path
            if not full_path.exists():
                issues.append(Issue(
                    type=IssueType.CONFIGURATION_DRIFT,
                    severity="HIGH",
                    description=f"Expected directory missing: {dir_path}",
                    component="configuration",
                    timestamp=datetime.now().isoformat(),
                    metadata={"directory": dir_path},
                    auto_fixable=True
                ))

        return issues

    def _check_security(self) -> List[Issue]:
        """Check for security violations"""
        issues = []

        # Check for exposed secrets
        secret_patterns = [
            r'(?i)(api[_-]?key|password|secret|token)\s*[:=]\s*["\']?[a-zA-Z0-9]{20,}',
            r'(?i)-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----'
        ]

        # Scan critical files for secrets
        for py_file in self.base_dir.rglob("*.py"):
            if ".git" in str(py_file) or "venv" in str(py_file):
                continue

            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')
                for pattern in secret_patterns:
                    if re.search(pattern, content):
                        issues.append(Issue(
                            type=IssueType.SECURITY_VIOLATION,
                            severity="CRITICAL",
                            description=f"Potential secret exposed in {py_file.name}",
                            component="security",
                            timestamp=datetime.now().isoformat(),
                            metadata={"file": str(py_file.relative_to(self.base_dir))},
                            auto_fixable=False
                        ))
                        break
            except Exception:
                pass

        return issues

    def _check_dependencies(self) -> List[Issue]:
        """Check dependency health"""
        issues = []

        requirements_file = self.base_dir / "requirements.txt"
        if not requirements_file.exists():
            issues.append(Issue(
                type=IssueType.DEPENDENCY_ISSUE,
                severity="MEDIUM",
                description="requirements.txt not found",
                component="dependencies",
                timestamp=datetime.now().isoformat(),
                metadata={},
                auto_fixable=True
            ))
            return issues

        # Check if dependencies are installed
        try:
            result = subprocess.run(
                ["pip", "list", "--format=json"],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                installed = json.loads(result.stdout)
                installed_packages = {pkg["name"].lower() for pkg in installed}

                # Check critical dependencies
                critical_deps = ["pyyaml", "pytest", "jsonschema"]
                for dep in critical_deps:
                    if dep.lower() not in installed_packages:
                        issues.append(Issue(
                            type=IssueType.DEPENDENCY_ISSUE,
                            severity="HIGH",
                            description=f"Critical dependency missing: {dep}",
                            component="dependencies",
                            timestamp=datetime.now().isoformat(),
                            metadata={"package": dep},
                            auto_fixable=True
                        ))

        except Exception as e:
            logger.error(f"Dependency check failed: {e}")

        return issues

    def _determine_status(self, issues: List[Issue]) -> SystemStatus:
        """Determine overall system status based on issues"""
        if not issues:
            return SystemStatus.HEALTHY

        severity_counts = {
            "CRITICAL": sum(1 for i in issues if i.severity == "CRITICAL"),
            "HIGH": sum(1 for i in issues if i.severity == "HIGH"),
            "MEDIUM": sum(1 for i in issues if i.severity == "MEDIUM"),
            "LOW": sum(1 for i in issues if i.severity == "LOW")
        }

        if severity_counts["CRITICAL"] > 0:
            return SystemStatus.CRITICAL
        elif severity_counts["HIGH"] > 2:
            return SystemStatus.CRITICAL
        elif severity_counts["HIGH"] > 0 or severity_counts["MEDIUM"] > 5:
            return SystemStatus.DEGRADED
        else:
            return SystemStatus.HEALTHY

    def _generate_recommendations(self, issues: List[Issue], metrics: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations based on issues and metrics"""
        recommendations = []

        # Issue-based recommendations
        critical_count = sum(1 for i in issues if i.severity == "CRITICAL")
        if critical_count > 0:
            recommendations.append(f"Address {critical_count} critical issues immediately")

        # Metrics-based recommendations
        if metrics.get("test_coverage_percent", 0) < 80:
            recommendations.append("Increase test coverage to at least 80%")

        if metrics.get("security_violations", 0) > 0:
            recommendations.append("Review and remediate security violations")

        if metrics.get("configuration_drift_count", 0) > 0:
            recommendations.append("Sync configuration to expected state")

        if not recommendations:
            recommendations.append("All systems operating within normal parameters")

        return recommendations

    def _load_reference_hashes(self) -> Dict[str, str]:
        """Load reference file hashes"""
        hash_file = self.base_dir / "24_meta_orchestration" / "registry" / "sot_reference_hashes.json"

        if hash_file.exists():
            try:
                with open(hash_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load reference hashes: {e}")

        return {}

    def _compute_file_hash(self, file_path: Path) -> str:
        """Compute SHA-256 hash of a file"""
        sha256 = hashlib.sha256()
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except Exception as e:
            logger.error(f"Failed to hash {file_path}: {e}")
            return ""

    def _parse_coverage_report(self, coverage_file: Path) -> float:
        """Parse coverage percentage from XML report"""
        try:
            import xml.etree.ElementTree as ET
            tree = ET.parse(coverage_file)
            root = tree.getroot()

            # Find coverage element
            coverage_elem = root.find(".//coverage")
            if coverage_elem is not None:
                line_rate = float(coverage_elem.get("line-rate", 0))
                return line_rate * 100

        except Exception as e:
            logger.error(f"Failed to parse coverage report: {e}")

        return 0.0


if __name__ == "__main__":
    # Test the monitor
    base_dir = Path("C:/Users/bibel/Documents/Github/SSID")
    monitor = ContinuousMonitor(base_dir)

    print("Running health check...")
    health = monitor.check_health()

    print(f"\nHealth Status: {health.status.value}")
    print(f"Issues Detected: {len(health.issues)}")
    print(f"\nMetrics:")
    for key, value in health.metrics.items():
        print(f"  {key}: {value}")

    if health.issues:
        print(f"\nTop Issues:")
        for issue in health.issues[:5]:
            print(f"  [{issue.severity}] {issue.description}")

    print(f"\nRecommendations:")
    for rec in health.recommendations:
        print(f"  - {rec}")
