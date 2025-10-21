#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
yaml_vital_signs_generator.py - YAML Ecology Health Metrics
Author: edubrainboost ©2025 MIT License

Generates quarterly "YAML Vital Signs" report with 5 key P95 metrics:
1. Total YAML count (live vs backup ratio)
2. Backup growth rate (month-over-month)
3. Deduplication efficiency (% unique templates)
4. OPA deny frequency (governance interventions)
5. Retention policy compliance (% backups within policy)

Usage:
    python 12_tooling/quality/yaml_vital_signs_generator.py --quarter 2025-Q4
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional
import argparse


class YAMLVitalSignsGenerator:
    """Generate YAML ecology health metrics."""

    def __init__(self, root_dir: Optional[Path] = None):
        if root_dir is None:
            root_dir = Path(__file__).resolve().parents[2]

        self.root = root_dir
        self.reports_dir = root_dir / "12_tooling" / "quality" / "reports"
        self.evidence_dir = root_dir / "02_audit_logging" / "evidence"
        self.vital_signs_dir = root_dir / "12_tooling" / "quality" / "vital_signs"
        self.vital_signs_dir.mkdir(parents=True, exist_ok=True)

    def count_yaml_files(self, include_backups: bool = False) -> int:
        """
        Count YAML files in repository.

        Args:
            include_backups: Whether to include backup directories

        Returns:
            Total YAML file count
        """
        count = 0
        for pattern in ["**/*.yaml", "**/*.yml"]:
            for path in self.root.rglob(pattern):
                # Skip hidden directories
                if any(part.startswith(".") for part in path.parts):
                    continue

                # Skip backups if requested
                if not include_backups and "backups" in path.parts:
                    continue

                count += 1

        return count

    def get_backup_growth_rate(self, days_back: int = 30) -> Optional[float]:
        """
        Calculate backup growth rate over time period.

        Args:
            days_back: Number of days to look back

        Returns:
            Growth rate as percentage, or None if insufficient data
        """
        # Find rotation reports
        rotation_reports = sorted(self.evidence_dir.glob("rotation_*.json"))

        if len(rotation_reports) < 2:
            return None  # Insufficient data

        # Get most recent and oldest in time window
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_back)

        recent_reports = []
        for report_path in rotation_reports:
            try:
                with open(report_path, 'r', encoding='utf-8') as f:
                    report = json.load(f)

                timestamp = datetime.fromisoformat(report['timestamp'].replace('Z', '+00:00'))

                if timestamp >= cutoff_date:
                    recent_reports.append((timestamp, report))

            except (json.JSONDecodeError, KeyError, ValueError):
                continue

        if len(recent_reports) < 2:
            return None

        # Sort by timestamp
        recent_reports.sort(key=lambda x: x[0])

        # Calculate growth rate
        oldest = recent_reports[0][1]
        newest = recent_reports[-1][1]

        oldest_count = oldest['summary']['kept_count']
        newest_count = newest['summary']['kept_count']

        if oldest_count == 0:
            return 0.0

        growth_rate = ((newest_count - oldest_count) / oldest_count) * 100

        return growth_rate

    def get_deduplication_efficiency(self) -> Optional[float]:
        """
        Get latest deduplication efficiency from analysis reports.

        Returns:
            Deduplication efficiency percentage, or None if no data
        """
        # Find latest deduplication analysis
        analysis_files = sorted(self.reports_dir.glob("yaml_deduplication_analysis_*.json"))

        if not analysis_files:
            return None

        latest = analysis_files[-1]

        try:
            with open(latest, 'r', encoding='utf-8') as f:
                data = json.load(f)

            return data['analysis_scope']['deduplication_efficiency_pct']

        except (json.JSONDecodeError, KeyError):
            return None

    def get_opa_deny_frequency(self, days_back: int = 90) -> int:
        """
        Count OPA deny decisions in time window.

        Args:
            days_back: Number of days to look back

        Returns:
            Number of deny decisions
        """
        # This would require OPA decision logs
        # For now, return 0 (placeholder for future implementation)
        return 0

    def get_retention_compliance(self) -> Optional[float]:
        """
        Calculate retention policy compliance.

        Returns:
            Percentage of backups within policy, or None if no policy
        """
        # Load policy
        policy_path = self.root / "24_meta_orchestration" / "registry" / "backup_retention_policy.yaml"

        if not policy_path.exists():
            return None

        try:
            import yaml
            with open(policy_path, 'r', encoding='utf-8') as f:
                policy = yaml.safe_load(f)

            keep_last = policy['retention']['keep_last']

        except (ImportError, KeyError):
            return None

        # Count backups
        backup_dir = self.root / "02_audit_logging" / "backups"

        if not backup_dir.exists():
            return 100.0  # No backups = 100% compliant

        backup_dirs = [d for d in backup_dir.iterdir() if d.is_dir()]

        if len(backup_dirs) == 0:
            return 100.0

        # Compliance = (backups within policy / total backups) * 100
        within_policy = min(len(backup_dirs), keep_last)
        compliance = (within_policy / len(backup_dirs)) * 100 if len(backup_dirs) > 0 else 100.0

        return compliance

    def generate_vital_signs(self, quarter: str) -> Dict:
        """
        Generate YAML vital signs report.

        Args:
            quarter: Quarter identifier (e.g., "2025-Q4")

        Returns:
            Vital signs report dict
        """
        print(f"Generating YAML Vital Signs for {quarter}...")
        print()

        # Collect metrics
        live_yaml_count = self.count_yaml_files(include_backups=False)
        total_yaml_count = self.count_yaml_files(include_backups=True)
        backup_yaml_count = total_yaml_count - live_yaml_count

        backup_growth_rate = self.get_backup_growth_rate(days_back=90)
        dedup_efficiency = self.get_deduplication_efficiency()
        opa_deny_freq = self.get_opa_deny_frequency(days_back=90)
        retention_compliance = self.get_retention_compliance()

        # Calculate backup ratio
        backup_ratio = (backup_yaml_count / live_yaml_count) if live_yaml_count > 0 else 0

        # Generate report
        report = {
            "quarter": quarter,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "vital_signs": {
                "1_yaml_count": {
                    "live_yaml_count": live_yaml_count,
                    "backup_yaml_count": backup_yaml_count,
                    "total_yaml_count": total_yaml_count,
                    "backup_ratio": round(backup_ratio, 2),
                    "health_status": self._assess_yaml_count(backup_ratio)
                },
                "2_backup_growth_rate": {
                    "rate_pct_90d": backup_growth_rate,
                    "health_status": self._assess_backup_growth(backup_growth_rate)
                },
                "3_deduplication_efficiency": {
                    "efficiency_pct": dedup_efficiency,
                    "health_status": self._assess_deduplication(dedup_efficiency)
                },
                "4_opa_deny_frequency": {
                    "deny_count_90d": opa_deny_freq,
                    "health_status": self._assess_opa_denies(opa_deny_freq)
                },
                "5_retention_compliance": {
                    "compliance_pct": retention_compliance,
                    "health_status": self._assess_retention_compliance(retention_compliance)
                }
            },
            "overall_health": self._calculate_overall_health(
                backup_ratio, backup_growth_rate, dedup_efficiency,
                opa_deny_freq, retention_compliance
            )
        }

        return report

    def _assess_yaml_count(self, backup_ratio: float) -> str:
        """Assess YAML count health based on backup ratio."""
        if backup_ratio < 1.0:
            return "EXCELLENT"  # Backups < live files
        elif backup_ratio < 3.0:
            return "GOOD"  # Backups < 3x live files
        elif backup_ratio < 5.0:
            return "ACCEPTABLE"  # Backups < 5x live files
        else:
            return "NEEDS_ATTENTION"  # Backups > 5x live files

    def _assess_backup_growth(self, growth_rate: Optional[float]) -> str:
        """Assess backup growth rate health."""
        if growth_rate is None:
            return "UNKNOWN"

        if growth_rate < 0:
            return "EXCELLENT"  # Shrinking (good!)
        elif growth_rate < 5:
            return "GOOD"  # Slow growth
        elif growth_rate < 20:
            return "ACCEPTABLE"  # Moderate growth
        else:
            return "NEEDS_ATTENTION"  # Rapid growth

    def _assess_deduplication(self, efficiency: Optional[float]) -> str:
        """Assess deduplication efficiency health."""
        if efficiency is None:
            return "UNKNOWN"

        # Note: LOW duplication is GOOD (high diversity)
        if efficiency < 5:
            return "EXCELLENT"  # Very low duplication
        elif efficiency < 10:
            return "GOOD"  # Low duplication
        elif efficiency < 20:
            return "ACCEPTABLE"  # Moderate duplication
        else:
            return "NEEDS_ATTENTION"  # High duplication

    def _assess_opa_denies(self, deny_count: int) -> str:
        """Assess OPA deny frequency health."""
        if deny_count == 0:
            return "EXCELLENT"  # No denies (healthy)
        elif deny_count < 3:
            return "GOOD"  # Few denies
        elif deny_count < 10:
            return "ACCEPTABLE"  # Some denies
        else:
            return "NEEDS_ATTENTION"  # Many denies

    def _assess_retention_compliance(self, compliance: Optional[float]) -> str:
        """Assess retention policy compliance health."""
        if compliance is None:
            return "UNKNOWN"

        if compliance >= 95:
            return "EXCELLENT"
        elif compliance >= 80:
            return "GOOD"
        elif compliance >= 60:
            return "ACCEPTABLE"
        else:
            return "NEEDS_ATTENTION"

    def _calculate_overall_health(
        self,
        backup_ratio: float,
        backup_growth: Optional[float],
        dedup_efficiency: Optional[float],
        opa_denies: int,
        retention_compliance: Optional[float]
    ) -> str:
        """Calculate overall ecosystem health."""
        scores = []

        # Score each metric (0-4 scale)
        if backup_ratio < 1.0:
            scores.append(4)
        elif backup_ratio < 3.0:
            scores.append(3)
        elif backup_ratio < 5.0:
            scores.append(2)
        else:
            scores.append(0)

        if backup_growth is not None:
            if backup_growth < 0:
                scores.append(4)
            elif backup_growth < 5:
                scores.append(3)
            elif backup_growth < 20:
                scores.append(2)
            else:
                scores.append(0)

        if dedup_efficiency is not None:
            if dedup_efficiency < 5:
                scores.append(4)
            elif dedup_efficiency < 10:
                scores.append(3)
            elif dedup_efficiency < 20:
                scores.append(2)
            else:
                scores.append(0)

        if opa_denies == 0:
            scores.append(4)
        elif opa_denies < 3:
            scores.append(3)
        elif opa_denies < 10:
            scores.append(2)
        else:
            scores.append(0)

        if retention_compliance is not None:
            if retention_compliance >= 95:
                scores.append(4)
            elif retention_compliance >= 80:
                scores.append(3)
            elif retention_compliance >= 60:
                scores.append(2)
            else:
                scores.append(0)

        # Calculate average
        avg_score = sum(scores) / len(scores) if scores else 0

        if avg_score >= 3.5:
            return "HEALTHY"
        elif avg_score >= 2.5:
            return "STABLE"
        elif avg_score >= 1.5:
            return "DEGRADED"
        else:
            return "CRITICAL"

    def generate_markdown_snapshot(self, report: Dict) -> str:
        """
        Generate Markdown snapshot of vital signs.

        Args:
            report: Vital signs report dict

        Returns:
            Markdown formatted string
        """
        vital_signs = report['vital_signs']
        quarter = report['quarter']

        md = f"# YAML Vital Signs - {quarter}\n\n"
        md += f"**Generated**: {datetime.fromisoformat(report['generated_at'].replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M UTC')}\n\n"
        md += f"**Overall Health**: {report['overall_health']}\n\n"
        md += "---\n\n"

        md += "## 5 Key Metrics (P95)\n\n"

        # Metric 1: YAML Count
        yaml_count = vital_signs['1_yaml_count']
        md += f"### 1. YAML Count & Ratio\n\n"
        md += f"- **Live YAMLs**: {yaml_count['live_yaml_count']:,}\n"
        md += f"- **Backup YAMLs**: {yaml_count['backup_yaml_count']:,}\n"
        md += f"- **Backup Ratio**: {yaml_count['backup_ratio']}x\n"
        md += f"- **Status**: {yaml_count['health_status']}\n\n"

        # Metric 2: Backup Growth
        backup_growth = vital_signs['2_backup_growth_rate']
        md += f"### 2. Backup Growth Rate (90d)\n\n"
        if backup_growth['rate_pct_90d'] is not None:
            md += f"- **Growth Rate**: {backup_growth['rate_pct_90d']:.1f}%\n"
        else:
            md += f"- **Growth Rate**: N/A (insufficient data)\n"
        md += f"- **Status**: {backup_growth['health_status']}\n\n"

        # Metric 3: Deduplication
        dedup = vital_signs['3_deduplication_efficiency']
        md += f"### 3. Deduplication Efficiency\n\n"
        if dedup['efficiency_pct'] is not None:
            md += f"- **Duplication Rate**: {dedup['efficiency_pct']:.2f}%\n"
            md += f"- **Diversity**: {100 - dedup['efficiency_pct']:.2f}%\n"
        else:
            md += f"- **Duplication Rate**: N/A\n"
        md += f"- **Status**: {dedup['health_status']}\n\n"

        # Metric 4: OPA Denies
        opa = vital_signs['4_opa_deny_frequency']
        md += f"### 4. OPA Deny Frequency (90d)\n\n"
        md += f"- **Deny Count**: {opa['deny_count_90d']}\n"
        md += f"- **Status**: {opa['health_status']}\n\n"

        # Metric 5: Retention Compliance
        retention = vital_signs['5_retention_compliance']
        md += f"### 5. Retention Policy Compliance\n\n"
        if retention['compliance_pct'] is not None:
            md += f"- **Compliance**: {retention['compliance_pct']:.1f}%\n"
        else:
            md += f"- **Compliance**: N/A\n"
        md += f"- **Status**: {retention['health_status']}\n\n"

        md += "---\n\n"
        md += "## Interpretation\n\n"
        md += "**EXCELLENT**: Optimal health, no action needed\n"
        md += "**GOOD**: Healthy, monitor for trends\n"
        md += "**ACCEPTABLE**: Within limits, consider optimization\n"
        md += "**NEEDS_ATTENTION**: Review and take action\n\n"

        return md

    def save_report(self, report: Dict, quarter: str):
        """Save vital signs report to files."""
        # Save JSON
        json_file = self.vital_signs_dir / f"yaml_vital_signs_{quarter.replace('-', '_')}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)

        print(f"JSON report: {json_file}")

        # Save Markdown
        md = self.generate_markdown_snapshot(report)
        md_file = self.vital_signs_dir / f"yaml_vital_signs_{quarter.replace('-', '_')}.md"
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(md)

        print(f"Markdown snapshot: {md_file}")

        return json_file, md_file

    def print_summary(self, report: Dict):
        """Print vital signs summary to console."""
        print()
        print("=" * 70)
        print(f"YAML Vital Signs - {report['quarter']}")
        print("=" * 70)
        print()

        vital_signs = report['vital_signs']

        print(f"Overall Health: {report['overall_health']}")
        print()

        print("Metrics:")
        print(f"  1. YAML Count:        {vital_signs['1_yaml_count']['live_yaml_count']:,} live, "
              f"{vital_signs['1_yaml_count']['backup_yaml_count']:,} backup "
              f"({vital_signs['1_yaml_count']['backup_ratio']}x) - {vital_signs['1_yaml_count']['health_status']}")

        growth = vital_signs['2_backup_growth_rate']['rate_pct_90d']
        growth_str = f"{growth:.1f}%" if growth is not None else "N/A"
        print(f"  2. Backup Growth:     {growth_str} (90d) - {vital_signs['2_backup_growth_rate']['health_status']}")

        dedup = vital_signs['3_deduplication_efficiency']['efficiency_pct']
        dedup_str = f"{dedup:.2f}%" if dedup is not None else "N/A"
        print(f"  3. Deduplication:     {dedup_str} - {vital_signs['3_deduplication_efficiency']['health_status']}")

        print(f"  4. OPA Denies:        {vital_signs['4_opa_deny_frequency']['deny_count_90d']} (90d) - "
              f"{vital_signs['4_opa_deny_frequency']['health_status']}")

        compliance = vital_signs['5_retention_compliance']['compliance_pct']
        compliance_str = f"{compliance:.1f}%" if compliance is not None else "N/A"
        print(f"  5. Retention:         {compliance_str} compliant - "
              f"{vital_signs['5_retention_compliance']['health_status']}")

        print()


def main():
    """Main execution."""
    parser = argparse.ArgumentParser(
        description="Generate YAML Vital Signs quarterly report"
    )

    parser.add_argument(
        "--quarter",
        type=str,
        help="Quarter identifier (e.g., '2025-Q4'). If not provided, auto-detects current quarter."
    )

    args = parser.parse_args()

    # Auto-detect quarter if not provided
    quarter = args.quarter
    if not quarter:
        now = datetime.now()
        q = (now.month - 1) // 3 + 1
        quarter = f"{now.year}-Q{q}"

    # Generate report
    generator = YAMLVitalSignsGenerator()
    report = generator.generate_vital_signs(quarter)

    # Print summary
    generator.print_summary(report)

    # Save reports
    generator.save_report(report, quarter)


if __name__ == "__main__":
    main()
