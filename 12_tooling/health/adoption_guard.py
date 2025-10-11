"""
Health Check Adoption Guard (v4.2)

Enforces template-based health check adoption across all 388 shard health files.
Scans repository for non-compliant health.py files and reports violations.

Enforcement Rules:
1. MUST: Reference template_health (via import or file loader)
2. FORBIDDEN: Hardcoded "up" status (return "up" or {"status": "up"})

Usage:
    python 12_tooling/health/adoption_guard.py

Exit Codes:
    0 - All health files compliant
    1 - Violations found (CI should fail)

Output:
    JSON report with files_scanned and violations
"""

import os
import re
import json
import sys
import fnmatch
from typing import List, Dict, Any

# Template indicators that must be present
TEMPLATE_HINTS = [
    "template_health",  # Import by module name
    "12_tooling/health/template_health.py",  # Import by path
    "12_tooling/health/template_health",  # Partial path
]

# Forbidden patterns that indicate hardcoded "up" status
FORBIDDEN_PATTERNS = [
    re.compile(r"""['"]status['"]\s*:\s*['"]up['"]"""),  # {"status": "up"}
    re.compile(r"""\breturn\s+['"]up['"]"""),  # return "up"
    re.compile(r"""\breturn\s+\{\s*['"]status['"]\s*:\s*['"]up['"]"""),  # return {"status": "up"}
]


def _all_files(root: str, pattern: str) -> List[str]:
    """
    Recursively find all files matching pattern.

    Args:
        root: Directory to search
        pattern: Glob pattern (e.g., "*/shards/*/health.py")

    Returns:
        List of matching file paths
    """
    out = []
    for dirpath, _, files in os.walk(root):
        for f in files:
            p = os.path.join(dirpath, f)
            # Normalize path separators for glob matching
            normalized = p.replace('\\', '/')
            if fnmatch.fnmatch(normalized, pattern):
                out.append(p)
    return out


def scan_repo_for_adoption(root: str = ".") -> Dict[str, Any]:
    """
    Scan all shard health.py files and enforce template import usage.

    Args:
        root: Repository root directory

    Returns:
        {
            "files_scanned": int,
            "violations": [
                {
                    "file": "path/to/health.py",
                    "error": "missing-template-import" | "hardcoded-up-status" | "read-failed: ..."
                }
            ]
        }
    """
    # Pattern: */shards/*/health.py at any depth
    pattern = "*/shards/*/health.py"
    matches = _all_files(root, pattern)

    violations = []

    for path in matches:
        try:
            with open(path, "r", encoding="utf-8") as f:
                src = f.read()
        except Exception as e:
            violations.append({
                "file": path,
                "error": f"read-failed: {e}"
            })
            continue

        # Rule 1: Must reference template (by module name or file path loading)
        has_template_ref = any(hint in src for hint in TEMPLATE_HINTS)
        if not has_template_ref:
            violations.append({
                "file": path,
                "error": "missing-template-import"
            })
            continue

        # Rule 2: Must not hardcode 'up' status
        for rx in FORBIDDEN_PATTERNS:
            if rx.search(src):
                violations.append({
                    "file": path,
                    "error": "hardcoded-up-status"
                })
                break

    return {
        "files_scanned": len(matches),
        "violations": violations
    }


def main():
    """
    Main entry point for adoption guard CLI.

    Scans repository and exits with code 1 if violations found.
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="Health Check Adoption Guard - Enforce template usage"
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Repository root directory (default: current directory)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON only (no human-readable text)"
    )

    args = parser.parse_args()

    res = scan_repo_for_adoption(args.root)

    if args.json:
        # JSON-only output for CI parsing
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        # Human-readable output
        print("=" * 70)
        print("Health Check Adoption Guard Report")
        print("=" * 70)
        print(f"Files scanned: {res['files_scanned']}")
        print(f"Violations: {len(res['violations'])}")
        print()

        if res["violations"]:
            print("VIOLATIONS FOUND:")
            print("-" * 70)
            for v in res["violations"]:
                print(f"  File: {v['file']}")
                print(f"  Error: {v['error']}")
                print()
            print("=" * 70)
            print("STATUS: FAIL - Fix violations before merge")
            print("=" * 70)
        else:
            print("=" * 70)
            print("STATUS: PASS - All health files compliant")
            print("=" * 70)

    # Exit with error code if violations found
    sys.exit(1 if res["violations"] else 0)


if __name__ == "__main__":
    main()
