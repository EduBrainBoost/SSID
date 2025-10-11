#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto Report Generator - Compliance Report Automation
SSID Phase 3 Implementation

Purpose:
- Automatically generate GDPR/DORA/MiCA/AMLD6 compliance reports
- Aggregate evidence from multiple sources
- Create audit-ready PDF/HTML reports
- Sign reports with SHA-256 for forensic integrity

Architecture:
Evidence Sources → Data Aggregation → Report Template → PDF/HTML Export

Data Sources:
- Issue Registry: 23_compliance/evidence/issue_registry/
- Score Logs: 02_audit_logging/evidence/score_logs/
- Evidence Links: 23_compliance/evidence/links/
- Proof System: 03_evidence_system/proofs/
- Quarterly Reviews: 23_compliance/reviews/

Outputs:
- PDF compliance report (signed with SHA-256)
- HTML version (web-friendly)
- JSON data export (machine-readable)

Integration:
- Governance quarterly reviews
- External auditor submissions
- Regulatory authority requests

Compliance Frameworks:
- GDPR: Articles 5, 22, 30, 32
- DORA: ICT risk management, audit trails
- MiCA: Fraud prevention, transparency
- AMLD6: Transaction monitoring, record-keeping
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, asdict
from collections import defaultdict


@dataclass
class ComplianceReport:
    """
    Represents a complete compliance report.

    Fields:
    - report_id: Unique identifier
    - report_type: Type of report (quarterly, annual, ad-hoc)
    - frameworks: List of frameworks covered (GDPR, DORA, etc.)
    - period_start: Report period start date
    - period_end: Report period end date
    - generated_at: Generation timestamp
    - summary: Executive summary
    - sections: Report sections
    - evidence_count: Number of evidence items
    - signature: SHA-256 signature
    """
    report_id: str
    report_type: str
    frameworks: List[str]
    period_start: str
    period_end: str
    generated_at: str
    summary: Dict
    sections: List[Dict]
    evidence_count: int
    signature: str

    def to_dict(self) -> Dict:
        return asdict(self)


class AutoReportGenerator:
    """
    Generate comprehensive compliance reports automatically.

    Responsibilities:
    1. Aggregate data from all evidence sources
    2. Map findings to regulatory requirements
    3. Calculate compliance scores per framework
    4. Generate executive summary
    5. Create detailed sections per framework
    6. Sign report cryptographically
    7. Export to PDF/HTML/JSON
    """

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.registry_dir = repo_root / "23_compliance" / "evidence" / "issue_registry"
        self.score_logs_dir = repo_root / "02_audit_logging" / "evidence" / "score_logs"
        self.links_dir = repo_root / "23_compliance" / "evidence" / "links"
        self.proofs_dir = repo_root / "03_evidence_system" / "proofs"
        self.reviews_dir = repo_root / "23_compliance" / "reviews"
        self.reports_dir = repo_root / "23_compliance" / "reports" / "generated"
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def load_issue_registry(self) -> Optional[Dict]:
        """
        Load the most recent issue registry.

        Returns:
            Registry dict or None if not found
        """
        registry_files = sorted(self.registry_dir.glob("issue_registry_*.json"), reverse=True)

        if not registry_files:
            raise NotImplementedError("TODO: Implement this function")

        with open(registry_files[0], 'r', encoding='utf-8') as f:
            return json.load(f)

    def load_score_events(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict]:
        """
        Load score algorithm events from JSONL logs.

        Args:
            start_date: Start date filter
            end_date: End date filter

        Returns:
            List of score event dicts
        """
        events = []

        if self.score_logs_dir.exists():
            for log_file in sorted(self.score_logs_dir.glob("score_algorithm_*.jsonl")):
                with open(log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            event = json.loads(line.strip())
                            event_time = datetime.fromisoformat(event["timestamp"])

                            if start_date <= event_time <= end_date:
                                events.append(event)

                        except (json.JSONDecodeError, KeyError, ValueError):
                            raise NotImplementedError("TODO: Implement this block")

        return events

    def load_proofs(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict]:
        """
        Load compliance proofs from JSONL logs.

        Args:
            start_date: Start date filter
            end_date: End date filter

        Returns:
            List of proof dicts
        """
        proofs = []

        if self.proofs_dir.exists():
            for proof_dir in sorted(self.proofs_dir.glob("????????")):
                if not proof_dir.is_dir():
                    continue

                log_file = proof_dir / "proofs.jsonl"
                if not log_file.exists():
                    continue

                with open(log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            proof = json.loads(line.strip())
                            proof_time = datetime.fromtimestamp(proof["timestamp"], tz=timezone.utc)

                            if start_date <= proof_time <= end_date:
                                proofs.append(proof)

                        except (json.JSONDecodeError, KeyError, ValueError):
                            raise NotImplementedError("TODO: Implement this block")

        return proofs

    def calculate_framework_scores(
        self,
        findings: List[Dict]
    ) -> Dict[str, float]:
        """
        Calculate compliance scores per framework.

        Args:
            findings: List of findings from issue registry

        Returns:
            Dict mapping framework to compliance score (0-100)

        Scoring:
        - Start at 100
        - Critical finding: -20 points
        - High finding: -10 points
        - Medium finding: -5 points
        - Low finding: -1 point
        - Minimum: 0
        """
        framework_scores = {
            "GDPR": 100.0,
            "DORA": 100.0,
            "MiCA": 100.0,
            "AMLD6": 100.0
        }

        for finding in findings:
            regulations = finding.get("regulations", [])
            severity = finding.get("severity", "low")

            # Determine penalty
            if severity == "critical":
                penalty = 20
            elif severity == "high":
                penalty = 10
            elif severity == "medium":
                penalty = 5
            else:
                penalty = 1

            # Apply penalty to relevant frameworks
            for regulation in regulations:
                if regulation in framework_scores:
                    framework_scores[regulation] = max(0.0, framework_scores[regulation] - penalty)

        return framework_scores

    def generate_executive_summary(
        self,
        findings: List[Dict],
        framework_scores: Dict[str, float],
        score_events: List[Dict],
        proofs: List[Dict]
    ) -> Dict:
        """
        Generate executive summary section.

        Args:
            findings: List of findings
            framework_scores: Compliance scores per framework
            score_events: Score algorithm events
            proofs: Compliance proofs

        Returns:
            Dict containing executive summary data
        """
        # Count findings by severity
        severity_counts = defaultdict(int)
        for finding in findings:
            severity_counts[finding.get("severity", "low")] += 1

        # Calculate average compliance score
        avg_score = sum(framework_scores.values()) / len(framework_scores)

        # Determine overall compliance status
        if avg_score >= 90:
            status = "COMPLIANT"
            status_description = "All frameworks meet compliance thresholds"
        elif avg_score >= 75:
            status = "CONDITIONAL"
            status_description = "Minor issues require remediation"
        else:
            status = "NON-COMPLIANT"
            status_description = "Critical issues require immediate action"

        return {
            "compliance_status": status,
            "status_description": status_description,
            "overall_compliance_score": round(avg_score, 2),
            "framework_scores": framework_scores,
            "findings_summary": {
                "total": len(findings),
                "critical": severity_counts["critical"],
                "high": severity_counts["high"],
                "medium": severity_counts["medium"],
                "low": severity_counts["low"]
            },
            "evidence_summary": {
                "score_events": len(score_events),
                "compliance_proofs": len(proofs),
                "total_evidence_items": len(score_events) + len(proofs)
            }
        }

    def generate_framework_section(
        self,
        framework_name: str,
        findings: List[Dict],
        framework_score: float
    ) -> Dict:
        """
        Generate detailed section for a specific framework.

        Args:
            framework_name: Name of framework (GDPR, DORA, etc.)
            findings: All findings
            framework_score: Compliance score for this framework

        Returns:
            Dict containing framework section data
        """
        # Filter findings relevant to this framework
        relevant_findings = [
            f for f in findings
            if framework_name in f.get("regulations", [])
        ]

        # Group findings by severity
        by_severity = defaultdict(list)
        for finding in relevant_findings:
            severity = finding.get("severity", "low")
            by_severity[severity].append(finding)

        # Calculate compliance percentage
        total_possible = 100
        deductions = sum([
            len(by_severity["critical"]) * 20,
            len(by_severity["high"]) * 10,
            len(by_severity["medium"]) * 5,
            len(by_severity["low"]) * 1
        ])
        compliance_percentage = max(0, total_possible - deductions)

        return {
            "framework": framework_name,
            "compliance_score": framework_score,
            "compliance_percentage": compliance_percentage,
            "total_findings": len(relevant_findings),
            "findings_by_severity": {
                "critical": len(by_severity["critical"]),
                "high": len(by_severity["high"]),
                "medium": len(by_severity["medium"]),
                "low": len(by_severity["low"])
            },
            "findings": [
                {
                    "finding_id": f.get("finding_id"),
                    "severity": f.get("severity"),
                    "description": f.get("description"),
                    "affected_entities": f.get("affected_entities", []),
                    "status": f.get("status"),
                    "recommendation": f.get("remediation")
                }
                for f in relevant_findings[:10]  # Limit to top 10 for report
            ],
            "recommendations": self._generate_framework_recommendations(
                framework_name,
                by_severity
            )
        }

    def _generate_framework_recommendations(
        self,
        framework_name: str,
        findings_by_severity: Dict[str, List[Dict]]
    ) -> List[str]:
        """
        Generate framework-specific recommendations.

        Args:
            framework_name: Name of framework
            findings_by_severity: Findings grouped by severity

        Returns:
            List of recommendation strings
        """
        recommendations = []

        critical_count = len(findings_by_severity.get("critical", []))
        high_count = len(findings_by_severity.get("high", []))

        if critical_count > 0:
            recommendations.append(
                f"URGENT: Address {critical_count} critical {framework_name} findings within 30 days"
            )

        if high_count > 0:
            recommendations.append(
                f"Address {high_count} high-severity {framework_name} findings within 60 days"
            )

        # Framework-specific recommendations
        framework_specific = {
            "GDPR": [
                "Review data processing activities per Article 30",
                "Validate automated decision-making logging (Article 22)",
                "Audit data retention policies"
            ],
            "DORA": [
                "Strengthen ICT risk management procedures",
                "Enhance incident response testing",
                "Review third-party dependency risk assessments"
            ],
            "MiCA": [
                "Validate fraud detection mechanisms",
                "Review token classification compliance",
                "Audit CASP requirements implementation"
            ],
            "AMLD6": [
                "Strengthen customer due diligence (CDD) procedures",
                "Enhance transaction monitoring systems",
                "Validate travel rule compliance"
            ]
        }

        if framework_name in framework_specific:
            recommendations.extend(framework_specific[framework_name][:3])

        return recommendations

    def compute_report_signature(self, report_data: Dict) -> str:
        """
        Compute SHA-256 signature for report.

        Args:
            report_data: Report data dict

        Returns:
            SHA-256 hex digest
        """
        # Create canonical representation (excluding signature field)
        canonical = json.dumps(report_data, sort_keys=True)
        return hashlib.sha256(canonical.encode('utf-8')).hexdigest()

    def generate_report(
        self,
        start_date: datetime,
        end_date: datetime,
        report_type: str = "quarterly",
        frameworks: Optional[List[str]] = None
    ) -> ComplianceReport:
        """
        Generate comprehensive compliance report.

        Args:
            start_date: Report period start
            end_date: Report period end
            report_type: Type of report (quarterly, annual, ad-hoc)
            frameworks: List of frameworks to include (default: all)

        Returns:
            ComplianceReport object
        """
        if not frameworks:
            frameworks = ["GDPR", "DORA", "MiCA", "AMLD6"]

        print(f"Generating {report_type} compliance report...")
        print(f"Period: {start_date.date()} to {end_date.date()}")

        # Load data
        print("Loading issue registry...")
        registry = self.load_issue_registry()

        findings = registry.get("findings", []) if registry else []

        print(f"Loading score events...")
        score_events = self.load_score_events(start_date, end_date)

        print(f"Loading compliance proofs...")
        proofs = self.load_proofs(start_date, end_date)

        # Calculate scores
        print("Calculating framework scores...")
        framework_scores = self.calculate_framework_scores(findings)

        # Generate executive summary
        print("Generating executive summary...")
        summary = self.generate_executive_summary(
            findings,
            framework_scores,
            score_events,
            proofs
        )

        # Generate framework sections
        print("Generating framework sections...")
        sections = []

        for framework in frameworks:
            section = self.generate_framework_section(
                framework,
                findings,
                framework_scores.get(framework, 0.0)
            )
            sections.append(section)

        # Create report object
        report_id = f"REP-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"

        report_data = {
            "report_id": report_id,
            "report_type": report_type,
            "frameworks": frameworks,
            "period_start": start_date.isoformat(),
            "period_end": end_date.isoformat(),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "summary": summary,
            "sections": sections,
            "evidence_count": len(score_events) + len(proofs)
        }

        # Compute signature
        signature = self.compute_report_signature(report_data)
        report_data["signature"] = signature

        report = ComplianceReport(**report_data)

        return report

    def export_report_json(self, report: ComplianceReport) -> Path:
        """
        Export report to JSON format.

        Args:
            report: ComplianceReport object

        Returns:
            Path to exported JSON file
        """
        output_file = self.reports_dir / f"{report.report_id}.json"

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report.to_dict(), f, indent=2, sort_keys=True)

        print(f"JSON report saved: {output_file}")
        return output_file

    def export_report_html(self, report: ComplianceReport) -> Path:
        """
        Export report to HTML format.

        Args:
            report: ComplianceReport object

        Returns:
            Path to exported HTML file
        """
        output_file = self.reports_dir / f"{report.report_id}.html"

        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SSID Compliance Report - {report.report_id}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 4px solid #3498db;
            padding-bottom: 15px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
            border-bottom: 2px solid #ecf0f1;
            padding-bottom: 10px;
        }}
        .status-compliant {{ color: #27ae60; font-weight: bold; }}
        .status-conditional {{ color: #f39c12; font-weight: bold; }}
        .status-non-compliant {{ color: #e74c3c; font-weight: bold; }}
        .score-card {{
            display: inline-block;
            background-color: #ecf0f1;
            padding: 15px 25px;
            margin: 10px;
            border-radius: 8px;
            text-align: center;
        }}
        .score-value {{
            font-size: 32px;
            font-weight: bold;
            color: #2c3e50;
        }}
        .score-label {{
            font-size: 14px;
            color: #7f8c8d;
        }}
        .finding {{
            background-color: #f9f9f9;
            border-left: 4px solid #3498db;
            padding: 15px;
            margin: 10px 0;
        }}
        .finding-critical {{ border-left-color: #e74c3c; }}
        .finding-high {{ border-left-color: #f39c12; }}
        .finding-medium {{ border-left-color: #f1c40f; }}
        .finding-low {{ border-left-color: #3498db; }}
        .metadata {{
            margin-top: 40px;
            padding: 20px;
            background-color: #ecf0f1;
            border-radius: 8px;
            font-size: 14px;
        }}
        .signature {{
            font-family: 'Courier New', monospace;
            color: #7f8c8d;
            word-break: break-all;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>SSID Compliance Report</h1>
        <p><strong>Report ID:</strong> {report.report_id}</p>
        <p><strong>Report Type:</strong> {report.report_type.title()}</p>
        <p><strong>Period:</strong> {report.period_start[:10]} to {report.period_end[:10]}</p>
        <p><strong>Generated:</strong> {report.generated_at}</p>

        <h2>Executive Summary</h2>
        <p><strong>Compliance Status:</strong> <span class="status-{report.summary['compliance_status'].lower()}">{report.summary['compliance_status']}</span></p>
        <p>{report.summary['status_description']}</p>

        <div>
"""

        # Add framework scores
        for framework, score in report.summary["framework_scores"].items():
            html += f"""
            <div class="score-card">
                <div class="score-label">{framework}</div>
                <div class="score-value">{score:.1f}</div>
            </div>
"""

        html += f"""
        </div>

        <h2>Findings Summary</h2>
        <p><strong>Total Findings:</strong> {report.summary['findings_summary']['total']}</p>
        <ul>
            <li>Critical: {report.summary['findings_summary']['critical']}</li>
            <li>High: {report.summary['findings_summary']['high']}</li>
            <li>Medium: {report.summary['findings_summary']['medium']}</li>
            <li>Low: {report.summary['findings_summary']['low']}</li>
        </ul>

        <h2>Evidence Summary</h2>
        <p><strong>Total Evidence Items:</strong> {report.evidence_count}</p>
        <ul>
            <li>Score Algorithm Events: {report.summary['evidence_summary']['score_events']}</li>
            <li>Compliance Proofs: {report.summary['evidence_summary']['compliance_proofs']}</li>
        </ul>
"""

        # Add framework sections
        for section in report.sections:
            html += f"""
        <h2>{section['framework']} Compliance</h2>
        <p><strong>Compliance Score:</strong> {section['compliance_score']:.1f}/100</p>
        <p><strong>Total Findings:</strong> {section['total_findings']}</p>

        <h3>Top Findings</h3>
"""

            for finding in section['findings'][:5]:
                severity_class = f"finding-{finding['severity']}"
                html += f"""
        <div class="finding {severity_class}">
            <p><strong>[{finding['severity'].upper()}] {finding['finding_id']}</strong></p>
            <p>{finding['description']}</p>
            <p><strong>Recommendation:</strong> {finding['recommendation']}</p>
        </div>
"""

            html += f"""
        <h3>Recommendations</h3>
        <ul>
"""
            for rec in section['recommendations']:
                html += f"<li>{rec}</li>\n"

            html += "</ul>\n"

        html += f"""
        <div class="metadata">
            <p><strong>Report Signature (SHA-256):</strong></p>
            <p class="signature">{report.signature}</p>
            <p><strong>SSID Compliance System</strong> | Phase 3 Evidence Automation</p>
        </div>
    </div>
</body>
</html>
"""

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)

        print(f"HTML report saved: {output_file}")
        return output_file


def main():
    """CLI entry point"""
    repo_root = Path(__file__).resolve().parents[2]

    generator = AutoReportGenerator(repo_root)

    # Generate quarterly report for last 90 days
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=90)

    print("Generating compliance report...")
    report = generator.generate_report(
        start_date=start_date,
        end_date=end_date,
        report_type="quarterly"
    )

    # Export in multiple formats
    json_path = generator.export_report_json(report)
    html_path = generator.export_report_html(report)

    print(f"\n✅ Compliance report generated successfully!")
    print(f"   Report ID: {report.report_id}")
    print(f"   Overall Score: {report.summary['overall_compliance_score']:.1f}/100")
    print(f"   Status: {report.summary['compliance_status']}")
    print(f"\n   JSON: {json_path}")
    print(f"   HTML: {html_path}")


if __name__ == "__main__":
    main()
