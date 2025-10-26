#!/usr/bin/env python3
"""
Prose Rule Extractor - Extract MUSS/SOLL/DARF Prosa Rules from SoT Files
=========================================================================
Extracts natural language requirement statements from the 4 Holy SoT Files.

Patterns captured:
- "MUSS ..." (MUST)
- "SOLL ..." (SHOULD)
- "DARF NICHT ..." (MUST NOT)
- "DARF ..." (MAY)
- "NIEMALS ..." (NEVER)

This complements the YAML-block extraction (966 rules) by capturing
freeform textual requirements embedded in prose.

Target: ~1,500 additional prose rules
"""

import re
from pathlib import Path
from typing import List, Dict, Any
import json
from datetime import datetime


class ProseRuleExtractor:
    """Extract prose requirements from SoT markdown files"""

    def __init__(self):
        self.repo_root = Path(__file__).parent.parent.parent.parent
        self.sot_files = [
            '16_codex/structure/SSID_structure_level3_part1_MAX.md',
            '16_codex/structure/SSID_structure_level3_part2_MAX.md',
            '16_codex/structure/SSID_structure_level3_part3_MAX.md',
            '16_codex/structure/ssid_master_definition_corrected_v1.1.1.md'
        ]

        # Regex patterns for requirement keywords
        self.patterns = [
            # MUSS (MUST)
            (r'(?:^|\s)MUSS\s+(.+?)(?:\.|$)', 'MUST', 'CRITICAL'),

            # SOLL (SHOULD)
            (r'(?:^|\s)SOLL\s+(.+?)(?:\.|$)', 'SHOULD', 'HIGH'),

            # DARF NICHT (MUST NOT)
            (r'(?:^|\s)DARF\s+NICHT\s+(.+?)(?:\.|$)', 'MUST_NOT', 'CRITICAL'),

            # NIEMALS (NEVER)
            (r'(?:^|\s)NIEMALS\s+(.+?)(?:\.|$)', 'NEVER', 'CRITICAL'),

            # DARF (MAY)
            (r'(?:^|\s)DARF\s+(.+?)(?:\.|$)', 'MAY', 'LOW'),

            # English equivalents
            (r'(?:^|\s)MUST\s+(.+?)(?:\.|$)', 'MUST', 'CRITICAL'),
            (r'(?:^|\s)SHOULD\s+(.+?)(?:\.|$)', 'SHOULD', 'HIGH'),
            (r'(?:^|\s)MUST\s+NOT\s+(.+?)(?:\.|$)', 'MUST_NOT', 'CRITICAL'),
            (r'(?:^|\s)SHALL\s+(.+?)(?:\.|$)', 'SHALL', 'CRITICAL'),
            (r'(?:^|\s)SHALL\s+NOT\s+(.+?)(?:\.|$)', 'SHALL_NOT', 'CRITICAL'),
            (r'(?:^|\s)MAY\s+(.+?)(?:\.|$)', 'MAY', 'LOW'),
        ]

    def extract_from_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Extract prose rules from a single markdown file"""
        full_path = self.repo_root / file_path

        if not full_path.exists():
            print(f"WARNING: File not found: {file_path}")
            return []

        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()

        rules = []
        lines = content.split('\n')

        for line_num, line in enumerate(lines, 1):
            # Skip YAML code blocks
            if line.strip().startswith('```'):
                continue

            # Skip markdown headers
            if line.strip().startswith('#'):
                continue

            # Skip empty lines
            if not line.strip():
                continue

            # Check each pattern
            for pattern, rule_type, severity in self.patterns:
                matches = re.finditer(pattern, line, re.IGNORECASE)

                for match in matches:
                    requirement_text = match.group(1).strip()

                    # Skip very short matches (likely false positives)
                    if len(requirement_text) < 10:
                        continue

                    # Skip matches that are just metadata
                    if any(skip in requirement_text.lower() for skip in ['version', 'date', 'author', 'generated']):
                        continue

                    rule = {
                        'rule_type': rule_type,
                        'severity': severity,
                        'requirement': requirement_text,
                        'source_file': file_path,
                        'line_number': line_num,
                        'context': line.strip(),
                        'category': 'PROSE_REQUIREMENT'
                    }

                    rules.append(rule)

        return rules

    def extract_all(self) -> Dict[str, Any]:
        """Extract prose rules from all 4 SoT files"""
        all_rules = []
        file_stats = {}

        for sot_file in self.sot_files:
            print(f"\nProcessing: {sot_file}")
            rules = self.extract_from_file(sot_file)

            file_name = Path(sot_file).name
            file_stats[file_name] = len(rules)

            # Add file-specific rule IDs
            for i, rule in enumerate(rules, 1):
                rule['rule_id'] = f"PROSE-{file_name.replace('.md', '').upper()}-{i:04d}"
                all_rules.append(rule)

            print(f"  Extracted: {len(rules)} prose rules")

        return {
            'total_rules': len(all_rules),
            'extraction_date': datetime.now().isoformat(),
            'source_files': self.sot_files,
            'file_breakdown': file_stats,
            'rules': all_rules
        }

    def generate_report(self, data: Dict[str, Any], output_file: str):
        """Generate markdown report of extracted prose rules"""
        report_path = self.repo_root / output_file

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# Prose Rule Extraction Report\n\n")
            f.write(f"**Generated:** {data['extraction_date']}\n\n")
            f.write(f"**Total Rules:** {data['total_rules']}\n\n")

            f.write("## Breakdown by Source File\n\n")
            f.write("| File | Rules Extracted |\n")
            f.write("|------|----------------|\n")
            for file, count in data['file_breakdown'].items():
                f.write(f"| {file} | {count} |\n")

            f.write("\n## Rule Type Distribution\n\n")
            type_counts = {}
            severity_counts = {}

            for rule in data['rules']:
                rule_type = rule['rule_type']
                severity = rule['severity']
                type_counts[rule_type] = type_counts.get(rule_type, 0) + 1
                severity_counts[severity] = severity_counts.get(severity, 0) + 1

            f.write("### By Type\n\n")
            for rule_type, count in sorted(type_counts.items(), key=lambda x: -x[1]):
                f.write(f"- **{rule_type}**: {count} rules\n")

            f.write("\n### By Severity\n\n")
            for severity, count in sorted(severity_counts.items(), key=lambda x: -x[1]):
                f.write(f"- **{severity}**: {count} rules\n")

            f.write("\n## Sample Rules (First 20)\n\n")
            for rule in data['rules'][:20]:
                f.write(f"### {rule['rule_id']}\n\n")
                f.write(f"- **Type:** {rule['rule_type']}\n")
                f.write(f"- **Severity:** {rule['severity']}\n")
                f.write(f"- **Requirement:** {rule['requirement']}\n")
                f.write(f"- **Source:** {rule['source_file']}:{rule['line_number']}\n")
                f.write(f"- **Context:** `{rule['context']}`\n\n")

        print(f"\nReport generated: {output_file}")


def main():
    print("="* 80)
    print("Prose Rule Extractor - MUSS/SOLL/DARF Requirements")
    print("="* 80)

    extractor = ProseRuleExtractor()

    # Extract all prose rules
    data = extractor.extract_all()

    # Save JSON
    json_output = '16_codex/structure/level3/prose_rules_all_4_files.json'
    json_path = extractor.repo_root / json_output
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"\nJSON saved: {json_output}")

    # Generate markdown report
    md_output = '05_documentation/reports/validator_integration/PROSE_RULES_EXTRACTION_REPORT.md'
    extractor.generate_report(data, md_output)

    print("="* 80)
    print(f"TOTAL PROSE RULES EXTRACTED: {data['total_rules']}")
    print("="* 80)


if __name__ == "__main__":
    main()
