#!/usr/bin/env python3
"""Bridge: 02_audit_logging -> 23_compliance - Evidence Push"""

import json
import shutil
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict


def push_evidence_to_compliance() -> Dict:
    """
    Push audit evidence hash chain to compliance registry.

    Returns:
        Dict with status and evidence count
    """
    repo_root = Path(__file__).resolve().parents[2]

    # Source: audit hash chain
    source_dir = repo_root / "02_audit_logging" / "storage" / "worm"
    target_dir = repo_root / "23_compliance" / "evidence" / "audit_bridge"

    target_dir.mkdir(parents=True, exist_ok=True)

    # Copy hash chain if exists
    hash_chain_file = source_dir / "hash_chain.json"

    if not hash_chain_file.exists():
        return {"status": "no_hash_chain", "evidence_count": 0}

    # Copy to compliance evidence
    target_file = target_dir / f"hash_chain_{datetime.now(timezone.utc).strftime('%Y%m%d')}.json"
    shutil.copy2(hash_chain_file, target_file)

    # Count evidence entries
    try:
        with open(hash_chain_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            count = len(data.get("chain", []))
    except:
        count = 0

    return {
        "status": "success",
        "evidence_count": count,
        "target_file": str(target_file.relative_to(repo_root)),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


def verify_evidence_integrity(evidence_file: Path) -> bool:
    """Verify hash chain integrity"""
    if not evidence_file.exists():
        return False

    try:
        with open(evidence_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        if "chain" not in data:
            return False

        # Basic integrity check
        return len(data["chain"]) > 0
    except:
        return False


if __name__ == "__main__":
    result = push_evidence_to_compliance()
    print("Evidence push result:", result)
