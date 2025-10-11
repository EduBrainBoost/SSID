#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Duplicate Identity Hash Detection
Anti-Gaming Module - Detects identity hash reuse (score manipulation)
"""

import json
import hashlib
from pathlib import Path
from typing import Iterable, List, Dict
from datetime import datetime, timezone


def detect_duplicate_identity_hashes(identity_hashes: Iterable[str]) -> List[str]:
    """
    Return a list of duplicate hashes preserving first-seen order.
    A hash is considered duplicate if encountered more than once.

    Args:
        identity_hashes: Iterable of identity hash strings

    Returns:
        List of duplicate hashes in order of first duplicate occurrence
    """
    seen = set()
    dupes = []
    for h in identity_hashes:
        if h in seen:
            if h not in dupes:  # Only add each duplicate once
                dupes.append(h)
        else:
            seen.add(h)
    return dupes


def analyze_hash_dataset(hash_list: List[str]) -> Dict:
    """
    Comprehensive analysis of identity hash dataset for gaming detection.

    Args:
        hash_list: List of identity hashes

    Returns:
        Dict with analysis results including duplicates, statistics, risk level
    """
    duplicates = detect_duplicate_identity_hashes(hash_list)
    unique_count = len(set(hash_list))
    total_count = len(hash_list)
    duplicate_rate = len(duplicates) / total_count if total_count > 0 else 0.0

    # Risk assessment
    if duplicate_rate == 0:
        risk_level = "NONE"
    elif duplicate_rate < 0.01:
        risk_level = "LOW"
    elif duplicate_rate < 0.05:
        risk_level = "MEDIUM"
    else:
        risk_level = "HIGH"

    return {
        "total_hashes": total_count,
        "unique_hashes": unique_count,
        "duplicate_hashes": duplicates,
        "duplicate_count": len(duplicates),
        "duplicate_rate": round(duplicate_rate, 4),
        "risk_level": risk_level,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


def generate_evidence_report(analysis: Dict, output_path: Path) -> None:
    """
    Generate evidence report for audit trail.

    Args:
        analysis: Analysis results from analyze_hash_dataset
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

    # Test with sample data
    test_hashes = [
        "abc123",
        "def456",
        "abc123",  # duplicate
        "ghi789",
        "def456",  # duplicate
        "abc123",  # duplicate again
    ]

    print("=" * 60)
    print("Duplicate Identity Hash Detection - Test Run")
    print("=" * 60)

    # Run analysis
    result = analyze_hash_dataset(test_hashes)

    print(f"\nTotal hashes analyzed: {result['total_hashes']}")
    print(f"Unique hashes: {result['unique_hashes']}")
    print(f"Duplicate count: {result['duplicate_count']}")
    print(f"Duplicate rate: {result['duplicate_rate']:.2%}")
    print(f"Risk level: {result['risk_level']}")

    if result['duplicate_hashes']:
        print(f"\nDuplicate hashes detected:")
        for h in result['duplicate_hashes']:
            print(f"  - {h}")

    # Generate evidence
    repo_root = Path(__file__).resolve().parents[2]
    evidence_path = repo_root / "23_compliance" / "evidence" / "anti_gaming" / f"duplicate_hashes_{datetime.now(timezone.utc).strftime('%Y%m%d')}.json"
    generate_evidence_report(result, evidence_path)

    print(f"\nEvidence report: {evidence_path}")
    print("\n[OK] Test complete" if result['duplicate_count'] > 0 else "\n[OK] No duplicates detected")

    sys.exit(0 if result['risk_level'] in ["NONE", "LOW"] else 1)
