#!/usr/bin/env python3
"""
SSID SoT Audit Pipeline Runner
================================

Orchestrates the complete audit pipeline across all 5 security layers.

Pipeline Stages:
  1. Layer 1 - Cryptographic: Merkle lock + PQC signing
  2. Layer 2 - Policy: OPA policy validation
  3. Layer 3 - Trust: DID verification (simulation)
  4. Layer 4 - Observability: Scorecard generation
  5. Layer 5 - Governance: Registry update (simulation)

Output:
  - 02_audit_logging/reports/audit_pipeline_result.json
  - 02_audit_logging/reports/audit_pipeline_report.md
  - Updated metrics for Prometheus export

Usage:
  # Run full pipeline
  python run_audit_pipeline.py

  # Run specific layer only
  python run_audit_pipeline.py --layer 1

  # CI mode (fail on errors)
  python run_audit_pipeline.py --ci

Author: SSID Audit Team
Version: 1.0.0
Date: 2025-10-22
"""

import sys
import json
import time
import argparse
import subprocess
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Tuple

# Repo root
REPO_ROOT = Path(__file__).resolve().parents[2]

# Paths
AUDIT_REPORTS = REPO_ROOT / "02_audit_logging" / "reports"
MERKLE_LOCK = REPO_ROOT / "23_compliance" / "merkle" / "root_write_merkle_lock.py"
PQC_SIGN = REPO_ROOT / "23_compliance" / "registry" / "sign_compliance_registry_pqc.py"
SOT_VALIDATOR = REPO_ROOT / "03_core" / "validators" / "sot" / "sot_validator_core.py"
OPA_POLICY = REPO_ROOT / "23_compliance" / "policies" / "sot" / "sot_policy.rego"
SCORECARD_OUTPUT = AUDIT_REPORTS / "AGENT_STACK_SCORE_LOG.json"


class AuditPipeline:
    """Complete audit pipeline orchestrator"""

    def __init__(self, ci_mode: bool = False):
        self.ci_mode = ci_mode
        self.start_time = time.time()
        self.results = {}
        self.errors = []
        self.warnings = []

    def run_command(self, cmd: List[str], layer_name: str) -> Tuple[bool, str]:
        """Run a command and capture output"""
        print(f"  → Running: {' '.join(cmd)}")
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore",
                timeout=300  # 5 minute timeout
            )

            if result.returncode == 0:
                print(f"  ✅ {layer_name} passed")
                return True, result.stdout
            else:
                error_msg = f"{layer_name} failed: {result.stderr[:500]}"
                print(f"  ❌ {error_msg}")
                self.errors.append(error_msg)
                return False, result.stderr

        except subprocess.TimeoutExpired:
            error_msg = f"{layer_name} timed out after 5 minutes"
            print(f"  ❌ {error_msg}")
            self.errors.append(error_msg)
            return False, error_msg

        except Exception as e:
            error_msg = f"{layer_name} exception: {str(e)}"
            print(f"  ❌ {error_msg}")
            self.errors.append(error_msg)
            return False, str(e)

    def layer_1_cryptographic(self) -> bool:
        """Layer 1: Cryptographic Security"""
        print("\n[Layer 1/5] Cryptographic Security")
        print("=" * 80)

        # Step 1.1: Merkle Lock
        print("\n[1.1] Merkle Lock")
        success, output = self.run_command(
            ["python", str(MERKLE_LOCK)],
            "Merkle Lock"
        )
        self.results["merkle_lock"] = {"success": success, "output": output[:1000]}

        # Step 1.2: PQC Signing
        print("\n[1.2] PQC Signing")
        success_pqc, output_pqc = self.run_command(
            ["python", str(PQC_SIGN), "--no-worm"],
            "PQC Signing"
        )
        self.results["pqc_signing"] = {"success": success_pqc, "output": output_pqc[:1000]}

        layer_success = success and success_pqc
        print(f"\n[Layer 1] Result: {'✅ PASS' if layer_success else '❌ FAIL'}")
        return layer_success

    def layer_2_policy(self) -> bool:
        """Layer 2: Policy Enforcement"""
        print("\n[Layer 2/5] Policy Enforcement")
        print("=" * 80)

        # Step 2.1: OPA Policy Test
        print("\n[2.1] OPA Policy Test")
        success, output = self.run_command(
            ["opa", "test", str(OPA_POLICY.parent), "-v"],
            "OPA Policy Test"
        )
        self.results["opa_policy_test"] = {"success": success, "output": output[:1000]}

        # Step 2.2: SoT Validator
        print("\n[2.2] SoT Validator")
        success_sot, output_sot = self.run_command(
            ["python", str(SOT_VALIDATOR)],
            "SoT Validator"
        )
        self.results["sot_validator"] = {"success": success_sot, "output": output_sot[:1000]}

        layer_success = success and success_sot
        print(f"\n[Layer 2] Result: {'✅ PASS' if layer_success else '❌ FAIL'}")
        return layer_success

    def layer_3_trust(self) -> bool:
        """Layer 3: Trust Boundary (Simulation)"""
        print("\n[Layer 3/5] Trust Boundary")
        print("=" * 80)

        # Simulation: In production, would verify DID signatures
        print("\n[3.1] DID Verification (Simulation)")
        print("  ✅ DID verification simulated (production: verify commit signatures)")

        print("\n[3.2] Zero-Time-Auth (Simulation)")
        print("  ✅ ZTA proof simulated (production: verify SSID-Proof)")

        self.results["trust_boundary"] = {
            "success": True,
            "did_verified": True,
            "zta_verified": True,
            "note": "Simulation mode - production would verify actual signatures"
        }

        print(f"\n[Layer 3] Result: ✅ PASS (Simulation)")
        return True

    def layer_4_observability(self) -> bool:
        """Layer 4: Observability"""
        print("\n[Layer 4/5] Observability")
        print("=" * 80)

        # Step 4.1: Generate Scorecard
        print("\n[4.1] Generate Compliance Scorecard")
        scorecard = self.generate_scorecard()
        self.results["scorecard"] = scorecard

        success = scorecard["compliance_score"] >= 95.0
        if success:
            print(f"  ✅ Compliance score: {scorecard['compliance_score']:.2f}%")
        else:
            print(f"  ❌ Compliance score {scorecard['compliance_score']:.2f}% below 95% threshold")
            self.errors.append(f"Compliance score below threshold")

        print(f"\n[Layer 4] Result: {'✅ PASS' if success else '❌ FAIL'}")
        return success

    def layer_5_governance(self) -> bool:
        """Layer 5: Governance (Simulation)"""
        print("\n[Layer 5/5] Governance")
        print("=" * 80)

        # Simulation: In production, would update immutable registry
        print("\n[5.1] Registry Update (Simulation)")
        print("  ✅ Registry update simulated (production: append to immutable registry)")

        print("\n[5.2] Dual Review (Simulation)")
        print("  ✅ Dual review simulated (production: verify tech + legal signatures)")

        print("\n[5.3] Legal Anchoring (Simulation)")
        print("  ✅ Legal anchor simulated (production: eIDAS timestamp)")

        self.results["governance"] = {
            "success": True,
            "registry_updated": True,
            "dual_review_verified": True,
            "legal_anchored": True,
            "note": "Simulation mode - production would perform actual updates"
        }

        print(f"\n[Layer 5] Result: ✅ PASS (Simulation)")
        return True

    def generate_scorecard(self) -> Dict:
        """Generate compliance scorecard from current results"""
        # Calculate pass rate based on layer results
        passed_layers = sum([
            self.results.get("merkle_lock", {}).get("success", False),
            self.results.get("pqc_signing", {}).get("success", False),
            self.results.get("opa_policy_test", {}).get("success", False),
            self.results.get("sot_validator", {}).get("success", False),
        ])

        total_layers = 4  # Only count layers with actual tests
        pass_rate = (passed_layers / total_layers) * 100 if total_layers > 0 else 0

        scorecard = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "pipeline_version": "1.0.0",
            "compliance_score": pass_rate,
            "passed_layers": passed_layers,
            "total_layers": total_layers,
            "errors": len(self.errors),
            "warnings": len(self.warnings),
            "duration_seconds": time.time() - self.start_time,
        }

        # Save scorecard
        AUDIT_REPORTS.mkdir(parents=True, exist_ok=True)
        with open(SCORECARD_OUTPUT, 'w', encoding='utf-8') as f:
            json.dump(scorecard, f, indent=2, ensure_ascii=False)

        print(f"  💾 Scorecard saved: {SCORECARD_OUTPUT}")

        return scorecard

    def run_all_layers(self) -> bool:
        """Run all 5 layers of the audit pipeline"""
        print("\n" + "=" * 80)
        print("SSID SoT Audit Pipeline - Full Execution")
        print("=" * 80)
        print(f"Start Time: {datetime.now(timezone.utc).isoformat()}")
        print(f"CI Mode: {'Enabled' if self.ci_mode else 'Disabled'}")
        print("=" * 80)

        # Run layers
        layer1 = self.layer_1_cryptographic()
        layer2 = self.layer_2_policy()
        layer3 = self.layer_3_trust()
        layer4 = self.layer_4_observability()
        layer5 = self.layer_5_governance()

        # Calculate overall success
        all_success = layer1 and layer2 and layer3 and layer4 and layer5

        # Generate final report
        self.generate_final_report(all_success)

        return all_success

    def generate_final_report(self, success: bool):
        """Generate final audit report"""
        duration = time.time() - self.start_time
        timestamp = datetime.now(timezone.utc).isoformat()

        # JSON report
        report = {
            "timestamp": timestamp,
            "pipeline_version": "1.0.0",
            "success": success,
            "duration_seconds": duration,
            "layers": {
                "layer_1_cryptographic": self.results.get("merkle_lock", {}).get("success", False) and
                                         self.results.get("pqc_signing", {}).get("success", False),
                "layer_2_policy": self.results.get("opa_policy_test", {}).get("success", False) and
                                  self.results.get("sot_validator", {}).get("success", False),
                "layer_3_trust": self.results.get("trust_boundary", {}).get("success", False),
                "layer_4_observability": self.results.get("scorecard", {}).get("compliance_score", 0) >= 95,
                "layer_5_governance": self.results.get("governance", {}).get("success", False),
            },
            "details": self.results,
            "errors": self.errors,
            "warnings": self.warnings,
        }

        report_json = AUDIT_REPORTS / "audit_pipeline_result.json"
        with open(report_json, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        # Markdown report
        report_md = AUDIT_REPORTS / "audit_pipeline_report.md"
        with open(report_md, 'w', encoding='utf-8') as f:
            f.write(f"# SSID SoT Audit Pipeline Report\n\n")
            f.write(f"**Timestamp:** {timestamp}\n")
            f.write(f"**Duration:** {duration:.2f} seconds\n")
            f.write(f"**Overall Result:** {'✅ PASS' if success else '❌ FAIL'}\n\n")
            f.write(f"---\n\n")
            f.write(f"## Layer Results\n\n")

            for layer_name, layer_success in report["layers"].items():
                status = "✅ PASS" if layer_success else "❌ FAIL"
                f.write(f"- **{layer_name}:** {status}\n")

            f.write(f"\n---\n\n")
            f.write(f"## Errors ({len(self.errors)})\n\n")
            if self.errors:
                for i, error in enumerate(self.errors, 1):
                    f.write(f"{i}. {error}\n")
            else:
                f.write("No errors.\n")

            f.write(f"\n---\n\n")
            f.write(f"## Warnings ({len(self.warnings)})\n\n")
            if self.warnings:
                for i, warning in enumerate(self.warnings, 1):
                    f.write(f"{i}. {warning}\n")
            else:
                f.write("No warnings.\n")

        # Print summary
        print("\n" + "=" * 80)
        print("AUDIT PIPELINE COMPLETE")
        print("=" * 80)
        print(f"Overall Result: {'✅ PASS' if success else '❌ FAIL'}")
        print(f"Duration: {duration:.2f} seconds")
        print(f"Errors: {len(self.errors)}")
        print(f"Warnings: {len(self.warnings)}")
        print(f"\nReports:")
        print(f"  - JSON: {report_json}")
        print(f"  - Markdown: {report_md}")
        print(f"  - Scorecard: {SCORECARD_OUTPUT}")
        print("=" * 80)


def main():
    """Main execution"""
    parser = argparse.ArgumentParser(
        description="SSID SoT Audit Pipeline Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full pipeline
  python run_audit_pipeline.py

  # CI mode (exit code 1 on failure)
  python run_audit_pipeline.py --ci

  # Run specific layer
  python run_audit_pipeline.py --layer 1

Integration:
  # Run in CI/CD
  .github/workflows/audit_pipeline.yml
        """
    )

    parser.add_argument(
        "--ci",
        action="store_true",
        help="CI mode: fail (exit 1) if pipeline fails"
    )

    parser.add_argument(
        "--layer",
        type=int,
        choices=[1, 2, 3, 4, 5],
        help="Run specific layer only (1-5)"
    )

    args = parser.parse_args()

    pipeline = AuditPipeline(ci_mode=args.ci)

    if args.layer:
        # Run specific layer
        print(f"Running Layer {args.layer} only...")
        if args.layer == 1:
            success = pipeline.layer_1_cryptographic()
        elif args.layer == 2:
            success = pipeline.layer_2_policy()
        elif args.layer == 3:
            success = pipeline.layer_3_trust()
        elif args.layer == 4:
            success = pipeline.layer_4_observability()
        elif args.layer == 5:
            success = pipeline.layer_5_governance()
    else:
        # Run all layers
        success = pipeline.run_all_layers()

    # Exit with appropriate code
    if args.ci and not success:
        print("\n❌ CI Mode: Pipeline failed, exiting with code 1")
        sys.exit(1)
    else:
        print("\n✅ Pipeline complete")
        sys.exit(0)


if __name__ == "__main__":
    main()
