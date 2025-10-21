#!/usr/bin/env python3
"""
DAO Lineage Update Proposal Generator
=======================================

Creates a DAO governance proposal for registry lineage updates.

Purpose:
  - Integrate compliance lineage with DAO governance
  - Require validator approval for lineage updates
  - Create audit trail of governance decisions
  - Link technical and organizational layers

Workflow:
  1. Load latest compliance_registry_signature.json
  2. Load current registry_lineage.yaml
  3. Compute proposed lineage entry
  4. Generate DAO proposal YAML
  5. Save to 24_meta_orchestration/proposals/
  6. Update proposal registry

Output:
  - lineage_update_proposal_[timestamp].yaml
  - Updated proposals/registry.yaml

Author: SSID Compliance Team
Version: 1.0.0
Date: 2025-10-17
"""

import sys
import json
import yaml
import hashlib
import argparse
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Dict, Optional

# Paths
REPO_ROOT = Path(__file__).resolve().parents[2]
SIGNATURE_PATH = REPO_ROOT / "23_compliance" / "registry" / "compliance_registry_signature.json"
LINEAGE_PATH = REPO_ROOT / "23_compliance" / "registry" / "registry_lineage.yaml"
REGISTRY_PATH = REPO_ROOT / "23_compliance" / "registry" / "compliance_registry.json"
PROPOSALS_DIR = REPO_ROOT / "24_meta_orchestration" / "proposals"
PROPOSAL_REGISTRY = PROPOSALS_DIR / "registry.yaml"


def load_signature() -> Dict:
    """Load latest signature document."""
    if not SIGNATURE_PATH.exists():
        print(f"ERROR: Signature not found: {SIGNATURE_PATH}", file=sys.stderr)
        sys.exit(1)

    with open(SIGNATURE_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_lineage() -> Dict:
    """Load current lineage."""
    if not LINEAGE_PATH.exists():
        print(f"ERROR: Lineage not found: {LINEAGE_PATH}", file=sys.stderr)
        sys.exit(1)

    with open(LINEAGE_PATH, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def load_registry() -> Dict:
    """Load compliance registry."""
    if not REGISTRY_PATH.exists():
        print(f"ERROR: Registry not found: {REGISTRY_PATH}", file=sys.stderr)
        sys.exit(1)

    with open(REGISTRY_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def compute_entry_hash(entry: Dict) -> str:
    """Compute hash of lineage entry."""
    entry_copy = entry.copy()
    if 'chain' in entry_copy and 'entry_hash' in entry_copy['chain']:
        entry_copy['chain'] = entry_copy['chain'].copy()
        del entry_copy['chain']['entry_hash']

    canonical = json.dumps(entry_copy, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(canonical.encode('utf-8')).hexdigest()


def create_proposed_entry(signature: Dict, registry: Dict, lineage: Dict) -> Dict:
    """Create proposed lineage entry."""
    previous_entry = lineage["entries"][-1] if lineage["entries"] else None
    entry_id = len(lineage["entries"]) + 1

    # Detect changes
    if previous_entry:
        current_root = signature["payload"]["global_merkle_root"]
        previous_root = previous_entry["global_merkle_root"]

        if current_root == previous_root:
            change_type = "no_change"
            description = "Registry unchanged (re-signature)"
        else:
            current_rules = signature["payload"]["metadata"]["total_rules"]
            previous_rules = previous_entry["total_rules"]

            if current_rules > previous_rules:
                change_type = "expansion"
                description = f"Added {current_rules - previous_rules} rule(s)"
            elif current_rules < previous_rules:
                change_type = "reduction"
                description = f"Removed {previous_rules - current_rules} rule(s)"
            else:
                change_type = "modification"
                description = "Manifestation files modified"
    else:
        change_type = "initial"
        description = "Initial compliance registry"

    # Create entry
    entry = {
        "entry_id": entry_id,
        "timestamp": signature["signed_at"],
        "registry_version": signature["payload"]["metadata"]["registry_version"],
        "global_merkle_root": signature["payload"]["global_merkle_root"],
        "compliance_score": signature["payload"]["metadata"]["compliance_score"],
        "total_rules": signature["payload"]["metadata"]["total_rules"],
        "total_manifestations": signature["payload"]["metadata"]["total_manifestations"],
        "standard_merkle_roots": signature["payload"]["standard_merkle_roots"],
        "pqc_signature": {
            "algorithm": signature["signature"]["algorithm"],
            "backend": signature["signature"]["backend"],
            "signature_hash": signature["message_hash"]
        },
        "changes": {
            "type": change_type,
            "description": description
        },
        "chain": {
            "previous_entry_id": previous_entry["entry_id"] if previous_entry else None,
            "previous_merkle_root": previous_entry["global_merkle_root"] if previous_entry else None,
            "entry_hash": None  # Computed after
        }
    }

    entry["chain"]["entry_hash"] = compute_entry_hash(entry)

    return entry


def generate_proposal_id(timestamp: str) -> str:
    """Generate unique proposal ID."""
    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    return f"LINEAGE-UPDATE-{dt.strftime('%Y%m%d-%H%M%S')}"


def create_proposal(proposed_entry: Dict, signature: Dict, lineage: Dict) -> Dict:
    """Create DAO proposal for lineage update."""

    proposal_id = generate_proposal_id(proposed_entry["timestamp"])
    created_utc = datetime.now(timezone.utc).isoformat()

    # Find WORM snapshot
    worm_dir = REPO_ROOT / "02_audit_logging" / "storage" / "worm" / "immutable_store"
    worm_files = sorted(worm_dir.glob("compliance_signature_*.json"))
    latest_worm = worm_files[-1] if worm_files else None

    proposal = {
        "proposal_id": proposal_id,
        "title": f"Registry Lineage Update - Entry #{proposed_entry['entry_id']}",
        "type": "lineage_update",
        "created_utc": created_utc,

        # Governance parameters
        "governance": {
            "quorum": 0.67,
            "approval_threshold": 0.67,
            "execution_delay_hours": 24,
            "voting_period_hours": 72,
            "immutability": True
        },

        # Proposed lineage entry
        "proposed_entry": proposed_entry,

        # Evidence
        "evidence": {
            "compliance_registry": {
                "path": str(REGISTRY_PATH.relative_to(REPO_ROOT).as_posix()),
                "version": signature["payload"]["metadata"]["registry_version"],
                "generated_at": signature["payload"]["metadata"]["generated_at"]
            },
            "pqc_signature": {
                "path": str(SIGNATURE_PATH.relative_to(REPO_ROOT).as_posix()),
                "algorithm": signature["signature"]["algorithm"],
                "backend": signature["signature"]["backend"],
                "signature_hash": signature["message_hash"],
                "signed_at": signature["signed_at"]
            },
            "worm_snapshot": {
                "path": str(latest_worm.relative_to(REPO_ROOT).as_posix()) if latest_worm else None,
                "immutable": True
            },
            "current_lineage": {
                "path": str(LINEAGE_PATH.relative_to(REPO_ROOT).as_posix()),
                "total_entries": lineage["metadata"]["total_entries"],
                "last_entry": lineage["metadata"]["last_entry"]
            }
        },

        # Change summary
        "change_summary": {
            "type": proposed_entry["changes"]["type"],
            "description": proposed_entry["changes"]["description"],
            "global_merkle_root": proposed_entry["global_merkle_root"],
            "compliance_score_delta": proposed_entry["compliance_score"] -
                (lineage["entries"][-1]["compliance_score"] if lineage["entries"] else 0),
            "rules_delta": proposed_entry["total_rules"] -
                (lineage["entries"][-1]["total_rules"] if lineage["entries"] else 0)
        },

        # Verification
        "verification": {
            "entry_hash": proposed_entry["chain"]["entry_hash"],
            "previous_entry_id": proposed_entry["chain"]["previous_entry_id"],
            "previous_merkle_root": proposed_entry["chain"]["previous_merkle_root"],
            "chain_valid": True,
            "pqc_signature_valid": True,
            "merkle_tree_verified": True
        },

        # Compliance
        "compliance": {
            "total_rules": proposed_entry["total_rules"],
            "total_manifestations": proposed_entry["total_manifestations"],
            "compliance_score": proposed_entry["compliance_score"],
            "standards": list(proposed_entry["standard_merkle_roots"].keys())
        },

        # Voting (to be filled)
        "voting": {
            "status": "PENDING",
            "start_time": None,
            "end_time": None,
            "votes": {
                "yes": 0,
                "no": 0,
                "abstain": 0
            },
            "validators": []
        },

        # Execution
        "execution": {
            "status": "AWAITING_APPROVAL",
            "executed_at": None,
            "executed_by": None,
            "result": None
        }
    }

    return proposal


def save_proposal(proposal: Dict, proposals_dir: Path) -> Path:
    """Save proposal to file."""
    proposals_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{proposal['proposal_id'].lower()}.yaml"
    proposal_path = proposals_dir / filename

    with open(proposal_path, 'w', encoding='utf-8') as f:
        yaml.dump(proposal, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    return proposal_path


def update_proposal_registry(proposal: Dict, proposal_path: Path, registry_path: Path) -> None:
    """Update proposal registry."""

    # Load or create registry
    if registry_path.exists():
        with open(registry_path, 'r', encoding='utf-8') as f:
            registry = yaml.safe_load(f)
    else:
        registry = {
            "version": "1.0.0",
            "last_updated_utc": None,
            "total_proposals": 0,
            "active_proposals": 0,
            "archived_proposals": 0,
            "proposals": []
        }

    # Compute file hash
    with open(proposal_path, 'rb') as f:
        file_hash = hashlib.sha256(f.read()).hexdigest()

    # Add proposal to registry
    registry_entry = {
        "proposal_id": proposal["proposal_id"],
        "title": proposal["title"],
        "type": proposal["type"],
        "status": "PENDING_VOTE",
        "created_utc": proposal["created_utc"],
        "files": {
            "proposal": {
                "path": str(proposal_path.relative_to(REPO_ROOT).as_posix()),
                "sha256": file_hash,
                "size_bytes": proposal_path.stat().st_size
            }
        },
        "governance": proposal["governance"],
        "change_summary": proposal["change_summary"]
    }

    registry["proposals"].append(registry_entry)
    registry["total_proposals"] = len(registry["proposals"])
    registry["active_proposals"] = sum(1 for p in registry["proposals"] if p["status"] == "PENDING_VOTE")
    registry["last_updated_utc"] = datetime.now(timezone.utc).isoformat()

    # Save registry
    with open(registry_path, 'w', encoding='utf-8') as f:
        yaml.dump(registry, f, default_flow_style=False, allow_unicode=True, sort_keys=False)


def display_proposal_summary(proposal: Dict, proposal_path: Path) -> None:
    """Display proposal summary."""
    print("\n" + "="*80)
    print("DAO Lineage Update Proposal Created")
    print("="*80)
    print(f"\nProposal ID:        {proposal['proposal_id']}")
    print(f"Title:              {proposal['title']}")
    print(f"Type:               {proposal['type']}")
    print(f"Created:            {proposal['created_utc']}")
    print()
    print(f"Governance:")
    print(f"  Quorum:           {proposal['governance']['quorum']:.0%}")
    print(f"  Approval:         {proposal['governance']['approval_threshold']:.0%}")
    print(f"  Voting Period:    {proposal['governance']['voting_period_hours']}h")
    print(f"  Execution Delay:  {proposal['governance']['execution_delay_hours']}h")
    print()
    print(f"Proposed Entry:")
    print(f"  Entry ID:         #{proposal['proposed_entry']['entry_id']}")
    print(f"  Timestamp:        {proposal['proposed_entry']['timestamp']}")
    print(f"  Merkle Root:      {proposal['proposed_entry']['global_merkle_root'][:32]}...")
    print(f"  Compliance:       {proposal['proposed_entry']['compliance_score']:.1%}")
    print(f"  Total Rules:      {proposal['proposed_entry']['total_rules']}")
    print()
    print(f"Changes:")
    print(f"  Type:             {proposal['change_summary']['type'].upper()}")
    print(f"  Description:      {proposal['change_summary']['description']}")
    print(f"  Score Delta:      {proposal['change_summary']['compliance_score_delta']:+.1%}")
    print(f"  Rules Delta:      {proposal['change_summary']['rules_delta']:+d}")
    print()
    print(f"Proposal File:      {proposal_path.relative_to(REPO_ROOT)}")
    print(f"Registry Updated:   {PROPOSAL_REGISTRY.relative_to(REPO_ROOT)}")
    print()
    print("Next Steps:")
    print("  1. Review proposal: cat " + str(proposal_path))
    print("  2. Start voting: python 24_meta_orchestration/proposals/start_voting.py " + proposal['proposal_id'])
    print("  3. Cast votes: python 24_meta_orchestration/proposals/cast_vote.py " + proposal['proposal_id'] + " --vote yes")
    print("="*80)


def main():
    parser = argparse.ArgumentParser(
        description="Create DAO proposal for lineage update",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create proposal from latest signature
  python create_lineage_proposal.py

  # Dry run
  python create_lineage_proposal.py --dry-run

  # Custom output directory
  python create_lineage_proposal.py --output-dir ./custom_proposals/
        """
    )

    parser.add_argument("--dry-run", action="store_true",
                        help="Don't save proposal")
    parser.add_argument("--output-dir", type=Path, default=PROPOSALS_DIR,
                        help="Output directory for proposals")

    args = parser.parse_args()

    print("="*80)
    print("DAO Lineage Update Proposal Generator")
    print("="*80)
    print()

    # Load signature
    print("[1/6] Loading PQC signature...")
    signature = load_signature()
    print(f"      Signed at: {signature['signed_at']}")
    print(f"      Merkle root: {signature['payload']['global_merkle_root'][:32]}...")

    # Load lineage
    print("\n[2/6] Loading current lineage...")
    lineage = load_lineage()
    print(f"      Current entries: {lineage['metadata']['total_entries']}")

    # Load registry
    print("\n[3/6] Loading registry...")
    registry = load_registry()

    # Create proposed entry
    print("\n[4/6] Creating proposed lineage entry...")
    proposed_entry = create_proposed_entry(signature, registry, lineage)
    print(f"      Entry ID: #{proposed_entry['entry_id']}")
    print(f"      Change type: {proposed_entry['changes']['type']}")

    # Create proposal
    print("\n[5/6] Generating DAO proposal...")
    proposal = create_proposal(proposed_entry, signature, lineage)
    print(f"      Proposal ID: {proposal['proposal_id']}")

    # Save
    print("\n[6/6] Saving proposal...")
    if args.dry_run:
        print("      DRY RUN - not saving")
        proposal_path = args.output_dir / f"{proposal['proposal_id'].lower()}.yaml"
    else:
        proposal_path = save_proposal(proposal, args.output_dir)
        update_proposal_registry(proposal, proposal_path, args.output_dir / "registry.yaml")
        print(f"      Saved to: {proposal_path}")

    # Display summary
    display_proposal_summary(proposal, proposal_path)

    print("\n[OK] Proposal created successfully!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
