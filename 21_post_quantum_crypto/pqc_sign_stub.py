
# Placeholder for PQC signing (e.g., Dilithium3). Replace with real lib in production.
import hashlib, json

def pqc_sign(obj: dict, secret: str) -> dict:
    raw = json.dumps(obj, sort_keys=True).encode("utf-8")
    return {"alg":"DILITHIUM3-STUB","sig": hashlib.sha256(secret.encode()+raw).hexdigest()}
