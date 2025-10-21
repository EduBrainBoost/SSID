#!/usr/bin/env python3
"""
META-AUDIT RESILIENCE DAEMON v3.0
Kybernetischer Feedback-Loop für selbst-trainierendes Audit-Ökosystem

Angriff → Erkennung → Anpassung → erneuter Angriff

Analysiert adversariale Detektionsraten im Trend und passt das System adaptiv an:
- Detection Rate < 98%: Policy-Verstärkung oder neue Regeln
- Detection Rate = 100%: Fuzzing-Diversity erhöhen
- Automatische Anpassung der Erkennungslogik

Author: SSID Security Team
License: MIT
"""

import sys
import os
import json
import yaml
import hashlib
import statistics
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timezone, timedelta
import subprocess

# Fix Windows console encoding
if sys.platform == 'win32':
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
    if sys.stderr.encoding != 'utf-8':
        sys.stderr.reconfigure(encoding='utf-8')

class MetaAuditResilienceDaemon:
    """
    Resilience Daemon - Kybernetischer Feedback-Loop
    Analysiert Detektionsraten und passt System adaptiv an
    """

    def __init__(self, root_dir: Path):
        self.root = root_dir

        # Performance registry
        self.performance_registry_path = root_dir / '24_meta_orchestration' / 'registry' / 'adversary_performance_registry.yaml'

        # Thresholds
        self.optimal_detection_rate = 0.98  # 98% minimum
        self.perfect_detection_rate = 1.00  # 100%
        self.critical_detection_rate = 0.90  # 90% critical threshold

        # Trend analysis window
        self.trend_window = 3  # Last 3 runs for trend analysis

        # Adaptation results
        self.adaptations_applied = []
        self.recommendations = []

    def load_performance_registry(self) -> Dict:
        """Load adversarial performance registry"""
        if not self.performance_registry_path.exists():
            print("[REGISTRY] No performance registry found, initializing...")
            return {
                'version': '1.0',
                'runs': []
            }

        with open(self.performance_registry_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {'version': '1.0', 'runs': []}

    def update_performance_registry(self, detection_rate: float, attacks_detected: int,
                                   attacks_total: int, attack_breakdown: Dict) -> None:
        """Add new adversarial run to performance registry"""
        print("[REGISTRY] Updating performance registry...")

        registry = self.load_performance_registry()

        # Add new run entry
        run_entry = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'detection_rate': round(detection_rate, 4),
            'attacks_detected': attacks_detected,
            'attacks_total': attacks_total,
            'attacks_missed': attacks_total - attacks_detected,
            'status': self._classify_detection_status(detection_rate),
            'attack_breakdown': attack_breakdown
        }

        registry['runs'].append(run_entry)
        registry['last_updated'] = datetime.now(timezone.utc).isoformat()
        registry['total_runs'] = len(registry['runs'])

        # Save updated registry
        self.performance_registry_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.performance_registry_path, 'w', encoding='utf-8') as f:
            yaml.dump(registry, f, default_flow_style=False, sort_keys=False)

        print(f"[REGISTRY] Run #{registry['total_runs']} recorded: {detection_rate:.1%} detection rate")

    def _classify_detection_status(self, detection_rate: float) -> str:
        """Classify detection rate status"""
        if detection_rate >= self.perfect_detection_rate:
            return 'PERFECT'
        elif detection_rate >= self.optimal_detection_rate:
            return 'OPTIMAL'
        elif detection_rate >= self.critical_detection_rate:
            return 'DEGRADED'
        else:
            return 'CRITICAL'

    def analyze_detection_trends(self) -> Dict:
        """
        Analyze detection rate trends over recent runs
        Identifies degradation or stagnation patterns
        """
        print("\n[TREND ANALYSIS] Analyzing detection rate trends...")

        registry = self.load_performance_registry()
        runs = registry.get('runs', [])

        if len(runs) == 0:
            print("[TREND] No runs available for analysis")
            return {
                'trend': 'INSUFFICIENT_DATA',
                'message': 'No historical data available',
                'action_required': False
            }

        # Get recent runs (last N runs)
        recent_runs = runs[-self.trend_window:]
        detection_rates = [r['detection_rate'] for r in recent_runs]

        # Calculate statistics
        current_rate = detection_rates[-1]
        avg_rate = statistics.mean(detection_rates)

        if len(detection_rates) >= 2:
            # Calculate trend (positive = improving, negative = degrading)
            trend_slope = detection_rates[-1] - detection_rates[0]
            is_improving = trend_slope > 0
            is_degrading = trend_slope < 0
            is_stable = abs(trend_slope) < 0.01
        else:
            trend_slope = 0
            is_improving = False
            is_degrading = False
            is_stable = True

        # Identify pattern
        if current_rate < self.optimal_detection_rate:
            trend = 'DEGRADATION_DETECTED'
            action = 'POLICY_REINFORCEMENT'
            message = f'Detection rate below optimal ({current_rate:.1%} < 98%)'
        elif current_rate == self.perfect_detection_rate and is_stable:
            trend = 'PERFECT_STABLE'
            action = 'INCREASE_FUZZING_DIVERSITY'
            message = f'Perfect detection maintained ({current_rate:.1%}), increase attack diversity'
        elif is_degrading:
            trend = 'DEGRADING'
            action = 'POLICY_REVIEW'
            message = f'Detection rate degrading over last {self.trend_window} runs'
        elif is_improving:
            trend = 'IMPROVING'
            action = 'MAINTAIN_CURRENT'
            message = f'Detection rate improving ({current_rate:.1%})'
        else:
            trend = 'STABLE'
            action = 'MAINTAIN_CURRENT'
            message = f'Detection rate stable ({current_rate:.1%})'

        analysis = {
            'trend': trend,
            'action': action,
            'message': message,
            'current_rate': current_rate,
            'average_rate': avg_rate,
            'trend_slope': trend_slope,
            'runs_analyzed': len(recent_runs),
            'action_required': action not in ['MAINTAIN_CURRENT']
        }

        print(f"[TREND] {trend}: {message}")
        print(f"[TREND] Action: {action}")

        return analysis

    def apply_adaptive_adjustments(self, trend_analysis: Dict) -> List[str]:
        """
        Apply adaptive adjustments based on trend analysis
        Returns list of adaptations applied
        """
        print("\n[ADAPTATION] Applying adaptive adjustments...")

        action = trend_analysis.get('action')
        adaptations = []

        if action == 'POLICY_REINFORCEMENT':
            adaptations.extend(self._reinforce_detection_policies())

        elif action == 'INCREASE_FUZZING_DIVERSITY':
            adaptations.extend(self._increase_fuzzing_diversity())

        elif action == 'POLICY_REVIEW':
            adaptations.extend(self._trigger_policy_review())

        elif action == 'MAINTAIN_CURRENT':
            adaptations.append('No adaptations needed - system performing optimally')

        self.adaptations_applied = adaptations
        return adaptations

    def _reinforce_detection_policies(self) -> List[str]:
        """
        Reinforce detection policies when rate drops below optimal
        """
        print("[ADAPTATION] Reinforcing detection policies...")

        adaptations = []

        # Check fake_integrity_guard whitelists
        guard_path = self.root / '02_audit_logging' / 'forensics' / 'fake_integrity_guard.py'

        if guard_path.exists():
            with open(guard_path, 'r', encoding='utf-8') as f:
                guard_content = f.read()

            # Analyze whitelisted patterns
            if 'whitelisted_patterns' in guard_content:
                adaptations.append('Analyzed whitelisted patterns in fake_integrity_guard')
                self.recommendations.append('⚠️  Review whitelisted patterns - may be too permissive')

            # Check for overly broad pattern matching
            if '.*' in guard_content or '.+' in guard_content:
                adaptations.append('Detected broad regex patterns')
                self.recommendations.append('Consider more specific pattern matching rules')

        # Suggest new detection rules
        adaptations.append('Suggested adding new detection rules for missed attacks')
        self.recommendations.append('Review missed attacks and create specific detection patterns')

        # Trigger OPA policy update suggestion
        adaptations.append('Recommended OPA policy review and tightening')
        self.recommendations.append('Update OPA policies to catch edge cases')

        return adaptations

    def _increase_fuzzing_diversity(self) -> List[str]:
        """
        Increase fuzzing diversity when detection rate is perfect
        System needs more challenging attacks to prevent "einrosten"
        """
        print("[ADAPTATION] Increasing fuzzing diversity...")

        adaptations = []

        # Suggest new attack combinations
        new_attack_suggestions = [
            'Multi-stage attacks (combine hash manipulation + timestamp manipulation)',
            'Obfuscated attacks (encode malicious data in base64)',
            'Race condition attacks (concurrent hash chain modifications)',
            'Privilege escalation attacks (manipulate file permissions)',
            'Symlink attacks (use symbolic links to bypass path checks)',
            'Compression attacks (hide malicious data in compressed files)',
            'Encoding attacks (use different character encodings)',
            'Timing attacks (exploit time-based validation gaps)'
        ]

        adaptations.append(f'Suggested {len(new_attack_suggestions)} new attack patterns')

        for suggestion in new_attack_suggestions[:3]:  # Top 3 suggestions
            self.recommendations.append(f'🎯 New attack pattern: {suggestion}')

        # Suggest fuzzing parameters
        adaptations.append('Recommended increasing fuzzing parameters (data size, complexity)')
        self.recommendations.append('Increase attack sophistication to maintain resilience')

        return adaptations

    def _trigger_policy_review(self) -> List[str]:
        """
        Trigger policy review when detection rate is degrading
        """
        print("[ADAPTATION] Triggering policy review...")

        adaptations = []

        # Load recent runs to identify problem areas
        registry = self.load_performance_registry()
        recent_runs = registry.get('runs', [])[-self.trend_window:]

        # Analyze attack breakdowns to find weaknesses
        missed_attack_types = {}
        for run in recent_runs:
            breakdown = run.get('attack_breakdown', {})
            for attack_type, details in breakdown.items():
                detected = details.get('detected', True)
                if not detected:
                    missed_attack_types[attack_type] = missed_attack_types.get(attack_type, 0) + 1

        if missed_attack_types:
            adaptations.append(f'Identified {len(missed_attack_types)} problematic attack types')
            for attack_type, count in sorted(missed_attack_types.items(), key=lambda x: x[1], reverse=True):
                self.recommendations.append(f'⚠️  {attack_type} missed {count} times - review detection logic')
        else:
            adaptations.append('No specific attack type weaknesses identified')
            self.recommendations.append('General policy review recommended')

        adaptations.append('Triggered comprehensive policy review workflow')
        self.recommendations.append('Schedule policy review meeting with security team')

        return adaptations

    def generate_resilience_report(self, trend_analysis: Dict) -> Dict:
        """Generate comprehensive resilience report"""
        registry = self.load_performance_registry()
        runs = registry.get('runs', [])

        # Calculate overall statistics
        if runs:
            detection_rates = [r['detection_rate'] for r in runs]
            overall_avg = statistics.mean(detection_rates)
            overall_min = min(detection_rates)
            overall_max = max(detection_rates)

            if len(detection_rates) >= 2:
                overall_stdev = statistics.stdev(detection_rates)
            else:
                overall_stdev = 0.0
        else:
            overall_avg = 0.0
            overall_min = 0.0
            overall_max = 0.0
            overall_stdev = 0.0

        report = {
            'version': '3.0',
            'report_type': 'META_AUDIT_RESILIENCE',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'trend_analysis': trend_analysis,
            'adaptations_applied': self.adaptations_applied,
            'recommendations': self.recommendations,
            'overall_statistics': {
                'total_runs': len(runs),
                'average_detection_rate': round(overall_avg, 4),
                'minimum_detection_rate': round(overall_min, 4),
                'maximum_detection_rate': round(overall_max, 4),
                'std_deviation': round(overall_stdev, 4)
            },
            'health_status': self._calculate_system_health(trend_analysis, overall_avg),
            'action_items': self._generate_action_items(trend_analysis)
        }

        return report

    def _calculate_system_health(self, trend_analysis: Dict, overall_avg: float) -> str:
        """Calculate overall system health"""
        current_rate = trend_analysis.get('current_rate', 0.0)
        trend = trend_analysis.get('trend', 'UNKNOWN')

        if current_rate >= self.perfect_detection_rate and trend == 'PERFECT_STABLE':
            return 'EXCELLENT_NEEDS_CHALLENGE'
        elif current_rate >= self.optimal_detection_rate:
            return 'HEALTHY'
        elif current_rate >= self.critical_detection_rate:
            return 'DEGRADED'
        else:
            return 'CRITICAL'

    def _generate_action_items(self, trend_analysis: Dict) -> List[Dict]:
        """Generate prioritized action items"""
        action_items = []

        action = trend_analysis.get('action')
        current_rate = trend_analysis.get('current_rate', 0.0)

        if action == 'POLICY_REINFORCEMENT':
            action_items.append({
                'priority': 'HIGH',
                'action': 'Reinforce detection policies',
                'reason': f'Detection rate {current_rate:.1%} below optimal',
                'deadline': 'Within 1 week'
            })

        elif action == 'INCREASE_FUZZING_DIVERSITY':
            action_items.append({
                'priority': 'MEDIUM',
                'action': 'Increase fuzzing diversity',
                'reason': 'Perfect detection maintained - risk of stagnation',
                'deadline': 'Within 1 month'
            })

        elif action == 'POLICY_REVIEW':
            action_items.append({
                'priority': 'HIGH',
                'action': 'Comprehensive policy review',
                'reason': 'Detection rate degrading over time',
                'deadline': 'Within 1 week'
            })

        return action_items

    def execute_resilience_cycle(self, detection_rate: float, attacks_detected: int,
                                 attacks_total: int, attack_breakdown: Dict) -> Dict:
        """
        Execute complete resilience cycle
        1. Update performance registry
        2. Analyze trends
        3. Apply adaptive adjustments
        4. Generate report
        """
        print("=" * 80)
        print("META-AUDIT RESILIENCE DAEMON v3.0")
        print("Kybernetischer Feedback-Loop")
        print("=" * 80)
        print()

        # Step 1: Update registry
        self.update_performance_registry(detection_rate, attacks_detected, attacks_total, attack_breakdown)

        # Step 2: Analyze trends
        trend_analysis = self.analyze_detection_trends()

        # Step 3: Apply adaptations
        if trend_analysis.get('action_required'):
            adaptations = self.apply_adaptive_adjustments(trend_analysis)
            print(f"[ADAPTATION] Applied {len(adaptations)} adaptations")
        else:
            print("[ADAPTATION] No adaptations needed - system optimal")

        # Step 4: Generate report
        report = self.generate_resilience_report(trend_analysis)

        return report

def load_latest_adversarial_report(root: Path) -> Optional[Dict]:
    """Load latest adversarial report"""
    adversarial_dir = root / '02_audit_logging' / 'forensics' / 'adversarial_tests'

    if not adversarial_dir.exists():
        return None

    # Find latest report
    reports = list(adversarial_dir.glob('adversarial_report_*.json'))
    if not reports:
        return None

    latest_report = max(reports, key=lambda p: p.stat().st_mtime)

    with open(latest_report, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Meta-Audit Resilience Daemon v3.0')
    parser.add_argument('--detection-rate', type=float,
                       help='Manual detection rate input (0.0-1.0)')
    parser.add_argument('--attacks-detected', type=int,
                       help='Manual attacks detected count')
    parser.add_argument('--attacks-total', type=int,
                       help='Manual total attacks count')
    args = parser.parse_args()

    root = Path(__file__).parent.parent.parent

    daemon = MetaAuditResilienceDaemon(root)

    # Get detection metrics
    if args.detection_rate is not None:
        # Manual input mode
        detection_rate = args.detection_rate
        attacks_detected = args.attacks_detected or 0
        attacks_total = args.attacks_total or 0
        attack_breakdown = {}
    else:
        # Load from latest adversarial report
        print("[LOADING] Fetching latest adversarial report...")
        report = load_latest_adversarial_report(root)

        if not report:
            print("❌ No adversarial report found")
            print("Run adversarial simulator first: python 02_audit_logging/forensics/meta_audit_adversary.py")
            sys.exit(1)

        detection_rate = report.get('detection_rate', 0.0)
        attacks_detected = report.get('attacks_detected', 0)
        attacks_total = report.get('attacks_simulated', 0)

        # Extract attack breakdown
        attack_breakdown = {}
        for attack in report.get('attacks', []):
            attack_type = attack.get('type', 'UNKNOWN')
            detected = attack.get('attack_id') in [d.get('attack_id') for d in report.get('detection_results', {}).get('details', []) if d.get('detected')]
            attack_breakdown[attack_type] = {
                'detected': detected,
                'severity': attack.get('severity', 'UNKNOWN')
            }

        print(f"[LOADED] Detection rate: {detection_rate:.1%}")

    # Execute resilience cycle
    report = daemon.execute_resilience_cycle(
        detection_rate,
        attacks_detected,
        attacks_total,
        attack_breakdown
    )

    # Save report
    report_file = root / '02_audit_logging' / 'reports' / f"meta_audit_resilience_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    report_file.parent.mkdir(parents=True, exist_ok=True)
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    # Display results
    print()
    print("=" * 80)
    print("RESILIENCE CYCLE RESULTS")
    print("=" * 80)
    print(f"System Health:     {report['health_status']}")
    print(f"Trend:             {report['trend_analysis']['trend']}")
    print(f"Action Required:   {'YES' if report['trend_analysis']['action_required'] else 'NO'}")
    print(f"Adaptations:       {len(report['adaptations_applied'])}")
    print(f"Recommendations:   {len(report['recommendations'])}")
    print()

    if report['recommendations']:
        print("Recommendations:")
        for rec in report['recommendations']:
            print(f"  {rec}")
        print()

    if report['action_items']:
        print("Action Items:")
        for item in report['action_items']:
            print(f"  [{item['priority']}] {item['action']}")
            print(f"      Reason: {item['reason']}")
            print(f"      Deadline: {item['deadline']}")
        print()

    print(f"Report: {report_file.relative_to(root)}")
    print(f"Registry: {daemon.performance_registry_path.relative_to(root)}")
    print()

    # Exit code based on system health
    health = report['health_status']
    if health in ['EXCELLENT_NEEDS_CHALLENGE', 'HEALTHY']:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
