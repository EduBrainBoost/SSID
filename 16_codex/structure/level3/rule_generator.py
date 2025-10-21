#!/usr/bin/env python3
"""
Automatic Rule Generator - List-to-Rule Lifting

Generiert aus Policy-Lists (YAML) individuelle Regeln für Coverage-Checking.
Erhöht semantische Tiefe von ~172 auf ~256 Regeln.

Usage:
    python rule_generator.py \
        --input list_to_rule_schema.yaml \
        --output master_rules_lifted.yaml
"""

import argparse
import yaml
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime


class RuleGenerator:
    """Generiert Regeln aus Policy-Lists."""
    
    def __init__(self, schema_path: Path):
        """
        Initialisiert Generator.
        
        Args:
            schema_path: Pfad zu list_to_rule_schema.yaml
        """
        with open(schema_path, 'r', encoding='utf-8') as f:
            self.schema = yaml.safe_load(f)
        
        self.policy_lists = self.schema.get('policy_lists', {})
        self.generated_rules = {}
    
    def generate_all_rules(self) -> Dict[str, Dict]:
        """
        Generiert alle Regeln aus Policy-Lists.
        
        Returns:
            Dict mit generierten Regeln
        """
        print(f"\n[*] Generating rules from {len(self.policy_lists)} policy lists...")

        for list_name, list_data in self.policy_lists.items():
            print(f"\n[*] Processing: {list_name}")
            print(f"   Parent Rule: {list_data['parent_rule']}")
            print(f"   Items: {len(list_data['items'])}")

            rules = self._generate_rules_from_list(list_name, list_data)
            self.generated_rules.update(rules)

            print(f"   [+] Generated {len(rules)} rules")

        print(f"\n[+] Total generated rules: {len(self.generated_rules)}")
        return self.generated_rules
    
    def _generate_rules_from_list(
        self,
        list_name: str,
        list_data: Dict
    ) -> Dict[str, Dict]:
        """
        Generiert Regeln aus einer Policy-List.
        
        Args:
            list_name: Name der Liste
            list_data: List-Daten aus Schema
        
        Returns:
            Dict mit generierten Regeln
        """
        rules = {}
        
        parent_rule = list_data['parent_rule']
        description = list_data['description']
        category = self._derive_category(list_name)
        
        for idx, item in enumerate(list_data['items']):
            rule_id = item.get('rule_id', f"{parent_rule}_{list_name.upper()}_{idx:03d}")
            
            rule = self._generate_single_rule(
                rule_id=rule_id,
                list_name=list_name,
                list_data=list_data,
                item=item,
                index=idx,
                category=category
            )
            
            rules[rule_id] = rule
        
        return rules
    
    def _generate_single_rule(
        self,
        rule_id: str,
        list_name: str,
        list_data: Dict,
        item: Dict,
        index: int,
        category: str
    ) -> Dict:
        """
        Generiert einzelne Regel aus Listen-Item.
        
        Args:
            rule_id: Regel-ID
            list_name: Name der Liste
            list_data: List-Metadaten
            item: Item-Daten
            index: Index in Liste
            category: Kategorie
        
        Returns:
            Regel-Dict
        """
        # Generiere Regel-Text basierend auf Listen-Typ
        rule_text = self._generate_rule_text(list_name, item)
        
        # Generiere Implementation Requirements
        impl_reqs = self._generate_implementation_requirements(
            list_name, item, rule_id
        )
        
        rule = {
            'type': 'MUST',
            'rule': rule_text,
            'source': f"List-to-Rule Lifting - {list_data['parent_rule']}",
            'category': category,
            'severity': item.get('severity', 'MEDIUM'),
            'list_metadata': {
                'list_name': list_name,
                'list_source': list_data['source'],
                'list_index': index,
                'audit_requirement': list_data['audit_requirement']
            },
            'item_data': {k: v for k, v in item.items() if k not in ['rule_id', 'severity']},
            'implementation_requirements': impl_reqs
        }
        
        return rule
    
    def _generate_rule_text(self, list_name: str, item: Dict) -> str:
        """Generiert Menschen-lesbaren Regel-Text."""
        
        if list_name == 'blacklist_jurisdictions':
            return (
                f"System MUSS Transaktionen aus {item['name']} ({item['code']}) "
                f"blockieren. Grund: {item['reason']}"
            )
        
        elif list_name == 'governance_proposal_types':
            return (
                f"System MUSS Proposal-Typ '{item['name']}' ({item['type']}) "
                f"unterstützen mit Quorum {item['quorum']} und Threshold {item['threshold']}"
            )
        
        elif list_name.startswith('covered_jurisdictions'):
            return (
                f"System MUSS {item['name']} ({item['code']}) als Tier {item['tier']} "
                f"Market mit eIDAS-Level '{item['eidas_level']}' unterstützen"
            )
        
        elif list_name == 'reward_pools':
            return (
                f"System MUSS Reward Pool '{item['name']}' ({item['pool_id']}) "
                f"mit {item['allocation_percent']}% Allocation und "
                f"Vesting '{item['vesting']}' verwalten"
            )
        
        elif list_name == 'supported_networks':
            return (
                f"System MUSS Blockchain-Netzwerk {item['name']} "
                f"(Chain ID: {item['chain_id']}) unterstützen"
            )
        
        elif list_name == 'supported_auth_methods':
            return (
                f"System MUSS Authentifizierungsmethode '{item['name']}' "
                f"({item['method_id']}) mit eIDAS-Level '{item['eidas_level']}' "
                f"unterstützen"
            )
        
        elif list_name == 'pii_categories':
            special = " (GDPR Special Category)" if item.get('special_category') else ""
            return (
                f"System MUSS PII-Kategorie '{item['name']}' ({item['category_id']}) "
                f"gemäß {item['gdpr_article']} behandeln{special}"
            )
        
        elif list_name == 'approved_hash_algorithms':
            qs = " (Quantum-Safe)" if item.get('quantum_safe') else ""
            return (
                f"System MUSS Hash-Algorithmus {item['name']} ({item['bits']} bits) "
                f"als '{item['status']}'{qs} unterstützen"
            )
        
        elif list_name == 'data_retention_periods':
            return (
                f"System MUSS Retention Period für '{item['data_type']}' "
                f"auf {item['retention_days']} Tage setzen. Grund: {item['reason']}"
            )
        
        elif list_name == 'supported_did_methods':
            return (
                f"System MUSS DID-Methode {item['method_name']} ({item['name']}) "
                f"gemäß Spec {item['spec']} unterstützen"
            )
        
        else:
            # Fallback für unbekannte Listen-Typen
            item_name = item.get('name', item.get('code', 'Unknown'))
            return f"System MUSS Item '{item_name}' aus Liste '{list_name}' unterstützen"
    
    def _generate_implementation_requirements(
        self,
        list_name: str,
        item: Dict,
        rule_id: str
    ) -> List[str]:
        """Generiert Implementation Requirements pro Regel."""
        
        requirements = [
            f"OPA Policy: deny/allow für {rule_id}",
            f"Unit Test: test_{rule_id.lower()}()",
            f"Audit Trail: Log all {rule_id}-related events"
        ]
        
        # Spezifische Requirements basierend auf Listen-Typ
        if list_name == 'blacklist_jurisdictions':
            code = item['code']
            requirements.extend([
                f"Runtime Check: Block if input.country_code == '{code}'",
                f"API Response: 403 Forbidden with reason 'Sanctioned jurisdiction: {code}'"
            ])
        
        elif list_name == 'governance_proposal_types':
            proposal_type = item['type']
            requirements.extend([
                f"DAO Contract: Validate proposal type == '{proposal_type}'",
                f"Quorum Check: Require {item['quorum']} participation",
                f"Threshold Check: Require {item['threshold']} approval"
            ])
        
        elif list_name == 'supported_networks':
            chain_id = item['chain_id']
            requirements.extend([
                f"Network Config: Add Chain ID {chain_id}",
                f"RPC Endpoint: Configure for {item['name']}",
                f"Block Explorer: Link to {item['explorer']}"
            ])
        
        elif list_name == 'pii_categories':
            requirements.extend([
                f"PII Detector: Recognize {item['category_id']}",
                f"Hash-Only Storage: Never store raw {item['category_id']}",
                f"GDPR Compliance: Implement {item['gdpr_article']}"
            ])
        
        return requirements
    
    def _derive_category(self, list_name: str) -> str:
        """Leitet Kategorie aus Listen-Namen ab."""
        
        category_map = {
            'blacklist_jurisdictions': 'Sanctions Compliance',
            'governance_proposal_types': 'DAO Governance',
            'covered_jurisdictions': 'Market Coverage',
            'reward_pools': 'Tokenomics',
            'supported_networks': 'Blockchain Integration',
            'supported_auth_methods': 'Authentication',
            'pii_categories': 'GDPR Compliance',
            'approved_hash_algorithms': 'Cryptography',
            'data_retention_periods': 'GDPR Retention',
            'supported_did_methods': 'Identity Standards'
        }
        
        for key, category in category_map.items():
            if key in list_name:
                return category
        
        return 'General Compliance'
    
    def export_to_yaml(self, output_path: Path):
        """
        Exportiert generierte Regeln als YAML.
        
        Args:
            output_path: Ziel-Datei
        """
        output = {
            'version': '1.3.0',
            'generation_date': datetime.now().isoformat(),
            'generation_method': 'automatic_list_to_rule_lifting',
            'total_generated_rules': len(self.generated_rules),
            'source_schema': 'list_to_rule_schema.yaml',
            'lifted_rules': self.generated_rules,
            'statistics': {
                'total_rules': len(self.generated_rules),
                'rules_by_severity': self._count_by_severity(),
                'rules_by_category': self._count_by_category()
            }
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(output, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

        print(f"\n[+] Exported to: {output_path}")
        print(f"[+] Total rules: {len(self.generated_rules)}")
    
    def _count_by_severity(self) -> Dict[str, int]:
        """Zählt Regeln nach Severity."""
        counts = {}
        for rule in self.generated_rules.values():
            severity = rule['severity']
            counts[severity] = counts.get(severity, 0) + 1
        return counts
    
    def _count_by_category(self) -> Dict[str, int]:
        """Zählt Regeln nach Kategorie."""
        counts = {}
        for rule in self.generated_rules.values():
            category = rule['category']
            counts[category] = counts.get(category, 0) + 1
        return counts


def main():
    """CLI Entry Point."""
    parser = argparse.ArgumentParser(
        description="Generate rules from policy lists (List-to-Rule Lifting)"
    )
    parser.add_argument(
        '--input',
        type=Path,
        required=True,
        help='Path to list_to_rule_schema.yaml'
    )
    parser.add_argument(
        '--output',
        type=Path,
        default=Path('master_rules_lifted.yaml'),
        help='Output path for generated rules'
    )
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Print detailed statistics'
    )
    
    args = parser.parse_args()
    
    # Validierung
    if not args.input.exists():
        print(f"[ERROR] Input file not found: {args.input}")
        return 1

    # Generierung
    generator = RuleGenerator(args.input)
    rules = generator.generate_all_rules()

    # Export
    generator.export_to_yaml(args.output)

    # Statistiken
    if args.stats:
        print("\n" + "="*70)
        print("STATISTICS")
        print("="*70)

        print("\n[*] Rules by Severity:")
        for severity, count in sorted(
            generator._count_by_severity().items(),
            key=lambda x: x[1],
            reverse=True
        ):
            print(f"  {severity:12s}: {count:3d}")

        print("\n[*] Rules by Category:")
        for category, count in sorted(
            generator._count_by_category().items(),
            key=lambda x: x[1],
            reverse=True
        ):
            print(f"  {category:30s}: {count:3d}")

    print("\n[SUCCESS] Done!")
    return 0


if __name__ == "__main__":
    exit(main())
