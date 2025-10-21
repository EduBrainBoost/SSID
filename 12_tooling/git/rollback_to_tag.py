#!/usr/bin/env python3
# Read-only safety check for rollback feasibility
import argparse, subprocess, sys

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True)
    ap.add_argument("--check-only", action="store_true")
    args = ap.parse_args()
    try:
        out = subprocess.check_output(["git","rev-parse","--verify", f"refs/tags/{args.tag}"], text=True).strip()
        print(f"[rollback] tag {args.tag} resolves to {out}")
        if not args.check_only:
            print("To rollback non-destructively, create a branch:")
            print(f"  git switch -c restore/{args.tag} {args.tag}")
    except subprocess.CalledProcessError:
        print(f"[rollback] tag not found: {args.tag}", file=sys.stderr)
        sys.exit(2)

if __name__=="__main__":
    main()
