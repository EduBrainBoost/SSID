import json, re, sys
from pathlib import Path
from importlib.machinery import SourceFileLoader

def load_mod(tmp_path: Path):
    mod_path = Path(__file__).resolve().parents[2] / "12_tooling" / "maintenance" / "apply_hygiene_patch.py"
    return SourceFileLoader("apply_hygiene_patch", str(mod_path)).load_module()

def test_idempotent_patch(tmp_path: Path):
    mod = load_mod(tmp_path)
    (tmp_path / "02_audit_logging" / "reports").mkdir(parents=True, exist_ok=True)
    (tmp_path / "24_meta_orchestration" / "registry").mkdir(parents=True, exist_ok=True)
    (tmp_path / "13_ui_layer" / "assets" / "badges").mkdir(parents=True, exist_ok=True)
    (tmp_path / "02_audit_logging" / "logs").mkdir(parents=True, exist_ok=True)
    (tmp_path / "02_audit_logging" / "reports" / "test_hygiene_certificate_v1.md").write_text("# TEST HYGIENE CERTIFICATE v1.0\n", encoding="utf-8")
    (tmp_path / "24_meta_orchestration" / "registry" / "test_hygiene_certificate.yaml").write_text("", encoding="utf-8")
    (tmp_path / "13_ui_layer" / "assets" / "badges" / "test_hygiene_badge.svg").write_text("<svg><text>CERTIFIED 100/100</text></svg>", encoding="utf-8")
    params = dict(cert_id="SSID-TH-2025-10-15-001", valid_from="2025-10-15", valid_to="2026-10-15", cert_hash="ef6a26061246349e4a495b71246d33f624dcb8cdb96fe31eb1e12fad7720094e", alg_label="Dilithium2", backend="placeholder-hmac-sha256")
    diff1 = mod.patch_repo(tmp_path, params, dry_run=False)
    diff2 = mod.patch_repo(tmp_path, params, dry_run=False)
    assert all(not c["changed"] for c in diff2["changes"]), diff2
    md = (tmp_path / "02_audit_logging" / "reports" / "test_hygiene_certificate_v1.md").read_text(encoding="utf-8")
    assert "Certificate ID: SSID-TH-2025-10-15-001" in md
    assert "Validity: 2025-10-15" in md and "2026-10-15" in md
    assert "ef6a26061246349e4a495b71246d33f624dcb8cdb96fe31eb1e12fad7720094e" in md
    assert "PRODUCTION SEALED" in md

def test_dry_run_diff(tmp_path: Path):
    mod = load_mod(tmp_path)
    params = dict(cert_id="X", valid_from="2025-01-01", valid_to="2026-01-01", cert_hash="a"*64, alg_label="Dilithium2", backend="placeholder")
    diff = mod.patch_repo(tmp_path, params, dry_run=True)
    assert any(c["changed"] for c in diff["changes"])
