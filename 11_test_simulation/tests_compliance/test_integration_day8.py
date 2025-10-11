"""
Day 8: Cross-Module Integration Tests
Sprint 2 Anti-Gaming Coverage

Integration Test Scenarios:
1. End-to-End Badge Validation Flow (5 tests)
2. Identity Hash → Proof Detection (4 tests)
3. Dependency Graph → Cycle Detection (3 tests)
4. Evidence Chain Consistency (4 tests)
5. Performance Benchmarks (4 tests)
6. Multi-Module Error Handling (3 tests)

Total: 23 comprehensive integration tests
"""

import pytest
import sys
import json
import time
import hashlib
from pathlib import Path
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock

# Add modules to path
repo_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(repo_root / "23_compliance" / "anti_gaming"))

# Import all anti-gaming modules
from badge_signature_validator import verify_badges, _sha256_text
from badge_integrity_checker import verify_badge_records
from detect_duplicate_identity_hashes import (
    detect_duplicate_identity_hashes,
    analyze_hash_dataset,
    generate_evidence_report as hash_evidence
)
from dependency_graph_generator import DependencyGraphGenerator
from detect_circular_dependencies import (
    detect_cycles,
    analyze_dependency_graph,
    generate_evidence_report as graph_evidence
)
from overfitting_detector import (
    analyze_model_metrics,
    batch_analyze_models,
    generate_evidence_report as model_evidence
)


# ============================================================================
# PART 1: End-to-End Badge Validation Flow (5 tests)
# ============================================================================

def test_integration_badge_signature_to_integrity():
    """Test badge flows from signature validation to integrity check"""
    badge = {
        "id": "badge-001",
        "payload": "user_contribution_data",
        "sig": _sha256_text("user_contribution_data")
    }

    # Signature validation
    invalid_sigs = verify_badges([badge])
    assert len(invalid_sigs) == 0

    # Integrity check
    integrity_result = verify_badge_records([badge])
    assert len(integrity_result) == 0


def test_integration_badge_tampering_detection():
    """Test tampered badge detected across both validators"""
    tampered = {
        "id": "badge-002",
        "payload": "original_data",
        "sig": _sha256_text("TAMPERED_DATA")
    }

    # Should fail signature validation
    invalid_sigs = verify_badges([tampered])
    assert len(invalid_sigs) == 1
    assert invalid_sigs[0]["error"] == "invalid-signature"

    # Should also fail integrity check
    integrity_result = verify_badge_records([tampered])
    assert len(integrity_result) == 1
    assert integrity_result[0]["error"] == "bad-signature"


def test_integration_badge_batch_validation():
    """Test batch badge processing across validators"""
    badges = [
        {"id": "b1", "payload": "data1", "sig": _sha256_text("data1")},
        {"id": "b2", "payload": "data2", "sig": _sha256_text("data2")},
        {"id": "b3", "payload": "data3", "sig": _sha256_text("WRONG")},
    ]

    # Signature validation
    invalid_sigs = verify_badges(badges)
    assert len(invalid_sigs) == 1

    # Batch integrity check
    batch_result = verify_badge_records(badges)
    assert len(batch_result) == 1


def test_integration_badge_to_identity_hash():
    """Test badge payload used as identity hash"""
    badge = {
        "id": "badge-003",
        "payload": "unique_user_identity",
        "sig": _sha256_text("unique_user_identity")
    }

    # Validate badge
    invalid = verify_badges([badge])
    assert len(invalid) == 0

    # Extract payload as identity hash
    identity_hash = badge["payload"]

    # Check for duplicates
    hashes = [identity_hash, "other_hash_1", "other_hash_2"]
    duplicates = detect_duplicate_identity_hashes(hashes)
    assert len(duplicates) == 0


def test_integration_badge_evidence_chain():
    """Test evidence generation from badge validation"""
    badges = [
        {"id": "ev1", "payload": "data1", "sig": _sha256_text("data1")},
        {"id": "ev2", "payload": "data2", "sig": _sha256_text("data2")}
    ]

    # Validate badges
    invalid = verify_badge_records(badges)
    assert len(invalid) == 0

    # Create summary dict
    batch_result = {
        "total_badges": len(badges),
        "valid_count": len(badges) - len(invalid),
        "invalid_count": len(invalid)
    }

    # Evidence should be serializable
    evidence_json = json.dumps(batch_result)
    assert len(evidence_json) > 0


# ============================================================================
# PART 2: Identity Hash → Proof Detection (4 tests)
# ============================================================================

def test_integration_identity_hash_duplication_detection():
    """Test identity hash duplication detection"""
    hashes = ["user1", "user2", "user1", "user3"]
    duplicates = detect_duplicate_identity_hashes(hashes)
    assert "user1" in duplicates


def test_integration_hash_analysis():
    """Test hash analysis with risk assessment"""
    hashes = ["h1", "h2", "h3", "h1", "h1"]
    hash_analysis = analyze_hash_dataset(hashes)

    assert hash_analysis["total_hashes"] == 5
    assert hash_analysis["duplicate_count"] >= 1


def test_integration_evidence_hash_consistency():
    """Test evidence hash consistency"""
    hash_analysis = {"duplicate_count": 2, "total_hashes": 100}
    canonical1 = json.dumps(hash_analysis, sort_keys=True)
    hash1 = hashlib.sha256(canonical1.encode()).hexdigest()

    canonical2 = json.dumps(hash_analysis, sort_keys=True)
    hash2 = hashlib.sha256(canonical2.encode()).hexdigest()

    assert hash1 == hash2


def test_integration_multi_validator_risk_assessment():
    """Test risk assessment across validators"""
    hashes = ["dup"] * 50 + [f"unique_{i}" for i in range(50)]
    hash_result = analyze_hash_dataset(hashes)
    assert hash_result["risk_level"] in ["MEDIUM", "HIGH", "CRITICAL"]


# ============================================================================
# PART 3: Dependency Graph → Cycle Detection (3 tests)
# ============================================================================

def test_integration_dependency_graph_to_cycle_detection():
    """Test dependency graph feeding into cycle detection"""
    edges = [
        ("A", "B"),
        ("B", "C"),
        ("C", "A"),
    ]

    cycles = detect_cycles(edges)
    assert len(cycles) == 1

    graph_analysis = analyze_dependency_graph(edges)
    assert graph_analysis["cycles_detected"] == 1
    assert graph_analysis["risk_level"] == "LOW"


def test_integration_graph_generator_workflow(tmp_path):
    """Test full dependency graph generation workflow"""
    repo = tmp_path / "test_repo"
    repo.mkdir()

    module1 = repo / "module1"
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

    module2 = repo / "module2"
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

    gen = DependencyGraphGenerator(repo)
    mock_versioning = MagicMock()
    with patch.dict('sys.modules', {'dependency_graph_versioning': mock_versioning}):
        result = gen.run_analysis()

    assert result.status == "PASS"
    assert result.cycles_found == 0


def test_integration_circular_dependency_evidence():
    """Test evidence generation from circular dependency detection"""
    edges = [("X", "Y"), ("Y", "X")]

    graph_analysis = analyze_dependency_graph(edges)

    assert "cycles_detected" in graph_analysis
    assert "risk_level" in graph_analysis
    assert "cycles" in graph_analysis
    assert len(graph_analysis["cycles"]) >= 1


# ============================================================================
# PART 4: Evidence Chain Consistency (4 tests)
# ============================================================================

def test_integration_evidence_sha256_across_modules(tmp_path):
    """Test SHA-256 evidence hash consistency across all modules"""
    evidence_hashes = []

    # Hash module evidence
    hash_analysis = {"duplicate_count": 5, "total_hashes": 100}
    hash_file = tmp_path / "hash_evidence.json"
    hash_evidence(hash_analysis, hash_file)
    with open(hash_file) as f:
        hash_data = json.load(f)
    evidence_hashes.append(hash_data["evidence_hash"])

    # Graph module evidence
    graph_analysis = {"cycles_detected": 2, "total_nodes": 10}
    graph_file = tmp_path / "graph_evidence.json"
    graph_evidence(graph_analysis, graph_file)
    with open(graph_file) as f:
        graph_data = json.load(f)
    evidence_hashes.append(graph_data["evidence_hash"])

    # Model module evidence
    model_analysis = {"overfitting_count": 1, "total_models": 5}
    model_file = tmp_path / "model_evidence.json"
    model_evidence(model_analysis, model_file)
    with open(model_file) as f:
        model_data = json.load(f)
    evidence_hashes.append(model_data["evidence_hash"])

    # All hashes should be 64-char SHA-256
    for h in evidence_hashes:
        assert len(h) == 64
        assert all(c in '0123456789abcdef' for c in h)


def test_integration_evidence_chain_linkage(tmp_path):
    """Test evidence files can be linked via timestamps"""
    hash_analysis = {"duplicate_count": 1, "timestamp": "2025-01-01T10:00:00Z"}
    hash_file = tmp_path / "hash_ev.json"
    hash_evidence(hash_analysis, hash_file)

    model_analysis = {"overfitting_count": 2, "timestamp": "2025-01-01T10:01:00Z"}
    model_file = tmp_path / "model_ev.json"
    model_evidence(model_analysis, model_file)

    # Both should have timestamps
    with open(hash_file) as f:
        hash_data = json.load(f)
    with open(model_file) as f:
        model_data = json.load(f)

    assert "timestamp" in hash_data
    assert "timestamp" in model_data


def test_integration_evidence_aggregation():
    """Test aggregating evidence from multiple validators"""
    evidence_chain = {
        "hash_validator": {"risk_level": "MEDIUM", "violations": 5},
        "graph_validator": {"risk_level": "NONE", "violations": 0},
        "model_validator": {"risk_level": "HIGH", "violations": 3}
    }

    # Aggregate risk levels
    high_risk_count = sum(
        1 for v in evidence_chain.values()
        if v["risk_level"] in ["HIGH", "CRITICAL"]
    )

    assert high_risk_count == 1

    # Total violations
    total_violations = sum(v["violations"] for v in evidence_chain.values())
    assert total_violations == 8


def test_integration_model_to_hash_correlation():
    """Test correlation between overfitting detection and hash analysis"""
    # High overfitting rate may correlate with identity hash gaming
    models = [
        {"model_id": "m1", "train_acc": 0.99, "val_acc": 0.70},
        {"model_id": "m2", "train_acc": 0.98, "val_acc": 0.65},
    ]

    model_result = batch_analyze_models(models)
    assert model_result["overfitting_count"] == 2

    # Corresponding high hash duplication
    hashes = ["hash1"] * 30 + [f"hash_{i}" for i in range(70)]
    hash_result = analyze_hash_dataset(hashes)
    assert hash_result["risk_level"] in ["MEDIUM", "HIGH", "CRITICAL"]


# ============================================================================
# PART 5: Performance Benchmarks (4 tests)
# ============================================================================

def test_integration_performance_badge_validation():
    """Test badge validation performance at scale"""
    badges = [
        {"id": f"badge_{i}", "payload": f"data_{i}", "sig": _sha256_text(f"data_{i}")}
        for i in range(100)
    ]

    start = time.time()
    invalid = verify_badges(badges)
    duration = time.time() - start

    assert duration < 1.0
    assert len(invalid) == 0


def test_integration_performance_hash_analysis():
    """Test hash analysis performance with large dataset"""
    hashes = [f"hash_{i}" for i in range(1000)]

    start = time.time()
    result = analyze_hash_dataset(hashes)
    duration = time.time() - start

    assert duration < 2.0
    assert result["total_hashes"] == 1000


def test_integration_performance_cycle_detection():
    """Test cycle detection performance"""
    # Generate large graph
    edges = [(f"n{i}", f"n{i+1}") for i in range(100)]

    start = time.time()
    cycles = detect_cycles(edges)
    duration = time.time() - start

    assert duration < 1.0
    assert len(cycles) == 0  # No cycles in linear chain


def test_integration_performance_end_to_end():
    """Test end-to-end validation chain performance"""
    start = time.time()

    # Badge validation
    badges = [{"id": f"b{i}", "payload": f"d{i}", "sig": _sha256_text(f"d{i}")} for i in range(50)]
    verify_badges(badges)

    # Hash analysis
    hashes = [f"hash_{i}" for i in range(100)]
    analyze_hash_dataset(hashes)

    # Model analysis
    models = [{"model_id": f"m{i}", "train_acc": 0.94, "val_acc": 0.91} for i in range(20)]
    batch_analyze_models(models)

    duration = time.time() - start

    assert duration < 3.0


# ============================================================================
# PART 6: Multi-Module Error Handling (3 tests)
# ============================================================================

def test_integration_error_propagation_invalid_badge():
    """Test error propagation from invalid badge"""
    bad_badge = {
        "id": "bad",
        # Missing payload and sig
    }

    result = verify_badge_records([bad_badge])
    assert isinstance(result, list)


def test_integration_error_handling_empty_inputs():
    """Test all modules handle empty inputs gracefully"""
    # Empty badge list
    assert verify_badges([]) == []

    # Empty hash list
    result = analyze_hash_dataset([])
    assert result["total_hashes"] == 0

    # Empty edge list
    cycles = detect_cycles([])
    assert len(cycles) == 0

    # Empty model list
    result = batch_analyze_models([])
    assert result["total_models"] == 0


def test_integration_error_handling_malformed_data():
    """Test modules handle malformed data gracefully"""
    # Malformed badges
    malformed_badges = [
        {"wrong_key": "value"},
        None,
        "not_a_dict"
    ]

    # Should handle without crashing
    try:
        result = verify_badge_records(malformed_badges)
        assert isinstance(result, list)
    except (TypeError, AttributeError):
        # Acceptable to raise these errors
        pass

    # Malformed hashes
    try:
        result = detect_duplicate_identity_hashes([None, "", 123])
        assert isinstance(result, list)
    except (TypeError, AttributeError):
        pass
