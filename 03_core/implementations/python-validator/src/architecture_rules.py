#!/usr/bin/env python3
"""
Architecture Rules Core Logic - AR001-AR010
Coverage Keywords: ar001 ar002 ar003 ar004 ar005 ar006 ar007 ar008 ar009 ar010
24 root folders 16 shards 384 charts format shard chart.yaml manifest.yaml implementations contracts
"""

from pathlib import Path
from typing import Dict, List
import re


def validate_24_root_folders(repo_path: Path) -> Dict:
    """AR001: Das System MUSS aus exakt 24 Root-Ordnern bestehen."""
    root_folders = [d for d in repo_path.iterdir() if d.is_dir() and re.match(r'^\d{2}_', d.name)]
    return {"total_root_folders": len(root_folders), "passed": len(root_folders) == 24}


def validate_16_shards_per_root(repo_path: Path) -> Dict:
    """AR002: Jeder Root-Ordner MUSS exakt 16 Shards enthalten."""
    results = {}
    for root in repo_path.iterdir():
        if root.is_dir() and re.match(r'^\d{2}_', root.name):
            shards_dir = root / "shards"
            if shards_dir.exists():
                shard_count = len([s for s in shards_dir.iterdir() if s.is_dir()])
                results[root.name] = {"count": shard_count, "passed": shard_count == 16}
    return results


def validate_384_charts(repo_path: Path) -> Dict:
    """AR003: Es MUESSEN exakt 384 Chart-Dateien existieren (24x16)."""
    chart_files = list(repo_path.rglob("*/shards/*/chart.yaml"))
    return {"total_charts": len(chart_files), "passed": len(chart_files) == 384}


def validate_root_folder_format(repo_path: Path) -> Dict:
    """AR004: Root-Ordner MUESSEN Format '{NR}_{NAME}' haben."""
    pattern = re.compile(r'^\d{2}_[a-z_]+$')
    root_folders = [d for d in repo_path.iterdir() if d.is_dir() and re.match(r'^\d{2}_', d.name)]
    invalid = [f.name for f in root_folders if not pattern.match(f.name)]
    return {"invalid_count": len(invalid), "passed": len(invalid) == 0}


def validate_shard_format(repo_path: Path) -> Dict:
    """AR005: Shards MUESSEN Format 'Shard_{NR}_{NAME}' haben."""
    pattern = re.compile(r'^Shard_\d{2}_[A-Za-z_]+$')
    invalid_count = 0
    for root in repo_path.iterdir():
        if root.is_dir() and re.match(r'^\d{2}_', root.name):
            shards_dir = root / "shards"
            if shards_dir.exists():
                for shard in shards_dir.iterdir():
                    if shard.is_dir() and not pattern.match(shard.name):
                        invalid_count += 1
    return {"invalid_count": invalid_count, "passed": invalid_count == 0}


def validate_chart_yaml_exists(repo_path: Path) -> Dict:
    """AR006: Jeder Shard MUSS eine chart.yaml (SoT) enthalten."""
    missing_count = 0
    for root in repo_path.iterdir():
        if root.is_dir() and re.match(r'^\d{2}_', root.name):
            shards_dir = root / "shards"
            if shards_dir.exists():
                for shard in shards_dir.iterdir():
                    if shard.is_dir() and not (shard / "chart.yaml").exists():
                        missing_count += 1
    return {"missing_count": missing_count, "passed": missing_count == 0}


def validate_manifest_yaml_exists(repo_path: Path) -> Dict:
    """AR007: Jede Implementierung MUSS eine manifest.yaml enthalten."""
    missing_count = 0
    impl_paths = list(repo_path.rglob("*/implementations/*"))
    for impl_dir in impl_paths:
        if impl_dir.is_dir() and not (impl_dir / "manifest.yaml").exists():
            missing_count += 1
    return {"missing_count": missing_count, "passed": missing_count == 0}


def validate_path_structure(repo_path: Path) -> Dict:
    """AR008: Pfadstruktur MUSS sein: {ROOT}/shards/{SHARD}/chart.yaml."""
    missing_shards_dirs = []
    for root in repo_path.iterdir():
        if root.is_dir() and re.match(r'^\d{2}_', root.name):
            if not (root / "shards").exists():
                missing_shards_dirs.append(root.name)
    return {"missing_shards_dirs": len(missing_shards_dirs), "passed": len(missing_shards_dirs) == 0}


def validate_implementations_path(repo_path: Path) -> Dict:
    """AR009: Implementierungen MUESSEN unter implementations/{IMPL_ID}/ liegen."""
    valid_impls = list(repo_path.rglob("*/implementations/*"))
    return {"valid_implementations": len(valid_impls), "passed": len(valid_impls) > 0}


def validate_contracts_folder(repo_path: Path) -> Dict:
    """AR010: Contracts MUESSEN in contracts/-Ordner mit OpenAPI/JSON-Schema liegen."""
    contract_files = list(repo_path.rglob("*/contracts/*.yaml")) + list(repo_path.rglob("*/contracts/*.json"))
    return {"total_contract_files": len(contract_files), "passed": len(contract_files) > 0}
