"""
Central Test Fixtures and Utilities for SSID Test Suite

Provides shared fixtures for:
- Audit log data
- Hash chains
- Health endpoints
- Dependency graphs
- Badge data
- Time freezing

Version: Sprint 2 Week 5-6 Day 2
"""

# ============================================================================
# CRITICAL IMPORT ORDER - DO NOT CHANGE
# Set up sys.path FIRST, before any other imports
# ============================================================================

import sys
from pathlib import Path

# Execute IMMEDIATELY when this module is imported (before pytest collection)
_root = Path(__file__).parent.parent
_critical_modules = [
    "02_audit_logging",
    "03_core",
    "08_identity_score",
    "23_compliance",
    "24_meta_orchestration"
]

for _module_name in _critical_modules:
    _module_path = _root / _module_name
    if _module_path.exists() and str(_module_path) not in sys.path:
        sys.path.insert(0, str(_module_path))

# NOW import other modules after sys.path is set up
import pytest
from datetime import datetime
import hashlib

# ============================================================================
# pytest_configure - Additional configuration
# ============================================================================

def pytest_configure(config):
    """
    Configure pytest BEFORE test collection starts.
    Path setup is already done at module import time above.
    """
    # Paths already set up - this is just a backup
    pass

# ============================================================================
# Import Helper for Number-Prefixed Modules
# ============================================================================

def add_module_path(module_name):
    """
    Add number-prefixed module to sys.path for imports.

    Example:
        add_module_path("02_audit_logging")
        from validators.check_hash_chain import validate_hash_chain
    """
    root = Path(__file__).parent.parent
    module_path = root / module_name
    if module_path.exists() and str(module_path) not in sys.path:
        sys.path.insert(0, str(module_path))

# Auto-add critical modules to path (backward compatibility)
CRITICAL_MODULES = [
    "02_audit_logging",
    "03_core",
    "08_identity_score",
    "23_compliance",
    "24_meta_orchestration"
]

for module in CRITICAL_MODULES:
    add_module_path(module)

# ============================================================================
# Audit Logging Fixtures
# ============================================================================

@pytest.fixture
def sample_audit_log():
    """
    Sample audit log entries for testing validators.

    Returns:
        List of dict with audit log structure
    """
    return [
        {
            "ts": "2025-01-01T00:00:00Z",
            "level": "INFO",
            "message": "Test event 1",
            "source": "unit-test",
            "hash": "abc123def456",
            "user_id": "user_001"
        },
        {
            "ts": "2025-01-01T00:01:00Z",
            "level": "WARN",
            "message": "Test event 2",
            "source": "unit-test",
            "hash": "def456abc789",
            "user_id": "user_002"
        }
    ]

@pytest.fixture
def sample_hash_chain():
    """
    Sample hash chain for testing hash chain validators.

    Returns:
        List of dict representing a valid hash chain
    """
    def compute_hash(index, prev_hash, payload):
        """Compute deterministic hash for chain link"""
        data = f"{index}|{prev_hash}|{payload}"
        return hashlib.sha256(data.encode()).hexdigest()

    # Genesis block
    genesis_hash = compute_hash(0, "GENESIS", "genesis_payload")

    chain = [
        {
            "index": 0,
            "payload": "genesis_payload",
            "prev_hash": "GENESIS",
            "hash": genesis_hash,
            "timestamp": "2025-01-01T00:00:00Z"
        }
    ]

    # Add 3 more blocks
    for i in range(1, 4):
        prev_block = chain[-1]
        payload = f"payload_{i}"
        block_hash = compute_hash(i, prev_block["hash"], payload)

        chain.append({
            "index": i,
            "payload": payload,
            "prev_hash": prev_block["hash"],
            "hash": block_hash,
            "timestamp": f"2025-01-01T00:0{i}:00Z"
        })

    return chain

# ============================================================================
# Health Check Fixtures
# ============================================================================

@pytest.fixture
def mock_health_endpoint(monkeypatch):
    """
    Mock HTTP health endpoint for testing health checkers.

    Usage:
        def test_health(mock_health_endpoint):
            result = health_checker.check()
            assert result["status"] == "healthy"
    """
    def mock_get(*args, **kwargs):
        class MockResponse:
            status_code = 200
            text = '{"status": "healthy"}'

            def json(self):
                return {"status": "healthy"}

        return MockResponse()

    try:
        import requests
        monkeypatch.setattr("requests.get", mock_get)
    except ImportError:
        pass  # requests not installed

@pytest.fixture
def sample_health_data():
    """
    Sample health check response data.

    Returns:
        Dict with health check structure
    """
    return {
        "status": "healthy",
        "timestamp": "2025-01-01T00:00:00Z",
        "checks": {
            "database": {"status": "ok", "latency_ms": 5},
            "cache": {"status": "ok", "latency_ms": 2},
            "api": {"status": "ok", "latency_ms": 10}
        },
        "uptime_seconds": 3600
    }

# ============================================================================
# Dependency Graph Fixtures
# ============================================================================

@pytest.fixture
def sample_dependency_graph():
    """
    Sample dependency graph for testing graph generators/validators.

    Returns:
        Dict with nodes and edges
    """
    return {
        "nodes": ["A", "B", "C", "D"],
        "edges": [
            ("A", "B"),
            ("A", "C"),
            ("B", "D"),
            ("C", "D")
        ]
    }

@pytest.fixture
def sample_circular_dependencies():
    """
    Sample dependency graph WITH circular dependencies.

    Returns:
        Dict with nodes and edges containing cycles
    """
    return {
        "nodes": ["A", "B", "C"],
        "edges": [
            ("A", "B"),
            ("B", "C"),
            ("C", "A")  # Cycle: A -> B -> C -> A
        ]
    }

# ============================================================================
# Badge/Signature Fixtures
# ============================================================================

@pytest.fixture
def sample_badge_data():
    """
    Sample badge data for testing badge integrity checkers.

    Returns:
        Dict with badge structure
    """
    return {
        "id": "badge_test_123",
        "signature": "abc123def456789",
        "issued_at": "2025-01-01T00:00:00Z",
        "expires_at": "2026-01-01T00:00:00Z",
        "data": {
            "score": 90,
            "level": "gold",
            "user_id": "user_001",
            "achievements": ["first_login", "verified_identity"]
        }
    }

@pytest.fixture
def sample_tampered_badge():
    """
    Sample tampered badge (data modified but signature unchanged).

    Returns:
        Dict with tampered badge structure
    """
    return {
        "id": "badge_test_456",
        "signature": "original_signature_xyz",
        "issued_at": "2025-01-01T00:00:00Z",
        "data": {
            "score": 95,  # Modified from original!
            "level": "platinum",  # Modified!
            "user_id": "user_002"
        }
    }

# ============================================================================
# Time Fixtures
# ============================================================================

@pytest.fixture
def freeze_time_2025():
    """
    Freeze time to 2025-01-01 12:00:00 UTC.

    Requires: freezegun (pip install freezegun)

    Usage:
        def test_with_frozen_time(freeze_time_2025):
            # Time is frozen at 2025-01-01 12:00:00
            now = datetime.now()
            assert now.year == 2025
    """
    try:
        from freezegun import freeze_time
        with freeze_time("2025-01-01 12:00:00"):
            yield
    except ImportError:
        pytest.skip("freezegun not installed")

# ============================================================================
# Anti-Gaming Fixtures
# ============================================================================

@pytest.fixture
def sample_event_sequence():
    """
    Sample event sequence for testing anti-gaming detectors.

    Returns:
        List of events with timestamps
    """
    return [
        {"ts": "2025-01-01T12:00:00Z", "user": "alice", "action": "login"},
        {"ts": "2025-01-01T12:00:30Z", "user": "alice", "action": "view"},
        {"ts": "2025-01-01T12:01:00Z", "user": "bob", "action": "login"},
        {"ts": "2025-01-01T12:01:15Z", "user": "alice", "action": "submit"},
        {"ts": "2025-01-01T12:02:00Z", "user": "bob", "action": "view"}
    ]

@pytest.fixture
def sample_anomaly_events():
    """
    Sample event sequence WITH anomalies (rate spike, time skew).

    Returns:
        List of events with suspicious patterns
    """
    # 100 events in 1 second = rate spike
    events = [
        {"ts": "2025-01-01T12:00:00Z", "user": "attacker", "action": "spam"}
        for _ in range(100)
    ]

    # Add time travel event
    events.append({
        "ts": "2025-01-01T11:00:00Z",  # Back in time!
        "user": "attacker",
        "action": "time_skew"
    })

    return events

# ============================================================================
# Identity Score Fixtures
# ============================================================================

@pytest.fixture
def sample_identity_data():
    """
    Sample identity data for score calculation.

    Returns:
        Dict with identity attributes
    """
    return {
        "verified": True,
        "documents": 3,
        "age_days": 365,
        "activity_count": 50,
        "social_links": 2
    }

# ============================================================================
# Anti-Gaming Specific Fixtures (23_compliance/anti_gaming)
# ============================================================================

@pytest.fixture
def sample_valid_badges():
    """
    Sample valid badge records with correct signatures.

    Returns:
        List of dicts with id, payload, sig (valid)
    """
    def sha256(text):
        return hashlib.sha256(text.encode()).hexdigest()

    return [
        {
            "id": "badge-001",
            "payload": "user:alice,merit:kyc_verified",
            "sig": sha256("user:alice,merit:kyc_verified")
        },
        {
            "id": "badge-002",
            "payload": "user:bob,merit:high_trust",
            "sig": sha256("user:bob,merit:high_trust")
        },
        {
            "id": "badge-003",
            "payload": "user:charlie,merit:expert_reviewer",
            "sig": sha256("user:charlie,merit:expert_reviewer")
        }
    ]

@pytest.fixture
def sample_invalid_badges():
    """
    Sample badge records with invalid/tampered signatures.

    Returns:
        List of dicts with id, payload, sig (some invalid)
    """
    def sha256(text):
        return hashlib.sha256(text.encode()).hexdigest()

    return [
        {
            "id": "badge-004",
            "payload": "user:david,merit:early_adopter",
            "sig": "TAMPERED_SIGNATURE_12345"  # Invalid!
        },
        {
            "id": "badge-005",
            "payload": "user:eve,merit:high_volume",
            "sig": sha256("WRONG_PAYLOAD")  # Hash of wrong payload
        },
        {
            "id": "badge-006",
            "payload": "user:frank,merit:moderator",
            "sig": ""  # Empty signature
        }
    ]

@pytest.fixture
def sample_mixed_badges(sample_valid_badges, sample_invalid_badges):
    """
    Mix of valid and invalid badges for batch testing.

    Returns:
        Combined list of valid and invalid badges
    """
    return sample_valid_badges + sample_invalid_badges

@pytest.fixture
def sample_identity_hashes_clean():
    """
    Sample identity hashes with NO duplicates (clean dataset).

    Returns:
        List of unique identity hash strings
    """
    return [
        "abc123def456",
        "789ghi012jkl",
        "345mno678pqr",
        "901stu234vwx",
        "567yza890bcd"
    ]

@pytest.fixture
def sample_identity_hashes_duplicates():
    """
    Sample identity hashes WITH duplicates (gaming attempt).

    Returns:
        List of identity hashes with some duplicates
    """
    return [
        "abc123",  # First occurrence
        "def456",
        "abc123",  # Duplicate!
        "ghi789",
        "def456",  # Duplicate!
        "abc123",  # Duplicate again!
        "jkl012",
        "ghi789"   # Duplicate!
    ]

@pytest.fixture
def sample_dependency_graph_acyclic():
    """
    Sample dependency graph WITHOUT cycles (valid).

    Returns:
        Dict with nodes and edges (directed acyclic graph)
    """
    return {
        "nodes": ["Module_A", "Module_B", "Module_C", "Module_D"],
        "edges": [
            {"from": "Module_A", "to": "Module_B"},
            {"from": "Module_A", "to": "Module_C"},
            {"from": "Module_B", "to": "Module_D"},
            {"from": "Module_C", "to": "Module_D"}
        ],
        "has_cycles": False
    }

@pytest.fixture
def sample_dependency_graph_cyclic():
    """
    Sample dependency graph WITH cycles (invalid).

    Returns:
        Dict with nodes and edges containing circular dependencies
    """
    return {
        "nodes": ["Module_X", "Module_Y", "Module_Z"],
        "edges": [
            {"from": "Module_X", "to": "Module_Y"},
            {"from": "Module_Y", "to": "Module_Z"},
            {"from": "Module_Z", "to": "Module_X"}  # Cycle: X->Y->Z->X
        ],
        "has_cycles": True,
        "cycles": [
            ["Module_X", "Module_Y", "Module_Z", "Module_X"]
        ]
    }

@pytest.fixture
def sample_overfitting_patterns_clean():
    """
    Sample test patterns with normal distribution (no overfitting).

    Returns:
        Dict with test patterns and frequencies
    """
    return {
        "test_login_success": 100,
        "test_login_failure": 95,
        "test_registration": 102,
        "test_profile_update": 98,
        "test_logout": 101
    }

@pytest.fixture
def sample_overfitting_patterns_suspicious():
    """
    Sample test patterns showing overfitting (repeated patterns).

    Returns:
        Dict with test patterns showing suspicious repetition
    """
    return {
        "test_login_success": 1000,  # Way too high!
        "test_login_failure": 5,
        "test_registration": 3,
        "test_profile_update": 2,
        "test_logout": 4
    }

# ============================================================================
# Utility Functions
# ============================================================================

def generate_hash(data: str) -> str:
    """Generate SHA-256 hash for testing"""
    return hashlib.sha256(data.encode()).hexdigest()

@pytest.fixture
def hash_generator():
    """
    Fixture that provides hash generation utility.

    Usage:
        def test_hash(hash_generator):
            h = hash_generator("test")
            assert len(h) == 64
    """
    return generate_hash
