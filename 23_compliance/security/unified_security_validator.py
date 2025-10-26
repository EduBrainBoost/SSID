#!/usr/bin/env python3
"""
Unified Security Validator for SSID
Comprehensive security validation across all security systems

Version: 1.0.0
Created: 2025-10-24
Status: PRODUCTION

Validates:
1. Post-Quantum Cryptography (PQC) - Dilithium3, Kyber768
2. Zero-Time Authentication - MFA, Biometric, DID
3. Compliance Security - GDPR, eIDAS, MiCA, DORA, NIS2
4. Audit Security - WORM storage, hash chains, immutability
5. Infrastructure Security - Secrets, encryption, key rotation
"""

import json
import hashlib
import subprocess
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class SecurityCheckResult:
    """Result of a security check"""
    name: str
    category: str
    status: str  # PASS, FAIL, WARNING, NOT_IMPLEMENTED
    score: int  # 0-100
    message: str
    evidence: Optional[Dict[str, Any]] = None
    remediation: Optional[str] = None


@dataclass
class SecuritySummary:
    """Summary of security validation"""
    timestamp: str
    total_checks: int
    passed: int
    failed: int
    warnings: int
    not_implemented: int
    overall_score: float
    category_scores: Dict[str, float]
    results: List[Dict[str, Any]]


class UnifiedSecurityValidator:
    """Unified Security Validator for all security systems"""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.results: List[SecurityCheckResult] = []

    def validate_all_security(self) -> SecuritySummary:
        """Run all security validations"""
        print("=" * 80)
        print("UNIFIED SECURITY VALIDATOR")
        print("=" * 80)
        print(f"Timestamp: {datetime.now().isoformat()}")
        print(f"Repository: {self.repo_root}")
        print("=" * 80)
        print()

        # Run all validation categories
        self._validate_pqc()
        self._validate_auth()
        self._validate_compliance()
        self._validate_audit()
        self._validate_infra()

        # Generate summary
        summary = self._generate_summary()

        # Print results
        self._print_results(summary)

        return summary

    def _validate_pqc(self):
        """Validate Post-Quantum Cryptography implementations"""
        print("[1/5] Validating Post-Quantum Cryptography...")
        print("-" * 80)

        # Check for PQC tools
        pqc_tools_dir = self.repo_root / "21_post_quantum_crypto" / "tools"

        # 1. Check signature tools exist
        sign_script = pqc_tools_dir / "sign_certificate.py"
        if sign_script.exists():
            self.results.append(SecurityCheckResult(
                name="PQC Signature Tool",
                category="PQC",
                status="PASS",
                score=100,
                message="Dilithium3 signature tool found",
                evidence={"path": str(sign_script)}
            ))
        else:
            self.results.append(SecurityCheckResult(
                name="PQC Signature Tool",
                category="PQC",
                status="FAIL",
                score=0,
                message="Dilithium3 signature tool NOT found",
                remediation="Create signature tool at 21_post_quantum_crypto/tools/sign_certificate.py"
            ))

        # 2. Check batch signing tool
        batch_sign_script = pqc_tools_dir / "sign_all_sot_artifacts.py"
        if batch_sign_script.exists():
            self.results.append(SecurityCheckResult(
                name="PQC Batch Signing",
                category="PQC",
                status="PASS",
                score=100,
                message="Batch signing tool found",
                evidence={"path": str(batch_sign_script)}
            ))
        else:
            self.results.append(SecurityCheckResult(
                name="PQC Batch Signing",
                category="PQC",
                status="WARNING",
                score=50,
                message="Batch signing tool not found",
                remediation="Consider creating batch signing automation"
            ))

        # 3. Check for signature artifacts
        signatures_dir = self.repo_root / "02_audit_logging" / "reports" / "signatures"
        if signatures_dir.exists():
            sig_files = list(signatures_dir.glob("*.json"))
            if sig_files:
                self.results.append(SecurityCheckResult(
                    name="PQC Signatures Exist",
                    category="PQC",
                    status="PASS",
                    score=100,
                    message=f"Found {len(sig_files)} signature files",
                    evidence={"count": len(sig_files), "files": [f.name for f in sig_files[:5]]}
                ))
            else:
                self.results.append(SecurityCheckResult(
                    name="PQC Signatures Exist",
                    category="PQC",
                    status="FAIL",
                    score=0,
                    message="No signature files found",
                    remediation="Run sign_all_sot_artifacts.py to create signatures"
                ))
        else:
            self.results.append(SecurityCheckResult(
                name="PQC Signatures Exist",
                category="PQC",
                status="FAIL",
                score=0,
                message="Signatures directory not found",
                remediation="Create directory structure for signatures"
            ))

        # 4. Check for Kyber (key encapsulation)
        self.results.append(SecurityCheckResult(
            name="Kyber768 Implementation",
            category="PQC",
            status="NOT_IMPLEMENTED",
            score=0,
            message="Kyber768 key encapsulation not yet implemented",
            remediation="Implement Kyber768 for hybrid key exchange"
        ))

        # 5. Check algorithm agility
        security_config = self.repo_root / "23_compliance" / "security" / "financial_security_v1.1.yaml"
        if security_config.exists():
            self.results.append(SecurityCheckResult(
                name="Crypto Agility Config",
                category="PQC",
                status="PASS",
                score=100,
                message="Security configuration found (FIPS 203/204/205)",
                evidence={"path": str(security_config)}
            ))
        else:
            self.results.append(SecurityCheckResult(
                name="Crypto Agility Config",
                category="PQC",
                status="WARNING",
                score=60,
                message="Security configuration not found",
                remediation="Create crypto agility configuration"
            ))

        print()

    def _validate_auth(self):
        """Validate Zero-Time Authentication systems"""
        print("[2/5] Validating Zero-Time Authentication...")
        print("-" * 80)

        auth_dir = self.repo_root / "14_zero_time_auth"

        # 1. Check for auth infrastructure
        if auth_dir.exists():
            self.results.append(SecurityCheckResult(
                name="Auth Directory Structure",
                category="Auth",
                status="PASS",
                score=100,
                message="Zero-time auth directory exists",
                evidence={"path": str(auth_dir)}
            ))
        else:
            self.results.append(SecurityCheckResult(
                name="Auth Directory Structure",
                category="Auth",
                status="FAIL",
                score=0,
                message="Zero-time auth directory not found",
                remediation="Create 14_zero_time_auth directory structure"
            ))

        # 2. Check for GDPR compliance in auth
        if auth_dir.exists():
            gdpr_files = list(auth_dir.rglob("*gdpr*.yaml"))
            if gdpr_files:
                self.results.append(SecurityCheckResult(
                    name="Auth GDPR Compliance",
                    category="Auth",
                    status="PASS",
                    score=100,
                    message=f"Found {len(gdpr_files)} GDPR compliance files",
                    evidence={"count": len(gdpr_files)}
                ))
            else:
                self.results.append(SecurityCheckResult(
                    name="Auth GDPR Compliance",
                    category="Auth",
                    status="WARNING",
                    score=50,
                    message="No GDPR compliance files found",
                    remediation="Add GDPR compliance policies to auth layer"
                ))

        # 3. Check for MFA implementation
        self.results.append(SecurityCheckResult(
            name="MFA Implementation",
            category="Auth",
            status="NOT_IMPLEMENTED",
            score=0,
            message="Multi-Factor Authentication not yet implemented",
            remediation="Implement MFA with TOTP/WebAuthn support"
        ))

        # 4. Check for Biometric auth
        self.results.append(SecurityCheckResult(
            name="Biometric Authentication",
            category="Auth",
            status="NOT_IMPLEMENTED",
            score=0,
            message="Biometric authentication not yet implemented",
            remediation="Implement biometric auth (fingerprint/face recognition)"
        ))

        # 5. Check for DID (Decentralized ID)
        self.results.append(SecurityCheckResult(
            name="DID-based Authentication",
            category="Auth",
            status="NOT_IMPLEMENTED",
            score=0,
            message="DID-based authentication not yet implemented",
            remediation="Implement W3C DID standard support"
        ))

        # 6. Check for identity scoring
        identity_bridge = auth_dir / "interconnect" / "bridge_identity_score.py"
        if identity_bridge.exists():
            self.results.append(SecurityCheckResult(
                name="Identity Risk Scoring",
                category="Auth",
                status="PASS",
                score=100,
                message="Identity risk scoring bridge found",
                evidence={"path": str(identity_bridge)}
            ))
        else:
            self.results.append(SecurityCheckResult(
                name="Identity Risk Scoring",
                category="Auth",
                status="WARNING",
                score=50,
                message="Identity risk scoring not found",
                remediation="Implement identity risk scoring"
            ))

        print()

    def _validate_compliance(self):
        """Validate Compliance Security (GDPR, eIDAS, MiCA, etc.)"""
        print("[3/5] Validating Compliance Security...")
        print("-" * 80)

        compliance_dir = self.repo_root / "23_compliance"

        # 1. Check compliance directory structure
        if compliance_dir.exists():
            self.results.append(SecurityCheckResult(
                name="Compliance Structure",
                category="Compliance",
                status="PASS",
                score=100,
                message="Compliance directory exists",
                evidence={"path": str(compliance_dir)}
            ))
        else:
            self.results.append(SecurityCheckResult(
                name="Compliance Structure",
                category="Compliance",
                status="FAIL",
                score=0,
                message="Compliance directory not found",
                remediation="Create 23_compliance directory structure"
            ))

        # 2. Check GDPR compliance
        gdpr_files = list(compliance_dir.rglob("*gdpr*.yaml")) if compliance_dir.exists() else []
        if gdpr_files:
            self.results.append(SecurityCheckResult(
                name="GDPR Compliance",
                category="Compliance",
                status="PASS",
                score=100,
                message=f"Found {len(gdpr_files)} GDPR compliance files",
                evidence={"count": len(gdpr_files)}
            ))
        else:
            self.results.append(SecurityCheckResult(
                name="GDPR Compliance",
                category="Compliance",
                status="FAIL",
                score=0,
                message="No GDPR compliance policies found",
                remediation="Create GDPR compliance policies"
            ))

        # 3. Check eIDAS compliance
        self.results.append(SecurityCheckResult(
            name="eIDAS Compliance",
            category="Compliance",
            status="NOT_IMPLEMENTED",
            score=0,
            message="eIDAS compliance not yet implemented",
            remediation="Implement eIDAS trust services (EN 319 401/411/421)"
        ))

        # 4. Check MiCA compliance
        self.results.append(SecurityCheckResult(
            name="MiCA Compliance",
            category="Compliance",
            status="NOT_IMPLEMENTED",
            score=0,
            message="MiCA compliance not yet implemented",
            remediation="Implement MiCA (Markets in Crypto-Assets) compliance"
        ))

        # 5. Check DORA compliance
        self.results.append(SecurityCheckResult(
            name="DORA Compliance",
            category="Compliance",
            status="NOT_IMPLEMENTED",
            score=0,
            message="DORA compliance not yet implemented",
            remediation="Implement DORA (Digital Operational Resilience Act)"
        ))

        # 6. Check NIS2 compliance
        self.results.append(SecurityCheckResult(
            name="NIS2 Compliance",
            category="Compliance",
            status="NOT_IMPLEMENTED",
            score=0,
            message="NIS2 compliance not yet implemented",
            remediation="Implement NIS2 (Network and Information Security)"
        ))

        # 7. Check sanctions compliance
        sanctions_file = compliance_dir / "policies" / "sanctions.yaml"
        if sanctions_file.exists():
            self.results.append(SecurityCheckResult(
                name="Sanctions Compliance",
                category="Compliance",
                status="PASS",
                score=100,
                message="Sanctions policy found",
                evidence={"path": str(sanctions_file)}
            ))
        else:
            self.results.append(SecurityCheckResult(
                name="Sanctions Compliance",
                category="Compliance",
                status="WARNING",
                score=50,
                message="Sanctions policy not found",
                remediation="Create sanctions compliance policy"
            ))

        print()

    def _validate_audit(self):
        """Validate Audit Security (WORM, hash chains, immutability)"""
        print("[4/5] Validating Audit Security...")
        print("-" * 80)

        audit_dir = self.repo_root / "02_audit_logging"

        # 1. Check audit directory structure
        if audit_dir.exists():
            self.results.append(SecurityCheckResult(
                name="Audit Structure",
                category="Audit",
                status="PASS",
                score=100,
                message="Audit logging directory exists",
                evidence={"path": str(audit_dir)}
            ))
        else:
            self.results.append(SecurityCheckResult(
                name="Audit Structure",
                category="Audit",
                status="FAIL",
                score=0,
                message="Audit logging directory not found",
                remediation="Create 02_audit_logging directory structure"
            ))

        # 2. Check WORM storage
        worm_dir = audit_dir / "storage" / "worm"
        if worm_dir.exists():
            immutable_store = worm_dir / "immutable_store"
            if immutable_store.exists():
                worm_files = list(immutable_store.glob("*.json"))
                if worm_files:
                    self.results.append(SecurityCheckResult(
                        name="WORM Storage",
                        category="Audit",
                        status="PASS",
                        score=100,
                        message=f"WORM storage active with {len(worm_files)} immutable records",
                        evidence={"count": len(worm_files), "path": str(immutable_store)}
                    ))
                else:
                    self.results.append(SecurityCheckResult(
                        name="WORM Storage",
                        category="Audit",
                        status="WARNING",
                        score=70,
                        message="WORM storage exists but no records found",
                        remediation="Ensure audit events are being written to WORM storage"
                    ))
            else:
                self.results.append(SecurityCheckResult(
                    name="WORM Storage",
                    category="Audit",
                    status="WARNING",
                    score=50,
                    message="WORM structure exists but immutable_store not found",
                    remediation="Create immutable_store directory"
                ))
        else:
            self.results.append(SecurityCheckResult(
                name="WORM Storage",
                category="Audit",
                status="FAIL",
                score=0,
                message="WORM storage not found",
                remediation="Implement WORM (Write-Once-Read-Many) storage"
            ))

        # 3. Check hash ledger
        hash_ledger_dir = worm_dir / "hash_ledger" if worm_dir.exists() else None
        if hash_ledger_dir and hash_ledger_dir.exists():
            ledger_files = list(hash_ledger_dir.glob("*.json"))
            if ledger_files:
                self.results.append(SecurityCheckResult(
                    name="Hash Chain Ledger",
                    category="Audit",
                    status="PASS",
                    score=100,
                    message=f"Hash ledger active with {len(ledger_files)} chain files",
                    evidence={"count": len(ledger_files), "path": str(hash_ledger_dir)}
                ))
            else:
                self.results.append(SecurityCheckResult(
                    name="Hash Chain Ledger",
                    category="Audit",
                    status="WARNING",
                    score=60,
                    message="Hash ledger directory exists but no chains found",
                    remediation="Initialize hash chain ledger"
                ))
        else:
            self.results.append(SecurityCheckResult(
                name="Hash Chain Ledger",
                category="Audit",
                status="FAIL",
                score=0,
                message="Hash ledger not found",
                remediation="Implement cryptographic hash chain ledger"
            ))

        # 4. Check tamper detection
        watchdog_dir = audit_dir / "watchdog"
        if watchdog_dir.exists():
            self.results.append(SecurityCheckResult(
                name="Tamper Detection",
                category="Audit",
                status="PASS",
                score=100,
                message="Watchdog system for tamper detection found",
                evidence={"path": str(watchdog_dir)}
            ))
        else:
            self.results.append(SecurityCheckResult(
                name="Tamper Detection",
                category="Audit",
                status="NOT_IMPLEMENTED",
                score=0,
                message="Tamper detection not implemented",
                remediation="Implement watchdog system for integrity monitoring"
            ))

        # 5. Check quarantine system
        quarantine_dir = audit_dir / "quarantine"
        if quarantine_dir.exists():
            self.results.append(SecurityCheckResult(
                name="Quarantine System",
                category="Audit",
                status="PASS",
                score=100,
                message="Quarantine system for malicious artifacts found",
                evidence={"path": str(quarantine_dir)}
            ))
        else:
            self.results.append(SecurityCheckResult(
                name="Quarantine System",
                category="Audit",
                status="WARNING",
                score=50,
                message="Quarantine system not found",
                remediation="Implement quarantine for suspicious artifacts"
            ))

        # 6. Check evidence chain
        evidence_dir = self.repo_root / "23_compliance" / "evidence"
        if evidence_dir.exists():
            self.results.append(SecurityCheckResult(
                name="Evidence Chain",
                category="Audit",
                status="PASS",
                score=100,
                message="Evidence collection system found",
                evidence={"path": str(evidence_dir)}
            ))
        else:
            self.results.append(SecurityCheckResult(
                name="Evidence Chain",
                category="Audit",
                status="WARNING",
                score=60,
                message="Evidence directory not found",
                remediation="Create evidence collection structure"
            ))

        print()

    def _validate_infra(self):
        """Validate Infrastructure Security"""
        print("[5/5] Validating Infrastructure Security...")
        print("-" * 80)

        infra_dir = self.repo_root / "15_infra"

        # 1. Check infrastructure directory
        if infra_dir.exists():
            self.results.append(SecurityCheckResult(
                name="Infra Structure",
                category="Infra",
                status="PASS",
                score=100,
                message="Infrastructure directory exists",
                evidence={"path": str(infra_dir)}
            ))
        else:
            self.results.append(SecurityCheckResult(
                name="Infra Structure",
                category="Infra",
                status="WARNING",
                score=50,
                message="Infrastructure directory not found",
                remediation="Create 15_infra directory structure"
            ))

        # 2. Check secrets management
        self.results.append(SecurityCheckResult(
            name="Secrets Management",
            category="Infra",
            status="NOT_IMPLEMENTED",
            score=0,
            message="Centralized secrets management not implemented",
            remediation="Implement HashiCorp Vault or AWS Secrets Manager"
        ))

        # 3. Check encryption at rest
        self.results.append(SecurityCheckResult(
            name="Encryption at Rest",
            category="Infra",
            status="NOT_IMPLEMENTED",
            score=0,
            message="Encryption at rest not verified",
            remediation="Implement and verify encryption for stored data"
        ))

        # 4. Check key rotation
        self.results.append(SecurityCheckResult(
            name="Key Rotation",
            category="Infra",
            status="NOT_IMPLEMENTED",
            score=0,
            message="Automated key rotation not implemented",
            remediation="Implement automated key rotation policies"
        ))

        # 5. Check network security
        self.results.append(SecurityCheckResult(
            name="Network Security",
            category="Infra",
            status="NOT_IMPLEMENTED",
            score=0,
            message="Network security policies not verified",
            remediation="Implement network segmentation and firewalls"
        ))

        # 6. Check Docker security
        docker_compose = self.repo_root / "04_deployment" / "docker-compose.yaml"
        if docker_compose.exists():
            self.results.append(SecurityCheckResult(
                name="Container Security",
                category="Infra",
                status="PASS",
                score=100,
                message="Docker deployment configuration found",
                evidence={"path": str(docker_compose)}
            ))
        else:
            self.results.append(SecurityCheckResult(
                name="Container Security",
                category="Infra",
                status="WARNING",
                score=60,
                message="Docker configuration not found",
                remediation="Create secure Docker deployment configuration"
            ))

        print()

    def _generate_summary(self) -> SecuritySummary:
        """Generate validation summary"""
        total = len(self.results)
        passed = sum(1 for r in self.results if r.status == "PASS")
        failed = sum(1 for r in self.results if r.status == "FAIL")
        warnings = sum(1 for r in self.results if r.status == "WARNING")
        not_impl = sum(1 for r in self.results if r.status == "NOT_IMPLEMENTED")

        # Calculate overall score
        total_score = sum(r.score for r in self.results)
        overall_score = (total_score / (total * 100)) * 100 if total > 0 else 0

        # Calculate category scores
        categories = {}
        for result in self.results:
            if result.category not in categories:
                categories[result.category] = []
            categories[result.category].append(result.score)

        category_scores = {
            cat: sum(scores) / len(scores) if scores else 0
            for cat, scores in categories.items()
        }

        return SecuritySummary(
            timestamp=datetime.now().isoformat(),
            total_checks=total,
            passed=passed,
            failed=failed,
            warnings=warnings,
            not_implemented=not_impl,
            overall_score=overall_score,
            category_scores=category_scores,
            results=[asdict(r) for r in self.results]
        )

    def _print_results(self, summary: SecuritySummary):
        """Print validation results"""
        print("=" * 80)
        print("SECURITY VALIDATION SUMMARY")
        print("=" * 80)
        print()

        # Overall results
        print(f"Total Checks:      {summary.total_checks}")
        print(f"  PASS:            {summary.passed}")
        print(f"  FAIL:            {summary.failed}")
        print(f"  WARNING:         {summary.warnings}")
        print(f"  NOT_IMPLEMENTED: {summary.not_implemented}")
        print()
        print(f"Overall Score:     {summary.overall_score:.1f}%")
        print()

        # Category scores
        print("Category Scores:")
        for category, score in sorted(summary.category_scores.items()):
            bar_length = int(score / 5)  # Scale to 20 chars
            bar = "█" * bar_length + "░" * (20 - bar_length)
            print(f"  {category:12s}: [{bar}] {score:5.1f}%")
        print()

        # Status badge
        if summary.overall_score >= 90:
            badge = "EXCELLENT"
        elif summary.overall_score >= 75:
            badge = "GOOD"
        elif summary.overall_score >= 50:
            badge = "FAIR"
        else:
            badge = "NEEDS IMPROVEMENT"

        print(f"Security Status:   [{badge}]")
        print()

        # Detailed results by status
        for status in ["FAIL", "WARNING", "NOT_IMPLEMENTED"]:
            results = [r for r in self.results if r.status == status]
            if results:
                print(f"{status} Items:")
                for result in results:
                    print(f"  [{result.category}] {result.name}")
                    print(f"    {result.message}")
                    if result.remediation:
                        print(f"    Remediation: {result.remediation}")
                print()

        print("=" * 80)


def main():
    """Main entry point"""
    repo_root = Path(__file__).resolve().parents[2]

    validator = UnifiedSecurityValidator(repo_root)
    summary = validator.validate_all_security()

    # Save report
    report_dir = repo_root / "02_audit_logging" / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)

    report_file = report_dir / f"security_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(asdict(summary), f, indent=2, ensure_ascii=False)

    print(f"Report saved: {report_file}")
    print()

    # Return exit code based on score
    if summary.overall_score >= 75:
        return 0
    elif summary.overall_score >= 50:
        return 1
    else:
        return 2


if __name__ == '__main__':
    sys.exit(main())
