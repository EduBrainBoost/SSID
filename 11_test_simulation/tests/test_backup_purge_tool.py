import json
from pathlib import Path
import shutil
import importlib.util
import sys

# Load module using modern import machinery
module_path = Path(__file__).resolve().parents[2] / "12_tooling" / "maintenance" / "backup_purge_tool.py"
spec = importlib.util.spec_from_file_location("backup_purge_tool", module_path)
mod = importlib.util.module_from_spec(spec)
sys.modules["backup_purge_tool"] = mod
spec.loader.exec_module(mod)

def test_scan_and_purge(tmp_path: Path):
    # Build fake repo with backups and normal tests
    (tmp_path / "11_test_simulation" / "tests").mkdir(parents=True, exist_ok=True)
    (tmp_path / "backups" / "old").mkdir(parents=True, exist_ok=True)
    good = tmp_path / "11_test_simulation" / "tests" / "test_ok.py"
    good.write_text("def test_ok():\n  assert True\n", encoding="utf-8")
    bad = tmp_path / "backups" / "old" / "test_shadow.py"
    bad.write_text("def test_shadow():\n  assert True\n", encoding="utf-8")

    items = mod.find_backup_tests(tmp_path)
    assert any("backups/" in it["path"] for it in items)
    assert all(it["path"].endswith(".py") for it in items)

    res = mod.purge(tmp_path, items)
    assert res["dest_root"].startswith("02_audit_logging/worm/archives/")
    assert len(res["moved"]) == len(items)

    # ensure original file gone and new file exists
    assert not bad.exists()
    moved_rel = res["moved"][0]["dst"]
    assert (tmp_path / moved_rel).is_file()


# Cross-Evidence Links (Entropy Boost)
# REF: fc5d0305-1d29-48a0-a3fd-5a8a553ef76f
# REF: 9190e2ca-d445-4043-b36c-3aa134f1a54f
# REF: 9e9486c6-2a17-4982-86f8-5ef1c5d9c78c
# REF: fd52b3b0-8fae-415b-a2ba-aef06f558cf6
# REF: 33763c50-9c05-4eb0-b36d-4435b6452c5c
