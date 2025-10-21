#!/usr/bin/env python3
import json, os, subprocess, sys, fnmatch, pathlib

ROOTS = [f"{i:02d}" for i in range(1,25)] + [".github"]

def git_changed_files():
    # PR: diff to origin/main; fallback: last commit
    base = os.environ.get("GITHUB_BASE_REF") or "origin/main"
    try:
        out = subprocess.check_output(["git","diff","--name-status", base], text=True).strip().splitlines()
    except Exception:
        out = subprocess.check_output(["git","diff","--name-status","HEAD~1"], text=True).strip().splitlines()
    changed, new_count = [], 0
    for line in out:
        parts = line.split(maxsplit=1)
        if not parts:
            continue
        status, path = parts[0], parts[1]
        path = path.strip()
        if not any(path.startswith(r + "/") or path==r for r in ROOTS):
            continue
        changed.append(path)
        if status.upper().startswith("A"):  # Added
            new_count += 1
    return changed, new_count

def load_budget():
    p = pathlib.Path("24_meta_orchestration/registry/change_budget.yaml")
    if not p.exists():
        print("ERROR: change_budget.yaml missing", file=sys.stderr)
        sys.exit(3)
    # tiny yaml parser (no external deps): read naive
    import re
    txt = p.read_text(encoding="utf-8")
    allowed, forbidden, max_new = [], [], 8
    in_allowed, in_forbidden = False, False
    for line in txt.splitlines():
        s=line.strip()
        if s.startswith("allowed_paths:"):
            in_allowed, in_forbidden = True, False
        elif s.startswith("forbidden_globs:"):
            in_allowed, in_forbidden = False, True
        elif s.startswith("max_new_files_per_pr:"):
            max_new = int(s.split(":")[1].strip())
            in_allowed, in_forbidden = False, False
        elif s.startswith("- ") and (in_allowed or in_forbidden):
            val = s[2:].strip()
            # Remove inline comments
            if "#" in val:
                val = val.split("#")[0].strip()
            # Remove quotes
            val = val.strip('"').strip("'")
            if val:  # Only append non-empty values
                if in_allowed:
                    allowed.append(val)
                elif in_forbidden:
                    forbidden.append(val)
        elif s and not s.startswith("#") and ":" in s:
            # New section detected, reset flags
            in_allowed, in_forbidden = False, False
    return {"allowed_paths": allowed, "forbidden_globs": forbidden, "max_new_files_per_pr": max_new}

def main():
    changed, new_count = git_changed_files()
    budget = load_budget()
    opa_input = {"changed": changed, "budget": budget, "stats": {"new_files": new_count}}
    print(json.dumps(opa_input))
    # exit 0 here; OPA eval runs in CI step

if __name__ == "__main__":
    main()
