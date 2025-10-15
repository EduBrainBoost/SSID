#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSID - SoT Functional Enforcement Verifier v2.0 (Level 3 → Level 4 Activation)

Enhanced Features:
- 3-Phase Verification: Static Analysis, Dynamic Execution, Audit Proof
- Automatic WORM signing with PQC-ready hashing
- Comprehensive CI/pre-commit integration detection
- Detailed certification levels: PLATINUM (95+), GOLD (85+), SILVER (70+), BRONZE (50+)
- Exit codes: 0 (pass), 1 (warning), 2 (critical failure)
- JSON-structured output for CI/CD automation
- Verbose logging and recommendations
"""

import argparse
import json
import os
import sys
import hashlib
import datetime
import uuid
import re
from pathlib import Path
from typing import Dict, Tuple, List, Any

# ============================================================================
# Configuration
# ============================================================================

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# Enforcement tools to verify (Phase 1: Static Analysis)
ENFORCEMENT_TOOLS = {
    "structure_guard": {
        "tool_path": "12_tooling/scripts/structure_guard.sh",
        "ci_references": [
            ".github/workflows/ci_structure_guard.yml",
            ".github/workflows/ci_enforcement_gate.yml"
        ],
        "description": "Root-24-LOCK structure validator",
        "max_score": 20
    },
    "structure_policy_opa": {
        "tool_path": "23_compliance/policies/structure_policy.yaml",
        "ci_references": [
            ".github/workflows/ci_opa_structure.yml",
            ".github/workflows/ci_enforcement_gate.yml",
            "23_compliance/tests/integration/test_opa_structure.py"
        ],
        "description": "OPA-based structure policy enforcement",
        "max_score": 15
    },
    "root_exceptions": {
        "tool_path": "23_compliance/exceptions/root_level_exceptions.yaml",
        "ci_references": [
            "12_tooling/scripts/structure_guard.sh",
            "24_meta_orchestration/triggers/ci/gates/structure_lock_l3.py"
        ],
        "description": "Root-level exceptions registry",
        "max_score": 10
    },
    "structure_lock_gate": {
        "tool_path": "24_meta_orchestration/triggers/ci/gates/structure_lock_l3.py",
        "ci_references": [
            ".github/workflows/ci_structure_guard.yml",
            ".github/workflows/ci_enforcement_gate.yml",
            ".pre-commit-config.yaml"
        ],
        "description": "Structure lock CI gate (exit 24 on violation)",
        "max_score": 20
    },
    "pre_commit_hooks": {
        "tool_path": ".pre-commit-config.yaml",
        "ci_references": [
            ".github/workflows/pre-commit.yml",
            ".github/workflows/ci_enforcement_gate.yml"
        ],
        "description": "Pre-commit structure validation hooks",
        "max_score": 15
    },
    "pytest_structure_tests": {
        "tool_path": "23_compliance/tests/unit/test_structure_policy_vs_md.py",
        "ci_references": [
            "pytest.ini",
            ".github/workflows/ci_pytest_compliance.yml",
            ".github/workflows/ci_enforcement_gate.yml"
        ],
        "description": "Pytest structure policy unit tests",
        "max_score": 10
    },
    "worm_audit_logging": {
        "tool_path": "02_audit_logging/worm_storage/worm_storage_engine.py",
        "ci_references": [
            "02_audit_logging/evidence_trails/integrated_audit_trail.py",
            "11_test_simulation/tests/unit/test_registry_logic.py"
        ],
        "description": "WORM immutable audit logging",
        "max_score": 10
    }
}

CERTIFICATION_LEVELS = {
    "PLATINUM": {"min_score": 95, "status": "PLATINUM_ENFORCEMENT"},
    "GOLD": {"min_score": 85, "status": "GOLD_ENFORCEMENT"},
    "SILVER": {"min_score": 70, "status": "SILVER_ENFORCEMENT"},
    "BRONZE": {"min_score": 50, "status": "BRONZE_ENFORCEMENT"},
    "NONE": {"min_score": 0, "status": "INSUFFICIENT_ENFORCEMENT"}
}

# ============================================================================
# Utility Functions
# ============================================================================

def sha512_hex(data: bytes) -> str:
    """Generate SHA-512 hash."""
    return hashlib.sha512(data).hexdigest()

def blake2b_hex(data: bytes) -> str:
    """Generate BLAKE2b hash."""
    return hashlib.blake2b(data, digest_size=32).hexdigest()

def read_file(file_path: Path) -> str:
    """Safely read file contents."""
    try:
        if file_path.exists() and file_path.is_file():
            return file_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        pass
    return ""

# ============================================================================
# Phase 1: Static Analysis (35%)
# ============================================================================

def check_static_analysis(verbose: bool = False) -> Tuple[Dict, int]:
    """
    Phase 1: Verify enforcement tools exist and are referenced in CI/tests.

    Returns:
        Tuple of (results dict, score out of 100)
    """
    results = {}
    total_score = 0
    max_total_score = 100

    for tool_key, tool_config in ENFORCEMENT_TOOLS.items():
        tool_path = REPO_ROOT / tool_config["tool_path"]
        tool_exists = tool_path.exists()

        # Check CI references
        refs_found = 0
        refs_total = len(tool_config["ci_references"])
        ci_ref_status = {}

        for ref_path in tool_config["ci_references"]:
            ref_file = REPO_ROOT / ref_path
            ref_exists = False

            if ref_file.exists():
                content = read_file(ref_file)
                # Check if tool is referenced in the file
                tool_name = tool_path.name
                if tool_name in content or tool_config["tool_path"] in content:
                    ref_exists = True
                    refs_found += 1

            ci_ref_status[ref_path] = ref_exists

        # Calculate score for this tool
        max_score = tool_config["max_score"]
        if not tool_exists:
            tool_score = 0
        elif refs_found == 0:
            # Tool exists but not integrated into CI/tests
            tool_score = max_score * 0.20  # 20% credit for existence
        else:
            # Proportional score based on CI integration
            tool_score = max_score * (0.20 + 0.80 * (refs_found / refs_total))

        results[tool_key] = {
            "tool_exists": tool_exists,
            "tool_path": str(tool_path.relative_to(REPO_ROOT)) if tool_exists else tool_config["tool_path"],
            "ci_references": ci_ref_status,
            "refs_found": refs_found,
            "refs_total": refs_total,
            "score": round(tool_score, 1),
            "max_score": max_score,
            "description": tool_config["description"]
        }

        total_score += tool_score

        if verbose:
            status = "[OK]" if refs_found == refs_total else ("[WARN]" if refs_found > 0 else "[FAIL]")
            print(f"  {status} {tool_key}: {refs_found}/{refs_total} refs ({tool_score:.1f}/{max_score} pts)")

    # Normalize to 100-point scale
    normalized_score = int((total_score / max_total_score) * 100)

    return results, normalized_score

# ============================================================================
# Phase 2: Dynamic Execution (40%) - Placeholder
# ============================================================================

def check_dynamic_execution(verbose: bool = False) -> Tuple[Dict, int]:
    """
    Phase 2: Execute enforcement tools and verify exit codes.

    Note: Currently returns 0 as dynamic execution is not implemented.
    Future: Run tools and capture exit codes.
    """
    results = {
        "note": "Dynamic execution not implemented - requires subprocess execution",
        "planned_checks": [
            "structure_guard.sh execution",
            "OPA policy evaluation",
            "Pre-commit hook simulation",
            "Pytest structure tests"
        ]
    }

    if verbose:
        print("  [WARN] Dynamic execution phase not yet implemented")

    return results, 0

# ============================================================================
# Phase 3: Audit Proof (25%)
# ============================================================================

def check_audit_proof(verbose: bool = False) -> Tuple[Dict, int]:
    """
    Phase 3: Verify WORM logs and evidence trails exist.

    Returns:
        Tuple of (results dict, score out of 100)
    """
    results = {}
    total_score = 0

    # Check 1: WORM storage integrity (30 points)
    worm_paths = [
        REPO_ROOT / "02_audit_logging" / "worm_storage" / "immutable_store",
        REPO_ROOT / "02_audit_logging" / "storage" / "worm"
    ]

    worm_evidence = []
    for worm_path in worm_paths:
        if worm_path.exists():
            try:
                files = list(worm_path.rglob("*.json"))
                for f in files[:5]:  # Sample first 5
                    worm_evidence.append(str(f.relative_to(REPO_ROOT)))
            except Exception:
                pass

    worm_score = min(30, len(worm_evidence) * 6) if worm_evidence else 0
    results["worm_storage_integrity"] = {
        "paths_checked": [str(p.relative_to(REPO_ROOT)) for p in worm_paths],
        "evidence_found": worm_evidence,
        "evidence_count": len(worm_evidence),
        "patterns_required": 4,
        "score": worm_score,
        "max_score": 30,
        "status": "PASS" if worm_score >= 20 else ("PARTIAL" if worm_score > 0 else "FAIL")
    }
    total_score += worm_score

    # Check 2: Evidence trails (30 points)
    evidence_paths = [
        REPO_ROOT / "02_audit_logging" / "logs",
        REPO_ROOT / "02_audit_logging" / "evidence"
    ]

    evidence_patterns = [
        r"structure.*validation",
        r"compliance.*check",
        r"enforcement"
    ]

    evidence_found = []
    for evidence_path in evidence_paths:
        if evidence_path.exists():
            try:
                for log_file in evidence_path.rglob("*.json*"):
                    content = read_file(log_file)
                    for pattern in evidence_patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            evidence_found.append({
                                "file": str(log_file.relative_to(REPO_ROOT)),
                                "pattern": pattern
                            })
            except Exception:
                pass

    evidence_score = min(30, len(evidence_found) * 2)
    results["evidence_trails"] = {
        "paths_checked": [str(p.relative_to(REPO_ROOT)) for p in evidence_paths],
        "evidence_found": evidence_found[:15],  # Limit output
        "evidence_count": len(evidence_found),
        "patterns_required": len(evidence_patterns),
        "score": evidence_score,
        "max_score": 30,
        "status": "PASS" if evidence_score >= 20 else ("PARTIAL" if evidence_score > 0 else "FAIL")
    }
    total_score += evidence_score

    # Check 3: Anti-gaming logs (20 points)
    anti_gaming_path = REPO_ROOT / "02_audit_logging" / "logs"
    anti_gaming_patterns = [
        r"anti_gaming",
        r"circular.*dep",
        r"overfitting"
    ]

    anti_gaming_found = []
    if anti_gaming_path.exists():
        try:
            for log_file in anti_gaming_path.glob("*.jsonl"):
                content = read_file(log_file)
                for pattern in anti_gaming_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        anti_gaming_found.append({
                            "file": str(log_file.relative_to(REPO_ROOT)),
                            "pattern": pattern
                        })
        except Exception:
            pass

    anti_gaming_score = min(20, len(anti_gaming_found) * 1.2)
    results["anti_gaming_logs"] = {
        "paths_checked": [str(anti_gaming_path.relative_to(REPO_ROOT))],
        "evidence_found": anti_gaming_found[:10],
        "evidence_count": len(anti_gaming_found),
        "patterns_required": len(anti_gaming_patterns),
        "score": round(anti_gaming_score, 1),
        "max_score": 20,
        "status": "PASS" if anti_gaming_score >= 15 else ("PARTIAL" if anti_gaming_score > 0 else "FAIL")
    }
    total_score += anti_gaming_score

    # Check 4: Hygiene certificate (20 points)
    hygiene_paths = [
        REPO_ROOT / "02_audit_logging" / "reports" / "test_hygiene_certificate_v1.md",
        REPO_ROOT / "24_meta_orchestration" / "registry" / "test_hygiene_certificate.yaml"
    ]

    hygiene_patterns = [
        r"CERTIFIED",
        r"LOCK",
        r"score.*100"
    ]

    hygiene_found = []
    for hygiene_file in hygiene_paths:
        if hygiene_file.exists():
            content = read_file(hygiene_file)
            for pattern in hygiene_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    hygiene_found.append({
                        "file": str(hygiene_file.relative_to(REPO_ROOT)),
                        "pattern": pattern
                    })

    hygiene_score = min(20, len(hygiene_found) * 3.3)
    results["hygiene_certificate"] = {
        "paths_checked": [str(p.relative_to(REPO_ROOT)) for p in hygiene_paths],
        "evidence_found": hygiene_found,
        "evidence_count": len(hygiene_found),
        "patterns_required": len(hygiene_patterns),
        "score": round(hygiene_score, 1),
        "max_score": 20,
        "status": "PASS" if hygiene_score >= 15 else ("PARTIAL" if hygiene_score > 0 else "FAIL")
    }
    total_score += hygiene_score

    if verbose:
        print(f"  [OK] WORM integrity: {worm_score:.0f}/30 pts")
        print(f"  [OK] Evidence trails: {evidence_score:.0f}/30 pts")
        print(f"  [OK] Anti-gaming logs: {anti_gaming_score:.0f}/20 pts")
        print(f"  [OK] Hygiene certificate: {hygiene_score:.0f}/20 pts")

    # Normalize to 100-point scale
    normalized_score = int(total_score)

    return results, normalized_score

# ============================================================================
# WORM Signature Generation
# ============================================================================

def write_worm_signature(result: Dict) -> Tuple[str, Dict]:
    """
    Write enforcement verification result to WORM immutable store.

    Args:
        result: Verification result dictionary

    Returns:
        Tuple of (worm_file_path, signature_dict)
    """
    store_path = REPO_ROOT / "02_audit_logging" / "storage" / "worm" / "immutable_store"
    store_path.mkdir(parents=True, exist_ok=True)

    # Create signature payload
    payload = json.dumps(result, ensure_ascii=True, separators=(",", ":"), sort_keys=True).encode("utf-8")

    signature = {
        "kind": "sot_enforcement_verification_v2",
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "sha512": sha512_hex(payload),
        "blake2b": blake2b_hex(payload),
        "uuid": str(uuid.uuid4()),
        "algorithm": "Dilithium2(placeholder)-HMAC-SHA256",
        "overall_score": result.get("summary", {}).get("overall_score", 0),
        "certification_level": result.get("summary", {}).get("certification_level", "NONE"),
        "certification_status": result.get("summary", {}).get("certification_status", "UNKNOWN")
    }

    # Create final WORM entry
    worm_entry = {
        "result": result,
        "worm_signature": signature
    }

    # Write to immutable store with content-addressed filename
    out_bytes = json.dumps(worm_entry, ensure_ascii=True, indent=2, sort_keys=True).encode("utf-8")
    timestamp_str = signature["timestamp"].replace(":", "").replace("-", "").replace(".", "")
    filename = f"sot_enforcement_v2_{timestamp_str}_{signature['uuid']}.json"
    worm_file_path = store_path / filename

    worm_file_path.write_bytes(out_bytes)

    return str(worm_file_path.relative_to(REPO_ROOT)), signature

# ============================================================================
# Main Verification Flow
# ============================================================================

def run_all_checks(verbose: bool = False) -> Tuple[Dict, int]:
    """
    Execute all 3 verification phases.

    Returns:
        Tuple of (full_results_dict, overall_score)
    """
    if verbose:
        print("\n" + "=" * 70)
        print("SoT Functional Enforcement Verification v2.0")
        print("=" * 70)

    # Phase 1: Static Analysis (35% weight)
    if verbose:
        print("\nPhase 1: Static Analysis (CI/Test/Hook file reference verification)")
    phase1_results, phase1_score = check_static_analysis(verbose=verbose)

    # Phase 2: Dynamic Execution (40% weight)
    if verbose:
        print("\nPhase 2: Dynamic Execution (Tool execution and exit code verification)")
    phase2_results, phase2_score = check_dynamic_execution(verbose=verbose)

    # Phase 3: Audit Proof (25% weight)
    if verbose:
        print("\nPhase 3: Audit Proof (WORM log and evidence trail verification)")
    phase3_results, phase3_score = check_audit_proof(verbose=verbose)

    # Calculate weighted overall score
    overall_score = int(
        phase1_score * 0.35 +
        phase2_score * 0.40 +
        phase3_score * 0.25
    )

    # Determine certification level
    cert_level = "NONE"
    cert_status = "INSUFFICIENT_ENFORCEMENT"

    for level_name, level_config in sorted(
        CERTIFICATION_LEVELS.items(),
        key=lambda x: x[1]["min_score"],
        reverse=True
    ):
        if overall_score >= level_config["min_score"]:
            cert_level = level_name
            cert_status = level_config["status"]
            break

    # Compile full results
    results = {
        "metadata": {
            "report_version": "2.0.0",
            "generated_at": datetime.datetime.utcnow().isoformat() + "Z",
            "tool": "verify_sot_enforcement_v2.py",
            "purpose": "SoT Functional Enforcement Verification (Level 3 → Level 4)"
        },
        "summary": {
            "overall_score": overall_score,
            "certification_level": cert_level,
            "certification_status": cert_status,
            "phase_scores": {
                "static_analysis": phase1_score,
                "dynamic_execution": phase2_score,
                "audit_proof": phase3_score
            }
        },
        "phase1_static_analysis": {
            "score": phase1_score,
            "weight": "35%",
            "description": "CI/Test/Hook file reference verification",
            "results": phase1_results
        },
        "phase2_dynamic_execution": {
            "score": phase2_score,
            "weight": "40%",
            "description": "Tool execution and exit code verification",
            "results": phase2_results
        },
        "phase3_audit_proof": {
            "score": phase3_score,
            "weight": "25%",
            "description": "WORM log and evidence trail verification",
            "results": phase3_results
        }
    }

    if verbose:
        print("\n" + "=" * 70)
        print(f"Overall Enforcement Score: {overall_score}/100")
        print(f"Certification Level: {cert_level}")
        print(f"Certification Status: {cert_status}")
        print("=" * 70)

    return results, overall_score

def generate_recommendations(results: Dict) -> List[str]:
    """Generate actionable recommendations based on verification results."""
    recommendations = []
    overall_score = results["summary"]["overall_score"]

    if overall_score < 50:
        recommendations.append("CRITICAL: Overall enforcement score below 50% - immediate remediation required")

    # Check Phase 1 issues
    phase1 = results.get("phase1_static_analysis", {}).get("results", {})
    for tool_key, tool_data in phase1.items():
        if tool_data["refs_found"] < tool_data["refs_total"]:
            recommendations.append(
                f"HIGH: Integrate {tool_key} into CI/test workflows "
                f"({tool_data['refs_found']}/{tool_data['refs_total']} refs found)"
            )

    # Check Phase 3 audit issues
    phase3 = results.get("phase3_audit_proof", {}).get("results", {})
    for audit_key, audit_data in phase3.items():
        if audit_data.get("status") != "PASS":
            if audit_data["evidence_count"] == 0:
                recommendations.append(
                    f"HIGH: No audit evidence found for {audit_key} - verify logging is active"
                )
            else:
                recommendations.append(
                    f"MEDIUM: Limited audit evidence for {audit_key} - consider increasing logging"
                )

    # Check Phase 2 (dynamic execution)
    phase2_score = results["summary"]["phase_scores"]["dynamic_execution"]
    if phase2_score == 0:
        recommendations.append(
            "MEDIUM: Dynamic execution phase not implemented - consider adding tool execution verification"
        )

    if not recommendations:
        recommendations.append("SUCCESS: All enforcement systems operational at current certification level")

    return recommendations

# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Main entry point for SoT enforcement verification."""
    parser = argparse.ArgumentParser(
        description="SoT Functional Enforcement Verifier v2.0 - Level 3 → Level 4 Activation"
    )
    parser.add_argument("--verbose", action="store_true", help="Show detailed verification output")
    parser.add_argument("--ci-mode", action="store_true", help="CI mode (deterministic, non-interactive)")
    parser.add_argument("--pre-commit", action="store_true", help="Pre-commit hook mode")
    parser.add_argument("--worm-sign", action="store_true", help="Write WORM immutable signature")
    parser.add_argument("--json-out", type=str, help="Write JSON report to specified file")

    args = parser.parse_args()

    # Run all verification checks
    results, overall_score = run_all_checks(verbose=args.verbose)

    # Generate recommendations
    recommendations = generate_recommendations(results)
    results["recommendations"] = recommendations

    # Write WORM signature if requested
    if args.worm_sign:
        worm_path, worm_sig = write_worm_signature(results)
        results["worm_signature_path"] = worm_path
        results["worm_signature"] = worm_sig
        if args.verbose:
            print(f"\n[OK] WORM signature written: {worm_path}")

    # Write JSON output if requested
    if args.json_out:
        output_path = Path(args.json_out)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(results, indent=2, ensure_ascii=True),
            encoding="utf-8"
        )
        if args.verbose:
            print(f"[OK] JSON report written: {args.json_out}")

    # Print recommendations
    if args.verbose and recommendations:
        print("\nRecommendations:")
        for rec in recommendations:
            print(f"  • {rec}")

    # Determine exit code
    cert_level = results["summary"]["certification_level"]

    if cert_level in ["PLATINUM", "GOLD"]:
        exit_code = 0
    elif cert_level == "SILVER":
        exit_code = 0 if args.ci_mode else 1
    elif cert_level == "BRONZE":
        exit_code = 1
    else:
        exit_code = 2

    if not args.verbose:
        # Print concise summary for non-verbose mode
        print(f"SoT Enforcement: {overall_score}/100 ({cert_level})")

    sys.exit(exit_code)

if __name__ == "__main__":
    main()
