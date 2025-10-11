"""
Comprehensive tests for detect_duplicate_identity_hashes module.
Tests all edge cases and ensures 80%+ code coverage.
"""
import pytest
from typing import List
import sys
from pathlib import Path

# Add repo root to path
repo_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(repo_root))

# Import using importlib to handle module names starting with numbers
import importlib.util
spec = importlib.util.spec_from_file_location(
    "detect_duplicate_identity_hashes",
    repo_root / "23_compliance" / "anti_gaming" / "detect_duplicate_identity_hashes.py"
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
detect_duplicate_identity_hashes = module.detect_duplicate_identity_hashes


def test_no_duplicates():
    """Test with unique hashes only."""
    result = detect_duplicate_identity_hashes(["a", "b", "c"])
    assert result == []


def test_with_duplicates():
    """Test with multiple duplicate hashes."""
    result = detect_duplicate_identity_hashes(["x", "y", "x", "z", "y"])
    assert result == ["x", "y"]


def test_empty_list():
    """Test with empty input."""
    result = detect_duplicate_identity_hashes([])
    assert result == []


def test_single_element():
    """Test with single hash (no duplicates possible)."""
    result = detect_duplicate_identity_hashes(["single"])
    assert result == []


def test_all_duplicates():
    """Test when all hashes are the same."""
    result = detect_duplicate_identity_hashes(["same", "same", "same", "same"])
    # Implementation returns each unique duplicate once
    assert result == ["same"]


def test_triple_duplicates():
    """Test hash appearing three times."""
    result = detect_duplicate_identity_hashes(["a", "b", "a", "c", "a"])
    # Implementation returns each unique duplicate once
    assert result == ["a"]


def test_preserves_order():
    """Test that duplicates are returned in order of first duplicate occurrence."""
    result = detect_duplicate_identity_hashes(["hash1", "hash2", "hash3", "hash2", "hash1"])
    assert result == ["hash2", "hash1"]


def test_realistic_sha256_hashes():
    """Test with realistic SHA-256 hash values."""
    hash1 = "5d41402abc4b2a76b9719d911017c592"
    hash2 = "7d793037a0760186574b0282f2f435e7"
    hash3 = "5d41402abc4b2a76b9719d911017c592"  # duplicate of hash1

    result = detect_duplicate_identity_hashes([hash1, hash2, hash3])
    assert result == [hash1]
    assert len(result) == 1


def test_with_generator_input():
    """Test with generator/iterator input instead of list."""
    def hash_generator():
        yield "h1"
        yield "h2"
        yield "h1"

    result = detect_duplicate_identity_hashes(hash_generator())
    assert result == ["h1"]


def test_large_dataset():
    """Test performance with large dataset (1000 hashes)."""
    hashes = [f"hash_{i % 100}" for i in range(1000)]  # 10 duplicates per hash
    result = detect_duplicate_identity_hashes(hashes)

    # Should have 100 unique hashes that were duplicated
    assert len(result) == 100


def test_unicode_hashes():
    """Test with unicode strings."""
    result = detect_duplicate_identity_hashes(["café", "naïve", "café", "résumé"])
    assert result == ["café"]


def test_numeric_string_hashes():
    """Test with numeric strings."""
    result = detect_duplicate_identity_hashes(["123", "456", "123", "789"])
    assert result == ["123"]


def test_consecutive_duplicates():
    """Test with consecutive duplicate hashes."""
    result = detect_duplicate_identity_hashes(["a", "a", "b", "b", "c", "c"])
    assert result == ["a", "b", "c"]
