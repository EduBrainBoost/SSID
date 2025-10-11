"""
Compliance Auditor REST API

Read-only REST API for external auditors to verify compliance evidence
without requiring repository access.

Version: 2025-Q4
Last Updated: 2025-10-07
Maintainer: edubrainboost
Classification: PUBLIC - External Auditor Interface
"""

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from flask import Flask, jsonify, request, Response
from flask_cors import CORS


app = Flask(__name__)
CORS(app)  # Enable CORS for external auditors

# Repository root
REPO_ROOT = Path(__file__).parent.parent

# Data paths
REGISTRY_ANCHOR_PATH = REPO_ROOT / "02_audit_logging/evidence/registry/registry_anchor.json"
BLOCKCHAIN_EVENTS_PATH = REPO_ROOT / "02_audit_logging/evidence/blockchain/compliance_events.jsonl"
UNIFIED_INDEX_PATH = REPO_ROOT / "23_compliance/mappings/compliance_unified_index.yaml"
MAPPINGS_DIR = REPO_ROOT / "23_compliance/mappings"
DASHBOARD_OUTPUT_PATH = REPO_ROOT / "13_ui_layer/compliance_dashboard_output.json"


# ============================================================================
# Health & Info Endpoints
# ============================================================================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "SSID Compliance Auditor API",
        "version": "2025-Q4",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    })


@app.route('/api/v1/info', methods=['GET'])
def api_info():
    """API information and available endpoints."""
    return jsonify({
        "api_version": "v1",
        "service": "SSID Compliance Auditor API",
        "description": "Read-only compliance evidence API for external auditors",
        "endpoints": {
            "health": "/health",
            "info": "/api/v1/info",
            "unified_index": "/api/v1/unified-index",
            "dashboard": "/api/v1/dashboard",
            "anchors": "/api/v1/anchors",
            "anchors_by_id": "/api/v1/anchors/<anchor_id>",
            "blockchain_events": "/api/v1/blockchain/events",
            "framework": "/api/v1/framework/<framework_name>",
            "verify_hash": "/api/v1/verify/<file_type>/<expected_hash>"
        },
        "authentication": "none (read-only public API)",
        "rate_limiting": "not implemented (recommended for production)"
    })


# ============================================================================
# Compliance Data Endpoints
# ============================================================================

@app.route('/api/v1/unified-index', methods=['GET'])
def get_unified_index():
    """
    Get the unified compliance index.

    Returns cross-framework mappings, control categories, and risk classifications.
    """
    if not UNIFIED_INDEX_PATH.exists():
        return jsonify({"error": "Unified index not found"}), 404

    try:
        with open(UNIFIED_INDEX_PATH, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        # Calculate file hash for verification
        with open(UNIFIED_INDEX_PATH, 'rb') as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()

        return jsonify({
            "data": data,
            "metadata": {
                "file_hash": f"sha256:{file_hash}",
                "file_path": "23_compliance/mappings/compliance_unified_index.yaml",
                "retrieved_at": datetime.utcnow().isoformat() + "Z"
            }
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/v1/dashboard', methods=['GET'])
def get_dashboard():
    """
    Get the latest compliance dashboard summary.

    Returns real-time compliance status for all frameworks.
    """
    if not DASHBOARD_OUTPUT_PATH.exists():
        return jsonify({"error": "Dashboard output not found. Run compliance_dashboard.py first."}), 404

    try:
        with open(DASHBOARD_OUTPUT_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return jsonify({
            "data": data,
            "metadata": {
                "retrieved_at": datetime.utcnow().isoformat() + "Z",
                "source": "13_ui_layer/compliance_dashboard_output.json"
            }
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/v1/anchors', methods=['GET'])
def get_anchors():
    """
    Get all compliance registry anchors.

    Query parameters:
    - limit: Number of anchors to return (default: all)
    - offset: Offset for pagination (default: 0)
    """
    if not REGISTRY_ANCHOR_PATH.exists():
        return jsonify({"error": "Registry anchors not found"}), 404

    try:
        with open(REGISTRY_ANCHOR_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)

        anchors = data.get("anchors", [])

        # Pagination
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', default=0, type=int)

        if limit:
            anchors = anchors[offset:offset + limit]
        elif offset:
            anchors = anchors[offset:]

        return jsonify({
            "anchors": anchors,
            "total_count": len(data.get("anchors", [])),
            "returned_count": len(anchors),
            "metadata": {
                "retrieved_at": datetime.utcnow().isoformat() + "Z",
                "source": "02_audit_logging/evidence/registry/registry_anchor.json"
            }
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/v1/anchors/<anchor_id>', methods=['GET'])
def get_anchor_by_id(anchor_id: str):
    """Get a specific anchor by ID."""
    if not REGISTRY_ANCHOR_PATH.exists():
        return jsonify({"error": "Registry anchors not found"}), 404

    try:
        with open(REGISTRY_ANCHOR_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)

        anchors = data.get("anchors", [])
        anchor = next((a for a in anchors if a.get("anchor_id") == anchor_id), None)

        if not anchor:
            return jsonify({"error": f"Anchor {anchor_id} not found"}), 404

        return jsonify({
            "anchor": anchor,
            "metadata": {
                "retrieved_at": datetime.utcnow().isoformat() + "Z"
            }
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/v1/blockchain/events', methods=['GET'])
def get_blockchain_events():
    """
    Get blockchain compliance events.

    Query parameters:
    - limit: Number of events to return (default: 100)
    - status: Filter by confirmation_status (pending|confirmed|finalized)
    """
    if not BLOCKCHAIN_EVENTS_PATH.exists():
        return jsonify({"error": "Blockchain events not found"}), 404

    try:
        events = []
        with open(BLOCKCHAIN_EVENTS_PATH, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    events.append(json.loads(line))

        # Filter by status if provided
        status_filter = request.args.get('status')
        if status_filter:
            events = [e for e in events if e.get('blockchain', {}).get('confirmation_status') == status_filter]

        # Limit results
        limit = request.args.get('limit', default=100, type=int)
        events = events[-limit:]  # Return most recent

        return jsonify({
            "events": events,
            "total_count": len(events),
            "metadata": {
                "retrieved_at": datetime.utcnow().isoformat() + "Z",
                "source": "02_audit_logging/evidence/blockchain/compliance_events.jsonl"
            }
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/v1/framework/<framework_name>', methods=['GET'])
def get_framework(framework_name: str):
    """
    Get specific framework mapping.

    Parameters:
    - framework_name: GDPR, DORA, MiCA, or AMLD6
    """
    framework_name = framework_name.upper()
    if framework_name not in ["GDPR", "DORA", "MICA", "AMLD6"]:
        return jsonify({"error": "Invalid framework name. Use GDPR, DORA, MiCA, or AMLD6"}), 400

    mapping_path = MAPPINGS_DIR / f"{framework_name.lower()}_mapping.yaml"

    if not mapping_path.exists():
        return jsonify({"error": f"Mapping for {framework_name} not found"}), 404

    try:
        with open(mapping_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        # Calculate file hash
        with open(mapping_path, 'rb') as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()

        return jsonify({
            "framework": framework_name,
            "data": data,
            "metadata": {
                "file_hash": f"sha256:{file_hash}",
                "file_path": f"23_compliance/mappings/{framework_name.lower()}_mapping.yaml",
                "retrieved_at": datetime.utcnow().isoformat() + "Z"
            }
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================================
# Verification Endpoints
# ============================================================================

@app.route('/api/v1/verify/<file_type>/<expected_hash>', methods=['GET'])
def verify_hash(file_type: str, expected_hash: str):
    """
    Verify file integrity by comparing hash.

    Parameters:
    - file_type: unified_index, gdpr, dora, mica, amld6, anchors
    - expected_hash: Expected SHA256 hash (with or without 'sha256:' prefix)
    """
    # Remove sha256: prefix if present
    if expected_hash.startswith("sha256:"):
        expected_hash = expected_hash[7:]

    # Map file type to path
    file_map = {
        "unified_index": UNIFIED_INDEX_PATH,
        "gdpr": MAPPINGS_DIR / "gdpr_mapping.yaml",
        "dora": MAPPINGS_DIR / "dora_mapping.yaml",
        "mica": MAPPINGS_DIR / "mica_mapping.yaml",
        "amld6": MAPPINGS_DIR / "amld6_mapping.yaml",
        "anchors": REGISTRY_ANCHOR_PATH
    }

    if file_type not in file_map:
        return jsonify({"error": f"Invalid file type. Use: {', '.join(file_map.keys())}"}), 400

    file_path = file_map[file_type]

    if not file_path.exists():
        return jsonify({"error": f"File not found: {file_type}"}), 404

    try:
        # Calculate actual hash
        with open(file_path, 'rb') as f:
            actual_hash = hashlib.sha256(f.read()).hexdigest()

        matches = actual_hash == expected_hash

        return jsonify({
            "file_type": file_type,
            "file_path": str(file_path.relative_to(REPO_ROOT)),
            "expected_hash": f"sha256:{expected_hash}",
            "actual_hash": f"sha256:{actual_hash}",
            "verified": matches,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/v1/verify/anchor/<anchor_id>', methods=['GET'])
def verify_anchor(anchor_id: str):
    """
    Verify a specific anchor's registry lock hash.

    Checks if the stored registry_lock_hash matches the actual registry_lock.yaml hash.
    """
    if not REGISTRY_ANCHOR_PATH.exists():
        return jsonify({"error": "Registry anchors not found"}), 404

    try:
        # Load anchor
        with open(REGISTRY_ANCHOR_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)

        anchor = next((a for a in data.get("anchors", []) if a.get("anchor_id") == anchor_id), None)

        if not anchor:
            return jsonify({"error": f"Anchor {anchor_id} not found"}), 404

        stored_hash = anchor.get("registry_lock_hash", "")
        if stored_hash.startswith("sha256:"):
            stored_hash = stored_hash[7:]

        # In production, you'd verify against the actual registry_lock.yaml at the time
        # For now, we acknowledge the limitation
        return jsonify({
            "anchor_id": anchor_id,
            "stored_hash": f"sha256:{stored_hash}",
            "verification_note": "Historical verification requires blockchain anchoring for full trustlessness",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================================
# Statistics Endpoints
# ============================================================================

@app.route('/api/v1/stats', methods=['GET'])
def get_statistics():
    """Get overall compliance statistics."""
    stats = {
        "frameworks": {
            "total": 4,
            "available": []
        },
        "anchors": {
            "total": 0,
            "latest": None
        },
        "blockchain_events": {
            "total": 0,
            "pending": 0,
            "confirmed": 0
        }
    }

    # Count frameworks
    for fw in ["gdpr", "dora", "mica", "amld6"]:
        if (MAPPINGS_DIR / f"{fw}_mapping.yaml").exists():
            stats["frameworks"]["available"].append(fw.upper())

    # Count anchors
    if REGISTRY_ANCHOR_PATH.exists():
        with open(REGISTRY_ANCHOR_PATH, 'r', encoding='utf-8') as f:
            anchor_data = json.load(f)
            anchors = anchor_data.get("anchors", [])
            stats["anchors"]["total"] = len(anchors)
            if anchors:
                stats["anchors"]["latest"] = anchors[-1].get("timestamp")

    # Count blockchain events
    if BLOCKCHAIN_EVENTS_PATH.exists():
        with open(BLOCKCHAIN_EVENTS_PATH, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    stats["blockchain_events"]["total"] += 1
                    event = json.loads(line)
                    status = event.get("blockchain", {}).get("confirmation_status")
                    if status == "pending":
                        stats["blockchain_events"]["pending"] += 1
                    elif status in ["confirmed", "finalized"]:
                        stats["blockchain_events"]["confirmed"] += 1

    return jsonify({
        "statistics": stats,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    })


# ============================================================================
# Main
# ============================================================================

def main():
    """Run the Flask development server."""
    print("\n" + "=" * 80)
    print("SSID Compliance Auditor API".center(80))
    print("=" * 80)
    print("\nStarting API server for external auditors...")
    print(f"Repository Root: {REPO_ROOT}")
    print("\nAvailable Endpoints:")
    print("  - http://localhost:5000/health")
    print("  - http://localhost:5000/api/v1/info")
    print("  - http://localhost:5000/api/v1/unified-index")
    print("  - http://localhost:5000/api/v1/dashboard")
    print("  - http://localhost:5000/api/v1/anchors")
    print("  - http://localhost:5000/api/v1/blockchain/events")
    print("  - http://localhost:5000/api/v1/framework/<framework_name>")
    print("  - http://localhost:5000/api/v1/verify/<file_type>/<hash>")
    print("  - http://localhost:5000/api/v1/stats")
    print("\n" + "=" * 80 + "\n")

    app.run(debug=True, host='0.0.0.0', port=5000)


if __name__ == '__main__':
    main()
