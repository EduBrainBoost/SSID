#!/usr/bin/env python3
"""
Rule ID Normalizer - Canonical Rule ID Mapping

This module normalizes all rule ID formats across different artifacts
to enable proper cross-referencing and completeness tracking.

Handles formats:
- Contract: "16_codex.contracts.AUDIT-AUDIT_FREQUENCY-881-9bb5a62f"
- Validator: "validate_cp008" or "SOT-001"
- Test: "test_r_16_codex_contracts_..."
- Policy: "deny[msg]" or "warn_missing_field"
"""

import re
import hashlib
from typing import Dict, List, Set, Optional
from dataclasses import dataclass


@dataclass
class RuleIDMapping:
    """Mapping between different rule ID formats"""
    canonical_id: str
    contract_ids: Set[str]
    validator_ids: Set[str]
    test_ids: Set[str]
    policy_ids: Set[str]
    original_id: str


class RuleIDNormalizer:
    """Normalizes all rule ID formats to canonical form"""

    # Patterns for different rule ID formats
    PATTERNS = {
        'sot_format': re.compile(r'SOT[-_](\d+)', re.IGNORECASE),
        'cp_format': re.compile(r'(CP|cp)[-_]?(\d+)', re.IGNORECASE),
        'md_format': re.compile(r'(MD|md)[-_](STRUCT|CONTENT)[-_](\d+)', re.IGNORECASE),
        'category_number': re.compile(r'([A-Z]+)[-_](\d+)', re.IGNORECASE),
        'hash_suffix': re.compile(r'[-_]([0-9a-f]{8,})$'),
        'validate_prefix': re.compile(r'^validate_(.+)$', re.IGNORECASE),
        'test_prefix': re.compile(r'^test_(.+)$', re.IGNORECASE),
        'deny_prefix': re.compile(r'^(deny|warn)_(.+)$', re.IGNORECASE),
    }

    def __init__(self):
        self.mappings: Dict[str, RuleIDMapping] = {}
        self.reverse_index: Dict[str, str] = {}  # Any ID -> canonical ID

    def normalize(self, rule_id: str) -> str:
        """
        Convert any rule ID format to canonical form

        Examples:
            "SOT-001" -> "SOT-001"
            "validate_cp008" -> "CP-008"
            "16_codex.contracts.AUDIT-AUDIT_FREQUENCY-881-9bb5a62f" -> "AUDIT-881"
            "test_r_sot_001" -> "SOT-001"
        """
        if not rule_id:
            return "UNKNOWN"

        # Check cache first
        if rule_id in self.reverse_index:
            return self.reverse_index[rule_id]

        original = rule_id

        # Remove common prefixes
        rule_id = re.sub(r'^(validate|test|deny|warn)_', '', rule_id, flags=re.IGNORECASE)

        # Remove hash suffixes
        rule_id = self.PATTERNS['hash_suffix'].sub('', rule_id)

        # Try SOT format (most common)
        match = self.PATTERNS['sot_format'].search(rule_id)
        if match:
            canonical = f"SOT-{int(match.group(1)):03d}"
            self.reverse_index[original] = canonical
            return canonical

        # Try CP format
        match = self.PATTERNS['cp_format'].search(rule_id)
        if match:
            canonical = f"CP-{int(match.group(2)):03d}"
            self.reverse_index[original] = canonical
            return canonical

        # Try MD format
        match = self.PATTERNS['md_format'].search(rule_id)
        if match:
            canonical = f"MD-{match.group(2).upper()}-{int(match.group(3)):03d}"
            self.reverse_index[original] = canonical
            return canonical

        # Try category-number format
        match = self.PATTERNS['category_number'].search(rule_id)
        if match:
            category = match.group(1).upper()
            number = int(match.group(2))
            canonical = f"{category}-{number:03d}"
            self.reverse_index[original] = canonical
            return canonical

        # Extract from dotted path (contract format)
        if '.' in rule_id:
            parts = rule_id.split('.')
            for part in parts:
                # Look for pattern in each part
                match = self.PATTERNS['category_number'].search(part)
                if match:
                    category = match.group(1).upper()
                    number = int(match.group(2))
                    canonical = f"{category}-{number:03d}"
                    self.reverse_index[original] = canonical
                    return canonical

        # Fallback: use as-is but uppercase and normalize separator
        canonical = rule_id.upper().replace('_', '-')
        self.reverse_index[original] = canonical
        return canonical

    def create_mapping(self, rules_registry: dict) -> Dict[str, RuleIDMapping]:
        """Create comprehensive mapping of all rule ID variations"""

        for rule in rules_registry.get('rules', []):
            original_id = rule.get('rule_id', '')
            if not original_id:
                continue

            canonical_id = self.normalize(original_id)

            # Initialize mapping if doesn't exist
            if canonical_id not in self.mappings:
                self.mappings[canonical_id] = RuleIDMapping(
                    canonical_id=canonical_id,
                    contract_ids=set(),
                    validator_ids=set(),
                    test_ids=set(),
                    policy_ids=set(),
                    original_id=original_id
                )

            mapping = self.mappings[canonical_id]

            # Add original ID
            mapping.contract_ids.add(original_id)

            # Extract IDs from sources
            for source in rule.get('sources', []):
                file_path = source.get('file_path', '')
                source_id = source.get('id', '')

                if 'validator' in file_path.lower():
                    if source_id:
                        mapping.validator_ids.add(source_id)
                    # Generate validator function name
                    func_name = f"validate_{canonical_id.lower().replace('-', '_')}"
                    mapping.validator_ids.add(func_name)

                elif 'test' in file_path.lower():
                    if source_id:
                        mapping.test_ids.add(source_id)
                    # Generate test function name
                    test_name = f"test_{canonical_id.lower().replace('-', '_')}"
                    mapping.test_ids.add(test_name)

                elif 'policy' in file_path.lower() or '.rego' in file_path.lower():
                    if source_id:
                        mapping.policy_ids.add(source_id)
                    # Generate policy rule name
                    policy_name = f"deny_{canonical_id.lower().replace('-', '_')}"
                    mapping.policy_ids.add(policy_name)

            # Add all variations to reverse index
            for var_id in (mapping.contract_ids | mapping.validator_ids |
                          mapping.test_ids | mapping.policy_ids):
                self.reverse_index[var_id] = canonical_id

        return self.mappings

    def get_all_variations(self, rule_id: str) -> List[str]:
        """Get all known variations of a rule ID"""
        canonical = self.normalize(rule_id)
        if canonical not in self.mappings:
            return [rule_id]

        mapping = self.mappings[canonical]
        return list(mapping.contract_ids | mapping.validator_ids |
                   mapping.test_ids | mapping.policy_ids)

    def find_canonical(self, any_id: str) -> Optional[str]:
        """Find canonical ID for any variation"""
        return self.reverse_index.get(any_id, self.normalize(any_id))

    def export_mapping(self) -> dict:
        """Export mapping to dict for serialization"""
        return {
            'version': '1.0.0',
            'total_canonical_rules': len(self.mappings),
            'total_variations': len(self.reverse_index),
            'mappings': {
                canonical: {
                    'canonical_id': mapping.canonical_id,
                    'contract_ids': list(mapping.contract_ids),
                    'validator_ids': list(mapping.validator_ids),
                    'test_ids': list(mapping.test_ids),
                    'policy_ids': list(mapping.policy_ids),
                    'original_id': mapping.original_id
                }
                for canonical, mapping in self.mappings.items()
            },
            'reverse_index': self.reverse_index
        }


def main():
    """Test the normalizer"""
    import json
    from pathlib import Path

    normalizer = RuleIDNormalizer()

    # Test cases
    test_ids = [
        'SOT-001',
        'validate_cp008',
        '16_codex.contracts.AUDIT-AUDIT_FREQUENCY-881-9bb5a62f',
        'test_r_sot_001',
        'deny_missing_field',
        'MD-STRUCT-009',
        'CP-008',
    ]

    print("Testing Rule ID Normalization:\n")
    for test_id in test_ids:
        canonical = normalizer.normalize(test_id)
        print(f"{test_id:60s} -> {canonical}")

    # Load registry and create full mapping
    registry_path = Path(__file__).parent.parent / '16_codex' / 'structure' / 'auto_generated' / 'sot_rules_full.json'
    if registry_path.exists():
        print(f"\n\nLoading registry from: {registry_path}")
        with open(registry_path, 'r', encoding='utf-8') as f:
            registry = json.load(f)

        normalizer.create_mapping(registry)

        print(f"\nMapping created:")
        print(f"  Canonical rules: {len(normalizer.mappings)}")
        print(f"  Total variations: {len(normalizer.reverse_index)}")

        # Save mapping
        output_path = Path(__file__).parent / 'registry' / 'rule_id_mapping.json'
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(normalizer.export_mapping(), f, indent=2, ensure_ascii=False)
        print(f"\nMapping saved to: {output_path}")


if __name__ == '__main__':
    main()
