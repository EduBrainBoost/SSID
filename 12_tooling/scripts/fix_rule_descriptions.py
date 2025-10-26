#!/usr/bin/env python3
"""
Fix Rule Descriptions - Resolve 33 Validation Warnings

This script adds proper descriptions to all rules that have empty descriptions,
using their raw_data fields to generate comprehensive, meaningful descriptions.

Target: Fix all 33 rules with "insufficient description" warnings
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any

# Warning rule IDs
WARNING_RULE_IDS = [
    'SOT-001', 'SOT-002', 'SOT-003', 'SOT-004', 'SOT-005',
    'SOT-018', 'SOT-019', 'SOT-020', 'SOT-021', 'SOT-026',
    'SOT-031', 'SOT-032', 'SOT-037', 'SOT-038', 'SOT-043',
    'SOT-044', 'SOT-049', 'SOT-054', 'SOT-067', 'SOT-068',
    'SOT-069', 'SOT-070', 'SOT-071', 'SOT-072', 'SOT-073',
    'SOT-074', 'SOT-075', 'SOT-076', 'SOT-077', 'SOT-078',
    'SOT-079', 'SOT-080', 'SOT-081'
]


def generate_description(rule: Dict[str, Any]) -> str:
    """Generate a comprehensive description from rule metadata"""

    raw_data = rule.get('raw_data', {})

    # Extract key information
    rule_name = raw_data.get('rule_name', 'Unknown Rule')
    scientific_foundation = raw_data.get('scientific_foundation', {})
    technical_manifestation = raw_data.get('technical_manifestation', {})
    enforcement = raw_data.get('enforcement', {})

    # Build description
    parts = []

    # Start with rule name
    parts.append(f"This rule validates {rule_name}.")

    # Add scientific foundation
    if isinstance(scientific_foundation, dict):
        standard = scientific_foundation.get('standard', '')
        principle = scientific_foundation.get('principle', '')

        if standard and principle:
            parts.append(f"Based on {standard}, this rule enforces the principle: {principle}")
        elif standard:
            parts.append(f"This rule is based on the {standard} standard.")
        elif principle:
            parts.append(f"Principle: {principle}")

    # Add enforcement information
    if isinstance(enforcement, dict):
        method = enforcement.get('method', '')
        timing = enforcement.get('timing', '')

        if method:
            parts.append(f"Enforcement method: {method}.")
        if timing:
            parts.append(f"Applied at: {timing}.")

    # Add technical details
    if isinstance(technical_manifestation, dict):
        validator = technical_manifestation.get('validator', '')
        if validator:
            parts.append(f"Implemented in: {validator}")

    description = " ".join(parts)

    # Ensure minimum length
    if len(description) < 10:
        description = f"Validation rule for {rule_name} - ensures compliance with system requirements and standards."

    return description


def fix_descriptions(registry_path: Path, output_path: Path) -> Dict[str, Any]:
    """Fix all missing descriptions in the registry"""

    print(f"Loading registry from: {registry_path}")
    with open(registry_path, 'r', encoding='utf-8') as f:
        registry = json.load(f)

    total_rules = len(registry['rules'])
    print(f"Total rules: {total_rules}")

    fixed_count = 0
    warning_rules_found = 0

    for rule in registry['rules']:
        rule_id = rule.get('rule_id', '')
        description = rule.get('description', '')

        # Check if this is a warning rule
        if rule_id in WARNING_RULE_IDS:
            warning_rules_found += 1

            # Check if description is insufficient
            if not description or len(description) < 10:
                # Generate new description
                new_description = generate_description(rule)
                rule['description'] = new_description

                # Also populate name if missing
                if not rule.get('name') or rule.get('name') == '':
                    raw_data = rule.get('raw_data', {})
                    rule_name = raw_data.get('rule_name', rule_id)
                    rule['name'] = rule_name

                fixed_count += 1
                print(f"[OK] Fixed {rule_id}: {rule['name']}")
                print(f"  Description: {new_description[:100]}...")

    print(f"\n{'='*60}")
    print(f"Warning rules found: {warning_rules_found}/{len(WARNING_RULE_IDS)}")
    print(f"Descriptions fixed: {fixed_count}")
    print(f"{'='*60}")

    # Write updated registry
    print(f"\nWriting updated registry to: {output_path}")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)

    print("[SUCCESS] Registry updated successfully!")

    return {
        'total_rules': total_rules,
        'warning_rules_found': warning_rules_found,
        'fixed_count': fixed_count
    }


def main():
    # Paths
    project_root = Path(__file__).parents[2]
    registry_path = project_root / '16_codex' / 'structure' / 'auto_generated' / 'sot_rules_full.json'
    output_path = registry_path  # Overwrite in place

    if not registry_path.exists():
        print(f"[ERROR] Registry not found at {registry_path}")
        sys.exit(1)

    # Fix descriptions
    results = fix_descriptions(registry_path, output_path)

    # Summary
    if results['fixed_count'] == len(WARNING_RULE_IDS):
        print(f"\n[SUCCESS] All {results['fixed_count']} warnings fixed!")
        return 0
    else:
        print(f"\n[WARNING] Fixed {results['fixed_count']}/{len(WARNING_RULE_IDS)} warnings")
        return 1


if __name__ == '__main__':
    sys.exit(main())
