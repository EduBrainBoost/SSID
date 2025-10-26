
#!/usr/bin/env python3
import os, sys, subprocess, json, argparse, pathlib

def main():
    p = argparse.ArgumentParser(prog="ssid-sec", description="Security Autonomy CLI")
    p.add_argument("--threat-scan", action="store_true")
    p.add_argument("--integrity", action="store_true")
    p.add_argument("--backup", action="store_true")
    args = p.parse_args()

    repo = os.environ.get("SSID_REPO_ROOT", os.getcwd())
    def run(mod):
        return subprocess.run([sys.executable, str(pathlib.Path(repo)/mod)], capture_output=True, text=True)

    if args.threat_scan:
        r = run("17_observability/threat_detection_engine.py"); print(r.stdout); sys.exit(r.returncode)
    if args.integrity:
        r = run("03_core/monitors/integrity_monitor.py"); print(r.stdout); sys.exit(r.returncode)
    if args.backup:
        r = run("15_infra/backup/backup_daemon.py"); print(r.stdout); sys.exit(r.returncode)

    p.print_help()

if __name__ == "__main__":
    main()
