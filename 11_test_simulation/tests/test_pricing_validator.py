import json, subprocess, sys, pathlib

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.returncode, r.stdout.strip()

def test_pricing_validator_pass():
    base = pathlib.Path(__file__).resolve().parents[2]
    model = base / "07_governance_legal" / "docs" / "pricing" / "enterprise_subscription_model_v5_2.yaml"
    tool = base / "11_test_simulation" / "tools" / "pricing_validator.py"
    code, out = run([sys.executable, str(tool), str(model)])
    assert code == 0, out
    data = json.loads(out)
    assert data["status"] == "PASS"

def test_pricing_validator_fail_when_thresholds_low(tmp_path):
    bad = tmp_path / "bad.yaml"
    bad.write_text("""apiVersion: ssid/v1
kind: EnterpriseSubscriptionModel
spec:
  revenue_bands:
    S2_prime_eur: 1000000
    S3_prime_eur: 3000000
""", encoding="utf-8")
    base = pathlib.Path(__file__).resolve().parents[2]
    tool = base / "11_test_simulation" / "tools" / "pricing_validator.py"
    code, out = run([sys.executable, str(tool), str(bad)])
    assert code != 0
    data = json.loads(out)
    assert data["status"] == "FAIL"
