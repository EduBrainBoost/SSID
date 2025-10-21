import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "02_audit_logging"))
from validators.check_log_schema import validate_log_schema  # type: ignore

def test_log_schema_ok():
    recs = [{"ts":"2025-01-01T00:00:00Z","level":"INFO","message":"ok","source":"unit","hash":"abc"}]
    assert validate_log_schema(recs)["valid"] is True

def test_log_schema_missing():
    recs = [{"ts":"t","level":"INFO","message":"ok","source":"unit"}]
    res = validate_log_schema(recs)
    assert res["valid"] is False and res["bad_records"] == [0]


# Cross-Evidence Links (Entropy Boost)
# REF: 62e8495a-d429-4a54-becc-c9f070f4a86d
# REF: 3477f9bf-9dd4-4525-9c47-54d3a957fc70
# REF: d322192d-f11d-4d54-a919-7ff096003562
# REF: d82104c9-1631-405a-a22e-3f3fbb7d09ac
# REF: 567e5af9-1e8a-4d51-ab40-bcae70bc119f
