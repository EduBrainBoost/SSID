#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Circular Dependency Detection
Anti-Gaming Module - Detects manipulative dependency cycles
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple, Set
from datetime import datetime, timezone

Edge = Tuple[str, str]


def detect_cycles(edges: List[Edge]) -> List[List[str]]:
    """
    Detect simple cycles in a directed graph defined by edges.
    Uses DFS with path stack; returns list of cycles (each as node list).

    Args:
        edges: List of (source, target) tuples representing directed edges

    Returns:
        List of cycles, where each cycle is a list of node names
    """
    graph: Dict[str, Set[str]] = {}
    for a, b in edges:
        graph.setdefault(a, set()).add(b)
        graph.setdefault(b, set())  # ensure sink appears

    visited: Set[str] = set()
    stack: Set[str] = set()
    path: List[str] = []
    cycles: List[List[str]] = []

    def dfs(node: str):
        visited.add(node)
        stack.add(node)
        path.append(node)
        for nbr in graph.get(node, ()):
            if nbr not in visited:
                dfs(nbr)
            elif nbr in stack:
                # found a cycle: slice path from nbr to end + nbr
                try:
                    i = path.index(nbr)
                    cyc = path[i:] + [nbr]
                    # normalize cycle representation (start with smallest string) to avoid duplicates
                    if cyc:
                        min_idx = min(range(len(cyc)-1), key=lambda k: cyc[k])
                        norm = cyc[min_idx:-1] + cyc[:min_idx] + [cyc[min_idx]]
                        if norm not in cycles:
                            cycles.append(norm)
                except ValueError:
                    raise NotImplementedError("TODO: Implement this block")
        stack.remove(node)
        path.pop()

    for n in list(graph.keys()):
        if n not in visited:
            dfs(n)
    return cycles


def analyze_dependency_graph(edges: List[Edge]) -> Dict:
    """
    Comprehensive dependency graph analysis for gaming detection.

    Args:
        edges: List of (source, target) dependency edges

    Returns:
        Dict with analysis results including cycles, statistics, risk level
    """
    cycles = detect_cycles(edges)

    # Build graph statistics
    nodes = set()
    for a, b in edges:
        nodes.add(a)
        nodes.add(b)

    # Risk assessment
    if len(cycles) == 0:
        risk_level = "NONE"
    elif len(cycles) <= 2:
        risk_level = "LOW"
    elif len(cycles) <= 5:
        risk_level = "MEDIUM"
    else:
        risk_level = "HIGH"

    # Calculate cycle complexity
    max_cycle_length = max((len(c) - 1 for c in cycles), default=0)  # -1 because last element repeats first
    avg_cycle_length = sum(len(c) - 1 for c in cycles) / len(cycles) if cycles else 0

    return {
        "total_nodes": len(nodes),
        "total_edges": len(edges),
        "cycles_detected": len(cycles),
        "cycles": [[str(n) for n in cycle] for cycle in cycles],  # Ensure JSON serializable
        "max_cycle_length": max_cycle_length,
        "avg_cycle_length": round(avg_cycle_length, 2),
        "risk_level": risk_level,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


def generate_evidence_report(analysis: Dict, output_path: Path) -> None:
    """
    Generate evidence report for audit trail.

    Args:
        analysis: Analysis results from analyze_dependency_graph
        output_path: Path to output evidence file
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Add evidence hash
    canonical = json.dumps(analysis, sort_keys=True)
    evidence_hash = hashlib.sha256(canonical.encode()).hexdigest()
    analysis["evidence_hash"] = evidence_hash

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(analysis, f, indent=2)


if __name__ == "__main__":
    import sys

    print("=" * 60)
    print("Circular Dependency Detection - Test Run")
    print("=" * 60)

    # Test case: dependency graph with cycles
    test_edges = [
        ("A", "B"),
        ("B", "C"),
        ("C", "A"),  # Cycle: A -> B -> C -> A
        ("D", "E"),
        ("E", "F"),
        ("F", "D"),  # Cycle: D -> E -> F -> D
        ("G", "H"),
        ("H", "I"),  # No cycle
    ]

    # Run analysis
    result = analyze_dependency_graph(test_edges)

    print(f"\nTotal nodes: {result['total_nodes']}")
    print(f"Total edges: {result['total_edges']}")
    print(f"Cycles detected: {result['cycles_detected']}")
    print(f"Risk level: {result['risk_level']}")

    if result['cycles']:
        print(f"\nDetected cycles:")
        for i, cycle in enumerate(result['cycles'], 1):
            cycle_str = " -> ".join(cycle)
            print(f"  {i}. {cycle_str}")
            print(f"     Length: {len(cycle) - 1} edges")

    # Generate evidence
    repo_root = Path(__file__).resolve().parents[2]
    evidence_path = repo_root / "23_compliance" / "evidence" / "anti_gaming" / f"circular_dependencies_{datetime.now(timezone.utc).strftime('%Y%m%d')}.json"
    generate_evidence_report(result, evidence_path)

    print(f"\nEvidence report: {evidence_path}")

    if result['cycles_detected'] > 0:
        print(f"\n[FAIL] {result['cycles_detected']} circular dependencies detected!")
        sys.exit(1)
    else:
        print(f"\n[OK] No circular dependencies detected")
        sys.exit(0)
