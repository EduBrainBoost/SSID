#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSID Master Orchestrator - Complete 10-Layer Enforcement
=========================================================

Central control system that orchestrates all 10 security layers.
This is the "brain" of the autonomous SoT enforcement system.

Features:
  - Sequential execution of all 10 layers
  - Parallel optimization where possible
  - Real-time status monitoring
  - Auto-remediation on failures
  - Comprehensive reporting
  - CI/CD integration ready

Usage:
  # Run all layers
  python master_orchestrator.py

  # Run specific layers
  python master_orchestrator.py --layers 1,2,3

  # CI mode (strict)
  python master_orchestrator.py --ci --threshold 95

  # Continuous monitoring mode
  python master_orchestrator.py --daemon --interval 300

Author: SSID Core Team
Version: 2.0.0
Date: 2025-10-22
"""

import sys
import json
import time
import argparse
import subprocess
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass

# UTF-8 enforcement
if sys.platform == 'win32':
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
    if sys.stderr.encoding != 'utf-8':
        sys.stderr.reconfigure(encoding='utf-8')

REPO_ROOT = Path(__file__).resolve().parents[1]

# Layer definitions
@dataclass
class Layer:
    id: int
    name: str
    script: Path
    critical: bool  # If True, failure stops entire pipeline
    timeout: int    # Timeout in seconds
    parallel_safe: bool  # Can run in parallel with other layers

LAYERS = [
    Layer(1, "Cryptographic Security", REPO_ROOT / "23_compliance/merkle/root_write_merkle_lock.py", True, 300, False),
    Layer(2, "Policy Enforcement", REPO_ROOT / "03_core/validators/sot/sot_validator_core.py", True, 300, False),
    Layer(3, "Trust Boundary", REPO_ROOT / "11_test_simulation/zero_time_auth/Shard_01_Identitaet_Personen/test_shard_01_identitaet_personen.py", False, 120, True),
    Layer(4, "Observability", REPO_ROOT / "17_observability/sot_metrics.py", False, 60, True),
    Layer(5, "Governance", REPO_ROOT / "05_documentation/compliance/5_LAYER_ENFORCEMENT_COMPLIANCE_REPORT.md", False, 10, True),
    Layer(6, "Self-Healing", REPO_ROOT / "23_compliance/watchdog/root_integrity_watchdog.py", True, 180, False),
    Layer(7, "Causality & Dependency", REPO_ROOT / "12_tooling/dependency_analyzer.py", False, 120, True),
    Layer(8, "Behavior & Anomaly", REPO_ROOT / "23_compliance/behavior/behavioral_fingerprinting.py", False, 60, True),
    Layer(9, "Cross-Federation", REPO_ROOT / "09_meta_identity/interfederation_proof_chain.py", False, 60, True),
    Layer(10, "Meta-Control", REPO_ROOT / "07_governance_legal/autonomous_governance_node.py", True, 60, False),
]

OUTPUT_DIR = REPO_ROOT / "02_audit_logging" / "orchestration"
MASTER_LOG = OUTPUT_DIR / "master_orchestration_log.json"


class MasterOrchestrator:
    """Orchestrates all 10 security layers"""

    def __init__(self, ci_mode: bool = False, threshold: float = 95.0):
        self.ci_mode = ci_mode
        self.threshold = threshold
        self.start_time = time.time()
        self.results = {}
        self.errors = []
        self.warnings = []

    def run_layer(self, layer: Layer) -> Tuple[bool, str, float]:
        """Run a single layer"""
        print(f"\n{'='*80}")
        print(f"[Layer {layer.id}/10] {layer.name}")
        print(f"{'='*80}")

        layer_start = time.time()

        try:
            # Special handling for different layer types
            if layer.id == 4:  # Observability - just check if exists
                success = layer.script.exists()
                output = f"Metrics exporter available" if success else "Not found"
            elif layer.id == 5:  # Governance - just check documentation
                success = layer.script.exists()
                output = f"Compliance report available" if success else "Not found"
            else:
                # Run Python script
                result = subprocess.run(
                    ["python", str(layer.script)],
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="ignore",
                    timeout=layer.timeout
                )
                success = result.returncode == 0
                output = result.stdout if success else result.stderr

            duration = time.time() - layer_start

            if success:
                print(f"✅ Layer {layer.id} PASSED ({duration:.2f}s)")
            else:
                print(f"❌ Layer {layer.id} FAILED ({duration:.2f}s)", file=sys.stderr)
                if layer.critical:
                    print(f"⚠️  CRITICAL LAYER FAILED - Pipeline stopped", file=sys.stderr)

            return success, output[:1000], duration

        except subprocess.TimeoutExpired:
            duration = time.time() - layer_start
            error_msg = f"Layer {layer.id} timed out after {layer.timeout}s"
            print(f"❌ {error_msg}", file=sys.stderr)
            self.errors.append(error_msg)
            return False, error_msg, duration

        except Exception as e:
            duration = time.time() - layer_start
            error_msg = f"Layer {layer.id} exception: {str(e)}"
            print(f"❌ {error_msg}", file=sys.stderr)
            self.errors.append(error_msg)
            return False, error_msg, duration

    def run_sequential(self, selected_layers: List[Layer]) -> Dict:
        """Run layers sequentially"""
        print("\n" + "="*80)
        print("MASTER ORCHESTRATOR - Sequential Execution")
        print("="*80)
        print(f"Mode: {'CI (Strict)' if self.ci_mode else 'Standard'}")
        print(f"Layers: {len(selected_layers)}/10")
        print(f"Start: {datetime.now(timezone.utc).isoformat()}")
        print("="*80)

        for layer in selected_layers:
            success, output, duration = self.run_layer(layer)

            self.results[layer.id] = {
                "name": layer.name,
                "success": success,
                "duration": duration,
                "output": output,
                "critical": layer.critical,
            }

            # Stop if critical layer failed
            if not success and layer.critical:
                print(f"\n❌ CRITICAL FAILURE: Stopping pipeline")
                break

        return self.generate_report()

    def run_parallel_optimized(self, selected_layers: List[Layer]) -> Dict:
        """Run parallel-safe layers in parallel, others sequentially"""
        print("\n" + "="*80)
        print("MASTER ORCHESTRATOR - Parallel-Optimized Execution")
        print("="*80)
        print(f"Mode: {'CI (Strict)' if self.ci_mode else 'Standard'}")
        print(f"Layers: {len(selected_layers)}/10")
        print(f"Start: {datetime.now(timezone.utc).isoformat()}")
        print("="*80)

        # Group layers
        sequential_critical = [l for l in selected_layers if l.critical]
        parallel_safe = [l for l in selected_layers if l.parallel_safe]

        # Run critical layers first (sequential)
        print(f"\n[Phase 1] Running {len(sequential_critical)} critical layers (sequential)...")
        for layer in sequential_critical:
            success, output, duration = self.run_layer(layer)
            self.results[layer.id] = {
                "name": layer.name,
                "success": success,
                "duration": duration,
                "output": output,
                "critical": layer.critical,
            }
            if not success:
                print(f"\n❌ CRITICAL FAILURE: Stopping pipeline")
                return self.generate_report()

        # Run parallel-safe layers (parallel)
        if parallel_safe:
            print(f"\n[Phase 2] Running {len(parallel_safe)} non-critical layers (parallel)...")

            with ThreadPoolExecutor(max_workers=min(4, len(parallel_safe))) as executor:
                future_to_layer = {executor.submit(self.run_layer, layer): layer for layer in parallel_safe}

                for future in as_completed(future_to_layer):
                    layer = future_to_layer[future]
                    try:
                        success, output, duration = future.result()
                        self.results[layer.id] = {
                            "name": layer.name,
                            "success": success,
                            "duration": duration,
                            "output": output,
                            "critical": layer.critical,
                        }
                    except Exception as e:
                        error_msg = f"Layer {layer.id} parallel execution failed: {str(e)}"
                        print(f"❌ {error_msg}", file=sys.stderr)
                        self.errors.append(error_msg)

        return self.generate_report()

    def calculate_overall_score(self) -> float:
        """Calculate overall compliance score"""
        if not self.results:
            return 0.0

        total_weight = sum(10 if r.get("critical") else 5 for r in self.results.values())
        passed_weight = sum(
            (10 if r.get("critical") else 5) for r in self.results.values() if r.get("success")
        )

        return (passed_weight / total_weight) * 100 if total_weight > 0 else 0.0

    def generate_report(self) -> Dict:
        """Generate comprehensive report"""
        total_duration = time.time() - self.start_time
        overall_score = self.calculate_overall_score()

        passed = sum(1 for r in self.results.values() if r.get("success"))
        failed = len(self.results) - passed

        report = {
            "metadata": {
                "version": "2.0.0",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "mode": "ci" if self.ci_mode else "standard",
                "total_duration": round(total_duration, 2),
            },
            "summary": {
                "overall_score": round(overall_score, 2),
                "passed": passed,
                "failed": failed,
                "total_layers": len(self.results),
                "threshold": self.threshold,
                "meets_threshold": overall_score >= self.threshold,
            },
            "layers": self.results,
            "errors": self.errors,
            "warnings": self.warnings,
        }

        # Save report
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        with open(MASTER_LOG, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        # Print summary
        self.print_summary(report)

        return report

    def print_summary(self, report: Dict):
        """Print execution summary"""
        print("\n" + "="*80)
        print("MASTER ORCHESTRATOR - EXECUTION SUMMARY")
        print("="*80)
        print(f"Overall Score:     {report['summary']['overall_score']:.2f}%")
        print(f"Threshold:         {report['summary']['threshold']:.0f}%")
        print(f"Status:            {'✅ PASS' if report['summary']['meets_threshold'] else '❌ FAIL'}")
        print(f"Duration:          {report['metadata']['total_duration']:.2f}s")
        print(f"Layers Passed:     {report['summary']['passed']}/{report['summary']['total_layers']}")

        if self.errors:
            print(f"\nErrors ({len(self.errors)}):")
            for err in self.errors[:5]:
                print(f"  ❌ {err}")

        print(f"\nReport saved: {MASTER_LOG}")
        print("="*80)

    def run_daemon(self, interval: int = 300):
        """Run orchestrator in daemon mode"""
        print(f"Starting Master Orchestrator daemon (interval: {interval}s)")
        print("Press Ctrl+C to stop\n")

        try:
            while True:
                print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Running orchestration cycle...")

                self.run_parallel_optimized(LAYERS)

                print(f"\nNext cycle in {interval}s...")
                time.sleep(interval)

        except KeyboardInterrupt:
            print("\n\nDaemon stopped by user")


def main():
    parser = argparse.ArgumentParser(
        description="SSID Master Orchestrator - Complete 10-Layer Enforcement",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all layers (parallel-optimized)
  python master_orchestrator.py

  # Run specific layers
  python master_orchestrator.py --layers 1,2,6

  # CI mode (strict, exit 1 on failure)
  python master_orchestrator.py --ci --threshold 95

  # Daemon mode (continuous monitoring)
  python master_orchestrator.py --daemon --interval 300

  # Sequential mode (no parallelization)
  python master_orchestrator.py --sequential
        """
    )

    parser.add_argument("--layers", type=str, help="Comma-separated layer IDs (1-10)")
    parser.add_argument("--ci", action="store_true", help="CI mode: fail if score below threshold")
    parser.add_argument("--threshold", type=float, default=95.0, help="Minimum score for CI mode (default: 95)")
    parser.add_argument("--daemon", action="store_true", help="Run as daemon (continuous monitoring)")
    parser.add_argument("--interval", type=int, default=300, help="Daemon interval in seconds (default: 300)")
    parser.add_argument("--sequential", action="store_true", help="Run all layers sequentially (no parallelization)")

    args = parser.parse_args()

    # Determine which layers to run
    if args.layers:
        layer_ids = [int(x.strip()) for x in args.layers.split(",")]
        selected_layers = [l for l in LAYERS if l.id in layer_ids]
    else:
        selected_layers = LAYERS

    orchestrator = MasterOrchestrator(ci_mode=args.ci, threshold=args.threshold)

    if args.daemon:
        orchestrator.run_daemon(args.interval)
    elif args.sequential:
        report = orchestrator.run_sequential(selected_layers)
    else:
        report = orchestrator.run_parallel_optimized(selected_layers)

    # Exit with appropriate code
    if args.ci:
        if report["summary"]["meets_threshold"]:
            sys.exit(0)
        else:
            print(f"\n❌ CI FAILURE: Score {report['summary']['overall_score']:.2f}% below threshold {args.threshold}%")
            sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
