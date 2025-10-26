#!/usr/bin/env python3
"""
SSID Shard Consolidation Tool
==============================

Consolidates duplicate files and orphaned content into the proper shard structure.

Version: 1.0.0
Author: SSID System
Date: 2025-10-24
"""

import os
import sys
import shutil
import hashlib
from pathlib import Path
from typing import Dict, List, Set, Tuple
from datetime import datetime
import json

REPO_ROOT = Path(__file__).parent.parent.parent

# 24 Root Layers
ROOT_LAYERS = [
    "01_ai_layer", "02_audit_logging", "03_core", "04_deployment",
    "05_documentation", "06_data_pipeline", "07_governance_legal",
    "08_identity_score", "09_meta_identity", "10_interoperability",
    "11_test_simulation", "12_tooling", "13_ui_layer", "14_zero_time_auth",
    "15_infra", "16_codex", "17_observability", "18_data_layer",
    "19_adapters", "20_foundation", "21_post_quantum_crypto", "22_datasets",
    "23_compliance", "24_meta_orchestration"
]

# 16 Shards
SHARD_IDS = [
    "01_identitaet_personen", "02_dokumente_nachweise", "03_zugang_berechtigungen",
    "04_kommunikation_daten", "05_gesundheit_medizin", "06_bildung_qualifikationen",
    "07_familie_soziales", "08_mobilitaet_fahrzeuge", "09_arbeit_karriere",
    "10_finanzen_banking", "11_versicherungen_risiken", "12_immobilien_grundstuecke",
    "13_unternehmen_gewerbe", "14_vertraege_vereinbarungen", "15_handel_transaktionen",
    "16_behoerden_verwaltung"
]

# Shard keywords for automatic classification
SHARD_KEYWORDS = {
    "01_identitaet_personen": ["identity", "identit", "person", "did", "profile", "auth"],
    "02_dokumente_nachweise": ["document", "dokument", "certificate", "zertifikat", "proof", "nachweis"],
    "03_zugang_berechtigungen": ["access", "zugang", "permission", "berechtigung", "role", "rolle"],
    "04_kommunikation_daten": ["communication", "kommunikation", "message", "nachricht", "data", "daten"],
    "05_gesundheit_medizin": ["health", "gesundheit", "medical", "medizin", "patient"],
    "06_bildung_qualifikationen": ["education", "bildung", "qualification", "qualifikation", "certificate"],
    "07_familie_soziales": ["family", "familie", "social", "sozial", "marriage", "birth"],
    "08_mobilitaet_fahrzeuge": ["mobility", "mobilit", "vehicle", "fahrzeug", "transport", "license"],
    "09_arbeit_karriere": ["work", "arbeit", "career", "karriere", "employment", "job"],
    "10_finanzen_banking": ["finance", "finanz", "banking", "payment", "zahlung", "account"],
    "11_versicherungen_risiken": ["insurance", "versicherung", "risk", "risiko", "policy", "claim"],
    "12_immobilien_grundstuecke": ["real_estate", "immobilie", "property", "grundst", "land"],
    "13_unternehmen_gewerbe": ["company", "unternehmen", "business", "gewerbe", "commercial"],
    "14_vertraege_vereinbarungen": ["contract", "vertrag", "agreement", "vereinbarung", "terms"],
    "15_handel_transaktionen": ["trade", "handel", "transaction", "transaktion", "purchase", "sale"],
    "16_behoerden_verwaltung": ["authority", "beh", "administration", "verwaltung", "government"]
}


def compute_file_hash(file_path: Path) -> str:
    """Compute SHA256 hash of file"""
    try:
        with open(file_path, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()
    except Exception:
        return ""


def classify_file_to_shard(file_path: Path) -> str:
    """
    Classify a file to a shard based on:
    1. File path
    2. File name
    3. File content (keywords)
    """

    # Check file path for shard hints
    path_str = str(file_path).lower()

    # Score each shard
    scores = {shard: 0 for shard in SHARD_IDS}

    for shard_id, keywords in SHARD_KEYWORDS.items():
        for keyword in keywords:
            if keyword in path_str:
                scores[shard_id] += 2

    # Check file content (first 1000 chars)
    try:
        if file_path.suffix in ['.py', '.md', '.txt', '.yaml', '.json']:
            content = file_path.read_text(encoding='utf-8', errors='ignore')[:1000].lower()

            for shard_id, keywords in SHARD_KEYWORDS.items():
                for keyword in keywords:
                    if keyword in content:
                        scores[shard_id] += 1
    except Exception:
        pass

    # Get shard with highest score
    best_shard = max(scores.items(), key=lambda x: x[1])

    # If no clear winner, use a default
    if best_shard[1] == 0:
        return "01_identitaet_personen"  # Default shard

    return best_shard[0]


def find_duplicates() -> Dict[str, List[Path]]:
    """Find duplicate files across all layers/shards"""

    print("\n[SCAN] Finding duplicate files...")

    file_hashes: Dict[str, List[Path]] = {}

    for layer in ROOT_LAYERS:
        layer_path = REPO_ROOT / layer

        if not layer_path.exists():
            continue

        for file_path in layer_path.rglob("*"):
            if file_path.is_file() and file_path.suffix in ['.py', '.yaml', '.json', '.md', '.txt']:
                # Skip some directories
                if any(skip in file_path.parts for skip in ['.git', '__pycache__', 'node_modules', '.venv']):
                    continue

                file_hash = compute_file_hash(file_path)
                if file_hash:
                    if file_hash not in file_hashes:
                        file_hashes[file_hash] = []
                    file_hashes[file_hash].append(file_path)

    # Filter to only duplicates
    duplicates = {h: files for h, files in file_hashes.items() if len(files) > 1}

    print(f"  [FOUND] {len(duplicates)} sets of duplicate files")

    return duplicates


def find_orphaned_files() -> List[Path]:
    """Find files outside shard structure"""

    print("\n[SCAN] Finding orphaned files...")

    orphaned = []

    allowed_root_files = {
        "README.md", "CHANGELOG.md", "LICENSE", ".gitignore",
        "requirements.txt", "setup.py", "pyproject.toml",
        "Dockerfile", "docker-compose.yml", ".dockerignore",
        "__init__.py"
    }

    for layer in ROOT_LAYERS:
        layer_path = REPO_ROOT / layer

        if not layer_path.exists():
            continue

        for file_path in layer_path.rglob("*"):
            if not file_path.is_file():
                continue

            # Skip if in shards
            if "shards" in file_path.parts:
                continue

            # Skip system directories
            if any(skip in file_path.parts for skip in ['.git', '__pycache__', 'node_modules', '.venv']):
                continue

            # Skip allowed root files
            rel_path = file_path.relative_to(layer_path)
            if rel_path.name in allowed_root_files and len(rel_path.parts) == 1:
                continue

            # This is orphaned
            orphaned.append(file_path)

    print(f"  [FOUND] {len(orphaned)} orphaned files")

    return orphaned


def consolidate_duplicates(duplicates: Dict[str, List[Path]], dry_run: bool = True) -> int:
    """
    Consolidate duplicate files:
    - Keep one copy in appropriate shard
    - Delete others
    """

    print(f"\n[CONSOLIDATE] Processing {len(duplicates)} duplicate sets...")
    if dry_run:
        print("  [DRY RUN] No files will be modified")

    actions = []
    consolidated = 0

    for file_hash, files in duplicates.items():
        # Sort files by priority
        # Priority: files in shards > files in implementations > other files
        files_sorted = sorted(files, key=lambda f: (
            0 if "shards" in f.parts else 1,
            0 if "implementations" in f.parts else 1,
            len(f.parts)  # Prefer deeper paths (more specific)
        ))

        # Keep the first (highest priority)
        keep = files_sorted[0]
        remove = files_sorted[1:]

        for rm_file in remove:
            action = {
                "action": "delete_duplicate",
                "file": str(rm_file.relative_to(REPO_ROOT)),
                "kept_original": str(keep.relative_to(REPO_ROOT)),
                "reason": "duplicate"
            }
            actions.append(action)

            if not dry_run:
                try:
                    rm_file.unlink()
                    print(f"  [DELETE] {rm_file.relative_to(REPO_ROOT)}")
                    consolidated += 1
                except Exception as e:
                    print(f"  [ERROR] Failed to delete {rm_file}: {e}")
            else:
                print(f"  [WOULD DELETE] {rm_file.relative_to(REPO_ROOT)}")
                consolidated += 1

    return consolidated


def move_orphaned_files(orphaned: List[Path], dry_run: bool = True) -> int:
    """
    Move orphaned files into appropriate shards
    """

    print(f"\n[CONSOLIDATE] Processing {len(orphaned)} orphaned files...")
    if dry_run:
        print("  [DRY RUN] No files will be modified")

    actions = []
    moved = 0

    for file_path in orphaned:
        # Determine layer
        for layer in ROOT_LAYERS:
            if str(file_path).startswith(str(REPO_ROOT / layer)):
                # Classify to shard
                shard_id = classify_file_to_shard(file_path)

                # Determine target path
                # Try to preserve some structure
                rel_path = file_path.relative_to(REPO_ROOT / layer)

                # Default target: implementations directory in shard
                target = REPO_ROOT / layer / "shards" / shard_id / "implementations" / "legacy" / rel_path

                action = {
                    "action": "move_to_shard",
                    "from": str(file_path.relative_to(REPO_ROOT)),
                    "to": str(target.relative_to(REPO_ROOT)),
                    "shard": shard_id,
                    "reason": "orphaned"
                }
                actions.append(action)

                if not dry_run:
                    try:
                        target.parent.mkdir(parents=True, exist_ok=True)
                        shutil.move(str(file_path), str(target))
                        print(f"  [MOVE] {file_path.relative_to(REPO_ROOT)} -> {target.relative_to(REPO_ROOT)}")
                        moved += 1
                    except Exception as e:
                        print(f"  [ERROR] Failed to move {file_path}: {e}")
                else:
                    print(f"  [WOULD MOVE] {file_path.relative_to(REPO_ROOT)} -> {shard_id}")
                    moved += 1

                break

    return moved


def generate_consolidation_report(duplicates: int, orphaned: int, actions: List[Dict]) -> Dict:
    """Generate consolidation report"""

    report = {
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "summary": {
            "duplicates_consolidated": duplicates,
            "orphaned_files_moved": orphaned,
            "total_actions": len(actions)
        },
        "actions": actions[:100]  # Top 100 actions
    }

    return report


def main():
    """Main entry point"""

    import argparse

    parser = argparse.ArgumentParser(description="Consolidate files into shard structure")
    parser.add_argument("--dry-run", action="store_true", help="Don't modify files, just report")
    parser.add_argument("--execute", action="store_true", help="Actually move/delete files")

    args = parser.parse_args()

    dry_run = not args.execute

    print("=" * 80)
    print("SSID SHARD CONSOLIDATION TOOL")
    print("=" * 80)

    if dry_run:
        print("\n[MODE] DRY RUN - No files will be modified")
    else:
        print("\n[MODE] EXECUTE - Files will be moved/deleted")
        print("\n[WARNING] This will modify files. Make sure you have a backup!")
        response = input("Continue? (yes/no): ")
        if response.lower() != "yes":
            print("Aborted.")
            return

    # 1. Find duplicates
    duplicates = find_duplicates()

    # 2. Find orphaned files
    orphaned = find_orphaned_files()

    # 3. Consolidate duplicates
    dup_count = consolidate_duplicates(duplicates, dry_run=dry_run)

    # 4. Move orphaned files
    orphan_count = move_orphaned_files(orphaned, dry_run=dry_run)

    # 5. Generate report
    print("\n[REPORT] Generating consolidation report...")

    report = generate_consolidation_report(dup_count, orphan_count, [])

    report_path = REPO_ROOT / "02_audit_logging" / "reports" / "shard_consolidation_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)

    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"  [SAVED] {report_path.relative_to(REPO_ROOT)}")

    # Summary
    print("\n" + "=" * 80)
    print("CONSOLIDATION SUMMARY")
    print("=" * 80)
    print(f"Duplicate Sets: {len(duplicates)}")
    print(f"Duplicates Consolidated: {dup_count}")
    print(f"Orphaned Files: {len(orphaned)}")
    print(f"Orphaned Files Moved: {orphan_count}")
    print(f"\nTotal Actions: {dup_count + orphan_count}")

    if dry_run:
        print("\n[INFO] This was a DRY RUN. Use --execute to apply changes.")

    print("=" * 80)


if __name__ == "__main__":
    main()
