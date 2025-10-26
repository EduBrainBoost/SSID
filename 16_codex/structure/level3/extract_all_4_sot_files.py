#!/usr/bin/env python3
"""
Komplette semantische Extraktion aus ALLEN 4 heiligen SoT-Dateien
==================================================================
Input: Die 4 heiligen SoT-Dateien in 16_codex/structure/
Output: Unified JSON mit ~1,500-2,000 semantischen Regeln

Die 4 heiligen Dateien:
1. SSID_structure_level3_part1_MAX.md (1,257 Zeilen)
2. SSID_structure_level3_part2_MAX.md (1,366 Zeilen)
3. SSID_structure_level3_part3_MAX.md (1,210 Zeilen)
4. ssid_master_definition_corrected_v1.1.1.md (1,063 Zeilen)

Total: 4,896 Zeilen → ~1,500-2,000 semantische Regeln
"""

from pathlib import Path
from typing import Dict, List, Any
import yaml
import json
from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass
class SemanticRule:
    """Unified semantic rule from any SoT file"""
    rule_id: str
    source_file: str
    source_line: int
    category: str
    yaml_file: str | None
    yaml_path: str | None
    field_name: str | None
    expected_value: Any
    rule_type: str  # MUST, SHOULD, MAY
    severity: str   # CRITICAL, HIGH, MEDIUM, LOW, INFO
    description: str
    validation_method: str
    evidence_required: str


class UnifiedSemanticExtractor:
    """Extract semantic rules from all 4 holy SoT files"""

    def __init__(self, codex_dir: Path):
        self.codex_dir = codex_dir
        self.rules: List[SemanticRule] = []
        self.rule_counter = 0

        # Define the 4 holy files
        self.holy_files = [
            {
                'filename': 'SSID_structure_level3_part1_MAX.md',
                'prefix': 'PART1',
                'lines': 1257
            },
            {
                'filename': 'SSID_structure_level3_part2_MAX.md',
                'prefix': 'PART2',
                'lines': 1366
            },
            {
                'filename': 'SSID_structure_level3_part3_MAX.md',
                'prefix': 'PART3',
                'lines': 1210
            },
            {
                'filename': 'ssid_master_definition_corrected_v1.1.1.md',
                'prefix': 'MASTER',
                'lines': 1063
            }
        ]

    def extract_all(self) -> List[SemanticRule]:
        """Extract semantic rules from all 4 files"""
        print("="*80)
        print("UNIFIED SEMANTIC EXTRACTION - All 4 Holy SoT Files")
        print("="*80)
        print()

        for file_info in self.holy_files:
            filepath = self.codex_dir / file_info['filename']

            if not filepath.exists():
                print(f"[WARN] File not found: {filepath}")
                continue

            print(f"Processing: {file_info['filename']} ({file_info['lines']} lines)")

            rules_before = len(self.rules)
            self._extract_from_file(filepath, file_info)
            rules_added = len(self.rules) - rules_before

            print(f"  [OK] Extracted {rules_added} semantic rules")
            print()

        return self.rules

    def _extract_from_file(self, filepath: Path, file_info: Dict[str, Any]):
        """Extract rules from a single SoT file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Extract YAML blocks
        yaml_blocks = self._extract_yaml_blocks(lines)

        # Parse each YAML block
        for block_info in yaml_blocks:
            self._parse_yaml_block(block_info, filepath.name)

        # Extract text-based rules
        self._extract_text_rules(lines, filepath.name, file_info['prefix'])

    def _extract_yaml_blocks(self, lines: List[str]) -> List[Dict[str, Any]]:
        """Extract all YAML and JSON code blocks"""
        blocks = []
        in_block = False
        block_type = None  # 'yaml' or 'json'
        current_block = []
        file_path = None
        start_line = 0

        for i, line in enumerate(lines, start=1):
            # Detect file path comment (YAML or JSON)
            if line.strip().startswith('# ') or line.strip().startswith('// '):
                if '.yaml' in line or '.json' in line:
                    file_path = line.strip()[2:].strip() if line.strip().startswith('# ') else line.strip()[3:].strip()

            # Detect YAML code block start
            if line.strip() == '```yaml':
                in_block = True
                block_type = 'yaml'
                start_line = i
                current_block = []
                continue

            # Detect JSON code block start
            if line.strip() == '```json':
                in_block = True
                block_type = 'json'
                start_line = i
                current_block = []
                continue

            # Detect code block end
            if line.strip() == '```' and in_block:
                in_block = False
                try:
                    if block_type == 'yaml':
                        parsed_content = yaml.safe_load('\n'.join(current_block))
                    else:  # json
                        parsed_content = json.loads('\n'.join(current_block))

                    if parsed_content:
                        # Generate default file_path if none specified
                        if not file_path:
                            file_path = f"unnamed_block_line_{start_line}.{block_type}"

                        blocks.append({
                            'start_line': start_line,
                            'end_line': i,
                            'yaml_file': file_path,  # Keep key name for compatibility
                            'content': parsed_content,
                            'raw_lines': current_block,
                            'block_type': block_type
                        })
                except (yaml.YAMLError, json.JSONDecodeError):
                    pass  # Skip invalid blocks
                file_path = None
                block_type = None
                continue

            # Collect block content
            if in_block:
                current_block.append(line)

        return blocks

    def _parse_yaml_block(self, block_info: Dict[str, Any], source_file: str):
        """Parse semantic rules from a YAML block"""
        yaml_file = block_info['yaml_file']
        content = block_info['content']
        start_line = block_info['start_line']
        raw_lines = block_info.get('raw_lines', [])

        if not yaml_file or not content:
            return

        # Recursively extract fields from parsed content
        self._extract_fields_recursive(
            source_file=source_file,
            yaml_file=yaml_file,
            yaml_data=content,
            path_prefix='',
            base_line=start_line
        )

        # ALSO extract every meaningful line from raw YAML as a rule
        # This captures nested paths, comments, and structure that parsing might miss
        for i, line in enumerate(raw_lines):
            stripped = line.strip()

            # Skip empty lines and pure comments
            if not stripped or stripped.startswith('#'):
                continue

            # Skip lines that are just structural (like bare colons or brackets)
            if stripped in [':', '{', '}', '[', ']', '---', '...']:
                continue

            # This is a meaningful YAML line - create a rule
            self.rule_counter += 1

            # Detect if it's a path, key, or value
            is_path = stripped.endswith(('/', ':'))
            is_list_item = stripped.startswith('-')

            category = "YAML_PATH" if is_path else "YAML_LINE"

            rule = SemanticRule(
                rule_id=f"YAML-ALL-{self.rule_counter:04d}",
                source_file=source_file,
                source_line=start_line + i + 1,
                category=category,
                yaml_file=yaml_file,
                yaml_path=None,
                field_name=None,
                expected_value=stripped[:200],
                rule_type="MUST",
                severity=self._determine_severity_from_text(stripped),
                description=f"YAML line: {stripped[:200]}",
                validation_method=f"yaml_line_present('{stripped[:100]}')",
                evidence_required=f"Line {start_line + i + 1} in {source_file}"
            )

            self.rules.append(rule)

    def _extract_fields_recursive(self, source_file: str, yaml_file: str, yaml_data: Any, path_prefix: str, base_line: int):
        """Recursively extract YAML fields"""
        if isinstance(yaml_data, dict):
            for key, value in yaml_data.items():
                current_path = f"{path_prefix}.{key}" if path_prefix else key

                if isinstance(value, (str, int, float, bool)):
                    # Leaf node - create rule
                    self._create_yaml_field_rule(
                        source_file=source_file,
                        yaml_file=yaml_file,
                        yaml_path=current_path,
                        field_name=key,
                        expected_value=value,
                        source_line=base_line
                    )
                elif isinstance(value, list):
                    # List - create rule
                    self._create_yaml_list_rule(
                        source_file=source_file,
                        yaml_file=yaml_file,
                        yaml_path=current_path,
                        field_name=key,
                        expected_list=value,
                        source_line=base_line
                    )
                elif isinstance(value, dict):
                    # Nested dict - recurse
                    self._extract_fields_recursive(
                        source_file=source_file,
                        yaml_file=yaml_file,
                        yaml_data=value,
                        path_prefix=current_path,
                        base_line=base_line
                    )

    def _create_yaml_field_rule(self, source_file: str, yaml_file: str, yaml_path: str, field_name: str, expected_value: Any, source_line: int):
        """Create semantic rule for YAML field"""
        self.rule_counter += 1
        rule_id = f"YAML-ALL-{self.rule_counter:04d}"

        severity = self._determine_severity(field_name, str(expected_value))
        description = f"YAML field '{yaml_path}' must equal '{expected_value}'"
        validation_method = f'yaml_field_equals("{yaml_file}", "{yaml_path}", {repr(expected_value)})'

        rule = SemanticRule(
            rule_id=rule_id,
            source_file=source_file,
            source_line=source_line,
            category="YAML_FIELD",
            yaml_file=yaml_file,
            yaml_path=yaml_path,
            field_name=field_name,
            expected_value=expected_value,
            rule_type="MUST",
            severity=severity,
            description=description,
            validation_method=validation_method,
            evidence_required=f"YAML file content at {yaml_path}"
        )

        self.rules.append(rule)

    def _create_yaml_list_rule(self, source_file: str, yaml_file: str, yaml_path: str, field_name: str, expected_list: List[Any], source_line: int):
        """Create semantic rule for YAML list"""
        self.rule_counter += 1
        rule_id = f"YAML-ALL-{self.rule_counter:04d}"

        severity = self._determine_severity(field_name, str(expected_list))
        description = f"YAML list '{yaml_path}' must contain {len(expected_list)} elements"
        validation_method = f'yaml_list_equals("{yaml_file}", "{yaml_path}", {repr(expected_list)})'

        rule = SemanticRule(
            rule_id=rule_id,
            source_file=source_file,
            source_line=source_line,
            category="YAML_LIST",
            yaml_file=yaml_file,
            yaml_path=yaml_path,
            field_name=field_name,
            expected_value=expected_list,
            rule_type="MUST",
            severity=severity,
            description=description,
            validation_method=validation_method,
            evidence_required=f"YAML list content at {yaml_path}"
        )

        self.rules.append(rule)

    def _extract_text_rules(self, lines: List[str], source_file: str, prefix: str):
        """Extract text-based rules from Markdown prose, lists, tables"""
        import re

        current_section = ""
        in_code_block = False

        for i, line in enumerate(lines, start=1):
            stripped = line.strip()

            # Track code block boundaries (but don't skip - we need to continue parsing below)
            if stripped.startswith('```'):
                in_code_block = not in_code_block
                continue

            # Skip empty lines
            if not stripped:
                continue

            # Track sections (headers)
            if stripped.startswith('#'):
                current_section = stripped.lstrip('#').strip()
                continue

            # Extract rules from various patterns:

            # Pattern 1: Explicit rule statements (e.g., "Zeile 20: 1 Regel (description)")
            rule_match = re.search(r'(\d+)\s+Regel(?:n)?\s*\(([^)]+)\)', stripped)
            if rule_match:
                count = int(rule_match.group(1))
                description = rule_match.group(2)

                for j in range(count):
                    self.rule_counter += 1
                    rule = SemanticRule(
                        rule_id=f"TEXT-{prefix}-{self.rule_counter:04d}",
                        source_file=source_file,
                        source_line=i,
                        category="TEXT_RULE",
                        yaml_file=None,
                        yaml_path=None,
                        field_name=None,
                        expected_value=description,
                        rule_type="MUST",
                        severity=self._determine_severity_from_text(description),
                        description=f"{description} (from {current_section})",
                        validation_method=f"text_rule({description})",
                        evidence_required=f"Line {i} in {source_file}"
                    )
                    self.rules.append(rule)
                continue

            # Pattern 2: MUST/SHOULD/MAY statements
            if re.search(r'\b(MUST|SHOULD|MAY|CRITICAL|REQUIRED|MANDATORY)\b', stripped, re.IGNORECASE):
                # Skip if already captured in YAML
                if not any(stripped.startswith(p) for p in ['```', '#', '|', '-', '*']):
                    self.rule_counter += 1

                    rule_type = "MUST" if "MUST" in stripped.upper() or "CRITICAL" in stripped.upper() else \
                                "SHOULD" if "SHOULD" in stripped.upper() else "MAY"

                    rule = SemanticRule(
                        rule_id=f"TEXT-{prefix}-{self.rule_counter:04d}",
                        source_file=source_file,
                        source_line=i,
                        category="TEXT_REQUIREMENT",
                        yaml_file=None,
                        yaml_path=None,
                        field_name=None,
                        expected_value=stripped[:100],
                        rule_type=rule_type,
                        severity="CRITICAL" if rule_type == "MUST" else "HIGH" if rule_type == "SHOULD" else "MEDIUM",
                        description=stripped[:200],
                        validation_method=f"text_requirement_check(line_{i})",
                        evidence_required=f"Line {i} in {source_file}"
                    )
                    self.rules.append(rule)
                continue

            # Pattern 3: List items (markdown lists)
            if stripped.startswith(('-', '*', '+')):
                list_content = stripped[1:].strip()

                # Only create rule if it's meaningful (not just navigation)
                if len(list_content) > 10 and not list_content.startswith('['):
                    self.rule_counter += 1
                    rule = SemanticRule(
                        rule_id=f"LIST-{prefix}-{self.rule_counter:04d}",
                        source_file=source_file,
                        source_line=i,
                        category="LIST_ITEM",
                        yaml_file=None,
                        yaml_path=None,
                        field_name=None,
                        expected_value=list_content[:100],
                        rule_type="SHOULD",
                        severity=self._determine_severity_from_text(list_content),
                        description=f"List item: {list_content[:150]}",
                        validation_method=f"list_item_check(line_{i})",
                        evidence_required=f"Line {i} in {source_file}"
                    )
                    self.rules.append(rule)
                continue

            # Pattern 4: Table rows (markdown tables)
            if '|' in stripped and not stripped.startswith('#'):
                # Skip table headers and separators
                if not re.match(r'^\|[\s\-:]+\|', stripped):
                    cells = [c.strip() for c in stripped.split('|') if c.strip()]

                    if len(cells) >= 2:  # At least 2 columns
                        self.rule_counter += 1
                        rule = SemanticRule(
                            rule_id=f"TABLE-{prefix}-{self.rule_counter:04d}",
                            source_file=source_file,
                            source_line=i,
                            category="TABLE_ROW",
                            yaml_file=None,
                            yaml_path=None,
                            field_name=cells[0] if cells else None,
                            expected_value=' | '.join(cells[1:]) if len(cells) > 1 else cells[0],
                            rule_type="SHOULD",
                            severity="MEDIUM",
                            description=f"Table row: {' | '.join(cells[:3])}",
                            validation_method=f"table_row_check(line_{i})",
                            evidence_required=f"Line {i} in {source_file}"
                        )
                        self.rules.append(rule)
                continue

            # Pattern 5: Numbered policy items (e.g., "1. Policy statement", "2. Requirement")
            numbered_match = re.match(r'^(\d+)\.\s+(.+)', stripped)
            if numbered_match and len(numbered_match.group(2)) > 15:
                policy_text = numbered_match.group(2)
                self.rule_counter += 1
                rule = SemanticRule(
                    rule_id=f"POLICY-{prefix}-{self.rule_counter:04d}",
                    source_file=source_file,
                    source_line=i,
                    category="POLICY_ITEM",
                    yaml_file=None,
                    yaml_path=None,
                    field_name=f"policy_{numbered_match.group(1)}",
                    expected_value=policy_text[:100],
                    rule_type="MUST",
                    severity=self._determine_severity_from_text(policy_text),
                    description=f"Policy #{numbered_match.group(1)}: {policy_text[:150]}",
                    validation_method=f"policy_check(line_{i})",
                    evidence_required=f"Line {i} in {source_file}"
                )
                self.rules.append(rule)
                continue

            # Pattern 6: Key-value pairs with colons (e.g., "Retention: 10 years", "Status: CRITICAL")
            colon_match = re.match(r'^([A-Za-z_\s]+):\s+(.+)', stripped)
            if colon_match and len(colon_match.group(2)) > 3 and not in_code_block:
                field_name = colon_match.group(1).strip()
                field_value = colon_match.group(2).strip()

                # Skip common non-rule patterns
                if not any(skip in field_name.lower() for skip in ['note', 'see', 'example', 'reference', 'link']):
                    self.rule_counter += 1
                    rule = SemanticRule(
                        rule_id=f"KV-{prefix}-{self.rule_counter:04d}",
                        source_file=source_file,
                        source_line=i,
                        category="KEY_VALUE",
                        yaml_file=None,
                        yaml_path=None,
                        field_name=field_name,
                        expected_value=field_value[:100],
                        rule_type="SHOULD",
                        severity=self._determine_severity_from_text(f"{field_name} {field_value}"),
                        description=f"{field_name}: {field_value[:150]}",
                        validation_method=f"key_value_check('{field_name}', '{field_value}')",
                        evidence_required=f"Line {i} in {source_file}"
                    )
                    self.rules.append(rule)
                continue

    def _determine_severity_from_text(self, text: str) -> str:
        """Determine severity from text content"""
        text_lower = text.lower()

        critical_keywords = ['critical', 'must', 'required', 'mandatory', 'security', 'legal',
                            'compliance', 'forbidden', 'verboten', 'pflicht']
        high_keywords = ['should', 'important', 'recommended', 'standard']

        if any(kw in text_lower for kw in critical_keywords):
            return "CRITICAL"
        elif any(kw in text_lower for kw in high_keywords):
            return "HIGH"
        else:
            return "MEDIUM"

    def _determine_severity(self, field_name: str, value_str: str) -> str:
        """Determine severity based on keywords"""
        # Handle None or non-string field names
        field_lower = str(field_name).lower() if field_name is not None else ""
        value_lower = str(value_str).lower() if value_str is not None else ""

        critical_keywords = ['security', 'legal', 'compliance', 'admin', 'deprecated',
                            'false', 'true', 'must', 'critical', 'sanctioned', 'blacklist']

        if any(kw in field_lower or kw in value_lower for kw in critical_keywords):
            return "CRITICAL"

        high_keywords = ['version', 'blockchain', 'standard', 'governance', 'token']
        if any(kw in field_lower or kw in value_lower for kw in high_keywords):
            return "HIGH"

        return "MEDIUM"

    def export_to_json(self, output_file: Path):
        """Export all rules to JSON"""
        rules_dict = [asdict(rule) for rule in self.rules]

        # Count by source file
        by_file = {}
        for rule in self.rules:
            by_file[rule.source_file] = by_file.get(rule.source_file, 0) + 1

        output = {
            'total_rules': len(self.rules),
            'extraction_method': 'unified_yaml_parsing',
            'generated': datetime.now().isoformat(),
            'source_files': list(by_file.keys()),
            'rules_by_file': by_file,
            'rules': rules_dict
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        print(f"[OK] JSON export: {output_file}")
        print(f"     Size: {output_file.stat().st_size / 1024:.1f} KB")

    def print_summary(self):
        """Print extraction summary"""
        print("="*80)
        print("EXTRACTION SUMMARY")
        print("="*80)
        print()

        print(f"Total Rules Extracted: {len(self.rules)}")
        print()

        # By source file
        by_file = {}
        for rule in self.rules:
            by_file[rule.source_file] = by_file.get(rule.source_file, 0) + 1

        print("Rules by Source File:")
        print("-"*80)
        for filename, count in sorted(by_file.items()):
            print(f"  {filename:50s} {count:5d} rules")
        print("-"*80)
        print()

        # By category
        by_category = {}
        for rule in self.rules:
            by_category[rule.category] = by_category.get(rule.category, 0) + 1

        print("Rules by Category:")
        print("-"*80)
        for cat, count in sorted(by_category.items()):
            print(f"  {cat:30s} {count:5d} rules")
        print("-"*80)
        print()

        # By severity
        by_severity = {}
        for rule in self.rules:
            by_severity[rule.severity] = by_severity.get(rule.severity, 0) + 1

        print("Rules by Severity:")
        print("-"*80)
        for sev, count in sorted(by_severity.items()):
            print(f"  {sev:15s} {count:5d} rules")
        print("-"*80)
        print()


def main():
    """Main execution"""
    script_dir = Path(__file__).parent
    codex_dir = script_dir.parent

    print("="*80)
    print("UNIFIED SEMANTIC EXTRACTION - All 4 Holy SoT Files")
    print("="*80)
    print()
    print(f"Source Directory: {codex_dir}")
    print()

    # Extract
    extractor = UnifiedSemanticExtractor(codex_dir)
    rules = extractor.extract_all()

    # Summary
    extractor.print_summary()

    # Export
    output_json = script_dir / "all_4_sot_semantic_rules.json"
    extractor.export_to_json(output_json)

    print()
    print("="*80)
    print("[COMPLETE] Unified extraction from all 4 holy files")
    print("="*80)


if __name__ == '__main__':
    main()
