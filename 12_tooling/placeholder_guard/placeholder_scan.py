import sys, re, json, fnmatch, os
from typing import List, Dict

PATTERNS = [
    (re.compile(r"\bTODO\b"), "TODO"),
    (re.compile(r"^\s*pass\s*$"), "pass-line"),
    (re.compile(r"\bassert\s+True\b"), "assert-true"),
]

def load_allowlist(path: str) -> List[str]:
    try:
        import yaml
    except ImportError:
        return []
    import yaml as _yaml
    with open(path, "r", encoding="utf-8") as f:
        data = _yaml.safe_load(f) or {}
    return data.get("allowed", [])

def is_allowed(path: str, allowlist: List[str]) -> bool:
    for pat in allowlist:
        if fnmatch.fnmatch(path.replace('\\','/'), pat):
            return True
    return False

def scan(root: str, allowlist_file: str = None) -> Dict[str, List[Dict[str, str]]]:
    allowlist = load_allowlist(allowlist_file) if allowlist_file and os.path.exists(allowlist_file) else []
    findings = []
    for dirpath, _, filenames in os.walk(root):
        for fn in filenames:
            if fn.endswith((".py", ".md", ".yaml", ".yml", ".sh")):
                fpath = os.path.join(dirpath, fn)
                rel = os.path.relpath(fpath, root)
                if is_allowed(rel, allowlist):
                    continue
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        for i, line in enumerate(f, start=1):
                            for rx, tag in PATTERNS:
                                if rx.search(line):
                                    findings.append({"file": rel, "line": i, "tag": tag, "snippet": line.strip()})
                except Exception as e:
                    findings.append({"file": rel, "line": 0, "tag": "read-error", "snippet": str(e)})
    return {"findings": findings}

def main():
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    allow = sys.argv[2] if len(sys.argv) > 2 else "12_tooling/placeholder_guard/allowlist_paths.yaml"
    res = scan(root, allow)
    has_findings = len(res["findings"]) > 0
    # Use ensure_ascii=True for Windows compatibility
    print(json.dumps(res, ensure_ascii=True, indent=2))
    sys.exit(1 if has_findings else 0)

if __name__ == "__main__":
    main()
