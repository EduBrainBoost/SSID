#!/usr/bin/env python3
"""
Coverage Mapper: Map 194 Validators to 416 Rules

Ziel: Identifiziere welche Regeln durch Validators abgedeckt sind
      und welche Gaps existieren
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Set


class CoverageMapper:
    """Map validators to rules and identify gaps"""

    def __init__(self, rules_file: Path, validators_file: Path):
        with open(rules_file, encoding='utf-8') as f:
            self.rules_data = json.load(f)
            self.rules = self.rules_data['rules']

        with open(validators_file, encoding='utf-8') as f:
            self.validators_data = json.load(f)
            self.validators = self.validators_data['validators']

        self.mapping = []
        self.covered_rules = set()
        self.uncovered_rules = []

    def map_validators_to_rules(self):
        """Create mapping between validators and rules"""

        print(f"Mapping {len(self.validators)} validators to {len(self.rules)} rules...")
        print()

        for validator in self.validators:
            validator_id = validator['rule_id']
            function_name = validator['function']
            description = validator['description']

            # Try to find matching rules
            matched_rules = self._find_matching_rules(validator_id, function_name, description)

            self.mapping.append({
                'validator': validator,
                'matched_rules': matched_rules,
                'coverage_count': len(matched_rules)
            })

            for rule_id in matched_rules:
                self.covered_rules.add(rule_id)

        # Identify uncovered rules
        all_rule_ids = {rule['rule_id'] for rule in self.rules}
        uncovered_ids = all_rule_ids - self.covered_rules

        self.uncovered_rules = [
            rule for rule in self.rules
            if rule['rule_id'] in uncovered_ids
        ]

    def _find_matching_rules(self, validator_id: str, function_name: str, description: str) -> List[str]:
        """Find rules that match this validator"""
        matched = []

        # Mapping patterns:
        # AR001-AR010 -> ARCHITECTURE rules
        # CP001-CP012 -> POLICIES rules (NON-CUSTODIAL, HASH-ONLY, GDPR, etc.)
        # VG001-VG008 -> VERSIONING/GOVERNANCE rules
        # CS001-CS011 -> CHART-YAML/STRUCTURE rules
        # MS001-MS006 -> MANIFEST-YAML rules
        # KP001-KP010 -> PRINCIPLES rules
        # TS001-TS005 -> STANDARDS rules
        # DC001-DC004 -> DEPLOYMENT/CI rules
        # MD-* -> Various master definition rules

        # Architecture validators (AR001-AR010)
        if validator_id.startswith('AR'):
            matched.extend([r['rule_id'] for r in self.rules if r['category'] == 'architecture'])

        # Policy validators (CP001-CP012)
        elif validator_id.startswith('CP'):
            # Map to specific policy categories
            if 'non_custodial' in description.lower() or 'pii' in description.lower():
                matched.extend([r['rule_id'] for r in self.rules
                                if r['category'] == 'policies' and
                                r['rule_id'].startswith('NON-CUSTODIAL')])
            elif 'hash' in description.lower():
                matched.extend([r['rule_id'] for r in self.rules
                                if r['category'] == 'policies' and
                                r['rule_id'].startswith('HASH-ONLY')])
            elif 'gdpr' in description.lower():
                matched.extend([r['rule_id'] for r in self.rules
                                if r['category'] == 'policies' and
                                r['rule_id'].startswith('GDPR')])
            elif 'bias' in description.lower():
                matched.extend([r['rule_id'] for r in self.rules
                                if r['category'] == 'policies' and
                                r['rule_id'].startswith('BIAS')])
            elif 'evidence' in description.lower() or 'audit' in description.lower():
                matched.extend([r['rule_id'] for r in self.rules
                                if r['category'] == 'policies' and
                                r['rule_id'].startswith('EVIDENCE')])
            elif 'secret' in description.lower():
                matched.extend([r['rule_id'] for r in self.rules
                                if r['category'] == 'policies' and
                                r['rule_id'].startswith('SECRETS')])

        # Versioning/Governance validators (VG001-VG008)
        elif validator_id.startswith('VG'):
            if 'semver' in description.lower() or 'version' in description.lower():
                matched.extend([r['rule_id'] for r in self.rules
                                if r['category'] == 'policies' and
                                r['rule_id'].startswith('VERSIONING')])
            if 'breaking' in description.lower() or 'deprecat' in description.lower():
                matched.extend([r['rule_id'] for r in self.rules
                                if r['category'] == 'governance'])

        # Chart Structure validators (CS001-CS011)
        elif validator_id.startswith('CS'):
            matched.extend([r['rule_id'] for r in self.rules if r['category'] == 'chart_yaml'])

        # Manifest Structure validators (MS001-MS006)
        elif validator_id.startswith('MS'):
            matched.extend([r['rule_id'] for r in self.rules if r['category'] == 'manifest_yaml'])

        # Core Principles validators (KP001-KP010)
        elif validator_id.startswith('KP'):
            matched.extend([r['rule_id'] for r in self.rules if r['category'] == 'principles'])

        # Tech Standards validators (TS001-TS005)
        elif validator_id.startswith('TS'):
            if 'mtls' in description.lower():
                matched.extend([r['rule_id'] for r in self.rules
                                if r['category'] == 'principles' and
                                'Zero-Trust' in r['description']])

        # Deployment/CI validators (DC001-DC004)
        elif validator_id.startswith('DC'):
            matched.extend([r['rule_id'] for r in self.rules if r['category'] == 'additions_v1_1_1' and r['subcategory'] == 'ci'])

        # Master Definition validators (MD-*)
        elif validator_id.startswith('MD'):
            # MD-ROOTS-* -> roots category
            if 'ROOTS' in validator_id or 'ROOT' in validator_id:
                matched.extend([r['rule_id'] for r in self.rules if r['category'] == 'roots'])

            # MD-SHARDS-* -> shards category
            elif 'SHARDS' in validator_id or 'SHARD' in validator_id:
                matched.extend([r['rule_id'] for r in self.rules if r['category'] == 'shards'])

            # MD-CHART-* -> chart_yaml category
            elif 'CHART' in validator_id:
                matched.extend([r['rule_id'] for r in self.rules if r['category'] == 'chart_yaml'])

            # MD-MANIFEST-* -> manifest_yaml category
            elif 'MANIFEST' in validator_id:
                matched.extend([r['rule_id'] for r in self.rules if r['category'] == 'manifest_yaml'])

            # MD-NAMING-* -> naming category
            elif 'NAMING' in validator_id:
                matched.extend([r['rule_id'] for r in self.rules if r['category'] == 'naming'])

            # MD-PRINC-* -> principles category
            elif 'PRINC' in validator_id:
                matched.extend([r['rule_id'] for r in self.rules if r['category'] == 'principles'])

        # Enhanced validators
        elif validator_id in ['VG002_ENHANCED', 'VG003_ENHANCED', 'VG004_ENHANCED']:
            matched.extend([r['rule_id'] for r in self.rules
                            if r['category'] == 'governance' or
                            (r['category'] == 'policies' and r['rule_id'].startswith('VERSIONING'))])

        elif validator_id == 'DC003_CANARY_ENHANCED':
            matched.extend([r['rule_id'] for r in self.rules
                            if r['category'] == 'governance' and
                            'Canary' in r['description']])

        elif validator_id == 'TS005_MTLS_ENFORCED':
            matched.extend([r['rule_id'] for r in self.rules
                            if r['category'] == 'principles' and
                            ('Zero-Trust' in r['description'] or 'mTLS' in r['description'])])

        elif validator_id == 'MD-PRINC-020_ENHANCED':
            matched.extend([r['rule_id'] for r in self.rules
                            if r['category'] == 'principles' and
                            'Docs-as-Code' in r['description']])

        # Maximalstand validators
        elif validator_id.startswith('FILE-') or validator_id.startswith('DOC-'):
            matched.extend([r['rule_id'] for r in self.rules if r['category'] == 'structure'])

        elif validator_id.startswith('REG-'):
            matched.extend([r['rule_id'] for r in self.rules
                            if r['category'] == 'additions_v1_1_1' and
                            r['subcategory'] == 'reg'])

        return list(set(matched))  # Remove duplicates

    def generate_coverage_report(self) -> Dict:
        """Generate coverage report"""
        total_validators = len(self.validators)
        total_rules = len(self.rules)
        covered_rules_count = len(self.covered_rules)
        uncovered_rules_count = len(self.uncovered_rules)

        coverage_percentage = (covered_rules_count / total_rules) * 100 if total_rules > 0 else 0

        # Group uncovered rules by category
        uncovered_by_category = {}
        for rule in self.uncovered_rules:
            cat = rule['category']
            if cat not in uncovered_by_category:
                uncovered_by_category[cat] = []
            uncovered_by_category[cat].append(rule)

        # Group covered rules by category
        covered_by_category = {}
        for rule_id in self.covered_rules:
            rule = next((r for r in self.rules if r['rule_id'] == rule_id), None)
            if rule:
                cat = rule['category']
                if cat not in covered_by_category:
                    covered_by_category[cat] = 0
                covered_by_category[cat] += 1

        report = {
            'summary': {
                'total_validators': total_validators,
                'total_rules': total_rules,
                'covered_rules': covered_rules_count,
                'uncovered_rules': uncovered_rules_count,
                'coverage_percentage': round(coverage_percentage, 2)
            },
            'coverage_by_category': {
                cat: {
                    'total': len([r for r in self.rules if r['category'] == cat]),
                    'covered': covered_by_category.get(cat, 0),
                    'uncovered': len(uncovered_by_category.get(cat, [])),
                    'percentage': round((covered_by_category.get(cat, 0) / len([r for r in self.rules if r['category'] == cat])) * 100, 2) if len([r for r in self.rules if r['category'] == cat]) > 0 else 0
                }
                for cat in set([r['category'] for r in self.rules])
            },
            'uncovered_rules_by_category': {
                cat: [r['rule_id'] + ': ' + r['description'][:60] for r in rules]
                for cat, rules in uncovered_by_category.items()
            },
            'mapping': self.mapping
        }

        return report

    def save_report(self, output_path: Path):
        """Save coverage report to JSON"""
        report = self.generate_coverage_report()

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"\nCoverage Report Summary:")
        print(f"  Total Validators: {report['summary']['total_validators']}")
        print(f"  Total Rules: {report['summary']['total_rules']}")
        print(f"  Covered Rules: {report['summary']['covered_rules']} ({report['summary']['coverage_percentage']}%)")
        print(f"  Uncovered Rules: {report['summary']['uncovered_rules']}")
        print()
        print("Coverage by Category:")
        for cat, stats in sorted(report['coverage_by_category'].items()):
            print(f"  {cat:20s}: {stats['covered']:3d}/{stats['total']:3d} ({stats['percentage']:5.1f}%)")
        print()
        print(f"Report saved to: {output_path}")


def main():
    rules_file = Path("C:/Users/bibel/Documents/Github/SSID/03_core/validators/sot/extracted_rules_master_def.json")
    validators_file = Path("C:/Users/bibel/Documents/Github/SSID/03_core/validators/sot/validator_inventory.json")
    output_file = Path("C:/Users/bibel/Documents/Github/SSID/03_core/validators/sot/coverage_report.json")

    mapper = CoverageMapper(rules_file, validators_file)
    mapper.map_validators_to_rules()
    mapper.save_report(output_file)


if __name__ == '__main__':
    main()
