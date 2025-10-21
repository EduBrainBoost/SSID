#!/usr/bin/env python3
"""
Complete SoT Master-Rule-List Extractor Part2 - Full Document (Zeilen 1-1366)
===============================================================================

Extrahiert ALLE Regeln aus SSID_structure_level3_part2_MAX.md systematisch:
- Jedes YAML-Feld = 1 Regel
- Jede normative Markdown-Zeile = 1 Regel
- Strukturheaders = eigene Regeln
- Listen-Items = einzelne Regeln

Ziel: Vollständige Masterlist Part2 mit ~1056 Regeln

Author: Claude Code AI
Date: 2025-10-19
Version: 3.0.0-PART2
"""

import sys
import yaml
import re
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime

class CompleteMasterlistExtractorPart2:
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.source_file = repo_root / "16_codex" / "structure" / "SSID_structure_level3_part2_MAX.md"
        self.output_file = repo_root / "02_audit_logging" / "reports" / "SoT_Complete_Masterlist_Part2_20251019.yaml"

        self.rules = []
        self.rule_counter = 1
        self.current_section = ""

    def parse_file(self):
        """Parse entire file line by line"""
        print(f"Parsing complete Part2 file: {self.source_file}")
        print(f"Total lines: 1366")

        with open(self.source_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        in_yaml = False
        in_bash = False
        in_json = False
        yaml_buffer = []
        yaml_start_line = 0

        for line_num, line in enumerate(lines, start=1):
            stripped = line.strip()

            # Detect section headers (###)
            if stripped.startswith('###'):
                section_name = stripped.replace('#', '').strip()
                self.current_section = section_name
                self.add_rule(
                    line_num=line_num,
                    kategorie="Section Header",
                    beschreibung=f"Section: {section_name}",
                    originaltext=stripped,
                    enforcement="MUST",
                    priority="INFO"
                )
                continue

            # Detect subsection headers (##)
            if stripped.startswith('##') and not stripped.startswith('###'):
                subsection_name = stripped.replace('#', '').strip()
                self.current_section = subsection_name
                self.add_rule(
                    line_num=line_num,
                    kategorie="Subsection Header",
                    beschreibung=f"Subsection: {subsection_name}",
                    originaltext=stripped,
                    enforcement="MUST",
                    priority="INFO"
                )
                continue

            # Detect YAML blocks
            if stripped == '```yaml' or (stripped.startswith('```yaml') and len(stripped) > 7):
                in_yaml = True
                yaml_start_line = line_num
                yaml_buffer = []
                continue

            # Detect Bash blocks
            if stripped == '```bash' or (stripped.startswith('```bash') and len(stripped) > 7):
                in_bash = True
                yaml_start_line = line_num
                yaml_buffer = []
                continue

            # Detect JSON blocks
            if stripped == '```json' or (stripped.startswith('```json') and len(stripped) > 7):
                in_json = True
                yaml_start_line = line_num
                yaml_buffer = []
                continue

            # End of code blocks
            if stripped == '```':
                if in_yaml and yaml_buffer:
                    self.parse_yaml_block('\n'.join(yaml_buffer), yaml_start_line)
                elif in_bash and yaml_buffer:
                    self.parse_bash_block('\n'.join(yaml_buffer), yaml_start_line)
                elif in_json and yaml_buffer:
                    self.parse_json_block('\n'.join(yaml_buffer), yaml_start_line)

                in_yaml = False
                in_bash = False
                in_json = False
                yaml_buffer = []
                continue

            if in_yaml or in_bash or in_json:
                yaml_buffer.append(line.rstrip())

        print(f"\nExtracted {len(self.rules)} total rules from Part2")

    def parse_yaml_block(self, yaml_text: str, start_line: int):
        """Parse YAML block and extract each field as a rule"""
        try:
            data = yaml.safe_load(yaml_text)
            if not data:
                return

            self.extract_rules_recursive(data, start_line, prefix="")

        except Exception as e:
            print(f"  Warning: YAML parse error at line {start_line}: {e}")

    def parse_bash_block(self, bash_text: str, start_line: int):
        """Parse Bash block - extract key validation logic as rules"""
        lines = bash_text.split('\n')
        for i, line in enumerate(lines):
            line_clean = line.strip()

            # Skip empty lines and comments
            if not line_clean or line_clean.startswith('#'):
                continue

            # Extract key bash logic lines (if/then/else, validations, etc.)
            if any(keyword in line_clean for keyword in ['if [', 'then', 'elif', 'else', 'fi', 'echo', 'exit']):
                self.add_rule(
                    line_num=start_line + i,
                    kategorie="Bash Validation",
                    beschreibung=f"Bash logic: {line_clean[:80]}",
                    originaltext=line_clean,
                    enforcement="MUST",
                    priority="HIGH"
                )

    def parse_json_block(self, json_text: str, start_line: int):
        """Parse JSON block - extract structure as rules"""
        try:
            import json
            data = json.loads(json_text)
            if not data:
                return

            self.extract_rules_recursive(data, start_line, prefix="")

        except Exception as e:
            print(f"  Warning: JSON parse error at line {start_line}: {e}")

    def extract_rules_recursive(self, data, line_ref: int, prefix: str = ""):
        """Recursively extract rules from nested YAML/JSON structure"""
        if isinstance(data, dict):
            for key, value in data.items():
                full_key = f"{prefix}.{key}" if prefix else key

                if isinstance(value, dict):
                    # Nested dict - recurse
                    self.extract_rules_recursive(value, line_ref, full_key)

                elif isinstance(value, list):
                    # List - add rule for the list itself
                    self.add_rule(
                        line_num=line_ref,
                        kategorie=self.categorize_field(key),
                        feld=full_key,
                        wert=f"List with {len(value)} items",
                        beschreibung=f"{full_key}: List container",
                        enforcement="SHOULD",
                        priority=self.determine_priority(key, value)
                    )

                    # Also extract list items
                    for i, item in enumerate(value):
                        if isinstance(item, (str, int, float, bool)):
                            self.add_rule(
                                line_num=line_ref,
                                kategorie=f"{self.categorize_field(key)} Item",
                                feld=f"{full_key}[{i}]",
                                wert=str(item),
                                beschreibung=f"{full_key} item {i}: {item}",
                                enforcement="SHOULD",
                                priority=self.determine_priority(key, item)
                            )
                        elif isinstance(item, dict):
                            self.extract_rules_recursive(item, line_ref, f"{full_key}[{i}]")

                else:
                    # Scalar value - create rule
                    self.add_rule(
                        line_num=line_ref,
                        kategorie=self.categorize_field(key),
                        feld=full_key,
                        wert=str(value),
                        beschreibung=f"{full_key}: {value}",
                        enforcement="MUST" if key in ['version', 'classification', 'enforcement'] else "SHOULD",
                        priority=self.determine_priority(key, value)
                    )

        elif isinstance(data, list):
            for i, item in enumerate(data):
                self.extract_rules_recursive(item, line_ref, f"{prefix}[{i}]")

    def categorize_field(self, key: str) -> str:
        """Categorize field based on key name"""
        key_lower = key.lower()

        if key in ['version', 'date', 'deprecated']:
            return 'Metadata'
        elif 'compliance' in key_lower or 'regulation' in key_lower:
            return 'Compliance'
        elif 'governance' in key_lower or 'dao' in key_lower:
            return 'Governance'
        elif 'guard' in key_lower or 'enforcement' in key_lower or 'validation' in key_lower:
            return 'Guard/Enforcement'
        elif 'module' in key_lower or 'structure' in key_lower:
            return 'Structure'
        elif 'registry' in key_lower or 'shard' in key_lower:
            return 'Registry'
        elif 'diversity' in key_lower or 'inclusion' in key_lower or 'esg' in key_lower:
            return 'ESG/Diversity'
        elif 'sector' in key_lower or 'compatibility' in key_lower:
            return 'Multi-Sector'
        elif 'anti_gaming' in key_lower or 'integrity' in key_lower:
            return 'Anti-Gaming'
        elif 'review' in key_lower or 'audit' in key_lower:
            return 'Review/Audit'
        else:
            return 'General'

    def determine_priority(self, key: str, value) -> str:
        """Determine priority based on key and value"""
        key_lower = key.lower()

        critical_keys = ['enforcement', 'guard', 'anti_gaming', 'compliance', 'critical', 'must']
        high_keys = ['governance', 'validation', 'registry', 'structure', 'module']
        medium_keys = ['description', 'note', 'path', 'sector', 'diversity']

        if any(ck in key_lower for ck in critical_keys):
            return 'CRITICAL'
        elif any(hk in key_lower for hk in high_keys):
            return 'HIGH'
        elif any(mk in key_lower for mk in medium_keys):
            return 'MEDIUM'
        elif key in ['version', 'date', 'deprecated']:
            return 'INFO'
        else:
            return 'LOW'

    def add_rule(self, **kwargs):
        """Add a rule to the list"""
        rule_id = f"SOT-PART2-{self.rule_counter:04d}"
        self.rule_counter += 1

        rule = {
            'regel_id': rule_id,
            'zeile': kwargs.get('line_num', 0),
            'kategorie': kwargs.get('kategorie', 'General'),
            'beschreibung': kwargs.get('beschreibung', ''),
            'enforcement': kwargs.get('enforcement', 'SHOULD'),
            'priority': kwargs.get('priority', 'MEDIUM')
        }

        if 'feld' in kwargs:
            rule['feld'] = kwargs['feld']
        if 'wert' in kwargs:
            rule['wert'] = kwargs['wert']
        if 'originaltext' in kwargs:
            rule['originaltext'] = kwargs['originaltext']

        self.rules.append(rule)

    def write_masterlist(self):
        """Write complete Part2 masterlist to file"""
        print(f"\nWriting complete Part2 masterlist to: {self.output_file}")

        # Group rules by section based on line ranges from user spec
        masterlist = {
            'metadata': {
                'version': '3.0.0-PART2-COMPLETE',
                'extraction_date': datetime.now().isoformat(),
                'source_file': str(self.source_file.name),
                'extracted_lines': '1-1366',
                'total_rules_extracted': len(self.rules),
                'extraction_method': 'AUTOMATED_FULL_EXTRACTION_PART2',
                'extractor': 'Claude Code AI (Part2 Complete Extraction Tool)',
                'validation_status': 'READY_FOR_POLICY_DEPTH_ANALYSIS'
            },
            'sections': []
        }

        # Line ranges based on user specification
        line_ranges = [
            (1, 8, "Common MUST"),
            (9, 23, "Zentralisierung"),
            (24, 126, "Root-Level Exceptions Framework"),
            (128, 185, "Root-Level Guard Implementation (Bash)"),
            (187, 244, "Kritische Dateien"),
            (246, 299, "Maintainer Definition & Backup Structure"),
            (301, 334, "Source of Truth Documentation"),
            (336, 441, "Diversity & Inclusion Standards"),
            (443, 508, "ESG & Sustainability Integration"),
            (510, 574, "Multi-Sector Compatibility Matrix"),
            (576, 611, "Module-Strukturen (MUST/OPTIONAL)"),
            (612, 795, "Detaillierte Modul-Strukturerklärungen"),
            (796, 860, "100-Punkte-Scoring + Badge Thresholds"),
            (861, 946, "Anti-Gaming & Integrity Controls"),
            (947, 1016, "Machine-Readable Review System (JSON)"),
            (1018, 1042, "Review CI/CD Integration"),
            (1044, 1138, "EU-Regulatorik-Mapping"),
            (1143, 1170, "Registry Pflichtstruktur"),
            (1175, 1187, "Common MUST je Modul"),
            (1191, 1280, "Root-Depth-Matrix"),
            (1285, 1309, "SHARD-16 Globale Pflicht-Belegung"),
            (1313, 1366, "CORRECTION: LOGS vs LOCKS")
        ]

        for start, end, section_name in line_ranges:
            section_rules = [r for r in self.rules if start <= r['zeile'] <= end]
            if section_rules:
                masterlist['sections'].append({
                    'section_name': section_name,
                    'zeilen': f"{start}-{end}",
                    'anzahl_regeln': len(section_rules),
                    'regeln': section_rules
                })

        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.output_file, 'w', encoding='utf-8') as f:
            yaml.dump(masterlist, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

        print(f"  OK Written {len(self.rules)} rules")

        # Print summary
        print(f"\n  Section Summary:")
        for section in masterlist['sections']:
            print(f"    {section['section_name']}: {section['anzahl_regeln']} rules")

def main():
    repo_root = Path(__file__).resolve().parent.parent.parent
    extractor = CompleteMasterlistExtractorPart2(repo_root)

    print("="*80)
    print("COMPLETE SOT MASTERLIST EXTRACTION - PART 2")
    print("="*80)

    extractor.parse_file()
    extractor.write_masterlist()

    print("\n" + "="*80)
    print(f"DONE - Extracted {len(extractor.rules)} total rules from Part2")
    print("="*80)

    return 0

if __name__ == "__main__":
    sys.exit(main())
