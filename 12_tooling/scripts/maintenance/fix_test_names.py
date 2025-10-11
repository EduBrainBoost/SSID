# fix_test_names.py
from pathlib import Path

test_base = Path("11_test_simulation")
for test_file in test_base.rglob("test_structure.py"):
    shard_name = test_file.parent.name  # z.B. "Shard_01_Identitaet_Personen"
    new_name = f"test_{shard_name.lower()}.py"
    test_file.rename(test_file.parent / new_name)
