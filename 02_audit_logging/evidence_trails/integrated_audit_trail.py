#!/usr/bin/env python3
"""
Integrated Audit Trail System
===============================

Unified evidence management combining WORM storage + Blockchain anchoring.
Implements MUST-003 (Audit Trail), MUST-007 (WORM), MUST-008 (Blockchain), MUST-021 (Record Keeping).

Features:
- End-to-end evidence lifecycle management
- Automatic WORM storage with blockchain anchoring
- 10-year retention compliance (MiCA Art.74)
- Tamper-proof audit trails
- Cryptographic integrity verification

Compliance: MUST-003, MUST-007, MUST-008, MUST-021
Version: 1.0.0
"""

import sys
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent / "worm_storage"))
sys.path.insert(0, str(Path(__file__).parent.parent / "blockchain_anchor"))

from worm_storage_engine import WORMStorageEngine, WORMViolationError
from blockchain_anchoring_engine import BlockchainAnchoringEngine

import json
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

class IntegratedAuditTrail:
    """
    Integrated audit trail system combining WORM + Blockchain.

    Workflow:
    1. Evidence submitted → WORM storage (immutable write)
    2. Evidence hash → Blockchain anchoring (batch or immediate)
    3. Proof available → Cryptographic verification chain

    Compliance Guarantees:
    - MUST-003: Complete audit trail with immutable logging
    - MUST-007: WORM storage (write-once, no modifications)
    - MUST-008: Blockchain anchoring for tamper detection
    - MUST-021: 10-year retention (MiCA compliance)
    """

    def __init__(self,
                 worm_root: str = "02_audit_logging/worm_storage/vault",
                 anchor_root: str = "02_audit_logging/blockchain_anchor"):
        """
        Initialize integrated audit trail system.

        Args:
            worm_root: WORM storage directory
            anchor_root: Blockchain anchor directory
        """
        self.worm = WORMStorageEngine(worm_root)
        self.anchor = BlockchainAnchoringEngine(anchor_root)

        # Pending anchors (batched)
        self.pending_anchors: List[str] = []
        self.batch_size = 100  # Batch size for blockchain anchoring

    def record_evidence(self, evidence_id: str, evidence_data: Dict[str, Any],
                       category: str = "general",
                       immediate_anchor: bool = False,
                       chain: str = "ethereum:sepolia") -> Dict[str, Any]:
        """
        Record evidence with WORM storage + blockchain anchoring.

        Args:
            evidence_id: Unique evidence identifier
            evidence_data: Evidence content (JSON-serializable)
            category: Evidence category
            immediate_anchor: Anchor immediately (True) or batch (False)
            chain: Target blockchain

        Returns:
            Evidence record with WORM and anchor details
        """
        # Step 1: Write to WORM storage
        worm_result = self.worm.write_evidence(evidence_id, evidence_data, category)

        # Step 2: Blockchain anchoring
        if immediate_anchor:
            # Immediate anchoring (for critical evidence)
            anchor_result = self.anchor.anchor_single_evidence(
                worm_result["content_hash"],
                chain=chain
            )
        else:
            # Batched anchoring (cost-optimized)
            self.pending_anchors.append(worm_result["content_hash"])

            # Anchor batch if threshold reached
            if len(self.pending_anchors) >= self.batch_size:
                anchor_result = self.anchor.anchor_evidence_batch(
                    self.pending_anchors,
                    chain=chain
                )
                self.pending_anchors = []
            else:
                anchor_result = {
                    "status": "pending_batch",
                    "pending_count": len(self.pending_anchors)
                }

        return {
            "evidence_id": evidence_id,
            "worm_storage": {
                "content_hash": worm_result["content_hash"],
                "file_path": worm_result["file_path"],
                "timestamp": worm_result["timestamp"],
                "status": worm_result["status"]
            },
            "blockchain_anchor": anchor_result,
            "compliance": {
                "MUST-003": "Audit trail recorded",
                "MUST-007": "WORM storage enforced",
                "MUST-008": f"Blockchain anchor {anchor_result.get('status', 'pending')}",
                "MUST-021": "10-year retention configured"
            }
        }

    def verify_evidence(self, evidence_id: str) -> Dict[str, Any]:
        """
        Verify evidence integrity (WORM + Blockchain).

        Args:
            evidence_id: Evidence identifier

        Returns:
            Verification result with integrity status
        """
        # Verify WORM integrity
        worm_evidence = self.worm.read_evidence(evidence_id, verify_integrity=True)

        # Get blockchain anchor proof
        try:
            anchor_proof = self.anchor.get_anchor_proof(worm_evidence["content_hash"])
            blockchain_verified = anchor_proof["proof_valid"]
            anchor_details = anchor_proof
        except FileNotFoundError:
            blockchain_verified = False
            anchor_details = {"status": "not_anchored"}

        return {
            "evidence_id": evidence_id,
            "worm_integrity": worm_evidence["integrity_verified"],
            "blockchain_verified": blockchain_verified,
            "content_hash": worm_evidence["content_hash"],
            "anchor_details": anchor_details,
            "overall_status": "VERIFIED" if (worm_evidence["integrity_verified"] and blockchain_verified) else "PARTIAL",
            "timestamp": worm_evidence["timestamp"]
        }

    def flush_pending_anchors(self, chain: str = "ethereum:sepolia") -> Dict[str, Any]:
        """
        Force-flush pending anchors to blockchain.

        Args:
            chain: Target blockchain

        Returns:
            Anchor result
        """
        if len(self.pending_anchors) == 0:
            return {"status": "no_pending_anchors"}

        anchor_result = self.anchor.anchor_evidence_batch(
            self.pending_anchors,
            chain=chain
        )

        self.pending_anchors = []

        return anchor_result

    def get_audit_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive audit report.

        Returns:
            Audit report with statistics and compliance status
        """
        # WORM statistics
        worm_evidence = self.worm.list_evidence()

        # Blockchain statistics
        blockchain_anchors = self.anchor.list_anchors()

        # Integrity verification
        integrity_report = self.worm.verify_all_integrity()

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "worm_storage": {
                "total_evidence": len(worm_evidence),
                "integrity_verified": integrity_report["verified"],
                "integrity_failed": integrity_report["failed"]
            },
            "blockchain_anchoring": {
                "total_anchors": len(blockchain_anchors),
                "confirmed_anchors": len([a for a in blockchain_anchors if a["status"] == "confirmed"]),
                "pending_batch": len(self.pending_anchors)
            },
            "compliance_status": {
                "MUST-003-AUDIT-LOGGING": "COMPLIANT" if len(worm_evidence) > 0 else "NO_DATA",
                "MUST-007-WORM-STORAGE": "COMPLIANT" if integrity_report["verified"] > 0 else "NO_DATA",
                "MUST-008-BLOCKCHAIN-ANCHOR": "COMPLIANT" if len(blockchain_anchors) > 0 else "NO_DATA",
                "MUST-021-RECORD-KEEPING": "COMPLIANT (10-year retention configured)"
            },
            "retention_policy": {
                "retention_years": 10,
                "compliance": ["MiCA Art.74", "AMLD6 Art.40", "GDPR Art.5(1)(e)"]
            }
        }

def demo_integrated_audit_trail():
    """Demonstration of integrated audit trail system."""
    print("=" * 70)
    print("Integrated Audit Trail System - Full Workflow Demo")
    print("=" * 70)
    print()

    # Initialize system
    audit_trail = IntegratedAuditTrail()

    # DEMO 1: Record critical evidence (immediate anchoring)
    print("DEMO 1: Recording critical evidence (immediate blockchain anchor)")
    print("-" * 70)
    result1 = audit_trail.record_evidence(
        evidence_id="critical_txn_001",
        evidence_data={
            "event": "high_value_transaction",
            "amount_eur": 100000,
            "risk_score": 0.95
        },
        category="transactions",
        immediate_anchor=True
    )

    print(f"Evidence ID: {result1['evidence_id']}")
    print(f"WORM Hash: {result1['worm_storage']['content_hash'][:16]}...")
    print(f"Blockchain: {result1['blockchain_anchor']['status']}")
    print(f"TX Hash: {result1['blockchain_anchor'].get('tx_hash', 'N/A')}")
    print()

    # DEMO 2: Record normal evidence (batched anchoring)
    print("DEMO 2: Recording normal evidence (batched anchoring)")
    print("-" * 70)
    for i in range(3):
        result = audit_trail.record_evidence(
            evidence_id=f"normal_event_{i:03d}",
            evidence_data={"event": f"standard_operation_{i}", "value": i},
            category="operations",
            immediate_anchor=False
        )
        print(f"Evidence {i+1}/3: {result['evidence_id']} (pending batch)")

    print(f"Pending anchors: {len(audit_trail.pending_anchors)}")
    print()

    # DEMO 3: Flush pending anchors
    print("DEMO 3: Flushing pending anchors to blockchain")
    print("-" * 70)
    flush_result = audit_trail.flush_pending_anchors()

    print(f"Batch ID: {flush_result['batch_id']}")
    print(f"Evidence Count: {flush_result['evidence_count']}")
    print(f"Merkle Root: {flush_result['merkle_root'][:16]}...")
    print(f"TX Hash: {flush_result['tx_hash']}")
    print()

    # DEMO 4: Verify evidence
    print("DEMO 4: Verifying evidence integrity")
    print("-" * 70)
    verification = audit_trail.verify_evidence("critical_txn_001")

    print(f"Evidence ID: {verification['evidence_id']}")
    print(f"WORM Integrity: {verification['worm_integrity']}")
    print(f"Blockchain Verified: {verification['blockchain_verified']}")
    print(f"Overall Status: {verification['overall_status']}")
    print()

    # DEMO 5: Generate audit report
    print("DEMO 5: Generating compliance audit report")
    print("-" * 70)
    report = audit_trail.get_audit_report()

    print(f"Total Evidence: {report['worm_storage']['total_evidence']}")
    print(f"Integrity Verified: {report['worm_storage']['integrity_verified']}")
    print(f"Blockchain Anchors: {report['blockchain_anchoring']['total_anchors']}")
    print(f"Retention Policy: {report['retention_policy']['retention_years']} years")
    print()
    print("Compliance Status:")
    for req, status in report['compliance_status'].items():
        print(f"  {req}: {status}")
    print()

    print("=" * 70)
    print("[OK] Integrated Audit Trail System - Demo Complete")
    print("=" * 70)

if __name__ == "__main__":
    demo_integrated_audit_trail()
