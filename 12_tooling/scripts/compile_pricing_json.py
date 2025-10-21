#!/usr/bin/env python3
import sys, json, yaml, pathlib

def main():
    if len(sys.argv) < 3:
        print("usage: compile_pricing_json.py <input_yaml> <output_json>", file=sys.stderr)
        sys.exit(2)
    inp = pathlib.Path(sys.argv[1])
    out = pathlib.Path(sys.argv[2])
    data = yaml.safe_load(inp.read_text(encoding="utf-8"))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"wrote {out}")
if __name__ == "__main__":
    main()
