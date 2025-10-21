#!/usr/bin/env python3
"""
SSID Historical Compliance Simulator
AI-Powered Time-Travel Audit Capability

Enables AI module to replay historical audit states, showing compliance posture
at any point in time. Provides not just evidence, but contextual understanding
of compliance evolution.
"""

import json
import yaml
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import hashlib

@dataclass
class ComplianceSnapshot:
    """Point-in-time compliance state"""
    timestamp: datetime
    period: str
    framework_coverage: Dict[str, float]
    control_states: Dict[str, str]
    risk_assessment: Dict[str, Any]
    critical_issues: List[Dict[str, Any]]
    remediation_activities: List[Dict[str, Any]]
    audit_events: List[Dict[str, Any]]
    metadata: Dict[str, Any]

@dataclass
class ComplianceTimeline:
    """Timeline of compliance evolution"""
    start_date: datetime
    end_date: datetime
    snapshots: List[ComplianceSnapshot]
    key_events: List[Dict[str, Any]]
    trends: Dict[str, Any]

class HistoricalSimulator:
    """
    Historical Compliance State Simulator

    Replays past audit states, enabling temporal queries like:
    - "What was our GDPR compliance in Q1 2024?"
    - "Show me the timeline of critical control implementation"
    - "How did our risk profile change over the past year?"
    """

    def __init__(self, data_dir: Path):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Snapshot storage
        self.snapshots_dir = self.data_dir / "snapshots"
        self.snapshots_dir.mkdir(exist_ok=True)

        # Timeline cache
        self.timeline_cache: Dict[str, ComplianceTimeline] = {}

    def capture_snapshot(
        self,
        timestamp: datetime,
        unified_index: Dict,
        additional_context: Optional[Dict] = None
    ) -> ComplianceSnapshot:
        """
        Capture current compliance state as snapshot

        Creates point-in-time record of complete compliance posture
        """
        metrics = unified_index.get("compliance_metrics_unified", {})
        mappings = unified_index.get("cross_framework_mappings", {})

        # Extract framework coverage
        coverage = metrics.get("overall_coverage", {})
        framework_coverage = {
            k: self._parse_percentage(v)
            for k, v in coverage.items()
        }

        # Extract control states
        control_states = {}
        for domain, controls in mappings.items():
            if isinstance(controls, list):
                for control in controls:
                    control_states[control['unified_id']] = control['implementation_status']

        # Risk assessment
        by_risk = metrics.get("by_risk_level", {})
        risk_assessment = {
            "critical": self._parse_percentage(by_risk.get("critical", "0%")),
            "high": self._parse_percentage(by_risk.get("high", "0%")),
            "medium": self._parse_percentage(by_risk.get("medium", "0%")),
            "low": self._parse_percentage(by_risk.get("low", "0%")),
            "overall_risk_score": self._calculate_risk_score(by_risk)
        }

        # Critical issues
        critical_issues = []
        for domain, controls in mappings.items():
            if isinstance(controls, list):
                for control in controls:
                    if control['risk_level'] == 'CRITICAL' and control['implementation_status'] != 'implemented':
                        critical_issues.append({
                            "control_id": control['unified_id'],
                            "description": control['description'],
                            "frameworks": [m['framework'] for m in control['mappings']]
                        })

        # Create snapshot
        snapshot = ComplianceSnapshot(
            timestamp=timestamp,
            period=self._format_period(timestamp),
            framework_coverage=framework_coverage,
            control_states=control_states,
            risk_assessment=risk_assessment,
            critical_issues=critical_issues,
            remediation_activities=[],
            audit_events=[],
            metadata={
                "snapshot_id": hashlib.sha256(f"{timestamp.isoformat()}".encode()).hexdigest()[:16],
                "total_controls": len(control_states),
                "additional_context": additional_context or {}
            }
        )

        # Persist snapshot
        self._save_snapshot(snapshot)

        print(f"[Historical Simulator] Captured snapshot: {snapshot.period} (ID: {snapshot.metadata['snapshot_id']})")
        return snapshot

    def query_historical_state(
        self,
        query_date: datetime,
        framework: Optional[str] = None
    ) -> Optional[ComplianceSnapshot]:
        """
        Query compliance state at specific point in time

        Returns nearest snapshot to requested date
        """
        snapshots = self._load_all_snapshots()

        if not snapshots:
            print(f"[Historical Simulator] No snapshots available")
            raise NotImplementedError("TODO: Implement this function")

        # Find closest snapshot
        closest = min(
            snapshots,
            key=lambda s: abs((s.timestamp - query_date).total_seconds())
        )

        time_diff = abs((closest.timestamp - query_date).days)
        print(f"[Historical Simulator] Retrieved snapshot from {closest.period} ({time_diff} days from query)")

        return closest

    def generate_timeline(
        self,
        start_date: datetime,
        end_date: datetime,
        framework: Optional[str] = None
    ) -> ComplianceTimeline:
        """
        Generate compliance timeline between dates

        Shows evolution of compliance posture over time
        """
        snapshots = self._load_snapshots_in_range(start_date, end_date)

        if not snapshots:
            print(f"[Historical Simulator] No snapshots found in range")
            return ComplianceTimeline(
                start_date=start_date,
                end_date=end_date,
                snapshots=[],
                key_events=[],
                trends={}
            )

        # Identify key events
        key_events = self._identify_key_events(snapshots, framework)

        # Calculate trends
        trends = self._calculate_trends(snapshots, framework)

        timeline = ComplianceTimeline(
            start_date=start_date,
            end_date=end_date,
            snapshots=snapshots,
            key_events=key_events,
            trends=trends
        )

        print(f"[Historical Simulator] Generated timeline: {len(snapshots)} snapshots, {len(key_events)} key events")

        return timeline

    def simulate_historical_query(self, natural_language_query: str) -> Dict[str, Any]:
        """
        Process natural language historical query

        Examples:
        - "What was our GDPR compliance in Q1 2024?"
        - "Show me how DORA compliance changed over the past year"
        - "When did we achieve 90% MiCA compliance?"
        """
        # Parse query (simplified - in production, use NLP)
        query_lower = natural_language_query.lower()

        # Extract framework
        framework = None
        for fw in ['gdpr', 'dora', 'mica', 'amld6']:
            if fw in query_lower:
                framework = fw
                break

        # Extract time reference
        query_date = self._parse_time_reference(query_lower)

        if not query_date:
            return {
                "error": "Could not parse time reference from query",
                "query": natural_language_query
            }

        # Query snapshot
        snapshot = self.query_historical_state(query_date, framework)

        if not snapshot:
            return {
                "error": "No historical data available for requested period",
                "query": natural_language_query,
                "requested_date": query_date.isoformat()
            }

        # Format response
        return self._format_query_response(snapshot, framework, natural_language_query)

    def generate_historical_report(
        self,
        output_path: Path,
        period: str = "last_year"
    ) -> bool:
        """
        Generate comprehensive historical compliance report

        Analyzes compliance evolution over specified period
        """
        # Determine date range
        end_date = datetime.now()
        if period == "last_year":
            start_date = end_date - timedelta(days=365)
        elif period == "last_quarter":
            start_date = end_date - timedelta(days=90)
        elif period == "last_month":
            start_date = end_date - timedelta(days=30)
        else:
            start_date = end_date - timedelta(days=365)

        # Generate timeline
        timeline = self.generate_timeline(start_date, end_date)

        if not timeline.snapshots:
            print(f"[Historical Simulator] No data for historical report")
            return False

        # Generate report
        report = self._generate_timeline_report(timeline)

        output_path.write_text(report, encoding='utf-8')
        print(f"[Historical Simulator] Generated historical report: {output_path}")

        return True

    def export_timeline_data(self, output_path: Path, format: str = "json") -> bool:
        """
        Export timeline data for external analysis

        Supports JSON and CSV formats
        """
        snapshots = self._load_all_snapshots()

        if format == "json":
            data = []
            for snapshot in snapshots:
                data.append({
                    "timestamp": snapshot.timestamp.isoformat(),
                    "period": snapshot.period,
                    "framework_coverage": snapshot.framework_coverage,
                    "risk_score": snapshot.risk_assessment["overall_risk_score"],
                    "critical_issues_count": len(snapshot.critical_issues),
                    "total_controls": snapshot.metadata["total_controls"]
                })

            output_path.write_text(json.dumps(data, indent=2), encoding='utf-8')

        elif format == "csv":
            import csv
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    "Timestamp", "Period", "GDPR", "DORA", "MiCA", "AMLD6",
                    "Risk Score", "Critical Issues", "Total Controls"
                ])

                for snapshot in snapshots:
                    writer.writerow([
                        snapshot.timestamp.isoformat(),
                        snapshot.period,
                        snapshot.framework_coverage.get('gdpr', 0),
                        snapshot.framework_coverage.get('dora', 0),
                        snapshot.framework_coverage.get('mica', 0),
                        snapshot.framework_coverage.get('amld6', 0),
                        snapshot.risk_assessment["overall_risk_score"],
                        len(snapshot.critical_issues),
                        snapshot.metadata["total_controls"]
                    ])

        print(f"[Historical Simulator] Exported timeline data: {output_path}")
        return True

    # Private helper methods

    def _parse_percentage(self, value: Any) -> float:
        """Parse percentage value"""
        if isinstance(value, str):
            return float(value.strip('%'))
        return float(value) if value else 0.0

    def _calculate_risk_score(self, by_risk: Dict) -> float:
        """Calculate overall risk score (0-100, lower is better)"""
        critical = 100 - self._parse_percentage(by_risk.get("critical", "100%"))
        high = 100 - self._parse_percentage(by_risk.get("high", "100%"))
        medium = 100 - self._parse_percentage(by_risk.get("medium", "100%"))

        # Weighted score: critical 50%, high 30%, medium 20%
        score = (critical * 0.5) + (high * 0.3) + (medium * 0.2)
        return round(score, 2)

    def _format_period(self, timestamp: datetime) -> str:
        """Format timestamp as period string"""
        quarter = (timestamp.month - 1) // 3 + 1
        return f"{timestamp.year}-Q{quarter}"

    def _save_snapshot(self, snapshot: ComplianceSnapshot):
        """Persist snapshot to disk"""
        snapshot_file = self.snapshots_dir / f"snapshot_{snapshot.timestamp.strftime('%Y%m%d_%H%M%S')}.json"

        data = {
            "timestamp": snapshot.timestamp.isoformat(),
            "period": snapshot.period,
            "framework_coverage": snapshot.framework_coverage,
            "control_states": snapshot.control_states,
            "risk_assessment": snapshot.risk_assessment,
            "critical_issues": snapshot.critical_issues,
            "remediation_activities": snapshot.remediation_activities,
            "audit_events": snapshot.audit_events,
            "metadata": snapshot.metadata
        }

        snapshot_file.write_text(json.dumps(data, indent=2), encoding='utf-8')

    def _load_snapshot(self, snapshot_file: Path) -> ComplianceSnapshot:
        """Load snapshot from disk"""
        data = json.loads(snapshot_file.read_text(encoding='utf-8'))

        return ComplianceSnapshot(
            timestamp=datetime.fromisoformat(data['timestamp']),
            period=data['period'],
            framework_coverage=data['framework_coverage'],
            control_states=data['control_states'],
            risk_assessment=data['risk_assessment'],
            critical_issues=data['critical_issues'],
            remediation_activities=data['remediation_activities'],
            audit_events=data['audit_events'],
            metadata=data['metadata']
        )

    def _load_all_snapshots(self) -> List[ComplianceSnapshot]:
        """Load all snapshots"""
        snapshots = []
        for snapshot_file in sorted(self.snapshots_dir.glob("snapshot_*.json")):
            snapshots.append(self._load_snapshot(snapshot_file))
        return sorted(snapshots, key=lambda s: s.timestamp)

    def _load_snapshots_in_range(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[ComplianceSnapshot]:
        """Load snapshots within date range"""
        all_snapshots = self._load_all_snapshots()
        return [
            s for s in all_snapshots
            if start_date <= s.timestamp <= end_date
        ]

    def _identify_key_events(
        self,
        snapshots: List[ComplianceSnapshot],
        framework: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Identify significant events in timeline"""
        events = []

        for i in range(1, len(snapshots)):
            prev = snapshots[i-1]
            curr = snapshots[i]

            # Check for significant coverage changes
            for fw, curr_cov in curr.framework_coverage.items():
                if framework and fw != framework:
                    continue

                prev_cov = prev.framework_coverage.get(fw, 0)
                delta = curr_cov - prev_cov

                if abs(delta) >= 5:  # 5% threshold
                    events.append({
                        "type": "coverage_change",
                        "timestamp": curr.timestamp,
                        "period": curr.period,
                        "framework": fw.upper(),
                        "change": delta,
                        "description": f"{fw.upper()} compliance {'increased' if delta > 0 else 'decreased'} by {abs(delta):.1f}%"
                    })

            # Check for critical issue resolution
            prev_critical = len(prev.critical_issues)
            curr_critical = len(curr.critical_issues)

            if prev_critical > curr_critical:
                events.append({
                    "type": "critical_resolution",
                    "timestamp": curr.timestamp,
                    "period": curr.period,
                    "resolved_count": prev_critical - curr_critical,
                    "description": f"Resolved {prev_critical - curr_critical} critical issue(s)"
                })

            # Check for milestone achievements
            for fw, cov in curr.framework_coverage.items():
                prev_cov = prev.framework_coverage.get(fw, 0)
                if prev_cov < 90 <= cov:
                    events.append({
                        "type": "milestone",
                        "timestamp": curr.timestamp,
                        "period": curr.period,
                        "framework": fw.upper(),
                        "description": f"{fw.upper()} achieved 90% compliance threshold"
                    })

        return events

    def _calculate_trends(
        self,
        snapshots: List[ComplianceSnapshot],
        framework: Optional[str]
    ) -> Dict[str, Any]:
        """Calculate compliance trends"""
        if len(snapshots) < 2:
            return {}

        first = snapshots[0]
        last = snapshots[-1]

        trends = {
            "period": f"{first.period} to {last.period}",
            "duration_days": (last.timestamp - first.timestamp).days
        }

        # Framework coverage trends
        for fw in ['gdpr', 'dora', 'mica', 'amld6']:
            if framework and fw != framework:
                continue

            first_cov = first.framework_coverage.get(fw, 0)
            last_cov = last.framework_coverage.get(fw, 0)
            delta = last_cov - first_cov

            trends[f"{fw}_trend"] = {
                "start": first_cov,
                "end": last_cov,
                "change": delta,
                "direction": "improving" if delta > 0 else "declining" if delta < 0 else "stable"
            }

        # Risk trend
        first_risk = first.risk_assessment["overall_risk_score"]
        last_risk = last.risk_assessment["overall_risk_score"]

        trends["risk_trend"] = {
            "start": first_risk,
            "end": last_risk,
            "change": last_risk - first_risk,
            "direction": "improving" if last_risk < first_risk else "worsening" if last_risk > first_risk else "stable"
        }

        return trends

    def _parse_time_reference(self, query: str) -> Optional[datetime]:
        """Parse time reference from query"""
        now = datetime.now()

        # Simple patterns (in production, use sophisticated NLP)
        if "q1 2024" in query:
            return datetime(2024, 2, 15)
        elif "q2 2024" in query:
            return datetime(2024, 5, 15)
        elif "q3 2024" in query:
            return datetime(2024, 8, 15)
        elif "q4 2024" in query:
            return datetime(2024, 11, 15)
        elif "last year" in query:
            return now - timedelta(days=365)
        elif "last quarter" in query:
            return now - timedelta(days=90)
        elif "last month" in query:
            return now - timedelta(days=30)
        else:
            return now

    def _format_query_response(
        self,
        snapshot: ComplianceSnapshot,
        framework: Optional[str],
        original_query: str
    ) -> Dict[str, Any]:
        """Format query response"""
        response = {
            "query": original_query,
            "period": snapshot.period,
            "timestamp": snapshot.timestamp.isoformat()
        }

        if framework:
            coverage = snapshot.framework_coverage.get(framework, 0)
            response["answer"] = f"{framework.upper()} compliance in {snapshot.period} was {coverage:.1f}%"
            response["framework_coverage"] = {framework: coverage}
        else:
            response["answer"] = f"Overall compliance in {snapshot.period}"
            response["framework_coverage"] = snapshot.framework_coverage

        response["risk_score"] = snapshot.risk_assessment["overall_risk_score"]
        response["critical_issues"] = len(snapshot.critical_issues)

        return response

    def _generate_timeline_report(self, timeline: ComplianceTimeline) -> str:
        """Generate timeline report"""
        report = f"""
# HISTORICAL COMPLIANCE REPORT
## Timeline: {timeline.start_date.strftime('%Y-%m-%d')} to {timeline.end_date.strftime('%Y-%m-%d')}

**Report Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Snapshots Analyzed:** {len(timeline.snapshots)}
**Key Events:** {len(timeline.key_events)}

---

## EXECUTIVE SUMMARY

{self._generate_timeline_summary(timeline)}

---

## COMPLIANCE EVOLUTION

{self._generate_evolution_charts(timeline)}

---

## KEY EVENTS

{self._generate_events_list(timeline.key_events)}

---

## TREND ANALYSIS

{self._generate_trends_section(timeline.trends)}

---

*Generated by SSID Historical Simulator*
"""
        return report

    def _generate_timeline_summary(self, timeline: ComplianceTimeline) -> str:
        """Generate timeline summary"""
        if not timeline.snapshots:
            return "No data available for analysis."

        first = timeline.snapshots[0]
        last = timeline.snapshots[-1]

        summary = f"Compliance posture analysis from **{first.period}** to **{last.period}**.\n\n"

        for fw in ['gdpr', 'dora', 'mica', 'amld6']:
            first_cov = first.framework_coverage.get(fw, 0)
            last_cov = last.framework_coverage.get(fw, 0)
            delta = last_cov - first_cov

            trend = "↑" if delta > 0 else "↓" if delta < 0 else "→"
            summary += f"- **{fw.upper()}:** {first_cov:.1f}% → {last_cov:.1f}% ({trend} {abs(delta):.1f}%)\n"

        return summary

    def _generate_evolution_charts(self, timeline: ComplianceTimeline) -> str:
        """Generate text-based evolution visualization"""
        # Simple ASCII chart representation
        chart = "| Period | GDPR | DORA | MiCA | AMLD6 | Risk |\n"
        chart += "|--------|------|------|------|-------|------|\n"

        for snapshot in timeline.snapshots[-5:]:  # Last 5 snapshots
            chart += f"| {snapshot.period} | "
            chart += f"{snapshot.framework_coverage.get('gdpr', 0):.0f}% | "
            chart += f"{snapshot.framework_coverage.get('dora', 0):.0f}% | "
            chart += f"{snapshot.framework_coverage.get('mica', 0):.0f}% | "
            chart += f"{snapshot.framework_coverage.get('amld6', 0):.0f}% | "
            chart += f"{snapshot.risk_assessment['overall_risk_score']:.1f} |\n"

        return chart

    def _generate_events_list(self, events: List[Dict]) -> str:
        """Generate events list"""
        if not events:
            return "No significant events recorded."

        text = ""
        for event in events:
            text += f"\n### {event['period']} - {event['description']}\n"
            text += f"- Type: {event['type']}\n"
            text += f"- Date: {event['timestamp'].strftime('%Y-%m-%d')}\n"

        return text

    def _generate_trends_section(self, trends: Dict) -> str:
        """Generate trends section"""
        if not trends:
            return "Insufficient data for trend analysis."

        text = f"**Analysis Period:** {trends.get('period', 'N/A')} ({trends.get('duration_days', 0)} days)\n\n"

        for key, value in trends.items():
            if key.endswith('_trend') and isinstance(value, dict):
                fw = key.replace('_trend', '').upper()
                text += f"**{fw}:**\n"
                text += f"- Start: {value['start']:.1f}%\n"
                text += f"- End: {value['end']:.1f}%\n"
                text += f"- Change: {value['change']:+.1f}%\n"
                text += f"- Direction: {value['direction']}\n\n"

        return text

def demo_historical_simulation():
    """Demonstrate historical simulation capabilities"""
    print("=== SSID Historical Compliance Simulator Demo ===\n")

    # Initialize simulator
    simulator = HistoricalSimulator(Path("./historical_data"))

    # Load current compliance state
    unified_index_path = Path("C:/Users/bibel/Documents/Github/SSID/23_compliance/mappings/compliance_unified_index.yaml")

    if unified_index_path.exists():
        print("1. Loading current compliance state...")
        with open(unified_index_path, 'r', encoding='utf-8') as f:
            unified_index = yaml.safe_load(f)

        # Simulate historical snapshots (backdated for demo)
        print("\n2. Creating historical snapshots...")
        base_date = datetime.now()

        for i in range(4, -1, -1):
            snapshot_date = base_date - timedelta(days=i * 90)
            snapshot = simulator.capture_snapshot(snapshot_date, unified_index)

        # Query historical state
        print("\n3. Querying historical state...")
        query_date = base_date - timedelta(days=180)
        snapshot = simulator.query_historical_state(query_date)

        if snapshot:
            print(f"   Period: {snapshot.period}")
            print(f"   GDPR: {snapshot.framework_coverage.get('gdpr', 0):.1f}%")
            print(f"   Risk Score: {snapshot.risk_assessment['overall_risk_score']:.1f}")

        # Natural language query
        print("\n4. Processing natural language queries...")
        queries = [
            "What was our GDPR compliance in Q1 2024?",
            "Show me DORA compliance last quarter"
        ]

        for query in queries:
            result = simulator.simulate_historical_query(query)
            print(f"\n   Q: {query}")
            print(f"   A: {result.get('answer', 'No data')}")

        # Generate timeline
        print("\n5. Generating compliance timeline...")
        timeline = simulator.generate_timeline(
            base_date - timedelta(days=365),
            base_date
        )
        print(f"   Snapshots: {len(timeline.snapshots)}")
        print(f"   Key events: {len(timeline.key_events)}")

        # Export data
        print("\n6. Exporting timeline data...")
        export_path = Path("./historical_data/timeline_export.json")
        simulator.export_timeline_data(export_path, format="json")

        print("\n=== Demo Complete ===")
    else:
        print(f"Unified index not found at {unified_index_path}")

if __name__ == "__main__":
    demo_historical_simulation()
