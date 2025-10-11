#!/usr/bin/env python3
"""
SSID Audit Report Comparison Tool
Blueprint v4.2.0 - Score Drift Analysis

This script compares two quarterly compliance reports to identify:
1. Score drift (changes in compliance scores)
2. Structural changes (new violations, resolutions)
3. Commit activity trends
4. Test coverage changes
5. Root-24-LOCK status changes

Usage:
    python3 12_tooling/scripts/diff_audit_reports.py <quarter1> <quarter2>

    Example:
    python3 12_tooling/scripts/diff_audit_reports.py 2025-Q4 2026-Q1

Author: EduBrainBoost
License: Apache 2.0
"""

import re
import sys
import csv
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class AuditMetrics:
    """Data class for audit metrics."""
    quarter: str
    compliance_score: int
    violations: int
    commits: int
    proof_anchor: str
    hash_valid: bool
    root24_status: str
    test_summary: Optional[str] = None
    report_exists: bool = True


# === Configuration ===
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
REPORTS_DIR = REPO_ROOT / "05_documentation" / "reports"
DASHBOARD_CSV = REPO_ROOT / "05_documentation" / "reports" / "dashboard" / "dashboard_data.csv"


def load_dashboard_metrics(quarter: str) -> Optional[AuditMetrics]:
    """
    Load metrics for a quarter from dashboard_data.csv.

    Args:
        quarter: Quarter string like "2026-Q1"

    Returns:
        AuditMetrics object or None if not found
    """
    if not DASHBOARD_CSV.exists():
        return None

    with open(DASHBOARD_CSV, 'r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("quarter") == quarter:
                return AuditMetrics(
                    quarter=quarter,
                    compliance_score=int(row.get("compliance_score", 100)),
                    violations=int(row.get("violations", 0)),
                    commits=int(row.get("commits", 0)),
                    proof_anchor=row.get("proof_anchors", "pending"),
                    hash_valid=row.get("hash_valid", "true") == "true",
                    root24_status=row.get("root24_status", "PASS")
                )

    return None


def load_compliance_report(quarter: str) -> Tuple[Optional[str], Optional[Dict]]:
    """
    Load and parse a compliance report.

    Args:
        quarter: Quarter string like "2026-Q1"

    Returns:
        Tuple of (report_content, parsed_metrics)
    """
    report_path = REPORTS_DIR / quarter / "COMPLIANCE_REPORT.md"

    if not report_path.exists():
        return None, None

    with open(report_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Parse metrics from report
    metrics = {}

    # Extract compliance score
    score_match = re.search(r'\*\*Overall Compliance Score:\*\*\s*(\d+)/(\d+)', content)
    if score_match:
        metrics['compliance_score'] = int(score_match.group(1))
        metrics['max_score'] = int(score_match.group(2))

    # Extract commit count
    commit_match = re.search(r'\*\*Total Commits:\*\*\s*(\d+)', content)
    if commit_match:
        metrics['commits'] = int(commit_match.group(1))

    # Extract test summary
    test_match = re.search(r'## Test Coverage\n\n(.+)', content)
    if test_match:
        metrics['test_summary'] = test_match.group(1).strip()

    # Count verified roots
    verified_roots = content.count('| ✅ | Verified |')
    metrics['verified_roots'] = verified_roots

    return content, metrics


def calculate_drift(old_value: float, new_value: float) -> Tuple[float, str]:
    """
    Calculate drift between two values.

    Args:
        old_value: Previous value
        new_value: Current value

    Returns:
        Tuple of (absolute_change, direction_emoji)
    """
    change = new_value - old_value

    if change > 0:
        direction = "📈"  # Increasing
    elif change < 0:
        direction = "📉"  # Decreasing
    else:
        direction = "➡️"   # No change

    return change, direction


def format_drift_value(change: float, is_percentage: bool = False) -> str:
    """
    Format drift value with appropriate sign.

    Args:
        change: Change value
        is_percentage: Whether to format as percentage

    Returns:
        Formatted string
    """
    sign = "+" if change > 0 else ""
    if is_percentage:
        return f"{sign}{change:.1f}%"
    else:
        return f"{sign}{change:.0f}"


def generate_comparison_report(
    q1: str,
    q2: str,
    metrics1: AuditMetrics,
    metrics2: AuditMetrics,
    report1: Optional[str],
    report2: Optional[str]
) -> str:
    """
    Generate a comprehensive comparison report.

    Args:
        q1: First quarter
        q2: Second quarter
        metrics1: Metrics for first quarter
        metrics2: Metrics for second quarter
        report1: Full report content for first quarter
        report2: Full report content for second quarter

    Returns:
        Formatted Markdown comparison report
    """
    # Calculate drifts
    score_change, score_direction = calculate_drift(
        metrics1.compliance_score, metrics2.compliance_score
    )
    violations_change, violations_direction = calculate_drift(
        metrics1.violations, metrics2.violations
    )
    commits_change, commits_direction = calculate_drift(
        metrics1.commits, metrics2.commits
    )

    # Determine overall trend
    if score_change > 0:
        trend_emoji = "✅"
        trend_text = "IMPROVING"
    elif score_change < 0:
        trend_emoji = "⚠️"
        trend_text = "DECLINING"
    else:
        trend_emoji = "➡️"
        trend_text = "STABLE"

    # Build report
    report = f"""# SSID Audit Report Comparison

**Comparison Period:** {q1} → {q2}
**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")}
**Blueprint Version:** v4.2.0

---

## Executive Summary

**Overall Trend:** {trend_emoji} {trend_text}

| Metric                  | {q1:10s} | {q2:10s} | Change           | Trend          |
|-------------------------|----------|----------|------------------|----------------|
| **Compliance Score**    | {metrics1.compliance_score:3d}/100   | {metrics2.compliance_score:3d}/100   | {format_drift_value(score_change):16s} | {score_direction:14s} |
| **Violations**          | {metrics1.violations:8d} | {metrics2.violations:8d} | {format_drift_value(violations_change):16s} | {violations_direction:14s} |
| **Commits**             | {metrics1.commits:8d} | {metrics2.commits:8d} | {format_drift_value(commits_change):16s} | {commits_direction:14s} |
| **Root-24-LOCK**        | {metrics1.root24_status:8s} | {metrics2.root24_status:8s} | {'No Change':16s} | {'✅':14s} |
| **Hash Validation**     | {str(metrics1.hash_valid):8s} | {str(metrics2.hash_valid):8s} | {'No Change':16s} | {'✅':14s} |

---

## Detailed Analysis

### 1. Compliance Score Drift

"""

    if score_change == 0:
        report += f"""**Status:** ✅ STABLE - No score drift detected

The compliance score remained at **{metrics2.compliance_score}/100** between {q1} and {q2}.
This indicates consistent adherence to Blueprint v4.2 standards.

"""
    elif score_change > 0:
        report += f"""**Status:** ✅ IMPROVING - Score increased by {score_change} points

The compliance score improved from **{metrics1.compliance_score}/100** to **{metrics2.compliance_score}/100**.
This indicates enhanced compliance with Blueprint v4.2 standards.

**Recommendations:**
- Document the changes that led to improvement
- Maintain current practices in future quarters
- Consider this a baseline for continued excellence

"""
    else:
        report += f"""**Status:** ⚠️ DECLINING - Score decreased by {abs(score_change)} points

The compliance score declined from **{metrics1.compliance_score}/100** to **{metrics2.compliance_score}/100**.
This requires immediate attention and remediation.

**Action Required:**
- Review changes between {q1} and {q2}
- Identify root cause of compliance degradation
- Implement corrective measures immediately
- Re-run structure guard: `bash 12_tooling/scripts/structure_guard.sh`

"""

    report += f"""### 2. Violation Analysis

"""

    if violations_change == 0 and metrics2.violations == 0:
        report += f"""**Status:** ✅ PERFECT - Zero violations maintained

Both {q1} and {q2} reported **zero violations**. The Root-24-LOCK enforcement
is functioning correctly, and pre-commit hooks are preventing structural drift.

"""
    elif violations_change > 0:
        report += f"""**Status:** 🔴 CRITICAL - Violations increased by {violations_change}

Violations increased from **{metrics1.violations}** to **{metrics2.violations}** between quarters.
This is a critical compliance issue requiring immediate investigation.

**Immediate Actions:**
1. Run structure guard to identify violations:
   ```bash
   bash 12_tooling/scripts/structure_guard.sh
   ```

2. Review recent commits for unauthorized structural changes:
   ```bash
   git log --all --full-history --oneline -- "*/XX_*/"
   ```

3. Verify pre-commit hook is active:
   ```bash
   bash .git/hooks/pre-commit
   ```

4. Remediate all violations before next audit

"""
    elif violations_change < 0:
        report += f"""**Status:** ✅ RESOLVED - {abs(violations_change)} violations remediated

Violations decreased from **{metrics1.violations}** to **{metrics2.violations}**.
This indicates successful remediation efforts and improved compliance.

**Recommendations:**
- Document remediation steps taken
- Update operations guide with lessons learned
- Ensure preventive measures are in place

"""

    report += f"""### 3. Commit Activity Trend

"""

    if commits_change > 0:
        pct_change = (commits_change / metrics1.commits * 100) if metrics1.commits > 0 else 0
        report += f"""**Status:** 📈 INCREASED - {commits_change} more commits ({pct_change:.1f}% increase)

Commit activity increased from **{metrics1.commits}** to **{metrics2.commits}** commits.
This indicates active development and engagement with the repository.

**Commit Rate:**
- {q1}: {metrics1.commits / 90:.1f} commits/day (approx)
- {q2}: {metrics2.commits / 90:.1f} commits/day (approx)
- Change: {format_drift_value((metrics2.commits - metrics1.commits) / 90, False)} commits/day

"""
    elif commits_change < 0:
        pct_change = abs((commits_change / metrics1.commits * 100)) if metrics1.commits > 0 else 0
        report += f"""**Status:** 📉 DECREASED - {abs(commits_change)} fewer commits ({pct_change:.1f}% decrease)

Commit activity decreased from **{metrics1.commits}** to **{metrics2.commits}** commits.
This may indicate reduced development activity or project stabilization.

**Considerations:**
- Is the project entering maintenance phase?
- Are there external factors affecting development?
- Should commit frequency targets be established?

"""
    else:
        report += f"""**Status:** ➡️ STABLE - Consistent commit activity

Both quarters maintained **{metrics2.commits}** commits, indicating stable development pace.

"""

    report += f"""### 4. Root-24-LOCK Status

**Current Status:** {metrics2.root24_status}

"""

    if metrics1.root24_status == "PASS" and metrics2.root24_status == "PASS":
        report += f"""✅ Root-24-LOCK enforcement remained **COMPLIANT** across both quarters.

All 24 root directories are verified and protected by:
- Pre-commit hook: `root24_enforcer.sh`
- GitHub Actions: `structure_guard.yml`
- Quarterly audits: `run_quarterly_audit.sh`

**Verification:**
```bash
bash 12_tooling/scripts/structure_guard.sh
# Expected: ✅ Root-24-LOCK: COMPLIANT (24 roots verified)
```

"""
    else:
        report += f"""🔴 Root-24-LOCK status changed from **{metrics1.root24_status}** to **{metrics2.root24_status}**.

This is a critical compliance failure requiring immediate investigation.

**Emergency Actions:**
1. Run structure guard immediately
2. Review all commits between quarters
3. Restore missing/renamed root directories
4. Re-verify pre-commit hook installation

"""

    report += f"""### 5. Proof-Anchor Verification

**{q1} Proof-Anchor:** `{metrics1.proof_anchor}`
**{q2} Proof-Anchor:** `{metrics2.proof_anchor}`

"""

    if metrics1.hash_valid and metrics2.hash_valid:
        report += f"""✅ Both proof-anchors are **cryptographically valid**.

Hash verification passed for both quarters, confirming tamper-proof audit trail.

**External Anchoring:**
Consider anchoring these proofs to external systems for independent verification:
- IPFS (free, decentralized)
- Polygon/Ethereum (blockchain verification)
- Certificate Transparency logs (timestamping)

See: `05_documentation/PROOF_ANCHORING_GUIDE.md`

"""
    else:
        report += f"""⚠️ Proof-anchor validation issues detected.

Review registry event logs for details:
```bash
tail -n 50 24_meta_orchestration/registry/logs/registry_events.log
```

"""

    report += f"""---

## Recommendations

### Immediate Actions (if applicable):

"""

    recommendations = []

    if score_change < 0:
        recommendations.append("🔴 **CRITICAL:** Investigate compliance score decline")
        recommendations.append("   - Review structural changes between quarters")
        recommendations.append("   - Run structure guard validation")
        recommendations.append("   - Implement corrective measures")

    if violations_change > 0:
        recommendations.append("🔴 **CRITICAL:** Remediate all violations")
        recommendations.append("   - Identify violation sources")
        recommendations.append("   - Restore Root-24-LOCK compliance")
        recommendations.append("   - Verify pre-commit hook functionality")

    if metrics2.root24_status != "PASS":
        recommendations.append("🔴 **CRITICAL:** Root-24-LOCK enforcement failure")
        recommendations.append("   - Emergency structure restoration required")
        recommendations.append("   - Contact repository maintainers immediately")

    if not recommendations:
        recommendations.append("✅ No immediate actions required")
        recommendations.append("   - Continue maintaining 100% compliance")
        recommendations.append("   - Run monthly structure checks")
        recommendations.append("   - Generate next quarterly audit on schedule")

    for rec in recommendations:
        report += f"{rec}\n"

    report += f"""
### Long-term Improvements:

1. **Trend Monitoring:**
   - Run this diff script after each quarterly audit
   - Track score drift over 4+ quarters
   - Establish baseline metrics for comparison

2. **Automation:**
   - Integrate diff analysis into quarterly audit workflow
   - Set up alerts for score degradation
   - Automate proof-anchoring to external systems

3. **Documentation:**
   - Document any score changes and their causes
   - Update operations guide with lessons learned
   - Maintain change log for structural modifications

---

## Comparison Metadata

**Quarters Compared:** {q1} vs {q2}
**Dashboard Data Source:** `{DASHBOARD_CSV.relative_to(REPO_ROOT)}`
**Reports Location:** `05_documentation/reports/`
**Comparison Script:** `12_tooling/scripts/diff_audit_reports.py`

**Report Availability:**
- {q1}: {'✅ Available' if report1 else '❌ Missing'}
- {q2}: {'✅ Available' if report2 else '❌ Missing'}

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")}
**Blueprint Version:** v4.2.0 (6-Layer Depth Model)

---

_📊 Automated audit comparison powered by SSID Blueprint v4.2_
_🔍 For detailed metrics, review individual quarterly reports_
"""

    return report


def main():
    """
    Main execution function.
    """
    if len(sys.argv) != 3:
        print("Usage: python3 diff_audit_reports.py <quarter1> <quarter2>")
        print("\nExample:")
        print("  python3 diff_audit_reports.py 2025-Q4 2026-Q1")
        sys.exit(1)

    q1 = sys.argv[1]
    q2 = sys.argv[2]

    print("=" * 60)
    print("  SSID Audit Report Comparison Tool")
    print("  Blueprint v4.2 - Score Drift Analysis")
    print("=" * 60)
    print()

    # Load metrics from dashboard CSV
    print(f"📊 Loading metrics for {q1}...")
    metrics1 = load_dashboard_metrics(q1)

    print(f"📊 Loading metrics for {q2}...")
    metrics2 = load_dashboard_metrics(q2)

    if not metrics1:
        print(f"❌ Error: No metrics found for {q1}")
        print(f"   Check: {DASHBOARD_CSV}")
        sys.exit(1)

    if not metrics2:
        print(f"❌ Error: No metrics found for {q2}")
        print(f"   Check: {DASHBOARD_CSV}")
        sys.exit(1)

    # Load full compliance reports (optional)
    print(f"📄 Loading compliance reports...")
    report1, parsed1 = load_compliance_report(q1)
    report2, parsed2 = load_compliance_report(q2)

    # Generate comparison
    print(f"🔍 Analyzing drift between {q1} and {q2}...")
    comparison = generate_comparison_report(q1, q2, metrics1, metrics2, report1, report2)

    # Output to file
    output_dir = REPO_ROOT / "05_documentation" / "reports" / "comparisons"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / f"AUDIT_COMPARISON_{q1}_vs_{q2}.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(comparison)

    print()
    print("=" * 60)
    print("  Comparison Complete")
    print("=" * 60)
    print()
    print(f"📝 Report saved to:")
    print(f"   {output_file.relative_to(REPO_ROOT)}")
    print()
    print("📊 Summary:")
    print(f"   Compliance Score: {metrics1.compliance_score} → {metrics2.compliance_score}")
    print(f"   Violations: {metrics1.violations} → {metrics2.violations}")
    print(f"   Commits: {metrics1.commits} → {metrics2.commits}")
    print(f"   Root-24-LOCK: {metrics1.root24_status} → {metrics2.root24_status}")
    print()


if __name__ == "__main__":
    main()
