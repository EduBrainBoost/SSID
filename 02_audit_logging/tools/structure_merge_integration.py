#!/usr/bin/env python3
"""
SSID Structure Merge & Integration Tool
========================================
Merged Inhalte von falschen lowercase Shards in korrekte Shard_XX_XXX

Usage:
    python structure_merge_integration.py
"""

from pathlib import Path
import shutil
from datetime import datetime
import json


# Mapping lowercase → Shard_XX
SHARD_MAPPING = {
    "01_identitaet_personen": "Shard_01_Identitaet_Personen",
    "02_dokumente_nachweise": "Shard_02_Dokumente_Nachweise",
    "03_zugang_berechtigungen": "Shard_03_Zugang_Berechtigungen",
    "04_kommunikation_daten": "Shard_04_Kommunikation_Daten",
    "05_gesundheit_medizin": "Shard_05_Gesundheit_Medizin",
    "06_bildung_qualifikationen": "Shard_06_Bildung_Qualifikationen",
    "07_familie_soziales": "Shard_07_Familie_Soziales",
    "08_mobilitaet_fahrzeuge": "Shard_08_Mobilitaet_Fahrzeuge",
    "09_arbeit_karriere": "Shard_09_Arbeit_Karriere",
    "10_finanzen_banking": "Shard_10_Finanzen_Banking",
    "11_versicherungen_risiken": "Shard_11_Versicherungen_Risiken",
    "12_immobilien_grundstuecke": "Shard_12_Immobilien_Grundstuecke",
    "13_unternehmen_gewerbe": "Shard_13_Unternehmen_Gewerbe",
    "14_vertraege_vereinbarungen": "Shard_14_Vertraege_Vereinbarungen",
    "15_handel_transaktionen": "Shard_15_Handel_Transaktionen",
    "16_behoerden_verwaltung": "Shard_16_Behoerden_Verwaltung",
}

ALL_ROOTS = [
    "01_ai_layer", "02_audit_logging", "03_core", "04_deployment",
    "05_documentation", "06_data_pipeline", "07_governance_legal",
    "08_identity_score", "09_meta_identity", "10_interoperability",
    "11_test_simulation", "12_tooling", "13_ui_layer", "14_zero_time_auth",
    "15_infra", "16_codex", "17_observability", "18_data_layer",
    "19_adapters", "20_foundation", "21_post_quantum_crypto",
    "22_datasets", "23_compliance", "24_meta_orchestration",
]


def merge_directories(src: Path, dst: Path, dry_run=False):
    """Merge src directory into dst, keeping dst files on conflict."""

    if not src.exists():
        return 0, 0, []

    if not dst.exists():
        # Simple case: just rename/move
        if not dry_run:
            shutil.move(str(src), str(dst))
        return 1, 0, [f"MOVE: {src} -> {dst}"]

    # Complex case: merge contents
    actions = []
    files_copied = 0
    conflicts = 0

    for item in src.rglob("*"):
        if not item.is_file():
            continue

        relative = item.relative_to(src)
        target = dst / relative

        if target.exists():
            # Conflict: file exists in both
            conflicts += 1
            actions.append(f"CONFLICT: {relative} (keeping destination version)")
        else:
            # Safe to copy
            files_copied += 1
            if not dry_run:
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(str(item), str(target))
            actions.append(f"COPY: {relative}")

    return files_copied, conflicts, actions


def integrate_shards(repo_path: Path, dry_run=True):
    """Integrate lowercase shards into correct Shard_XX_XXX structure."""

    print()
    print("=" * 80)
    print("SSID STRUCTURE MERGE & INTEGRATION")
    print("=" * 80)
    print()

    if dry_run:
        print("[DRY RUN] No changes will be made - showing what WOULD happen")
        print()

    total_merged = 0
    total_files = 0
    total_conflicts = 0
    merge_log = []

    for root_name in ALL_ROOTS:
        root_path = repo_path / root_name / "shards"

        if not root_path.exists():
            continue

        for lowercase, correct in SHARD_MAPPING.items():
            src_shard = root_path / lowercase
            dst_shard = root_path / correct

            if not src_shard.exists():
                continue  # Already cleaned or never existed

            print(f"[{root_name}] Merging: {lowercase} -> {correct}")

            files, conflicts, actions = merge_directories(src_shard, dst_shard, dry_run=dry_run)

            total_merged += 1
            total_files += files
            total_conflicts += conflicts

            merge_log.append({
                "root": root_name,
                "source": lowercase,
                "destination": correct,
                "files_copied": files,
                "conflicts": conflicts,
                "actions": actions[:10]  # First 10 actions only
            })

            if files > 0:
                print(f"  -> Copied {files} files")
            if conflicts > 0:
                print(f"  -> {conflicts} conflicts (kept destination)")

            # Remove empty source directory
            if not dry_run and src_shard.exists():
                try:
                    shutil.rmtree(src_shard)
                    print(f"  -> Removed {lowercase}")
                except:
                    print(f"  -> Could not remove {lowercase} (may have remaining files)")

    print()
    print("=" * 80)
    print("MERGE SUMMARY")
    print("=" * 80)
    print(f"  Shards merged:        {total_merged}")
    print(f"  Files copied:         {total_files}")
    print(f"  Conflicts (kept dst): {total_conflicts}")
    print()

    # Save merge log
    log_path = repo_path / "02_audit_logging" / "reports" / "structure_merge_log.json"
    log_path.parent.mkdir(parents=True, exist_ok=True)

    with open(log_path, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "dry_run": dry_run,
            "summary": {
                "shards_merged": total_merged,
                "files_copied": total_files,
                "conflicts": total_conflicts,
            },
            "details": merge_log
        }, f, indent=2)

    print(f"[+] Merge log saved: {log_path}")
    print()

    return total_merged, total_files, total_conflicts


def main():
    repo_path = Path(".")

    # Step 1: Dry run to show what would happen
    print("[STEP 1] DRY RUN - Preview changes")
    print()
    merged, files, conflicts = integrate_shards(repo_path, dry_run=True)

    if merged == 0:
        print("[OK] No lowercase shards found - structure already clean!")
        return 0

    print()
    print("=" * 80)
    print("[STEP 2] Ready to execute")
    print("=" * 80)
    print()
    print(f"Will merge {merged} shards and copy {files} files")
    print(f"{conflicts} conflicts will be resolved by keeping destination files")
    print()

    response = input("Execute merge? [yes/no]: ").strip().lower()

    if response == "yes":
        print()
        print("[STEP 2] EXECUTING MERGE...")
        print()
        integrate_shards(repo_path, dry_run=False)

        print("=" * 80)
        print("[SUCCESS] Structure merge complete!")
        print("=" * 80)
        print()
        print("[NEXT] Run structure_audit.py again to verify 384 correct shards")
        print()
    else:
        print()
        print("[CANCELLED] No changes made")
        print()

    return 0


if __name__ == "__main__":
    exit(main())
