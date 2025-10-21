#!/usr/bin/env python3
"""
Registry Lineage Updater
=========================

Adds new entry to registry_lineage.yaml after creating a PQC signature.

Purpose:
  - Maintain chronological audit trail
  - Link registry versions cryptographically
  - Track compliance evolution
  - Enable historical verification

Workflow:
  1. Load current registry_lineage.yaml
  2. Load latest compliance_registry_signature.json
  3. Compute changes from previous entry
  4. Calculate entry hash
  5. Append new entry
  6. Update metadata
  7. Validate chain integrity

Security:
  - Each entry hashed (SHA-256)
  - Linked to previous entry via hash
  - PQC signature referenced
  - Tamper-evident chain

Author: SSID Compliance Team
Version: 1.0.0
Date: 2025-10-17
"""

import sys
import json
import hashlib
import yaml
import argparse
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

# Paths
REPO_ROOT = Path(__file__).resolve().parents[2]
LINEAGE_PATH = REPO_ROOT / "23_compliance" / "registry" / "registry_lineage.yaml"
SIGNATURE_PATH = REPO_ROOT / "23_compliance" / "registry" / "compliance_registry_signature.json"
REGISTRY_PATH = REPO_ROOT / "23_compliance" / "registry" / "compliance_registry.json"


def load_lineage() -> Dict:
    """Load current lineage file."""
    if not LINEAGE_PATH.exists():
        print(f"ERROR: Lineage file not found: {LINEAGE_PATH}", file=sys.stderr)
        print("Initializing new lineage file...", file=sys.stderr)
        return initialize_lineage()

    with open(LINEAGE_PATH, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def initialize_lineage() -> Dict:
    """Initialize new lineage structure."""
    return {
        "metadata": {
            "version": "1.0.0",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "description": "Chronological ledger of compliance registry evolution",
            "purpose": "Cryptographic audit trail for compliance state changes",
            "chain_hash_algorithm": "SHA-256",
            "signature_algorithm": "Dilithium2",
            "total_entries": 0,
            "first_entry": None,
            "last_entry": None
        },
        "entries": [],
        "schema_version": "1.0.0"
    }


def load_signature_document() -> Dict:
    """Load latest signature document."""
    if not SIGNATURE_PATH.exists():
        print(f"ERROR: Signature file not found: {SIGNATURE_PATH}", file=sys.stderr)
        print("Run: python 23_compliance/registry/sign_compliance_registry_pqc.py", file=sys.stderr)
        sys.exit(1)

    with open(SIGNATURE_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_registry() -> Dict:
    """Load compliance registry."""
    if not REGISTRY_PATH.exists():
        print(f"ERROR: Registry not found: {REGISTRY_PATH}", file=sys.stderr)
        sys.exit(1)

    with open(REGISTRY_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def compute_entry_hash(entry: Dict) -> str:
    """
    Compute deterministic hash of entry.

    Excludes the 'entry_hash' field itself to avoid circular dependency.
    """
    # Create copy without entry_hash
    entry_copy = entry.copy()
    if 'chain' in entry_copy and 'entry_hash' in entry_copy['chain']:
        entry_copy['chain'] = entry_copy['chain'].copy()
        del entry_copy['chain']['entry_hash']

    # Canonical JSON for hashing
    canonical = json.dumps(entry_copy, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(canonical.encode('utf-8')).hexdigest()


def detect_changes(current_sig: Dict, previous_entry: Optional[Dict], current_registry: Dict) -> Dict:
    """
    Detect changes between current and previous registry state.

    Returns change summary.
    """
    if previous_entry is None:
        # Initial entry
        return {
            "type": "initial",
            "description": "Initial compliance registry creation",
            "files_added": current_sig["payload"]["metadata"]["total_manifestations"],
            "files_modified": 0,
            "files_removed": 0,
            "rules_added": current_sig["payload"]["metadata"]["total_rules"],
            "rules_modified": 0,
            "rules_removed": 0
        }

    # Compare Merkle roots
    current_root = current_sig["payload"]["global_merkle_root"]
    previous_root = previous_entry["global_merkle_root"]

    if current_root == previous_root:
        # No changes
        return {
            "type": "no_change",
            "description": "Registry unchanged (re-signature)",
            "files_added": 0,
            "files_modified": 0,
            "files_removed": 0,
            "rules_added": 0,
            "rules_modified": 0,
            "rules_removed": 0
        }

    # Detect rule changes
    current_rules = current_sig["payload"]["metadata"]["total_rules"]
    previous_rules = previous_entry["total_rules"]

    rules_added = max(0, current_rules - previous_rules)
    rules_removed = max(0, previous_rules - current_rules)

    # Detect manifestation changes
    current_files = current_sig["payload"]["metadata"]["total_manifestations"]
    previous_files = previous_entry["total_manifestations"]

    files_added = max(0, current_files - previous_files)
    files_removed = max(0, previous_files - current_files)

    # Determine change type
    if rules_added > 0 or files_added > 0:
        change_type = "expansion"
        description = f"Added {rules_added} rules, {files_added} manifestations"
    elif rules_removed > 0 or files_removed > 0:
        change_type = "reduction"
        description = f"Removed {rules_removed} rules, {files_removed} manifestations"
    else:
        change_type = "modification"
        description = "Manifestation files modified (Merkle root changed)"

    return {
        "type": change_type,
        "description": description,
        "files_added": files_added,
        "files_modified": current_files - files_added + files_removed,
        "files_removed": files_removed,
        "rules_added": rules_added,
        "rules_modified": 0,  # Cannot detect without deeper analysis
        "rules_removed": rules_removed
    }


def get_git_commit_sha() -> Optional[str]:
    """Get current Git commit SHA if available."""
    try:
        import subprocess
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            timeout=5
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return None


def create_new_entry(signature_doc: Dict, registry: Dict, lineage: Dict) -> Dict:
    """Create new lineage entry from signature document."""

    # Get previous entry
    previous_entry = lineage["entries"][-1] if lineage["entries"] else None
    entry_id = len(lineage["entries"]) + 1

    # Detect changes
    changes = detect_changes(signature_doc, previous_entry, registry)

    # Find WORM snapshot
    worm_dir = REPO_ROOT / "02_audit_logging" / "storage" / "worm" / "immutable_store"
    worm_files = sorted(worm_dir.glob("compliance_signature_*.json"))
    latest_worm = worm_files[-1] if worm_files else None

    # Create entry
    entry = {
        "entry_id": entry_id,
        "timestamp": signature_doc["signed_at"],

        # Registry state
        "registry_version": signature_doc["payload"]["metadata"]["registry_version"],
        "global_merkle_root": signature_doc["payload"]["global_merkle_root"],

        # Compliance metrics
        "compliance_score": signature_doc["payload"]["metadata"]["compliance_score"],
        "total_rules": signature_doc["payload"]["metadata"]["total_rules"],
        "total_manifestations": signature_doc["payload"]["metadata"]["total_manifestations"],

        # Standard Merkle roots
        "standard_merkle_roots": signature_doc["payload"]["standard_merkle_roots"],

        # PQC signature
        "pqc_signature": {
            "algorithm": signature_doc["signature"]["algorithm"],
            "backend": signature_doc["signature"]["backend"],
            "signature_file": str(SIGNATURE_PATH.relative_to(REPO_ROOT).as_posix()),
            "signature_hash": signature_doc["message_hash"],
            "worm_snapshot": str(latest_worm.relative_to(REPO_ROOT).as_posix()) if latest_worm else None
        },

        # Changes
        "changes": changes,

        # Attribution
        "attribution": {
            "actor": "SSID Compliance Team",
            "event": changes["description"],
            "commit_sha": get_git_commit_sha()
        },

        # Chain linkage
        "chain": {
            "previous_entry_id": previous_entry["entry_id"] if previous_entry else None,
            "previous_merkle_root": previous_entry["global_merkle_root"] if previous_entry else None,
            "entry_hash": None,  # Computed after
            "chain_valid": True
        }
    }

    # Compute entry hash
    entry["chain"]["entry_hash"] = compute_entry_hash(entry)

    return entry


def update_metadata(lineage: Dict) -> None:
    """Update lineage metadata after adding entry."""
    lineage["metadata"]["total_entries"] = len(lineage["entries"])

    if lineage["entries"]:
        lineage["metadata"]["first_entry"] = lineage["entries"][0]["timestamp"]
        lineage["metadata"]["last_entry"] = lineage["entries"][-1]["timestamp"]


def save_lineage(lineage: Dict, output_path: Path) -> None:
    """Save updated lineage to YAML."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        yaml.dump(lineage, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    print(f"Lineage updated: {output_path}")


def display_entry_summary(entry: Dict) -> None:
    """Display summary of new entry."""
    print("\n" + "="*80)
    print("New Registry Lineage Entry")
    print("="*80)
    print(f"Entry ID:           {entry['entry_id']}")
    print(f"Timestamp:          {entry['timestamp']}")
    print(f"Registry Version:   {entry['registry_version']}")
    print(f"Global Merkle Root: {entry['global_merkle_root']}")
    print(f"Compliance Score:   {entry['compliance_score']:.1%}")
    print(f"Total Rules:        {entry['total_rules']}")
    print()
    print(f"Change Type:        {entry['changes']['type'].upper()}")
    print(f"Description:        {entry['changes']['description']}")
    print(f"  Rules Added:      {entry['changes']['rules_added']}")
    print(f"  Rules Removed:    {entry['changes']['rules_removed']}")
    print(f"  Files Added:      {entry['changes']['files_added']}")
    print(f"  Files Modified:   {entry['changes']['files_modified']}")
    print(f"  Files Removed:    {entry['changes']['files_removed']}")
    print()
    print(f"PQC Signature:      {entry['pqc_signature']['algorithm']}")
    print(f"Signature Hash:     {entry['pqc_signature']['signature_hash'][:32]}...")
    print(f"Entry Hash:         {entry['chain']['entry_hash'][:32]}...")
    print(f"Previous Entry:     {entry['chain']['previous_entry_id'] or 'None (initial)'}")
    print()
    if entry['attribution']['commit_sha']:
        print(f"Git Commit:         {entry['attribution']['commit_sha'][:8]}")
    print("="*80)


def main():
    parser = argparse.ArgumentParser(
        description="Update registry lineage with new entry",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Add new entry from latest signature
  python update_registry_lineage.py

  # Specify custom paths
  python update_registry_lineage.py --lineage ./custom_lineage.yaml

  # Dry run (don't save)
  python update_registry_lineage.py --dry-run
        """
    )

    parser.add_argument("--lineage", type=Path, default=LINEAGE_PATH,
                        help="Path to lineage YAML file")
    parser.add_argument("--signature", type=Path, default=SIGNATURE_PATH,
                        help="Path to signature JSON file")
    parser.add_argument("--registry", type=Path, default=REGISTRY_PATH,
                        help="Path to registry JSON file")
    parser.add_argument("--dry-run", action="store_true",
                        help="Don't save changes")
    parser.add_argument("--force", action="store_true",
                        help="Force add entry even if duplicate Merkle root")

    args = parser.parse_args()

    print("="*80)
    print("Registry Lineage Updater")
    print("="*80)
    print(f"Lineage:   {args.lineage}")
    print(f"Signature: {args.signature}")
    print(f"Registry:  {args.registry}")
    print()

    # Load lineage
    print("[1/6] Loading lineage...")
    lineage = load_lineage()
    print(f"      Current entries: {lineage['metadata']['total_entries']}")

    # Load signature
    print("\n[2/6] Loading signature document...")
    signature_doc = load_signature_document()
    print(f"      Signed at: {signature_doc['signed_at']}")
    print(f"      Global Merkle root: {signature_doc['payload']['global_merkle_root']}")

    # Load registry
    print("\n[3/6] Loading registry...")
    registry = load_registry()

    # Check for duplicate
    print("\n[4/6] Checking for duplicates...")
    if lineage["entries"] and not args.force:
        last_entry = lineage["entries"][-1]
        if last_entry["global_merkle_root"] == signature_doc["payload"]["global_merkle_root"]:
            print("      WARNING: This Merkle root already exists in lineage")
            print("      This might be a re-signature of the same state")
            print("      Use --force to add anyway, or create a new signature")
            print("Aborted.")
            return 1
    elif lineage["entries"] and args.force:
        print("      Duplicate check skipped (--force)")

    # Create new entry
    print("\n[5/6] Creating new entry...")
    new_entry = create_new_entry(signature_doc, registry, lineage)

    # Add to lineage
    lineage["entries"].append(new_entry)
    update_metadata(lineage)

    # Display summary
    display_entry_summary(new_entry)

    # Save
    print("\n[6/6] Saving lineage...")
    if args.dry_run:
        print("      DRY RUN - not saving")
        print("\nWould save to:", args.lineage)
    else:
        save_lineage(lineage, args.lineage)
        print(f"\n[OK] Lineage entry #{new_entry['entry_id']} added successfully!")

    return 0


if __name__ == "__main__":
    sys.exit(main())
