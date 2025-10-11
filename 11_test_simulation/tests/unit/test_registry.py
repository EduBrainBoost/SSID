
import importlib.util
from pathlib import Path

def test_registry():
    module_path = Path(__file__).parents[3] / "24_meta_orchestration" / "src" / "registry_manifest_loader.py"
    spec = importlib.util.spec_from_file_location("registry_manifest_loader", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert isinstance(module.load_manifest("example.yaml"), dict)
