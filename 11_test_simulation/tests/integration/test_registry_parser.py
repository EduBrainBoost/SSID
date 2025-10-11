
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
