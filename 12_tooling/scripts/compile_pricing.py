#!/usr/bin/env python3
import sys, json, yaml, argparse, pathlib

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", dest="out", required=True)
    args = ap.parse_args()
    src = pathlib.Path(args.inp)
    dst = pathlib.Path(args.out)
    with open(src, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    dst.parent.mkdir(parents=True, exist_ok=True)
    with open(dst, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Wrote JSON: {dst}")

if __name__ == "__main__":
    main()
