
import json, os, time, hashlib, pathlib

REPO_ROOT = os.environ.get("SSID_REPO_ROOT", os.getcwd())
STATE_FILE = pathlib.Path(REPO_ROOT) / "24_meta_orchestration" / "meta_state_matrix.json"
REGISTRY_FILE = pathlib.Path(REPO_ROOT) / "24_meta_orchestration" / "meta_registry.json"
OUT = pathlib.Path(REPO_ROOT) / "02_audit_logging" / "reports" / "INTEGRITY_MONITOR_REPORT.json"

def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for c in iter(lambda: f.read(8192), b""):
            h.update(c)
    return h.hexdigest()

def run_integrity():
    result = {
        "timestamp": int(time.time()),
        "checks": [],
        "drift": 0
    }
    if REGISTRY_FILE.exists():
        reg = json.loads(REGISTRY_FILE.read_text(encoding="utf-8"))
        for f in reg.get("files", []):
            p = os.path.join(REPO_ROOT, f["path"])
            ok = os.path.exists(p)
            sha = _sha256(p) if ok else None
            drift = 0
            if ok and sha != f["sha256"]:
                drift = 1
            result["checks"].append({"path": f["path"], "present": ok, "expected_sha256": f["sha256"], "actual_sha256": sha, "drift": drift})
            result["drift"] += drift
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result

if __name__ == "__main__":
    print(json.dumps(run_integrity(), ensure_ascii=False))
