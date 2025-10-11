#!/usr/bin/env python3
"""
SSID Policy Compiler - OPA/Rego Policy Generation

This script automatically generates OPA/Rego policies from compliance mapping files
(GDPR, DORA, MiCA, AMLD6) and validates their syntax.

Blueprint: v4.4.0 - Functional Expansion
Layer: L4 - Policy Layer
Compliance: GDPR / eIDAS / MiCA / DORA / AMLD6
"""

import json
import yaml
import hashlib
import argparse
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict

# Configuration
MAPPINGS_DIR = Path("23_compliance/mappings")
POLICY_OUTPUT_DIR = Path("23_compliance/policy")
POLICY_TEST_OUTPUT_DIR = Path("23_compliance/policy/tests")
AUDIT_LOG_PATH = Path("02_audit_logging/reports/policy_activation_log.json")


@dataclass
class PolicyRule:
    """Represents a single OPA/Rego policy rule."""
    rule_id: str
    regulation: str
    article: str
    obligation: str
    rego_code: str
    hash: str
    status: str = "active"

    @classmethod
    def from_mapping(cls, regulation: str, article: str, mapping_data: Dict) -> 'PolicyRule':
        """Create PolicyRule from mapping data."""
        rule_id = f"{regulation.lower()}_{article.replace('.', '_').replace(' ', '_')}"
        obligation = mapping_data.get('obligation', 'Compliance required')

        # Generate Rego code
        rego_code = cls._generate_rego_code(rule_id, regulation, article, obligation, mapping_data)

        # Calculate hash
        rule_hash = hashlib.sha256(rego_code.encode()).hexdigest()

        return cls(
            rule_id=rule_id,
            regulation=regulation,
            article=article,
            obligation=obligation,
            rego_code=rego_code,
            hash=rule_hash
        )

    @staticmethod
    def _generate_rego_code(rule_id: str, regulation: str, article: str,
                           obligation: str, mapping_data: Dict) -> str:
        """Generate OPA/Rego policy code."""
        # Extract compliance requirements
        requirements = mapping_data.get('requirements', [])
        severity = mapping_data.get('severity', 'medium')

        # Build Rego policy
        rego_lines = [
            f"# Policy: {regulation} - {article}",
            f"# Obligation: {obligation}",
            f"# Severity: {severity}",
            f"package ssid.compliance.{regulation.lower()}",
            "",
            f"# Rule: {rule_id}",
            f"{rule_id}_compliant {{",
        ]

        # Add requirements as conditions
        if requirements:
            for req in requirements:
                rego_lines.append(f"    # Requirement: {req}")
                # Convert requirement to Rego condition
                condition = PolicyRule._requirement_to_condition(req)
                rego_lines.append(f"    {condition}")
        else:
            # Default compliance check
            rego_lines.append(f"    # Default compliance check")
            rego_lines.append(f"    input.governance_enabled == true")
            rego_lines.append(f"    input.audit_trail_enabled == true")

        rego_lines.append("}")
        rego_lines.append("")

        # Add violation detection
        rego_lines.extend([
            f"{rule_id}_violation {{",
            f"    not {rule_id}_compliant",
            "}",
            "",
            f"{rule_id}_result = {{",
            f'    "regulation": "{regulation}",',
            f'    "article": "{article}",',
            f'    "compliant": {rule_id}_compliant,',
            f'    "violation": {rule_id}_violation,',
            f'    "severity": "{severity}",',
            f'    "obligation": "{obligation}"',
            "}",
            ""
        ])

        return "\n".join(rego_lines)

    @staticmethod
    def _requirement_to_condition(requirement: str) -> str:
        """Convert human-readable requirement to Rego condition."""
        req_lower = requirement.lower()

        # Common requirement patterns
        if "data protection" in req_lower or "privacy" in req_lower:
            return "input.data_protection_enabled == true"
        elif "audit" in req_lower or "logging" in req_lower:
            return "input.audit_trail_enabled == true"
        elif "encryption" in req_lower:
            return "input.encryption_enabled == true"
        elif "access control" in req_lower:
            return "input.access_control_enabled == true"
        elif "transparency" in req_lower:
            return "input.transparency_enabled == true"
        elif "incident" in req_lower or "breach" in req_lower:
            return "input.incident_response_enabled == true"
        elif "testing" in req_lower or "resilience" in req_lower:
            return "input.testing_enabled == true"
        elif "third party" in req_lower or "vendor" in req_lower:
            return "input.third_party_monitoring_enabled == true"
        else:
            # Generic compliance check
            return "input.compliance_framework_enabled == true"


@dataclass
class PolicyCompilationResult:
    """Result of policy compilation."""
    timestamp: str
    total_mappings: int
    total_policies: int
    policies_generated: List[str]
    policies_failed: List[str]
    output_files: List[str]
    hash: str
    status: str


class PolicyCompiler:
    """Compiles OPA/Rego policies from compliance mappings."""

    def __init__(self):
        self.mappings_dir = MAPPINGS_DIR
        self.policy_output_dir = POLICY_OUTPUT_DIR
        self.policy_test_output_dir = POLICY_TEST_OUTPUT_DIR
        self.audit_log_path = AUDIT_LOG_PATH
        self.policies: List[PolicyRule] = []

    def compile_all(self) -> PolicyCompilationResult:
        """Compile all policies from mapping files."""
        print("=" * 60)
        print("  SSID Policy Compiler - OPA/Rego Generation")
        print("  Blueprint v4.4.0 - Policy Layer Automation")
        print("=" * 60)
        print()

        # Scan mapping files
        mapping_files = self._scan_mapping_files()
        print(f"Found {len(mapping_files)} mapping files")
        print()

        # Extract policies
        policies_generated = []
        policies_failed = []

        for mapping_file in mapping_files:
            try:
                print(f"Processing: {mapping_file.name}")
                rules = self._extract_policies_from_mapping(mapping_file)
                self.policies.extend(rules)
                policies_generated.append(mapping_file.name)
                print(f"  -> Generated {len(rules)} policies")
            except Exception as e:
                print(f"  -> ERROR: {e}")
                policies_failed.append(mapping_file.name)

        print()
        print(f"Total policies generated: {len(self.policies)}")
        print()

        # Generate Rego files
        output_files = self._generate_rego_files()

        # Generate test files
        test_files = self._generate_test_files()
        output_files.extend(test_files)

        # Validate syntax (if OPA available)
        self._validate_rego_syntax()

        # Create audit log
        result = PolicyCompilationResult(
            timestamp=datetime.utcnow().isoformat() + "Z",
            total_mappings=len(mapping_files),
            total_policies=len(self.policies),
            policies_generated=policies_generated,
            policies_failed=policies_failed,
            output_files=[str(f) for f in output_files],
            hash=self._calculate_compilation_hash(),
            status="success" if not policies_failed else "partial_success"
        )

        self._write_audit_log(result)

        print()
        print("=" * 60)
        print("  Policy Compilation Complete")
        print("=" * 60)
        print()
        print(f"Status: {result.status.upper()}")
        print(f"Total Policies: {result.total_policies}")
        print(f"Output Files: {len(result.output_files)}")
        print(f"Compilation Hash: {result.hash[:16]}...")
        print()

        return result

    def _scan_mapping_files(self) -> List[Path]:
        """Scan for compliance mapping YAML files."""
        if not self.mappings_dir.exists():
            raise FileNotFoundError(f"Mappings directory not found: {self.mappings_dir}")

        yaml_files = list(self.mappings_dir.glob("*.yaml")) + list(self.mappings_dir.glob("*.yml"))
        return sorted(yaml_files)

    def _extract_policies_from_mapping(self, mapping_file: Path) -> List[PolicyRule]:
        """Extract policy rules from a mapping file."""
        with open(mapping_file, 'r', encoding='utf-8') as f:
            mapping_data = yaml.safe_load(f)

        if not mapping_data:
            return []

        # Determine regulation name from file or content
        regulation = mapping_data.get('regulation', mapping_file.stem.upper())

        # Extract articles/requirements
        policies = []
        articles = mapping_data.get('articles', mapping_data.get('requirements', {}))

        for article_key, article_data in articles.items():
            if isinstance(article_data, dict):
                policy_rule = PolicyRule.from_mapping(regulation, article_key, article_data)
                policies.append(policy_rule)

        return policies

    def _generate_rego_files(self) -> List[Path]:
        """Generate Rego policy files by regulation."""
        output_files = []

        # Group policies by regulation
        policies_by_regulation = {}
        for policy in self.policies:
            if policy.regulation not in policies_by_regulation:
                policies_by_regulation[policy.regulation] = []
            policies_by_regulation[policy.regulation].append(policy)

        # Generate file for each regulation
        for regulation, policies in policies_by_regulation.items():
            output_file = self.policy_output_dir / f"{regulation.lower()}_policies.rego"

            with open(output_file, 'w', encoding='utf-8') as f:
                # Header
                f.write(f"# SSID OPA/Rego Policies - {regulation}\n")
                f.write(f"# Auto-generated by policy_compiler.py\n")
                f.write(f"# Blueprint v4.4.0 - Policy Layer\n")
                f.write(f"# Generated: {datetime.utcnow().isoformat()}Z\n")
                f.write(f"# Total Rules: {len(policies)}\n\n")

                # Write all policies for this regulation
                for policy in policies:
                    f.write(policy.rego_code)
                    f.write("\n")

            output_files.append(output_file)
            print(f"Generated: {output_file}")

        # Generate consolidated active_policies.rego
        consolidated_file = self.policy_output_dir / "active_policies.rego"

        with open(consolidated_file, 'w', encoding='utf-8') as f:
            f.write("# SSID Active Policies - Consolidated\n")
            f.write("# Auto-generated by policy_compiler.py\n")
            f.write(f"# Blueprint v4.4.0 - Policy Layer\n")
            f.write(f"# Generated: {datetime.utcnow().isoformat()}Z\n")
            f.write(f"# Total Regulations: {len(policies_by_regulation)}\n")
            f.write(f"# Total Rules: {len(self.policies)}\n\n")

            f.write("package ssid.compliance\n\n")

            # Import all regulation packages
            for regulation in policies_by_regulation.keys():
                f.write(f'import data.ssid.compliance.{regulation.lower()}\n')

            f.write("\n# Consolidated compliance check\n")
            f.write("all_compliant {\n")
            for regulation in policies_by_regulation.keys():
                f.write(f"    {regulation.lower()}.compliant\n")
            f.write("}\n\n")

            f.write("# Collect all violations\n")
            f.write("violations[violation] {\n")
            for regulation in policies_by_regulation.keys():
                f.write(f"    violation := {regulation.lower()}.violation\n")
            f.write("}\n")

        output_files.append(consolidated_file)
        print(f"Generated: {consolidated_file}")

        return output_files

    def _generate_test_files(self) -> List[Path]:
        """Generate Rego test files."""
        output_files = []

        # Group policies by regulation
        policies_by_regulation = {}
        for policy in self.policies:
            if policy.regulation not in policies_by_regulation:
                policies_by_regulation[policy.regulation] = []
            policies_by_regulation[policy.regulation].append(policy)

        # Generate test file for each regulation
        for regulation, policies in policies_by_regulation.items():
            test_file = self.policy_test_output_dir / f"{regulation.lower()}_test.rego"

            with open(test_file, 'w', encoding='utf-8') as f:
                f.write(f"# SSID OPA/Rego Policy Tests - {regulation}\n")
                f.write(f"# Auto-generated by policy_compiler.py\n")
                f.write(f"# Blueprint v4.4.0 - Policy Layer\n")
                f.write(f"# Generated: {datetime.utcnow().isoformat()}Z\n\n")

                f.write(f"package ssid.compliance.{regulation.lower()}_test\n\n")
                f.write(f"import data.ssid.compliance.{regulation.lower()}\n\n")

                # Generate test cases
                for policy in policies[:3]:  # Sample first 3 policies
                    f.write(f"# Test: {policy.rule_id}\n")
                    f.write(f"test_{policy.rule_id}_compliant {{\n")
                    f.write(f"    {regulation.lower()}.{policy.rule_id}_compliant with input as {{\n")
                    f.write('        "governance_enabled": true,\n')
                    f.write('        "audit_trail_enabled": true,\n')
                    f.write('        "data_protection_enabled": true,\n')
                    f.write('        "encryption_enabled": true\n')
                    f.write('    }\n')
                    f.write('}\n\n')

                    f.write(f"test_{policy.rule_id}_violation {{\n")
                    f.write(f"    {regulation.lower()}.{policy.rule_id}_violation with input as {{\n")
                    f.write('        "governance_enabled": false\n')
                    f.write('    }\n')
                    f.write('}\n\n')

            output_files.append(test_file)
            print(f"Generated: {test_file}")

        # Generate consolidated test file
        consolidated_test = self.policy_test_output_dir / "policy_compliance_test.rego"

        with open(consolidated_test, 'w', encoding='utf-8') as f:
            f.write("# SSID Policy Compliance Tests - Consolidated\n")
            f.write("# Auto-generated by policy_compiler.py\n")
            f.write(f"# Generated: {datetime.utcnow().isoformat()}Z\n\n")

            f.write("package ssid.compliance_test\n\n")
            f.write("import data.ssid.compliance\n\n")

            f.write("# Test all policies are compliant with valid input\n")
            f.write("test_all_compliant {\n")
            f.write("    compliance.all_compliant with input as {\n")
            f.write('        "governance_enabled": true,\n')
            f.write('        "audit_trail_enabled": true,\n')
            f.write('        "data_protection_enabled": true,\n')
            f.write('        "encryption_enabled": true,\n')
            f.write('        "access_control_enabled": true,\n')
            f.write('        "transparency_enabled": true,\n')
            f.write('        "incident_response_enabled": true,\n')
            f.write('        "testing_enabled": true,\n')
            f.write('        "third_party_monitoring_enabled": true,\n')
            f.write('        "compliance_framework_enabled": true\n')
            f.write('    }\n')
            f.write('}\n\n')

            f.write("# Test violations are detected with invalid input\n")
            f.write("test_violations_detected {\n")
            f.write("    count(compliance.violations) > 0 with input as {\n")
            f.write('        "governance_enabled": false\n')
            f.write('    }\n')
            f.write('}\n')

        output_files.append(consolidated_test)
        print(f"Generated: {consolidated_test}")

        return output_files

    def _validate_rego_syntax(self):
        """Validate Rego syntax using OPA CLI (if available)."""
        import shutil

        if not shutil.which('opa'):
            print()
            print("! OPA CLI not found - skipping syntax validation")
            print("  Install OPA: https://www.openpolicyagent.org/docs/latest/#running-opa")
            return

        print()
        print("Validating Rego syntax with OPA...")

        import subprocess

        rego_files = list(self.policy_output_dir.glob("*.rego"))

        for rego_file in rego_files:
            try:
                result = subprocess.run(
                    ['opa', 'check', str(rego_file)],
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                if result.returncode == 0:
                    print(f"  OK: {rego_file.name}")
                else:
                    print(f"  ERROR: {rego_file.name}")
                    print(f"    {result.stderr}")
            except Exception as e:
                print(f"  SKIP: {rego_file.name} - {e}")

    def _calculate_compilation_hash(self) -> str:
        """Calculate hash of all generated policies."""
        policy_hashes = [p.hash for p in sorted(self.policies, key=lambda x: x.rule_id)]
        combined = "".join(policy_hashes)
        return hashlib.sha256(combined.encode()).hexdigest()

    def _write_audit_log(self, result: PolicyCompilationResult):
        """Write audit log."""
        self.audit_log_path.parent.mkdir(parents=True, exist_ok=True)

        # Read existing log
        if self.audit_log_path.exists():
            with open(self.audit_log_path, 'r') as f:
                audit_log = json.load(f)
        else:
            audit_log = {
                "log_version": "1.0.0",
                "description": "Policy compilation and activation audit log",
                "compilations": []
            }

        # Add new compilation
        audit_log["compilations"].append(asdict(result))
        audit_log["last_updated"] = result.timestamp

        # Write log
        with open(self.audit_log_path, 'w') as f:
            json.dump(audit_log, f, indent=2)

        print(f"Audit log updated: {self.audit_log_path}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="SSID Policy Compiler - Generate OPA/Rego policies from compliance mappings"
    )

    parser.add_argument(
        '--compile-all',
        action='store_true',
        help='Compile all policies from mapping files'
    )

    parser.add_argument(
        '--validate-only',
        action='store_true',
        help='Validate existing Rego files without compiling'
    )

    args = parser.parse_args()

    compiler = PolicyCompiler()

    if args.validate_only:
        compiler._validate_rego_syntax()
    elif args.compile_all:
        result = compiler.compile_all()
        sys.exit(0 if result.status == "success" else 1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
