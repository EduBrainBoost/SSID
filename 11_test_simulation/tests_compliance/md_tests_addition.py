
# ==============================================================================
# MD-* RULES: Master-Definition Granular Rules Tests (57 NEW)
# Source: ssid_master_definition_corrected_v1.1.1.md
# ==============================================================================

class TestMDStructRules:
    """Test MD-STRUCT: Structure Path Validation (2 rules)."""

    def test_md_struct_009(self, validator):
        """Test MD-STRUCT-009: Chart.yaml path structure."""
        result = validator.validate_md_struct_009()
        assert isinstance(result, sot_core.ValidationResult)
        assert result.rule_id == "MD-STRUCT-009"
        assert result.severity == sot_core.Severity.CRITICAL
        assert isinstance(result.passed, bool)

    def test_md_struct_010(self, validator):
        """Test MD-STRUCT-010: Manifest.yaml path structure."""
        result = validator.validate_md_struct_010()
        assert isinstance(result, sot_core.ValidationResult)
        assert result.rule_id == "MD-STRUCT-010"
        assert result.severity == sot_core.Severity.CRITICAL
        assert isinstance(result.passed, bool)


class TestMDChartRules:
    """Test MD-CHART: Chart.yaml Field Validation (5 rules)."""

    def test_md_chart_024(self, validator):
        """Test MD-CHART-024: compatibility.core_min_version."""
        result = validator.validate_md_chart_024()
        assert isinstance(result, sot_core.ValidationResult)
        assert result.rule_id == "MD-CHART-024"
        assert result.severity == sot_core.Severity.HIGH
        assert isinstance(result.passed, bool)

    def test_md_chart_029(self, validator):
        """Test MD-CHART-029: orchestration.workflows."""
        result = validator.validate_md_chart_029()
        assert isinstance(result, sot_core.ValidationResult)
        assert result.rule_id == "MD-CHART-029"
        assert result.severity == sot_core.Severity.MEDIUM
        assert result.passed is True  # SOLLTE = always passes

    def test_md_chart_045(self, validator):
        """Test MD-CHART-045: security.encryption."""
        result = validator.validate_md_chart_045()
        assert isinstance(result, sot_core.ValidationResult)
        assert result.rule_id == "MD-CHART-045"
        assert result.severity == sot_core.Severity.CRITICAL
        assert isinstance(result.passed, bool)

    def test_md_chart_048(self, validator):
        """Test MD-CHART-048: resources.compute."""
        result = validator.validate_md_chart_048()
        assert isinstance(result, sot_core.ValidationResult)
        assert result.rule_id == "MD-CHART-048"
        assert result.severity == sot_core.Severity.MEDIUM
        assert isinstance(result.passed, bool)

    def test_md_chart_050(self, validator):
        """Test MD-CHART-050: roadmap.upcoming."""
        result = validator.validate_md_chart_050()
        assert isinstance(result, sot_core.ValidationResult)
        assert result.rule_id == "MD-CHART-050"
        assert result.severity == sot_core.Severity.LOW
        assert result.passed is True  # SOLLTE = always passes


class TestMDManifestRules:
    """Test MD-MANIFEST: Manifest.yaml Field Validation (28 rules)."""

    def test_md_manifest_004(self, validator):
        """Test MD-MANIFEST-004: metadata.maturity."""
        result = validator.validate_md_manifest_004()
        assert isinstance(result, sot_core.ValidationResult)
        assert result.rule_id == "MD-MANIFEST-004"
        assert isinstance(result.passed, bool)

    def test_md_manifest_009(self, validator):
        """Test MD-MANIFEST-009: technology_stack.linting_formatting."""
        result = validator.validate_md_manifest_009()
        assert isinstance(result, sot_core.ValidationResult)
        assert result.rule_id == "MD-MANIFEST-009"
        assert isinstance(result.passed, bool)

    def test_md_manifest_012(self, validator):
        """Test MD-MANIFEST-012: artifacts.configuration.location."""
        result = validator.validate_md_manifest_012()
        assert isinstance(result, sot_core.ValidationResult)
        assert result.rule_id == "MD-MANIFEST-012"
        assert isinstance(result.passed, bool)

    def test_md_manifest_013(self, validator):
        """Test MD-MANIFEST-013: artifacts.models.location."""
        result = validator.validate_md_manifest_013()
        assert isinstance(result, sot_core.ValidationResult)
        assert result.rule_id == "MD-MANIFEST-013"
        assert result.passed is True  # SOLLTE = always passes

    def test_md_manifest_014(self, validator):
        """Test MD-MANIFEST-014: artifacts.protocols.location."""
        result = validator.validate_md_manifest_014()
        assert isinstance(result, sot_core.ValidationResult)
        assert result.rule_id == "MD-MANIFEST-014"
        assert result.passed is True  # SOLLTE = always passes

    def test_md_manifest_015(self, validator):
        """Test MD-MANIFEST-015: artifacts.tests.location."""
        result = validator.validate_md_manifest_015()
        assert isinstance(result, sot_core.ValidationResult)
        assert result.rule_id == "MD-MANIFEST-015"
        assert result.severity == sot_core.Severity.HIGH
        assert isinstance(result.passed, bool)

    def test_md_manifest_016(self, validator):
        """Test MD-MANIFEST-016: artifacts.documentation.location."""
        result = validator.validate_md_manifest_016()
        assert isinstance(result, sot_core.ValidationResult)
        assert result.rule_id == "MD-MANIFEST-016"
        assert isinstance(result.passed, bool)

    def test_md_manifest_017(self, validator):
        """Test MD-MANIFEST-017: artifacts.scripts.location."""
        result = validator.validate_md_manifest_017()
        assert isinstance(result, sot_core.ValidationResult)
        assert result.rule_id == "MD-MANIFEST-017"
        assert isinstance(result.passed, bool)

    def test_md_manifest_018(self, validator):
        """Test MD-MANIFEST-018: artifacts.docker.files."""
        result = validator.validate_md_manifest_018()
        assert isinstance(result, sot_core.ValidationResult)
        assert result.rule_id == "MD-MANIFEST-018"
        assert result.severity == sot_core.Severity.HIGH
        assert isinstance(result.passed, bool)

    def test_md_manifest_023(self, validator):
        """Test MD-MANIFEST-023: build.commands."""
        result = validator.validate_md_manifest_023()
        assert isinstance(result, sot_core.ValidationResult)
        assert result.rule_id == "MD-MANIFEST-023"
        assert result.severity == sot_core.Severity.HIGH
        assert isinstance(result.passed, bool)

    def test_md_manifest_024(self, validator):
        """Test MD-MANIFEST-024: build.docker."""
        result = validator.validate_md_manifest_024()
        assert isinstance(result, sot_core.ValidationResult)
        assert result.rule_id == "MD-MANIFEST-024"
        assert result.severity == sot_core.Severity.HIGH
        assert isinstance(result.passed, bool)

    def test_md_manifest_025(self, validator):
        """Test MD-MANIFEST-025: deployment.kubernetes.manifests_location."""
        result = validator.validate_md_manifest_025()
        assert isinstance(result, sot_core.ValidationResult)
        assert result.rule_id == "MD-MANIFEST-025"
        assert result.severity == sot_core.Severity.HIGH
        assert isinstance(result.passed, bool)

    def test_md_manifest_026(self, validator):
        """Test MD-MANIFEST-026: deployment.helm.chart_location."""
        result = validator.validate_md_manifest_026()
        assert isinstance(result, sot_core.ValidationResult)
        assert result.rule_id == "MD-MANIFEST-026"
        assert result.severity == sot_core.Severity.HIGH
        assert isinstance(result.passed, bool)

    def test_md_manifest_027(self, validator):
        """Test MD-MANIFEST-027: deployment.environment_variables."""
        result = validator.validate_md_manifest_027()
        assert isinstance(result, sot_core.ValidationResult)
        assert result.rule_id == "MD-MANIFEST-027"
        assert result.severity == sot_core.Severity.HIGH
        assert isinstance(result.passed, bool)

    def test_md_manifest_029(self, validator):
        """Test MD-MANIFEST-029: testing.unit_tests.coverage_target>=80."""
        result = validator.validate_md_manifest_029()
        assert isinstance(result, sot_core.ValidationResult)
        assert result.rule_id == "MD-MANIFEST-029"
        assert result.severity == sot_core.Severity.CRITICAL
        assert isinstance(result.passed, bool)

    def test_md_manifest_032(self, validator):
        """Test MD-MANIFEST-032: testing.security_tests."""
        result = validator.validate_md_manifest_032()
        assert isinstance(result, sot_core.ValidationResult)
        assert result.rule_id == "MD-MANIFEST-032"
        assert result.severity == sot_core.Severity.CRITICAL
        assert isinstance(result.passed, bool)

    def test_md_manifest_033(self, validator):
        """Test MD-MANIFEST-033: testing.performance_tests."""
        result = validator.validate_md_manifest_033()
        assert isinstance(result, sot_core.ValidationResult)
        assert result.rule_id == "MD-MANIFEST-033"
        assert result.severity == sot_core.Severity.HIGH
        assert isinstance(result.passed, bool)

    def test_md_manifest_036(self, validator):
        """Test MD-MANIFEST-036: observability.logging.format=json."""
        result = validator.validate_md_manifest_036()
        assert isinstance(result, sot_core.ValidationResult)
        assert result.rule_id == "MD-MANIFEST-036"
        assert result.severity == sot_core.Severity.HIGH
        assert isinstance(result.passed, bool)

    def test_md_manifest_038(self, validator):
        """Test MD-MANIFEST-038: observability.health_checks.liveness."""
        result = validator.validate_md_manifest_038()
        assert isinstance(result, sot_core.ValidationResult)
        assert result.rule_id == "MD-MANIFEST-038"
        assert result.severity == sot_core.Severity.CRITICAL
        assert isinstance(result.passed, bool)

    def test_md_manifest_039(self, validator):
        """Test MD-MANIFEST-039: observability.health_checks.readiness."""
        result = validator.validate_md_manifest_039()
        assert isinstance(result, sot_core.ValidationResult)
        assert result.rule_id == "MD-MANIFEST-039"
        assert result.severity == sot_core.Severity.CRITICAL
        assert isinstance(result.passed, bool)

    def test_md_manifest_040(self, validator):
        """Test MD-MANIFEST-040: development.setup."""
        result = validator.validate_md_manifest_040()
        assert isinstance(result, sot_core.ValidationResult)
        assert result.rule_id == "MD-MANIFEST-040"
        assert isinstance(result.passed, bool)

    def test_md_manifest_041(self, validator):
        """Test MD-MANIFEST-041: development.local_development."""
        result = validator.validate_md_manifest_041()
        assert isinstance(result, sot_core.ValidationResult)
        assert result.rule_id == "MD-MANIFEST-041"
        assert isinstance(result.passed, bool)

    def test_md_manifest_042(self, validator):
        """Test MD-MANIFEST-042: development.pre_commit_hooks."""
        result = validator.validate_md_manifest_042()
        assert isinstance(result, sot_core.ValidationResult)
        assert result.rule_id == "MD-MANIFEST-042"
        assert result.severity == sot_core.Severity.HIGH
        assert isinstance(result.passed, bool)

    def test_md_manifest_046(self, validator):
        """Test MD-MANIFEST-046: performance.baseline_benchmarks."""
        result = validator.validate_md_manifest_046()
        assert isinstance(result, sot_core.ValidationResult)
        assert result.rule_id == "MD-MANIFEST-046"
        assert result.severity == sot_core.Severity.HIGH
        assert isinstance(result.passed, bool)

    def test_md_manifest_047(self, validator):
        """Test MD-MANIFEST-047: performance.optimization_targets."""
        result = validator.validate_md_manifest_047()
        assert isinstance(result, sot_core.ValidationResult)
        assert result.rule_id == "MD-MANIFEST-047"
        assert result.severity == sot_core.Severity.HIGH
        assert isinstance(result.passed, bool)

    def test_md_manifest_048(self, validator):
        """Test MD-MANIFEST-048: performance.resource_requirements."""
        result = validator.validate_md_manifest_048()
        assert isinstance(result, sot_core.ValidationResult)
        assert result.rule_id == "MD-MANIFEST-048"
        assert result.severity == sot_core.Severity.HIGH
        assert isinstance(result.passed, bool)

    def test_md_manifest_049(self, validator):
        """Test MD-MANIFEST-049: changelog.location=CHANGELOG.md."""
        result = validator.validate_md_manifest_049()
        assert isinstance(result, sot_core.ValidationResult)
        assert result.rule_id == "MD-MANIFEST-049"
        assert isinstance(result.passed, bool)

    def test_md_manifest_050(self, validator):
        """Test MD-MANIFEST-050: support.contacts."""
        result = validator.validate_md_manifest_050()
        assert isinstance(result, sot_core.ValidationResult)
        assert result.rule_id == "MD-MANIFEST-050"
        assert isinstance(result.passed, bool)


class TestMDPolicyRules:
    """Test MD-POLICY: Critical Policy Enforcement (6 rules)."""

    def test_md_policy_009(self, validator):
        """Test MD-POLICY-009: Deterministic hashing."""
        result = validator.validate_md_policy_009()
        assert isinstance(result, sot_core.ValidationResult)
        assert result.rule_id == "MD-POLICY-009"
        assert result.severity == sot_core.Severity.CRITICAL
        assert isinstance(result.passed, bool)

    def test_md_policy_012(self, validator):
        """Test MD-POLICY-012: Purpose limitation enforcement."""
        result = validator.validate_md_policy_012()
        assert isinstance(result, sot_core.ValidationResult)
        assert result.rule_id == "MD-POLICY-012"
        assert result.severity == sot_core.Severity.CRITICAL
        assert isinstance(result.passed, bool)

    def test_md_policy_023(self, validator):
        """Test MD-POLICY-023: Hourly anchoring."""
        result = validator.validate_md_policy_023()
        assert isinstance(result, sot_core.ValidationResult)
        assert result.rule_id == "MD-POLICY-023"
        assert result.severity == sot_core.Severity.CRITICAL
        assert isinstance(result.passed, bool)

    def test_md_policy_027(self, validator):
        """Test MD-POLICY-027: AES-256-GCM encryption."""
        result = validator.validate_md_policy_027()
        assert isinstance(result, sot_core.ValidationResult)
        assert result.rule_id == "MD-POLICY-027"
        assert result.severity == sot_core.Severity.CRITICAL
        assert isinstance(result.passed, bool)

    def test_md_policy_028(self, validator):
        """Test MD-POLICY-028: TLS 1.3 in-transit encryption."""
        result = validator.validate_md_policy_028()
        assert isinstance(result, sot_core.ValidationResult)
        assert result.rule_id == "MD-POLICY-028"
        assert result.severity == sot_core.Severity.CRITICAL
        assert isinstance(result.passed, bool)


class TestMDPrincRules:
    """Test MD-PRINC: Principles (6 rules)."""

    def test_md_princ_007(self, validator):
        """Test MD-PRINC-007: RBAC for all access."""
        result = validator.validate_md_princ_007()
        assert isinstance(result, sot_core.ValidationResult)
        assert result.rule_id == "MD-PRINC-007"
        assert result.severity == sot_core.Severity.CRITICAL
        assert isinstance(result.passed, bool)

    def test_md_princ_009(self, validator):
        """Test MD-PRINC-009: Continuous vulnerability scanning."""
        result = validator.validate_md_princ_009()
        assert isinstance(result, sot_core.ValidationResult)
        assert result.rule_id == "MD-PRINC-009"
        assert result.severity == sot_core.Severity.HIGH
        assert isinstance(result.passed, bool)

    def test_md_princ_013(self, validator):
        """Test MD-PRINC-013: AlertManager integration."""
        result = validator.validate_md_princ_013()
        assert isinstance(result, sot_core.ValidationResult)
        assert result.rule_id == "MD-PRINC-013"
        assert result.severity == sot_core.Severity.HIGH
        assert isinstance(result.passed, bool)

    def test_md_princ_018(self, validator):
        """Test MD-PRINC-018: Load balancing configuration."""
        result = validator.validate_md_princ_018()
        assert isinstance(result, sot_core.ValidationResult)
        assert result.rule_id == "MD-PRINC-018"
        assert result.severity == sot_core.Severity.MEDIUM
        assert isinstance(result.passed, bool)

    def test_md_princ_019(self, validator):
        """Test MD-PRINC-019: Caching strategies."""
        result = validator.validate_md_princ_019()
        assert isinstance(result, sot_core.ValidationResult)
        assert result.rule_id == "MD-PRINC-019"
        assert result.severity == sot_core.Severity.MEDIUM
        assert isinstance(result.passed, bool)

    def test_md_princ_020(self, validator):
        """Test MD-PRINC-020: Performance benchmark gates."""
        result = validator.validate_md_princ_020()
        assert isinstance(result, sot_core.ValidationResult)
        assert result.rule_id == "MD-PRINC-020"
        assert result.severity == sot_core.Severity.HIGH
        assert isinstance(result.passed, bool)


class TestMDGovRules:
    """Test MD-GOV: Governance Rules (7 rules)."""

    def test_md_gov_005(self, validator):
        """Test MD-GOV-005: Compliance team policy review."""
        result = validator.validate_md_gov_005()
        assert isinstance(result, sot_core.ValidationResult)
        assert result.rule_id == "MD-GOV-005"
        assert result.severity == sot_core.Severity.HIGH
        assert isinstance(result.passed, bool)

    def test_md_gov_006(self, validator):
        """Test MD-GOV-006: Compliance team constraint approval."""
        result = validator.validate_md_gov_006()
        assert isinstance(result, sot_core.ValidationResult)
        assert result.rule_id == "MD-GOV-006"
        assert result.severity == sot_core.Severity.HIGH
        assert isinstance(result.passed, bool)

    def test_md_gov_007(self, validator):
        """Test MD-GOV-007: Security team threat modeling."""
        result = validator.validate_md_gov_007()
        assert isinstance(result, sot_core.ValidationResult)
        assert result.rule_id == "MD-GOV-007"
        assert result.severity == sot_core.Severity.HIGH
        assert isinstance(result.passed, bool)

    def test_md_gov_008(self, validator):
        """Test MD-GOV-008: Change process 7 steps."""
        result = validator.validate_md_gov_008()
        assert isinstance(result, sot_core.ValidationResult)
        assert result.rule_id == "MD-GOV-008"
        assert result.severity == sot_core.Severity.HIGH
        assert isinstance(result.passed, bool)

    def test_md_gov_009(self, validator):
        """Test MD-GOV-009: SHOULD->MUST promotion criteria (90d + 99.5% SLA)."""
        result = validator.validate_md_gov_009()
        assert isinstance(result, sot_core.ValidationResult)
        assert result.rule_id == "MD-GOV-009"
        assert result.severity == sot_core.Severity.HIGH
        assert isinstance(result.passed, bool)

    def test_md_gov_010(self, validator):
        """Test MD-GOV-010: SHOULD->MUST promotion 95% contract test coverage."""
        result = validator.validate_md_gov_010()
        assert isinstance(result, sot_core.ValidationResult)
        assert result.rule_id == "MD-GOV-010"
        assert result.severity == sot_core.Severity.HIGH
        assert isinstance(result.passed, bool)

    def test_md_gov_011(self, validator):
        """Test MD-GOV-011: HAVE->SHOULD promotion (feature complete + beta + docs)."""
        result = validator.validate_md_gov_011()
        assert isinstance(result, sot_core.ValidationResult)
        assert result.rule_id == "MD-GOV-011"
        assert result.severity == sot_core.Severity.HIGH
        assert isinstance(result.passed, bool)


class TestMDExtRules:
    """Test MD-EXT: Extension Rules v1.1.1 (4 rules)."""

    def test_md_ext_012(self, validator):
        """Test MD-EXT-012: OPA string_similarity() helper."""
        result = validator.validate_md_ext_012()
        assert isinstance(result, sot_core.ValidationResult)
        assert result.rule_id == "MD-EXT-012"
        assert result.severity == sot_core.Severity.MEDIUM
        assert isinstance(result.passed, bool)

    def test_md_ext_014(self, validator):
        """Test MD-EXT-014: CI quarterly audit schedule."""
        result = validator.validate_md_ext_014()
        assert isinstance(result, sot_core.ValidationResult)
        assert result.rule_id == "MD-EXT-014"
        assert result.severity == sot_core.Severity.MEDIUM
        assert isinstance(result.passed, bool)

    def test_md_ext_015(self, validator):
        """Test MD-EXT-015: CI upload-artifact@v4."""
        result = validator.validate_md_ext_015()
        assert isinstance(result, sot_core.ValidationResult)
        assert result.rule_id == "MD-EXT-015"
        assert result.severity == sot_core.Severity.LOW
        assert isinstance(result.passed, bool)

    def test_md_ext_018(self, validator):
        """Test MD-EXT-018: Sanctions sha256 hash."""
        result = validator.validate_md_ext_018()
        assert isinstance(result, sot_core.ValidationResult)
        assert result.rule_id == "MD-EXT-018"
        assert result.severity == sot_core.Severity.HIGH
        assert isinstance(result.passed, bool)


