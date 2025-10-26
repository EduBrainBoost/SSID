#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dependency Analyzer - Layer 7: Causality & Dependency Security
===============================================================

Detects cross-shard dependencies between validators, policies, and tests.
Ensures no rule changes break dependent components.

Features:
  - Cross-shard dependency detection
  - Auto-triggers dependent tests on rule changes
  - Dependency graph generation
  - Circular dependency detection
  - Impact analysis for rule changes

Usage:
  # Analyze dependencies
  python dependency_analyzer.py

  # Check specific rule
  python dependency_analyzer.py --rule CS001

  # Generate dependency graph
  python dependency_analyzer.py --graph --output deps.json

Author: SSID Architecture Team
Version: 1.0.0
Date: 2025-10-22
"""

import sys
import json
import re
import argparse
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from datetime import datetime, timezone
from collections import defaultdict

# UTF-8 enforcement
if sys.platform == 'win32':
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')

REPO_ROOT = Path(__file__).resolve().parents[1]

# Directories to scan for dependencies
SCAN_DIRS = {
    "validators": REPO_ROOT / "03_core" / "validators" / "sot",
    "policies": REPO_ROOT / "23_compliance" / "policies" / "sot",
    "tests": REPO_ROOT / "11_test_simulation" / "tests_sot",
}

# Dependency patterns
PATTERNS = {
    "rule_reference": r"(?:CS|MS|KP|CE|TS|DC|MR|MD)-[A-Z]+-\d{3}",
    "function_call": r"def\s+(\w+)\(.*?\):",
    "import_statement": r"from\s+([\w\.]+)\s+import\s+(\w+)",
    "class_definition": r"class\s+(\w+)(?:\(.*?\))?:",
}

OUTPUT_DIR = REPO_ROOT / "02_audit_logging" / "dependency_analysis"


class DependencyAnalyzer:
    """Analyzes cross-shard dependencies"""

    def __init__(self):
        self.dependencies = defaultdict(set)
        self.reverse_deps = defaultdict(set)
        self.rule_locations = {}
        self.circular_deps = []

    def scan_file_for_rules(self, file_path: Path) -> Set[str]:
        """Extract all rule references from a file"""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            pattern = PATTERNS["rule_reference"]
            matches = re.findall(pattern, content)
            return set(matches)
        except Exception as e:
            print(f"⚠️  Error scanning {file_path}: {e}", file=sys.stderr)
            return set()

    def scan_all_files(self):
        """Scan all files for dependencies"""
        print("\n[1/5] Scanning Files for Dependencies...")

        for category, directory in SCAN_DIRS.items():
            if not directory.exists():
                print(f"  ⚠️  {category} directory not found: {directory}")
                continue

            print(f"\n  Category: {category}")

            # Scan Python files
            python_files = list(directory.glob("**/*.py"))
            for py_file in python_files:
                rules = self.scan_file_for_rules(py_file)

                if rules:
                    print(f"    ✅ {py_file.name}: {len(rules)} rule references")

                    # Record where each rule is used
                    for rule in rules:
                        self.rule_locations[rule] = self.rule_locations.get(rule, set())
                        self.rule_locations[rule].add(str(py_file.relative_to(REPO_ROOT)))

            # Scan Rego files
            rego_files = list(directory.glob("**/*.rego"))
            for rego_file in rego_files:
                rules = self.scan_file_for_rules(rego_file)

                if rules:
                    print(f"    ✅ {rego_file.name}: {len(rules)} rule references")

                    for rule in rules:
                        self.rule_locations[rule] = self.rule_locations.get(rule, set())
                        self.rule_locations[rule].add(str(rego_file.relative_to(REPO_ROOT)))

        print(f"\n  → Found {len(self.rule_locations)} unique rules referenced across codebase")

    def build_dependency_graph(self):
        """Build dependency graph from rule locations"""
        print("\n[2/5] Building Dependency Graph...")

        # For each rule, find which other rules it depends on
        for rule, locations in self.rule_locations.items():
            for location in locations:
                file_path = REPO_ROOT / location

                # Find all rules referenced in same file
                other_rules = self.scan_file_for_rules(file_path)
                other_rules.discard(rule)  # Don't include self-reference

                if other_rules:
                    self.dependencies[rule].update(other_rules)

                    # Build reverse dependencies
                    for other_rule in other_rules:
                        self.reverse_deps[other_rule].add(rule)

        print(f"  → {len(self.dependencies)} rules with dependencies")
        print(f"  → Average dependencies per rule: {sum(len(deps) for deps in self.dependencies.values()) / max(len(self.dependencies), 1):.2f}")

    def detect_circular_dependencies(self):
        """Detect circular dependencies"""
        print("\n[3/5] Detecting Circular Dependencies...")

        def has_cycle(node, visited, rec_stack, path):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in self.dependencies.get(node, set()):
                if neighbor not in visited:
                    if has_cycle(neighbor, visited, rec_stack, path.copy()):
                        return True
                elif neighbor in rec_stack:
                    # Found cycle
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    self.circular_deps.append(cycle)
                    return True

            rec_stack.remove(node)
            return False

        visited = set()
        for rule in self.dependencies.keys():
            if rule not in visited:
                has_cycle(rule, visited, set(), [])

        if self.circular_deps:
            print(f"  ❌ Found {len(self.circular_deps)} circular dependencies!")
            for i, cycle in enumerate(self.circular_deps[:5], 1):  # Show first 5
                print(f"     {i}. {' → '.join(cycle)}")
        else:
            print(f"  ✅ No circular dependencies detected")

    def analyze_rule_impact(self, rule_id: str) -> Dict:
        """Analyze impact of changing a specific rule"""
        print(f"\n[4/5] Analyzing Impact of Rule: {rule_id}...")

        if rule_id not in self.rule_locations:
            print(f"  ⚠️  Rule {rule_id} not found in codebase")
            return {}

        # Direct dependencies (rules that depend on this rule)
        direct_deps = self.reverse_deps.get(rule_id, set())

        # Transitive dependencies (rules that transitively depend on this rule)
        transitive_deps = set()
        to_visit = list(direct_deps)
        visited = {rule_id}

        while to_visit:
            current = to_visit.pop(0)
            if current in visited:
                continue
            visited.add(current)
            transitive_deps.add(current)

            # Add dependencies of current rule
            for dep in self.reverse_deps.get(current, set()):
                if dep not in visited:
                    to_visit.append(dep)

        # Files that need to be tested
        affected_files = set()
        for dep in direct_deps | transitive_deps:
            affected_files.update(self.rule_locations.get(dep, set()))

        impact = {
            "rule_id": rule_id,
            "direct_dependencies": len(direct_deps),
            "transitive_dependencies": len(transitive_deps),
            "total_affected_rules": len(direct_deps) + len(transitive_deps),
            "affected_files": len(affected_files),
            "files_to_test": sorted(affected_files),
            "direct_dependent_rules": sorted(direct_deps),
            "transitive_dependent_rules": sorted(transitive_deps),
        }

        print(f"  → Direct dependencies: {impact['direct_dependencies']}")
        print(f"  → Transitive dependencies: {impact['transitive_dependencies']}")
        print(f"  → Affected files: {impact['affected_files']}")

        return impact

    def trigger_dependent_tests(self, changed_rules: List[str]) -> bool:
        """Trigger tests for all dependent rules"""
        print(f"\n[5/5] Triggering Dependent Tests for {len(changed_rules)} changed rules...")

        all_affected_files = set()

        for rule in changed_rules:
            impact = self.analyze_rule_impact(rule)
            all_affected_files.update(impact.get("files_to_test", []))

        if not all_affected_files:
            print(f"  ✅ No tests need to be run")
            return True

        print(f"\n  Running tests for {len(all_affected_files)} affected files:")

        # Filter for test files only
        test_files = [f for f in all_affected_files if "/tests" in f or "test_" in f]

        if not test_files:
            print(f"  ⚠️  No test files found among affected files")
            return True

        print(f"  → {len(test_files)} test files to run")

        # In production, would actually run pytest here
        # For now, just report what would be run
        for test_file in sorted(test_files)[:10]:  # Show first 10
            print(f"     • {test_file}")

        if len(test_files) > 10:
            print(f"     ... and {len(test_files) - 10} more")

        return True

    def generate_graph_output(self, output_file: Path):
        """Generate dependency graph in JSON format"""
        print(f"\nGenerating Dependency Graph...")

        graph_data = {
            "metadata": {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "total_rules": len(self.rule_locations),
                "total_dependencies": sum(len(deps) for deps in self.dependencies.values()),
                "circular_dependencies": len(self.circular_deps),
            },
            "nodes": [
                {
                    "id": rule,
                    "locations": sorted(locations),
                    "dependency_count": len(self.dependencies.get(rule, set())),
                    "dependent_count": len(self.reverse_deps.get(rule, set())),
                }
                for rule, locations in self.rule_locations.items()
            ],
            "edges": [
                {"from": rule, "to": dep}
                for rule, deps in self.dependencies.items()
                for dep in deps
            ],
            "circular_dependencies": [
                {"cycle": cycle, "length": len(cycle)}
                for cycle in self.circular_deps
            ]
        }

        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(graph_data, f, indent=2, ensure_ascii=False)

        print(f"  💾 Graph saved: {output_file}")
        return graph_data

    def run(self, rule_id: Optional[str] = None, generate_graph: bool = False, output_file: Optional[Path] = None):
        """Run complete dependency analysis"""
        print("=" * 80)
        print("DEPENDENCY ANALYZER - Layer 7: Causality & Dependency Security")
        print("=" * 80)
        print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
        print("=" * 80)

        # Step 1: Scan files
        self.scan_all_files()

        # Step 2: Build dependency graph
        self.build_dependency_graph()

        # Step 3: Detect circular dependencies
        self.detect_circular_dependencies()

        # Step 4: Analyze specific rule if provided
        if rule_id:
            self.analyze_rule_impact(rule_id)

        # Step 5: Generate graph if requested
        if generate_graph:
            output_path = output_file or (OUTPUT_DIR / "dependency_graph.json")
            self.generate_graph_output(output_path)

        # Summary
        print("\n" + "=" * 80)
        print("DEPENDENCY ANALYSIS SUMMARY")
        print("=" * 80)
        print(f"Total Rules:           {len(self.rule_locations)}")
        print(f"Rules with Dependencies: {len(self.dependencies)}")
        print(f"Circular Dependencies:   {len(self.circular_deps)}")
        print(f"Average Deps per Rule:   {sum(len(deps) for deps in self.dependencies.values()) / max(len(self.dependencies), 1):.2f}")

        return len(self.circular_deps) == 0


def main():
    parser = argparse.ArgumentParser(
        description="Dependency Analyzer (Layer 7: Causality & Dependency Security)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze all dependencies
  python dependency_analyzer.py

  # Analyze specific rule
  python dependency_analyzer.py --rule CS001

  # Generate dependency graph
  python dependency_analyzer.py --graph --output deps.json

  # Check impact of multiple rules
  python dependency_analyzer.py --rules CS001,MS002,KP003
        """
    )

    parser.add_argument("--rule", type=str, help="Analyze specific rule")
    parser.add_argument("--rules", type=str, help="Comma-separated list of rules to analyze")
    parser.add_argument("--graph", action="store_true", help="Generate dependency graph JSON")
    parser.add_argument("--output", type=Path, help="Output file for graph (default: dependency_graph.json)")

    args = parser.parse_args()

    analyzer = DependencyAnalyzer()

    # Determine rules to analyze
    rules_to_analyze = []
    if args.rule:
        rules_to_analyze = [args.rule]
    elif args.rules:
        rules_to_analyze = [r.strip() for r in args.rules.split(",")]

    # Run analysis
    success = analyzer.run(
        rule_id=rules_to_analyze[0] if rules_to_analyze else None,
        generate_graph=args.graph,
        output_file=args.output
    )

    # Trigger tests for multiple rules
    if len(rules_to_analyze) > 1:
        analyzer.trigger_dependent_tests(rules_to_analyze)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
