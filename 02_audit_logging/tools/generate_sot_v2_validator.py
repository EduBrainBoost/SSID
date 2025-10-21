#!/usr/bin/env python3
"""
Generate SOT-V2 Python Validator Logic
========================================
Generates specific field validation functions for 189 SOT-V2 rules.

Replaces generic check:
    contract_files = list(self.repo_root.rglob("**/contracts/*.{yaml,yml,json}"))
    passed = len(contract_files) > 0

With specific field validation:
    def validate_sot_v2(self, num: int) -> ValidationResult:
        if num == 1:
            return self._validate_field("business_model", "SOT-V2-0001")
        elif num == 2:
            return self._validate_field("business_model.data_custody", "SOT-V2-0002")
        ...

Usage:
    python generate_sot_v2_validator.py
"""

from pathlib import Path
import yaml
from datetime import datetime


def load_sot_v2_rules(source_file: Path):
    """Load SOT-V2 rules with field paths from source YAML."""
    with open(source_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    rules = {}
    for rule in data.get('rules', []):
        rule_id = rule.get('rule_id', '')
        if rule_id.startswith('SOT-V2-'):
            num = int(rule_id.split('-')[2])
            rules[num] = {
                'rule_id': rule_id,
                'field_path': rule.get('source', {}).get('path', ''),
                'category': rule.get('category', 'GENERAL'),
                'severity': rule.get('severity', 'MEDIUM'),
                'description': rule.get('description', '')
            }

    return rules


def generate_helper_method():
    """Generate helper method for field validation."""
    return '''
    def _validate_field(self, field_path: str, rule_id: str, category: str = "GENERAL") -> ValidationResult:
        """
        Helper method to validate field existence in contract YAML.

        Args:
            field_path: Dot-separated path (e.g., "business_model.data_custody")
            rule_id: Rule ID (e.g., "SOT-V2-0002")
            category: Rule category (GENERAL, COMPLIANCE, etc.)

        Returns:
            ValidationResult with field validation status
        """
        # Locate contract YAML files
        contract_files = list(self.repo_root.rglob("**/contracts/**/*.{yaml,yml}"))

        if not contract_files:
            return ValidationResult(
                rule_id=rule_id,
                passed=False,
                severity=self._get_severity(category),
                message=f"{rule_id}: No contract files found in repository",
                evidence={"error": "No contract files", "field_path": field_path}
            )

        # Use first contract file found (or implement multi-contract logic)
        contract_path = contract_files[0]

        try:
            with open(contract_path, 'r', encoding='utf-8') as f:
                contract = yaml.safe_load(f)
        except Exception as e:
            return ValidationResult(
                rule_id=rule_id,
                passed=False,
                severity=self._get_severity(category),
                message=f"{rule_id}: Failed to load contract YAML: {e}",
                evidence={"error": str(e), "file": str(contract_path)}
            )

        # Navigate to field using dot-separated path
        parts = field_path.split('.')
        current = contract

        for i, part in enumerate(parts):
            if not isinstance(current, dict):
                return ValidationResult(
                    rule_id=rule_id,
                    passed=False,
                    severity=self._get_severity(category),
                    message=f"{rule_id}: Path '{'.'.join(parts[:i])}' is not a dict",
                    evidence={
                        "field_path": field_path,
                        "failed_at": '.'.join(parts[:i]),
                        "type": str(type(current))
                    }
                )

            if part not in current:
                return ValidationResult(
                    rule_id=rule_id,
                    passed=False,
                    severity=self._get_severity(category),
                    message=f"{rule_id}: Missing required field '{field_path}'",
                    evidence={
                        "field_path": field_path,
                        "missing_field": part,
                        "available_fields": list(current.keys()) if isinstance(current, dict) else []
                    }
                )

            current = current[part]

        # Field exists!
        return ValidationResult(
            rule_id=rule_id,
            passed=True,
            severity=self._get_severity(category),
            message=f"{rule_id}: Field '{field_path}' exists",
            evidence={
                "field_path": field_path,
                "value_type": str(type(current)),
                "contract_file": str(contract_path)
            }
        )

    def _get_severity(self, category: str) -> Severity:
        """Map category to severity."""
        severity_map = {
            "COMPLIANCE": Severity.HIGH,
            "GOVERNANCE": Severity.HIGH,
            "ECONOMICS": Severity.HIGH,
            "GENERAL": Severity.MEDIUM,
            "METADATA": Severity.INFO,
        }
        return severity_map.get(category, Severity.MEDIUM)
'''


def generate_validate_sot_v2_method(rules: dict):
    """Generate main validate_sot_v2(num) method with specific logic."""

    code = '''
    def validate_sot_v2(self, num: int) -> ValidationResult:
        """
        SOT-V2-0001 to SOT-V2-0189: Contract validation rules.

        Now with SPECIFIC field validation instead of generic file checks!

        Args:
            num: Rule number (1-189)

        Returns:
            ValidationResult with specific field validation
        """
        # Map rule numbers to field paths
        field_map = {
'''

    # Generate field map entries
    for num in sorted(rules.keys()):
        if num in [91, 92, 93, 94]:
            # Skip - these have custom implementations
            continue

        rule = rules[num]
        field_path = rule['field_path']
        category = rule['category']

        if field_path:
            code += f'            {num}: ("{field_path}", "{category}"),\n'
        else:
            code += f'            {num}: ("", "{category}"),  # No field path - needs manual impl\n'

    code += '''        }

        if num in field_map:
            field_path, category = field_map[num]
            if field_path:
                return self._validate_field(field_path, f"SOT-V2-{num:04d}", category)
            else:
                # No field path specified - use generic check for now
                return ValidationResult(
                    rule_id=f"SOT-V2-{num:04d}",
                    passed=False,
                    severity=self._get_severity(category),
                    message=f"SOT-V2-{num:04d}: No field path specified - needs manual implementation",
                    evidence={"category": category, "status": "placeholder"}
                )

        # Unknown rule number
        return ValidationResult(
            rule_id=f"SOT-V2-{num:04d}",
            passed=False,
            severity=Severity.MEDIUM,
            message=f"SOT-V2-{num:04d}: Unknown rule number",
            evidence={"error": "Unknown rule", "num": num}
        )
'''

    return code


def main():
    source_file = Path("16_codex/structure/level3/sot_contract_v2.yaml")
    output_file = Path("02_audit_logging/reports/sot_v2_validator_generated.py")

    if not source_file.exists():
        print(f"[ERROR] Source file not found: {source_file}")
        return 1

    print()
    print("=" * 80)
    print("GENERATE SOT-V2 PYTHON VALIDATOR")
    print("=" * 80)
    print()

    # Load rules
    print("[STEP 1] Loading SOT-V2 rules...")
    rules = load_sot_v2_rules(source_file)
    print(f"[+] Loaded {len(rules)} rules")

    # Count rules with field paths
    with_paths = sum(1 for r in rules.values() if r['field_path'])
    without_paths = len(rules) - with_paths
    print(f"[+] Rules with field paths: {with_paths}")
    print(f"[+] Rules without field paths: {without_paths}")

    # Generate code
    print()
    print("[STEP 2] Generating validator code...")

    code_parts = []

    # Header
    code_parts.append('''"""
Generated SOT-V2 Validator Methods
===================================
Auto-generated from sot_contract_v2.yaml
Date: ''' + datetime.now().isoformat() + '''

Usage:
    Replace validate_sot_v2() method in sot_validator_core.py
    Add _validate_field() helper method
"""

from pathlib import Path
import yaml
from typing import Dict, Any
''')

    # Helper method
    code_parts.append("\n# Helper Method")
    code_parts.append(generate_helper_method())

    # Main method
    code_parts.append("\n# Main Validator Method")
    code_parts.append(generate_validate_sot_v2_method(rules))

    # Write output
    output_content = '\n'.join(code_parts)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(output_content)

    print(f"[+] Generated code saved to: {output_file}")
    print()

    # Statistics
    print("=" * 80)
    print("STATISTICS")
    print("=" * 80)
    print(f"  Total rules:              {len(rules)}")
    print(f"  With field paths:         {with_paths}")
    print(f"  Without field paths:      {without_paths}")
    print(f"  Custom implementations:   4 (SOT-V2-0091 to 0094)")
    print()

    # Category breakdown
    categories = {}
    for rule in rules.values():
        cat = rule['category']
        categories[cat] = categories.get(cat, 0) + 1

    print("Rules by category:")
    for cat, count in sorted(categories.items()):
        print(f"  {cat:20s} {count:3d}")
    print()

    print("[NEXT STEPS]")
    print(f"  1. Review generated code: {output_file}")
    print(f"  2. Copy _validate_field() to sot_validator_core.py")
    print(f"  3. Replace validate_sot_v2() method in sot_validator_core.py")
    print(f"  4. Run validator to test: python -m pytest tests/")
    print()

    return 0


if __name__ == "__main__":
    exit(main())
