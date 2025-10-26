
import json, os, subprocess, sys, pathlib

REPO_ROOT = os.environ.get("SSID_REPO_ROOT", os.getcwd())

def p(*parts):
    return str(pathlib.Path(REPO_ROOT).joinpath(*parts))

def test_repair_mode_off(monkeypatch):
    monkeypatch.setenv("SSID_REPO_ROOT", REPO_ROOT)
    r = subprocess.run([sys.executable, p("12_tooling","cli","meta_cli.py"), "--repair"], capture_output=True, text=True)
    assert r.returncode == 0
    assert "repair not allowed" in r.stdout

def test_backup_snapshot(monkeypatch):
    monkeypatch.setenv("SSID_REPO_ROOT", REPO_ROOT)
    r = subprocess.run([sys.executable, p("15_infra","backup","backup_snapshot.py")], capture_output=True, text=True)
    assert r.returncode == 0
    meta = json.loads(r.stdout)
    assert "sha256" in meta and meta["path"].endswith(".tar.gz")

def test_malware_interface_writes_report(monkeypatch):
    monkeypatch.setenv("SSID_REPO_ROOT", REPO_ROOT)
    r = subprocess.run([sys.executable, p("12_tooling","security","malware_scan_interface.py")], capture_output=True, text=True)
    assert r.returncode == 0
    report = pathlib.Path(p("02_audit_logging","reports","MALWARE_SCAN.json"))
    assert report.exists()
