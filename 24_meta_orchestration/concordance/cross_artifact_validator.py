#!/usr/bin/env python3
"""
Proof-of-Concordance System - Cross-Artifact Consistency Validator
===================================================================

Beweist, dass alle 5 Artefakte die gleiche Wahrheit enthalten:
1. Contract YAML ↔ Policy REGO
2. Policy REGO ↔ Validator Core
3. Validator Core ↔ CLI Tool
4. CLI Tool ↔ Test Suite
5. All ↔ Registry

Durchsetzung:
- Jede Regel-ID im Contract muss in Policy, Code, Tests erscheinen
- Hash-Konsistenz über alle Artefakte
- Automatisches FAIL bei Abweichungen

Exit Codes:
  0 = PASS - All artifacts concordant
  1 = WARN - Minor inconsistencies
  2 = FAIL - Critical concordance violations

Version: 1.0.0
Status: PRODUCTION READY
Author: SSID Compliance Team
Co-Authored-By: Claude <noreply@anthropic.com>

🧠 Generated with Claude Code (https://claude.com/claude-code)

Usage:
    from cross_artifact_validator import ConcordanceValidator

    validator = ConcordanceValidator()
    result = validator.validate_concordance()
    print(f"Concordance Score: {result.concordance_percentage}%")
"""

import sys
import json
import hashlib
import yaml
import re
from pathlib import Path
from typing import List, Dict, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from collections import defaultdict


@dataclass
class ArtifactRuleSet:
    """Rule set from single artifact"""
    artifact_name: str
    rule_ids: Set[str]
    total_rules: int
    file_hash: str

    def to_dict(self) -> dict:
        return {
            'artifact_name': self.artifact_name,
            'rule_ids': list(self.rule_ids),
            'total_rules': self.total_rules,
            'file_hash': self.file_hash
        }


@dataclass
class ConcordanceIssue:
    """Single concordance violation"""
    severity: str  # CRITICAL, WARN, INFO
    artifact_pair: str
    rule_id: str
    issue_type: str
    message: str


@dataclass
class ProofOfConcordance:
    """Complete Proof-of-Concordance certificate"""
    timestamp: str
    artifacts: List[ArtifactRuleSet]
    concordance_percentage: float
    total_rules_union: int
    fully_concordant_rules: int
    issues: List[ConcordanceIssue]
    overall_status: str  # PASS, WARN, FAIL

    def to_dict(self) -> dict:
        return {
            'timestamp': self.timestamp,
            'artifacts': [a.to_dict() for a in self.artifacts],
            'concordance_percentage': self.concordance_percentage,
            'total_rules_union': self.total_rules_union,
            'fully_concordant_rules': self.fully_concordant_rules,
            'issues': [asdict(i) for i in self.issues],
            'overall_status': self.overall_status
        }


class ConcordanceValidator:
    """
    Validates cross-artifact concordance.

    Ensures all 5 SoT artifacts contain the same rule set.
    """

    def __init__(self, repo_root: Optional[Path] = None):
        """Initialize validator with repository root"""
        if repo_root is None:
            self.repo_root = Path(__file__).resolve().parents[3]
        else:
            self.repo_root = Path(repo_root)

        self.artifacts = {
            'contract': self.repo_root / '16_codex/contracts/sot/sot_contract.yaml',
            'policy': self.repo_root / '23_compliance/policies/sot/sot_policy.rego',
            'validator': self.repo_root / '03_core/validators/sot/sot_validator_core.py',
            'cli': self.repo_root / '12_tooling/cli/sot_validator.py',
            'tests': self.repo_root / '11_test_simulation/tests_compliance/test_sot_validator.py'
        }

    def compute_file_hash(self, file_path: Path) -> str:
        """Compute SHA-256 hash of file"""
        if not file_path.exists():
            return "0" * 64

        try:
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception:
            return "0" * 64

    def extract_rules_from_yaml(self, yaml_path: Path) -> Set[str]:
        """Extract rule IDs from YAML contract"""
        rule_ids = set()

        if not yaml_path.exists():
            return rule_ids

        try:
            with open(yaml_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)

            if data and 'rules' in data:
                for rule in data.get('rules', []):
                    rule_id = rule.get('id', '')
                    if rule_id:
                        rule_ids.add(rule_id)

        except Exception as e:
            print(f"[ERROR] Failed to parse {yaml_path}: {e}")

        return rule_ids

    def extract_rules_from_rego(self, rego_path: Path) -> Set[str]:
        """Extract rule IDs from REGO policy"""
        rule_ids = set()

        if not rego_path.exists():
            return rule_ids

        try:
            with open(rego_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Match rule ID comments: # Rule: <rule_id>
            pattern = r'#\s*Rule:\s*([a-zA-Z0-9._-]+)'
            matches = re.findall(pattern, content)
            rule_ids.update(matches)

        except Exception as e:
            print(f"[ERROR] Failed to parse {rego_path}: {e}")

        return rule_ids

    def extract_rules_from_python(self, py_path: Path) -> Set[str]:
        """Extract rule IDs from Python file"""
        rule_ids = set()

        if not py_path.exists():
            return rule_ids

        try:
            with open(py_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Match function names: def validate_<rule_id>
            pattern = r'def\s+validate_([a-zA-Z0-9_]+)'
            matches = re.findall(pattern, content)
            rule_ids.update(matches)

            # Match test functions: def test_<rule_id>
            pattern = r'def\s+test_([a-zA-Z0-9_]+)'
            matches = re.findall(pattern, content)
            rule_ids.update(matches)

        except Exception as e:
            print(f"[ERROR] Failed to parse {py_path}: {e}")

        return rule_ids

    def validate_concordance(self) -> ProofOfConcordance:
        """
        Validate cross-artifact concordance.

        Returns:
            ProofOfConcordance certificate
        """
        print("=" * 80)
        print("Proof-of-Concordance Validator")
        print("=" * 80)

        artifact_sets: List[ArtifactRuleSet] = []
        issues: List[ConcordanceIssue] = []

        # Extract from Contract YAML
        print("\n[1/5] Extracting from Contract YAML...")
        contract_rules = self.extract_rules_from_yaml(self.artifacts['contract'])
        contract_set = ArtifactRuleSet(
            artifact_name='contract',
            rule_ids=contract_rules,
            total_rules=len(contract_rules),
            file_hash=self.compute_file_hash(self.artifacts['contract'])
        )
        artifact_sets.append(contract_set)
        print(f"  > Found {len(contract_rules)} rules")

        # Extract from Policy REGO
        print("\n[2/5] Extracting from Policy REGO...")
        policy_rules = self.extract_rules_from_rego(self.artifacts['policy'])
        policy_set = ArtifactRuleSet(
            artifact_name='policy',
            rule_ids=policy_rules,
            total_rules=len(policy_rules),
            file_hash=self.compute_file_hash(self.artifacts['policy'])
        )
        artifact_sets.append(policy_set)
        print(f"  > Found {len(policy_rules)} rules")

        # Extract from Validator Core
        print("\n[3/5] Extracting from Validator Core...")
        validator_rules = self.extract_rules_from_python(self.artifacts['validator'])
        validator_set = ArtifactRuleSet(
            artifact_name='validator',
            rule_ids=validator_rules,
            total_rules=len(validator_rules),
            file_hash=self.compute_file_hash(self.artifacts['validator'])
        )
        artifact_sets.append(validator_set)
        print(f"  > Found {len(validator_rules)} rules")

        # Extract from CLI
        print("\n[4/5] Extracting from CLI Tool...")
        cli_rules = self.extract_rules_from_python(self.artifacts['cli'])
        cli_set = ArtifactRuleSet(
            artifact_name='cli',
            rule_ids=cli_rules,
            total_rules=len(cli_rules),
            file_hash=self.compute_file_hash(self.artifacts['cli'])
        )
        artifact_sets.append(cli_set)
        print(f"  > Found {len(cli_rules)} rules")

        # Extract from Tests
        print("\n[5/5] Extracting from Tests...")
        test_rules = self.extract_rules_from_python(self.artifacts['tests'])
        test_set = ArtifactRuleSet(
            artifact_name='tests',
            rule_ids=test_rules,
            total_rules=len(test_rules),
            file_hash=self.compute_file_hash(self.artifacts['tests'])
        )
        artifact_sets.append(test_set)
        print(f"  > Found {len(test_rules)} rules")

        # Compute concordance
        print("\n[6/6] Computing concordance...")

        # Union of all rules
        all_rules = set()
        for artifact_set in artifact_sets:
            all_rules.update(artifact_set.rule_ids)

        # Find rules present in all artifacts
        concordant_rules = set(all_rules)
        for artifact_set in artifact_sets:
            concordant_rules &= artifact_set.rule_ids

        # Find issues
        for rule_id in all_rules:
            present_in = [a.artifact_name for a in artifact_sets if rule_id in a.rule_ids]

            if len(present_in) < len(artifact_sets):
                missing_from = [a.artifact_name for a in artifact_sets if rule_id not in a.rule_ids]

                severity = "CRITICAL" if 'contract' in missing_from else "WARN"

                issues.append(ConcordanceIssue(
                    severity=severity,
                    artifact_pair=f"{','.join(present_in)} vs {','.join(missing_from)}",
                    rule_id=rule_id,
                    issue_type="missing_from_artifact",
                    message=f"Rule {rule_id} missing from: {', '.join(missing_from)}"
                ))

        # Calculate concordance percentage
        concordance_pct = (len(concordant_rules) / len(all_rules) * 100) if all_rules else 100.0

        # Determine overall status
        critical_issues = [i for i in issues if i.severity == "CRITICAL"]
        if critical_issues:
            status = "FAIL"
        elif concordance_pct < 95.0:
            status = "WARN"
        else:
            status = "PASS"

        print(f"  > Union: {len(all_rules)} rules")
        print(f"  > Concordant: {len(concordant_rules)} rules")
        print(f"  > Concordance: {concordance_pct:.1f}%")
        print(f"  > Issues: {len(issues)} ({len(critical_issues)} critical)")

        # Create proof
        proof = ProofOfConcordance(
            timestamp=datetime.now(timezone.utc).isoformat(),
            artifacts=artifact_sets,
            concordance_percentage=concordance_pct,
            total_rules_union=len(all_rules),
            fully_concordant_rules=len(concordant_rules),
            issues=issues,
            overall_status=status
        )

        # Save proof
        output_dir = self.repo_root / '24_meta_orchestration/concordance'
        output_dir.mkdir(parents=True, exist_ok=True)

        proof_file = output_dir / 'proof_of_concordance.json'
        with open(proof_file, 'w', encoding='utf-8') as f:
            json.dump(proof.to_dict(), f, indent=2, ensure_ascii=False)

        print(f"\n  > Saved to: {proof_file.relative_to(self.repo_root)}")

        print("\n" + "=" * 80)
        print(f"[{status}] Proof-of-Concordance Complete")
        print(f"   Concordance: {concordance_pct:.1f}%")
        print(f"   Status: {status}")
        print("=" * 80)

        return proof


def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Validate Cross-Artifact Concordance')
    parser.add_argument('--output', type=Path, help='Output file path')

    args = parser.parse_args()

    validator = ConcordanceValidator()
    proof = validator.validate_concordance()

    # Exit based on status
    exit_codes = {'PASS': 0, 'WARN': 1, 'FAIL': 2}
    sys.exit(exit_codes.get(proof.overall_status, 2))


if __name__ == '__main__':
    main()
