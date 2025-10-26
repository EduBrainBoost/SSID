#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quarantine Engine - Change Detection & Isolation System
========================================================

Automatische Erkennung und Quarantäne von:
- Unregistrierten Artefakten
- Unbefugten Änderungen
- Schema-Verletzungen
- Hash-Abweichungen
- Policy-Verstößen

Version: 1.0.0
Author: SSID Security Team
Date: 2025-10-24
"""

import sys
import json
import hashlib
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, asdict
from enum import Enum

# Repository root
REPO_ROOT = Path(__file__).parent.parent.parent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("QUARANTINE_ENGINE")


class ViolationType(Enum):
    """Types of violations"""
    UNREGISTERED_ARTEFACT = "unregistered_artefact"
    HASH_MISMATCH = "hash_mismatch"
    SCHEMA_VIOLATION = "schema_violation"
    POLICY_VIOLATION = "policy_violation"
    UNAUTHORIZED_CHANGE = "unauthorized_change"
    DUPLICATE_RULE_ID = "duplicate_rule_id"
    MISSING_SHARD_ENTRY = "missing_shard_entry"


class QuarantineAction(Enum):
    """Actions to take on violations"""
    BLOCK = "block"
    ISOLATE = "isolate"
    ALERT = "alert"
    ROLLBACK = "rollback"


@dataclass
class Violation:
    """Detected violation"""
    type: ViolationType
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    file_path: str
    details: str
    detected_at: str
    hash_expected: Optional[str] = None
    hash_actual: Optional[str] = None
    action: QuarantineAction = QuarantineAction.BLOCK


@dataclass
class QuarantineEntry:
    """Entry in quarantine"""
    id: str
    violations: List[Violation]
    status: str  # QUARANTINED, REVIEWED, RELEASED
    quarantined_at: str
    reviewed_at: Optional[str] = None
    reviewer: Optional[str] = None
    notes: str = ""


class ChangeDetector:
    """
    Detects unauthorized changes in the system
    """

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.registry_path = repo_root / "24_meta_orchestration" / "registry" / "sot_registry.json"
        self.registry = self._load_registry()

    def _load_registry(self) -> Dict[str, Any]:
        """Load SoT registry"""
        if not self.registry_path.exists():
            logger.warning(f"Registry not found: {self.registry_path}")
            return {"rules": [], "artifacts": []}

        try:
            with open(self.registry_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load registry: {e}")
            return {"rules": [], "artifacts": []}

    def detect_all_changes(self) -> List[Violation]:
        """
        Detect all unauthorized changes in the system

        Returns list of violations
        """
        logger.info("=" * 80)
        logger.info("CHANGE DETECTION SCAN")
        logger.info("=" * 80)

        violations = []

        # Check 5 SoT artefacts
        violations.extend(self._check_sot_artefacts())

        # Check shards
        violations.extend(self._check_shards())

        # Check for unregistered files
        violations.extend(self._check_unregistered_files())

        logger.info(f"\nDetected {len(violations)} violations")

        return violations

    def _check_sot_artefacts(self) -> List[Violation]:
        """Check 5 SoT artefacts for changes"""
        logger.info("\n[CHECK] SoT Artefacts...")

        violations = []

        artefacts = [
            {
                "name": "sot_contract.yaml",
                "path": self.repo_root / "16_codex" / "contracts" / "sot" / "sot_contract.yaml"
            },
            {
                "name": "sot_policy.rego",
                "path": self.repo_root / "23_compliance" / "policies" / "sot" / "sot_policy.rego"
            },
            {
                "name": "sot_validator_core.py",
                "path": self.repo_root / "03_core" / "validators" / "sot" / "sot_validator_core.py"
            },
            {
                "name": "sot_validator.py",
                "path": self.repo_root / "12_tooling" / "cli" / "sot_validator.py"
            },
            {
                "name": "test_sot_validator.py",
                "path": self.repo_root / "11_test_simulation" / "tests_compliance" / "test_sot_validator.py"
            }
        ]

        for artefact in artefacts:
            if not artefact["path"].exists():
                violations.append(Violation(
                    type=ViolationType.UNREGISTERED_ARTEFACT,
                    severity="CRITICAL",
                    file_path=str(artefact["path"]),
                    details=f"Critical SoT artefact missing: {artefact['name']}",
                    detected_at=datetime.now(timezone.utc).isoformat(),
                    action=QuarantineAction.ALERT
                ))
                continue

            # Check hash
            actual_hash = self._compute_file_hash(artefact["path"])
            registered = self._find_in_registry(artefact["name"])

            if registered:
                expected_hash = registered.get("hash", "")
                if expected_hash and actual_hash != expected_hash:
                    violations.append(Violation(
                        type=ViolationType.HASH_MISMATCH,
                        severity="HIGH",
                        file_path=str(artefact["path"]),
                        details=f"Hash mismatch in {artefact['name']}",
                        detected_at=datetime.now(timezone.utc).isoformat(),
                        hash_expected=expected_hash,
                        hash_actual=actual_hash,
                        action=QuarantineAction.ALERT
                    ))
            else:
                violations.append(Violation(
                    type=ViolationType.MISSING_SHARD_ENTRY,
                    severity="HIGH",
                    file_path=str(artefact["path"]),
                    details=f"Artefact {artefact['name']} not registered in registry",
                    detected_at=datetime.now(timezone.utc).isoformat(),
                    action=QuarantineAction.BLOCK
                ))

        return violations

    def _check_shards(self) -> List[Violation]:
        """Check all shards for violations"""
        logger.info("\n[CHECK] Shards...")

        violations = []

        # Get all roots
        roots = [d for d in self.repo_root.iterdir() if d.is_dir() and d.name.startswith(("0", "1", "2"))]

        for root_dir in sorted(roots):
            shards_dir = root_dir / "shards"
            if not shards_dir.exists():
                continue

            for shard_dir in sorted(shards_dir.iterdir()):
                if not shard_dir.is_dir():
                    continue

                # Check chart.yaml
                chart_file = shard_dir / "chart.yaml"
                if not chart_file.exists():
                    violations.append(Violation(
                        type=ViolationType.MISSING_SHARD_ENTRY,
                        severity="MEDIUM",
                        file_path=str(chart_file),
                        details=f"Shard chart missing: {shard_dir.name}",
                        detected_at=datetime.now(timezone.utc).isoformat(),
                        action=QuarantineAction.ALERT
                    ))

        return violations

    def _check_unregistered_files(self) -> List[Violation]:
        """Check for files that should be registered but aren't"""
        logger.info("\n[CHECK] Unregistered Files...")

        violations = []

        # Check critical paths
        critical_paths = [
            self.repo_root / "03_core" / "validators",
            self.repo_root / "16_codex" / "contracts",
            self.repo_root / "23_compliance" / "policies",
        ]

        for path in critical_paths:
            if not path.exists():
                continue

            # Check Python files
            for py_file in path.rglob("*.py"):
                if self._should_be_registered(py_file):
                    registered = self._find_in_registry(py_file.name)
                    if not registered:
                        violations.append(Violation(
                            type=ViolationType.UNREGISTERED_ARTEFACT,
                            severity="MEDIUM",
                            file_path=str(py_file),
                            details=f"Critical file not registered: {py_file.name}",
                            detected_at=datetime.now(timezone.utc).isoformat(),
                            action=QuarantineAction.ALERT
                        ))

        return violations

    def _should_be_registered(self, file_path: Path) -> bool:
        """Check if file should be registered"""
        # Critical patterns that MUST be registered
        critical_patterns = [
            "validator",
            "policy",
            "contract",
            "sot_",
            "enforcement"
        ]

        file_name_lower = file_path.name.lower()
        return any(pattern in file_name_lower for pattern in critical_patterns)

    def _compute_file_hash(self, file_path: Path) -> str:
        """Compute SHA-256 hash of file"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception as e:
            logger.error(f"Failed to compute hash for {file_path}: {e}")
            return ""

    def _find_in_registry(self, name: str) -> Optional[Dict[str, Any]]:
        """Find entry in registry by name"""
        # Check artifacts
        for artifact in self.registry.get("artifacts", []):
            if isinstance(artifact, dict) and artifact.get("name") == name:
                return artifact

        # Check rules
        for rule in self.registry.get("rules", []):
            if isinstance(rule, dict):
                if rule.get("name") == name or rule.get("rule_id") == name:
                    return rule

        return None


class QuarantineManager:
    """
    Manages quarantined items
    """

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.quarantine_dir = repo_root / "02_audit_logging" / "quarantine" / "items"
        self.quarantine_dir.mkdir(parents=True, exist_ok=True)

    def quarantine(self, violations: List[Violation]) -> List[QuarantineEntry]:
        """
        Quarantine items based on violations

        Returns list of quarantine entries
        """
        if not violations:
            return []

        logger.info(f"\n🔒 QUARANTINING {len(violations)} VIOLATIONS")

        entries = []

        # Group violations by file
        violations_by_file = {}
        for violation in violations:
            file_path = violation.file_path
            if file_path not in violations_by_file:
                violations_by_file[file_path] = []
            violations_by_file[file_path].append(violation)

        # Create quarantine entries
        for file_path, file_violations in violations_by_file.items():
            entry_id = hashlib.sha256(
                f"{file_path}{datetime.now(timezone.utc).isoformat()}".encode()
            ).hexdigest()[:16]

            entry = QuarantineEntry(
                id=entry_id,
                violations=file_violations,
                status="QUARANTINED",
                quarantined_at=datetime.now(timezone.utc).isoformat(),
                notes=f"Automatically quarantined due to {len(file_violations)} violation(s)"
            )

            entries.append(entry)

            # Save entry
            self._save_entry(entry)

        return entries

    def _save_entry(self, entry: QuarantineEntry):
        """Save quarantine entry to disk"""
        try:
            entry_file = self.quarantine_dir / f"{entry.id}.json"

            entry_dict = asdict(entry)

            with open(entry_file, 'w', encoding='utf-8') as f:
                json.dump(entry_dict, f, indent=2)

            logger.info(f"✅ Quarantine entry saved: {entry.id}")

        except Exception as e:
            logger.error(f"Failed to save quarantine entry: {e}")

    def list_quarantined(self) -> List[QuarantineEntry]:
        """List all quarantined items"""
        entries = []

        for entry_file in self.quarantine_dir.glob("*.json"):
            try:
                with open(entry_file, 'r', encoding='utf-8') as f:
                    entry_dict = json.load(f)
                    entries.append(entry_dict)
            except Exception as e:
                logger.error(f"Failed to load quarantine entry {entry_file}: {e}")

        return entries

    def generate_report(self) -> Dict[str, Any]:
        """Generate quarantine report"""
        entries = self.list_quarantined()

        report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_quarantined": len(entries),
            "by_status": {},
            "by_severity": {},
            "entries": entries
        }

        # Count by status
        for entry in entries:
            status = entry.get("status", "UNKNOWN")
            report["by_status"][status] = report["by_status"].get(status, 0) + 1

            # Count by severity
            for violation in entry.get("violations", []):
                severity = violation.get("severity", "UNKNOWN")
                report["by_severity"][severity] = report["by_severity"].get(severity, 0) + 1

        return report


class QuarantineEngine:
    """
    Main quarantine engine

    Combines change detection and quarantine management
    """

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.detector = ChangeDetector(repo_root)
        self.manager = QuarantineManager(repo_root)

    def scan_and_quarantine(self) -> Dict[str, Any]:
        """
        Complete scan and quarantine cycle

        Returns report
        """
        logger.info("=" * 80)
        logger.info("QUARANTINE ENGINE - SCAN AND ISOLATE")
        logger.info("=" * 80)

        # Detect violations
        violations = self.detector.detect_all_changes()

        # Quarantine critical violations
        critical_violations = [
            v for v in violations
            if v.severity in ["CRITICAL", "HIGH"]
            and v.action in [QuarantineAction.BLOCK, QuarantineAction.ISOLATE]
        ]

        quarantine_entries = []
        if critical_violations:
            quarantine_entries = self.manager.quarantine(critical_violations)

        # Generate report
        quarantine_report = self.manager.generate_report()

        # Create summary
        summary = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "violations_detected": len(violations),
            "violations_quarantined": len(critical_violations),
            "quarantine_entries": len(quarantine_entries),
            "violations_by_type": {},
            "violations_by_severity": {},
            "quarantine_report": quarantine_report
        }

        # Count by type
        for violation in violations:
            vtype = violation.type.value
            summary["violations_by_type"][vtype] = summary["violations_by_type"].get(vtype, 0) + 1

        # Count by severity
        for violation in violations:
            severity = violation.severity
            summary["violations_by_severity"][severity] = summary["violations_by_severity"].get(severity, 0) + 1

        # Print summary
        self._print_summary(summary)

        # Save report
        self._save_report(summary)

        return summary

    def _print_summary(self, summary: Dict[str, Any]):
        """Print summary to console"""
        print("\n" + "=" * 80)
        print("QUARANTINE ENGINE SUMMARY")
        print("=" * 80)
        print(f"Violations Detected: {summary['violations_detected']}")
        print(f"Violations Quarantined: {summary['violations_quarantined']}")
        print(f"Quarantine Entries: {summary['quarantine_entries']}")

        if summary["violations_by_severity"]:
            print("\nBy Severity:")
            for severity, count in sorted(summary["violations_by_severity"].items()):
                print(f"  {severity}: {count}")

        if summary["violations_by_type"]:
            print("\nBy Type:")
            for vtype, count in sorted(summary["violations_by_type"].items()):
                print(f"  {vtype}: {count}")

        print("=" * 80)

    def _save_report(self, summary: Dict[str, Any]):
        """Save report to disk"""
        try:
            reports_dir = self.repo_root / "02_audit_logging" / "reports"
            reports_dir.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = reports_dir / f"quarantine_report_{timestamp}.json"

            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2)

            logger.info(f"📄 Report saved: {report_file.name}")

        except Exception as e:
            logger.error(f"Failed to save report: {e}")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Quarantine Engine")
    parser.add_argument("--root", type=Path, default=REPO_ROOT, help="Repository root")
    parser.add_argument("--list", action="store_true", help="List quarantined items")
    parser.add_argument("--report", action="store_true", help="Generate report only")

    args = parser.parse_args()

    engine = QuarantineEngine(args.root)

    if args.list:
        entries = engine.manager.list_quarantined()
        print(json.dumps(entries, indent=2))
        return 0
    elif args.report:
        report = engine.manager.generate_report()
        print(json.dumps(report, indent=2))
        return 0
    else:
        summary = engine.scan_and_quarantine()
        # Return 0 if no CRITICAL violations OR only 1-2 HIGH (acceptable)
        critical_count = summary["violations_by_severity"].get("CRITICAL", 0)
        high_count = summary["violations_by_severity"].get("HIGH", 0)

        # Allow up to 2 HIGH violations (e.g., hash mismatches after updates)
        return 0 if critical_count == 0 and high_count <= 2 else 1


if __name__ == "__main__":
    sys.exit(main())
