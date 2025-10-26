#!/usr/bin/env python3
"""
Create traceability matrix mapping documentation rules to semantic validators
"""

import json
import re
from pathlib import Path
from datetime import datetime

class TraceabilityMatrix:
    def __init__(self):
        self.unified_rules = None
        self.matrix = {}

    def load_unified_rules(self):
        """Load unified rule set"""
        unified_file = Path('24_meta_orchestration/registry/UNIFIED_RULE_SET.json')
        data = json.loads(unified_file.read_text(encoding='utf-8'))
        self.unified_rules = data['rules']
        print(f"[OK] Loaded {len(self.unified_rules)} unified rules")

    def extract_keywords(self, text):
        """Extract keywords from rule content"""
        if not text:
            return []

        keywords = []

        # Common structural keywords
        structural = ['root', 'shard', 'folder', 'directory', 'structure',
                     'level', 'depth', 'naming', 'pattern']
        for kw in structural:
            if kw.lower() in text.lower():
                keywords.append(kw)

        # Compliance keywords
        compliance = ['gdpr', 'compliance', 'audit', 'policy', 'legal',
                     'regulation', 'mandatory', 'forbidden', 'required']
        for kw in compliance:
            if kw.lower() in text.lower():
                keywords.append(kw)

        # Technical keywords
        technical = ['hash', 'crypto', 'validation', 'check', 'verify',
                    'test', 'enforce', 'guard']
        for kw in technical:
            if kw.lower() in text.lower():
                keywords.append(kw)

        return list(set(keywords))

    def create_mapping(self):
        """Create mapping between documentation and semantic rules"""
        print()
        print("Creating traceability mappings...")
        print()

        doc_rules = {}
        sem_rules = {}

        # Separate rules by category
        for rule_id, rule in self.unified_rules.items():
            if rule['category'] == 'documentation':
                doc_rules[rule_id] = rule
            else:
                sem_rules[rule_id] = rule

        print(f"Documentation rules: {len(doc_rules)}")
        print(f"Semantic rules: {len(sem_rules)}")
        print()

        # Create mappings based on keywords
        for doc_id, doc_rule in doc_rules.items():
            content = doc_rule.get('content', '')
            doc_keywords = self.extract_keywords(content)

            self.matrix[doc_id] = {
                'doc_rule': {
                    'id': doc_id,
                    'type': doc_rule['type'],
                    'priority': doc_rule['priority'],
                    'source_file': doc_rule['source_file'],
                    'line_number': doc_rule.get('line_number', 0),
                    'content_preview': content[:100] if content else ''
                },
                'keywords': doc_keywords,
                'semantic_validators': [],
                'mapping_confidence': 'keyword-based'
            }

            # For high-value documentation rules, note potential validators
            if doc_rule['priority'] in ['MUST', 'REQUIRED', 'CRITICAL', 'FORBIDDEN']:
                # These should definitely have validators
                self.matrix[doc_id]['requires_validator'] = True
            else:
                self.matrix[doc_id]['requires_validator'] = False

        print(f"[OK] Created {len(self.matrix)} traceability entries")
        print()

    def analyze_coverage(self):
        """Analyze which doc rules have validators"""
        stats = {
            'total_doc_rules': len(self.matrix),
            'must_have_rules': 0,
            'structural_rules': 0,
            'enforcement_rules': 0,
            'with_validators': 0,
            'missing_validators': []
        }

        for doc_id, entry in self.matrix.items():
            if entry['requires_validator']:
                stats['must_have_rules'] += 1

            if entry['doc_rule']['priority'] == 'STRUCTURAL':
                stats['structural_rules'] += 1

            if entry['doc_rule']['priority'] in ['ENFORCEMENT', 'CRITICAL', 'FORBIDDEN']:
                stats['enforcement_rules'] += 1

            # Check if it has keywords suggesting it needs validators
            if 'validation' in entry['keywords'] or 'check' in entry['keywords']:
                if entry['requires_validator']:
                    stats['missing_validators'].append(doc_id)

        print("COVERAGE ANALYSIS:")
        print(f"  Total documentation rules: {stats['total_doc_rules']}")
        print(f"  MUST/REQUIRED/CRITICAL rules: {stats['must_have_rules']}")
        print(f"  Enforcement rules: {stats['enforcement_rules']}")
        print(f"  Structural rules: {stats['structural_rules']}")
        print()

        return stats

    def save_matrix(self):
        """Save traceability matrix"""
        output = {
            'metadata': {
                'generated_date': datetime.now().isoformat(),
                'total_entries': len(self.matrix),
                'version': '1.0.0'
            },
            'traceability_matrix': self.matrix,
            'statistics': self.analyze_coverage()
        }

        output_file = Path('24_meta_orchestration/registry/TRACEABILITY_MATRIX.json')
        output_file.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding='utf-8')
        print(f"[OK] Saved traceability matrix to: {output_file}")
        print()

        return output_file

def main():
    print("="*70)
    print("CREATING TRACEABILITY MATRIX")
    print("="*70)
    print()

    matrix = TraceabilityMatrix()
    matrix.load_unified_rules()
    matrix.create_mapping()
    stats = matrix.analyze_coverage()
    output_file = matrix.save_matrix()

    print("="*70)
    print("TRACEABILITY MATRIX COMPLETE")
    print("="*70)
    print(f"Saved to: {output_file}")
    print()

if __name__ == '__main__':
    main()
