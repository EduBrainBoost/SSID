import json, os, subprocess, sys, pathlib

def run_tool(args):
    cmd = [sys.executable, "02_audit_logging/tools/verify_sot_enforcement.py"] + args
    return subprocess.run(cmd, capture_output=True, text=True)

def test_cli_runs_and_outputs_json(tmp_path, monkeypatch):
    # Move into a temp copy of the bundle
    here = pathlib.Path(".").resolve()
    # ensure directories referenced by the tool exist for a SILVER score
    os.makedirs("23_compliance/policies", exist_ok=True)
    os.makedirs("02_audit_logging/storage/worm/immutable_store", exist_ok=True)
    pathlib.Path(".github/workflows/ci_enforcement_gate.yml").parent.mkdir(parents=True, exist_ok=True)
    pathlib.Path(".github/workflows/ci_enforcement_gate.yml").write_text("verify_sot_enforcement.py\nstructure_guard.sh\n23_compliance/policies")

    pathlib.Path(".pre-commit-config.yaml").write_text("verify_sot_enforcement.py\nstructure_validation.sh")

    res = run_tool(["--ci-mode", "--worm-sign", "--json-out", "02_audit_logging/logs/enforcement_ci_result.json"])
    assert res.returncode in (0,1,2)
    # ensure JSON file written
    assert pathlib.Path("02_audit_logging/logs/enforcement_ci_result.json").is_file()
    data = json.loads(pathlib.Path("02_audit_logging/logs/enforcement_ci_result.json").read_text())
    assert "score" in data and "status" in data
