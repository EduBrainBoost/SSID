
import os, time, subprocess, sys, pathlib, json, datetime

REPO_ROOT = os.environ.get("SSID_REPO_ROOT", os.getcwd())
SNAP = pathlib.Path(REPO_ROOT) / "15_infra" / "backup" / "backup_snapshot.py"
LOG = pathlib.Path(REPO_ROOT) / "02_audit_logging" / "reports" / "BACKUP_DAEMON_LOG.jsonl"

def run_once():
    r = subprocess.run([sys.executable, str(SNAP)], capture_output=True, text=True)
    ok = r.returncode == 0
    entry = {
        "ts": datetime.datetime.utcnow().isoformat()+"Z",
        "ok": ok,
        "output": r.stdout.strip()[:2000],
        "error": r.stderr.strip()[:1000]
    }
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
    return ok

if __name__ == "__main__":
    # Not a real daemon loop; CI-friendly single shot
    ok = run_once()
    print(json.dumps({"ok": ok}, ensure_ascii=False))
