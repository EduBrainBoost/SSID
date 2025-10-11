
import importlib.util
from pathlib import Path

def test_compliance():
    module_path = Path(__file__).parents[3] / "23_compliance" / "src" / "policy_engine.py"
    spec = importlib.util.spec_from_file_location("policy_engine", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.check_policy("sample") == True
