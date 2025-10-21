from __future__ import annotations
def interop_call(op: str, payload: dict) -> dict:
    if op == 'attest_performance':
        return {'status': 'ok', 'proof': 'att-ok-'+str(len(str(payload)))}
    return {'status': 'noop'}
