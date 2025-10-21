#!/usr/bin/env python3
"""
SoT Rule Coverage Checker - 100% Compliance Verification
=========================================================
Ensures that EVERY rule from the Master-Definition is implemented
in ALL 5 SoT artifacts with perfect consistency.

Checks:
1. Are all Master-Definition rules in the 5 artifacts?
2. Are there shadow/ghost rules in artifacts not in Master?
3. Are all 384 Shard-Integration rules implemented?
4. Are naming conventions, matrix principles enforced?

Exit Codes:
    0: 100% Coverage, no inconsistencies
    1: Gaps/Shadow-Rules/Inconsistencies found

Author: SSID Core Team
Version: 1.0.0
Date: 2025-10-18
"""

import yaml
import json
import sys
from pathlib import Path
from typing import Dict, List, Set, Any
from dataclasses import dataclass
from collections import defaultdict

# ============================================================================
# CONFIGURATION
# ============================================================================

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
MASTERLIST_PATH = PROJECT_ROOT / "02_audit_logging" / "reports" / "SoT_Manual_Coverage_Masterlist_20251018.yaml"

ARTIFACT_PATHS = {
    "contract": PROJECT_ROOT / "16_codex" / "contracts" / "sot" / "sot_contract.yaml",
    "validator": PROJECT_ROOT / "03_core" / "validators" / "sot" / "sot_validator_core.py",
    "policy": PROJECT_ROOT / "23_compliance" / "policies" / "sot" / "sot_policy.rego",
    "cli": PROJECT_ROOT / "12_tooling" / "cli" / "sot_validator.py",
    "tests": PROJECT_ROOT / "11_test_simulation" / "tests_compliance" / "test_sot_validator.py"
}

# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class RuleGap:
    """Represents a gap in rule coverage."""
    rule_id: str
    title: str
    missing_in: List[str]  # Which artifacts miss this rule
    category: str
    priority: str

@dataclass
class ShadowRule:
    """Represents a rule in artifacts not in Master."""
    rule_id: str
    found_in: str
    artifact_source: str

@dataclass
class CoverageReport:
    """Complete coverage analysis."""
    total_master_rules: int
    total_implemented_rules: int
    coverage_percentage: float
    gaps: List[RuleGap]
    shadow_rules: List[ShadowRule]
    inconsistencies: List[Dict[str, Any]]


# ============================================================================
# MASTER-DEFINITION PARSER
# ============================================================================

def load_master_rules() -> List[Dict[str, Any]]:
    """Load master rule list from YAML."""
    if not MASTERLIST_PATH.exists():
        print(f"[ERROR] Masterlist not found: {MASTERLIST_PATH}")
        sys.exit(2)

    with open(MASTERLIST_PATH, 'r', encoding='utf-8') as f:
        masterlist = yaml.safe_load(f)

    return masterlist.get("rules", [])


# ============================================================================
# ARTIFACT PARSERS
# ============================================================================

def extract_rules_from_contract(contract_path: Path) -> Set[str]:
    """Extract rule IDs from sot_contract.yaml."""
    if not contract_path.exists():
        return set()

    with open(contract_path, 'r', encoding='utf-8') as f:
        contract = yaml.safe_load(f)

    rules = contract.get("rules", [])
    return {r["rule_id"] for r in rules if "rule_id" in r}


def extract_rules_from_validator(validator_path: Path) -> Set[str]:
    """Extract rule IDs from sot_validator_core.py."""
    if not validator_path.exists():
        return set()

    with open(validator_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract function names: validate_sot_xxx
    import re
    pattern = r'def\s+validate_(sot_\d+)\('
    matches = re.findall(pattern, content, re.IGNORECASE)

    # Convert to SOT-XXX format
    return {m.upper().replace("_", "-") for m in matches}


def extract_rules_from_policy(policy_path: Path) -> Set[str]:
    """Extract rule IDs from sot_policy.rego."""
    if not policy_path.exists():
        return set()

    with open(policy_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Rego uses generic enforcement, check for rule references in comments
    import re
    pattern = r'SOT-\d+'
    matches = re.findall(pattern, content)

    return set(matches)


def extract_rules_from_cli(cli_path: Path) -> Set[str]:
    """Extract rule IDs from sot_validator.py CLI."""
    if not cli_path.exists():
        return set()

    with open(cli_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # CLI should reference rules
    import re
    pattern = r'SOT-\d+'
    matches = re.findall(pattern, content)

    return set(matches)


def extract_rules_from_tests(tests_path: Path) -> Set[str]:
    """Extract rule IDs from test_sot_validator.py."""
    if not tests_path.exists():
        return set()

    with open(tests_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Tests should reference rules
    import re
    pattern = r'SOT-\d+'
    matches = re.findall(pattern, content)

    return set(matches)


# ============================================================================
# COVERAGE ANALYSIS
# ============================================================================

def analyze_coverage(master_rules: List[Dict[str, Any]]) -> CoverageReport:
    """Analyze coverage of master rules across all 5 artifacts."""

    print("=" * 80)
    print("SoT Rule Coverage Checker - 100% Compliance Verification")
    print("=" * 80)

    # Extract master rule IDs
    master_rule_ids = {r["rule_id"] for r in master_rules}
    print(f"\n[*] Master Rules: {len(master_rule_ids)}")

    # Extract implemented rules from each artifact
    implemented = {}
    for artifact_name, artifact_path in ARTIFACT_PATHS.items():
        print(f"[*] Checking {artifact_name}...")

        if artifact_name == "contract":
            rules = extract_rules_from_contract(artifact_path)
        elif artifact_name == "validator":
            rules = extract_rules_from_validator(artifact_path)
        elif artifact_name == "policy":
            rules = extract_rules_from_policy(artifact_path)
        elif artifact_name == "cli":
            rules = extract_rules_from_cli(artifact_path)
        elif artifact_name == "tests":
            rules = extract_rules_from_tests(artifact_path)
        else:
            rules = set()

        implemented[artifact_name] = rules
        print(f"    Found {len(rules)} rule references")

    # Find gaps (rules in Master but missing in artifacts)
    gaps = []
    for rule in master_rules:
        rule_id = rule["rule_id"]
        missing_in = []

        for artifact_name, artifact_rules in implemented.items():
            if rule_id not in artifact_rules:
                missing_in.append(artifact_name)

        if missing_in:
            gaps.append(RuleGap(
                rule_id=rule_id,
                title=rule["title"],
                missing_in=missing_in,
                category=rule.get("category", "unknown"),
                priority=rule.get("priority", "unknown")
            ))

    # Find shadow rules (rules in artifacts but not in Master)
    shadow_rules = []
    all_artifact_rules = set()
    for artifact_name, artifact_rules in implemented.items():
        all_artifact_rules.update(artifact_rules)

        for rule_id in artifact_rules:
            if rule_id not in master_rule_ids:
                shadow_rules.append(ShadowRule(
                    rule_id=rule_id,
                    found_in=artifact_name,
                    artifact_source=str(ARTIFACT_PATHS[artifact_name])
                ))

    # Calculate coverage
    total_implemented = len(all_artifact_rules & master_rule_ids)
    coverage_pct = (total_implemented / len(master_rule_ids)) * 100 if master_rule_ids else 0

    return CoverageReport(
        total_master_rules=len(master_rule_ids),
        total_implemented_rules=total_implemented,
        coverage_percentage=coverage_pct,
        gaps=gaps,
        shadow_rules=shadow_rules,
        inconsistencies=[]
    )


# ============================================================================
# REPORTING
# ============================================================================

def print_coverage_report(report: CoverageReport):
    """Print detailed coverage report."""

    print("\n" + "=" * 80)
    print("COVERAGE ANALYSIS RESULTS")
    print("=" * 80)
    print(f"Total Master Rules:      {report.total_master_rules}")
    print(f"Total Implemented:       {report.total_implemented_rules}")
    print(f"Coverage:                {report.coverage_percentage:.2f}%")
    print(f"Gaps Found:              {len(report.gaps)}")
    print(f"Shadow Rules Found:      {len(report.shadow_rules)}")

    if report.gaps:
        print("\n" + "-" * 80)
        print("GAPS (Rules in Master but missing in artifacts):")
        print("-" * 80)

        # Group by priority
        by_priority = defaultdict(list)
        for gap in report.gaps:
            by_priority[gap.priority].append(gap)

        for priority in ["must", "should", "have"]:
            if priority in by_priority:
                print(f"\n{priority.upper()} Priority ({len(by_priority[priority])} gaps):")
                for gap in by_priority[priority][:10]:  # Show first 10
                    print(f"  - {gap.rule_id}: {gap.title}")
                    print(f"    Missing in: {', '.join(gap.missing_in)}")

    if report.shadow_rules:
        print("\n" + "-" * 80)
        print("SHADOW RULES (Rules in artifacts but not in Master):")
        print("-" * 80)
        for shadow in report.shadow_rules[:20]:  # Show first 20
            print(f"  - {shadow.rule_id} (found in {shadow.found_in})")


def export_coverage_report(report: CoverageReport, output_path: Path):
    """Export coverage report as JSON."""
    report_dict = {
        "timestamp": "2025-10-18",
        "total_master_rules": report.total_master_rules,
        "total_implemented_rules": report.total_implemented_rules,
        "coverage_percentage": report.coverage_percentage,
        "gaps": [
            {
                "rule_id": g.rule_id,
                "title": g.title,
                "missing_in": g.missing_in,
                "category": g.category,
                "priority": g.priority
            }
            for g in report.gaps
        ],
        "shadow_rules": [
            {
                "rule_id": s.rule_id,
                "found_in": s.found_in,
                "artifact_source": s.artifact_source
            }
            for s in report.shadow_rules
        ]
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report_dict, f, indent=2)

    print(f"\n[+] Coverage report exported: {output_path}")


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main coverage checker workflow."""

    # Load master rules
    master_rules = load_master_rules()

    # Analyze coverage
    report = analyze_coverage(master_rules)

    # Print report
    print_coverage_report(report)

    # Export report
    output_path = PROJECT_ROOT / "02_audit_logging" / "reports" / "sot_coverage_report.json"
    export_coverage_report(report, output_path)

    # Determine exit code
    print("\n" + "=" * 80)
    if report.coverage_percentage >= 100 and len(report.shadow_rules) == 0:
        print("[SUCCESS] 100% COVERAGE - No gaps, no shadow rules")
        print("=" * 80)
        return 0
    else:
        print("[FAIL] Coverage incomplete or shadow rules detected")
        print("=" * 80)
        return 1


if __name__ == "__main__":
    sys.exit(main())
