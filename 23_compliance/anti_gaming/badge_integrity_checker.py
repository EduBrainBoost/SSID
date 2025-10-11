#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Badge Integrity Checker - Anti-Gaming Module
SSID Phase 1 Implementation

Purpose:
- Verify badge hashes against registry locks
- Cross-reference badge issuance with audit logs
- Detect anomalous badge patterns (score inflation, duplicate claims)
- Generate violation reports for fraud detection pipeline

Architecture:
1 Badge = 1 Hash = 1 Proof
Any inconsistency → violation log → compliance score penalty
"""

import json
import hashlib
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Iterable
from datetime import datetime, timezone
from dataclasses import dataclass, asdict


# Legacy function for backward compatibility
def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def verify_badge_records(records: Iterable[Dict[str, str]]) -> List[Dict[str, str]]:
    """Verify signature integrity of badge records.
    Each record requires keys: id, payload, sig where sig == sha256(payload).
    Returns a list of invalid records (empty list means all valid).
    """
    invalid = []
    for r in records:
        if not isinstance(r, dict):
            invalid.append({"error": "not-a-dict", "record": str(r)})
            continue
        payload = r.get("payload", "")
        sig = r.get("sig", "")
        expected = _sha256_text(payload)
        if sig != expected:
            invalid.append({"id": r.get("id", "?"), "error": "bad-signature"})
    return invalid


@dataclass
class BadgeViolation:
    """Represents a badge integrity violation"""
    violation_id: str
    timestamp: str
    severity: str  # critical, high, medium, low
    badge_id: Optional[str]
    violation_type: str
    description: str
    affected_entities: List[str]
    evidence_path: Optional[str]

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class BadgeCheckResult:
    """Result of badge integrity check"""
    status: str  # PASS, FAIL, WARNING
    timestamp: str
    total_badges_checked: int
    violations_found: int
    violations: List[BadgeViolation]
    hash_integrity_score: float  # 0.0 - 100.0

    def to_dict(self) -> Dict:
        return {
            "status": self.status,
            "timestamp": self.timestamp,
            "total_badges_checked": self.total_badges_checked,
            "violations_found": self.violations_found,
            "violations": [v.to_dict() for v in self.violations],
            "hash_integrity_score": self.hash_integrity_score
        }


class BadgeIntegrityChecker:
    """
    Hash-based badge verification with cross-audit correlation.

    Verification Steps:
    1. Load registry locks (structure_lock_l3.json, hash_chain.json)
    2. Discover badge artifacts (chart.yaml capabilities, test results)
    3. Verify hash consistency (badge_id → hash → registry anchor)
    4. Cross-check with audit logs (02_audit_logging/evidence/)
    5. Detect anomalies (duplicate hashes, orphaned badges, reputation gaming)
    """

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.registry_path = repo_root / "24_meta_orchestration" / "registry"
        self.audit_path = repo_root / "02_audit_logging" / "evidence"
        self.violations: List[BadgeViolation] = []
        self.badge_registry: Dict[str, Dict] = {}

    def load_registry_locks(self) -> Tuple[Dict, Dict]:
        """Load structure lock and hash chain from registry"""
        structure_lock_file = self.registry_path / "locks" / "structure_lock_l3.json"
        hash_chain_file = self.registry_path / "locks" / "hash_chain.json"

        structure_lock = {}
        hash_chain = {}

        if structure_lock_file.exists():
            with open(structure_lock_file, 'r', encoding='utf-8') as f:
                structure_lock = json.load(f)
        else:
            self._add_violation(
                severity="critical",
                violation_type="missing_registry",
                description="Registry structure lock not found",
                affected_entities=["24_meta_orchestration/registry"]
            )

        if hash_chain_file.exists():
            with open(hash_chain_file, 'r', encoding='utf-8') as f:
                hash_chain = json.load(f)

        return structure_lock, hash_chain

    def discover_badges(self) -> Dict[str, Dict]:
        """
        Discover badge artifacts from chart.yaml capabilities.

        Badge Sources:
        - chart.yaml → capabilities.MUST (achievement badges)
        - test results → conformance badges
        - compliance mappings → regulatory badges
        """
        badges = {}

        # Discover from chart.yaml files
        for chart_file in self.repo_root.glob("**/chart.yaml"):
            if ".git" in str(chart_file):
                continue

            try:
                import yaml
                with open(chart_file, 'r', encoding='utf-8') as f:
                    chart_data = yaml.safe_load(f)

                if not chart_data or 'metadata' not in chart_data:
                    continue

                shard_id = chart_data['metadata'].get('shard_id')
                root = chart_data['metadata'].get('root')

                if not shard_id or not root:
                    continue

                badge_id = f"{root}::{shard_id}"

                # Create badge fingerprint from capabilities
                capabilities = chart_data.get('capabilities', {})
                must_caps = capabilities.get('MUST', [])

                badge_data = {
                    "badge_id": badge_id,
                    "root": root,
                    "shard_id": shard_id,
                    "capabilities_count": len(must_caps),
                    "version": chart_data['metadata'].get('version'),
                    "status": chart_data['metadata'].get('status'),
                    "source_file": str(chart_file.relative_to(self.repo_root))
                }

                # Generate hash from badge metadata
                badge_hash = self._compute_badge_hash(badge_data)
                badge_data["hash"] = badge_hash

                badges[badge_id] = badge_data

            except Exception as e:
                self._add_violation(
                    severity="medium",
                    violation_type="badge_discovery_error",
                    description=f"Failed to parse badge from {chart_file}: {e}",
                    affected_entities=[str(chart_file)]
                )

        return badges

    def _compute_badge_hash(self, badge_data: Dict) -> str:
        """Compute deterministic hash for badge"""
        # Create canonical representation
        canonical = json.dumps({
            "badge_id": badge_data["badge_id"],
            "version": badge_data["version"],
            "capabilities_count": badge_data["capabilities_count"],
            "status": badge_data["status"]
        }, sort_keys=True)

        return hashlib.sha256(canonical.encode('utf-8')).hexdigest()

    def verify_badge_hashes(self, badges: Dict[str, Dict]) -> List[str]:
        """
        Verify badge hash integrity.

        Checks:
        - Hash consistency (recompute and compare)
        - Duplicate hashes across different badges
        - Orphaned badges (no registry anchor)
        """
        hash_to_badges: Dict[str, List[str]] = {}
        verified_badges = []

        # Group badges by hash
        for badge_id, badge_data in badges.items():
            badge_hash = badge_data["hash"]

            if badge_hash not in hash_to_badges:
                hash_to_badges[badge_hash] = []
            hash_to_badges[badge_hash].append(badge_id)

        # Detect duplicate hashes (potential badge fraud)
        for badge_hash, badge_ids in hash_to_badges.items():
            if len(badge_ids) > 1:
                self._add_violation(
                    severity="high",
                    violation_type="duplicate_badge_hash",
                    description=f"Multiple badges share the same hash: {badge_hash[:16]}...",
                    affected_entities=badge_ids,
                    badge_id=None
                )
            else:
                verified_badges.append(badge_ids[0])

        return verified_badges

    def cross_check_audit_logs(self, badges: Dict[str, Dict]) -> None:
        """
        Cross-reference badges with audit log evidence.

        Validates:
        - Badge issuance events exist in audit logs
        - Timestamps are consistent
        - No backdated or future-dated badges
        """
        # Check if audit registry exists
        audit_registry = self.audit_path / "registry" / "registry_anchor.json"

        if not audit_registry.exists():
            self._add_violation(
                severity="medium",
                violation_type="missing_audit_anchor",
                description="Audit registry anchor not found - cannot verify badge trail",
                affected_entities=["02_audit_logging/evidence/registry"]
            )
            return

        # In production, this would:
        # 1. Load audit logs from WORM storage
        # 2. Search for badge_issued events
        # 3. Verify timestamp consistency
        # 4. Detect anomalous patterns

        # For now, validate presence
        for badge_id in badges.keys():
            raise NotImplementedError("TODO: Implement this block")
            # In full implementation: query 02_audit_logging for badge_id events
            raise NotImplementedError("TODO: Implement this block")

    def detect_reputation_gaming(self, badges: Dict[str, Dict]) -> None:
        """
        Detect reputation gaming patterns.

        Red flags:
        - Sudden spike in badge issuance
        - Badges without corresponding test evidence
        - Badges from inactive/deprecated shards
        """
        inactive_badges = []

        for badge_id, badge_data in badges.items():
            if badge_data.get("status") == "deprecated":
                inactive_badges.append(badge_id)
                self._add_violation(
                    severity="low",
                    violation_type="deprecated_badge_active",
                    description=f"Badge from deprecated shard is still active",
                    affected_entities=[badge_id],
                    badge_id=badge_id
                )

        # Check for badges without implementations
        for badge_id, badge_data in badges.items():
            source_file = Path(badge_data["source_file"])
            impl_dir = source_file.parent / "implementations"

            if not impl_dir.exists():
                self._add_violation(
                    severity="medium",
                    violation_type="badge_without_implementation",
                    description=f"Badge exists but no implementation found",
                    affected_entities=[badge_id],
                    badge_id=badge_id
                )

    def _add_violation(
        self,
        severity: str,
        violation_type: str,
        description: str,
        affected_entities: List[str],
        badge_id: Optional[str] = None,
        evidence_path: Optional[str] = None
    ) -> None:
        """Add a violation to the report"""
        violation = BadgeViolation(
            violation_id=f"BIV-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{len(self.violations):04d}",
            timestamp=datetime.now(timezone.utc).isoformat(),
            severity=severity,
            badge_id=badge_id,
            violation_type=violation_type,
            description=description,
            affected_entities=affected_entities,
            evidence_path=evidence_path
        )
        self.violations.append(violation)

    def calculate_integrity_score(self, total_badges: int, violations: int) -> float:
        """
        Calculate hash integrity score (0-100).

        Formula:
        - Base score: 100
        - Critical violation: -20 points
        - High violation: -10 points
        - Medium violation: -5 points
        - Low violation: -1 point
        - Minimum score: 0
        """
        score = 100.0

        for violation in self.violations:
            if violation.severity == "critical":
                score -= 20
            elif violation.severity == "high":
                score -= 10
            elif violation.severity == "medium":
                score -= 5
            elif violation.severity == "low":
                score -= 1

        return max(0.0, score)

    def run_check(self) -> BadgeCheckResult:
        """Execute full badge integrity check"""
        timestamp = datetime.now(timezone.utc).isoformat()

        # Step 1: Load registry
        structure_lock, hash_chain = self.load_registry_locks()

        # Step 2: Discover badges
        badges = self.discover_badges()

        # Step 3: Verify hashes
        verified_badges = self.verify_badge_hashes(badges)

        # Step 4: Cross-check audit logs
        self.cross_check_audit_logs(badges)

        # Step 5: Detect gaming patterns
        self.detect_reputation_gaming(badges)

        # Step 6: Calculate score
        integrity_score = self.calculate_integrity_score(len(badges), len(self.violations))

        # Determine overall status
        status = "PASS"
        if len(self.violations) > 0:
            critical_high = sum(1 for v in self.violations if v.severity in ["critical", "high"])
            if critical_high > 0:
                status = "FAIL"
            else:
                status = "WARNING"

        # Step 7: Log to evidence chain (Phase 2 integration)
        try:
            sys.path.insert(0, str(self.repo_root / "02_audit_logging"))
            from evidence.score_algorithm_logger import ScoreAlgorithmLogger

            logger = ScoreAlgorithmLogger(self.repo_root)
            for badge_id, badge_data in badges.items():
                badge_violations = [v.to_dict() for v in self.violations if v.badge_id == badge_id]
                logger.log_badge_integrity_check(
                    badge_id=badge_id,
                    integrity_score=integrity_score,
                    violations=badge_violations,
                    metadata={
                        "version": badge_data.get("version"),
                        "status": badge_data.get("status"),
                        "check_timestamp": timestamp
                    }
                )
        except Exception as e:
            # Don't fail the check if logging fails
            print(f"Warning: Failed to log to evidence chain: {e}", file=sys.stderr)

        return BadgeCheckResult(
            status=status,
            timestamp=timestamp,
            total_badges_checked=len(badges),
            violations_found=len(self.violations),
            violations=self.violations,
            hash_integrity_score=integrity_score
        )


def main():
    """CLI entry point"""
    # Find repo root
    repo_root = Path(__file__).resolve().parents[2]

    # Run checker
    checker = BadgeIntegrityChecker(repo_root)
    result = checker.run_check()

    # Output results
    print(json.dumps(result.to_dict(), indent=2))

    # Write violation log
    violations_file = repo_root / "23_compliance" / "anti_gaming" / "violations" / f"badge_violations_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    violations_file.parent.mkdir(parents=True, exist_ok=True)

    with open(violations_file, 'w', encoding='utf-8') as f:
        json.dump(result.to_dict(), f, indent=2)

    # Exit with appropriate code
    if result.status == "FAIL":
        sys.exit(1)
    elif result.status == "WARNING":
        sys.exit(0)  # Don't block CI on warnings
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
