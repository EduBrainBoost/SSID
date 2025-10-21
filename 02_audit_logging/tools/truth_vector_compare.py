#!/usr/bin/env python3
"""
Truth Vector Compare - Release-to-Release Integrity Governance

This CLI tool compares Truth Vector magnitudes between releases to objectively
measure integrity evolution. Calculates Δ|V| and automatically determines
whether a new release represents integrity gain or loss.

Mathematical Foundation:
- Δ|V| = |V_new| - |V_baseline|
- Δ|V| > +0.05: Significant improvement
- Δ|V| = -0.03 to +0.05: Stable (normal fluctuation)
- Δ|V| < -0.03: Degradation - investigate
- Δ|V| < -0.10: Critical decline - block release

Usage:
    python truth_vector_compare.py --baseline v1.0.0 --new v2.0.0
    python truth_vector_compare.py --auto  # Compare to latest baseline
    python truth_vector_compare.py --trend  # Show historical trend

Copyright: SSID Project
License: ROOT-24-LOCK compliant
Version: 1.0.0
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timezone

# Ensure UTF-8 encoding for Windows
if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')


class TruthVectorComparator:
    """
    Compares Truth Vector magnitudes between releases for integrity governance.

    Features:
    - Δ|V| calculation with statistical significance
    - Dimension-level delta analysis (X, Y, Z)
    - Trend detection (improving, stable, degrading)
    - Release governance recommendations
    - Historical trend visualization
    """

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.reports_dir = repo_root / "02_audit_logging" / "reports"
        self.history_dir = repo_root / "02_audit_logging" / "reports" / "truth_vector_history"

        # Thresholds for interpretation
        self.thresholds = {
            "significant_improvement": 0.05,  # 5% gain
            "stable_upper": 0.05,
            "stable_lower": -0.03,
            "degradation": -0.03,  # 3% loss
            "critical": -0.10  # 10% loss
        }

        # Ensure history directory exists
        self.history_dir.mkdir(parents=True, exist_ok=True)

    def compare(self, baseline_version: str, new_version: str) -> Dict[str, Any]:
        """
        Compare two Truth Vector reports.

        Args:
            baseline_version: Baseline version identifier
            new_version: New version identifier

        Returns:
            Comparison report with Δ|V| and governance recommendation
        """
        print("=" * 70)
        print("TRUTH VECTOR COMPARE - RELEASE INTEGRITY GOVERNANCE")
        print("=" * 70)
        print()

        # Step 1: Load baseline report
        print(f"Step 1: Loading baseline report (version: {baseline_version})...")
        baseline_data = self._load_report(baseline_version)
        if not baseline_data:
            print(f"  [ERROR] Baseline report not found for {baseline_version}")
            return {}
        print(f"  Baseline |V|: {baseline_data['magnitude']:.6f}")
        print()

        # Step 2: Load new report
        print(f"Step 2: Loading new report (version: {new_version})...")
        new_data = self._load_report(new_version)
        if not new_data:
            print(f"  [ERROR] New report not found for {new_version}")
            return {}
        print(f"  New |V|: {new_data['magnitude']:.6f}")
        print()

        # Step 3: Calculate delta
        print("Step 3: Calculating Δ|V| (magnitude delta)...")
        delta_magnitude = new_data['magnitude'] - baseline_data['magnitude']
        delta_percent = (delta_magnitude / baseline_data['magnitude']) * 100
        print(f"  Δ|V| = {delta_magnitude:+.6f} ({delta_percent:+.2f}%)")
        print()

        # Step 4: Calculate dimension deltas
        print("Step 4: Calculating dimension-level deltas...")
        dimension_deltas = self._calculate_dimension_deltas(
            baseline_data['vector'],
            new_data['vector']
        )
        for dim, delta in dimension_deltas.items():
            print(f"  Δ{dim.upper()} = {delta:+.6f}")
        print()

        # Step 5: Interpret delta
        print("Step 5: Interpreting integrity change...")
        interpretation = self._interpret_delta(delta_magnitude, delta_percent)
        print(f"  Status: {interpretation['status']}")
        print(f"  Category: {interpretation['category']}")
        print()

        # Step 6: Generate governance recommendation
        print("Step 6: Generating governance recommendation...")
        recommendation = self._generate_recommendation(
            interpretation,
            delta_magnitude,
            dimension_deltas
        )
        print(f"  Action: {recommendation['action']}")
        print()

        # Step 7: Compile comparison report
        comparison = {
            "comparison_metadata": {
                "tool": "truth_vector_compare.py",
                "version": "1.0.0",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "baseline_version": baseline_version,
                "new_version": new_version
            },
            "baseline": {
                "version": baseline_version,
                "magnitude": baseline_data['magnitude'],
                "vector": baseline_data['vector'],
                "timestamp": baseline_data.get('timestamp', 'unknown')
            },
            "new": {
                "version": new_version,
                "magnitude": new_data['magnitude'],
                "vector": new_data['vector'],
                "timestamp": new_data.get('timestamp', 'unknown')
            },
            "delta": {
                "magnitude": delta_magnitude,
                "percent": delta_percent,
                "dimensions": dimension_deltas
            },
            "interpretation": interpretation,
            "recommendation": recommendation
        }

        # Step 8: Save comparison
        print("Step 8: Saving comparison report...")
        self._save_comparison(comparison, baseline_version, new_version)
        print()

        # Step 9: Display results
        self._display_comparison(comparison)

        print("=" * 70)
        print(f"INTEGRITY CHANGE: {interpretation['category']}")
        print(f"GOVERNANCE ACTION: {recommendation['action']}")
        print("=" * 70)
        print()

        return comparison

    def auto_compare(self) -> Dict[str, Any]:
        """
        Automatically compare current report to latest baseline.

        Returns:
            Comparison report
        """
        print("Auto-comparing to latest baseline...")
        print()

        # Find latest baseline
        baseline = self._find_latest_baseline()
        if not baseline:
            print("[ERROR] No baseline found. Run truth_vector_analysis.py first.")
            return {}

        # Load current report
        current_report = self.reports_dir / "truth_vector_analysis.json"
        if not current_report.exists():
            print("[ERROR] Current report not found. Run truth_vector_analysis.py first.")
            return {}

        # Use timestamp as version
        with open(current_report, 'r', encoding='utf-8') as f:
            current_data = json.load(f)
            current_version = current_data.get('analysis_metadata', {}).get('timestamp', 'current')

        return self.compare(baseline['version'], current_version)

    def show_trend(self) -> Dict[str, Any]:
        """
        Show historical trend of Truth Vector magnitude.

        Returns:
            Trend analysis report
        """
        print("=" * 70)
        print("TRUTH VECTOR HISTORICAL TREND")
        print("=" * 70)
        print()

        # Load all historical comparisons
        comparisons = self._load_all_comparisons()

        if not comparisons:
            print("[INFO] No historical comparisons found yet.")
            print("Run comparisons first to build trend data.")
            return {}

        # Sort by timestamp
        comparisons.sort(key=lambda x: x.get('comparison_metadata', {}).get('timestamp', ''))

        # Display trend
        print("Release History:")
        print("-" * 70)

        for i, comp in enumerate(comparisons, 1):
            baseline = comp.get('baseline', {})
            new = comp.get('new', {})
            delta = comp.get('delta', {})
            interp = comp.get('interpretation', {})

            print(f"{i}. {baseline.get('version', '?')} → {new.get('version', '?')}")
            print(f"   |V|: {baseline.get('magnitude', 0):.6f} → {new.get('magnitude', 0):.6f}")
            print(f"   Δ|V|: {delta.get('magnitude', 0):+.6f} ({delta.get('percent', 0):+.2f}%)")
            print(f"   Status: {interp.get('category', '?')}")
            print()

        # Overall trend
        if len(comparisons) >= 2:
            first_magnitude = comparisons[0]['baseline']['magnitude']
            last_magnitude = comparisons[-1]['new']['magnitude']
            total_delta = last_magnitude - first_magnitude
            total_percent = (total_delta / first_magnitude) * 100

            print("Overall Trend:")
            print("-" * 70)
            print(f"First Release: {first_magnitude:.6f}")
            print(f"Latest Release: {last_magnitude:.6f}")
            print(f"Total Change: {total_delta:+.6f} ({total_percent:+.2f}%)")
            print()

        return {"comparisons": comparisons}

    def _load_report(self, version: str) -> Optional[Dict[str, Any]]:
        """
        Load Truth Vector report for a specific version.

        Tries multiple strategies:
        1. Direct file with version in name
        2. Baseline file if version matches
        3. History directory
        4. Current report if version matches timestamp
        """
        # Strategy 1: Version-specific file
        version_file = self.reports_dir / f"truth_vector_analysis_{version}.json"
        if version_file.exists():
            with open(version_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return self._extract_vector_data(data, version)

        # Strategy 2: Current report (check timestamp)
        current_file = self.reports_dir / "truth_vector_analysis.json"
        if current_file.exists():
            with open(current_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                timestamp = data.get('analysis_metadata', {}).get('timestamp', '')
                if version in timestamp or version == 'current':
                    return self._extract_vector_data(data, version)

        # Strategy 3: Baseline comparison data
        baseline_file = self.reports_dir / "truth_vector_baseline.json"
        if baseline_file.exists():
            with open(baseline_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if data.get('version') == version:
                    return data

        # Strategy 4: History directory
        for history_file in self.history_dir.glob("*.json"):
            if version in history_file.name:
                with open(history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return self._extract_vector_data(data, version)

        return None

    def _extract_vector_data(self, data: Dict[str, Any], version: str) -> Dict[str, Any]:
        """Extract relevant vector data from full report."""
        truth_vector = data.get('truth_vector', {})
        return {
            "version": version,
            "magnitude": truth_vector.get('magnitude', data.get('magnitude', 0.0)),
            "vector": {
                "x": truth_vector.get('x', 0.0),
                "y": truth_vector.get('y', 0.0),
                "z": truth_vector.get('z', 0.0)
            },
            "timestamp": data.get('analysis_metadata', {}).get('timestamp', '')
        }

    def _calculate_dimension_deltas(self, baseline_vector: Dict, new_vector: Dict) -> Dict[str, float]:
        """Calculate delta for each dimension (X, Y, Z)."""
        return {
            "x": new_vector.get('x', 0) - baseline_vector.get('x', 0),
            "y": new_vector.get('y', 0) - baseline_vector.get('y', 0),
            "z": new_vector.get('z', 0) - baseline_vector.get('z', 0)
        }

    def _interpret_delta(self, delta: float, percent: float) -> Dict[str, Any]:
        """
        Interpret magnitude delta for governance.

        Returns:
            Interpretation with status, category, and explanation
        """
        if delta >= self.thresholds["significant_improvement"]:
            status = "IMPROVEMENT"
            category = "Significant Integrity Gain"
            explanation = (
                f"Δ|V| = {delta:+.6f} ({percent:+.2f}%) indicates significant improvement. "
                "The release has enhanced system integrity across multiple dimensions. "
                "This represents measurable progress in compliance and trust."
            )
            severity = "POSITIVE"

        elif delta >= self.thresholds["stable_lower"]:
            status = "STABLE"
            category = "Stable Integrity (Normal Fluctuation)"
            explanation = (
                f"Δ|V| = {delta:+.6f} ({percent:+.2f}%) falls within normal fluctuation range. "
                "The release maintains system integrity without significant gains or losses. "
                "This is expected for routine updates and minor changes."
            )
            severity = "NEUTRAL"

        elif delta >= self.thresholds["critical"]:
            status = "DEGRADATION"
            category = "Integrity Decline (Investigation Required)"
            explanation = (
                f"Δ|V| = {delta:+.6f} ({percent:+.2f}%) indicates integrity degradation. "
                "The release has weakened system integrity. Root cause analysis required. "
                "Consider reverting changes or implementing corrective measures."
            )
            severity = "WARNING"

        else:  # delta < critical threshold
            status = "CRITICAL_DECLINE"
            category = "Critical Integrity Loss (Block Release)"
            explanation = (
                f"Δ|V| = {delta:+.6f} ({percent:+.2f}%) indicates critical integrity loss. "
                "The release has severely compromised system integrity. "
                "BLOCK RELEASE - immediate investigation and remediation required."
            )
            severity = "CRITICAL"

        return {
            "status": status,
            "category": category,
            "explanation": explanation,
            "severity": severity,
            "delta": delta,
            "percent": percent
        }

    def _generate_recommendation(self, interpretation: Dict, delta: float,
                                  dimension_deltas: Dict[str, float]) -> Dict[str, Any]:
        """Generate governance recommendation based on interpretation."""
        status = interpretation['status']
        severity = interpretation['severity']

        # Identify most changed dimension
        max_delta_dim = max(dimension_deltas.items(), key=lambda x: abs(x[1]))
        dimension_name = {"x": "Structural", "y": "Content", "z": "Temporal"}[max_delta_dim[0]]

        if status == "IMPROVEMENT":
            action = "APPROVE"
            reason = "Release improves system integrity"
            next_steps = [
                "Document improvements in release notes",
                "Update baseline for future comparisons",
                "Continue monitoring in production"
            ]

        elif status == "STABLE":
            action = "APPROVE"
            reason = "Release maintains integrity within acceptable bounds"
            next_steps = [
                "Proceed with standard deployment",
                "Monitor for unexpected changes post-deployment"
            ]

        elif status == "DEGRADATION":
            action = "INVESTIGATE"
            reason = f"Integrity decline detected (Δ|V| = {delta:+.6f})"
            next_steps = [
                f"Investigate {dimension_name} dimension (Δ{max_delta_dim[0].upper()} = {max_delta_dim[1]:+.6f})",
                "Review changes that may have caused degradation",
                "Consider selective rollback of problematic changes",
                "Re-run forensic analysis after fixes"
            ]

        else:  # CRITICAL_DECLINE
            action = "BLOCK"
            reason = f"Critical integrity loss (Δ|V| = {delta:+.6f})"
            next_steps = [
                "BLOCK RELEASE - do not deploy",
                "Immediate root cause analysis required",
                f"Focus on {dimension_name} dimension (Δ{max_delta_dim[0].upper()} = {max_delta_dim[1]:+.6f})",
                "Revert changes and re-test",
                "Escalate to security team"
            ]

        return {
            "action": action,
            "reason": reason,
            "severity": severity,
            "next_steps": next_steps,
            "focus_dimension": dimension_name,
            "focus_delta": max_delta_dim[1]
        }

    def _find_latest_baseline(self) -> Optional[Dict[str, Any]]:
        """Find latest baseline for auto-comparison."""
        baseline_file = self.reports_dir / "truth_vector_baseline.json"
        if baseline_file.exists():
            with open(baseline_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None

    def _save_comparison(self, comparison: Dict, baseline_version: str, new_version: str):
        """Save comparison to history."""
        # Save to history directory
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"comparison_{baseline_version}_to_{new_version}_{timestamp}.json"
        filepath = self.history_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(comparison, f, indent=2, ensure_ascii=False)

        print(f"  Saved: {filepath}")

    def _load_all_comparisons(self) -> List[Dict]:
        """Load all historical comparisons."""
        comparisons = []
        for comp_file in self.history_dir.glob("comparison_*.json"):
            try:
                with open(comp_file, 'r', encoding='utf-8') as f:
                    comparisons.append(json.load(f))
            except Exception:
                pass
        return comparisons

    def _display_comparison(self, comparison: Dict):
        """Display comparison results in formatted output."""
        print("=" * 70)
        print("COMPARISON RESULTS")
        print("=" * 70)
        print()

        baseline = comparison['baseline']
        new = comparison['new']
        delta = comparison['delta']
        interp = comparison['interpretation']
        rec = comparison['recommendation']

        # Magnitude comparison
        print("Truth Vector Magnitude:")
        print("-" * 70)
        print(f"Baseline ({baseline['version']}):  {baseline['magnitude']:.6f}")
        print(f"New ({new['version']}):       {new['magnitude']:.6f}")
        print(f"Delta:                  {delta['magnitude']:+.6f} ({delta['percent']:+.2f}%)")
        print()

        # Dimension deltas
        print("Dimension Deltas:")
        print("-" * 70)
        print(f"ΔX (Structural):   {delta['dimensions']['x']:+.6f}")
        print(f"ΔY (Content):      {delta['dimensions']['y']:+.6f}")
        print(f"ΔZ (Temporal):     {delta['dimensions']['z']:+.6f}")
        print()

        # Interpretation
        print("Interpretation:")
        print("-" * 70)
        print(f"Status: {interp['status']}")
        print(f"Category: {interp['category']}")
        print(f"Severity: {interp['severity']}")
        print()
        print(interp['explanation'])
        print()

        # Recommendation
        print("Governance Recommendation:")
        print("-" * 70)
        print(f"Action: {rec['action']}")
        print(f"Reason: {rec['reason']}")
        print(f"Focus Dimension: {rec['focus_dimension']} (Δ = {rec['focus_delta']:+.6f})")
        print()
        print("Next Steps:")
        for i, step in enumerate(rec['next_steps'], 1):
            print(f"  {i}. {step}")
        print()


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Compare Truth Vector magnitudes between releases",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Compare specific versions
  python truth_vector_compare.py --baseline v1.0.0 --new v2.0.0

  # Auto-compare to latest baseline
  python truth_vector_compare.py --auto

  # Show historical trend
  python truth_vector_compare.py --trend
        """
    )

    parser.add_argument('--baseline', type=str, help='Baseline version identifier')
    parser.add_argument('--new', type=str, help='New version identifier')
    parser.add_argument('--auto', action='store_true', help='Auto-compare to latest baseline')
    parser.add_argument('--trend', action='store_true', help='Show historical trend')

    args = parser.parse_args()

    # Detect repository root
    repo_root = Path(__file__).resolve().parent.parent.parent

    # Create comparator
    comparator = TruthVectorComparator(repo_root)

    # Execute requested operation
    if args.trend:
        result = comparator.show_trend()
    elif args.auto:
        result = comparator.auto_compare()
    elif args.baseline and args.new:
        result = comparator.compare(args.baseline, args.new)
    else:
        parser.print_help()
        return 1

    # Exit code based on recommendation
    if result:
        action = result.get('recommendation', {}).get('action', 'APPROVE')
        if action == "BLOCK":
            return 2  # Critical - block release
        elif action == "INVESTIGATE":
            return 1  # Warning - investigate
        else:
            return 0  # Approve

    return 0


if __name__ == "__main__":
    sys.exit(main())
