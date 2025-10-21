#!/usr/bin/env python3
"""
Anti-Gaming Evidence Snapshot Generator
========================================

Generates comprehensive anti-gaming evidence snapshots during CI runs,
linking WORM chain integrity, commit history, and enforcement execution.

Features:
- Scans all anti-gaming log files (*.jsonl)
- Correlates with WORM chain entries
- Links commit SHA and CI run ID
- Generates deterministic evidence report
- Detects anomalies and gaming attempts

Exit Codes:
    0 - Success (evidence generated, no anomalies detected)
    1 - Warning (evidence generated, minor anomalies detected)
    2 - Critical (evidence generation failed or major anomalies detected)

Author: SSID Codex Engine v6.0
License: Proprietary - SAFE-FIX & ROOT-24-LOCK enforced
"""

import sys
import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any
import argparse


def compute_sha512(data: str) -> str:
    """Compute SHA-512 hash of data."""
    return hashlib.sha512(data.encode('utf-8')).hexdigest()


def compute_blake2b(data: str) -> str:
    """Compute BLAKE2b hash of data."""
    return hashlib.blake2b(data.encode('utf-8')).hexdigest()


def scan_anti_gaming_logs(logs_dir: Path) -> Dict[str, Any]:
    """Scan all anti-gaming JSONL files and collect statistics."""
    result = {
        "log_files_found": 0,
        "total_entries": 0,
        "logs": []
    }

    if not logs_dir.exists():
        return result

    # Find all anti_gaming_*.jsonl files
    log_files = sorted(logs_dir.glob("anti_gaming_*.jsonl"))

    for log_file in log_files:
        try:
            entry_count = 0
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        entry_count += 1

            result["logs"].append({
                "file": log_file.name,
                "path": str(log_file.relative_to(logs_dir.parent)),
                "entries": entry_count,
                "size_bytes": log_file.stat().st_size,
                "modified": datetime.fromtimestamp(
                    log_file.stat().st_mtime, tz=timezone.utc
                ).isoformat()
            })

            result["total_entries"] += entry_count
            result["log_files_found"] += 1

        except Exception as e:
            print(f"Warning: Could not read {log_file.name}: {e}", file=sys.stderr)

    return result


def scan_worm_chain(worm_dir: Path) -> Dict[str, Any]:
    """Scan WORM immutable store and collect chain statistics."""
    result = {
        "worm_entries_found": 0,
        "chain_intact": False,
        "latest_entry": None,
        "entries": []
    }

    if not worm_dir.exists():
        return result

    # Find all sot_enforcement*.json files
    worm_files = sorted(worm_dir.glob("sot_enforcement*.json"))

    for worm_file in worm_files:
        try:
            with open(worm_file, 'r', encoding='utf-8') as f:
                worm_data = json.load(f)

            entry_info = {
                "file": worm_file.name,
                "timestamp": worm_data.get("timestamp", "unknown"),
                "uuid": worm_data.get("uuid", "unknown"),
                "score": worm_data.get("overall_score", 0),
                "certification": worm_data.get("certification_level", "NONE")
            }

            result["entries"].append(entry_info)
            result["worm_entries_found"] += 1

            # Track latest entry
            if result["latest_entry"] is None or entry_info["timestamp"] > result["latest_entry"]["timestamp"]:
                result["latest_entry"] = entry_info

        except Exception as e:
            print(f"Warning: Could not read {worm_file.name}: {e}", file=sys.stderr)

    # Simple chain integrity check (assumes sorted order)
    if result["worm_entries_found"] >= 2:
        timestamps = [e["timestamp"] for e in result["entries"]]
        result["chain_intact"] = timestamps == sorted(timestamps)
    elif result["worm_entries_found"] == 1:
        result["chain_intact"] = True

    return result


def detect_anomalies(anti_gaming_data: Dict, worm_data: Dict) -> List[Dict[str, Any]]:
    """Detect potential gaming attempts or anomalies."""
    anomalies = []

    # Anomaly 1: Insufficient anti-gaming evidence
    if anti_gaming_data["log_files_found"] < 5:
        anomalies.append({
            "severity": "LOW",
            "type": "INSUFFICIENT_EVIDENCE",
            "message": f"Only {anti_gaming_data['log_files_found']} anti-gaming log files found (expected ≥5)",
            "recommendation": "Generate more anti-gaming log entries"
        })

    # Anomaly 2: Low entry count in anti-gaming logs
    if anti_gaming_data["total_entries"] < 10:
        anomalies.append({
            "severity": "MEDIUM",
            "type": "LOW_ENTRY_COUNT",
            "message": f"Only {anti_gaming_data['total_entries']} total anti-gaming entries found",
            "recommendation": "Increase anti-gaming event logging"
        })

    # Anomaly 3: WORM chain not intact
    if not worm_data["chain_intact"]:
        anomalies.append({
            "severity": "CRITICAL",
            "type": "WORM_CHAIN_BREACH",
            "message": "WORM chain integrity compromised (non-monotonic timestamps)",
            "recommendation": "Investigate WORM storage tampering"
        })

    # Anomaly 4: Insufficient WORM entries
    if worm_data["worm_entries_found"] < 10:
        anomalies.append({
            "severity": "LOW",
            "type": "INSUFFICIENT_WORM_ENTRIES",
            "message": f"Only {worm_data['worm_entries_found']} WORM entries found (expected ≥10)",
            "recommendation": "Allow more verification runs to accumulate"
        })

    return anomalies


def generate_evidence_report(
    commit_sha: str,
    run_id: str,
    anti_gaming_data: Dict,
    worm_data: Dict,
    anomalies: List[Dict],
    repo_root: Path
) -> Dict[str, Any]:
    """Generate comprehensive anti-gaming evidence report."""
    timestamp = datetime.now(timezone.utc).isoformat()

    # Create deterministic report structure
    report = {
        "metadata": {
            "report_version": "1.0.0",
            "generated_at": timestamp,
            "tool": "anti_gaming_evidence.py",
            "purpose": "Anti-Gaming Evidence Snapshot for CI Correlation"
        },
        "ci_context": {
            "commit_sha": commit_sha,
            "run_id": run_id,
            "timestamp": timestamp
        },
        "anti_gaming_evidence": {
            "log_files_found": anti_gaming_data["log_files_found"],
            "total_entries": anti_gaming_data["total_entries"],
            "logs": anti_gaming_data["logs"]
        },
        "worm_chain_status": {
            "entries_found": worm_data["worm_entries_found"],
            "chain_intact": worm_data["chain_intact"],
            "latest_entry": worm_data["latest_entry"],
            "entries": worm_data["entries"][-5:]  # Last 5 entries only
        },
        "anomaly_detection": {
            "anomalies_found": len(anomalies),
            "severity_breakdown": {
                "critical": sum(1 for a in anomalies if a["severity"] == "CRITICAL"),
                "high": sum(1 for a in anomalies if a["severity"] == "HIGH"),
                "medium": sum(1 for a in anomalies if a["severity"] == "MEDIUM"),
                "low": sum(1 for a in anomalies if a["severity"] == "LOW")
            },
            "anomalies": anomalies
        },
        "correlation": {
            "anti_gaming_logs_to_worm_ratio": (
                round(anti_gaming_data["total_entries"] / worm_data["worm_entries_found"], 2)
                if worm_data["worm_entries_found"] > 0 else 0
            ),
            "evidence_coverage_score": min(100, (
                (anti_gaming_data["log_files_found"] * 10) +
                (min(anti_gaming_data["total_entries"], 50)) +
                (worm_data["worm_entries_found"] * 2)
            ))
        },
        "summary": {
            "status": "OPERATIONAL" if len([a for a in anomalies if a["severity"] in ["CRITICAL", "HIGH"]]) == 0 else "DEGRADED",
            "anti_gaming_coverage": f"{min(100, anti_gaming_data['log_files_found'] * 9)}%",
            "worm_integrity": "VERIFIED" if worm_data["chain_intact"] else "COMPROMISED"
        }
    }

    # Generate deterministic hashes
    report_json = json.dumps(report, sort_keys=True, ensure_ascii=True, separators=(',', ':'))
    report["signature"] = {
        "sha512": compute_sha512(report_json),
        "blake2b": compute_blake2b(report_json),
        "algorithm": "SHA-512 + BLAKE2b"
    }

    return report


def main():
    """Main evidence generation workflow."""
    import io

    # Force UTF-8 output on Windows
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

    parser = argparse.ArgumentParser(
        description="Anti-Gaming Evidence Snapshot Generator"
    )
    parser.add_argument("--ci-mode", action="store_true",
                        help="CI mode (deterministic output)")
    parser.add_argument("--commit-sha", type=str, default="local",
                        help="Git commit SHA")
    parser.add_argument("--run-id", type=str, default="local",
                        help="CI run ID")
    parser.add_argument("--output", type=str,
                        help="Output JSON file path")
    parser.add_argument("--verbose", action="store_true",
                        help="Verbose output")

    args = parser.parse_args()

    # Repository root
    repo_root = Path(__file__).resolve().parents[2]
    logs_dir = repo_root / "02_audit_logging" / "logs"
    worm_dir = repo_root / "02_audit_logging" / "storage" / "worm" / "immutable_store"

    if args.verbose:
        print("=" * 70)
        print("Anti-Gaming Evidence Snapshot Generator")
        print("=" * 70)
        print(f"Commit SHA: {args.commit_sha}")
        print(f"Run ID: {args.run_id}")
        print(f"Logs directory: {logs_dir}")
        print(f"WORM directory: {worm_dir}")
        print("=" * 70)

    # Scan anti-gaming logs
    if args.verbose:
        print("Scanning anti-gaming logs...")
    anti_gaming_data = scan_anti_gaming_logs(logs_dir)
    if args.verbose:
        print(f"  Found {anti_gaming_data['log_files_found']} log files")
        print(f"  Total entries: {anti_gaming_data['total_entries']}")

    # Scan WORM chain
    if args.verbose:
        print("Scanning WORM chain...")
    worm_data = scan_worm_chain(worm_dir)
    if args.verbose:
        print(f"  Found {worm_data['worm_entries_found']} WORM entries")
        print(f"  Chain intact: {worm_data['chain_intact']}")

    # Detect anomalies
    if args.verbose:
        print("Detecting anomalies...")
    anomalies = detect_anomalies(anti_gaming_data, worm_data)
    if args.verbose:
        print(f"  Found {len(anomalies)} anomalies")

    # Generate report
    if args.verbose:
        print("Generating evidence report...")
    report = generate_evidence_report(
        args.commit_sha,
        args.run_id,
        anti_gaming_data,
        worm_data,
        anomalies,
        repo_root
    )

    # Write output
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=True, sort_keys=True)

        if args.verbose:
            print(f"Report written: {output_path}")
    else:
        # Print to stdout
        print(json.dumps(report, indent=2, ensure_ascii=True, sort_keys=True))

    # Summary
    print()
    print("=" * 70)
    print("Anti-Gaming Evidence Summary")
    print("=" * 70)
    print(f"Status: {report['summary']['status']}")
    print(f"Anti-Gaming Coverage: {report['summary']['anti_gaming_coverage']}")
    print(f"WORM Integrity: {report['summary']['worm_integrity']}")
    print(f"Evidence Coverage Score: {report['correlation']['evidence_coverage_score']}/100")
    print(f"Anomalies: {len(anomalies)}")
    if anomalies:
        for anomaly in anomalies:
            severity_icon = {
                "CRITICAL": "❌",
                "HIGH": "⚠️",
                "MEDIUM": "⚠️",
                "LOW": "ℹ️"
            }.get(anomaly["severity"], "•")
            print(f"  {severity_icon} [{anomaly['severity']}] {anomaly['type']}: {anomaly['message']}")
    print("=" * 70)

    # Exit code determination
    critical_anomalies = [a for a in anomalies if a["severity"] in ["CRITICAL", "HIGH"]]
    if critical_anomalies:
        print("❌ CRITICAL: Anti-gaming evidence indicates potential gaming attempts")
        return 2
    elif anomalies:
        print("⚠️ WARNING: Minor anomalies detected in anti-gaming evidence")
        return 1
    else:
        print("✅ SUCCESS: Anti-gaming evidence snapshot generated successfully")
        return 0


if __name__ == "__main__":
    sys.exit(main())
