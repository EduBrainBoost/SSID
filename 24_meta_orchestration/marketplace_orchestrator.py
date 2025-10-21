"""
SSID Marketplace Orchestrator v1.0.1
=====================================

Meta-Integration Marketplace Framework under 24_meta_orchestration.
Enforces SoT-alignment, ROOT-24-LOCK, and non-custodial settlement.

Features:
- Reputation-based listing (score >= 50)
- Compliance gates (GDPR/MiCA/DORA/AMLD6)
- Non-custodial attestation-based settlement
- Complete audit trail with SHA-256 hashing
- No PII in motion enforcement

Copyright (c) 2025 SSID Project
"""

from __future__ import annotations
import json, hashlib, time
from typing import Dict, Any, Callable


class MarketplaceOrchestrator:
    """
    Orchestrates marketplace operations with full SoT-Guard enforcement.

    Invariants:
    - No PII in motion (GDPR compliance)
    - Reputation >= 50 for all sellers
    - All events hashed with SHA-256
    - Audit trail for all operations
    - Non-custodial settlement only
    """

    VERSION = "1.0.1"

    # SoT-Guard: Minimum reputation score
    MIN_REPUTATION_SCORE = 50

    def __init__(
        self,
        audit_sink: Callable[[Dict[str, Any]], None],
        compliance_checker: Callable[[str, Dict[str, Any]], None],
        reputation_resolver: Callable[[str], Dict[str, Any]],
        interop_bridge: Callable[[str, Dict[str, Any]], Dict[str, Any]]
    ):
        """
        Initialize orchestrator with required dependencies.

        Args:
            audit_sink: Function to write audit events
            compliance_checker: Function to verify compliance rules
            reputation_resolver: Function to resolve seller reputation
            interop_bridge: Function for interop attestations
        """
        self.audit_sink = audit_sink
        self.compliance_checker = compliance_checker
        self.reputation_resolver = reputation_resolver
        self.interop_bridge = interop_bridge

    @staticmethod
    def _hash(obj: Any) -> str:
        """
        Compute SHA-256 hash of JSON-serializable object.

        SoT-Guard: Ensures deterministic hashing for audit trail.
        """
        b = json.dumps(obj, sort_keys=True, separators=(',', ':')).encode('utf-8')
        return hashlib.sha256(b).hexdigest()

    @staticmethod
    def _sot_guard_no_pii(data: Dict[str, Any]) -> None:
        """
        SoT-Guard: Verify no PII in motion (GDPR compliance).

        Raises:
            AssertionError: If 'pii' keyword detected in data
        """
        dump = json.dumps(data).lower()
        assert 'pii' not in dump, 'SoT-Guard violation: no_pii_in_motion'

    @staticmethod
    def _sot_guard_valid_offer(offer: Dict[str, Any]) -> None:
        """
        SoT-Guard: Verify offer structure is valid.

        Raises:
            AssertionError: If required fields missing
        """
        required = {'asset_id', 'seller_did', 'price'}
        assert required <= set(offer.keys()), f'SoT-Guard violation: invalid_offer (missing {required - set(offer.keys())})'
        assert isinstance(offer['price'], int) and offer['price'] > 0, 'SoT-Guard violation: price must be positive integer'

    def _sot_guard_reputation(self, did: str) -> Dict[str, Any]:
        """
        SoT-Guard: Verify seller reputation meets minimum threshold.

        Returns:
            Reputation data with score

        Raises:
            AssertionError: If reputation < MIN_REPUTATION_SCORE
        """
        rep = self.reputation_resolver(did)
        score = rep.get('score', 0)
        assert score >= self.MIN_REPUTATION_SCORE, \
            f'SoT-Guard violation: reputation_insufficient (score={score}, required>={self.MIN_REPUTATION_SCORE})'
        return rep

    def list_offer(self, offer: Dict[str, Any]) -> Dict[str, Any]:
        """
        List an offer on the marketplace.

        SoT-Guards:
        - Valid offer structure
        - No PII in motion
        - Seller reputation >= 50
        - Compliance rules passed

        Args:
            offer: Offer data with asset_id, seller_did, price

        Returns:
            Event dict with event_hash

        Raises:
            AssertionError: If any SoT-Guard fails
        """
        # SoT-Guard 1: Valid offer
        self._sot_guard_valid_offer(offer)

        # SoT-Guard 2: No PII
        self._sot_guard_no_pii(offer)

        # SoT-Guard 3: Reputation check
        rep = self._sot_guard_reputation(offer['seller_did'])

        # SoT-Guard 4: Compliance check
        self.compliance_checker('list', offer)

        # Create auditable event
        event = {
            'type': 'offer_listed',
            'ts': int(time.time()),
            'offer': offer,
            'reputation': rep,
            'version': self.VERSION
        }
        event['event_hash'] = self._hash(event)

        # Write to audit trail
        self.audit_sink(event)

        return event

    def trade(self, offer: Dict[str, Any], buyer_did: str) -> Dict[str, Any]:
        """
        Settle a trade (non-custodial).

        SoT-Guards:
        - Compliance rules passed
        - Interop attestation successful
        - No PII in motion

        Args:
            offer: Original offer data
            buyer_did: Buyer's DID

        Returns:
            Trade event dict with event_hash

        Raises:
            AssertionError: If any SoT-Guard fails
        """
        trade_data = {'offer': offer, 'buyer_did': buyer_did}

        # SoT-Guard 1: No PII
        self._sot_guard_no_pii(trade_data)

        # SoT-Guard 2: Compliance check
        self.compliance_checker('trade', trade_data)

        # SoT-Guard 3: Interop attestation (non-custodial proof)
        attest = self.interop_bridge('attest_performance', trade_data)
        assert attest.get('status') == 'ok', \
            f'SoT-Guard violation: attestation_failed (status={attest.get("status")})'

        # Create auditable event
        trade_evt = {
            'type': 'trade_settled',
            'ts': int(time.time()),
            'offer': offer,
            'buyer_did': buyer_did,
            'attestation': attest,
            'version': self.VERSION
        }
        trade_evt['event_hash'] = self._hash(trade_evt)

        # Write to audit trail
        self.audit_sink(trade_evt)

        return trade_evt


# SoT-Guard: Module-level invariant documentation
__sot_invariants__ = {
    "no_pii_in_motion": True,
    "non_custodial_only": True,
    "audit_trail_required": True,
    "reputation_gate": True,
    "compliance_gate": True,
    "deterministic_hashing": True
}
