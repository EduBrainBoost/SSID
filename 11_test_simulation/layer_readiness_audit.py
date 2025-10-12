#!/usr/bin/env python3
# 11_test_simulation/layer_readiness_audit.py
import os, sys, json, hashlib, datetime, argparse, yaml

def load_yaml(p):
  with open(p, 'r', encoding='utf-8') as f:
    return yaml.safe_load(f)

def check_paths(root, paths):
  missing = []
  for p in paths:
    fp = os.path.join(root, p)
    if not (os.path.isdir(fp) or os.path.isfile(fp)):
      missing.append(p)
  return missing

def any_exists(root, paths):
  for p in paths:
    fp = os.path.join(root, p)
    if os.path.isdir(fp) or os.path.isfile(fp):
      return True
  return False

def score_layer(missing, has_any, w):
  ex_score = 1.0 if not missing else 1.0 - min(1.0, len(missing)/max(1,len(missing)+1))
  any_score = 1.0 if has_any else 0.0
  return w['existence']*ex_score + w['contents']*any_score

def main():
  ap = argparse.ArgumentParser()
  ap.add_argument('--project-root', required=True)
  ap.add_argument('--policy', default='02_audit_logging/config/layer_readiness_policy.yaml')
  ap.add_argument('--out-dir', default='02_audit_logging/reports')
  args = ap.parse_args()

  root = args.project_root
  policy = load_yaml(os.path.join(root, args.policy))
  ts = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
  weights = policy['scoring']['weights']
  pass_threshold = float(policy['scoring']['pass_threshold'])

  sot_missing = []
  for v in policy['sot_paths'].values():
    if not os.path.isfile(os.path.join(root, v)):
      sot_missing.append(v)

  results, total = [], 0.0
  for layer_key, req in policy['layers_1_8_requirements'].items():
    missing = check_paths(root, req.get('must_exist', []))
    has_any = any_exists(root, req.get('must_contain_any', []))
    sc = score_layer(missing, has_any, weights)
    results.append({'layer': layer_key, 'missing': missing, 'has_any': has_any, 'score': round(sc,4)})
    total += sc

  avg = total / max(1, len(results))
  status = 'PASS' if (avg >= pass_threshold and not sot_missing) else 'FAIL'

  out_dir = os.path.join(root, args.out_dir)
  os.makedirs(out_dir, exist_ok=True)
  score_json = {
    'timestamp_utc': ts,
    'project_root': root,
    'sot_missing': sot_missing,
    'layer_results': results,
    'avg_score': round(avg,4),
    'pass_threshold': pass_threshold,
    'status': status
  }
  json_path = os.path.join(out_dir, 'layer_readiness_score.json')
  with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(score_json, f, indent=2, ensure_ascii=False)

  md_path = os.path.join(out_dir, 'layer_readiness_audit_report.md')
  with open(md_path, 'w', encoding='utf-8') as f:
    f.write("# Layer 1–8 Readiness Audit\n")
    f.write(f"- Timestamp (UTC): {ts}\n")
    f.write(f"- Project Root: `{root}`\n")
    f.write(f"- Status: **{status}**\n")
    f.write(f"- Average Score: **{avg:.4f}** (threshold {pass_threshold})\n\n")
    f.write("## SoT Presence\n")
    if sot_missing:
      f.write("- Missing SoT files:\n" + "\n".join([f"  - {m}" for m in sot_missing]) + "\n\n")
    else:
      f.write("- All SoT files present.\n\n")
    f.write("## Layer Results\n")
    for r in results:
      f.write(f"### {r['layer']}\n- score: **{r['score']:.4f}**\n- has_any_required_content: **{r['has_any']}**\n")
      if r['missing']:
        f.write("- missing:\n" + "\n".join([f"  - {m}" for m in r['missing']]) + "\n\n")
      else:
        f.write("- missing: none\n\n")

  print(f"STATUS={status}; AVG_SCORE={avg:.4f}")
  print(json_path)
  print(md_path)

if __name__ == '__main__':
  main()
