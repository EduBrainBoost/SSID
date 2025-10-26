
#!/usr/bin/env python3
import json, sys, os, pathlib
REPO_ROOT = os.environ.get("SSID_REPO_ROOT", os.getcwd())
STATE = pathlib.Path(REPO_ROOT) / "24_meta_orchestration" / "meta_state_matrix.json"
out = {
  "boot_report_required": True,
  "global_score": 0,
  "artifacts": []
}
if STATE.exists():
    data = json.loads(STATE.read_text(encoding="utf-8"))
    out["global_score"] = data.get("global_score", 0)
    out["artifacts"] = data.get("artifacts", [])
print(json.dumps(out, ensure_ascii=False))
