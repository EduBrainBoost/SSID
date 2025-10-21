
#!/usr/bin/env python3
import sys, json, os, hashlib, argparse, time

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

def load_yaml(path):
    # improved YAML subset parser for key: value / list of scalars
    data = {"intents": []}
    with open(path, "r", encoding="utf-8") as f:
        lines = [l.rstrip("\n") for l in f]
    cur = None
    in_check_section = False
    keys_required_active = False

    for ln in lines:
        stripped = ln.strip()
        indent = len(ln) - len(ln.lstrip())

        # New intent starts
        if stripped.startswith("- id:"):
            cur = {"check":{}}
            cur["id"] = stripped.split(":", 1)[1].strip()
            data["intents"].append(cur)
            in_check_section = False
            keys_required_active = False
            continue

        if not cur:
            continue

        # Check if we're entering check section
        if stripped == "check:" and indent <= 4:
            in_check_section = True
            continue

        # Parse fields at intent level (not in check section)
        if not in_check_section:
            if "name:" in stripped:
                cur["name"] = stripped.split("name:", 1)[1].strip()
            elif "required:" in stripped:
                cur["required"] = "true" in stripped.lower()
            elif "root:" in stripped:
                cur["root"] = stripped.split("root:", 1)[1].strip().strip('"')
            elif "path:" in stripped:
                cur["path"] = stripped.split("path:", 1)[1].strip().strip('"')
        else:
            # Inside check section
            if "type:" in stripped:
                cur["check"]["type"] = stripped.split("type:", 1)[1].strip()
            elif "keys_required:" in stripped:
                cur["check"]["keys_required"] = []
                keys_required_active = True
            elif keys_required_active and stripped.startswith("- "):
                cur["check"]["keys_required"].append(stripped[2:].strip().strip('"'))
            elif stripped.startswith("tags:") or (indent <= 4 and ":" in stripped and not stripped.startswith("-")):
                # Exiting check section
                keys_required_active = False

    return data

def json_has_keys(path, keys):
    try:
        data = json.load(open(path,"r",encoding="utf-8"))
        return all(k in data for k in keys)
    except Exception:
        return False

def yaml_has_keys(path, keys):
    try:
        # naive: just check that each key token appears
        txt = open(path,"r",encoding="utf-8").read()
        return all((k + ":") in txt for k in keys)
    except Exception:
        return False

def verify_intent(intent):
    p = intent.get("path","")
    t = intent.get("check",{}).get("type","")
    if not os.path.exists(p):
        return False, f"missing:{p}"
    if t == "json_presence":
        keys = intent["check"].get("keys_required",[])
        return (json_has_keys(p, keys), "ok" if json_has_keys(p, keys) else "key-missing")
    if t == "yaml_presence":
        keys = intent["check"].get("keys_required",[])
        return (yaml_has_keys(p, keys), "ok" if yaml_has_keys(p, keys) else "key-missing")
    return True, "ok"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", default="24_meta_orchestration/registry/artifact_intent_manifest.yaml")
    ap.add_argument("--report-json", default="02_audit_logging/reports/intent_coverage_report.json")
    ap.add_argument("--report-md", default="02_audit_logging/reports/intent_coverage_report.md")
    ap.add_argument("--fail-on-missing", action="store_true")
    args = ap.parse_args()

    man = load_yaml(args.manifest)
    intents = man.get("intents", [])
    coverage, gaps = [], []
    for it in intents:
        ok, reason = verify_intent(it)
        rec = {
            "id": it.get("id"),
            "path": it.get("path"),
            "required": it.get("required", False),
            "status": "present" if ok else "missing",
            "reason": reason
        }
        coverage.append(rec)
        if not ok and rec["required"]:
            gaps.append(rec)
    summary = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "required_total": sum(1 for i in intents if i.get("required")),
        "required_present": sum(1 for r in coverage if r["required"] and r["status"]=="present"),
        "required_missing": sum(1 for r in coverage if r["required"] and r["status"]=="missing"),
    }
    os.makedirs(os.path.dirname(args.report_json), exist_ok=True)
    json.dump({"summary":summary,"coverage":coverage,"gaps":gaps}, open(args.report_json,"w",encoding="utf-8"), indent=2)
    open(args.report_md,"w",encoding="utf-8").write(
        f"# Intent Coverage Report\\n\\n- Required total: {summary['required_total']}\\n- Required present: {summary['required_present']}\\n- Required missing: {summary['required_missing']}\\n"
    )
    if args.fail_on_missing and gaps:
        sys.stderr.write(f"FAIL: {len(gaps)} required artifacts missing.\\n")
        sys.exit(2)
    print("OK")
if __name__ == "__main__":
    main()
