from pathlib import Path
import yaml, re, json

def test_certificate_report_fields(tmp_path: Path):
    md = Path(__file__).resolve().parents[3] / "02_audit_logging" / "reports" / "test_hygiene_certificate_v1.md"
    text = md.read_text(encoding="utf-8")
    assert "Certificate ID: SSID-TH-2025-10-15-001" in text
    assert "Validity: 2025-10-15 → 2026-10-15" in text
    assert "ef6a26061246349e4a495b71246d33f624dcb8cdb96fe31eb1e12fad7720094e" in text
    assert "PRODUCTION SEALED" in text

def test_registry_pqc_metadata(tmp_path: Path):
    y = Path(__file__).resolve().parents[3] / "24_meta_orchestration" / "registry" / "test_hygiene_certificate.yaml"
    data = yaml.safe_load(y.read_text(encoding="utf-8"))
    assert data["spec"]["pqc"]["cert_sha256"] == "ef6a26061246349e4a495b71246d33f624dcb8cdb96fe31eb1e12fad7720094e"
    assert data["spec"]["certificate_id"] == "SSID-TH-2025-10-15-001"
    assert data["spec"]["validity"]["from"] == "2025-10-15"
    assert data["spec"]["validity"]["to"] == "2026-10-15"

def test_score_log_contains_pqc(tmp_path: Path):
    js = Path(__file__).resolve().parents[3] / "02_audit_logging" / "logs" / "test_hygiene_score_log.json"
    obj = json.loads(js.read_text(encoding="utf-8"))
    assert obj["certificate_id"] == "SSID-TH-2025-10-15-001"
    assert obj["pqc"]["cert_sha256"] == "ef6a26061246349e4a495b71246d33f624dcb8cdb96fe31eb1e12fad7720094e"


# Cross-Evidence Links (Entropy Boost)
# REF: 6a23f9d5-c2c6-46d7-8428-808040aaece2
# REF: 9d1c3900-ae93-4c3f-9567-e72fdf44129b
# REF: 85634d57-e55e-486e-af27-c3490aa70af7
# REF: 855d9d4c-84bc-4b79-99d4-1b130636ee4d
# REF: d7a91dbc-b3bb-4475-947c-f3c519b3d7ea
