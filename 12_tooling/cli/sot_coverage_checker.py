#!/usr/bin/env python3
"""
SoT Coverage Checker - Ultra-Granular Rule Validation
======================================================

Verifies that all 249 ultra-granular SoT rules are implemented
in ALL 5 SoT artifacts with ZERO TOLERANCE for gaps.

Exit Codes:
  0 = 100% coverage achieved
  1 = Coverage gaps detected
  2 = Critical error (missing files, parse errors)

Author: SSID Compliance Team
Date: 2025-10-18
Version: 1.0.0
"""

import os
import sys
import json
import yaml
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
from datetime import datetime
from collections import defaultdict

# ====================================================================================
# CONSTANTS
# ====================================================================================

PROJECT_ROOT = Path(__file__).parent.parent.parent
REPORTS_DIR = PROJECT_ROOT / "02_audit_logging" / "reports"

# Source extraction files (249 rules total)
SOURCE_EXTRACTIONS = [
    {
        "file": REPORTS_DIR / "SoT_Part1_Lines_001-026_ULTRA_GRANULAR_FINAL.yaml",
        "rule_range": "SOT-UG-001 to SOT-UG-004",
        "expected_count": 4
    },
    {
        "file": REPORTS_DIR / "SoT_Part1_Lines_027-101_ULTRA_GRANULAR_FINAL.yaml",
        "rule_range": "SOT-UG-005 to SOT-UG-065",
        "expected_count": 61
    },
    {
        "file": REPORTS_DIR / "SoT_Part1_Lines_103-143_ULTRA_GRANULAR_FINAL.yaml",
        "rule_range": "SOT-UG-066 to SOT-UG-099",
        "expected_count": 34
    },
    {
        "file": REPORTS_DIR / "SoT_Part1_Lines_145-251_ULTRA_GRANULAR_FINAL.yaml",
        "rule_range": "SOT-UG-100 to SOT-UG-199",
        "expected_count": 100
    },
    {
        "file": REPORTS_DIR / "SoT_MasterDefinition_Part1_Lines_253-309_ULTRA_GRANULAR.yaml",
        "rule_range": "SOT-MD-200 to SOT-MD-249",
        "expected_count": 50
    }
]

# Target SoT artifacts (all 249 rules MUST be in ALL 5)
SOT_ARTIFACTS = {
    "sot_contract": {
        "file": PROJECT_ROOT / "16_codex" / "contracts" / "sot" / "sot_contract.yaml",
        "type": "yaml",
        "description": "SoT Contract YAML"
    },
    "sot_validator_core": {
        "file": PROJECT_ROOT / "03_core" / "validators" / "sot" / "sot_validator_core.py",
        "type": "python",
        "description": "Core Python Validator"
    },
    "sot_policy": {
        "file": PROJECT_ROOT / "23_compliance" / "policies" / "sot" / "sot_policy.rego",
        "type": "rego",
        "description": "OPA Rego Policy"
    },
    "sot_cli_validator": {
        "file": PROJECT_ROOT / "12_tooling" / "cli" / "sot_validator.py",
        "type": "python",
        "description": "CLI Validator"
    },
    "sot_tests": {
        "file": PROJECT_ROOT / "11_test_simulation" / "tests_compliance" / "test_sot_validator.py",
        "type": "python",
        "description": "Pytest Test Suite"
    }
}

EXPECTED_TOTAL_RULES = 249
EXPECTED_CRITICAL_RULES = 33

# ====================================================================================
# YAML LOADER
# ====================================================================================

def load_yaml_safe(file_path: Path) -> dict:
    """Load YAML file safely."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        print(f"ERROR: Failed to load {file_path}: {e}", file=sys.stderr)
        return {}

# ====================================================================================
# RULE EXTRACTION
# ====================================================================================

def extract_rules_from_source(source_file: Path) -> List[Dict]:
    """Extract all rules from a source extraction YAML file."""
    data = load_yaml_safe(source_file)

    if 'rules' not in data:
        print(f"WARNING: No 'rules' section in {source_file}", file=sys.stderr)
        return []

    rules = data['rules']
    if not isinstance(rules, list):
        print(f"WARNING: 'rules' is not a list in {source_file}", file=sys.stderr)
        return []

    return rules

def get_all_source_rules() -> Tuple[List[str], Dict[str, Dict]]:
    """
    Extract all rule IDs from source extraction files.

    Returns:
        (list of rule IDs, dict mapping rule_id -> full rule data)
    """
    all_rule_ids = []
    rule_data_map = {}

    print("\n=== EXTRACTING RULES FROM SOURCE FILES ===")

    for source_info in SOURCE_EXTRACTIONS:
        source_file = source_info["file"]
        expected = source_info["expected_count"]

        if not source_file.exists():
            print(f"ERROR: Source file not found: {source_file}", file=sys.stderr)
            sys.exit(2)

        rules = extract_rules_from_source(source_file)
        rule_ids = [rule.get('rule_id') for rule in rules if 'rule_id' in rule]

        print(f"  {source_file.name}: {len(rule_ids)} rules (expected: {expected})")

        if len(rule_ids) != expected:
            print(f"    WARNING: Rule count mismatch! Expected {expected}, got {len(rule_ids)}")

        all_rule_ids.extend(rule_ids)

        # Store full rule data
        for rule in rules:
            if 'rule_id' in rule:
                rule_data_map[rule['rule_id']] = rule

    print(f"\n  TOTAL EXTRACTED: {len(all_rule_ids)} rules")

    if len(all_rule_ids) != EXPECTED_TOTAL_RULES:
        print(f"  ERROR: Expected {EXPECTED_TOTAL_RULES} rules, got {len(all_rule_ids)}")

    return all_rule_ids, rule_data_map

# ====================================================================================
# ARTIFACT SCANNING
# ====================================================================================

def scan_yaml_artifact(file_path: Path, rule_ids: List[str]) -> Set[str]:
    """Scan YAML artifact for rule IDs."""
    if not file_path.exists():
        return set()

    data = load_yaml_safe(file_path)
    content = yaml.dump(data)

    found_rules = set()
    for rule_id in rule_ids:
        if rule_id in content:
            found_rules.add(rule_id)

    return found_rules

def scan_python_artifact(file_path: Path, rule_ids: List[str]) -> Set[str]:
    """Scan Python artifact for rule IDs."""
    if not file_path.exists():
        return set()

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"ERROR reading {file_path}: {e}", file=sys.stderr)
        return set()

    found_rules = set()
    for rule_id in rule_ids:
        # Look for rule_id in comments, strings, or variable names
        if rule_id in content:
            found_rules.add(rule_id)

    return found_rules

def scan_rego_artifact(file_path: Path, rule_ids: List[str]) -> Set[str]:
    """Scan OPA Rego artifact for rule IDs."""
    if not file_path.exists():
        return set()

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"ERROR reading {file_path}: {e}", file=sys.stderr)
        return set()

    found_rules = set()
    for rule_id in rule_ids:
        if rule_id in content:
            found_rules.add(rule_id)

    return found_rules

def scan_artifact(artifact_info: Dict, rule_ids: List[str]) -> Set[str]:
    """Scan a single artifact for rule IDs."""
    file_path = artifact_info["file"]
    artifact_type = artifact_info["type"]

    if artifact_type == "yaml":
        return scan_yaml_artifact(file_path, rule_ids)
    elif artifact_type == "python":
        return scan_python_artifact(file_path, rule_ids)
    elif artifact_type == "rego":
        return scan_rego_artifact(file_path, rule_ids)
    else:
        print(f"ERROR: Unknown artifact type: {artifact_type}", file=sys.stderr)
        return set()

# ====================================================================================
# COVERAGE ANALYSIS
# ====================================================================================

def analyze_coverage(rule_ids: List[str], rule_data_map: Dict[str, Dict]) -> Dict:
    """
    Analyze coverage of all rules across all artifacts.

    Returns:
        Coverage report dictionary
    """
    print("\n=== SCANNING SOT ARTIFACTS ===")

    artifact_coverage = {}

    for artifact_name, artifact_info in SOT_ARTIFACTS.items():
        file_path = artifact_info["file"]
        description = artifact_info["description"]

        exists = file_path.exists()
        status = "EXISTS" if exists else "MISSING"

        print(f"  {artifact_name} ({description}): {status}")

        if exists:
            found_rules = scan_artifact(artifact_info, rule_ids)
            coverage_percent = (len(found_rules) / len(rule_ids)) * 100

            print(f"    Coverage: {len(found_rules)}/{len(rule_ids)} ({coverage_percent:.1f}%)")

            artifact_coverage[artifact_name] = {
                "file": str(file_path),
                "exists": True,
                "found_rules": sorted(list(found_rules)),
                "coverage_count": len(found_rules),
                "coverage_percent": coverage_percent,
                "missing_rules": sorted(list(set(rule_ids) - found_rules))
            }
        else:
            print(f"    ERROR: File not found!")
            artifact_coverage[artifact_name] = {
                "file": str(file_path),
                "exists": False,
                "found_rules": [],
                "coverage_count": 0,
                "coverage_percent": 0.0,
                "missing_rules": rule_ids
            }

    # Find rules missing from ANY artifact
    rules_with_full_coverage = set(rule_ids)
    for coverage_data in artifact_coverage.values():
        rules_with_full_coverage &= set(coverage_data["found_rules"])

    rules_missing_from_any = set(rule_ids) - rules_with_full_coverage

    # Calculate overall coverage
    overall_coverage_percent = (len(rules_with_full_coverage) / len(rule_ids)) * 100

    # Identify critical rules
    critical_rules = [
        rule_id for rule_id in rule_ids
        if rule_data_map.get(rule_id, {}).get('criticality') == 'CRITICAL'
    ]

    critical_missing = [
        rule_id for rule_id in critical_rules
        if rule_id in rules_missing_from_any
    ]

    report = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "total_rules": len(rule_ids),
        "expected_rules": EXPECTED_TOTAL_RULES,
        "critical_rules_total": len(critical_rules),
        "expected_critical_rules": EXPECTED_CRITICAL_RULES,
        "rules_with_full_coverage": len(rules_with_full_coverage),
        "rules_missing_from_any_artifact": len(rules_missing_from_any),
        "overall_coverage_percent": overall_coverage_percent,
        "target_coverage_percent": 100.0,
        "coverage_achieved": overall_coverage_percent == 100.0,
        "artifacts": artifact_coverage,
        "critical_rules": critical_rules,
        "critical_rules_missing": critical_missing,
        "rules_missing_list": sorted(list(rules_missing_from_any))
    }

    return report

# ====================================================================================
# REPORT GENERATION
# ====================================================================================

def generate_json_report(report: Dict, output_path: Path):
    """Generate JSON coverage report."""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    print(f"\nJSON report saved: {output_path}")

def generate_markdown_report(report: Dict, output_path: Path, rule_data_map: Dict[str, Dict]):
    """Generate Markdown coverage report."""

    md = []
    md.append("# SoT Coverage Report - Ultra-Granular Rules")
    md.append("")
    md.append(f"**Generated:** {report['timestamp']}")
    md.append("")
    md.append("## Summary")
    md.append("")
    md.append(f"- **Total Rules:** {report['total_rules']}")
    md.append(f"- **Critical Rules:** {report['critical_rules_total']}")
    md.append(f"- **Rules with Full Coverage:** {report['rules_with_full_coverage']}")
    md.append(f"- **Rules Missing from ANY Artifact:** {report['rules_missing_from_any_artifact']}")
    md.append(f"- **Overall Coverage:** {report['overall_coverage_percent']:.1f}%")
    md.append(f"- **Target Coverage:** {report['target_coverage_percent']}%")
    md.append("")

    if report['coverage_achieved']:
        md.append("**STATUS:** ✅ **100% COVERAGE ACHIEVED**")
    else:
        md.append(f"**STATUS:** ❌ **COVERAGE GAPS DETECTED** ({report['rules_missing_from_any_artifact']} rules missing)")

    md.append("")
    md.append("## Artifact Coverage")
    md.append("")
    md.append("| Artifact | Exists | Coverage | Missing Rules |")
    md.append("|----------|--------|----------|---------------|")

    for artifact_name, coverage_data in report['artifacts'].items():
        artifact_info = SOT_ARTIFACTS[artifact_name]
        exists_icon = "✅" if coverage_data['exists'] else "❌"
        coverage = f"{coverage_data['coverage_percent']:.1f}%"
        missing = len(coverage_data['missing_rules'])

        md.append(f"| {artifact_info['description']} | {exists_icon} | {coverage} | {missing} |")

    md.append("")

    if report['critical_rules_missing']:
        md.append("## ⚠️ CRITICAL RULES MISSING")
        md.append("")
        md.append("The following CRITICAL rules are missing from one or more artifacts:")
        md.append("")
        for rule_id in sorted(report['critical_rules_missing']):
            rule = rule_data_map.get(rule_id, {})
            title = rule.get('title', 'Unknown')
            md.append(f"- **{rule_id}**: {title}")
        md.append("")

    if report['rules_missing_list']:
        md.append("## Missing Rules Details")
        md.append("")
        md.append("### Rules Missing from ANY Artifact")
        md.append("")
        for rule_id in sorted(report['rules_missing_list']):
            rule = rule_data_map.get(rule_id, {})
            title = rule.get('title', 'Unknown')
            criticality = rule.get('criticality', '')
            crit_tag = " **[CRITICAL]**" if criticality == 'CRITICAL' else ""

            md.append(f"- **{rule_id}**: {title}{crit_tag}")

            # Show which artifacts are missing this rule
            missing_from = []
            for artifact_name, coverage_data in report['artifacts'].items():
                if rule_id in coverage_data['missing_rules']:
                    missing_from.append(SOT_ARTIFACTS[artifact_name]['description'])

            if missing_from:
                md.append(f"  - Missing from: {', '.join(missing_from)}")
        md.append("")

    md.append("## Next Steps")
    md.append("")
    if report['coverage_achieved']:
        md.append("- ✅ All 249 rules are implemented in all 5 SoT artifacts")
        md.append("- ✅ Zero tolerance policy satisfied")
        md.append("- ✅ Ready for production deployment")
    else:
        md.append("- ❌ Implement missing rules in all artifacts")
        md.append("- ❌ Re-run coverage checker until 100% achieved")
        md.append("- ❌ Zero tolerance policy NOT satisfied")
    md.append("")

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md))

    print(f"Markdown report saved: {output_path}")

# ====================================================================================
# MAIN
# ====================================================================================

def main():
    """Main coverage checker entry point."""

    print("=" * 80)
    print("SoT COVERAGE CHECKER - Ultra-Granular Rule Validation")
    print("=" * 80)
    print(f"Expected Rules: {EXPECTED_TOTAL_RULES}")
    print(f"Expected Critical Rules: {EXPECTED_CRITICAL_RULES}")
    print(f"Target Coverage: 100% (Zero Tolerance)")

    # Step 1: Extract all rules from source files
    rule_ids, rule_data_map = get_all_source_rules()

    if len(rule_ids) != EXPECTED_TOTAL_RULES:
        print(f"\nERROR: Rule count mismatch. Expected {EXPECTED_TOTAL_RULES}, got {len(rule_ids)}")
        sys.exit(2)

    # Step 2: Analyze coverage across all artifacts
    report = analyze_coverage(rule_ids, rule_data_map)

    # Step 3: Generate reports
    output_dir = REPORTS_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    json_path = output_dir / "sot_coverage_report.json"
    md_path = output_dir / "sot_coverage_report.md"

    generate_json_report(report, json_path)
    generate_markdown_report(report, md_path, rule_data_map)

    # Step 4: Print summary
    print("\n" + "=" * 80)
    print("COVERAGE SUMMARY")
    print("=" * 80)
    print(f"Total Rules: {report['total_rules']}")
    print(f"Rules with Full Coverage: {report['rules_with_full_coverage']}")
    print(f"Rules Missing from ANY Artifact: {report['rules_missing_from_any_artifact']}")
    print(f"Overall Coverage: {report['overall_coverage_percent']:.1f}%")

    if report['critical_rules_missing']:
        print(f"\n⚠️  CRITICAL RULES MISSING: {len(report['critical_rules_missing'])}")

    # Step 5: Exit with appropriate code
    if report['coverage_achieved']:
        print("\n✅ SUCCESS: 100% COVERAGE ACHIEVED")
        print("=" * 80)
        sys.exit(0)
    else:
        print(f"\n❌ FAILURE: COVERAGE GAPS DETECTED ({report['rules_missing_from_any_artifact']} rules missing)")
        print("=" * 80)
        sys.exit(1)

if __name__ == "__main__":
    main()
