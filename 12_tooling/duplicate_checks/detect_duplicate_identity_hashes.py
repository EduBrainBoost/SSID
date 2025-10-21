#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
detect_duplicate_identity_hashes.py – SSID Anti-Gaming Detector
Prüft auf Hash-Kollisionen und doppelte DID-Proofs in identity_score/ & audit_logging/.
Autor: edubrainboost ©2025 MIT License
"""

import os
import json
import hashlib
import re
import yaml
import csv
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[2]
IDENTITY_DIR = ROOT / "08_identity_score"
AUDIT_DIR = ROOT / "02_audit_logging"
LOG_DIR = AUDIT_DIR / "logs"
EVIDENCE_DIR = AUDIT_DIR / "evidence"
REPORT_PATH = LOG_DIR / "anti_gaming_duplicate_hashes.jsonl"

SUPPORTED_EXT = (".json", ".yaml", ".yml", ".csv")
HASH_RE = re.compile(r"sha(256|3-256|512):[0-9a-f]{64,128}|blake2b:[0-9a-f]{64,128}", re.I)
DID_RE = re.compile(r"did:[a-z0-9]+:[a-zA-Z0-9._-]+", re.I)

def load_text(path: Path) -> str:
    """Load text content from file, handling errors gracefully."""
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""

def extract_candidates(content: str):
    """Extract hash and DID candidates from text content."""
    hashes = set(HASH_RE.findall(content))
    dids = set(DID_RE.findall(content))
    return hashes, dids

def scan_dir(directory: Path):
    """Recursively scan directory for supported file types and extract candidates."""
    candidates = []
    if not directory.exists():
        return candidates

    for root, _, files in os.walk(directory):
        for f in files:
            if f.endswith(SUPPORTED_EXT):
                p = Path(root) / f
                content = load_text(p)
                h, d = extract_candidates(content)
                if h or d:
                    candidates.append((p, h, d))
    return candidates

def build_index():
    """Build index of all hashes and DIDs found across monitored directories."""
    index = defaultdict(lambda: {"files": set(), "type": None})

    for directory in (IDENTITY_DIR, EVIDENCE_DIR):
        if not directory.exists():
            continue

        for path, hashes, dids in scan_dir(directory):
            for h in hashes:
                index[h]["files"].add(str(path))
                index[h]["type"] = "hash"

            for d in dids:
                index[d]["files"].add(str(path))
                index[d]["type"] = "did"

    return index

def detect_collisions(index):
    """Detect collisions where same hash/DID appears in multiple files."""
    collisions = []

    for key, meta in index.items():
        if len(meta["files"]) > 1:
            collisions.append({
                "value": key,
                "type": meta["type"],
                "count": len(meta["files"]),
                "files": sorted(meta["files"])
            })

    return sorted(collisions, key=lambda x: x["count"], reverse=True)

def log_findings(collisions):
    """Log findings to JSONL audit log."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    try:
        ts = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    except AttributeError:
        # Fallback for Python < 3.11
        ts = datetime.utcnow().isoformat() + "Z"
    status = "PASS" if not collisions else "FAIL"

    entry = {
        "timestamp": ts,
        "component": "anti_gaming",
        "check": "duplicate_identity_hashes",
        "status": status,
        "collision_count": len(collisions),
        "collisions": collisions
    }

    with REPORT_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    print(f"[{status}] {len(collisions)} duplicate identities detected.")

    if collisions:
        print("\nCollision details:")
        for c in collisions[:5]:  # Show top 5
            print(f"  - {c['type'].upper()}: {c['value'][:50]}... ({c['count']} files)")
        if len(collisions) > 5:
            print(f"  ... and {len(collisions) - 5} more (see log)")

    return status, collisions

def main():
    """Main execution function."""
    print("[SCAN] Scanning for duplicate identity hashes and DIDs...")

    index = build_index()
    print(f"       Found {len(index)} unique identifiers")

    collisions = detect_collisions(index)
    status, _ = log_findings(collisions)

    if status == "FAIL":
        # Exit code 2 = policy violation
        exit(2)
    else:
        exit(0)

if __name__ == "__main__":
    main()
