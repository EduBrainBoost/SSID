
import json, os, subprocess, sys, pathlib

REPO_ROOT = os.environ.get("SSID_REPO_ROOT", os.getcwd())

def run_cli(*args):
    cli = pathlib.Path(REPO_ROOT) / "12_tooling" / "cli" / "meta_cli.py"
    cmd = [sys.executable, str(cli)] + list(args)
    return subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True, check=False)

def test_boot_and_state_created(tmp_path, monkeypatch):
    # Point to sandbox repo
    monkeypatch.setenv("SSID_REPO_ROOT", REPO_ROOT)
    r = run_cli("--boot")
    assert r.returncode == 0
    state_path = pathlib.Path(REPO_ROOT) / "24_meta_orchestration" / "meta_state_matrix.json"
    assert state_path.exists()
    data = json.loads(state_path.read_text(encoding="utf-8"))
    assert "global_score" in data

def test_validator_accepts_state(monkeypatch):
    monkeypatch.setenv("SSID_REPO_ROOT", REPO_ROOT)
    state_path = pathlib.Path(REPO_ROOT) / "24_meta_orchestration" / "meta_state_matrix.json"
    if not state_path.exists():
        run_cli("--boot")
    vmod = pathlib.Path(REPO_ROOT) / "03_core" / "validators" / "meta_state_validator.py"
    r = subprocess.run([sys.executable, str(vmod), str(state_path)], capture_output=True, text=True)
    assert r.returncode == 0
    assert "OK" in r.stdout

def test_run_pipelines_updates_scorecard(monkeypatch):
    monkeypatch.setenv("SSID_REPO_ROOT", REPO_ROOT)
    run_cli("--boot")
    # run pipelines by invoking orchestrator directly (it's the same code path)
    orch = pathlib.Path(REPO_ROOT) / "24_meta_orchestration" / "meta_orchestrator.py"
    r = subprocess.run([sys.executable, str(orch)], capture_output=True, text=True)
    assert r.returncode == 0
    scorecard = pathlib.Path(REPO_ROOT) / "24_meta_orchestration" / "meta_global_scorecard.md"
    assert scorecard.exists()
    assert "Global Score" in scorecard.read_text(encoding="utf-8")
