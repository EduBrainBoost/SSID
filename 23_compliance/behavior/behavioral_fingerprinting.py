#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Layer 8: Behavioral Fingerprinting - Detects anomalous build behavior"""
import sys, json, time, hashlib, psutil
from pathlib import Path
from datetime import datetime, timezone

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

REPO_ROOT = Path(__file__).resolve().parents[2]
FINGERPRINT_LOG = REPO_ROOT / "02_audit_logging" / "behavior" / "build_fingerprints.json"

def generate_build_fingerprint(build_id: str) -> dict:
    """Generate behavioral fingerprint for current build"""
    start_time = time.time()

    fingerprint = {
        "build_id": build_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_mb": psutil.virtual_memory().used / (1024**2),
        "disk_io": psutil.disk_io_counters()._asdict() if psutil.disk_io_counters() else {},
        "process_count": len(psutil.pids()),
        "duration_seconds": time.time() - start_time,
    }

    # Compute fingerprint hash
    fp_str = json.dumps(fingerprint, sort_keys=True)
    fingerprint["fingerprint_hash"] = hashlib.sha256(fp_str.encode()).hexdigest()[:16]

    return fingerprint

def detect_anomaly(fingerprint: dict, historical: list) -> bool:
    """Detect if fingerprint is anomalous compared to history"""
    if len(historical) < 5:
        return False  # Need baseline

    # Simple anomaly detection: check if CPU usage is >2x avg
    avg_cpu = sum(h.get("cpu_percent", 0) for h in historical[-10:]) / min(len(historical), 10)
    current_cpu = fingerprint.get("cpu_percent", 0)

    return current_cpu > (avg_cpu * 2)

def main():
    build_id = f"build_{int(time.time())}"
    print(f"[Layer 8] Generating behavioral fingerprint for {build_id}...")

    fingerprint = generate_build_fingerprint(build_id)

    # Load historical fingerprints
    FINGERPRINT_LOG.parent.mkdir(parents=True, exist_ok=True)
    historical = []
    if FINGERPRINT_LOG.exists():
        with open(FINGERPRINT_LOG, 'r', encoding='utf-8') as f:
            data = json.load(f)
            historical = data.get("fingerprints", [])

    # Detect anomaly
    is_anomalous = detect_anomaly(fingerprint, historical)
    fingerprint["anomalous"] = is_anomalous

    # Save
    historical.append(fingerprint)
    historical = historical[-100:]  # Keep last 100

    with open(FINGERPRINT_LOG, 'w', encoding='utf-8') as f:
        json.dump({"fingerprints": historical}, f, indent=2)

    if is_anomalous:
        print(f"  ❌ ANOMALY DETECTED: CPU usage {fingerprint['cpu_percent']:.1f}%")
        return 1
    else:
        print(f"  ✅ Fingerprint normal: CPU {fingerprint['cpu_percent']:.1f}%")
        return 0

if __name__ == "__main__":
    sys.exit(main())
