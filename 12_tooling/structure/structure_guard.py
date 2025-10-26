#!/usr/bin/env python3
import sys, argparse, json, pathlib, re
import yaml

ALLOWED_ROOTS = [
 "01_ai_layer","02_audit_logging","03_core","04_deployment","05_documentation",
 "06_data_pipeline","07_governance_legal","08_identity_score","09_meta_identity",
 "10_interoperability","11_test_simulation","12_tooling","13_ui_layer",
 "14_zero_time_auth","15_infra","16_codex","17_observability","18_data_layer",
 "19_adapters","20_foundation","21_post_quantum_crypto","22_datasets",
 "23_compliance","24_meta_orchestration",".github",".git",".gitattributes",
 ".gitmodules",".gitignore","LICENSE","README.md",".claude","ssid_validator",
 ".pytest",".pytest_cache",".coverage","__pycache__",".venv","venv",
 "pytest.ini",".ssid_cache"
]

PLACEHOLDER_PATTERNS = re.compile(r"\b(TODO|FIXME|PLACEHOLDER|STUB|MOCK|XXX)\b", re.I)

def load_policy(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def scan(repo: pathlib.Path, cfg: dict):
    violations = []
    files_info = []
    for p in repo.rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(repo).as_posix()
        root = rel.split("/",1)[0]
        if root not in ALLOWED_ROOTS:
            violations.append({"type":"root_violation","path":rel,"msg":"outside Root-24"})
        if p.suffix in (".py",".rego",".ts",".sh",".yml",".yaml"):
            txt = p.read_text("utf-8", errors="ignore")
            if PLACEHOLDER_PATTERNS.search(txt):
                files_info.append({"path":rel,"placeholder":True})
            else:
                files_info.append({"path":rel,"placeholder":False})
    # SoT presence check per root
    required = ["chart.yaml","manifest.yaml"]
    missing_sot = []
    for r in [d for d in ALLOWED_ROOTS if re.match(r"^\d{2}_", d or "")]:
        root_dir = repo / r
        if root_dir.exists() and root_dir.is_dir():
            for req in required:
                if not (root_dir / req).exists():
                    missing_sot.append({"type":"sot_missing","root":r,"file":req})
    return violations, files_info, missing_sot

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--policy", required=True)
    ap.add_argument("--report", required=True)
    ap.add_argument("--emit-opa-input", default="02_audit_logging/reports/structure_guard_input.json")
    args = ap.parse_args()

    repo = pathlib.Path(".").resolve()
    cfg = load_policy(args.policy)
    violations, files_info, missing_sot = scan(repo, cfg)

    report = {
        "status":"PASS" if not violations and not missing_sot else "FAIL",
        "violations": violations + missing_sot,
        "files": files_info
    }
    pathlib.Path(args.report).parent.mkdir(parents=True, exist_ok=True)
    with open(args.report,"w",encoding="utf-8") as f: json.dump(report, f, indent=2)

    # Minimal OPA input
    opa_input = {
        "allowed_roots": [r for r in ALLOWED_ROOTS if re.match(r"^\d{2}_", r) or r.startswith(".")],
        "files": [{"path": f["path"]} for f in files_info],
        "violations": report["violations"]
    }
    with open(args.emit_opa_input,"w",encoding="utf-8") as f: json.dump(opa_input, f, indent=2)

    print(f"[structure_guard] status={report['status']} violations={len(report['violations'])}")
    sys.exit(0 if report["status"]=="PASS" else 2)

if __name__ == "__main__":
    main()
