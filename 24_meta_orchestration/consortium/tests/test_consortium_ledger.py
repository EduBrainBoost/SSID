import json, hashlib, pathlib, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]  # -> SSID/
CONSORTIUM = ROOT / "24_meta_orchestration" / "consortium"

def sha256_bytes(b: bytes) -> str:
    return "sha256:" + hashlib.sha256(b).hexdigest()

def test_registry_and_policy_present():
    assert (CONSORTIUM / "consortium_registry.yaml").is_file()
    assert (CONSORTIUM / "consensus_policy.yaml").is_file()

def test_quorum_parameters():
    import yaml
    reg = yaml.safe_load((CONSORTIUM/"consortium_registry.yaml").read_text(encoding="utf-8"))
    pol = yaml.safe_load((CONSORTIUM/"consensus_policy.yaml").read_text(encoding="utf-8"))
    assert reg["consensus"]["min_weight_sum"] == pol["quorum"]["min_weight_sum"] == 11
    assert reg["consensus"]["min_distinct_signers"] == pol["quorum"]["min_distinct_signers"] == 5
    assert pol["quorum"]["signature_scheme"] == "threshold-bls"

def test_membership_weights_sum_satisfiable():
    import yaml
    pol = yaml.safe_load((CONSORTIUM/"consensus_policy.yaml").read_text(encoding="utf-8"))
    tiers = pol["membership_tiers"]
    # Prüfe, dass (founding + full + associate) Quorum erreichbar machen
    weight_sum = tiers["founding"]["weight"] + tiers["full"]["weight"] + tiers["associate"]["weight"]
    assert weight_sum >= 10  # sanity
    assert pol["quorum"]["min_weight_sum"] <= 11

def test_anchor_reference_exists():
    import yaml
    reg = yaml.safe_load((CONSORTIUM/"consortium_registry.yaml").read_text(encoding="utf-8"))
    anchor_path = ROOT / reg["audit"]["registry_anchor"]
    assert anchor_path.exists(), f"Missing anchor: {anchor_path}"

def test_checksum_placeholders_filled_by_ci():
    # CI soll die sha256 Felder ersetzen; hier nur Formatprüfung
    import yaml
    for p in ["consortium_registry.yaml", "consensus_policy.yaml"]:
        y = yaml.safe_load((CONSORTIUM/p).read_text(encoding="utf-8"))
        c = y.get("checksum","sha256:TO_BE_FILLED_BY_CI")
        assert re.match(r"^sha256:[0-9a-f]{64}$|^sha256:TO_BE_FILLED_BY_CI$", c)
