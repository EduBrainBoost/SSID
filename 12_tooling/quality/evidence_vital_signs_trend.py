#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
evidence_vital_signs_trend.py - Historical Evidence Health Trend Analyzer
Author: edubrainboost ©2025 MIT License

Analyzes historical Evidence Vital Signs reports to identify trends:
- Active evidence growth/decline
- Archive accumulation rate
- Verify success rate stability
- Integrity error patterns
- OPA deny frequency

Requires at least 2 monthly reports for trend analysis.

Usage:
    python evidence_vital_signs_trend.py
"""

import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional


class EvidenceVitalSignsTrendAnalyzer:
    """Analyze trends across multiple Evidence Vital Signs reports."""

    def __init__(self, root_dir: Optional[Path] = None):
        if root_dir is None:
            root_dir = Path(__file__).resolve().parents[2]

        self.root = root_dir
        self.vital_signs_dir = root_dir / "12_tooling" / "quality" / "vital_signs"

    def load_historical_reports(self) -> List[Dict]:
        """
        Load all historical Evidence Vital Signs JSON reports.

        Returns:
            List of reports sorted by month
        """
        reports = []

        if not self.vital_signs_dir.exists():
            return reports

        # Find all evidence vital signs JSON files
        for json_file in sorted(self.vital_signs_dir.glob("evidence_vital_signs_*.json")):
            with open(json_file, 'r', encoding='utf-8') as f:
                report = json.load(f)
                reports.append(report)

        return reports

    def calculate_trends(self, reports: List[Dict]) -> Dict:
        """
        Calculate trends from historical reports.

        Args:
            reports: List of vital signs reports

        Returns:
            Dict with trend analysis
        """
        if len(reports) < 2:
            return {
                "trend_available": False,
                "reason": "Insufficient historical data (need >= 2 months)"
            }

        # Extract time series data
        months = []
        active_counts = []
        archive_counts = []
        verify_rates = []
        integrity_errors = []
        opa_denies = []

        for report in reports:
            months.append(report['month'])
            vs = report['vital_signs']

            active_counts.append(vs['1_active_evidence']['count'])
            archive_counts.append(vs['2_archive_size']['archive_count'])
            verify_rates.append(vs['3_verify_success']['rate_pct'])
            integrity_errors.append(vs['4_integrity_errors']['count'])
            opa_denies.append(vs['5_opa_denies']['count'])

        # Calculate trends
        trends = {
            "trend_available": True,
            "period": {
                "start": months[0],
                "end": months[-1],
                "months": len(months)
            },
            "metrics": {}
        }

        # Active Evidence Trend
        active_change = active_counts[-1] - active_counts[0]
        active_change_pct = (active_change / active_counts[0] * 100) if active_counts[0] > 0 else 0

        trends["metrics"]["active_evidence"] = {
            "start": active_counts[0],
            "end": active_counts[-1],
            "change": active_change,
            "change_pct": round(active_change_pct, 1),
            "trend": self._classify_trend(active_change_pct, reverse=True),  # Lower is better
            "interpretation": self._interpret_active_trend(active_change_pct)
        }

        # Archive Growth Trend
        archive_change = archive_counts[-1] - archive_counts[0]

        trends["metrics"]["archive_growth"] = {
            "start": archive_counts[0],
            "end": archive_counts[-1],
            "change": archive_change,
            "avg_per_month": round(archive_change / len(months), 1) if len(months) > 0 else 0,
            "trend": "GROWING" if archive_change > 0 else "STABLE",
            "interpretation": "Normal rolling window operation" if archive_change >= 0 else "No archiving activity"
        }

        # Verify Success Stability
        verify_avg = sum(verify_rates) / len(verify_rates) if verify_rates else 0
        verify_min = min(verify_rates) if verify_rates else 0

        trends["metrics"]["verify_success"] = {
            "average": round(verify_avg, 1),
            "minimum": round(verify_min, 1),
            "trend": "STABLE" if verify_min >= 95.0 or archive_counts[-1] == 0 else "DEGRADING",
            "interpretation": "Verify success stable" if verify_min >= 95.0 or archive_counts[-1] == 0
                            else "Verification issues detected"
        }

        # Integrity Error Pattern
        total_errors = sum(integrity_errors)

        trends["metrics"]["integrity_errors"] = {
            "total": total_errors,
            "trend": "HEALTHY" if total_errors == 0 else "CRITICAL",
            "interpretation": "No integrity errors" if total_errors == 0 else f"{total_errors} integrity errors detected"
        }

        # OPA Deny Frequency
        total_denies = sum(opa_denies)
        avg_denies = total_denies / len(opa_denies) if opa_denies else 0

        trends["metrics"]["opa_denies"] = {
            "total": total_denies,
            "average_per_month": round(avg_denies, 1),
            "trend": "HEALTHY" if total_denies <= 2 else "NEEDS_ATTENTION",
            "interpretation": "Policy compliance good" if total_denies <= 2
                            else "Repeated policy violations"
        }

        # Overall trend assessment
        trends["overall_assessment"] = self._assess_overall_trend(trends["metrics"])

        return trends

    def _classify_trend(self, change_pct: float, reverse: bool = False) -> str:
        """
        Classify trend based on percentage change.

        Args:
            change_pct: Percentage change
            reverse: If True, negative is better (for metrics like active count)

        Returns:
            Trend classification: IMPROVING, STABLE, DEGRADING
        """
        threshold = 10.0

        if reverse:
            if change_pct < -threshold:
                return "IMPROVING"
            elif change_pct > threshold:
                return "DEGRADING"
            else:
                return "STABLE"
        else:
            if change_pct > threshold:
                return "IMPROVING"
            elif change_pct < -threshold:
                return "DEGRADING"
            else:
                return "STABLE"

    def _interpret_active_trend(self, change_pct: float) -> str:
        """Interpret active evidence trend."""
        if change_pct < -20:
            return "Significant decrease - rolling window working effectively"
        elif change_pct < -10:
            return "Moderate decrease - evidence cleanup active"
        elif change_pct < 10:
            return "Stable - evidence accumulation balanced"
        elif change_pct < 20:
            return "Moderate increase - monitor for cleanup needs"
        else:
            return "Significant increase - review retention policy"

    def _assess_overall_trend(self, metrics: Dict) -> str:
        """
        Assess overall trend health.

        Args:
            metrics: Trend metrics

        Returns:
            Overall assessment: IMPROVING, STABLE, DEGRADING, CRITICAL
        """
        # Critical conditions
        if metrics["integrity_errors"]["trend"] == "CRITICAL":
            return "CRITICAL"
        if metrics["verify_success"]["trend"] == "DEGRADING":
            return "CRITICAL"

        # Degrading conditions
        if metrics["active_evidence"]["trend"] == "DEGRADING":
            return "DEGRADING"
        if metrics["opa_denies"]["trend"] == "NEEDS_ATTENTION":
            return "DEGRADING"

        # Improving conditions
        if metrics["active_evidence"]["trend"] == "IMPROVING":
            return "IMPROVING"

        return "STABLE"

    def write_trend_report(self, trends: Dict) -> Path:
        """
        Write trend analysis to JSON file.

        Args:
            trends: Trend analysis data

        Returns:
            Path to trend report
        """
        output_path = self.vital_signs_dir / "evidence_vital_signs_trends.json"

        report = {
            "generated_at": datetime.now().isoformat(),
            **trends
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)

        return output_path

    def generate_trend_summary(self, trends: Dict) -> str:
        """
        Generate human-readable trend summary.

        Args:
            trends: Trend analysis data

        Returns:
            Markdown-formatted summary
        """
        if not trends.get("trend_available"):
            return f"# Evidence Vital Signs - Trend Analysis\n\n**Status**: {trends.get('reason')}\n"

        period = trends["period"]
        metrics = trends["metrics"]
        overall = trends["overall_assessment"]

        summary = f"""# Evidence Vital Signs - Trend Analysis

**Period**: {period['start']} to {period['end']} ({period['months']} months)
**Overall Assessment**: {overall}

---

## Metric Trends

### Active Evidence
- **Change**: {metrics['active_evidence']['start']} → {metrics['active_evidence']['end']} files ({metrics['active_evidence']['change']:+d})
- **Trend**: {metrics['active_evidence']['trend']}
- **Interpretation**: {metrics['active_evidence']['interpretation']}

### Archive Growth
- **Change**: {metrics['archive_growth']['start']} → {metrics['archive_growth']['end']} archives ({metrics['archive_growth']['change']:+d})
- **Rate**: {metrics['archive_growth']['avg_per_month']} archives/month
- **Interpretation**: {metrics['archive_growth']['interpretation']}

### Verify Success
- **Average**: {metrics['verify_success']['average']}%
- **Minimum**: {metrics['verify_success']['minimum']}%
- **Trend**: {metrics['verify_success']['trend']}
- **Interpretation**: {metrics['verify_success']['interpretation']}

### Integrity Errors
- **Total**: {metrics['integrity_errors']['total']}
- **Trend**: {metrics['integrity_errors']['trend']}
- **Interpretation**: {metrics['integrity_errors']['interpretation']}

### OPA Deny Events
- **Total**: {metrics['opa_denies']['total']}
- **Average**: {metrics['opa_denies']['average_per_month']}/month
- **Trend**: {metrics['opa_denies']['trend']}
- **Interpretation**: {metrics['opa_denies']['interpretation']}

---

## Recommendations

"""

        # Add recommendations based on overall assessment
        if overall == "IMPROVING":
            summary += """- Evidence management is improving
- Rolling window cleanup effective
- Continue current monitoring schedule
"""
        elif overall == "STABLE":
            summary += """- Evidence storage is stable
- No significant trends detected
- Continue monthly monitoring
"""
        elif overall == "DEGRADING":
            summary += """- Evidence management showing signs of degradation
- Review retention policy compliance
- Consider more frequent cleanup runs
"""
        else:  # CRITICAL
            summary += """- **IMMEDIATE ACTION REQUIRED**
- Critical issues detected (integrity errors or verification failures)
- Investigate root cause immediately
- Suspend cleanup until issues resolved
"""

        summary += f"""
---

**Generated**: {datetime.now().strftime('%Y-%m-%d')}
**Next Trend Analysis**: Next month after new vital signs report
"""

        return summary


def main():
    """Main execution."""
    analyzer = EvidenceVitalSignsTrendAnalyzer()

    print("Loading historical Evidence Vital Signs reports...")
    reports = analyzer.load_historical_reports()

    if not reports:
        print("No historical reports found.")
        print("Generate first report with: python evidence_vital_signs_generator.py")
        return

    print(f"Found {len(reports)} report(s)")
    print()

    # Calculate trends
    trends = analyzer.calculate_trends(reports)

    # Write trend report
    trend_path = analyzer.write_trend_report(trends)
    print(f"Trend report: {trend_path}")

    # Generate summary
    summary = analyzer.generate_trend_summary(trends)
    print()
    print(summary)


if __name__ == "__main__":
    main()
