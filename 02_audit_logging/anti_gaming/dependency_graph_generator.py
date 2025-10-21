#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
dependency_graph_generator.py – Deterministic Dependency Graph Builder
Autor: edubrainboost ©2025 MIT License

Builds deterministic import dependency graph (nodes + edges) with SHA-256 hash.
Read-only scan, outputs JSON graph and JSONL audit log.

Exit Codes:
  0 - Always PASS (informational tool)
"""

import sys
import json
import ast
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set
from collections import defaultdict

# Import the static resolver for enhanced import resolution
try:
    from .static_import_resolver import StaticImportResolver
    RESOLVER_AVAILABLE = True
except ImportError:
    try:
        # Fallback for direct execution
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent))
        from static_import_resolver import StaticImportResolver
        RESOLVER_AVAILABLE = True
    except ImportError:
        RESOLVER_AVAILABLE = False

ROOT = Path(__file__).resolve().parents[2]
OUTPUT_PATH = ROOT / "02_audit_logging" / "evidence" / "deps" / "dependency_graph.json"
LOG_PATH = ROOT / "02_audit_logging" / "logs" / "anti_gaming_dependency_graph.jsonl"

EXCLUDE_DIRS = {
    ".git", "venv", "__pycache__", ".github", "datasets", "logs",
    ".pytest_cache", "node_modules", "dist", "build", ".venv", "backups"
}

class DependencyGraphGenerator:
    """Generate deterministic dependency graph from Python imports."""

    def __init__(self, root_dir: Path, use_resolver: bool = True):
        self.root = root_dir
        self.nodes = set()
        self.edges = []  # List of [from, to] for deterministic ordering
        self.use_resolver = use_resolver and RESOLVER_AVAILABLE
        self.resolver = None

        if self.use_resolver:
            self.resolver = StaticImportResolver(root_dir)

    def scan_repository(self) -> None:
        """Scan all Python files and extract import relationships."""
        if self.use_resolver and self.resolver:
            # Use enhanced static resolver for comprehensive import analysis
            self.resolver.scan_repository()

            # Convert resolver edges to graph format
            for edge_data in self.resolver.import_edges:
                if edge_data["resolved"]:
                    source = edge_data["source"]
                    target = edge_data["target"]

                    # Filter out standard library and external packages for cleaner graph
                    # unless they're project-internal modules
                    if target != "unknown" and not target.startswith("unknown_"):
                        self.nodes.add(source)
                        self.nodes.add(target)
                        self.edges.append([source, target])
        else:
            # Fallback to original basic import extraction
            python_files = []
            for py_file in self.root.rglob("*.py"):
                if any(excluded in py_file.parts for excluded in EXCLUDE_DIRS):
                    continue
                python_files.append(py_file)

            # Sort for deterministic processing
            python_files.sort()

            for py_file in python_files:
                module_name = self._get_module_name(py_file)
                imports = self._extract_imports(py_file)

                self.nodes.add(module_name)
                for imported in imports:
                    self.nodes.add(imported)
                    self.edges.append([module_name, imported])

    def _get_module_name(self, file_path: Path) -> str:
        """Convert file path to module name."""
        try:
            rel_path = file_path.relative_to(self.root)
        except ValueError:
            return str(file_path.stem)

        parts = list(rel_path.parent.parts) + [rel_path.stem]
        if parts[-1] == "__init__":
            parts = parts[:-1]
        return ".".join(parts)

    def _extract_imports(self, file_path: Path) -> Set[str]:
        """Extract import statements from Python file."""
        imports = set()

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read(), filename=str(file_path))

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name.split(".")[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module and node.level == 0:
                        imports.add(node.module.split(".")[0])

        except (SyntaxError, UnicodeDecodeError, OSError):
            # Skip files with syntax errors or encoding issues
            pass

        return imports

    def generate_graph(self) -> Dict:
        """Generate deterministic graph structure."""
        # Sort for deterministic output
        nodes_list = sorted(list(self.nodes))
        edges_list = sorted(self.edges, key=lambda e: (e[0], e[1]))

        metadata = {
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "root_directory": str(self.root.name),
            "node_count": len(nodes_list),
            "edge_count": len(edges_list),
            "generator_version": "2.0.0",
            "resolver_enabled": self.use_resolver
        }

        # Add resolver statistics if available
        if self.use_resolver and self.resolver:
            audit = self.resolver.generate_audit_report()
            metadata["resolver_stats"] = {
                "total_imports": audit["statistics"]["total_imports"],
                "resolution_rate": audit["statistics"]["resolution_rate"],
                "unresolved_count": audit["statistics"]["unresolved_imports"]
            }

        graph = {
            "metadata": metadata,
            "nodes": nodes_list,
            "edges": edges_list
        }

        return graph

    def calculate_hash(self, graph: Dict) -> str:
        """Calculate SHA-256 hash of graph (deterministic)."""
        # Create canonical JSON representation
        canonical = json.dumps(
            {
                "nodes": graph["nodes"],
                "edges": graph["edges"]
            },
            sort_keys=True,
            separators=(",", ":")
        )

        return hashlib.sha256(canonical.encode()).hexdigest()

def write_graph(graph: Dict, graph_hash: str) -> None:
    """Write graph to JSON file."""
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Add hash to graph
    graph["graph_sha256"] = f"sha256:{graph_hash}"

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2, sort_keys=True)

def write_audit_log(graph_hash: str, node_count: int, edge_count: int) -> None:
    """Write deterministic audit log entry."""
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    entry = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "component": "anti_gaming",
        "check": "dependency_graph",
        "status": "PASS",
        "graph_sha256": f"sha256:{graph_hash}",
        "node_count": node_count,
        "edge_count": edge_count,
        "output_path": str(OUTPUT_PATH.relative_to(ROOT))
    }

    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, sort_keys=True) + "\n")

def main() -> int:
    """Main execution."""
    print("SSID Dependency Graph Generator")
    print("=" * 60)

    # Generate graph
    print("Scanning repository...")
    generator = DependencyGraphGenerator(ROOT)
    generator.scan_repository()

    print(f"Nodes: {len(generator.nodes)}")
    print(f"Edges: {len(generator.edges)}")

    # Create graph structure
    print("Generating graph...")
    graph = generator.generate_graph()

    # Calculate hash
    graph_hash = generator.calculate_hash(graph)
    print(f"Graph Hash: sha256:{graph_hash[:16]}...")

    # Write outputs
    write_graph(graph, graph_hash)
    write_audit_log(graph_hash, len(generator.nodes), len(generator.edges))

    print()
    print("=" * 60)
    print("Status: PASS")
    print(f"Graph: {OUTPUT_PATH}")
    print(f"Audit log: {LOG_PATH}")

    return 0

if __name__ == "__main__":
    sys.exit(main())
