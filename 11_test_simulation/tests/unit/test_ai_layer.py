
import importlib.util
from pathlib import Path

def test_ai_layer():
    module_path = Path(__file__).parents[3] / "01_ai_layer" / "src" / "example_module.py"
    spec = importlib.util.spec_from_file_location("example_module", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.example_function() == "✅ AI Layer OK"
