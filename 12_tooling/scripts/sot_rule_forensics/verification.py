"""
Layer 16-17: Zyklische Konsistenzprüfung & Deprecation-Handling
================================================================

Bidirectional reference checking and deprecated rule handling
Version: 3.0.0
"""

from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class DeprecatedRule:
    """Deprecated rule information"""
    rule_id: str
    deprecated_date: datetime
    replacement_id: Optional[str] = None
    reason: str = ""

class CyclicVerification:
    """Cyclic consistency verification"""

    def __init__(self):
        self.forward_refs: Dict[str, Set[str]] = {}
        self.backward_refs: Dict[str, Set[str]] = {}

    def add_reference(self, source: str, target: str):
        """Add bidirectional reference"""
        if source not in self.forward_refs:
            self.forward_refs[source] = set()
        self.forward_refs[source].add(target)

        if target not in self.backward_refs:
            self.backward_refs[target] = set()
        self.backward_refs[target].add(source)

    def verify_consistency(self) -> bool:
        """Verify bidirectional consistency"""
        for source, targets in self.forward_refs.items():
            for target in targets:
                if target not in self.backward_refs:
                    return False
                if source not in self.backward_refs[target]:
                    return False
        return True

    def detect_cycles(self) -> List[List[str]]:
        """Detect cyclic dependencies"""
        cycles = []
        visited = set()

        def dfs(node, path):
            if node in path:
                cycle_start = path.index(node)
                cycles.append(path[cycle_start:])
                return
            if node in visited:
                return

            visited.add(node)
            path.append(node)

            for neighbor in self.forward_refs.get(node, []):
                dfs(neighbor, path.copy())

        for node in self.forward_refs:
            dfs(node, [])

        return cycles

    def self_verify(self) -> Tuple[bool, List[str]]:
        """Self-verification"""
        issues = []

        if not self.verify_consistency():
            issues.append("Bidirectional consistency check failed")

        cycles = self.detect_cycles()
        if cycles:
            issues.append(f"Detected {len(cycles)} cyclic dependencies")

        return len(issues) == 0, issues


class DeprecationHandler:
    """Handle deprecated rules"""

    def __init__(self):
        self.deprecated_rules: Dict[str, DeprecatedRule] = {}

    def mark_deprecated(self, rule_id: str, replacement_id: Optional[str] = None,
                       reason: str = ""):
        """Mark rule as deprecated"""
        self.deprecated_rules[rule_id] = DeprecatedRule(
            rule_id=rule_id,
            deprecated_date=datetime.now(),
            replacement_id=replacement_id,
            reason=reason
        )

    def is_deprecated(self, rule_id: str) -> bool:
        """Check if rule is deprecated"""
        return rule_id in self.deprecated_rules

    def get_replacement(self, rule_id: str) -> Optional[str]:
        """Get replacement rule ID"""
        if rule_id in self.deprecated_rules:
            return self.deprecated_rules[rule_id].replacement_id
        return None

    def self_verify(self) -> Tuple[bool, List[str]]:
        """Self-verification"""
        issues = []

        # Check for circular deprecation
        for rule_id, dep_rule in self.deprecated_rules.items():
            if dep_rule.replacement_id == rule_id:
                issues.append(f"Circular deprecation: {rule_id}")

        return len(issues) == 0, issues
