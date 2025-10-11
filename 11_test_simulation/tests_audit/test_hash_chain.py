import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "02_audit_logging"))
from validators.check_hash_chain import validate_hash_chain  # type: ignore

def test_hash_chain_valid():
    import hashlib
    def h(i, prev, payload): 
        return hashlib.sha256(f"{i}|{prev}|{payload}".encode()).hexdigest()
    chain = [
        {"index": 0, "payload": "gen", "prev_hash": "GENESIS", "hash": h(0,"GENESIS","gen")},
        {"index": 1, "payload": "a", "prev_hash": None, "hash": ""},
    ]
    chain[1]["prev_hash"] = chain[0]["hash"]
    chain[1]["hash"] = h(1, chain[0]["hash"], "a")
    res = validate_hash_chain(chain)
    assert res["valid"] is True

def test_hash_chain_invalid_prev():
    import hashlib
    def h(i, prev, payload):
        return hashlib.sha256(f"{i}|{prev}|{payload}".encode()).hexdigest()
    chain = [
        {"index": 0, "payload": "gen", "prev_hash": "GENESIS", "hash": h(0,"GENESIS","gen")},
        {"index": 1, "payload": "a", "prev_hash": "WRONG", "hash": h(1,"WRONG","a")},
    ]
    res = validate_hash_chain(chain)
    assert res["valid"] is False and any("prev-mismatch" in e for e in res["errors"])


# ============================================================================
# Phase 1 Quick Wins: Edge Cases for 100% Coverage
# ============================================================================

def test_hash_chain_bad_genesis():
    """Test that first entry must have prev_hash='GENESIS'"""
    import hashlib
    def h(i, prev, payload):
        return hashlib.sha256(f"{i}|{prev}|{payload}".encode()).hexdigest()

    # First entry with wrong prev_hash
    chain = [
        {"index": 0, "payload": "gen", "prev_hash": "WRONG", "hash": h(0, "WRONG", "gen")}
    ]

    res = validate_hash_chain(chain)

    assert res["valid"] is False, "Chain with bad genesis should fail"
    assert any("bad-genesis-prev" in e for e in res["errors"]), \
        "Should report bad genesis prev_hash"


def test_hash_chain_hash_mismatch():
    """Test detection of tampered hash (doesn't match computed hash)"""
    import hashlib
    def h(i, prev, payload):
        return hashlib.sha256(f"{i}|{prev}|{payload}".encode()).hexdigest()

    # Valid genesis but with tampered hash
    chain = [
        {
            "index": 0,
            "payload": "gen",
            "prev_hash": "GENESIS",
            "hash": "TAMPERED_HASH_123456789"  # Wrong hash!
        }
    ]

    res = validate_hash_chain(chain)

    assert res["valid"] is False, "Chain with hash mismatch should fail"
    assert any("hash-mismatch" in e for e in res["errors"]), \
        "Should report hash mismatch"


def test_hash_chain_multiple_errors():
    """Test chain with multiple errors (bad genesis + hash mismatch)"""
    chain = [
        {
            "index": 0,
            "payload": "gen",
            "prev_hash": "NOT_GENESIS",  # Error 1
            "hash": "WRONG_HASH"  # Error 2
        }
    ]

    res = validate_hash_chain(chain)

    assert res["valid"] is False
    # Should have both errors
    errors_str = " ".join(res["errors"])
    assert "bad-genesis-prev" in errors_str
    assert "hash-mismatch" in errors_str


def test_hash_chain_with_fixture(sample_hash_chain):
    """Test hash chain validation using conftest.py fixture"""
    # Use the sample_hash_chain fixture from conftest.py
    res = validate_hash_chain(sample_hash_chain)

    assert res["valid"] is True, "Valid chain from fixture should pass"
    assert len(res["errors"]) == 0
