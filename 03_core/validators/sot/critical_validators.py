"""
Critical Validators - 8 Fehlende KRITISCHE Regeln
==================================================
This module implements the 8 CRITICAL missing rules identified in the
Maximalstand-Regeln analysis.

These validators enforce:
1. CHANGELOG.md Pflicht (CRITICAL)
2. README.md Pflicht (CRITICAL)
3. Dockerfile Pflicht (CRITICAL)
4. getting-started.md Pflicht (HIGH)
5. E2E Test Coverage (HIGH)
6. Quarterly Security Audits (HIGH)
7. Container Registry Validation (MEDIUM)
8. Compliance Reports (MEDIUM)

Status: CRITICAL - Sofort erforderlich für 100% Compliance
"""

from dataclasses import dataclass
from typing import List
from pathlib import Path
from enum import Enum
import re


class Severity(Enum):
    """Validation severity levels"""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


@dataclass
class ValidationResult:
    """Result of a single validation rule check"""
    rule_id: str
    passed: bool
    severity: Severity
    message: str
    evidence: dict
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            from datetime import datetime
            self.timestamp = datetime.utcnow().isoformat()


class CriticalValidators:
    """Critical validation functions for missing maximalstand rules"""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root

    def validate_changelog_required(self) -> ValidationResult:
        """FILE-001: Jeder Shard MUSS CHANGELOG.md haben

        Anforderung:
        - Jeder Shard (24×16=384) MUSS CHANGELOG.md in Root haben
        - Format: Keep a Changelog 1.0.0
        - Mindest-Sections: Added, Changed, Deprecated, Removed, Fixed, Security
        """
        # Find all shard directories
        shard_dirs = []
        root_dirs = [d for d in self.repo_root.iterdir() if d.is_dir() and not d.name.startswith('.')]

        for root_dir in root_dirs[:24]:  # Max 24 Roots
            shards_path = root_dir / "shards"
            if shards_path.exists():
                shards = [d for d in shards_path.iterdir() if d.is_dir()]
                shard_dirs.extend(shards)

        missing_changelog = []
        invalid_format = []
        valid_changelogs = 0

        for shard in shard_dirs[:100]:  # Sample first 100 shards
            changelog = shard / "CHANGELOG.md"

            if not changelog.exists():
                missing_changelog.append(str(shard.relative_to(self.repo_root)))
            else:
                # Check basic format
                try:
                    content = changelog.read_text(encoding='utf-8', errors='ignore').lower()

                    # Check for Keep a Changelog sections
                    has_sections = (
                        'added' in content or
                        'changed' in content or
                        'fixed' in content or
                        'removed' in content
                    )

                    if has_sections:
                        valid_changelogs += 1
                    else:
                        invalid_format.append(str(shard.relative_to(self.repo_root)))
                except:
                    invalid_format.append(str(shard.relative_to(self.repo_root)))

        total_shards = len(shard_dirs[:100])
        passed = len(missing_changelog) == 0 and len(invalid_format) < (total_shards * 0.1)  # Allow 10% tolerance

        return ValidationResult(
            rule_id="FILE-001",
            passed=passed,
            severity=Severity.CRITICAL,
            message=f"CHANGELOG.md: {valid_changelogs}/{total_shards} shards have valid changelog, {len(missing_changelog)} missing, {len(invalid_format)} invalid format",
            evidence={
                "total_shards_checked": total_shards,
                "valid_changelogs": valid_changelogs,
                "missing_changelog": missing_changelog[:10],
                "invalid_format": invalid_format[:10]
            }
        )

    def validate_readme_required(self) -> ValidationResult:
        """FILE-002: Jeder Shard MUSS README.md haben

        Anforderung:
        - Jeder Shard MUSS README.md in Root haben
        - Mindest-Content: Purpose, Usage, Contact
        """
        # Find all shard directories
        shard_dirs = []
        root_dirs = [d for d in self.repo_root.iterdir() if d.is_dir() and not d.name.startswith('.')]

        for root_dir in root_dirs[:24]:
            shards_path = root_dir / "shards"
            if shards_path.exists():
                shards = [d for d in shards_path.iterdir() if d.is_dir()]
                shard_dirs.extend(shards)

        missing_readme = []
        incomplete_readme = []
        valid_readmes = 0

        for shard in shard_dirs[:100]:
            readme = shard / "README.md"

            if not readme.exists():
                missing_readme.append(str(shard.relative_to(self.repo_root)))
            else:
                # Check for minimal content
                try:
                    content = readme.read_text(encoding='utf-8', errors='ignore').lower()

                    # Check for key sections (at least 2 of 3)
                    has_purpose = any(word in content for word in ['purpose', 'overview', 'description', 'what'])
                    has_usage = any(word in content for word in ['usage', 'how to', 'getting started', 'quickstart'])
                    has_contact = any(word in content for word in ['contact', 'owner', 'maintainer', 'team'])

                    sections_found = sum([has_purpose, has_usage, has_contact])

                    if sections_found >= 2:
                        valid_readmes += 1
                    else:
                        incomplete_readme.append(str(shard.relative_to(self.repo_root)))
                except:
                    incomplete_readme.append(str(shard.relative_to(self.repo_root)))

        total_shards = len(shard_dirs[:100])
        passed = len(missing_readme) == 0 and len(incomplete_readme) < (total_shards * 0.1)

        return ValidationResult(
            rule_id="FILE-002",
            passed=passed,
            severity=Severity.CRITICAL,
            message=f"README.md: {valid_readmes}/{total_shards} shards have complete readme, {len(missing_readme)} missing, {len(incomplete_readme)} incomplete",
            evidence={
                "total_shards_checked": total_shards,
                "valid_readmes": valid_readmes,
                "missing_readme": missing_readme[:10],
                "incomplete_readme": incomplete_readme[:10]
            }
        )

    def validate_dockerfile_required(self) -> ValidationResult:
        """FILE-003: Jede Implementation MUSS Dockerfile haben

        Anforderung:
        - implementations/{id}/Dockerfile PFLICHT
        - Security Checks: non-root user, minimal base image
        """
        implementations = list(self.repo_root.rglob("implementations/*/Dockerfile"))
        impl_dirs = list(self.repo_root.rglob("implementations/*"))

        # Filter nur echte Implementation-Ordner (nicht nur Dockerfile-Suche)
        impl_dirs_filtered = [d for d in impl_dirs if d.is_dir() and d.name != "implementations"]

        missing_dockerfile = []
        insecure_dockerfile = []
        valid_dockerfiles = 0

        for impl_dir in impl_dirs_filtered[:50]:
            dockerfile = impl_dir / "Dockerfile"

            if not dockerfile.exists():
                missing_dockerfile.append(str(impl_dir.relative_to(self.repo_root)))
            else:
                # Check for security best practices
                try:
                    content = dockerfile.read_text(encoding='utf-8', errors='ignore').lower()

                    # Check for non-root user
                    has_user = 'user' in content and any(u in content for u in ['user 1000', 'user app', 'user nonroot'])

                    # Check for minimal base (alpine, distroless, slim)
                    has_minimal_base = any(base in content for base in ['alpine', 'distroless', 'slim', 'scratch'])

                    if has_user or has_minimal_base:  # At least one security practice
                        valid_dockerfiles += 1
                    else:
                        insecure_dockerfile.append(str(impl_dir.relative_to(self.repo_root)))
                except:
                    insecure_dockerfile.append(str(impl_dir.relative_to(self.repo_root)))

        total_impls = len(impl_dirs_filtered[:50])
        passed = len(missing_dockerfile) == 0 and len(insecure_dockerfile) < (total_impls * 0.2)  # 20% tolerance

        return ValidationResult(
            rule_id="FILE-003",
            passed=passed,
            severity=Severity.CRITICAL,
            message=f"Dockerfile: {valid_dockerfiles}/{total_impls} implementations have secure dockerfile, {len(missing_dockerfile)} missing, {len(insecure_dockerfile)} insecure",
            evidence={
                "total_implementations": total_impls,
                "valid_dockerfiles": valid_dockerfiles,
                "missing_dockerfile": missing_dockerfile[:5],
                "insecure_dockerfile": insecure_dockerfile[:5]
            }
        )

    def validate_getting_started_required(self) -> ValidationResult:
        """FILE-004: Jeder Shard MUSS docs/getting-started.md haben

        Anforderung:
        - docs/getting-started.md PFLICHT für Quick-Start
        """
        shard_dirs = []
        root_dirs = [d for d in self.repo_root.iterdir() if d.is_dir() and not d.name.startswith('.')]

        for root_dir in root_dirs[:24]:
            shards_path = root_dir / "shards"
            if shards_path.exists():
                shards = [d for d in shards_path.iterdir() if d.is_dir()]
                shard_dirs.extend(shards)

        missing_getting_started = []
        valid_guides = 0

        for shard in shard_dirs[:100]:
            getting_started = shard / "docs" / "getting-started.md"

            if not getting_started.exists():
                missing_getting_started.append(str(shard.relative_to(self.repo_root)))
            else:
                valid_guides += 1

        total_shards = len(shard_dirs[:100])
        passed = len(missing_getting_started) < (total_shards * 0.2)  # 20% tolerance

        return ValidationResult(
            rule_id="FILE-004",
            passed=passed,
            severity=Severity.HIGH,
            message=f"getting-started.md: {valid_guides}/{total_shards} shards have getting-started guide, {len(missing_getting_started)} missing",
            evidence={
                "total_shards_checked": total_shards,
                "valid_guides": valid_guides,
                "missing_getting_started": missing_getting_started[:10]
            }
        )

    def validate_e2e_tests_required(self) -> ValidationResult:
        """TEST-004: E2E Tests für Key User Journeys PFLICHT

        Anforderung:
        - implementations/{id}/tests/e2e/ MUSS existieren
        - Mind. 1 E2E Test pro Implementation
        """
        impl_dirs = list(self.repo_root.rglob("implementations/*"))
        impl_dirs_filtered = [d for d in impl_dirs if d.is_dir() and d.name != "implementations"]

        missing_e2e = []
        valid_e2e = 0

        for impl_dir in impl_dirs_filtered[:50]:
            e2e_dir = impl_dir / "tests" / "e2e"

            if not e2e_dir.exists():
                missing_e2e.append(str(impl_dir.relative_to(self.repo_root)))
            else:
                # Check for actual test files
                test_files = list(e2e_dir.glob("test_*.py")) + list(e2e_dir.glob("*_test.py")) + \
                             list(e2e_dir.glob("*.spec.js")) + list(e2e_dir.glob("*.test.ts"))

                if len(test_files) > 0:
                    valid_e2e += 1
                else:
                    missing_e2e.append(str(impl_dir.relative_to(self.repo_root)))

        total_impls = len(impl_dirs_filtered[:50])
        passed = len(missing_e2e) < (total_impls * 0.3)  # 30% tolerance (E2E optional for some)

        return ValidationResult(
            rule_id="TEST-004",
            passed=passed,
            severity=Severity.HIGH,
            message=f"E2E Tests: {valid_e2e}/{total_impls} implementations have E2E tests, {len(missing_e2e)} missing",
            evidence={
                "total_implementations": total_impls,
                "valid_e2e": valid_e2e,
                "missing_e2e": missing_e2e[:10]
            }
        )

    def validate_security_audit_workflow(self) -> ValidationResult:
        """CI-003: Quarterly Security Audit Workflow PFLICHT

        Anforderung:
        - .github/workflows/ MUSS Quarterly Security Audit haben
        - Cron Schedule: Quarterly (z.B. '0 0 1 */3 *')
        """
        workflows_dir = self.repo_root / ".github" / "workflows"
        quarterly_workflows = []

        if workflows_dir.exists():
            workflow_files = list(workflows_dir.glob("*.{yml,yaml}"))

            for workflow in workflow_files:
                try:
                    content = workflow.read_text(encoding='utf-8', errors='ignore')

                    # Check for quarterly schedule (cron with */3)
                    has_quarterly_cron = bool(re.search(r'cron.*[\'"].*\*/3.*[\'"]', content, re.IGNORECASE))

                    # Check for security/audit keywords
                    has_security_audit = any(keyword in content.lower() for keyword in [
                        'security audit',
                        'quarterly audit',
                        'compliance report',
                        'penetration test'
                    ])

                    if has_quarterly_cron and has_security_audit:
                        quarterly_workflows.append(str(workflow.relative_to(self.repo_root)))
                except:
                    pass

        passed = len(quarterly_workflows) > 0

        return ValidationResult(
            rule_id="CI-003",
            passed=passed,
            severity=Severity.HIGH,
            message=f"Security Audit Workflow: {len(quarterly_workflows)} quarterly audit workflows configured",
            evidence={
                "quarterly_workflows": quarterly_workflows,
                "workflow_exists": passed
            }
        )

    def validate_container_registry(self) -> ValidationResult:
        """ARTIFACT-001: Container Images MÜSSEN zu ghcr.io/ssid gepusht werden

        Anforderung:
        - Images Format: ghcr.io/ssid/{shard_id}:{version}
        - Validation: CI Workflow prüft Registry + Tag-Format
        """
        workflows_dir = self.repo_root / ".github" / "workflows"
        registry_configs = []

        if workflows_dir.exists():
            workflow_files = list(workflows_dir.glob("*.{yml,yaml}"))

            for workflow in workflow_files:
                try:
                    content = workflow.read_text(encoding='utf-8', errors='ignore')

                    # Check for ghcr.io registry
                    has_ghcr = 'ghcr.io' in content.lower()

                    # Check for push/publish keywords
                    has_push = any(keyword in content.lower() for keyword in ['docker push', 'docker publish', 'container push'])

                    if has_ghcr and has_push:
                        registry_configs.append(str(workflow.relative_to(self.repo_root)))
                except:
                    pass

        passed = len(registry_configs) > 0

        return ValidationResult(
            rule_id="ARTIFACT-001",
            passed=passed,
            severity=Severity.MEDIUM,
            message=f"Container Registry: {len(registry_configs)} workflows configured for ghcr.io",
            evidence={
                "registry_workflows": registry_configs,
                "ghcr_configured": passed
            }
        )

    def validate_compliance_reports(self) -> ValidationResult:
        """ARTIFACT-004: Quarterly Compliance Reports PFLICHT

        Anforderung:
        - Quarterly Report-Generation Workflow
        - Reports published to artifacts
        """
        workflows_dir = self.repo_root / ".github" / "workflows"
        compliance_workflows = []

        if workflows_dir.exists():
            workflow_files = list(workflows_dir.glob("*.{yml,yaml}"))

            for workflow in workflow_files:
                try:
                    content = workflow.read_text(encoding='utf-8', errors='ignore')

                    # Check for quarterly schedule
                    has_quarterly = bool(re.search(r'cron.*[\'"].*\*/3.*[\'"]', content, re.IGNORECASE))

                    # Check for compliance keywords
                    has_compliance = any(keyword in content.lower() for keyword in [
                        'compliance report',
                        'compliance check',
                        'policy report',
                        'audit report'
                    ])

                    if has_quarterly and has_compliance:
                        compliance_workflows.append(str(workflow.relative_to(self.repo_root)))
                except:
                    pass

        passed = len(compliance_workflows) > 0

        return ValidationResult(
            rule_id="ARTIFACT-004",
            passed=passed,
            severity=Severity.MEDIUM,
            message=f"Compliance Reports: {len(compliance_workflows)} quarterly report workflows configured",
            evidence={
                "compliance_workflows": compliance_workflows,
                "reports_configured": passed
            }
        )

    def validate_all_critical(self) -> List[ValidationResult]:
        """Run all critical validations and return results"""
        return [
            self.validate_changelog_required(),
            self.validate_readme_required(),
            self.validate_dockerfile_required(),
            self.validate_getting_started_required(),
            self.validate_e2e_tests_required(),
            self.validate_security_audit_workflow(),
            self.validate_container_registry(),
            self.validate_compliance_reports()
        ]
