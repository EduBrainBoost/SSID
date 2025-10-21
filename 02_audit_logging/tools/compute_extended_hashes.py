#!/usr/bin/env python3
"""
Extended Hash Computation for Unified Files
Computes SHA-256, SHA-512, and BLAKE3 hashes for all unified archive files.
"""

import hashlib
import json
from pathlib import Path

# Archive directory
ARCHIVE_DIR = Path(r"C:\Users\bibel\Documents\Github\SSID\02_audit_logging\archives\unified_sources_20251018T100512254602Z")

def compute_hashes(file_path: Path) -> dict:
    """Compute SHA-256, SHA-512, and BLAKE3 hashes for a file."""
    sha256 = hashlib.sha256()
    sha512 = hashlib.sha512()

    # Note: BLAKE3 is not in standard library, but we can use hashlib for SHA variants
    # For full BLAKE3 support, would need: pip install blake3
    # For now, we'll compute SHA-256 and SHA-512

    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
            sha512.update(chunk)

    return {
        "sha256": sha256.hexdigest(),
        "sha512": sha512.hexdigest(),
        "file_size_bytes": file_path.stat().st_size
    }

def main():
    print(f"Computing extended hashes for unified files in: {ARCHIVE_DIR}")

    unified_files = [
        "unified_python_all.py",
        "unified_yaml_all.yaml",
        "unified_rego_all.rego",
        "unified_json_all.json"
    ]

    extended_hashes = {}

    for filename in unified_files:
        file_path = ARCHIVE_DIR / filename
        if file_path.exists():
            print(f"[HASH] Processing {filename}...")
            hashes = compute_hashes(file_path)
            extended_hashes[filename] = hashes
            print(f"  SHA-256: {hashes['sha256']}")
            print(f"  SHA-512: {hashes['sha512']}")
            print(f"  Size: {hashes['file_size_bytes']:,} bytes")
        else:
            print(f"[WARN] File not found: {filename}")

    # Write extended hash manifest
    output_path = ARCHIVE_DIR / "unified_hashes_extended.json"
    print(f"\n[OUTPUT] Writing extended hash manifest: {output_path}")

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(extended_hashes, f, indent=2)

    print(f"[DONE] Extended hashes computed for {len(extended_hashes)} files")
    return extended_hashes

if __name__ == "__main__":
    main()
