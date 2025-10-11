#!/usr/bin/env python3
"""Fast policy migration - Python version for Windows compatibility"""

import shutil
import json
from pathlib import Path
from datetime import datetime, timezone

repo_root = Path(__file__).resolve().parents[1]
policy_inventory = repo_root / "23_compliance" / "reports" / "policy_dirs.txt"

print("="*60)
print("Fast Policy Migration - Python Version")
print("="*60)

# Read inventory
with open(policy_inventory, 'r') as f:
    policy_dirs = [line.strip() for line in f if line.strip()]

print(f"\nProcessing {len(policy_dirs)} policy directories...")

migrated = 0
skipped = 0
errors = 0

for policy_dir_str in policy_dirs:
    policy_dir = repo_root / policy_dir_str.lstrip('./')

    if not policy_dir.exists():
        skipped += 1
        continue

    # Extract module name
    parts = policy_dir.parts
    module_idx = None
    for i, part in enumerate(parts):
        if part.startswith(tuple(f"{n:02d}_" for n in range(1, 25))):
            module_idx = i
            break

    if module_idx is None:
        skipped += 1
        continue

    module = parts[module_idx]
    target_dir = repo_root / "23_compliance" / "policies" / module
    target_dir.mkdir(parents=True, exist_ok=True)

    # Copy YAML files
    for yaml_file in list(policy_dir.glob("*.yaml")) + list(policy_dir.glob("*.yml")):
        try:
            target_file = target_dir / yaml_file.name

            if target_file.exists():
                if yaml_file.read_bytes() == target_file.read_bytes():
                    skipped += 1
                    continue

            shutil.copy2(yaml_file, target_file)
            migrated += 1

            if migrated % 100 == 0:
                print(f"  Progress: {migrated} files migrated...")

        except Exception as e:
            print(f"  ERROR: {yaml_file}: {e}")
            errors += 1

print(f"\nMigration complete:")
print(f"  Migrated: {migrated}")
print(f"  Skipped: {skipped}")
print(f"  Errors: {errors}")

# Count centralized files
total_centralized = len(list((repo_root / "23_compliance" / "policies").rglob("*.yaml")))
total_centralized += len(list((repo_root / "23_compliance" / "policies").rglob("*.yml")))

print(f"\nTotal centralized policy files: {total_centralized}")

# Generate evidence
evidence = {
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "migrated": migrated,
    "skipped": skipped,
    "errors": errors,
    "total_centralized": total_centralized
}

evidence_file = repo_root / "23_compliance" / "evidence" / "policy_migration" / f"migration_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
evidence_file.parent.mkdir(parents=True, exist_ok=True)

with open(evidence_file, 'w') as f:
    json.dump(evidence, f, indent=2)

print(f"\nEvidence saved: {evidence_file}")
print("\n[OK] Migration complete!")
