#!/usr/bin/env python3
"""
INTEGRATION: Merge 586 manual documentation rules with 4,723 semantic rules
Creates unified rule set and generates updated artefacts
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime

class RuleIntegrator:
    def __init__(self):
        self.manual_primary = None
        self.manual_inline = None
        self.semantic_rules = None
        self.unified_rules = {}

    def load_all_sources(self):
        """Load all rule sources"""
        print("="*70)
        print("LOADING ALL RULE SOURCES")
        print("="*70)
        print()

        # Load manual extraction (primary)
        manual_primary_file = Path('02_audit_logging/reports/COMPLETE_MANUAL_EXTRACTION_4_MASTER_FILES.json')
        self.manual_primary = json.loads(manual_primary_file.read_text(encoding='utf-8'))
        print(f"[OK] Loaded manual primary: {len(self.manual_primary['rules'])} rules")

        # Load inline supplement
        manual_inline_file = Path('02_audit_logging/reports/INLINE_RULES_SUPPLEMENT.json')
        self.manual_inline = json.loads(manual_inline_file.read_text(encoding='utf-8'))
        print(f"[OK] Loaded inline supplement: {len(self.manual_inline['inline_rules'])} rules")

        # Load semantic rules
        semantic_file = Path('16_codex/structure/level3/all_4_sot_semantic_rules.json')
        self.semantic_rules = json.loads(semantic_file.read_text(encoding='utf-8'))

        if isinstance(self.semantic_rules, list):
            semantic_count = len(self.semantic_rules)
        elif isinstance(self.semantic_rules, dict) and 'rules' in self.semantic_rules:
            semantic_count = len(self.semantic_rules['rules'])
        else:
            semantic_count = len(self.semantic_rules)

        print(f"[OK] Loaded semantic rules: {semantic_count} rules")
        print()

    def create_unified_rule_set(self):
        """Merge all rules into unified set with proper categorization"""
        print("="*70)
        print("CREATING UNIFIED RULE SET")
        print("="*70)
        print()

        # Add manual primary rules
        for rule in self.manual_primary['rules']:
            unified_id = f"DOC-{rule['rule_id']}"
            self.unified_rules[unified_id] = {
                'unified_id': unified_id,
                'original_id': rule['rule_id'],
                'source': 'manual_extraction_primary',
                'source_file': rule['source_file'],
                'line_number': rule.get('line_number', 0),
                'type': rule['type'],
                'category': 'documentation',
                'priority': rule['priority'],
                'content': rule.get('content', ''),
                'extracted_date': self.manual_primary['metadata']['extraction_date']
            }

        print(f"[OK] Added {len(self.manual_primary['rules'])} documentation rules (primary)")

        # Add inline supplement rules
        for rule in self.manual_inline['inline_rules']:
            unified_id = f"DOC-{rule['rule_id']}"
            self.unified_rules[unified_id] = {
                'unified_id': unified_id,
                'original_id': rule['rule_id'],
                'source': 'manual_extraction_inline',
                'source_file': rule['source_file'],
                'line_number': rule.get('line_number', 0),
                'type': rule['type'],
                'category': 'documentation',
                'priority': rule['priority'],
                'content': rule.get('content', ''),
                'keyword': rule.get('keyword', ''),
                'extracted_date': self.manual_inline['metadata']['extraction_date']
            }

        print(f"[OK] Added {len(self.manual_inline['inline_rules'])} documentation rules (inline)")

        # Add semantic rules
        if isinstance(self.semantic_rules, list):
            semantic_list = self.semantic_rules
        elif isinstance(self.semantic_rules, dict) and 'rules' in self.semantic_rules:
            rules_data = self.semantic_rules['rules']
            if isinstance(rules_data, list):
                semantic_list = rules_data
            else:
                semantic_list = [{'id': k, **v} for k, v in rules_data.items()]
        else:
            semantic_list = [{'id': k, **v} for k, v in self.semantic_rules.items()]

        for i, rule in enumerate(semantic_list):
            if isinstance(rule, dict):
                rule_id = rule.get('id', f'RULE-{i:04d}')
                unified_id = f"SEM-{rule_id}"

                self.unified_rules[unified_id] = {
                    'unified_id': unified_id,
                    'original_id': rule_id,
                    'source': 'semantic_extraction',
                    'category': 'semantic',
                    'priority': 'VALIDATOR',
                    'rule_data': rule
                }

        print(f"[OK] Added {len(semantic_list)} semantic rules")
        print()

        total = len(self.unified_rules)
        print(f"[OK] Total unified rules: {total}")
        print()

        return total

    def generate_statistics(self):
        """Generate statistics about unified rule set"""
        print("="*70)
        print("UNIFIED RULE SET STATISTICS")
        print("="*70)
        print()

        stats = {
            'total_rules': len(self.unified_rules),
            'by_category': {},
            'by_source': {},
            'by_priority': {},
            'documentation_types': {},
            'semantic_count': 0,
            'documentation_count': 0
        }

        for rule_id, rule in self.unified_rules.items():
            # By category
            category = rule['category']
            stats['by_category'][category] = stats['by_category'].get(category, 0) + 1

            # By source
            source = rule['source']
            stats['by_source'][source] = stats['by_source'].get(source, 0) + 1

            # By priority
            priority = rule['priority']
            stats['by_priority'][priority] = stats['by_priority'].get(priority, 0) + 1

            # Count types
            if category == 'documentation':
                stats['documentation_count'] += 1
                doc_type = rule['type']
                stats['documentation_types'][doc_type] = stats['documentation_types'].get(doc_type, 0) + 1
            else:
                stats['semantic_count'] += 1

        print(f"Total Rules: {stats['total_rules']}")
        print()

        print("By Category:")
        for cat, count in sorted(stats['by_category'].items()):
            print(f"  {cat}: {count}")
        print()

        print("By Source:")
        for src, count in sorted(stats['by_source'].items()):
            print(f"  {src}: {count}")
        print()

        print("Documentation Rule Types (Top 10):")
        for dtype, count in sorted(stats['documentation_types'].items(), key=lambda x: -x[1])[:10]:
            print(f"  {dtype}: {count}")
        print()

        return stats

    def save_unified_rule_set(self):
        """Save unified rule set to file"""
        output = {
            'metadata': {
                'integration_date': datetime.now().isoformat(),
                'total_rules': len(self.unified_rules),
                'documentation_rules': 586,
                'semantic_rules': 4723,
                'version': '1.0.0-UNIFIED'
            },
            'rules': self.unified_rules,
            'statistics': self.generate_statistics()
        }

        output_file = Path('24_meta_orchestration/registry/UNIFIED_RULE_SET.json')
        output_file.parent.mkdir(parents=True, exist_ok=True)

        output_file.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding='utf-8')
        print(f"[OK] Saved unified rule set to: {output_file}")
        print()

        # Also save a hash manifest
        rule_hash = hashlib.sha256(json.dumps(self.unified_rules, sort_keys=True).encode()).hexdigest()

        manifest = {
            'unified_rule_set_hash': rule_hash,
            'total_rules': len(self.unified_rules),
            'timestamp': datetime.now().isoformat(),
            'sources': {
                'manual_primary': len(self.manual_primary['rules']),
                'manual_inline': len(self.manual_inline['inline_rules']),
                'semantic': 4723
            }
        }

        manifest_file = Path('24_meta_orchestration/registry/unified_rule_manifest.json')
        manifest_file.write_text(json.dumps(manifest, indent=2), encoding='utf-8')
        print(f"[OK] Saved manifest to: {manifest_file}")
        print()

        return output_file

def main():
    print("="*70)
    print("INTEGRATION: 586 Documentation Rules + 4,723 Semantic Rules")
    print("="*70)
    print()

    integrator = RuleIntegrator()

    # Step 1: Load all sources
    integrator.load_all_sources()

    # Step 2: Create unified rule set
    total = integrator.create_unified_rule_set()

    # Step 3: Generate statistics
    stats = integrator.generate_statistics()

    # Step 4: Save unified rule set
    output_file = integrator.save_unified_rule_set()

    print("="*70)
    print("INTEGRATION COMPLETE")
    print("="*70)
    print(f"Total unified rules: {total}")
    print(f"  - Documentation: {stats['documentation_count']}")
    print(f"  - Semantic: {stats['semantic_count']}")
    print()
    print(f"Unified rule set saved to: {output_file}")
    print()
    print("Next Steps:")
    print("  1. Generate updated artefacts from unified set")
    print("  2. Create traceability matrix")
    print("  3. Export documentation to 05_documentation/")
    print()

if __name__ == '__main__':
    main()
