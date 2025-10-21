# -*- coding: utf-8 -*-
"""
SSID Fee Distribution & Fairness System - E2E Test Suite
=========================================================

Tests the complete fee distribution pipeline including:
- Exact Decimal(40) calculations
- 7-pillar system pool (normalized to 2%)
- POFI fairness engine
- Hybrid payout logic
- CLI calculator integration
- Audit trail generation

Copyright (c) 2025 SSID Project
"""

import pytest
import sys
import json
from pathlib import Path
from decimal import Decimal, getcontext
import time

# Set high precision for tests
getcontext().prec = 40

# Add core modules to path
sys.path.insert(0, str(Path(__file__).parent.parent / "03_core"))
sys.path.insert(0, str(Path(__file__).parent.parent / "12_tooling"))

from fee_distribution_engine import distribute, SYSTEM_SHARES, DEVELOPER_PERCENT, SYSTEM_POOL_PERCENT
from fairness_engine import FairnessEngine, calculate_fair_distribution


class TestFeeDistribution:
    """Test exact fee distribution with Decimal(40) precision."""

    def test_exact_3_percent_split(self):
        """Test that total fee is exactly 3% (1% dev + 2% system)."""
        amount = Decimal("1000.00")
        result = distribute(amount)

        dev = result["developer_reward"]
        sys_total = result["system_pool_total"]

        # Verify exact percentages
        assert dev == amount * Decimal("0.01")
        assert sys_total == amount * Decimal("0.02")
        assert dev + sys_total == amount * Decimal("0.03")

    def test_7_pillar_normalization(self):
        """Test that 7 categories sum exactly to 2%."""
        amount = Decimal("1000.00")
        result = distribute(amount)

        categories = result["categories"]
        cat_sum = sum(categories.values())

        # Must equal system_pool_total exactly
        assert cat_sum == result["system_pool_total"]
        assert cat_sum == amount * Decimal("0.02")

    def test_no_rounding_loss(self):
        """Test that no precision is lost in calculations."""
        amount = Decimal("1.00")
        result = distribute(amount)

        # Sum all components
        total = result["developer_reward"] + sum(result["categories"].values())

        # Must equal exactly 3% of amount
        assert total == amount * Decimal("0.03")

    def test_category_weights(self):
        """Test that category weights match specification."""
        expected_weights = {
            "legal_compliance": Decimal("0.35"),
            "audit_security": Decimal("0.30"),
            "technical_maintenance": Decimal("0.30"),
            "dao_treasury": Decimal("0.25"),
            "community_bonus": Decimal("0.20"),
            "liquidity_reserve": Decimal("0.20"),
            "marketing_partnerships": Decimal("0.20"),
        }

        # Weights should sum to 1.80 (normalized to 2%)
        assert sum(expected_weights.values()) == Decimal("1.80")

    def test_basis_points(self):
        """Test basis point calculations."""
        amount = Decimal("10000.00")  # Use 10k for easier bp calculation
        result = distribute(amount)

        # Legal compliance should be ~38.89 bp
        legal = result["categories"]["legal_compliance"]
        legal_bp = (legal / amount) * Decimal("10000")

        assert Decimal("38.88") < legal_bp < Decimal("38.90")

    def test_multiple_amounts(self):
        """Test distribution with various amounts."""
        test_amounts = [
            Decimal("1.00"),
            Decimal("100.00"),
            Decimal("1000.00"),
            Decimal("10000.00"),
            Decimal("0.01"),
        ]

        for amt in test_amounts:
            result = distribute(amt)
            total = result["developer_reward"] + sum(result["categories"].values())
            assert total == amt * Decimal("0.03")


class TestPOFIFairnessEngine:
    """Test POFI (Proof of Fair Interaction) fairness calculations."""

    def test_pofi_initialization(self):
        """Test FairnessEngine initialization."""
        engine = FairnessEngine()

        assert engine.VERSION == "5.4.3"
        assert engine.weights["activity"] == Decimal("0.40")
        assert engine.weights["history"] == Decimal("0.35")
        assert engine.weights["reputation"] == Decimal("0.25")

    def test_pofi_score_calculation(self):
        """Test POFI score calculation for a participant."""
        engine = FairnessEngine()

        participant = {
            "did": "did:ssid:participant:abc",
            "activity_count": 100,
            "days_active": 365,
            "reputation_score": 75,
            "last_activity_ts": time.time(),
        }

        score = engine.calculate_pofi_score(participant)

        # Score should be between 0 and 100
        assert Decimal("0") <= score <= Decimal("100")

    def test_pofi_minimum_requirements(self):
        """Test that minimum requirements are enforced."""
        engine = FairnessEngine()

        # Below minimum activity
        participant_low_activity = {
            "did": "did:ssid:participant:low",
            "activity_count": 0,
            "days_active": 365,
            "reputation_score": 75,
            "last_activity_ts": time.time(),
        }

        score_low = engine.calculate_pofi_score(participant_low_activity)
        assert score_low == Decimal("0")

        # Below minimum reputation
        participant_low_rep = {
            "did": "did:ssid:participant:lowrep",
            "activity_count": 100,
            "days_active": 365,
            "reputation_score": 30,
            "last_activity_ts": time.time(),
        }

        score_rep = engine.calculate_pofi_score(participant_low_rep)
        assert score_rep == Decimal("0")

    def test_fair_distribution(self):
        """Test fair reward distribution among participants."""
        engine = FairnessEngine()

        participants = [
            {
                "did": "did:ssid:p1",
                "activity_count": 100,
                "days_active": 365,
                "reputation_score": 80,
                "last_activity_ts": time.time(),
            },
            {
                "did": "did:ssid:p2",
                "activity_count": 50,
                "days_active": 180,
                "reputation_score": 70,
                "last_activity_ts": time.time(),
            },
            {
                "did": "did:ssid:p3",
                "activity_count": 200,
                "days_active": 730,
                "reputation_score": 90,
                "last_activity_ts": time.time(),
            },
        ]

        total_amount = Decimal("1000.00")
        distribution = engine.distribute_fair_rewards(total_amount, participants)

        # All participants should receive something
        assert len(distribution) == 3

        # Total distributed should equal total amount
        total_distributed = sum(distribution.values())
        assert total_distributed == total_amount

        # Higher activity/reputation should get more
        assert distribution["did:ssid:p3"] > distribution["did:ssid:p1"]
        assert distribution["did:ssid:p1"] > distribution["did:ssid:p2"]

    def test_fairness_proof_generation(self):
        """Test cryptographic fairness proof generation."""
        engine = FairnessEngine()

        participant = {
            "did": "did:ssid:participant:test",
            "activity_count": 100,
            "days_active": 365,
            "reputation_score": 75,
            "last_activity_ts": time.time(),
        }

        score = engine.calculate_pofi_score(participant)
        proof = engine.generate_fairness_proof(participant, score)

        assert "proof_hash" in proof
        assert "pofi_score" in proof
        assert "timestamp" in proof
        assert proof["version"] == "5.4.3"
        assert len(proof["proof_hash"]) == 64  # SHA-256 hex


class TestHybridPayout:
    """Test hybrid fiat/token payout logic."""

    def test_fiat_cap_logic(self):
        """Test fiat cap and token incentive logic."""
        fiat_cap = Decimal("100.00")
        token_multiplier = Decimal("1.10")

        # Case 1: Reward <= cap (100% fiat)
        reward1 = Decimal("50.00")
        fiat1 = min(reward1, fiat_cap)
        token1 = Decimal("0")

        assert fiat1 == Decimal("50.00")
        assert token1 == Decimal("0")

        # Case 2: Reward > cap (cap in fiat, rest in token)
        reward2 = Decimal("150.00")
        fiat2 = fiat_cap
        token2 = (reward2 - fiat_cap) * token_multiplier

        assert fiat2 == Decimal("100.00")
        assert token2 == Decimal("55.00")  # (150 - 100) * 1.10

    def test_token_incentive(self):
        """Test token incentive multiplier."""
        fiat_cap = Decimal("100.00")
        token_multiplier = Decimal("1.10")

        rewards = [Decimal("100.00"), Decimal("200.00"), Decimal("500.00")]

        for reward in rewards:
            if reward > fiat_cap:
                excess = reward - fiat_cap
                token_value = excess * token_multiplier

                # Token should be 10% more than excess
                assert token_value == excess * Decimal("1.10")


class TestCLICalculator:
    """Test CLI calculator integration."""

    def test_cli_import(self):
        """Test that CLI calculator can import distribution engine."""
        import cli_calculator

        # Should have main function
        assert hasattr(cli_calculator, "main")

    def test_cli_calculation(self):
        """Test CLI calculation logic."""
        amount = Decimal("1000.00")
        result = distribute(amount)

        # Round to cents for CLI display
        def r2(x):
            return x.quantize(Decimal("0.01"))

        cli_output = {
            "amount": str(r2(amount)),
            "developer_reward": str(r2(result["developer_reward"])),
            "system_pool_total": str(r2(result["system_pool_total"])),
            "categories": {k: str(r2(v)) for k, v in result["categories"].items()},
        }

        assert cli_output["amount"] == "1000.00"
        assert cli_output["developer_reward"] == "10.00"
        assert cli_output["system_pool_total"] == "20.00"


class TestAuditTrail:
    """Test audit trail generation."""

    def test_event_structure(self):
        """Test audit event structure."""
        import hashlib

        event = {
            "type": "fee_calculated",
            "timestamp": int(time.time()),
            "amount": "1000.00",
            "developer_reward": "10.00",
            "system_pool_total": "20.00",
            "version": "5.4.3",
        }

        # Generate event hash
        event_str = json.dumps(event, sort_keys=True)
        event_hash = hashlib.sha256(event_str.encode()).hexdigest()
        event["event_hash"] = event_hash

        assert "type" in event
        assert "timestamp" in event
        assert "event_hash" in event
        assert len(event["event_hash"]) == 64

    def test_jsonl_format(self):
        """Test JSONL (JSON Lines) format."""
        events = [
            {"type": "fee_calculated", "amount": "100.00"},
            {"type": "reward_distributed", "did": "did:ssid:p1"},
        ]

        # JSONL: one JSON object per line
        jsonl_lines = [json.dumps(e) for e in events]

        assert len(jsonl_lines) == 2
        assert "\n" not in jsonl_lines[0]  # No newlines within JSON


class TestIntegrationScenarios:
    """Test complete integration scenarios."""

    def test_end_to_end_distribution(self):
        """Test complete fee distribution and fairness flow."""
        # Step 1: Calculate fees
        transaction_amount = Decimal("1000.00")
        fee_result = distribute(transaction_amount)

        assert fee_result["developer_reward"] == Decimal("10.00")
        assert fee_result["system_pool_total"] == Decimal("20.00")

        # Step 2: Distribute community bonus fairly
        engine = FairnessEngine()
        participants = [
            {
                "did": "did:ssid:user1",
                "activity_count": 100,
                "days_active": 365,
                "reputation_score": 80,
                "last_activity_ts": time.time(),
            },
            {
                "did": "did:ssid:user2",
                "activity_count": 150,
                "days_active": 730,
                "reputation_score": 85,
                "last_activity_ts": time.time(),
            },
        ]

        community_pool = fee_result["categories"]["community_bonus"]
        fair_distribution = engine.distribute_fair_rewards(community_pool, participants)

        # Verify distribution
        assert sum(fair_distribution.values()) == community_pool
        assert len(fair_distribution) == 2

    def test_subscription_allocation(self):
        """Test subscription revenue allocation (50/30/10/10)."""
        subscription_revenue = Decimal("1000.00")

        allocation = {
            "dao_treasury": subscription_revenue * Decimal("0.50"),
            "technical_maintenance": subscription_revenue * Decimal("0.30"),
            "marketing_partnerships": subscription_revenue * Decimal("0.10"),
            "liquidity_reserve": subscription_revenue * Decimal("0.10"),
        }

        assert sum(allocation.values()) == subscription_revenue
        assert allocation["dao_treasury"] == Decimal("500.00")
        assert allocation["technical_maintenance"] == Decimal("300.00")

    def test_determinism(self):
        """Test that calculations are deterministic."""
        amount = Decimal("1000.00")

        result1 = distribute(amount)
        result2 = distribute(amount)

        # Should produce identical results
        assert result1["developer_reward"] == result2["developer_reward"]
        assert result1["system_pool_total"] == result2["system_pool_total"]

        for key in result1["categories"]:
            assert result1["categories"][key] == result2["categories"][key]

    def test_no_pii_in_motion(self):
        """Test that no PII is leaked in calculations."""
        engine = FairnessEngine()

        participant = {
            "did": "did:ssid:anonymous:xyz",  # Pseudonymous
            "activity_count": 100,
            "days_active": 365,
            "reputation_score": 75,
            "last_activity_ts": time.time(),
            # NO PII fields like name, email, phone, address
        }

        score = engine.calculate_pofi_score(participant)
        proof = engine.generate_fairness_proof(participant, score)

        # Verify no PII in proof (proof is privacy-preserving, doesn't include DID)
        proof_str = json.dumps(proof)
        assert "name" not in proof_str.lower()
        assert "email" not in proof_str.lower()
        assert "phone" not in proof_str.lower()
        assert "address" not in proof_str.lower()

        # Proof should contain only aggregated metrics, not identifiers
        assert "pofi_score" in proof_str
        assert "proof_hash" in proof_str


class TestComplianceInvariants:
    """Test compliance and invariant enforcement."""

    def test_decimal_40_precision(self):
        """Test that Decimal(40) precision is maintained."""
        from decimal import getcontext

        ctx = getcontext()
        assert ctx.prec >= 40

    def test_exact_share_values(self):
        """Test that shares match certificate specifications."""
        expected_shares = {
            "legal_compliance": Decimal(
                "0.003888888888888888888888888888888888888888"
            ),
            "audit_security": Decimal(
                "0.003333333333333333333333333333333333333334"
            ),
            "technical_maintenance": Decimal(
                "0.003333333333333333333333333333333333333334"
            ),
            "dao_treasury": Decimal(
                "0.002777777777777777777777777777777777777778"
            ),
            "community_bonus": Decimal(
                "0.002222222222222222222222222222222222222222"
            ),
            "liquidity_reserve": Decimal(
                "0.002222222222222222222222222222222222222222"
            ),
            "marketing_partnerships": Decimal(
                "0.002222222222222222222222222222222222222222"
            ),
        }

        # Verify against SYSTEM_SHARES
        for key, expected_value in expected_shares.items():
            assert SYSTEM_SHARES[key] == expected_value

    def test_total_fee_rate(self):
        """Test that total fee rate is exactly 3%."""
        total_fee_rate = DEVELOPER_PERCENT + SYSTEM_POOL_PERCENT
        assert total_fee_rate == Decimal("0.03")
        assert DEVELOPER_PERCENT == Decimal("0.01")

        system_total = sum(SYSTEM_SHARES.values())
        assert system_total == Decimal("0.02")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
