#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
yaml_vital_signs_trend.py - Historical YAML Ecology Trend Analysis
Author: edubrainboost ©2025 MIT License

Analyzes trends in YAML vital signs across quarters to detect:
- Degradation patterns (worsening metrics)
- Improvement trends (optimization effects)
- Stability assessment (consistent health)

Usage:
    python 12_tooling/quality/yaml_vital_signs_trend.py
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import argparse


class YAMLVitalSignsTrendAnalyzer:
    """Analyze trends in YAML vital signs over time."""

    def __init__(self, root_dir: Path = None):
        if root_dir is None:
            root_dir = Path(__file__).resolve().parents[2]

        self.root = root_dir
        self.vital_signs_dir = root_dir / "12_tooling" / "quality" / "vital_signs"

    def load_all_vital_signs(self) -> List[Dict]:
        """
        Load all historical vital signs reports.

        Returns:
            List of vital signs reports, sorted by quarter
        """
        if not self.vital_signs_dir.exists():
            return []

        reports = []

        for report_file in self.vital_signs_dir.glob("yaml_vital_signs_*.json"):
            try:
                with open(report_file, 'r', encoding='utf-8') as f:
                    report = json.load(f)
                    reports.append(report)
            except (json.JSONDecodeError, KeyError):
                continue

        # Sort by quarter
        reports.sort(key=lambda r: r.get('quarter', ''))

        return reports

    def calculate_trends(self, reports: List[Dict]) -> Dict:
        """
        Calculate trends from historical reports.

        Args:
            reports: List of vital signs reports

        Returns:
            Trend analysis dict
        """
        if len(reports) < 2:
            return {
                "trend_available": False,
                "reason": "Insufficient historical data (need >= 2 quarters)"
            }

        # Extract metrics over time
        quarters = []
        yaml_counts = []
        backup_ratios = []
        dedup_efficiencies = []
        retention_compliances = []

        for report in reports:
            quarters.append(report['quarter'])
            vital_signs = report['vital_signs']

            # YAML count
            yaml_counts.append(vital_signs['1_yaml_count']['live_yaml_count'])

            # Backup ratio
            backup_ratios.append(vital_signs['1_yaml_count']['backup_ratio'])

            # Deduplication efficiency
            dedup = vital_signs['3_deduplication_efficiency']['efficiency_pct']
            if dedup is not None:
                dedup_efficiencies.append(dedup)

            # Retention compliance
            retention = vital_signs['5_retention_compliance']['compliance_pct']
            if retention is not None:
                retention_compliances.append(retention)

        # Calculate trends
        trends = {
            "trend_available": True,
            "quarters_analyzed": len(reports),
            "time_span": f"{quarters[0]} to {quarters[-1]}",
            "metrics": {}
        }

        # YAML count trend
        if len(yaml_counts) >= 2:
            change = yaml_counts[-1] - yaml_counts[0]
            change_pct = (change / yaml_counts[0] * 100) if yaml_counts[0] > 0 else 0

            trends["metrics"]["yaml_count"] = {
                "start": yaml_counts[0],
                "end": yaml_counts[-1],
                "change": change,
                "change_pct": round(change_pct, 1),
                "trend": self._classify_trend(change_pct, "yaml_count")
            }

        # Backup ratio trend
        if len(backup_ratios) >= 2:
            change = backup_ratios[-1] - backup_ratios[0]
            change_pct = (change / backup_ratios[0] * 100) if backup_ratios[0] > 0 else 0

            trends["metrics"]["backup_ratio"] = {
                "start": backup_ratios[0],
                "end": backup_ratios[-1],
                "change": round(change, 2),
                "change_pct": round(change_pct, 1),
                "trend": self._classify_trend(change_pct, "backup_ratio")
            }

        # Deduplication efficiency trend
        if len(dedup_efficiencies) >= 2:
            change = dedup_efficiencies[-1] - dedup_efficiencies[0]
            change_pct = (change / dedup_efficiencies[0] * 100) if dedup_efficiencies[0] > 0 else 0

            trends["metrics"]["deduplication"] = {
                "start": dedup_efficiencies[0],
                "end": dedup_efficiencies[-1],
                "change": round(change, 2),
                "change_pct": round(change_pct, 1),
                "trend": self._classify_trend(change_pct, "deduplication")
            }

        # Retention compliance trend
        if len(retention_compliances) >= 2:
            change = retention_compliances[-1] - retention_compliances[0]
            change_pct = (change / retention_compliances[0] * 100) if retention_compliances[0] > 0 else 0

            trends["metrics"]["retention_compliance"] = {
                "start": retention_compliances[0],
                "end": retention_compliances[-1],
                "change": round(change, 2),
                "change_pct": round(change_pct, 1),
                "trend": self._classify_trend(change_pct, "retention_compliance")
            }

        return trends

    def _classify_trend(self, change_pct: float, metric: str) -> str:
        """
        Classify trend direction and health.

        Args:
            change_pct: Percentage change
            metric: Metric name

        Returns:
            Trend classification
        """
        # For some metrics, increase is bad; for others, increase is good
        if metric in ["backup_ratio", "deduplication"]:
            # Lower is better
            if change_pct < -10:
                return "IMPROVING"  # Getting better
            elif change_pct < 10:
                return "STABLE"
            else:
                return "DEGRADING"  # Getting worse

        elif metric in ["retention_compliance"]:
            # Higher is better
            if change_pct > 10:
                return "IMPROVING"
            elif change_pct > -10:
                return "STABLE"
            else:
                return "DEGRADING"

        else:
            # Neutral metrics (change is neither good nor bad)
            if abs(change_pct) < 10:
                return "STABLE"
            elif change_pct > 0:
                return "INCREASING"
            else:
                return "DECREASING"

    def generate_trend_report(self) -> Dict:
        """
        Generate trend analysis report.

        Returns:
            Trend report dict
        """
        reports = self.load_all_vital_signs()

        if not reports:
            return {
                "status": "NO_DATA",
                "message": "No historical vital signs reports found"
            }

        trends = self.calculate_trends(reports)

        # Add latest snapshot
        latest = reports[-1] if reports else None

        report = {
            "generated_at": datetime.now().isoformat(),
            "latest_quarter": latest['quarter'] if latest else None,
            "latest_health": latest['overall_health'] if latest else None,
            "trend_analysis": trends,
            "recommendations": self._generate_recommendations(trends)
        }

        return report

    def _generate_recommendations(self, trends: Dict) -> List[str]:
        """
        Generate recommendations based on trends.

        Args:
            trends: Trend analysis dict

        Returns:
            List of recommendations
        """
        if not trends.get("trend_available"):
            return ["Accumulate more quarterly data for trend analysis"]

        recommendations = []
        metrics = trends.get("metrics", {})

        # Backup ratio trend
        backup_ratio = metrics.get("backup_ratio", {})
        if backup_ratio.get("trend") == "DEGRADING":
            recommendations.append(
                "⚠️ Backup ratio increasing - execute backup rotation immediately"
            )
        elif backup_ratio.get("trend") == "IMPROVING":
            recommendations.append(
                "✅ Backup ratio improving - rotation policy working"
            )

        # Retention compliance trend
        retention = metrics.get("retention_compliance", {})
        if retention.get("trend") == "DEGRADING":
            recommendations.append(
                "⚠️ Retention compliance declining - review backup rotation frequency"
            )
        elif retention.get("end", 0) < 80:
            recommendations.append(
                "⚠️ Retention compliance low (<80%) - execute cleanup script"
            )

        # Deduplication trend
        dedup = metrics.get("deduplication", {})
        if dedup.get("trend") == "DEGRADING":
            recommendations.append(
                "⚠️ Duplication increasing - review for copy-paste patterns"
            )

        if not recommendations:
            recommendations.append("✅ All trends stable - no action required")

        return recommendations

    def print_trend_report(self, report: Dict):
        """Print trend report to console."""
        print()
        print("=" * 70)
        print("YAML Vital Signs - Historical Trends")
        print("=" * 70)
        print()

        if report.get("status") == "NO_DATA":
            print(report["message"])
            return

        print(f"Latest Quarter: {report['latest_quarter']}")
        print(f"Latest Health:  {report['latest_health']}")
        print()

        trends = report['trend_analysis']

        if not trends.get("trend_available"):
            print(trends.get("reason", "No trend data"))
            return

        print(f"Trend Analysis: {trends['time_span']} ({trends['quarters_analyzed']} quarters)")
        print()

        metrics = trends.get("metrics", {})

        if "yaml_count" in metrics:
            m = metrics["yaml_count"]
            print(f"YAML Count:        {m['start']:,} → {m['end']:,} ({m['change']:+,}, {m['change_pct']:+.1f}%) - {m['trend']}")

        if "backup_ratio" in metrics:
            m = metrics["backup_ratio"]
            print(f"Backup Ratio:      {m['start']:.1f}x → {m['end']:.1f}x ({m['change']:+.1f}x, {m['change_pct']:+.1f}%) - {m['trend']}")

        if "deduplication" in metrics:
            m = metrics["deduplication"]
            print(f"Deduplication:     {m['start']:.2f}% → {m['end']:.2f}% ({m['change']:+.2f}%, {m['change_pct']:+.1f}%) - {m['trend']}")

        if "retention_compliance" in metrics:
            m = metrics["retention_compliance"]
            print(f"Retention:         {m['start']:.1f}% → {m['end']:.1f}% ({m['change']:+.1f}%, {m['change_pct']:+.1f}%) - {m['trend']}")

        print()
        print("Recommendations:")
        for rec in report['recommendations']:
            print(f"  {rec}")

        print()


def main():
    """Main execution."""
    analyzer = YAMLVitalSignsTrendAnalyzer()
    report = analyzer.generate_trend_report()

    analyzer.print_trend_report(report)

    # Save report
    output_file = analyzer.vital_signs_dir / "yaml_vital_signs_trends.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

    print(f"Trend report saved: {output_file}")


if __name__ == "__main__":
    main()
