import os, importlib.util

def test_scoring_logic_import():
    path = os.path.abspath('12_tooling/cli/sot_audit_verifier.py')
    spec = importlib.util.spec_from_file_location('sot_audit_verifier', path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert hasattr(mod, 'main')
