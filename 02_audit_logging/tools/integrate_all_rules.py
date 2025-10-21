#!/usr/bin/env python3
"""
Complete Rule Integration Orchestrator v1.0
============================================
Haupt-Orchestrator für automatische Integration aller 384 Regeln über alle 5 SoT-Artefakte.

Führt aus:
1. YAML-Generierung aus Python Validator
2. Test-Generierung aus Python Validator
3. Cross-Artefakt Konsistenz-Verifikation
4. Final Report Generierung

Usage:
    python integrate_all_rules.py --repo /path/to/ssid [--auto-fix]

Options:
    --auto-fix    Automatisch fehlende Regeln ergänzen (wo möglich)
    --strict      Strict mode: Fail bei jeder Inkonsistenz
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List


# ============================================================================
# ORCHESTRATOR
# ============================================================================

class IntegrationOrchestrator:
    """Hauptklasse für vollständige Integration."""

    def __init__(self, repo_root: Path, auto_fix: bool = False, strict: bool = False):
        self.repo_root = repo_root
        self.auto_fix = auto_fix
        self.strict = strict

        # Tool paths
        self.tools_dir = repo_root / "02_audit_logging" / "tools"
        self.yaml_generator = self.tools_dir / "generate_yaml_from_validator.py"
        self.test_generator = self.tools_dir / "generate_tests_from_validator.py"
        self.consistency_verifier = self.tools_dir / "verify_cross_artifact_consistency.py"
        self.rule_counter = self.tools_dir / "automatic_rule_counter.py"

        # Artefakt paths
        self.python_validator = repo_root / "03_core" / "validators" / "sot" / "sot_validator_core.py"
        self.opa_policy = repo_root / "23_compliance" / "policies" / "sot" / "sot_policy.rego"
        self.contract_yaml = repo_root / "16_codex" / "contracts" / "sot" / "sot_contract.yaml"
        self.test_suite = repo_root / "11_test_simulation" / "tests_compliance" / "test_sot_validator.py"

        # Output dir
        self.output_dir = repo_root / "02_audit_logging" / "reports"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run_full_integration(self) -> Dict:
        """Führt vollständige Integration durch."""
        print(f"\n{'='*80}")
        print(f"SSID RULE INTEGRATION ORCHESTRATOR v1.0")
        print(f"{'='*80}")
        print(f"Repository: {self.repo_root}")
        print(f"Auto-fix: {self.auto_fix}")
        print(f"Strict mode: {self.strict}")
        print(f"{'='*80}\n")

        results = {
            "timestamp": datetime.now().isoformat(),
            "repo_root": str(self.repo_root),
            "phases": {}
        }

        # Phase 1: Rule Counting (Baseline)
        print(f"\n[PHASE 1] Baseline Rule Count")
        print(f"{'-'*60}")
        phase1_result = self._run_phase_1_baseline()
        results["phases"]["phase1_baseline"] = phase1_result

        # Phase 2: YAML Generation
        print(f"\n[PHASE 2] YAML Contract Generation")
        print(f"{'-'*60}")
        phase2_result = self._run_phase_2_yaml_generation()
        results["phases"]["phase2_yaml"] = phase2_result

        # Phase 3: Test Generation
        print(f"\n[PHASE 3] Test Suite Generation")
        print(f"{'-'*60}")
        phase3_result = self._run_phase_3_test_generation()
        results["phases"]["phase3_tests"] = phase3_result

        # Phase 4: Consistency Verification
        print(f"\n[PHASE 4] Cross-Artifact Consistency")
        print(f"{'-'*60}")
        phase4_result = self._run_phase_4_consistency()
        results["phases"]["phase4_consistency"] = phase4_result

        # Phase 5: Final Count
        print(f"\n[PHASE 5] Final Rule Count")
        print(f"{'-'*60}")
        phase5_result = self._run_phase_5_final_count()
        results["phases"]["phase5_final"] = phase5_result

        # Save results
        self._save_results(results)

        # Print summary
        self._print_summary(results)

        return results

    def _run_phase_1_baseline(self) -> Dict:
        """Phase 1: Baseline Rule Count."""
        result = {"status": "running"}

        if not self.rule_counter.exists():
            result["status"] = "skipped"
            result["reason"] = "Rule counter not found"
            return result

        try:
            # Run rule counter
            cmd = [
                "python",
                str(self.rule_counter),
                "--repo", str(self.repo_root),
                "--output", str(self.output_dir / "baseline_count.json")
            ]

            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )

            result["exit_code"] = process.returncode
            result["stdout"] = process.stdout[-1000:]  # Last 1000 chars
            result["status"] = "success" if process.returncode == 0 else "warning"

            # Load count data
            count_file = self.output_dir / "baseline_count.json"
            if count_file.exists():
                with open(count_file, 'r') as f:
                    count_data = json.load(f)
                result["total_rules"] = count_data.get("total_rules", 0)
                result["overall_percentage"] = count_data.get("overall_percentage", 0)

        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)

        return result

    def _run_phase_2_yaml_generation(self) -> Dict:
        """Phase 2: Generate YAML from Python validator."""
        result = {"status": "running"}

        if not self.yaml_generator.exists():
            result["status"] = "skipped"
            result["reason"] = "YAML generator not found"
            return result

        try:
            # Run YAML generator
            cmd = [
                "python",
                str(self.yaml_generator),
                "--validator", str(self.python_validator),
                "--output", str(self.output_dir / "sot_contract_generated.yaml")
            ]

            if self.contract_yaml.exists():
                cmd.extend(["--integrate", str(self.contract_yaml)])

            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )

            result["exit_code"] = process.returncode
            result["stdout"] = process.stdout[-1000:]
            result["status"] = "success" if process.returncode == 0 else "error"

        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)

        return result

    def _run_phase_3_test_generation(self) -> Dict:
        """Phase 3: Generate tests from Python validator."""
        result = {"status": "running"}

        if not self.test_generator.exists():
            result["status"] = "skipped"
            result["reason"] = "Test generator not found"
            return result

        try:
            # Run test generator
            cmd = [
                "python",
                str(self.test_generator),
                "--validator", str(self.python_validator),
                "--output", str(self.output_dir / "test_sot_validator_generated.py")
            ]

            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )

            result["exit_code"] = process.returncode
            result["stdout"] = process.stdout[-1000:]
            result["status"] = "success" if process.returncode == 0 else "error"

        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)

        return result

    def _run_phase_4_consistency(self) -> Dict:
        """Phase 4: Verify cross-artifact consistency."""
        result = {"status": "running"}

        if not self.consistency_verifier.exists():
            result["status"] = "skipped"
            result["reason"] = "Consistency verifier not found"
            return result

        try:
            # Run consistency verifier
            cmd = [
                "python",
                str(self.consistency_verifier),
                "--repo", str(self.repo_root),
                "--output", str(self.output_dir / "consistency_report.json")
            ]

            if self.strict:
                cmd.append("--strict")

            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )

            result["exit_code"] = process.returncode
            result["stdout"] = process.stdout[-1000:]
            result["status"] = "success" if process.returncode == 0 else "warning"

            # Load consistency data
            consistency_file = self.output_dir / "consistency_report.json"
            if consistency_file.exists():
                with open(consistency_file, 'r') as f:
                    consistency_data = json.load(f)
                result["consistency_percentage"] = consistency_data.get("consistency_percentage", 0)
                result["issues_count"] = len(consistency_data.get("issues", []))

        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)

        return result

    def _run_phase_5_final_count(self) -> Dict:
        """Phase 5: Final rule count after integration."""
        result = {"status": "running"}

        if not self.rule_counter.exists():
            result["status"] = "skipped"
            result["reason"] = "Rule counter not found"
            return result

        try:
            # Run rule counter again
            cmd = [
                "python",
                str(self.rule_counter),
                "--repo", str(self.repo_root),
                "--output", str(self.output_dir / "final_count.json")
            ]

            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )

            result["exit_code"] = process.returncode
            result["stdout"] = process.stdout[-1000:]
            result["status"] = "success" if process.returncode == 0 else "warning"

            # Load final count data
            count_file = self.output_dir / "final_count.json"
            if count_file.exists():
                with open(count_file, 'r') as f:
                    count_data = json.load(f)
                result["total_rules"] = count_data.get("total_rules", 0)
                result["overall_percentage"] = count_data.get("overall_percentage", 0)

        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)

        return result

    def _save_results(self, results: Dict):
        """Speichert Ergebnisse."""
        output_file = self.output_dir / "integration_results.json"

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"\n[+] Results saved: {output_file}")

    def _print_summary(self, results: Dict):
        """Gibt Zusammenfassung aus."""
        print(f"\n{'='*80}")
        print(f"INTEGRATION SUMMARY")
        print(f"{'='*80}")

        for phase_name, phase_result in results["phases"].items():
            status = phase_result.get("status", "unknown")
            status_symbol = {
                "success": "[OK]",
                "warning": "[WARN]",
                "error": "[FAIL]",
                "skipped": "[SKIP]"
            }.get(status, "[?]")

            print(f"{status_symbol} {phase_name:30s} {status.upper()}")

        # Final metrics
        print(f"\n{'='*80}")
        print(f"FINAL METRICS")
        print(f"{'='*80}")

        baseline = results["phases"].get("phase1_baseline", {})
        final = results["phases"].get("phase5_final", {})

        if "total_rules" in baseline:
            print(f"Baseline Coverage: {baseline.get('overall_percentage', 0):.1f}%")

        if "total_rules" in final:
            print(f"Final Coverage:    {final.get('overall_percentage', 0):.1f}%")

        consistency = results["phases"].get("phase4_consistency", {})
        if "consistency_percentage" in consistency:
            print(f"Consistency:       {consistency.get('consistency_percentage', 0):.1f}%")
            print(f"Issues Found:      {consistency.get('issues_count', 0)}")

        print(f"{'='*80}\n")


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Complete Rule Integration Orchestrator"
    )
    parser.add_argument(
        '--repo',
        type=Path,
        default=Path.cwd(),
        help='Path to SSID repository root'
    )
    parser.add_argument(
        '--auto-fix',
        action='store_true',
        help='Automatically fix missing rules (where possible)'
    )
    parser.add_argument(
        '--strict',
        action='store_true',
        help='Strict mode: fail on any inconsistency'
    )

    args = parser.parse_args()

    # Run orchestrator
    orchestrator = IntegrationOrchestrator(
        repo_root=args.repo,
        auto_fix=args.auto_fix,
        strict=args.strict
    )

    results = orchestrator.run_full_integration()

    # Exit code based on final status
    final_phase = results["phases"].get("phase5_final", {})
    final_coverage = final_phase.get("overall_percentage", 0)

    if final_coverage >= 100.0:
        print(f"\n[SUCCESS] 100% Coverage achieved!")
        sys.exit(0)
    elif final_coverage >= 95.0:
        print(f"\n[SUCCESS] {final_coverage:.1f}% Coverage (>= 95% target)")
        sys.exit(0)
    else:
        print(f"\n[WARNING] {final_coverage:.1f}% Coverage (< 95% target)")
        sys.exit(1 if args.strict else 0)


if __name__ == "__main__":
    main()
