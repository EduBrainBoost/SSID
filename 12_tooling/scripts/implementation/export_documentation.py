#!/usr/bin/env python3
"""
Export 586 documentation rules to 05_documentation/ as structured markdown
"""

import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

class DocumentationExporter:
    def __init__(self):
        self.unified_rules = None
        self.doc_rules = {}

    def load_unified_rules(self):
        """Load unified rule set"""
        unified_file = Path('24_meta_orchestration/registry/UNIFIED_RULE_SET.json')
        data = json.loads(unified_file.read_text(encoding='utf-8'))
        self.unified_rules = data['rules']

        # Filter documentation rules only
        for rule_id, rule in self.unified_rules.items():
            if rule['category'] == 'documentation':
                self.doc_rules[rule_id] = rule

        print(f"[OK] Loaded {len(self.doc_rules)} documentation rules")

    def export_by_category(self):
        """Export rules organized by category"""
        print()
        print("Exporting documentation by category...")
        print()

        # Group by type
        by_type = defaultdict(list)
        for rule_id, rule in self.doc_rules.items():
            by_type[rule['type']].append(rule)

        output_dir = Path('05_documentation/extracted_rules')
        output_dir.mkdir(parents=True, exist_ok=True)

        # Export headers (architectural structure)
        self.export_headers(by_type.get('header', []), output_dir)

        # Export YAML blocks (configurations)
        self.export_yaml_blocks(by_type.get('yaml_block', []), output_dir)

        # Export tables (mappings)
        self.export_tables(by_type.get('table_row', []), output_dir)

        # Export policies (MUST/SHOULD/MAY)
        policies = []
        for key in ['policy_list_item', 'inline_enforcement', 'bold_policy']:
            policies.extend(by_type.get(key, []))
        self.export_policies(policies, output_dir)

        # Export enforcement rules
        enforcement = []
        for key in ['inline_exit_code', 'inline_fail_condition', 'inline_ci_guard']:
            enforcement.extend(by_type.get(key, []))
        self.export_enforcement(enforcement, output_dir)

        # Export lifecycle (deprecations)
        lifecycle = by_type.get('inline_deprecation', [])
        self.export_lifecycle(lifecycle, output_dir)

        # Export constraints (forbidden/critical)
        constraints = []
        for key in ['inline_forbidden', 'inline_critical']:
            constraints.extend(by_type.get(key, []))
        self.export_constraints(constraints, output_dir)

        # Export processes (checklists, numbered lists)
        processes = []
        for key in ['checkbox', 'numbered_list']:
            processes.extend(by_type.get(key, []))
        self.export_processes(processes, output_dir)

        print(f"[OK] Documentation exported to: {output_dir}")
        print()

    def export_headers(self, headers, output_dir):
        """Export header hierarchy as architecture doc"""
        if not headers:
            return

        content = f"""# Architecture Structure (from Headers)

**Generated:** {datetime.now().isoformat()}
**Total Headers:** {len(headers)}

---

## Document Hierarchy

"""
        # Sort by line number to maintain order
        sorted_headers = sorted(headers, key=lambda x: (x['source_file'], x['line_number']))

        current_file = None
        for header in sorted_headers:
            if header['source_file'] != current_file:
                current_file = header['source_file']
                content += f"\n### From: {current_file}\n\n"

            level = header.get('level', 1)
            header_text = header['content']
            content += f"{'  ' * (level-1)}- {header_text} (L{header['line_number']})\n"

        output_file = output_dir / '01_architecture_structure.md'
        output_file.write_text(content, encoding='utf-8')
        print(f"[OK] Exported {len(headers)} headers to: {output_file.name}")

    def export_yaml_blocks(self, yaml_blocks, output_dir):
        """Export YAML configuration blocks"""
        if not yaml_blocks:
            return

        content = f"""# Configuration Templates (from YAML Blocks)

**Generated:** {datetime.now().isoformat()}
**Total YAML Blocks:** {len(yaml_blocks)}

---

"""
        for i, block in enumerate(yaml_blocks, 1):
            source = block['source_file']
            line = block['line_number']
            yaml_content = block['content']

            content += f"## Block {i}: {source}:L{line}\n\n"
            content += f"```yaml\n{yaml_content}\n```\n\n"

        output_file = output_dir / '02_configuration_templates.md'
        output_file.write_text(content, encoding='utf-8')
        print(f"[OK] Exported {len(yaml_blocks)} YAML blocks to: {output_file.name}")

    def export_tables(self, tables, output_dir):
        """Export table mappings"""
        if not tables:
            return

        content = f"""# Mapping Tables

**Generated:** {datetime.now().isoformat()}
**Total Table Rows:** {len(tables)}

---

"""
        # Group by source file
        by_file = defaultdict(list)
        for table in tables:
            by_file[table['source_file']].append(table)

        for filename, rows in by_file.items():
            content += f"## From: {filename}\n\n"
            for row in rows[:10]:  # Sample first 10
                content += f"- L{row['line_number']}: {row['content'][:100]}\n"
            if len(rows) > 10:
                content += f"\n... and {len(rows) - 10} more rows\n"
            content += "\n"

        output_file = output_dir / '03_mapping_tables.md'
        output_file.write_text(content, encoding='utf-8')
        print(f"[OK] Exported {len(tables)} table rows to: {output_file.name}")

    def export_policies(self, policies, output_dir):
        """Export policy requirements"""
        if not policies:
            return

        content = f"""# Policy Requirements

**Generated:** {datetime.now().isoformat()}
**Total Policy Rules:** {len(policies)}

---

## MUST Requirements

"""
        must_rules = [p for p in policies if p['priority'] == 'MUST']
        for rule in must_rules:
            content += f"- **{rule['source_file']}:L{rule['line_number']}** - {rule['content']}\n"

        content += "\n## SHOULD Recommendations\n\n"
        should_rules = [p for p in policies if p['priority'] == 'SHOULD']
        for rule in should_rules:
            content += f"- **{rule['source_file']}:L{rule['line_number']}** - {rule['content']}\n"

        content += "\n## MAY Optional\n\n"
        may_rules = [p for p in policies if p['priority'] == 'MAY']
        for rule in may_rules:
            content += f"- **{rule['source_file']}:L{rule['line_number']}** - {rule['content']}\n"

        output_file = output_dir / '04_policy_requirements.md'
        output_file.write_text(content, encoding='utf-8')
        print(f"[OK] Exported {len(policies)} policies to: {output_file.name}")

    def export_enforcement(self, enforcement, output_dir):
        """Export enforcement rules"""
        if not enforcement:
            return

        content = f"""# Enforcement Rules

**Generated:** {datetime.now().isoformat()}
**Total Enforcement Rules:** {len(enforcement)}

---

"""
        for rule in enforcement:
            content += f"## {rule['type']}: {rule['source_file']}:L{rule['line_number']}\n\n"
            content += f"{rule['content']}\n\n"

        output_file = output_dir / '05_enforcement_rules.md'
        output_file.write_text(content, encoding='utf-8')
        print(f"[OK] Exported {len(enforcement)} enforcement rules to: {output_file.name}")

    def export_lifecycle(self, lifecycle, output_dir):
        """Export lifecycle management (deprecations)"""
        if not lifecycle:
            return

        content = f"""# Lifecycle Management

**Generated:** {datetime.now().isoformat()}
**Total Deprecation Flags:** {len(lifecycle)}

---

"""
        for rule in lifecycle:
            content += f"- **{rule['source_file']}:L{rule['line_number']}** - {rule['content']}\n"

        output_file = output_dir / '06_lifecycle_management.md'
        output_file.write_text(content, encoding='utf-8')
        print(f"[OK] Exported {len(lifecycle)} lifecycle rules to: {output_file.name}")

    def export_constraints(self, constraints, output_dir):
        """Export constraints (VERBOTEN/KRITISCH)"""
        if not constraints:
            return

        content = f"""# Critical Constraints

**Generated:** {datetime.now().isoformat()}
**Total Constraints:** {len(constraints)}

---

"""
        for rule in constraints:
            priority = rule['priority']
            content += f"## {priority}: {rule['source_file']}:L{rule['line_number']}\n\n"
            content += f"{rule['content']}\n\n"

        output_file = output_dir / '07_critical_constraints.md'
        output_file.write_text(content, encoding='utf-8')
        print(f"[OK] Exported {len(constraints)} constraints to: {output_file.name}")

    def export_processes(self, processes, output_dir):
        """Export process workflows"""
        if not processes:
            return

        content = f"""# Process Workflows

**Generated:** {datetime.now().isoformat()}
**Total Process Items:** {len(processes)}

---

## Checklists

"""
        checklists = [p for p in processes if p['type'] == 'checkbox']
        for item in checklists:
            checked = "[x]" if item.get('checked') else "[ ]"
            content += f"- {checked} {item['content']} ({item['source_file']}:L{item['line_number']})\n"

        content += "\n## Sequential Processes\n\n"
        numbered = [p for p in processes if p['type'] == 'numbered_list']
        for item in numbered:
            number = item.get('number', '?')
            content += f"{number}. {item['content']} ({item['source_file']}:L{item['line_number']})\n"

        output_file = output_dir / '08_process_workflows.md'
        output_file.write_text(content, encoding='utf-8')
        print(f"[OK] Exported {len(processes)} process items to: {output_file.name}")

    def create_index(self):
        """Create index of all exported documentation"""
        output_dir = Path('05_documentation/extracted_rules')

        content = f"""# Extracted Rules Index

**Generated:** {datetime.now().isoformat()}
**Total Documentation Rules:** {len(self.doc_rules)}

---

## Overview

This directory contains all {len(self.doc_rules)} documentation rules extracted from the 4 master SoT files.

## Files

1. **01_architecture_structure.md** - Document hierarchy from headers (341 headers)
2. **02_configuration_templates.md** - YAML configuration blocks (47 blocks)
3. **03_mapping_tables.md** - Mapping tables (56 tables)
4. **04_policy_requirements.md** - MUST/SHOULD/MAY policies
5. **05_enforcement_rules.md** - Exit codes, CI guards
6. **06_lifecycle_management.md** - Deprecation tracking (36 flags)
7. **07_critical_constraints.md** - VERBOTEN/KRITISCH rules
8. **08_process_workflows.md** - Checklists and numbered workflows

## Source Files

- ssid_master_definition_corrected_v1.1.1.md (197 rules)
- SSID_structure_level3_part1_MAX.md (107 rules)
- SSID_structure_level3_part2_MAX.md (156 rules)
- SSID_structure_level3_part3_MAX.md (126 rules)

## Related Files

- `24_meta_orchestration/registry/UNIFIED_RULE_SET.json` - Complete unified rule set (5,306 rules)
- `24_meta_orchestration/registry/TRACEABILITY_MATRIX.json` - Mappings between doc and semantic rules

---

**Note:** These are DOCUMENTATION rules (WHAT). See semantic rules for IMPLEMENTATION (HOW).
"""

        index_file = output_dir / 'README.md'
        index_file.write_text(content, encoding='utf-8')
        print(f"[OK] Created index: {index_file}")

def main():
    print("="*70)
    print("EXPORTING DOCUMENTATION TO 05_documentation/")
    print("="*70)
    print()

    exporter = DocumentationExporter()
    exporter.load_unified_rules()
    exporter.export_by_category()
    exporter.create_index()

    print("="*70)
    print("DOCUMENTATION EXPORT COMPLETE")
    print("="*70)
    print()

if __name__ == '__main__':
    main()
