
#!/usr/bin/env python3
import os, sys, json, subprocess, argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(prog="ssid-meta", description="SSID Meta Orchestrator CLI")
    parser.add_argument("--boot", action="store_true", help="Boot & integrity checks")
    parser.add_argument("--run", action="store_true", help="Run pipelines")
    parser.add_argument("--status", action="store_true", help="Print global status")
    parser.add_argument("--repair", action="store_true", help="Self-healing repair mode (needs governance flag)")
    args = parser.parse_args()

    repo_root = os.environ.get("SSID_REPO_ROOT", os.getcwd())
    orch = Path(repo_root) / "24_meta_orchestration" / "meta_orchestrator.py"
    if not orch.exists():
        print("meta_orchestrator.py not found", file=sys.stderr)
        sys.exit(2)

    env = os.environ.copy()
    env["SSID_REPO_ROOT"] = str(repo_root)

    if args.boot:
        subprocess.check_call([sys.executable, str(orch)], env=env)
    elif args.run:
        subprocess.check_call([sys.executable, str(orch)], env=env)
    elif args.status:
        state = Path(repo_root) / "24_meta_orchestration" / "meta_state_matrix.json"
        if not state.exists():
            print("No state. Run --boot first.", file=sys.stderr); sys.exit(1)
        print(state.read_text(encoding="utf-8"))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
