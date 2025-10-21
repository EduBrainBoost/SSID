from __future__ import annotations
def compute_market_fees(price_wei: int) -> dict:
    dao = price_wei * 2 // 100
    dev = price_wei * 1 // 100
    return {'dao': dao, 'developer': dev, 'total': dao + dev}
