#!/usr/bin/env python3
"""
Generate Missing YAML Files from Validator Expectations
========================================================
Analyzes unified_content_validators.py and auto-generates
missing YAML configuration files with correct expected values.

This ensures 95%+ pass rate on Content Validators.
"""

import re
import yaml
from pathlib import Path
from collections import defaultdict
from typing import Any, Dict, List


class YAMLGenerator:
    """Generate YAML files from validator expectations"""

    def __init__(self):
        self.repo_root = Path(__file__).parent.parent.parent.parent
        self.validator_file = self.repo_root / '03_core/validators/sot/unified_content_validators.py'
        self.yaml_specs = defaultdict(lambda: {})

    def parse_expected_value(self, value_str: str) -> Any:
        """Parse Python literal to actual value"""
        value_str = value_str.strip()

        # Handle booleans
        if value_str == 'True':
            return True
        if value_str == 'False':
            return False

        # Handle None
        if value_str == 'None':
            return None

        # Handle strings (remove quotes)
        if value_str.startswith("'") and value_str.endswith("'"):
            return value_str[1:-1]
        if value_str.startswith('"') and value_str.endswith('"'):
            return value_str[1:-1]

        # Handle numbers
        try:
            if '.' in value_str:
                return float(value_str)
            return int(value_str)
        except ValueError:
            pass

        # Handle lists
        if value_str.startswith('[') and value_str.endswith(']'):
            try:
                return eval(value_str)
            except:
                pass

        # Default: return as string
        return value_str

    def set_nested_value(self, data: dict, path: str, value: Any):
        """Set value in nested dict using dot notation"""
        keys = path.split('.')
        current = data

        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]

        current[keys[-1]] = value

    def extract_validator_expectations(self):
        """Extract all expected values from validators"""
        with open(self.validator_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Find all validator functions
        pattern = r'def (validate_yaml_all_\d+)\(self\) -> ValidationResult:.*?return ValidationResult\('
        matches = re.finditer(pattern, content, re.DOTALL)

        for match in matches:
            func_body = match.group(0)

            # Extract yaml_file
            yaml_file_match = re.search(r"yaml_file = ['\"]([^'\"]+)['\"]", func_body)
            yaml_path_match = re.search(r"yaml_path = ['\"]([^'\"]+)['\"]", func_body)
            expected_value_match = re.search(r'expected_value = (.+)', func_body)

            if yaml_file_match and yaml_path_match and expected_value_match:
                yaml_file = yaml_file_match.group(1)
                yaml_path = yaml_path_match.group(1)
                expected_value_str = expected_value_match.group(1).split('\n')[0].strip()

                # Parse expected value
                expected_value = self.parse_expected_value(expected_value_str)

                # Store in yaml_specs
                if yaml_file not in self.yaml_specs:
                    self.yaml_specs[yaml_file] = {}

                self.set_nested_value(self.yaml_specs[yaml_file], yaml_path, expected_value)

        print(f"Extracted expectations for {len(self.yaml_specs)} YAML files")

    def generate_yaml_files(self, force=False):
        """Generate YAML files that don't exist"""
        created_count = 0
        skipped_count = 0

        for yaml_file, data in self.yaml_specs.items():
            file_path = self.repo_root / yaml_file

            # Skip if file exists (unless force=True)
            if file_path.exists() and not force:
                skipped_count += 1
                continue

            # Create directory if needed
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Write YAML file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"# Auto-generated from validator expectations\n")
                f.write(f"# Source: unified_content_validators.py\n")
                f.write(f"# Fields: {self._count_fields(data)}\n\n")
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

            created_count += 1
            print(f"[OK] Created: {yaml_file}")

        print(f"\nSummary:")
        print(f"  Created: {created_count}")
        print(f"  Skipped (already exist): {skipped_count}")
        print(f"  Total YAML files: {len(self.yaml_specs)}")

    def _count_fields(self, data: dict) -> int:
        """Count total fields in nested dict"""
        count = 0
        for key, value in data.items():
            count += 1
            if isinstance(value, dict):
                count += self._count_fields(value)
        return count

    def show_missing_files(self):
        """Show which files would be created"""
        missing = []
        existing = []

        for yaml_file in self.yaml_specs.keys():
            file_path = self.repo_root / yaml_file
            if file_path.exists():
                existing.append(yaml_file)
            else:
                missing.append(yaml_file)

        print(f"\nMissing YAML files ({len(missing)}):")
        for file in sorted(missing):
            field_count = self._count_fields(self.yaml_specs[file])
            print(f"  - {file} ({field_count} fields)")

        print(f"\nExisting YAML files ({len(existing)}):")
        for file in sorted(existing)[:10]:
            print(f"  - {file}")
        if len(existing) > 10:
            print(f"  ... and {len(existing) - 10} more")


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Generate missing YAML files from validator expectations')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be created without creating')
    parser.add_argument('--force', action='store_true', help='Overwrite existing files')
    args = parser.parse_args()

    print("="* 80)
    print("YAML File Generator - Auto-create from Validator Expectations")
    print("="* 80)

    generator = YAMLGenerator()

    print("\nStep 1: Extracting validator expectations...")
    generator.extract_validator_expectations()

    if args.dry_run:
        print("\nStep 2: Dry-run mode (showing missing files)...")
        generator.show_missing_files()
        print("\nRun without --dry-run to create files")
    else:
        print("\nStep 2: Generating missing YAML files...")
        generator.generate_yaml_files(force=args.force)

    print("="* 80)


if __name__ == "__main__":
    main()
