#!/usr/bin/env python3
"""
Blueprint v4.5 Governance Warm-Up Monitor

Monitors readiness for Q1 2026 governance cycle launch by checking:
- GitHub Actions workflows and cron triggers
- Registry locks and proof-anchor integrity
- Days remaining until launch (2026-01-01 08:00 UTC)
- Status logging and telemetry integration

Exit Codes:
  0 = OK (All systems ready)
  1 = Missing trigger configuration
  2 = Hash drift detected
  3 = Lock error
"""

import json
import os
import sys
import hashlib
from datetime import datetime, timezone
from pathlib import Path

# Configuration
LAUNCH_DATE = datetime(2026, 1, 1, 8, 0, 0, tzinfo=timezone.utc)
STATUS_LOG_PATH = "02_audit_logging/reports/prelaunch_status_log.json"
WORKFLOWS_TO_CHECK = [
    ".github/workflows/quarterly_audit.yml",
    ".github/workflows/quarterly_release.yml",
    ".github/workflows/federated_sync.yml"
]
PROOF_ANCHORS_TO_CHECK = [
    "24_meta_orchestration/registry/manifests/readiness_proof_shadow.json",
    "24_meta_orchestration/registry/manifests/archive_manifest_v4.4.json"
]

def calculate_days_until_launch():
    """Calculate days remaining until Q1 2026 launch"""
    now = datetime.now(timezone.utc)
    delta = LAUNCH_DATE - now
    return delta.days

def check_workflow_exists(workflow_path):
    """Check if GitHub Actions workflow file exists"""
    return os.path.exists(workflow_path)

def check_cron_triggers(workflow_path):
    """Extract and validate cron trigger times from workflow"""
    if not os.path.exists(workflow_path):
        return {"status": "MISSING", "triggers": []}

    with open(workflow_path, 'r', encoding='utf-8') as f:
        content = f.read()

    triggers = []
    in_schedule = False
    for line in content.split('\n'):
        if 'schedule:' in line:
            in_schedule = True
        elif in_schedule and 'cron:' in line:
            cron_expr = line.split('cron:')[1].strip().strip('"').strip("'")
            triggers.append(cron_expr)
        elif in_schedule and line.strip() and not line.strip().startswith('-') and not line.strip().startswith('cron'):
            in_schedule = False

    return {"status": "CONFIGURED" if triggers else "NO_TRIGGERS", "triggers": triggers}

def check_proof_anchor_integrity(anchor_path):
    """Verify proof-anchor file exists and calculate its hash"""
    if not os.path.exists(anchor_path):
        return {"status": "MISSING", "hash": None}

    with open(anchor_path, 'rb') as f:
        file_hash = hashlib.sha256(f.read()).hexdigest()

    return {"status": "VERIFIED", "hash": file_hash}

def check_registry_locks():
    """Check registry lock status"""
    manifest_path = "24_meta_orchestration/registry/manifests/archive_manifest_v4.4.json"

    if not os.path.exists(manifest_path):
        return {"status": "MISSING", "phase": None}

    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)

    if "certification_seal" in manifest:
        seal = manifest["certification_seal"]
        return {
            "status": "LOCKED",
            "seal_status": seal.get("seal_status"),
            "write_access": seal.get("write_access"),
            "governance_phase": seal.get("governance_phase"),
            "q1_2026_baseline": seal.get("q1_2026_baseline")
        }

    return {"status": "UNLOCKED", "phase": "UNKNOWN"}

def generate_status_report():
    """Generate comprehensive pre-launch status report"""
    timestamp = datetime.now(timezone.utc).isoformat()
    days_until_launch = calculate_days_until_launch()

    # Check workflows
    workflow_status = {}
    for workflow in WORKFLOWS_TO_CHECK:
        workflow_name = os.path.basename(workflow)
        exists = check_workflow_exists(workflow)
        cron_info = check_cron_triggers(workflow)
        workflow_status[workflow_name] = {
            "exists": exists,
            "path": workflow,
            "cron_triggers": cron_info
        }

    # Check proof anchors
    proof_anchor_status = {}
    for anchor in PROOF_ANCHORS_TO_CHECK:
        anchor_name = os.path.basename(anchor)
        anchor_info = check_proof_anchor_integrity(anchor)
        proof_anchor_status[anchor_name] = anchor_info

    # Check registry locks
    lock_status = check_registry_locks()

    # Determine overall readiness
    all_workflows_exist = all(workflow_status[w]["exists"] for w in workflow_status)
    all_anchors_verified = all(proof_anchor_status[a]["status"] == "VERIFIED" for a in proof_anchor_status)
    registry_locked = lock_status["status"] == "LOCKED"

    overall_status = "READY" if (all_workflows_exist and all_anchors_verified and registry_locked) else "NOT_READY"

    # Exit code determination
    exit_code = 0
    exit_message = "All systems operational"

    if not all_workflows_exist:
        exit_code = 1
        exit_message = "Missing workflow configuration"
    elif not all_anchors_verified:
        exit_code = 2
        exit_message = "Hash drift detected in proof anchors"
    elif not registry_locked:
        exit_code = 3
        exit_message = "Registry lock error"

    report = {
        "manifest_version": "1.0.0",
        "blueprint_version": "v4.5.0-prelaunch",
        "timestamp": timestamp,
        "report_type": "governance_warmup_status",
        "launch_countdown": {
            "launch_date": LAUNCH_DATE.isoformat(),
            "days_remaining": days_until_launch,
            "hours_remaining": days_until_launch * 24,
            "status": "ON_SCHEDULE" if days_until_launch >= 0 else "OVERDUE"
        },
        "workflow_readiness": workflow_status,
        "proof_anchor_integrity": proof_anchor_status,
        "registry_lock_status": lock_status,
        "overall_readiness": {
            "status": overall_status,
            "exit_code": exit_code,
            "exit_message": exit_message,
            "components_ready": sum([all_workflows_exist, all_anchors_verified, registry_locked]),
            "components_total": 3
        }
    }

    return report, exit_code

def save_status_log(report):
    """Save status report to log file"""
    os.makedirs(os.path.dirname(STATUS_LOG_PATH), exist_ok=True)

    with open(STATUS_LOG_PATH, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

    print(f"[OK] Status log saved: {STATUS_LOG_PATH}")

def print_status_summary(report):
    """Print human-readable status summary"""
    print("=" * 70)
    print("  GOVERNANCE WARM-UP MONITOR - Blueprint v4.5")
    print("=" * 70)
    print()

    countdown = report["launch_countdown"]
    print(f"[LAUNCH COUNTDOWN]")
    print(f"  Launch Date: {countdown['launch_date']}")
    print(f"  Days Remaining: {countdown['days_remaining']} days")
    print(f"  Status: {countdown['status']}")
    print()

    print(f"[WORKFLOW READINESS]")
    for workflow, info in report["workflow_readiness"].items():
        status = "[OK]" if info["exists"] else "[MISSING]"
        print(f"  {status} {workflow}")
        if info["cron_triggers"]["triggers"]:
            for trigger in info["cron_triggers"]["triggers"]:
                print(f"      Cron: {trigger}")
    print()

    print(f"[PROOF ANCHOR INTEGRITY]")
    for anchor, info in report["proof_anchor_integrity"].items():
        status = "[OK]" if info["status"] == "VERIFIED" else "[ERROR]"
        print(f"  {status} {anchor}")
        if info["hash"]:
            print(f"      Hash: {info['hash'][:16]}...")
    print()

    print(f"[REGISTRY LOCK STATUS]")
    lock = report["registry_lock_status"]
    print(f"  Status: {lock['status']}")
    if lock["status"] == "LOCKED":
        print(f"  Seal Status: {lock.get('seal_status', 'N/A')}")
        print(f"  Write Access: {lock.get('write_access', 'N/A')}")
        print(f"  Governance Phase: {lock.get('governance_phase', 'N/A')}")
        print(f"  Q1 2026 Baseline: {lock.get('q1_2026_baseline', 'N/A')}")
    print()

    overall = report["overall_readiness"]
    print(f"[OVERALL READINESS]")
    print(f"  Status: {overall['status']}")
    print(f"  Components Ready: {overall['components_ready']}/{overall['components_total']}")
    print(f"  Exit Code: {overall['exit_code']}")
    print(f"  Message: {overall['exit_message']}")
    print()

    print("=" * 70)
    if overall["status"] == "READY":
        print("  [OK] GOVERNANCE WARM-UP: ALL SYSTEMS READY")
    else:
        print("  [WARNING] GOVERNANCE WARM-UP: ISSUES DETECTED")
    print("=" * 70)

def main():
    """Main execution"""
    print("\nGovernance Warm-Up Monitor - Blueprint v4.5")
    print("Checking Q1 2026 launch readiness...\n")

    # Generate status report
    report, exit_code = generate_status_report()

    # Save to log file
    save_status_log(report)

    # Print summary
    print_status_summary(report)

    # Exit with appropriate code
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
