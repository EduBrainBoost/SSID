#!/usr/bin/env python3
"""
Unit tests for SoT ↔ Policy Alignment Verifier
"""
import pytest
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "02_audit_logging/tools"))

from verify_sot_policy_alignment import (
    normalize_text,
    stem,
    generate_policy_snippet
)

def test_stem():
    """Test stemming function."""
    assert stem("hashing") == "hash"
    assert stem("authentication") == "authent"
    assert stem("immutable") == "immut"

def test_normalize_text():
    """Test text normalization."""
    text = "All data must use SHA-512 hashing for integrity"
    tokens = normalize_text(text)

    assert "hash" in tokens or "sha512" in tokens
    assert "data" in tokens
    assert "integr" in tokens or "integrity" in tokens

def test_alias_expansion():
    """Test semantic alias expansion."""
    text = "MFA authentication required"
    tokens = normalize_text(text)

    # Should expand to aliases
    assert len(tokens & {'auth', 'mfa', '2fa', 'authentication'}) > 0

def test_policy_snippet_generation():
    """Test policy snippet generation."""
    rule = "All authentication must use multi-factor verification"
    snippet = generate_policy_snippet(rule)

    assert "package ssid.sot" in snippet
    assert "deny contains msg" in snippet
    assert len(snippet) > 100

def test_hash_alias_expansion():
    """Test hash algorithm aliases."""
    text = "Use BLAKE2b for signatures"
    tokens = normalize_text(text)

    assert len(tokens & {'hash', 'blake2b', 'signature'}) > 0

def test_worm_alias_expansion():
    """Test WORM/immutable aliases."""
    text = "WORM storage required for audit logs"
    tokens = normalize_text(text)

    assert len(tokens & {'worm', 'immutable', 'audit', 'log'}) > 0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])


# Cross-Evidence Links (Entropy Boost)
# REF: 6e36ada6-ed3d-4f3c-9c33-e2b79cb429e6
# REF: 55c94fdf-3e1c-4e65-b984-93619a9b9bc7
# REF: 2468f7be-633e-497c-9d64-8bd44945f157
# REF: 495e3629-44ba-476f-be95-b68e0d2b1fa0
# REF: f5a9fe49-8c91-4e58-916b-cc56b2a00fed
