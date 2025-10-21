#!/usr/bin/env python3
"""
SSID Snapshot Diff Engine
Semantic Compliance Change Analysis

Performs semantic diffs between compliance snapshots, identifying:
- Which regulatory articles/paragraphs changed
- Which SSID modules were affected
- Root cause analysis of compliance shifts
"""

import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from collections import defaultdict
from difflib import SequenceMatcher

@dataclass
class RegulatoryChange:
    """Detected change in regulatory compliance"""
    change_id: str
    change_type: str  # "new_requirement", "modified_requirement", "removed_requirement"
    framework: str
    article_reference: str
    control_id: str
    previous_state: Optional[str]
    new_state: str
    affected_modules: List[str]
    impact_severity: str
    description: str

@dataclass
class ModuleImpact:
    """Impact analysis for SSID module"""
    module_name: str
    changes_count: int
    critical_changes: int
    high_priority_changes: int
    compliance_delta: float  # Change in compliance percentage
    affected_controls: List[str]
    required_actions: List[str]

@dataclass
class SnapshotDiff:
    """Difference between two compliance snapshots"""
    diff_id: str
    from_snapshot: str
    to_snapshot: str
    from_date: datetime
    to_date: datetime
    time_delta_days: int

    # Changes
    regulatory_changes: List[RegulatoryChange]
    module_impacts: List[ModuleImpact]
    framework_deltas: Dict[str, float]

    # Summary statistics
    total_changes: int
    critical_changes: int
    modules_affected: int

    # Semantic analysis
    root_causes: List[Dict]
    trending_issues: List[str]
    recommendations: List[str]

class SnapshotDiffEngine:
    """
    Semantic Snapshot Diff Engine

    Analyzes differences between compliance snapshots with semantic understanding:
    - Identifies regulatory article changes
    - Maps changes to affected modules
    - Performs root cause analysis
    - Generates actionable recommendations
    """

    def __init__(
        self,
        snapshots_dir: Path,
        unified_index_path: Path
    ):
        self.snapshots_dir = Path(snapshots_dir)
        self.unified_index_path = Path(unified_index_path)

        # Load unified index for reference
        with open(self.unified_index_path, 'r', encoding='utf-8') as f:
            self.unified_index = yaml.safe_load(f)

        # Build article-to-module mapping
        self.article_to_modules = self._build_article_module_mapping()

    def compute_diff(
        self,
        from_snapshot_id: str,
        to_snapshot_id: str
    ) -> SnapshotDiff:
        """
        Compute semantic diff between two snapshots

        Returns detailed analysis of changes, impacts, and recommendations
        """
        print(f"[Snapshot Diff] Computing diff: {from_snapshot_id} -> {to_snapshot_id}")

        # Load snapshots
        from_snapshot = self._load_snapshot(from_snapshot_id)
        to_snapshot = self._load_snapshot(to_snapshot_id)

        if not from_snapshot or not to_snapshot:
            raise ValueError("Snapshots not found")

        diff_id = f"diff_{from_snapshot_id}_{to_snapshot_id}"

        # Calculate time delta
        time_delta = (to_snapshot['timestamp'] - from_snapshot['timestamp']).days

        print(f"  Period: {from_snapshot['period']} to {to_snapshot['period']} ({time_delta} days)")

        # Detect regulatory changes
        regulatory_changes = self._detect_regulatory_changes(from_snapshot, to_snapshot)
        print(f"  Regulatory changes: {len(regulatory_changes)}")

        # Analyze module impacts
        module_impacts = self._analyze_module_impacts(regulatory_changes, from_snapshot, to_snapshot)
        print(f"  Modules affected: {len(module_impacts)}")

        # Calculate framework deltas
        framework_deltas = self._calculate_framework_deltas(from_snapshot, to_snapshot)

        # Count change severity
        critical_changes = sum(1 for c in regulatory_changes if c.impact_severity == 'CRITICAL')
        total_changes = len(regulatory_changes)

        # Perform semantic analysis
        root_causes = self._analyze_root_causes(regulatory_changes, module_impacts)
        trending_issues = self._identify_trending_issues(regulatory_changes)
        recommendations = self._generate_recommendations(
            regulatory_changes,
            module_impacts,
            framework_deltas
        )

        # Create diff
        diff = SnapshotDiff(
            diff_id=diff_id,
            from_snapshot=from_snapshot_id,
            to_snapshot=to_snapshot_id,
            from_date=from_snapshot['timestamp'],
            to_date=to_snapshot['timestamp'],
            time_delta_days=time_delta,
            regulatory_changes=regulatory_changes,
            module_impacts=module_impacts,
            framework_deltas=framework_deltas,
            total_changes=total_changes,
            critical_changes=critical_changes,
            modules_affected=len(module_impacts),
            root_causes=root_causes,
            trending_issues=trending_issues,
            recommendations=recommendations
        )

        return diff

    def query_article_changes(
        self,
        from_date: datetime,
        to_date: datetime,
        framework: Optional[str] = None,
        article: Optional[str] = None
    ) -> List[RegulatoryChange]:
        """
        Query regulatory article changes in date range

        Example queries:
        - "Which GDPR articles changed between Q2 2024 and Q3 2025?"
        - "What changes affected DORA Art. 6?"
        """
        print(f"[Snapshot Diff] Querying article changes: {from_date.date()} to {to_date.date()}")

        # Find snapshots in range
        snapshots = self._find_snapshots_in_range(from_date, to_date)

        if len(snapshots) < 2:
            print(f"  Insufficient snapshots for comparison")
            return []

        # Compute diffs between consecutive snapshots
        all_changes = []

        for i in range(len(snapshots) - 1):
            from_snap = snapshots[i]
            to_snap = snapshots[i + 1]

            changes = self._detect_regulatory_changes(from_snap, to_snap)

            # Filter by framework/article if specified
            if framework:
                changes = [c for c in changes if c.framework.lower() == framework.lower()]

            if article:
                changes = [c for c in changes if article.lower() in c.article_reference.lower()]

            all_changes.extend(changes)

        print(f"  Found {len(all_changes)} regulatory changes")

        return all_changes

    def query_module_impact_timeline(
        self,
        module_name: str,
        from_date: datetime,
        to_date: datetime
    ) -> Dict:
        """
        Query impact timeline for specific module

        Shows how compliance for a module evolved over time
        """
        print(f"[Snapshot Diff] Querying module impact timeline: {module_name}")

        snapshots = self._find_snapshots_in_range(from_date, to_date)

        timeline = {
            "module": module_name,
            "period": f"{from_date.date()} to {to_date.date()}",
            "snapshots": [],
            "total_changes": 0,
            "trend": "unknown"
        }

        for snapshot in snapshots:
            # Find controls affecting this module
            module_controls = [
                ctrl_id for ctrl_id, state in snapshot.get('control_states', {}).items()
                if module_name in self._get_modules_for_control(ctrl_id)
            ]

            implemented = sum(
                1 for ctrl in module_controls
                if snapshot.get('control_states', {}).get(ctrl) == 'implemented'
            )

            timeline["snapshots"].append({
                "date": snapshot['timestamp'].isoformat(),
                "period": snapshot['period'],
                "controls_total": len(module_controls),
                "controls_implemented": implemented,
                "compliance_rate": (implemented / len(module_controls) * 100) if module_controls else 0
            })

        # Determine trend
        if len(timeline["snapshots"]) >= 2:
            first_rate = timeline["snapshots"][0]["compliance_rate"]
            last_rate = timeline["snapshots"][-1]["compliance_rate"]

            if last_rate > first_rate + 5:
                timeline["trend"] = "improving"
            elif last_rate < first_rate - 5:
                timeline["trend"] = "declining"
            else:
                timeline["trend"] = "stable"

        print(f"  Trend: {timeline['trend']}")

        return timeline

    def export_diff_report(self, diff: SnapshotDiff, output_path: Path, format: str = "markdown"):
        """
        Export diff report

        Formats: markdown, json, html
        """
        if format == "markdown":
            self._export_diff_markdown(diff, output_path)
        elif format == "json":
            self._export_diff_json(diff, output_path)
        elif format == "html":
            self._export_diff_html(diff, output_path)

        print(f"[Snapshot Diff] Exported diff report: {output_path}")

    def _detect_regulatory_changes(
        self,
        from_snapshot: Dict,
        to_snapshot: Dict
    ) -> List[RegulatoryChange]:
        """Detect regulatory changes between snapshots"""
        changes = []

        from_controls = from_snapshot.get('control_states', {})
        to_controls = to_snapshot.get('control_states', {})

        # Find all controls (union of both snapshots)
        all_controls = set(from_controls.keys()) | set(to_controls.keys())

        for control_id in all_controls:
            from_state = from_controls.get(control_id)
            to_state = to_controls.get(control_id)

            if from_state != to_state:
                # State changed
                change_type = self._determine_change_type(from_state, to_state)

                control_info = self._get_control_info(control_id)

                if control_info:
                    # Determine which frameworks/articles affected
                    for mapping in control_info.get('mappings', []):
                        change = RegulatoryChange(
                            change_id=f"{control_id}_{mapping['framework']}_{to_snapshot['period']}",
                            change_type=change_type,
                            framework=mapping['framework'],
                            article_reference=mapping.get('article', 'N/A'),
                            control_id=control_id,
                            previous_state=from_state,
                            new_state=to_state,
                            affected_modules=control_info.get('ssid_modules', []),
                            impact_severity=control_info.get('risk_level', 'MEDIUM'),
                            description=control_info.get('description', 'No description')
                        )
                        changes.append(change)

        return changes

    def _analyze_module_impacts(
        self,
        changes: List[RegulatoryChange],
        from_snapshot: Dict,
        to_snapshot: Dict
    ) -> List[ModuleImpact]:
        """Analyze impact of changes on SSID modules"""
        module_changes = defaultdict(list)

        for change in changes:
            for module in change.affected_modules:
                module_changes[module].append(change)

        impacts = []

        for module, module_change_list in module_changes.items():
            critical_changes = sum(1 for c in module_change_list if c.impact_severity == 'CRITICAL')
            high_changes = sum(1 for c in module_change_list if c.impact_severity == 'HIGH')

            # Calculate compliance delta
            from_compliance = self._get_module_compliance(module, from_snapshot)
            to_compliance = self._get_module_compliance(module, to_snapshot)
            delta = to_compliance - from_compliance

            # Generate required actions
            required_actions = []
            if critical_changes > 0:
                required_actions.append(f"Address {critical_changes} critical change(s) immediately")
            if high_changes > 0:
                required_actions.append(f"Implement {high_changes} high-priority change(s)")
            if delta < -5:
                required_actions.append("Investigate compliance decline")

            impact = ModuleImpact(
                module_name=module,
                changes_count=len(module_change_list),
                critical_changes=critical_changes,
                high_priority_changes=high_changes,
                compliance_delta=delta,
                affected_controls=[c.control_id for c in module_change_list],
                required_actions=required_actions
            )
            impacts.append(impact)

        # Sort by severity
        impacts.sort(key=lambda x: (x.critical_changes, x.high_priority_changes), reverse=True)

        return impacts

    def _calculate_framework_deltas(
        self,
        from_snapshot: Dict,
        to_snapshot: Dict
    ) -> Dict[str, float]:
        """Calculate framework compliance deltas"""
        deltas = {}

        from_fw = from_snapshot.get('framework_coverage', {})
        to_fw = to_snapshot.get('framework_coverage', {})

        for fw in set(from_fw.keys()) | set(to_fw.keys()):
            from_val = from_fw.get(fw, 0)
            to_val = to_fw.get(fw, 0)
            deltas[fw] = to_val - from_val

        return deltas

    def _analyze_root_causes(
        self,
        changes: List[RegulatoryChange],
        impacts: List[ModuleImpact]
    ) -> List[Dict]:
        """Analyze root causes of compliance changes"""
        causes = []

        # Cause 1: New regulatory requirements
        new_reqs = [c for c in changes if c.change_type == 'new_requirement']
        if new_reqs:
            causes.append({
                "cause": "New Regulatory Requirements",
                "count": len(new_reqs),
                "description": f"{len(new_reqs)} new compliance requirements introduced",
                "frameworks": list(set(c.framework for c in new_reqs))
            })

        # Cause 2: Implementation gaps
        impl_gaps = [c for c in changes if c.new_state in ['planned', 'partial']]
        if impl_gaps:
            causes.append({
                "cause": "Implementation Gaps",
                "count": len(impl_gaps),
                "description": f"{len(impl_gaps)} controls not fully implemented",
                "affected_modules": list(set(m for c in impl_gaps for m in c.affected_modules))
            })

        # Cause 3: Module-specific issues
        critical_modules = [m for m in impacts if m.critical_changes > 0]
        if critical_modules:
            causes.append({
                "cause": "Module-Specific Issues",
                "count": len(critical_modules),
                "description": f"{len(critical_modules)} modules with critical compliance issues",
                "modules": [m.module_name for m in critical_modules]
            })

        return causes

    def _identify_trending_issues(self, changes: List[RegulatoryChange]) -> List[str]:
        """Identify trending compliance issues"""
        trends = []

        # Count by framework
        framework_counts = defaultdict(int)
        for change in changes:
            framework_counts[change.framework] += 1

        # Identify high-activity frameworks
        for framework, count in framework_counts.items():
            if count >= 3:
                trends.append(f"{framework} shows {count} regulatory changes")

        # Identify common articles
        article_counts = defaultdict(int)
        for change in changes:
            article_counts[change.article_reference] += 1

        for article, count in article_counts.items():
            if count >= 2:
                trends.append(f"Article {article} affected multiple controls")

        return trends

    def _generate_recommendations(
        self,
        changes: List[RegulatoryChange],
        impacts: List[ModuleImpact],
        deltas: Dict[str, float]
    ) -> List[str]:
        """Generate actionable recommendations"""
        recs = []

        # Critical changes
        critical = [c for c in changes if c.impact_severity == 'CRITICAL']
        if critical:
            recs.append(f"URGENT: Address {len(critical)} critical regulatory changes within 7 days")

        # Declining frameworks
        declining = {fw: delta for fw, delta in deltas.items() if delta < -5}
        if declining:
            for fw, delta in declining.items():
                recs.append(f"Investigate {fw.upper()} compliance decline ({delta:+.1f}%)")

        # High-impact modules
        high_impact_modules = [m for m in impacts if m.critical_changes > 0 or m.compliance_delta < -5]
        if high_impact_modules:
            for module in high_impact_modules[:3]:  # Top 3
                recs.append(f"Review module {module.module_name}: {module.changes_count} changes, {module.compliance_delta:+.1f}% compliance")

        if not recs:
            recs.append("Continue monitoring compliance metrics quarterly")

        return recs

    def _export_diff_markdown(self, diff: SnapshotDiff, output_path: Path):
        """Export diff as markdown report"""

        report = f"""# Compliance Snapshot Diff Report
## {diff.from_snapshot} → {diff.to_snapshot}

**Period:** {diff.from_date.strftime('%Y-%m-%d')} to {diff.to_date.strftime('%Y-%m-%d')} ({diff.time_delta_days} days)
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## Executive Summary

**Total Changes:** {diff.total_changes}
**Critical Changes:** {diff.critical_changes}
**Modules Affected:** {diff.modules_affected}

### Framework Compliance Deltas

| Framework | Change |
|-----------|--------|
"""

        for fw, delta in diff.framework_deltas.items():
            indicator = "↑" if delta > 0 else "↓" if delta < 0 else "→"
            report += f"| {fw.upper()} | {indicator} {delta:+.1f}% |\n"

        report += f"""

---

## Regulatory Changes

{len(diff.regulatory_changes)} regulatory changes detected:

"""

        for change in diff.regulatory_changes[:20]:  # Limit to 20
            report += f"""
### {change.control_id} - {change.framework} {change.article_reference}

**Type:** {change.change_type}
**Severity:** {change.impact_severity}
**State Change:** {change.previous_state or 'N/A'} → {change.new_state}
**Description:** {change.description}
**Affected Modules:** {', '.join(change.affected_modules)}

---
"""

        report += f"""
## Module Impact Analysis

{len(diff.module_impacts)} modules affected:

| Module | Changes | Critical | Delta |
|--------|---------|----------|-------|
"""

        for impact in diff.module_impacts:
            report += f"| {impact.module_name} | {impact.changes_count} | {impact.critical_changes} | {impact.compliance_delta:+.1f}% |\n"

        report += f"""

---

## Root Cause Analysis

"""

        for cause in diff.root_causes:
            report += f"### {cause['cause']}\n\n"
            report += f"{cause['description']}\n\n"
            if 'frameworks' in cause:
                report += f"**Frameworks:** {', '.join(cause['frameworks'])}\n\n"
            if 'modules' in cause:
                report += f"**Modules:** {', '.join(cause['modules'])}\n\n"

        report += f"""
---

## Trending Issues

"""

        for trend in diff.trending_issues:
            report += f"- {trend}\n"

        report += f"""

---

## Recommendations

"""

        for i, rec in enumerate(diff.recommendations, 1):
            report += f"{i}. {rec}\n"

        report += f"""

---

*Generated by SSID Snapshot Diff Engine*
"""

        output_path.write_text(report, encoding='utf-8')

    def _export_diff_json(self, diff: SnapshotDiff, output_path: Path):
        """Export diff as JSON"""
        data = {
            "diff_id": diff.diff_id,
            "from_snapshot": diff.from_snapshot,
            "to_snapshot": diff.to_snapshot,
            "from_date": diff.from_date.isoformat(),
            "to_date": diff.to_date.isoformat(),
            "time_delta_days": diff.time_delta_days,
            "summary": {
                "total_changes": diff.total_changes,
                "critical_changes": diff.critical_changes,
                "modules_affected": diff.modules_affected
            },
            "framework_deltas": diff.framework_deltas,
            "regulatory_changes": [
                {
                    "control_id": c.control_id,
                    "framework": c.framework,
                    "article": c.article_reference,
                    "change_type": c.change_type,
                    "severity": c.impact_severity,
                    "affected_modules": c.affected_modules
                }
                for c in diff.regulatory_changes
            ],
            "module_impacts": [
                {
                    "module": m.module_name,
                    "changes": m.changes_count,
                    "critical": m.critical_changes,
                    "compliance_delta": m.compliance_delta
                }
                for m in diff.module_impacts
            ],
            "root_causes": diff.root_causes,
            "recommendations": diff.recommendations
        }

        output_path.write_text(json.dumps(data, indent=2), encoding='utf-8')

    def _export_diff_html(self, diff: SnapshotDiff, output_path: Path):
        """Export diff as HTML (simplified)"""
        # Reuse markdown and add HTML wrapper
        md_path = output_path.with_suffix('.md')
        self._export_diff_markdown(diff, md_path)

        html = f"""<!DOCTYPE html>
<html><head><title>Snapshot Diff: {diff.diff_id}</title>
<style>body{{font-family:sans-serif;margin:40px;}}table{{border-collapse:collapse;}}th,td{{border:1px solid #ddd;padding:8px;}}</style>
</head><body>
<h1>Compliance Snapshot Diff</h1>
<p>From: {diff.from_snapshot} ({diff.from_date.date()})</p>
<p>To: {diff.to_snapshot} ({diff.to_date.date()})</p>
<p>See markdown report for details: <a href="{md_path.name}">{md_path.name}</a></p>
</body></html>"""

        output_path.write_text(html, encoding='utf-8')

    # Helper methods

    def _build_article_module_mapping(self) -> Dict:
        """Build mapping of regulatory articles to SSID modules"""
        mapping = defaultdict(list)

        mappings = self.unified_index.get('cross_framework_mappings', {})

        for domain, controls in mappings.items():
            if isinstance(controls, list):
                for control in controls:
                    for map_entry in control.get('mappings', []):
                        article = f"{map_entry['framework']}:{map_entry.get('article', 'N/A')}"
                        for module in control.get('ssid_modules', []):
                            if module not in mapping[article]:
                                mapping[article].append(module)

        return dict(mapping)

    def _load_snapshot(self, snapshot_id: str) -> Optional[Dict]:
        """Load snapshot by ID or period"""
        # Try loading from historical simulator snapshots
        for snapshot_file in self.snapshots_dir.glob("snapshot_*.json"):
            data = json.loads(snapshot_file.read_text(encoding='utf-8'))
            if data.get('period') == snapshot_id or snapshot_id in snapshot_file.stem:
                data['timestamp'] = datetime.fromisoformat(data['timestamp'])
                return data
 raise NotImplementedError("TODO: Implement this function")
        return None

    def _find_snapshots_in_range(self, from_date: datetime, to_date: datetime) -> List[Dict]:
        """Find snapshots in date range"""
        snapshots = []

        for snapshot_file in sorted(self.snapshots_dir.glob("snapshot_*.json")):
            data = json.loads(snapshot_file.read_text(encoding='utf-8'))
            timestamp = datetime.fromisoformat(data['timestamp'])
            data['timestamp'] = timestamp

            if from_date <= timestamp <= to_date:
                snapshots.append(data)

        return sorted(snapshots, key=lambda s: s['timestamp'])

    def _determine_change_type(self, from_state: Optional[str], to_state: str) -> str:
        """Determine type of change"""
        if from_state is None:
            return "new_requirement"
        elif to_state == "implemented" and from_state != "implemented":
            return "implemented"
        elif to_state != "implemented" and from_state == "implemented":
            return "compliance_regression"
        else:
            return "modified_requirement"

    def _get_control_info(self, control_id: str) -> Optional[Dict]:
        """Get control information from unified index"""
        mappings = self.unified_index.get('cross_framework_mappings', {})

        for domain, controls in mappings.items():
            if isinstance(controls, list):
                for control in controls:
                    if control.get('unified_id') == control_id:
                        return control
 raise NotImplementedError("TODO: Implement this function")
        return None

    def _get_modules_for_control(self, control_id: str) -> List[str]:
        """Get modules affected by control"""
        control_info = self._get_control_info(control_id)
        return control_info.get('ssid_modules', []) if control_info else []

    def _get_module_compliance(self, module: str, snapshot: Dict) -> float:
        """Calculate compliance rate for module in snapshot"""
        control_states = snapshot.get('control_states', {})

        module_controls = [
            ctrl_id for ctrl_id in control_states.keys()
            if module in self._get_modules_for_control(ctrl_id)
        ]

        if not module_controls:
            return 0.0

        implemented = sum(
            1 for ctrl in module_controls
            if control_states.get(ctrl) == 'implemented'
        )

        return (implemented / len(module_controls) * 100)

def main():
    """Main CLI entry point"""
    print("=== SSID Snapshot Diff Engine ===\n")

    # Paths
    snapshots_dir = Path("C:/Users/bibel/Documents/Github/SSID/23_compliance/ai_ml_ready/historical_data/snapshots")
    unified_index_path = Path("C:/Users/bibel/Documents/Github/SSID/23_compliance/mappings/compliance_unified_index.yaml")
    output_dir = Path("C:/Users/bibel/Documents/Github/SSID/23_compliance/ai_ml_ready/snapshot_diffs")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Initialize engine
    engine = SnapshotDiffEngine(snapshots_dir, unified_index_path)

    # List available snapshots
    snapshots = sorted(snapshots_dir.glob("snapshot_*.json"))

    if len(snapshots) < 2:
        print("Need at least 2 snapshots to compute diff")
        print("Run historical_simulator.py first to generate snapshots")
        return

    print(f"Found {len(snapshots)} snapshots")

    # Compute diff between first and last
    from_snap = snapshots[0].stem
    to_snap = snapshots[-1].stem

    print(f"\n1. Computing diff: {from_snap} -> {to_snap}...")
    diff = engine.compute_diff(from_snap, to_snap)

    # Export reports
    print("\n2. Exporting diff reports...")
    engine.export_diff_report(diff, output_dir / f"{diff.diff_id}.md", format="markdown")
    engine.export_diff_report(diff, output_dir / f"{diff.diff_id}.json", format="json")

    # Query example: article changes
    print("\n3. Example query: Article changes in period...")
    from_date = datetime.now() - timedelta(days=365)
    to_date = datetime.now()
    article_changes = engine.query_article_changes(from_date, to_date, framework="gdpr")

    print("\n=== Analysis Complete ===")
    print(f"\nDiff reports: {output_dir}")
    print(f"Total changes: {diff.total_changes}")
    print(f"Critical changes: {diff.critical_changes}")
    print(f"Modules affected: {diff.modules_affected}")

if __name__ == "__main__":
    from datetime import timedelta
    main()
