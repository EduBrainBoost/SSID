#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Audit Findings Injector - Phase 2 Governance Hook
SSID Phase 2 Implementation

Purpose:
- Automatically inject CI/CD findings into quarterly review templates
- Update audit_findings.yaml from issue registry
- Trigger governance workflow when critical findings appear
- Maintain evidence chain integrity

Architecture:
Issue Registry → Findings Injector → Review Template → Governance Workflow

Integration:
1. CI/CD generates findings (badge violations, dependency cycles)
2. Converter creates issue registry
3. Injector updates quarterly review template
4. Governance committee reviews findings
5. Status changes flow back to issue registry

This is the automation layer for "DRAFT → PRODUCTION" status transitions.
"""

import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from dataclasses import dataclass


@dataclass
class AuditFinding:
    """
    Represents a finding in the review template format.

    Fields match 23_compliance/reviews/*/review_template.yaml structure.
    """
    id: str
    severity: str  # critical, major, minor, observation
    description: str
    affected_modules: List[str]
    recommendation: str
    remediation_deadline: str
    status: str  # open, in_progress, resolved


class AuditFindingsInjector:
    """
    Inject findings from issue registry into quarterly review templates.

    Responsibilities:
    1. Load issue registry from 23_compliance/evidence/issue_registry/
    2. Load quarterly review template from 23_compliance/reviews/<quarter>/
    3. Map findings to appropriate review sections (GDPR, DORA, MiCA, AMLD6)
    4. Inject findings into template YAML
    5. Update statistics (critical_issues, major_issues, etc.)
    6. Preserve template structure and checksums
    """

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.registry_dir = repo_root / "23_compliance" / "evidence" / "issue_registry"
        self.reviews_dir = repo_root / "23_compliance" / "reviews"
        self.links_dir = repo_root / "23_compliance" / "evidence" / "links"

    def get_current_quarter(self) -> str:
        """
        Get current quarter identifier (e.g., "2025-Q4").

        Returns:
            Quarter string in format YYYY-QX
        """
        now = datetime.now(timezone.utc)
        year = now.year
        month = now.month

        if month <= 3:
            quarter = 1
        elif month <= 6:
            quarter = 2
        elif month <= 9:
            quarter = 3
        else:
            quarter = 4

        return f"{year}-Q{quarter}"

    def load_latest_registry(self) -> Optional[Dict]:
        """
        Load the most recent issue registry.

        Returns:
            Registry dict or None if no registry exists
        """
        registry_files = sorted(self.registry_dir.glob("issue_registry_*.json"), reverse=True)

        if not registry_files:
            raise NotImplementedError("TODO: Implement this function")

        latest_file = registry_files[0]

        with open(latest_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def load_review_template(self, quarter: str) -> Optional[Dict]:
        """
        Load quarterly review template.

        Args:
            quarter: Quarter identifier (e.g., "2025-Q4")

        Returns:
            Review template dict or None if not found
        """
        review_file = self.reviews_dir / quarter / "review_template.yaml"

        if not review_file.exists():
            # Try to find audit_findings.yaml instead
            findings_file = self.reviews_dir / quarter / "audit_findings.yaml"
            if findings_file.exists():
                review_file = findings_file
            else:
                raise NotImplementedError("TODO: Implement this function")

        with open(review_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def save_review_template(self, quarter: str, review_data: Dict) -> Path:
        """
        Save updated review template.

        Args:
            quarter: Quarter identifier
            review_data: Updated review template dict

        Returns:
            Path to saved file
        """
        review_dir = self.reviews_dir / quarter
        review_dir.mkdir(parents=True, exist_ok=True)

        audit_findings_file = review_dir / "audit_findings.yaml"

        with open(audit_findings_file, 'w', encoding='utf-8') as f:
            yaml.dump(review_data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

        return audit_findings_file

    def map_finding_to_framework(self, finding: Dict) -> List[str]:
        """
        Map finding regulations to review template frameworks.

        Args:
            finding: Finding dict with 'regulations' field

        Returns:
            List of framework section names (e.g., ['gdpr_review', 'dora_review'])
        """
        regulation_to_section = {
            "GDPR": "gdpr_review",
            "DORA": "dora_review",
            "MiCA": "mica_review",
            "AMLD6": "amld6_review",
            "AI-Act": "gdpr_review"  # Map AI Act to GDPR for now
        }

        sections = []
        for regulation in finding.get("regulations", []):
            section = regulation_to_section.get(regulation)
            if section and section not in sections:
                sections.append(section)

        # Default to GDPR if no specific mapping
        if not sections:
            sections.append("gdpr_review")

        return sections

    def convert_to_audit_finding(self, finding: Dict) -> AuditFinding:
        """
        Convert issue registry finding to review template format.

        Args:
            finding: Finding dict from issue registry

        Returns:
            AuditFinding object
        """
        # Map severity (keep compatible)
        severity_map = {
            "critical": "critical",
            "high": "major",
            "medium": "minor",
            "low": "observation"
        }

        severity = severity_map.get(finding.get("severity", "low"), "observation")

        # Calculate remediation deadline (30 days for critical, 60 for major, 90 for minor)
        created_at = datetime.fromisoformat(finding.get("created_at", datetime.now(timezone.utc).isoformat()))

        if severity == "critical":
            deadline = created_at.replace(day=min(created_at.day + 30, 28))
        elif severity == "major":
            deadline = created_at.replace(day=min(created_at.day + 60, 28))
        else:
            deadline = created_at.replace(day=min(created_at.day + 90, 28))

        return AuditFinding(
            id=finding.get("finding_id", ""),
            severity=severity,
            description=finding.get("description", ""),
            affected_modules=finding.get("affected_entities", []),
            recommendation=finding.get("remediation", ""),
            remediation_deadline=deadline.strftime('%Y-%m-%d'),
            status=finding.get("status", "open")
        )

    def inject_findings(self, quarter: Optional[str] = None) -> Optional[Path]:
        """
        Inject latest findings into quarterly review template.

        Args:
            quarter: Quarter identifier (default: current quarter)

        Returns:
            Path to updated audit_findings.yaml
        """
        if not quarter:
            quarter = self.get_current_quarter()

        # Load latest registry
        registry = self.load_latest_registry()
        if not registry:
            print(f"No issue registry found in {self.registry_dir}")
            raise NotImplementedError("TODO: Implement this function")

        # Load or create review template
        review_template = self.load_review_template(quarter)

        if not review_template:
            # Create minimal template structure
            review_template = {
                "meta": {
                    "version": quarter,
                    "type": "audit_findings",
                    "last_updated": datetime.now(timezone.utc).isoformat(),
                    "auto_generated": True
                },
                "review_sections": {
                    "executive_summary": {
                        "critical_issues": 0,
                        "major_issues": 0,
                        "minor_issues": 0,
                        "recommendations": 0
                    },
                    "gdpr_review": {"findings": []},
                    "dora_review": {"findings": []},
                    "mica_review": {"findings": []},
                    "amld6_review": {"findings": []},
                    "badge_integrity": {"findings": []},
                    "anti_gaming_controls": {"findings": []}
                }
            }

        # Initialize findings lists if missing
        if "review_sections" not in review_template:
            review_template["review_sections"] = {}

        for section in ["gdpr_review", "dora_review", "mica_review", "amld6_review", "badge_integrity", "anti_gaming_controls"]:
            if section not in review_template["review_sections"]:
                review_template["review_sections"][section] = {}
            if "findings" not in review_template["review_sections"][section]:
                review_template["review_sections"][section]["findings"] = []

        # Process findings
        findings = registry.get("findings", [])

        for finding_dict in findings:
            # Convert to audit finding format
            audit_finding = self.convert_to_audit_finding(finding_dict)

            # Determine which sections to inject into
            sections = self.map_finding_to_framework(finding_dict)

            # Special handling for badge/anti-gaming findings
            source = finding_dict.get("source", "")
            if "badge" in source or "anti_gaming" in source:
                sections.append("badge_integrity")
                sections.append("anti_gaming_controls")

            # Inject into each relevant section
            for section in sections:
                # Check if finding already exists (by ID)
                existing_ids = [f.get("id") for f in review_template["review_sections"][section]["findings"]]

                if audit_finding.id not in existing_ids:
                    review_template["review_sections"][section]["findings"].append({
                        "id": audit_finding.id,
                        "severity": audit_finding.severity,
                        "description": audit_finding.description,
                        "affected_modules": audit_finding.affected_modules,
                        "recommendation": audit_finding.recommendation,
                        "remediation_deadline": audit_finding.remediation_deadline,
                        "status": audit_finding.status
                    })

        # Update statistics
        if "executive_summary" not in review_template["review_sections"]:
            review_template["review_sections"]["executive_summary"] = {}

        statistics = registry.get("statistics", {})
        review_template["review_sections"]["executive_summary"]["critical_issues"] = statistics.get("critical", 0)
        review_template["review_sections"]["executive_summary"]["major_issues"] = statistics.get("high", 0)
        review_template["review_sections"]["executive_summary"]["minor_issues"] = statistics.get("medium", 0)
        review_template["review_sections"]["executive_summary"]["recommendations"] = statistics.get("total_findings", 0)

        # Update metadata
        if "meta" in review_template:
            review_template["meta"]["last_updated"] = datetime.now(timezone.utc).isoformat()
            review_template["meta"]["findings_injected"] = len(findings)

        # Save updated template
        output_file = self.save_review_template(quarter, review_template)

        print(f"Injected {len(findings)} findings into {output_file}")

        return output_file

    def create_governance_alert(self, findings_count: int, critical_count: int) -> None:
        """
        Create governance alert if critical findings exceed threshold.

        Args:
            findings_count: Total number of findings
            critical_count: Number of critical findings
        """
        if critical_count > 0:
            alert_file = self.repo_root / "07_governance_legal" / "alerts" / f"critical_findings_{datetime.now(timezone.utc).strftime('%Y%m%d')}.yaml"
            alert_file.parent.mkdir(parents=True, exist_ok=True)

            alert = {
                "alert_type": "critical_findings",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "total_findings": findings_count,
                "critical_findings": critical_count,
                "action_required": "Governance committee review required within 48 hours",
                "review_file": str(self.reviews_dir / self.get_current_quarter() / "audit_findings.yaml")
            }

            with open(alert_file, 'w', encoding='utf-8') as f:
                yaml.dump(alert, f, default_flow_style=False)

            print(f"Governance alert created: {alert_file}")


def main():
    """CLI entry point"""
    repo_root = Path(__file__).resolve().parents[2]

    injector = AuditFindingsInjector(repo_root)

    print("Injecting findings into quarterly review...")
    output_file = injector.inject_findings()

    if output_file:
        print(f"Findings injected successfully: {output_file}")

        # Check if governance alert is needed
        registry = injector.load_latest_registry()
        if registry:
            stats = registry.get("statistics", {})
            injector.create_governance_alert(
                findings_count=stats.get("total_findings", 0),
                critical_count=stats.get("critical", 0)
            )
    else:
        print("No findings to inject")


if __name__ == "__main__":
    main()
