#!/usr/bin/env python3
"""
YAML Rule Definitions Generator v1.0
=====================================
Automatisch generiert sot_contract.yaml Definitionen aus sot_validator_core.py

Extrahiert aus Python Validator:
- Rule ID (z.B. MD-STRUCT-009)
- Description (aus Docstring)
- Severity (aus ValidationResult)
- Category
- Validation Logic
- Dependencies

Generiert YAML im korrekten Format für sot_contract.yaml Integration.

Usage:
    python generate_yaml_from_validator.py --validator path/to/sot_validator_core.py
"""

import argparse
import ast
import re
import sys
import yaml
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Dict, List, Optional, Set
from datetime import datetime


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class RuleDefinition:
    """Repräsentiert eine vollständige Regel-Definition."""
    id: str
    description: str
    severity: str
    category: str
    implementation_status: str = "implemented"
    validation: Dict = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    test_coverage: bool = True
    opa_policy: str = ""
    source_function: str = ""
    docstring: str = ""


# ============================================================================
# AST-BASED VALIDATOR PARSER
# ============================================================================

class ValidatorParser:
    """Parses Python validator using AST to extract rule definitions."""

    def __init__(self, validator_path: Path):
        self.validator_path = validator_path
        with open(validator_path, 'r', encoding='utf-8') as f:
            self.source = f.read()
        self.tree = ast.parse(self.source)

    def extract_all_rules(self) -> List[RuleDefinition]:
        """Extrahiert alle Regel-Definitionen aus dem Validator."""
        rules = []

        # Find SoTValidator class
        for node in ast.walk(self.tree):
            if isinstance(node, ast.ClassDef) and node.name == "SoTValidator":
                # Extract all validate_* methods
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name.startswith("validate_"):
                        rule = self._parse_validation_function(item)
                        if rule:
                            rules.append(rule)

        return rules

    def _parse_validation_function(self, func_node: ast.FunctionDef) -> Optional[RuleDefinition]:
        """Parses a single validation function."""
        func_name = func_node.name

        # Extract rule ID from function name
        # validate_ar001 -> AR001
        # validate_md_struct_009 -> MD-STRUCT-009
        rule_id = self._extract_rule_id(func_name)
        if not rule_id:
            return None

        # Extract docstring
        docstring = ast.get_docstring(func_node) or ""
        description = self._extract_description(docstring)

        # Extract severity from return statement
        severity = self._extract_severity(func_node)

        # Extract category
        category = self._determine_category(rule_id)

        # Extract validation logic
        validation = self._extract_validation_logic(func_node, docstring)

        # Extract dependencies
        dependencies = self._extract_dependencies(func_node)

        # Generate OPA policy name
        opa_policy = f"sot.rules.{rule_id.lower().replace('-', '_')}"

        return RuleDefinition(
            id=rule_id,
            description=description,
            severity=severity,
            category=category,
            validation=validation,
            dependencies=dependencies,
            opa_policy=opa_policy,
            source_function=func_name,
            docstring=docstring
        )

    def _extract_rule_id(self, func_name: str) -> Optional[str]:
        """Converts function name to rule ID."""
        # validate_ar001 -> AR001
        match = re.match(r'validate_ar(\d{3})', func_name)
        if match:
            return f"AR{match.group(1)}"

        # validate_cp012 -> CP012
        match = re.match(r'validate_cp(\d{3})', func_name)
        if match:
            return f"CP{match.group(1)}"

        # validate_juris_bl_001 -> JURIS_BL_001
        match = re.match(r'validate_juris_bl_(\d{3})', func_name)
        if match:
            return f"JURIS_BL_{match.group(1)}"

        # validate_vg_001 -> VG_001
        match = re.match(r'validate_vg_?(\d{3})', func_name)
        if match:
            return f"VG_{match.group(1)}"

        # validate_sot_v2_0001 -> SOT-V2-0001
        match = re.match(r'validate_sot_v2_(\d{4})', func_name)
        if match:
            return f"SOT-V2-{match.group(1)}"

        # validate_md_struct_009 -> MD-STRUCT-009
        match = re.match(r'validate_md_struct_(\d+)', func_name)
        if match:
            return f"MD-STRUCT-{match.group(1)}"

        # validate_md_chart_024 -> MD-CHART-024
        match = re.match(r'validate_md_chart_(\d+)', func_name)
        if match:
            return f"MD-CHART-{match.group(1)}"

        # validate_md_manifest_004 -> MD-MANIFEST-004
        match = re.match(r'validate_md_manifest_(\d+)', func_name)
        if match:
            return f"MD-MANIFEST-{match.group(1)}"

        # validate_md_policy_009 -> MD-POLICY-009
        match = re.match(r'validate_md_policy_(\d+)', func_name)
        if match:
            return f"MD-POLICY-{match.group(1)}"

        # validate_md_princ_007 -> MD-PRINC-007
        match = re.match(r'validate_md_princ_(\d+)', func_name)
        if match:
            return f"MD-PRINC-{match.group(1)}"

        # validate_md_gov_005 -> MD-GOV-005
        match = re.match(r'validate_md_gov_(\d+)', func_name)
        if match:
            return f"MD-GOV-{match.group(1)}"

        # validate_md_ext_012 -> MD-EXT-012
        match = re.match(r'validate_md_ext_(\d+)', func_name)
        if match:
            return f"MD-EXT-{match.group(1)}"

        # Master rules: validate_cs001 -> CS001
        match = re.match(r'validate_([a-z]+)(\d{3})', func_name)
        if match:
            return f"{match.group(1).upper()}{match.group(2)}"

        return None

    def _extract_description(self, docstring: str) -> str:
        """Extrahiert Description aus Docstring."""
        if not docstring:
            return "No description available"

        # First line of docstring is usually the description
        lines = docstring.strip().split('\n')
        if lines:
            desc = lines[0].strip()
            # Remove rule ID prefix if present (e.g. "AR001: Description" -> "Description")
            desc = re.sub(r'^[A-Z]+-?[A-Z]*-?\d+:\s*', '', desc)
            return desc

        return "No description available"

    def _extract_severity(self, func_node: ast.FunctionDef) -> str:
        """Extrahiert Severity aus ValidationResult."""
        # Look for Severity.CRITICAL, Severity.HIGH, etc. in return statements
        for node in ast.walk(func_node):
            if isinstance(node, ast.Return) and node.value:
                # Look for ValidationResult(..., severity=Severity.XXX, ...)
                if isinstance(node.value, ast.Call):
                    for keyword in node.value.keywords:
                        if keyword.arg == "severity":
                            if isinstance(keyword.value, ast.Attribute):
                                return keyword.value.attr

        # Default to MEDIUM if not found
        return "MEDIUM"

    def _determine_category(self, rule_id: str) -> str:
        """Determines category based on rule ID."""
        if rule_id.startswith("AR"):
            return "ARCHITECTURE"
        elif rule_id.startswith("CP"):
            return "CRITICAL_POLICIES"
        elif rule_id.startswith("JURIS"):
            return "JURISDICTIONS"
        elif rule_id.startswith("VG"):
            return "VERSIONING_GOVERNANCE"
        elif rule_id.startswith("SOT-V2"):
            return "SOT_CONTRACT_V2"
        elif rule_id.startswith("MD-STRUCT"):
            return "MASTER_DEF_STRUCTURE"
        elif rule_id.startswith("MD-CHART"):
            return "MASTER_DEF_CHART"
        elif rule_id.startswith("MD-MANIFEST"):
            return "MASTER_DEF_MANIFEST"
        elif rule_id.startswith("MD-POLICY"):
            return "MASTER_DEF_POLICIES"
        elif rule_id.startswith("MD-PRINC"):
            return "MASTER_DEF_PRINCIPLES"
        elif rule_id.startswith("MD-GOV"):
            return "MASTER_DEF_GOVERNANCE"
        elif rule_id.startswith("MD-EXT"):
            return "MASTER_DEF_EXTENSIONS"
        elif rule_id.startswith("CS"):
            return "CHART_STRUCTURE"
        elif rule_id.startswith("MS"):
            return "MANIFEST_STRUCTURE"
        elif rule_id.startswith("KP"):
            return "CORE_PRINCIPLES"
        elif rule_id.startswith("CE"):
            return "CONSOLIDATED_EXTENSIONS"
        elif rule_id.startswith("TS"):
            return "TECHNOLOGY_STANDARDS"
        elif rule_id.startswith("DC"):
            return "DEPLOYMENT_CICD"
        elif rule_id.startswith("MR"):
            return "MATRIX_REGISTRY"
        else:
            return "GENERAL"

    def _extract_validation_logic(self, func_node: ast.FunctionDef, docstring: str) -> Dict:
        """Extracts validation logic summary."""
        validation = {
            "type": "structural",
            "checks": []
        }

        # Extract from docstring
        if "MUSS" in docstring or "must" in docstring.lower():
            validation["checks"].append("mandatory_compliance")

        if "matrix" in docstring.lower() or "24" in docstring or "16" in docstring:
            validation["checks"].append("matrix_alignment")

        if "path" in docstring.lower() or "structure" in docstring.lower():
            validation["checks"].append("structure_validation")

        if "yaml" in docstring.lower() or "chart" in docstring.lower():
            validation["checks"].append("yaml_schema_validation")

        if "field" in docstring.lower():
            validation["checks"].append("field_validation")

        if not validation["checks"]:
            validation["checks"].append("general_validation")

        return validation

    def _extract_dependencies(self, func_node: ast.FunctionDef) -> List[str]:
        """Extracts rule dependencies (other rules referenced)."""
        dependencies = []

        # Look for calls to other validate_* functions
        for node in ast.walk(func_node):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr.startswith("validate_"):
                        # Extract rule ID from function name
                        rule_id = self._extract_rule_id(node.func.attr)
                        if rule_id:
                            dependencies.append(rule_id)

        return list(set(dependencies))  # Remove duplicates


# ============================================================================
# YAML GENERATOR
# ============================================================================

class YamlGenerator:
    """Generates YAML contract from rule definitions."""

    def __init__(self, rules: List[RuleDefinition]):
        self.rules = rules

    def generate_yaml_structure(self) -> Dict:
        """Generates complete YAML structure."""
        # Group rules by category
        rules_by_category = self._group_by_category()

        yaml_structure = {
            "metadata": {
                "version": "5.2.0",
                "generated": datetime.now().isoformat(),
                "total_rules": len(self.rules),
                "matrix_alignment": "24x16 (24 Root-Ordner x 16 Shards = 384 Rules)",
                "source": "AUTO-GENERATED from sot_validator_core.py",
                "generator_version": "1.0.0"
            },
            "rule_categories": self._generate_category_summary(),
            "rules": []
        }

        # Add all rules sorted by ID
        sorted_rules = sorted(self.rules, key=lambda r: r.id)
        for rule in sorted_rules:
            yaml_structure["rules"].append(self._rule_to_dict(rule))

        return yaml_structure

    def _group_by_category(self) -> Dict[str, List[RuleDefinition]]:
        """Groups rules by category."""
        grouped = {}
        for rule in self.rules:
            if rule.category not in grouped:
                grouped[rule.category] = []
            grouped[rule.category].append(rule)
        return grouped

    def _generate_category_summary(self) -> List[Dict]:
        """Generates category summary."""
        grouped = self._group_by_category()
        summary = []

        for category, rules in sorted(grouped.items()):
            summary.append({
                "category": category,
                "total_rules": len(rules),
                "severity_breakdown": self._severity_breakdown(rules)
            })

        return summary

    def _severity_breakdown(self, rules: List[RuleDefinition]) -> Dict[str, int]:
        """Calculates severity breakdown."""
        breakdown = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
        for rule in rules:
            if rule.severity in breakdown:
                breakdown[rule.severity] += 1
        return breakdown

    def _rule_to_dict(self, rule: RuleDefinition) -> Dict:
        """Converts RuleDefinition to dict for YAML."""
        rule_dict = {
            "rule_id": rule.id,
            "description": rule.description,
            "severity": rule.severity,
            "category": rule.category,
            "implementation_status": rule.implementation_status,
            "validation": rule.validation,
            "test_coverage": rule.test_coverage,
            "opa_policy": rule.opa_policy
        }

        if rule.dependencies:
            rule_dict["dependencies"] = rule.dependencies

        # Add metadata
        rule_dict["metadata"] = {
            "source_function": rule.source_function,
            "auto_generated": True
        }

        return rule_dict

    def save_to_file(self, output_path: Path):
        """Saves YAML to file."""
        yaml_structure = self.generate_yaml_structure()

        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(
                yaml_structure,
                f,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False,
                indent=2
            )

        print(f"[+] YAML contract saved: {output_path}")
        print(f"[+] Total rules: {len(self.rules)}")
        print(f"[+] Categories: {len(set(r.category for r in self.rules))}")


# ============================================================================
# INTEGRATION WITH EXISTING CONTRACT
# ============================================================================

class ContractIntegrator:
    """Integrates new rules into existing sot_contract.yaml."""

    def __init__(self, existing_contract_path: Path, new_rules: List[RuleDefinition]):
        self.existing_contract_path = existing_contract_path
        self.new_rules = new_rules

        # Load existing contract if it exists
        if existing_contract_path.exists():
            with open(existing_contract_path, 'r', encoding='utf-8') as f:
                self.existing_contract = yaml.safe_load(f)
        else:
            self.existing_contract = {"rules": []}

    def merge_rules(self) -> Dict:
        """Merges new rules with existing contract."""
        existing_rule_ids = set()

        if "rules" in self.existing_contract:
            existing_rule_ids = {r["rule_id"] for r in self.existing_contract["rules"]}

        # Add only new rules (avoid duplicates)
        new_rules_to_add = [r for r in self.new_rules if r.id not in existing_rule_ids]

        print(f"\n[*] Existing rules: {len(existing_rule_ids)}")
        print(f"[*] New rules to add: {len(new_rules_to_add)}")

        # Create updated contract
        generator = YamlGenerator(self.new_rules)
        updated_contract = generator.generate_yaml_structure()

        # Merge metadata
        if "metadata" in self.existing_contract:
            # Preserve some existing metadata
            updated_contract["metadata"]["previous_version"] = self.existing_contract["metadata"].get("version", "unknown")

        return updated_contract

    def save_integrated(self, output_path: Path):
        """Saves integrated contract."""
        integrated = self.merge_rules()

        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(
                integrated,
                f,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False,
                indent=2
            )

        print(f"[+] Integrated contract saved: {output_path}")


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Generate YAML contract from Python validator"
    )
    parser.add_argument(
        '--validator',
        type=Path,
        required=True,
        help='Path to sot_validator_core.py'
    )
    parser.add_argument(
        '--output',
        type=Path,
        default=Path('sot_contract_generated.yaml'),
        help='Output YAML file'
    )
    parser.add_argument(
        '--integrate',
        type=Path,
        help='Integrate with existing sot_contract.yaml'
    )

    args = parser.parse_args()

    # Validate input
    if not args.validator.exists():
        print(f"[ERROR] Validator file not found: {args.validator}", file=sys.stderr)
        sys.exit(1)

    print(f"\n[*] Parsing validator: {args.validator}")

    # Parse validator
    parser = ValidatorParser(args.validator)
    rules = parser.extract_all_rules()

    print(f"[+] Extracted {len(rules)} rules")

    # Generate YAML
    if args.integrate and args.integrate.exists():
        print(f"\n[*] Integrating with existing contract: {args.integrate}")
        integrator = ContractIntegrator(args.integrate, rules)
        integrator.save_integrated(args.output)
    else:
        generator = YamlGenerator(rules)
        generator.save_to_file(args.output)

    # Print summary
    print(f"\n{'='*60}")
    print(f"YAML GENERATION COMPLETE")
    print(f"{'='*60}")
    print(f"Total Rules: {len(rules)}")

    # Severity breakdown
    severity_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for rule in rules:
        if rule.severity in severity_counts:
            severity_counts[rule.severity] += 1

    print(f"\nSeverity Breakdown:")
    for severity, count in sorted(severity_counts.items()):
        print(f"  {severity}: {count}")

    print(f"\nOutput: {args.output}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
