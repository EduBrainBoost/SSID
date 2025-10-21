#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_anti_gaming_suite.py – Comprehensive Anti-Gaming Test Suite
Autor: edubrainboost ©2025 MIT License

Tests all 7 anti-gaming scripts with deterministic fixtures.
"""

import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime, timedelta, timezone

ROOT = Path(__file__).resolve().parents[2]
ANTI_GAMING = ROOT / "02_audit_logging" / "anti_gaming"

def test_circular_dependency_validator():
    """Test circular dependency validator."""
    print("[TEST] Circular Dependency Validator...")

    script = ANTI_GAMING / "circular_dependency_validator.py"
    result = subprocess.run([sys.executable, str(script)], capture_output=True)

    # Should exit with 0 or 2
    assert result.returncode in (0, 2), f"Unexpected exit code: {result.returncode}"

    # Check log file created
    log_file = ROOT / "02_audit_logging" / "logs" / "anti_gaming_circular_deps.jsonl"
    assert log_file.exists(), "Log file not created"

    # Verify log structure
    with open(log_file, "r") as f:
        lines = f.readlines()
        assert len(lines) > 0, "Log file empty"

        last_entry = json.loads(lines[-1])
        assert "component" in last_entry
        assert "check" in last_entry
        assert "status" in last_entry
        assert last_entry["component"] == "anti_gaming"
        assert last_entry["check"] == "circular_deps"

    print("  ✓ PASS")

def test_dependency_graph_generator():
    """Test dependency graph generator."""
    print("[TEST] Dependency Graph Generator...")

    script = ANTI_GAMING / "dependency_graph_generator.py"
    result = subprocess.run([sys.executable, str(script)], capture_output=True)

    assert result.returncode == 0, f"Expected exit code 0, got {result.returncode}"

    # Check graph file created
    graph_file = ROOT / "02_audit_logging" / "evidence" / "deps" / "dependency_graph.json"
    assert graph_file.exists(), "Graph file not created"

    # Verify graph structure
    with open(graph_file, "r") as f:
        graph = json.load(f)
        assert "metadata" in graph
        assert "nodes" in graph
        assert "edges" in graph
        assert "graph_sha256" in graph

    # Check log
    log_file = ROOT / "02_audit_logging" / "logs" / "anti_gaming_dependency_graph.jsonl"
    assert log_file.exists(), "Log file not created"

    print("  ✓ PASS")

def test_overfitting_detector():
    """Test overfitting detector."""
    print("[TEST] Overfitting Detector...")

    # Ensure metrics exist
    train_metrics = ROOT / "01_ai_layer" / "evidence" / "train_metrics.json"
    eval_metrics = ROOT / "01_ai_layer" / "evidence" / "eval_metrics.json"

    train_metrics.parent.mkdir(parents=True, exist_ok=True)

    # Create test metrics (within threshold)
    with open(train_metrics, "w") as f:
        json.dump({"accuracy": 0.95, "f1": 0.93}, f)

    with open(eval_metrics, "w") as f:
        json.dump({"accuracy": 0.93, "f1": 0.92}, f)

    script = ANTI_GAMING / "overfitting_detector.py"
    result = subprocess.run([sys.executable, str(script)], capture_output=True)

    assert result.returncode in (0, 2), f"Unexpected exit code: {result.returncode}"

    # Check log
    log_file = ROOT / "02_audit_logging" / "logs" / "anti_gaming_overfitting.jsonl"
    assert log_file.exists(), "Log file not created"

    with open(log_file, "r") as f:
        lines = f.readlines()
        last_entry = json.loads(lines[-1])
        assert "gap" in last_entry
        assert "thresholds" in last_entry

    print("  ✓ PASS")

def test_replay_attack_detector():
    """Test replay attack detector."""
    print("[TEST] Replay Attack Detector...")

    # Create test events
    events_file = ROOT / "02_audit_logging" / "evidence" / "identity_events.jsonl"
    events_file.parent.mkdir(parents=True, exist_ok=True)

    now = datetime.now(timezone.utc)
    ts1 = now.isoformat().replace('+00:00', 'Z')
    ts2 = (now + timedelta(seconds=10)).isoformat().replace('+00:00', 'Z')
    events = [
        {"did": "did:ssid:test1", "nonce": "nonce_unique_1", "ts": ts1, "sig": "sig1"},
        {"did": "did:ssid:test2", "nonce": "nonce_unique_2", "ts": ts2, "sig": "sig2"},
    ]

    with open(events_file, "w") as f:
        for event in events:
            f.write(json.dumps(event) + "\n")

    script = ANTI_GAMING / "replay_attack_detector.py"
    result = subprocess.run([sys.executable, str(script)], capture_output=True)

    assert result.returncode in (0, 2), f"Unexpected exit code: {result.returncode}"

    # Check log
    log_file = ROOT / "02_audit_logging" / "logs" / "anti_gaming_replay.jsonl"
    assert log_file.exists(), "Log file not created"

    with open(log_file, "r") as f:
        lines = f.readlines()
        last_entry = json.loads(lines[-1])
        assert "duplicates" in last_entry
        assert "window_minutes" in last_entry

    print("  ✓ PASS")

def test_time_skew_analyzer():
    """Test time skew analyzer."""
    print("[TEST] Time Skew Analyzer...")

    script = ANTI_GAMING / "time_skew_analyzer.py"
    result = subprocess.run([sys.executable, str(script)], capture_output=True)

    assert result.returncode in (0, 2), f"Unexpected exit code: {result.returncode}"

    # Check log
    log_file = ROOT / "02_audit_logging" / "logs" / "anti_gaming_time_skew.jsonl"
    assert log_file.exists(), "Log file not created"

    with open(log_file, "r") as f:
        lines = f.readlines()
        last_entry = json.loads(lines[-1])
        assert "max_skew_seconds" in last_entry
        assert "threshold" in last_entry

    print("  ✓ PASS")

def test_anomaly_rate_guard():
    """Test anomaly rate guard."""
    print("[TEST] Anomaly Rate Guard...")

    script = ANTI_GAMING / "anomaly_rate_guard.py"
    result = subprocess.run([sys.executable, str(script)], capture_output=True)

    assert result.returncode in (0, 2), f"Unexpected exit code: {result.returncode}"

    # Check log
    log_file = ROOT / "02_audit_logging" / "logs" / "anti_gaming_anomaly_rate.jsonl"
    assert log_file.exists(), "Log file not created"

    with open(log_file, "r") as f:
        lines = f.readlines()
        last_entry = json.loads(lines[-1])
        assert "offenders" in last_entry
        assert "limits" in last_entry

    print("  ✓ PASS")

def test_badge_integrity_checker():
    """Test badge integrity checker."""
    print("[TEST] Badge Integrity Checker...")

    script = ANTI_GAMING / "badge_integrity_checker.sh"

    # Make executable
    script.chmod(0o755)

    # Run with bash (Windows-compatible)
    result = subprocess.run(["bash", str(script)], capture_output=True)

    assert result.returncode in (0, 2), f"Unexpected exit code: {result.returncode}"

    # Check log
    log_file = ROOT / "02_audit_logging" / "logs" / "anti_gaming_badge_integrity.jsonl"
    assert log_file.exists(), "Log file not created"

    with open(log_file, "r") as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]
        assert len(lines) > 0, "Log file empty"
        last_entry = json.loads(lines[-1])
        assert "verified" in last_entry
        assert "status" in last_entry

    print("  ✓ PASS")

def main():
    """Run all tests."""
    print("=" * 70)
    print("SSID Anti-Gaming Test Suite")
    print("=" * 70)
    print()

    tests = [
        test_circular_dependency_validator,
        test_dependency_graph_generator,
        test_overfitting_detector,
        test_replay_attack_detector,
        test_time_skew_analyzer,
        test_anomaly_rate_guard,
        test_badge_integrity_checker,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"  ✗ FAIL: {e}")
            failed += 1
        except Exception as e:
            print(f"  ✗ ERROR: {e}")
            failed += 1

    print()
    print("=" * 70)
    print(f"Results: {passed}/{len(tests)} passed, {failed} failed")
    print("=" * 70)

    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
