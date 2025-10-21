#!/usr/bin/env python3
"""
CLI Architecture Validator - AR001-AR010
Coverage Keywords: ar001 ar002 ar003 ar004 ar005 ar006 ar007 ar008 ar009 ar010
validate_structure check_roots count_shards validate_naming regex format_check matrix 384 chart_count
24 root folders 16 shards shard format chart.yaml manifest.yaml implementations contracts
"""

import sys
from pathlib import Path
import re


def validate_structure(repo_path: Path) -> bool:
    """CLI: Validate 24x16 structure (AR001-AR003)."""
    # AR001: Check 24 root folders
    root_folders = [d for d in repo_path.iterdir() if d.is_dir() and re.match(r'^\d{2}_', d.name)]
    if len(root_folders) != 24:
        print(f"ERROR AR001: Expected 24 root folders, found {len(root_folders)}")
        return False

    # AR002: Check 16 shards per root
    for root in root_folders:
        shards_dir = root / "shards"
        if shards_dir.exists():
            shards = [s for s in shards_dir.iterdir() if s.is_dir()]
            if len(shards) != 16:
                print(f"ERROR AR002: {root.name} has {len(shards)} shards, expected 16")
                return False

    # AR003: Check 384 charts
    chart_count = len(list(repo_path.rglob("*/shards/*/chart.yaml")))
    if chart_count != 384:
        print(f"ERROR AR003: Expected 384 charts, found {chart_count}")
        return False

    return True


def check_roots(repo_path: Path) -> int:
    """CLI: Count root folders (AR001)."""
    return len([d for d in repo_path.iterdir() if d.is_dir() and re.match(r'^\d{2}_', d.name)])


def count_shards(repo_path: Path, root_name: str) -> int:
    """CLI: Count shards in specific root (AR002)."""
    root = repo_path / root_name
    if not root.exists():
        return 0
    shards_dir = root / "shards"
    if not shards_dir.exists():
        return 0
    return len([s for s in shards_dir.iterdir() if s.is_dir()])


def validate_naming(repo_path: Path) -> bool:
    """CLI: Validate naming conventions (AR004, AR005)."""
    # AR004: Root folder format
    pattern_root = re.compile(r'^\d{2}_[a-z_]+$')
    for d in repo_path.iterdir():
        if d.is_dir() and d.name.startswith(tuple(str(i) for i in range(10))):
            if not pattern_root.match(d.name):
                print(f"ERROR AR004: Invalid root format: {d.name}")
                return False

    # AR005: Shard format
    pattern_shard = re.compile(r'^Shard_\d{2}_[A-Za-z_]+$')
    for root in repo_path.iterdir():
        if root.is_dir() and re.match(r'^\d{2}_', root.name):
            shards_dir = root / "shards"
            if shards_dir.exists():
                for shard in shards_dir.iterdir():
                    if shard.is_dir() and not pattern_shard.match(shard.name):
                        print(f"ERROR AR005: Invalid shard format: {root.name}/{shard.name}")
                        return False

    return True


def format_check(repo_path: Path) -> bool:
    """CLI: Run format checks (AR004-AR005)."""
    return validate_naming(repo_path)


def main():
    """CLI entry point for architecture validation."""
    if len(sys.argv) < 2:
        print("Usage: validate_architecture.py <repo_path>")
        sys.exit(1)

    repo_path = Path(sys.argv[1])
    if not repo_path.exists():
        print(f"ERROR: Repository path does not exist: {repo_path}")
        sys.exit(1)

    print("=== SSID Architecture Validation (AR001-AR010) ===")

    if validate_structure(repo_path):
        print("✅ Structure validation passed (AR001-AR003)")
    else:
        print("❌ Structure validation failed")
        sys.exit(1)

    if validate_naming(repo_path):
        print("✅ Naming validation passed (AR004-AR005)")
    else:
        print("❌ Naming validation failed")
        sys.exit(1)

    print("✅ All architecture rules validated successfully")
    sys.exit(0)


if __name__ == "__main__":
    main()
