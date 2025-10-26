#!/usr/bin/env python3
"""
SUPPLEMENT: Extract inline rules that might have been missed
Focuses on:
- Inline MUST/SHOULD/MAY statements (not in lists)
- deprecation flags in YAML
- Exit code enforcement rules
- KRITISCH/VERBOTEN markers
- mandatory flags
"""

import re
import json
from pathlib import Path
from datetime import datetime

class InlineRuleExtractor:
    def __init__(self, source_dir: Path):
        self.source_dir = source_dir
        self.master_files = [
            "ssid_master_definition_corrected_v1.1.1.md",
            "SSID_structure_level3_part1_MAX.md",
            "SSID_structure_level3_part2_MAX.md",
            "SSID_structure_level3_part3_MAX.md"
        ]
        self.inline_rules = []

    def extract_from_all_files(self):
        print("=" * 70)
        print("EXTRACTING INLINE RULES (SUPPLEMENT)")
        print("=" * 70)
        print()

        for filename in self.master_files:
            file_path = self.source_dir / filename

            if not file_path.exists():
                print(f"[WARNING] File not found: {filename}")
                continue

            print(f"Processing: {filename}")
            content = file_path.read_text(encoding='utf-8')

            rules = self.extract_inline_patterns(content, filename)
            self.inline_rules.extend(rules)

            print(f"  Extracted: {len(rules)} inline rules")
            print()

        return self.inline_rules

    def extract_inline_patterns(self, content: str, source_file: str):
        rules = []
        lines = content.split('\n')

        for i, line in enumerate(lines, 1):
            # Skip if it's a list item (already captured)
            if re.match(r'^\s*[-*+]\s+', line):
                continue

            # Skip if it's a header (already captured)
            if re.match(r'^\s*#{1,6}\s+', line):
                continue

            # Skip if it's in a code block marker
            if line.strip().startswith('```'):
                continue

            # Pattern 1: Inline **MUST** statements
            if re.search(r'\*\*(MUST|SHALL|REQUIRED)\*\*', line, re.IGNORECASE):
                rules.append({
                    'rule_id': f'INLINE-MUST-{i}',
                    'type': 'inline_enforcement',
                    'content': line.strip(),
                    'source_file': source_file,
                    'line_number': i,
                    'priority': 'MUST',
                    'keyword': 'inline_must'
                })

            # Pattern 2: Inline **SHOULD** statements
            elif re.search(r'\*\*(SHOULD|RECOMMENDED)\*\*', line, re.IGNORECASE):
                rules.append({
                    'rule_id': f'INLINE-SHOULD-{i}',
                    'type': 'inline_enforcement',
                    'content': line.strip(),
                    'source_file': source_file,
                    'line_number': i,
                    'priority': 'SHOULD',
                    'keyword': 'inline_should'
                })

            # Pattern 3: KRITISCH markers
            elif re.search(r'\*\*KRITISCH\*\*', line, re.IGNORECASE) or line.strip().startswith('**KRITISCH:**'):
                rules.append({
                    'rule_id': f'INLINE-CRITICAL-{i}',
                    'type': 'inline_critical',
                    'content': line.strip(),
                    'source_file': source_file,
                    'line_number': i,
                    'priority': 'CRITICAL',
                    'keyword': 'kritisch'
                })

            # Pattern 4: VERBOTEN markers
            elif 'VERBOTEN' in line.upper():
                rules.append({
                    'rule_id': f'INLINE-FORBIDDEN-{i}',
                    'type': 'inline_forbidden',
                    'content': line.strip(),
                    'source_file': source_file,
                    'line_number': i,
                    'priority': 'FORBIDDEN',
                    'keyword': 'verboten'
                })

            # Pattern 5: Exit Code 24 enforcement
            elif re.search(r'Exit\s+(Code\s+)?24', line, re.IGNORECASE):
                rules.append({
                    'rule_id': f'INLINE-EXITCODE-{i}',
                    'type': 'inline_exit_code',
                    'content': line.strip(),
                    'source_file': source_file,
                    'line_number': i,
                    'priority': 'ENFORCEMENT',
                    'keyword': 'exit_code_24'
                })

            # Pattern 6: FAIL conditions
            elif re.search(r'\*\*FAIL\*\*.*wenn', line, re.IGNORECASE):
                rules.append({
                    'rule_id': f'INLINE-FAIL-{i}',
                    'type': 'inline_fail_condition',
                    'content': line.strip(),
                    'source_file': source_file,
                    'line_number': i,
                    'priority': 'ENFORCEMENT',
                    'keyword': 'fail_condition'
                })

            # Pattern 7: deprecated: true/false (inline, not in YAML block)
            elif re.search(r'deprecated:\s*(true|false)', line, re.IGNORECASE):
                # Only if not inside a yaml block context
                if not re.match(r'^\s{2,}', line):  # Not indented (not in YAML)
                    rules.append({
                        'rule_id': f'INLINE-DEPRECATED-{i}',
                        'type': 'inline_deprecation',
                        'content': line.strip(),
                        'source_file': source_file,
                        'line_number': i,
                        'priority': 'METADATA',
                        'keyword': 'deprecated_flag'
                    })

            # Pattern 8: mandatory: true/false
            elif re.search(r'mandatory:\s*(true|false)', line, re.IGNORECASE):
                if not re.match(r'^\s{2,}', line):
                    rules.append({
                        'rule_id': f'INLINE-MANDATORY-{i}',
                        'type': 'inline_mandatory',
                        'content': line.strip(),
                        'source_file': source_file,
                        'line_number': i,
                        'priority': 'MANDATORY',
                        'keyword': 'mandatory_flag'
                    })

            # Pattern 9: CI-Guard mentions
            elif 'CI-Guard' in line or 'CI Guard' in line:
                rules.append({
                    'rule_id': f'INLINE-CIGUARD-{i}',
                    'type': 'inline_ci_guard',
                    'content': line.strip(),
                    'source_file': source_file,
                    'line_number': i,
                    'priority': 'ENFORCEMENT',
                    'keyword': 'ci_guard'
                })

        return rules

    def save_results(self, output_file: Path):
        output = {
            'metadata': {
                'extraction_date': datetime.now().isoformat(),
                'total_inline_rules': len(self.inline_rules),
                'source_files': self.master_files,
                'extraction_type': 'INLINE_SUPPLEMENT',
                'version': '1.0.0'
            },
            'inline_rules': self.inline_rules,
            'breakdown_by_type': self.get_breakdown_by_type(),
            'breakdown_by_priority': self.get_breakdown_by_priority(),
            'breakdown_by_keyword': self.get_breakdown_by_keyword(),
            'breakdown_by_file': self.get_breakdown_by_file()
        }

        output_file.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding='utf-8')
        print(f"[OK] Results saved to: {output_file}")

    def get_breakdown_by_type(self):
        breakdown = {}
        for rule in self.inline_rules:
            rule_type = rule['type']
            breakdown[rule_type] = breakdown.get(rule_type, 0) + 1
        return breakdown

    def get_breakdown_by_priority(self):
        breakdown = {}
        for rule in self.inline_rules:
            priority = rule['priority']
            breakdown[priority] = breakdown.get(priority, 0) + 1
        return breakdown

    def get_breakdown_by_keyword(self):
        breakdown = {}
        for rule in self.inline_rules:
            keyword = rule['keyword']
            breakdown[keyword] = breakdown.get(keyword, 0) + 1
        return breakdown

    def get_breakdown_by_file(self):
        breakdown = {}
        for rule in self.inline_rules:
            file_name = rule['source_file']
            breakdown[file_name] = breakdown.get(file_name, 0) + 1
        return breakdown


def main():
    source_dir = Path('16_codex/structure')
    output_file = Path('02_audit_logging/reports/INLINE_RULES_SUPPLEMENT.json')
    output_file.parent.mkdir(parents=True, exist_ok=True)

    extractor = InlineRuleExtractor(source_dir)
    rules = extractor.extract_from_all_files()

    print("=" * 70)
    print("INLINE EXTRACTION COMPLETE")
    print("=" * 70)
    print(f"Total inline rules: {len(rules)}")
    print()

    if len(rules) > 0:
        print("Breakdown by keyword:")
        for keyword, count in sorted(extractor.get_breakdown_by_keyword().items(), key=lambda x: -x[1]):
            print(f"  {keyword}: {count}")
        print()

        print("Breakdown by priority:")
        for priority, count in sorted(extractor.get_breakdown_by_priority().items(), key=lambda x: -x[1]):
            print(f"  {priority}: {count}")
        print()

        extractor.save_results(output_file)
    else:
        print("[INFO] No additional inline rules found.")
        print("[INFO] Original extraction was comprehensive.")


if __name__ == '__main__':
    main()
