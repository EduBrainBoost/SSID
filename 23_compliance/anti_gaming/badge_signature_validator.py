#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Badge Signature Validator
Anti-Gaming Module - Simple badge integrity verification
Complements the comprehensive badge_integrity_checker.py
"""

import hashlib
import json
from pathlib import Path
from typing import List, Dict
from datetime import datetime, timezone


def _sha256_text(txt: str) -> str:
    """
    Compute SHA-256 hash of text.

    Args:
        txt: Text to hash

    Returns:
        Hexadecimal hash string
    """
    return hashlib.sha256(txt.encode("utf-8")).hexdigest()


def verify_badges(records: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Validate integrity of badge records: sig must equal sha256(payload).

    Args:
        records: List of badge dicts with keys: id, payload, sig

    Returns:
        List of invalid badge records with error descriptions
    """
    invalid = []
    for i, r in enumerate(records):
        # Handle non-dict records
        if not isinstance(r, dict):
            invalid.append({
                "id": f"record_{i}",
                "error": "not-a-dict",
                "type": str(type(r).__name__)
            })
            continue

        payload = r.get("payload", "")
        sig = r.get("sig", "")

        # Verify signature matches payload hash
        if _sha256_text(payload) != sig:
            invalid.append({
                "id": r.get("id", "unknown"),
                "error": "invalid-signature",
                "expected": _sha256_text(payload),
                "actual": sig
            })

    return invalid


def analyze_badge_batch(records: List[Dict[str, str]]) -> Dict:
    """
    Comprehensive badge batch analysis.

    Args:
        records: List of badge records

    Returns:
        Dict with analysis results and risk assessment
    """
    invalid_badges = verify_badges(records)
    total = len(records)
    invalid_count = len(invalid_badges)
    valid_count = total - invalid_count
    invalid_rate = invalid_count / total if total > 0 else 0.0

    # Risk assessment
    if invalid_count == 0:
        risk_level = "NONE"
    elif invalid_rate < 0.01:
        risk_level = "LOW"
    elif invalid_rate < 0.05:
        risk_level = "MEDIUM"
    else:
        risk_level = "HIGH"

    return {
        "total_badges": total,
        "valid_badges": valid_count,
        "invalid_badges": invalid_count,
        "invalid_rate": round(invalid_rate, 4),
        "invalid_records": invalid_badges,
        "risk_level": risk_level,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


def generate_evidence_report(analysis: Dict, output_path: Path) -> None:
    """
    Generate evidence report for audit trail.

    Args:
        analysis: Analysis results from analyze_badge_batch
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

    print("=" * 60)
    print("Badge Signature Validator - Test Run")
    print("=" * 60)

    # Test data
    test_badges = [
        {
            "id": "badge-001",
            "payload": "user:alice,merit:kyc_verified",
            "sig": _sha256_text("user:alice,merit:kyc_verified")  # Valid
        },
        {
            "id": "badge-002",
            "payload": "user:bob,merit:high_trust",
            "sig": "invalid_signature_here"  # Invalid!
        },
        {
            "id": "badge-003",
            "payload": "user:charlie,merit:expert_reviewer",
            "sig": _sha256_text("user:charlie,merit:expert_reviewer")  # Valid
        },
        {
            "id": "badge-004",
            "payload": "user:david,merit:early_adopter",
            "sig": "0000000000000000"  # Invalid!
        }
    ]

    # Run analysis
    result = analyze_badge_batch(test_badges)

    print(f"\nTotal badges: {result['total_badges']}")
    print(f"Valid badges: {result['valid_badges']}")
    print(f"Invalid badges: {result['invalid_badges']}")
    print(f"Invalid rate: {result['invalid_rate']:.2%}")
    print(f"Risk level: {result['risk_level']}")

    if result['invalid_records']:
        print(f"\nInvalid badge details:")
        for inv in result['invalid_records']:
            print(f"  - ID: {inv['id']}")
            print(f"    Error: {inv['error']}")
            print(f"    Expected: {inv['expected'][:16]}...")
            print(f"    Actual: {inv['actual'][:16]}...")

    # Generate evidence
    repo_root = Path(__file__).resolve().parents[2]
    evidence_path = repo_root / "23_compliance" / "evidence" / "anti_gaming" / f"badge_validation_{datetime.now(timezone.utc).strftime('%Y%m%d')}.json"
    generate_evidence_report(result, evidence_path)

    print(f"\nEvidence report: {evidence_path}")

    if result['invalid_badges'] > 0:
        print(f"\n[FAIL] {result['invalid_badges']} invalid badge signatures detected!")
        sys.exit(1)
    else:
        print(f"\n[OK] All badge signatures valid")
        sys.exit(0)
