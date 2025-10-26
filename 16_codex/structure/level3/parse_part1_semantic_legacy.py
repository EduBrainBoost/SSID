#!/usr/bin/env python3
"""
Maschinelle Extraktion semantischer Regeln aus Part1
======================================================
Quelle: SSID_structure_level3_part1_MAX.md
Methode: Automatische YAML-Parsing + Text-Analyse
Datum: 2025-10-21
"""

from pathlib import Path
from typing import Dict, List, Any, Optional
import yaml
import re
import hashlib
from dataclasses import dataclass, asdict
import json


@dataclass
class SemanticRule:
    """Semantic rule extracted from Part1"""
    rule_id: str
    source_line: int
    category: str
    yaml_file: Optional[str]
    yaml_path: Optional[str]
    field_name: Optional[str]
    expected_value: Any
    rule_type: str  # MUST, SHOULD, MAY, NIEMALS
    severity: str   # CRITICAL, HIGH, MEDIUM, LOW, INFO
    description: str
    validation_method: str
    evidence_required: str


class Part1SemanticParser:
    """Parse semantic rules from Part1 YAML blocks and text"""

    def __init__(self, part1_file: Path):
        self.part1_file = part1_file
        self.rules: List[SemanticRule] = []
        self.rule_counter = 0

    def parse_all(self) -> List[SemanticRule]:
        """Parse all semantic rules from Part1"""
        with open(self.part1_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Extract YAML blocks
        yaml_blocks = self._extract_yaml_blocks(lines)

        # Parse each YAML block
        for block_info in yaml_blocks:
            self._parse_yaml_block(block_info)

        # Extract text-based rules (non-YAML)
        self._extract_text_rules(lines)

        return self.rules

    def _extract_yaml_blocks(self, lines: List[str]) -> List[Dict[str, Any]]:
        """Extract all YAML code blocks with metadata"""
        blocks = []
        in_yaml = False
        current_block = []
        yaml_file_path = None
        start_line = 0

        for i, line in enumerate(lines, start=1):
            # Detect YAML file path comment
            if line.strip().startswith('# ') and '.yaml' in line:
                yaml_file_path = line.strip()[2:].strip()

            # Detect YAML code block start
            if line.strip() == '```yaml':
                in_yaml = True
                start_line = i
                current_block = []
                continue

            # Detect YAML code block end
            if line.strip() == '```' and in_yaml:
                in_yaml = False
                try:
                    parsed_yaml = yaml.safe_load('\n'.join(current_block))
                    if parsed_yaml:
                        blocks.append({
                            'start_line': start_line,
                            'end_line': i,
                            'yaml_file': yaml_file_path,
                            'content': parsed_yaml,
                            'raw_lines': current_block
                        })
                except yaml.YAMLError as e:
                    print(f"[WARN] YAML parse error at line {start_line}: {e}")
                yaml_file_path = None
                continue

            # Collect YAML content
            if in_yaml:
                current_block.append(line)

        return blocks

    def _parse_yaml_block(self, block_info: Dict[str, Any]):
        """Parse semantic rules from a YAML block"""
        yaml_file = block_info['yaml_file']
        content = block_info['content']
        start_line = block_info['start_line']

        if not yaml_file or not content:
            return

        # Recursively extract fields
        self._extract_fields_recursive(
            yaml_file=yaml_file,
            yaml_data=content,
            path_prefix='',
            base_line=start_line
        )

    def _extract_fields_recursive(self, yaml_file: str, yaml_data: Any, path_prefix: str, base_line: int):
        """Recursively extract YAML fields as semantic rules"""
        if isinstance(yaml_data, dict):
            for key, value in yaml_data.items():
                current_path = f"{path_prefix}.{key}" if path_prefix else key

                if isinstance(value, (str, int, float, bool)):
                    # Leaf node - create rule
                    self._create_yaml_field_rule(
                        yaml_file=yaml_file,
                        yaml_path=current_path,
                        field_name=key,
                        expected_value=value,
                        source_line=base_line
                    )
                elif isinstance(value, list):
                    # List - create rule for list validation
                    self._create_yaml_list_rule(
                        yaml_file=yaml_file,
                        yaml_path=current_path,
                        field_name=key,
                        expected_list=value,
                        source_line=base_line
                    )
                elif isinstance(value, dict):
                    # Nested dict - recurse
                    self._extract_fields_recursive(
                        yaml_file=yaml_file,
                        yaml_data=value,
                        path_prefix=current_path,
                        base_line=base_line
                    )

        elif isinstance(yaml_data, list):
            # Handle list items
            for item in yaml_data:
                if isinstance(item, dict):
                    self._extract_fields_recursive(
                        yaml_file=yaml_file,
                        yaml_data=item,
                        path_prefix=path_prefix,
                        base_line=base_line
                    )

    def _create_yaml_field_rule(self, yaml_file: str, yaml_path: str, field_name: str, expected_value: Any, source_line: int):
        """Create semantic rule for YAML field"""
        self.rule_counter += 1
        rule_id = f"YAML-P1-{self.rule_counter:03d}"

        # Determine severity based on keywords
        severity = self._determine_severity(field_name, str(expected_value))

        # Determine rule type
        rule_type = "MUST"  # Default - all YAML fields are MUST

        # Create description
        description = f"YAML field '{yaml_path}' must equal '{expected_value}'"

        # Validation method
        validation_method = f'yaml_field_equals("{yaml_file}", "{yaml_path}", {repr(expected_value)})'

        rule = SemanticRule(
            rule_id=rule_id,
            source_line=source_line,
            category="YAML_FIELD",
            yaml_file=yaml_file,
            yaml_path=yaml_path,
            field_name=field_name,
            expected_value=expected_value,
            rule_type=rule_type,
            severity=severity,
            description=description,
            validation_method=validation_method,
            evidence_required=f"YAML file content at {yaml_path}"
        )

        self.rules.append(rule)

    def _create_yaml_list_rule(self, yaml_file: str, yaml_path: str, field_name: str, expected_list: List[Any], source_line: int):
        """Create semantic rule for YAML list field"""
        self.rule_counter += 1
        rule_id = f"YAML-P1-{self.rule_counter:03d}"

        # Determine severity
        severity = self._determine_severity(field_name, str(expected_list))

        # Create description
        description = f"YAML list '{yaml_path}' must contain {len(expected_list)} elements: {expected_list}"

        # Validation method
        validation_method = f'yaml_list_equals("{yaml_file}", "{yaml_path}", {repr(expected_list)})'

        rule = SemanticRule(
            rule_id=rule_id,
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

    def _extract_text_rules(self, lines: List[str]):
        """Extract semantic rules from non-YAML text (Markdown)"""
        # Rule 1: Exactly 24 root folders
        for i, line in enumerate(lines, start=1):
            if "24 Root-Ordner" in line or "24 Root-Module" in line:
                self.rule_counter += 1
                rule = SemanticRule(
                    rule_id=f"STRUCT-P1-{self.rule_counter:03d}",
                    source_line=i,
                    category="STRUCTURE",
                    yaml_file=None,
                    yaml_path=None,
                    field_name="root_count",
                    expected_value=24,
                    rule_type="MUST",
                    severity="CRITICAL",
                    description="Repository MUST have exactly 24 root directories",
                    validation_method="count(root_directories) == 24",
                    evidence_required="Directory listing of repository root"
                )
                self.rules.append(rule)
                break

        # Rule 2: Root-Level Exceptions file
        for i, line in enumerate(lines, start=1):
            if "23_compliance/exceptions/root_level_exceptions.yaml" in line:
                self.rule_counter += 1
                rule = SemanticRule(
                    rule_id=f"STRUCT-P1-{self.rule_counter:03d}",
                    source_line=i,
                    category="STRUCTURE",
                    yaml_file=None,
                    yaml_path=None,
                    field_name="root_exceptions_file",
                    expected_value="23_compliance/exceptions/root_level_exceptions.yaml",
                    rule_type="MUST",
                    severity="HIGH",
                    description="Root-level exceptions file MUST exist",
                    validation_method='file_exists("23_compliance/exceptions/root_level_exceptions.yaml")',
                    evidence_required="File path validation"
                )
                self.rules.append(rule)
                break

        # Rule 3: Structure exceptions unique
        for i, line in enumerate(lines, start=1):
            if "einzige gültige Struktur-Exception" in line and "structure_exceptions.yaml" in line:
                self.rule_counter += 1
                rule = SemanticRule(
                    rule_id=f"STRUCT-P1-{self.rule_counter:03d}",
                    source_line=i,
                    category="STRUCTURE",
                    yaml_file=None,
                    yaml_path=None,
                    field_name="structure_exceptions_unique",
                    expected_value="23_compliance/exceptions/structure_exceptions.yaml",
                    rule_type="MUST",
                    severity="CRITICAL",
                    description="Structure exceptions file MUST be unique (no copies in root)",
                    validation_method='unique_file("23_compliance/exceptions/structure_exceptions.yaml")',
                    evidence_required="File uniqueness check"
                )
                self.rules.append(rule)
                break

    def _determine_severity(self, field_name: str, value_str: str) -> str:
        """Determine severity based on field name and value keywords"""
        field_lower = field_name.lower()
        value_lower = value_str.lower()

        # CRITICAL keywords
        critical_keywords = ['security', 'legal', 'compliance', 'admin', 'deprecated', 'false',
                            'true', 'must', 'critical', 'sanctioned', 'blacklist', 'investment',
                            'yield', 'redemption', 'custodial', 'upgrade', 'dao']

        if any(kw in field_lower or kw in value_lower for kw in critical_keywords):
            return "CRITICAL"

        # HIGH keywords
        high_keywords = ['version', 'blockchain', 'standard', 'governance', 'token',
                        'fee', 'burn', 'distribution', 'supply']

        if any(kw in field_lower or kw in value_lower for kw in high_keywords):
            return "HIGH"

        # MEDIUM keywords
        medium_keywords = ['description', 'classification', 'date', 'scope']

        if any(kw in field_lower for kw in medium_keywords):
            return "MEDIUM"

        # Default
        return "LOW"

    def export_to_json(self, output_file: Path):
        """Export rules to JSON"""
        rules_dict = [asdict(rule) for rule in self.rules]

        output = {
            'source': str(self.part1_file.name),
            'total_rules': len(self.rules),
            'extraction_method': 'automated_yaml_parsing',
            'generated': '2025-10-21',
            'rules': rules_dict
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

    def export_to_markdown(self, output_file: Path):
        """Export rules to Markdown for comparison"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# Part1 Semantische Regeln - Maschinelle Extraktion\n")
            f.write("**Quelle:** SSID_structure_level3_part1_MAX.md\n")
            f.write("**Methode:** Automatische YAML-Parsing + Text-Analyse\n")
            f.write(f"**Total Rules:** {len(self.rules)}\n\n")
            f.write("---\n\n")

            # Group by category
            categories = {}
            for rule in self.rules:
                if rule.category not in categories:
                    categories[rule.category] = []
                categories[rule.category].append(rule)

            for category, rules in sorted(categories.items()):
                f.write(f"## {category} ({len(rules)} rules)\n\n")

                for rule in rules:
                    f.write(f"### {rule.rule_id}: {rule.description}\n")
                    f.write(f"- **Zeile:** {rule.source_line}\n")
                    if rule.yaml_file:
                        f.write(f"- **YAML-Datei:** `{rule.yaml_file}`\n")
                    if rule.yaml_path:
                        f.write(f"- **YAML-Pfad:** `{rule.yaml_path}`\n")
                    f.write(f"- **Erwarteter Wert:** `{repr(rule.expected_value)}`\n")
                    f.write(f"- **Typ:** {rule.rule_type}\n")
                    f.write(f"- **Severity:** {rule.severity}\n")
                    f.write(f"- **Validierung:** `{rule.validation_method}`\n")
                    f.write(f"- **Evidence:** {rule.evidence_required}\n")
                    f.write("\n")

                f.write("\n")


def main():
    """Main execution"""
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent.parent.parent

    part1_file = script_dir.parent / "SSID_structure_level3_part1_MAX.md"

    if not part1_file.exists():
        print(f"[ERROR] Part1 file not found: {part1_file}")
        return

    print("="*80)
    print("MASCHINELLE EXTRAKTION - Part1 Semantische Regeln")
    print("="*80)
    print()
    print(f"Quelle: {part1_file.name}")
    print()

    # Parse
    parser = Part1SemanticParser(part1_file)
    rules = parser.parse_all()

    print(f"Total Rules Extracted: {len(rules)}")
    print()

    # Category breakdown
    categories = {}
    for rule in rules:
        categories[rule.category] = categories.get(rule.category, 0) + 1

    print("Rules by Category:")
    print("-"*80)
    for cat, count in sorted(categories.items()):
        print(f"  {cat:30s} {count:4d} rules")
    print("-"*80)
    print()

    # Export
    json_output = script_dir / "part1_semantic_rules_machine.json"
    md_output = script_dir / "part1_semantic_rules_machine.md"

    parser.export_to_json(json_output)
    parser.export_to_markdown(md_output)

    print(f"[OK] JSON export: {json_output}")
    print(f"[OK] Markdown export: {md_output}")
    print()

    # Sample rules
    print("Sample Rules (first 10):")
    print("-"*80)
    for rule in rules[:10]:
        print(f"  {rule.rule_id}: {rule.description[:70]}")
    print()

    print("="*80)
    print("[COMPLETE] Maschinelle Extraktion abgeschlossen")
    print("="*80)


if __name__ == '__main__':
    main()
