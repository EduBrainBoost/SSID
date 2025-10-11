"""
Comprehensive tests for badge_integrity_checker module.
Tests all edge cases and ensures 80%+ code coverage.
"""
import pytest
import hashlib
import sys
from pathlib import Path

# Add repo root to path
repo_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(repo_root))

# Import using importlib to handle module names starting with numbers
import importlib.util
spec = importlib.util.spec_from_file_location(
    "badge_signature_validator",
    repo_root / "23_compliance" / "anti_gaming" / "badge_signature_validator.py"
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
verify_badges = module.verify_badges


def _sha256_text_local(t: str) -> str:
    """Local helper for generating test signatures."""
    return hashlib.sha256(t.encode('utf-8')).hexdigest()


def test_all_valid_badges():
    """Test with all valid badge signatures."""
    recs = [
        {"id": "badge_001", "payload": "alpha", "sig": _sha256_text_local("alpha")},
        {"id": "badge_002", "payload": "beta", "sig": _sha256_text_local("beta")},
        {"id": "badge_003", "payload": "gamma", "sig": _sha256_text_local("gamma")},
    ]
    invalid = verify_badges(recs)
    assert len(invalid) == 0
    assert invalid == []


def test_mixed_valid_and_invalid():
    """Test with mix of valid and invalid signatures."""
    recs = [
        {"id": "1", "payload": "alpha", "sig": _sha256_text_local("alpha")},
        {"id": "2", "payload": "beta", "sig": "wrong_signature_here"},
        {"id": "3", "payload": "gamma", "sig": _sha256_text_local("gamma")},
        {"id": "4", "payload": "delta", "sig": "also_wrong"},
    ]
    invalid = verify_badges(recs)

    assert len(invalid) == 2
    assert invalid[0]["id"] == "2"
    assert invalid[0]["error"] == "invalid-signature"
    assert invalid[1]["id"] == "4"
    assert invalid[1]["error"] == "invalid-signature"


def test_empty_payload():
    """Test badge with empty payload."""
    recs = [
        {"id": "empty_badge", "payload": "", "sig": _sha256_text_local("")},
    ]
    invalid = verify_badges(recs)
    assert len(invalid) == 0


def test_missing_fields():
    """Test badges with missing required fields."""
    recs = [
        {"id": "missing_sig", "payload": "data"},  # missing sig
        {"id": "missing_payload", "sig": "somesig"},  # missing payload
        {},  # missing all fields
    ]
    invalid = verify_badges(recs)

    # All should be flagged as invalid (empty sig/payload don't match expected)
    assert len(invalid) == 3


def test_non_dict_records():
    """Test with non-dictionary records."""
    recs = [
        {"id": "valid", "payload": "test", "sig": _sha256_text_local("test")},
        "not_a_dict",
        None,
        42,
    ]
    invalid = verify_badges(recs)

    # Should flag 3 non-dict entries
    assert len(invalid) >= 3
    assert any("not-a-dict" in str(inv.get("error", "")) for inv in invalid)


def test_empty_record_list():
    """Test with empty list of records."""
    invalid = verify_badges([])
    assert invalid == []


def test_unicode_payloads():
    """Test with unicode content in payloads."""
    payload_unicode = "Hello 世界 🌍"
    recs = [
        {"id": "unicode_badge", "payload": payload_unicode, "sig": _sha256_text_local(payload_unicode)},
    ]
    invalid = verify_badges(recs)
    assert len(invalid) == 0


def test_large_payload():
    """Test with large payload content."""
    large_payload = "x" * 10000  # 10KB payload
    recs = [
        {"id": "large", "payload": large_payload, "sig": _sha256_text_local(large_payload)},
    ]
    invalid = verify_badges(recs)
    assert len(invalid) == 0


def test_signature_case_sensitivity():
    """Test that signature comparison is case-sensitive."""
    payload = "test"
    correct_sig = _sha256_text_local(payload)
    wrong_case_sig = correct_sig.upper()  # SHA-256 hex is lowercase

    recs = [
        {"id": "case_test", "payload": payload, "sig": wrong_case_sig},
    ]
    invalid = verify_badges(recs)

    # Should be invalid because of case mismatch
    assert len(invalid) == 1


def test_whitespace_in_payload():
    """Test payload with various whitespace characters."""
    payloads = [
        "  leading_spaces",
        "trailing_spaces  ",
        "mid\ndle\nlines",
        "tab\tseparated",
    ]

    recs = [
        {"id": f"ws_{i}", "payload": p, "sig": _sha256_text_local(p)}
        for i, p in enumerate(payloads)
    ]

    invalid = verify_badges(recs)
    assert len(invalid) == 0


def test_generator_input():
    """Test with generator/iterator input."""
    def badge_generator():
        yield {"id": "gen_1", "payload": "data1", "sig": _sha256_text_local("data1")}
        yield {"id": "gen_2", "payload": "data2", "sig": "wrong"}
        yield {"id": "gen_3", "payload": "data3", "sig": _sha256_text_local("data3")}

    invalid = verify_badges(badge_generator())
    assert len(invalid) == 1
    assert invalid[0]["id"] == "gen_2"


def test_realistic_batch():
    """Test realistic batch of 100 badges with 5% error rate."""
    recs = []
    for i in range(100):
        payload = f"badge_payload_{i}"
        # 5% of badges have wrong signatures
        sig = _sha256_text_local(payload) if i % 20 != 0 else "intentionally_wrong"
        recs.append({"id": f"batch_{i}", "payload": payload, "sig": sig})

    invalid = verify_badges(recs)
    assert len(invalid) == 5  # 100 / 20 = 5 invalid badges


def test_json_payload():
    """Test with JSON-like payload content."""
    import json
    payload_data = {"user": "alice", "score": 95, "timestamp": "2025-10-09T12:00:00Z"}
    payload_str = json.dumps(payload_data, sort_keys=True)

    recs = [
        {"id": "json_badge", "payload": payload_str, "sig": _sha256_text_local(payload_str)},
    ]

    invalid = verify_badges(recs)
    assert len(invalid) == 0


def test_special_characters_in_id():
    """Test badges with special characters in ID field."""
    recs = [
        {"id": "badge/with/slashes", "payload": "data", "sig": _sha256_text_local("data")},
        {"id": "badge:with:colons", "payload": "data2", "sig": _sha256_text_local("data2")},
        {"id": "badge-with-dashes", "payload": "data3", "sig": _sha256_text_local("data3")},
    ]

    invalid = verify_badges(recs)
    assert len(invalid) == 0
