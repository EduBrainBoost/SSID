from typing import Iterable, Dict

def verify_worm_meta(files_meta: Iterable[Dict]) -> Dict[str, object]:
    """WORM (Write Once Read Many) meta verification using provided metadata.
    Expects dicts with fields: path, immutable(bool), created_at, checksum.
    Returns validity and per-file issues. No filesystem writes performed.
    """
    issues = []
    for m in files_meta:
        if not m.get("immutable", False):
            issues.append({"path": m.get("path"), "error": "not-immutable"})
        if not m.get("checksum"):
            issues.append({"path": m.get("path"), "error": "missing-checksum"})
    return {"valid": len(issues) == 0, "issues": issues}
