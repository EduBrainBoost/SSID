import json, os, time, hashlib
LOG = os.path.join(os.path.dirname(__file__), 'logs', 'marketplace_events.jsonl')
os.makedirs(os.path.dirname(LOG), exist_ok=True)
def write_event(evt: dict):
    evt = dict(evt)
    evt.setdefault('ts', int(time.time()))
    evt.setdefault('event_hash', hashlib.sha256(json.dumps(evt, sort_keys=True).encode('utf-8')).hexdigest())
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(json.dumps(evt, sort_keys=True) + "\n")
