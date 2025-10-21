#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSID - WORM Chain Integrity Verifier

Validates SHA-512 chain integrity and monotonic timestamps in WORM immutable store.

Exit Codes:
  0: Chain OK (all signatures valid, monotonic timestamps)
  1: Too few entries (< 2 files - warning level)
  2: Integrity failure (bad SHA-512 or non-monotonic timestamps)
"""

import json
import hashlib
import sys
from pathlib import Path
from typing import Dict, Any

STORE = Path("02_audit_logging/storage/worm/immutable_store")

def h512(b: bytes) -> str:
    """Calculate SHA-512 hash."""
    return hashlib.sha512(b).hexdigest()

def main() -> int:
    """
    Main verification flow.

    Returns:
        Exit code (0=OK, 1=warn, 2=fail)
    """
    repo_root = Path(__file__).resolve().parent.parent.parent
    store_path = repo_root / STORE

    if not store_path.exists():
        print(f"[FAIL] WORM store not found: {STORE}")
        return 2

    # Find all sot_enforcement WORM files
    files = sorted(p for p in store_path.glob("sot_enforcement*.json") if p.is_file())

    if len(files) < 2:
        print(f"[WARN] Not enough WORM entries for chain verification (found {len(files)}, need ≥ 2)")
        return 1

    print(f"[OK] Found {len(files)} WORM entries, verifying chain...")

    prev_doc = None
    errors = []

    for idx, file_path in enumerate(files):
        try:
            # Read WORM entry
            data = file_path.read_bytes()
            doc = json.loads(data)

            # Extract result and signature
            result = doc.get("result", {})
            signature = doc.get("worm_signature", {})

            # Verify SHA-512 hash of result
            result_json = json.dumps(result, ensure_ascii=True, separators=(",", ":"), sort_keys=True)
            calculated_sha512 = h512(result_json.encode("utf-8"))
            stored_sha512 = signature.get("sha512", "")

            if calculated_sha512 != stored_sha512:
                errors.append(f"[FAIL] SHA-512 mismatch in {file_path.name}")
                errors.append(f"       Expected: {stored_sha512}")
                errors.append(f"       Calculated: {calculated_sha512}")

            # Verify monotonic timestamps
            current_ts = signature.get("timestamp", "")
            if prev_doc:
                prev_ts = prev_doc.get("worm_signature", {}).get("timestamp", "")
                if current_ts <= prev_ts:
                    errors.append(f"[FAIL] Non-monotonic timestamp at {file_path.name}")
                    errors.append(f"       Previous: {prev_ts}")
                    errors.append(f"       Current:  {current_ts}")

            # Verify required fields exist
            if not signature.get("uuid"):
                errors.append(f"[FAIL] Missing UUID in {file_path.name}")
            if not signature.get("blake2b"):
                errors.append(f"[FAIL] Missing BLAKE2b hash in {file_path.name}")

            # Store for next iteration
            prev_doc = doc

        except json.JSONDecodeError as e:
            errors.append(f"[FAIL] JSON parse error in {file_path.name}: {e}")
        except Exception as e:
            errors.append(f"[FAIL] Error processing {file_path.name}: {e}")

    # Print results
    if errors:
        print(f"\n[FAIL] WORM chain integrity check FAILED ({len(errors)} errors):")
        for error in errors:
            print(f"  {error}")
        return 2
    else:
        print(f"[OK] WORM chain intact - all {len(files)} signatures valid")
        print(f"[OK] Monotonic timestamps verified")
        print(f"[OK] SHA-512 hashes verified")
        return 0

if __name__ == "__main__":
    sys.exit(main())
