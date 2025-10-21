#!/usr/bin/env python3
"""
Root Forensic Audit - SSID Root-24-LOCK Forensic Analysis
Version: 2.0.0 (Forensic Edition)
Purpose: Deep forensic analysis with SHA-256 verification and integrity checking

Compliance Framework: SSID Master Definition v1.1.1
Policy: Root-24-LOCK (24 authorized root modules only)
Mode: FORENSIC (includes hash verification, deep scanning)
Cost: $0 (local analysis)
"""

import os
import sys
import hashlib
from pathlib import Path
from typing import List, Dict, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
from datetime import datetime

class ViolationSeverity(Enum):
    """Violation severity levels"""
    CRITICAL = "CRITICAL"  # Unauthorized root directory or security violation
    WARNING = "WARNING"    # Root file that should be moved
    INFO = "INFO"          # Acceptable exception

@dataclass
class FileFingerprint:
    """SHA-256 fingerprint of a file"""
    path: str
    size_bytes: int
    sha256: str
    last_modified: float

@dataclass
class RootViolation:
    """Represents a Root-24 violation with forensic data"""
    path: str
    severity: ViolationSeverity
    violation_type: str
    recommendation: str
    is_exception: bool = False
    fingerprint: FileFingerprint | None = None

class ForensicRoot24Auditor:
    """
    Forensic Root-24 Structure Auditor
    Deep analysis with SHA-256 verification and integrity checking
    """

    # Official Root-24 modules (as per SoT v1.1.1)
    AUTHORIZED_ROOTS = {
        "01_ai_layer",
        "02_audit_logging",
        "03_core",
        "04_deployment",
        "05_documentation",
        "06_data_pipeline",
        "07_governance_legal",
        "08_identity_score",
        "09_meta_identity",
        "10_interoperability",
        "11_test_simulation",
        "12_tooling",
        "13_ui_layer",
        "14_zero_time_auth",
        "15_infra",
        "16_codex",
        "17_observability",
        "18_data_layer",
        "19_adapters",
        "20_foundation",
        "21_post_quantum_crypto",
        "22_datasets",
        "23_compliance",
        "24_meta_orchestration"
    }

    # Authorized exceptions (infrastructure/config files)
    AUTHORIZED_EXCEPTIONS = {
        "LICENSE",
        "README.md",
        ".gitignore",
        ".gitattributes",
        ".pre-commit-config.yaml",
        ".git",  # Directory exception
        ".github",  # GitHub workflows and CI/CD configuration
        ".claude"  # Claude AI IDE configuration (v9.0+ permanent documented exception)
    }

    # Files that should be migrated with their target paths
    MIGRATION_CANDIDATES = {
        # Deployment docs
        "DEPLOYMENT_v5.2.md": "05_documentation/deployment/DEPLOYMENT_v5.2.md",
        "DEPLOYMENT_v5.4_Federation.md": "05_documentation/deployment/DEPLOYMENT_v5.4_Federation.md",
        "DEPLOYMENT_v6.0_Planetary_Continuum.md": "05_documentation/deployment/DEPLOYMENT_v6.0_Planetary_Continuum.md",
        "DEPLOYMENT_v8.0_Continuum_Ignition.md": "05_documentation/deployment/DEPLOYMENT_v8.0_Continuum_Ignition.md",

        # Transition docs
        "TRANSITION_v6_to_v7_DORMANT.md": "05_documentation/transitions/TRANSITION_v6_to_v7_DORMANT.md",

        # Compliance summary
        "ROOT_24_LOCK_COMPLIANCE_SUMMARY.md": "05_documentation/compliance/ROOT_24_LOCK_COMPLIANCE_SUMMARY.md"
    }

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.violations: List[RootViolation] = []
        self.file_fingerprints: Dict[str, FileFingerprint] = {}
        self.stats = {
            "critical_violations": 0,
            "warnings": 0,
            "info": 0,
            "total_root_items": 0,
            "authorized_roots": 0,
            "authorized_exceptions": 0,
            "unauthorized_items": 0,
            "total_size_bytes": 0,
            "files_scanned": 0
        }

    def calculate_sha256(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of a file"""
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                # Read in 64kb chunks
                for byte_block in iter(lambda: f.read(65536), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception as e:
            return f"ERROR: {str(e)}"

    def create_fingerprint(self, file_path: Path) -> FileFingerprint:
        """Create forensic fingerprint of a file"""
        stat = file_path.stat()
        sha256 = self.calculate_sha256(file_path)

        return FileFingerprint(
            path=str(file_path.relative_to(self.project_root)),
            size_bytes=stat.st_size,
            sha256=sha256,
            last_modified=stat.st_mtime
        )

    def scan(self) -> List[RootViolation]:
        """
        Forensic scan of project root
        Returns list of violations with fingerprints
        """
        if not self.project_root.exists():
            raise ValueError(f"Project root does not exist: {self.project_root}")

        # Get all items in project root
        root_items = [item for item in self.project_root.iterdir()]
        self.stats["total_root_items"] = len(root_items)

        for item in root_items:
            self._check_item(item)

        return self.violations

    def _check_item(self, item: Path):
        """Check a single root-level item with forensic analysis"""
        item_name = item.name

        # Check if it's an authorized root directory
        if item.is_dir() and item_name in self.AUTHORIZED_ROOTS:
            self.stats["authorized_roots"] += 1
            return

        # Check if it's an authorized exception
        if item_name in self.AUTHORIZED_EXCEPTIONS:
            self.stats["authorized_exceptions"] += 1

            # Create fingerprint for files (not directories)
            fingerprint = None
            if item.is_file():
                fingerprint = self.create_fingerprint(item)
                self.file_fingerprints[item_name] = fingerprint
                self.stats["total_size_bytes"] += fingerprint.size_bytes
                self.stats["files_scanned"] += 1

            self.violations.append(RootViolation(
                path=item_name,
                severity=ViolationSeverity.INFO,
                violation_type="Authorized Exception",
                recommendation="No action required (authorized infrastructure file)",
                is_exception=True,
                fingerprint=fingerprint
            ))
            return

        # Check if it's a known migration candidate
        if item_name in self.MIGRATION_CANDIDATES:
            self.stats["warnings"] += 1
            self.stats["unauthorized_items"] += 1

            # Create fingerprint
            fingerprint = None
            if item.is_file():
                fingerprint = self.create_fingerprint(item)
                self.file_fingerprints[item_name] = fingerprint
                self.stats["total_size_bytes"] += fingerprint.size_bytes
                self.stats["files_scanned"] += 1

            self.violations.append(RootViolation(
                path=item_name,
                severity=ViolationSeverity.WARNING,
                violation_type="Root File - Should Migrate",
                recommendation=f"Move to: {self.MIGRATION_CANDIDATES[item_name]}",
                fingerprint=fingerprint
            ))
            return

        # Unknown root-level item (CRITICAL violation)
        if item.is_dir():
            self.stats["critical_violations"] += 1
            self.stats["unauthorized_items"] += 1
            self.violations.append(RootViolation(
                path=item_name,
                severity=ViolationSeverity.CRITICAL,
                violation_type="Unauthorized Root Directory",
                recommendation=f"Remove or integrate into authorized Root-24 structure"
            ))
        else:
            self.stats["warnings"] += 1
            self.stats["unauthorized_items"] += 1

            # Create fingerprint
            fingerprint = self.create_fingerprint(item)
            self.file_fingerprints[item_name] = fingerprint
            self.stats["total_size_bytes"] += fingerprint.size_bytes
            self.stats["files_scanned"] += 1

            self.violations.append(RootViolation(
                path=item_name,
                severity=ViolationSeverity.WARNING,
                violation_type="Unauthorized Root File",
                recommendation=f"Move to appropriate module or add to exceptions",
                fingerprint=fingerprint
            ))

    def generate_forensic_report(self, output_path: Path) -> str:
        """Generate detailed forensic markdown report"""
        report_lines = [
            "# SSID Root-24 Forensic Audit Report",
            "",
            f"**Audit Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Project Root:** {self.project_root}",
            f"**Policy Version:** Root-24-LOCK v1.0",
            f"**Audit Mode:** FORENSIC (with SHA-256 verification)",
            f"**Compliance Framework:** SSID Master Definition v1.1.1",
            "",
            "---",
            "",
            "## Executive Summary",
            "",
            f"- **Total Root Items:** {self.stats['total_root_items']}",
            f"- **Authorized Roots (24):** {self.stats['authorized_roots']}",
            f"- **Authorized Exceptions:** {self.stats['authorized_exceptions']}",
            f"- **Unauthorized Items:** {self.stats['unauthorized_items']}",
            f"- **Files Scanned:** {self.stats['files_scanned']}",
            f"- **Total Size:** {self.stats['total_size_bytes']:,} bytes ({self.stats['total_size_bytes'] / 1024:.2f} KB)",
            "",
            "### Violations by Severity",
            "",
            f"- **CRITICAL:** {self.stats['critical_violations']}",
            f"- **WARNING:** {self.stats['warnings']}",
            f"- **INFO:** {self.stats['info']}",
            "",
        ]

        # Compliance status
        if self.stats['critical_violations'] == 0 and self.stats['warnings'] == 0:
            report_lines.extend([
                "### Compliance Status",
                "",
                "✅ **PASS** - Full Root-24-LOCK compliance",
                "",
            ])
        elif self.stats['critical_violations'] == 0:
            report_lines.extend([
                "### Compliance Status",
                "",
                "⚠️ **WARNING** - No critical violations, but warnings present",
                "",
            ])
        else:
            report_lines.extend([
                "### Compliance Status",
                "",
                "❌ **FAIL** - Critical violations detected",
                "",
            ])

        # Root-24 verification
        report_lines.extend([
            "---",
            "",
            "## Root-24 Module Verification",
            "",
            "### Authorized Root Modules (24)",
            ""
        ])

        for root in sorted(self.AUTHORIZED_ROOTS):
            root_path = self.project_root / root
            if root_path.exists() and root_path.is_dir():
                report_lines.append(f"- ✅ `{root}/`")
            else:
                report_lines.append(f"- ❌ `{root}/` (MISSING)")

        # Violations with fingerprints
        report_lines.extend([
            "",
            "---",
            "",
            "## Forensic Analysis: Violations with SHA-256 Fingerprints",
            ""
        ])

        critical_violations = [v for v in self.violations if v.severity == ViolationSeverity.CRITICAL]
        warning_violations = [v for v in self.violations if v.severity == ViolationSeverity.WARNING]
        info_violations = [v for v in self.violations if v.severity == ViolationSeverity.INFO]

        # CRITICAL
        if critical_violations:
            report_lines.extend([
                "### ❌ CRITICAL Violations",
                "",
                "| Path | Type | Recommendation |",
                "|------|------|----------------|"
            ])
            for v in critical_violations:
                report_lines.append(f"| `{v.path}` | {v.violation_type} | {v.recommendation} |")
            report_lines.append("")

        # WARNING with hashes
        if warning_violations:
            report_lines.extend([
                "### ⚠️ WARNING Violations (with SHA-256)",
                "",
                "| Path | Size (bytes) | SHA-256 | Target |",
                "|------|--------------|---------|--------|"
            ])
            for v in warning_violations:
                if v.fingerprint:
                    fp = v.fingerprint
                    target = self.MIGRATION_CANDIDATES.get(v.path, "N/A")
                    report_lines.append(f"| `{v.path}` | {fp.size_bytes:,} | `{fp.sha256[:16]}...` | `{target}` |")
                else:
                    report_lines.append(f"| `{v.path}` | - | - | - |")
            report_lines.append("")

        # INFO with hashes
        if info_violations:
            report_lines.extend([
                "### ℹ️ Authorized Exceptions (with SHA-256)",
                "",
                "| Path | Size (bytes) | SHA-256 |",
                "|------|--------------|---------|"
            ])
            for v in info_violations:
                if v.fingerprint:
                    fp = v.fingerprint
                    report_lines.append(f"| `{v.path}` | {fp.size_bytes:,} | `{fp.sha256[:16]}...` |")
                else:
                    report_lines.append(f"| `{v.path}` | - (directory) | - |")
            report_lines.append("")

        # Full SHA-256 table
        if self.file_fingerprints:
            report_lines.extend([
                "---",
                "",
                "## Complete SHA-256 Fingerprint Table",
                "",
                "| File | Size | SHA-256 (full) |",
                "|------|------|----------------|"
            ])
            for filename in sorted(self.file_fingerprints.keys()):
                fp = self.file_fingerprints[filename]
                report_lines.append(f"| `{filename}` | {fp.size_bytes:,} | `{fp.sha256}` |")
            report_lines.append("")

        # Migration commands
        if warning_violations:
            report_lines.extend([
                "---",
                "",
                "## Migration Plan with SHA-256 Verification",
                "",
                "```bash",
                "# Migration commands with hash verification",
                ""
            ])

            for v in warning_violations:
                if v.path in self.MIGRATION_CANDIDATES and v.fingerprint:
                    target = self.MIGRATION_CANDIDATES[v.path]
                    target_dir = str(Path(target).parent)
                    report_lines.extend([
                        f"# Migrate {v.path}",
                        f"# Current SHA-256: {v.fingerprint.sha256}",
                        f"mkdir -p {target_dir}",
                        f"mv {v.path} {target}",
                        f"# Verify: sha256sum {target}",
                        ""
                    ])

            report_lines.extend([
                "```",
                ""
            ])

        # Metadata
        report_lines.extend([
            "---",
            "",
            "## Audit Metadata",
            "",
            f"- **Auditor:** root_forensic_audit.py v2.0.0",
            f"- **Mode:** FORENSIC",
            f"- **Policy:** Root-24-LOCK",
            f"- **Hash Algorithm:** SHA-256",
            f"- **Files Hashed:** {self.stats['files_scanned']}",
            f"- **Total Data Analyzed:** {self.stats['total_size_bytes']:,} bytes",
            f"- **Cost:** $0 (local analysis)",
            f"- **Reproducible:** Yes (deterministic hashing)",
            "",
            "**END OF FORENSIC REPORT**"
        ])

        # Write report
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))

        return str(output_path)

    def generate_json_summary(self, output_path: Path) -> str:
        """Generate JSON summary with forensic data"""
        summary = {
            "audit_date": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "policy_version": "Root-24-LOCK v1.0",
            "audit_mode": "FORENSIC",
            "statistics": self.stats,
            "compliance_status": "PASS" if self.stats['critical_violations'] == 0 and self.stats['warnings'] == 0 else "FAIL",
            "violations": [
                {
                    "path": v.path,
                    "severity": v.severity.value,
                    "type": v.violation_type,
                    "recommendation": v.recommendation,
                    "is_exception": v.is_exception,
                    "fingerprint": {
                        "size_bytes": v.fingerprint.size_bytes,
                        "sha256": v.fingerprint.sha256,
                        "last_modified": v.fingerprint.last_modified
                    } if v.fingerprint else None
                }
                for v in self.violations
            ],
            "file_fingerprints": {
                filename: {
                    "path": fp.path,
                    "size_bytes": fp.size_bytes,
                    "sha256": fp.sha256,
                    "last_modified": fp.last_modified
                }
                for filename, fp in self.file_fingerprints.items()
            }
        }

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)

        return str(output_path)

def main():
    """Main execution"""
    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    print("=" * 70)
    print("SSID Root-24 Forensic Audit")
    print("=" * 70)
    print(f"Project Root: {project_root}")
    print(f"Mode: FORENSIC (SHA-256 verification)")
    print(f"Policy: Root-24-LOCK v1.0")
    print()

    # Create auditor
    auditor = ForensicRoot24Auditor(project_root)

    # Scan
    print("Performing forensic scan...")
    violations = auditor.scan()

    # Display results
    print(f"\nForensic Scan Complete:")
    print(f"  Total Items: {auditor.stats['total_root_items']}")
    print(f"  Authorized Roots: {auditor.stats['authorized_roots']}/24")
    print(f"  Files Scanned: {auditor.stats['files_scanned']}")
    print(f"  Total Size: {auditor.stats['total_size_bytes']:,} bytes")
    print(f"  Violations: {auditor.stats['unauthorized_items']}")
    print(f"    - Critical: {auditor.stats['critical_violations']}")
    print(f"    - Warning: {auditor.stats['warnings']}")
    print()

    # Generate reports
    report_path = project_root / "02_audit_logging" / "reports" / "root_forensic_audit_report.md"
    json_path = project_root / "02_audit_logging" / "reports" / "root_forensic_audit_summary.json"

    print("Generating forensic reports...")
    md_report = auditor.generate_forensic_report(report_path)
    json_summary = auditor.generate_json_summary(json_path)

    print(f"  Markdown Report: {md_report}")
    print(f"  JSON Summary: {json_summary}")
    print()

    # Exit code based on compliance
    if auditor.stats['critical_violations'] > 0:
        print("AUDIT FAILED - Critical violations detected")
        sys.exit(1)
    elif auditor.stats['warnings'] > 0:
        print("AUDIT WARNING - Warnings present, migration recommended")
        sys.exit(0)
    else:
        print("AUDIT PASSED - Full Root-24 compliance")
        sys.exit(0)

if __name__ == "__main__":
    main()
