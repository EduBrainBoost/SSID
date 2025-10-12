#!/usr/bin/env python3
# 03_core/simulation/layer9_proof_aggregator.py
import json, hashlib, argparse, sys, os

def sha512_hex(b: bytes) -> str:
  return hashlib.sha512(b).hexdigest()

def aggregate_layer9(proofs_layer8, trust_weights, global_epoch_id):
  ecosystems = sorted(set([p['ecosystem'] for p in proofs_layer8]))
  if len(ecosystems) < 2:
    raise ValueError("Min Ecosystems not met (>=2).")
  concat = ""
  for p in proofs_layer8:
    eco = p['ecosystem']; hv = p['hash']; tw = float(trust_weights.get(eco, 1.0))
    reps = max(1, int(round(tw * 10)))
    concat += (hv + "|" + eco + "|") * reps
  concat += f"epoch:{global_epoch_id}"
  return sha512_hex(concat.encode('utf-8'))

def threshold_check(approvals, threshold_pct=0.85):
  if not approvals: return False
  approved = sum(1 for a in approvals if a is True)
  return (approved / len(approvals)) >= threshold_pct

def main():
  ap = argparse.ArgumentParser()
  ap.add_argument("--input", required=True, help="JSON: proofs_layer8, trust_weights, global_epoch_id, approvals")
  ap.add_argument("--out", required=True, help="Output JSON")
  ap.add_argument("--readiness", required=False, help="Path to 02_audit_logging/reports/layer_readiness_score.json")
  ap.add_argument("--gate_threshold", default="0.90", help="Required avg readiness (default 0.90)")
  args = ap.parse_args()

  with open(args.input, "r", encoding="utf-8") as f:
    data = json.load(f)

  # Optional readiness gate
  gate_pass = True
  need = float(args.gate_threshold)
  readiness_val = None
  if args.readiness and os.path.isfile(args.readiness):
    with open(args.readiness, "r", encoding="utf-8") as f:
      rj = json.load(f)
    readiness_val = float(rj.get("avg_score", 0.0))
    gate_pass = (readiness_val >= need) and (rj.get("status") == "PASS")

  l9 = aggregate_layer9(data["proofs_layer8"], data["trust_weights"], data["global_epoch_id"])
  ok = threshold_check(data.get("approvals", []), threshold_pct=0.85)

  out = {
    "layer9_root": l9,
    "threshold_pass": ok,
    "gate_threshold": need,
    "readiness_avg": readiness_val,
    "gate_pass_l1_8": gate_pass
  }
  with open(args.out, "w", encoding="utf-8") as f:
    json.dump(out, f, indent=2)
  print(l9)
  print(f"THRESHOLD_PASS={ok}; GATE_PASS_L1_8={gate_pass}; READINESS={readiness_val}")

if __name__ == "__main__":
  main()
