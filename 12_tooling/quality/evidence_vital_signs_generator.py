#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
evidence_vital_signs_generator.py - Evidence Storage Health Monitor
Author: edubrainboost ©2025 MIT License

Generates "Evidence Vital Signs" - 5 key metrics tracking evidence storage health.
Analogous to YAML Vital Signs, provides monthly snapshot for long-term monitoring.

5 Key Metrics:
    1. Active Evidence Count (files in active window)
    2. Archive Size (total compressed archive storage)
    3. Verify Success Rate (% of archives with valid checksums)
    4. Integrity Errors (count of checksum mismatches)
    5. OPA Deny Events (policy violations in last 30 days)

Output:
    - Markdown snapshot: evidence_vital_signs_YYYY-MM.md
    - JSON report: evidence_vital_signs_YYYY-MM.json

Usage:
    # Generate current month's vital signs
    python evidence_vital_signs_generator.py

    # Generate for specific month
    python evidence_vital_signs_generator.py --month 2025-10
"""

import sys
import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple
import argparse


class EvidenceVitalSignsGenerator:
    """Generate Evidence Vital Signs health metrics."""

    def __init__(self, root_dir: Optional[Path] = None):
        if root_dir is None:
            root_dir = Path(__file__).resolve().parents[2]

        self.root = root_dir
        self.evidence_dir = root_dir / "02_audit_logging" / "evidence"
        self.archive_dir = root_dir / "02_audit_logging" / "archives" / "evidence"
        self.output_dir = root_dir / "12_tooling" / "quality" / "vital_signs"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def count_active_evidence(self) -> Tuple[int, float]:
        """
        Count active evidence files and total size.

        Returns:
            Tuple of (file_count, size_mb)
        """
        if not self.evidence_dir.exists():
            return 0, 0.0

        file_count = 0
        total_bytes = 0

        for file_path in self.evidence_dir.rglob("*"):
            if file_path.is_file() and file_path.name not in [".gitkeep", ".gitignore"]:
                file_count += 1
                total_bytes += file_path.stat().st_size

        size_mb = total_bytes / (1024 * 1024)
        return file_count, size_mb

    def analyze_archives(self) -> Dict:
        """
        Analyze archive storage and integrity.

        Returns:
            Dict with archive metrics
        """
        if not self.archive_dir.exists():
            return {
                "archive_count": 0,
                "total_size_mb": 0.0,
                "verified_archives": 0,
                "integrity_errors": 0,
                "verify_success_rate": 0.0
            }

        archives = list(self.archive_dir.glob("*.tar.gz"))
        total_bytes = sum(archive.stat().st_size for archive in archives)

        # Check verification files
        verified_count = 0
        integrity_errors = 0

        for archive in archives:
            verify_file = archive.with_suffix('.tar.gz.verify.json')

            if verify_file.exists():
                # Load verification data
                with open(verify_file, 'r', encoding='utf-8') as f:
                    verification = json.load(f)

                # Verify archive checksum
                with open(archive, 'rb') as f:
                    actual_hash = hashlib.sha256(f.read()).hexdigest()

                if actual_hash == verification.get('archive_sha256'):
                    verified_count += 1
                else:
                    integrity_errors += 1

        verify_success_rate = (verified_count / len(archives) * 100) if archives else 0.0

        return {
            "archive_count": len(archives),
            "total_size_mb": total_bytes / (1024 * 1024),
            "verified_archives": verified_count,
            "integrity_errors": integrity_errors,
            "verify_success_rate": verify_success_rate
        }

    def count_opa_denies(self, days_back: int = 30) -> int:
        """
        Count OPA policy deny events in recent cleanup reports.

        Args:
            days_back: Number of days to look back

        Returns:
            Count of OPA deny events
        """
        if not self.evidence_dir.exists():
            return 0

        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_back)
        deny_count = 0

        # Search for cleanup reports
        cleanup_reports = list(self.evidence_dir.glob("evidence_cleanup_*.json"))

        for report_path in cleanup_reports:
            # Check report age
            report_time = datetime.fromtimestamp(
                report_path.stat().st_mtime,
                tz=timezone.utc
            )

            if report_time < cutoff_date:
                continue

            # Check for OPA denies
            try:
                with open(report_path, 'r', encoding='utf-8') as f:
                    report = json.load(f)

                if report.get('opa_decision', {}).get('allow') is False:
                    deny_count += 1
            except (json.JSONDecodeError, KeyError):
                continue

        return deny_count

    def calculate_overall_health(self, metrics: Dict) -> str:
        """
        Calculate overall evidence health status.

        Args:
            metrics: Vital signs metrics

        Returns:
            Health status: HEALTHY, STABLE, NEEDS_ATTENTION, CRITICAL
        """
        active_count = metrics['1_active_evidence']['count']
        integrity_errors = metrics['4_integrity_errors']['count']
        verify_success_rate = metrics['3_verify_success']['rate_pct']

        # Critical conditions
        if active_count > 500:
            return "CRITICAL"
        if integrity_errors > 0:
            return "CRITICAL"
        if verify_success_rate < 95.0 and metrics['2_archive_size']['archive_count'] > 0:
            return "CRITICAL"

        # Warning conditions
        if active_count > 400:
            return "NEEDS_ATTENTION"
        if verify_success_rate < 98.0 and metrics['2_archive_size']['archive_count'] > 0:
            return "NEEDS_ATTENTION"

        # Stable conditions
        if active_count > 250:
            return "STABLE"

        return "HEALTHY"

    def generate_vital_signs(self, month: Optional[str] = None) -> Dict:
        """
        Generate Evidence Vital Signs report.

        Args:
            month: Optional month string (YYYY-MM), defaults to current

        Returns:
            Dict with vital signs metrics
        """
        if month is None:
            month = datetime.now().strftime("%Y-%m")

        print(f"Generating Evidence Vital Signs for {month}...")
        print()

        # Metric 1: Active Evidence Count
        active_count, active_size_mb = self.count_active_evidence()

        # Metric 2 & 3 & 4: Archive Analysis
        archive_metrics = self.analyze_archives()

        # Metric 5: OPA Deny Events
        opa_denies = self.count_opa_denies(days_back=30)

        # Compile vital signs
        vital_signs = {
            "month": month,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "vital_signs": {
                "1_active_evidence": {
                    "count": active_count,
                    "size_mb": round(active_size_mb, 2),
                    "threshold": 500,
                    "status": "HEALTHY" if active_count <= 500 else "CRITICAL"
                },
                "2_archive_size": {
                    "archive_count": archive_metrics["archive_count"],
                    "total_size_mb": round(archive_metrics["total_size_mb"], 2),
                    "avg_size_mb": round(
                        archive_metrics["total_size_mb"] / archive_metrics["archive_count"], 2
                    ) if archive_metrics["archive_count"] > 0 else 0.0,
                    "status": "HEALTHY"
                },
                "3_verify_success": {
                    "verified_archives": archive_metrics["verified_archives"],
                    "total_archives": archive_metrics["archive_count"],
                    "rate_pct": round(archive_metrics["verify_success_rate"], 1),
                    "threshold": 95.0,
                    "status": "HEALTHY" if archive_metrics["verify_success_rate"] >= 95.0
                            or archive_metrics["archive_count"] == 0 else "CRITICAL"
                },
                "4_integrity_errors": {
                    "count": archive_metrics["integrity_errors"],
                    "threshold": 0,
                    "status": "HEALTHY" if archive_metrics["integrity_errors"] == 0 else "CRITICAL"
                },
                "5_opa_denies": {
                    "count": opa_denies,
                    "lookback_days": 30,
                    "threshold": 2,
                    "status": "HEALTHY" if opa_denies <= 2 else "NEEDS_ATTENTION"
                }
            }
        }

        # Calculate overall health
        vital_signs["overall_health"] = self.calculate_overall_health(vital_signs["vital_signs"])

        return vital_signs

    def write_markdown_snapshot(self, vital_signs: Dict) -> Path:
        """
        Write Markdown snapshot of vital signs.

        Args:
            vital_signs: Vital signs data

        Returns:
            Path to markdown file
        """
        month = vital_signs["month"]
        md_path = self.output_dir / f"evidence_vital_signs_{month}.md"

        vs = vital_signs["vital_signs"]
        overall = vital_signs["overall_health"]

        # Health emoji
        health_emoji = {
            "HEALTHY": "✅",
            "STABLE": "🟢",
            "NEEDS_ATTENTION": "⚠️",
            "CRITICAL": "🔴"
        }.get(overall, "❓")

        content = f"""# Evidence Vital Signs - {month}

**Generated**: {vital_signs['generated_at'][:10]}
**Overall Health**: {overall} {health_emoji}

---

## 5 Key Metrics

### 1. Active Evidence Count
- **Files**: {vs['1_active_evidence']['count']}
- **Size**: {vs['1_active_evidence']['size_mb']} MB
- **Threshold**: ≤ {vs['1_active_evidence']['threshold']} files
- **Status**: {vs['1_active_evidence']['status']}

### 2. Archive Size
- **Archives**: {vs['2_archive_size']['archive_count']}
- **Total Size**: {vs['2_archive_size']['total_size_mb']} MB
- **Avg Size**: {vs['2_archive_size']['avg_size_mb']} MB/archive
- **Status**: {vs['2_archive_size']['status']}

### 3. Verify Success Rate
- **Verified**: {vs['3_verify_success']['verified_archives']} / {vs['3_verify_success']['total_archives']}
- **Success Rate**: {vs['3_verify_success']['rate_pct']}%
- **Threshold**: ≥ {vs['3_verify_success']['threshold']}%
- **Status**: {vs['3_verify_success']['status']}

### 4. Integrity Errors
- **Errors**: {vs['4_integrity_errors']['count']}
- **Threshold**: = {vs['4_integrity_errors']['threshold']}
- **Status**: {vs['4_integrity_errors']['status']}

### 5. OPA Deny Events (Last 30d)
- **Denies**: {vs['5_opa_denies']['count']}
- **Threshold**: ≤ {vs['5_opa_denies']['threshold']}
- **Status**: {vs['5_opa_denies']['status']}

---

## Interpretation

"""

        # Add interpretation based on health
        if overall == "HEALTHY":
            content += """**Evidence storage is healthy:**
- Active evidence well within limits
- No integrity errors
- Archives verified successfully
- No policy violations

**Recommendation**: Continue monitoring monthly.
"""
        elif overall == "STABLE":
            content += """**Evidence storage is stable:**
- Active evidence count moderate
- Archives functioning correctly
- Minor policy compliance

**Recommendation**: Monitor trends, consider cleanup if approaching limits.
"""
        elif overall == "NEEDS_ATTENTION":
            content += """**Evidence storage needs attention:**
- Active evidence count elevated OR
- Archive success rate below target OR
- Repeated policy violations

**Recommendation**: Review retention policy, execute rolling window cleanup.
"""
        else:  # CRITICAL
            content += """**Evidence storage is critical:**
- Active evidence exceeds limits OR
- Integrity errors detected OR
- Archive verification failing

**Recommendation**: IMMEDIATE ACTION REQUIRED. Investigate integrity errors, execute cleanup.
"""

        content += f"""
---

**Generated by**: Evidence Vital Signs Generator
**Policy**: `24_meta_orchestration/registry/evidence_retention_policy.yaml`
**Next Review**: {month} (monthly)
"""

        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return md_path

    def write_json_report(self, vital_signs: Dict) -> Path:
        """
        Write JSON report for programmatic access.

        Args:
            vital_signs: Vital signs data

        Returns:
            Path to JSON file
        """
        month = vital_signs["month"]
        json_path = self.output_dir / f"evidence_vital_signs_{month}.json"

        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(vital_signs, f, indent=2)

        return json_path


def main():
    """Main execution."""
    parser = argparse.ArgumentParser(
        description="Evidence Vital Signs Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate current month's vital signs
  python evidence_vital_signs_generator.py

  # Generate for specific month
  python evidence_vital_signs_generator.py --month 2025-10
        """
    )

    parser.add_argument(
        "--month",
        type=str,
        help="Month in YYYY-MM format (default: current month)"
    )

    args = parser.parse_args()

    generator = EvidenceVitalSignsGenerator()

    # Generate vital signs
    vital_signs = generator.generate_vital_signs(month=args.month)

    # Write outputs
    md_path = generator.write_markdown_snapshot(vital_signs)
    json_path = generator.write_json_report(vital_signs)

    print(f"Overall Health: {vital_signs['overall_health']}")
    print()
    print(f"Markdown: {md_path}")
    print(f"JSON:     {json_path}")
    print()
    print("Vital Signs Summary:")
    for key, metric in vital_signs["vital_signs"].items():
        metric_name = key.split('_', 1)[1].replace('_', ' ').title()
        status = metric.get('status', 'N/A')
        print(f"  {metric_name}: {status}")


if __name__ == "__main__":
    main()
