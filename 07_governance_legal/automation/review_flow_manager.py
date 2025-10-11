#!/usr/bin/env python3
"""
SSID Review Flow Manager - Automated Governance Review Pipeline

This script automates the governance review and approval process, implementing
2-stage review (Technical + Compliance) with quorum-based promotion triggers.

Blueprint: v4.4.0 - Functional Expansion
Layer: L5 - Governance Layer
Compliance: GDPR / eIDAS / MiCA / DORA / AMLD6
"""

import json
import hashlib
import argparse
import sys
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from enum import Enum

# Configuration
PROMOTION_RULES_FILE = Path("07_governance_legal/automation/promotion_rules.yaml")
REVIEW_LOG_FILE = Path("24_meta_orchestration/registry/logs/governance_review.log")
REVIEW_EVENT_FILE = Path("24_meta_orchestration/registry/events/governance_review_event.json")


class ReviewState(str, Enum):
    """Review states for governance items."""
    PENDING_REVIEW = "PENDING_REVIEW"
    UNDER_REVIEW = "UNDER_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    PROMOTED = "PROMOTED"


class ReviewStage(str, Enum):
    """Review stages in the approval pipeline."""
    TECHNICAL = "TECHNICAL"
    COMPLIANCE = "COMPLIANCE"
    FINAL = "FINAL"


@dataclass
class Reviewer:
    """Represents a reviewer with role and approval authority."""
    username: str
    role: str
    stage: ReviewStage
    approval_weight: int = 1


@dataclass
class Review:
    """Represents a single review action."""
    reviewer: str
    role: str
    stage: ReviewStage
    decision: str  # "approve" or "reject"
    comment: str
    timestamp: str
    signature: str  # SHA256 digest


@dataclass
class ReviewItem:
    """Represents an item under governance review."""
    item_id: str
    item_type: str  # "blueprint", "policy", "promotion", etc.
    title: str
    description: str
    state: ReviewState
    created_at: str
    reviews: List[Review]
    technical_approvals: int = 0
    compliance_approvals: int = 0
    technical_rejections: int = 0
    compliance_rejections: int = 0

    def calculate_hash(self) -> str:
        """Calculate SHA256 digest of review item."""
        item_str = f"{self.item_id}|{self.item_type}|{self.title}|{self.state}|{self.created_at}"
        return hashlib.sha256(item_str.encode()).hexdigest()


@dataclass
class PromotionRules:
    """Governance promotion rules."""
    technical_quorum: int
    compliance_quorum: int
    require_both_stages: bool
    allow_parallel_review: bool
    auto_promote_on_quorum: bool


@dataclass
class ReviewFlowResult:
    """Result of review flow operation."""
    timestamp: str
    operation: str
    item_id: str
    state: ReviewState
    approvals: Dict[str, int]
    rejections: Dict[str, int]
    promotion_triggered: bool
    status: str


class ReviewFlowManager:
    """Manages automated governance review workflows."""

    def __init__(self):
        self.promotion_rules_file = PROMOTION_RULES_FILE
        self.review_log_file = REVIEW_LOG_FILE
        self.review_event_file = REVIEW_EVENT_FILE
        self.reviewers: List[Reviewer] = self._load_reviewers()
        self.promotion_rules: PromotionRules = self._load_promotion_rules()

    def _load_reviewers(self) -> List[Reviewer]:
        """Load reviewer configuration."""
        # Default reviewers (would be loaded from YAML in production)
        return [
            Reviewer("governance-lead", "Governance Lead", ReviewStage.FINAL, 2),
            Reviewer("compliance-officer", "Compliance Officer", ReviewStage.COMPLIANCE, 1),
            Reviewer("security-officer", "Security Officer", ReviewStage.COMPLIANCE, 1),
            Reviewer("technical-lead", "Technical Lead", ReviewStage.TECHNICAL, 1),
            Reviewer("architect", "System Architect", ReviewStage.TECHNICAL, 1),
        ]

    def _load_promotion_rules(self) -> PromotionRules:
        """Load promotion rules."""
        # Default rules (would be loaded from YAML in production)
        return PromotionRules(
            technical_quorum=2,
            compliance_quorum=2,
            require_both_stages=True,
            allow_parallel_review=True,
            auto_promote_on_quorum=True
        )

    def create_review_item(
        self,
        item_type: str,
        title: str,
        description: str
    ) -> ReviewItem:
        """Create a new review item."""
        print("=" * 60)
        print("  SSID Review Flow Manager - Create Review Item")
        print("=" * 60)
        print()

        item_id = self._generate_item_id(item_type, title)

        review_item = ReviewItem(
            item_id=item_id,
            item_type=item_type,
            title=title,
            description=description,
            state=ReviewState.PENDING_REVIEW,
            created_at=datetime.utcnow().isoformat() + "Z",
            reviews=[]
        )

        print(f"Review Item Created:")
        print(f"  ID: {item_id}")
        print(f"  Type: {item_type}")
        print(f"  Title: {title}")
        print(f"  State: {review_item.state}")
        print()

        self._save_review_item(review_item)
        self._log_review_event("item_created", review_item)

        return review_item

    def submit_review(
        self,
        item_id: str,
        reviewer_username: str,
        decision: str,
        comment: str = ""
    ) -> ReviewFlowResult:
        """Submit a review for an item."""
        print("=" * 60)
        print("  SSID Review Flow Manager - Submit Review")
        print("=" * 60)
        print()

        # Load review item
        review_item = self._load_review_item(item_id)

        if not review_item:
            raise ValueError(f"Review item not found: {item_id}")

        # Find reviewer
        reviewer = self._find_reviewer(reviewer_username)

        if not reviewer:
            raise ValueError(f"Reviewer not authorized: {reviewer_username}")

        # Create review
        review = Review(
            reviewer=reviewer_username,
            role=reviewer.role,
            stage=reviewer.stage,
            decision=decision,
            comment=comment,
            timestamp=datetime.utcnow().isoformat() + "Z",
            signature=self._sign_review(review_item, reviewer_username, decision)
        )

        # Add review to item
        review_item.reviews.append(review)

        # Update approval/rejection counts
        if decision == "approve":
            if reviewer.stage == ReviewStage.TECHNICAL:
                review_item.technical_approvals += reviewer.approval_weight
            elif reviewer.stage == ReviewStage.COMPLIANCE:
                review_item.compliance_approvals += reviewer.approval_weight
        elif decision == "reject":
            if reviewer.stage == ReviewStage.TECHNICAL:
                review_item.technical_rejections += reviewer.approval_weight
            elif reviewer.stage == ReviewStage.COMPLIANCE:
                review_item.compliance_rejections += reviewer.approval_weight

        # Update state
        if review_item.state == ReviewState.PENDING_REVIEW:
            review_item.state = ReviewState.UNDER_REVIEW

        print(f"Review Submitted:")
        print(f"  Item ID: {item_id}")
        print(f"  Reviewer: {reviewer_username} ({reviewer.role})")
        print(f"  Decision: {decision.upper()}")
        print(f"  Stage: {reviewer.stage}")
        print()

        # Check quorum
        promotion_triggered = self._check_quorum(review_item)

        # Save review item
        self._save_review_item(review_item)

        # Create result
        result = ReviewFlowResult(
            timestamp=datetime.utcnow().isoformat() + "Z",
            operation="submit_review",
            item_id=item_id,
            state=review_item.state,
            approvals={
                "technical": review_item.technical_approvals,
                "compliance": review_item.compliance_approvals
            },
            rejections={
                "technical": review_item.technical_rejections,
                "compliance": review_item.compliance_rejections
            },
            promotion_triggered=promotion_triggered,
            status="success"
        )

        self._log_review_event("review_submitted", review_item, result)

        print("=" * 60)
        print(f"  Review Flow Status: {result.status.upper()}")
        print("=" * 60)
        print()

        if promotion_triggered:
            print("! PROMOTION TRIGGERED - Quorum reached")
            print()

        return result

    def _check_quorum(self, review_item: ReviewItem) -> bool:
        """Check if quorum is reached and trigger promotion if needed."""
        rules = self.promotion_rules

        # Check technical quorum
        technical_quorum_reached = review_item.technical_approvals >= rules.technical_quorum

        # Check compliance quorum
        compliance_quorum_reached = review_item.compliance_approvals >= rules.compliance_quorum

        # Check if any rejections
        has_rejections = (review_item.technical_rejections > 0 or
                         review_item.compliance_rejections > 0)

        # Determine if promotion should be triggered
        if has_rejections:
            review_item.state = ReviewState.REJECTED
            return False

        if rules.require_both_stages:
            quorum_reached = technical_quorum_reached and compliance_quorum_reached
        else:
            quorum_reached = technical_quorum_reached or compliance_quorum_reached

        if quorum_reached:
            if rules.auto_promote_on_quorum:
                self._trigger_promotion(review_item)
                return True
            else:
                review_item.state = ReviewState.APPROVED
                return False

        return False

    def _trigger_promotion(self, review_item: ReviewItem):
        """Trigger promotion for approved item."""
        print(f"Triggering promotion for: {review_item.item_id}")

        review_item.state = ReviewState.PROMOTED

        # Execute registry event trigger
        try:
            subprocess.run(
                [
                    "bash",
                    "12_tooling/scripts/registry_event_trigger.sh",
                    "--event", "promotion_executed",
                    "--version", "v4.4.0",
                    "--hash", self._get_current_commit_hash()
                ],
                check=True,
                capture_output=True,
                text=True
            )
            print("  OK: Registry event triggered")
        except subprocess.CalledProcessError as e:
            print(f"  ERROR: Failed to trigger registry event - {e}")

        # Create governance review event
        self._create_governance_review_event(review_item)

    def _create_governance_review_event(self, review_item: ReviewItem):
        """Create governance review event with SHA256 signature."""
        self.review_event_file.parent.mkdir(parents=True, exist_ok=True)

        event_data = {
            "event_type": "governance_review_completed",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "item_id": review_item.item_id,
            "item_type": review_item.item_type,
            "title": review_item.title,
            "state": review_item.state.value,
            "approvals": {
                "technical": review_item.technical_approvals,
                "compliance": review_item.compliance_approvals
            },
            "rejections": {
                "technical": review_item.technical_rejections,
                "compliance": review_item.compliance_rejections
            },
            "total_reviews": len(review_item.reviews),
            "signature": review_item.calculate_hash()
        }

        with open(self.review_event_file, 'w') as f:
            json.dump(event_data, f, indent=2)

        print(f"  Governance review event created: {self.review_event_file}")

    def quarterly_check(self) -> Dict:
        """Perform quarterly review status check."""
        print("=" * 60)
        print("  SSID Review Flow - Quarterly Status Check")
        print("=" * 60)
        print()

        # Load all review items
        review_items = self._load_all_review_items()

        # Count by state
        state_counts = {state: 0 for state in ReviewState}
        for item in review_items:
            state_counts[item.state] += 1

        print("Review Item Status:")
        for state, count in state_counts.items():
            print(f"  {state.value}: {count}")
        print()

        # Find items needing attention
        pending = [item for item in review_items if item.state == ReviewState.PENDING_REVIEW]
        under_review = [item for item in review_items if item.state == ReviewState.UNDER_REVIEW]

        if pending:
            print(f"Items Pending Review ({len(pending)}):")
            for item in pending[:5]:  # Show first 5
                print(f"  - {item.item_id}: {item.title}")
            print()

        if under_review:
            print(f"Items Under Review ({len(under_review)}):")
            for item in under_review[:5]:  # Show first 5
                approvals = item.technical_approvals + item.compliance_approvals
                required = self.promotion_rules.technical_quorum + self.promotion_rules.compliance_quorum
                print(f"  - {item.item_id}: {item.title} ({approvals}/{required} approvals)")
            print()

        result = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "total_items": len(review_items),
            "state_counts": {k.value: v for k, v in state_counts.items()},
            "pending_count": len(pending),
            "under_review_count": len(under_review)
        }

        return result

    def finalize_quarter(self) -> Dict:
        """Finalize quarterly governance review cycle."""
        print("=" * 60)
        print("  SSID Review Flow - Finalize Quarter")
        print("=" * 60)
        print()

        # Run quarterly check
        quarterly_status = self.quarterly_check()

        # Archive completed reviews
        review_items = self._load_all_review_items()
        promoted = [item for item in review_items if item.state == ReviewState.PROMOTED]

        print(f"Finalizing {len(promoted)} promoted items...")

        # Create summary
        summary = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "quarter": self._get_current_quarter(),
            "total_reviews": len(review_items),
            "promoted": len(promoted),
            "approved": quarterly_status["state_counts"].get("APPROVED", 0),
            "rejected": quarterly_status["state_counts"].get("REJECTED", 0),
            "pending": quarterly_status["state_counts"].get("PENDING_REVIEW", 0),
            "status": "complete"
        }

        print()
        print("Quarter Finalized:")
        print(f"  Quarter: {summary['quarter']}")
        print(f"  Total Reviews: {summary['total_reviews']}")
        print(f"  Promoted: {summary['promoted']}")
        print(f"  Approved: {summary['approved']}")
        print(f"  Rejected: {summary['rejected']}")
        print()

        return summary

    def _generate_item_id(self, item_type: str, title: str) -> str:
        """Generate unique item ID."""
        timestamp = datetime.utcnow().isoformat()
        combined = f"{item_type}|{title}|{timestamp}"
        hash_digest = hashlib.sha256(combined.encode()).hexdigest()[:12]
        return f"{item_type}_{hash_digest}"

    def _find_reviewer(self, username: str) -> Optional[Reviewer]:
        """Find reviewer by username."""
        for reviewer in self.reviewers:
            if reviewer.username == username:
                return reviewer
        return None

    def _sign_review(self, review_item: ReviewItem, reviewer: str, decision: str) -> str:
        """Create cryptographic signature for review."""
        signature_str = f"{review_item.item_id}|{reviewer}|{decision}|{datetime.utcnow().isoformat()}"
        return hashlib.sha256(signature_str.encode()).hexdigest()

    def _save_review_item(self, review_item: ReviewItem):
        """Save review item to disk."""
        items_dir = Path("24_meta_orchestration/registry/review_items")
        items_dir.mkdir(parents=True, exist_ok=True)

        item_file = items_dir / f"{review_item.item_id}.json"

        with open(item_file, 'w') as f:
            # Convert to dict with proper serialization
            item_dict = asdict(review_item)
            item_dict["state"] = item_dict["state"].value if hasattr(item_dict["state"], "value") else item_dict["state"]

            # Convert ReviewStage enums in reviews
            for review in item_dict.get("reviews", []):
                if "stage" in review and hasattr(review["stage"], "value"):
                    review["stage"] = review["stage"].value

            json.dump(item_dict, f, indent=2)

    def _load_review_item(self, item_id: str) -> Optional[ReviewItem]:
        """Load review item from disk."""
        items_dir = Path("24_meta_orchestration/registry/review_items")
        item_file = items_dir / f"{item_id}.json"

        if not item_file.exists():
            return None

        with open(item_file, 'r') as f:
            item_dict = json.load(f)

        # Convert state string back to enum
        item_dict["state"] = ReviewState(item_dict["state"])

        # Convert reviews
        reviews = []
        for review_dict in item_dict.get("reviews", []):
            review_dict["stage"] = ReviewStage(review_dict["stage"])
            reviews.append(Review(**review_dict))

        item_dict["reviews"] = reviews

        return ReviewItem(**item_dict)

    def _load_all_review_items(self) -> List[ReviewItem]:
        """Load all review items."""
        items_dir = Path("24_meta_orchestration/registry/review_items")

        if not items_dir.exists():
            return []

        items = []
        for item_file in items_dir.glob("*.json"):
            item_id = item_file.stem
            item = self._load_review_item(item_id)
            if item:
                items.append(item)

        return items

    def _log_review_event(self, event_type: str, review_item: ReviewItem, result: Optional[ReviewFlowResult] = None):
        """Log review event to audit trail."""
        self.review_log_file.parent.mkdir(parents=True, exist_ok=True)

        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "event_type": event_type,
            "item_id": review_item.item_id,
            "state": review_item.state.value if hasattr(review_item.state, "value") else review_item.state,
            "result": asdict(result) if result else None
        }

        # Append to log file
        with open(self.review_log_file, 'a') as f:
            f.write(json.dumps(log_entry) + "\n")

    def _get_current_commit_hash(self) -> str:
        """Get current git commit hash."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except:
            return "unknown"

    def _get_current_quarter(self) -> str:
        """Get current quarter string (e.g., "2026-Q1")."""
        now = datetime.utcnow()
        quarter = (now.month - 1) // 3 + 1
        return f"{now.year}-Q{quarter}"


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="SSID Review Flow Manager - Automated governance review pipeline"
    )

    parser.add_argument(
        '--create-item',
        nargs=3,
        metavar=('TYPE', 'TITLE', 'DESCRIPTION'),
        help='Create a new review item'
    )

    parser.add_argument(
        '--submit-review',
        nargs=4,
        metavar=('ITEM_ID', 'REVIEWER', 'DECISION', 'COMMENT'),
        help='Submit a review (decision: approve/reject)'
    )

    parser.add_argument(
        '--quarterly-check',
        action='store_true',
        help='Perform quarterly review status check'
    )

    parser.add_argument(
        '--finalize-quarter',
        action='store_true',
        help='Finalize quarterly governance review cycle'
    )

    args = parser.parse_args()

    manager = ReviewFlowManager()

    if args.create_item:
        item_type, title, description = args.create_item
        manager.create_review_item(item_type, title, description)

    elif args.submit_review:
        item_id, reviewer, decision, comment = args.submit_review
        result = manager.submit_review(item_id, reviewer, decision, comment)
        sys.exit(0 if result.status == "success" else 1)

    elif args.quarterly_check:
        manager.quarterly_check()

    elif args.finalize_quarter:
        manager.finalize_quarter()

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
