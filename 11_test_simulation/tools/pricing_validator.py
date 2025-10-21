#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pricing Validator v5.2
Validates Enterprise Subscription SoT against v5.2 revenue thresholds:
- S2' >= 2,000,000 EUR
- S3' >= 5,000,000 EUR
Blocks CI (exit code != 0) if thresholds not met.
"""
import sys, json, os, yaml

# Set UTF-8 encoding for stdout
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

TH_S2 = 2_000_000
TH_S3 = 5_000_000

def load_yaml(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def validate_thresholds(model: dict):
    ok = True
    errors = []

    # Try spec.revenue_bands first (v5.0 format), then root revenue_bands (v5.2 format)
    bands = (model or {}).get("spec", {}).get("revenue_bands", {})
    if not bands:
        bands = (model or {}).get("revenue_bands", {})

    # Check for both old and new field names
    s2 = bands.get("S2_prime_eur") or bands.get("S2_prime_min_eur")
    s3 = bands.get("S3_prime_eur") or bands.get("S3_prime_min_eur")

    if s2 is None or s2 < TH_S2:
        ok = False
        errors.append(f"S2' invalid: expected >= {TH_S2}, got {s2}")
    if s3 is None or s3 < TH_S3:
        ok = False
        errors.append(f"S3' invalid: expected >= {TH_S3}, got {s3}")

    return ok, errors

def main():
    if len(sys.argv) != 2:
        print("USAGE: pricing_validator.py <path_to_enterprise_subscription_model_v5_2.yaml>")
        sys.exit(2)
    path = sys.argv[1]
    if not os.path.exists(path):
        print(f"File not found: {path}")
        sys.exit(2)
    model = load_yaml(path)
    ok, errors = validate_thresholds(model)

    # Extract values for result
    bands = (model or {}).get("spec", {}).get("revenue_bands", {})
    if not bands:
        bands = (model or {}).get("revenue_bands", {})
    s2 = bands.get("S2_prime_eur") or bands.get("S2_prime_min_eur", 0)
    s3 = bands.get("S3_prime_eur") or bands.get("S3_prime_min_eur", 0)

    result = {
        "status": "PASS" if ok else "FAIL",
        "errors": errors,
        "S2_growth_extended": float(s2) if s2 else 0.0,
        "S3_prime": float(s3) if s3 else 0.0
    }
    print(json.dumps(result, ensure_ascii=False))
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
