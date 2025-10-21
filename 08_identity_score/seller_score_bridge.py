from __future__ import annotations
import hashlib
def resolve_seller_reputation(did: str) -> dict:
    h = hashlib.sha256(did.encode('utf-8')).hexdigest()
    base = int(h[-2:], 16)  # 0..255
    score = 50 + (base % 51)  # 50..100
    return {'did': did, 'score': score, 'source': '08_identity_score'}
