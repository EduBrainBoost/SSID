#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Register SoT Artefacts in Registry
===================================

Registers the 5 critical SoT artefacts in sot_registry.json

Version: 1.0.0
Date: 2025-10-24
"""

import sys
import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone

REPO_ROOT = Path(__file__).parent.parent

ARTEFACTS = [
    {
        "name": "sot_contract.yaml",
        "path": REPO_ROOT / "16_codex" / "contracts" / "sot" / "sot_contract.yaml",
        "type": "contract"
    },
    {
        "name": "sot_policy.rego",
        "path": REPO_ROOT / "23_compliance" / "policies" / "sot" / "sot_policy.rego",
        "type": "policy"
    },
    {
        "name": "sot_validator_core.py",
        "path": REPO_ROOT / "03_core" / "validators" / "sot" / "sot_validator_engine.py",
        "type": "validator"
    },
    {
        "name": "sot_validator.py",
        "path": REPO_ROOT / "12_tooling" / "cli" / "sot_validator.py",
        "type": "cli"
    },
    {
        "name": "test_sot_validator.py",
        "path": REPO_ROOT / "11_test_simulation" / "tests_compliance" / "test_sot_validator.py",
        "type": "test"
    }
]

def compute_hash(file_path: Path) -> str:
    """Compute SHA-256 hash"""
    try:
        with open(file_path, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()
    except:
        return ""

def main():
    """Register all SoT artefacts"""
    registry_path = REPO_ROOT / "24_meta_orchestration" / "registry" / "sot_registry.json"

    # Load registry
    if registry_path.exists():
        with open(registry_path, 'r', encoding='utf-8') as f:
            registry = json.load(f)
    else:
        registry = {"artifacts": [], "rules": []}

    if "artifacts" not in registry:
        registry["artifacts"] = []

    # Register each artefact
    for artefact in ARTEFACTS:
        if not artefact["path"].exists():
            print(f"[SKIP] {artefact['name']} - File not found")
            continue

        # Check if already registered
        existing = None
        for a in registry["artifacts"]:
            if isinstance(a, dict) and a.get("name") == artefact["name"]:
                existing = a
                break

        hash_value = compute_hash(artefact["path"])

        if existing:
            # Update hash
            existing["hash"] = hash_value
            existing["updated_at"] = datetime.now(timezone.utc).isoformat()
            print(f"[UPDATE] {artefact['name']} - Hash updated")
        else:
            # Add new
            registry["artifacts"].append({
                "name": artefact["name"],
                "type": artefact["type"],
                "path": str(artefact["path"].relative_to(REPO_ROOT)),
                "hash": hash_value,
                "registered_at": datetime.now(timezone.utc).isoformat(),
                "status": "active"
            })
            print(f"[ADD] {artefact['name']} - Registered")

    # Save registry
    with open(registry_path, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2)

    print(f"\n[SUCCESS] Registry updated: {len(registry['artifacts'])} artifacts registered")
    return 0

if __name__ == "__main__":
    sys.exit(main())
