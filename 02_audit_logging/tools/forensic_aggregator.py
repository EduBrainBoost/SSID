#!/usr/bin/env python3
"""
SSID Forensic Integrity Aggregator (PROMPT 8)
Combines all integrity dimensions into master score with 1.0 cap logic.
Exit 0: master >= 0.93, Exit 1: below threshold
"""
import json, sys, uuid
from pathlib import Path
from datetime import datetime

REPO_ROOT = Path(__file__).resolve().parents[2]
REPORTS_DIR = REPO_ROOT / "02_audit_logging/reports"
OUTPUT_PATH = REPORTS_DIR / "forensic_integrity_matrix.json"

CAP_THRESHOLDS = {"structural_integrity": 0.99, "authenticity_rate": 0.99, "resilience": 0.70, "vector_magnitude": 0.90}
MASTER_THRESHOLD = 0.93

def load_report(path): 
    if not path.exists(): return {}
    try: return json.loads(path.read_text())
    except: return {}

def extract_metrics():
    truth = load_report(REPORTS_DIR / "truth_vector_analysis.json")
    auth = load_report(REPORTS_DIR / "score_authenticity_strict.json")
    entropy = load_report(REPORTS_DIR / "trust_entropy_analysis.json")
    return {
        "structural_integrity": truth.get("truth_vector", {}).get("x", 0.0),
        "content_integrity_y": truth.get("truth_vector", {}).get("y", 0.0),
        "temporal_coherence_z": truth.get("truth_vector", {}).get("z", 0.0),
        "vector_magnitude": truth.get("magnitude", 0.0),
        "authenticity_rate": auth.get("authenticity_rate", 0.0),
        "resilience": entropy.get("resilience", entropy.get("resilience_index", {}).get("value", 0.0))
    }

def check_cap_conditions(m):
    conds = {k: m.get(k, 0.0) >= CAP_THRESHOLDS[k] for k in CAP_THRESHOLDS}
    return all(conds.values()), conds

def calculate_master_score(m):
    all_met, conds = check_cap_conditions(m)
    if all_met: return 1.0, "PLATINUM-Forensic", True
    weights = {"structural_integrity": 0.25, "authenticity_rate": 0.30, "resilience": 0.20, "vector_magnitude": 0.25}
    master = sum(m.get(k, 0.0) * w for k, w in weights.items())
    grade = "PLATINUM-Forensic" if master>=0.96 else "PLATINUM" if master>=0.93 else "GOLD" if master>=0.85 else "SILVER"
    return master, grade, False

def main():
    print("="*80 + "\nSSID Forensic Integrity Aggregator\n" + "="*80)
    m = extract_metrics()
    print("[*] Metrics:\n" + "\n".join(f"    {k}: {v:.4f}" for k,v in m.items()))
    master, grade, capped = calculate_master_score(m)
    print(f"\n[*] Master Score: {master:.4f}\n[*] Grade: {grade}")
    if capped: print("[*] CAPPED at 1.0 (all conditions met)")
    all_met, conds = check_cap_conditions(m)
    report = {"aggregation_id": str(uuid.uuid4()), "timestamp": datetime.now().isoformat()+"Z", "master_score": round(master,6), "grade": grade, "capped": capped, "metrics": {k:round(v,6) for k,v in m.items()}, "cap_conditions": {"all_met": all_met, "conditions": conds, "thresholds": CAP_THRESHOLDS}, "certification": {"level": grade, "score": f"{int(master*100)}/100", "status": "PASS" if master>=MASTER_THRESHOLD else "FAIL"}}
    OUTPUT_PATH.write_text(json.dumps(report, indent=2))
    print(f"\n{'='*80}\nCertification: {grade} ({report['certification']['score']})\nReport: {OUTPUT_PATH.relative_to(REPO_ROOT)}\n{'='*80}")
    return 0 if master>=MASTER_THRESHOLD else 1

if __name__ == "__main__": sys.exit(main())
