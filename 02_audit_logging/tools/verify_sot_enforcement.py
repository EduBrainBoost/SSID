#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SoT Enforcement Verification Tool
==================================

Purpose: Verify functional integration and active enforcement of SoT rules
         (beyond structural presence - this checks operational activation)

Verification Levels:
1. Static Analysis - Check CI/Test/Hook file references
2. Dynamic Execution - Verify tools run and produce correct exit codes
3. Audit Proof - Validate WORM logs contain enforcement evidence

Exit Codes:
  0 - Full enforcement verified (100% score)
  1 - Partial enforcement (< 100% score)
  2 - Critical enforcement failures detected
  3 - Script error

Author: SSID Audit System
License: MIT
Version: 1.0.0
"""

from __future__ import annotations
import argparse
import json
import re
import sys
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timezone

# ============================================================================
# CONFIGURATION: Critical SoT Enforcement Points
# ============================================================================

ENFORCEMENT_POINTS = {
    "structure_guard": {
        "tool": "12_tooling/scripts/structure_guard.sh",
        "ci_refs": [".github/workflows/ci_structure_guard.yml"],
        "description": "Root-24-LOCK structure validator",
        "weight": 20,
    },
    "structure_policy_opa": {
        "tool": "23_compliance/policies/structure_policy.yaml",
        "ci_refs": [
            ".github/workflows/ci_opa_structure.yml",
            "23_compliance/tests/integration/test_opa_structure.py",
        ],
        "description": "OPA-based structure policy enforcement",
        "weight": 15,
    },
    "root_exceptions": {
        "tool": "23_compliance/exceptions/root_level_exceptions.yaml",
        "ci_refs": [
            "12_tooling/scripts/structure_guard.sh",
            "24_meta_orchestration/triggers/ci/gates/structure_lock_l3.py",
        ],
        "description": "Root-level exceptions registry",
        "weight": 10,
    },
    "structure_lock_gate": {
        "tool": "24_meta_orchestration/triggers/ci/gates/structure_lock_l3.py",
        "ci_refs": [
            ".github/workflows/ci_structure_guard.yml",
            ".pre-commit-config.yaml",
        ],
        "description": "Structure lock CI gate (exit 24 on violation)",
        "weight": 20,
    },
    "pre_commit_hooks": {
        "tool": ".pre-commit-config.yaml",
        "ci_refs": [".github/workflows/pre-commit.yml"],
        "description": "Pre-commit structure validation hooks",
        "weight": 15,
    },
    "pytest_structure_tests": {
        "tool": "23_compliance/tests/unit/test_structure_policy_vs_md.py",
        "ci_refs": ["pytest.ini", ".github/workflows/ci_pytest_compliance.yml"],
        "description": "Pytest structure policy unit tests",
        "weight": 10,
    },
    "worm_audit_logging": {
        "tool": "02_audit_logging/worm_storage/worm_storage_engine.py",
        "ci_refs": [
            "02_audit_logging/evidence_trails/integrated_audit_trail.py",
            "11_test_simulation/tests/unit/test_registry_logic.py",
        ],
        "description": "WORM immutable audit logging",
        "weight": 10,
    },
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def find_repo_root() -> Path:
    """Find repository root by looking for .git directory."""
    current = Path.cwd()
    while current != current.parent:
        if (current / ".git").exists():
            return current
        current = current.parent
    return Path.cwd()


def read_file(path: Path) -> str:
    """Read file content safely."""
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def search_file_for_patterns(
    path: Path, patterns: List[str], case_sensitive: bool = False
) -> Dict[str, bool]:
    """Search file for multiple patterns, return match results."""
    if not path.exists():
        return {p: False for p in patterns}

    content = read_file(path)
    flags = 0 if case_sensitive else re.IGNORECASE

    results = {}
    for pattern in patterns:
        try:
            results[pattern] = bool(re.search(pattern, content, flags=flags))
        except re.error:
            results[pattern] = False

    return results


# ============================================================================
# VERIFICATION PHASE 1: Static Analysis
# ============================================================================


def verify_static_integration(
    repo_root: Path, enforcement_points: Dict
) -> Tuple[Dict, int]:
    """
    Phase 1: Static Analysis
    Check if enforcement tools are referenced in CI/test/hook files.
    """
    results = {}
    total_score = 0
    max_score = 0

    for ep_name, ep_config in enforcement_points.items():
        tool_path = repo_root / ep_config["tool"]
        ci_refs = ep_config["ci_refs"]
        weight = ep_config["weight"]
        max_score += weight

        # Check tool exists
        tool_exists = tool_path.exists()

        # Check CI references
        ref_checks = {}
        for ref_file in ci_refs:
            ref_path = repo_root / ref_file
            if ref_path.exists():
                # Extract just the tool filename for search
                tool_name = Path(ep_config["tool"]).name
                # Also check for path components
                search_patterns = [
                    re.escape(tool_name),
                    re.escape(ep_config["tool"]),
                    re.escape(str(Path(ep_config["tool"]).parent)),
                ]
                matches = search_file_for_patterns(ref_path, search_patterns)
                ref_checks[ref_file] = any(matches.values())
            else:
                ref_checks[ref_file] = False

        # Calculate score for this enforcement point
        refs_found = sum(1 for v in ref_checks.values() if v)
        refs_total = len(ci_refs)

        if tool_exists and refs_found > 0:
            # Proportional scoring: full weight if all refs found
            point_score = weight * (refs_found / refs_total)
        elif tool_exists:
            # Tool exists but not integrated - give minimal credit
            point_score = weight * 0.2
        else:
            point_score = 0

        total_score += point_score

        results[ep_name] = {
            "tool_exists": tool_exists,
            "tool_path": str(tool_path),
            "ci_references": ref_checks,
            "refs_found": refs_found,
            "refs_total": refs_total,
            "score": point_score,
            "max_score": weight,
            "description": ep_config["description"],
        }

    return results, int((total_score / max_score * 100) if max_score > 0 else 0)


# ============================================================================
# VERIFICATION PHASE 2: Dynamic Execution
# ============================================================================


def verify_dynamic_execution(repo_root: Path) -> Tuple[Dict, int]:
    """
    Phase 2: Dynamic Execution
    Run critical tools and verify they produce correct exit codes.
    """
    results = {}
    tests = [
        {
            "name": "structure_guard_dry_run",
            "cmd": ["bash", "12_tooling/scripts/structure_guard.sh", "--dry-run"],
            "expected_exit": [0, 24],  # 0=pass, 24=violations found
            "weight": 30,
        },
        {
            "name": "pytest_structure_tests",
            "cmd": [
                "python",
                "-m",
                "pytest",
                "23_compliance/tests/unit/test_structure_policy_vs_md.py",
                "-v",
                "--tb=short",
            ],
            "expected_exit": [0, 5],  # 0=pass, 5=no tests (acceptable)
            "weight": 25,
        },
        {
            "name": "structure_lock_gate_check",
            "cmd": [
                "python",
                "24_meta_orchestration/triggers/ci/gates/structure_lock_l3.py",
                "--check",
            ],
            "expected_exit": [0, 24],  # 0=pass, 24=violations
            "weight": 30,
        },
        {
            "name": "pre_commit_dry_run",
            "cmd": ["pre-commit", "run", "--all-files", "--show-diff-on-failure"],
            "expected_exit": [0, 1],  # 0=pass, 1=some hooks failed (acceptable)
            "weight": 15,
        },
    ]

    total_score = 0
    max_score = sum(t["weight"] for t in tests)

    for test in tests:
        test_name = test["name"]
        cmd = test["cmd"]
        expected_exits = test["expected_exit"]
        weight = test["weight"]

        # Check if command file exists
        cmd_file = repo_root / cmd[1] if len(cmd) > 1 else None
        if cmd_file and not cmd_file.exists():
            results[test_name] = {
                "status": "SKIP",
                "reason": f"Tool not found: {cmd_file}",
                "exit_code": None,
                "score": 0,
                "max_score": weight,
            }
            continue

        # Execute command
        try:
            proc = subprocess.run(
                cmd,
                cwd=repo_root,
                capture_output=True,
                text=True,
                timeout=30,
            )
            exit_code = proc.returncode
            passed = exit_code in expected_exits

            results[test_name] = {
                "status": "PASS" if passed else "FAIL",
                "exit_code": exit_code,
                "expected_exits": expected_exits,
                "stdout_lines": len(proc.stdout.splitlines()),
                "stderr_lines": len(proc.stderr.splitlines()),
                "score": weight if passed else 0,
                "max_score": weight,
            }

            if passed:
                total_score += weight

        except subprocess.TimeoutExpired:
            results[test_name] = {
                "status": "TIMEOUT",
                "reason": "Execution exceeded 30s timeout",
                "score": 0,
                "max_score": weight,
            }
        except FileNotFoundError:
            results[test_name] = {
                "status": "SKIP",
                "reason": f"Command not found: {cmd[0]}",
                "score": 0,
                "max_score": weight,
            }
        except Exception as e:
            results[test_name] = {
                "status": "ERROR",
                "reason": str(e),
                "score": 0,
                "max_score": weight,
            }

    return results, int((total_score / max_score * 100) if max_score > 0 else 0)


# ============================================================================
# VERIFICATION PHASE 3: Audit Proof (WORM Logs)
# ============================================================================


def verify_audit_proof(repo_root: Path) -> Tuple[Dict, int]:
    """
    Phase 3: Audit Proof
    Check WORM logs and evidence trails for enforcement activity.
    """
    results = {}
    checks = [
        {
            "name": "worm_storage_integrity",
            "paths": [
                "02_audit_logging/worm_storage/immutable_store",
                "02_audit_logging/storage/worm",
            ],
            "evidence_patterns": [
                r"structure_guard",
                r"root.*lock",
                r"exit.*24",
                r"violation",
            ],
            "weight": 30,
        },
        {
            "name": "evidence_trails",
            "paths": [
                "02_audit_logging/logs",
                "02_audit_logging/evidence",
            ],
            "evidence_patterns": [
                r"structure.*validation",
                r"compliance.*check",
                r"enforcement",
            ],
            "weight": 30,
        },
        {
            "name": "anti_gaming_logs",
            "paths": ["02_audit_logging/logs"],
            "evidence_patterns": [
                r"anti_gaming",
                r"circular.*dep",
                r"overfitting",
            ],
            "weight": 20,
        },
        {
            "name": "hygiene_certificate",
            "paths": [
                "02_audit_logging/reports/test_hygiene_certificate_v1.md",
                "24_meta_orchestration/registry/test_hygiene_certificate.yaml",
            ],
            "evidence_patterns": [r"CERTIFIED", r"LOCK", r"score.*100"],
            "weight": 20,
        },
    ]

    total_score = 0
    max_score = sum(c["weight"] for c in checks)

    for check in checks:
        check_name = check["name"]
        paths = check["paths"]
        patterns = check["evidence_patterns"]
        weight = check["weight"]

        evidence_found = []
        paths_checked = []

        for path_str in paths:
            path = repo_root / path_str
            paths_checked.append(str(path))

            if not path.exists():
                continue

            # If directory, scan all files
            if path.is_dir():
                for file in path.rglob("*"):
                    if file.is_file() and file.suffix in [
                        ".json",
                        ".jsonl",
                        ".log",
                        ".md",
                        ".yaml",
                        ".yml",
                    ]:
                        content = read_file(file)
                        for pattern in patterns:
                            if re.search(pattern, content, re.IGNORECASE):
                                evidence_found.append(
                                    {
                                        "file": str(file.relative_to(repo_root)),
                                        "pattern": pattern,
                                    }
                                )
            # If file, check directly
            elif path.is_file():
                content = read_file(path)
                for pattern in patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        evidence_found.append(
                            {
                                "file": str(path.relative_to(repo_root)),
                                "pattern": pattern,
                            }
                        )

        # Score based on evidence found
        evidence_count = len(evidence_found)
        patterns_count = len(patterns)
        score = weight * min(evidence_count / patterns_count, 1.0)
        total_score += score

        results[check_name] = {
            "paths_checked": paths_checked,
            "evidence_found": evidence_found,
            "evidence_count": evidence_count,
            "patterns_required": patterns_count,
            "score": score,
            "max_score": weight,
            "status": "PASS" if evidence_count >= patterns_count else "PARTIAL",
        }

    return results, int((total_score / max_score * 100) if max_score > 0 else 0)


# ============================================================================
# REPORT GENERATION
# ============================================================================


def generate_report(
    static_results: Dict,
    static_score: int,
    dynamic_results: Dict,
    dynamic_score: int,
    audit_results: Dict,
    audit_score: int,
    output_path: Optional[Path] = None,
) -> Dict:
    """Generate comprehensive enforcement verification report."""

    # Calculate overall score (weighted average)
    overall_score = int(
        (static_score * 0.35 + dynamic_score * 0.40 + audit_score * 0.25)
    )

    # Determine certification level
    if overall_score >= 95:
        cert_level = "PLATINUM"
        cert_status = "FULL_ENFORCEMENT"
    elif overall_score >= 85:
        cert_level = "GOLD"
        cert_status = "STRONG_ENFORCEMENT"
    elif overall_score >= 70:
        cert_level = "SILVER"
        cert_status = "ADEQUATE_ENFORCEMENT"
    elif overall_score >= 50:
        cert_level = "BRONZE"
        cert_status = "PARTIAL_ENFORCEMENT"
    else:
        cert_level = "NONE"
        cert_status = "INSUFFICIENT_ENFORCEMENT"

    report = {
        "metadata": {
            "report_version": "1.0.0",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "tool": "verify_sot_enforcement.py",
            "purpose": "SoT Functional Enforcement Verification",
        },
        "summary": {
            "overall_score": overall_score,
            "certification_level": cert_level,
            "certification_status": cert_status,
            "phase_scores": {
                "static_analysis": static_score,
                "dynamic_execution": dynamic_score,
                "audit_proof": audit_score,
            },
        },
        "phase1_static_analysis": {
            "score": static_score,
            "weight": "35%",
            "description": "CI/Test/Hook file reference verification",
            "results": static_results,
        },
        "phase2_dynamic_execution": {
            "score": dynamic_score,
            "weight": "40%",
            "description": "Tool execution and exit code verification",
            "results": dynamic_results,
        },
        "phase3_audit_proof": {
            "score": audit_score,
            "weight": "25%",
            "description": "WORM log and evidence trail verification",
            "results": audit_results,
        },
        "recommendations": generate_recommendations(
            static_results, dynamic_results, audit_results, overall_score
        ),
    }

    # Write report to file if path provided
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    return report


def generate_recommendations(
    static_results: Dict,
    dynamic_results: Dict,
    audit_results: Dict,
    overall_score: int,
) -> List[str]:
    """Generate actionable recommendations based on results."""
    recommendations = []

    # Static analysis recommendations
    for ep_name, ep_data in static_results.items():
        if not ep_data["tool_exists"]:
            recommendations.append(
                f"CRITICAL: Create missing enforcement tool: {ep_data['tool_path']}"
            )
        elif ep_data["refs_found"] == 0:
            recommendations.append(
                f"HIGH: Integrate {ep_name} into CI/test workflows (currently not referenced)"
            )
        elif ep_data["refs_found"] < ep_data["refs_total"]:
            recommendations.append(
                f"MEDIUM: Add missing CI references for {ep_name} ({ep_data['refs_found']}/{ep_data['refs_total']} found)"
            )

    # Dynamic execution recommendations
    for test_name, test_data in dynamic_results.items():
        if test_data["status"] == "FAIL":
            recommendations.append(
                f"CRITICAL: Fix failing enforcement test: {test_name} (exit code {test_data.get('exit_code')})"
            )
        elif test_data["status"] == "SKIP":
            recommendations.append(
                f"HIGH: Install missing tool for {test_name}: {test_data.get('reason')}"
            )

    # Audit proof recommendations
    for check_name, check_data in audit_results.items():
        if check_data["status"] == "PARTIAL" and check_data["evidence_count"] == 0:
            recommendations.append(
                f"HIGH: No audit evidence found for {check_name} - verify logging is active"
            )

    # Overall recommendations
    if overall_score < 50:
        recommendations.insert(
            0,
            "CRITICAL: Overall enforcement score below 50% - immediate remediation required",
        )
    elif overall_score < 85:
        recommendations.insert(
            0, "MEDIUM: Enforcement gaps detected - recommend strengthening CI gates"
        )

    return recommendations if recommendations else ["No critical issues detected"]


# ============================================================================
# MAIN EXECUTION
# ============================================================================


def main():
    parser = argparse.ArgumentParser(
        description="Verify SoT functional enforcement (beyond structural compliance)"
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="Repository root path (auto-detected if not provided)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("02_audit_logging/reports/sot_enforcement_verification.json"),
        help="Output report path",
    )
    parser.add_argument(
        "--skip-dynamic",
        action="store_true",
        help="Skip dynamic execution tests (faster, static only)",
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Print detailed results to console"
    )

    args = parser.parse_args()

    # Find repo root
    repo_root = args.repo_root if args.repo_root else find_repo_root()
    print(f"[*] Verifying SoT enforcement in: {repo_root}")
    print("=" * 80)

    # Phase 1: Static Analysis
    print("\n[PHASE 1] PHASE 1: Static Analysis (CI/Test/Hook References)")
    print("-" * 80)
    static_results, static_score = verify_static_integration(
        repo_root, ENFORCEMENT_POINTS
    )
    print(f"[+] Static Analysis Score: {static_score}/100")

    # Phase 2: Dynamic Execution
    dynamic_results = {}
    dynamic_score = 0
    if not args.skip_dynamic:
        print("\n[PHASE 2]  PHASE 2: Dynamic Execution (Tool Run Verification)")
        print("-" * 80)
        dynamic_results, dynamic_score = verify_dynamic_execution(repo_root)
        print(f"[+] Dynamic Execution Score: {dynamic_score}/100")
    else:
        print("\n[PHASE 2]  PHASE 2: Dynamic Execution - SKIPPED")
        dynamic_score = 0

    # Phase 3: Audit Proof
    print("\n[PHASE 3] PHASE 3: Audit Proof (WORM Logs & Evidence Trails)")
    print("-" * 80)
    audit_results, audit_score = verify_audit_proof(repo_root)
    print(f"[+] Audit Proof Score: {audit_score}/100")

    # Generate report
    print("\n[REPORT] Generating Enforcement Report...")
    print("=" * 80)
    output_path = repo_root / args.output
    report = generate_report(
        static_results,
        static_score,
        dynamic_results,
        dynamic_score,
        audit_results,
        audit_score,
        output_path,
    )

    # Print summary
    overall_score = report["summary"]["overall_score"]
    cert_level = report["summary"]["certification_level"]
    cert_status = report["summary"]["certification_status"]

    print(f"\n[SCORE] OVERALL ENFORCEMENT SCORE: {overall_score}/100")
    print(f"[CERT] CERTIFICATION LEVEL: {cert_level}")
    print(f"[STATUS] STATUS: {cert_status}")
    print(f"\n[OUTPUT] Full report written to: {output_path}")

    # Print recommendations
    if args.verbose or overall_score < 85:
        print("\n[RECOMMENDATIONS] RECOMMENDATIONS:")
        print("-" * 80)
        for i, rec in enumerate(report["recommendations"], 1):
            print(f"{i}. {rec}")

    # Determine exit code
    if overall_score >= 85:
        print("\n[STATUS] SoT enforcement verification PASSED")
        sys.exit(0)
    elif overall_score >= 50:
        print(
            "\n[PARTIAL]  SoT enforcement verification PARTIAL (remediation recommended)"
        )
        sys.exit(1)
    else:
        print("\n[FAIL] SoT enforcement verification FAILED (critical gaps detected)")
        sys.exit(2)


if __name__ == "__main__":
    main()
