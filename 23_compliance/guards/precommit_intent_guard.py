
#!/usr/bin/env python3
import os, sys, subprocess
MANIFEST = "24_meta_orchestration/registry/artifact_intent_manifest.yaml"
TRACKER  = "12_tooling/tools/intent_coverage_tracker.py"
def run(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)
def main():
    if not os.path.exists(TRACKER):
        print("[intent-guard] tracker missing", file=sys.stderr)
        sys.exit(1)
    r = run(f'python "{TRACKER}" --manifest "{MANIFEST}" --fail-on-missing')
    if r.returncode != 0:
        print(r.stdout); print(r.stderr, file=sys.stderr)
        sys.exit(r.returncode)
    print("[intent-guard] ok")
if __name__ == "__main__":
    main()
