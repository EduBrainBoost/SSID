"""
Predictive Compliance AI Module

Analyzes historical compliance anchors to predict regulatory risk patterns.
Identifies modules with highest violation rates and provides proactive recommendations.

Version: 2025-Q4
Last Updated: 2025-10-07
Maintainer: edubrainboost
Classification: AI/ML - Predictive Analytics
"""

import json
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

class ComplianceAnomalyDetector:
    """
    AI-driven anomaly detection for compliance violations.

    Uses historical anchor data and audit findings to:
    - Identify patterns in framework violations
    - Predict high-risk modules
    - Recommend proactive compliance actions
    """

    def __init__(self, repo_root: Optional[Path] = None):
        """Initialize predictive compliance AI."""
        self.repo_root = repo_root or Path(__file__).parent.parent
        self.anchor_path = self.repo_root / "02_audit_logging/evidence/registry/registry_anchor.json"
        self.blockchain_events_path = self.repo_root / "02_audit_logging/evidence/blockchain/compliance_events.jsonl"
        self.reviews_dir = self.repo_root / "23_compliance/reviews"
        self.mappings_dir = self.repo_root / "23_compliance/mappings"
        self.unified_index_path = self.mappings_dir / "compliance_unified_index.yaml"

    def load_historical_anchors(self) -> List[Dict[str, Any]]:
        """Load all historical compliance anchors."""
        if not self.anchor_path.exists():
            return []

        with open(self.anchor_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return data.get("anchors", [])

    def load_audit_findings(self) -> List[Dict[str, Any]]:
        """Load all historical audit findings from review cycles."""
        all_findings = []

        if not self.reviews_dir.exists():
            return all_findings

        for review_dir in self.reviews_dir.iterdir():
            if not review_dir.is_dir():
                continue

            audit_findings_path = review_dir / "audit_findings.yaml"
            if audit_findings_path.exists():
                try:
                    with open(audit_findings_path, "r", encoding="utf-8") as f:
                        data = yaml.safe_load(f)

                    findings = data.get("findings", [])
                    for finding in findings:
                        finding["review_cycle"] = review_dir.name
                        all_findings.append(finding)

                except Exception as e:
                    print(f"Warning: Could not load {audit_findings_path}: {e}")

        return all_findings

    def load_unified_index(self) -> Dict[str, Any]:
        """Load unified compliance index."""
        if not self.unified_index_path.exists():
            return {}

        with open(self.unified_index_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def analyze_framework_violations(self, findings: List[Dict[str, Any]]) -> Dict[str, Dict[str, int]]:
        """
        Analyze violations by framework.

        Returns:
            Dict mapping framework -> severity -> count
        """
        violations = defaultdict(lambda: defaultdict(int))

        for finding in findings:
            framework = finding.get("framework", "unknown")
            severity = finding.get("severity", "unknown")
            violations[framework][severity] += 1

        return dict(violations)

    def analyze_module_violations(self, findings: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        Analyze violations by module.

        Returns:
            Dict mapping module -> violation statistics
        """
        module_stats = defaultdict(lambda: {
            "total_findings": 0,
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
            "frameworks": Counter(),
            "categories": Counter()
        })

        for finding in findings:
            affected_modules = finding.get("affected_modules", [])
            severity = finding.get("severity", "unknown")
            framework = finding.get("framework", "unknown")
            category = finding.get("category", "unknown")

            for module in affected_modules:
                module_stats[module]["total_findings"] += 1
                module_stats[module]["frameworks"][framework] += 1
                module_stats[module]["categories"][category] += 1

                # Count by severity
                if severity in ["critical", "high", "medium", "low"]:
                    module_stats[module][severity] += 1

        return dict(module_stats)

    def calculate_risk_score(self, module_stats: Dict[str, Any]) -> float:
        """
        Calculate risk score for a module based on violation history.

        Risk Score Formula:
        - Critical: 10 points
        - High: 5 points
        - Medium: 2 points
        - Low: 1 point

        Normalized to 0-100 scale.
        """
        critical = module_stats.get("critical", 0)
        high = module_stats.get("high", 0)
        medium = module_stats.get("medium", 0)
        low = module_stats.get("low", 0)

        raw_score = (critical * 10) + (high * 5) + (medium * 2) + (low * 1)

        # Normalize to 0-100 scale (assume max possible is 100)
        # In practice, you'd calculate this based on actual distribution
        normalized_score = min(raw_score, 100)

        return normalized_score

    def predict_high_risk_modules(
        self,
        module_stats: Dict[str, Dict[str, Any]],
        threshold: float = 10.0
    ) -> List[Tuple[str, float, Dict[str, Any]]]:
        """
        Predict modules at high risk of future violations.

        Args:
            module_stats: Module violation statistics
            threshold: Minimum risk score to be considered high risk

        Returns:
            List of (module_name, risk_score, stats) sorted by risk score
        """
        risk_predictions = []

        for module, stats in module_stats.items():
            risk_score = self.calculate_risk_score(stats)

            if risk_score >= threshold:
                risk_predictions.append((module, risk_score, stats))

        # Sort by risk score descending
        risk_predictions.sort(key=lambda x: x[1], reverse=True)

        return risk_predictions

    def analyze_temporal_trends(self, findings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze temporal trends in compliance violations.

        Identifies if violations are increasing, decreasing, or stable.
        """
        # Group findings by review cycle
        cycle_stats = defaultdict(lambda: {
            "total": 0,
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0
        })

        for finding in findings:
            cycle = finding.get("review_cycle", "unknown")
            severity = finding.get("severity", "unknown")

            cycle_stats[cycle]["total"] += 1
            if severity in ["critical", "high", "medium", "low"]:
                cycle_stats[cycle][severity] += 1

        # Calculate trend (simple: compare first and last cycle)
        cycles = sorted(cycle_stats.keys())

        if len(cycles) < 2:
            trend = "insufficient_data"
            trend_direction = 0
        else:
            first_total = cycle_stats[cycles[0]]["total"]
            last_total = cycle_stats[cycles[-1]]["total"]

            if last_total > first_total * 1.1:
                trend = "increasing"
                trend_direction = 1
            elif last_total < first_total * 0.9:
                trend = "decreasing"
                trend_direction = -1
            else:
                trend = "stable"
                trend_direction = 0

        return {
            "trend": trend,
            "trend_direction": trend_direction,
            "cycle_stats": dict(cycle_stats),
            "cycles_analyzed": len(cycles)
        }

    def generate_recommendations(
        self,
        high_risk_modules: List[Tuple[str, float, Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """
        Generate actionable recommendations based on risk predictions.
        """
        recommendations = []

        for module, risk_score, stats in high_risk_modules:
            # Identify primary issue
            if stats.get("critical", 0) > 0:
                priority = "CRITICAL"
                action = "Immediate audit and remediation required"
            elif stats.get("high", 0) > 2:
                priority = "HIGH"
                action = "Schedule comprehensive compliance review"
            elif stats.get("medium", 0) > 5:
                priority = "MEDIUM"
                action = "Increase monitoring frequency and automated testing"
            else:
                priority = "LOW"
                action = "Monitor and include in next quarterly review"

            # Identify most common framework violations
            frameworks = stats.get("frameworks", Counter())
            most_common_framework = frameworks.most_common(1)[0][0] if frameworks else "unknown"

            # Identify most common categories
            categories = stats.get("categories", Counter())
            most_common_category = categories.most_common(1)[0][0] if categories else "unknown"

            recommendations.append({
                "module": module,
                "risk_score": risk_score,
                "priority": priority,
                "total_findings": stats.get("total_findings", 0),
                "primary_framework": most_common_framework,
                "primary_category": most_common_category,
                "recommended_action": action,
                "automated_testing": "Increase pytest coverage" if stats.get("total_findings", 0) > 3 else "Current testing adequate",
                "review_frequency": "Weekly" if priority == "CRITICAL" else "Monthly" if priority == "HIGH" else "Quarterly"
            })

        return recommendations

    def predict_compliance_risk(self) -> Dict[str, Any]:
        """
        Main prediction function: Analyze historical data and predict future risks.

        Returns:
            Comprehensive risk prediction report
        """
        # Load historical data
        anchors = self.load_historical_anchors()
        findings = self.load_audit_findings()

        if not findings:
            return {
                "status": "no_data",
                "message": "Insufficient historical data for predictions",
                "recommendation": "Run at least one compliance audit cycle to enable predictions"
            }

        # Analyze violations
        framework_violations = self.analyze_framework_violations(findings)
        module_violations = self.analyze_module_violations(findings)
        high_risk_modules = self.predict_high_risk_modules(module_violations)
        temporal_trends = self.analyze_temporal_trends(findings)

        # Generate recommendations
        recommendations = self.generate_recommendations(high_risk_modules)

        # Calculate overall risk score
        total_findings = len(findings)
        critical_findings = sum(1 for f in findings if f.get("severity") == "critical")
        high_findings = sum(1 for f in findings if f.get("severity") == "high")

        overall_risk_score = ((critical_findings * 10) + (high_findings * 5)) / max(total_findings, 1)

        return {
            "status": "success",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "overall_risk_score": overall_risk_score,
            "risk_level": "CRITICAL" if overall_risk_score > 7 else "HIGH" if overall_risk_score > 4 else "MEDIUM" if overall_risk_score > 2 else "LOW",
            "total_findings_analyzed": total_findings,
            "framework_violations": framework_violations,
            "high_risk_modules": [
                {
                    "module": module,
                    "risk_score": score,
                    "total_findings": stats.get("total_findings", 0)
                }
                for module, score, stats in high_risk_modules
            ],
            "temporal_trends": temporal_trends,
            "recommendations": recommendations,
            "anchors_analyzed": len(anchors)
        }

    def generate_report(self, prediction: Dict[str, Any]) -> str:
        """Generate human-readable prediction report."""
        if prediction.get("status") == "no_data":
            return f"""
═══════════════════════════════════════════════════════════════
PREDICTIVE COMPLIANCE AI - INSUFFICIENT DATA
═══════════════════════════════════════════════════════════════

{prediction.get('message', '')}

Recommendation: {prediction.get('recommendation', '')}
"""

        lines = [
            "═" * 80,
            "PREDICTIVE COMPLIANCE AI - RISK ASSESSMENT REPORT".center(80),
            "═" * 80,
            "",
            f"Generated: {prediction.get('timestamp', 'N/A')}",
            f"Findings Analyzed: {prediction.get('total_findings_analyzed', 0)}",
            f"Anchors Analyzed: {prediction.get('anchors_analyzed', 0)}",
            "",
            "OVERALL RISK ASSESSMENT",
            "─" * 80,
            f"Risk Level: {prediction.get('risk_level', 'UNKNOWN')}",
            f"Risk Score: {prediction.get('overall_risk_score', 0):.2f}/10",
            "",
            "HIGH-RISK MODULES",
            "─" * 80,
        ]

        high_risk = prediction.get("high_risk_modules", [])
        if high_risk:
            for i, module_data in enumerate(high_risk[:10], 1):  # Top 10
                lines.append(
                    f"{i:2d}. {module_data['module']:30s} | "
                    f"Risk: {module_data['risk_score']:5.1f} | "
                    f"Findings: {module_data['total_findings']}"
                )
        else:
            lines.append("✅ No high-risk modules identified")

        lines.extend([
            "",
            "TEMPORAL TRENDS",
            "─" * 80,
        ])

        trends = prediction.get("temporal_trends", {})
        lines.append(f"Trend: {trends.get('trend', 'unknown').upper()}")
        lines.append(f"Cycles Analyzed: {trends.get('cycles_analyzed', 0)}")

        lines.extend([
            "",
            "RECOMMENDATIONS",
            "─" * 80,
        ])

        recommendations = prediction.get("recommendations", [])
        if recommendations:
            for i, rec in enumerate(recommendations[:5], 1):  # Top 5
                lines.extend([
                    f"\n{i}. Module: {rec['module']}",
                    f"   Priority: {rec['priority']}",
                    f"   Action: {rec['recommended_action']}",
                    f"   Review Frequency: {rec['review_frequency']}"
                ])
        else:
            lines.append("✅ No immediate actions required")

        lines.extend([
            "",
            "═" * 80,
        ])

        return "\n".join(lines)

def main():
    """Main entry point for predictive compliance AI."""
    print("\n🤖 SSID Predictive Compliance AI\n")

    detector = ComplianceAnomalyDetector()

    # Run prediction
    prediction = detector.predict_compliance_risk()

    # Generate and print report
    report = detector.generate_report(prediction)
    print(report)

    # Save prediction to file
    output_path = Path(__file__).parent / "compliance_risk_prediction.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(prediction, f, indent=2, ensure_ascii=False)

    print(f"\n📊 Prediction data saved to: {output_path}\n")

if __name__ == "__main__":
    main()
