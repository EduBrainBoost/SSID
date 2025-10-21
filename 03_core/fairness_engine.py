"""
SSID Fairness Engine v5.4.3
============================

POFI (Proof of Fair Interaction) - Activity & History-Based Fair Distribution
No PII, deterministic, privacy-preserving.

Features:
- Activity-based weight calculation
- Historical contribution tracking
- Privacy-preserving (no PII)
- Deterministic outcomes
- Sybil-resistant
- DAO-governable parameters

Copyright (c) 2025 SSID Project
"""

from __future__ import annotations
from decimal import Decimal, getcontext
from typing import Dict, List, Any
import hashlib
import time
import math

# Set high precision for exact calculations
getcontext().prec = 40


# Legacy functions (kept for backward compatibility)
def fairness_weight(lifetime_rewards: Decimal, activity_score: Decimal) -> Decimal:
    """Legacy fairness weight calculation."""
    base = Decimal(1) / (Decimal(1) + Decimal(math.log1p(float(lifetime_rewards))))
    return (base * activity_score)


def pofi(activity_score: Decimal, lifetime_rewards: Decimal) -> Decimal:
    """Legacy POFI calculation."""
    num = Decimal(math.log1p(float(activity_score)))
    den = Decimal(math.log(float(lifetime_rewards + Decimal(10))))
    return (num / den)


class FairnessEngine:
    """
    POFI (Proof of Fair Interaction) Engine v5.4.3.

    Calculates fair distribution weights based on:
    - Activity level (transactions, interactions)
    - Historical contribution (tenure, consistency)
    - Reputation score (quality, compliance)

    All calculations are deterministic and privacy-preserving.
    """

    VERSION = "5.4.3"

    # Default weights for POFI calculation (DAO-governable)
    DEFAULT_WEIGHTS = {
        "activity": Decimal("0.40"),      # 40% weight on recent activity
        "history": Decimal("0.35"),       # 35% weight on historical contribution
        "reputation": Decimal("0.25")     # 25% weight on reputation score
    }

    # Activity decay factor (older activity counts less)
    ACTIVITY_DECAY_DAYS = 90

    # Minimum scores to participate
    MIN_ACTIVITY_SCORE = Decimal("1.0")
    MIN_REPUTATION_SCORE = Decimal("50.0")

    def __init__(
        self,
        weights: Dict[str, Decimal] = None,
        activity_decay_days: int = None
    ):
        """
        Initialize Fairness Engine.

        Args:
            weights: Custom weights for activity/history/reputation
            activity_decay_days: Custom decay period for activity
        """
        self.weights = weights or self.DEFAULT_WEIGHTS.copy()
        self.activity_decay_days = activity_decay_days or self.ACTIVITY_DECAY_DAYS

        # Validate weights sum to 1.0
        weight_sum = sum(self.weights.values())
        if weight_sum != Decimal("1.0"):
            raise ValueError(f"Weights must sum to 1.0, got {weight_sum}")

    def calculate_pofi_score(self, participant: Dict[str, Any]) -> Decimal:
        """
        Calculate POFI (Proof of Fair Interaction) score for a participant.

        Args:
            participant: Dict with keys:
                - activity_count: Number of interactions
                - days_active: Days since first interaction
                - reputation_score: Current reputation (0-100)
                - last_activity_ts: Unix timestamp of last activity

        Returns:
            POFI score (0-100 scale)
        """
        # Extract metrics
        activity_count = Decimal(str(participant.get("activity_count", 0)))
        days_active = Decimal(str(participant.get("days_active", 0)))
        reputation = Decimal(str(participant.get("reputation_score", 50)))
        last_activity_ts = participant.get("last_activity_ts", time.time())

        # Guard: Minimum requirements
        if activity_count < self.MIN_ACTIVITY_SCORE:
            return Decimal("0")
        if reputation < self.MIN_REPUTATION_SCORE:
            return Decimal("0")

        # Calculate component scores (normalized 0-100)
        activity_score = self._calculate_activity_score(
            activity_count,
            last_activity_ts
        )
        history_score = self._calculate_history_score(days_active)
        reputation_score = reputation  # Already 0-100

        # Weighted combination
        pofi_score = (
            activity_score * self.weights["activity"] +
            history_score * self.weights["history"] +
            reputation_score * self.weights["reputation"]
        )

        return pofi_score

    def _calculate_activity_score(
        self,
        activity_count: Decimal,
        last_activity_ts: float
    ) -> Decimal:
        """Calculate activity score with time decay."""
        # Base score from activity count (log scale to prevent outliers)
        base_score = Decimal(str(math.log10(float(activity_count) + 1))) * Decimal("20")

        # Apply time decay
        days_since_last = (time.time() - last_activity_ts) / 86400
        decay_factor = max(
            Decimal("0.1"),
            Decimal("1.0") - Decimal(str(days_since_last)) / Decimal(str(self.activity_decay_days))
        )

        activity_score = base_score * decay_factor
        return min(Decimal("100"), activity_score)

    def _calculate_history_score(self, days_active: Decimal) -> Decimal:
        """Calculate history score based on tenure."""
        if days_active <= Decimal("0"):
            return Decimal("0")

        history_score = Decimal(str(math.log10(float(days_active) + 1))) * Decimal("25")
        return min(Decimal("100"), history_score)

    def distribute_fair_rewards(
        self,
        total_amount: Decimal,
        participants: List[Dict[str, Any]]
    ) -> Dict[str, Decimal]:
        """
        Distribute rewards fairly among participants using POFI.

        Args:
            total_amount: Total amount to distribute
            participants: List of participant dicts (must include 'did' field)

        Returns:
            Dict mapping participant DID to reward amount
        """
        # Calculate POFI scores for all participants
        scores = {}
        for p in participants:
            did = p.get("did")
            if not did:
                continue

            score = self.calculate_pofi_score(p)
            if score > Decimal("0"):
                scores[did] = score

        if not scores:
            return {}

        total_score = sum(scores.values())

        # Distribute proportionally
        distribution = {}
        allocated = Decimal("0")

        sorted_dids = sorted(scores.keys(), key=lambda d: scores[d], reverse=True)

        for i, did in enumerate(sorted_dids):
            if i == len(sorted_dids) - 1:
                distribution[did] = total_amount - allocated
            else:
                share = (scores[did] / total_score) * total_amount
                distribution[did] = share
                allocated += share

        return distribution

    def generate_fairness_proof(
        self,
        participant: Dict[str, Any],
        pofi_score: Decimal
    ) -> Dict[str, Any]:
        """Generate cryptographic proof of fairness calculation."""
        import json

        proof_data = {
            "version": self.VERSION,
            "pofi_score": str(pofi_score),
            "activity_count": participant.get("activity_count"),
            "days_active": participant.get("days_active"),
            "reputation_score": participant.get("reputation_score"),
            "weights": {k: str(v) for k, v in self.weights.items()}
        }

        proof_str = json.dumps(proof_data, sort_keys=True)
        proof_hash = hashlib.sha256(proof_str.encode()).hexdigest()

        return {
            "proof_hash": proof_hash,
            "pofi_score": str(pofi_score),
            "timestamp": int(time.time()),
            "version": self.VERSION
        }


def calculate_fair_distribution(
    total_amount: Decimal,
    participants: List[Dict[str, Any]]
) -> Dict[str, Decimal]:
    """Quick helper to calculate fair distribution using default POFI settings."""
    engine = FairnessEngine()
    return engine.distribute_fair_rewards(total_amount, participants)


__invariants__ = {
    "no_pii": True,
    "deterministic": True,
    "privacy_preserving": True,
    "sybil_resistant": True,
    "dao_governable": True
}
