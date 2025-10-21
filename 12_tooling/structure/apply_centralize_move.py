#!/usr/bin/env python3
# PLAN→APPROVAL→APPLY for structure corrections; non-destructive by default.
import argparse, json, pathlib, sys

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan-only", action="store_true")
    ap.add_argument("--from-report", default="02_audit_logging/reports/structure_guard_report.json")
    ap.add_argument("--evidence-out", default="02_audit_logging/reports/centralize_move_plan.json")
    args = ap.parse_args()

    rpt = json.loads(pathlib.Path(args.from_report).read_text(encoding="utf-8"))
    plan = {"moves": [], "timestamp": None, "status":"PLAN"}
    for v in rpt.get("violations", []):
        if v.get("type")=="root_violation":
            plan["moves"].append({"action":"CENTRALIZE_MOVE","path":v["path"],"target_root":"23_compliance"})
    plan["timestamp"] = __import__("time").strftime("%Y-%m-%dT%H:%M:%SZ", __import__("time").gmtime())
    pathlib.Path(args.evidence_out).write_text(json.dumps(plan, indent=2), encoding="utf-8")
    print("[centralize_move] plan created:", args.evidence_out)
    if not args.plan_only:
        print("[centralize_move] APPROVAL REQUIRED – not applying automatically")
        sys.exit(3)

if __name__=="__main__":
    main()
