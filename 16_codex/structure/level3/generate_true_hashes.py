#!/usr/bin/env python3
"""
Generate True SoT Contract with Real SHA256 Hashes
====================================================
Extracts SHA256 hashes from ALL 4 holy SoT source files:
1. SSID_structure_level3_part1_MAX.md (1,257 lines)
2. SSID_structure_level3_part2_MAX.md (1,366 lines)
3. SSID_structure_level3_part3_MAX.md (1,210 lines)
4. ssid_master_definition_corrected_v1.1.1.md (1,063 lines)

Total: 4,896 lines = 4,896 SOT-LINE rules

This script generates sot_contract_expanded_TRUE.yaml with correct hashes
from the 4 sacred SoT files in 16_codex/structure/ directory.

Generated: 2025-10-21
Author: Claude Code
Status: PRODUCTION-READY
"""

import hashlib
import yaml
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any


# The 4 Holy SoT Files (SACRED SOURCE - DO NOT MODIFY)
HOLY_SOT_FILES = [
    {
        'filename': 'SSID_structure_level3_part1_MAX.md',
        'lines': 1257,
        'category_prefix': 'PART1',
        'severity': 'INFO'
    },
    {
        'filename': 'SSID_structure_level3_part2_MAX.md',
        'lines': 1366,
        'category_prefix': 'PART2',
        'severity': 'INFO'
    },
    {
        'filename': 'SSID_structure_level3_part3_MAX.md',
        'lines': 1210,
        'category_prefix': 'PART3',
        'severity': 'INFO'
    },
    {
        'filename': 'ssid_master_definition_corrected_v1.1.1.md',
        'lines': 1063,
        'category_prefix': 'MASTER',
        'severity': 'MEDIUM'
    }
]


def compute_sha256(line: str) -> str:
    """
    Compute SHA256 hash of a single line.

    Args:
        line: Line content (with newline preserved)

    Returns:
        64-character hexadecimal SHA256 hash
    """
    return hashlib.sha256(line.encode('utf-8')).hexdigest()


def extract_hashes_from_holy_file(filepath: Path, file_info: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract SHA256 hash for every line in a holy SoT file.

    Args:
        filepath: Path to holy SoT file
        file_info: Metadata about the file

    Returns:
        List of rule definitions with hashes
    """
    rules = []

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        print(f"  Processing {filepath.name}: {len(lines)} lines")

        for line_num, line_content in enumerate(lines, start=1):
            line_hash = compute_sha256(line_content)

            # Categorize line by content
            category = categorize_line(line_content, file_info['category_prefix'])
            severity = determine_severity(line_content, file_info['severity'])

            rule = {
                'source': filepath.name,
                'line_ref': line_num,
                'hash_ref': line_hash,
                'auto_generated': True,
                'category': category,
                'severity': severity,
                'enforcement': 'strict',
                'line_preview': line_content[:80].strip() if len(line_content) > 80 else line_content.strip()
            }

            rules.append(rule)

    except Exception as e:
        print(f"  ERROR processing {filepath.name}: {e}")
        return []

    return rules


def categorize_line(line_content: str, prefix: str) -> str:
    """
    Categorize a line by its content pattern.

    Args:
        line_content: The line text
        prefix: Category prefix (PART1, PART2, PART3, MASTER)

    Returns:
        Category string
    """
    line_lower = line_content.lower().strip()

    # Empty lines
    if not line_lower:
        return f'{prefix}_BLANK'

    # Headers (markdown)
    if line_content.startswith('#'):
        level = len(line_content) - len(line_content.lstrip('#'))
        return f'{prefix}_HEADER_H{level}'

    # YAML frontmatter
    if line_content.strip() in ['---', '...']:
        return f'{prefix}_YAML_MARKER'

    # Code blocks
    if line_content.strip().startswith('```'):
        return f'{prefix}_CODE_BLOCK'

    # Lists
    if line_content.strip().startswith(('-', '*', '+')):
        return f'{prefix}_LIST'

    # Numbered lists
    if line_content.strip() and line_content.strip()[0].isdigit() and '.' in line_content[:10]:
        return f'{prefix}_NUMBERED_LIST'

    # Tables
    if '|' in line_content:
        return f'{prefix}_TABLE'

    # HASH markers (special case for part files)
    if line_content.startswith('HASH_START::') or line_content.startswith('HASH_END::'):
        return f'{prefix}_HASH_MARKER'

    # Default: regular content
    return f'{prefix}_CONTENT'


def determine_severity(line_content: str, default_severity: str) -> str:
    """
    Determine severity based on line content keywords.

    Args:
        line_content: The line text
        default_severity: Default severity from file metadata

    Returns:
        Severity level (CRITICAL, HIGH, MEDIUM, LOW, INFO)
    """
    line_lower = line_content.lower()

    # Critical keywords
    if any(kw in line_lower for kw in ['critical', 'must', 'required', 'mandatory', 'pflicht']):
        return 'CRITICAL'

    # High keywords
    if any(kw in line_lower for kw in ['shall', 'important', 'security', 'compliance', 'gdpr']):
        return 'HIGH'

    # Medium keywords
    if any(kw in line_lower for kw in ['should', 'recommended', 'best practice']):
        return 'MEDIUM'

    # Low keywords
    if any(kw in line_lower for kw in ['may', 'optional', 'consider']):
        return 'LOW'

    # Default
    return default_severity


def generate_sot_contract_true(repo_root: Path, output_file: Path):
    """
    Generate sot_contract_expanded_TRUE.yaml with real hashes from 4 holy files.

    Args:
        repo_root: Path to SSID repository root
        output_file: Path to output YAML file
    """
    print("="*80)
    print("GENERATING TRUE SOT CONTRACT WITH REAL SHA256 HASHES")
    print("="*80)
    print()
    print("Sacred Source Directory: 16_codex/structure/")
    print()

    holy_dir = repo_root / "16_codex" / "structure"

    all_rules = []
    rule_id_counter = 1

    # Process each holy file
    for file_info in HOLY_SOT_FILES:
        filepath = holy_dir / file_info['filename']

        if not filepath.exists():
            print(f"[WARN]  WARNING: Holy file not found: {filepath}")
            continue

        print(f"Processing: {file_info['filename']}")

        # Extract hashes from this file
        file_rules = extract_hashes_from_holy_file(filepath, file_info)

        # Assign rule IDs
        for rule in file_rules:
            rule['rule_id'] = f"SOT-LINE-{rule_id_counter:04d}"
            rule_id_counter += 1

        all_rules.extend(file_rules)
        print(f"  [OK] Extracted {len(file_rules)} rules")
        print()

    # Build contract YAML structure
    contract = {
        'version': '4.0.0',
        'generated': datetime.now().isoformat(),
        'description': 'True SoT Contract with Real SHA256 Hashes from 4 Holy Source Files',
        'total_rules': len(all_rules),
        'source_files': [f['filename'] for f in HOLY_SOT_FILES],
        'sacred_directory': '16_codex/structure/',
        'warning': 'DO NOT MODIFY SACRED SOURCE FILES - THIS CONTRACT IS GENERATED FROM THEM',
        'rules': all_rules
    }

    # Write YAML
    print(f"Writing contract to: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        yaml.dump(contract, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    print()
    print("="*80)
    print("GENERATION COMPLETE")
    print("="*80)
    print()
    print(f"Total Rules Generated: {len(all_rules)}")
    print(f"Output File: {output_file}")
    print(f"File Size: {output_file.stat().st_size / 1024:.1f} KB")
    print()

    # Summary by source file
    print("Rules by Source File:")
    print("-"*80)
    for file_info in HOLY_SOT_FILES:
        file_rules = [r for r in all_rules if r['source'] == file_info['filename']]
        print(f"  {file_info['filename']:50s} {len(file_rules):5d} rules")
    print("-"*80)
    print(f"  TOTAL:{'':<44s} {len(all_rules):5d} rules")
    print()

    # Category breakdown
    categories = {}
    for rule in all_rules:
        cat = rule['category']
        categories[cat] = categories.get(cat, 0) + 1

    print(f"Rules by Category: ({len(categories)} unique categories)")
    print("-"*80)
    for cat in sorted(categories.keys())[:20]:  # Top 20
        print(f"  {cat:40s} {categories[cat]:5d} rules")
    if len(categories) > 20:
        print(f"  ... and {len(categories) - 20} more categories")
    print()

    print("[OK] sot_contract_expanded_TRUE.yaml generated successfully!")
    print()


if __name__ == '__main__':
    # Determine repo root
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent.parent.parent  # ../../../ from level3/

    # Output file
    output_file = script_dir / "sot_contract_expanded_TRUE.yaml"

    # Generate contract
    generate_sot_contract_true(repo_root, output_file)
