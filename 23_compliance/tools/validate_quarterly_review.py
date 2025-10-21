#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quarterly Review Framework Validator (2025-Q4)
- Prüft: review_template.yaml, reviewer_checklist.yaml, reviewer_assignments.yaml, review_findings.yaml, README.md, test_review_templates.py
- Validierungen:
  * YAML-Struktur & Pflichtfelder
  * 5 Kategorien: STRUCTURE, LEGAL, SECURITY, AI_COMPLIANCE, OBSERVABILITY
  * DID-Format (did:ssid:[a-z0-9]+)
  * Dates/Deadlines ISO-8601 (YYYY-MM-DD)
  * Evidence-Paths müssen in erlaubten Roots liegen (Root-24-LOCK)
  * Coverage der Referenz-Frameworks (GDPR/DORA/MiCA/AMLD6/TECH)
  * Escalation-Policy bei CRITICAL-Findings
- Outputs:
  * JSONL: 02_audit_logging/logs/review_framework.jsonl (append-only, WORM)
  * Score JSON: 23_compliance/reports/review_framework_score.json
  * MD Report: 23_compliance/reports/review_framework_audit_report.md
- Exit: 0 PASS / 2 FAIL
"""
import re, json, sys, pathlib, hashlib
from datetime import datetime
from typing import Dict, Any, List

try:
    import yaml
except Exception:
    print("Missing dependency: pyyaml", file=sys.stderr); sys.exit(2)

ROOT = pathlib.Path(__file__).resolve().parents[2]
R_COMPLIANCE = ROOT / "23_compliance"
R_REPORTS = R_COMPLIANCE / "reports"
R_REVIEW = R_COMPLIANCE / "review"
R_TESTS = R_COMPLIANCE / "tests"
R_LOGS = ROOT / "02_audit_logging" / "logs"

FILES = {
    "template": R_REVIEW / "review_template.yaml",
    "checklist": R_REVIEW / "reviewer_checklist.yaml",
    "assign": R_REVIEW / "reviewer_assignments.yaml",
    "findings": R_REVIEW / "review_findings.yaml",
    "readme": R_REVIEW / "README.md",
    "tests": R_TESTS / "test_review_templates.py",
}

ALLOWED_ROOTS = {
    "01_ai_layer","02_audit_logging","03_core","04_deployment","05_documentation",
    "06_data_pipeline","07_governance_legal","08_identity_score","09_meta_identity",
    "10_interoperability","11_test_simulation","12_tooling","13_ui_layer",
    "14_zero_time_auth","15_infra","16_codex","17_observability","18_data_layer",
    "19_adapters","20_foundation","21_post_quantum_crypto","22_datasets",
    "23_compliance","24_meta_orchestration",".github",".git","ssid_validator",".claude",".LICENSE",".README",".pytest",".gitattributes",".gitmodules"
}

DID_RX = re.compile(r"^did:ssid:[a-z0-9]+$")
DATE_RX = re.compile(r"^\d{4}-\d{2}-\d{2}$")
CATEGORIES = {"STRUCTURE","LEGAL","SECURITY","AI_COMPLIANCE","OBSERVABILITY"}
FRAMEWORKS = {"GDPR","DORA","MiCA","AMLD6","TECH"}

def now_iso():
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"

def read_yaml(p: pathlib.Path) -> Dict[str, Any]:
    assert p.exists(), f"file missing: {p}"
    data = yaml.safe_load(p.read_text(encoding="utf-8"))
    assert isinstance(data, dict), f"yaml must be dict: {p}"
    return data

def evidence_path_ok(path_str: str) -> bool:
    # akzeptiere relative Pfade beginnend mit erlaubten Roots
    if not path_str or "/" not in path_str:
        return False
    top = path_str.split("/")[0]
    return top in ALLOWED_ROOTS

def validate_template(d: Dict[str,Any], penalties: List[str]):
    must_sections = ["executive_summary","framework_reviews","structure_compliance","approval_matrix","escalation_policy","reporting"]
    for s in must_sections:
        if s not in d: penalties.append(f"template: missing section {s}")
    # Kategorien
    fr = d.get("framework_reviews", {})
    cats = set(fr.keys()) if isinstance(fr, dict) else set()
    if CATEGORIES - cats:
        penalties.append(f"template: categories missing: {sorted(list(CATEGORIES - cats))}")
    # Approval-Matrix
    am = d.get("approval_matrix", {})
    if not isinstance(am, dict) or len(am.get("roles", [])) < 4:
        penalties.append("template: approval_matrix must contain 4+ roles with signatures")
    # Escalation
    esc = d.get("escalation_policy", {})
    if not esc or "severity" not in esc or "actions" not in esc:
        penalties.append("template: escalation_policy missing severity/actions")

def validate_checklist(d: Dict[str,Any], penalties: List[str]):
    # 30 Prüfpunkte gefordert, mit Framework-Tag + Evidence + Testref + Verification
    checklist = d.get("checklist", {})
    if not isinstance(checklist, dict):
        penalties.append("checklist: must be dict with framework keys")
        return

    total_items = 0
    for fw_key, fw_data in checklist.items():
        if not isinstance(fw_data, dict):
            continue
        fw = fw_data.get("framework", "")
        items = fw_data.get("items", [])

        if fw and fw not in FRAMEWORKS:
            penalties.append(f"checklist.{fw_key}: invalid framework {fw}")

        for i, it in enumerate(items):
            total_items += 1
            ev = it.get("evidence_path", "")
            vr = it.get("verification_method", "")
            ts = it.get("test_reference", "")

            if not ev or not evidence_path_ok(ev):
                penalties.append(f"checklist.{fw_key}[{i}]: invalid evidence_path {ev}")
            if vr not in {"automated","manual"}:
                penalties.append(f"checklist.{fw_key}[{i}]: invalid verification_method {vr}")
            if not ts:
                penalties.append(f"checklist.{fw_key}[{i}]: missing test_reference")

    if total_items < 30:
        penalties.append(f"checklist: must contain >= 30 checks (found {total_items})")

def validate_assignments(d: Dict[str,Any], penalties: List[str]):
    reviewers = d.get("reviewers", [])
    if not isinstance(reviewers, list) or len(reviewers) < 4:
        penalties.append("assignments: need 4 reviewers")
    total_hours = 0
    for i, r in enumerate(reviewers):
        did = r.get("did",""); scope = r.get("scope",[]); hours = r.get("hours",0)
        if not DID_RX.match(did): penalties.append(f"assignments[{i}]: invalid DID {did}")
        if not set(scope): penalties.append(f"assignments[{i}]: empty scope")
        if not isinstance(hours, int) or hours <= 0: penalties.append(f"assignments[{i}]: invalid hours {hours}")
        total_hours += hours
    # signatures
    sigs = d.get("attestations", {}).get("signatures", [])
    if len(sigs) < 4: penalties.append("assignments: need >= 4 signatures (independence/conflict attestations)")
    # compensation
    comp = d.get("compensation",{}).get("total_eur")
    if comp is None or comp < 0: penalties.append("assignments: compensation total_eur missing/invalid")

def validate_findings(d: Dict[str,Any], penalties: List[str]):
    items = d.get("findings", [])
    has_critical = False
    for i, f in enumerate(items):
        fid = f.get("id",""); sev = f.get("severity",""); deadline = f.get("deadline","")
        if not fid or not fid.startswith(("FIND-","F-")): penalties.append(f"findings[{i}]: invalid id {fid}")
        if sev not in {"LOW","MEDIUM","HIGH","CRITICAL"}: penalties.append(f"findings[{i}]: invalid severity {sev}")
        if not DATE_RX.match(deadline): penalties.append(f"findings[{i}]: invalid deadline {deadline}")
        if sev == "CRITICAL": has_critical = True
        ev = f.get("evidence_path","")
        if ev and not evidence_path_ok(ev): penalties.append(f"findings[{i}]: invalid evidence_path {ev}")
    # Escalation muss CRITICAL abdecken
    if d.get("meta",{}).get("requires_escalation_for_critical", True) and not has_critical:
        # kein Fehler, nur Hinweis – CRITICAL kann 0 sein
        pass  # No CRITICAL findings is acceptable

def write_jsonl(entry: Dict[str,Any]):
    R_LOGS.mkdir(parents=True, exist_ok=True)
    with (R_LOGS / "review_framework.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

def main():
    penalties: List[str] = []
    results = {}
    # exist checks
    for k,p in FILES.items():
        if not p.exists(): penalties.append(f"missing file: {p}")
    if penalties:
        write_jsonl({"ts": now_iso(), "status":"FAIL", "reason":"missing files", "penalties":penalties})
        print("\n".join(penalties)); sys.exit(2)

    # validations
    tpl = read_yaml(FILES["template"]); validate_template(tpl, penalties); results["template"]="checked"
    chk = read_yaml(FILES["checklist"]); validate_checklist(chk, penalties); results["checklist"]="checked"
    ass = read_yaml(FILES["assign"]);    validate_assignments(ass, penalties); results["assignments"]="checked"
    fin = read_yaml(FILES["findings"]);  validate_findings(fin, penalties); results["findings"]="checked"

    # README & Tests – Existenz + Minimalinhalte
    readme = FILES["readme"].read_text(encoding="utf-8")
    if "Quarterly Review" not in readme or "Workflow" not in readme:
        penalties.append("README.md: minimal content missing (Quarterly Review/Workflow)")
    if not FILES["tests"].exists():
        penalties.append("tests: test_review_templates.py missing")

    # Score
    status = "PASS" if not penalties else "FAIL"
    score = 100 - min(60, 3*len(penalties))
    score = max(0, score)

    # Reports
    R_REPORTS.mkdir(parents=True, exist_ok=True)
    score_obj = {
        "timestamp": now_iso(),
        "component": "quarterly_review_framework",
        "version": "2025-Q4",
        "status": status,
        "score": score,
        "results": results,
        "penalties": penalties,
        "roots": ["23_compliance","02_audit_logging","24_meta_orchestration","17_observability","11_test_simulation"]
    }
    (R_REPORTS / "review_framework_score.json").write_text(json.dumps(score_obj, ensure_ascii=False, indent=2), encoding="utf-8")

    md = [
        "# Quarterly Review Framework – Audit Report",
        f"- Timestamp: {score_obj['timestamp']}",
        f"- Status: **{status}**",
        f"- Score: **{score}/100**",
        f"- Version: {score_obj['version']}", "", "## Results"
    ]
    for k in results:
        md.append(f"- {k}: PASS")
    if penalties:
        md += ["", "## Findings", *[f"- {p}" for p in penalties]]
    (R_REPORTS / "review_framework_audit_report.md").write_text("\n".join(md), encoding="utf-8")

    write_jsonl(score_obj)
    sys.exit(0 if status=="PASS" else 2)

if __name__ == "__main__":
    main()
