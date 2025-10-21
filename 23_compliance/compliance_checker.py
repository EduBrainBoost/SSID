import json
def check(action: str, payload: dict) -> None:
    dump = json.dumps(payload).lower()
    assert 'pii' not in dump, 'pii_detected'
