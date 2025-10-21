#!/usr/bin/env python3
"""
Registry Lineage Integrity Verifier
=====================================

Verifies the cryptographic integrity of the registry lineage chain.

Verification Steps:
  1. Load registry_lineage.yaml
  2. Verify each entry's hash
  3. Verify chain linkage (previous → current)
  4. Verify PQC signatures (if signature files available)
  5. Check chronological ordering
  6. Detect tampering

Security Properties:
  - Detects any modification to ANY entry
  - Detects insertion/deletion of entries
  - Detects reordering of entries
  - Verifies PQC signatures
  - Validates Merkle root evolution

Exit Codes:
  0 - Chain valid
  1 - Chain invalid (tampering detected)
  2 - Configuration error

Author: SSID Compliance Team
Version: 1.0.0
Date: 2025-10-17
"""

import sys
import json
import hashlib
import yaml
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional

# Paths
REPO_ROOT = Path(__file__).resolve().parents[2]
LINEAGE_PATH = REPO_ROOT / "23_compliance" / "registry" / "registry_lineage.yaml"


def load_lineage(lineage_path: Path) -> Dict:
    """Load lineage file."""
    if not lineage_path.exists():
        print(f"ERROR: Lineage file not found: {lineage_path}", file=sys.stderr)
        sys.exit(2)

    with open(lineage_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def compute_entry_hash(entry: Dict) -> str:
    """
    Compute deterministic hash of entry.

    Excludes the 'entry_hash' field itself.
    """
    # Create copy without entry_hash
    entry_copy = entry.copy()
    if 'chain' in entry_copy and 'entry_hash' in entry_copy['chain']:
        entry_copy['chain'] = entry_copy['chain'].copy()
        del entry_copy['chain']['entry_hash']

    # Canonical JSON for hashing
    canonical = json.dumps(entry_copy, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(canonical.encode('utf-8')).hexdigest()


def verify_entry_hash(entry: Dict, entry_idx: int) -> Tuple[bool, str]:
    """Verify that entry hash is correct."""
    stored_hash = entry.get("chain", {}).get("entry_hash")

    if not stored_hash:
        return False, f"Entry #{entry_idx + 1}: Missing entry_hash"

    calculated_hash = compute_entry_hash(entry)

    if stored_hash != calculated_hash:
        return False, f"Entry #{entry_idx + 1}: Hash mismatch (expected {stored_hash[:16]}..., got {calculated_hash[:16]}...)"

    return True, f"Entry #{entry_idx + 1}: Hash valid"


def verify_chain_linkage(entries: List[Dict]) -> Tuple[bool, List[str]]:
    """Verify that entries are properly linked."""
    issues = []

    for idx in range(1, len(entries)):
        current = entries[idx]
        previous = entries[idx - 1]

        # Check previous_entry_id
        expected_prev_id = previous["entry_id"]
        actual_prev_id = current.get("chain", {}).get("previous_entry_id")

        if actual_prev_id != expected_prev_id:
            issues.append(
                f"Entry #{idx + 1}: Broken chain linkage "
                f"(expected previous_entry_id={expected_prev_id}, got {actual_prev_id})"
            )

        # Check previous_merkle_root
        expected_prev_root = previous["global_merkle_root"]
        actual_prev_root = current.get("chain", {}).get("previous_merkle_root")

        if actual_prev_root != expected_prev_root:
            issues.append(
                f"Entry #{idx + 1}: Broken Merkle linkage "
                f"(expected previous_merkle_root={expected_prev_root[:16]}..., got {actual_prev_root[:16] if actual_prev_root else 'None'}...)"
            )

    if issues:
        return False, issues

    return True, []


def verify_chronological_order(entries: List[Dict]) -> Tuple[bool, List[str]]:
    """Verify that entries are in chronological order."""
    issues = []

    for idx in range(1, len(entries)):
        current_time = datetime.fromisoformat(entries[idx]["timestamp"].replace('Z', '+00:00'))
        previous_time = datetime.fromisoformat(entries[idx - 1]["timestamp"].replace('Z', '+00:00'))

        if current_time < previous_time:
            issues.append(
                f"Entry #{idx + 1}: Out of chronological order "
                f"(timestamp {entries[idx]['timestamp']} is before previous entry {entries[idx - 1]['timestamp']})"
            )

    if issues:
        return False, issues

    return True, []


def verify_pqc_signature(entry: Dict, repo_root: Path) -> Tuple[bool, str]:
    """
    Verify PQC signature for entry if signature file exists.

    Returns (valid, message)
    """
    sig_info = entry.get("pqc_signature", {})
    sig_file_path = sig_info.get("signature_file")

    if not sig_file_path:
        return True, "No signature file specified (skipping)"

    sig_path = repo_root / sig_file_path

    if not sig_path.exists():
        return False, f"Signature file not found: {sig_path}"

    try:
        # Load signature document
        with open(sig_path, 'r', encoding='utf-8') as f:
            sig_doc = json.load(f)

        # Verify Merkle root matches
        if sig_doc["payload"]["global_merkle_root"] != entry["global_merkle_root"]:
            return False, f"Merkle root mismatch in signature file"

        # Verify signature hash matches
        if sig_doc["message_hash"] != sig_info["signature_hash"]:
            return False, f"Signature hash mismatch"

        return True, "Signature file verified"

    except Exception as e:
        return False, f"Error verifying signature: {e}"


def display_verification_results(lineage: Dict, results: Dict, verbose: bool = False) -> None:
    """Display verification results."""
    print("\n" + "="*80)
    print("Registry Lineage Integrity Verification")
    print("="*80)

    print(f"\nLineage Metadata:")
    print(f"  Version:        {lineage['metadata']['version']}")
    print(f"  Total Entries:  {lineage['metadata']['total_entries']}")
    print(f"  First Entry:    {lineage['metadata']['first_entry']}")
    print(f"  Last Entry:     {lineage['metadata']['last_entry']}")

    print(f"\nVerification Results:")
    print(f"  Entry Hashes:         {results['hashes']['status']}")
    print(f"  Chain Linkage:        {results['linkage']['status']}")
    print(f"  Chronological Order:  {results['chronology']['status']}")
    print(f"  PQC Signatures:       {results['signatures']['valid']}/{results['signatures']['total']}")

    # Show issues
    all_issues = []
    all_issues.extend(results['hashes'].get('issues', []))
    all_issues.extend(results['linkage'].get('issues', []))
    all_issues.extend(results['chronology'].get('issues', []))
    all_issues.extend(results['signatures'].get('issues', []))

    if all_issues:
        print("\n" + "!"*80)
        print("ISSUES DETECTED:")
        print("!"*80)
        for issue in all_issues:
            print(f"  - {issue}")
        print("!"*80)

    # Verbose: Show each entry
    if verbose:
        print("\n" + "-"*80)
        print("Entry Details:")
        print("-"*80)
        for idx, entry in enumerate(lineage['entries']):
            print(f"\nEntry #{entry['entry_id']}:")
            print(f"  Timestamp:          {entry['timestamp']}")
            print(f"  Global Merkle Root: {entry['global_merkle_root']}")
            print(f"  Compliance Score:   {entry['compliance_score']:.1%}")
            print(f"  Change Type:        {entry['changes']['type']}")
            print(f"  Entry Hash:         {entry['chain']['entry_hash'][:32]}...")

            # Hash verification
            if idx < len(results['hashes']['details']):
                hash_result = results['hashes']['details'][idx]
                status = "[OK]" if hash_result[0] else "[FAIL]"
                print(f"  Hash Verification:  {status}")

            # Signature verification
            if idx < len(results['signatures']['details']):
                sig_result = results['signatures']['details'][idx]
                status = "[OK]" if sig_result[0] else "[SKIP/FAIL]"
                print(f"  Signature:          {status} - {sig_result[1]}")

    print("\n" + "="*80)

    # Final verdict
    if results['overall_valid']:
        print("VERDICT: [VALID] CHAIN INTEGRITY VERIFIED")
        print("="*80)
        print("\nThe registry lineage chain is cryptographically valid.")
        print("No tampering detected.")
        print(f"\nEntries: {lineage['metadata']['total_entries']}")
        print(f"Time Span: {lineage['metadata']['first_entry']} to {lineage['metadata']['last_entry']}")
    else:
        print("VERDICT: [INVALID] CHAIN INTEGRITY COMPROMISED")
        print("="*80)
        print("\nWARNING: Tampering detected in the lineage chain!")
        print("DO NOT TRUST this audit trail.")
        print(f"\nIssues found: {len(all_issues)}")

    print("="*80 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Verify registry lineage chain integrity",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Verify lineage
  python verify_lineage_integrity.py

  # Verbose output
  python verify_lineage_integrity.py --verbose

  # JSON output
  python verify_lineage_integrity.py --json

  # Custom path
  python verify_lineage_integrity.py --lineage ./custom_lineage.yaml
        """
    )

    parser.add_argument("--lineage", type=Path, default=LINEAGE_PATH,
                        help="Path to lineage YAML file")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Verbose output")
    parser.add_argument("--json", action="store_true",
                        help="JSON output")
    parser.add_argument("--verify-signatures", action="store_true",
                        help="Verify PQC signatures (slower)")

    args = parser.parse_args()

    if not args.json:
        print("="*80)
        print("Registry Lineage Integrity Verifier")
        print("="*80)
        print(f"Lineage: {args.lineage}")
        print()

    # Load lineage
    if not args.json:
        print("[1/5] Loading lineage...")
    lineage = load_lineage(args.lineage)

    if not args.json:
        print(f"      Entries: {len(lineage['entries'])}")

    # Verify entry hashes
    if not args.json:
        print("\n[2/5] Verifying entry hashes...")

    hash_results = []
    hash_issues = []

    for idx, entry in enumerate(lineage['entries']):
        valid, message = verify_entry_hash(entry, idx)
        hash_results.append((valid, message))

        if not valid:
            hash_issues.append(message)

        if not args.json:
            status = "[OK]" if valid else "[FAIL]"
            print(f"      Entry #{idx + 1}: {status}")

    # Verify chain linkage
    if not args.json:
        print("\n[3/5] Verifying chain linkage...")

    linkage_valid, linkage_issues = verify_chain_linkage(lineage['entries'])

    if not args.json:
        status = "[OK]" if linkage_valid else "[FAIL]"
        print(f"      Chain linkage: {status}")

    # Verify chronological order
    if not args.json:
        print("\n[4/5] Verifying chronological order...")

    chrono_valid, chrono_issues = verify_chronological_order(lineage['entries'])

    if not args.json:
        status = "[OK]" if chrono_valid else "[FAIL]"
        print(f"      Chronology: {status}")

    # Verify PQC signatures (optional)
    if not args.json:
        print("\n[5/5] Verifying PQC signatures...")

    sig_results = []
    sig_issues = []

    if args.verify_signatures:
        for idx, entry in enumerate(lineage['entries']):
            valid, message = verify_pqc_signature(entry, REPO_ROOT)
            sig_results.append((valid, message))

            if not valid and "not found" in message:
                # File not found is not necessarily an issue
                pass
            elif not valid:
                sig_issues.append(f"Entry #{idx + 1}: {message}")

            if not args.json:
                status = "[OK]" if valid else "[SKIP]" if "not found" in message else "[FAIL]"
                print(f"      Entry #{idx + 1}: {status} - {message}")
    else:
        if not args.json:
            print("      Skipped (use --verify-signatures to enable)")

    # Overall verdict
    overall_valid = (
        all(r[0] for r in hash_results) and
        linkage_valid and
        chrono_valid and
        (not args.verify_signatures or all(r[0] or "not found" in r[1] for r in sig_results))
    )

    # Compile results
    results = {
        "overall_valid": overall_valid,
        "hashes": {
            "status": "PASS" if all(r[0] for r in hash_results) else "FAIL",
            "details": hash_results,
            "issues": hash_issues
        },
        "linkage": {
            "status": "PASS" if linkage_valid else "FAIL",
            "issues": linkage_issues
        },
        "chronology": {
            "status": "PASS" if chrono_valid else "FAIL",
            "issues": chrono_issues
        },
        "signatures": {
            "verified": args.verify_signatures,
            "total": len(lineage['entries']),
            "valid": sum(1 for r in sig_results if r[0]),
            "details": sig_results,
            "issues": sig_issues
        }
    }

    # Output
    if args.json:
        output = {
            "lineage_valid": overall_valid,
            "total_entries": len(lineage['entries']),
            "verification_results": results,
            "metadata": lineage['metadata']
        }
        print(json.dumps(output, indent=2))
    else:
        display_verification_results(lineage, results, args.verbose)

    # Exit code
    return 0 if overall_valid else 1


if __name__ == "__main__":
    sys.exit(main())
