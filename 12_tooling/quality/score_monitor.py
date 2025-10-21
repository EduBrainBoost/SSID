#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
score_monitor.py - Automatic Score Tracking & Gap Analysis
Author: edubrainboost ©2025 MIT License

Scans all reports for score patterns and tracks progress toward 100/100.

Usage:
    # Generate score dashboard
    python score_monitor.py

    # Generate with trend analysis
    python score_monitor.py --with-trends

    # Alert if any score < threshold
    python score_monitor.py --alert-threshold 95
"""

import re
import json
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
import argparse

# UTF-8 enforcement for Windows
if sys.platform == 'win32':
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')


class ScoreMonitor:
    """Monitor and track scores across all reports."""

    def __init__(self, root_dir: Optional[Path] = None):
        if root_dir is None:
            root_dir = Path(__file__).resolve().parents[2]

        self.root = root_dir
        self.reports_dir = root_dir / "02_audit_logging" / "reports"
        self.output_dir = root_dir / "12_tooling" / "quality" / "vital_signs"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def scan_scores(self) -> Dict[str, List[Tuple[str, float, str]]]:
        """
        Scan all reports for score patterns.

        Returns:
            Dict mapping component names to list of (file, score, context)
        """
        scores = defaultdict(list)

        # Score patterns to match
        patterns = [
            r"(?P<component>[A-Za-z0-9\s_\-]+):\s*(?P<score>\d+(?:\.\d+)?)/100",
            r"\*\*(?P<component>[A-Za-z0-9\s_\-]+)\*\*:\s*(?P<score>\d+(?:\.\d+)?)/100",
            r"Score:\s*(?P<score>\d+(?:\.\d+)?)/100",
            r"Final Score:\s*(?P<score>\d+(?:\.\d+)?)/100",
            r"Overall:\s*(?P<score>\d+(?:\.\d+)?)/100",
        ]

        if not self.reports_dir.exists():
            return dict(scores)

        for report_file in self.reports_dir.glob("*.md"):
            content = report_file.read_text(encoding='utf-8', errors='ignore')

            for pattern in patterns:
                for match in re.finditer(pattern, content):
                    component = match.group('component') if 'component' in match.groupdict() else report_file.stem
                    score = float(match.group('score'))

                    # Get context (surrounding text)
                    start = max(0, match.start() - 50)
                    end = min(len(content), match.end() + 50)
                    context = content[start:end].replace('\n', ' ')

                    scores[component].append((
                        report_file.name,
                        score,
                        context
                    ))

        return dict(scores)

    def aggregate_scores(self, scores: Dict) -> Dict[str, float]:
        """
        Aggregate scores by component (use latest/highest).

        Args:
            scores: Raw scores from scan

        Returns:
            Dict mapping component to aggregated score
        """
        aggregated = {}

        for component, score_list in scores.items():
            # Use highest score for component (optimistic)
            aggregated[component] = max(score for _, score, _ in score_list)

        return aggregated

    def categorize_scores(self, aggregated: Dict[str, float]) -> Dict[str, List[str]]:
        """
        Categorize components by score range.

        Args:
            aggregated: Aggregated scores

        Returns:
            Dict with categories: perfect, near_perfect, medium, low
        """
        categories = {
            "perfect": [],           # 100/100
            "near_perfect": [],      # 90-99
            "medium": [],            # 70-89
            "low": [],              # <70
        }

        for component, score in aggregated.items():
            if score == 100:
                categories["perfect"].append(component)
            elif score >= 90:
                categories["near_perfect"].append(component)
            elif score >= 70:
                categories["medium"].append(component)
            else:
                categories["low"].append(component)

        return categories

    def calculate_statistics(self, aggregated: Dict[str, float]) -> Dict:
        """Calculate score statistics."""
        scores = list(aggregated.values())

        if not scores:
            return {
                "total_components": 0,
                "average_score": 0.0,
                "median_score": 0.0,
                "min_score": 0.0,
                "max_score": 0.0
            }

        scores_sorted = sorted(scores)
        n = len(scores)

        return {
            "total_components": n,
            "average_score": round(sum(scores) / n, 2),
            "median_score": round(scores_sorted[n // 2], 2),
            "min_score": round(min(scores), 2),
            "max_score": round(max(scores), 2)
        }

    def identify_gaps(
        self,
        aggregated: Dict[str, float],
        threshold: float = 100.0
    ) -> Dict[str, float]:
        """
        Identify components below threshold.

        Args:
            aggregated: Aggregated scores
            threshold: Score threshold

        Returns:
            Dict of components with gaps
        """
        gaps = {}

        for component, score in aggregated.items():
            if score < threshold:
                gap = threshold - score
                gaps[component] = round(gap, 2)

        # Sort by gap size (descending)
        return dict(sorted(gaps.items(), key=lambda x: x[1], reverse=True))

    def generate_dashboard(
        self,
        alert_threshold: Optional[float] = None
    ) -> Dict:
        """
        Generate score monitoring dashboard.

        Args:
            alert_threshold: Alert if any score below this

        Returns:
            Dashboard data
        """
        print("Scanning reports for scores...")
        raw_scores = self.scan_scores()

        print(f"Found {len(raw_scores)} components with scores")
        print()

        aggregated = self.aggregate_scores(raw_scores)
        categories = self.categorize_scores(aggregated)
        statistics = self.calculate_statistics(aggregated)
        gaps = self.identify_gaps(aggregated, threshold=100.0)

        dashboard = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "statistics": statistics,
            "categories": {
                "perfect_100": sorted(categories["perfect"]),
                "near_perfect_90_99": sorted(categories["near_perfect"]),
                "medium_70_89": sorted(categories["medium"]),
                "low_below_70": sorted(categories["low"])
            },
            "top_gaps": dict(list(gaps.items())[:10]),  # Top 10 gaps
            "alerts": []
        }

        # Generate alerts if threshold specified
        if alert_threshold:
            for component, score in aggregated.items():
                if score < alert_threshold:
                    dashboard["alerts"].append({
                        "component": component,
                        "score": score,
                        "threshold": alert_threshold,
                        "message": f"{component} below threshold: {score}/100 < {alert_threshold}"
                    })

        return dashboard

    def write_dashboard(self, dashboard: Dict) -> Path:
        """Write dashboard to JSON file."""
        timestamp = datetime.now().strftime("%Y%m%d")
        output_file = self.output_dir / f"score_dashboard_{timestamp}.json"

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(dashboard, f, indent=2)

        return output_file

    def write_markdown_report(self, dashboard: Dict) -> Path:
        """Write human-readable markdown report."""
        timestamp = datetime.now().strftime("%Y%m%d")
        output_file = self.output_dir / f"score_dashboard_{timestamp}.md"

        stats = dashboard["statistics"]
        cats = dashboard["categories"]
        gaps = dashboard["top_gaps"]

        content = f"""# Score Monitoring Dashboard

**Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M")}

---

## Summary Statistics

- **Total Components**: {stats['total_components']}
- **Average Score**: {stats['average_score']}/100
- **Median Score**: {stats['median_score']}/100
- **Min Score**: {stats['min_score']}/100
- **Max Score**: {stats['max_score']}/100

---

## Score Distribution

### ✅ Perfect (100/100)
**Count**: {len(cats['perfect_100'])}

"""
        for component in cats['perfect_100'][:20]:  # Top 20
            content += f"- {component}\n"

        if len(cats['perfect_100']) > 20:
            content += f"\n... and {len(cats['perfect_100']) - 20} more\n"

        content += f"""

### 🟢 Near Perfect (90-99/100)
**Count**: {len(cats['near_perfect_90_99'])}

"""
        for component in cats['near_perfect_90_99']:
            content += f"- {component}\n"

        content += f"""

### 🟡 Medium (70-89/100)
**Count**: {len(cats['medium_70_89'])}

"""
        for component in cats['medium_70_89']:
            content += f"- {component}\n"

        content += f"""

### 🔴 Low (<70/100)
**Count**: {len(cats['low_below_70'])}

"""
        for component in cats['low_below_70']:
            content += f"- {component}\n"

        content += """

---

## Top 10 Gaps (to 100/100)

"""
        for i, (component, gap) in enumerate(list(gaps.items())[:10], 1):
            score = 100 - gap
            content += f"{i}. **{component}**: {score:.2f}/100 (gap: {gap:.2f})\n"

        content += """

---

## Alerts

"""
        if dashboard["alerts"]:
            for alert in dashboard["alerts"]:
                content += f"⚠️ **{alert['component']}**: {alert['score']}/100 (below threshold {alert['threshold']})\n"
        else:
            content += "No alerts - all components above threshold ✅\n"

        content += """

---

## Next Actions

Based on gaps identified:

1. **Immediate** (This Week): Address top 3 gaps
2. **Short-term** (Next Month): Bring near-perfect to 100
3. **Long-term** (Quarter): Eliminate all gaps

See: `24_meta_orchestration/SCORE_IMPROVEMENT_ROADMAP.md`

---

**Generated by**: Score Monitoring System
**Next Scan**: Weekly (automated via CI)
"""

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)

        return output_file

    def print_summary(self, dashboard: Dict):
        """Print dashboard summary to console."""
        stats = dashboard["statistics"]
        cats = dashboard["categories"]

        print("=" * 70)
        print("Score Monitoring Dashboard")
        print("=" * 70)
        print()

        print(f"Total Components: {stats['total_components']}")
        print(f"Average Score:    {stats['average_score']}/100")
        print()

        print("Score Distribution:")
        print(f"  [100]:      {len(cats['perfect_100'])} components (PERFECT)")
        print(f"  [90-99]:    {len(cats['near_perfect_90_99'])} components (NEAR PERFECT)")
        print(f"  [70-89]:    {len(cats['medium_70_89'])} components (MEDIUM)")
        print(f"  [<70]:      {len(cats['low_below_70'])} components (LOW)")
        print()

        if dashboard["top_gaps"]:
            print("Top 5 Gaps:")
            for i, (component, gap) in enumerate(list(dashboard["top_gaps"].items())[:5], 1):
                score = 100 - gap
                print(f"  {i}. {component}: {score:.2f}/100 (gap: {gap:.2f})")
            print()

        if dashboard["alerts"]:
            print(f"⚠️  {len(dashboard['alerts'])} ALERTS")
            for alert in dashboard["alerts"][:5]:
                print(f"  - {alert['message']}")
            print()


def main():
    """Main execution."""
    parser = argparse.ArgumentParser(
        description="Score Monitoring & Gap Analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate dashboard
  python score_monitor.py

  # Alert if any score < 95
  python score_monitor.py --alert-threshold 95

  # Generate with trends (future feature)
  python score_monitor.py --with-trends
        """
    )

    parser.add_argument(
        "--alert-threshold",
        type=float,
        help="Alert if any score below threshold"
    )

    parser.add_argument(
        "--with-trends",
        action="store_true",
        help="Include trend analysis (requires historical data)"
    )

    args = parser.parse_args()

    monitor = ScoreMonitor()

    # Generate dashboard
    dashboard = monitor.generate_dashboard(alert_threshold=args.alert_threshold)

    # Write outputs
    json_file = monitor.write_dashboard(dashboard)
    md_file = monitor.write_markdown_report(dashboard)

    # Print summary
    monitor.print_summary(dashboard)

    print(f"Dashboard saved:")
    print(f"  JSON: {json_file}")
    print(f"  Markdown: {md_file}")


if __name__ == "__main__":
    main()
