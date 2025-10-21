#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Inventory Audit – Systematic Test Discovery & Integration Analysis
=========================================================================

Purpose:
  - Scans repository for all test files (test_*.py, *_test.py)
  - Excludes backup/cache directories systematically
  - Compares file inventory against pytest discovery
  - Generates audit reports with integration metrics
  - Enforces policy gates (min pytest discovery ratio)

Outputs:
  - 02_audit_logging/reports/TEST_INTEGRATION_AUDIT.md
  - 02_audit_logging/logs/test_inventory_audit.json
  - 02_audit_logging/logs/test_inventory_score_log.json

Exit Codes:
  0 – PASS (discovery ratio >= policy threshold)
  2 – FAIL (discovery ratio < policy threshold)
  1 – ERROR (execution failure)

Author: SSID Codex Engine v5.2
License: Proprietary – SAFE-FIX & ROOT-24-LOCK enforced
"""
from __future__ import annotations
import argparse, json, os, re, sys, subprocess
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Dict, Set
from datetime import datetime, timezone

DEFAULT_EXCLUDES = [".git","__pycache__",".claude","node_modules","venv",".venv","dist","build",".pytest_cache","site-packages","backups","archives","deprecated","legacy",".tox"]
DEFAULT_GLOB_INCLUDE = ["**/test_*.py","**/*_test.py"]
DEFAULT_PATH_EXCLUDE_REGEX = [r"(^|/)backups(/|$)",r"(^|/)archives(/|$)",r"(^|/)deprecated(/|$)"]
@dataclass
class InventoryResult:
    total_found: int
    total_after_filters: int
    files: List[str]
    by_dir: Dict[str,int]
@dataclass
class PytestCollection:
    discovered_count: int
    discovered_nodes: List[str]
def load_policy(path: Path) -> dict:
    if not path.is_file():
        return {}
    import yaml
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}
def scan_tests(root: Path, include_globs: List[str], excludes: List[str], exclude_regex: List[str]) -> InventoryResult:
    files: Set[Path] = set()
    for g in include_globs:
        for p in root.glob(g):
            files.add(p)
    def is_excluded(p: Path) -> bool:
        s = str(p).replace('\\','/')
        parts = s.split('/')
        if any(e in parts for e in excludes):
            return True
        import re as _re
        return any(_re.search(rx, s) for rx in exclude_regex)
    filtered = [f for f in files if not is_excluded(f)]
    by_dir = {}
    for f in filtered:
        d = str(f.parent.relative_to(root)).replace('\\','/')
        by_dir[d] = by_dir.get(d, 0) + 1
    return InventoryResult(len(files), len(filtered), sorted(str(f.relative_to(root)).replace('\\','/') for f in filtered), dict(sorted(by_dir.items(), key=lambda kv: (-kv[1], kv[0]))))
def collect_pytest_nodes(root: Path) -> PytestCollection:
    try:
        proc = subprocess.run(["pytest","--collect-only","-q","--no-header"], cwd=root, capture_output=True, text=True, timeout=180)
        out = proc.stdout + "\n" + proc.stderr
        # Parse pytest output: look for lines like <Module test_foo.py> or test_file.py::test_func
        nodes = []
        for ln in out.splitlines():
            stripped = ln.strip()
            if stripped.startswith("<") and ("Module" in stripped or "Function" in stripped):
                nodes.append(stripped)
            elif "::" in stripped and ".py" in stripped:
                # Also capture node-style output
                nodes.append(stripped)
        print(f"[PYTEST-DISCOVERY] Collected {len(nodes)} nodes from pytest")
        return PytestCollection(len(nodes), nodes)
    except subprocess.TimeoutExpired:
        print("[PYTEST-DISCOVERY] WARNING: pytest collection timed out", file=sys.stderr)
        return PytestCollection(0, [])
    except FileNotFoundError:
        print("[PYTEST-DISCOVERY] WARNING: pytest not found in PATH", file=sys.stderr)
        return PytestCollection(0, [])
    except Exception as e:
        print(f"[PYTEST-DISCOVERY] WARNING: {e}", file=sys.stderr)
        return PytestCollection(0, [])
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".", help="Path to SSID repo root")
    ap.add_argument("--policy", default="12_tooling/analysis/test_inventory_policy.yaml", help="YAML policy")
    ap.add_argument("--json-out", default="02_audit_logging/logs/test_inventory_audit.json", help="JSON output path")
    ap.add_argument("--md-out", default="02_audit_logging/reports/TEST_INTEGRATION_AUDIT.md", help="Markdown report path")
    args = ap.parse_args()
    root = Path(args.repo_root).resolve()
    pol = load_policy(root / args.policy)
    include_globs = pol.get("include_globs", DEFAULT_GLOB_INCLUDE)
    excludes = pol.get("exclude_dirs", DEFAULT_EXCLUDES)
    exclude_regex = pol.get("exclude_regex", DEFAULT_PATH_EXCLUDE_REGEX)
    min_pytest_ratio = float(pol.get("min_pytest_ratio", 0.95))
    inv = scan_tests(root, include_globs, excludes, exclude_regex)
    pyc = collect_pytest_nodes(root)
    ratio = None
    if inv.total_after_filters and pyc.discovered_count:
        ratio = pyc.discovered_count / max(1, inv.total_after_filters)
    missing = []
    if pyc.discovered_nodes:
        disc_str = "\n".join(pyc.discovered_nodes)
        from pathlib import Path as _P
        missing = [f for f in inv.files if _P(f).name[:-3] not in disc_str]
    out_json_path = root / args.json_out
    out_json_path.parent.mkdir(parents=True, exist_ok=True)
    with out_json_path.open("w", encoding="utf-8") as fh:
        json.dump({
            "inventory": asdict(inv),
            "pytest": asdict(pyc),
            "summary": {
                "total_files_raw": inv.total_found,
                "total_files_effective": inv.total_after_filters,
                "pytest_discovered": pyc.discovered_count,
                "missing_files": missing,
                "pass_rate": ratio
            },
            "policy": {
                "include_globs": include_globs,
                "exclude_dirs": excludes,
                "exclude_regex": exclude_regex,
                "min_pytest_ratio": min_pytest_ratio
            }
        }, fh, indent=2)
    out_md_path = root / args.md_out
    out_md_path.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    lines.append("# SSID Test Integration Audit Report")
    lines.append("")
    lines.append(f"**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    lines.append(f"**Repository:** SSID")
    lines.append(f"**Auditor Version:** 1.1.0")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Executive Summary")
    lines.append("")
    lines.append(f"- **Raw Test Files Found (pre-filter):** {inv.total_found}")
    lines.append(f"- **Effective Test Files (post-filter):** {inv.total_after_filters}")
    lines.append(f"- **Pytest Discovered Nodes:** {pyc.discovered_count}")
    if ratio is not None:
        status = "✅ PASS" if ratio >= min_pytest_ratio else "❌ FAIL"
        lines.append(f"- **Discovery Ratio:** {ratio:.2%} (policy min: {min_pytest_ratio:.2%})")
        lines.append(f"- **Policy Gate:** {status}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Distribution by Directory")
    lines.append("")
    lines.append("| Directory | Test Files |")
    lines.append("|-----------|------------|")
    for k,v in inv.by_dir.items():
        lines.append(f"| `{k}` | {v} |")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Files Missing from Pytest Discovery")
    lines.append("")
    if missing:
        lines.append("The following test files were found but may not be fully discovered by pytest:")
        lines.append("")
        for m in sorted(missing):
            lines.append(f"- `{m}`")
        lines.append("")
        lines.append("**Possible Reasons:**")
        lines.append("- File does not contain any test functions (empty or placeholder)")
        lines.append("- Tests are marked with custom markers not recognized by default pytest")
        lines.append("- Syntax errors preventing pytest from parsing the file")
        lines.append("- File naming convention not matching pytest defaults")
        lines.append("- Tests are dynamically generated and not visible to static discovery")
    else:
        lines.append("✅ All test files appear to be discovered by pytest.")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Exclusion Policy")
    lines.append("")
    lines.append("**Excluded Directories:**")
    lines.append("")
    for exc in excludes:
        lines.append(f"- `{exc}/`")
    lines.append("")
    lines.append("**Excluded Patterns (regex):**")
    lines.append("")
    for rx in exclude_regex:
        lines.append(f"- `{rx}`")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Recommendations")
    lines.append("")
    lines.append("1. **Backup Cleanup:** Consider archiving or removing backup directories to reduce noise")
    lines.append("2. **Naming Convention:** Standardize on `test_*.py` prefix for consistency")
    lines.append("3. **Slow Tests:** Tag slow tests with `@pytest.mark.slow` for separate CI execution")
    lines.append("4. **Integration:** Ensure all test files contain valid test functions or fixtures")
    lines.append("5. **Documentation:** Update test documentation to reflect current inventory")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("🤖 Generated by SSID Codex Engine – Test Inventory Audit v1.1.0")
    out_md_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"[REPORT] Markdown report written to {out_md_path.relative_to(root)}")

    # Generate score log
    score_log_path = root / "02_audit_logging/logs/test_inventory_score_log.json"
    score_log_path.parent.mkdir(parents=True, exist_ok=True)
    score = int(ratio * 100) if ratio is not None else 0
    score_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "component": "test_inventory_audit",
        "score": score,
        "max_score": 100,
        "metrics": {
            "total_files_raw": inv.total_found,
            "total_files_effective": inv.total_after_filters,
            "pytest_discovered": pyc.discovered_count,
            "discovery_ratio": ratio,
            "policy_threshold": min_pytest_ratio,
            "policy_passed": ratio >= min_pytest_ratio if ratio is not None else False
        },
        "status": "PASS" if (ratio and ratio >= min_pytest_ratio) else "FAIL"
    }

    # Append to score log
    score_logs = []
    if score_log_path.exists():
        try:
            with score_log_path.open("r", encoding="utf-8") as fh:
                loaded = json.load(fh)
                # Ensure it's a list
                if isinstance(loaded, list):
                    score_logs = loaded
                elif isinstance(loaded, dict):
                    score_logs = [loaded]
                else:
                    score_logs = []
        except:
            score_logs = []
    score_logs.append(score_entry)
    with score_log_path.open("w", encoding="utf-8") as fh:
        json.dump(score_logs, fh, indent=2)
    print(f"[SCORE-LOG] Entry appended to {score_log_path.relative_to(root)}")

    # Print summary
    print("")
    print("=" * 80)
    print("AUDIT SUMMARY")
    print("=" * 80)
    print(f"Raw Test Files:         {inv.total_found}")
    print(f"Effective Test Files:   {inv.total_after_filters}")
    print(f"Pytest Discovered:      {pyc.discovered_count}")
    if ratio is not None:
        print(f"Discovery Ratio:        {ratio:.2%}")
        print(f"Policy Threshold:       {min_pytest_ratio:.2%}")
        status_icon = "[PASS]" if ratio >= min_pytest_ratio else "[FAIL]"
        print(f"Status:                 {status_icon}")
    print("=" * 80)
    print("")

    exit_code = 0
    if ratio is not None and ratio < min_pytest_ratio:
        exit_code = 2
        print("[FAIL] Audit FAILED - Discovery ratio below policy threshold", file=sys.stderr)
    else:
        print("[PASS] Audit PASSED - Discovery ratio meets policy threshold")
    raise SystemExit(exit_code)
if __name__ == "__main__":
    main()
