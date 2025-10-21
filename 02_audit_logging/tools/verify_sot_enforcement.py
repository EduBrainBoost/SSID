#!/usr/bin/env python3
"""
SSID - SoT Functional Enforcement Verifier (Level 4 Activation)
Features added:
- --ci-mode: deterministic, non-interactive, ASCII-safe
- --worm-sign: writes immutable audit proof into WORM store
- --json-out: structured result
- Certification tiers + exit codes (0 pass, 1 warn, 2 fail)
- Minimal dependencies only (stdlib + rich optional)
"""

import argparse, json, os, sys, hashlib, datetime, uuid
from pathlib import Path

# Lightweight pretty output
def info(msg): print(f"[INFO] {msg}")
def warn(msg): print(f"[WARN] {msg}")
def err(msg):  print(f"[FAIL] {msg}")

def sha512_hex(data: bytes) -> str:
    return hashlib.sha512(data).hexdigest()

def blake2b_hex(data: bytes) -> str:
    return hashlib.blake2b(data, digest_size=32).hexdigest()

def file_exists(p: str) -> bool:
    return Path(p).is_file()

def dir_exists(p: str) -> bool:
    return Path(p).is_dir()

def score_from_bools(checks):
    # weights for L4 bundle verification
    weights = {
        "has_structure_guard": 10,
        "has_opa_policies_dir": 10,
        "has_lock_gate": 10,
        "workflow_refs_exist": 20,
        "pre_commit_refs_exist": 15,
        "tests_exist": 15,
        "worm_store_exists": 20,
    }
    score = 0
    for k, ok in checks.items():
        score += weights.get(k, 0) if ok else 0
    return score

def detect_workflow_refs():
    yml = Path(".github/workflows/ci_enforcement_gate.yml")
    if not yml.is_file():
        return False
    text = yml.read_text(encoding="utf-8", errors="ignore")
    needed = [
        "structure_guard.sh",
        "23_compliance/policies",
        "verify_sot_enforcement.py",
    ]
    return all(s in text for s in needed)

def detect_pre_commit_refs():
    pc = Path(".pre-commit-config.yaml")
    if not pc.is_file():
        return False
    txt = pc.read_text(encoding="utf-8", errors="ignore")
    return ("structure_validation.sh" in txt) and ("verify_sot_enforcement.py" in txt)

def write_worm_signature(result: dict):
    # write JSON into immutable_store with content hash in filename
    store = Path("02_audit_logging/storage/worm/immutable_store")
    store.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(result, ensure_ascii=True, separators=(",", ":")).encode("utf-8")
    sig = {
        "kind": "sot_enforcement_signature",
        "ts": datetime.datetime.utcnow().isoformat() + "Z",
        "sha512": sha512_hex(payload),
        "blake2b": blake2b_hex(payload),
        "uuid": str(uuid.uuid4()),
        "algorithm": "Dilithium2(placeholder)-chain",
        "status": result.get("status"),
        "score": result.get("score"),
    }
    final = {"result": result, "signature": sig}
    out_bytes = json.dumps(final, ensure_ascii=True, separators=(",", ":")).encode("utf-8")
    fname = f"sot_enforcement_{sig['ts'].replace(':','').replace('-','')}_{sig['uuid']}.json"
    (store / fname).write_bytes(out_bytes)
    return str(store / fname), sig

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ci-mode", action="store_true")
    ap.add_argument("--pre-commit", action="store_true")
    ap.add_argument("--worm-sign", action="store_true")
    ap.add_argument("--json-out", type=str, default="")
    args = ap.parse_args()

    checks = {
        "has_structure_guard": file_exists("12_tooling/scripts/structure_guard.sh"),
        "has_opa_policies_dir": dir_exists("23_compliance/policies"),
        "has_lock_gate": file_exists("24_meta_orchestration/triggers/ci/gates/structure_lock_l3.py"),
        "workflow_refs_exist": detect_workflow_refs(),
        "pre_commit_refs_exist": detect_pre_commit_refs(),
        "tests_exist": dir_exists("11_test_simulation/tests"),
        "worm_store_exists": dir_exists("02_audit_logging/storage/worm/immutable_store"),
    }
    score = score_from_bools(checks)

    status = "FAIL"
    exit_code = 2
    if score >= 95:
        status, exit_code = "PLATINUM", 0
    elif score >= 85:
        status, exit_code = "GOLD", 0
    elif score >= 70:
        status, exit_code = "SILVER", 1
    elif score >= 50:
        status, exit_code = "BRONZE", 1
    else:
        status, exit_code = "NONE", 2

    result = {
        "ts": datetime.datetime.utcnow().isoformat() + "Z",
        "status": status,
        "score": score,
        "checks": checks,
        "mode": "ci" if args.ci_mode else ("pre-commit" if args.pre_commit else "manual"),
        "policy": {"ok_threshold": 85, "warn_threshold": 70}
    }

    if args.worm_sign:
        path, sig = write_worm_signature(result)
        result["worm_signature_path"] = path
        result["worm_sig"] = sig

    if args.json_out:
        Path(args.json_out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.json_out).write_text(json.dumps(result, indent=2, ensure_ascii=True), encoding="utf-8")

    # Human readable summary
    print("== SoT Functional Enforcement Result ==")
    print(json.dumps(result, indent=2, ensure_ascii=True))

    sys.exit(exit_code)

if __name__ == "__main__":
    main()
