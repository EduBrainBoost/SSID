#!/usr/bin/env python3
"""
DAO Proposal Vote Tallying & Execution
========================================

Tallies votes for a DAO proposal and executes if approved.

Actions:
  1. Check voting period ended
  2. Tally votes
  3. Check quorum reached
  4. Check approval threshold met
  5. Execute proposal if approved
  6. Update registry

Exit Codes:
  0 - Success (proposal approved and executed)
  1 - Proposal rejected or quorum not reached
  2 - Error

Author: SSID Compliance Team
Version: 1.0.0
Date: 2025-10-17
"""

import sys
import yaml
import argparse
import shutil
from pathlib import Path
from datetime import datetime, timezone, timedelta

# Paths
REPO_ROOT = Path(__file__).resolve().parents[2]
PROPOSALS_DIR = REPO_ROOT / "24_meta_orchestration" / "proposals"
REGISTRY_PATH = PROPOSALS_DIR / "registry.yaml"
LINEAGE_PATH = REPO_ROOT / "23_compliance" / "registry" / "registry_lineage.yaml"


def load_proposal(proposal_path: Path) -> dict:
    """Load proposal YAML."""
    if not proposal_path.exists():
        print(f"ERROR: Proposal not found: {proposal_path}", file=sys.stderr)
        sys.exit(2)

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
        sys.exit(2)

    with open(REGISTRY_PATH, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def save_registry(registry: dict) -> None:
    """Save proposal registry."""
    with open(REGISTRY_PATH, 'w', encoding='utf-8') as f:
        yaml.dump(registry, f, default_flow_style=False, allow_unicode=True, sort_keys=False)


def load_validators() -> dict:
    """Load validator configuration."""
    validators_path = PROPOSALS_DIR / "validators.yaml"

    if not validators_path.exists():
        print("ERROR: Validators config not found", file=sys.stderr)
        sys.exit(2)

    with open(validators_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def check_voting_ended(proposal: dict) -> tuple[bool, str]:
    """Check if voting period has ended."""
    voting = proposal.get("voting", {})
    status = voting.get("status")

    if status != "VOTING":
        return False, f"Voting not active (status: {status})"

    end_time_str = voting.get("end_time")
    if not end_time_str:
        return False, "Voting end time not set"

    now = datetime.now(timezone.utc)
    end_time = datetime.fromisoformat(end_time_str.replace('Z', '+00:00'))

    if now < end_time:
        return False, f"Voting still active (ends {end_time.isoformat()})"

    return True, "Voting period ended"


def tally_votes(proposal: dict, validators_config: dict) -> dict:
    """Tally votes and determine outcome."""
    voting = proposal["voting"]
    votes = voting["votes"]
    governance = proposal["governance"]

    total_power = validators_config["total_voting_power"]
    total_votes = votes['yes'] + votes['no'] + votes['abstain']

    participation = total_votes / total_power if total_power > 0 else 0
    quorum_reached = participation >= governance["quorum"]

    # Calculate approval ratio (excluding abstentions)
    total_decisive_votes = votes['yes'] + votes['no']
    approval_ratio = votes['yes'] / total_decisive_votes if total_decisive_votes > 0 else 0

    approved = quorum_reached and approval_ratio >= governance["approval_threshold"]

    result = {
        "total_voting_power": total_power,
        "total_votes_cast": total_votes,
        "participation": participation,
        "quorum_required": governance["quorum"],
        "quorum_reached": quorum_reached,
        "yes_votes": votes['yes'],
        "no_votes": votes['no'],
        "abstain_votes": votes['abstain'],
        "approval_ratio": approval_ratio,
        "approval_threshold": governance["approval_threshold"],
        "approved": approved,
        "outcome": "APPROVED" if approved else ("REJECTED" if quorum_reached else "QUORUM_NOT_REACHED")
    }

    return result


def execute_proposal(proposal: dict, proposal_id: str) -> tuple[bool, str]:
    """Execute approved proposal."""

    if proposal["type"] != "lineage_update":
        return False, f"Unknown proposal type: {proposal['type']}"

    # Execute lineage update
    try:
        # Load current lineage
        with open(LINEAGE_PATH, 'r', encoding='utf-8') as f:
            lineage = yaml.safe_load(f)

        # Add proposed entry
        proposed_entry = proposal["proposed_entry"]

        # Verify entry_id is sequential
        expected_entry_id = len(lineage["entries"]) + 1
        if proposed_entry["entry_id"] != expected_entry_id:
            return False, f"Entry ID mismatch (expected {expected_entry_id}, got {proposed_entry['entry_id']})"

        # Add governance approval metadata
        proposed_entry["dao_approval"] = {
            "proposal_id": proposal_id,
            "approved_at": datetime.now(timezone.utc).isoformat(),
            "approval_ratio": proposal["voting"].get("votes", {}).get("yes", 0) / (
                proposal["voting"].get("votes", {}).get("yes", 0) +
                proposal["voting"].get("votes", {}).get("no", 0)
            ) if (proposal["voting"].get("votes", {}).get("yes", 0) + proposal["voting"].get("votes", {}).get("no", 0)) > 0 else 0,
            "quorum": len(proposal["voting"].get("validators", [])),
            "governance_locked": True
        }

        # Recalculate entry hash after adding DAO approval
        entry_copy = proposed_entry.copy()
        if 'chain' in entry_copy and 'entry_hash' in entry_copy['chain']:
            entry_copy['chain'] = entry_copy['chain'].copy()
            del entry_copy['chain']['entry_hash']

        canonical = json.dumps(entry_copy, sort_keys=True, ensure_ascii=False)
        proposed_entry["chain"]["entry_hash"] = hashlib.sha256(canonical.encode('utf-8')).hexdigest()

        # Append entry
        lineage["entries"].append(proposed_entry)

        # Update metadata
        lineage["metadata"]["total_entries"] = len(lineage["entries"])
        lineage["metadata"]["last_entry"] = proposed_entry["timestamp"]

        # Backup current lineage
        backup_path = LINEAGE_PATH.parent / f"registry_lineage_backup_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.yaml"
        shutil.copy(LINEAGE_PATH, backup_path)

        # Save updated lineage
        with open(LINEAGE_PATH, 'w', encoding='utf-8') as f:
            yaml.dump(lineage, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

        return True, f"Lineage updated: Entry #{proposed_entry['entry_id']} added (backup: {backup_path.name})"

    except Exception as e:
        return False, f"Execution failed: {e}"


def update_proposal_status(proposal: dict, result: dict, execution_result: tuple[bool, str]) -> None:
    """Update proposal with final status."""

    proposal["voting"]["status"] = "COMPLETED"
    proposal["voting"]["tallied_at"] = datetime.now(timezone.utc).isoformat()
    proposal["voting"]["result"] = result

    if result["approved"]:
        proposal["execution"]["status"] = "EXECUTED" if execution_result[0] else "FAILED"
        proposal["execution"]["executed_at"] = datetime.now(timezone.utc).isoformat()
        proposal["execution"]["executed_by"] = "DAO Consensus"
        proposal["execution"]["result"] = execution_result[1]
    else:
        proposal["execution"]["status"] = "REJECTED"
        proposal["execution"]["result"] = result["outcome"]


def update_registry_status(registry: dict, proposal_id: str, approved: bool) -> None:
    """Update proposal status in registry."""
    for prop in registry.get("proposals", []):
        if prop["proposal_id"] == proposal_id:
            prop["status"] = "APPROVED" if approved else "REJECTED"
            prop["finalized_at"] = datetime.now(timezone.utc).isoformat()
            break

    registry["last_updated_utc"] = datetime.now(timezone.utc).isoformat()
    registry["active_proposals"] = sum(1 for p in registry["proposals"] if p["status"] in ["PENDING_VOTE", "VOTING"])
    registry["archived_proposals"] = sum(1 for p in registry["proposals"] if p["status"] in ["APPROVED", "REJECTED"])


def display_results(proposal: dict, result: dict, execution_result: tuple[bool, str]) -> None:
    """Display tallying results."""
    print("\n" + "="*80)
    print("VOTE TALLYING RESULTS")
    print("="*80)

    print(f"\nProposal: {proposal['proposal_id']}")
    print(f"Title:    {proposal['title']}")

    print(f"\nVoting Summary:")
    print(f"  Total Voting Power:  {result['total_voting_power']:.1f}")
    print(f"  Votes Cast:          {result['total_votes_cast']:.1f}")
    print(f"  Participation:       {result['participation']:.1%}")

    print(f"\nVote Distribution:")
    print(f"  Yes:                 {result['yes_votes']:.1f} ({result['yes_votes']/result['total_voting_power']*100:.1f}%)")
    print(f"  No:                  {result['no_votes']:.1f} ({result['no_votes']/result['total_voting_power']*100:.1f}%)")
    print(f"  Abstain:             {result['abstain_votes']:.1f} ({result['abstain_votes']/result['total_voting_power']*100:.1f}%)")

    print(f"\nGovernance Checks:")
    print(f"  Quorum Required:     {result['quorum_required']:.0%}")
    print(f"  Quorum Reached:      {'[YES]' if result['quorum_reached'] else '[NO]'}")

    if result['quorum_reached']:
        print(f"  Approval Ratio:      {result['approval_ratio']:.1%}")
        print(f"  Approval Threshold:  {result['approval_threshold']:.0%}")
        print(f"  Threshold Met:       {'[YES]' if result['approved'] else '[NO]'}")

    print("\n" + "="*80)

    if result["approved"]:
        print("OUTCOME: [APPROVED]")
        print("="*80)
        print(f"\nThe proposal has been approved by DAO consensus.")
        print(f"Approval ratio: {result['approval_ratio']:.1%} (threshold: {result['approval_threshold']:.0%})")

        print(f"\nExecution:")
        if execution_result[0]:
            print(f"  Status:  [SUCCESS]")
            print(f"  Result:  {execution_result[1]}")
        else:
            print(f"  Status:  [FAILED]")
            print(f"  Error:   {execution_result[1]}")
    else:
        print(f"OUTCOME: [{result['outcome']}]")
        print("="*80)

        if result['quorum_reached']:
            print(f"\nThe proposal was rejected by DAO vote.")
            print(f"Approval ratio: {result['approval_ratio']:.1%} (threshold: {result['approval_threshold']:.0%})")
        else:
            print(f"\nThe proposal failed due to insufficient quorum.")
            print(f"Participation: {result['participation']:.1%} (required: {result['quorum_required']:.0%})")

    print("="*80 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Tally votes and execute DAO proposal",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Tally votes
  python tally_votes.py LINEAGE-UPDATE-20251017-102944

  # Dry run
  python tally_votes.py LINEAGE-UPDATE-20251017-102944 --dry-run

  # Force tally before voting period ends (for testing)
  python tally_votes.py LINEAGE-UPDATE-20251017-102944 --force
        """
    )

    parser.add_argument("proposal_id",
                        help="Proposal ID to tally")
    parser.add_argument("--dry-run", action="store_true",
                        help="Don't save results or execute")
    parser.add_argument("--force", action="store_true",
                        help="Tally even if voting period hasn't ended")

    args = parser.parse_args()

    print("="*80)
    print("DAO Proposal Vote Tallying")
    print("="*80)
    print()

    # Load proposal
    proposal_path = PROPOSALS_DIR / f"{args.proposal_id.lower()}.yaml"
    print(f"[1/6] Loading proposal: {args.proposal_id}")
    proposal = load_proposal(proposal_path)

    # Load validators
    print(f"[2/6] Loading validators...")
    validators = load_validators()

    # Check voting ended
    print(f"[3/6] Checking voting period...")
    ended, message = check_voting_ended(proposal)

    if not ended and not args.force:
        print(f"ERROR: {message}", file=sys.stderr)
        print("Use --force to tally before voting ends (for testing)", file=sys.stderr)
        sys.exit(1)

    if args.force and not ended:
        print(f"      WARNING: Forcing tally before voting ends")
    else:
        print(f"      {message}")

    # Tally votes
    print(f"[4/6] Tallying votes...")
    result = tally_votes(proposal, validators)
    print(f"      Outcome: {result['outcome']}")

    # Execute if approved
    execution_result = (True, "Not executed (proposal rejected)")

    if result["approved"]:
        print(f"[5/6] Executing proposal...")

        if args.dry_run:
            print(f"      DRY RUN - not executing")
            execution_result = (True, "Dry run - execution skipped")
        else:
            execution_result = execute_proposal(proposal, args.proposal_id)

            if execution_result[0]:
                print(f"      [SUCCESS] {execution_result[1]}")
            else:
                print(f"      [FAILED] {execution_result[1]}")
    else:
        print(f"[5/6] Execution skipped (proposal not approved)")

    # Update proposal and registry
    print(f"[6/6] Updating proposal status...")

    if args.dry_run:
        print(f"      DRY RUN - not saving")
    else:
        update_proposal_status(proposal, result, execution_result)
        save_proposal(proposal, proposal_path)

        registry = load_registry()
        update_registry_status(registry, args.proposal_id, result["approved"])
        save_registry(registry)

        print(f"      Saved to: {proposal_path}")

    # Display results
    display_results(proposal, result, execution_result)

    # Exit code
    return 0 if result["approved"] else 1


if __name__ == "__main__":
    sys.exit(main())
