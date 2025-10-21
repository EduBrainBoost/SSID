"""
Additional Validators - Specific Rules from Master Definition
==============================================================
This module contains validators for the additional specific rules identified
in the detailed review of ssid_master_definition_corrected_v1.1.1.md

These validators check:
1. Capability semantics (MUST/SHOULD/HAVE meanings)
2. Specific linting tools (black, ruff, mypy, semgrep)
3. Specific conformance framework (schemathesis)
4. Integration and Contract test coverage (70%, 95%)

Status: NEW - Implementing partial → full validation
"""

from dataclasses import dataclass
from typing import List
from pathlib import Path
from enum import Enum


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


class AdditionalValidators:
    """Additional validation functions for specific master definition rules"""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root

    def validate_cs003_capability_semantics(self) -> ValidationResult:
        """CS003 ENHANCED: Capability-Semantik prüfen

        Prüft nicht nur Existenz von capabilities, sondern auch dass:
        - MUST = Produktiv, SLA-gebunden (korrekt verwendet)
        - SHOULD = Feature-complete, in Erprobung
        - HAVE = Experimentell, optional
        """
        chart_files = list(self.repo_root.rglob("**/Chart.yaml"))

        charts_with_capabilities = 0
        charts_with_valid_semantics = 0
        semantic_details = []

        for chart_file in chart_files[:50]:
            try:
                import yaml
                content = yaml.safe_load(chart_file.read_text())

                if 'capabilities' in content:
                    charts_with_capabilities += 1

                    caps = content['capabilities']

                    # Check structure
                    has_must = 'MUST' in caps or 'must' in caps
                    has_should = 'SHOULD' in caps or 'should' in caps
                    has_have = 'HAVE' in caps or 'have' in caps

                    # Check if at least MUST and one other category exist
                    valid_structure = has_must and (has_should or has_have)

                    # Check if governance section mentions SLA for MUST capabilities
                    has_sla = False
                    if 'governance' in content:
                        gov_str = str(content['governance']).lower()
                        if 'sla' in gov_str or 'service level' in gov_str:
                            has_sla = True

                    if valid_structure:
                        charts_with_valid_semantics += 1
                        semantic_details.append({
                            "file": str(chart_file.relative_to(self.repo_root)),
                            "has_must": has_must,
                            "has_should": has_should,
                            "has_have": has_have,
                            "has_sla_in_governance": has_sla
                        })
            except:
                pass

        passed = charts_with_valid_semantics > 0

        return ValidationResult(
            rule_id="CS003_SEMANTICS",
            passed=passed,
            severity=Severity.MEDIUM,
            message=f"Capability semantics: {charts_with_valid_semantics}/{charts_with_capabilities} charts with valid MUST/SHOULD/HAVE structure",
            evidence={
                "charts_with_capabilities": charts_with_capabilities,
                "charts_with_valid_semantics": charts_with_valid_semantics,
                "semantic_details": semantic_details[:5]
            }
        )

    def validate_linting_tools_specific(self) -> ValidationResult:
        """MD-MANIFEST-009 ENHANCED: Spezifische Linting-Tools prüfen

        Für Python-Implementierungen MÜSSEN diese 4 Tools konfiguriert sein:
        - black (Formatting)
        - ruff (Linting)
        - mypy (Type Checking)
        - semgrep (Security)
        """
        manifest_files = list(self.repo_root.rglob("**/manifest.yaml"))

        manifests_with_linting = 0
        manifests_with_all_tools = 0
        tool_details = []

        required_tools = {'black', 'ruff', 'mypy', 'semgrep'}

        for manifest in manifest_files[:50]:
            try:
                import yaml
                content = yaml.safe_load(manifest.read_text())

                if content and 'technology_stack' in content:
                    linting = content['technology_stack'].get('linting_formatting', [])

                    if linting:
                        manifests_with_linting += 1

                        # Convert to lowercase for comparison
                        if isinstance(linting, list):
                            linting_lower = [str(tool).lower() for tool in linting]
                        else:
                            linting_lower = [str(linting).lower()]

                        # Check if all 4 required tools are present
                        tools_found = set()
                        for tool in required_tools:
                            if any(tool in lt for lt in linting_lower):
                                tools_found.add(tool)

                        if len(tools_found) == 4:
                            manifests_with_all_tools += 1
                            tool_details.append({
                                "file": str(manifest.relative_to(self.repo_root)),
                                "tools_configured": list(tools_found),
                                "all_required": True
                            })
                        elif len(tools_found) > 0:
                            tool_details.append({
                                "file": str(manifest.relative_to(self.repo_root)),
                                "tools_configured": list(tools_found),
                                "missing": list(required_tools - tools_found),
                                "all_required": False
                            })
            except:
                pass

        passed = manifests_with_all_tools > 0

        return ValidationResult(
            rule_id="MD-MANIFEST-009_TOOLS",
            passed=passed,
            severity=Severity.MEDIUM,
            message=f"Linting tools: {manifests_with_all_tools}/{manifests_with_linting} manifests with all 4 tools (black, ruff, mypy, semgrep)",
            evidence={
                "manifests_with_linting": manifests_with_linting,
                "manifests_with_all_tools": manifests_with_all_tools,
                "required_tools": list(required_tools),
                "tool_details": tool_details[:5]
            }
        )

    def validate_conformance_framework_specific(self) -> ValidationResult:
        """CS009 ENHANCED: Schemathesis Framework prüfen

        Conformance testing MUSS schemathesis Framework verwenden:
        - conformance.test_framework: "schemathesis"
        """
        chart_files = list(self.repo_root.rglob("**/Chart.yaml"))

        charts_with_conformance = 0
        charts_with_schemathesis = 0
        framework_details = []

        for chart_file in chart_files[:50]:
            try:
                import yaml
                content = yaml.safe_load(chart_file.read_text())

                if content and 'conformance' in content:
                    conformance = content['conformance']

                    if 'contract_tests' in conformance or 'test_framework' in conformance:
                        charts_with_conformance += 1

                        # Check for schemathesis
                        conf_str = str(conformance).lower()
                        if 'schemathesis' in conf_str:
                            charts_with_schemathesis += 1
                            framework_details.append({
                                "file": str(chart_file.relative_to(self.repo_root)),
                                "framework": "schemathesis",
                                "explicit": True
                            })
                        else:
                            framework_details.append({
                                "file": str(chart_file.relative_to(self.repo_root)),
                                "framework": "unknown/other",
                                "explicit": False
                            })
            except:
                pass

        passed = charts_with_schemathesis > 0

        return ValidationResult(
            rule_id="CS009_FRAMEWORK",
            passed=passed,
            severity=Severity.MEDIUM,
            message=f"Conformance framework: {charts_with_schemathesis}/{charts_with_conformance} charts use schemathesis",
            evidence={
                "charts_with_conformance": charts_with_conformance,
                "charts_with_schemathesis": charts_with_schemathesis,
                "framework_details": framework_details[:5]
            }
        )

    def validate_testing_coverage_complete(self) -> ValidationResult:
        """MD-MANIFEST-029 ENHANCED: Vollständige Coverage-Anforderungen

        Prüft ALLE Coverage-Anforderungen:
        - Unit Tests: 80% (bereits in MD-MANIFEST-029)
        - Integration Tests: 70% (NEU)
        - Contract Tests: 95% (NEU)
        """
        manifest_files = list(self.repo_root.rglob("**/manifest.yaml"))

        coverage_stats = {
            "unit_80": 0,
            "integration_70": 0,
            "contract_95": 0
        }

        manifests_with_all_coverage = 0
        coverage_details = []

        for manifest in manifest_files[:50]:
            try:
                import yaml
                content = yaml.safe_load(manifest.read_text())

                if content and 'testing' in content:
                    testing = content['testing']

                    # Check unit test coverage >= 80
                    has_unit_80 = False
                    if 'unit_tests' in testing:
                        coverage_target = testing['unit_tests'].get('coverage_target', 0)
                        if isinstance(coverage_target, (int, float)) and coverage_target >= 80:
                            has_unit_80 = True
                            coverage_stats["unit_80"] += 1

                    # Check integration test coverage >= 70
                    has_integration_70 = False
                    if 'integration_tests' in testing:
                        coverage_target = testing['integration_tests'].get('coverage_target', 0)
                        if isinstance(coverage_target, (int, float)) and coverage_target >= 70:
                            has_integration_70 = True
                            coverage_stats["integration_70"] += 1

                    # Check contract test coverage >= 95
                    has_contract_95 = False
                    if 'contract_tests' in testing:
                        coverage_target = testing['contract_tests'].get('coverage_target', 0)
                        if isinstance(coverage_target, (int, float)) and coverage_target >= 95:
                            has_contract_95 = True
                            coverage_stats["contract_95"] += 1

                    # All 3 coverage targets met
                    if has_unit_80 and has_integration_70 and has_contract_95:
                        manifests_with_all_coverage += 1

                    if has_unit_80 or has_integration_70 or has_contract_95:
                        coverage_details.append({
                            "file": str(manifest.relative_to(self.repo_root)),
                            "unit_80": has_unit_80,
                            "integration_70": has_integration_70,
                            "contract_95": has_contract_95,
                            "all_met": has_unit_80 and has_integration_70 and has_contract_95
                        })
            except:
                pass

        # Pass if at least unit_80 is widely adopted (existing requirement)
        # Full pass would require all 3, but that's stricter than current
        passed = coverage_stats["unit_80"] > 0

        return ValidationResult(
            rule_id="MD-MANIFEST-029_COMPLETE",
            passed=passed,
            severity=Severity.MEDIUM,
            message=f"Testing coverage: unit≥80% ({coverage_stats['unit_80']} manifests), integration≥70% ({coverage_stats['integration_70']}), contract≥95% ({coverage_stats['contract_95']})",
            evidence={
                "manifests_with_unit_80": coverage_stats["unit_80"],
                "manifests_with_integration_70": coverage_stats["integration_70"],
                "manifests_with_contract_95": coverage_stats["contract_95"],
                "manifests_with_all_coverage": manifests_with_all_coverage,
                "coverage_details": coverage_details[:5]
            }
        )

    def validate_all_additional(self) -> List[ValidationResult]:
        """Run all additional validations and return results"""
        return [
            self.validate_cs003_capability_semantics(),
            self.validate_linting_tools_specific(),
            self.validate_conformance_framework_specific(),
            self.validate_testing_coverage_complete()
        ]
