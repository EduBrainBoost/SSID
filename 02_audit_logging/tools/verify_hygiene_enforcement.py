#!/usr/bin/env python3
"""
verify_hygiene_enforcement.py

Continuous Monitoring Script for Test Hygiene Certificate Enforcement

PURPOSE:
--------
This script monitors the test hygiene certificate status to ensure:
1. [LOCK] status remains valid
2. Hash signatures match registry
3. Score log shows no degradation
4. Certificate validity period is maintained until 2026-10-15

This addresses the gap between one-time certificate issuance and continuous validation.

MONITORING CHECKS:
-----------------
1. Certificate Status: Verify [LOCK] status in markdown report
2. Hash Integrity: Compare PQC hashes between report and registry
3. Score Stability: Check score log for any deviations from 100/100
4. Temporal Validity: Ensure certificate hasn't expired
5. File Integrity: Verify all certificate files exist and are readable

EXIT CODES:
-----------
0: All checks passed - certificate valid
1: Warning - minor deviations detected
2: Critical - certificate integrity compromised

USAGE:
------
    python verify_hygiene_enforcement.py [--verbose] [--json]

    --verbose: Show detailed check results
    --json: Output results in JSON format
    --alarm: Trigger alarm on any deviation

INTEGRATION:
-----------
Can be scheduled via:
- GitHub Actions weekly workflow
- Cron job: 0 0 * * 0 python verify_hygiene_enforcement.py --alarm
- Pre-commit hook for critical changes

Author: SSID Compliance Team
Version: 1.0.0
Created: 2025-10-15
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple, Optional


# --- Configuration ---

REPO_ROOT = Path(__file__).resolve().parents[2]

CERTIFICATE_FILES = {
    "report": REPO_ROOT / "02_audit_logging" / "reports" / "test_hygiene_certificate_v1.md",
    "registry": REPO_ROOT / "24_meta_orchestration" / "registry" / "test_hygiene_certificate.yaml",
    "badge": REPO_ROOT / "13_ui_layer" / "assets" / "badges" / "test_hygiene_badge.svg",
    "score_log": REPO_ROOT / "02_audit_logging" / "logs" / "test_hygiene_score_log.json",
}

EXPECTED_CERT_ID = "SSID-TH-2025-10-15-001"
EXPECTED_VALIDITY = {
    "valid_from": "2025-10-15",
    "valid_to": "2026-10-15",
}
EXPECTED_SCORE = 100
EXPECTED_HASH_PATTERN = r"^[a-f0-9]{64}$"  # SHA256 hex


# --- Helper Functions ---

def read_file(path: Path) -> str:
    """Read file content, return empty string on error."""
    try:
        return path.read_text(encoding="utf-8")
    except Exception as e:
        return ""


def check_file_existence() -> Tuple[Dict, int]:
    """
    Phase 1: Verify all certificate files exist and are readable.

    Returns:
        (results_dict, score) where score is 0-20
    """
    results = {}
    score = 0
    max_score = 20
    points_per_file = max_score / len(CERTIFICATE_FILES)

    for file_key, file_path in CERTIFICATE_FILES.items():
        exists = file_path.exists()
        readable = False
        size = 0

        if exists:
            try:
                content = file_path.read_text(encoding="utf-8")
                readable = len(content) > 0
                size = len(content)
            except Exception:
                readable = False

        results[file_key] = {
            "path": str(file_path.relative_to(REPO_ROOT)),
            "exists": exists,
            "readable": readable,
            "size_bytes": size,
            "status": "PASS" if (exists and readable) else "FAIL",
        }

        if exists and readable:
            score += points_per_file

    return results, int(score)


def check_lock_status(report_path: Path) -> Tuple[Dict, int]:
    """
    Phase 2: Verify [LOCK] status in certificate report.

    Returns:
        (results_dict, score) where score is 0-25
    """
    results = {
        "lock_markers_found": [],
        "lock_count": 0,
        "status": "UNKNOWN",
    }
    score = 0
    max_score = 25

    content = read_file(report_path)
    if not content:
        results["status"] = "FAIL"
        results["error"] = "Cannot read certificate report"
        return results, 0

    # Search for [LOCK] markers
    lock_pattern = r"\[LOCK\]"
    matches = re.findall(lock_pattern, content, re.IGNORECASE)

    results["lock_count"] = len(matches)
    results["lock_markers_found"] = matches[:5]  # Show first 5

    # Require at least 1 [LOCK] marker
    if results["lock_count"] >= 1:
        results["status"] = "PASS"
        score = max_score
    else:
        results["status"] = "FAIL"
        results["error"] = "No [LOCK] markers found in certificate report"
        score = 0

    return results, score


def check_hash_integrity(report_path: Path, registry_path: Path) -> Tuple[Dict, int]:
    """
    Phase 3: Verify PQC hash consistency between report and registry.

    Returns:
        (results_dict, score) where score is 0-25
    """
    results = {
        "report_hash": None,
        "registry_hash": None,
        "hashes_match": False,
        "status": "UNKNOWN",
    }
    score = 0
    max_score = 25

    # Extract hash from markdown report
    report_content = read_file(report_path)
    report_hash_match = re.search(r"PQC Hash.*?([a-f0-9]{64})", report_content, re.IGNORECASE | re.DOTALL)
    if report_hash_match:
        results["report_hash"] = report_hash_match.group(1)

    # Extract hash from YAML registry
    registry_content = read_file(registry_path)
    registry_hash_match = re.search(r"pqc_hash:\s*['\"]?([a-f0-9]{64})['\"]?", registry_content, re.IGNORECASE)
    if registry_hash_match:
        results["registry_hash"] = registry_hash_match.group(1)

    # Compare hashes
    if results["report_hash"] and results["registry_hash"]:
        if results["report_hash"] == results["registry_hash"]:
            results["hashes_match"] = True
            results["status"] = "PASS"
            score = max_score
        else:
            results["status"] = "FAIL"
            results["error"] = "Hash mismatch between report and registry"
            score = 0
    else:
        results["status"] = "FAIL"
        results["error"] = "Could not extract hashes from both files"
        score = 0

    return results, score


def check_score_stability(score_log_path: Path) -> Tuple[Dict, int]:
    """
    Phase 4: Verify score log shows 100/100 with no degradation.

    Returns:
        (results_dict, score) where score is 0-20
    """
    results = {
        "log_entries": 0,
        "latest_score": None,
        "score_stable": False,
        "status": "UNKNOWN",
    }
    score = 0
    max_score = 20

    if not score_log_path.exists():
        results["status"] = "FAIL"
        results["error"] = "Score log file does not exist"
        return results, 0

    try:
        content = score_log_path.read_text(encoding="utf-8")
        log_data = json.loads(content)

        if isinstance(log_data, dict):
            # Single entry format
            entries = [log_data]
        elif isinstance(log_data, list):
            # Multiple entries format
            entries = log_data
        else:
            results["status"] = "FAIL"
            results["error"] = "Invalid score log format"
            return results, 0

        results["log_entries"] = len(entries)

        if entries:
            # Check latest entry
            latest = entries[-1]
            latest_score = latest.get("score", latest.get("hygiene_score", None))
            results["latest_score"] = latest_score

            # Verify score is 100
            if latest_score == EXPECTED_SCORE:
                results["score_stable"] = True
                results["status"] = "PASS"
                score = max_score
            else:
                results["status"] = "FAIL"
                results["error"] = f"Score degraded to {latest_score}/100"
                score = int(max_score * (latest_score / EXPECTED_SCORE)) if latest_score else 0
        else:
            results["status"] = "FAIL"
            results["error"] = "Score log is empty"
            score = 0

    except json.JSONDecodeError:
        results["status"] = "FAIL"
        results["error"] = "Score log contains invalid JSON"
        score = 0
    except Exception as e:
        results["status"] = "FAIL"
        results["error"] = f"Error reading score log: {str(e)}"
        score = 0

    return results, score


def check_temporal_validity(report_path: Path) -> Tuple[Dict, int]:
    """
    Phase 5: Verify certificate is within valid date range.

    Returns:
        (results_dict, score) where score is 0-10
    """
    results = {
        "valid_from": None,
        "valid_to": None,
        "current_date": datetime.now(timezone.utc).date().isoformat(),
        "is_valid": False,
        "status": "UNKNOWN",
    }
    score = 0
    max_score = 10

    content = read_file(report_path)
    if not content:
        results["status"] = "FAIL"
        results["error"] = "Cannot read certificate report"
        return results, 0

    # Extract validity dates
    valid_from_match = re.search(r"Valid From:\s*(\d{4}-\d{2}-\d{2})", content, re.IGNORECASE)
    valid_to_match = re.search(r"Valid To:\s*(\d{4}-\d{2}-\d{2})", content, re.IGNORECASE)

    if valid_from_match:
        results["valid_from"] = valid_from_match.group(1)
    if valid_to_match:
        results["valid_to"] = valid_to_match.group(1)

    # Check if current date is within range
    if results["valid_from"] and results["valid_to"]:
        try:
            valid_from_date = datetime.fromisoformat(results["valid_from"]).date()
            valid_to_date = datetime.fromisoformat(results["valid_to"]).date()
            current_date = datetime.now(timezone.utc).date()

            if valid_from_date <= current_date <= valid_to_date:
                results["is_valid"] = True
                results["status"] = "PASS"
                score = max_score
            else:
                results["status"] = "FAIL"
                if current_date < valid_from_date:
                    results["error"] = "Certificate not yet valid"
                else:
                    results["error"] = "Certificate has expired"
                score = 0
        except ValueError:
            results["status"] = "FAIL"
            results["error"] = "Invalid date format"
            score = 0
    else:
        results["status"] = "FAIL"
        results["error"] = "Could not extract validity dates"
        score = 0

    return results, score


def run_all_checks(verbose: bool = False) -> Tuple[Dict, int]:
    """
    Run all hygiene enforcement checks.

    Returns:
        (full_results_dict, overall_score)
    """
    if verbose:
        print("[*] Starting Hygiene Enforcement Verification...")
        print(f"[*] Repository Root: {REPO_ROOT}")
        print()

    results = {
        "metadata": {
            "tool": "verify_hygiene_enforcement.py",
            "version": "1.0.0",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "purpose": "Continuous monitoring of test hygiene certificate",
        },
        "checks": {},
        "summary": {},
    }

    total_score = 0
    max_score = 100

    # Phase 1: File Existence
    if verbose:
        print("[CHECK 1/5] Verifying certificate file existence...")
    check1_results, check1_score = check_file_existence()
    results["checks"]["file_existence"] = {
        "results": check1_results,
        "score": check1_score,
        "max_score": 20,
        "weight": "20%",
    }
    total_score += check1_score
    if verbose:
        print(f"  Score: {check1_score}/20")
        for file_key, file_result in check1_results.items():
            status_icon = "[+]" if file_result["status"] == "PASS" else "[X]"
            print(f"  {status_icon} {file_key}: {file_result['status']}")
        print()

    # Phase 2: [LOCK] Status
    if verbose:
        print("[CHECK 2/5] Verifying [LOCK] status in certificate report...")
    check2_results, check2_score = check_lock_status(CERTIFICATE_FILES["report"])
    results["checks"]["lock_status"] = {
        "results": check2_results,
        "score": check2_score,
        "max_score": 25,
        "weight": "25%",
    }
    total_score += check2_score
    if verbose:
        print(f"  Score: {check2_score}/25")
        print(f"  [LOCK] markers found: {check2_results['lock_count']}")
        print(f"  Status: {check2_results['status']}")
        print()

    # Phase 3: Hash Integrity
    if verbose:
        print("[CHECK 3/5] Verifying PQC hash integrity...")
    check3_results, check3_score = check_hash_integrity(
        CERTIFICATE_FILES["report"],
        CERTIFICATE_FILES["registry"]
    )
    results["checks"]["hash_integrity"] = {
        "results": check3_results,
        "score": check3_score,
        "max_score": 25,
        "weight": "25%",
    }
    total_score += check3_score
    if verbose:
        print(f"  Score: {check3_score}/25")
        report_hash = check3_results.get('report_hash')
        registry_hash = check3_results.get('registry_hash')
        report_hash_display = (report_hash[:16] + "...") if report_hash else "N/A"
        registry_hash_display = (registry_hash[:16] + "...") if registry_hash else "N/A"
        print(f"  Report Hash: {report_hash_display}")
        print(f"  Registry Hash: {registry_hash_display}")
        print(f"  Match: {check3_results['hashes_match']}")
        print()

    # Phase 4: Score Stability
    if verbose:
        print("[CHECK 4/5] Verifying score log stability...")
    check4_results, check4_score = check_score_stability(CERTIFICATE_FILES["score_log"])
    results["checks"]["score_stability"] = {
        "results": check4_results,
        "score": check4_score,
        "max_score": 20,
        "weight": "20%",
    }
    total_score += check4_score
    if verbose:
        print(f"  Score: {check4_score}/20")
        print(f"  Latest Score: {check4_results.get('latest_score', 'N/A')}/100")
        print(f"  Stable: {check4_results['score_stable']}")
        print()

    # Phase 5: Temporal Validity
    if verbose:
        print("[CHECK 5/5] Verifying certificate temporal validity...")
    check5_results, check5_score = check_temporal_validity(CERTIFICATE_FILES["report"])
    results["checks"]["temporal_validity"] = {
        "results": check5_results,
        "score": check5_score,
        "max_score": 10,
        "weight": "10%",
    }
    total_score += check5_score
    if verbose:
        print(f"  Score: {check5_score}/10")
        print(f"  Valid From: {check5_results.get('valid_from', 'N/A')}")
        print(f"  Valid To: {check5_results.get('valid_to', 'N/A')}")
        print(f"  Is Valid: {check5_results['is_valid']}")
        print()

    # Calculate certification level
    if total_score >= 95:
        cert_level = "PLATINUM"
        cert_status = "FULLY_VALID"
    elif total_score >= 85:
        cert_level = "GOLD"
        cert_status = "VALID_WITH_WARNINGS"
    elif total_score >= 70:
        cert_level = "SILVER"
        cert_status = "DEGRADED"
    elif total_score >= 50:
        cert_level = "BRONZE"
        cert_status = "CRITICAL"
    else:
        cert_level = "NONE"
        cert_status = "INVALID"

    results["summary"] = {
        "overall_score": total_score,
        "max_score": max_score,
        "certification_level": cert_level,
        "certification_status": cert_status,
        "all_checks_passed": total_score == max_score,
    }

    return results, total_score


def generate_recommendations(results: Dict) -> List[str]:
    """
    Generate actionable recommendations based on check results.

    Args:
        results: Full results dictionary from run_all_checks()

    Returns:
        List of recommendation strings
    """
    recommendations = []

    # Check file existence issues
    file_check = results["checks"]["file_existence"]
    for file_key, file_result in file_check["results"].items():
        if file_result["status"] != "PASS":
            recommendations.append(
                f"CRITICAL: Certificate file '{file_key}' is missing or unreadable - restore immediately"
            )

    # Check [LOCK] status
    lock_check = results["checks"]["lock_status"]
    if lock_check["results"]["status"] != "PASS":
        recommendations.append(
            "CRITICAL: [LOCK] markers missing from certificate - integrity compromised"
        )

    # Check hash integrity
    hash_check = results["checks"]["hash_integrity"]
    if not hash_check["results"]["hashes_match"]:
        recommendations.append(
            "CRITICAL: PQC hash mismatch between report and registry - possible tampering detected"
        )

    # Check score stability
    score_check = results["checks"]["score_stability"]
    if not score_check["results"]["score_stable"]:
        latest_score = score_check["results"].get("latest_score", 0)
        recommendations.append(
            f"HIGH: Hygiene score degraded to {latest_score}/100 - investigate test failures"
        )

    # Check temporal validity
    temporal_check = results["checks"]["temporal_validity"]
    if not temporal_check["results"]["is_valid"]:
        error = temporal_check["results"].get("error", "unknown")
        recommendations.append(
            f"CRITICAL: Certificate temporal validity failed - {error}"
        )

    # Overall score recommendations
    overall_score = results["summary"]["overall_score"]
    if overall_score < 50:
        recommendations.append(
            "CRITICAL: Overall hygiene score below 50% - certificate is INVALID"
        )
    elif overall_score < 70:
        recommendations.append(
            "HIGH: Overall hygiene score below 70% - certificate is DEGRADED"
        )
    elif overall_score < 95:
        recommendations.append(
            "MEDIUM: Overall hygiene score below 95% - minor issues detected"
        )

    if not recommendations:
        recommendations.append("SUCCESS: All hygiene checks passed - certificate is fully valid")

    return recommendations


def main():
    """Main entry point for hygiene enforcement verification."""
    parser = argparse.ArgumentParser(
        description="Continuous monitoring of test hygiene certificate enforcement"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed check results during execution"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results in JSON format"
    )
    parser.add_argument(
        "--alarm",
        action="store_true",
        help="Trigger alarm (exit code 2) on any deviation"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Write JSON report to specified file"
    )

    args = parser.parse_args()

    # Run all checks
    results, overall_score = run_all_checks(verbose=args.verbose)

    # Generate recommendations
    recommendations = generate_recommendations(results)
    results["recommendations"] = recommendations

    # Output results
    if args.json or args.output:
        json_output = json.dumps(results, indent=2)
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(json_output, encoding="utf-8")
            print(f"[*] Report written to: {args.output}")
        else:
            print(json_output)
    else:
        # Human-readable output
        if not args.verbose:
            print("\n" + "="*70)
            print("HYGIENE ENFORCEMENT VERIFICATION REPORT")
            print("="*70)
            print(f"\nOverall Score: {overall_score}/100")
            print(f"Certification Level: {results['summary']['certification_level']}")
            print(f"Status: {results['summary']['certification_status']}")
            print(f"\nAll Checks Passed: {results['summary']['all_checks_passed']}")
            print("\nRecommendations:")
            for i, rec in enumerate(recommendations, 1):
                print(f"  {i}. {rec}")
            print("\n" + "="*70)

    # Determine exit code
    if overall_score == 100:
        exit_code = 0  # Perfect score
    elif overall_score >= 70:
        exit_code = 1 if args.alarm else 0  # Warning
    else:
        exit_code = 2  # Critical failure

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
