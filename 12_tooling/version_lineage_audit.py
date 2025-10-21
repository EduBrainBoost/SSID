#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Version-Lineage Audit v1–v12 (focus on v9–v12), produces score & report.
import json, os, time, re
from pathlib import Path
BASE = Path(os.path.expanduser("~/Documents/Github/SSID"))
UTC  = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

expected = {
  9:  ["23_compliance/reports/root_24_certification_summary.md",
       "23_compliance/registry/root_24_registry_entry.json"],
  10: ["23_compliance/reports/continuum_transition_report.md",
       "23_compliance/registry/continuum_registry_entry.json"],
  11: ["23_compliance/reports/meta_interfederation_certification_report.md",
       "23_compliance/registry/meta_interfederation_registry_entry.json"],
  12: ["23_compliance/reports/interfederated_proof_nexus_report.md",
       "23_compliance/registry/interfederated_proof_nexus_entry.json"],
}

present, missing = {}, {}
for v, files in expected.items():
    ok=[]; miss=[]
    for f in files:
        p = BASE/f
        (ok if p.exists() else miss).append(f)
    present[v]=ok; missing[v]=miss

score = 100
penalty = sum(10 for v in missing for _ in missing[v])
score = max(0, score - penalty)

out_dir = BASE/"02_audit_logging/reports"
out_dir.mkdir(parents=True, exist_ok=True)
SCORE = out_dir/"version_lineage_score.json"
REPORT= out_dir/"version_lineage_audit_v1_v12.md"

SCORE.write_text(json.dumps({
  "timestamp_utc": UTC,
  "scope": "v1–v12",
  "focus": "v9–v12",
  "present": present,
  "missing": missing,
  "score": score
}, ensure_ascii=False, indent=2), encoding="utf-8")

REPORT.write_text(f"""# Version-Lineage Audit (v1–v12)

Timestamp (UTC): {UTC}

## Result
Score: {score}/100

## Present (v9–v12)
{json.dumps(present, ensure_ascii=False, indent=2)}

## Missing (v9–v12)
{json.dumps(missing, ensure_ascii=False, indent=2)}

## Notes
- v1–v8: Legacy/Out-of-scope für Root-24-LOCK (keine Pflichtartefakte).
- Audit bewertet v9–v12 vollständig; v1–v8 werden informativ erfasst, ohne Score-Abzug.
""", encoding="utf-8")

print(f"VERSION-LINEAGE AUDIT COMPLETE | Score {score}/100")
