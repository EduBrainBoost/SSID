#!/usr/bin/env python3
"""
SoT Coverage Checker - Deterministic Validation of ALL 5 SoT Artifacts
=======================================================================

Purpose:
--------
Ensures 100% coverage of ALL Master-Rules from SoT_Manual_Coverage_Masterlist
in ALL 5 SoT artifacts:
  1. Contract (OpenAPI/JSON-Schema) - 10_interoperability/contracts/
  2. Core (Core Logic) - 03_core/
  3. Policy (Compliance/Governance) - 07_governance_legal/ + 23_compliance/
  4. CLI (Command-Line Interface) - 12_tooling/cli/
  5. Test (Test Suites) - 11_test_simulation/

Zero-Tolerance Policy:
----------------------
- NO Ghost Rules (in code but not in Master-List)
- NO Shadow Rules (in Master-List but not in code)
- NO Partial Coverage (all 5 artifacts MUST implement ALL rules)
- Exit Code 0 ONLY if 100% coverage

Author: Claude Code AI
Date: 2025-10-19
Version: 1.0.0
"""

import sys
import os
import yaml
import json
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum

# ANSI Colors for terminal output
class Color:
    RESET = "\033[0m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"

class CoverageStatus(Enum):
    """Coverage status for a rule"""
    COVERED = "COVERED"
    MISSING = "MISSING"
    PARTIAL = "PARTIAL"
    GHOST = "GHOST"  # In code but not in Master-List
    SHADOW = "SHADOW"  # In Master-List but not in code

@dataclass
class Rule:
    """Represents a single SoT rule from Master-List"""
    regel_id: str
    kategorie: str
    beschreibung: str
    zeilennummer: int or str
    priority: str
    enforcement: str = ""
    originaltext: str = ""
    feld: str = ""
    wert: any = None
    referenced_file: str = ""

@dataclass
class CoverageReport:
    """Coverage report for all 5 SoT artifacts"""
    total_rules: int = 0
    covered_rules: int = 0
    missing_rules: int = 0
    partial_rules: int = 0
    ghost_rules: int = 0
    shadow_rules: int = 0

    # Per-artifact coverage
    contract_coverage: float = 0.0
    core_coverage: float = 0.0
    policy_coverage: float = 0.0
    cli_coverage: float = 0.0
    test_coverage: float = 0.0

    # Detailed findings
    missing_in_contract: List[str] = field(default_factory=list)
    missing_in_core: List[str] = field(default_factory=list)
    missing_in_policy: List[str] = field(default_factory=list)
    missing_in_cli: List[str] = field(default_factory=list)
    missing_in_test: List[str] = field(default_factory=list)

    ghost_rules_found: List[str] = field(default_factory=list)
    shadow_rules_found: List[str] = field(default_factory=list)

class SoTCoverageChecker:
    """Main Coverage Checker Class"""

    def __init__(self, repo_root: Path, masterlist_path: Path):
        self.repo_root = repo_root
        self.masterlist_path = masterlist_path
        self.rules: Dict[str, Rule] = {}
        self.report = CoverageReport()

        # Define SoT Artifact paths
        self.artifact_paths = {
            "contract": repo_root / "10_interoperability" / "contracts",
            "core": repo_root / "03_core",
            "policy": [
                repo_root / "07_governance_legal",
                repo_root / "23_compliance"
            ],
            "cli": repo_root / "12_tooling" / "cli",
            "test": repo_root / "11_test_simulation"
        }

    def load_master_list(self) -> None:
        """Load Master-Rule-List from YAML"""
        print(f"{Color.CYAN}Loading Master-Rule-List from: {self.masterlist_path}{Color.RESET}")

        with open(self.masterlist_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        # Extract rules from all sections
        sections = [
            'grundprinzipien',
            'token_architecture',
            'token_utility',
            'token_economics',
            'language_strategy',
            'multi_jurisdiction'
        ]

        for section in sections:
            if section not in data:
                continue

            section_data = data[section]

            # Handle different section structures
            if isinstance(section_data, list):
                rules_list = section_data
            elif isinstance(section_data, dict) and 'regeln' in section_data:
                rules_list = section_data['regeln']
            else:
                continue

            for rule_data in rules_list:
                rule = Rule(
                    regel_id=rule_data.get('regel_id', ''),
                    kategorie=rule_data.get('kategorie', ''),
                    beschreibung=rule_data.get('beschreibung', ''),
                    zeilennummer=rule_data.get('zeilennummer', 0),
                    priority=rule_data.get('priority', 'MEDIUM'),
                    enforcement=rule_data.get('enforcement', ''),
                    originaltext=rule_data.get('originaltext', ''),
                    feld=rule_data.get('feld', ''),
                    wert=rule_data.get('wert'),
                    referenced_file=rule_data.get('referenced_file', '')
                )
                self.rules[rule.regel_id] = rule

        self.report.total_rules = len(self.rules)
        print(f"{Color.GREEN}OK Loaded {self.report.total_rules} rules from Master-List{Color.RESET}\n")

    def check_contract_coverage(self) -> None:
        """Check coverage in Contract artifacts (OpenAPI/JSON-Schema)"""
        print(f"{Color.CYAN}Checking Contract (OpenAPI/JSON-Schema) coverage...{Color.RESET}")

        contract_path = self.artifact_paths["contract"]

        if not contract_path.exists():
            print(f"{Color.RED}X Contract path does not exist: {contract_path}{Color.RESET}")
            self.report.missing_in_contract = [r.regel_id for r in self.rules.values()]
            return

        # Search for OpenAPI/JSON-Schema files
        openapi_files = list(contract_path.rglob("*.openapi.yaml")) + \
                       list(contract_path.rglob("*.openapi.yml")) + \
                       list(contract_path.rglob("*.schema.json"))

        covered_rules = set()

        for file_path in openapi_files:
            content = file_path.read_text(encoding='utf-8')

            # Search for rule references in comments/descriptions
            for regel_id, rule in self.rules.items():
                if regel_id in content or \
                   rule.feld in content or \
                   rule.beschreibung.lower() in content.lower():
                    covered_rules.add(regel_id)

        self.report.contract_coverage = len(covered_rules) / self.report.total_rules * 100
        self.report.missing_in_contract = [r for r in self.rules.keys() if r not in covered_rules]

        print(f"{Color.YELLOW}  Coverage: {self.report.contract_coverage:.2f}%{Color.RESET}")
        print(f"{Color.YELLOW}  Missing: {len(self.report.missing_in_contract)} rules{Color.RESET}\n")

    def check_core_coverage(self) -> None:
        """Check coverage in Core Logic"""
        print(f"{Color.CYAN}Checking Core Logic coverage...{Color.RESET}")

        core_path = self.artifact_paths["core"]

        if not core_path.exists():
            print(f"{Color.RED}X Core path does not exist: {core_path}{Color.RESET}")
            self.report.missing_in_core = [r.regel_id for r in self.rules.values()]
            return

        # Search for Python/JS/TS files in core
        code_files = list(core_path.rglob("*.py")) + \
                    list(core_path.rglob("*.js")) + \
                    list(core_path.rglob("*.ts"))

        covered_rules = set()

        for file_path in code_files:
            content = file_path.read_text(encoding='utf-8', errors='ignore')

            # Search for rule references in code/comments
            for regel_id, rule in self.rules.items():
                if regel_id in content or \
                   rule.feld in content:
                    covered_rules.add(regel_id)

        self.report.core_coverage = len(covered_rules) / self.report.total_rules * 100
        self.report.missing_in_core = [r for r in self.rules.keys() if r not in covered_rules]

        print(f"{Color.YELLOW}  Coverage: {self.report.core_coverage:.2f}%{Color.RESET}")
        print(f"{Color.YELLOW}  Missing: {len(self.report.missing_in_core)} rules{Color.RESET}\n")

    def check_policy_coverage(self) -> None:
        """Check coverage in Policy artifacts (Compliance/Governance)"""
        print(f"{Color.CYAN}Checking Policy (Compliance/Governance) coverage...{Color.RESET}")

        covered_rules = set()

        for policy_path in self.artifact_paths["policy"]:
            if not policy_path.exists():
                continue

            # Search for YAML/MD files
            policy_files = list(policy_path.rglob("*.yaml")) + \
                          list(policy_path.rglob("*.yml")) + \
                          list(policy_path.rglob("*.md"))

            for file_path in policy_files:
                content = file_path.read_text(encoding='utf-8', errors='ignore')

                for regel_id, rule in self.rules.items():
                    if regel_id in content or \
                       rule.feld in content or \
                       rule.beschreibung.lower() in content.lower():
                        covered_rules.add(regel_id)

        self.report.policy_coverage = len(covered_rules) / self.report.total_rules * 100
        self.report.missing_in_policy = [r for r in self.rules.keys() if r not in covered_rules]

        print(f"{Color.YELLOW}  Coverage: {self.report.policy_coverage:.2f}%{Color.RESET}")
        print(f"{Color.YELLOW}  Missing: {len(self.report.missing_in_policy)} rules{Color.RESET}\n")

    def check_cli_coverage(self) -> None:
        """Check coverage in CLI artifacts"""
        print(f"{Color.CYAN}Checking CLI coverage...{Color.RESET}")

        cli_path = self.artifact_paths["cli"]

        if not cli_path.exists():
            print(f"{Color.RED}X CLI path does not exist: {cli_path}{Color.RESET}")
            self.report.missing_in_cli = [r.regel_id for r in self.rules.values()]
            return

        # Search for CLI files
        cli_files = list(cli_path.rglob("*.py")) + \
                   list(cli_path.rglob("*.sh")) + \
                   list(cli_path.rglob("*.bash"))

        covered_rules = set()

        for file_path in cli_files:
            content = file_path.read_text(encoding='utf-8', errors='ignore')

            for regel_id, rule in self.rules.items():
                if regel_id in content or \
                   rule.feld in content:
                    covered_rules.add(regel_id)

        self.report.cli_coverage = len(covered_rules) / self.report.total_rules * 100
        self.report.missing_in_cli = [r for r in self.rules.keys() if r not in covered_rules]

        print(f"{Color.YELLOW}  Coverage: {self.report.cli_coverage:.2f}%{Color.RESET}")
        print(f"{Color.YELLOW}  Missing: {len(self.report.missing_in_cli)} rules{Color.RESET}\n")

    def check_test_coverage(self) -> None:
        """Check coverage in Test Suites"""
        print(f"{Color.CYAN}Checking Test Suite coverage...{Color.RESET}")

        test_path = self.artifact_paths["test"]

        if not test_path.exists():
            print(f"{Color.RED}X Test path does not exist: {test_path}{Color.RESET}")
            self.report.missing_in_test = [r.regel_id for r in self.rules.values()]
            return

        # Search for test files
        test_files = list(test_path.rglob("*test*.py")) + \
                    list(test_path.rglob("*spec*.py")) + \
                    list(test_path.rglob("*.test.js")) + \
                    list(test_path.rglob("*.spec.js"))

        covered_rules = set()

        for file_path in test_files:
            content = file_path.read_text(encoding='utf-8', errors='ignore')

            for regel_id, rule in self.rules.items():
                if regel_id in content or \
                   rule.feld in content:
                    covered_rules.add(regel_id)

        self.report.test_coverage = len(covered_rules) / self.report.total_rules * 100
        self.report.missing_in_test = [r for r in self.rules.keys() if r not in covered_rules]

        print(f"{Color.YELLOW}  Coverage: {self.report.test_coverage:.2f}%{Color.RESET}")
        print(f"{Color.YELLOW}  Missing: {len(self.report.missing_in_test)} rules{Color.RESET}\n")

    def detect_ghost_rules(self) -> None:
        """Detect Ghost Rules (in code but not in Master-List)"""
        print(f"{Color.CYAN}Detecting Ghost Rules (in code but not in Master-List)...{Color.RESET}")

        # Search for SOT-MD-* patterns in all SoT artifacts
        ghost_pattern = re.compile(r'SOT-MD-\d+')
        found_ids = set()

        for artifact_name, artifact_path in self.artifact_paths.items():
            paths = [artifact_path] if not isinstance(artifact_path, list) else artifact_path

            for path in paths:
                if not path.exists():
                    continue

                for file_path in path.rglob("*"):
                    if file_path.is_file():
                        try:
                            content = file_path.read_text(encoding='utf-8', errors='ignore')
                            matches = ghost_pattern.findall(content)
                            found_ids.update(matches)
                        except:
                            pass

        # Ghost rules are found but not in Master-List
        master_ids = set(self.rules.keys())
        ghost_ids = found_ids - master_ids

        self.report.ghost_rules = len(ghost_ids)
        self.report.ghost_rules_found = sorted(list(ghost_ids))

        if ghost_ids:
            print(f"{Color.RED}  X Found {len(ghost_ids)} Ghost Rules: {ghost_ids}{Color.RESET}\n")
        else:
            print(f"{Color.GREEN}  OK No Ghost Rules found{Color.RESET}\n")

    def detect_shadow_rules(self) -> None:
        """Detect Shadow Rules (in Master-List but not in ANY code)"""
        print(f"{Color.CYAN}Detecting Shadow Rules (in Master-List but not in ANY code)...{Color.RESET}")

        # Shadow rules are in Master-List but missing from ALL 5 artifacts
        all_missing = set(self.report.missing_in_contract) & \
                     set(self.report.missing_in_core) & \
                     set(self.report.missing_in_policy) & \
                     set(self.report.missing_in_cli) & \
                     set(self.report.missing_in_test)

        self.report.shadow_rules = len(all_missing)
        self.report.shadow_rules_found = sorted(list(all_missing))

        if all_missing:
            print(f"{Color.RED}  X Found {len(all_missing)} Shadow Rules: {all_missing}{Color.RESET}\n")
        else:
            print(f"{Color.GREEN}  OK No Shadow Rules found{Color.RESET}\n")

    def generate_report(self) -> None:
        """Generate final coverage report"""
        print(f"\n{Color.BOLD}{Color.CYAN}{'='*80}{Color.RESET}")
        print(f"{Color.BOLD}{Color.CYAN}SoT COVERAGE CHECKER - FINAL REPORT{Color.RESET}")
        print(f"{Color.BOLD}{Color.CYAN}{'='*80}{Color.RESET}\n")

        # Overall statistics
        print(f"{Color.BOLD}Total Rules in Master-List:{Color.RESET} {self.report.total_rules}")

        # Per-Artifact Coverage
        print(f"\n{Color.BOLD}Per-Artifact Coverage:{Color.RESET}")
        print(f"  Contract (OpenAPI/JSON-Schema): {self.report.contract_coverage:.2f}%")
        print(f"  Core (Core Logic):              {self.report.core_coverage:.2f}%")
        print(f"  Policy (Compliance/Governance): {self.report.policy_coverage:.2f}%")
        print(f"  CLI (Command-Line Interface):   {self.report.cli_coverage:.2f}%")
        print(f"  Test (Test Suites):             {self.report.test_coverage:.2f}%")

        # Average coverage
        avg_coverage = (self.report.contract_coverage +
                       self.report.core_coverage +
                       self.report.policy_coverage +
                       self.report.cli_coverage +
                       self.report.test_coverage) / 5

        print(f"\n{Color.BOLD}Average Coverage Across All 5 Artifacts:{Color.RESET} {avg_coverage:.2f}%")

        # Ghost/Shadow Rules
        print(f"\n{Color.BOLD}Zero-Tolerance Policy Violations:{Color.RESET}")
        print(f"  Ghost Rules (in code, not in Master-List):  {self.report.ghost_rules}")
        print(f"  Shadow Rules (in Master-List, not in code): {self.report.shadow_rules}")

        # Final verdict
        print(f"\n{Color.BOLD}{'='*80}{Color.RESET}")
        if avg_coverage == 100.0 and self.report.ghost_rules == 0 and self.report.shadow_rules == 0:
            print(f"{Color.BOLD}{Color.GREEN}OK PASS - 100% COVERAGE ACHIEVED - ZERO VIOLATIONS{Color.RESET}")
            print(f"{Color.BOLD}{Color.CYAN}{'='*80}{Color.RESET}\n")
            return True
        else:
            print(f"{Color.BOLD}{Color.RED}X FAIL - COVERAGE GAPS OR VIOLATIONS DETECTED{Color.RESET}")
            print(f"{Color.BOLD}{Color.CYAN}{'='*80}{Color.RESET}\n")

            # Export detailed report
            self.export_coverage_report()
            return False

    def export_coverage_report(self) -> None:
        """Export detailed coverage report as YAML and Markdown"""
        timestamp = "20251019"

        # YAML report
        yaml_report_path = self.repo_root / "02_audit_logging" / "reports" / f"SoT_Coverage_Report_{timestamp}.yaml"

        report_data = {
            "metadata": {
                "timestamp": timestamp,
                "total_rules": self.report.total_rules,
                "status": "FAIL_COVERAGE_GAPS",
                "zero_tolerance_violated": True
            },
            "coverage": {
                "contract": f"{self.report.contract_coverage:.2f}%",
                "core": f"{self.report.core_coverage:.2f}%",
                "policy": f"{self.report.policy_coverage:.2f}%",
                "cli": f"{self.report.cli_coverage:.2f}%",
                "test": f"{self.report.test_coverage:.2f}%",
                "average": f"{(self.report.contract_coverage + self.report.core_coverage + self.report.policy_coverage + self.report.cli_coverage + self.report.test_coverage) / 5:.2f}%"
            },
            "violations": {
                "ghost_rules": self.report.ghost_rules_found,
                "shadow_rules": self.report.shadow_rules_found
            },
            "missing_rules": {
                "contract": self.report.missing_in_contract,
                "core": self.report.missing_in_core,
                "policy": self.report.missing_in_policy,
                "cli": self.report.missing_in_cli,
                "test": self.report.missing_in_test
            }
        }

        with open(yaml_report_path, 'w', encoding='utf-8') as f:
            yaml.dump(report_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

        print(f"{Color.GREEN}OK Exported detailed coverage report: {yaml_report_path}{Color.RESET}\n")

def main():
    """Main entry point"""
    # Repo root detection
    repo_root = Path(__file__).resolve().parent.parent.parent

    # Master-List path
    masterlist_path = repo_root / "02_audit_logging" / "reports" / "SoT_Manual_Coverage_Masterlist_CORRECTED_20251019.yaml"

    if not masterlist_path.exists():
        print(f"{Color.RED}ERROR: Master-List not found: {masterlist_path}{Color.RESET}")
        sys.exit(1)

    # Create checker instance
    checker = SoTCoverageChecker(repo_root, masterlist_path)

    # Load Master-List
    checker.load_master_list()

    # Check coverage in all 5 artifacts
    checker.check_contract_coverage()
    checker.check_core_coverage()
    checker.check_policy_coverage()
    checker.check_cli_coverage()
    checker.check_test_coverage()

    # Detect violations
    checker.detect_ghost_rules()
    checker.detect_shadow_rules()

    # Generate final report
    success = checker.generate_report()

    # Exit with appropriate code
    sys.exit(0 if success else 24)  # Exit 24 for ROOT-24-LOCK failure

if __name__ == "__main__":
    main()
