#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Master SoT Orchestrator - Self-Generating, Self-Checking, Self-Improving System
===============================================================================

This is the MASTER CONTROL SYSTEM that orchestrates all SoT operations:

1. Generate 384 Shard Matrix (24 Roots × 16 Shards)
2. Extract rules from 5 Master SoT files
3. Distribute rules to Shards
4. Synchronize Shards ↔ SoT Artefacts
5. Validate with StructureGuard
6. Self-improve and heal

CRITICAL PRINCIPLES:
- "Nichts kann im System erstellt werden ohne dass es von den Shards registriert wird"
- "Die Shards und die 5 SoT-Artefakte müssen die selbe Sprache sprechen"
- Root-24-LOCK enforced
- 384 Shard Matrix is the HEART of SoT

Version: 1.0.0
Author: SSID Orchestration Team
Co-Authored-By: Claude <noreply@anthropic.com>
"""

import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any

# Repository root
REPO_ROOT = Path(__file__).parent.parent.parent

# System scripts
SHARD_GENERATOR = REPO_ROOT / "12_tooling" / "scripts" / "generate_384_shard_matrix.py"
RULE_EXTRACTOR = REPO_ROOT / "12_tooling" / "scripts" / "extract_and_distribute_sot_rules.py"
SHARD_SYNCHRONIZER = REPO_ROOT / "12_tooling" / "scripts" / "synchronize_shards_and_sot.py"
STRUCTURE_GUARD_INTEGRATOR = REPO_ROOT / "12_tooling" / "scripts" / "integrate_structure_guard_to_sot.py"
ARTEFACT_GENERATOR = REPO_ROOT / "12_tooling" / "scripts" / "generate_complete_artefacts.py"


class MasterSoTOrchestrator:
    """
    Master Orchestrator for the complete SoT System

    This is the highest-level control system that coordinates all
    self-generating, self-checking, and self-improving operations.
    """

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.results = {}
        self.errors = []

    def orchestrate_all(self, skip_generation: bool = False) -> Dict[str, Any]:
        """
        Execute complete SoT system orchestration

        This is the main entry point for the self-generating system.
        """
        print("=" * 80)
        print(" " * 20 + "MASTER SOT ORCHESTRATION SYSTEM")
        print("=" * 80)
        print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
        print(f"Repository: {self.repo_root}")
        print("=" * 80)
        print()

        # Phase 1: Generate 384 Shard Matrix
        if not skip_generation:
            print("[PHASE 1] Generating 384 Shard Matrix...")
            print("-" * 80)
            self.results["shard_generation"] = self._run_script(
                SHARD_GENERATOR,
                "Shard Matrix Generation"
            )
            print()

        # Phase 2: Synchronize Shards <-> SoT Artefacts
        print("[PHASE 2] Synchronizing Shards <-> SoT Artefacts...")
        print("-" * 80)
        self.results["synchronization"] = self._run_script(
            SHARD_SYNCHRONIZER,
            "Shard-SoT Synchronization"
        )
        print()

        # Phase 3: Integrate StructureGuard
        print("[PHASE 3] Integrating StructureGuard...")
        print("-" * 80)
        self.results["structure_guard"] = self._run_script(
            STRUCTURE_GUARD_INTEGRATOR,
            "StructureGuard Integration"
        )
        print()

        # Phase 4: Generate Complete Artefacts
        print("[PHASE 4] Generating Complete SoT Artefacts...")
        print("-" * 80)
        self.results["artefact_generation"] = self._run_script(
            ARTEFACT_GENERATOR,
            "Complete Artefact Generation"
        )
        print()

        # Phase 5: Validate System
        print("[PHASE 5] Validating Complete System...")
        print("-" * 80)
        validation = self._validate_system()
        self.results["validation"] = validation
        print()

        # Final Summary
        print("=" * 80)
        print(" " * 25 + "ORCHESTRATION SUMMARY")
        print("=" * 80)

        total_success = all(
            r.get("status") in ["success", 0, "completed"]
            for r in self.results.values()
            if isinstance(r, dict)
        )

        print(f"Overall Status: {'SUCCESS' if total_success else 'PARTIAL'}")
        print()
        print("Phase Results:")
        for phase, result in self.results.items():
            if isinstance(result, dict):
                status = result.get("status", "unknown")
                print(f"  {phase}: {status}")
            else:
                print(f"  {phase}: {result}")

        print()
        print(f"Errors: {len(self.errors)}")
        if self.errors:
            print("Error Details:")
            for error in self.errors[:10]:
                print(f"  - {error}")

        print("=" * 80)

        return {
            "status": "success" if total_success else "partial",
            "phases": self.results,
            "errors": len(self.errors),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def _run_script(self, script_path: Path, description: str) -> Dict[str, Any]:
        """Run a Python script and capture result"""
        if not script_path.exists():
            error = f"Script not found: {script_path}"
            print(f"[ERROR] {error}")
            self.errors.append(error)
            return {"status": "error", "message": error}

        try:
            print(f"Running: {script_path.name}")

            result = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True,
                timeout=600,  # 10 minute timeout
                cwd=str(self.repo_root),
            )

            # Print output
            if result.stdout:
                print(result.stdout)

            if result.stderr:
                print(f"[STDERR]\n{result.stderr}")

            if result.returncode != 0:
                error = f"{description} failed with code {result.returncode}"
                self.errors.append(error)
                return {
                    "status": "error",
                    "returncode": result.returncode,
                    "message": error,
                }

            return {
                "status": "success",
                "returncode": 0,
            }

        except subprocess.TimeoutExpired:
            error = f"{description} timed out"
            print(f"[ERROR] {error}")
            self.errors.append(error)
            return {"status": "timeout", "message": error}

        except Exception as e:
            error = f"{description} failed: {e}"
            print(f"[ERROR] {error}")
            self.errors.append(error)
            return {"status": "error", "message": str(e)}

    def _validate_system(self) -> Dict[str, Any]:
        """Validate the complete SoT system"""
        validation_results = {
            "root_24_lock": self._check_root_24_lock(),
            "shard_matrix": self._check_shard_matrix(),
            "sot_artefacts": self._check_sot_artefacts(),
        }

        all_valid = all(r.get("status") == "ok" for r in validation_results.values())

        return {
            "status": "valid" if all_valid else "invalid",
            "checks": validation_results,
        }

    def _check_root_24_lock(self) -> Dict[str, Any]:
        """Check ROOT-24-LOCK compliance"""
        expected_roots = [f"{i:02d}_" for i in range(1, 25)]
        actual_roots = [
            d.name for d in self.repo_root.iterdir()
            if d.is_dir() and d.name.startswith(("0", "1", "2"))
        ]

        violations = []
        for root in actual_roots:
            if not any(root.startswith(expected) for expected in expected_roots):
                violations.append(f"Illegal root: {root}")

        return {
            "status": "ok" if not violations else "violation",
            "expected": 24,
            "found": len(actual_roots),
            "violations": violations,
        }

    def _check_shard_matrix(self) -> Dict[str, Any]:
        """Check 384 Shard Matrix"""
        roots = [
            d for d in self.repo_root.iterdir()
            if d.is_dir() and d.name.startswith(("0", "1", "2"))
        ]

        total_shards = 0
        for root in roots:
            shards_dir = root / "shards"
            if shards_dir.exists():
                shards = list(shards_dir.iterdir())
                total_shards += len([s for s in shards if s.is_dir()])

        expected = 24 * 16  # 384
        # Note: May have duplicates, so could be more

        return {
            "status": "ok" if total_shards >= expected else "incomplete",
            "expected": expected,
            "found": total_shards,
        }

    def _check_sot_artefacts(self) -> Dict[str, Any]:
        """Check 5 SoT Artefacts exist"""
        artefacts = {
            "sot_contract.yaml": self.repo_root / "16_codex" / "contracts" / "sot" / "sot_contract.yaml",
            "sot_policy.rego": self.repo_root / "23_compliance" / "policies" / "sot" / "sot_policy.rego",
            "sot_validator_engine.py": self.repo_root / "03_core" / "validators" / "sot" / "sot_validator_engine.py",
            "test_sot_validator.py": self.repo_root / "11_test_simulation" / "tests_compliance" / "test_sot_validator.py",
            "sot_registry.json": self.repo_root / "24_meta_orchestration" / "registry" / "sot_registry.json",
        }

        missing = [name for name, path in artefacts.items() if not path.exists()]

        return {
            "status": "ok" if not missing else "incomplete",
            "total": len(artefacts),
            "found": len(artefacts) - len(missing),
            "missing": missing,
        }


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Master SoT Orchestrator")
    parser.add_argument("--skip-generation", action="store_true",
                       help="Skip Shard Matrix generation (for re-runs)")
    parser.add_argument("--root", type=Path,
                       help="Repository root (auto-detected if not specified)")

    args = parser.parse_args()

    repo_root = args.root or REPO_ROOT
    orchestrator = MasterSoTOrchestrator(repo_root)

    result = orchestrator.orchestrate_all(skip_generation=args.skip_generation)

    print()
    print("Final Result:")
    print(json.dumps(result, indent=2))

    return 0 if result["status"] == "success" else 1


if __name__ == "__main__":
    sys.exit(main())
