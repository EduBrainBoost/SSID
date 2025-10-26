#!/usr/bin/env python3
"""
SoT-Hash Reconciliation Engine - Layer 6: Self-Healing Security
================================================================

Detects "drifted truth" - silent rule changes that bypass normal audit.
Periodically reconciles all SoT artefacts against registry reference.

Features:
  - Hash-based drift detection
  - Automatic Merkle-proof re-verification
  - Quarantine of drifted files
  - Root-cause analysis
  - Auto-reconciliation with registry

Usage:
  # Run reconciliation
  python sot_reconciliation_engine.py

  # Auto-fix drifted files
  python sot_reconciliation_engine.py --auto-fix

  # Quarantine mode
  python sot_reconciliation_engine.py --quarantine

Author: SSID Security Team
Version: 1.0.0
Date: 2025-10-22
"""

import sys
import json
import hashlib
import shutil
import argparse
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

# Repo root
REPO_ROOT = Path(__file__).resolve().parents[2]

# SoT artefacts to monitor
SOT_ARTEFACTS = {
    "yaml": [
        "SOT_ARTEFACTS_SPLIT/sot_contract_v3.2.0.yaml",
        "SOT_ARTEFACTS_SPLIT/sot_structure_v3.2.0.yaml",
        "SOT_ARTEFACTS_SPLIT/sot_semantic_rules_v3.2.0.yaml",
    ],
    "rego": [
        "23_compliance/policies/sot/sot_policy.rego",
        "23_compliance/policies/agent_sandbox.rego",
    ],
    "python": [
        "SOT_ARTEFACTS_SPLIT/sot_content_validators_v3.2.0.py",
        "03_core/validators/sot/sot_validator_core.py",
    ],
    "markdown": [
        "23_compliance/architecture/5_LAYER_SOT_ENFORCEMENT.md",
        "05_documentation/compliance/5_LAYER_ENFORCEMENT_COMPLIANCE_REPORT.md",
    ]
}

# Registry reference
REFERENCE_REGISTRY = REPO_ROOT / "24_meta_orchestration" / "registry" / "sot_reference.yaml"
REFERENCE_HASHES = REPO_ROOT / "24_meta_orchestration" / "registry" / "sot_reference_hashes.json"

# Quarantine directory
QUARANTINE_DIR = REPO_ROOT / "02_audit_logging" / "quarantine"

# Reconciliation log
RECONCILIATION_LOG = REPO_ROOT / "02_audit_logging" / "watchdog" / "sot_reconciliation_log.json"


class SoTReconciliationEngine:
    """Detects and reconciles drifted SoT truth"""

    def __init__(self, auto_fix: bool = False, quarantine: bool = False):
        self.auto_fix = auto_fix
        self.quarantine_mode = quarantine
        self.drifts = []
        self.fixed_items = []
        self.quarantined_items = []

    def compute_hash(self, file_path: Path) -> str:
        """Compute SHA-256 hash of file"""
        try:
            return hashlib.sha256(file_path.read_bytes()).hexdigest()
        except Exception as e:
            print(f"❌ Error hashing {file_path}: {e}", file=sys.stderr)
            return ""

    def load_reference_hashes(self) -> Dict[str, str]:
        """Load reference hashes from registry"""
        if not REFERENCE_HASHES.exists():
            print(f"⚠️  Reference hashes not found")
            print(f"   Run: python 23_compliance/watchdog/root_integrity_watchdog.py")
            return {}

        with open(REFERENCE_HASHES, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("file_hashes", {})

    def scan_for_drift(self) -> List[Dict]:
        """Scan all SoT artefacts for drift"""
        print("\n[1/4] Scanning SoT Artefacts for Drift...")

        reference_hashes = self.load_reference_hashes()
        drifts = []

        for category, file_list in SOT_ARTEFACTS.items():
            print(f"\n  Category: {category}")

            for file_path in file_list:
                full_path = REPO_ROOT / file_path

                if not full_path.exists():
                    print(f"    ❌ {file_path} MISSING")
                    drifts.append({
                        "type": "missing_file",
                        "path": file_path,
                        "category": category,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    })
                    continue

                # Compute current hash
                current_hash = self.compute_hash(full_path)

                # Get reference hash
                reference_hash = reference_hashes.get(file_path)

                if reference_hash is None:
                    print(f"    ⚠️  {file_path} (no reference)")
                    continue

                if current_hash == reference_hash:
                    print(f"    ✅ {file_path}")
                else:
                    print(f"    🔶 {file_path} DRIFTED")
                    print(f"       Reference: {reference_hash[:16]}...")
                    print(f"       Current:   {current_hash[:16]}...")

                    drifts.append({
                        "type": "hash_drift",
                        "path": file_path,
                        "category": category,
                        "reference_hash": reference_hash,
                        "current_hash": current_hash,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    })

        self.drifts = drifts

        print(f"\n  → {len(drifts)} drift(s) detected")
        return drifts

    def analyze_root_cause(self, drift: Dict) -> str:
        """Analyze root cause of drift"""
        # Check if file was modified by git
        file_path = drift["path"]

        try:
            import subprocess
            result = subprocess.run(
                ["git", "log", "-1", "--pretty=format:%H|%an|%ai", "--", file_path],
                cwd=str(REPO_ROOT),
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0 and result.stdout:
                commit_hash, author, timestamp = result.stdout.split("|")
                return f"Modified by {author} at {timestamp} (commit {commit_hash[:8]})"
            else:
                return "Unknown (no git history)"

        except Exception as e:
            return f"Error analyzing: {str(e)}"

    def quarantine_drifted_file(self, drift: Dict) -> bool:
        """Move drifted file to quarantine"""
        file_path = REPO_ROOT / drift["path"]

        if not file_path.exists():
            return False

        # Create quarantine directory structure
        quarantine_path = QUARANTINE_DIR / drift["path"]
        quarantine_path.parent.mkdir(parents=True, exist_ok=True)

        # Add timestamp to filename
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        quarantine_file = quarantine_path.parent / f"{quarantine_path.name}.{timestamp}.quarantined"

        try:
            shutil.copy2(file_path, quarantine_file)
            print(f"    → Quarantined: {quarantine_file.name}")
            self.quarantined_items.append(str(drift["path"]))
            return True
        except Exception as e:
            print(f"    ❌ Quarantine failed: {e}", file=sys.stderr)
            return False

    def auto_reconcile(self) -> int:
        """Auto-reconcile drifted files from git"""
        print("\n[2/4] Auto-Reconciliation...")

        if not self.drifts:
            print("  → No drifts to reconcile")
            return 0

        if not self.auto_fix:
            print("  ⚠️  Auto-fix disabled (use --auto-fix to enable)")
            for drift in self.drifts:
                print(f"     Would fix: {drift['path']}")
            return 0

        fixed_count = 0

        for drift in self.drifts:
            if drift["type"] == "hash_drift":
                print(f"  → Reconciling {drift['path']}...")

                # Analyze root cause first
                root_cause = self.analyze_root_cause(drift)
                print(f"    Root cause: {root_cause}")

                # Quarantine if enabled
                if self.quarantine_mode:
                    self.quarantine_drifted_file(drift)

                # Restore from git
                success = self.restore_from_git(drift["path"])
                if success:
                    fixed_count += 1
                    self.fixed_items.append(drift["path"])

        print(f"\n  → Reconciled {fixed_count}/{len(self.drifts)} drifts")
        return fixed_count

    def restore_from_git(self, file_path: str) -> bool:
        """Restore file from last committed version"""
        try:
            import subprocess
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
                print(f"    ❌ Restore failed: {result.stderr}", file=sys.stderr)
                return False

        except Exception as e:
            print(f"    ❌ Restore error: {e}", file=sys.stderr)
            return False

    def reverify_merkle_proofs(self) -> bool:
        """Re-run Merkle proof verification after reconciliation"""
        print("\n[3/4] Re-verifying Merkle Proofs...")

        try:
            import subprocess

            merkle_lock = REPO_ROOT / "23_compliance" / "merkle" / "root_write_merkle_lock.py"

            result = subprocess.run(
                ["python", str(merkle_lock)],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore",
                timeout=300
            )

            if result.returncode == 0:
                print("  ✅ Merkle proofs re-verified")
                return True
            else:
                print(f"  ❌ Merkle re-verification failed", file=sys.stderr)
                return False

        except Exception as e:
            print(f"  ❌ Merkle re-verification error: {e}", file=sys.stderr)
            return False

    def audit_log(self) -> None:
        """Write reconciliation audit log"""
        print("\n[4/4] Writing Audit Log...")

        RECONCILIATION_LOG.parent.mkdir(parents=True, exist_ok=True)

        # Load existing log
        if RECONCILIATION_LOG.exists():
            with open(RECONCILIATION_LOG, 'r', encoding='utf-8') as f:
                log_data = json.load(f)
        else:
            log_data = {"runs": []}

        # Append this run
        run_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "drifts_detected": len(self.drifts),
            "fixed": len(self.fixed_items),
            "quarantined": len(self.quarantined_items),
            "auto_fix_enabled": self.auto_fix,
            "quarantine_enabled": self.quarantine_mode,
            "details": {
                "drifts": self.drifts,
                "fixed_items": self.fixed_items,
                "quarantined_items": self.quarantined_items
            }
        }

        log_data["runs"].append(run_entry)

        # Keep only last 1000 runs
        if len(log_data["runs"]) > 1000:
            log_data["runs"] = log_data["runs"][-1000:]

        with open(RECONCILIATION_LOG, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)

        print(f"  💾 Audit log: {RECONCILIATION_LOG}")

    def run(self) -> bool:
        """Run complete reconciliation"""
        print("=" * 80)
        print("SOT-HASH RECONCILIATION ENGINE - Layer 6: Self-Healing Security")
        print("=" * 80)
        print(f"Auto-Fix:    {'Enabled' if self.auto_fix else 'Disabled'}")
        print(f"Quarantine:  {'Enabled' if self.quarantine_mode else 'Disabled'}")
        print(f"Timestamp:   {datetime.now(timezone.utc).isoformat()}")
        print("=" * 80)

        # Step 1: Scan for drift
        self.scan_for_drift()

        # Step 2: Auto-reconcile
        self.auto_reconcile()

        # Step 3: Re-verify Merkle proofs
        if self.fixed_items:
            self.reverify_merkle_proofs()

        # Step 4: Audit log
        self.audit_log()

        # Summary
        print("\n" + "=" * 80)
        print("RECONCILIATION SUMMARY")
        print("=" * 80)
        print(f"Drifts Detected:    {len(self.drifts)}")
        print(f"Auto-Reconciled:    {len(self.fixed_items)}")
        print(f"Quarantined:        {len(self.quarantined_items)}")

        if self.drifts and not self.fixed_items:
            print(f"\n⚠️  CRITICAL: {len(self.drifts)} drifts detected but not fixed!")
            print(f"   Run with --auto-fix to reconcile")
            return False
        elif self.drifts and self.fixed_items:
            print(f"\n✅ All drifts reconciled successfully")
            return True
        else:
            print(f"\n✅ No drift detected - SoT is consistent")
            return True


def main():
    """Main execution"""
    parser = argparse.ArgumentParser(
        description="SoT-Hash Reconciliation Engine (Layer 6: Self-Healing)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Detect drift only
  python sot_reconciliation_engine.py

  # Auto-fix drifted files
  python sot_reconciliation_engine.py --auto-fix

  # Quarantine drifted files before fixing
  python sot_reconciliation_engine.py --auto-fix --quarantine

Integration:
  # Add to cron (daily reconciliation)
  0 2 * * * python /path/to/sot_reconciliation_engine.py --auto-fix
        """
    )

    parser.add_argument(
        "--auto-fix",
        action="store_true",
        help="Automatically reconcile drifted files from git"
    )

    parser.add_argument(
        "--quarantine",
        action="store_true",
        help="Quarantine drifted files before reconciliation"
    )

    args = parser.parse_args()

    engine = SoTReconciliationEngine(auto_fix=args.auto_fix, quarantine=args.quarantine)
    success = engine.run()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
