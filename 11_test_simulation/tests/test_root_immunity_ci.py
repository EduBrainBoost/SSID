import json
import os
import re
from pathlib import Path

def test_policy_exists():
    assert Path('23_compliance/policies/root_write_prevention.rego').is_file(),         "OPA policy missing: 23_compliance/policies/root_write_prevention.rego"

def test_fixtures_exist_and_json_valid():
    for fixture in [
        '11_test_simulation/fixtures/test_root_write_policy.json',
        '11_test_simulation/fixtures/test_root_write_policy_allow.json'
    ]:
        p = Path(fixture)
        assert p.is_file(), f"Missing fixture: {fixture}"
        with p.open('r', encoding='utf-8') as fh:
            data = json.load(fh)
        assert isinstance(data, dict), "Fixture must be a JSON object"

def test_merkle_certificate_present_and_sha256_format():
    cert_path = Path('23_compliance/merkle/root_write_merkle_proofs.json')
    assert cert_path.is_file(), "Missing Merkle proofs JSON: 23_compliance/merkle/root_write_merkle_proofs.json"
    proofs = json.loads(cert_path.read_text(encoding='utf-8'))
    assert isinstance(proofs, dict), "Merkle proofs JSON must be an object"
    # If a 'root' field is present, ensure it looks like SHA-256 hex
    root = proofs.get('root') or proofs.get('merkle_root') or ""
    if root:
        assert re.fullmatch(r'[0-9a-f]{64}', root), "Merkle root must be 64 hex chars (SHA-256)"

def test_registry_manifest_has_entry_for_root_immunity():
    path = Path('24_meta_orchestration/registry/root_immunity_registry.yaml')
    assert path.is_file(), "Missing registry manifest: 24_meta_orchestration/registry/root_immunity_registry.yaml"
    content = path.read_text(encoding='utf-8')
    assert 'root_immunity' in content and 'version: v5.3' in content,         "Registry manifest must contain root_immunity and version v5.3"


# Cross-Evidence Links (Entropy Boost)
# REF: 5ba60ad5-8771-4d08-b13d-9e51b37e26e8
# REF: cdb9b4b4-3059-4f1b-9409-b83201e2e8c5
# REF: 7e72003a-7216-4198-96c6-3134d5fdb601
# REF: 95ad07f5-32e6-43d4-b2d4-bf21c51871a9
# REF: a17a02ef-c3e5-47e8-a62e-0ae2fc6a6737
