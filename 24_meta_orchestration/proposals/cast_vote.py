#!/usr/bin/env python3
"""
DAO Proposal Vote Casting
==========================

Allows validators to cast votes on DAO proposals.

Vote Options:
  - yes: Approve proposal
  - no: Reject proposal
  - abstain: Abstain from voting

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
import hashlib
from pathlib import Path
from datetime import datetime, timezone

# Paths
REPO_ROOT = Path(__file__).resolve().parents[2]
PROPOSALS_DIR = REPO_ROOT / "24_meta_orchestration" / "proposals"
VALIDATORS_CONFIG = PROPOSALS_DIR / "validators.yaml"


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


def load_validators() -> dict:
    """Load validator configuration."""
    if not VALIDATORS_CONFIG.exists():
        # Create default validators config
        default_validators = {
            "version": "1.0.0",
            "validators": [
                {
                    "id": "validator-1",
                    "name": "Primary Validator",
                    "voting_power": 1.0,
                    "active": True
                },
                {
                    "id": "validator-2",
                    "name": "Secondary Validator",
                    "voting_power": 1.0,
                    "active": True
                },
                {
                    "id": "validator-3",
                    "name": "Tertiary Validator",
                    "voting_power": 1.0,
                    "active": True
                }
            ],
            "total_voting_power": 3.0
        }

        with open(VALIDATORS_CONFIG, 'w', encoding='utf-8') as f:
            yaml.dump(default_validators, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

        print(f"[INFO] Created default validators config: {VALIDATORS_CONFIG}")
        return default_validators

    with open(VALIDATORS_CONFIG, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def validate_voting_period(proposal: dict) -> tuple[bool, str]:
    """Check if voting period is active."""
    voting = proposal.get("voting", {})
    status = voting.get("status")

    if status != "VOTING":
        return False, f"Voting not active (status: {status})"

    start_time_str = voting.get("start_time")
    end_time_str = voting.get("end_time")

    if not start_time_str or not end_time_str:
        return False, "Voting period not set"

    now = datetime.now(timezone.utc)
    start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
    end_time = datetime.fromisoformat(end_time_str.replace('Z', '+00:00'))

    if now < start_time:
        return False, "Voting has not started yet"

    if now > end_time:
        return False, "Voting period has ended"

    return True, "Voting period active"


def cast_vote(proposal: dict, validator_id: str, vote: str, validators_config: dict) -> None:
    """Cast a vote."""

    # Validate validator exists
    validator = next((v for v in validators_config["validators"] if v["id"] == validator_id), None)

    if not validator:
        print(f"ERROR: Validator not found: {validator_id}", file=sys.stderr)
        print(f"Available validators: {[v['id'] for v in validators_config['validators']]}", file=sys.stderr)
        sys.exit(1)

    if not validator.get("active", True):
        print(f"ERROR: Validator {validator_id} is not active", file=sys.stderr)
        sys.exit(1)

    # Check if already voted
    existing_votes = proposal["voting"].get("validators", [])
    existing_vote = next((v for v in existing_votes if v["validator_id"] == validator_id), None)

    if existing_vote:
        print(f"WARNING: Validator {validator_id} already voted: {existing_vote['vote']}")
        print("Updating vote...")
        existing_vote["vote"] = vote
        existing_vote["timestamp"] = datetime.now(timezone.utc).isoformat()
    else:
        # Add new vote
        vote_entry = {
            "validator_id": validator_id,
            "validator_name": validator.get("name", validator_id),
            "vote": vote,
            "voting_power": validator.get("voting_power", 1.0),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        if "validators" not in proposal["voting"]:
            proposal["voting"]["validators"] = []

        proposal["voting"]["validators"].append(vote_entry)

    # Update vote counts
    votes = proposal["voting"]["validators"]
    proposal["voting"]["votes"]["yes"] = sum(v.get("voting_power", 1.0) for v in votes if v["vote"] == "yes")
    proposal["voting"]["votes"]["no"] = sum(v.get("voting_power", 1.0) for v in votes if v["vote"] == "no")
    proposal["voting"]["votes"]["abstain"] = sum(v.get("voting_power", 1.0) for v in votes if v["vote"] == "abstain")

    print(f"\n[OK] Vote cast: {vote.upper()}")
    print(f"     Validator:     {validator_id}")
    print(f"     Voting Power:  {validator.get('voting_power', 1.0)}")
    print(f"     Timestamp:     {datetime.now(timezone.utc).isoformat()}")


def display_vote_summary(proposal: dict, validators_config: dict) -> None:
    """Display current vote summary."""
    voting = proposal["voting"]
    votes = voting["votes"]
    total_power = validators_config["total_voting_power"]

    print("\n" + "-"*80)
    print("Current Vote Summary:")
    print("-"*80)
    print(f"  Yes:      {votes['yes']:.1f} / {total_power:.1f} ({votes['yes']/total_power*100:.1f}%)")
    print(f"  No:       {votes['no']:.1f} / {total_power:.1f} ({votes['no']/total_power*100:.1f}%)")
    print(f"  Abstain:  {votes['abstain']:.1f} / {total_power:.1f} ({votes['abstain']/total_power*100:.1f}%)")
    print("-"*80)

    total_votes = votes['yes'] + votes['no'] + votes['abstain']
    participation = total_votes / total_power
    quorum = proposal["governance"]["quorum"]
    approval_threshold = proposal["governance"]["approval_threshold"]

    print(f"  Participation:  {participation:.1%} (quorum: {quorum:.0%})")

    if participation >= quorum:
        print("  Quorum:         [REACHED]")

        approval_ratio = votes['yes'] / (votes['yes'] + votes['no']) if (votes['yes'] + votes['no']) > 0 else 0

        print(f"  Approval:       {approval_ratio:.1%} (threshold: {approval_threshold:.0%})")

        if approval_ratio >= approval_threshold:
            print("  Status:         [WILL PASS]")
        else:
            print("  Status:         [WILL FAIL]")
    else:
        print("  Quorum:         [NOT REACHED]")
        print("  Status:         [PENDING MORE VOTES]")

    print("-"*80)


def main():
    parser = argparse.ArgumentParser(
        description="Cast vote on DAO proposal",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Vote yes
  python cast_vote.py LINEAGE-UPDATE-20251017-102944 --vote yes --validator validator-1

  # Vote no
  python cast_vote.py LINEAGE-UPDATE-20251017-102944 --vote no --validator validator-2

  # Abstain
  python cast_vote.py LINEAGE-UPDATE-20251017-102944 --vote abstain --validator validator-3

  # Dry run
  python cast_vote.py LINEAGE-UPDATE-20251017-102944 --vote yes --validator validator-1 --dry-run
        """
    )

    parser.add_argument("proposal_id",
                        help="Proposal ID to vote on")
    parser.add_argument("--vote", choices=["yes", "no", "abstain"], required=True,
                        help="Vote: yes, no, or abstain")
    parser.add_argument("--validator", default="validator-1",
                        help="Validator ID (default: validator-1)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Don't save vote")

    args = parser.parse_args()

    print("="*80)
    print("DAO Proposal Vote Casting")
    print("="*80)
    print()

    # Load proposal
    proposal_path = PROPOSALS_DIR / f"{args.proposal_id.lower()}.yaml"
    print(f"[1/4] Loading proposal: {args.proposal_id}")
    proposal = load_proposal(proposal_path)

    # Load validators
    print(f"[2/4] Loading validators...")
    validators = load_validators()

    # Validate voting period
    print(f"[3/4] Validating voting period...")
    valid, message = validate_voting_period(proposal)

    if not valid:
        print(f"ERROR: {message}", file=sys.stderr)
        sys.exit(1)

    print(f"      {message}")

    # Cast vote
    print(f"[4/4] Casting vote...")
    cast_vote(proposal, args.validator, args.vote, validators)

    # Save
    if args.dry_run:
        print("\n      DRY RUN - not saving")
    else:
        save_proposal(proposal, proposal_path)
        print(f"\n      Saved to: {proposal_path}")

    # Display summary
    display_vote_summary(proposal, validators)

    print()
    print("="*80)
    print("Next Steps:")
    print(f"  - Cast more votes: python cast_vote.py {args.proposal_id} --vote <yes|no|abstain> --validator <id>")
    print(f"  - Tally votes: python tally_votes.py {args.proposal_id}")
    print("="*80)
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
