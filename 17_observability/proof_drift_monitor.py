#!/usr/bin/env python3
"""
Proof-Drift Monitor - Early-Warning System for Semantic Inconsistencies
========================================================================

Detects divergences in Merkle branches before they violate consensus.
Acts as "semantic integrity guard" for the L9-Federated Proof Plane.

Purpose:
- Detect proof divergence between nodes BEFORE consensus round
- Identify semantic inconsistencies (e.g., different event serializations)
- Alert governance layer for manual review
- Prevent Byzantine attacks via early detection

Architecture:
- Passive monitoring (no blocking)
- Real-time drift scoring
- Automatic alerting at threshold
- Integration with 17_observability/compliance_alert_monitor

Status: Phase 3 Foundation
Version: 1.0.0
"""

import json
import time
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict, field
from datetime import datetime
from collections import deque


@dataclass
class ProofDrift:
    """
    Detected proof drift between federation nodes.
    """
    timestamp: str
    node_pair: Tuple[str, str]  # (node_id_1, node_id_2)

    # Drift metrics
    merkle_divergence: bool      # True if Merkle roots differ
    drift_score: float           # 0.0-1.0 (1.0 = complete divergence)

    # Proof details
    batch_id: str
    consensus_round: int
    proof_count: int

    # Divergent proofs
    divergent_proof_ids: List[str]
    divergent_hashes: Dict[str, str]  # event_id → hash

    # Root cause analysis
    root_cause: str              # "serialization", "timestamp_drift", "data_corruption"
    severity: str                # "low", "medium", "high", "critical"

    # Resolution
    resolved: bool = False
    resolution_timestamp: Optional[str] = None


@dataclass
class DriftAlert:
    """
    Alert for drift threshold violation.
    """
    timestamp: str
    alert_id: str
    drift: ProofDrift

    # Alert metadata
    alert_level: str             # "warning", "error", "critical"
    governance_notified: bool

    # Recommended actions
    recommended_actions: List[str]


class ProofDriftMonitor:
    """
    Monitor for proof drift detection across federation nodes.

    Detects divergences in Merkle branches before consensus violation.
    """

    def __init__(
        self,
        drift_log_path: str = "17_observability/logs/proof_drift.jsonl",
        alert_log_path: str = "17_observability/logs/drift_alerts.jsonl",
        drift_threshold: float = 0.1,  # Alert if drift > 10%
        alert_callback: Optional[callable] = None
    ):
        """
        Initialize proof drift monitor.

        Args:
            drift_log_path: Path to drift detection log (JSONL)
            alert_log_path: Path to alert log (JSONL)
            drift_threshold: Drift score threshold for alerts (0.0-1.0)
            alert_callback: Callback for real-time alerts
        """
        self.drift_log_path = Path(drift_log_path)
        self.alert_log_path = Path(alert_log_path)

        self.drift_log_path.parent.mkdir(parents=True, exist_ok=True)
        self.alert_log_path.parent.mkdir(parents=True, exist_ok=True)

        self.drift_threshold = drift_threshold
        self.alert_callback = alert_callback

        # Node state tracking
        self.node_merkle_roots: Dict[str, Dict[int, str]] = {}
        # node_id → {consensus_round → merkle_root}

        self.node_proof_hashes: Dict[str, Dict[str, str]] = {}
        # node_id → {event_id → proof_hash}

        # Drift detection window
        self.drift_window = deque(maxlen=1000)  # Last 1000 drift checks

        # Alert counters
        self.alerts_fired = 0
        self.drifts_detected = 0
        self.drifts_resolved = 0

    def register_node_merkle_root(
        self,
        node_id: str,
        consensus_round: int,
        merkle_root: str,
        proof_hashes: List[str]
    ) -> None:
        """
        Register Merkle root from federation node.

        Args:
            node_id: Node identifier
            consensus_round: Consensus round number
            merkle_root: Computed Merkle root
            proof_hashes: List of proof hashes in batch
        """
        if node_id not in self.node_merkle_roots:
            self.node_merkle_roots[node_id] = {}

        self.node_merkle_roots[node_id][consensus_round] = merkle_root

        # Store proof hashes for drift analysis
        if node_id not in self.node_proof_hashes:
            self.node_proof_hashes[node_id] = {}

        for i, proof_hash in enumerate(proof_hashes):
            event_id = f"event_{consensus_round}_{i}"
            self.node_proof_hashes[node_id][event_id] = proof_hash

    def check_drift(
        self,
        consensus_round: int
    ) -> List[ProofDrift]:
        """
        Check for proof drift across all node pairs.

        Args:
            consensus_round: Consensus round to check

        Returns:
            List of detected ProofDrift instances
        """
        drifts = []

        # Get all nodes with Merkle roots for this round
        nodes_with_roots = [
            node_id for node_id, roots in self.node_merkle_roots.items()
            if consensus_round in roots
        ]

        if len(nodes_with_roots) < 2:
            return drifts  # Need at least 2 nodes to compare

        # Compare all node pairs
        for i, node_1 in enumerate(nodes_with_roots):
            for node_2 in nodes_with_roots[i+1:]:
                drift = self._compare_nodes(
                    node_1,
                    node_2,
                    consensus_round
                )

                if drift is not None:
                    drifts.append(drift)
                    self.drifts_detected += 1

                    # Log drift
                    self._log_drift(drift)

                    # Check alert threshold
                    if drift.drift_score >= self.drift_threshold:
                        self._fire_alert(drift)

        return drifts

    def _compare_nodes(
        self,
        node_1: str,
        node_2: str,
        consensus_round: int
    ) -> Optional[ProofDrift]:
        """
        Compare Merkle roots and proof hashes between two nodes.

        Args:
            node_1: First node identifier
            node_2: Second node identifier
            consensus_round: Consensus round

        Returns:
            ProofDrift if divergence detected, None otherwise
        """
        # Get Merkle roots
        root_1 = self.node_merkle_roots[node_1].get(consensus_round)
        root_2 = self.node_merkle_roots[node_2].get(consensus_round)

        if root_1 is None or root_2 is None:
            return None

        # Check if roots match
        merkle_divergence = (root_1 != root_2)

        if not merkle_divergence:
            return None  # No drift

        # Analyze divergent proofs
        divergent_proof_ids = []
        divergent_hashes = {}

        # Compare proof hashes
        node_1_hashes = self.node_proof_hashes.get(node_1, {})
        node_2_hashes = self.node_proof_hashes.get(node_2, {})

        all_event_ids = set(node_1_hashes.keys()) | set(node_2_hashes.keys())

        for event_id in all_event_ids:
            hash_1 = node_1_hashes.get(event_id)
            hash_2 = node_2_hashes.get(event_id)

            if hash_1 != hash_2:
                divergent_proof_ids.append(event_id)
                divergent_hashes[event_id] = f"{hash_1} != {hash_2}"

        # Compute drift score
        total_proofs = len(all_event_ids)
        divergent_count = len(divergent_proof_ids)
        drift_score = divergent_count / total_proofs if total_proofs > 0 else 0.0

        # Root cause analysis
        root_cause = self._analyze_root_cause(divergent_proof_ids, divergent_hashes)
        severity = self._compute_severity(drift_score)

        drift = ProofDrift(
            timestamp=datetime.utcnow().isoformat() + "Z",
            node_pair=(node_1, node_2),
            merkle_divergence=merkle_divergence,
            drift_score=drift_score,
            batch_id=f"batch_{consensus_round}",
            consensus_round=consensus_round,
            proof_count=total_proofs,
            divergent_proof_ids=divergent_proof_ids,
            divergent_hashes=divergent_hashes,
            root_cause=root_cause,
            severity=severity,
            resolved=False,
            resolution_timestamp=None
        )

        return drift

    def _analyze_root_cause(
        self,
        divergent_proof_ids: List[str],
        divergent_hashes: Dict[str, str]
    ) -> str:
        """
        Analyze root cause of drift.

        Args:
            divergent_proof_ids: List of divergent proof IDs
            divergent_hashes: Dict of divergent hashes

        Returns:
            Root cause classification
        """
        # Heuristic root cause detection

        if len(divergent_proof_ids) == 0:
            return "no_divergence"

        # If all proofs diverge, likely serialization issue
        if len(divergent_proof_ids) > 10:
            return "serialization_divergence"

        # If only a few proofs diverge, likely timestamp drift
        if len(divergent_proof_ids) <= 3:
            return "timestamp_drift"

        # Medium divergence, likely data inconsistency
        return "data_inconsistency"

    def _compute_severity(self, drift_score: float) -> str:
        """
        Compute severity level from drift score.

        Args:
            drift_score: Drift score (0.0-1.0)

        Returns:
            Severity level
        """
        if drift_score >= 0.5:
            return "critical"
        elif drift_score >= 0.3:
            return "high"
        elif drift_score >= 0.1:
            return "medium"
        else:
            return "low"

    def _log_drift(self, drift: ProofDrift) -> None:
        """
        Log drift to persistent storage.

        Args:
            drift: ProofDrift to log
        """
        drift_dict = asdict(drift)

        with self.drift_log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(drift_dict) + "\n")

    def _fire_alert(self, drift: ProofDrift) -> None:
        """
        Fire alert for drift threshold violation.

        Args:
            drift: ProofDrift that triggered alert
        """
        alert_id = f"drift_alert_{int(time.time() * 1000)}"

        # Determine alert level
        alert_level = "warning" if drift.severity in ["low", "medium"] else "critical"

        # Recommended actions based on root cause
        recommended_actions = self._generate_recommendations(drift)

        alert = DriftAlert(
            timestamp=datetime.utcnow().isoformat() + "Z",
            alert_id=alert_id,
            drift=drift,
            alert_level=alert_level,
            governance_notified=False,
            recommended_actions=recommended_actions
        )

        # Log alert
        alert_dict = asdict(alert)

        with self.alert_log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(alert_dict) + "\n")

        # Fire callback (if configured)
        if self.alert_callback is not None:
            self.alert_callback(alert)

        self.alerts_fired += 1

    def _generate_recommendations(self, drift: ProofDrift) -> List[str]:
        """
        Generate recommended actions for drift resolution.

        Args:
            drift: ProofDrift to analyze

        Returns:
            List of recommended actions
        """
        recommendations = []

        if drift.root_cause == "serialization_divergence":
            recommendations.extend([
                "CHECK: Event serialization logic (to_dict()) consistency",
                "VERIFY: JSON serialization order (sort_keys=True)",
                "INSPECT: Timestamp formatting (ISO 8601 with 'Z')",
                "ACTION: Re-sync nodes with canonical serialization"
            ])
        elif drift.root_cause == "timestamp_drift":
            recommendations.extend([
                "CHECK: Node clock synchronization (NTP)",
                "VERIFY: Timestamp precision (milliseconds)",
                "INSPECT: Timezone handling (UTC only)",
                "ACTION: Re-calibrate node clocks"
            ])
        elif drift.root_cause == "data_inconsistency":
            recommendations.extend([
                "CHECK: Event data integrity (source module)",
                "VERIFY: Handler processing logic",
                "INSPECT: WORM storage writes",
                "ACTION: Manual governance review required"
            ])
        else:
            recommendations.append("ACTION: Unknown root cause - full forensic audit required")

        return recommendations

    def get_drift_summary(self) -> Dict[str, Any]:
        """
        Get drift monitoring summary.

        Returns:
            Dict with drift statistics
        """
        return {
            "total_drifts_detected": self.drifts_detected,
            "total_drifts_resolved": self.drifts_resolved,
            "total_alerts_fired": self.alerts_fired,
            "active_nodes": len(self.node_merkle_roots),
            "drift_window_size": len(self.drift_window)
        }

    def resolve_drift(
        self,
        drift: ProofDrift,
        resolution_notes: str
    ) -> None:
        """
        Mark drift as resolved.

        Args:
            drift: ProofDrift to resolve
            resolution_notes: Resolution notes
        """
        drift.resolved = True
        drift.resolution_timestamp = datetime.utcnow().isoformat() + "Z"

        self.drifts_resolved += 1

        # Log resolution
        resolution_entry = {
            "timestamp": drift.resolution_timestamp,
            "drift_timestamp": drift.timestamp,
            "node_pair": drift.node_pair,
            "consensus_round": drift.consensus_round,
            "drift_score": drift.drift_score,
            "resolution_notes": resolution_notes
        }

        resolution_log = self.drift_log_path.parent / "drift_resolutions.jsonl"
        with resolution_log.open("a", encoding="utf-8") as f:
            f.write(json.dumps(resolution_entry) + "\n")


# Example usage
if __name__ == "__main__":
    print("Proof-Drift Monitor - Early-Warning System")
    print("=" * 70)

    # Create monitor
    def alert_callback(alert: DriftAlert):
        print(f"\n[ALERT] {alert.alert_level.upper()}: Drift detected")
        print(f"  Node Pair: {alert.drift.node_pair[0]} <-> {alert.drift.node_pair[1]}")
        print(f"  Drift Score: {alert.drift.drift_score:.2%}")
        print(f"  Severity: {alert.drift.severity}")
        print(f"  Root Cause: {alert.drift.root_cause}")
        print(f"  Recommended Actions:")
        for action in alert.recommended_actions:
            print(f"    - {action}")

    monitor = ProofDriftMonitor(
        drift_log_path="17_observability/logs/proof_drift_test.jsonl",
        alert_log_path="17_observability/logs/drift_alerts_test.jsonl",
        drift_threshold=0.1,
        alert_callback=alert_callback
    )

    # Simulate proof batch from 3 nodes
    consensus_round = 42

    # Node 1: Correct proofs
    node_1_proofs = [f"proof_{i}_correct" for i in range(100)]
    node_1_hashes = [hashlib.sha256(p.encode()).hexdigest() for p in node_1_proofs]
    node_1_merkle = hashlib.sha256("_".join(node_1_hashes).encode()).hexdigest()

    monitor.register_node_merkle_root("eu-node-001", consensus_round, node_1_merkle, node_1_hashes)

    # Node 2: Identical proofs (no drift)
    monitor.register_node_merkle_root("us-node-002", consensus_round, node_1_merkle, node_1_hashes)

    # Node 3: Divergent proofs (simulate drift)
    node_3_proofs = [f"proof_{i}_divergent" if i < 15 else f"proof_{i}_correct" for i in range(100)]
    node_3_hashes = [hashlib.sha256(p.encode()).hexdigest() for p in node_3_proofs]
    node_3_merkle = hashlib.sha256("_".join(node_3_hashes).encode()).hexdigest()

    monitor.register_node_merkle_root("apac-node-003", consensus_round, node_3_merkle, node_3_hashes)

    # Check drift
    print("\nChecking drift for consensus round 42...")
    drifts = monitor.check_drift(consensus_round)

    print(f"\nDrift Detection Summary:")
    print(f"  Total Drifts Detected: {len(drifts)}")

    for drift in drifts:
        print(f"\n  Drift between {drift.node_pair[0]} <-> {drift.node_pair[1]}:")
        print(f"    Drift Score: {drift.drift_score:.2%}")
        print(f"    Divergent Proofs: {len(drift.divergent_proof_ids)}")
        print(f"    Root Cause: {drift.root_cause}")
        print(f"    Severity: {drift.severity}")

    # Get summary
    summary = monitor.get_drift_summary()
    print(f"\nMonitor Summary:")
    for key, value in summary.items():
        print(f"  {key}: {value}")

    print()
    print("=" * 70)
    print("[OK] Proof-Drift Monitor Test Complete")
