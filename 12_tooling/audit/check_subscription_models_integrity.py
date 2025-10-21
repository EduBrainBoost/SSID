#!/usr/bin/env python3
"""
SSID Subscription Integrity Check v12.4
Checks if all subscription models, pricing policies, and related artifacts exist
"""
import os, json, hashlib, pathlib

ROOTS = ["03_core", "07_governance_legal", "08_identity_score",
         "09_meta_identity", "13_ui_layer", "23_compliance"]

KEY_FILES = [
    "pricing_model.yaml",
    "subscription_tiers.yaml",
    "pricing_enforcement.rego",
    "pricing_enforcement_v5_2.rego",
    "pricing_enforcement_v6_0.rego",
    "policy_pricing_enforcement_v5_3.rego",
    "policy_pricing_enforcement_v6_1.rego",
    "policy_pricing_enforcement_v6_2.rego",
    "pricing_enforcement_v6_3.rego",
    "pricing_integration_test.py",
    "pricing_api.json",
    "pricing_sla.yaml",
    "pricing_limits.yaml",
]

REPORT = {"checked_files": [], "missing": [], "hashes": {}}

base = pathlib.Path.cwd()

for root in ROOTS:
    for name in KEY_FILES:
        path = base / root
        found = list(path.rglob(name))
        if found:
            for f in found:
                try:
                    h = hashlib.sha256(f.read_bytes()).hexdigest()
                    REPORT["checked_files"].append(str(f))
                    REPORT["hashes"][str(f)] = h
                except Exception as e:
                    REPORT["missing"].append(f"{root}/{name} (read error: {e})")
        else:
            REPORT["missing"].append(f"{root}/{name}")

out = base / "02_audit_logging/reports/subscription_integrity_report.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(REPORT, indent=2))
print(f"[OK] Subscription integrity report written to {out}")
print(f"Checked {len(REPORT['checked_files'])} files, missing {len(REPORT['missing'])}")
if REPORT["missing"]:
    print("Missing files:")
    for m in REPORT["missing"]:
        print(" -", m)
else:
    print("[OK] All subscription artifacts present and accounted for")
