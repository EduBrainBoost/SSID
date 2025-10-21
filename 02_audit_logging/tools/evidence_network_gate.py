#!/usr/bin/env python3
"""
SSID Evidence Network Gate (PROMPT 7)
Enforces minimum cross-evidence network integrity:
- Mutual Information >= 10 bits
- Graph Density >= 0.12
- Average Degree >= 10

Exit 0: PASS, Exit 2: FAIL
"""
import json
import sys
from pathlib import Path
from datetime import datetime
import uuid

REPO_ROOT = Path(__file__).resolve().parents[2]
GRAPH_PATH = REPO_ROOT / "02_audit_logging/reports/cross_evidence_graph.json"
REPORT_PATH = REPO_ROOT / "02_audit_logging/reports/evidence_network_gate.json"

# Thresholds
MIN_MUTUAL_INFORMATION = 10.0  # bits
MIN_GRAPH_DENSITY = 0.12
MIN_AVG_DEGREE = 10.0

def load_cross_evidence_graph():
    """Load cross-evidence graph analysis."""
    if not GRAPH_PATH.exists():
        return None

    with open(GRAPH_PATH, 'r') as f:
        return json.load(f)

def check_network_integrity(graph_data):
    """Check network meets minimum thresholds."""
    results = {
        "gate_id": str(uuid.uuid4()),
        "timestamp": datetime.now().isoformat() + "Z",
        "thresholds": {
            "min_mutual_information_bits": MIN_MUTUAL_INFORMATION,
            "min_graph_density": MIN_GRAPH_DENSITY,
            "min_avg_degree": MIN_AVG_DEGREE
        },
        "actual_values": {},
        "checks": [],
        "status": "UNKNOWN"
    }

    if not graph_data:
        results["status"] = "ERROR"
        results["error"] = "cross_evidence_graph.json not found"
        return results

    # Extract actual values
    mi_bits = graph_data.get("mutual_information_bits", 0)
    density = graph_data.get("graph_density", 0)
    avg_degree = graph_data.get("avg_degree", 0)

    results["actual_values"] = {
        "mutual_information_bits": mi_bits,
        "graph_density": density,
        "avg_degree": avg_degree
    }

    # Check 1: Mutual Information
    mi_check = {
        "check": "mutual_information",
        "threshold": MIN_MUTUAL_INFORMATION,
        "actual": mi_bits,
        "pass": mi_bits >= MIN_MUTUAL_INFORMATION
    }
    if not mi_check["pass"]:
        mi_check["recommendation"] = "Increase UUID cross-references in audit logs; add policy tags to evidence files"
    results["checks"].append(mi_check)

    # Check 2: Graph Density
    density_check = {
        "check": "graph_density",
        "threshold": MIN_GRAPH_DENSITY,
        "actual": density,
        "pass": density >= MIN_GRAPH_DENSITY
    }
    if not density_check["pass"]:
        density_check["recommendation"] = "Create more interconnections between evidence artifacts; use evidence_linker.py"
    results["checks"].append(density_check)

    # Check 3: Average Degree
    degree_check = {
        "check": "avg_degree",
        "threshold": MIN_AVG_DEGREE,
        "actual": avg_degree,
        "pass": avg_degree >= MIN_AVG_DEGREE
    }
    if not degree_check["pass"]:
        degree_check["recommendation"] = "Ensure each artifact references at least 10 other artifacts"
    results["checks"].append(degree_check)

    # Overall status
    all_pass = all(c["pass"] for c in results["checks"])
    results["status"] = "PASS" if all_pass else "FAIL"

    return results

def main():
    """Main gate execution."""
    print("=" * 80)
    print("SSID Evidence Network Gate")
    print("=" * 80)

    graph_data = load_cross_evidence_graph()

    if not graph_data:
        print("[!] ERROR: cross_evidence_graph.json not found")
        print(f"    Expected at: {GRAPH_PATH.relative_to(REPO_ROOT)}")
        return 2

    print(f"[+] Loaded: {GRAPH_PATH.relative_to(REPO_ROOT)}")

    results = check_network_integrity(graph_data)

    # Display checks
    print("\nIntegrity Checks:")
    print("-" * 80)
    for check in results["checks"]:
        status = "[PASS]" if check["pass"] else "[FAIL]"
        print(f"{status} {check['check']}: {check['actual']:.4f} (threshold: {check['threshold']:.4f})")
        if not check["pass"] and "recommendation" in check:
            print(f"       Recommendation: {check['recommendation']}")

    # Write report
    with open(REPORT_PATH, 'w') as f:
        json.dump(results, f, indent=2)

    print("\n" + "=" * 80)
    print(f"Status: {results['status']}")
    print(f"Report: {REPORT_PATH.relative_to(REPO_ROOT)}")
    print("=" * 80)

    return 0 if results["status"] == "PASS" else 2

if __name__ == "__main__":
    sys.exit(main())
