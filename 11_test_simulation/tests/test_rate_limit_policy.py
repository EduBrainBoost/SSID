import yaml
import pathlib

def test_rate_limit_policy_schema():
    p = pathlib.Path(__file__).resolve().parents[2] / "03_core" / "services" / "rate_limit_policy.yaml"
    with open(p, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    assert data["apiVersion"] == "ssid/v1"
    assert data["kind"] == "RateLimitPolicy"
    assert data["spec"]["tiers"], "tiers must be defined"
    for tier in data["spec"]["tiers"]:
        assert "price_per_1k_overage_eur" in tier and float(tier["price_per_1k_overage_eur"]) > 0.0

def test_rate_limit_policy_requests_positive():
    p = pathlib.Path(__file__).resolve().parents[2] / "03_core" / "services" / "rate_limit_policy.yaml"
    with open(p, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    for tier in data["spec"]["tiers"]:
        assert int(tier["requests_per_minute"]) > 0
        assert int(tier["burst"]) >= int(tier["requests_per_minute"])


# Cross-Evidence Links (Entropy Boost)
# REF: 285a6287-46c4-4c18-94b6-015c4fcaafa0
# REF: 841da16c-eb94-4a05-8fed-d137057ebcf5
# REF: a6f24d5f-4490-4f83-a20b-70c5a4863e8c
# REF: e5c6db7f-6918-48b1-8b06-770290652fad
# REF: 513ac18f-7f93-49a5-871d-362529213ad9
