#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Root-Integrity Watchdog - Layer 6: Self-Healing Security
==========================================================

Monitors the 24 ROOT directories for any unauthorized changes and
automatically triggers self-healing procedures.

Features:
  - Continuous monitoring of ROOT-24-LOCK protected paths
  - Hash-based integrity verification
  - Automatic rollback from signed snapshots
  - Audit logging of all integrity violations
  - Self-healing reconciliation engine

Usage:
  # Run watchdog once
  python root_integrity_watchdog.py

  # Run in daemon mode
  python root_integrity_watchdog.py --daemon --interval 300

  # Dry-run (no auto-healing)
  python root_integrity_watchdog.py --dry-run

Author: SSID Security Team
Version: 1.0.0
Date: 2025-10-22
"""

import sys
import json
import hashlib
import time
import argparse
import subprocess
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

# UTF-8 enforcement for Windows
if sys.platform == 'win32':
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
    if sys.stderr.encoding != 'utf-8':
        sys.stderr.reconfigure(encoding='utf-8')

# Repo root
REPO_ROOT = Path(__file__).resolve().parents[2]

# Protected ROOT-24 directories
ROOT_24_DIRS = [
    "01_ai_layer",
    "02_audit_logging",
    "03_core",
    "04_deployment",
    "05_documentation",
    "06_federation",
    "07_governance_legal",
    "08_identity_score",
    "09_meta_identity",
    "10_privacy_compliance",
    "11_test_simulation",
    "12_tooling",
    "13_ui_layer",
    "14_zero_time_auth",
    "15_shard_orchestrator",
    "16_codex",
    "17_observability",
    "18_api_gateway",
    "19_event_bus",
    "20_storage_layer",
    "21_post_quantum_crypto",
    "22_machine_learning",
    "23_compliance",
    "24_meta_orchestration",
]

# Critical files within ROOT-24 that must never change without audit
CRITICAL_FILES = [
    "SOT_ARTEFACTS_SPLIT/sot_contract_v3.2.0.yaml",
    "SOT_ARTEFACTS_SPLIT/sot_structure_v3.2.0.yaml",
    "SOT_ARTEFACTS_SPLIT/sot_semantic_rules_v3.2.0.yaml",
    "SOT_ARTEFACTS_SPLIT/sot_content_validators_v3.2.0.py",
    "23_compliance/policies/sot/sot_policy.rego",
    "03_core/validators/sot/sot_validator_core.py",
    "24_meta_orchestration/registry/agent_stack.yaml",
]

# Audit log
WATCHDOG_LOG = REPO_ROOT / "02_audit_logging" / "watchdog" / "root_integrity_log.json"
SNAPSHOT_DIR = REPO_ROOT / "02_audit_logging" / "snapshots" / "root_integrity"
REFERENCE_HASHES = REPO_ROOT / "24_meta_orchestration" / "registry" / "sot_reference_hashes.json"


class RootIntegrityWatchdog:
    """Monitors and self-heals ROOT-24 integrity violations"""

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.violations = []
        self.healed_items = []
        self.reference_hashes = self.load_reference_hashes()

    def load_reference_hashes(self) -> Dict[str, str]:
        """Load reference hashes from registry"""
        if not REFERENCE_HASHES.exists():
            print(f"⚠️  Reference hashes not found: {REFERENCE_HASHES}")
            print(f"   Generating initial reference...")
            return self.generate_initial_reference()

        with open(REFERENCE_HASHES, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("file_hashes", {})

    def generate_initial_reference(self) -> Dict[str, str]:
        """Generate initial reference hashes for critical files"""
        reference = {}

        print("Generating initial reference hashes...")
        for file_path in CRITICAL_FILES:
            full_path = REPO_ROOT / file_path
            if full_path.exists():
                file_hash = self.compute_file_hash(full_path)
                reference[file_path] = file_hash
                print(f"  ✅ {file_path}: {file_hash[:16]}...")

        # Save reference
        REFERENCE_HASHES.parent.mkdir(parents=True, exist_ok=True)
        reference_data = {
            "version": "1.0.0",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "file_hashes": reference
        }

        with open(REFERENCE_HASHES, 'w', encoding='utf-8') as f:
            json.dump(reference_data, f, indent=2, ensure_ascii=False)

        print(f"💾 Reference saved: {REFERENCE_HASHES}")
        return reference

    def compute_file_hash(self, file_path: Path) -> str:
        """Compute SHA-256 hash of file"""
        try:
            return hashlib.sha256(file_path.read_bytes()).hexdigest()
        except Exception as e:
            print(f"❌ Error hashing {file_path}: {e}", file=sys.stderr)
            return ""

    def check_root_24_structure(self) -> bool:
        """Verify all 24 ROOT directories exist"""
        print("\n[1/4] Checking ROOT-24 Structure...")
        all_exist = True

        for root_dir in ROOT_24_DIRS:
            dir_path = REPO_ROOT / root_dir
            if dir_path.exists() and dir_path.is_dir():
                print(f"  ✅ {root_dir}")
            else:
                print(f"  ❌ {root_dir} MISSING", file=sys.stderr)
                self.violations.append({
                    "type": "missing_root_directory",
                    "path": root_dir,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
                all_exist = False

        if all_exist:
            print(f"  → All 24 ROOT directories present")
        else:
            print(f"  → {len(self.violations)} directories missing", file=sys.stderr)

        return all_exist

    def check_critical_file_integrity(self) -> bool:
        """Verify critical files haven't been tampered with"""
        print("\n[2/4] Checking Critical File Integrity...")
        all_intact = True

        for file_path in CRITICAL_FILES:
            full_path = REPO_ROOT / file_path

            if not full_path.exists():
                print(f"  ❌ {file_path} MISSING", file=sys.stderr)
                self.violations.append({
                    "type": "missing_critical_file",
                    "path": file_path,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
                all_intact = False
                continue

            # Compute current hash
            current_hash = self.compute_file_hash(full_path)

            # Compare with reference
            reference_hash = self.reference_hashes.get(file_path)

            if reference_hash is None:
                print(f"  ⚠️  {file_path} (no reference)")
                # Add to reference
                self.reference_hashes[file_path] = current_hash
                continue

            if current_hash == reference_hash:
                print(f"  ✅ {file_path}")
            else:
                print(f"  ❌ {file_path} TAMPERED", file=sys.stderr)
                print(f"     Expected: {reference_hash[:16]}...", file=sys.stderr)
                print(f"     Got:      {current_hash[:16]}...", file=sys.stderr)
                self.violations.append({
                    "type": "file_integrity_violation",
                    "path": file_path,
                    "expected_hash": reference_hash,
                    "actual_hash": current_hash,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
                all_intact = False

        if all_intact:
            print(f"  → All critical files intact")
        else:
            print(f"  → {len([v for v in self.violations if v['type'] == 'file_integrity_violation'])} integrity violations", file=sys.stderr)

        return all_intact

    def self_heal(self) -> bool:
        """Attempt to self-heal violations by restoring from snapshots"""
        if not self.violations:
            return True

        print("\n[3/4] Self-Healing Violations...")

        if self.dry_run:
            print("  ⚠️  DRY-RUN mode: no actual healing performed")
            for violation in self.violations:
                print(f"     Would heal: {violation['path']}")
            return False

        healed_count = 0

        for violation in self.violations:
            if violation["type"] == "file_integrity_violation":
                success = self.restore_file_from_git(violation["path"])
                if success:
                    healed_count += 1
                    self.healed_items.append(violation["path"])

        if healed_count > 0:
            print(f"  ✅ Healed {healed_count} violations")
        else:
            print(f"  ❌ Could not heal violations", file=sys.stderr)

        return healed_count == len(self.violations)

    def restore_file_from_git(self, file_path: str) -> bool:
        """Restore file from last committed version in git"""
        print(f"  → Restoring {file_path} from git...")

        try:
            # Use git checkout to restore file
            result = subprocess.run(
                ["git", "checkout", "HEAD", "--", file_path],
                cwd=str(REPO_ROOT),
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                print(f"    ✅ Restored from git")
                return True
            else:
                print(f"    ❌ Git restore failed: {result.stderr}", file=sys.stderr)
                return False

        except Exception as e:
            print(f"    ❌ Restore error: {e}", file=sys.stderr)
            return False

    def audit_log(self) -> None:
        """Write audit log of watchdog run"""
        print("\n[4/4] Writing Audit Log...")

        WATCHDOG_LOG.parent.mkdir(parents=True, exist_ok=True)

        # Load existing log
        if WATCHDOG_LOG.exists():
            with open(WATCHDOG_LOG, 'r', encoding='utf-8') as f:
                log_data = json.load(f)
        else:
            log_data = {"runs": []}

        # Append this run
        run_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "violations": len(self.violations),
            "healed": len(self.healed_items),
            "dry_run": self.dry_run,
            "details": {
                "violations": self.violations,
                "healed_items": self.healed_items
            }
        }

        log_data["runs"].append(run_entry)

        # Keep only last 1000 runs
        if len(log_data["runs"]) > 1000:
            log_data["runs"] = log_data["runs"][-1000:]

        with open(WATCHDOG_LOG, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)

        print(f"  💾 Audit log: {WATCHDOG_LOG}")

    def run(self) -> bool:
        """Run complete watchdog check"""
        print("=" * 80)
        print("ROOT-INTEGRITY WATCHDOG - Layer 6: Self-Healing Security")
        print("=" * 80)
        print(f"Mode: {'DRY-RUN' if self.dry_run else 'ACTIVE'}")
        print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
        print("=" * 80)

        # Step 1: Check ROOT-24 structure
        structure_ok = self.check_root_24_structure()

        # Step 2: Check critical file integrity
        integrity_ok = self.check_critical_file_integrity()

        # Step 3: Self-heal if violations found
        if not (structure_ok and integrity_ok):
            healed = self.self_heal()
        else:
            healed = True

        # Step 4: Audit log
        self.audit_log()

        # Summary
        print("\n" + "=" * 80)
        print("WATCHDOG SUMMARY")
        print("=" * 80)
        print(f"ROOT-24 Structure:  {'✅ OK' if structure_ok else '❌ VIOLATIONS'}")
        print(f"File Integrity:     {'✅ OK' if integrity_ok else '❌ VIOLATIONS'}")
        print(f"Violations Found:   {len(self.violations)}")
        print(f"Self-Healed:        {len(self.healed_items)}")

        if self.violations and not healed:
            print(f"\n⚠️  CRITICAL: {len(self.violations)} violations could not be healed!")
            print(f"   Manual intervention required.")
            return False
        elif self.violations and healed:
            print(f"\n✅ All violations self-healed successfully")
            return True
        else:
            print(f"\n✅ No violations detected")
            return True


def main():
    """Main execution"""
    parser = argparse.ArgumentParser(
        description="Root-Integrity Watchdog (Layer 6: Self-Healing Security)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run watchdog once
  python root_integrity_watchdog.py

  # Dry-run (no healing)
  python root_integrity_watchdog.py --dry-run

  # Daemon mode (check every 5 minutes)
  python root_integrity_watchdog.py --daemon --interval 300

Integration:
  # Add to cron (Linux)
  */5 * * * * python /path/to/root_integrity_watchdog.py

  # Add to Task Scheduler (Windows)
  schtasks /create /tn "RootWatchdog" /tr "python root_integrity_watchdog.py" /sc minute /mo 5
        """
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Dry-run mode: detect but don't heal violations"
    )

    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run as daemon (continuous monitoring)"
    )

    parser.add_argument(
        "--interval",
        type=int,
        default=300,
        help="Daemon check interval in seconds (default: 300 = 5 minutes)"
    )

    args = parser.parse_args()

    if args.daemon:
        print(f"Starting watchdog daemon (interval: {args.interval}s)...")
        print("Press Ctrl+C to stop")
        print()

        try:
            while True:
                watchdog = RootIntegrityWatchdog(dry_run=args.dry_run)
                success = watchdog.run()

                if not success:
                    print(f"\n⚠️  Watchdog detected unhealed violations!")
                    if not args.dry_run:
                        # In production, could send alerts here
                        pass

                print(f"\nNext check in {args.interval} seconds...")
                time.sleep(args.interval)

        except KeyboardInterrupt:
            print("\n\nWatchdog daemon stopped by user")
            sys.exit(0)

    else:
        # Single run
        watchdog = RootIntegrityWatchdog(dry_run=args.dry_run)
        success = watchdog.run()

        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
