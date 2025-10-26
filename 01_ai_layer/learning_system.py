#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Learning System - Continuous System Improvement
===================================================

Lernt aus:
- Performance Metriken
- Fehlermustern
- Healing-Erfolgen
- System-Verhalten

Verbessert:
- Detection Algorithms
- Healing Strategies
- Performance Optimierung
- Predictive Maintenance

Version: 1.0.0
Author: SSID AI Layer Team
Date: 2025-10-24
"""

import sys
import json
import statistics
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any, Tuple
from collections import defaultdict
from dataclasses import dataclass, asdict

REPO_ROOT = Path(__file__).parent.parent


@dataclass
class PerformanceMetric:
    """Performance metric"""
    timestamp: str
    metric_name: str
    value: float
    unit: str
    phase: str


@dataclass
class LearningInsight:
    """Learning insight"""
    category: str
    insight: str
    confidence: float
    recommendation: str
    impact: str  # LOW, MEDIUM, HIGH


class LearningSystem:
    """
    AI-powered learning system that improves over time
    """

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.reports_dir = repo_root / "02_audit_logging" / "reports"
        self.learning_data_file = repo_root / "01_ai_layer" / "learning_data.json"
        self.insights_file = repo_root / "01_ai_layer" / "insights.json"

        self.metrics = []
        self.insights = []
        self.learning_data = self._load_learning_data()

    def _load_learning_data(self) -> Dict:
        """Load historical learning data"""
        if self.learning_data_file.exists():
            try:
                with open(self.learning_data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass

        return {
            "performance_history": [],
            "error_patterns": {},
            "healing_success_rate": {},
            "optimization_applied": []
        }

    def collect_metrics(self) -> List[PerformanceMetric]:
        """Collect performance metrics from recent reports"""
        print("=" * 80)
        print("COLLECTING PERFORMANCE METRICS")
        print("=" * 80)

        metrics = []

        # Get recent orchestration reports
        orchestration_reports = sorted(
            self.reports_dir.glob("orchestration_complete_*.json"),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )[:10]  # Last 10 reports

        for report_file in orchestration_reports:
            try:
                with open(report_file, 'r', encoding='utf-8') as f:
                    report = json.load(f)

                timestamp = report.get("timestamp", "")

                # Overall metrics
                metrics.append(PerformanceMetric(
                    timestamp=timestamp,
                    metric_name="overall_score",
                    value=report.get("overall_score", 0),
                    unit="score",
                    phase="overall"
                ))

                metrics.append(PerformanceMetric(
                    timestamp=timestamp,
                    metric_name="total_duration",
                    value=report.get("total_duration_seconds", 0),
                    unit="seconds",
                    phase="overall"
                ))

                # Phase metrics
                for phase in report.get("phases", []):
                    metrics.append(PerformanceMetric(
                        timestamp=timestamp,
                        metric_name=f"{phase['phase']}_score",
                        value=phase.get("score", 0),
                        unit="score",
                        phase=phase.get("phase", "unknown")
                    ))

                    metrics.append(PerformanceMetric(
                        timestamp=timestamp,
                        metric_name=f"{phase['phase']}_duration",
                        value=phase.get("duration_seconds", 0),
                        unit="seconds",
                        phase=phase.get("phase", "unknown")
                    ))

            except Exception as e:
                print(f"[WARN] Failed to parse {report_file.name}: {e}")

        self.metrics = metrics
        print(f"\nCollected {len(metrics)} metrics from {len(orchestration_reports)} reports")

        return metrics

    def analyze_trends(self) -> List[LearningInsight]:
        """Analyze trends and generate insights"""
        print("\n" + "=" * 80)
        print("ANALYZING TRENDS")
        print("=" * 80)

        insights = []

        # Group metrics by name
        metrics_by_name = defaultdict(list)
        for metric in self.metrics:
            metrics_by_name[metric.metric_name].append(metric.value)

        # Analyze each metric
        for metric_name, values in metrics_by_name.items():
            if len(values) < 2:
                continue

            # Calculate statistics
            mean = statistics.mean(values)
            if len(values) >= 2:
                stdev = statistics.stdev(values) if len(values) > 1 else 0
            else:
                stdev = 0

            # Trend detection
            if len(values) >= 3:
                recent = statistics.mean(values[:3])
                older = statistics.mean(values[-3:])
                trend = ((recent - older) / older * 100) if older != 0 else 0

                # Generate insights based on trends
                if "score" in metric_name and trend < -5:
                    insights.append(LearningInsight(
                        category="performance_degradation",
                        insight=f"{metric_name} decreased by {abs(trend):.1f}%",
                        confidence=0.8,
                        recommendation=f"Investigate {metric_name} decline",
                        impact="HIGH"
                    ))
                elif "duration" in metric_name and trend > 20:
                    insights.append(LearningInsight(
                        category="performance_degradation",
                        insight=f"{metric_name} increased by {trend:.1f}%",
                        confidence=0.7,
                        recommendation=f"Optimize {metric_name} execution",
                        impact="MEDIUM"
                    ))
                elif "score" in metric_name and mean >= 95:
                    insights.append(LearningInsight(
                        category="excellence",
                        insight=f"{metric_name} consistently high ({mean:.1f})",
                        confidence=0.9,
                        recommendation="Maintain current practices",
                        impact="LOW"
                    ))

        # Stability analysis
        if "overall_score" in metrics_by_name:
            scores = metrics_by_name["overall_score"]
            if len(scores) >= 3:
                if all(s >= 95 for s in scores[:3]):
                    insights.append(LearningInsight(
                        category="stability",
                        insight="System highly stable (3+ consecutive high scores)",
                        confidence=0.95,
                        recommendation="System ready for production load increase",
                        impact="HIGH"
                    ))

        self.insights = insights
        print(f"\nGenerated {len(insights)} insights")

        return insights

    def learn_from_errors(self) -> List[LearningInsight]:
        """Learn from error patterns"""
        print("\n" + "=" * 80)
        print("LEARNING FROM ERRORS")
        print("=" * 80)

        insights = []

        # Analyze healing history
        healing_log_file = self.repo_root / "02_audit_logging" / "self_healing_log.json"
        if healing_log_file.exists():
            try:
                with open(healing_log_file, 'r', encoding='utf-8') as f:
                    healing_history = json.load(f)

                if healing_history:
                    # Count healing actions
                    action_counts = defaultdict(int)
                    for entry in healing_history:
                        action = entry.get("action", "unknown")
                        action_counts[action] += 1

                    # Find most common issues
                    for action, count in action_counts.items():
                        if count >= 3:
                            insights.append(LearningInsight(
                                category="recurring_issue",
                                insight=f"Action '{action}' used {count} times",
                                confidence=0.85,
                                recommendation=f"Implement proactive prevention for {action}",
                                impact="MEDIUM"
                            ))

                    print(f"Analyzed {len(healing_history)} healing events")

            except Exception as e:
                print(f"[WARN] Failed to analyze healing history: {e}")

        return insights

    def generate_optimizations(self) -> List[Dict[str, Any]]:
        """Generate optimization recommendations"""
        print("\n" + "=" * 80)
        print("GENERATING OPTIMIZATIONS")
        print("=" * 80)

        optimizations = []

        # Based on duration metrics
        duration_metrics = [m for m in self.metrics if "duration" in m.metric_name]
        if duration_metrics:
            avg_durations = defaultdict(list)
            for metric in duration_metrics:
                avg_durations[metric.phase].append(metric.value)

            for phase, durations in avg_durations.items():
                if durations:
                    avg = statistics.mean(durations)
                    if avg > 15:  # Slow phase
                        optimizations.append({
                            "target": phase,
                            "current_performance": f"{avg:.1f}s",
                            "recommendation": f"Optimize {phase} - currently taking {avg:.1f}s",
                            "priority": "HIGH" if avg > 30 else "MEDIUM",
                            "estimated_improvement": "20-30% faster"
                        })

        # Based on insights
        for insight in self.insights:
            if insight.impact == "HIGH":
                optimizations.append({
                    "target": insight.category,
                    "current_performance": insight.insight,
                    "recommendation": insight.recommendation,
                    "priority": "HIGH",
                    "estimated_improvement": "Significant"
                })

        print(f"\nGenerated {len(optimizations)} optimization recommendations")

        return optimizations

    def save_learning_data(self):
        """Save learning data for future use"""
        # Update learning data
        self.learning_data["performance_history"].extend(
            [asdict(m) for m in self.metrics]
        )

        # Keep only recent data (last 100 entries)
        self.learning_data["performance_history"] = \
            self.learning_data["performance_history"][-100:]

        # Save to file
        with open(self.learning_data_file, 'w', encoding='utf-8') as f:
            json.dump(self.learning_data, f, indent=2)

        print(f"\n[SAVE] Learning data saved: {self.learning_data_file}")

    def save_insights(self):
        """Save insights to file"""
        insights_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "insights": [asdict(i) for i in self.insights],
            "total_metrics_analyzed": len(self.metrics),
            "confidence_avg": statistics.mean([i.confidence for i in self.insights]) if self.insights else 0
        }

        with open(self.insights_file, 'w', encoding='utf-8') as f:
            json.dump(insights_data, f, indent=2)

        print(f"[SAVE] Insights saved: {self.insights_file}")

    def generate_report(self) -> Dict[str, Any]:
        """Generate learning report"""
        print("\n" + "=" * 80)
        print("GENERATING LEARNING REPORT")
        print("=" * 80)

        # Calculate summary statistics
        if self.metrics:
            overall_scores = [m.value for m in self.metrics if m.metric_name == "overall_score"]
            avg_score = statistics.mean(overall_scores) if overall_scores else 0

            durations = [m.value for m in self.metrics if m.metric_name == "total_duration"]
            avg_duration = statistics.mean(durations) if durations else 0
        else:
            avg_score = 0
            avg_duration = 0

        report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metrics_collected": len(self.metrics),
            "insights_generated": len(self.insights),
            "average_score": avg_score,
            "average_duration": avg_duration,
            "insights_by_category": {},
            "high_impact_insights": [],
            "learning_status": "ACTIVE"
        }

        # Group insights by category
        for insight in self.insights:
            cat = insight.category
            if cat not in report["insights_by_category"]:
                report["insights_by_category"][cat] = 0
            report["insights_by_category"][cat] += 1

            if insight.impact == "HIGH":
                report["high_impact_insights"].append(asdict(insight))

        return report

    def run_learning_cycle(self) -> Dict[str, Any]:
        """Run complete learning cycle"""
        print("=" * 80)
        print("AI LEARNING SYSTEM - CONTINUOUS IMPROVEMENT")
        print("=" * 80)
        print(f"Started: {datetime.now(timezone.utc).isoformat()}")
        print("=" * 80)

        # 1. Collect metrics
        self.collect_metrics()

        # 2. Analyze trends
        self.analyze_trends()

        # 3. Learn from errors
        error_insights = self.learn_from_errors()
        self.insights.extend(error_insights)

        # 4. Generate optimizations
        optimizations = self.generate_optimizations()

        # 5. Save data
        self.save_learning_data()
        self.save_insights()

        # 6. Generate report
        report = self.generate_report()

        # Print summary
        self._print_summary(report, optimizations)

        return report

    def _print_summary(self, report: Dict, optimizations: List):
        """Print learning summary"""
        print("\n" + "=" * 80)
        print("LEARNING SYSTEM SUMMARY")
        print("=" * 80)
        print(f"Metrics Analyzed: {report['metrics_collected']}")
        print(f"Insights Generated: {report['insights_generated']}")
        print(f"Average Score: {report['average_score']:.1f}/100")
        print(f"Average Duration: {report['average_duration']:.1f}s")

        if report.get("high_impact_insights"):
            print(f"\n[HIGH IMPACT] {len(report['high_impact_insights'])} Critical Insights:")
            for insight in report["high_impact_insights"]:
                print(f"  - {insight['insight']}")
                print(f"    Recommendation: {insight['recommendation']}")

        if optimizations:
            print(f"\n[OPTIMIZE] {len(optimizations)} Optimization Opportunities:")
            for opt in optimizations[:5]:  # Top 5
                print(f"  - [{opt['priority']}] {opt['recommendation']}")

        print("=" * 80)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="AI Learning System")
    parser.add_argument("--root", type=Path, default=REPO_ROOT, help="Repository root")
    parser.add_argument("--report-only", action="store_true", help="Only show report")

    args = parser.parse_args()

    learning_system = LearningSystem(args.root)

    if args.report_only:
        # Just load and show existing insights
        if learning_system.insights_file.exists():
            with open(learning_system.insights_file, 'r', encoding='utf-8') as f:
                print(json.dumps(json.load(f), indent=2))
        else:
            print("No insights file found. Run learning cycle first.")
        return 0

    # Run full learning cycle
    report = learning_system.run_learning_cycle()

    return 0


if __name__ == "__main__":
    sys.exit(main())
