#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dependency Graph Generator - Anti-Gaming Module
SSID Phase 1 Implementation

Purpose:
- Parse module dependencies from chart.yaml files
- Generate directed graph representation
- Detect circular dependencies (anti-gaming violation)
- Export graph visualization (SVG) and violations (JSON)

Architecture:
- YAML Parsing → Graph Object → Cycle Detection
- CI Gate: "0 Cycles" → PASS
- Output: dependency_graph.svg + violations.json
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from collections import defaultdict, deque


@dataclass
class DependencyViolation:
    """Represents a circular dependency violation"""
    violation_id: str
    timestamp: str
    severity: str  # always "critical" for circular deps
    violation_type: str
    cycle: List[str]
    description: str

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class GraphAnalysisResult:
    """Result of dependency graph analysis"""
    status: str  # PASS, FAIL
    timestamp: str
    total_modules: int
    total_dependencies: int
    cycles_found: int
    violations: List[DependencyViolation]
    graph_file: Optional[str]
    violations_file: Optional[str]

    def to_dict(self) -> Dict:
        return {
            "status": self.status,
            "timestamp": self.timestamp,
            "total_modules": self.total_modules,
            "total_dependencies": self.total_dependencies,
            "cycles_found": self.cycles_found,
            "violations": [v.to_dict() for v in self.violations],
            "graph_file": self.graph_file,
            "violations_file": self.violations_file
        }


class DependencyGraphGenerator:
    """
    Module dependency graph generator with cycle detection.

    Algorithm:
    1. Scan all chart.yaml files
    2. Extract dependencies.required and dependencies.optional
    3. Build adjacency list representation
    4. Run DFS-based cycle detection
    5. Generate graph visualization (DOT → SVG)
    6. Output violations
    """

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.graph: Dict[str, List[str]] = defaultdict(list)
        self.modules: Set[str] = set()
        self.violations: List[DependencyViolation] = []

    def parse_dependencies(self) -> Dict[str, List[str]]:
        """
        Parse dependencies from all chart.yaml files.

        Returns:
            Dict mapping module_id → list of dependency module_ids
        """
        dependencies_map = {}

        for chart_file in self.repo_root.glob("**/chart.yaml"):
            if ".git" in str(chart_file):
                continue

            try:
                import yaml
                with open(chart_file, 'r', encoding='utf-8') as f:
                    chart_data = yaml.safe_load(f)

                if not chart_data or 'metadata' not in chart_data:
                    continue

                shard_id = chart_data['metadata'].get('shard_id')
                root = chart_data['metadata'].get('root')

                if not shard_id or not root:
                    continue

                module_id = f"{root}::{shard_id}"
                self.modules.add(module_id)

                # Extract dependencies
                deps = chart_data.get('dependencies', {})
                required_deps = deps.get('required', [])
                optional_deps = deps.get('optional', [])

                # Combine required and optional
                all_deps = required_deps + optional_deps

                dep_list = []
                for dep in all_deps:
                    if isinstance(dep, dict):
                        dep_root = dep.get('root')
                        if dep_root:
                            # For root-level dependencies, we need to find shards
                            # For simplicity, use root as dependency
                            dep_list.append(dep_root)
                    elif isinstance(dep, str):
                        dep_list.append(dep)

                dependencies_map[module_id] = dep_list

            except Exception as e:
                print(f"Warning: Failed to parse {chart_file}: {e}", file=sys.stderr)

        # Also parse module.yaml for root-level dependencies
        for module_file in self.repo_root.glob("*/module.yaml"):
            if ".git" in str(module_file):
                continue

            try:
                import yaml
                with open(module_file, 'r', encoding='utf-8') as f:
                    module_data = yaml.safe_load(f)

                if not module_data:
                    continue

                module_name = module_data.get('module')
                if not module_name:
                    continue

                # Infer module root from directory
                root_name = module_file.parent.name

                self.modules.add(root_name)

                # module.yaml files don't typically have dependencies listed
                # but we include them in the module set
                if root_name not in dependencies_map:
                    dependencies_map[root_name] = []

            except Exception as e:
                print(f"Warning: Failed to parse {module_file}: {e}", file=sys.stderr)

        return dependencies_map

    def build_graph(self, dependencies_map: Dict[str, List[str]]) -> None:
        """Build adjacency list representation of dependency graph"""
        for module_id, deps in dependencies_map.items():
            for dep in deps:
                # Normalize dependency references
                # Handle both "root::shard" and "root" formats
                if "::" in dep:
                    dep_normalized = dep
                else:
                    # Root-level dependency
                    dep_normalized = dep

                self.graph[module_id].append(dep_normalized)

    def detect_cycles(self) -> List[List[str]]:
        """
        Detect cycles using DFS with recursion stack tracking.

        Returns:
            List of cycles, where each cycle is a list of module IDs
        """
        visited = set()
        rec_stack = set()
        cycles = []
        path = []

        def dfs(node: str) -> bool:
            """DFS helper that returns True if cycle found"""
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in self.graph.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    # Cycle detected
                    cycle_start_idx = path.index(neighbor)
                    cycle = path[cycle_start_idx:] + [neighbor]
                    cycles.append(cycle)
                    return True

            path.pop()
            rec_stack.remove(node)
            return False

        # Run DFS from all unvisited nodes
        for node in self.modules:
            if node not in visited:
                dfs(node)

        return cycles

    def find_all_cycles_tarjan(self) -> List[List[str]]:
        """
        Find all cycles using Tarjan's algorithm for strongly connected components.

        This is more thorough than basic DFS and finds all cycles, not just one.
        """
        index_counter = [0]
        stack = []
        lowlinks = {}
        index = {}
        on_stack = set()
        sccs = []

        def strongconnect(node: str):
            index[node] = index_counter[0]
            lowlinks[node] = index_counter[0]
            index_counter[0] += 1
            stack.append(node)
            on_stack.add(node)

            for neighbor in self.graph.get(node, []):
                if neighbor not in index:
                    strongconnect(neighbor)
                    lowlinks[node] = min(lowlinks[node], lowlinks[neighbor])
                elif neighbor in on_stack:
                    lowlinks[node] = min(lowlinks[node], index[neighbor])

            if lowlinks[node] == index[node]:
                component = []
                while True:
                    w = stack.pop()
                    on_stack.remove(w)
                    component.append(w)
                    if w == node:
                        break
                # Only report SCCs with more than 1 node (actual cycles)
                if len(component) > 1:
                    sccs.append(component)

        for node in self.modules:
            if node not in index:
                strongconnect(node)

        return sccs

    def generate_violations(self, cycles: List[List[str]]) -> None:
        """Generate violation objects from detected cycles"""
        for idx, cycle in enumerate(cycles):
            violation = DependencyViolation(
                violation_id=f"CDV-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{idx:04d}",
                timestamp=datetime.now(timezone.utc).isoformat(),
                severity="critical",
                violation_type="circular_dependency",
                cycle=cycle,
                description=f"Circular dependency detected: {' → '.join(cycle)}"
            )
            self.violations.append(violation)

    def export_graph_dot(self, output_file: Path) -> None:
        """Export graph in DOT format for visualization"""
        dot_content = ["digraph DependencyGraph {"]
        dot_content.append('  rankdir=LR;')
        dot_content.append('  node [shape=box, style=rounded];')

        # Add nodes
        for module in self.modules:
            # Color code by root
            if "::" in module:
                root = module.split("::")[0]
                color = self._get_color_for_root(root)
            else:
                color = "#lightgray"

            dot_content.append(f'  "{module}" [fillcolor="{color}", style="rounded,filled"];')

        # Add edges
        for source, targets in self.graph.items():
            for target in targets:
                dot_content.append(f'  "{source}" -> "{target}";')

        # Highlight cycles
        if self.violations:
            for violation in self.violations:
                cycle = violation.cycle
                for i in range(len(cycle) - 1):
                    dot_content.append(f'  "{cycle[i]}" -> "{cycle[i+1]}" [color=red, penwidth=2.0];')

        dot_content.append("}")

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(dot_content))

    def _get_color_for_root(self, root: str) -> str:
        """Get a consistent color for each root module"""
        # Simple hash-based color assignment
        colors = [
            "#FFE6E6", "#E6F3FF", "#E6FFE6", "#FFF0E6", "#F0E6FF",
            "#FFFFE6", "#E6FFFF", "#FFE6F0", "#F0FFE6", "#E6E6FF"
        ]
        return colors[hash(root) % len(colors)]

    def run_analysis(self) -> GraphAnalysisResult:
        """Execute full dependency graph analysis"""
        timestamp = datetime.now(timezone.utc).isoformat()

        # Step 1: Parse dependencies
        dependencies_map = self.parse_dependencies()

        # Step 2: Build graph
        self.build_graph(dependencies_map)

        # Step 3: Detect cycles
        cycles = self.find_all_cycles_tarjan()

        # Step 4: Generate violations
        self.generate_violations(cycles)

        # Step 5: Export graph
        output_dir = self.repo_root / "23_compliance" / "anti_gaming" / "graphs"
        output_dir.mkdir(parents=True, exist_ok=True)

        graph_dot_file = output_dir / "dependency_graph.dot"
        self.export_graph_dot(graph_dot_file)

        # Try to convert DOT to SVG if graphviz is available
        graph_svg_file = output_dir / "dependency_graph.svg"
        try:
            import subprocess
            subprocess.run(
                ["dot", "-Tsvg", str(graph_dot_file), "-o", str(graph_svg_file)],
                check=True,
                capture_output=True
            )
        except (FileNotFoundError, subprocess.CalledProcessError):
            print("Warning: graphviz 'dot' command not found. Skipping SVG generation.", file=sys.stderr)
            print(f"DOT file saved at: {graph_dot_file}", file=sys.stderr)
            graph_svg_file = None

        # Step 6: Export violations
        violations_file = output_dir / f"dependency_violations_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"

        # Calculate stats
        total_deps = sum(len(deps) for deps in self.graph.values())

        # Determine status
        status = "PASS" if len(cycles) == 0 else "FAIL"

        result = GraphAnalysisResult(
            status=status,
            timestamp=timestamp,
            total_modules=len(self.modules),
            total_dependencies=total_deps,
            cycles_found=len(cycles),
            violations=self.violations,
            graph_file=str(graph_svg_file) if graph_svg_file else str(graph_dot_file),
            violations_file=str(violations_file)
        )

        # Write violations
        with open(violations_file, 'w', encoding='utf-8') as f:
            json.dump(result.to_dict(), f, indent=2)

        # Step 7: Version the graph (Phase 2 integration)
        try:
            sys.path.insert(0, str(self.repo_root / "24_meta_orchestration" / "registry" / "logs"))
            from dependency_graph_versioning import DependencyGraphVersioning

            versioning = DependencyGraphVersioning(self.repo_root)

            # Prepare file paths
            graph_files = {
                "dot": graph_dot_file
            }
            if graph_svg_file and graph_svg_file.exists():
                graph_files["svg"] = graph_svg_file

            # Create version
            version = versioning.create_version(
                graph=dict(self.graph),
                modules=list(self.modules),
                cycles=cycles,
                graph_files=graph_files,
                metadata={
                    "total_modules": len(self.modules),
                    "total_dependencies": total_deps,
                    "cycles_found": len(cycles),
                    "status": status,
                    "analysis_timestamp": timestamp
                }
            )

            print(f"Graph versioned: {version.version_id}", file=sys.stderr)

        except Exception as e:
            # Don't fail the analysis if versioning fails
            print(f"Warning: Failed to version graph: {e}", file=sys.stderr)

        return result


def main():
    """CLI entry point"""
    # Find repo root
    repo_root = Path(__file__).resolve().parents[2]

    # Run analysis
    generator = DependencyGraphGenerator(repo_root)
    result = generator.run_analysis()

    # Output results
    print(json.dumps(result.to_dict(), indent=2))

    # Exit with appropriate code
    if result.status == "FAIL":
        print(f"\nERROR: {result.cycles_found} circular dependencies detected!", file=sys.stderr)
        sys.exit(1)
    else:
        print(f"\nSUCCESS: No circular dependencies found.", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
