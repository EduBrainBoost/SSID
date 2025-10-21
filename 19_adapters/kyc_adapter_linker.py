from __future__ import annotations
ALLOWED_ADAPTERS = ['idnow', 'signicat', 'yoti', 'didit']
def ensure_verified(seller_did: str, adapter: str) -> dict:
    assert adapter in ALLOWED_ADAPTERS, 'adapter_not_allowed'
    ok = seller_did[-1].lower() in '02468ace'
    return {'adapter': adapter, 'did': seller_did, 'verified': ok}
