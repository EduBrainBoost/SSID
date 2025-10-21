#!/usr/bin/env python3
"""
Real-Time Compliance Verifier
==============================

Verifies compliance in REAL-TIME without CI/CD by:
1. Loading compliance_registry.json
2. Recalculating hashes of all manifestation files
3. Verifying Merkle trees
4. Reporting compliance status instantly

This enables:
- Instant compliance checks (no CI wait time)
- Local development verification
- Pre-commit validation
- Continuous monitoring

Usage:
    python verify_compliance_realtime.py [--rule CC1.1] [--standard soc2]

Author: SSID Compliance Team
Version: 1.0.0
Date: 2025-10-17
"""

import sys
import json
import hashlib
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime


# Repository root
REPO_ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = REPO_ROOT / "23_compliance" / "registry" / "compliance_registry.json"


def sha256_file(filepath: Path) -> str:
    """Calculate SHA-256 hash of file"""
    if not filepath.exists():
        return "0" * 64

    sha256_hash = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception:
        return "0" * 64


def sha256_string(text: str) -> str:
    """Calculate SHA-256 hash of string"""
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def load_registry() -> Dict:
    """Load compliance registry"""
    if not REGISTRY_PATH.exists():
        print(f"ERROR: Registry not found: {REGISTRY_PATH}", file=sys.stderr)
        print("Run: python 23_compliance/registry/generate_compliance_registry.py", file=sys.stderr)
        sys.exit(1)

    with open(REGISTRY_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def verify_rule_merkle_tree(rule_data: Dict, repo_root: Path) -> Tuple[bool, Dict]:
    """
    Verify Merkle tree for a single rule by recalculating hashes

    Returns:
        (is_valid: bool, details: Dict)
    """
    details = {
        "rule_id": rule_data["rule_id"],
        "name": rule_data["name"],
        "manifestations_valid": {},
        "merkle_valid": False,
        "expected_root": rule_data["merkle_tree"]["root_hash"],
        "calculated_root": None,
        "hash_mismatches": []
    }

    # Recalculate hashes for all manifestations
    leaf_hashes = []
    all_valid = True

    for mtype in ["python", "rego", "yaml", "cli"]:
        manifest = rule_data["manifestations"][mtype]
        expected_hash = manifest["hash"]

        # Get actual file path - all paths are relative to repo_root
        file_path = repo_root / manifest["path"].replace("\\", "/")

        # Calculate actual hash
        actual_hash = sha256_file(file_path)
        leaf_hashes.append(actual_hash)

        # Compare
        is_match = (actual_hash == expected_hash)
        details["manifestations_valid"][mtype] = is_match

        if not is_match:
            details["hash_mismatches"].append({
                "type": mtype,
                "expected": expected_hash,
                "actual": actual_hash,
                "path": str(file_path),
                "exists": file_path.exists()
            })
            all_valid = False

    # Rebuild Merkle tree
    if len(leaf_hashes) == 4:
        # Level 1: Combine pairs
        left_intermediate = sha256_string(leaf_hashes[0] + leaf_hashes[1])
        right_intermediate = sha256_string(leaf_hashes[2] + leaf_hashes[3])

        # Level 2: Root
        calculated_root = sha256_string(left_intermediate + right_intermediate)

        details["calculated_root"] = calculated_root
        details["merkle_valid"] = (calculated_root == details["expected_root"])

    return (all_valid and details["merkle_valid"], details)


def verify_all_rules(registry: Dict, repo_root: Path) -> Dict:
    """Verify all rules in registry"""
    results = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "standards": {},
        "summary": {
            "total_rules": 0,
            "valid_rules": 0,
            "partial_rules": 0,
            "invalid_rules": 0
        }
    }

    for standard, std_data in registry["standards"].items():
        standard_results = {
            "name": std_data["name"],
            "rules": {}
        }

        for rule_id, rule_data in std_data["rules"].items():
            is_valid, details = verify_rule_merkle_tree(rule_data, repo_root)

            standard_results["rules"][rule_id] = {
                "valid": is_valid,
                "details": details
            }

            # Update summary
            results["summary"]["total_rules"] += 1

            if is_valid:
                results["summary"]["valid_rules"] += 1
            elif any(details["manifestations_valid"].values()):
                results["summary"]["partial_rules"] += 1
            else:
                results["summary"]["invalid_rules"] += 1

        results["standards"][standard] = standard_results

    return results


def print_verification_results(results: Dict, verbose: bool = False):
    """Print verification results to console"""
    print("\n" + "="*80)
    print("Real-Time Compliance Verification")
    print("="*80)
    print(f"Timestamp: {results['timestamp']}")
    print()

    summary = results["summary"]
    print("Summary:")
    print(f"  Total Rules:   {summary['total_rules']}")
    print(f"  Valid:         {summary['valid_rules']} (OK - Merkle verified)")
    print(f"  Partial:       {summary['partial_rules']} (WARNING - Some manifestations OK)")
    print(f"  Invalid:       {summary['invalid_rules']} (FAIL - Merkle mismatch)")
    print()

    # Per-standard results
    for standard, std_results in results["standards"].items():
        print(f"\n[{standard.upper()}] {std_results['name']}")
        print("-" * 80)

        for rule_id, rule_result in std_results["rules"].items():
            details = rule_result["details"]
            is_valid = rule_result["valid"]

            # Status icon
            if is_valid:
                icon = "OK"
                color = ""
            elif any(details["manifestations_valid"].values()):
                icon = "WARN"
                color = ""
            else:
                icon = "FAIL"
                color = ""

            print(f"  [{icon}] {rule_id} - {details['name']}")

            if verbose or not is_valid:
                # Show manifestation status
                for mtype, valid in details["manifestations_valid"].items():
                    status = "OK" if valid else "FAIL"
                    print(f"       {mtype:8s}: {status}")

                if details["hash_mismatches"]:
                    print(f"       Merkle Root: MISMATCH")
                    print(f"         Expected: {details['expected_root'][:16]}...")
                    print(f"         Actual:   {details['calculated_root'][:16] if details['calculated_root'] else 'N/A'}...")

                    if verbose:
                        print("\n       Hash Mismatches:")
                        for mismatch in details["hash_mismatches"]:
                            print(f"         {mismatch['type']}:")
                            print(f"           Expected: {mismatch['expected'][:32]}...")
                            print(f"           Actual:   {mismatch['actual'][:32]}...")
                            print(f"           Exists:   {mismatch['exists']}")
                            print()

    print("\n" + "="*80)

    # Final verdict
    if summary["invalid_rules"] > 0 or summary["partial_rules"] > 0:
        print("VERDICT: COMPLIANCE VIOLATIONS DETECTED")
        print(f"         {summary['invalid_rules']} rules FAILED")
        print(f"         {summary['partial_rules']} rules PARTIAL")
        print("="*80)
        return False
    else:
        print("VERDICT: FULL COMPLIANCE - All Merkle trees verified")
        print("="*80)
        return True


def verify_single_rule(registry: Dict, standard: str, rule_id: str, repo_root: Path) -> bool:
    """Verify a single rule"""
    if standard not in registry["standards"]:
        print(f"ERROR: Unknown standard: {standard}", file=sys.stderr)
        return False

    std_data = registry["standards"][standard]

    if rule_id not in std_data["rules"]:
        print(f"ERROR: Unknown rule: {rule_id} in {standard}", file=sys.stderr)
        return False

    rule_data = std_data["rules"][rule_id]

    print(f"\nVerifying {standard.upper()} {rule_id} - {rule_data['name']}...")
    print("="*80)

    is_valid, details = verify_rule_merkle_tree(rule_data, repo_root)

    print(f"\nRule: {details['rule_id']} - {details['name']}")
    print(f"Expected Merkle Root: {details['expected_root']}")
    print(f"Calculated Merkle Root: {details['calculated_root']}")
    print()

    print("Manifestations:")
    for mtype, valid in details["manifestations_valid"].items():
        status = "OK" if valid else "FAIL"
        print(f"  {mtype:10s}: {status}")

    if details["hash_mismatches"]:
        print("\nHash Mismatches:")
        for mismatch in details["hash_mismatches"]:
            print(f"\n  {mismatch['type'].upper()}:")
            print(f"    Path:     {mismatch['path']}")
            print(f"    Exists:   {mismatch['exists']}")
            print(f"    Expected: {mismatch['expected']}")
            print(f"    Actual:   {mismatch['actual']}")

    print("\n" + "="*80)

    if is_valid:
        print("RESULT: VALID - Merkle tree verified")
    else:
        print("RESULT: INVALID - Merkle verification FAILED")

    print("="*80 + "\n")

    return is_valid


def main():
    parser = argparse.ArgumentParser(
        description="Real-Time Compliance Verifier (Merkle-based)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Verify all rules
  python verify_compliance_realtime.py

  # Verify single rule
  python verify_compliance_realtime.py --standard soc2 --rule CC1.1

  # Verbose output
  python verify_compliance_realtime.py --verbose

  # JSON output
  python verify_compliance_realtime.py --json
        """
    )

    parser.add_argument("--standard", "-s", help="Standard to verify (soc2, gaia_x, etsi_en_319_421)")
    parser.add_argument("--rule", "-r", help="Rule ID to verify (e.g., CC1.1)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT, help="Repository root")

    args = parser.parse_args()

    # Load registry
    print(f"Loading registry from: {REGISTRY_PATH}")
    registry = load_registry()

    print(f"Registry loaded: {registry['metadata']['total_rules']} rules")
    print(f"Generated: {registry['metadata']['generated_at']}")

    # Verify
    if args.standard and args.rule:
        # Single rule verification
        is_valid = verify_single_rule(registry, args.standard, args.rule, args.repo_root)
        return 0 if is_valid else 1

    else:
        # Full verification
        results = verify_all_rules(registry, args.repo_root)

        if args.json:
            print(json.dumps(results, indent=2))
            # Determine validity from results
            is_valid = (results["summary"]["invalid_rules"] == 0 and
                       results["summary"]["partial_rules"] == 0)
        else:
            is_valid = print_verification_results(results, verbose=args.verbose)

        return 0 if is_valid else 1


if __name__ == "__main__":
    sys.exit(main())
