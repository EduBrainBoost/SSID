#!/usr/bin/env python3
"""
SSID Structure Lock L3 – Final Version (v4.1)
Validates Root-24 structure, policies, and exceptions,
then writes reproducible evidence and hash-lock for CI.
"""

import os, sys, json, hashlib, datetime, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[4]
LOCK_DIR = ROOT / "24_meta_orchestration/registry/locks"
EVIDENCE_DIR = ROOT / "23_compliance/evidence/structure_lock"
POLICY_FILE = ROOT / "23_compliance/policies/structure_policy.yaml"
EXCEPTIONS_FILE = ROOT / "23_compliance/exceptions/root_level_exceptions.yaml"

def sha256sum(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def get_root_modules():
    return sorted([p.name for p in ROOT.iterdir() if p.is_dir() and p.name[:2].isdigit()])

def validate_structure():
    errors = []
    roots = get_root_modules()
    if len(roots) != 24:
        errors.append(f"Expected 24 roots, found {len(roots)}: {roots}")
    if not POLICY_FILE.exists():
        errors.append("Missing policy file")
    if not EXCEPTIONS_FILE.exists():
        errors.append("Missing exceptions file")
    return errors, roots

def write_lock(roots, errors):
    ts = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    LOCK_DIR.mkdir(parents=True, exist_ok=True)
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)

    data = {
        "timestamp_utc": ts,
        "roots_detected": roots,
        "root_count": len(roots),
        "policy_hash": sha256sum(POLICY_FILE) if POLICY_FILE.exists() else None,
        "exceptions_hash": sha256sum(EXCEPTIONS_FILE) if EXCEPTIONS_FILE.exists() else None,
        "errors": errors,
        "status": "PASS" if not errors else "FAIL"
    }

    # Write JSONs
    lock_file = LOCK_DIR / f"structure_lock_l3.json"
    evidence_file = EVIDENCE_DIR / f"structure_lock_l3_{ts}.json"
    lock_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
    evidence_file.write_text(json.dumps(data, indent=2), encoding="utf-8")

    print(f"🔒 Structure Lock L3 → {data['status']}")
    print(f"🧾 Evidence written to {evidence_file.relative_to(ROOT)}")

    return 0 if not errors else 24

def main():
    print("Running SSID Structure Lock L3 check …")
    errors, roots = validate_structure()
    exit_code = write_lock(roots, errors)
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
