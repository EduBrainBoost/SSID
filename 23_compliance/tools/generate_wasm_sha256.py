#!/usr/bin/env python3
"""
Generate SHA-256 hash files for WASM artifacts
Creates .wasm.sha256 files for all .wasm files in the wasm directory
"""
import hashlib
from pathlib import Path

def compute_sha256(file_path: Path) -> str:
    """Compute SHA-256 hash of a file"""
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    return sha256.hexdigest()

def main():
    wasm_dir = Path("23_compliance/wasm")

    if not wasm_dir.exists():
        print(f"[ERROR] WASM directory not found: {wasm_dir}")
        return 1

    wasm_files = list(wasm_dir.glob("*.wasm"))
    print(f"[SCAN] Found {len(wasm_files)} WASM files")
    print()

    created_count = 0
    for wasm_file in wasm_files:
        # Compute hash
        sha256_hash = compute_sha256(wasm_file)

        # Create .wasm.sha256 file
        sha_file = wasm_file.with_suffix('.wasm.sha256')
        sha_file.write_text(f"{sha256_hash}  {wasm_file.name}\n")

        print(f"[CREATED] {sha_file.name}")
        print(f"          {sha256_hash}")

        created_count += 1

    print()
    print(f"[OK] Generated {created_count} SHA-256 hash files")

    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
