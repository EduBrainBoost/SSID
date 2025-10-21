#!/usr/bin/env python3
"""
SOC2 CC1.1 - COSO Integrity & Ethics Control
==============================================

Scientific Basis:
-----------------
AICPA TSC CC1.1 - The entity demonstrates a commitment to integrity and ethical values.
Based on COSO Internal Control Framework (2013) Principle 1.

Technical Manifestation:
------------------------
This module validates that the organization has documented integrity and ethical standards,
including code of conduct, conflict of interest policies, and ethical violation reporting mechanisms.

SoT Compliance Requirements:
- Must have documented code of conduct
- Must have conflict of interest policy
- Must have ethics violation reporting mechanism
- Must evidence annual ethics training
- Must maintain ethics violation log (WORM storage)

Evidence Chain:
- Code of Conduct: 07_governance_legal/policies/code_of_conduct.md
- Ethics Policy: 07_governance_legal/policies/ethics_policy.md
- Training Records: 07_governance_legal/training/ethics_training_log.json
- Violation Log: 02_audit_logging/storage/worm/immutable_store/ethics_violations.jsonl

Author: SSID Compliance Team
Version: 1.0.0
Date: 2025-10-17
"""

import json
import hashlib
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class CC11IntegrityEthicsValidator:
    """
    Validates SOC2 CC1.1 compliance - Integrity and Ethical Values
    """

    REQUIRED_DOCUMENTS = {
        "code_of_conduct": "07_governance_legal/policies/code_of_conduct.md",
        "ethics_policy": "07_governance_legal/policies/ethics_policy.md",
        "conflict_of_interest": "07_governance_legal/policies/conflict_of_interest_policy.md",
        "whistleblower_policy": "07_governance_legal/policies/whistleblower_policy.md"
    }

    EVIDENCE_PATHS = {
        "training_log": "07_governance_legal/training/ethics_training_log.json",
        "violation_log": "02_audit_logging/storage/worm/immutable_store/ethics_violations.jsonl",
        "acknowledgment_log": "07_governance_legal/training/code_conduct_acknowledgments.json"
    }

    # Minimum 80% of personnel must complete annual ethics training
    TRAINING_COMPLIANCE_THRESHOLD = 0.80

    def __init__(self, repo_root: Optional[Path] = None):
        """Initialize validator with repository root path"""
        self.repo_root = repo_root or Path.cwd()
        self.findings: List[Dict] = []
        self.is_compliant = False

    def validate(self) -> Tuple[bool, List[Dict]]:
        """
        Execute full CC1.1 validation

        Returns:
            Tuple of (is_compliant: bool, findings: List[Dict])
        """
        self.findings = []

        # Step 1: Validate required policy documents exist
        policies_valid = self._validate_policy_documents()

        # Step 2: Validate training completion
        training_valid = self._validate_ethics_training()

        # Step 3: Validate violation reporting mechanism
        reporting_valid = self._validate_violation_reporting()

        # Step 4: Validate code of conduct acknowledgments
        acknowledgment_valid = self._validate_acknowledgments()

        # Overall compliance
        self.is_compliant = all([
            policies_valid,
            training_valid,
            reporting_valid,
            acknowledgment_valid
        ])

        return self.is_compliant, self.findings

    def _validate_policy_documents(self) -> bool:
        """Validate all required policy documents exist and are non-empty"""
        all_valid = True

        for doc_type, rel_path in self.REQUIRED_DOCUMENTS.items():
            full_path = self.repo_root / rel_path

            if not full_path.exists():
                self.findings.append({
                    "rule": "CC1.1",
                    "severity": "CRITICAL",
                    "finding": f"Missing required document: {doc_type}",
                    "path": rel_path,
                    "remediation": f"Create {doc_type} policy document at {rel_path}"
                })
                all_valid = False
                continue

            # Validate document is not empty (minimum 100 chars)
            content_size = full_path.stat().st_size
            if content_size < 100:
                self.findings.append({
                    "rule": "CC1.1",
                    "severity": "HIGH",
                    "finding": f"Policy document too short: {doc_type} ({content_size} bytes)",
                    "path": rel_path,
                    "remediation": f"Policy must contain substantive content (min 100 bytes)"
                })
                all_valid = False
            else:
                self.findings.append({
                    "rule": "CC1.1",
                    "severity": "INFO",
                    "finding": f"Valid policy document: {doc_type} ({content_size} bytes)",
                    "path": rel_path,
                    "status": "PASS"
                })

        return all_valid

    def _validate_ethics_training(self) -> bool:
        """Validate ethics training completion rates"""
        training_log_path = self.repo_root / self.EVIDENCE_PATHS["training_log"]

        if not training_log_path.exists():
            self.findings.append({
                "rule": "CC1.1",
                "severity": "CRITICAL",
                "finding": "Missing ethics training log",
                "path": self.EVIDENCE_PATHS["training_log"],
                "remediation": "Create ethics training tracking system"
            })
            return False

        try:
            with open(training_log_path, 'r', encoding='utf-8') as f:
                training_data = json.load(f)

            # Check training within last 365 days
            cutoff_date = datetime.now() - timedelta(days=365)
            total_personnel = training_data.get("total_personnel", 0)
            completed_training = []

            for record in training_data.get("training_records", []):
                completion_date = datetime.fromisoformat(record.get("completion_date", "1970-01-01"))
                if completion_date >= cutoff_date:
                    completed_training.append(record)

            if total_personnel == 0:
                self.findings.append({
                    "rule": "CC1.1",
                    "severity": "WARNING",
                    "finding": "No personnel recorded in training system",
                    "remediation": "Initialize personnel roster in training log"
                })
                return False

            compliance_rate = len(completed_training) / total_personnel

            if compliance_rate >= self.TRAINING_COMPLIANCE_THRESHOLD:
                self.findings.append({
                    "rule": "CC1.1",
                    "severity": "INFO",
                    "finding": f"Ethics training compliance: {compliance_rate:.1%} (threshold: {self.TRAINING_COMPLIANCE_THRESHOLD:.0%})",
                    "status": "PASS"
                })
                return True
            else:
                self.findings.append({
                    "rule": "CC1.1",
                    "severity": "HIGH",
                    "finding": f"Ethics training compliance below threshold: {compliance_rate:.1%} < {self.TRAINING_COMPLIANCE_THRESHOLD:.0%}",
                    "remediation": f"Complete training for {int((self.TRAINING_COMPLIANCE_THRESHOLD - compliance_rate) * total_personnel)} additional personnel"
                })
                return False

        except json.JSONDecodeError as e:
            self.findings.append({
                "rule": "CC1.1",
                "severity": "CRITICAL",
                "finding": f"Invalid JSON in training log: {e}",
                "remediation": "Fix JSON syntax in training log"
            })
            return False

    def _validate_violation_reporting(self) -> bool:
        """Validate ethics violation reporting mechanism exists"""
        violation_log_path = self.repo_root / self.EVIDENCE_PATHS["violation_log"]

        # WORM storage directory must exist even if no violations reported
        worm_dir = violation_log_path.parent
        if not worm_dir.exists():
            self.findings.append({
                "rule": "CC1.1",
                "severity": "CRITICAL",
                "finding": "WORM storage for ethics violations not configured",
                "path": str(worm_dir),
                "remediation": "Initialize WORM-compliant ethics violation logging"
            })
            return False

        # Log file can be empty if no violations
        if violation_log_path.exists():
            line_count = sum(1 for _ in open(violation_log_path, 'r', encoding='utf-8'))
            self.findings.append({
                "rule": "CC1.1",
                "severity": "INFO",
                "finding": f"Ethics violation log exists ({line_count} entries)",
                "status": "PASS"
            })
        else:
            # Create empty WORM log
            violation_log_path.touch()
            self.findings.append({
                "rule": "CC1.1",
                "severity": "INFO",
                "finding": "Initialized empty ethics violation log",
                "status": "PASS"
            })

        return True

    def _validate_acknowledgments(self) -> bool:
        """Validate code of conduct acknowledgments"""
        ack_log_path = self.repo_root / self.EVIDENCE_PATHS["acknowledgment_log"]

        if not ack_log_path.exists():
            self.findings.append({
                "rule": "CC1.1",
                "severity": "HIGH",
                "finding": "No code of conduct acknowledgment log",
                "remediation": "Implement code of conduct acknowledgment tracking"
            })
            return False

        try:
            with open(ack_log_path, 'r', encoding='utf-8') as f:
                ack_data = json.load(f)

            ack_count = len(ack_data.get("acknowledgments", []))

            if ack_count == 0:
                self.findings.append({
                    "rule": "CC1.1",
                    "severity": "WARNING",
                    "finding": "No code of conduct acknowledgments recorded",
                    "remediation": "Obtain signed acknowledgments from all personnel"
                })
                return False

            self.findings.append({
                "rule": "CC1.1",
                "severity": "INFO",
                "finding": f"Code of conduct acknowledgments: {ack_count} personnel",
                "status": "PASS"
            })
            return True

        except json.JSONDecodeError:
            self.findings.append({
                "rule": "CC1.1",
                "severity": "CRITICAL",
                "finding": "Invalid JSON in acknowledgment log",
                "remediation": "Fix JSON syntax"
            })
            return False

    def generate_evidence_hash(self) -> str:
        """Generate SHA-256 hash of all evidence for audit trail"""
        evidence_data = {
            "timestamp": datetime.now().isoformat(),
            "rule": "SOC2_CC1.1",
            "findings": self.findings,
            "is_compliant": self.is_compliant
        }

        evidence_json = json.dumps(evidence_data, sort_keys=True)
        return hashlib.sha256(evidence_json.encode()).hexdigest()


def cli_check() -> int:
    """CLI entry point for CC1.1 validation"""
    validator = CC11IntegrityEthicsValidator()
    is_compliant, findings = validator.validate()

    print(f"\n{'='*80}")
    print(f"SOC2 CC1.1 - Integrity & Ethical Values Validation")
    print(f"{'='*80}\n")

    for finding in findings:
        severity = finding.get("severity", "INFO")
        icon = "✓" if finding.get("status") == "PASS" else "✗" if severity in ["CRITICAL", "HIGH"] else "⚠"
        print(f"{icon} [{severity}] {finding.get('finding')}")
        if "remediation" in finding:
            print(f"  → Remediation: {finding['remediation']}")
        print()

    print(f"{'='*80}")
    print(f"Overall Compliance: {'PASS ✓' if is_compliant else 'FAIL ✗'}")
    print(f"Evidence Hash: {validator.generate_evidence_hash()}")
    print(f"{'='*80}\n")

    return 0 if is_compliant else 1


if __name__ == "__main__":
    exit(cli_check())
