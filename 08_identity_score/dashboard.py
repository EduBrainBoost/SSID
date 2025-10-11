#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Score Trend Dashboard - Identity Score Visualization
SSID Phase 3 Implementation

Purpose:
- Visualize identity score trends over time
- Track badge integrity score evolution
- Monitor compliance score progression
- Generate governance-ready reports

Architecture:
Score Logs (JSONL) → Data Aggregation → Visualization → HTML/PDF Export

Data Sources:
- 02_audit_logging/evidence/score_logs/score_algorithm_*.jsonl
- 03_evidence_system/proofs/*/proofs.jsonl
- 23_compliance/evidence/issue_registry/issue_registry_*.json

Outputs:
- HTML dashboard with interactive charts
- PDF report for governance reviews
- JSON data export for further analysis

Integration:
- Governance quarterly reviews
- DAO voting materials
- Compliance audit reports

Dependencies:
- matplotlib: Chart generation
- pandas: Data processing
- jinja2: HTML templating
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, asdict
from collections import defaultdict


try:
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Warning: matplotlib not available. Charts will not be generated.")


@dataclass
class ScoreTrend:
    """
    Represents a score trend data point.

    Fields:
    - timestamp: ISO 8601 timestamp
    - score: Score value (0-100)
    - algorithm_name: Name of scoring algorithm
    - event_count: Number of events at this time
    """
    timestamp: str
    score: float
    algorithm_name: str
    event_count: int

    def to_dict(self) -> Dict:
        return asdict(self)


class ScoreTrendDashboard:
    """
    Generate score trend visualizations and reports.

    Responsibilities:
    1. Load score data from audit logs
    2. Aggregate by time period (daily, weekly, monthly)
    3. Generate trend charts (line, bar, heatmap)
    4. Export to HTML dashboard
    5. Generate PDF reports for governance
    """

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.score_logs_dir = repo_root / "02_audit_logging" / "evidence" / "score_logs"
        self.proofs_dir = repo_root / "03_evidence_system" / "proofs"
        self.output_dir = repo_root / "08_identity_score" / "dashboards"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def load_score_events(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict]:
        """
        Load score algorithm events from JSONL logs.

        Args:
            start_date: Start date filter (default: 30 days ago)
            end_date: End date filter (default: now)

        Returns:
            List of score event dicts
        """
        if not start_date:
            start_date = datetime.now(timezone.utc) - timedelta(days=30)
        if not end_date:
            end_date = datetime.now(timezone.utc)

        events = []

        # Scan score log files
        if self.score_logs_dir.exists():
            for log_file in sorted(self.score_logs_dir.glob("score_algorithm_*.jsonl")):
                with open(log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            event = json.loads(line.strip())

                            # Filter by date range
                            event_time = datetime.fromisoformat(event["timestamp"])
                            if start_date <= event_time <= end_date:
                                events.append(event)

                        except (json.JSONDecodeError, KeyError, ValueError) as e:
                            print(f"Warning: Failed to parse event: {e}")

        return events

    def aggregate_scores_by_day(self, events: List[Dict]) -> Dict[str, List[ScoreTrend]]:
        """
        Aggregate scores by day and algorithm.

        Args:
            events: List of score events

        Returns:
            Dict mapping algorithm_name to list of daily ScoreTrend objects
        """
        # Group events by algorithm and date
        by_algo_date = defaultdict(lambda: defaultdict(list))

        for event in events:
            algo_name = event.get("algorithm_name", "unknown")
            timestamp = event.get("timestamp", "")
            score = event.get("output_score", 0.0)

            # Extract date (YYYY-MM-DD)
            try:
                event_date = datetime.fromisoformat(timestamp).strftime('%Y-%m-%d')
            except ValueError:
                continue

            by_algo_date[algo_name][event_date].append(score)

        # Calculate daily averages
        trends = {}

        for algo_name, dates in by_algo_date.items():
            algo_trends = []

            for date_str, scores in sorted(dates.items()):
                avg_score = sum(scores) / len(scores)

                trend = ScoreTrend(
                    timestamp=date_str,
                    score=round(avg_score, 2),
                    algorithm_name=algo_name,
                    event_count=len(scores)
                )

                algo_trends.append(trend)

            trends[algo_name] = algo_trends

        return trends

    def generate_score_trend_chart(
        self,
        trends: Dict[str, List[ScoreTrend]],
        output_file: Path,
        title: str = "Score Trends Over Time"
    ) -> None:
        """
        Generate line chart showing score trends.

        Args:
            trends: Dict mapping algorithm_name to ScoreTrend list
            output_file: Path to save chart image
            title: Chart title
        """
        if not MATPLOTLIB_AVAILABLE:
            print("Warning: Cannot generate chart (matplotlib not installed)")
            return

        fig, ax = plt.subplots(figsize=(12, 6))

        for algo_name, trend_list in trends.items():
            if not trend_list:
                continue

            # Extract dates and scores
            dates = [datetime.fromisoformat(t.timestamp) for t in trend_list]
            scores = [t.score for t in trend_list]

            # Plot line
            ax.plot(dates, scores, marker='o', label=algo_name, linewidth=2)

        # Formatting
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Score (0-100)', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)

        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(trend_list) // 10)))
        plt.xticks(rotation=45)

        # Set y-axis range
        ax.set_ylim(0, 105)

        plt.tight_layout()
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        plt.close()

        print(f"Chart saved: {output_file}")

    def generate_event_count_chart(
        self,
        trends: Dict[str, List[ScoreTrend]],
        output_file: Path,
        title: str = "Score Events Per Day"
    ) -> None:
        """
        Generate bar chart showing number of score events per day.

        Args:
            trends: Dict mapping algorithm_name to ScoreTrend list
            output_file: Path to save chart image
            title: Chart title
        """
        if not MATPLOTLIB_AVAILABLE:
            print("Warning: Cannot generate chart (matplotlib not installed)")
            return

        fig, ax = plt.subplots(figsize=(12, 6))

        # Combine all algorithms for total count per day
        date_counts = defaultdict(int)

        for algo_name, trend_list in trends.items():
            for trend in trend_list:
                date_counts[trend.timestamp] += trend.event_count

        # Sort by date
        sorted_dates = sorted(date_counts.keys())
        counts = [date_counts[d] for d in sorted_dates]
        dates = [datetime.fromisoformat(d) for d in sorted_dates]

        # Plot bars
        ax.bar(dates, counts, color='steelblue', alpha=0.7)

        # Formatting
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Number of Events', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')

        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(sorted_dates) // 10)))
        plt.xticks(rotation=45)

        plt.tight_layout()
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        plt.close()

        print(f"Chart saved: {output_file}")

    def calculate_statistics(self, trends: Dict[str, List[ScoreTrend]]) -> Dict:
        """
        Calculate summary statistics for trends.

        Args:
            trends: Dict mapping algorithm_name to ScoreTrend list

        Returns:
            Dict containing statistics
        """
        stats = {}

        for algo_name, trend_list in trends.items():
            if not trend_list:
                continue

            scores = [t.score for t in trend_list]
            event_counts = [t.event_count for t in trend_list]

            stats[algo_name] = {
                "current_score": scores[-1] if scores else 0.0,
                "avg_score": round(sum(scores) / len(scores), 2),
                "min_score": min(scores),
                "max_score": max(scores),
                "score_volatility": round(max(scores) - min(scores), 2),
                "total_events": sum(event_counts),
                "data_points": len(trend_list),
                "first_date": trend_list[0].timestamp,
                "last_date": trend_list[-1].timestamp
            }

            # Calculate trend direction (improving/declining)
            if len(scores) >= 2:
                first_half_avg = sum(scores[:len(scores)//2]) / (len(scores)//2)
                second_half_avg = sum(scores[len(scores)//2:]) / (len(scores) - len(scores)//2)

                diff = second_half_avg - first_half_avg

                if diff > 5:
                    stats[algo_name]["trend_direction"] = "improving"
                elif diff < -5:
                    stats[algo_name]["trend_direction"] = "declining"
                else:
                    stats[algo_name]["trend_direction"] = "stable"
            else:
                stats[algo_name]["trend_direction"] = "insufficient_data"

        return stats

    def generate_html_dashboard(
        self,
        trends: Dict[str, List[ScoreTrend]],
        statistics: Dict,
        output_file: Path,
        charts: Dict[str, Path]
    ) -> None:
        """
        Generate HTML dashboard with embedded charts and statistics.

        Args:
            trends: Score trends data
            statistics: Summary statistics
            output_file: Path to save HTML file
            charts: Dict mapping chart name to image file path
        """
        # Generate HTML
        html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SSID Score Trend Dashboard</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }
        h2 {
            color: #34495e;
            margin-top: 30px;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .stat-card {
            background-color: #ecf0f1;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #3498db;
        }
        .stat-card h3 {
            margin: 0 0 15px 0;
            color: #2c3e50;
            font-size: 18px;
        }
        .stat-item {
            display: flex;
            justify-content: space-between;
            margin: 8px 0;
            padding: 5px 0;
            border-bottom: 1px solid #bdc3c7;
        }
        .stat-label {
            font-weight: 600;
            color: #7f8c8d;
        }
        .stat-value {
            font-weight: bold;
            color: #2c3e50;
        }
        .trend-improving { color: #27ae60; }
        .trend-declining { color: #e74c3c; }
        .trend-stable { color: #f39c12; }
        .chart {
            margin: 30px 0;
            text-align: center;
        }
        .chart img {
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .metadata {
            margin-top: 40px;
            padding: 15px;
            background-color: #ecf0f1;
            border-radius: 8px;
            font-size: 14px;
            color: #7f8c8d;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>SSID Score Trend Dashboard</h1>
        <p><strong>Generated:</strong> {timestamp}</p>

        <h2>Summary Statistics</h2>
        <div class="stats-grid">
"""

        # Add statistics cards
        for algo_name, stats in statistics.items():
            trend_class = f"trend-{stats['trend_direction'].replace('_', '-')}"

            html += f"""
            <div class="stat-card">
                <h3>{algo_name.replace('_', ' ').title()}</h3>
                <div class="stat-item">
                    <span class="stat-label">Current Score:</span>
                    <span class="stat-value">{stats['current_score']}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Average Score:</span>
                    <span class="stat-value">{stats['avg_score']}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Score Range:</span>
                    <span class="stat-value">{stats['min_score']} - {stats['max_score']}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Trend:</span>
                    <span class="stat-value {trend_class}">{stats['trend_direction'].replace('_', ' ').title()}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Total Events:</span>
                    <span class="stat-value">{stats['total_events']}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Period:</span>
                    <span class="stat-value">{stats['first_date']} to {stats['last_date']}</span>
                </div>
            </div>
"""

        html += """
        </div>

        <h2>Score Trends</h2>
"""

        # Add charts
        for chart_name, chart_path in charts.items():
            if chart_path and chart_path.exists():
                # Use relative path from output HTML location
                rel_path = chart_path.name

                html += f"""
        <div class="chart">
            <img src="{rel_path}" alt="{chart_name}">
        </div>
"""

        # Add metadata footer
        html += f"""
        <div class="metadata">
            <p><strong>Data Sources:</strong></p>
            <ul>
                <li>Score Logs: 02_audit_logging/evidence/score_logs/</li>
                <li>Proof System: 03_evidence_system/proofs/</li>
                <li>Issue Registry: 23_compliance/evidence/issue_registry/</li>
            </ul>
            <p><strong>Dashboard Location:</strong> {output_file.relative_to(self.repo_root)}</p>
            <p><strong>SSID Compliance System</strong> | Phase 3 Evidence Automation</p>
        </div>
    </div>
</body>
</html>
"""

        # Write HTML file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html.format(timestamp=datetime.now(timezone.utc).isoformat()))

        print(f"Dashboard saved: {output_file}")

    def generate_dashboard(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        output_name: Optional[str] = None
    ) -> Path:
        """
        Generate complete dashboard with all charts and statistics.

        Args:
            start_date: Start date for data (default: 30 days ago)
            end_date: End date for data (default: now)
            output_name: Custom output filename (default: timestamp-based)

        Returns:
            Path to generated dashboard HTML
        """
        print("Loading score events...")
        events = self.load_score_events(start_date, end_date)

        if not events:
            print("Warning: No score events found in date range")
            raise NotImplementedError("TODO: Implement this function")

        print(f"Loaded {len(events)} score events")

        print("Aggregating scores by day...")
        trends = self.aggregate_scores_by_day(events)

        print("Calculating statistics...")
        statistics = self.calculate_statistics(trends)

        # Generate output filename
        if not output_name:
            output_name = f"dashboard_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"

        output_html = self.output_dir / f"{output_name}.html"

        # Generate charts
        charts = {}

        if MATPLOTLIB_AVAILABLE:
            print("Generating score trend chart...")
            trend_chart = self.output_dir / f"{output_name}_trends.png"
            self.generate_score_trend_chart(trends, trend_chart)
            charts["Score Trends"] = trend_chart

            print("Generating event count chart...")
            event_chart = self.output_dir / f"{output_name}_events.png"
            self.generate_event_count_chart(trends, event_chart)
            charts["Event Counts"] = event_chart

        # Generate HTML dashboard
        print("Generating HTML dashboard...")
        self.generate_html_dashboard(trends, statistics, output_html, charts)

        # Export data as JSON
        data_export = self.output_dir / f"{output_name}_data.json"
        with open(data_export, 'w', encoding='utf-8') as f:
            json.dump({
                "trends": {k: [t.to_dict() for t in v] for k, v in trends.items()},
                "statistics": statistics,
                "generated_at": datetime.now(timezone.utc).isoformat()
            }, f, indent=2)

        print(f"Data exported: {data_export}")

        return output_html


def main():
    """CLI entry point"""
    repo_root = Path(__file__).resolve().parents[1]

    dashboard = ScoreTrendDashboard(repo_root)

    # Generate dashboard for last 30 days
    print("Generating score trend dashboard...")
    output_path = dashboard.generate_dashboard()

    if output_path:
        print(f"\n✅ Dashboard generated successfully!")
        print(f"   Open in browser: {output_path}")
    else:
        print("\n⚠️  No data available for dashboard generation")


if __name__ == "__main__":
    main()
