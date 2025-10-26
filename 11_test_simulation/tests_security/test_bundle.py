
import os, sys, subprocess, json, pathlib

REPO_ROOT = os.environ.get("SSID_REPO_ROOT", os.getcwd())

def p(*parts): return str(pathlib.Path(REPO_ROOT).joinpath(*parts))

def test_threat_scan_runs(monkeypatch):
    monkeypatch.setenv("SSID_REPO_ROOT", REPO_ROOT)
    r = subprocess.run([sys.executable, p("12_tooling","cli","security_cli.py"), "--threat-scan"],
                       capture_output=True, text=True)
    assert r.returncode == 0
    assert "positives" in r.stdout

def test_integrity_monitor_runs(monkeypatch):
    monkeypatch.setenv("SSID_REPO_ROOT", REPO_ROOT)
    r = subprocess.run([sys.executable, p("12_tooling","cli","security_cli.py"), "--integrity"],
                       capture_output=True, text=True)
    assert r.returncode == 0
    assert "drift" in r.stdout

def test_backup_daemon_runs(monkeypatch):
    monkeypatch.setenv("SSID_REPO_ROOT", REPO_ROOT)
    r = subprocess.run([sys.executable, p("12_tooling","cli","security_cli.py"), "--backup"],
                       capture_output=True, text=True)
    assert r.returncode == 0
    # Should print JSON with {"ok": true/false}
    assert "ok" in r.stdout.lower()
