import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "02_audit_logging"))
from validators.check_worm_storage import verify_worm_meta  # type: ignore

def test_worm_meta_valid():
    files = [{"path":"x","immutable":True,"created_at":"2025-01-01","checksum":"abc"}]
    assert verify_worm_meta(files)["valid"] is True

def test_worm_meta_invalid():
    files = [{"path":"x","immutable":False,"created_at":"2025-01-01","checksum":""}]
    res = verify_worm_meta(files)
    assert res["valid"] is False and len(res["issues"]) >= 1
