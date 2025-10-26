
import os, sys, tarfile, time, hashlib, json, pathlib
from datetime import datetime
REPO_ROOT = os.environ.get("SSID_REPO_ROOT", os.getcwd())
PLAN = pathlib.Path(REPO_ROOT)/"15_infra"/"backup"/"backup_plan.yaml"
OUTDIR = pathlib.Path(REPO_ROOT)/"02_audit_logging"/"archives"/"backups"
OUTDIR.mkdir(parents=True, exist_ok=True)
ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
tar_path = OUTDIR/f"ssid_backup_{ts}.tar.gz"
with tarfile.open(tar_path, "w:gz") as tar:
    tar.add(REPO_ROOT, arcname="SSID", filter=lambda info: info if ".git" not in info.name and "__pycache__" not in info.name and ".pytest_cache" not in info.name else None)
h=hashlib.sha256(open(tar_path,"rb").read()).hexdigest()
meta={"created": ts, "sha256": h, "path": str(tar_path)}
print(json.dumps(meta, ensure_ascii=False))
