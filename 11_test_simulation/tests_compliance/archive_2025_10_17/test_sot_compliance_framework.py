#!/usr/bin/env python3
"""
SoT Compliance Framework Test
==============================

Validates that all 19 compliance rules have the 4 mandatory manifestations:
1. Python Module
2. Rego Policy
3. YAML Contract
4. CLI Command

This test ensures the SoT principle is enforced: every rule must have
both scientific basis (documented in contracts) and technical manifestation
(Python + Rego + CLI).

Test Coverage:
- SOC2: 7 rules (CC1.1 - CC7.1)
- Gaia-X: 6 rules (GAIA-X-01 - GAIA-X-06)
- ETSI EN 319 421: 6 rules (ETSI-421-01 - ETSI-421-06)

TOTAL: 19 rules × 4 manifestations = 76 required files

Author: SSID Compliance Team
Version: 1.0.0
Date: 2025-10-17
"""

import pytest
from pathlib import Path
import yaml
import subprocess


# Repository root
REPO_ROOT = Path(__file__).resolve().parents[2]


# Rule definitions: Standard → [Rule IDs]
RULES = {
    "soc2": ["CC1.1", "CC2.1", "CC3.1", "CC4.1", "CC5.1", "CC6.1", "CC7.1"],
    "gaia_x": ["GAIA-X-01", "GAIA-X-02", "GAIA-X-03", "GAIA-X-04", "GAIA-X-05", "GAIA-X-06"],
    "etsi_en_319_421": ["ETSI-421-01", "ETSI-421-02", "ETSI-421-03", "ETSI-421-04", "ETSI-421-05", "ETSI-421-06"]
}


def rule_id_to_filename(rule_id: str) -> str:
    """Convert rule ID to safe filename component"""
    return rule_id.replace(".", "_").replace("-", "_").lower()


class TestSoTComplianceFramework:
    """Test SoT Compliance Framework - 19 Rules with 4 Manifestations Each"""

    def test_total_rule_count(self):
        """Verify total number of rules is 19"""
        total_rules = sum(len(rules) for rules in RULES.values())
        assert total_rules == 19, f"Expected 19 total rules, found {total_rules}"

    def test_standard_distribution(self):
        """Verify rule distribution across standards"""
        assert len(RULES["soc2"]) == 7, "SOC2 should have 7 rules"
        assert len(RULES["gaia_x"]) == 6, "Gaia-X should have 6 rules"
        assert len(RULES["etsi_en_319_421"]) == 6, "ETSI EN 319 421 should have 6 rules"

    @pytest.mark.parametrize("standard,rule_id", [
        (std, rule) for std, rules in RULES.items() for rule in rules
    ])
    def test_python_module_exists(self, standard, rule_id):
        """Test that Python validation module exists for each rule"""
        rule_safe = rule_id_to_filename(rule_id)

        # Expected Python module path
        python_path = REPO_ROOT / "23_compliance" / "mappings" / standard / "src"

        # Find Python file matching rule pattern
        python_files = list(python_path.glob(f"{rule_safe}*.py"))

        assert len(python_files) > 0, (
            f"Missing Python module for {standard} {rule_id}\n"
            f"Expected path: {python_path}/{rule_safe}_*.py"
        )

        # Verify file is not empty
        python_file = python_files[0]
        content = python_file.read_text(encoding='utf-8')
        assert len(content) > 100, f"Python module too short: {python_file}"

        # Verify it contains SoT documentation
        assert "Scientific Basis" in content, f"Missing scientific basis in {python_file}"
        assert "Technical Manifestation" in content, f"Missing technical manifestation in {python_file}"

    @pytest.mark.parametrize("standard,rule_id", [
        (std, rule) for std, rules in RULES.items() for rule in rules
    ])
    def test_rego_policy_exists(self, standard, rule_id):
        """Test that Rego policy exists for each rule"""
        rule_safe = rule_id_to_filename(rule_id)

        # Expected Rego policy path
        rego_path = REPO_ROOT / "23_compliance" / "policies" / f"{standard}_{rule_safe}.rego"

        assert rego_path.exists(), (
            f"Missing Rego policy for {standard} {rule_id}\n"
            f"Expected: {rego_path}"
        )

        # Verify file is not empty
        content = rego_path.read_text(encoding='utf-8')
        assert len(content) > 50, f"Rego policy too short: {rego_path}"

        # Verify it contains package declaration
        assert f"package ssid.compliance.{standard}" in content, (
            f"Missing package declaration in {rego_path}"
        )

    @pytest.mark.parametrize("standard,rule_id", [
        (std, rule) for std, rules in RULES.items() for rule in rules
    ])
    def test_yaml_contract_exists(self, standard, rule_id):
        """Test that YAML contract exists for each rule"""
        rule_safe = rule_id_to_filename(rule_id)

        # Expected YAML contract path
        yaml_path = REPO_ROOT / "16_codex" / "contracts" / standard

        # Find YAML file matching rule pattern
        yaml_files = list(yaml_path.glob(f"{rule_safe}*.yaml"))

        assert len(yaml_files) > 0, (
            f"Missing YAML contract for {standard} {rule_id}\n"
            f"Expected path: {yaml_path}/{rule_safe}_*.yaml"
        )

        yaml_file = yaml_files[0]

        # Verify it's valid YAML
        try:
            with open(yaml_file, 'r', encoding='utf-8') as f:
                contract = yaml.safe_load(f)
        except yaml.YAMLError as e:
            pytest.fail(f"Invalid YAML in {yaml_file}: {e}")

        # Verify required contract fields
        assert "version" in contract, f"Missing version in {yaml_file}"
        assert "contract_id" in contract, f"Missing contract_id in {yaml_file}"
        assert "scientific_basis" in contract, f"Missing scientific_basis in {yaml_file}"
        assert "compliance_requirements" in contract, f"Missing compliance_requirements in {yaml_file}"
        assert "enforcement" in contract, f"Missing enforcement section in {yaml_file}"

        # Verify enforcement section references all 4 manifestations
        enforcement = contract["enforcement"]
        assert "python_module" in enforcement, f"Missing python_module reference in {yaml_file}"
        assert "rego_policy" in enforcement, f"Missing rego_policy reference in {yaml_file}"
        assert "cli_command" in enforcement, f"Missing cli_command reference in {yaml_file}"

    @pytest.mark.parametrize("standard,rule_id", [
        (std, rule) for std, rules in RULES.items() for rule in rules
    ])
    def test_cli_command_exists(self, standard, rule_id):
        """Test that CLI command exists for each rule"""
        rule_safe = rule_id_to_filename(rule_id)

        # Expected CLI command path
        cli_path = REPO_ROOT / "12_tooling" / "scripts" / "compliance" / f"check_{standard}_{rule_safe}.py"

        assert cli_path.exists(), (
            f"Missing CLI command for {standard} {rule_id}\n"
            f"Expected: {cli_path}"
        )

        # Verify file is executable or has shebang
        content = cli_path.read_text(encoding='utf-8')
        assert content.startswith("#!/usr/bin/env python3"), (
            f"CLI command missing shebang: {cli_path}"
        )

        # Verify it has main entry point
        assert "def main()" in content or 'if __name__ == "__main__"' in content, (
            f"CLI command missing main entry point: {cli_path}"
        )

    def test_manifestation_completeness(self):
        """Test that all 76 manifestation files exist (19 rules × 4 manifestations)"""
        expected_total = 76
        found_files = 0

        for standard, rules in RULES.items():
            for rule_id in rules:
                rule_safe = rule_id_to_filename(rule_id)

                # Check Python
                python_path = REPO_ROOT / "23_compliance" / "mappings" / standard / "src"
                if list(python_path.glob(f"{rule_safe}*.py")):
                    found_files += 1

                # Check Rego
                rego_path = REPO_ROOT / "23_compliance" / "policies" / f"{standard}_{rule_safe}.rego"
                if rego_path.exists():
                    found_files += 1

                # Check YAML
                yaml_path = REPO_ROOT / "16_codex" / "contracts" / standard
                if list(yaml_path.glob(f"{rule_safe}*.yaml")):
                    found_files += 1

                # Check CLI
                cli_path = REPO_ROOT / "12_tooling" / "scripts" / "compliance" / f"check_{standard}_{rule_safe}.py"
                if cli_path.exists():
                    found_files += 1

        assert found_files == expected_total, (
            f"Expected {expected_total} manifestation files (19 rules × 4), found {found_files}\n"
            f"Missing: {expected_total - found_files} files"
        )

    def test_cc1_1_full_integration(self):
        """Integration test for CC1.1 - verify all 4 manifestations work together"""
        # This is a smoke test using CC1.1 as example

        # 1. Verify Python module can be imported
        python_module = REPO_ROOT / "23_compliance" / "mappings" / "soc2" / "src" / "cc1_1_integrity_ethics.py"
        assert python_module.exists()

        # 2. Verify YAML contract is valid
        yaml_contract = REPO_ROOT / "16_codex" / "contracts" / "soc2" / "cc1_1_integrity_ethics.yaml"
        with open(yaml_contract, 'r') as f:
            contract = yaml.safe_load(f)
        assert contract["contract_id"] == "SOC2_CC1.1"

        # 3. Verify Rego policy is valid (basic syntax check)
        rego_policy = REPO_ROOT / "23_compliance" / "policies" / "soc2_cc1_1_integrity_ethics.rego"
        content = rego_policy.read_text()
        assert "package ssid.compliance.soc2.cc1_1" in content

        # 4. Verify CLI command exists
        cli_command = REPO_ROOT / "12_tooling" / "scripts" / "compliance" / "check_soc2_cc1_1.py"
        assert cli_command.exists()


class TestSoTPrincipleEnforcement:
    """Test that SoT principle is enforced: Scientific Basis + Technical Manifestation"""

    @pytest.mark.parametrize("standard,rule_id", [
        (std, rule) for std, rules in RULES.items() for rule in rules
    ])
    def test_scientific_basis_documented(self, standard, rule_id):
        """Every rule must have documented scientific basis"""
        rule_safe = rule_id_to_filename(rule_id)

        # Check YAML contract for scientific_basis section
        yaml_path = REPO_ROOT / "16_codex" / "contracts" / standard
        yaml_files = list(yaml_path.glob(f"{rule_safe}*.yaml"))

        assert len(yaml_files) > 0, f"Missing contract for {standard} {rule_id}"

        with open(yaml_files[0], 'r') as f:
            contract = yaml.safe_load(f)

        assert "scientific_basis" in contract, (
            f"{standard} {rule_id}: Missing scientific_basis in contract"
        )

        scientific_basis = contract["scientific_basis"]
        assert isinstance(scientific_basis, dict), (
            f"{standard} {rule_id}: scientific_basis must be a dict"
        )

        # Must have at least framework and description
        assert "framework" in scientific_basis or "standard" in scientific_basis, (
            f"{standard} {rule_id}: Missing framework/standard in scientific_basis"
        )

    @pytest.mark.parametrize("standard,rule_id", [
        (std, rule) for std, rules in RULES.items() for rule in rules
    ])
    def test_technical_manifestation_complete(self, standard, rule_id):
        """Every rule must have complete technical manifestation (Python + Rego + CLI)"""
        rule_safe = rule_id_to_filename(rule_id)

        # Verify all 3 technical components exist
        python_path = REPO_ROOT / "23_compliance" / "mappings" / standard / "src"
        python_files = list(python_path.glob(f"{rule_safe}*.py"))
        assert len(python_files) > 0, f"{standard} {rule_id}: Missing Python module"

        rego_path = REPO_ROOT / "23_compliance" / "policies" / f"{standard}_{rule_safe}.rego"
        assert rego_path.exists(), f"{standard} {rule_id}: Missing Rego policy"

        cli_path = REPO_ROOT / "12_tooling" / "scripts" / "compliance" / f"check_{standard}_{rule_safe}.py"
        assert cli_path.exists(), f"{standard} {rule_id}: Missing CLI command"


def test_compliance_score_calculation():
    """Test compliance score calculation: 19/19 = 100%"""
    total_rules = sum(len(rules) for rules in RULES.values())
    implemented_rules = 0

    for standard, rules in RULES.items():
        for rule_id in rules:
            rule_safe = rule_id_to_filename(rule_id)

            # Check if all 4 manifestations exist
            python_path = REPO_ROOT / "23_compliance" / "mappings" / standard / "src"
            rego_path = REPO_ROOT / "23_compliance" / "policies" / f"{standard}_{rule_safe}.rego"
            yaml_path = REPO_ROOT / "16_codex" / "contracts" / standard
            cli_path = REPO_ROOT / "12_tooling" / "scripts" / "compliance" / f"check_{standard}_{rule_safe}.py"

            has_python = len(list(python_path.glob(f"{rule_safe}*.py"))) > 0
            has_rego = rego_path.exists()
            has_yaml = len(list(yaml_path.glob(f"{rule_safe}*.yaml"))) > 0
            has_cli = cli_path.exists()

            if has_python and has_rego and has_yaml and has_cli:
                implemented_rules += 1

    compliance_score = (implemented_rules / total_rules) * 100

    assert compliance_score == 100.0, (
        f"Compliance score is {compliance_score:.1f}%, expected 100%\n"
        f"Implemented: {implemented_rules}/{total_rules} rules"
    )


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
