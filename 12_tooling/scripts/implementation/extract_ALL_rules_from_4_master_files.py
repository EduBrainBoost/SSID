#!/usr/bin/env python3
"""
ULTIMATE RULE EXTRACTION FROM 4 MASTER SOT FILES
=================================================
Extracts EVERY single rule from:
1. ssid_master_definition_corrected_v1.1.1.md
2. SSID_structure_level3_part1_MAX.md
3. SSID_structure_level3_part2_MAX.md
4. SSID_structure_level3_part3_MAX.md

Extraction methods:
- YAML blocks (code fences with ```yaml)
- Markdown headers (# ## ### etc.)
- List items with policy keywords (MUST, SHOULD, MAY, SHALL, REQUIRED)
- Tables
- Inline policy statements
- Numbered lists
- Checkboxes
- Code blocks (Python, Bash, Rego)
- HASH_START markers
"""

import re
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any


class RuleExtractor:
    """Extract all rules from master SoT files"""

    def __init__(self, source_dir: Path):
        self.source_dir = source_dir
        self.master_files = [
            "ssid_master_definition_corrected_v1.1.1.md",
            "SSID_structure_level3_part1_MAX.md",
            "SSID_structure_level3_part2_MAX.md",
            "SSID_structure_level3_part3_MAX.md"
        ]
        self.all_rules = []

    def extract_from_all_files(self):
        """Extract rules from all 4 master files"""
        print("=" * 70)
        print("EXTRACTING ALL RULES FROM 4 MASTER SOT FILES")
        print("=" * 70)
        print()

        for filename in self.master_files:
            file_path = self.source_dir / filename

            if not file_path.exists():
                print(f"[WARNING] File not found: {filename}")
                continue

            print(f"Processing: {filename}")
            content = file_path.read_text(encoding='utf-8')

            rules = self.extract_all_rule_types(content, filename)
            self.all_rules.extend(rules)

            print(f"  Extracted: {len(rules)} rules")
            print()

        return self.all_rules

    def extract_all_rule_types(self, content: str, source_file: str) -> List[Dict]:
        """Extract ALL types of rules from content"""
        rules = []

        # 1. YAML blocks
        rules.extend(self.extract_yaml_blocks(content, source_file))

        # 2. Markdown headers
        rules.extend(self.extract_headers(content, source_file))

        # 3. List items with policy keywords
        rules.extend(self.extract_policy_lists(content, source_file))

        # 4. Tables
        rules.extend(self.extract_tables(content, source_file))

        # 5. Numbered lists
        rules.extend(self.extract_numbered_lists(content, source_file))

        # 6. Checkboxes
        rules.extend(self.extract_checkboxes(content, source_file))

        # 7. Code blocks (non-YAML)
        rules.extend(self.extract_code_blocks(content, source_file))

        # 8. HASH_START markers
        rules.extend(self.extract_hash_start_markers(content, source_file))

        # 9. Bold/Strong statements with policy keywords
        rules.extend(self.extract_bold_policies(content, source_file))

        return rules

    def extract_yaml_blocks(self, content: str, source_file: str) -> List[Dict]:
        """Extract rules from YAML code blocks"""
        rules = []
        pattern = r'```yaml\n(.*?)\n```'

        for match in re.finditer(pattern, content, re.DOTALL):
            yaml_content = match.group(1)
            line_num = content[:match.start()].count('\n') + 1

            # Each YAML block is a rule container
            rules.append({
                'rule_id': f"YAML-{hashlib.md5(yaml_content.encode()).hexdigest()[:8]}",
                'type': 'yaml_block',
                'content': yaml_content[:200],  # Truncate for readability
                'source_file': source_file,
                'line_number': line_num,
                'priority': 'MUST'
            })

        return rules

    def extract_headers(self, content: str, source_file: str) -> List[Dict]:
        """Extract markdown headers as structural rules"""
        rules = []
        lines = content.split('\n')

        for i, line in enumerate(lines, 1):
            match = re.match(r'^(#{1,6})\s+(.+)$', line)
            if match:
                level = len(match.group(1))
                header_text = match.group(2)

                rules.append({
                    'rule_id': f"HEADER-{i}-{hashlib.md5(line.encode()).hexdigest()[:8]}",
                    'type': 'header',
                    'level': level,
                    'content': header_text,
                    'source_file': source_file,
                    'line_number': i,
                    'priority': 'STRUCTURAL'
                })

        return rules

    def extract_policy_lists(self, content: str, source_file: str) -> List[Dict]:
        """Extract list items containing policy keywords"""
        rules = []
        lines = content.split('\n')

        policy_keywords = ['MUST', 'SHALL', 'SHOULD', 'MAY', 'REQUIRED', 'RECOMMENDED',
                          'OPTIONAL', 'MUSS', 'SOLL', 'KANN', 'DARF']

        for i, line in enumerate(lines, 1):
            # Match list items
            list_match = re.match(r'^\s*[-*+]\s+(.+)$', line)
            if list_match:
                text = list_match.group(1)

                # Check for policy keywords
                if any(kw in text.upper() for kw in policy_keywords):
                    # Determine priority
                    if any(kw in text.upper() for kw in ['MUST', 'SHALL', 'REQUIRED', 'MUSS']):
                        priority = 'MUST'
                    elif any(kw in text.upper() for kw in ['SHOULD', 'RECOMMENDED', 'SOLL']):
                        priority = 'SHOULD'
                    else:
                        priority = 'MAY'

                    rules.append({
                        'rule_id': f"LIST-{i}-{hashlib.md5(line.encode()).hexdigest()[:8]}",
                        'type': 'policy_list_item',
                        'content': text,
                        'source_file': source_file,
                        'line_number': i,
                        'priority': priority
                    })

        return rules

    def extract_tables(self, content: str, source_file: str) -> List[Dict]:
        """Extract table rows as rules"""
        rules = []
        lines = content.split('\n')

        in_table = False
        for i, line in enumerate(lines, 1):
            # Detect table row
            if '|' in line and not line.strip().startswith('#'):
                # Skip separator rows
                if re.match(r'^\s*\|[\s\-:]+\|', line):
                    in_table = True
                    continue

                if in_table or line.count('|') >= 2:
                    cells = [c.strip() for c in line.split('|') if c.strip()]
                    if cells:
                        rules.append({
                            'rule_id': f"TABLE-{i}-{hashlib.md5(line.encode()).hexdigest()[:8]}",
                            'type': 'table_row',
                            'content': ' | '.join(cells),
                            'source_file': source_file,
                            'line_number': i,
                            'priority': 'STRUCTURAL'
                        })
            else:
                in_table = False

        return rules

    def extract_numbered_lists(self, content: str, source_file: str) -> List[Dict]:
        """Extract numbered list items"""
        rules = []
        lines = content.split('\n')

        for i, line in enumerate(lines, 1):
            match = re.match(r'^\s*(\d+)\.\s+(.+)$', line)
            if match:
                number = match.group(1)
                text = match.group(2)

                rules.append({
                    'rule_id': f"NUM-{i}-{hashlib.md5(line.encode()).hexdigest()[:8]}",
                    'type': 'numbered_list',
                    'number': number,
                    'content': text,
                    'source_file': source_file,
                    'line_number': i,
                    'priority': 'STRUCTURAL'
                })

        return rules

    def extract_checkboxes(self, content: str, source_file: str) -> List[Dict]:
        """Extract checkbox items"""
        rules = []
        lines = content.split('\n')

        for i, line in enumerate(lines, 1):
            match = re.match(r'^\s*-\s+\[([ x])\]\s+(.+)$', line, re.IGNORECASE)
            if match:
                checked = match.group(1).lower() == 'x'
                text = match.group(2)

                rules.append({
                    'rule_id': f"CHECK-{i}-{hashlib.md5(line.encode()).hexdigest()[:8]}",
                    'type': 'checkbox',
                    'checked': checked,
                    'content': text,
                    'source_file': source_file,
                    'line_number': i,
                    'priority': 'MUST' if not checked else 'COMPLETED'
                })

        return rules

    def extract_code_blocks(self, content: str, source_file: str) -> List[Dict]:
        """Extract non-YAML code blocks"""
        rules = []
        pattern = r'```(\w+)\n(.*?)\n```'

        for match in re.finditer(pattern, content, re.DOTALL):
            language = match.group(1)
            code_content = match.group(2)
            line_num = content[:match.start()].count('\n') + 1

            # Skip YAML (already extracted)
            if language.lower() == 'yaml':
                continue

            rules.append({
                'rule_id': f"CODE-{language.upper()}-{hashlib.md5(code_content.encode()).hexdigest()[:8]}",
                'type': f'code_block_{language}',
                'content': code_content[:200],
                'source_file': source_file,
                'line_number': line_num,
                'priority': 'IMPLEMENTATION'
            })

        return rules

    def extract_hash_start_markers(self, content: str, source_file: str) -> List[Dict]:
        """Extract HASH_START:: markers"""
        rules = []
        lines = content.split('\n')

        for i, line in enumerate(lines, 1):
            match = re.match(r'^HASH_START::([A-Z])_(.+)', line)
            if match:
                segment_type = match.group(1)
                segment_name = match.group(2)

                rules.append({
                    'rule_id': f"HASH-START-{segment_type}",
                    'type': 'hash_start_marker',
                    'segment_type': segment_type,
                    'segment_name': segment_name,
                    'source_file': source_file,
                    'line_number': i,
                    'priority': 'STRUCTURAL'
                })

        return rules

    def extract_bold_policies(self, content: str, source_file: str) -> List[Dict]:
        """Extract bold/strong statements with policy keywords"""
        rules = []
        lines = content.split('\n')

        policy_keywords = ['MUST', 'SHALL', 'SHOULD', 'MAY', 'REQUIRED']

        for i, line in enumerate(lines, 1):
            # Match **text** or __text__
            bold_matches = re.findall(r'\*\*(.+?)\*\*|__(.+?)__', line)

            for match in bold_matches:
                text = match[0] or match[1]

                if any(kw in text.upper() for kw in policy_keywords):
                    rules.append({
                        'rule_id': f"BOLD-{i}-{hashlib.md5(text.encode()).hexdigest()[:8]}",
                        'type': 'bold_policy',
                        'content': text,
                        'source_file': source_file,
                        'line_number': i,
                        'priority': 'MUST'
                    })

        return rules

    def save_results(self, output_file: Path):
        """Save extracted rules to JSON"""
        output = {
            'metadata': {
                'extraction_date': datetime.now().isoformat(),
                'total_rules': len(self.all_rules),
                'source_files': self.master_files,
                'extraction_version': '4.0.0 ULTIMATE'
            },
            'rules': self.all_rules,
            'breakdown': self.get_breakdown()
        }

        output_file.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding='utf-8')
        print(f"Results saved to: {output_file}")

    def get_breakdown(self) -> Dict[str, Any]:
        """Get breakdown by type, priority, file"""
        breakdown = {
            'by_type': {},
            'by_priority': {},
            'by_file': {}
        }

        for rule in self.all_rules:
            # By type
            rule_type = rule['type']
            breakdown['by_type'][rule_type] = breakdown['by_type'].get(rule_type, 0) + 1

            # By priority
            priority = rule['priority']
            breakdown['by_priority'][priority] = breakdown['by_priority'].get(priority, 0) + 1

            # By file
            file_name = rule['source_file']
            breakdown['by_file'][file_name] = breakdown['by_file'].get(file_name, 0) + 1

        return breakdown


def main():
    source_dir = Path('16_codex/structure')
    output_file = Path('02_audit_logging/reports/COMPLETE_MANUAL_EXTRACTION_4_MASTER_FILES.json')
    output_file.parent.mkdir(parents=True, exist_ok=True)

    extractor = RuleExtractor(source_dir)
    rules = extractor.extract_from_all_files()

    print("=" * 70)
    print("EXTRACTION COMPLETE")
    print("=" * 70)
    print(f"Total rules extracted: {len(rules)}")
    print()

    breakdown = extractor.get_breakdown()

    print("Breakdown by type:")
    for rule_type, count in sorted(breakdown['by_type'].items(), key=lambda x: -x[1]):
        print(f"  {rule_type}: {count}")
    print()

    print("Breakdown by priority:")
    for priority, count in sorted(breakdown['by_priority'].items(), key=lambda x: -x[1]):
        print(f"  {priority}: {count}")
    print()

    print("Breakdown by file:")
    for filename, count in sorted(breakdown['by_file'].items(), key=lambda x: -x[1]):
        print(f"  {filename}: {count}")
    print()

    extractor.save_results(output_file)


if __name__ == '__main__':
    main()
