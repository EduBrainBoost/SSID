#!/usr/bin/env python3
"""
Root Structure Audit - SSID Root-24-LOCK Enforcement
Version: 1.0.0
Purpose: Detect and report violations of Root-24 structural integrity

Compliance Framework: SSID Master Definition v1.1.1
Policy: Root-24-LOCK (24 authorized root modules only)
Cost: $0 (local analysis)
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Set
from dataclasses import dataclass
from enum import Enum
import json
from datetime import datetime

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

class ViolationSeverity(Enum):
    """Violation severity levels"""
    CRITICAL = "CRITICAL"  # Unauthorized root directory
    WARNING = "WARNING"    # Root file that should be moved
    INFO = "INFO"          # Acceptable exception

@dataclass
class RootViolation:
    """Represents a Root-24 violation"""
    path: str
    severity: ViolationSeverity
    violation_type: str
    recommendation: str
    is_exception: bool = False

class Root24Auditor:
    """
    Root-24 Structure Auditor
    Validates SSID project structure against Root-24-LOCK policy
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
        ".github"  # GitHub workflows and CI/CD configuration
    }

    # Files that should be migrated (updated after auto-fix execution)
    MIGRATION_CANDIDATES = {
        # All files have been migrated as of 2025-10-12 auto-fix execution
    }

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.violations: List[RootViolation] = []
        self.stats = {
            "critical_violations": 0,
            "warnings": 0,
            "info": 0,
            "total_root_items": 0,
            "authorized_roots": 0,
            "authorized_exceptions": 0,
            "unauthorized_items": 0
        }

    def scan(self) -> List[RootViolation]:
        """
        Scan project root for violations
        Returns list of violations
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
        """Check a single root-level item"""
        item_name = item.name

        # Check if it's an authorized root directory
        if item.is_dir() and item_name in self.AUTHORIZED_ROOTS:
            self.stats["authorized_roots"] += 1
            return

        # Check if it's an authorized exception
        if item_name in self.AUTHORIZED_EXCEPTIONS:
            self.stats["authorized_exceptions"] += 1
            self.violations.append(RootViolation(
                path=item_name,
                severity=ViolationSeverity.INFO,
                violation_type="Authorized Exception",
                recommendation="No action required (authorized infrastructure file)",
                is_exception=True
            ))
            return

        # Check if it's a known migration candidate
        if item_name in self.MIGRATION_CANDIDATES:
            self.stats["warnings"] += 1
            self.stats["unauthorized_items"] += 1
            self.violations.append(RootViolation(
                path=item_name,
                severity=ViolationSeverity.WARNING,
                violation_type="Root File - Should Migrate",
                recommendation=f"Move to: {self.MIGRATION_CANDIDATES[item_name]}"
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
            self.violations.append(RootViolation(
                path=item_name,
                severity=ViolationSeverity.WARNING,
                violation_type="Unauthorized Root File",
                recommendation=f"Move to appropriate module or add to exceptions"
            ))

    def generate_report(self, output_path: Path) -> str:
        """
        Generate markdown audit report
        Returns path to generated report
        """
        report_lines = [
            "# SSID Root-24 Structure Audit Report",
            "",
            f"**Audit Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Project Root:** {self.project_root}",
            f"**Policy Version:** Root-24-LOCK v1.0",
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
            "",
            f"### Violations by Severity",
            "",
            f"- **CRITICAL:** {self.stats['critical_violations']}",
            f"- **WARNING:** {self.stats['warnings']}",
            f"- **INFO:** {self.stats['info']}",
            "",
        ]

        # Overall compliance status
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

        report_lines.extend([
            "---",
            "",
            "## Root-24 Module Verification",
            "",
            "### Authorized Root Modules (24)",
            ""
        ])

        # Check which authorized roots are present
        for root in sorted(self.AUTHORIZED_ROOTS):
            root_path = self.project_root / root
            if root_path.exists() and root_path.is_dir():
                report_lines.append(f"- ✅ `{root}/`")
            else:
                report_lines.append(f"- ❌ `{root}/` (MISSING)")

        report_lines.extend([
            "",
            "---",
            "",
            "## Violations Detail",
            ""
        ])

        # Group violations by severity
        critical_violations = [v for v in self.violations if v.severity == ViolationSeverity.CRITICAL]
        warning_violations = [v for v in self.violations if v.severity == ViolationSeverity.WARNING]
        info_violations = [v for v in self.violations if v.severity == ViolationSeverity.INFO]

        # CRITICAL violations
        if critical_violations:
            report_lines.extend([
                "### ❌ CRITICAL Violations",
                "",
                "These items violate Root-24-LOCK and must be addressed immediately.",
                "",
                "| Path | Type | Recommendation |",
                "|------|------|----------------|"
            ])
            for v in critical_violations:
                report_lines.append(f"| `{v.path}` | {v.violation_type} | {v.recommendation} |")
            report_lines.append("")

        # WARNING violations
        if warning_violations:
            report_lines.extend([
                "### ⚠️ WARNING Violations",
                "",
                "These items should be migrated to maintain clean structure.",
                "",
                "| Path | Type | Recommendation |",
                "|------|------|----------------|"
            ])
            for v in warning_violations:
                report_lines.append(f"| `{v.path}` | {v.violation_type} | {v.recommendation} |")
            report_lines.append("")

        # INFO (exceptions)
        if info_violations:
            report_lines.extend([
                "### ℹ️ Authorized Exceptions",
                "",
                "These items are explicitly permitted in project root.",
                "",
                "| Path | Type |",
                "|------|------|"
            ])
            for v in info_violations:
                report_lines.append(f"| `{v.path}` | {v.violation_type} |")
            report_lines.append("")

        # Migration plan
        if warning_violations:
            report_lines.extend([
                "---",
                "",
                "## Migration Plan",
                "",
                "The following files should be moved to maintain Root-24 compliance:",
                "",
                "```bash",
                "# Recommended migration commands",
                ""
            ])

            for v in warning_violations:
                if v.path in self.MIGRATION_CANDIDATES:
                    target = self.MIGRATION_CANDIDATES[v.path]
                    target_dir = str(Path(target).parent)
                    report_lines.extend([
                        f"# Migrate {v.path}",
                        f"mkdir -p {target_dir}",
                        f"mv {v.path} {target}",
                        ""
                    ])

            report_lines.extend([
                "```",
                ""
            ])

        # Recommendations
        report_lines.extend([
            "---",
            "",
            "## Recommendations",
            "",
            "1. **Immediate Actions:**"
        ])

        if self.stats['critical_violations'] > 0:
            report_lines.append(f"   - Remove or relocate {self.stats['critical_violations']} critical violation(s)")

        if self.stats['warnings'] > 0:
            report_lines.append(f"   - Migrate {self.stats['warnings']} warning item(s) to proper locations")

        report_lines.extend([
            "",
            "2. **Ongoing Enforcement:**",
            "   - Enable CI structure guard (ci_structure_guard.yml)",
            "   - Activate OPA policy (activation_guard.rego)",
            "   - Regular audits with this script",
            "",
            "3. **Documentation:**",
            "   - Update deployment docs after migration",
            "   - Reference Root-24-LOCK in contribution guidelines",
            "",
            "---",
            "",
            "## Audit Metadata",
            "",
            f"- **Auditor:** root_structure_audit.py v1.0.0",
            f"- **Policy:** Root-24-LOCK",
            f"- **Cost:** $0 (local analysis)",
            f"- **Reproducible:** Yes",
            "",
            "**END OF REPORT**"
        ])

        # Write report
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))

        return str(output_path)

    def generate_json_summary(self, output_path: Path) -> str:
        """Generate JSON summary for programmatic access"""
        summary = {
            "audit_date": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "policy_version": "Root-24-LOCK v1.0",
            "statistics": self.stats,
            "compliance_status": "PASS" if self.stats['critical_violations'] == 0 and self.stats['warnings'] == 0 else "FAIL",
            "violations": [
                {
                    "path": v.path,
                    "severity": v.severity.value,
                    "type": v.violation_type,
                    "recommendation": v.recommendation,
                    "is_exception": v.is_exception
                }
                for v in self.violations
            ]
        }

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)

        return str(output_path)

def main():
    """Main execution"""
    # Determine project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent  # Go up from 12_tooling/ to project root

    print("=" * 70)
    print("SSID Root-24 Structure Audit")
    print("=" * 70)
    print(f"Project Root: {project_root}")
    print(f"Policy: Root-24-LOCK v1.0")
    print()

    # Create auditor
    auditor = Root24Auditor(project_root)

    # Scan
    print("Scanning root structure...")
    violations = auditor.scan()

    # Display results
    print(f"\nScan Complete:")
    print(f"  Total Items: {auditor.stats['total_root_items']}")
    print(f"  Authorized Roots: {auditor.stats['authorized_roots']}/24")
    print(f"  Violations: {auditor.stats['unauthorized_items']}")
    print(f"    - Critical: {auditor.stats['critical_violations']}")
    print(f"    - Warning: {auditor.stats['warnings']}")
    print()

    # Generate reports
    report_path = project_root / "02_audit_logging" / "reports" / "root_structure_audit_report.md"
    json_path = project_root / "02_audit_logging" / "reports" / "root_structure_audit_summary.json"

    print("Generating reports...")
    md_report = auditor.generate_report(report_path)
    json_summary = auditor.generate_json_summary(json_path)

    print(f"  Markdown Report: {md_report}")
    print(f"  JSON Summary: {json_summary}")
    print()

    # Exit code based on compliance
    if auditor.stats['critical_violations'] > 0:
        print("❌ AUDIT FAILED - Critical violations detected")
        sys.exit(1)
    elif auditor.stats['warnings'] > 0:
        print("⚠️ AUDIT WARNING - Warnings present, migration recommended")
        sys.exit(0)
    else:
        print("✅ AUDIT PASSED - Full Root-24 compliance")
        sys.exit(0)

if __name__ == "__main__":
    main()
