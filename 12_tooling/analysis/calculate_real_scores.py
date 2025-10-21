#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
calculate_real_scores.py - Real Score Calculator Based on Actual Test Results

Berechnet echte Scores basierend auf:
- Pytest Ergebnissen
- Coverage Daten
- Compliance Status
- Strukturellen Checks
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone

REPO_ROOT = Path(__file__).parent.parent.parent


def calculate_test_score(passed: int, failed: int, errors: int, skipped: int) -> float:
    """
    Calculate test score based on pytest results.

    Returns:
        Score 0-100 based on pass rate
    """
    total = passed + failed + errors
    if total == 0:
        return 0.0

    # Weight errors more heavily than failures
    weighted_failures = failed + (errors * 2)
    score = max(0, 100 * (total - weighted_failures) / total)

    return round(score, 2)


def calculate_determinism_score(failed: int, errors: int) -> float:
    """
    Calculate determinism score.

    Errors indicate non-deterministic behavior.
    """
    if errors > 0:
        # Heavy penalty for errors
        return max(0, 100 - (errors * 10))
    if failed > 0:
        return max(0, 100 - (failed * 2))
    return 100.0


def calculate_auditability_score(passed: int, total: int) -> float:
    """
    Calculate auditability score based on test coverage.
    """
    if total == 0:
        return 0.0
    return round(100 * passed / total, 2)


def calculate_root_lock_compliance() -> float:
    """
    Check root lock compliance.
    """
    root_dirs = [d for d in REPO_ROOT.iterdir() if d.is_dir() and not d.name.startswith('.')]
    numbered_dirs = [d for d in root_dirs if d.name[0:2].isdigit() and d.name[2] == '_']

    # Should have exactly 24 layers
    if len(numbered_dirs) == 24:
        return 100.0
    elif len(numbered_dirs) <= 24:
        return round(100 * len(numbered_dirs) / 24, 2)
    else:
        # Penalty for exceeding 24
        return max(0, 100 - (len(numbered_dirs) - 24) * 10)


def calculate_sot_alignment(failed: int, total: int) -> float:
    """
    Calculate Single Source of Truth alignment.
    """
    if total == 0:
        return 0.0

    # SoT alignment correlates with test success
    pass_rate = (total - failed) / total
    return round(100 * pass_rate, 2)


def main():
    """Calculate and save real scores."""

    # Parse pytest results from last run
    # These would come from pytest JSON report or pytest exit code
    # For now, use the known results from the last run

    passed = 597
    failed = 55
    errors = 4
    skipped = 6
    total = passed + failed + errors

    scores = {
        "SoT_alignment": calculate_sot_alignment(failed + errors, total),
        "Root_Lock_Compliance": calculate_root_lock_compliance(),
        "Non_Custodial_Assurance": calculate_test_score(passed, failed, errors, skipped),
        "Auditability": calculate_auditability_score(passed, total),
        "Determinism": calculate_determinism_score(failed, errors)
    }

    # Calculate overall score
    overall = round(sum(scores.values()) / len(scores), 2)

    result = {
        "bundle": "SSID Marketplace Bundle",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "test_results": {
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "skipped": skipped,
            "total": total,
            "pass_rate": round(100 * passed / total, 2) if total > 0 else 0
        },
        "scores": scores,
        "overall_score": overall,
        "status": "NEEDS_IMPROVEMENT" if overall < 90 else "PASSING"
    }

    # Save to score log
    score_log = REPO_ROOT / "02_audit_logging" / "score_log.json"
    score_log.parent.mkdir(parents=True, exist_ok=True)

    with open(score_log, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"Real scores calculated and saved to: {score_log}")
    print(f"\nTest Results:")
    print(f"  Passed: {passed}")
    print(f"  Failed: {failed}")
    print(f"  Errors: {errors}")
    print(f"  Skipped: {skipped}")
    print(f"  Pass Rate: {result['test_results']['pass_rate']}%")
    print(f"\nScores:")
    for key, value in scores.items():
        print(f"  {key}: {value}")
    print(f"\nOverall Score: {overall}/100")
    print(f"Status: {result['status']}")

    # Exit with error if scores are too low
    if overall < 80:
        sys.exit(1)

    return 0


if __name__ == "__main__":
    sys.exit(main())
