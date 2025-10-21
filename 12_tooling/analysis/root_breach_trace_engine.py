#!/usr/bin/env python3
"""
ROOT BREACH TRACE ENGINE
Forensic tool to identify who/what/when created ROOT-24-LOCK violations

Author: SSID Compliance System
License: MIT
"""

import json
import subprocess
import sys
import pathlib
import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Fix Windows console encoding
if sys.platform == 'win32':
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
    if sys.stderr.encoding != 'utf-8':
        sys.stderr.reconfigure(encoding='utf-8')

REPORT_DIR = Path("02_audit_logging/reports")
SCAN_REPORT = REPORT_DIR / "root_immunity_scan.json"
OUT_REPORT = REPORT_DIR / "root_breach_trace_report.json"


def git_last_change(file_path: str) -> Dict:
    """
    Get last git change information for a file
    Returns: dict with commit, author, email, date
    """
    try:
        result = subprocess.run(
            ["git", "log", "-n", "1", "--pretty=format:%H|%an|%ae|%ad|%s", "--", file_path],
            capture_output=True,
            text=True,
            check=True,
            encoding='utf-8',
            errors='replace'
        )

        if not result.stdout.strip():
            # File not in git history (new/untracked)
            return {
                "commit": None,
                "author": "UNTRACKED",
                "email": None,
                "date": None,
                "message": "File not in git history"
            }

        parts = result.stdout.strip().split("|", 4)
        if len(parts) >= 4:
            commit_hash, author_name, author_email, author_date = parts[:4]
            commit_message = parts[4] if len(parts) > 4 else ""
            return {
                "commit": commit_hash,
                "author": author_name,
                "email": author_email,
                "date": author_date,
                "message": commit_message
            }
        else:
            return {
                "commit": None,
                "author": "UNKNOWN",
                "email": None,
                "date": None,
                "message": "Parse error"
            }

    except subprocess.CalledProcessError as e:
        return {
            "commit": None,
            "author": "ERROR",
            "email": None,
            "date": None,
            "message": f"Git error: {e}"
        }
    except Exception as e:
        return {
            "commit": None,
            "author": "ERROR",
            "email": None,
            "date": None,
            "message": f"Exception: {e}"
        }


def classify_offender(path: str, reason: str) -> str:
    """
    Classify the type of violation
    Returns: classification string
    """
    path_lower = path.lower()

    if "test" in path_lower or "pytest" in path_lower:
        return "TEST_ARTIFACT"
    elif path.endswith(".md"):
        return "DOCUMENTATION"
    elif path.endswith(".zip"):
        return "ARCHIVE"
    elif path.endswith(".log"):
        return "LOG_FILE"
    elif ".claude" in path_lower:
        return "CLAUDE_MISPLACED"
    elif path.startswith("."):
        return "HIDDEN_FILE"
    else:
        return "UNKNOWN"


def analyze_violations(violations: List[Dict]) -> Dict:
    """
    Analyze violations and generate statistics
    """
    offenders = []
    by_author = {}
    by_type = {}

    for v in violations:
        path = v["path"]
        reason = v.get("reason", "")

        # Get git metadata
        meta = git_last_change(path)

        # Classify violation
        classification = classify_offender(path, reason)

        offender = {
            "path": path,
            "reason": reason,
            "classification": classification,
            **meta
        }

        offenders.append(offender)

        # Track by author
        author = meta.get("author", "UNKNOWN")
        if author not in by_author:
            by_author[author] = []
        by_author[author].append(path)

        # Track by type
        if classification not in by_type:
            by_type[classification] = []
        by_type[classification].append(path)

    # Sort authors by violation count
    author_stats = [
        {"author": author, "count": len(paths), "files": paths}
        for author, paths in sorted(by_author.items(), key=lambda x: len(x[1]), reverse=True)
    ]

    # Sort types by count
    type_stats = [
        {"type": type_name, "count": len(paths), "files": paths}
        for type_name, paths in sorted(by_type.items(), key=lambda x: len(x[1]), reverse=True)
    ]

    return {
        "offenders": offenders,
        "by_author": author_stats,
        "by_type": type_stats,
        "total_violations": len(violations)
    }


def main():
    """Main entry point"""
    print("=" * 80)
    print("ROOT BREACH TRACE ENGINE")
    print("=" * 80)
    print()

    # Check if scan report exists
    if not SCAN_REPORT.exists():
        print(f"❌ No scan report found: {SCAN_REPORT}")
        print("   Run: python 23_compliance/guards/root_immunity_daemon.py --check --report")
        sys.exit(1)

    # Load scan report
    try:
        with open(SCAN_REPORT, 'r', encoding='utf-8') as f:
            scan_data = json.load(f)
    except Exception as e:
        print(f"❌ Failed to load scan report: {e}")
        sys.exit(1)

    violations = scan_data.get("violations", [])

    if not violations:
        print("✅ No violations found - system is compliant!")
        print()

        # Still write empty report
        report = {
            "generated_at": datetime.datetime.utcnow().isoformat() + "Z",
            "scan_report": str(SCAN_REPORT),
            "violations_found": 0,
            "status": "COMPLIANT",
            "offenders": [],
            "by_author": [],
            "by_type": []
        }

        with open(OUT_REPORT, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"✅ Report written: {OUT_REPORT}")
        sys.exit(0)

    # Analyze violations
    print(f"🔍 Analyzing {len(violations)} violations...")
    print()

    analysis = analyze_violations(violations)

    # Print summary
    print("=" * 80)
    print("VIOLATION SUMMARY")
    print("=" * 80)
    print()

    print(f"Total Violations: {analysis['total_violations']}")
    print()

    print("By Author:")
    for stat in analysis['by_author']:
        print(f"  {stat['author']}: {stat['count']} files")
    print()

    print("By Type:")
    for stat in analysis['by_type']:
        print(f"  {stat['type']}: {stat['count']} files")
    print()

    # Generate full report
    report = {
        "generated_at": datetime.datetime.utcnow().isoformat() + "Z",
        "scan_report": str(SCAN_REPORT),
        "violations_found": len(violations),
        "status": "NON_COMPLIANT",
        "offenders": analysis["offenders"],
        "by_author": analysis["by_author"],
        "by_type": analysis["by_type"]
    }

    # Write report
    with open(OUT_REPORT, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print("=" * 80)
    print(f"✅ Report written: {OUT_REPORT}")
    print("=" * 80)
    print()

    # Print actionable recommendations
    print("RECOMMENDATIONS:")
    print()

    for stat in analysis['by_type']:
        type_name = stat['type']
        count = stat['count']

        if type_name == "TEST_ARTIFACT":
            print(f"  [{count}] TEST_ARTIFACT: Add to .gitignore or move to test directories")
        elif type_name == "DOCUMENTATION":
            print(f"  [{count}] DOCUMENTATION: Move to 24_meta_orchestration/docs/ or appropriate root")
        elif type_name == "ARCHIVE":
            print(f"  [{count}] ARCHIVE: Move to 24_meta_orchestration/artifacts/")
        elif type_name == "LOG_FILE":
            print(f"  [{count}] LOG_FILE: Add to .gitignore")
        elif type_name == "CLAUDE_MISPLACED":
            print(f"  [{count}] CLAUDE_MISPLACED: .claude/ only allowed in 16_codex and 20_foundation")
        elif type_name == "HIDDEN_FILE":
            print(f"  [{count}] HIDDEN_FILE: Review and add to exception policy if legitimate")

    print()

    sys.exit(1)  # Exit with error code since violations exist


if __name__ == "__main__":
    main()
