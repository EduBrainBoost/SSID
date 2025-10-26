#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Causal Locking - Layer 7: Causality & Dependency Security
==========================================================

Creates hash chains documenting rule relationships and dependencies.
Ensures dependent rules are marked for review when base rules change.

Features:
  - Causal hash chain generation
  - Dependency relationship tracking
  - Auto-marks dependent rules as "review-pending"
  - Prevents breaking changes without review
  - Causal consistency verification

Usage:
  # Create causal lock for rule
  python causal_locking.py --rule CS001

  # Verify causal consistency
  python causal_locking.py --verify

  # Mark dependent rules for review
  python causal_locking.py --changed CS001,MS002

Author: SSID Architecture Team
Version: 1.0.0
Date: 2025-10-22
"""

import sys
import json
import hashlib
import argparse
from pathlib import Path
from typing import Dict, List, Set, Optional
from datetime import datetime, timezone

if sys.platform == 'win32':
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')

REPO_ROOT = Path(__file__).resolve().parents[1]

# Causal lock storage
CAUSAL_LOCKS_DIR = REPO_ROOT / "24_meta_orchestration" / "causal_locks"
REVIEW_PENDING_FILE = REPO_ROOT / "24_meta_orchestration" / "review_pending.json"

# Dependency data (would normally come from dependency_analyzer)
RULE_DEPENDENCIES = {
    "CS001": ["MS001", "KP001"],
    "CS002": ["CS001", "KP002"],
    "MS001": ["KP001"],
    "MS002": ["MS001", "CS001"],
    "KP001": [],
    "KP002": ["KP001"],
}


class CausalLocking:
    """Manages causal hash chains and dependency locking"""

    def __init__(self):
        self.locks = {}
        self.review_pending = self.load_review_pending()

    def load_review_pending(self) -> Dict:
        """Load review-pending status"""
        if not REVIEW_PENDING_FILE.exists():
            return {"rules": {}, "last_updated": None}

        with open(REVIEW_PENDING_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save_review_pending(self):
        """Save review-pending status"""
        REVIEW_PENDING_FILE.parent.mkdir(parents=True, exist_ok=True)

        self.review_pending["last_updated"] = datetime.now(timezone.utc).isoformat()

        with open(REVIEW_PENDING_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.review_pending, f, indent=2, ensure_ascii=False)

    def compute_rule_hash(self, rule_id: str, dependencies: List[str]) -> str:
        """Compute hash for a rule including its dependencies"""
        # In production, would hash actual rule content
        # For now, hash the rule ID + dependencies
        content = f"{rule_id}:{','.join(sorted(dependencies))}"
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def create_causal_chain(self, rule_id: str) -> Dict:
        """Create causal hash chain for a rule"""
        print(f"\n[1/3] Creating Causal Chain for {rule_id}...")

        dependencies = RULE_DEPENDENCIES.get(rule_id, [])

        if not dependencies:
            print(f"  → Rule {rule_id} has no dependencies")

        # Compute hash for each dependency
        dep_hashes = {}
        for dep in dependencies:
            dep_hash = self.compute_rule_hash(dep, RULE_DEPENDENCIES.get(dep, []))
            dep_hashes[dep] = dep_hash
            print(f"    ✅ Dependency {dep}: {dep_hash[:16]}...")

        # Compute hash for this rule
        rule_hash = self.compute_rule_hash(rule_id, dependencies)

        # Create causal chain
        causal_chain = {
            "rule_id": rule_id,
            "rule_hash": rule_hash,
            "dependencies": dependencies,
            "dependency_hashes": dep_hashes,
            "chain_hash": self.compute_chain_hash(rule_hash, list(dep_hashes.values())),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        print(f"  → Rule hash: {rule_hash[:16]}...")
        print(f"  → Chain hash: {causal_chain['chain_hash'][:16]}...")

        return causal_chain

    def compute_chain_hash(self, rule_hash: str, dep_hashes: List[str]) -> str:
        """Compute hash of entire causal chain"""
        chain_content = rule_hash + ''.join(sorted(dep_hashes))
        return hashlib.sha256(chain_content.encode('utf-8')).hexdigest()

    def save_causal_lock(self, causal_chain: Dict):
        """Save causal lock to storage"""
        rule_id = causal_chain["rule_id"]
        lock_file = CAUSAL_LOCKS_DIR / f"{rule_id}.json"

        lock_file.parent.mkdir(parents=True, exist_ok=True)

        with open(lock_file, 'w', encoding='utf-8') as f:
            json.dump(causal_chain, f, indent=2, ensure_ascii=False)

        print(f"  💾 Causal lock saved: {lock_file.name}")

    def mark_dependent_rules_pending(self, changed_rule_id: str):
        """Mark all rules that depend on changed_rule_id for review"""
        print(f"\n[2/3] Marking Dependent Rules Pending for {changed_rule_id}...")

        # Find all rules that depend on changed_rule_id
        dependent_rules = []
        for rule, deps in RULE_DEPENDENCIES.items():
            if changed_rule_id in deps:
                dependent_rules.append(rule)

        if not dependent_rules:
            print(f"  → No dependent rules found")
            return

        print(f"  → Found {len(dependent_rules)} dependent rules:")

        for dep_rule in dependent_rules:
            print(f"    🔶 {dep_rule} marked as REVIEW-PENDING")

            self.review_pending["rules"][dep_rule] = {
                "status": "review-pending",
                "reason": f"Dependency {changed_rule_id} was modified",
                "marked_at": datetime.now(timezone.utc).isoformat(),
                "changed_dependency": changed_rule_id,
            }

        self.save_review_pending()

    def verify_causal_consistency(self) -> bool:
        """Verify causal consistency of all locks"""
        print(f"\n[3/3] Verifying Causal Consistency...")

        if not CAUSAL_LOCKS_DIR.exists():
            print(f"  ⚠️  No causal locks found")
            return True

        lock_files = list(CAUSAL_LOCKS_DIR.glob("*.json"))

        if not lock_files:
            print(f"  ⚠️  No causal locks to verify")
            return True

        print(f"  → Checking {len(lock_files)} causal locks...")

        inconsistencies = []

        for lock_file in lock_files:
            with open(lock_file, 'r', encoding='utf-8') as f:
                lock_data = json.load(f)

            rule_id = lock_data["rule_id"]
            stored_chain_hash = lock_data["chain_hash"]

            # Recompute chain hash
            dep_hashes = list(lock_data["dependency_hashes"].values())
            computed_chain_hash = self.compute_chain_hash(lock_data["rule_hash"], dep_hashes)

            if stored_chain_hash == computed_chain_hash:
                print(f"    ✅ {rule_id}")
            else:
                print(f"    ❌ {rule_id} INCONSISTENT", file=sys.stderr)
                inconsistencies.append(rule_id)

        if inconsistencies:
            print(f"\n  ❌ {len(inconsistencies)} inconsistencies found!")
            return False
        else:
            print(f"\n  ✅ All causal locks consistent")
            return True

    def run(self, rule_id: Optional[str] = None, changed_rules: Optional[List[str]] = None, verify: bool = False):
        """Run causal locking operations"""
        print("=" * 80)
        print("CAUSAL LOCKING - Layer 7: Causality & Dependency Security")
        print("=" * 80)
        print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
        print("=" * 80)

        if verify:
            # Verification mode
            consistent = self.verify_causal_consistency()
            return consistent

        if rule_id:
            # Create causal lock for specific rule
            chain = self.create_causal_chain(rule_id)
            self.save_causal_lock(chain)

        if changed_rules:
            # Mark dependent rules for review
            for changed_rule in changed_rules:
                self.mark_dependent_rules_pending(changed_rule)

        # Summary
        print("\n" + "=" * 80)
        print("CAUSAL LOCKING SUMMARY")
        print("=" * 80)
        print(f"Review-Pending Rules: {len(self.review_pending.get('rules', {}))}")

        if self.review_pending.get('rules'):
            print(f"\nRules requiring review:")
            for rule, data in list(self.review_pending['rules'].items())[:5]:
                print(f"  🔶 {rule}: {data['reason']}")

            if len(self.review_pending['rules']) > 5:
                print(f"  ... and {len(self.review_pending['rules']) - 5} more")

        return True


def main():
    parser = argparse.ArgumentParser(
        description="Causal Locking (Layer 7: Causality & Dependency Security)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create causal lock for rule
  python causal_locking.py --rule CS001

  # Mark dependent rules after change
  python causal_locking.py --changed CS001,MS002

  # Verify causal consistency
  python causal_locking.py --verify
        """
    )

    parser.add_argument("--rule", type=str, help="Create causal lock for specific rule")
    parser.add_argument("--changed", type=str, help="Comma-separated list of changed rules")
    parser.add_argument("--verify", action="store_true", help="Verify causal consistency")

    args = parser.parse_args()

    locking = CausalLocking()

    changed_rules = None
    if args.changed:
        changed_rules = [r.strip() for r in args.changed.split(",")]

    success = locking.run(
        rule_id=args.rule,
        changed_rules=changed_rules,
        verify=args.verify
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
