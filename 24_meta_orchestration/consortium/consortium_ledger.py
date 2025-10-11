#!/usr/bin/env python3
"""
SSID Consortium Ledger
Distributed Audit Network Implementation

Connects federated evidence nodes into a consortium where organizations
cross-sign each other's compliance anchors, creating a decentralized
audit network without central authority.
"""

import json
import hashlib
import hmac
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import secrets


class ValidationResult(Enum):
    """Anchor validation results"""
    PASS = "PASS"
    FAIL = "FAIL"
    CONDITIONAL = "CONDITIONAL"


class MemberTier(Enum):
    """Consortium membership tiers"""
    FOUNDING = "founding_member"
    FULL = "full_member"
    ASSOCIATE = "associate_member"
    OBSERVER = "observer"


@dataclass
class ConsortiumMember:
    """Consortium member organization"""
    member_id: str
    organization_name: str
    public_key: str
    tier: MemberTier
    joined_date: datetime
    reputation_score: float = 1.0
    voting_weight: int = 1
    cross_signing_quota: int = 20
    total_validations: int = 0
    accurate_validations: int = 0
    last_active: datetime = field(default_factory=datetime.now)


@dataclass
class CrossSignature:
    """Cross-signature from validator organization"""
    validator_id: str
    anchor_hash: str
    validation_result: ValidationResult
    validation_timestamp: datetime
    validation_evidence: str
    signature: str
    reputation_at_signing: float


@dataclass
class ConsortiumAnchor:
    """Anchor in consortium ledger"""
    anchor_id: str
    submitter_id: str
    submission_timestamp: datetime
    compliance_data_cid: str  # IPFS CID
    evidence_merkle_root: str
    compliance_summary: Dict
    submitter_signature: str
    cross_signatures: List[CrossSignature] = field(default_factory=list)
    consensus_achieved: bool = False
    consensus_timestamp: Optional[datetime] = None
    ledger_sequence: Optional[int] = None


@dataclass
class LedgerBlock:
    """Block in consortium ledger"""
    sequence_number: int
    timestamp: datetime
    previous_hash: str
    anchor_batch: List[ConsortiumAnchor]
    consortium_hash: str
    merkle_root: str
    block_signatures: List[Dict[str, str]] = field(default_factory=list)


class ConsortiumLedger:
    """
    Distributed Consortium Ledger Implementation

    Manages multi-organization compliance validation with:
    - Distributed consensus
    - Cross-signing protocols
    - Reputation tracking
    - Immutable audit trail
    """

    def __init__(
        self,
        member_id: str,
        private_key: str,
        public_key: str,
        data_dir: Path = Path("./consortium_data")
    ):
        self.member_id = member_id
        self.private_key = private_key
        self.public_key = public_key
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Consortium state
        self.members: Dict[str, ConsortiumMember] = {}
        self.pending_anchors: Dict[str, ConsortiumAnchor] = {}
        self.ledger_chain: List[LedgerBlock] = []

        # Consensus parameters
        self.min_signatures_required = 5
        self.min_weighted_votes = 10
        self.max_fail_percentage = 10
        self.consensus_timeout = timedelta(hours=48)

        # Reputation parameters
        self.accurate_validation_reward = 0.02
        self.inaccurate_validation_penalty = 0.05
        self.reputation_decay_halflife = timedelta(days=90)

        # Initialize genesis block
        if not self.ledger_chain:
            self._create_genesis_block()

        # Load member registry
        self._load_member_registry()

    def register_member(
        self,
        organization_name: str,
        public_key: str,
        tier: MemberTier
    ) -> ConsortiumMember:
        """
        Register new consortium member

        Requires governance approval in production
        """
        member_id = hashlib.sha256(public_key.encode()).hexdigest()[:16]

        tier_config = {
            MemberTier.FOUNDING: (3, 100),
            MemberTier.FULL: (2, 50),
            MemberTier.ASSOCIATE: (1, 20),
            MemberTier.OBSERVER: (0, 0)
        }

        voting_weight, quota = tier_config[tier]

        member = ConsortiumMember(
            member_id=member_id,
            organization_name=organization_name,
            public_key=public_key,
            tier=tier,
            joined_date=datetime.now(),
            reputation_score=1.0,
            voting_weight=voting_weight,
            cross_signing_quota=quota
        )

        self.members[member_id] = member
        self._save_member_registry()

        print(f"[Consortium] Registered member: {organization_name} (Tier: {tier.value})")
        return member

    def submit_anchor(self, anchor: ConsortiumAnchor) -> bool:
        """
        Submit compliance anchor to consortium

        Anchor will be distributed to validators for cross-signing
        """
        # Verify submitter is member
        if anchor.submitter_id not in self.members:
            print(f"[Consortium] Submitter {anchor.submitter_id} not a member")
            return False

        # Verify signature
        if not self._verify_anchor_signature(anchor):
            print(f"[Consortium] Invalid anchor signature")
            return False

        # Add to pending pool
        self.pending_anchors[anchor.anchor_id] = anchor

        print(f"[Consortium] Anchor {anchor.anchor_id[:16]}... submitted by {self.members[anchor.submitter_id].organization_name}")

        # Broadcast to validators
        validators = self._select_validators(anchor.submitter_id)
        print(f"[Consortium] Broadcasting to {len(validators)} validators")

        # In production, send HTTP requests to validator endpoints
        # For now, simulate distribution
        return True

    def validate_anchor(
        self,
        anchor_id: str,
        validation_result: ValidationResult,
        validation_evidence: str
    ) -> Optional[CrossSignature]:
        """
        Validate anchor and generate cross-signature

        Called by validator organizations
        """
        if anchor_id not in self.pending_anchors:
            print(f"[Consortium] Anchor {anchor_id[:16]}... not found")
            raise NotImplementedError("TODO: Implement this function")

        anchor = self.pending_anchors[anchor_id]

        # Check if already validated by this member
        if any(sig.validator_id == self.member_id for sig in anchor.cross_signatures):
            print(f"[Consortium] Already validated this anchor")
            raise NotImplementedError("TODO: Implement this function")

        # Perform validation checks (simplified)
        if not self._perform_validation_checks(anchor):
            validation_result = ValidationResult.FAIL

        # Get current reputation
        current_member = self.members[self.member_id]

        # Create cross-signature
        cross_sig = CrossSignature(
            validator_id=self.member_id,
            anchor_hash=anchor.anchor_id,
            validation_result=validation_result,
            validation_timestamp=datetime.now(),
            validation_evidence=validation_evidence,
            signature=self._sign_data(f"{anchor.anchor_id}:{validation_result.value}"),
            reputation_at_signing=current_member.reputation_score
        )

        # Add to anchor
        anchor.cross_signatures.append(cross_sig)

        # Update validator stats
        current_member.total_validations += 1
        current_member.last_active = datetime.now()

        print(f"[Consortium] Validated anchor {anchor_id[:16]}... with result: {validation_result.value}")

        # Check consensus
        self._check_consensus(anchor_id)

        return cross_sig

    def _check_consensus(self, anchor_id: str) -> bool:
        """
        Check if anchor has achieved consortium consensus

        Requires minimum signatures and weighted votes
        """
        if anchor_id not in self.pending_anchors:
            return False

        anchor = self.pending_anchors[anchor_id]

        # Count signatures and weighted votes
        pass_signatures = [
            sig for sig in anchor.cross_signatures
            if sig.validation_result == ValidationResult.PASS
        ]

        fail_signatures = [
            sig for sig in anchor.cross_signatures
            if sig.validation_result == ValidationResult.FAIL
        ]

        # Calculate weighted votes
        weighted_pass = sum(
            self.members[sig.validator_id].voting_weight * sig.reputation_at_signing
            for sig in pass_signatures
            if sig.validator_id in self.members
        )

        total_signatures = len(anchor.cross_signatures)
        fail_percentage = (len(fail_signatures) / total_signatures * 100) if total_signatures > 0 else 0

        # Check consensus criteria
        consensus = (
            len(pass_signatures) >= self.min_signatures_required and
            weighted_pass >= self.min_weighted_votes and
            fail_percentage <= self.max_fail_percentage
        )

        if consensus:
            anchor.consensus_achieved = True
            anchor.consensus_timestamp = datetime.now()

            print(f"[Consortium] OK CONSENSUS ACHIEVED for anchor {anchor_id[:16]}...")
            print(f"  - Pass signatures: {len(pass_signatures)}")
            print(f"  - Weighted votes: {weighted_pass:.1f}")
            print(f"  - Fail percentage: {fail_percentage:.1f}%")

            # Commit to ledger
            self._commit_to_ledger(anchor)

            # Remove from pending
            del self.pending_anchors[anchor_id]

            # Update reputations
            self._update_validator_reputations(anchor)

            return True

        return False

    def _commit_to_ledger(self, anchor: ConsortiumAnchor):
        """
        Commit validated anchor to consortium ledger

        Creates new block with anchor and cross-signatures
        """
        # Assign sequence number
        anchor.ledger_sequence = len(self.ledger_chain)

        # Create new block
        previous_hash = self.ledger_chain[-1].consortium_hash if self.ledger_chain else "0" * 64

        block = LedgerBlock(
            sequence_number=len(self.ledger_chain),
            timestamp=datetime.now(),
            previous_hash=previous_hash,
            anchor_batch=[anchor],
            consortium_hash="",  # Calculated below
            merkle_root=self._calculate_merkle_root([anchor])
        )

        # Calculate consortium hash
        block_data = f"{block.previous_hash}:{block.merkle_root}:{block.timestamp.isoformat()}"
        block.consortium_hash = hashlib.sha256(block_data.encode()).hexdigest()

        # Add to chain
        self.ledger_chain.append(block)

        # Persist
        self._save_ledger_block(block)

        print(f"[Consortium] Committed to ledger: Block #{block.sequence_number}, Hash: {block.consortium_hash[:16]}...")

    def _update_validator_reputations(self, anchor: ConsortiumAnchor):
        """
        Update validator reputations based on validation accuracy

        Rewards accurate validators, penalizes inaccurate ones
        """
        # Determine ground truth (majority vote)
        pass_count = sum(
            1 for sig in anchor.cross_signatures
            if sig.validation_result == ValidationResult.PASS
        )
        fail_count = sum(
            1 for sig in anchor.cross_signatures
            if sig.validation_result == ValidationResult.FAIL
        )

        ground_truth = ValidationResult.PASS if pass_count > fail_count else ValidationResult.FAIL

        # Update each validator
        for sig in anchor.cross_signatures:
            if sig.validator_id not in self.members:
                continue

            validator = self.members[sig.validator_id]

            if sig.validation_result == ground_truth:
                # Accurate validation
                validator.reputation_score += self.accurate_validation_reward
                validator.accurate_validations += 1
                print(f"[Consortium] Reputation +{self.accurate_validation_reward:.3f}: {validator.organization_name}")
            else:
                # Inaccurate validation
                validator.reputation_score -= self.inaccurate_validation_penalty
                print(f"[Consortium] Reputation -{self.inaccurate_validation_penalty:.3f}: {validator.organization_name}")

            # Clamp reputation
            validator.reputation_score = max(0.0, min(2.0, validator.reputation_score))

        self._save_member_registry()

    def query_ledger(
        self,
        start_sequence: int = 0,
        end_sequence: Optional[int] = None
    ) -> List[LedgerBlock]:
        """Query consortium ledger by sequence range"""
        if end_sequence is None:
            end_sequence = len(self.ledger_chain)

        return self.ledger_chain[start_sequence:end_sequence]

    def verify_anchor_in_ledger(self, anchor_id: str) -> Tuple[bool, Optional[Dict]]:
        """
        Verify anchor exists in ledger with valid consensus

        Returns (verified, proof_data)
        """
        for block in self.ledger_chain:
            for anchor in block.anchor_batch:
                if anchor.anchor_id == anchor_id:
                    proof = {
                        "block_sequence": block.sequence_number,
                        "block_hash": block.consortium_hash,
                        "consensus": anchor.consensus_achieved,
                        "signatures_count": len(anchor.cross_signatures),
                        "timestamp": anchor.consensus_timestamp.isoformat() if anchor.consensus_timestamp else None
                    }
                    return (True, proof)

        return (False, None)

    def get_member_reputation(self, member_id: str) -> Optional[float]:
        """Get current reputation score for member"""
        if member_id not in self.members:
            raise NotImplementedError("TODO: Implement this function")

        member = self.members[member_id]

        # Apply time decay
        days_since_active = (datetime.now() - member.last_active).days
        decay_factor = 0.5 ** (days_since_active / self.reputation_decay_halflife.days)

        decayed_reputation = member.reputation_score * decay_factor

        return round(decayed_reputation, 3)

    def export_consortium_report(self, output_path: Path) -> bool:
        """
        Export consortium status report

        Includes member directory, reputation scores, and ledger stats
        """
        report = {
            "consortium": {
                "name": "SSID Audit Consortium",
                "establishment_date": "2025-10-07",
                "total_members": len(self.members),
                "ledger_blocks": len(self.ledger_chain),
                "report_date": datetime.now().isoformat()
            },
            "members": [
                {
                    "member_id": m.member_id,
                    "organization": m.organization_name,
                    "tier": m.tier.value,
                    "reputation_score": self.get_member_reputation(m.member_id),
                    "total_validations": m.total_validations,
                    "accuracy_rate": (m.accurate_validations / m.total_validations * 100) if m.total_validations > 0 else 0,
                    "joined_date": m.joined_date.isoformat()
                }
                for m in self.members.values()
            ],
            "ledger_statistics": {
                "total_blocks": len(self.ledger_chain),
                "total_anchors": sum(len(b.anchor_batch) for b in self.ledger_chain),
                "latest_block_hash": self.ledger_chain[-1].consortium_hash if self.ledger_chain else None,
                "chain_height": len(self.ledger_chain)
            },
            "pending_anchors": len(self.pending_anchors)
        }

        output_path.write_text(json.dumps(report, indent=2), encoding='utf-8')
        print(f"[Consortium] Exported report: {output_path}")
        return True

    # Private helper methods

    def _create_genesis_block(self):
        """Create genesis block"""
        genesis = LedgerBlock(
            sequence_number=0,
            timestamp=datetime.now(),
            previous_hash="0" * 64,
            anchor_batch=[],
            consortium_hash=hashlib.sha256(b"SSID_CONSORTIUM_GENESIS").hexdigest(),
            merkle_root="0" * 64
        )
        self.ledger_chain.append(genesis)
        print(f"[Consortium] Created genesis block")

    def _select_validators(self, submitter_id: str) -> List[ConsortiumMember]:
        """Select validators for anchor (exclude submitter)"""
        eligible = [
            m for m in self.members.values()
            if m.member_id != submitter_id
            and m.reputation_score >= 0.7
            and m.tier != MemberTier.OBSERVER
        ]

        # Sort by reputation
        eligible.sort(key=lambda m: m.reputation_score, reverse=True)

        return eligible[:10]  # Select top 10

    def _verify_anchor_signature(self, anchor: ConsortiumAnchor) -> bool:
        """Verify anchor signature (simplified)"""
        # In production: verify Ed25519 signature
        return True

    def _perform_validation_checks(self, anchor: ConsortiumAnchor) -> bool:
        """Perform validation checks on anchor"""
        # Simplified validation
        checks = [
            len(anchor.compliance_summary) > 0,
            len(anchor.evidence_merkle_root) == 64,
            anchor.submission_timestamp <= datetime.now()
        ]
        return all(checks)

    def _sign_data(self, data: str) -> str:
        """Sign data with member private key"""
        return hmac.new(
            self.private_key.encode(),
            data.encode(),
            hashlib.sha256
        ).hexdigest()

    def _calculate_merkle_root(self, anchors: List[ConsortiumAnchor]) -> str:
        """Calculate merkle root of anchor batch"""
        if not anchors:
            return "0" * 64

        hashes = [hashlib.sha256(a.anchor_id.encode()).digest() for a in anchors]

        while len(hashes) > 1:
            if len(hashes) % 2 != 0:
                hashes.append(hashes[-1])

            hashes = [
                hashlib.sha256(hashes[i] + hashes[i+1]).digest()
                for i in range(0, len(hashes), 2)
            ]

        return hashes[0].hex()

    def _save_member_registry(self):
        """Persist member registry"""
        registry_file = self.data_dir / "member_registry.json"
        data = {
            m_id: {
                "organization_name": m.organization_name,
                "public_key": m.public_key,
                "tier": m.tier.value,
                "joined_date": m.joined_date.isoformat(),
                "reputation_score": m.reputation_score,
                "voting_weight": m.voting_weight,
                "cross_signing_quota": m.cross_signing_quota,
                "total_validations": m.total_validations,
                "accurate_validations": m.accurate_validations,
                "last_active": m.last_active.isoformat()
            }
            for m_id, m in self.members.items()
        }
        registry_file.write_text(json.dumps(data, indent=2), encoding='utf-8')

    def _load_member_registry(self):
        """Load member registry"""
        registry_file = self.data_dir / "member_registry.json"
        if not registry_file.exists():
            return

        data = json.loads(registry_file.read_text(encoding='utf-8'))
        for m_id, m_data in data.items():
            self.members[m_id] = ConsortiumMember(
                member_id=m_id,
                organization_name=m_data['organization_name'],
                public_key=m_data['public_key'],
                tier=MemberTier(m_data['tier']),
                joined_date=datetime.fromisoformat(m_data['joined_date']),
                reputation_score=m_data['reputation_score'],
                voting_weight=m_data['voting_weight'],
                cross_signing_quota=m_data['cross_signing_quota'],
                total_validations=m_data['total_validations'],
                accurate_validations=m_data['accurate_validations'],
                last_active=datetime.fromisoformat(m_data['last_active'])
            )

    def _save_ledger_block(self, block: LedgerBlock):
        """Persist ledger block"""
        block_file = self.data_dir / f"block_{block.sequence_number:06d}.json"
        data = {
            "sequence_number": block.sequence_number,
            "timestamp": block.timestamp.isoformat(),
            "previous_hash": block.previous_hash,
            "consortium_hash": block.consortium_hash,
            "merkle_root": block.merkle_root,
            "anchors": [
                {
                    "anchor_id": a.anchor_id,
                    "submitter_id": a.submitter_id,
                    "consensus_achieved": a.consensus_achieved,
                    "signatures_count": len(a.cross_signatures)
                }
                for a in block.anchor_batch
            ]
        }
        block_file.write_text(json.dumps(data, indent=2), encoding='utf-8')


def demo_consortium():
    """Demonstrate consortium ledger functionality"""
    print("=== SSID Consortium Ledger Demo ===\n")

    # Create consortium with 5 member organizations
    members_data = [
        ("GlobalBank AG", MemberTier.FOUNDING),
        ("TechCorp Solutions", MemberTier.FULL),
        ("FinTech Innovations", MemberTier.FULL),
        ("Digital Trust GmbH", MemberTier.ASSOCIATE),
        ("Compliance Partners", MemberTier.ASSOCIATE)
    ]

    ledgers = []

    print("1. Initializing consortium members...")

    # Pre-generate consistent member IDs and keys for all orgs
    member_keys = {}
    for org_name, tier in members_data:
        public_key = secrets.token_hex(32)
        member_id = hashlib.sha256(public_key.encode()).hexdigest()[:16]
        member_keys[org_name] = {
            'member_id': member_id,
            'public_key': public_key,
            'private_key': secrets.token_hex(32),
            'tier': tier
        }

    for i, (org_name, tier) in enumerate(members_data):
        keys = member_keys[org_name]
        ledger = ConsortiumLedger(
            member_id=keys['member_id'],
            private_key=keys['private_key'],
            public_key=keys['public_key'],
            data_dir=Path(f"./consortium_data/member_{i}")
        )

        # Register all members in each ledger (simulating distributed registry)
        for other_org, other_tier in members_data:
            other_keys = member_keys[other_org]
            ledger.register_member(other_org, other_keys['public_key'], other_keys['tier'])

        ledgers.append(ledger)
        print(f"   Initialized: {org_name}")

    # Member 0 submits an anchor
    print("\n2. GlobalBank AG submits compliance anchor...")
    anchor = ConsortiumAnchor(
        anchor_id=hashlib.sha256(secrets.token_bytes(32)).hexdigest(),
        submitter_id=list(ledgers[0].members.keys())[0],
        submission_timestamp=datetime.now(),
        compliance_data_cid=f"ipfs://{secrets.token_hex(32)}",
        evidence_merkle_root=secrets.token_hex(32),
        compliance_summary={"gdpr": 95, "dora": 92, "mica": 88},
        submitter_signature=secrets.token_hex(64)
    )

    ledgers[0].submit_anchor(anchor)

    # Other members validate
    print("\n3. Consortium members validate anchor...")
    for i, ledger in enumerate(ledgers[1:], 1):
        # Simulate receiving anchor
        ledger.pending_anchors[anchor.anchor_id] = anchor

        result = ValidationResult.PASS if i != 4 else ValidationResult.FAIL  # One fails for demo
        cross_sig = ledger.validate_anchor(
            anchor.anchor_id,
            result,
            f"validation_evidence_{i}"
        )

        # Sync cross-signature back to all ledgers
        if cross_sig:
            for other_ledger in ledgers:
                if anchor.anchor_id in other_ledger.pending_anchors:
                    other_ledger.pending_anchors[anchor.anchor_id].cross_signatures.append(cross_sig)

    # Check consensus on originating ledger
    print("\n4. Checking consensus...")
    ledgers[0]._check_consensus(anchor.anchor_id)

    # Export report
    print("\n5. Exporting consortium report...")
    report_path = Path("./consortium_report.json")
    ledgers[0].export_consortium_report(report_path)

    # Verify anchor in ledger
    print("\n6. Verifying anchor in ledger...")
    verified, proof = ledgers[0].verify_anchor_in_ledger(anchor.anchor_id)
    if verified:
        print(f"   OK Anchor verified in block #{proof['block_sequence']}")
        print(f"   Block hash: {proof['block_hash'][:16]}...")
        print(f"   Signatures: {proof['signatures_count']}")

    print("\n=== Demo Complete ===")


if __name__ == "__main__":
    demo_consortium()
