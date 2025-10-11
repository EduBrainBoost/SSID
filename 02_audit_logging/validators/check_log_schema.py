from typing import Iterable, Dict

REQUIRED_KEYS = {"ts", "level", "message", "source", "hash"}

def validate_log_schema(records: Iterable[Dict]) -> Dict[str, object]:
    """Schema check for audit logs. Ensures required keys exist.
    Returns validity and list of offending record indices.
    """
    bad = []
    for i, r in enumerate(records):
        if not REQUIRED_KEYS.issubset(set(r.keys())):
            bad.append(i)
    return {"valid": len(bad) == 0, "bad_records": bad}
