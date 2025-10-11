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
