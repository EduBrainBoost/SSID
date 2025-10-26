"""
Layer 8: Cross-Referenz-Index
=============================

Cross-reference indexing with SQLite/JSON storage
Tracks all rule references and relationships

Version: 3.0.0
"""

from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import json
import hashlib


@dataclass
class CrossReference:
    """Cross-reference between rules"""
    source_rule_id: str
    target_rule_id: str
    reference_type: str  # 'extends', 'imports', 'requires', 'related'
    strength: float = 1.0  # 0.0-1.0


class CrossReferenceIndex:
    """Cross-reference index for rule tracking"""

    def __init__(self, index_file: Optional[Path] = None):
        self.index_file = index_file or Path("rule_cross_reference.json")
        self.references: List[CrossReference] = []
        self.rule_graph: Dict[str, Set[str]] = {}
        self.reverse_graph: Dict[str, Set[str]] = {}

    def add_reference(self, source: str, target: str, ref_type: str = 'related',
                     strength: float = 1.0):
        """Add cross-reference"""
        ref = CrossReference(source, target, ref_type, strength)
        self.references.append(ref)

        # Update forward graph
        if source not in self.rule_graph:
            self.rule_graph[source] = set()
        self.rule_graph[source].add(target)

        # Update reverse graph
        if target not in self.reverse_graph:
            self.reverse_graph[target] = set()
        self.reverse_graph[target].add(source)

    def get_references_from(self, rule_id: str) -> List[str]:
        """Get all rules referenced by this rule"""
        return list(self.rule_graph.get(rule_id, set()))

    def get_references_to(self, rule_id: str) -> List[str]:
        """Get all rules referencing this rule"""
        return list(self.reverse_graph.get(rule_id, set()))

    def save_index(self):
        """Save index to JSON"""
        data = {
            'references': [
                {
                    'source': ref.source_rule_id,
                    'target': ref.target_rule_id,
                    'type': ref.reference_type,
                    'strength': ref.strength
                }
                for ref in self.references
            ],
            'metadata': {
                'total_references': len(self.references),
                'total_rules': len(set(self.rule_graph.keys()) | set(self.reverse_graph.keys()))
            }
        }

        with open(self.index_file, 'w') as f:
            json.dump(data, f, indent=2)

    def load_index(self):
        """Load index from JSON"""
        if self.index_file.exists():
            with open(self.index_file, 'r') as f:
                data = json.load(f)

            self.references = []
            for ref_data in data.get('references', []):
                self.add_reference(
                    ref_data['source'],
                    ref_data['target'],
                    ref_data['type'],
                    ref_data['strength']
                )

    def self_verify(self) -> Tuple[bool, List[str]]:
        """Self-verification"""
        issues = []

        # Check for orphaned references
        all_rules = set(self.rule_graph.keys()) | set(self.reverse_graph.keys())
        for ref in self.references:
            if ref.source_rule_id not in all_rules:
                issues.append(f"Orphaned source: {ref.source_rule_id}")
            if ref.target_rule_id not in all_rules:
                issues.append(f"Orphaned target: {ref.target_rule_id}")

        return len(issues) == 0, issues
