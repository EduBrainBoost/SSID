#!/usr/bin/env python3
"""
Complete SoT Master-Rule-List Extractor Part3 - Full Document
==============================================================

Extrahiert ALLE Regeln aus SSID_structure_level3_part3_MAX.md systematisch.

Ziel: Vollständige Masterlist Part3 mit ~1.131 Regeln

Author: Claude Code AI
Date: 2025-10-19
Version: 3.0.0-PART3
"""

import sys
import yaml
import json
import re
from pathlib import Path
from typing import Dict, List
from datetime import datetime

class CompleteMasterlistExtractorPart3:
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.source_file = repo_root / "16_codex" / "structure" / "SSID_structure_level3_part3_MAX.md"
        self.output_file = repo_root / "02_audit_logging" / "reports" / "SoT_Complete_Masterlist_Part3_20251019.yaml"

        self.rules = []
        self.rule_counter = 1
        self.current_section = ""

    def parse_file(self):
        """Parse entire Part3 file line by line"""
        print(f"Parsing complete Part3 file: {self.source_file}")

        with open(self.source_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        print(f"Total lines: {len(lines)}")

        in_yaml = False
        in_bash = False
        in_json = False
        code_buffer = []
        code_start_line = 0

        for line_num, line in enumerate(lines, start=1):
            stripped = line.strip()

            # Detect section headers
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

            # Detect code blocks
            if stripped.startswith('```yaml'):
                in_yaml = True
                code_start_line = line_num
                code_buffer = []
                continue
            elif stripped.startswith('```bash'):
                in_bash = True
                code_start_line = line_num
                code_buffer = []
                continue
            elif stripped.startswith('```json'):
                in_json = True
                code_start_line = line_num
                code_buffer = []
                continue

            if stripped == '```':
                if in_yaml and code_buffer:
                    self.parse_yaml_block('\n'.join(code_buffer), code_start_line)
                elif in_bash and code_buffer:
                    self.parse_bash_block('\n'.join(code_buffer), code_start_line)
                elif in_json and code_buffer:
                    self.parse_json_block('\n'.join(code_buffer), code_start_line)

                in_yaml = False
                in_bash = False
                in_json = False
                code_buffer = []
                continue

            if in_yaml or in_bash or in_json:
                code_buffer.append(line.rstrip())

        print(f"\nExtracted {len(self.rules)} total rules from Part3")

    def parse_yaml_block(self, yaml_text: str, start_line: int):
        """Parse YAML block"""
        try:
            data = yaml.safe_load(yaml_text)
            if not data:
                return
            self.extract_rules_recursive(data, start_line, prefix="")
        except Exception as e:
            print(f"  Warning: YAML parse error at line {start_line}: {e}")

    def parse_bash_block(self, bash_text: str, start_line: int):
        """Parse Bash block - extract key logic"""
        lines = bash_text.split('\n')
        for i, line in enumerate(lines):
            line_clean = line.strip()
            if not line_clean or line_clean.startswith('#'):
                continue
            if any(kw in line_clean for kw in ['if [', 'then', 'elif', 'else', 'fi', 'echo', 'exit']):
                self.add_rule(
                    line_num=start_line + i,
                    kategorie="Bash Validation",
                    beschreibung=f"Bash logic: {line_clean[:80]}",
                    originaltext=line_clean,
                    enforcement="MUST",
                    priority="HIGH"
                )

    def parse_json_block(self, json_text: str, start_line: int):
        """Parse JSON block"""
        try:
            data = json.loads(json_text)
            if not data:
                return
            self.extract_rules_recursive(data, start_line, prefix="")
        except Exception as e:
            print(f"  Warning: JSON parse error at line {start_line}: {e}")

    def extract_rules_recursive(self, data, line_ref: int, prefix: str = ""):
        """Recursively extract rules from nested structures"""
        if isinstance(data, dict):
            for key, value in data.items():
                full_key = f"{prefix}.{key}" if prefix else key

                if isinstance(value, dict):
                    self.extract_rules_recursive(value, line_ref, full_key)
                elif isinstance(value, list):
                    self.add_rule(
                        line_num=line_ref,
                        kategorie=self.categorize_field(key),
                        feld=full_key,
                        wert=f"List with {len(value)} items",
                        beschreibung=f"{full_key}: List container",
                        enforcement="SHOULD",
                        priority=self.determine_priority(key, value)
                    )
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
        elif any(x in key_lower for x in ['regulation', 'compliance', 'gdpr', 'mica', 'fatf']):
            return 'Regulatory'
        elif any(x in key_lower for x in ['quarantine', 'evidence', 'audit']):
            return 'Quarantine/Evidence'
        elif any(x in key_lower for x in ['standard', 'iso', 'nist', 'etsi']):
            return 'Standards'
        elif any(x in key_lower for x in ['privacy', 'ccpa', 'data_protection']):
            return 'Privacy'
        elif any(x in key_lower for x in ['review', 'template', 'documentation']):
            return 'Review/Documentation'
        elif any(x in key_lower for x in ['opencore', 'integration']):
            return 'Integration'
        else:
            return 'General'

    def determine_priority(self, key: str, value) -> str:
        """Determine priority based on key"""
        key_lower = key.lower()

        critical_keys = ['enforcement', 'quarantine', 'compliance', 'regulatory', 'critical']
        high_keys = ['standard', 'privacy', 'audit', 'evidence', 'validation']
        medium_keys = ['description', 'note', 'template', 'documentation']

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
        rule_id = f"SOT-PART3-{self.rule_counter:04d}"
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
        """Write complete Part3 masterlist to file"""
        print(f"\nWriting complete Part3 masterlist to: {self.output_file}")

        masterlist = {
            'metadata': {
                'version': '3.0.0-PART3-COMPLETE',
                'extraction_date': datetime.now().isoformat(),
                'source_file': str(self.source_file.name),
                'extracted_lines': f'1-{len(open(self.source_file).readlines())}',
                'total_rules_extracted': len(self.rules),
                'extraction_method': 'AUTOMATED_FULL_EXTRACTION_PART3',
                'extractor': 'Claude Code AI (Part3 Complete Extraction Tool)',
                'validation_status': 'READY_FOR_POLICY_DEPTH_ANALYSIS'
            },
            'sections': []
        }

        # Line ranges based on user specification
        line_ranges = [
            (1, 21, "EU-Regulatorik Fortsetzung"),
            (23, 88, "Globale Grundsteine v2.0"),
            (90, 124, "EU/EEA & UK/CH/LI v1.5"),
            (126, 146, "MENA/Africa v1.2"),
            (148, 186, "APAC v1.8"),
            (188, 222, "Amerika v1.3"),
            (224, 288, "Datenschutz v2.2"),
            (290, 315, "Finanzmarkt-Sicherheit v1.1"),
            (317, 326, "Finaler Delta-Patch"),
            (327, 387, "Internal Issue Templates"),
            (389, 420, "Community Contribution Guidelines"),
            (422, 470, "Enhanced Evidence Management"),
            (472, 593, "Quarantine Singleton Framework"),
            (595, 629, "Quarantine Hash-Ledger Implementation"),
            (631, 644, "Storage Locations"),
            (646, 677, "CI/CD-Automatisierung"),
            (679, 726, "Standards-Implementierung v1.5"),
            (728, 767, "Internal Review Requirements"),
            (769, 858, "Review Documentation Templates"),
            (860, 884, "Validierung Enhanced 4-Level"),
            (886, 903, "Legal Disclaimers"),
            (905, 946, "Quarantine Framework Canonical"),
            (948, 962, "Enhanced File Structure Summary"),
            (964, 972, "SSID Enhanced Enterprise Structure"),
            (974, 1071, "OpenCore Integration Summary"),
            (1073, 1092, "Chat-Intake ADDENDUM"),
            (1094, 1140, "Frontend/Backend Platzierung"),
            (1142, 1153, "CI-Gates & Tests"),
            (1155, 1210, "CORRECTION LOGS vs LOCKS")
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

        print(f"\n  Section Summary:")
        for section in masterlist['sections']:
            print(f"    {section['section_name']}: {section['anzahl_regeln']} rules")

def main():
    repo_root = Path(__file__).resolve().parent.parent.parent
    extractor = CompleteMasterlistExtractorPart3(repo_root)

    print("="*80)
    print("COMPLETE SOT MASTERLIST EXTRACTION - PART 3")
    print("="*80)

    extractor.parse_file()
    extractor.write_masterlist()

    print("\n" + "="*80)
    print(f"DONE - Extracted {len(extractor.rules)} total rules from Part3")
    print("="*80)

    return 0

if __name__ == "__main__":
    sys.exit(main())
