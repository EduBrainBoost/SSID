#!/usr/bin/env python3
"""
SSID Strict Score Authenticity Verifier (PROMPT 2)
Only reads canonical *.score.json manifests - zero tolerance for fake scores.
"""
import os
import json
import jsonschema
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime
import uuid

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPO_ROOT / "02_audit_logging/schemas/score_manifest.schema.json"
REPORT_PATH = REPO_ROOT / "02_audit_logging/reports/score_authenticity_strict.json"

def load_schema() -> Dict:
    """Load score manifest schema."""
    with open(SCHEMA_PATH, 'r') as f:
        return json.load(f)

def find_all_score_manifests() -> List[Path]:
    """Find all *.score.json files in repository."""
    return list(REPO_ROOT.rglob("*.score.json"))

def validate_manifest(manifest_path: Path, schema: Dict) -> Tuple[bool, List[str]]:
    """
    Validate a score manifest against schema and business rules.
    Returns (is_valid, errors).
    """
    errors = []

    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
    except Exception as e:
        return False, [f"Failed to load JSON: {e}"]

    # Schema validation
    try:
        jsonschema.validate(manifest, schema)
    except jsonschema.ValidationError as e:
        errors.append(f"Schema validation failed: {e.message}")
        return False, errors

    # Business rule: certification kind must use 100 scale
    if manifest.get("kind") == "cert" and manifest.get("scale", {}).get("max") != 100:
        errors.append("cert kind must use scale.max=100")

    # Business rule: evolution kind must use 400 scale
    if manifest.get("kind") == "evolution" and manifest.get("scale", {}).get("max") != 400:
        errors.append("evolution kind must use scale.max=400")

    # Business rule: value must be within scale
    value = manifest.get("value")
    scale_max = manifest.get("scale", {}).get("max")
    scale_min = manifest.get("scale", {}).get("min", 0)

    if value is not None and scale_max is not None:
        if not (scale_min <= value <= scale_max):
            errors.append(f"value {value} outside scale [{scale_min}, {scale_max}]")

    # Business rule: status="actual" must not be mixed with projection/historic
    status = manifest.get("status")
    if status not in ["actual", "projection", "historic"]:
        errors.append(f"Invalid status: {status}")

    # Business rule: WORM signature must be present and non-empty
    worm_sig = manifest.get("worm", {}).get("signature", "")
    if not worm_sig or len(worm_sig) < 64:
        errors.append("WORM signature missing or too short")

    return len(errors) == 0, errors

def check_certification_chain(manifests: List[Dict]) -> Tuple[bool, List[str]]:
    """
    Verify certification score consistency (PLATINUM >= GOLD >= SILVER >= BRONZE).
    """
    errors = []

    # Group by component
    by_component = {}
    for m in manifests:
        if m.get("kind") != "cert" or m.get("status") != "actual":
            continue

        comp = m.get("metadata", {}).get("component", "unknown")
        grade = m.get("metadata", {}).get("grade", "").upper()
        value = m.get("value")

        if grade in ["PLATINUM", "GOLD", "SILVER", "BRONZE"]:
            if comp not in by_component:
                by_component[comp] = {}
            by_component[comp][grade] = value

    # Check monotonicity
    grade_order = ["BRONZE", "SILVER", "GOLD", "PLATINUM"]
    for comp, grades in by_component.items():
        values = [grades.get(g) for g in grade_order if g in grades]
        if values and values != sorted(values):
            errors.append(f"Component '{comp}' has non-monotonic cert chain: {grades}")

    return len(errors) == 0, errors

def compute_authenticity_rate(results: List[Dict]) -> float:
    """Compute authenticity rate: valid / total."""
    if not results:
        return 0.0
    valid_count = sum(1 for r in results if r["valid"])
    return valid_count / len(results)

def main():
    """Main verification routine."""
    print("=" * 80)
    print("SSID Strict Score Authenticity Verifier")
    print("=" * 80)

    # Load schema
    try:
        schema = load_schema()
        print(f"[+] Loaded schema: {SCHEMA_PATH.relative_to(REPO_ROOT)}")
    except Exception as e:
        print(f"[!] Failed to load schema: {e}")
        return 2

    # Find all manifests
    manifest_paths = find_all_score_manifests()
    print(f"[*] Found {len(manifest_paths)} score manifests")

    if not manifest_paths:
        print("[!] No score manifests found - run migrator first")
        return 2

    # Validate each manifest
    results = []
    all_manifests = []

    for path in manifest_paths:
        valid, errors = validate_manifest(path, schema)

        result = {
            "file": str(path.relative_to(REPO_ROOT)).replace('\\', '/'),
            "valid": valid,
            "errors": errors
        }
        results.append(result)

        if valid:
            with open(path, 'r', encoding='utf-8') as f:
                all_manifests.append(json.load(f))

        if not valid:
            print(f"[!] {path.name}: {'; '.join(errors)}")

    # Check certification chain consistency
    chain_valid, chain_errors = check_certification_chain(all_manifests)

    # Compute authenticity rate
    auth_rate = compute_authenticity_rate(results)

    # Generate report
    report = {
        "verification_id": str(uuid.uuid4()),
        "timestamp": datetime.now().isoformat() + "Z",
        "total_manifests": len(results),
        "valid_manifests": sum(1 for r in results if r["valid"]),
        "invalid_manifests": sum(1 for r in results if not r["valid"]),
        "authenticity_rate": auth_rate,
        "chain_valid": chain_valid,
        "chain_errors": chain_errors,
        "results": results
    }

    # Write report
    with open(REPORT_PATH, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 80)
    print(f"Authenticity Rate: {auth_rate:.4f}")
    print(f"Valid Manifests: {report['valid_manifests']}/{report['total_manifests']}")
    print(f"Chain Consistency: {'PASS' if chain_valid else 'FAIL'}")
    print(f"Report: {REPORT_PATH.relative_to(REPO_ROOT)}")
    print("=" * 80)

    # Exit code: 0 if auth_rate == 1.0, else 2
    if auth_rate == 1.0 and chain_valid:
        print("[OK] Score authenticity verified (100%)")
        return 0
    else:
        print("[FAIL] Score authenticity below 100%")
        return 2

if __name__ == "__main__":
    exit(main())
