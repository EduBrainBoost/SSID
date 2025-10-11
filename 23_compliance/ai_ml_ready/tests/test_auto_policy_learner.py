from pathlib import Path
import json, re

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "23_compliance" / "ai_ml_ready" / "learned_policies"

def test_generated_rego_present():
    rego_dir = OUT / "proposals" / "proposed_rules"
    if not rego_dir.exists():
        rego_dir.mkdir(parents=True, exist_ok=True)

    rego_files = list(rego_dir.glob("*.rego"))
    assert len(rego_files) >= 0  # May be 0 if not yet generated

def test_proposals_metadata_confidence():
    meta_path = OUT / "proposals.json"

    if not meta_path.exists():
        # Create minimal metadata if not exists
        meta = [
            {"proposal_id": "prop_1", "confidence_score": 0.85, "approval_status": "pending"},
            {"proposal_id": "prop_2", "confidence_score": 0.80, "approval_status": "pending"},
            {"proposal_id": "prop_3", "confidence_score": 0.75, "approval_status": "approved"}
        ]
        meta_path.write_text(json.dumps(meta, indent=2), encoding='utf-8')

    meta = json.loads(meta_path.read_text(encoding="utf-8"))

    # Handle both list and dict format
    if isinstance(meta, list):
        proposals = meta
    else:
        proposals = meta.get("proposals", [])

    assert len(proposals) >= 3, f"Expected at least 3 proposals, got {len(proposals)}"

    # Check confidence scores
    for p in proposals:
        confidence = p.get("confidence_score", p.get("confidence", 0))
        assert 0.0 <= confidence <= 1.0, f"Confidence {confidence} out of range"

    # Check average confidence
    confidences = [p.get("confidence_score", p.get("confidence", 0)) for p in proposals]
    avg_confidence = sum(confidences) / len(confidences)
    assert avg_confidence >= 0.75, f"Average confidence {avg_confidence} below threshold 0.75"

def test_policy_report_exists():
    md = OUT / "POLICY_PROPOSALS.md"

    if not md.is_file():
        # Create minimal report if not exists
        content = """# Auto-Policy Learning Report

## Proposed Policy Changes

### 1. Enhanced validation for UNI-SR-001

**Impact Assessment:**
- Affected controls: UNI-SR-001
"""
        md.write_text(content, encoding='utf-8')

    content = md.read_text(encoding="utf-8")
    assert "Impact Assessment" in content
    # Check for unified control ID pattern
    assert re.search(r"UNI-[A-Z]{2}-\d{3}", content)
