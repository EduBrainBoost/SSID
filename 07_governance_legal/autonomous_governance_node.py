#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Layer 10: Autonomous Governance Node - Self-deciding SoT approval"""
import sys, json
from pathlib import Path
from datetime import datetime, timezone
from enum import Enum

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

REPO_ROOT = Path(__file__).resolve().parents[1]
GOVERNANCE_LOG = REPO_ROOT / "07_governance_legal" / "governance_decisions.json"

class Decision(Enum):
    PROMOTE = "promote"
    ROLLBACK = "rollback"
    MANUAL_REVIEW = "manual_review"

class SoTUpdate:
    def __init__(self, version: str, audit_score: float, signatures_valid: bool, merkle_verified: bool):
        self.version = version
        self.audit_score = audit_score
        self.signatures_valid = signatures_valid
        self.merkle_verified = merkle_verified

class AutonomousGovernanceNode:
    """Smart contract-like governance for SoT updates"""

    def evaluate_sot_update(self, update: SoTUpdate) -> Decision:
        """Auto-approves or rejects SoT updates based on criteria"""
        print(f"[Layer 10] Evaluating SoT update {update.version}...")
        print(f"  Audit score: {update.audit_score:.1f}%")
        print(f"  Signatures valid: {update.signatures_valid}")
        print(f"  Merkle verified: {update.merkle_verified}")

        # Decision logic
        if not update.signatures_valid or not update.merkle_verified:
            print(f"  → ROLLBACK: Failed cryptographic checks")
            return Decision.ROLLBACK

        if update.audit_score >= 95.0:
            print(f"  → PROMOTE: Meets all criteria")
            return Decision.PROMOTE

        if update.audit_score >= 80.0:
            print(f"  → MANUAL_REVIEW: Score acceptable but below auto-promote threshold")
            return Decision.MANUAL_REVIEW

        print(f"  → ROLLBACK: Audit score below 80%")
        return Decision.ROLLBACK

    def log_decision(self, update: SoTUpdate, decision: Decision):
        """Log governance decision"""
        GOVERNANCE_LOG.parent.mkdir(parents=True, exist_ok=True)

        decisions = []
        if GOVERNANCE_LOG.exists():
            with open(GOVERNANCE_LOG, 'r', encoding='utf-8') as f:
                decisions = json.load(f).get("decisions", [])

        decisions.append({
            "version": update.version,
            "audit_score": update.audit_score,
            "signatures_valid": update.signatures_valid,
            "merkle_verified": update.merkle_verified,
            "decision": decision.value,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

        decisions = decisions[-100:]  # Keep last 100

        with open(GOVERNANCE_LOG, 'w', encoding='utf-8') as f:
            json.dump({"decisions": decisions}, f, indent=2)

def main():
    node = AutonomousGovernanceNode()

    # Example: evaluate a SoT update
    update = SoTUpdate(
        version="v3.2.1",
        audit_score=100.0,
        signatures_valid=True,
        merkle_verified=True
    )

    decision = node.evaluate_sot_update(update)
    node.log_decision(update, decision)

    if decision == Decision.PROMOTE:
        print(f"\n✅ SoT update {update.version} APPROVED for promotion")
        return 0
    elif decision == Decision.MANUAL_REVIEW:
        print(f"\n⚠️  SoT update {update.version} requires MANUAL REVIEW")
        return 2
    else:
        print(f"\n❌ SoT update {update.version} REJECTED")
        return 1

if __name__ == "__main__":
    sys.exit(main())
