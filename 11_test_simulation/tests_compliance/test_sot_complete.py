#!/usr/bin/env python3
"""
Complete SoT Test Suite
========================

Version: 4.0.0
Status: PRODUCTION

Tests all aspects of the SoT system using REAL SSID paths and validator engine.
"""

import pytest
import json
from pathlib import Path
import sys

# Get REAL repo root
REPO_ROOT = Path(__file__).resolve().parents[2]

# Add to path
sys.path.insert(0, str(REPO_ROOT / '03_core' / 'validators' / 'sot'))

from sot_validator_engine import RuleValidationEngine


class TestSoTSystemStructure:
    """Test SSID system structure"""

    @pytest.fixture
    def repo_root(self):
        """REAL repository root"""
        return REPO_ROOT

    def test_repo_root_exists(self, repo_root):
        """Test repository root exists"""
        assert repo_root.exists(), f"Repository root not found: {repo_root}"
        assert repo_root.is_dir(), f"Repository root is not a directory: {repo_root}"

    def test_24_roots_exist(self, repo_root):
        """Test that all 24 SSID root directories exist"""
        expected_roots = [
            "01_ai_layer", "02_audit_logging", "03_core", "04_deployment",
            "05_documentation", "06_data_pipeline", "07_governance_legal",
            "08_identity_score", "09_meta_identity", "10_interoperability",
            "11_test_simulation", "12_tooling", "13_ui_layer", "14_zero_time_auth",
            "15_infra", "16_codex", "17_observability", "18_data_layer",
            "19_adapters", "20_foundation", "21_post_quantum_crypto",
            "22_datasets", "23_compliance", "24_meta_orchestration"
        ]

        existing_roots = [d.name for d in repo_root.iterdir()
                         if d.is_dir() and d.name in expected_roots]

        assert len(existing_roots) == 24, \
            f"Expected 24 root directories, found {len(existing_roots)}: {existing_roots}"

    def test_registry_exists(self, repo_root):
        """Test that registry file exists"""
        registry_path = repo_root / '16_codex' / 'structure' / 'auto_generated' / 'sot_rules_full.json'
        assert registry_path.exists(), f"Registry not found at {registry_path}"

    def test_contract_exists(self, repo_root):
        """Test that contract file exists"""
        contract_path = repo_root / '16_codex' / 'contracts' / 'sot' / 'sot_contract.yaml'
        assert contract_path.exists(), f"Contract not found at {contract_path}"

    def test_policy_dir_exists(self, repo_root):
        """Test that policy directory exists"""
        policy_dir = repo_root / '23_compliance' / 'policies' / 'sot'
        assert policy_dir.exists(), f"Policy directory not found at {policy_dir}"

        rego_files = list(policy_dir.glob('*.rego'))
        assert len(rego_files) > 0, "No .rego policy files found"

    def test_validator_engine_exists(self, repo_root):
        """Test that validator engine exists"""
        validator_path = repo_root / '03_core' / 'validators' / 'sot' / 'sot_validator_engine.py'
        assert validator_path.exists(), f"Validator engine not found at {validator_path}"


class TestSoTRegistry:
    """Test SoT rule registry"""

    @pytest.fixture
    def registry_path(self):
        """Path to registry"""
        return REPO_ROOT / '16_codex' / 'structure' / 'auto_generated' / 'sot_rules_full.json'

    @pytest.fixture
    def registry(self, registry_path):
        """Load registry"""
        with open(registry_path, encoding='utf-8') as f:
            return json.load(f)

    def test_registry_valid_json(self, registry_path):
        """Test registry is valid JSON"""
        with open(registry_path, encoding='utf-8') as f:
            data = json.load(f)
        assert isinstance(data, dict), "Registry must be a dictionary"

    def test_registry_has_rules(self, registry):
        """Test registry has rules array"""
        assert 'rules' in registry, "Registry missing 'rules' key"
        assert isinstance(registry['rules'], list), "Registry 'rules' must be a list"
        assert len(registry['rules']) > 0, "Registry has no rules"

    def test_registry_has_many_rules(self, registry):
        """Test registry has expected number of rules"""
        rule_count = len(registry['rules'])
        assert rule_count > 30000, \
            f"Expected >30,000 rules, got {rule_count}"

    def test_rules_have_required_fields(self, registry):
        """Test that rules have required fields"""
        required_fields = ['rule_id', 'category', 'priority', 'description']

        for i, rule in enumerate(registry['rules'][:100]):  # Check first 100
            for field in required_fields:
                assert field in rule or 'id' in rule, \
                    f"Rule {i} missing required field '{field}': {rule}"

    def test_priorities_valid(self, registry):
        """Test that priorities are valid MoSCoW values"""
        valid_priorities = ['MUST', 'SHOULD', 'HAVE', 'CAN', 'UNKNOWN']

        for rule in registry['rules'][:100]:  # Check first 100
            priority = rule.get('priority', 'UNKNOWN').upper()
            assert priority in valid_priorities, \
                f"Invalid priority '{priority}' in rule {rule.get('rule_id', 'UNKNOWN')}"


class TestSoTValidatorEngine:
    """Test SoT validator engine"""

    @pytest.fixture
    def engine(self):
        """Create validator engine"""
        return RuleValidationEngine(repo_root=REPO_ROOT)

    def test_engine_initializes(self, engine):
        """Test engine initializes correctly"""
        assert engine is not None
        assert engine.repo_root is not None
        assert engine.registry is not None

    def test_engine_loads_rules(self, engine):
        """Test engine loads rules from registry"""
        assert len(engine.registry.rules) > 0, "Engine has no rules"
        assert len(engine.registry.rules) > 30000, \
            f"Expected >30,000 rules, got {len(engine.registry.rules)}"

    def test_engine_has_validators(self, engine):
        """Test engine has category validators"""
        assert hasattr(engine, 'validators'), "Engine missing validators"
        assert len(engine.validators) > 0, "Engine has no validators"

        expected_categories = ['structure', 'policy', 'compliance', 'security', 'testing', 'documentation']
        for category in expected_categories:
            assert category in engine.validators, \
                f"Engine missing validator for category '{category}'"

    def test_validate_all_runs(self, engine):
        """Test that validate_all() executes without errors"""
        report = engine.validate_all()

        assert report is not None
        assert hasattr(report, 'total_rules'), "Report missing total_rules"
        assert hasattr(report, 'passed'), "Report missing passed"
        assert hasattr(report, 'failed'), "Report missing failed"
        assert hasattr(report, 'overall_score'), "Report missing overall_score"

    def test_validate_all_returns_results(self, engine):
        """Test that validate_all() returns results"""
        report = engine.validate_all()

        assert report.total_rules > 0, "No rules validated"
        assert report.passed + report.failed + report.warnings + report.skipped == report.total_rules, \
            "Result counts don't add up"

    def test_overall_score_valid(self, engine):
        """Test that overall score is valid"""
        report = engine.validate_all()

        assert 0 <= report.overall_score <= 100, \
            f"Overall score must be 0-100, got {report.overall_score}"

    def test_priority_scores_present(self, engine):
        """Test that priority scores are present"""
        report = engine.validate_all()

        assert hasattr(report, 'priority_scores'), "Report missing priority_scores"
        assert 'MUST' in report.priority_scores, "Missing MUST priority scores"


class TestSoTValidationResults:
    """Test validation results quality"""

    @pytest.fixture
    def report(self):
        """Get validation report"""
        engine = RuleValidationEngine(repo_root=REPO_ROOT)
        return engine.validate_all()

    def test_must_rules_high_pass_rate(self, report):
        """Test MUST rules have high pass rate"""
        if 'MUST' not in report.priority_scores:
            pytest.skip("No MUST rules found")

        must_data = report.priority_scores['MUST']
        pass_rate = must_data['score']

        assert pass_rate >= 90.0, \
            f"MUST rules pass rate {pass_rate:.1f}% < 90% (expected >= 90%)"

    def test_overall_score_acceptable(self, report):
        """Test overall score is acceptable"""
        assert report.overall_score >= 85.0, \
            f"Overall score {report.overall_score:.1f}% < 85% (expected >= 85%)"

    def test_some_rules_pass(self, report):
        """Test that some rules pass"""
        assert report.passed > 0, "No rules passed validation"
        assert report.passed > report.total_rules * 0.5, \
            f"Less than 50% of rules passed: {report.passed}/{report.total_rules}"


class TestSoTComplianceFiles:
    """Test compliance-related files"""

    def test_compliance_dir_exists(self):
        """Test compliance directory exists"""
        compliance_dir = REPO_ROOT / '23_compliance'
        assert compliance_dir.exists()

    def test_gdpr_docs_exist(self):
        """Test GDPR documentation exists"""
        compliance_dir = REPO_ROOT / '23_compliance'
        gdpr_files = list(compliance_dir.glob('**/*gdpr*.md')) + \
                    list(compliance_dir.glob('**/*GDPR*.md'))

        assert len(gdpr_files) > 0, "No GDPR documentation found"

    def test_pqc_tools_exist(self):
        """Test PQC tools exist"""
        pqc_dir = REPO_ROOT / '21_post_quantum_crypto'
        assert pqc_dir.exists()

        tools_dir = pqc_dir / 'tools'
        assert tools_dir.exists()

        py_files = list(tools_dir.glob('*.py'))
        assert len(py_files) > 0, "No PQC tools found"


class TestSoTTestStructure:
    """Test test directory structure"""

    def test_test_dir_exists(self):
        """Test test directory exists"""
        test_dir = REPO_ROOT / '11_test_simulation'
        assert test_dir.exists()

    def test_compliance_tests_exist(self):
        """Test compliance test directory exists"""
        compliance_dir = REPO_ROOT / '11_test_simulation' / 'tests_compliance'
        assert compliance_dir.exists()

        test_files = list(compliance_dir.glob('test_*.py'))
        assert len(test_files) > 0, "No test files found"


class TestSoTCLITools:
    """Test CLI tools exist and are valid"""

    def test_cli_dir_exists(self):
        """Test CLI directory exists"""
        cli_dir = REPO_ROOT / '12_tooling' / 'cli'
        assert cli_dir.exists()

    def test_validator_cli_exists(self):
        """Test validator CLI exists"""
        cli_file = REPO_ROOT / '12_tooling' / 'cli' / 'sot_validator_complete_cli.py'
        assert cli_file.exists(), f"Validator CLI not found at {cli_file}"

    def test_unified_cli_exists(self):
        """Test unified CLI exists"""
        cli_file = REPO_ROOT / '12_tooling' / 'cli' / 'sot_cli_unified.py'
        assert cli_file.exists(), f"Unified CLI not found at {cli_file}"

    def test_autopilot_cli_exists(self):
        """Test autopilot CLI exists"""
        cli_file = REPO_ROOT / '12_tooling' / 'cli' / 'sot_cli_autopilot.py'
        assert cli_file.exists(), f"Autopilot CLI not found at {cli_file}"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
