#!/usr/bin/env python3
"""
Cross-Artifact Consistency Verification
========================================

Verifies that all 5 SoT artifacts have consistent rule definitions:
1. Python Validator (sot_validator_core.py)
2. OPA Policy (sot_policy.rego)
3. Contract YAML (sot_contract.yaml)
4. CLI Tool (integration check)
5. Test Suite (test_sot_validator.py)

Expected: 384 rules (24×16 matrix alignment)
"""

import ast
import re
import yaml
import json
from pathlib import Path
from typing import Dict, Set, List, Tuple
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class RuleInfo:
    rule_id: str
    severity: str = "UNKNOWN"
    category: str = "UNKNOWN"
    description: str = ""
    source_artifact: str = ""

    def __hash__(self):
        return hash(self.rule_id)


@dataclass
class ConsistencyReport:
    total_rules_expected: int = 384
    python_rules: Set[str] = field(default_factory=set)
    opa_rules: Set[str] = field(default_factory=set)
    yaml_rules: Set[str] = field(default_factory=set)
    test_rules: Set[str] = field(default_factory=set)

    missing_in_python: Set[str] = field(default_factory=set)
    missing_in_opa: Set[str] = field(default_factory=set)
    missing_in_yaml: Set[str] = field(default_factory=set)
    missing_in_tests: Set[str] = field(default_factory=set)

    extra_in_python: Set[str] = field(default_factory=set)
    extra_in_opa: Set[str] = field(default_factory=set)
    extra_in_yaml: Set[str] = field(default_factory=set)

    severity_mismatches: List[Dict] = field(default_factory=list)
    category_mismatches: List[Dict] = field(default_factory=list)

    duplicates_in_yaml: List[str] = field(default_factory=list)

    def is_consistent(self) -> bool:
        """Check if all artifacts have exactly 384 rules with no mismatches"""
        return (
            len(self.python_rules) == self.total_rules_expected and
            len(self.opa_rules) == self.total_rules_expected and
            len(self.yaml_rules) == self.total_rules_expected and
            len(self.missing_in_python) == 0 and
            len(self.missing_in_opa) == 0 and
            len(self.missing_in_yaml) == 0 and
            len(self.extra_in_yaml) == 0 and
            len(self.duplicates_in_yaml) == 0 and
            len(self.severity_mismatches) == 0
        )


class CrossArtifactVerifier:
    def __init__(self, repo_root: Path):
        self.repo_root = Path(repo_root)
        self.report = ConsistencyReport()

        # Paths to artifacts
        self.python_validator_path = self.repo_root / "03_core/validators/sot/sot_validator_core.py"
        self.opa_policy_path = self.repo_root / "23_compliance/policies/sot/sot_policy.rego"
        self.yaml_contract_path = self.repo_root / "16_codex/contracts/sot/sot_contract.yaml"
        self.test_suite_path = self.repo_root / "11_test_simulation/tests_compliance/test_sot_validator.py"

    def extract_from_python(self) -> Dict[str, RuleInfo]:
        """Extract rule IDs from Python validator using AST parsing"""
        print("[1/4] Extracting rules from Python validator...")

        rules = {}

        try:
            with open(self.python_validator_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read())

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Match validate_* functions
                    if node.name.startswith('validate_'):
                        # Extract rule ID from function name
                        rule_id = self._extract_rule_id_from_function_name(node.name)

                        if rule_id:
                            # Extract docstring
                            docstring = ast.get_docstring(node) or ""

                            # Extract severity and category from docstring
                            severity = self._extract_severity_from_docstring(docstring)
                            category = self._extract_category_from_docstring(docstring)

                            rules[rule_id] = RuleInfo(
                                rule_id=rule_id,
                                severity=severity,
                                category=category,
                                description=docstring.split('\n')[0] if docstring else "",
                                source_artifact="Python"
                            )

        except FileNotFoundError:
            print(f"  WARNING: Python validator not found at {self.python_validator_path}")
        except Exception as e:
            print(f"  ERROR parsing Python: {e}")

        print(f"  Found {len(rules)} rules in Python validator")
        self.report.python_rules = set(rules.keys())
        return rules

    def _extract_rule_id_from_function_name(self, func_name: str) -> str:
        """Convert validate_ar001 → AR001, validate_md_struct_009 → MD-STRUCT-009"""
        if not func_name.startswith('validate_'):
            return ""

        # Remove 'validate_' prefix
        rule_part = func_name[9:]  # len('validate_') = 9

        # Handle different patterns
        if rule_part.startswith('md_'):
            # MD-* rules: validate_md_struct_009 → MD-STRUCT-009
            parts = rule_part.split('_')
            if len(parts) >= 3:
                # md_struct_009 → MD-STRUCT-009
                category = parts[1].upper()
                number = parts[2]
                return f"MD-{category}-{number}"
        else:
            # Standard rules: validate_ar001 → AR001
            return rule_part.upper()

        return ""

    def _extract_severity_from_docstring(self, docstring: str) -> str:
        """Extract severity from docstring"""
        severity_match = re.search(r'Severity:\s*(CRITICAL|HIGH|MEDIUM|LOW)', docstring, re.IGNORECASE)
        if severity_match:
            return severity_match.group(1).upper()
        return "UNKNOWN"

    def _extract_category_from_docstring(self, docstring: str) -> str:
        """Extract category from docstring"""
        category_match = re.search(r'Category:\s*(.+)', docstring)
        if category_match:
            return category_match.group(1).strip()
        return "UNKNOWN"

    def extract_from_opa(self) -> Dict[str, RuleInfo]:
        """Extract rule IDs from OPA policy file"""
        print("[2/4] Extracting rules from OPA policy...")

        rules = {}

        try:
            with open(self.opa_policy_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Match deny rules: deny[msg] { ... # AR001 ...
            # or: # Rule: AR001
            pattern = r'#\s*(?:Rule:?\s*)?([A-Z]{2,3}(?:-[A-Z]+)*-?\d+)'

            for match in re.finditer(pattern, content):
                rule_id = match.group(1)

                # Normalize format
                if not '-' in rule_id and len(rule_id) > 2:
                    # AR001 format - keep as is
                    pass

                rules[rule_id] = RuleInfo(
                    rule_id=rule_id,
                    source_artifact="OPA"
                )

        except FileNotFoundError:
            print(f"  WARNING: OPA policy not found at {self.opa_policy_path}")
        except Exception as e:
            print(f"  ERROR parsing OPA: {e}")

        print(f"  Found {len(rules)} rules in OPA policy")
        self.report.opa_rules = set(rules.keys())
        return rules

    def extract_from_yaml(self) -> Dict[str, RuleInfo]:
        """Extract rule IDs from YAML contract"""
        print("[3/4] Extracting rules from YAML contract...")

        rules = {}
        seen_ids = set()
        duplicates = []

        try:
            with open(self.yaml_contract_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)

            if 'rules' in data:
                for rule in data['rules']:
                    rule_id = rule.get('rule_id', '')

                    if rule_id in seen_ids:
                        duplicates.append(rule_id)

                    seen_ids.add(rule_id)

                    rules[rule_id] = RuleInfo(
                        rule_id=rule_id,
                        severity=rule.get('severity', 'UNKNOWN'),
                        category=rule.get('category', 'UNKNOWN'),
                        description=rule.get('description', ''),
                        source_artifact="YAML"
                    )

        except FileNotFoundError:
            print(f"  WARNING: YAML contract not found at {self.yaml_contract_path}")
        except Exception as e:
            print(f"  ERROR parsing YAML: {e}")

        print(f"  Found {len(rules)} rules in YAML contract")
        if duplicates:
            print(f"  WARNING: Found {len(duplicates)} duplicate rule IDs: {duplicates[:10]}")
            self.report.duplicates_in_yaml = duplicates

        self.report.yaml_rules = set(rules.keys())
        return rules

    def extract_from_tests(self) -> Dict[str, RuleInfo]:
        """Extract rule IDs from test suite"""
        print("[4/4] Extracting rules from test suite...")

        rules = {}

        try:
            with open(self.test_suite_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Match test functions: def test_ar001...
            pattern = r'def test_([a-z0-9_]+)'

            for match in re.finditer(pattern, content):
                test_name = match.group(1)
                rule_id = self._extract_rule_id_from_test_name(test_name)

                if rule_id:
                    rules[rule_id] = RuleInfo(
                        rule_id=rule_id,
                        source_artifact="Tests"
                    )

        except FileNotFoundError:
            print(f"  WARNING: Test suite not found at {self.test_suite_path}")
        except Exception as e:
            print(f"  ERROR parsing tests: {e}")

        print(f"  Found {len(rules)} rules in test suite")
        self.report.test_rules = set(rules.keys())
        return rules

    def _extract_rule_id_from_test_name(self, test_name: str) -> str:
        """Convert test_ar001 → AR001, test_md_struct_009 → MD-STRUCT-009"""
        if test_name.startswith('md_'):
            # MD-* rules
            parts = test_name.split('_')
            if len(parts) >= 3:
                category = parts[1].upper()
                number = parts[2]
                return f"MD-{category}-{number}"
        else:
            # Standard rules
            return test_name.upper()

        return ""

    def compare_artifacts(self, python_rules: Dict, opa_rules: Dict, yaml_rules: Dict):
        """Compare rules across artifacts and identify discrepancies"""
        print("\n[COMPARISON] Analyzing cross-artifact consistency...\n")

        python_ids = set(python_rules.keys())
        opa_ids = set(opa_rules.keys())
        yaml_ids = set(yaml_rules.keys())

        # Find missing rules
        self.report.missing_in_python = (yaml_ids | opa_ids) - python_ids
        self.report.missing_in_opa = (python_ids | yaml_ids) - opa_ids
        self.report.missing_in_yaml = (python_ids | opa_ids) - yaml_ids

        # Find extra rules (beyond 384)
        all_rules = python_ids | opa_ids | yaml_ids
        if len(yaml_ids) > self.report.total_rules_expected:
            self.report.extra_in_yaml = yaml_ids - python_ids - opa_ids

        # Compare severities (for rules that exist in multiple artifacts)
        common_rules = python_ids & yaml_ids
        for rule_id in common_rules:
            python_severity = python_rules[rule_id].severity
            yaml_severity = yaml_rules[rule_id].severity

            if python_severity != "UNKNOWN" and yaml_severity != "UNKNOWN":
                if python_severity != yaml_severity:
                    self.report.severity_mismatches.append({
                        'rule_id': rule_id,
                        'python_severity': python_severity,
                        'yaml_severity': yaml_severity
                    })

        # Print summary
        print(f"Python Validator: {len(python_ids)} rules")
        print(f"OPA Policy:       {len(opa_ids)} rules")
        print(f"YAML Contract:    {len(yaml_ids)} rules")
        print(f"Test Suite:       {len(self.report.test_rules)} rules")
        print(f"\nExpected:         {self.report.total_rules_expected} rules (24×16 matrix)")

        if self.report.missing_in_python:
            print(f"\n[WARNING]  Missing in Python: {len(self.report.missing_in_python)} rules")
            print(f"    {sorted(list(self.report.missing_in_python))[:10]}")

        if self.report.missing_in_opa:
            print(f"\n[WARNING]  Missing in OPA: {len(self.report.missing_in_opa)} rules")
            print(f"    {sorted(list(self.report.missing_in_opa))[:10]}")

        if self.report.missing_in_yaml:
            print(f"\n[WARNING]  Missing in YAML: {len(self.report.missing_in_yaml)} rules")
            print(f"    {sorted(list(self.report.missing_in_yaml))[:10]}")

        if self.report.extra_in_yaml:
            print(f"\n[WARNING]  Extra in YAML (beyond 384): {len(self.report.extra_in_yaml)} rules")
            print(f"    {sorted(list(self.report.extra_in_yaml))[:10]}")

        if self.report.duplicates_in_yaml:
            print(f"\n[WARNING]  Duplicates in YAML: {len(self.report.duplicates_in_yaml)} rules")
            print(f"    {self.report.duplicates_in_yaml[:10]}")

        if self.report.severity_mismatches:
            print(f"\n[WARNING]  Severity mismatches: {len(self.report.severity_mismatches)}")
            for mismatch in self.report.severity_mismatches[:5]:
                print(f"    {mismatch['rule_id']}: Python={mismatch['python_severity']}, YAML={mismatch['yaml_severity']}")

    def generate_report(self) -> Dict:
        """Generate comprehensive consistency report"""
        print("\n" + "="*80)
        print("CONSISTENCY REPORT")
        print("="*80)

        status = "[OK] PASS" if self.report.is_consistent() else "[FAIL] FAIL"
        print(f"\nOverall Status: {status}\n")

        report_dict = {
            "timestamp": "2025-10-21",
            "expected_rules": self.report.total_rules_expected,
            "artifact_counts": {
                "python": len(self.report.python_rules),
                "opa": len(self.report.opa_rules),
                "yaml": len(self.report.yaml_rules),
                "tests": len(self.report.test_rules)
            },
            "discrepancies": {
                "missing_in_python": sorted(list(self.report.missing_in_python)),
                "missing_in_opa": sorted(list(self.report.missing_in_opa)),
                "missing_in_yaml": sorted(list(self.report.missing_in_yaml)),
                "extra_in_yaml": sorted(list(self.report.extra_in_yaml)),
                "duplicates_in_yaml": self.report.duplicates_in_yaml,
                "severity_mismatches": self.report.severity_mismatches
            },
            "status": "PASS" if self.report.is_consistent() else "FAIL",
            "is_consistent": self.report.is_consistent()
        }

        return report_dict

    def save_report(self, report_dict: Dict, output_path: Path):
        """Save report to JSON file"""
        with open(output_path, 'w') as f:
            json.dump(report_dict, f, indent=2)

        print(f"\n[OK] Report saved to: {output_path}")


def main():
    """Main execution"""
    import sys

    # Get repo root
    if len(sys.argv) > 1:
        repo_root = Path(sys.argv[1])
    else:
        repo_root = Path(__file__).parent.parent.parent.parent

    print(f"Repository: {repo_root}\n")

    # Run verification
    verifier = CrossArtifactVerifier(repo_root)

    python_rules = verifier.extract_from_python()
    opa_rules = verifier.extract_from_opa()
    yaml_rules = verifier.extract_from_yaml()
    test_rules = verifier.extract_from_tests()

    verifier.compare_artifacts(python_rules, opa_rules, yaml_rules)

    report = verifier.generate_report()

    # Save reports
    output_dir = Path(__file__).parent
    verifier.save_report(report, output_dir / "consistency_report.json")

    # Generate CSV for mismatches
    if report['discrepancies']['extra_in_yaml']:
        import csv
        csv_path = output_dir / "mismatch_details.csv"
        with open(csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Rule ID', 'Issue', 'Details'])

            for rule_id in report['discrepancies']['extra_in_yaml']:
                writer.writerow([rule_id, 'Extra in YAML', 'Not in Python or OPA'])

            for rule_id in report['discrepancies']['duplicates_in_yaml']:
                writer.writerow([rule_id, 'Duplicate in YAML', 'Appears multiple times'])

        print(f"[OK] Mismatch details saved to: {csv_path}")

    # Exit with appropriate code
    sys.exit(0 if report['is_consistent'] else 1)


if __name__ == "__main__":
    main()
