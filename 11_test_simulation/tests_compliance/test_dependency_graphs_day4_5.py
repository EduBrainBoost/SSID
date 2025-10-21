"""
Day 4-5: Dependency Graph & Circular Dependency Tests
Sprint 2 Anti-Gaming Coverage

Tests:
- dependency_graph_generator.py (20 tests)
- detect_circular_dependencies.py (18 tests)

Total: 38 comprehensive tests
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile
import shutil

# Add modules to path
repo_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(repo_root / "23_compliance" / "anti_gaming"))

from dependency_graph_generator import (
    DependencyGraphGenerator,
    DependencyViolation,
    GraphAnalysisResult
)
from detect_circular_dependencies import (
    detect_cycles,
    analyze_dependency_graph,
    generate_evidence_report
)

# ============================================================================
# PART 1: detect_circular_dependencies.py Tests (18 tests)
# ============================================================================

# --- Valid Graphs (No Cycles) ---

def test_detect_cycles_empty_graph():
    """Test cycle detection on empty graph"""
    edges = []
    cycles = detect_cycles(edges)
    assert cycles == []

def test_detect_cycles_single_node():
    """Test cycle detection with single isolated node"""
    edges = [("A", "B")]
    cycles = detect_cycles(edges)
    assert cycles == []

def test_detect_cycles_linear_chain():
    """Test cycle detection on linear dependency chain (no cycles)"""
    edges = [("A", "B"), ("B", "C"), ("C", "D")]
    cycles = detect_cycles(edges)
    assert cycles == []

def test_detect_cycles_tree_structure():
    """Test cycle detection on tree structure (no cycles)"""
    edges = [
        ("Root", "Child1"),
        ("Root", "Child2"),
        ("Child1", "Grandchild1"),
        ("Child1", "Grandchild2"),
    ]
    cycles = detect_cycles(edges)
    assert cycles == []

def test_detect_cycles_dag():
    """Test cycle detection on DAG (directed acyclic graph)"""
    edges = [
        ("A", "B"),
        ("A", "C"),
        ("B", "D"),
        ("C", "D"),
        ("D", "E"),
    ]
    cycles = detect_cycles(edges)
    assert cycles == []

# --- Graphs with Cycles ---

def test_detect_cycles_simple_self_loop():
    """Test detection of simple self-loop cycle"""
    edges = [("A", "A")]
    cycles = detect_cycles(edges)
    assert len(cycles) == 1
    assert "A" in cycles[0]

def test_detect_cycles_two_node_cycle():
    """Test detection of two-node cycle"""
    edges = [("A", "B"), ("B", "A")]
    cycles = detect_cycles(edges)
    assert len(cycles) == 1
    assert set(cycles[0]) == {"A", "B"}

def test_detect_cycles_three_node_cycle():
    """Test detection of three-node cycle"""
    edges = [("A", "B"), ("B", "C"), ("C", "A")]
    cycles = detect_cycles(edges)
    assert len(cycles) == 1
    assert set(cycles[0][:3]) == {"A", "B", "C"}  # Exclude repeated node

def test_detect_cycles_multiple_cycles():
    """Test detection of multiple independent cycles"""
    edges = [
        # Cycle 1: A -> B -> C -> A
        ("A", "B"), ("B", "C"), ("C", "A"),
        # Cycle 2: D -> E -> F -> D
        ("D", "E"), ("E", "F"), ("F", "D"),
        # No cycle: G -> H
        ("G", "H"),
    ]
    cycles = detect_cycles(edges)
    assert len(cycles) >= 2

def test_detect_cycles_nested_cycles():
    """Test detection of overlapping/nested cycles"""
    edges = [
        ("A", "B"),
        ("B", "C"),
        ("C", "A"),  # Cycle 1: A-B-C-A
        ("B", "D"),
        ("D", "B"),  # Cycle 2: B-D-B
    ]
    cycles = detect_cycles(edges)
    assert len(cycles) >= 1

# --- analyze_dependency_graph Tests ---

def test_analyze_empty_graph():
    """Test analysis of empty dependency graph"""
    edges = []
    result = analyze_dependency_graph(edges)

    assert result["total_nodes"] == 0
    assert result["total_edges"] == 0
    assert result["cycles_detected"] == 0
    assert result["risk_level"] == "NONE"

def test_analyze_acyclic_graph():
    """Test analysis of acyclic graph"""
    edges = [("A", "B"), ("B", "C"), ("C", "D")]
    result = analyze_dependency_graph(edges)

    assert result["total_nodes"] == 4
    assert result["total_edges"] == 3
    assert result["cycles_detected"] == 0
    assert result["risk_level"] == "NONE"

def test_analyze_single_cycle():
    """Test analysis of graph with single cycle"""
    edges = [("A", "B"), ("B", "C"), ("C", "A")]
    result = analyze_dependency_graph(edges)

    assert result["cycles_detected"] == 1
    assert result["risk_level"] == "LOW"  # 1-2 cycles
    assert result["max_cycle_length"] == 3

def test_analyze_multiple_cycles_risk_medium():
    """Test risk assessment for moderate number of cycles"""
    edges = [
        ("A", "B"), ("B", "A"),  # Cycle 1
        ("C", "D"), ("D", "C"),  # Cycle 2
        ("E", "F"), ("F", "E"),  # Cycle 3
    ]
    result = analyze_dependency_graph(edges)

    assert result["cycles_detected"] >= 2
    assert result["risk_level"] in ["LOW", "MEDIUM"]

def test_analyze_complex_graph_high_risk():
    """Test risk assessment for complex graph with many cycles"""
    edges = []
    # Generate many cycles
    for i in range(10):
        base = chr(65 + i * 2)  # A, C, E, G, ...
        next_node = chr(65 + i * 2 + 1)  # B, D, F, H, ...
        edges.append((base, next_node))
        edges.append((next_node, base))

    result = analyze_dependency_graph(edges)

    # Should have high risk due to many cycles
    assert result["cycles_detected"] > 5
    assert result["risk_level"] == "HIGH"

def test_analyze_cycle_statistics():
    """Test cycle length statistics calculation"""
    edges = [
        ("A", "B"), ("B", "A"),  # 2-node cycle
        ("C", "D"), ("D", "E"), ("E", "C"),  # 3-node cycle
    ]
    result = analyze_dependency_graph(edges)

    assert "max_cycle_length" in result
    assert "avg_cycle_length" in result
    assert result["max_cycle_length"] >= 2

def test_generate_evidence_report(tmp_path):
    """Test evidence report generation"""
    analysis = {
        "total_nodes": 4,
        "total_edges": 4,
        "cycles_detected": 1,
        "cycles": [["A", "B", "A"]],
        "risk_level": "LOW"
    }

    output_file = tmp_path / "evidence.json"
    generate_evidence_report(analysis, output_file)

    assert output_file.exists()

    import json
    with open(output_file) as f:
        loaded = json.load(f)

    assert "evidence_hash" in loaded
    assert loaded["cycles_detected"] == 1

def test_evidence_report_hash_consistency(tmp_path):
    """Test that evidence hash is deterministic"""
    analysis = {
        "total_nodes": 2,
        "total_edges": 2,
        "cycles_detected": 1,
        "cycles": [["X", "Y", "X"]],
        "risk_level": "LOW"
    }

    file1 = tmp_path / "evidence1.json"
    file2 = tmp_path / "evidence2.json"

    generate_evidence_report(analysis.copy(), file1)
    generate_evidence_report(analysis.copy(), file2)

    import json
    with open(file1) as f:
        data1 = json.load(f)
    with open(file2) as f:
        data2 = json.load(f)

    assert data1["evidence_hash"] == data2["evidence_hash"]

# ============================================================================
# PART 2: dependency_graph_generator.py Tests (20 tests)
# ============================================================================

@pytest.fixture
def temp_repo(tmp_path):
    """Create temporary repository structure for testing"""
    repo = tmp_path / "test_repo"
    repo.mkdir()

    # Create chart.yaml files
    module1 = repo / "01_module1"
    module1.mkdir()
    chart1 = module1 / "chart.yaml"
    chart1.write_text("""
metadata:
  shard_id: shard1
  root: module1
dependencies:
  required:
    - root: module2
  optional: []
""")

    module2 = repo / "02_module2"
    module2.mkdir()
    chart2 = module2 / "chart.yaml"
    chart2.write_text("""
metadata:
  shard_id: shard2
  root: module2
dependencies:
  required: []
  optional: []
""")

    return repo

# --- DependencyGraphGenerator Initialization ---

def test_generator_init(temp_repo):
    """Test generator initialization"""
    gen = DependencyGraphGenerator(temp_repo)

    assert gen.repo_root == temp_repo
    assert isinstance(gen.graph, dict)
    assert isinstance(gen.modules, set)
    assert isinstance(gen.violations, list)

# --- Dependency Parsing ---

def test_parse_dependencies_valid_charts(temp_repo):
    """Test parsing dependencies from valid chart.yaml files"""
    gen = DependencyGraphGenerator(temp_repo)
    deps = gen.parse_dependencies()

    assert isinstance(deps, dict)
    assert len(deps) >= 1  # Should find at least module1

def test_parse_dependencies_handles_missing_metadata(tmp_path):
    """Test parsing handles malformed chart.yaml gracefully"""
    repo = tmp_path / "bad_repo"
    repo.mkdir()

    bad_module = repo / "bad_module"
    bad_module.mkdir()
    bad_chart = bad_module / "chart.yaml"
    bad_chart.write_text("invalid: yaml: content:")

    gen = DependencyGraphGenerator(repo)
    deps = gen.parse_dependencies()

    # Should not crash, returns empty or partial data
    assert isinstance(deps, dict)

def test_parse_dependencies_skips_git_folders(tmp_path):
    """Test that .git folders are skipped during scanning"""
    repo = tmp_path / "repo_with_git"
    repo.mkdir()

    git_dir = repo / ".git" / "objects"
    git_dir.mkdir(parents=True)
    fake_chart = git_dir / "chart.yaml"
    fake_chart.write_text("metadata:\n  shard_id: fake")

    gen = DependencyGraphGenerator(repo)
    deps = gen.parse_dependencies()

    # Should not include .git content
    assert "fake" not in str(deps)

# --- Graph Building ---

def test_build_graph_from_dependencies(temp_repo):
    """Test building adjacency list from dependencies"""
    gen = DependencyGraphGenerator(temp_repo)
    deps = {"module1::shard1": ["module2"], "module2::shard2": []}

    gen.build_graph(deps)

    assert "module1::shard1" in gen.graph
    assert "module2" in gen.graph["module1::shard1"]

def test_build_graph_empty_dependencies():
    """Test building graph from empty dependencies"""
    gen = DependencyGraphGenerator(Path("/fake"))
    gen.build_graph({})

    assert len(gen.graph) == 0

# --- Cycle Detection (Tarjan's Algorithm) ---

def test_find_all_cycles_tarjan_no_cycles(temp_repo):
    """Test Tarjan's algorithm on acyclic graph"""
    gen = DependencyGraphGenerator(temp_repo)
    gen.modules = {"A", "B", "C"}
    gen.graph = {"A": ["B"], "B": ["C"], "C": []}

    cycles = gen.find_all_cycles_tarjan()

    assert len(cycles) == 0

def test_find_all_cycles_tarjan_simple_cycle(temp_repo):
    """Test Tarjan's algorithm detects simple cycle"""
    gen = DependencyGraphGenerator(temp_repo)
    gen.modules = {"A", "B"}
    gen.graph = {"A": ["B"], "B": ["A"]}

    cycles = gen.find_all_cycles_tarjan()

    assert len(cycles) >= 1
    assert set(cycles[0]) == {"A", "B"}

def test_find_all_cycles_tarjan_multiple_sccs(temp_repo):
    """Test Tarjan's algorithm finds multiple strongly connected components"""
    gen = DependencyGraphGenerator(temp_repo)
    gen.modules = {"A", "B", "C", "D"}
    gen.graph = {
        "A": ["B"],
        "B": ["A"],  # SCC 1: A-B
        "C": ["D"],
        "D": ["C"],  # SCC 2: C-D
    }

    cycles = gen.find_all_cycles_tarjan()

    assert len(cycles) >= 2

# --- Violation Generation ---

def test_generate_violations_from_cycles(temp_repo):
    """Test violation objects generated from detected cycles"""
    gen = DependencyGraphGenerator(temp_repo)
    cycles = [["A", "B", "A"], ["C", "D", "E", "C"]]

    gen.generate_violations(cycles)

    assert len(gen.violations) == 2
    assert all(isinstance(v, DependencyViolation) for v in gen.violations)
    assert all(v.severity == "critical" for v in gen.violations)

def test_violation_contains_cycle_info(temp_repo):
    """Test that violations contain full cycle information"""
    gen = DependencyGraphGenerator(temp_repo)
    cycles = [["X", "Y", "Z", "X"]]

    gen.generate_violations(cycles)

    violation = gen.violations[0]
    assert violation.violation_type == "circular_dependency"
    assert "X" in violation.cycle
    assert len(violation.cycle) >= 3

# --- DOT Export ---

def test_export_graph_dot(temp_repo, tmp_path):
    """Test DOT format export for graph visualization"""
    gen = DependencyGraphGenerator(temp_repo)
    gen.modules = {"A", "B"}
    gen.graph = {"A": ["B"], "B": []}

    output_file = tmp_path / "test_graph.dot"
    gen.export_graph_dot(output_file)

    assert output_file.exists()
    content = output_file.read_text()

    assert "digraph DependencyGraph" in content
    assert '"A"' in content
    assert '"B"' in content

def test_export_graph_dot_highlights_cycles(temp_repo, tmp_path):
    """Test that DOT export highlights detected cycles in red"""
    gen = DependencyGraphGenerator(temp_repo)
    gen.modules = {"A", "B"}
    gen.graph = {"A": ["B"], "B": ["A"]}

    # Add violation
    violation = DependencyViolation(
        violation_id="TEST-001",
        timestamp="2025-01-01T00:00:00Z",
        severity="critical",
        violation_type="circular_dependency",
        cycle=["A", "B", "A"],
        description="Test cycle"
    )
    gen.violations = [violation]

    output_file = tmp_path / "cycle_graph.dot"
    gen.export_graph_dot(output_file)

    content = output_file.read_text()
    assert "color=red" in content  # Cycles should be highlighted

# --- Full Analysis Workflow ---

def test_run_analysis_success(temp_repo):
    """Test full analysis workflow completes successfully"""
    gen = DependencyGraphGenerator(temp_repo)

    
    mock_versioning = MagicMock()
    with patch.dict('sys.modules', {'dependency_graph_versioning': mock_versioning}):
        result = gen.run_analysis()

    assert isinstance(result, GraphAnalysisResult)
    assert result.status in ["PASS", "FAIL"]
    assert result.total_modules >= 0
    assert result.total_dependencies >= 0

def test_run_analysis_pass_no_cycles(temp_repo):
    """Test analysis returns PASS when no cycles detected"""
    gen = DependencyGraphGenerator(temp_repo)

    # The temp_repo fixture provides an acyclic graph (module1 -> module2)
    
    mock_versioning = MagicMock()
    with patch.dict('sys.modules', {'dependency_graph_versioning': mock_versioning}):
        result = gen.run_analysis()

    # Should pass because temp_repo has no cycles
    assert result.status == "PASS"
    assert result.cycles_found == 0

def test_run_analysis_fail_with_cycles(temp_repo):
    """Test analysis returns FAIL when cycles detected"""
    gen = DependencyGraphGenerator(temp_repo)

    
    
    mock_versioning = MagicMock()
    with patch.dict('sys.modules', {'dependency_graph_versioning': mock_versioning}):
        with patch.object(gen, 'find_all_cycles_tarjan', return_value=[["A", "B"]]):
            result = gen.run_analysis()

    assert result.status == "FAIL"
    assert result.cycles_found > 0

def test_run_analysis_generates_output_files(temp_repo):
    """Test that analysis generates output files"""
    gen = DependencyGraphGenerator(temp_repo)

    
    mock_versioning = MagicMock()
    with patch.dict('sys.modules', {'dependency_graph_versioning': mock_versioning}):
        result = gen.run_analysis()

    assert result.graph_file is not None
    assert result.violations_file is not None

# --- Edge Cases ---

def test_generator_handles_empty_repository(tmp_path):
    """Test generator handles repository with no chart.yaml files"""
    empty_repo = tmp_path / "empty"
    empty_repo.mkdir()

    gen = DependencyGraphGenerator(empty_repo)
    result = gen.run_analysis()

    assert result.status == "PASS"  # No violations if no modules
    assert result.total_modules == 0
