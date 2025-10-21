#!/usr/bin/env python3
"""
DAO Proposal Voting Initiator
==============================

Starts the voting period for a DAO proposal.

Actions:
  1. Load proposal
  2. Validate proposal is in correct state
  3. Set voting start/end times
  4. Update proposal status to VOTING
  5. Update registry

Exit Codes:
  0 - Success
  1 - Error

Author: SSID Compliance Team
Version: 1.0.0
Date: 2025-10-17
"""

import sys
import yaml
import argparse
from pathlib import Path
from datetime import datetime, timezone, timedelta

# Paths
REPO_ROOT = Path(__file__).resolve().parents[2]
PROPOSALS_DIR = REPO_ROOT / "24_meta_orchestration" / "proposals"
REGISTRY_PATH = PROPOSALS_DIR / "registry.yaml"


def load_proposal(proposal_path: Path) -> dict:
    """Load proposal YAML."""
    if not proposal_path.exists():
        print(f"ERROR: Proposal not found: {proposal_path}", file=sys.stderr)
        sys.exit(1)

    with open(proposal_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def save_proposal(proposal: dict, proposal_path: Path) -> None:
    """Save proposal YAML."""
    with open(proposal_path, 'w', encoding='utf-8') as f:
        yaml.dump(proposal, f, default_flow_style=False, allow_unicode=True, sort_keys=False)


def load_registry() -> dict:
    """Load proposal registry."""
    if not REGISTRY_PATH.exists():
        print(f"ERROR: Registry not found: {REGISTRY_PATH}", file=sys.stderr)
        sys.exit(1)

    with open(REGISTRY_PATH, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def save_registry(registry: dict) -> None:
    """Save proposal registry."""
    with open(REGISTRY_PATH, 'w', encoding='utf-8') as f:
        yaml.dump(registry, f, default_flow_style=False, allow_unicode=True, sort_keys=False)


def start_voting(proposal: dict, proposal_id: str) -> None:
    """Start voting period for proposal."""

    # Check current status
    current_status = proposal.get("voting", {}).get("status")

    if current_status == "VOTING":
        print(f"WARNING: Voting already started for {proposal_id}")
        return

    if current_status not in ["PENDING", "AWAITING_APPROVAL", None]:
        print(f"ERROR: Cannot start voting for proposal in status: {current_status}", file=sys.stderr)
        sys.exit(1)

    # Set voting times
    now = datetime.now(timezone.utc)
    voting_period_hours = proposal["governance"]["voting_period_hours"]
    end_time = now + timedelta(hours=voting_period_hours)

    proposal["voting"]["status"] = "VOTING"
    proposal["voting"]["start_time"] = now.isoformat()
    proposal["voting"]["end_time"] = end_time.isoformat()

    print(f"\n[OK] Voting started for {proposal_id}")
    print(f"     Start:  {now.isoformat()}")
    print(f"     End:    {end_time.isoformat()}")
    print(f"     Period: {voting_period_hours} hours")


def update_registry_status(registry: dict, proposal_id: str) -> None:
    """Update proposal status in registry."""
    for prop in registry.get("proposals", []):
        if prop["proposal_id"] == proposal_id:
            prop["status"] = "VOTING"
            break

    registry["last_updated_utc"] = datetime.now(timezone.utc).isoformat()
    registry["active_proposals"] = sum(1 for p in registry["proposals"] if p["status"] in ["PENDING_VOTE", "VOTING"])


def main():
    parser = argparse.ArgumentParser(
        description="Start voting period for DAO proposal",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start voting
  python start_voting.py LINEAGE-UPDATE-20251017-102944

  # Dry run
  python start_voting.py LINEAGE-UPDATE-20251017-102944 --dry-run
        """
    )

    parser.add_argument("proposal_id",
                        help="Proposal ID to start voting for")
    parser.add_argument("--dry-run", action="store_true",
                        help="Don't save changes")

    args = parser.parse_args()

    print("="*80)
    print("DAO Proposal Voting Initiator")
    print("="*80)
    print()

    # Load proposal
    proposal_path = PROPOSALS_DIR / f"{args.proposal_id.lower()}.yaml"
    print(f"[1/4] Loading proposal: {args.proposal_id}")
    proposal = load_proposal(proposal_path)

    # Load registry
    print(f"[2/4] Loading registry...")
    registry = load_registry()

    # Start voting
    print(f"[3/4] Starting voting period...")
    start_voting(proposal, args.proposal_id)

    # Save
    print(f"[4/4] Saving changes...")
    if args.dry_run:
        print("      DRY RUN - not saving")
    else:
        save_proposal(proposal, proposal_path)
        update_registry_status(registry, args.proposal_id)
        save_registry(registry)
        print(f"      Saved to: {proposal_path}")

    print()
    print("="*80)
    print("Next Steps:")
    print(f"  1. Cast votes: python cast_vote.py {args.proposal_id} --vote yes")
    print(f"  2. Tally votes: python tally_votes.py {args.proposal_id}")
    print("="*80)
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
