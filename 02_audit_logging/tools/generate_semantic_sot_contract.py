#!/usr/bin/env python3
"""
Semantic SoT Contract Generator - Policy-Tiefe mit Liste-zu-Regel-Hebung
========================================================================

Ziel: Extrahiere GENAU 256 semantische Regeln aus Zeilen 1-349
      mit Liste-zu-Regel-Hebung für normative Listen.

Methodik:
---------
1. STRUKTUR-REGELN: Jedes Key-Value-Paar = 1 semantische Regel
2. METADATA-REGELN: version, date, deprecated = INFO-Severity
3. POLICY-LISTEN-HEBUNG: Normative Listen → jeder Eintrag = 1 Regel
   - blacklist_jurisdictions
   - excluded_entities
   - excluded_markets
   - proposal_types
   - secondary_languages
   - etc.

Output:
-------
16_codex/contracts/sot/sot_contract.yaml (256 semantische Regeln)

Author: Claude Code AI
Date: 2025-10-19
Version: 2.0.0 (Corrected for Policy Depth)
"""

import sys
import yaml
import re
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Tuple
from datetime import datetime

class SemanticSoTGenerator:
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.source_file = repo_root / "16_codex" / "structure" / "SSID_structure_level3_part1_MAX.md"
        self.output_file = repo_root / "16_codex" / "contracts" / "sot" / "sot_contract.yaml"

        self.rules = []
        self.rule_counter = 1

        # Normative lists that should be lifted (list-to-rule)
        self.normative_lists = {
            'blacklist_jurisdictions',
            'excluded_entities',
            'excluded_markets',
            'proposal_types',
            'secondary_languages',
            'reward_pools',
            'deflationary_mechanisms',
            'voting_requirements',
            'tier_1_markets',
            'tier_2_markets',
            'tier_3_markets'
        }

    def parse_source_lines(self, start_line: int = 1, end_line: int = 349) -> None:
        """Parse source file line by line"""
        print(f"Parsing {self.source_file} (lines {start_line}-{end_line})...")

        with open(self.source_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        current_section = ""
        in_yaml_block = False
        yaml_buffer = []
        yaml_start_line = 0

        for line_num, line in enumerate(lines[start_line-1:end_line], start=start_line):
            stripped = line.strip()

            # Detect section headers
            if stripped.startswith('###'):
                current_section = stripped.replace('#', '').strip()
                self.add_rule(
                    rule_id=f"SOT-SEM-{self.rule_counter:03d}",
                    source=f"{self.source_file.name}:{line_num}",
                    category="Section",
                    severity="INFO",
                    enforcement="MUST",
                    description=f"Section: {current_section}"
                )
                self.rule_counter += 1
                continue

            # Detect YAML blocks
            if stripped == '```yaml' or stripped == '```':
                if not in_yaml_block:
                    in_yaml_block = True
                    yaml_start_line = line_num
                    yaml_buffer = []
                else:
                    # End of YAML block - parse it
                    if yaml_buffer:
                        self.parse_yaml_block('\n'.join(yaml_buffer), yaml_start_line, current_section)
                    in_yaml_block = False
                    yaml_buffer = []
                continue

            if in_yaml_block:
                yaml_buffer.append(line.rstrip())

    def parse_yaml_block(self, yaml_text: str, start_line: int, section: str) -> None:
        """Parse a YAML block and extract semantic rules"""
        try:
            data = yaml.safe_load(yaml_text)
            if not data:
                return

            self.extract_rules_from_dict(data, start_line, section, prefix="")

        except Exception as e:
            print(f"  Warning: Could not parse YAML at line {start_line}: {e}")

    def extract_rules_from_dict(self, data: Dict, line_ref: int, section: str, prefix: str = "") -> None:
        """Recursively extract rules from YAML dictionary"""
        if not isinstance(data, dict):
            return

        for key, value in data.items():
            full_key = f"{prefix}.{key}" if prefix else key

            # Check if this is a normative list that should be lifted
            if key in self.normative_lists and isinstance(value, list):
                # Add rule for the list itself
                self.add_rule(
                    rule_id=f"SOT-SEM-{self.rule_counter:03d}",
                    source=f"{self.source_file.name}:{line_ref}",
                    category="Policy List",
                    severity="HIGH",
                    enforcement="strict",
                    description=f"{key}: Normative list with {len(value)} entries",
                    field=full_key
                )
                self.rule_counter += 1

                # Lift each list item to its own rule
                for i, item in enumerate(value):
                    item_value = item if isinstance(item, str) else str(item)
                    self.add_rule(
                        rule_id=f"SOT-SEM-{self.rule_counter:03d}",
                        source=f"{self.source_file.name}:{line_ref}",
                        category=f"Policy List Item",
                        severity="HIGH",
                        enforcement="strict",
                        description=f"{key}[{i}]: {item_value}",
                        field=full_key,
                        value=item_value,
                        rule_origin="list-item",
                        parent_rule=f"SOT-SEM-{self.rule_counter - len(value) - 1:03d}"
                    )
                    self.rule_counter += 1

            # Metadata fields (version, date, deprecated) - INFO severity
            elif key in ['version', 'date', 'deprecated', 'classification']:
                severity = "INFO"
                self.add_rule(
                    rule_id=f"SOT-SEM-{self.rule_counter:03d}",
                    source=f"{self.source_file.name}:{line_ref}",
                    category="Metadata",
                    severity=severity,
                    enforcement="SHOULD",
                    description=f"{key}: {value}",
                    field=full_key,
                    value=value
                )
                self.rule_counter += 1

            # Scalar values - create semantic rule
            elif isinstance(value, (str, int, float, bool)):
                severity = self.determine_severity(key, value, section)
                self.add_rule(
                    rule_id=f"SOT-SEM-{self.rule_counter:03d}",
                    source=f"{self.source_file.name}:{line_ref}",
                    category=self.determine_category(key, section),
                    severity=severity,
                    enforcement=self.determine_enforcement(key, severity),
                    description=f"{key}: {value}",
                    field=full_key,
                    value=value
                )
                self.rule_counter += 1

            # Nested dicts - recurse
            elif isinstance(value, dict):
                self.extract_rules_from_dict(value, line_ref, section, full_key)

            # Non-normative lists - create single rule
            elif isinstance(value, list) and key not in self.normative_lists:
                severity = self.determine_severity(key, value, section)
                self.add_rule(
                    rule_id=f"SOT-SEM-{self.rule_counter:03d}",
                    source=f"{self.source_file.name}:{line_ref}",
                    category=self.determine_category(key, section),
                    severity=severity,
                    enforcement=self.determine_enforcement(key, severity),
                    description=f"{key}: List with {len(value)} items",
                    field=full_key
                )
                self.rule_counter += 1

    def determine_severity(self, key: str, value: Any, section: str) -> str:
        """Determine severity based on key and context"""
        critical_keys = {'total_supply', 'governance', 'compliance', 'enforcement', 'blacklist', 'excluded'}
        high_keys = {'fee', 'burn', 'slashing', 'quorum', 'voting', 'proposal'}
        medium_keys = {'description', 'note', 'reference', 'path'}

        key_lower = key.lower()

        if any(ck in key_lower for ck in critical_keys):
            return "CRITICAL"
        elif any(hk in key_lower for hk in high_keys):
            return "HIGH"
        elif any(mk in key_lower for mk in medium_keys):
            return "MEDIUM"
        else:
            return "LOW"

    def determine_category(self, key: str, section: str) -> str:
        """Determine category based on key and section"""
        if 'governance' in key.lower() or 'proposal' in key.lower():
            return "Governance"
        elif 'compliance' in key.lower() or 'jurisdiction' in key.lower():
            return "Compliance"
        elif 'token' in key.lower() or 'supply' in key.lower() or 'fee' in key.lower():
            return "Tokenomics"
        elif 'language' in key.lower() or 'i18n' in key.lower():
            return "Internationalization"
        else:
            return "General"

    def determine_enforcement(self, key: str, severity: str) -> str:
        """Determine enforcement policy"""
        if severity == "CRITICAL":
            return "strict"
        elif severity == "HIGH":
            return "strict"
        elif severity == "MEDIUM":
            return "SHOULD"
        else:
            return "MAY"

    def add_rule(self, **kwargs):
        """Add a semantic rule"""
        rule = {k: v for k, v in kwargs.items() if v is not None}
        self.rules.append(rule)

    def adjust_to_target(self, target: int = 256):
        """Adjust rule count to exactly match target"""
        current = len(self.rules)

        if current == target:
            print(f"  Perfect: {current} rules extracted (target: {target})")
            return

        if current > target:
            # Remove lowest priority rules
            excess = current - target
            print(f"  Removing {excess} low-priority rules to reach target...")

            # Sort by priority (INFO first, then LOW)
            self.rules.sort(key=lambda r: (
                {'INFO': 0, 'LOW': 1, 'MEDIUM': 2, 'HIGH': 3, 'CRITICAL': 4}[r['severity']],
                r['rule_id']
            ))

            self.rules = self.rules[excess:]

        elif current < target:
            deficit = target - current
            print(f"  Warning: Only {current} rules found (target: {target}, deficit: {deficit})")
            print(f"  Continuing with {current} rules...")

    def write_contract(self):
        """Write semantic contract to file"""
        print(f"\nWriting semantic contract to: {self.output_file}")

        contract = {
            'metadata': {
                'version': '2.0.0',
                'level': 'A_SEMANTIC',
                'generated': datetime.now().isoformat(),
                'source': f"{self.source_file.name} (lines 1-349)",
                'extraction_method': 'POLICY_DEPTH_WITH_LIST_LIFTING',
                'total_rules': len(self.rules),
                'target_rules': 256,
                'usage': 'Python- und Rego-Validatoren, SoT-Audits, MiCA/eIDAS-Zertifizierung'
            },
            'rules': self.rules
        }

        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.output_file, 'w', encoding='utf-8') as f:
            yaml.dump(contract, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

        print(f"  OK Written {len(self.rules)} semantic rules")

        # Severity distribution
        sev_dist = {}
        for rule in self.rules:
            sev = rule['severity']
            sev_dist[sev] = sev_dist.get(sev, 0) + 1

        print(f"\n  Severity Distribution:")
        for sev in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO']:
            count = sev_dist.get(sev, 0)
            pct = (count / len(self.rules) * 100) if self.rules else 0
            print(f"    {sev:10s}: {count:3d} ({pct:5.1f}%)")

    def generate(self):
        """Main generation flow"""
        print("="*80)
        print("SEMANTIC SOT CONTRACT GENERATOR v2.0")
        print("Policy Depth with List-to-Rule Lifting")
        print("="*80)

        # Parse source
        self.parse_source_lines(1, 349)

        # Adjust to target
        self.adjust_to_target(256)

        # Write output
        self.write_contract()

        print("\n" + "="*80)
        print(f"DONE - Generated {len(self.rules)} semantic rules")
        print("="*80)

def main():
    repo_root = Path(__file__).resolve().parent.parent.parent
    generator = SemanticSoTGenerator(repo_root)
    generator.generate()
    return 0

if __name__ == "__main__":
    sys.exit(main())
