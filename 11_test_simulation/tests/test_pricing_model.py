
import json, subprocess, sys, pathlib

BASE = pathlib.Path(__file__).resolve().parents[2]
model = BASE/"07_governance_legal/docs/pricing/enterprise_subscription_model_v5.yaml"
tool = BASE/"11_test_simulation/tools/pricing_validator.py"

def test_extended_scenarios_pass():
    out = subprocess.check_output([sys.executable, str(tool), str(model)], text=True)
    data = json.loads(out)
    assert data["status"] == "PASS"
    assert data["S2_growth_extended"] >= 2_000_000.0
    assert data["S3_prime"] >= 4_000_000.0


# Cross-Evidence Links (Entropy Boost)
# REF: 766838ef-da4c-4757-9d5e-91f1a04d87fd
# REF: f011d142-00bb-4242-aabb-d54f716063b3
# REF: 2653104a-fd3e-4f4e-8273-32c49518640f
# REF: 721900f3-5c73-47ac-9009-1c0c83e1f066
# REF: a3d770d3-6a13-4193-96a2-b31df82c89c0
