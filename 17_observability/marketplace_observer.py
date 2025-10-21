from __future__ import annotations
import json
def export_metrics(audit_log_path: str):
    offers = trades = 0
    try:
        with open(audit_log_path, 'r', encoding='utf-8') as f:
            for line in f:
                evt = json.loads(line)
                if evt.get('type') == 'offer_listed': offers += 1
                elif evt.get('type') == 'trade_settled': trades += 1
    except FileNotFoundError:
        pass
    return {'offers_total': offers, 'trades_total': trades}
