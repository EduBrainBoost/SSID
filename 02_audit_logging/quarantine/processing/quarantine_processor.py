#!/usr/bin/env python3
import json, sys, time, pathlib
p = pathlib.Path("23_compliance/evidence/malware_quarantine_hashes")
p.mkdir(parents=True, exist_ok=True)
log = p/"quarantine_hash_ledger.json"
if not log.exists(): log.write_text("[]")
data = json.loads(log.read_text())
data.append({"ts": int(time.time()), "trigger": sys.argv[sys.argv.index("--trigger")+1] if "--trigger" in sys.argv else "manual"})
log.write_text(json.dumps(data, indent=2))
print("quarantine processed")
