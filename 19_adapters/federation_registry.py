#!/usr/bin/env python3
"""
Blueprint v4.8 - Federation Registry

Manages known federation nodes with public keys, DIDs, endpoints, and trust scores.
Provides node discovery, registration, and heartbeat tracking.

Exit Codes:
  0 - Operation successful
  1 - Node not found
  2 - Invalid node data
  3 - Trust score below threshold
"""

import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional

REGISTRY_DIR = Path("24_meta_orchestration/registry")
FEDERATION_REGISTRY_PATH = REGISTRY_DIR / "federation_registry.json"

def load_registry() -> Dict:
    """Load federation registry"""
    if FEDERATION_REGISTRY_PATH.exists():
        with open(FEDERATION_REGISTRY_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "registry_version": "1.0.0",
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "nodes": []
    }

def save_registry(registry: Dict) -> None:
    """Save federation registry"""
    REGISTRY_DIR.mkdir(parents=True, exist_ok=True)
    registry["last_updated"] = datetime.now(timezone.utc).isoformat()
    with open(FEDERATION_REGISTRY_PATH, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)

def add_node(node_id: str, public_key: str, did: str, endpoint: str, initial_trust: int = 75) -> Dict:
    """Add new node to registry"""
    registry = load_registry()

    node_entry = {
        "node_id": node_id,
        "public_key": public_key,
        "did": did,
        "endpoint": endpoint,
        "trust_score": initial_trust,
        "status": "ACTIVE",
        "registered_at": datetime.now(timezone.utc).isoformat(),
        "last_heartbeat": None,
        "total_heartbeats": 0,
        "last_proof_sync": None
    }

    registry["nodes"].append(node_entry)
    save_registry(registry)
    print(f"[SUCCESS] Node {node_id} registered")
    return node_entry

def update_heartbeat(node_id: str) -> bool:
    """Update node heartbeat timestamp"""
    registry = load_registry()

    for node in registry["nodes"]:
        if node["node_id"] == node_id:
            node["last_heartbeat"] = datetime.now(timezone.utc).isoformat()
            node["total_heartbeats"] = node.get("total_heartbeats", 0) + 1
            save_registry(registry)
            print(f"[HEARTBEAT] Node {node_id} updated")
            return True

    print(f"[ERROR] Node {node_id} not found")
    return False

def get_active_nodes(min_trust_score: int = 50) -> List[Dict]:
    """Get list of active nodes above trust threshold"""
    registry = load_registry()
    active_nodes = [
        node for node in registry["nodes"]
        if node["status"] == "ACTIVE" and node["trust_score"] >= min_trust_score
    ]
    return active_nodes

def main():
    print("=" * 70)
    print("Blueprint v4.8 - Federation Registry")
    print("=" * 70)

    # Example: List active nodes
    active_nodes = get_active_nodes()
    print(f"\n[INFO] Active nodes: {len(active_nodes)}")

    for node in active_nodes:
        print(f"  - {node['node_id']}: trust={node['trust_score']}, heartbeats={node['total_heartbeats']}")

    sys.exit(0)

if __name__ == "__main__":
    main()
