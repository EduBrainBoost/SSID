#!/usr/bin/env python3
"""
MoSCoW Scorecard Trend Analyzer
================================

Analyzes historical scorecard data from registry to generate trend reports.

Usage:
    python analyze_scorecard_trends.py --registry <path> --output <report.md>

Features:
- Score progression over time
- MUST/SHOULD/HAVE pass rate trends
- Regression detection
- Statistical analysis
- Compliance KPIs

Version: 1.0.0
Date: 2025-10-17
Author: SSID Core Team
"""

import argparse
import json
import os
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
from collections import defaultdict


class ScorecardTrendAnalyzer:
    """Analyze trends from historical MoSCoW scorecards"""

    def __init__(self, registry_path: str):
        self.registry_path = Path(registry_path)
        self.scorecards: List[Dict[str, Any]] = []
        self.load_scorecards()

    def load_scorecards(self):
        """Load all JSON scorecards from registry"""
        if not self.registry_path.exists():
            print(f"Warning: Registry path does not exist: {self.registry_path}")
            return

        json_files = sorted(self.registry_path.glob("scorecard_*.json"))

        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # Extract metadata from filename
                # Format: scorecard_20251017T152536Z_a6e6d2a.json
                filename = json_file.stem
                parts = filename.split('_')
                if len(parts) >= 3:
                    timestamp_str = parts[1]
                    commit_sha = parts[2]

                    # Parse timestamp
                    timestamp = datetime.strptime(timestamp_str, "%Y%m%dT%H%M%SZ")

                    self.scorecards.append({
                        "timestamp": timestamp,
                        "commit_sha": commit_sha,
                        "filename": json_file.name,
                        "scorecard": data["moscow_scorecard"],
                        "version": data.get("version", "unknown")
                    })
            except Exception as e:
                print(f"Warning: Failed to load {json_file}: {e}")

        # Sort by timestamp
        self.scorecards.sort(key=lambda x: x["timestamp"])

        print(f"Loaded {len(self.scorecards)} scorecards from {self.registry_path}")

    def calculate_statistics(self) -> Dict[str, Any]:
        """Calculate statistical metrics from scorecards"""
        if not self.scorecards:
            return {}

        scores = [sc["scorecard"]["moscow_score"] for sc in self.scorecards]
        must_pass_rates = [
            (sc["scorecard"]["must_rules"]["passed"] / sc["scorecard"]["must_rules"]["total"] * 100)
            if sc["scorecard"]["must_rules"]["total"] > 0 else 0
            for sc in self.scorecards
        ]
        should_pass_rates = [
            (sc["scorecard"]["should_rules"]["passed"] / sc["scorecard"]["should_rules"]["total"] * 100)
            if sc["scorecard"]["should_rules"]["total"] > 0 else 0
            for sc in self.scorecards
        ]

        return {
            "total_scorecards": len(self.scorecards),
            "date_range": {
                "first": self.scorecards[0]["timestamp"].isoformat(),
                "last": self.scorecards[-1]["timestamp"].isoformat()
            },
            "score": {
                "current": scores[-1] if scores else 0,
                "average": sum(scores) / len(scores) if scores else 0,
                "min": min(scores) if scores else 0,
                "max": max(scores) if scores else 0,
                "trend": self._calculate_trend(scores)
            },
            "must_pass_rate": {
                "current": must_pass_rates[-1] if must_pass_rates else 0,
                "average": sum(must_pass_rates) / len(must_pass_rates) if must_pass_rates else 0,
                "min": min(must_pass_rates) if must_pass_rates else 0,
                "max": max(must_pass_rates) if must_pass_rates else 0
            },
            "should_pass_rate": {
                "current": should_pass_rates[-1] if should_pass_rates else 0,
                "average": sum(should_pass_rates) / len(should_pass_rates) if should_pass_rates else 0,
                "min": min(should_pass_rates) if should_pass_rates else 0,
                "max": max(should_pass_rates) if should_pass_rates else 0
            }
        }

    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction from values"""
        if len(values) < 2:
            return "stable"

        # Simple linear regression slope
        n = len(values)
        x = list(range(n))
        y = values

        x_mean = sum(x) / n
        y_mean = sum(y) / n

        numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            return "stable"

        slope = numerator / denominator

        if slope > 0.5:
            return "improving"
        elif slope < -0.5:
            return "declining"
        else:
            return "stable"

    def detect_regressions(self) -> List[Dict[str, Any]]:
        """Detect score regressions between consecutive scorecards"""
        regressions = []

        for i in range(1, len(self.scorecards)):
            prev = self.scorecards[i - 1]
            curr = self.scorecards[i]

            prev_score = prev["scorecard"]["moscow_score"]
            curr_score = curr["scorecard"]["moscow_score"]

            # Regression if score drops by more than 2%
            if curr_score < prev_score - 2.0:
                regressions.append({
                    "from_commit": prev["commit_sha"],
                    "to_commit": curr["commit_sha"],
                    "from_score": prev_score,
                    "to_score": curr_score,
                    "drop": prev_score - curr_score,
                    "timestamp": curr["timestamp"]
                })

        return regressions

    def generate_markdown_report(self) -> str:
        """Generate comprehensive Markdown trend report"""
        stats = self.calculate_statistics()
        regressions = self.detect_regressions()

        report = f"""# MoSCoW Scorecard Trend Report

**Generated:** {datetime.utcnow().isoformat()}Z
**Registry Path:** `{self.registry_path}`
**Total Scorecards:** {stats.get('total_scorecards', 0)}

---

## Executive Summary

"""

        if stats:
            report += f"""
### Current Status

- **Current Score:** {stats['score']['current']:.1f}%
- **Average Score:** {stats['score']['average']:.1f}%
- **Score Trend:** {stats['score']['trend'].upper()}
- **MUST Pass Rate:** {stats['must_pass_rate']['current']:.1f}%
- **SHOULD Pass Rate:** {stats['should_pass_rate']['current']:.1f}%

### Date Range

- **First Scorecard:** {stats['date_range']['first']}
- **Latest Scorecard:** {stats['date_range']['last']}

---

## Score Statistics

| Metric | Current | Average | Min | Max |
|--------|---------|---------|-----|-----|
| MoSCoW Score | {stats['score']['current']:.1f}% | {stats['score']['average']:.1f}% | {stats['score']['min']:.1f}% | {stats['score']['max']:.1f}% |
| MUST Pass Rate | {stats['must_pass_rate']['current']:.1f}% | {stats['must_pass_rate']['average']:.1f}% | {stats['must_pass_rate']['min']:.1f}% | {stats['must_pass_rate']['max']:.1f}% |
| SHOULD Pass Rate | {stats['should_pass_rate']['current']:.1f}% | {stats['should_pass_rate']['average']:.1f}% | {stats['should_pass_rate']['min']:.1f}% | {stats['should_pass_rate']['max']:.1f}% |

---

## Score Progression

"""
        else:
            report += "\n*No scorecard data available for analysis.*\n\n---\n\n"

        # Score progression table
        if self.scorecards:
            report += "| Date | Commit | MoSCoW Score | MUST | SHOULD | HAVE | Status |\n"
            report += "|------|--------|--------------|------|--------|------|--------|\n"

            for sc in self.scorecards[-20:]:  # Last 20 scorecards
                timestamp = sc["timestamp"].strftime("%Y-%m-%d %H:%M")
                commit = sc["commit_sha"]
                score = sc["scorecard"]["moscow_score"]
                must_pass = sc["scorecard"]["must_rules"]["passed"]
                must_total = sc["scorecard"]["must_rules"]["total"]
                should_pass = sc["scorecard"]["should_rules"]["passed"]
                should_total = sc["scorecard"]["should_rules"]["total"]
                have_pass = sc["scorecard"]["have_rules"]["passed"]
                have_total = sc["scorecard"]["have_rules"]["total"]
                status = sc["scorecard"]["overall_status"]

                status_icon = "✅" if status == "PASS" else "❌"

                report += f"| {timestamp} | `{commit}` | {score:.1f}% | {must_pass}/{must_total} | {should_pass}/{should_total} | {have_pass}/{have_total} | {status_icon} {status} |\n"

        report += "\n---\n\n## Regression Analysis\n\n"

        if regressions:
            report += f"**{len(regressions)} regression(s) detected:**\n\n"
            report += "| From Commit | To Commit | Score Drop | Date |\n"
            report += "|-------------|-----------|------------|------|\n"

            for reg in regressions:
                report += f"| `{reg['from_commit']}` | `{reg['to_commit']}` | {reg['from_score']:.1f}% → {reg['to_score']:.1f}% (-{reg['drop']:.1f}%) | {reg['timestamp'].strftime('%Y-%m-%d')} |\n"
        else:
            report += "✅ **No significant regressions detected.**\n"

        report += "\n---\n\n## Compliance KPIs\n\n"

        if stats:
            # Calculate KPIs
            kpis = []

            if stats['must_pass_rate']['current'] == 100.0:
                kpis.append("✅ **100% MUST Rule Compliance** - All critical rules passing")
            else:
                kpis.append(f"⚠️ **MUST Rule Compliance:** {stats['must_pass_rate']['current']:.1f}% - Critical failures present")

            if stats['score']['current'] >= 90:
                kpis.append("✅ **Grade A+ Compliance** - Excellent score")
            elif stats['score']['current'] >= 75:
                kpis.append("✅ **Grade A Compliance** - Good score")
            elif stats['score']['current'] >= 60:
                kpis.append("⚠️ **Grade B Compliance** - Fair score")
            else:
                kpis.append("❌ **Grade C/F Compliance** - Below expectations")

            if stats['score']['trend'] == "improving":
                kpis.append("📈 **Improving Trend** - Score increasing over time")
            elif stats['score']['trend'] == "declining":
                kpis.append("📉 **Declining Trend** - Score decreasing over time")
            else:
                kpis.append("➡️ **Stable Trend** - Score relatively consistent")

            for kpi in kpis:
                report += f"- {kpi}\n"

        report += """

---

## Recommendations

"""

        if stats:
            recommendations = []

            if stats['must_pass_rate']['current'] < 100:
                recommendations.append("1. **Critical Priority:** Fix all MUST rule violations to unblock CI")

            if stats['should_pass_rate']['current'] < 80:
                recommendations.append(f"2. **Improve Best Practices:** SHOULD pass rate is {stats['should_pass_rate']['current']:.1f}%, target 80%+")

            if stats['score']['trend'] == "declining":
                recommendations.append("3. **Investigate Regression:** Score trend is declining, review recent changes")

            if len(regressions) > 2:
                recommendations.append(f"4. **Address Regressions:** {len(regressions)} score drops detected, implement preventive measures")

            if not recommendations:
                recommendations.append("✅ **No immediate actions required** - Maintain current compliance level")

            for rec in recommendations:
                report += f"{rec}\n"

        report += """

---

## Appendix: Data Sources

"""

        report += f"- **Registry Path:** `{self.registry_path}`\n"
        report += f"- **Total Scorecards Analyzed:** {len(self.scorecards)}\n"
        report += f"- **Analysis Method:** Linear regression trend + threshold-based regression detection\n"

        report += """

---

*Generated by MoSCoW Scorecard Trend Analyzer v1.0.0*
"""

        return report


def main():
    parser = argparse.ArgumentParser(
        description="Analyze MoSCoW scorecard trends from registry",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "--registry",
        required=True,
        help="Path to scorecard registry directory"
    )

    parser.add_argument(
        "--output",
        default="moscow_trend_report.md",
        help="Output Markdown report file (default: moscow_trend_report.md)"
    )

    args = parser.parse_args()

    # Analyze trends
    analyzer = ScorecardTrendAnalyzer(args.registry)

    # Generate report
    report = analyzer.generate_markdown_report()

    # Write to file
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"\n✅ Trend report generated: {args.output}")

    # Print summary to stdout
    stats = analyzer.calculate_statistics()
    if stats:
        print(f"\nSummary:")
        print(f"  Current Score: {stats['score']['current']:.1f}%")
        print(f"  Average Score: {stats['score']['average']:.1f}%")
        print(f"  Trend: {stats['score']['trend'].upper()}")
        print(f"  Regressions: {len(analyzer.detect_regressions())}")


if __name__ == "__main__":
    main()
