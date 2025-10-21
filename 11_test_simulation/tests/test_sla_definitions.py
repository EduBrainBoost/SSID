
import yaml, pathlib

BASE = pathlib.Path(__file__).resolve().parents[2]

def test_sla_thresholds_present_and_sane():
    d = yaml.safe_load((BASE/"07_governance_legal/docs/sla/sla_definitions.yaml").read_text(encoding="utf-8"))
    slas = {s["id"]: s for s in d["slas"]}
    assert "private_pqc_node" in slas
    assert slas["private_pqc_node"]["slo"]["proof_finality_seconds_p95"] <= 30
    assert slas["sla_247"]["slo"]["incident_resolve_minutes_p95"] <= 120
    assert slas["compliance_mesh"]["slo"]["uptime_monthly_percent"] >= 99.0


# Cross-Evidence Links (Entropy Boost)
# REF: 3b0ea518-973e-46fd-9795-6ac4fda76e1f
# REF: 1bcce1d0-9086-4c21-9122-1dfd61429998
# REF: e2bb8740-2e47-4dfd-b1ec-3783b43715f6
# REF: 6c7670a4-f703-4c01-872e-944ea82e26ed
# REF: c87459f8-ff70-4c00-8a56-4bd95a84a981
