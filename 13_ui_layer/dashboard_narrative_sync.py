#!/usr/bin/env python3
"""
SSID Dashboard-Narrative Synchronization
Unified Technical and Legal Compliance View

Synchronizes human-readable legal summaries with technical dashboard,
ensuring both views share the same data foundation and stay consistent.
"""

import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class SyncedComplianceView:
    """Synchronized compliance data for both technical and narrative views"""
    timestamp: datetime
    sync_id: str

    # Core metrics (single source of truth)
    framework_coverage: Dict[str, float]
    control_states: Dict[str, str]
    risk_scores: Dict[str, float]
    critical_issues: List[Dict]

    # Technical representation
    technical_dashboard: Dict

    # Narrative representation
    legal_summary: Dict

    # Sync metadata
    data_sources: List[str]
    last_sync: datetime
    sync_integrity_hash: str


class DashboardNarrativeSync:
    """
    Dashboard-Narrative Synchronization Engine

    Ensures technical dashboards and human-readable legal summaries
    always reflect the same underlying compliance data.
    """

    def __init__(
        self,
        unified_index_path: Path,
        dashboard_data_path: Path,
        output_dir: Path
    ):
        self.unified_index_path = Path(unified_index_path)
        self.dashboard_data_path = Path(dashboard_data_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Load source data
        self.unified_index = self._load_yaml(self.unified_index_path)

    def create_synced_view(self) -> SyncedComplianceView:
        """
        Create synchronized compliance view

        Extracts data from unified index and generates both
        technical and narrative representations
        """
        sync_id = f"sync_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        print(f"[Dashboard-Narrative Sync] Creating synced view: {sync_id}")

        # Extract core metrics
        metrics = self.unified_index.get('compliance_metrics_unified', {})
        mappings = self.unified_index.get('cross_framework_mappings', {})

        # Framework coverage
        framework_coverage = {
            k: self._parse_percentage(v)
            for k, v in metrics.get('overall_coverage', {}).items()
        }

        # Control states
        control_states = {}
        critical_issues = []

        for domain, controls in mappings.items():
            if isinstance(controls, list):
                for control in controls:
                    control_states[control['unified_id']] = control['implementation_status']

                    if control['risk_level'] == 'CRITICAL' and control['implementation_status'] != 'implemented':
                        critical_issues.append({
                            'control_id': control['unified_id'],
                            'description': control['description'],
                            'risk_level': control['risk_level'],
                            'frameworks': [m['framework'] for m in control['mappings']]
                        })

        # Risk scores
        by_risk = metrics.get('by_risk_level', {})
        risk_scores = {
            'critical': self._parse_percentage(by_risk.get('critical', '0%')),
            'high': self._parse_percentage(by_risk.get('high', '0%')),
            'medium': self._parse_percentage(by_risk.get('medium', '0%')),
            'low': self._parse_percentage(by_risk.get('low', '0%'))
        }

        # Generate technical dashboard
        technical = self._generate_technical_dashboard(
            framework_coverage,
            control_states,
            risk_scores,
            critical_issues
        )

        # Generate narrative summary
        narrative = self._generate_narrative_summary(
            framework_coverage,
            control_states,
            risk_scores,
            critical_issues
        )

        # Calculate sync integrity hash
        import hashlib
        sync_data = json.dumps({
            'framework_coverage': framework_coverage,
            'control_states': control_states,
            'risk_scores': risk_scores
        }, sort_keys=True)
        integrity_hash = hashlib.sha256(sync_data.encode()).hexdigest()

        # Create synced view
        synced_view = SyncedComplianceView(
            timestamp=datetime.now(),
            sync_id=sync_id,
            framework_coverage=framework_coverage,
            control_states=control_states,
            risk_scores=risk_scores,
            critical_issues=critical_issues,
            technical_dashboard=technical,
            legal_summary=narrative,
            data_sources=[
                str(self.unified_index_path)
            ],
            last_sync=datetime.now(),
            sync_integrity_hash=integrity_hash
        )

        print(f"[Dashboard-Narrative Sync] Synced view created")
        print(f"  - Framework coverage: {len(framework_coverage)} frameworks")
        print(f"  - Control states: {len(control_states)} controls")
        print(f"  - Critical issues: {len(critical_issues)}")
        print(f"  - Integrity hash: {integrity_hash[:16]}...")

        return synced_view

    def _generate_technical_dashboard(
        self,
        framework_coverage: Dict[str, float],
        control_states: Dict[str, str],
        risk_scores: Dict[str, float],
        critical_issues: List[Dict]
    ) -> Dict:
        """Generate technical dashboard data structure"""

        # Calculate derived metrics
        total_controls = len(control_states)
        implemented = sum(1 for s in control_states.values() if s == 'implemented')
        planned = sum(1 for s in control_states.values() if s == 'planned')

        return {
            "type": "technical_dashboard",
            "generated_at": datetime.now().isoformat(),
            "widgets": {
                "framework_compliance_chart": {
                    "type": "bar_chart",
                    "title": "Framework Compliance",
                    "data": [
                        {"framework": k.upper(), "coverage": v, "status": self._get_status_code(v)}
                        for k, v in framework_coverage.items()
                    ],
                    "x_axis": "framework",
                    "y_axis": "coverage",
                    "unit": "percent"
                },
                "risk_level_distribution": {
                    "type": "pie_chart",
                    "title": "Risk Level Coverage",
                    "data": [
                        {"level": k.upper(), "value": v}
                        for k, v in risk_scores.items()
                    ]
                },
                "control_implementation_status": {
                    "type": "gauge",
                    "title": "Control Implementation",
                    "value": (implemented / total_controls * 100) if total_controls > 0 else 0,
                    "max": 100,
                    "thresholds": [
                        {"value": 90, "color": "green"},
                        {"value": 75, "color": "yellow"},
                        {"value": 0, "color": "red"}
                    ]
                },
                "critical_issues_list": {
                    "type": "alert_list",
                    "title": "Critical Issues",
                    "count": len(critical_issues),
                    "items": [
                        {
                            "id": issue['control_id'],
                            "severity": "critical",
                            "title": issue['description'][:60] + "...",
                            "frameworks": issue['frameworks']
                        }
                        for issue in critical_issues[:10]
                    ]
                },
                "compliance_timeline": {
                    "type": "line_chart",
                    "title": "Compliance Trend",
                    "data": self._generate_timeline_data(framework_coverage),
                    "x_axis": "date",
                    "y_axis": "score"
                },
                "kpi_summary": {
                    "type": "kpi_panel",
                    "metrics": [
                        {
                            "label": "Overall Compliance",
                            "value": sum(framework_coverage.values()) / len(framework_coverage),
                            "unit": "%",
                            "trend": "stable"
                        },
                        {
                            "label": "Controls Implemented",
                            "value": implemented,
                            "total": total_controls,
                            "unit": "controls"
                        },
                        {
                            "label": "Critical Issues",
                            "value": len(critical_issues),
                            "severity": "high" if len(critical_issues) > 0 else "low"
                        },
                        {
                            "label": "Risk Score",
                            "value": self._calculate_overall_risk(risk_scores),
                            "unit": "score",
                            "scale": "0-100"
                        }
                    ]
                }
            },
            "data_integrity": {
                "controls_total": total_controls,
                "controls_implemented": implemented,
                "controls_planned": planned,
                "frameworks_tracked": len(framework_coverage)
            }
        }

    def _generate_narrative_summary(
        self,
        framework_coverage: Dict[str, float],
        control_states: Dict[str, str],
        risk_scores: Dict[str, float],
        critical_issues: List[Dict]
    ) -> Dict:
        """Generate narrative summary structure"""

        overall_avg = sum(framework_coverage.values()) / len(framework_coverage)
        status = self._get_status_label(overall_avg)

        # Generate narrative text
        executive_summary = self._generate_executive_text(
            overall_avg,
            status,
            framework_coverage,
            len(critical_issues)
        )

        key_findings = self._generate_key_findings_text(
            framework_coverage,
            risk_scores,
            critical_issues
        )

        recommendations = self._generate_recommendations_text(
            framework_coverage,
            critical_issues
        )

        return {
            "type": "legal_narrative",
            "generated_at": datetime.now().isoformat(),
            "sections": {
                "executive_summary": {
                    "title": "Executive Summary",
                    "content": executive_summary,
                    "data_points": {
                        "overall_compliance": f"{overall_avg:.1f}%",
                        "status": status,
                        "critical_issues": len(critical_issues)
                    }
                },
                "framework_analysis": {
                    "title": "Regulatory Framework Analysis",
                    "content": self._generate_framework_analysis_text(framework_coverage),
                    "table": [
                        {
                            "framework": k.upper(),
                            "coverage": f"{v:.1f}%",
                            "status": self._get_status_label(v),
                            "assessment": self._get_framework_assessment(k, v)
                        }
                        for k, v in framework_coverage.items()
                    ]
                },
                "key_findings": {
                    "title": "Key Findings",
                    "content": key_findings,
                    "bullet_points": self._generate_findings_bullets(
                        framework_coverage,
                        risk_scores
                    )
                },
                "critical_control_status": {
                    "title": "Critical Control Status",
                    "content": f"Analysis of {len(critical_issues)} critical control gaps requiring immediate attention.",
                    "items": [
                        {
                            "control_id": issue['control_id'],
                            "description": issue['description'],
                            "frameworks": ", ".join(issue['frameworks']),
                            "priority": "IMMEDIATE"
                        }
                        for issue in critical_issues
                    ]
                },
                "risk_assessment": {
                    "title": "Risk Assessment",
                    "content": self._generate_risk_assessment_text(risk_scores),
                    "risk_matrix": [
                        {
                            "level": k.upper(),
                            "coverage": f"{v:.1f}%",
                            "status": "COMPLIANT" if v >= 90 else "NEEDS ATTENTION"
                        }
                        for k, v in risk_scores.items()
                    ]
                },
                "recommendations": {
                    "title": "Recommendations",
                    "content": recommendations,
                    "action_items": self._generate_action_items(
                        framework_coverage,
                        critical_issues
                    )
                }
            },
            "data_integrity": {
                "source": "unified_compliance_index",
                "frameworks_analyzed": len(framework_coverage),
                "controls_evaluated": len(control_states),
                "data_as_of": datetime.now().isoformat()
            }
        }

    def export_synced_views(self, synced_view: SyncedComplianceView):
        """
        Export synchronized views in multiple formats

        - JSON (technical dashboard)
        - Markdown (legal narrative)
        - HTML (combined view)
        """

        # Export technical dashboard (JSON)
        dashboard_path = self.output_dir / f"dashboard_{synced_view.sync_id}.json"
        dashboard_path.write_text(
            json.dumps(synced_view.technical_dashboard, indent=2),
            encoding='utf-8'
        )
        print(f"[Dashboard-Narrative Sync] Exported dashboard: {dashboard_path}")

        # Export narrative summary (Markdown)
        narrative_path = self.output_dir / f"narrative_{synced_view.sync_id}.md"
        self._export_narrative_markdown(synced_view.legal_summary, narrative_path)
        print(f"[Dashboard-Narrative Sync] Exported narrative: {narrative_path}")

        # Export combined HTML view
        html_path = self.output_dir / f"combined_{synced_view.sync_id}.html"
        self._export_combined_html(synced_view, html_path)
        print(f"[Dashboard-Narrative Sync] Exported combined view: {html_path}")

        # Export sync metadata
        metadata_path = self.output_dir / f"sync_metadata_{synced_view.sync_id}.json"
        metadata = {
            "sync_id": synced_view.sync_id,
            "timestamp": synced_view.timestamp.isoformat(),
            "integrity_hash": synced_view.sync_integrity_hash,
            "data_sources": synced_view.data_sources,
            "framework_count": len(synced_view.framework_coverage),
            "control_count": len(synced_view.control_states),
            "critical_issues": len(synced_view.critical_issues)
        }
        metadata_path.write_text(json.dumps(metadata, indent=2), encoding='utf-8')

    def _export_narrative_markdown(self, narrative: Dict, output_path: Path):
        """Export narrative as markdown"""

        md = f"# Compliance Report\n\n"
        md += f"**Generated:** {narrative['generated_at']}\n\n"
        md += "---\n\n"

        for section_key, section in narrative['sections'].items():
            md += f"## {section['title']}\n\n"
            md += f"{section['content']}\n\n"

            # Add tables if present
            if 'table' in section:
                md += self._format_table_markdown(section['table'])
                md += "\n"

            # Add bullet points if present
            if 'bullet_points' in section:
                for bullet in section['bullet_points']:
                    md += f"- {bullet}\n"
                md += "\n"

            # Add items if present
            if 'items' in section:
                for item in section['items']:
                    if 'control_id' in item:
                        md += f"### {item['control_id']}\n"
                        md += f"{item['description']}\n"
                        md += f"**Frameworks:** {item['frameworks']}\n"
                        md += f"**Priority:** {item['priority']}\n\n"

            md += "---\n\n"

        output_path.write_text(md, encoding='utf-8')

    def _export_combined_html(self, synced_view: SyncedComplianceView, output_path: Path):
        """Export combined technical/narrative HTML view"""

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SSID Compliance Dashboard - {synced_view.sync_id}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        .header {{ background: white; padding: 20px; margin-bottom: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .tabs {{ display: flex; gap: 10px; margin-bottom: 20px; }}
        .tab {{ padding: 10px 20px; background: white; border-radius: 8px; cursor: pointer; transition: background 0.3s; }}
        .tab.active {{ background: #007bff; color: white; }}
        .content {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .metric {{ display: inline-block; margin: 10px; padding: 15px; background: #f8f9fa; border-radius: 4px; min-width: 150px; }}
        .metric-value {{ font-size: 32px; font-weight: bold; color: #007bff; }}
        .metric-label {{ font-size: 14px; color: #666; margin-top: 5px; }}
        .status-good {{ color: #28a745; }}
        .status-warn {{ color: #ffc107; }}
        .status-critical {{ color: #dc3545; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #dee2e6; }}
        th {{ background: #f8f9fa; font-weight: 600; }}
        .integrity {{ position: fixed; bottom: 20px; right: 20px; padding: 10px; background: white; border-radius: 4px; box-shadow: 0 2px 8px rgba(0,0,0,0.2); font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>SSID Compliance Dashboard</h1>
            <p>Sync ID: {synced_view.sync_id} | Generated: {synced_view.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>

        <div class="tabs">
            <div class="tab active" onclick="showTab('technical')">Technical Dashboard</div>
            <div class="tab" onclick="showTab('narrative')">Legal Narrative</div>
            <div class="tab" onclick="showTab('combined')">Combined View</div>
        </div>

        <div id="technical" class="content">
            <h2>Technical Dashboard</h2>
            {self._generate_technical_html(synced_view.technical_dashboard)}
        </div>

        <div id="narrative" class="content" style="display:none;">
            <h2>Legal Narrative</h2>
            {self._generate_narrative_html(synced_view.legal_summary)}
        </div>

        <div id="combined" class="content" style="display:none;">
            <h2>Combined View</h2>
            <p>Side-by-side technical and legal perspective on the same data.</p>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                <div>
                    <h3>Technical Metrics</h3>
                    {self._generate_technical_html(synced_view.technical_dashboard)}
                </div>
                <div>
                    <h3>Legal Summary</h3>
                    {self._generate_narrative_html(synced_view.legal_summary)}
                </div>
            </div>
        </div>
    </div>

    <div class="integrity">
        Data Integrity: {synced_view.sync_integrity_hash[:12]}...
    </div>

    <script>
        function showTab(tab) {{
            document.querySelectorAll('.content').forEach(c => c.style.display = 'none');
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.getElementById(tab).style.display = 'block';
            event.target.classList.add('active');
        }}
    </script>
</body>
</html>"""

        output_path.write_text(html, encoding='utf-8')

    def _generate_technical_html(self, dashboard: Dict) -> str:
        """Generate technical dashboard HTML"""
        html = "<div class='metrics'>"

        for metric in dashboard['widgets']['kpi_summary']['metrics']:
            value = metric['value']
            if isinstance(value, float):
                value_str = f"{value:.1f}"
            else:
                value_str = str(value)

            html += f"""
            <div class="metric">
                <div class="metric-value">{value_str}</div>
                <div class="metric-label">{metric['label']}</div>
            </div>
            """

        html += "</div>"

        # Framework table
        html += "<h3>Framework Compliance</h3><table><tr><th>Framework</th><th>Coverage</th><th>Status</th></tr>"
        for item in dashboard['widgets']['framework_compliance_chart']['data']:
            status_class = 'status-good' if item['status'] == 'good' else 'status-warn' if item['status'] == 'acceptable' else 'status-critical'
            html += f"<tr><td>{item['framework']}</td><td>{item['coverage']:.1f}%</td><td class='{status_class}'>{item['status'].upper()}</td></tr>"
        html += "</table>"

        return html

    def _generate_narrative_html(self, narrative: Dict) -> str:
        """Generate narrative summary HTML"""
        html = ""

        for section_key, section in narrative['sections'].items():
            html += f"<h3>{section['title']}</h3>"
            html += f"<p>{section['content']}</p>"

        return html

    # Helper methods

    def _load_yaml(self, path: Path) -> Dict:
        """Load YAML file"""
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def _parse_percentage(self, value) -> float:
        """Parse percentage value"""
        if isinstance(value, str):
            return float(value.strip('%'))
        return float(value) if value else 0.0

    def _get_status_code(self, percentage: float) -> str:
        """Get status code from percentage"""
        if percentage >= 90:
            return "good"
        elif percentage >= 75:
            return "acceptable"
        else:
            return "critical"

    def _get_status_label(self, percentage: float) -> str:
        """Get status label"""
        if percentage >= 95:
            return "EXCELLENT"
        elif percentage >= 90:
            return "GOOD"
        elif percentage >= 80:
            return "ACCEPTABLE"
        else:
            return "NEEDS IMPROVEMENT"

    def _calculate_overall_risk(self, risk_scores: Dict[str, float]) -> float:
        """Calculate overall risk score"""
        weights = {'critical': 0.5, 'high': 0.3, 'medium': 0.15, 'low': 0.05}
        score = sum((100 - risk_scores.get(level, 0)) * weight for level, weight in weights.items())
        return round(score, 1)

    def _generate_timeline_data(self, framework_coverage: Dict) -> List:
        """Generate timeline data (mock)"""
        return [
            {"date": "2025-Q1", "score": 88},
            {"date": "2025-Q2", "score": 90},
            {"date": "2025-Q3", "score": 92},
            {"date": "2025-Q4", "score": sum(framework_coverage.values()) / len(framework_coverage)}
        ]

    def _generate_executive_text(self, avg: float, status: str, frameworks: Dict, critical_count: int) -> str:
        """Generate executive summary text"""
        text = f"The organization maintains {avg:.1f}% overall compliance across four major regulatory frameworks. "
        text += f"Current status is {status}. "

        if critical_count > 0:
            text += f"However, {critical_count} critical control gap(s) require immediate attention."
        else:
            text += "No critical control gaps identified."

        return text

    def _generate_key_findings_text(self, frameworks: Dict, risks: Dict, critical: List) -> str:
        """Generate key findings text"""
        findings = []

        for fw, cov in frameworks.items():
            if cov < 90:
                findings.append(f"{fw.upper()} compliance at {cov:.1f}% requires improvement")

        if risks['critical'] < 100:
            findings.append(f"Critical controls at {risks['critical']:.1f}% coverage")

        if not findings:
            return "All key compliance indicators are within acceptable ranges."

        return " | ".join(findings)

    def _generate_recommendations_text(self, frameworks: Dict, critical: List) -> str:
        """Generate recommendations text"""
        recs = []

        if critical:
            recs.append(f"Address {len(critical)} critical control gap(s) immediately")

        for fw, cov in frameworks.items():
            if cov < 90:
                recs.append(f"Increase {fw.upper()} compliance from {cov:.1f}% to 90% minimum")

        if not recs:
            return "Continue quarterly reviews and maintain current compliance posture."

        return " | ".join(recs)

    def _generate_framework_analysis_text(self, frameworks: Dict) -> str:
        """Generate framework analysis text"""
        return f"Analysis of {len(frameworks)} regulatory frameworks shows varying compliance levels. Each framework has specific requirements that must be addressed."

    def _get_framework_assessment(self, framework: str, coverage: float) -> str:
        """Get framework assessment"""
        if coverage >= 95:
            return "Excellent compliance posture"
        elif coverage >= 90:
            return "Good compliance, minor improvements needed"
        elif coverage >= 80:
            return "Acceptable but requires focused effort"
        else:
            return "Critical gaps require immediate remediation"

    def _generate_findings_bullets(self, frameworks: Dict, risks: Dict) -> List[str]:
        """Generate findings bullets"""
        bullets = []
        for fw, cov in frameworks.items():
            bullets.append(f"{fw.upper()}: {cov:.1f}% compliance")
        return bullets

    def _generate_risk_assessment_text(self, risks: Dict) -> str:
        """Generate risk assessment text"""
        critical = risks.get('critical', 0)
        high = risks.get('high', 0)

        if critical == 100 and high >= 95:
            return "Low risk - All critical and high-priority controls implemented"
        elif critical < 100:
            return "High risk - Critical control gaps present"
        else:
            return "Medium risk - Some high-priority gaps exist"

    def _generate_action_items(self, frameworks: Dict, critical: List) -> List[Dict]:
        """Generate action items"""
        items = []

        if critical:
            items.append({
                "priority": "IMMEDIATE",
                "action": f"Address {len(critical)} critical control gaps",
                "deadline": "7 days"
            })

        for fw, cov in frameworks.items():
            if cov < 90:
                items.append({
                    "priority": "HIGH",
                    "action": f"Improve {fw.upper()} compliance to 90%",
                    "deadline": "30 days"
                })

        return items

    def _format_table_markdown(self, table: List[Dict]) -> str:
        """Format table as markdown"""
        if not table:
            return ""

        # Headers
        headers = list(table[0].keys())
        md = "| " + " | ".join(h.replace('_', ' ').title() for h in headers) + " |\n"
        md += "| " + " | ".join("---" for _ in headers) + " |\n"

        # Rows
        for row in table:
            md += "| " + " | ".join(str(row[h]) for h in headers) + " |\n"

        return md


def main():
    """Main CLI entry point"""
    print("=== SSID Dashboard-Narrative Sync ===\n")

    # Paths
    unified_index_path = Path("C:/Users/bibel/Documents/Github/SSID/23_compliance/mappings/compliance_unified_index.yaml")
    dashboard_data_path = Path("C:/Users/bibel/Documents/Github/SSID/13_ui_layer")
    output_dir = Path("C:/Users/bibel/Documents/Github/SSID/13_ui_layer/synced_views")

    # Initialize sync engine
    sync = DashboardNarrativeSync(unified_index_path, dashboard_data_path, output_dir)

    # Create synced view
    print("1. Creating synchronized view...")
    synced_view = sync.create_synced_view()

    # Export in multiple formats
    print("\n2. Exporting synchronized views...")
    sync.export_synced_views(synced_view)

    print("\n=== Sync Complete ===")
    print(f"\nSynced views available in: {output_dir}")
    print(f"Integrity hash: {synced_view.sync_integrity_hash}")


if __name__ == "__main__":
    main()
