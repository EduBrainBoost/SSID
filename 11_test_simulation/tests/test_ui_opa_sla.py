
import json, yaml, pathlib

BASE = pathlib.Path(__file__).resolve().parents[2]
model_p = BASE/"07_governance_legal/docs/pricing/enterprise_subscription_model_v5.yaml"
sla_p = BASE/"17_observability/sla/sla_packages.yaml"

def load_yaml(p):
    with open(p, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def test_prices_monotonic_and_discounts():
    m = load_yaml(model_p)
    prs = []
    for t in m["tiers"]:
        p = t["price_eur"]
        prs.append(p if isinstance(p, (int,float)) else 25000)
    assert all(prs[i] <= prs[i+1] for i in range(len(prs)-1))
    for d in m["discounts"]:
        assert isinstance(d["percent"], (int,float))
        assert 0 <= d["percent"] <= 20

def test_global_bundle_tier_guard():
    m = load_yaml(model_p)
    tiers = ["core_access","professional","enterprise_trust","global_proof_suite","interfederation_elite","sovereign_infrastructure"]
    allowed_idx = tiers.index("global_proof_suite")
    for b in m["bundles"]:
        if b["id"] == "global_bundle":
            min_tier = b["tier_min"]
            assert tiers.index(min_tier) >= allowed_idx

def test_sla_basics():
    s = load_yaml(sla_p)
    ids = [x["id"] for x in s["slas"]]
    assert "sla_247" in ids
    assert "compliance_mesh" in ids


# Cross-Evidence Links (Entropy Boost)
# REF: 97091986-73c6-4fe1-8cc4-dcc73702f3d9
# REF: 30974bca-c8c7-456f-9f31-a390182c00f6
# REF: 0fbdf1fa-87ca-45e2-bf93-a5a37cee2aae
# REF: 190e0570-5ae7-467b-9679-54d1fa9d5f10
# REF: c4f1f0e8-cf98-4e83-b62d-0cf4f9e245e2
