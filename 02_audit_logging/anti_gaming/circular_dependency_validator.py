#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
circular_dependency_validator.py – Circular Import Dependency Detector
Autor: edubrainboost ©2025 MIT License

Detects import cycles in Python code across the entire repository.
Read-only scan with deterministic output and JSONL logging.

Exit Codes:
  0 - PASS (no cycles or cycles within threshold)
  2 - FAIL (cycles exceed policy threshold)
"""

import sys
import json
import ast
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Tuple
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[2]
POLICY_PATH = ROOT / "23_compliance" / "policies" / "anti_gaming_policy.yaml"
LOG_PATH = ROOT / "02_audit_logging" / "logs" / "anti_gaming_circular_deps.jsonl"

# Directories to exclude from scan
EXCLUDE_DIRS = {
    ".git", "venv", "__pycache__", ".github", "datasets", "logs",
    ".pytest_cache", "node_modules", "dist", "build", ".venv"
}

class ImportGraphBuilder:
    """Build import dependency graph from Python files."""

    def __init__(self, root_dir: Path):
        self.root = root_dir
        self.graph = defaultdict(set)  # module -> set of imported modules

    def scan_repository(self) -> None:
        """Scan all Python files and build import graph."""
        python_files = []
        for py_file in self.root.rglob("*.py"):
            # Skip excluded directories
            if any(excluded in py_file.parts for excluded in EXCLUDE_DIRS):
                continue
            python_files.append(py_file)

        for py_file in python_files:
            module_name = self._get_module_name(py_file)
            imports = self._extract_imports(py_file)
            self.graph[module_name].update(imports)

    def _get_module_name(self, file_path: Path) -> str:
        """Convert file path to module name."""
        try:
            rel_path = file_path.relative_to(self.root)
        except ValueError:
            return str(file_path.stem)

        # Convert path to module notation
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
            pass  # Skip files that can't be parsed

        return imports

    def detect_cycles(self, max_cycle_length: int) -> List[List[str]]:
        """Detect circular dependencies using DFS."""
        cycles = []
        visited = set()
        rec_stack = []

        def dfs(node: str, path: List[str]) -> None:
            if node in rec_stack:
                # Found a cycle
                cycle_start = rec_stack.index(node)
                cycle = rec_stack[cycle_start:] + [node]

                if len(cycle) <= max_cycle_length + 1:  # +1 for repeated node
                    # Normalize cycle (start with lexicographically smallest)
                    min_idx = cycle.index(min(cycle[:-1]))
                    normalized = cycle[min_idx:-1] + cycle[:min_idx] + [cycle[min_idx]]

                    if normalized not in cycles:
                        cycles.append(normalized)
                return

            if node in visited:
                return

            visited.add(node)
            rec_stack.append(node)

            for neighbor in self.graph.get(node, set()):
                dfs(neighbor, path + [neighbor])

            rec_stack.pop()

        for node in self.graph.keys():
            dfs(node, [node])

        return cycles

def load_policy() -> Dict:
    """Load anti-gaming policy configuration."""
    if not POLICY_PATH.exists():
        return {"rules": {"circular_deps": {"max_cycle_length": 4, "severity": "high"}}}

    with open(POLICY_PATH, "r", encoding="utf-8") as f:
        policy = yaml.safe_load(f)

    return policy

def write_audit_log(status: str, cycles: List[List[str]], policy_version: str, thresholds: Dict) -> None:
    """Write deterministic audit log entry."""
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    entry = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "component": "anti_gaming",
        "check": "circular_deps",
        "status": status,
        "cycles": cycles,
        "cycle_count": len(cycles),
        "policy_version": policy_version,
        "thresholds": thresholds
    }

    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, sort_keys=True) + "\n")

def main() -> int:
    """Main execution."""
    print("SSID Circular Dependency Validator")
    print("=" * 60)

    # Load policy
    policy = load_policy()
    rules = policy.get("rules", {}).get("circular_deps", {})
    max_cycle_length = rules.get("max_cycle_length", 4)
    policy_version = policy.get("metadata", {}).get("version", "1.0.0")

    print(f"Policy Version: {policy_version}")
    print(f"Max Cycle Length: {max_cycle_length}")
    print()

    # Build import graph
    print("Scanning repository...")
    builder = ImportGraphBuilder(ROOT)
    builder.scan_repository()
    print(f"Analyzed {len(builder.graph)} modules")

    # Detect cycles
    print("Detecting circular dependencies...")
    cycles = builder.detect_cycles(max_cycle_length)

    # Determine status
    status = "PASS" if len(cycles) == 0 else "FAIL"

    # Write audit log
    write_audit_log(
        status=status,
        cycles=cycles,
        policy_version=policy_version,
        thresholds={"max_cycle_length": max_cycle_length}
    )

    # Report results
    print()
    print("=" * 60)
    print(f"Status: {status}")
    print(f"Cycles Detected: {len(cycles)}")

    if cycles:
        print("\nCircular Dependencies:")
        for i, cycle in enumerate(cycles, 1):
            print(f"  {i}. {' -> '.join(cycle)}")

    print()
    print(f"Audit log: {LOG_PATH}")

    return 0 if status == "PASS" else 2

if __name__ == "__main__":
    sys.exit(main())
