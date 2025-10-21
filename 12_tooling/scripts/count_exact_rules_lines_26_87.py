#!/usr/bin/env python3
"""
Zähle EXAKT alle Regeln in Zeilen 26-87
Jede nicht-leere Zeile mit Inhalt = 1 Regel
"""

file_path = "C:/Users/bibel/Documents/Github/SSID/16_codex/structure/SSID_structure_level3_part3_MAX.md"

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Zeilen 26-32 (Index 25-31)
print("="*80)
print("ZEILEN 26-32 (Header Section):")
print("="*80)
header_rules = []
for i in range(25, 32):  # Lines 26-32
    line = lines[i].rstrip('\n')
    if line.strip() and not line.strip() == '```yaml':
        header_rules.append((i+1, line))
        print(f"Line {i+1}: {line}")

print(f"\n**Count: {len(header_rules)} rules**\n")

# Zeilen 34-87 (Index 33-86)
print("="*80)
print("ZEILEN 34-87 (Compliance Section):")
print("="*80)
compliance_rules = []
for i in range(33, 87):  # Lines 34-87
    line = lines[i].rstrip('\n')
    if line.strip():  # Not empty
        compliance_rules.append((i+1, line))
        print(f"Line {i+1}: {line}")

print(f"\n**Count: {len(compliance_rules)} rules**\n")

print("="*80)
print(f"TOTAL: {len(header_rules)} + {len(compliance_rules)} = {len(header_rules) + len(compliance_rules)} rules")
print("="*80)
