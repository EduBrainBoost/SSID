import math, yaml
from typing import Dict

def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))

def compute_identity_score(profile: Dict, weights_cfg_path: str) -> int:
    """Compute a 0..100 identity trust score from a profile dict and weights.yaml.
    No placeholders; deterministic math only.
    Expected profile keys:
      - kyc_verified (bool)
      - credential_count (int)
      - reputation_score (0..1 float)
      - compliance_flags (0..1 float)  # higher is better
      - activity_score (0..1 float)
      - sanctions_hit (bool)
      - fraud_suspected (bool)
    """
    with open(weights_cfg_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    W = cfg["weights"]; scale = cfg.get("scale", 100)
    bounds = cfg.get("bounds", {}); pen = cfg.get("penalties", {})
    cred_max = max(1, int(bounds.get("credential_count_max", 20)))
    kyc = 1.0 if profile.get("kyc_verified", False) else 0.0
    cred = _clamp(profile.get("credential_count", 0) / cred_max, 0.0, 1.0)
    rep = _clamp(float(profile.get("reputation_score", 0.0)), 0.0, 1.0)
    comp = _clamp(float(profile.get("compliance_flags", 0.0)), 0.0, 1.0)
    act = _clamp(float(profile.get("activity_score", 0.0)), 0.0, 1.0)
    base = (
        W["kyc_verified"] * kyc +
        W["credential_count"] * cred +
        W["reputation_score"] * rep +
        W["compliance_flags"] * comp +
        W["activity_score"] * act
    ) * scale
    # penalties
    if profile.get("sanctions_hit", False):
        base += cfg["penalties"].get("sanctions_hit", -40)
    if profile.get("fraud_suspected", False):
        base += cfg["penalties"].get("fraud_suspected", -20)
    return int(_clamp(round(base), 0, 100))
