import hashlib
from typing import List, Dict

def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def validate_hash_chain(chain: List[Dict]) -> Dict[str, object]:
    """Validate a simple append-only hash chain of log entries.
    Each entry must include: index, payload, prev_hash, hash.
    The first entry's prev_hash must be 'GENESIS'.
    """
    errors = []
    if not chain:
        return {"valid": False, "errors": ["empty-chain"]}
    for i, entry in enumerate(chain):
        idx = entry.get("index")
        payload = entry.get("payload", "")
        prev = entry.get("prev_hash")
        h = entry.get("hash")
        if i == 0:
            if prev != "GENESIS":
                errors.append(f"index {idx}: bad-genesis-prev")
        else:
            if prev != chain[i-1].get("hash"):
                errors.append(f"index {idx}: prev-mismatch")
        if h != sha256_text(f"{idx}|{prev}|{payload}"):
            errors.append(f"index {idx}: hash-mismatch")
    return {"valid": len(errors) == 0, "errors": errors}
