#!/usr/bin/env python3
"""
Content-Validator Generator - Generiert echte Python-Validators aus semantischen Regeln
========================================================================================
Input: part1_semantic_rules_machine.json (468 Regeln)
Output: part1_content_validators.py (468 Validator-Funktionen)
Datum: 2025-10-21
"""

from pathlib import Path
import json
from typing import List, Dict, Any
from datetime import datetime


class ContentValidatorGenerator:
    """Generate Python validator functions from semantic rules"""

    def __init__(self, rules_file: Path, output_file: Path):
        self.rules_file = rules_file
        self.output_file = output_file
        self.rules: List[Dict[str, Any]] = []

    def load_rules(self):
        """Load semantic rules from JSON"""
        with open(self.rules_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.rules = data['rules']

        print(f"[OK] Loaded {len(self.rules)} semantic rules from {self.rules_file.name}")

    def generate_validators(self):
        """Generate all validator functions"""
        print(f"[INFO] Generating {len(self.rules)} validator functions...")

        with open(self.output_file, 'w', encoding='utf-8') as f:
            # Write file header
            self._write_header(f)

            # Write imports
            self._write_imports(f)

            # Write helper functions
            self._write_helper_functions(f)

            # Write validator class
            self._write_validator_class_start(f)

            # Generate each validator function
            for i, rule in enumerate(self.rules, start=1):
                self._generate_validator_function(f, rule, i)

            # Write validate_all method
            self._write_validate_all_method(f)

            # Close class
            f.write("\n\n")

        print(f"[OK] Generated {self.output_file}")

    def _write_header(self, f):
        """Write file header"""
        f.write('"""\n')
        f.write('Part1 Content Validators - Auto-Generated from Semantic Rules\n')
        f.write('=============================================================\n')
        f.write(f'Total Validators: {len(self.rules)}\n')
        f.write(f'Source: {self.rules_file.name}\n')
        f.write(f'Generated: {datetime.now().isoformat()}\n')
        f.write('Auto-Generated: DO NOT EDIT MANUALLY\n')
        f.write('=============================================================\n')
        f.write('\n')
        f.write('This module contains auto-generated content validators for all\n')
        f.write('semantic rules extracted from SSID_structure_level3_part1_MAX.md.\n')
        f.write('\n')
        f.write('Categories:\n')

        # Count categories
        categories = {}
        for rule in self.rules:
            cat = rule['category']
            categories[cat] = categories.get(cat, 0) + 1

        for cat, count in sorted(categories.items()):
            f.write(f'- {cat}: {count} validators\n')

        f.write('"""\n\n')

    def _write_imports(self, f):
        """Write import statements"""
        f.write('from pathlib import Path\n')
        f.write('from typing import Dict, Any, List, Optional\n')
        f.write('from dataclasses import dataclass\n')
        f.write('from datetime import datetime\n')
        f.write('import yaml\n')
        f.write('import json\n')
        f.write('\n')
        f.write('# Import from sot_validator_core\n')
        f.write('import sys\n')
        f.write('sys.path.insert(0, str(Path(__file__).parent.parent.parent / "03_core" / "validators" / "sot"))\n')
        f.write('from sot_validator_core import ValidationResult, Severity\n')
        f.write('\n\n')

    def _write_helper_functions(self, f):
        """Write helper utility functions"""
        f.write('# ============================================================\n')
        f.write('# HELPER FUNCTIONS FOR YAML VALIDATION\n')
        f.write('# ============================================================\n\n')

        # yaml_field_equals
        f.write('def yaml_field_equals(repo_root: Path, yaml_file: str, yaml_path: str, expected_value: Any) -> tuple[bool, Any]:\n')
        f.write('    """\n')
        f.write('    Check if YAML field equals expected value.\n')
        f.write('    \n')
        f.write('    Args:\n')
        f.write('        repo_root: Repository root path\n')
        f.write('        yaml_file: Relative path to YAML file\n')
        f.write('        yaml_path: Dot-separated path to field (e.g., "version" or "token_definition.purpose")\n')
        f.write('        expected_value: Expected value\n')
        f.write('    \n')
        f.write('    Returns:\n')
        f.write('        (passed: bool, actual_value: Any)\n')
        f.write('    """\n')
        f.write('    file_path = repo_root / yaml_file\n')
        f.write('    \n')
        f.write('    if not file_path.exists():\n')
        f.write('        return (False, None)\n')
        f.write('    \n')
        f.write('    try:\n')
        f.write('        with open(file_path, \'r\', encoding=\'utf-8\') as f:\n')
        f.write('            data = yaml.safe_load(f)\n')
        f.write('        \n')
        f.write('        # Navigate nested path\n')
        f.write('        keys = yaml_path.split(\'.\')\n')
        f.write('        current = data\n')
        f.write('        for key in keys:\n')
        f.write('            if isinstance(current, dict) and key in current:\n')
        f.write('                current = current[key]\n')
        f.write('            else:\n')
        f.write('                return (False, None)\n')
        f.write('        \n')
        f.write('        # Compare values\n')
        f.write('        passed = (current == expected_value)\n')
        f.write('        return (passed, current)\n')
        f.write('        \n')
        f.write('    except Exception as e:\n')
        f.write('        return (False, str(e))\n\n\n')

        # yaml_list_equals
        f.write('def yaml_list_equals(repo_root: Path, yaml_file: str, yaml_path: str, expected_list: List[Any]) -> tuple[bool, Any]:\n')
        f.write('    """\n')
        f.write('    Check if YAML list field equals expected list.\n')
        f.write('    \n')
        f.write('    Args:\n')
        f.write('        repo_root: Repository root path\n')
        f.write('        yaml_file: Relative path to YAML file\n')
        f.write('        yaml_path: Dot-separated path to list field\n')
        f.write('        expected_list: Expected list values\n')
        f.write('    \n')
        f.write('    Returns:\n')
        f.write('        (passed: bool, actual_list: Any)\n')
        f.write('    """\n')
        f.write('    passed, actual = yaml_field_equals(repo_root, yaml_file, yaml_path, expected_list)\n')
        f.write('    return (passed, actual)\n\n\n')

        # file_exists
        f.write('def file_exists(repo_root: Path, file_path: str) -> bool:\n')
        f.write('    """Check if file exists"""\n')
        f.write('    return (repo_root / file_path).exists()\n\n\n')

        # count_root_directories
        f.write('def count_root_directories(repo_root: Path) -> int:\n')
        f.write('    """Count numbered root directories (01_* through 24_*)"""\n')
        f.write('    count = 0\n')
        f.write('    for item in repo_root.iterdir():\n')
        f.write('        if item.is_dir() and item.name[:3].replace(\'_\', \'\').isdigit():\n')
        f.write('            count += 1\n')
        f.write('    return count\n\n\n')

    def _write_validator_class_start(self, f):
        """Write validator class start"""
        f.write('# ============================================================\n')
        f.write('# PART1 CONTENT VALIDATOR CLASS\n')
        f.write('# ============================================================\n\n')

        f.write('class Part1ContentValidators:\n')
        f.write('    """\n')
        f.write(f'    Part1 Content Validators - {len(self.rules)} auto-generated rules\n')
        f.write('    \n')
        f.write('    Validates semantic content from SSID_structure_level3_part1_MAX.md\n')
        f.write('    """\n\n')

        f.write('    def __init__(self, repo_root: Path):\n')
        f.write('        self.repo_root = Path(repo_root).resolve()\n\n')

    def _generate_validator_function(self, f, rule: Dict[str, Any], index: int):
        """Generate a single validator function"""
        rule_id = rule['rule_id'].replace('-', '_').lower()
        function_name = f"validate_{rule_id}"

        # Function signature
        f.write(f'    def {function_name}(self) -> ValidationResult:\n')

        # Docstring
        f.write(f'        """\n')
        f.write(f'        {rule["rule_id"]}: {rule["description"]}\n')
        f.write(f'        \n')
        f.write(f'        Category: {rule["category"]}\n')
        f.write(f'        Severity: {rule["severity"]}\n')
        f.write(f'        Source Line: {rule["source_line"]}\n')
        f.write(f'        """\n')

        # Function body based on category
        category = rule['category']

        if category == 'YAML_FIELD':
            self._generate_yaml_field_validator(f, rule)
        elif category == 'YAML_LIST':
            self._generate_yaml_list_validator(f, rule)
        elif category == 'STRUCTURE':
            self._generate_structure_validator(f, rule)
        else:
            # Generic fallback
            self._generate_generic_validator(f, rule)

        f.write('\n\n')

    def _generate_yaml_field_validator(self, f, rule: Dict[str, Any]):
        """Generate YAML field validator"""
        yaml_file = rule['yaml_file']
        yaml_path = rule['yaml_path']
        expected_value = rule['expected_value']
        severity = rule['severity']

        f.write(f'        passed, actual = yaml_field_equals(\n')
        f.write(f'            self.repo_root,\n')
        f.write(f'            "{yaml_file}",\n')
        f.write(f'            "{yaml_path}",\n')
        f.write(f'            {repr(expected_value)}\n')
        f.write(f'        )\n')
        f.write(f'        \n')
        f.write(f'        return ValidationResult(\n')
        f.write(f'            rule_id="{rule["rule_id"]}",\n')
        f.write(f'            passed=passed,\n')
        f.write(f'            severity=Severity.{severity},\n')
        f.write(f'            message=("PASS: {yaml_path} = " + str(actual)) if passed else ("FAIL: {yaml_path} expected {repr(expected_value)}, got " + str(actual)),\n')
        f.write(f'            evidence={{\n')
        f.write(f'                "yaml_file": "{yaml_file}",\n')
        f.write(f'                "yaml_path": "{yaml_path}",\n')
        f.write(f'                "expected": {repr(expected_value)},\n')
        f.write(f'                "actual": actual\n')
        f.write(f'            }}\n')
        f.write(f'        )\n')

    def _generate_yaml_list_validator(self, f, rule: Dict[str, Any]):
        """Generate YAML list validator"""
        yaml_file = rule['yaml_file']
        yaml_path = rule['yaml_path']
        expected_list = rule['expected_value']
        severity = rule['severity']

        f.write(f'        passed, actual = yaml_list_equals(\n')
        f.write(f'            self.repo_root,\n')
        f.write(f'            "{yaml_file}",\n')
        f.write(f'            "{yaml_path}",\n')
        f.write(f'            {repr(expected_list)}\n')
        f.write(f'        )\n')
        f.write(f'        \n')
        f.write(f'        return ValidationResult(\n')
        f.write(f'            rule_id="{rule["rule_id"]}",\n')
        f.write(f'            passed=passed,\n')
        f.write(f'            severity=Severity.{severity},\n')
        f.write(f'            message=("PASS: {yaml_path} list matches") if passed else ("FAIL: {yaml_path} expected {len(expected_list)} elements, got " + str(len(actual) if isinstance(actual, list) else 0)),\n')
        f.write(f'            evidence={{\n')
        f.write(f'                "yaml_file": "{yaml_file}",\n')
        f.write(f'                "yaml_path": "{yaml_path}",\n')
        f.write(f'                "expected_count": {len(expected_list)},\n')
        f.write(f'                "actual_count": len(actual) if isinstance(actual, list) else 0,\n')
        f.write(f'                "actual": actual\n')
        f.write(f'            }}\n')
        f.write(f'        )\n')

    def _generate_structure_validator(self, f, rule: Dict[str, Any]):
        """Generate structure validator"""
        field_name = rule['field_name']
        severity = rule['severity']

        if field_name == 'root_count':
            f.write(f'        actual_count = count_root_directories(self.repo_root)\n')
            f.write(f'        passed = (actual_count == 24)\n')
            f.write(f'        \n')
            f.write(f'        return ValidationResult(\n')
            f.write(f'            rule_id="{rule["rule_id"]}",\n')
            f.write(f'            passed=passed,\n')
            f.write(f'            severity=Severity.{severity},\n')
            f.write(f'            message=f"PASS: Found exactly 24 root directories" if passed else f"FAIL: Expected 24 root directories, found {{actual_count}}",\n')
            f.write(f'            evidence={{\n')
            f.write(f'                "expected": 24,\n')
            f.write(f'                "actual": actual_count\n')
            f.write(f'            }}\n')
            f.write(f'        )\n')

        elif 'file' in field_name.lower():
            expected_file = rule['expected_value']
            f.write(f'        passed = file_exists(self.repo_root, "{expected_file}")\n')
            f.write(f'        \n')
            f.write(f'        return ValidationResult(\n')
            f.write(f'            rule_id="{rule["rule_id"]}",\n')
            f.write(f'            passed=passed,\n')
            f.write(f'            severity=Severity.{severity},\n')
            f.write(f'            message=f"PASS: File exists: {expected_file}" if passed else f"FAIL: File not found: {expected_file}",\n')
            f.write(f'            evidence={{\n')
            f.write(f'                "file_path": "{expected_file}",\n')
            f.write(f'                "exists": passed\n')
            f.write(f'            }}\n')
            f.write(f'        )\n')

        else:
            # Generic structure validator
            self._generate_generic_validator(f, rule)

    def _generate_generic_validator(self, f, rule: Dict[str, Any]):
        """Generate generic validator (fallback)"""
        severity = rule['severity']

        f.write(f'        # TODO: Implement validation logic for {rule["rule_id"]}\n')
        f.write(f'        # {rule["description"]}\n')
        f.write(f'        \n')
        f.write(f'        return ValidationResult(\n')
        f.write(f'            rule_id="{rule["rule_id"]}",\n')
        f.write(f'            passed=False,\n')
        f.write(f'            severity=Severity.{severity},\n')
        f.write(f'            message="NOT IMPLEMENTED: {rule["description"]}",\n')
        f.write(f'            evidence={{\n')
        f.write(f'                "validation_method": "{rule["validation_method"]}"\n')
        f.write(f'            }}\n')
        f.write(f'        )\n')

    def _write_validate_all_method(self, f):
        """Write validate_all() method"""
        f.write('    def validate_all(self) -> List[ValidationResult]:\n')
        f.write('        """\n')
        f.write(f'        Validate all {len(self.rules)} Part1 content rules.\n')
        f.write('        \n')
        f.write('        Returns:\n')
        f.write('            List of ValidationResult objects\n')
        f.write('        """\n')
        f.write('        results = []\n\n')

        # Call each validator
        for rule in self.rules:
            rule_id = rule['rule_id'].replace('-', '_').lower()
            f.write(f'        results.append(self.validate_{rule_id}())\n')

        f.write('\n        return results\n')


def main():
    """Main execution"""
    script_dir = Path(__file__).parent

    rules_file = script_dir / "part1_semantic_rules_machine.json"
    output_file = script_dir / "part1_content_validators.py"

    if not rules_file.exists():
        print(f"[ERROR] Rules file not found: {rules_file}")
        print("[INFO] Run parse_part1_semantic.py first to generate rules")
        return

    print("="*80)
    print("CONTENT-VALIDATOR GENERATOR")
    print("="*80)
    print()

    generator = ContentValidatorGenerator(rules_file, output_file)
    generator.load_rules()
    print()

    generator.generate_validators()
    print()

    print("="*80)
    print("[COMPLETE] Validator generation abgeschlossen")
    print("="*80)
    print()
    print(f"Output: {output_file}")
    print(f"Size: {output_file.stat().st_size / 1024:.1f} KB")
    print()


if __name__ == '__main__':
    main()
