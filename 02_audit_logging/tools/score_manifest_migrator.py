#!/usr/bin/env python3
"""
SSID Score Manifest Migrator
Converts raw scores in .md/.yaml/.json to canonical *.score.json manifests + SCORE_REF blocks.
"""
import os
import re
import json
import hashlib
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import subprocess

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPO_ROOT / "02_audit_logging/schemas/score_manifest.schema.json"
SCAN_DIRS = [
    REPO_ROOT / "02_audit_logging/reports",
    REPO_ROOT / "24_meta_orchestration",
    REPO_ROOT / "11_test_simulation",
    REPO_ROOT / "03_core",
    REPO_ROOT / "01_ai_layer",
    REPO_ROOT / "02_audit_logging",
]

# Regex patterns for score extraction
SCORE_PATTERNS = [
    # Pattern: X/100 or X/400 (not in URLs, not percentages)
    re.compile(r'(?:^|[^/\d\w])(\d{1,3})/(100|400)(?:[^%\d]|$)', re.MULTILINE),
    # Pattern: score: X/100
    re.compile(r'score:\s*(\d{1,3})/(100|400)', re.IGNORECASE),
    # Pattern: certification: X/100
    re.compile(r'certification:\s*(\d{1,3})/(100|400)', re.IGNORECASE),
]

def get_git_commit() -> str:
    """Get current git commit SHA."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except:
        return "local-dev"

def get_file_hash(filepath: Path) -> str:
    """Compute SHA-512 hash of file."""
    sha512 = hashlib.sha512()
    with open(filepath, 'rb') as f:
        sha512.update(f.read())
    return sha512.hexdigest()

def get_worm_signature(manifest: Dict) -> str:
    """Compute BLAKE2b signature of manifest."""
    canonical = json.dumps(manifest, sort_keys=True, separators=(',', ':'))
    return hashlib.blake2b(canonical.encode()).hexdigest()

def infer_score_kind(filepath: Path, context: str, scale_max: int) -> str:
    """Infer score kind from context."""
    if scale_max == 400:
        return "evolution"

    lower_context = context.lower()
    lower_path = str(filepath).lower()

    if any(x in lower_context or x in lower_path for x in ["cert", "certification", "zertifizierung", "gold", "platinum"]):
        return "cert"
    elif any(x in lower_context or x in lower_path for x in ["phase", "sprint"]):
        return "phase"
    else:
        return "cert"  # default

def infer_metadata(filepath: Path, context: str, value: int, scale_max: int) -> Dict:
    """Infer metadata from context."""
    metadata = {}

    lower_context = context.lower()

    # Infer grade
    if scale_max == 100:
        if value >= 95:
            metadata["grade"] = "PLATINUM"
        elif value >= 90:
            metadata["grade"] = "GOLD"
        elif value >= 80:
            metadata["grade"] = "SILVER"
        elif value >= 70:
            metadata["grade"] = "BRONZE"

    # Infer label from context
    if "platinum" in lower_context:
        metadata["label"] = "PLATINUM"
    elif "gold" in lower_context:
        metadata["label"] = "GOLD"
    elif "forensic" in lower_context:
        metadata["label"] = "Forensic"

    # Infer component from path
    parts = filepath.parts
    if "01_ai_layer" in parts:
        metadata["component"] = "AI Layer"
    elif "02_audit_logging" in parts:
        metadata["component"] = "Audit & Compliance"
    elif "03_core" in parts:
        metadata["component"] = "Core Foundation"
    elif "24_meta_orchestration" in parts:
        metadata["component"] = "Meta Orchestration"

    return metadata

def extract_scores_from_file(filepath: Path) -> List[Tuple[int, int, str, int]]:
    """Extract scores from file. Returns [(line_num, value, scale_max, context)]."""
    if not filepath.exists() or filepath.suffix not in ['.md', '.yaml', '.yml', '.json']:
        return []

    try:
        content = filepath.read_text(encoding='utf-8')
    except:
        return []

    lines = content.splitlines()
    findings = []

    for line_num, line in enumerate(lines, 1):
        # Skip already referenced scores
        if "SCORE_REF:" in line or "score.json" in line:
            continue

        for pattern in SCORE_PATTERNS:
            for match in pattern.finditer(line):
                try:
                    value = int(match.group(1))
                    scale_max = int(match.group(2))

                    # Get context (3 lines before and after)
                    start = max(0, line_num - 4)
                    end = min(len(lines), line_num + 3)
                    context = '\n'.join(lines[start:end])

                    findings.append((line_num, value, scale_max, context))
                except:
                    pass

    return findings

def create_score_manifest(
    filepath: Path,
    line_num: int,
    value: int,
    scale_max: int,
    context: str,
    worm_chain_prev: Optional[str] = None
) -> Dict:
    """Create a canonical score manifest."""
    score_id = str(uuid.uuid4())
    worm_uuid = str(uuid.uuid4())

    # Cap value at scale_max (fix 101/100 errors)
    value = min(value, scale_max)

    manifest = {
        "id": score_id,
        "kind": infer_score_kind(filepath, context, scale_max),
        "scale": {"max": scale_max, "min": 0},
        "value": value,
        "status": "actual",
        "source": {
            "file": str(filepath.relative_to(REPO_ROOT)).replace('\\', '/'),
            "hash": get_file_hash(filepath),
            "line": line_num,
            "context": context[:200]  # truncate
        },
        "ci": {
            "commit": get_git_commit(),
            "run_id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat() + "Z"
        },
        "worm": {
            "uuid": worm_uuid,
            "signature": "",  # computed after
            "chain_prev": worm_chain_prev if worm_chain_prev else None  # JSON null, not string
        },
        "metadata": infer_metadata(filepath, context, value, scale_max)
    }

    # Compute signature
    manifest["worm"]["signature"] = get_worm_signature(manifest)

    return manifest

def migrate_file(filepath: Path, worm_chain: List[str]) -> Tuple[int, List[Dict]]:
    """Migrate one file. Returns (num_migrated, manifests)."""
    findings = extract_scores_from_file(filepath)
    if not findings:
        return 0, []

    manifests = []

    for idx, (line_num, value, scale_max, context) in enumerate(findings):
        worm_prev = worm_chain[-1] if worm_chain else None
        manifest = create_score_manifest(filepath, line_num, value, scale_max, context, worm_prev)

        # Write manifest to file
        manifest_filename = f"{filepath.stem}_line{line_num}_{value}of{scale_max}.score.json"
        manifest_path = filepath.parent / manifest_filename

        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)

        manifests.append(manifest)
        worm_chain.append(manifest["worm"]["uuid"])

        print(f"  [+] Created {manifest_path.relative_to(REPO_ROOT)}")

    # Replace raw scores with SCORE_REF in original file
    try:
        content = filepath.read_text(encoding='utf-8')
        lines = content.splitlines()

        # Sort findings by line_num descending to avoid offset issues
        sorted_findings = sorted(enumerate(findings), key=lambda x: x[1][0], reverse=True)

        for idx, (line_num, value, scale_max, context) in sorted_findings:
            manifest_filename = f"{filepath.stem}_line{line_num}_{value}of{scale_max}.score.json"
            ref_comment = f"<!-- SCORE_REF:{filepath.parent.name}/{manifest_filename} -->"

            # Replace the score with reference
            line_idx = line_num - 1
            if line_idx < len(lines):
                original_line = lines[line_idx]
                # Replace only the first occurrence of the pattern
                for pattern in SCORE_PATTERNS:
                    if pattern.search(original_line):
                        lines[line_idx] = pattern.sub(f"{value}/{scale_max} {ref_comment}", original_line, count=1)
                        break

        # Write back
        filepath.write_text('\n'.join(lines), encoding='utf-8')
        print(f"  [+] Replaced scores in {filepath.relative_to(REPO_ROOT)}")

    except Exception as e:
        print(f"  [!] Could not update source file: {e}")

    return len(findings), manifests

def main():
    """Main migration routine."""
    print("=" * 80)
    print("SSID Score Manifest Migrator")
    print("=" * 80)

    worm_chain = []
    total_migrated = 0
    all_manifests = []

    for scan_dir in SCAN_DIRS:
        if not scan_dir.exists():
            continue

        print(f"\n[*] Scanning {scan_dir.relative_to(REPO_ROOT)}...")

        for filepath in scan_dir.rglob("*"):
            if filepath.is_file() and filepath.suffix in ['.md', '.yaml', '.yml', '.json']:
                if "score.json" in filepath.name:
                    continue  # skip existing manifests

                num_migrated, manifests = migrate_file(filepath, worm_chain)
                if num_migrated > 0:
                    total_migrated += num_migrated
                    all_manifests.extend(manifests)

    # Generate migration report
    report = {
        "migration_id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "commit": get_git_commit(),
        "total_scores_migrated": total_migrated,
        "total_manifests_created": len(all_manifests),
        "worm_chain_length": len(worm_chain),
        "worm_chain_head": worm_chain[-1] if worm_chain else None,
        "manifests": [
            {
                "id": m["id"],
                "kind": m["kind"],
                "value": m["value"],
                "scale_max": m["scale"]["max"],
                "source_file": m["source"]["file"],
                "worm_uuid": m["worm"]["uuid"]
            }
            for m in all_manifests
        ]
    }

    report_path = REPO_ROOT / "02_audit_logging/reports/score_manifest_migration_report.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 80)
    print(f"[OK] Migration complete!")
    print(f"   Scores migrated: {total_migrated}")
    print(f"   Manifests created: {len(all_manifests)}")
    print(f"   WORM chain length: {len(worm_chain)}")
    print(f"   Report: {report_path.relative_to(REPO_ROOT)}")
    print("=" * 80)

    return 0 if total_migrated >= 0 else 1

if __name__ == "__main__":
    exit(main())
