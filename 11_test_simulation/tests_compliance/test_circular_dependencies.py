"""
Comprehensive tests for detect_circular_dependencies module.
Tests all edge cases and ensures 80%+ code coverage.
"""
import pytest
import sys
from pathlib import Path

# Add repo root to path
repo_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(repo_root))

# Import using importlib to handle module names starting with numbers
import importlib.util
spec = importlib.util.spec_from_file_location(
    "detect_circular_dependencies",
    repo_root / "23_compliance" / "anti_gaming" / "detect_circular_dependencies.py"
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
detect_cycles = module.detect_cycles
Edge = module.Edge


def test_simple_cycle():
    """Test simple 3-node cycle."""
    edges = [("A", "B"), ("B", "C"), ("C", "A")]
    cycles = detect_cycles(edges)
    assert len(cycles) == 1
    assert "A" in cycles[0]
    assert "B" in cycles[0]
    assert "C" in cycles[0]


def test_no_cycle():
    """Test acyclic graph."""
    edges = [("A", "B"), ("B", "C")]
    cycles = detect_cycles(edges)
    assert cycles == []


def test_self_loop():
    """Test node pointing to itself."""
    edges = [("A", "A")]
    cycles = detect_cycles(edges)
    assert len(cycles) == 1
    # Self-loop should be detected as a cycle
    assert "A" in cycles[0]


def test_two_node_cycle():
    """Test minimal cycle with 2 nodes."""
    edges = [("A", "B"), ("B", "A")]
    cycles = detect_cycles(edges)
    assert len(cycles) == 1
    assert set(cycles[0][:2]) == {"A", "B"}


def test_multiple_independent_cycles():
    """Test graph with multiple independent cycles."""
    edges = [
        # Cycle 1: A -> B -> A
        ("A", "B"), ("B", "A"),
        # Cycle 2: X -> Y -> Z -> X
        ("X", "Y"), ("Y", "Z"), ("Z", "X"),
    ]
    cycles = detect_cycles(edges)
    assert len(cycles) >= 2  # Should detect at least 2 cycles


def test_nested_cycles():
    """Test graph with nested/overlapping cycles."""
    edges = [
        ("A", "B"),
        ("B", "C"),
        ("C", "A"),  # Cycle: A -> B -> C -> A
        ("B", "D"),
        ("D", "B"),  # Cycle: B -> D -> B
    ]
    cycles = detect_cycles(edges)
    # Should detect both cycles
    assert len(cycles) >= 2


def test_large_cycle():
    """Test cycle with many nodes."""
    # Create a cycle: 0 -> 1 -> 2 -> ... -> 99 -> 0
    edges = [(str(i), str((i + 1) % 100)) for i in range(100)]
    cycles = detect_cycles(edges)
    assert len(cycles) == 1
    assert len(cycles[0]) >= 100  # Should include all nodes in cycle


def test_empty_graph():
    """Test with no edges."""
    edges = []
    cycles = detect_cycles(edges)
    assert cycles == []


def test_single_edge():
    """Test with single edge (no cycle)."""
    edges = [("A", "B")]
    cycles = detect_cycles(edges)
    assert cycles == []


def test_disconnected_components():
    """Test graph with disconnected components."""
    edges = [
        # Component 1: Linear
        ("A", "B"), ("B", "C"),
        # Component 2: Cycle
        ("X", "Y"), ("Y", "X"),
    ]
    cycles = detect_cycles(edges)
    # Should detect the X-Y cycle
    assert len(cycles) >= 1


def test_complex_graph():
    """Test realistic complex dependency graph."""
    edges = [
        ("core", "foundation"),
        ("foundation", "meta"),
        ("meta", "core"),  # Cycle!
        ("ai", "compliance"),
        ("audit", "compliance"),
        ("interop", "identity"),
    ]
    cycles = detect_cycles(edges)
    assert len(cycles) >= 1
    # Should detect core -> foundation -> meta -> core
    cycle_nodes = set(cycles[0])
    assert "core" in cycle_nodes
    assert "foundation" in cycle_nodes
    assert "meta" in cycle_nodes


def test_diamond_pattern_no_cycle():
    """Test diamond dependency pattern (no cycle)."""
    edges = [
        ("A", "B"),
        ("A", "C"),
        ("B", "D"),
        ("C", "D"),
    ]
    cycles = detect_cycles(edges)
    assert cycles == []


def test_multiple_edges_same_nodes():
    """Test duplicate edges (should handle gracefully)."""
    edges = [
        ("A", "B"),
        ("A", "B"),  # duplicate
        ("B", "A"),
    ]
    cycles = detect_cycles(edges)
    # Should still detect the A-B cycle
    assert len(cycles) >= 1


def test_cycle_with_tail():
    """Test cycle with non-cyclic tail."""
    edges = [
        ("Start", "A"),  # Tail leading into cycle
        ("A", "B"),
        ("B", "C"),
        ("C", "A"),  # Cycle: A -> B -> C -> A
    ]
    cycles = detect_cycles(edges)
    assert len(cycles) == 1
    cycle_nodes = set(cycles[0])
    assert "A" in cycle_nodes
    assert "B" in cycle_nodes
    assert "C" in cycle_nodes
    # "Start" should not be in the cycle
    assert "Start" not in cycle_nodes or cycle_nodes.count("Start") <= 1


def test_numeric_node_ids():
    """Test with numeric node identifiers."""
    edges = [
        (1, 2),
        (2, 3),
        (3, 1),
    ]
    # Convert to strings since detect_cycles expects strings
    edges_str = [(str(a), str(b)) for a, b in edges]
    cycles = detect_cycles(edges_str)
    assert len(cycles) == 1


def test_special_characters_in_nodes():
    """Test with special characters in node names."""
    edges = [
        ("node/with/slashes", "node:with:colons"),
        ("node:with:colons", "node-with-dashes"),
        ("node-with-dashes", "node/with/slashes"),
    ]
    cycles = detect_cycles(edges)
    assert len(cycles) == 1


def test_long_path_to_cycle():
    """Test long acyclic path leading to a cycle."""
    edges = [
        ("Start", "A"),
        ("A", "B"),
        ("B", "C"),
        ("C", "D"),
        ("D", "E"),
        # Now create a cycle at the end
        ("E", "F"),
        ("F", "G"),
        ("G", "E"),
    ]
    cycles = detect_cycles(edges)
    assert len(cycles) == 1
    # Cycle should be E-F-G
    cycle_nodes = set(cycles[0])
    assert "E" in cycle_nodes
    assert "F" in cycle_nodes
    assert "G" in cycle_nodes


def test_bidirectional_edges():
    """Test graph with bidirectional edges."""
    edges = [
        ("A", "B"),
        ("B", "A"),
        ("B", "C"),
        ("C", "B"),
    ]
    cycles = detect_cycles(edges)
    # Should detect A-B and B-C cycles
    assert len(cycles) >= 2


def test_star_topology_no_cycle():
    """Test star topology (central node with spokes, no cycle)."""
    edges = [
        ("Center", "Node1"),
        ("Center", "Node2"),
        ("Center", "Node3"),
        ("Center", "Node4"),
    ]
    cycles = detect_cycles(edges)
    assert cycles == []


def test_complete_graph_small():
    """Test small complete graph (all nodes connected to all)."""
    # 3-node complete graph has cycles
    edges = [
        ("A", "B"), ("A", "C"),
        ("B", "A"), ("B", "C"),
        ("C", "A"), ("C", "B"),
    ]
    cycles = detect_cycles(edges)
    # Should detect multiple cycles
    assert len(cycles) >= 1


def test_cycle_normalization():
    """Test that functionally identical cycles are detected correctly."""
    # Same cycle but starting from different points
    edges1 = [("A", "B"), ("B", "C"), ("C", "A")]
    edges2 = [("B", "C"), ("C", "A"), ("A", "B")]

    cycles1 = detect_cycles(edges1)
    cycles2 = detect_cycles(edges2)

    # Both should detect the same cycle
    assert len(cycles1) == len(cycles2) == 1


def test_sink_nodes():
    """Test graph with sink nodes (nodes with no outgoing edges)."""
    edges = [
        ("A", "B"),
        ("B", "Sink1"),
        ("A", "C"),
        ("C", "Sink2"),
    ]
    cycles = detect_cycles(edges)
    assert cycles == []


def test_source_nodes():
    """Test graph with source nodes (nodes with no incoming edges)."""
    edges = [
        ("Source1", "A"),
        ("Source2", "A"),
        ("A", "B"),
        ("B", "A"),  # Cycle
    ]
    cycles = detect_cycles(edges)
    assert len(cycles) >= 1
    # Should detect A-B cycle
    cycle_nodes = set(cycles[0])
    assert "A" in cycle_nodes
    assert "B" in cycle_nodes


def test_realistic_module_dependencies():
    """Test realistic software module dependency scenario."""
    edges = [
        # Valid dependencies
        ("ui", "api"),
        ("api", "business_logic"),
        ("business_logic", "data_access"),
        ("data_access", "database"),

        # Problematic circular dependency
        ("business_logic", "ui"),  # Creates cycle: ui -> api -> business_logic -> ui
    ]
    cycles = detect_cycles(edges)
    assert len(cycles) >= 1

    # Verify the cycle includes the problematic modules
    cycle_nodes = set(cycles[0])
    assert "ui" in cycle_nodes
    assert "business_logic" in cycle_nodes
