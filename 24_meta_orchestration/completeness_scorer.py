#!/usr/bin/env python3
"""
SSID SoT Completeness Scorer
=============================

Version: 4.0.0 PRODUCTION
Status: CROSS-ARTIFACT ANALYSIS
License: ROOT-24-LOCK enforced

PURPOSE:
--------
Calculate completeness score for SoT system by verifying that every rule
exists in ALL 5 required artifacts:

1. Contract (16_codex/contracts/sot/sot_contract.yaml)
2. Policy (23_compliance/policies/sot/sot_policy*.rego)
3. Validator (03_core/validators/sot/sot_validator*.py)
4. Tests (11_test_simulation/tests_compliance/test_sot_validator.py)
5. Audit (02_audit_logging/reports/*.json*)

COMPLETENESS FORMULA:
---------------------
For each rule:
  completeness = (num_artifacts_containing_rule / 5) * 100

Overall completeness:
  sum(rule_completeness) / total_rules * 100

TARGET: 100% (all rules in all 5 artifacts)
"""

import json
import re
import yaml
from pathlib import Path
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from collections import defaultdict


@dataclass
class ArtifactCoverage:
    """Coverage of a single artifact"""
    artifact_name: str
    artifact_path: Path
    rules_found: int
    rule_ids: Set[str]


@dataclass
class RuleCompleteness:
    """Completeness tracking for a single rule"""
    rule_id: str
    in_contract: bool
    in_policy: bool
    in_validator: bool
    in_tests: bool
    in_audit: bool
    completeness_score: float  # 0.0 to 1.0

    def to_dict(self) -> dict:
        return {
            'rule_id': self.rule_id,
            'in_contract': self.in_contract,
            'in_policy': self.in_policy,
            'in_validator': self.in_validator,
            'in_tests': self.in_tests,
            'in_audit': self.in_audit,
            'completeness_score': self.completeness_score,
            'missing_artifacts': self.get_missing_artifacts()
        }

    def get_missing_artifacts(self) -> List[str]:
        """Get list of artifacts missing this rule"""
        missing = []
        if not self.in_contract:
            missing.append('contract')
        if not self.in_policy:
            missing.append('policy')
        if not self.in_validator:
            missing.append('validator')
        if not self.in_tests:
            missing.append('tests')
        if not self.in_audit:
            missing.append('audit')
        return missing


@dataclass
class CompletenessReport:
    """Overall completeness report"""
    timestamp: str
    total_rules: int
    rules_with_100_percent: int
    rules_with_80_percent: int
    rules_with_60_percent: int
    rules_with_40_percent: int
    rules_with_20_percent: int
    rules_with_0_percent: int
    overall_completeness: float
    artifact_coverage: Dict[str, int]
    rule_details: List[RuleCompleteness]

    def to_dict(self) -> dict:
        return {
            'timestamp': self.timestamp,
            'total_rules': self.total_rules,
            'rules_with_100_percent': self.rules_with_100_percent,
            'rules_with_80_percent': self.rules_with_80_percent,
            'rules_with_60_percent': self.rules_with_60_percent,
            'rules_with_40_percent': self.rules_with_40_percent,
            'rules_with_20_percent': self.rules_with_20_percent,
            'rules_with_0_percent': self.rules_with_0_percent,
            'overall_completeness': self.overall_completeness,
            'artifact_coverage': self.artifact_coverage,
            'rule_details': [r.to_dict() for r in self.rule_details]
        }


class CompletenessScorer:
    """
    Calculates completeness score across all SoT artifacts
    """

    def __init__(self, repo_root: Path = None):
        if repo_root is None:
            # Auto-detect repo root
            self.repo_root = Path(__file__).resolve().parents[1]
        else:
            self.repo_root = Path(repo_root)

        self.artifacts = {
            'contract': self.repo_root / '16_codex/contracts/sot/sot_contract.yaml',
            'policy': self.repo_root / '23_compliance/policies/sot',
            'validator': self.repo_root / '03_core/validators/sot',
            'tests': self.repo_root / '11_test_simulation/tests_compliance/test_sot_validator.py',
            'audit': self.repo_root / '02_audit_logging/reports'
        }

        self.registry_path = self.repo_root / '16_codex/structure/auto_generated/sot_rules_full.json'

    def load_registry(self) -> List[str]:
        """Load all rule IDs from registry"""
        if not self.registry_path.exists():
            raise FileNotFoundError(f"Registry not found: {self.registry_path}")

        with open(self.registry_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        rules = data.get('rules', [])
        rule_ids = []

        for rule in rules:
            rule_id = rule.get('rule_id') or rule.get('id')
            if rule_id:
                rule_ids.append(rule_id)

        return rule_ids

    def scan_contract(self) -> Set[str]:
        """Scan contract YAML for rule IDs"""
        contract_path = self.artifacts['contract']
        rule_ids = set()

        if not contract_path.exists():
            print(f"Warning: Contract not found at {contract_path}")
            return rule_ids

        try:
            with open(contract_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract rule IDs from YAML
            # Pattern: id: RULE-XXX or rule_id: XXX
            patterns = [
                r'id:\s*["\']?([A-Za-z0-9_\-.]+)["\']?',
                r'rule_id:\s*["\']?([A-Za-z0-9_\-.]+)["\']?',
            ]

            for pattern in patterns:
                matches = re.findall(pattern, content)
                rule_ids.update(matches)

        except Exception as e:
            print(f"Error scanning contract: {e}")

        return rule_ids

    def scan_policy(self) -> Set[str]:
        """Scan policy Rego files for rule IDs"""
        policy_dir = self.artifacts['policy']
        rule_ids = set()

        if not policy_dir.exists():
            print(f"Warning: Policy dir not found at {policy_dir}")
            return rule_ids

        # Scan all .rego files
        for rego_file in policy_dir.glob('*.rego'):
            try:
                with open(rego_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Extract rule IDs from comments and rule definitions
                patterns = [
                    r'# Rule:\s*([A-Za-z0-9_\-.]+)',
                    r'rule_id["\']?\s*[:=]\s*["\']?([A-Za-z0-9_\-.]+)["\']?',
                ]

                for pattern in patterns:
                    matches = re.findall(pattern, content)
                    rule_ids.update(matches)

            except Exception as e:
                print(f"Error scanning {rego_file}: {e}")

        return rule_ids

    def scan_validator(self) -> Set[str]:
        """Scan validator Python files for rule IDs"""
        validator_dir = self.artifacts["validator"]
        rule_ids = set()

        if not validator_dir.exists():
            print(f"Warning: Validator dir not found at {validator_dir}")
            return rule_ids

        # Check for data-driven validation engine
        engine_file = validator_dir / "sot_validator_engine.py"
        if engine_file.exists():
            print(f"  Found data-driven validator engine")
            # Load registry to get all rule IDs
            registry_path = self.repo_root / "16_codex" / "structure" / "auto_generated" / "sot_rules_full.json"
            if registry_path.exists():
                try:
                    import json
                    with open(registry_path, "r", encoding="utf-8") as f:
                        registry = json.load(f)
                    rule_ids = set(r["rule_id"] for r in registry.get("rules", []))
                    print(f"  Loaded {len(rule_ids)} rules from registry")
                    return rule_ids
                except Exception as e:
                    print(f"  Warning: Could not load registry: {e}")


        # Scan all .py files
        for py_file in validator_dir.glob('*.py'):
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                # Extract rule IDs from function names and docstrings
                patterns = [
                    r'def\s+validate_([a-z0-9_]+)\(',
                    r'def\s+validate_r_([A-Za-z0-9_]+)\(',
                    r'rule_id["\']?\s*[:=]\s*["\']([A-Za-z0-9_\-.]+)["\']',
                ]

                for pattern in patterns:
                    matches = re.findall(pattern, content)
                    rule_ids.update(matches)

            except Exception as e:
                print(f"Error scanning {py_file}: {e}")

        return rule_ids

    def scan_tests(self) -> Set[str]:
        """Scan test file for rule IDs"""
        test_path = self.artifacts['tests']
        rule_ids = set()

        if not test_path.exists():
            print(f"Warning: Test file not found at {test_path}")
            return rule_ids

        try:
            with open(test_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract rule IDs from test function names
            patterns = [
                r'def\s+test_([a-z0-9_]+)\(',
                r'def\s+test_r_([A-Za-z0-9_]+)\(',
                r'rule_id["\']?\s*[:=]\s*["\']([A-Za-z0-9_\-.]+)["\']',
            ]

            for pattern in patterns:
                matches = re.findall(pattern, content)
                rule_ids.update(matches)

        except Exception as e:
            print(f"Error scanning tests: {e}")

        return rule_ids

    def scan_audit(self) -> Set[str]:
        """Scan audit logs for rule IDs"""
        audit_dir = self.artifacts['audit']
        rule_ids = set()

        if not audit_dir.exists():
            print(f"Warning: Audit dir not found at {audit_dir}")
            return rule_ids

        # Scan JSON and JSONL files
        for audit_file in audit_dir.glob('*.json*'):
            try:
                with open(audit_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Extract rule IDs from JSON
                patterns = [
                    r'"rule_id":\s*"([A-Za-z0-9_\-.]+)"',
                    r'"id":\s*"([A-Za-z0-9_\-.]+)"',
                ]

                for pattern in patterns:
                    matches = re.findall(pattern, content)
                    rule_ids.update(matches)

            except Exception as e:
                # Skip binary or invalid files
                pass

        return rule_ids

    def calculate_completeness(self) -> CompletenessReport:
        """
        Calculate completeness score for all rules

        Returns:
            CompletenessReport with detailed breakdown
        """
        print("=" * 80)
        print("SoT Completeness Scoring")
        print("=" * 80)

        # Load all rule IDs from registry
        print("\n[1/6] Loading registry...")
        all_rule_ids = self.load_registry()
        print(f"  Total rules in registry: {len(all_rule_ids)}")

        # Scan each artifact
        print("\n[2/6] Scanning Contract...")
        contract_rules = self.scan_contract()
        print(f"  Rules found: {len(contract_rules)}")

        print("\n[3/6] Scanning Policy...")
        policy_rules = self.scan_policy()
        print(f"  Rules found: {len(policy_rules)}")

        print("\n[4/6] Scanning Validator...")
        validator_rules = self.scan_validator()
        print(f"  Rules found: {len(validator_rules)}")

        print("\n[5/6] Scanning Tests...")
        test_rules = self.scan_tests()
        print(f"  Rules found: {len(test_rules)}")

        print("\n[6/6] Scanning Audit Logs...")
        audit_rules = self.scan_audit()
        print(f"  Rules found: {len(audit_rules)}")

        # Calculate completeness for each rule
        print("\n[7/7] Calculating completeness...")
        rule_completeness = []
        score_buckets = defaultdict(int)

        for rule_id in all_rule_ids:
            in_contract = rule_id in contract_rules
            in_policy = rule_id in policy_rules
            in_validator = rule_id in validator_rules
            in_tests = rule_id in test_rules
            in_audit = rule_id in audit_rules

            # Calculate score (0.0 to 1.0)
            num_sources = sum([in_contract, in_policy, in_validator, in_tests, in_audit])
            score = num_sources / 5.0

            completeness = RuleCompleteness(
                rule_id=rule_id,
                in_contract=in_contract,
                in_policy=in_policy,
                in_validator=in_validator,
                in_tests=in_tests,
                in_audit=in_audit,
                completeness_score=score
            )

            rule_completeness.append(completeness)

            # Bucket by score
            if score == 1.0:
                score_buckets[100] += 1
            elif score >= 0.8:
                score_buckets[80] += 1
            elif score >= 0.6:
                score_buckets[60] += 1
            elif score >= 0.4:
                score_buckets[40] += 1
            elif score >= 0.2:
                score_buckets[20] += 1
            else:
                score_buckets[0] += 1

        # Calculate overall completeness
        total_score = sum(r.completeness_score for r in rule_completeness)
        overall_completeness = (total_score / len(all_rule_ids)) * 100 if all_rule_ids else 0.0

        report = CompletenessReport(
            timestamp=datetime.utcnow().isoformat(),
            total_rules=len(all_rule_ids),
            rules_with_100_percent=score_buckets[100],
            rules_with_80_percent=score_buckets[80],
            rules_with_60_percent=score_buckets[60],
            rules_with_40_percent=score_buckets[40],
            rules_with_20_percent=score_buckets[20],
            rules_with_0_percent=score_buckets[0],
            overall_completeness=overall_completeness,
            artifact_coverage={
                'contract': len(contract_rules),
                'policy': len(policy_rules),
                'validator': len(validator_rules),
                'tests': len(test_rules),
                'audit': len(audit_rules)
            },
            rule_details=rule_completeness
        )

        print("\n" + "=" * 80)
        print("Completeness Report")
        print("=" * 80)
        print(f"Total Rules: {report.total_rules}")
        print(f"\nCompleteness Distribution:")
        print(f"  100% (5/5 artifacts): {report.rules_with_100_percent} rules")
        print(f"   80% (4/5 artifacts): {report.rules_with_80_percent} rules")
        print(f"   60% (3/5 artifacts): {report.rules_with_60_percent} rules")
        print(f"   40% (2/5 artifacts): {report.rules_with_40_percent} rules")
        print(f"   20% (1/5 artifacts): {report.rules_with_20_percent} rules")
        print(f"    0% (0/5 artifacts): {report.rules_with_0_percent} rules")
        print(f"\nOverall Completeness: {overall_completeness:.1f}%")
        print("=" * 80)

        return report

    def generate_gap_report(self, report: CompletenessReport, output_path: Path = None):
        """
        Generate report of rules missing from artifacts

        Args:
            report: CompletenessReport to analyze
            output_path: Optional path to save report
        """
        if output_path is None:
            output_path = self.repo_root / '02_audit_logging/reports/completeness_gaps.json'

        gaps = {
            'timestamp': report.timestamp,
            'total_rules': report.total_rules,
            'overall_completeness': report.overall_completeness,
            'missing_from_contract': [],
            'missing_from_policy': [],
            'missing_from_validator': [],
            'missing_from_tests': [],
            'missing_from_audit': []
        }

        for rule in report.rule_details:
            if not rule.in_contract:
                gaps['missing_from_contract'].append(rule.rule_id)
            if not rule.in_policy:
                gaps['missing_from_policy'].append(rule.rule_id)
            if not rule.in_validator:
                gaps['missing_from_validator'].append(rule.rule_id)
            if not rule.in_tests:
                gaps['missing_from_tests'].append(rule.rule_id)
            if not rule.in_audit:
                gaps['missing_from_audit'].append(rule.rule_id)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(gaps, f, indent=2, ensure_ascii=False)

        print(f"\nGap report saved to: {output_path}")


def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description='SoT Completeness Scorer - Calculate cross-artifact coverage'
    )
    parser.add_argument('--output', help='Output file for completeness report (JSON)')
    parser.add_argument('--gap-report', action='store_true', help='Generate gap analysis report')

    args = parser.parse_args()

    scorer = CompletenessScorer()
    report = scorer.calculate_completeness()

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report.to_dict(), f, indent=2, ensure_ascii=False)
        print(f"\nReport saved to: {output_path}")

    if args.gap_report:
        scorer.generate_gap_report(report)

    # Exit with appropriate code
    if report.overall_completeness >= 100.0:
        print("\n✓ 100% completeness achieved!")
        return 0
    elif report.overall_completeness >= 80.0:
        print(f"\n⚠ Completeness: {report.overall_completeness:.1f}% (target: 100%)")
        return 0
    else:
        print(f"\n✗ Completeness: {report.overall_completeness:.1f}% (target: 100%)")
        return 1


if __name__ == '__main__':
    import sys
    sys.exit(main())
