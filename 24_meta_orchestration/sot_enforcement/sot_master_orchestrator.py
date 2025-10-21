#!/usr/bin/env python3
"""
SoT Master Orchestrator (CONSOLIDATED)
========================================

Single Source of Truth (SoT) Principle - Master Enforcement Engine

This orchestrator coordinates all SoT rule validation across:
- Python Validators (03_core/validators/sot/sot_validator_core.py) - CONSOLIDATED
- OPA Policies (23_compliance/policies/sot/sot_policy.rego) - CONSOLIDATED
- YAML Contracts (16_codex/contracts/sot/sot_contract.yaml) - CONSOLIDATED
- CLI Commands (12_tooling/cli/sot_validator.py)
- Test Suite (11_test_simulation/tests_compliance/test_sot_validator.py) - CONSOLIDATED

Total Rules: 54 (SOT-001 through SOT-066 with gaps)

Author: SSID Core Team
Version: 2.0.0 (Consolidated)
Date: 2025-10-17
"""

import sys
import os
import json
import yaml
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Tuple
from datetime import datetime

# Add core module to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "03_core"))

# Import from CONSOLIDATED validator core
from validators.sot.sot_validator_core import (
    validate_all_sot_rules,
    generate_evidence_report,
    ALL_VALIDATORS
)


class SoTMasterOrchestrator:
    """Master orchestrator for SoT rule enforcement"""

    def __init__(self, config_path: str = None, verbose: bool = False):
        self.verbose = verbose
        self.config_path = config_path
        self.validation_results = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "version": "2.0.0",
            "total_rules": 54,  # Updated to consolidated validator (SOT-001 through SOT-066 with gaps)
            "passed": 0,
            "failed": 0,
            "errors": [],
            "warnings": [],
            "evidence": {}
        }

    def log(self, message: str, level: str = "INFO"):
        """Log message with timestamp"""
        if self.verbose or level in ["ERROR", "CRITICAL"]:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] [{level}] {message}")

    def load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML or JSON file"""
        self.log(f"Loading configuration from: {config_path}")

        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        with open(config_path, 'r', encoding='utf-8') as f:
            if config_path.endswith(('.yaml', '.yml')):
                return yaml.safe_load(f)
            elif config_path.endswith('.json'):
                return json.load(f)
            else:
                raise ValueError("Configuration must be YAML or JSON")

    def validate_python_modules(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate using consolidated Python validator"""
        self.log("=== Python Module Validation (Consolidated) ===", "INFO")

        results = {}

        try:
            # Use consolidated validator for ALL 54 rules
            validation_results = validate_all_sot_rules(config)

            # Group results by category for reporting
            categories = {
                "global_foundations": [],
                "yaml_markers": [],
                "hierarchy_markers": [],
                "entry_markers": [],
                "instance_properties": [],
                "deprecated_list": []
            }

            # Categorize rules by ID ranges
            for rule_id, result in validation_results.items():
                num = int(rule_id.split('-')[1])
                if 1 <= num <= 5:
                    categories["global_foundations"].append(result)
                elif 18 <= num <= 19:
                    categories["yaml_markers"].append(result)
                elif num in [20, 31, 37, 43]:
                    categories["hierarchy_markers"].append(result)
                elif num in [21, 26, 32, 38, 44, 49, 54]:
                    categories["entry_markers"].append(result)
                elif 22 <= num <= 58:
                    categories["instance_properties"].append(result)
                elif 59 <= num <= 66:
                    categories["deprecated_list"].append(result)

            # Create category-level summary
            for category, rule_results in categories.items():
                if rule_results:
                    passed = sum(1 for r in rule_results if r["is_valid"])
                    total = len(rule_results)
                    valid = (passed == total)
                    errors = [r["message"] for r in rule_results if not r["is_valid"]]

                    results[category] = {
                        "valid": valid,
                        "passed": passed,
                        "total": total,
                        "errors": errors
                    }

                    status = "✅ PASS" if valid else f"❌ FAIL ({passed}/{total})"
                    self.log(f"{category.replace('_', ' ').title()}: {status}")

            # Log overall stats
            total_rules = len(validation_results)
            total_passed = sum(1 for r in validation_results.values() if r["is_valid"])
            self.log(f"Overall: {total_passed}/{total_rules} rules passed")

        except Exception as e:
            self.log(f"❌ Consolidated validator ERROR - {str(e)}", "ERROR")
            results["error"] = {
                "valid": False,
                "errors": [str(e)]
            }

        return results

    def validate_opa_policies(self, config_path: str) -> Dict[str, Any]:
        """Validate using consolidated OPA policy"""
        self.log("=== OPA Policy Validation (Consolidated) ===", "INFO")

        results = {"valid": True, "errors": [], "policies_checked": []}

        # Check if OPA is installed
        try:
            subprocess.run(["opa", "version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.log("⚠️  WARNING: OPA not installed. Skipping OPA validation.", "WARNING")
            self.validation_results["warnings"].append("OPA not installed - policy validation skipped")
            return {"valid": True, "errors": [], "skipped": True}

        # Use CONSOLIDATED OPA policy
        policy_file = "23_compliance/policies/sot/sot_policy.rego"

        if os.path.exists(policy_file):
            try:
                # Check policy syntax
                check_result = subprocess.run(
                    ["opa", "check", policy_file],
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                if check_result.returncode == 0:
                    results["policies_checked"].append(policy_file)
                    self.log(f"✅ OPA Policy Syntax OK: {policy_file}")

                    # Evaluate policy against config
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config_data = f.read()

                    eval_result = subprocess.run(
                        ["opa", "eval", "-d", policy_file, "-i", config_path, "data.ssid.sot.consolidated.allow"],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )

                    if eval_result.returncode == 0:
                        self.log(f"✅ OPA Policy Evaluation OK")
                    else:
                        results["valid"] = False
                        error_msg = f"OPA evaluation failed: {eval_result.stderr}"
                        results["errors"].append(error_msg)
                        self.log(f"❌ {error_msg}", "ERROR")

                else:
                    results["valid"] = False
                    error_msg = f"OPA policy syntax error: {check_result.stderr}"
                    results["errors"].append(error_msg)
                    self.log(f"❌ {error_msg}", "ERROR")

            except subprocess.TimeoutExpired:
                results["valid"] = False
                error_msg = f"OPA policy timeout: {policy_file}"
                results["errors"].append(error_msg)
                self.log(f"❌ {error_msg}", "ERROR")

        else:
            results["valid"] = False
            error_msg = f"Consolidated OPA policy not found: {policy_file}"
            results["errors"].append(error_msg)
            self.log(f"❌ {error_msg}", "ERROR")

        return results

    def validate_yaml_contracts(self) -> Dict[str, Any]:
        """Validate consolidated YAML contract"""
        self.log("=== YAML Contract Validation (Consolidated) ===", "INFO")

        results = {"valid": True, "errors": [], "contracts_checked": []}

        # Use CONSOLIDATED YAML contract
        contract_file = "16_codex/contracts/sot/sot_contract.yaml"

        if os.path.exists(contract_file):
            try:
                with open(contract_file, 'r', encoding='utf-8') as f:
                    contract_data = yaml.safe_load(f)

                # Validate contract structure
                if "rules" not in contract_data:
                    results["valid"] = False
                    error_msg = "Contract missing 'rules' section"
                    results["errors"].append(error_msg)
                    self.log(f"❌ {error_msg}", "ERROR")
                else:
                    rule_count = len(contract_data["rules"])
                    results["contracts_checked"].append(contract_file)
                    self.log(f"✅ Contract OK: {contract_file} ({rule_count} rules documented)")

            except yaml.YAMLError as e:
                results["valid"] = False
                error_msg = f"Invalid YAML contract: {contract_file} - {str(e)}"
                results["errors"].append(error_msg)
                self.log(f"❌ {error_msg}", "ERROR")
        else:
            results["valid"] = False
            error_msg = f"Consolidated contract not found: {contract_file}"
            results["errors"].append(error_msg)
            self.log(f"❌ {error_msg}", "ERROR")

        return results

    def run_full_validation(self, config_path: str) -> Dict[str, Any]:
        """Run full SoT validation across all layers"""
        self.log("=" * 70, "INFO")
        self.log("SoT Master Orchestrator - Full Validation", "INFO")
        self.log("=" * 70, "INFO")

        # Load configuration
        try:
            config = self.load_config(config_path)
        except Exception as e:
            self.validation_results["errors"].append(f"Configuration load error: {str(e)}")
            self.log(f"❌ Configuration load failed: {str(e)}", "CRITICAL")
            return self.validation_results

        # 1. Python Module Validation
        python_results = self.validate_python_modules(config)
        self.validation_results["evidence"]["python_validators"] = python_results

        # 2. OPA Policy Validation
        opa_results = self.validate_opa_policies(config_path)
        self.validation_results["evidence"]["opa_policies"] = opa_results

        # 3. YAML Contract Validation
        yaml_results = self.validate_yaml_contracts()
        self.validation_results["evidence"]["yaml_contracts"] = yaml_results

        # Calculate summary
        total_passed = sum(1 for cat in python_results.values() if cat.get("valid", False))
        total_failed = len(python_results) - total_passed

        if not opa_results.get("skipped", False) and not opa_results["valid"]:
            total_failed += 1

        if not yaml_results["valid"]:
            total_failed += 1

        self.validation_results["passed"] = total_passed
        self.validation_results["failed"] = total_failed

        # Collect all errors
        for category, result in python_results.items():
            if result["errors"]:
                self.validation_results["errors"].extend(result["errors"])

        if opa_results.get("errors"):
            self.validation_results["errors"].extend(opa_results["errors"])

        if yaml_results.get("errors"):
            self.validation_results["errors"].extend(yaml_results["errors"])

        # Final summary
        self.log("=" * 70, "INFO")
        self.log("=== VALIDATION SUMMARY ===", "INFO")
        self.log(f"Total Categories: {len(python_results)}")
        self.log(f"✅ Passed: {total_passed}")
        self.log(f"❌ Failed: {total_failed}")
        self.log(f"⚠️  Warnings: {len(self.validation_results['warnings'])}")
        self.log("=" * 70, "INFO")

        return self.validation_results

    def save_evidence(self, output_path: str):
        """Save validation evidence to file"""
        self.log(f"Saving evidence to: {output_path}")

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.validation_results, f, indent=2)

        self.log(f"✅ Evidence saved: {output_path}")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="SoT Master Orchestrator - Full SoT Principle Enforcement"
    )

    parser.add_argument("--config", required=True, help="Configuration file (YAML/JSON)")
    parser.add_argument("--output", help="Output evidence file (JSON)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    # Create orchestrator
    orchestrator = SoTMasterOrchestrator(config_path=args.config, verbose=args.verbose)

    # Run validation
    results = orchestrator.run_full_validation(args.config)

    # Save evidence
    if args.output:
        orchestrator.save_evidence(args.output)

    # Exit with appropriate code
    if results["failed"] > 0:
        print("\n❌ SoT validation FAILED")
        sys.exit(24)  # ROOT-24-LOCK violation exit code
    else:
        print("\n✅ SoT validation PASSED")
        sys.exit(0)


if __name__ == "__main__":
    main()
