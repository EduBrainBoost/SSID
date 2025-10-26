from pathlib import Path
import json, subprocess, os

ROOT = Path(r"C:\Users\bibel\Documents\Github\SSID")

def run(args):
    return subprocess.run(["python", str(ROOT/"12_tooling/agent/agent_cli.py")] + args,
                          capture_output=True, text=True, cwd=str(ROOT))

def test_fs_write_and_read_roundtrip():
    p = ROOT/"02_audit_logging/reports/agent_test_roundtrip.txt"
    w = run(["fs-write", str(p), "SSID_AGENT_OK"])
    assert w.returncode == 0, w.stderr
    r = run(["fs-read", str(p)])
    assert r.returncode == 0, r.stderr
    out = json.loads(r.stdout)
    assert out["text"] == "SSID_AGENT_OK"

def test_sh_whitelist():
    r = run(["sh", "python -V"])
    assert r.returncode == 0
    assert "Python" in r.stdout

def test_http_whitelist():
    r = run(["http-get", "https://docs.python.org/3/"])
    assert r.returncode == 0
    j = json.loads(r.stdout)
    assert j["status"] == 200
