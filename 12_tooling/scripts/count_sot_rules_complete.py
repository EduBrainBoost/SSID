#!/usr/bin/env python3
"""
Count ALL SoT rules from lines 23-88 of SSID_structure_level3_part3_MAX.md
Every YAML element is a distinct rule requiring 5-pillar implementation.
"""

import re

def count_all_rules_lines_26_88():
    """
    Count rules from lines 26-88:
    - Line 26-32: Header section
    - Line 34-87: Compliance entries
    """

    file_path = "C:/Users/bibel/Documents/Github/SSID/16_codex/structure/SSID_structure_level3_part3_MAX.md"

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Lines 26-32 (index 25-31 in 0-indexed)
    header_section = lines[25:32]

    # Lines 34-87 (index 33-86 in 0-indexed)
    compliance_section = lines[33:87]

    print("=" * 80)
    print("SoT Rule Count - Lines 26-88")
    print("=" * 80)

    # Count header rules (lines 26-32)
    print("\n### HEADER SECTION (Lines 26-32):")
    header_rules = []
    for i, line in enumerate(header_section, start=26):
        line_stripped = line.strip()
        if line_stripped and not line_stripped.startswith('```'):
            print(f"  Line {i}: {line_stripped[:70]}")
            if line_stripped.startswith('#'):
                header_rules.append(f"Rule H{len(header_rules)+1}: YAML_FILE_COMMENT (line {i})")
            elif ':' in line_stripped:
                key = line_stripped.split(':')[0].strip()
                header_rules.append(f"Rule H{len(header_rules)+1}: {key} (line {i})")

    print(f"\n**Header Rules Count: {len(header_rules)}**")
    for rule in header_rules:
        print(f"  {rule}")

    # Count compliance rules (lines 34-87)
    print("\n### COMPLIANCE SECTION (Lines 34-87):")
    compliance_rules = []
    for i, line in enumerate(compliance_section, start=34):
        line_stripped = line.strip()
        if line_stripped and not line_stripped.startswith('```'):
            # Count hierarchy markers (e.g., "fatf/travel_rule/")
            if line_stripped.endswith('/') and line_stripped.count('/') >= 1:
                compliance_rules.append(f"Rule C{len(compliance_rules)+1}: HIERARCHY_{line_stripped.rstrip('/')} (line {i})")
                print(f"  Line {i}: [HIERARCHY] {line_stripped}")
            # Count entry markers (e.g., "ivms101_2023/:")
            elif line_stripped.endswith('/:'):
                entry_name = line_stripped.rstrip('/:')
                compliance_rules.append(f"Rule C{len(compliance_rules)+1}: ENTRY_{entry_name} (line {i})")
                print(f"  Line {i}: [ENTRY] {line_stripped}")
            # Count properties (e.g., "name:", "path:", "deprecated:")
            elif ':' in line_stripped:
                key = line_stripped.split(':')[0].strip()
                # Handle special cases like "deprecated_standards:" (section) vs "deprecated:" (property)
                if key == 'deprecated_standards':
                    compliance_rules.append(f"Rule C{len(compliance_rules)+1}: SECTION_{key} (line {i})")
                    print(f"  Line {i}: [SECTION] {line_stripped}")
                elif key == '-':
                    # This is a list item in deprecated_standards
                    compliance_rules.append(f"Rule C{len(compliance_rules)+1}: DEPRECATED_ITEM (line {i})")
                    print(f"  Line {i}: [LIST_ITEM] {line_stripped}")
                else:
                    compliance_rules.append(f"Rule C{len(compliance_rules)+1}: PROPERTY_{key} (line {i})")
                    print(f"  Line {i}: [PROPERTY] {key}")

    print(f"\n**Compliance Rules Count: {len(compliance_rules)}**")

    # Total count
    total = len(header_rules) + len(compliance_rules)

    print("\n" + "=" * 80)
    print(f"**TOTAL RULES: {total}**")
    print(f"  - Header (Lines 26-32): {len(header_rules)} rules")
    print(f"  - Compliance (Lines 34-87): {len(compliance_rules)} rules")
    print("=" * 80)

    # Export to file
    with open("C:/Users/bibel/Documents/Github/SSID/02_audit_logging/reports/SOT_RULE_COUNT_COMPLETE.txt", 'w', encoding='utf-8') as f:
        f.write("SoT Rule Count - Complete Analysis\n")
        f.write("=" * 80 + "\n\n")
        f.write("### HEADER SECTION (Lines 26-32):\n")
        for rule in header_rules:
            f.write(f"  {rule}\n")
        f.write(f"\n**Header Rules: {len(header_rules)}**\n\n")
        f.write("### COMPLIANCE SECTION (Lines 34-87):\n")
        for rule in compliance_rules:
            f.write(f"  {rule}\n")
        f.write(f"\n**Compliance Rules: {len(compliance_rules)}**\n\n")
        f.write(f"**TOTAL: {total} rules**\n")

    return len(header_rules), len(compliance_rules), total

if __name__ == "__main__":
    h, c, total = count_all_rules_lines_26_88()
    print(f"\nReport saved to: 02_audit_logging/reports/SOT_RULE_COUNT_COMPLETE.txt")
