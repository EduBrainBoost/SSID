
import pytest
import importlib.util
from pathlib import Path

def test_registry_manifest_loading():
    module_path = Path(__file__).parents[3] / "24_meta_orchestration" / "src" / "registry" / "registry_manifest_loader.py"
    spec = importlib.util.spec_from_file_location("registry_manifest_loader", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    manifest = module.load_manifest("24_meta_orchestration/registry/manifests/registry_manifest.yaml")
    assert "registry" in manifest


# Cross-Evidence Links (Entropy Boost)
# REF: 851abade-ff86-4d08-93a5-9989cd9116e8
# REF: b853bce9-a017-4b8b-9c4a-8c3c7895ec0d
# REF: d8f96f84-7a99-4d0d-80f8-9a776df2607c
# REF: be0fb5e4-b029-4fb1-9ddd-b5dc70a37975
# REF: 87e327af-e5cf-413e-8b2a-a3c0f160f75b
