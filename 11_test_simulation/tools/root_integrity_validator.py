#!/usr/bin/env python3
import os, sys, json, argparse, pathlib
ALLOWED = ["01_ai_layer","02_audit_logging","03_core","04_deployment","05_documentation","06_data_pipeline","07_governance_legal","08_identity_score","09_meta_identity","10_interoperability","11_test_simulation","12_tooling","13_ui_layer","14_zero_time_auth","15_infra","16_codex","17_observability","18_data_layer","19_adapters","20_foundation","21_post_quantum_crypto","22_datasets","23_compliance","24_meta_orchestration",".github",".git",".gitmodules",".gitattributes",".LICENSE",".README",".pytest",".claude","ssid_validator"]
WHITELIST_FILES = {".gitignore","LICENSE","README","playwright.config.ts","package.json","coverage","COVERAGE.out"}
ap = argparse.ArgumentParser(); ap.add_argument("--repo", required=True); ap.add_argument("--fail_on_violation", action="store_true"); a = ap.parse_args()
repo = pathlib.Path(a.repo).resolve(); offenders = []
for p in repo.iterdir():
  name = p.name
  if name in ALLOWED: continue
  if p.is_file() and name in WHITELIST_FILES: continue
  offenders.append(name)
print(json.dumps({"root": str(repo), "violations": sorted(offenders), "allowed_roots": ALLOWED}, indent=2))
if a.fail_on_violation and offenders: sys.exit(2)
