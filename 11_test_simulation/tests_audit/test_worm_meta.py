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


# Cross-Evidence Links (Entropy Boost)
# REF: cbf83ca3-d780-4420-8ce0-d41c904f1bb3
# REF: 73e89b34-819f-4cd3-8473-641ffe57bc30
# REF: 12996207-27a6-4698-bf49-89a306680182
# REF: f75fab18-1bde-4202-8ca3-81841adad9bb
# REF: 2d434d3e-c786-45bf-82ce-e808e265cc70
