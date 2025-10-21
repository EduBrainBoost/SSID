#!/usr/bin/env python3
"""
SSID Master Rules Coverage Checker v1.0
========================================
Prüft, ob alle extrahierten Master-Regeln in den 5 SoT-Artefakten implementiert sind.

Usage:
    python coverage_checker.py --rules master_rules.yaml --repo /path/to/ssid

Exit Codes:
    0: 100% Coverage (alle Regeln in allen 5 Artefakten)
    1: Coverage-Lücken gefunden
    2: Validierungsfehler
"""

import argparse
import hashlib
import json
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Optional

import yaml


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class Rule:
    """Repräsentiert eine extrahierte Master-Regel."""
    rule_id: str
    category: str
    type: str  # MUST, NIEMALS
    rule_text: str
    source_section: str
    severity: str = "HIGH"
    implementation_requirements: List[str] = field(default_factory=list)


@dataclass
class CoverageResult:
    """Ergebnis der Coverage-Prüfung für eine Regel."""
    rule_id: str
    rule_text: str
    contract_coverage: bool = False
    core_coverage: bool = False
    policy_coverage: bool = False
    cli_coverage: bool = False
    test_coverage: bool = False
    
    contract_evidence: List[str] = field(default_factory=list)
    core_evidence: List[str] = field(default_factory=list)
    policy_evidence: List[str] = field(default_factory=list)
    cli_evidence: List[str] = field(default_factory=list)
    test_evidence: List[str] = field(default_factory=list)
    
    @property
    def full_coverage(self) -> bool:
        """Prüft, ob Regel in allen 5 Artefakten implementiert ist."""
        return all([
            self.contract_coverage,
            self.core_coverage,
            self.policy_coverage,
            self.cli_coverage,
            self.test_coverage
        ])
    
    @property
    def coverage_percentage(self) -> float:
        """Berechnet Coverage-Prozentsatz (0-100)."""
        count = sum([
            self.contract_coverage,
            self.core_coverage,
            self.policy_coverage,
            self.cli_coverage,
            self.test_coverage
        ])
        return (count / 5) * 100


@dataclass
class CoverageReport:
    """Vollständiger Coverage-Report."""
    timestamp: str
    total_rules: int
    full_coverage_count: int
    partial_coverage_count: int
    no_coverage_count: int
    overall_percentage: float
    results: List[CoverageResult]
    missing_artifacts: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


# ============================================================================
# RULE LOADER
# ============================================================================

class RuleLoader:
    """Lädt Master-Regeln aus YAML."""
    
    @staticmethod
    def load(yaml_path: Path) -> List[Rule]:
        """Lädt und parsed Regeln aus YAML-Datei."""
        with open(yaml_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        rules = []
        
        # Iteriere durch alle Kategorien
        for category_key in [
            'architecture_rules',
            'critical_policies',
            'versioning_governance',
            'chart_structure',
            'manifest_structure',
            'core_principles',
            'consolidated_extensions',
            'technology_standards',
            'deployment_cicd',
            'matrix_registry'
        ]:
            if category_key not in data:
                continue
            
            for rule_id, rule_data in data[category_key].items():
                rule = Rule(
                    rule_id=rule_id,
                    category=rule_data.get('category', 'Unknown'),
                    type=rule_data.get('type', 'MUST'),
                    rule_text=rule_data.get('rule', ''),
                    source_section=rule_data.get('source_section', ''),
                    severity=rule_data.get('severity', 'HIGH'),
                    implementation_requirements=rule_data.get('implementation_requirements', [])
                )
                rules.append(rule)
        
        return rules


# ============================================================================
# ARTIFACT ANALYZERS
# ============================================================================

class ContractAnalyzer:
    """Analysiert Contract Definitions (OpenAPI + JSON-Schema)."""
    
    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.contracts: List[Path] = []
        self.schemas: List[Path] = []
        self._scan()
    
    def _scan(self):
        """Scannt Repository nach Contract-Dateien."""
        # Finde alle OpenAPI-Specs
        self.contracts = list(self.repo_path.rglob("contracts/*.openapi.yaml"))
        # Finde alle JSON-Schemas
        self.schemas = list(self.repo_path.rglob("contracts/schemas/*.schema.json"))
    
    def check_coverage(self, rule: Rule) -> tuple[bool, List[str]]:
        """Prüft, ob Regel in Contracts abgebildet ist."""
        evidence = []
        
        # Suche nach Keywords in OpenAPI-Specs
        keywords = self._extract_keywords(rule)
        
        for contract_file in self.contracts:
            try:
                with open(contract_file, 'r', encoding='utf-8') as f:
                    content = f.read().lower()
                    if any(keyword.lower() in content for keyword in keywords):
                        evidence.append(f"Contract: {contract_file.name}")
            except:
                pass
        
        # Suche in JSON-Schemas
        for schema_file in self.schemas:
            try:
                with open(schema_file, 'r', encoding='utf-8') as f:
                    content = f.read().lower()
                    if any(keyword.lower() in content for keyword in keywords):
                        evidence.append(f"Schema: {schema_file.name}")
            except:
                pass
        
        return len(evidence) > 0, evidence
    
    def _extract_keywords(self, rule: Rule) -> List[str]:
        """Extrahiert Suchbegriffe aus Regel."""
        keywords = []
        
        # Keywords aus Implementation Requirements
        for req in rule.implementation_requirements:
            # Extrahiere Begriffe in Quotes
            quoted = re.findall(r'["\']([^"\']+)["\']', req)
            keywords.extend(quoted)
        
        # Spezifische Keywords basierend auf Regel-Text
        if "pii" in rule.rule_text.lower():
            keywords.extend(["pii", "personal", "data"])
        if "hash" in rule.rule_text.lower():
            keywords.extend(["hash", "sha256", "sha3"])
        if "identity" in rule.rule_text.lower():
            keywords.extend(["identity", "did", "credential"])
        
        return keywords


class CoreLogicAnalyzer:
    """Analysiert Core Logic (Python/Rust Code)."""
    
    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.source_files: List[Path] = []
        self._scan()
    
    def _scan(self):
        """Scannt nach Source-Code-Dateien."""
        # Python
        self.source_files.extend(self.repo_path.rglob("implementations/*/src/**/*.py"))
        # Rust
        self.source_files.extend(self.repo_path.rglob("implementations/*/src/**/*.rs"))
    
    def check_coverage(self, rule: Rule) -> tuple[bool, List[str]]:
        """Prüft, ob Regel in Core Logic implementiert ist."""
        evidence = []
        keywords = self._extract_keywords(rule)
        
        for source_file in self.source_files:
            try:
                with open(source_file, 'r', encoding='utf-8') as f:
                    content = f.read().lower()
                    if any(keyword.lower() in content for keyword in keywords):
                        evidence.append(f"Source: {source_file.relative_to(self.repo_path)}")
            except:
                pass
        
        return len(evidence) > 0, evidence
    
    def _extract_keywords(self, rule: Rule) -> List[str]:
        """Extrahiert Code-relevante Keywords."""
        keywords = []
        
        # Non-Custodial
        if "pii" in rule.rule_text.lower() or "non-custodial" in rule.rule_text.lower():
            keywords.extend(["pii_detector", "hash_only", "no_raw_storage"])
        
        # Hash-based
        if "hash" in rule.rule_text.lower():
            keywords.extend(["sha3", "sha256", "hashlib", "pepper"])
        
        # GDPR
        if "gdpr" in rule.rule_text.lower():
            keywords.extend(["erasure", "portability", "redaction"])
        
        # Bias
        if "bias" in rule.rule_text.lower():
            keywords.extend(["bias", "fairness", "demographic_parity"])
        
        return keywords


class PolicyEnforcementAnalyzer:
    """Analysiert Policy Enforcement (OPA Rego)."""
    
    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.policy_files: List[Path] = []
        self._scan()
    
    def _scan(self):
        """Scannt nach Policy-Dateien."""
        # OPA Rego
        self.policy_files.extend(self.repo_path.rglob("23_compliance/opa/**/*.rego"))
        # YAML Policies
        self.policy_files.extend(self.repo_path.rglob("policies/*.yaml"))
        # Semgrep Rules
        self.policy_files.extend(self.repo_path.rglob("**/*.semgrep.yaml"))
    
    def check_coverage(self, rule: Rule) -> tuple[bool, List[str]]:
        """Prüft, ob Regel als Policy enforced wird."""
        evidence = []
        keywords = self._extract_keywords(rule)
        
        for policy_file in self.policy_files:
            try:
                with open(policy_file, 'r', encoding='utf-8') as f:
                    content = f.read().lower()
                    if any(keyword.lower() in content for keyword in keywords):
                        evidence.append(f"Policy: {policy_file.relative_to(self.repo_path)}")
            except:
                pass
        
        return len(evidence) > 0, evidence
    
    def _extract_keywords(self, rule: Rule) -> List[str]:
        """Extrahiert Policy-relevante Keywords."""
        keywords = []
        
        if rule.type == "NIEMALS":
            keywords.append("deny")
        
        if "pii" in rule.rule_text.lower():
            keywords.extend(["pii", "deny_pii_storage", "no_raw_pii"])
        
        if "secrets" in rule.rule_text.lower():
            keywords.extend(["secrets", "vault", "no_plaintext_secrets"])
        
        if "semver" in rule.rule_text.lower():
            keywords.extend(["semver", "version", "breaking_change"])
        
        return keywords


class CLIValidatorAnalyzer:
    """Analysiert CLI Validation."""
    
    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.cli_files: List[Path] = []
        self._scan()
    
    def _scan(self):
        """Scannt nach CLI-Dateien."""
        cli_path = self.repo_path / "12_tooling" / "cli"
        if cli_path.exists():
            self.cli_files = list(cli_path.rglob("**/*.py"))
    
    def check_coverage(self, rule: Rule) -> tuple[bool, List[str]]:
        """Prüft, ob Regel im CLI validiert wird."""
        evidence = []
        keywords = self._extract_keywords(rule)
        
        for cli_file in self.cli_files:
            try:
                with open(cli_file, 'r', encoding='utf-8') as f:
                    content = f.read().lower()
                    if any(keyword.lower() in content for keyword in keywords):
                        evidence.append(f"CLI: {cli_file.relative_to(self.repo_path)}")
            except:
                pass
        
        return len(evidence) > 0, evidence
    
    def _extract_keywords(self, rule: Rule) -> List[str]:
        """Extrahiert CLI-relevante Keywords."""
        keywords = []
        
        # Strukturregeln
        if "ordner" in rule.rule_text.lower() or "root" in rule.rule_text.lower():
            keywords.extend(["validate_structure", "check_roots", "count_shards"])
        
        # Naming
        if "format" in rule.rule_text.lower() or "naming" in rule.category.lower():
            keywords.extend(["validate_naming", "regex", "format_check"])
        
        # Matrix
        if "384" in rule.rule_text or "24×16" in rule.rule_text:
            keywords.extend(["matrix", "384", "chart_count"])
        
        return keywords


class TestSuiteAnalyzer:
    """Analysiert Test Suites."""
    
    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.test_files: List[Path] = []
        self._scan()
    
    def _scan(self):
        """Scannt nach Test-Dateien."""
        # Unit Tests
        self.test_files.extend(self.repo_path.rglob("**/tests/**/*.py"))
        # Contract Tests
        self.test_files.extend(self.repo_path.rglob("conformance/**/*.py"))
        self.test_files.extend(self.repo_path.rglob("conformance/**/*.yaml"))
    
    def check_coverage(self, rule: Rule) -> tuple[bool, List[str]]:
        """Prüft, ob Regel getestet wird."""
        evidence = []
        keywords = self._extract_keywords(rule)
        
        for test_file in self.test_files:
            try:
                with open(test_file, 'r', encoding='utf-8') as f:
                    content = f.read().lower()
                    if any(keyword.lower() in content for keyword in keywords):
                        evidence.append(f"Test: {test_file.relative_to(self.repo_path)}")
            except:
                pass
        
        return len(evidence) > 0, evidence
    
    def _extract_keywords(self, rule: Rule) -> List[str]:
        """Extrahiert Test-relevante Keywords."""
        keywords = []
        
        # Test-Namen basierend auf Regel
        if "pii" in rule.rule_text.lower():
            keywords.extend(["test_pii", "test_no_pii_storage"])
        
        if "hash" in rule.rule_text.lower():
            keywords.extend(["test_hash", "test_sha256"])
        
        if "384" in rule.rule_text or "matrix" in rule.rule_text.lower():
            keywords.extend(["test_matrix", "test_chart_count"])
        
        # Contract Tests
        keywords.extend(["contract_test", "conformance"])
        
        return keywords


# ============================================================================
# COVERAGE CHECKER
# ============================================================================

class CoverageChecker:
    """Hauptklasse für Coverage-Prüfung."""
    
    def __init__(self, rules_yaml: Path, repo_path: Path):
        self.rules = RuleLoader.load(rules_yaml)
        self.repo_path = repo_path
        
        # Initialisiere Analyzer
        self.contract_analyzer = ContractAnalyzer(repo_path)
        self.core_analyzer = CoreLogicAnalyzer(repo_path)
        self.policy_analyzer = PolicyEnforcementAnalyzer(repo_path)
        self.cli_analyzer = CLIValidatorAnalyzer(repo_path)
        self.test_analyzer = TestSuiteAnalyzer(repo_path)
    
    def run(self) -> CoverageReport:
        """Führt vollständige Coverage-Prüfung durch."""
        results = []
        
        print(f"\n🔍 Checking coverage for {len(self.rules)} rules...")
        
        for i, rule in enumerate(self.rules, 1):
            print(f"[{i}/{len(self.rules)}] {rule.rule_id}: {rule.rule_text[:60]}...")
            
            result = CoverageResult(
                rule_id=rule.rule_id,
                rule_text=rule.rule_text
            )
            
            # Check Contract Coverage
            result.contract_coverage, result.contract_evidence = \
                self.contract_analyzer.check_coverage(rule)
            
            # Check Core Logic Coverage
            result.core_coverage, result.core_evidence = \
                self.core_analyzer.check_coverage(rule)
            
            # Check Policy Enforcement Coverage
            result.policy_coverage, result.policy_evidence = \
                self.policy_analyzer.check_coverage(rule)
            
            # Check CLI Validation Coverage
            result.cli_coverage, result.cli_evidence = \
                self.cli_analyzer.check_coverage(rule)
            
            # Check Test Coverage
            result.test_coverage, result.test_evidence = \
                self.test_analyzer.check_coverage(rule)
            
            results.append(result)
        
        # Berechne Statistiken
        full_coverage = sum(1 for r in results if r.full_coverage)
        partial_coverage = sum(1 for r in results if 0 < r.coverage_percentage < 100)
        no_coverage = sum(1 for r in results if r.coverage_percentage == 0)
        
        overall_percentage = sum(r.coverage_percentage for r in results) / len(results)
        
        report = CoverageReport(
            timestamp=datetime.now().isoformat(),
            total_rules=len(self.rules),
            full_coverage_count=full_coverage,
            partial_coverage_count=partial_coverage,
            no_coverage_count=no_coverage,
            overall_percentage=overall_percentage,
            results=results
        )
        
        return report


# ============================================================================
# REPORT GENERATOR
# ============================================================================

class ReportGenerator:
    """Generiert Coverage-Reports."""
    
    @staticmethod
    def generate_console_report(report: CoverageReport):
        """Gibt Report auf Console aus."""
        print("\n" + "="*80)
        print("SSID MASTER RULES COVERAGE REPORT")
        print("="*80)
        print(f"Timestamp: {report.timestamp}")
        print(f"Total Rules: {report.total_rules}")
        print()
        print(f"✅ Full Coverage:    {report.full_coverage_count:3d} ({report.full_coverage_count/report.total_rules*100:.1f}%)")
        print(f"⚠️  Partial Coverage: {report.partial_coverage_count:3d} ({report.partial_coverage_count/report.total_rules*100:.1f}%)")
        print(f"❌ No Coverage:      {report.no_coverage_count:3d} ({report.no_coverage_count/report.total_rules*100:.1f}%)")
        print()
        print(f"📊 Overall Coverage: {report.overall_percentage:.1f}%")
        print("="*80)
        
        if report.warnings:
            print("\n⚠️  WARNINGS:")
            for warning in report.warnings:
                print(f"  - {warning}")
        
        print("\n📋 DETAILED RESULTS:\n")
        
        for result in report.results:
            if not result.full_coverage:
                print(f"\n🔴 {result.rule_id} - Coverage: {result.coverage_percentage:.0f}%")
                print(f"   Rule: {result.rule_text}")
                print(f"   Contract:  {'✅' if result.contract_coverage else '❌'}")
                print(f"   Core:      {'✅' if result.core_coverage else '❌'}")
                print(f"   Policy:    {'✅' if result.policy_coverage else '❌'}")
                print(f"   CLI:       {'✅' if result.cli_coverage else '❌'}")
                print(f"   Test:      {'✅' if result.test_coverage else '❌'}")
    
    @staticmethod
    def generate_json_report(report: CoverageReport, output_path: Path):
        """Speichert Report als JSON."""
        report_dict = {
            "timestamp": report.timestamp,
            "summary": {
                "total_rules": report.total_rules,
                "full_coverage": report.full_coverage_count,
                "partial_coverage": report.partial_coverage_count,
                "no_coverage": report.no_coverage_count,
                "overall_percentage": report.overall_percentage
            },
            "warnings": report.warnings,
            "missing_artifacts": report.missing_artifacts,
            "results": [
                {
                    "rule_id": r.rule_id,
                    "rule_text": r.rule_text,
                    "coverage_percentage": r.coverage_percentage,
                    "full_coverage": r.full_coverage,
                    "artifacts": {
                        "contract": {
                            "covered": r.contract_coverage,
                            "evidence": r.contract_evidence
                        },
                        "core": {
                            "covered": r.core_coverage,
                            "evidence": r.core_evidence
                        },
                        "policy": {
                            "covered": r.policy_coverage,
                            "evidence": r.policy_evidence
                        },
                        "cli": {
                            "covered": r.cli_coverage,
                            "evidence": r.cli_evidence
                        },
                        "test": {
                            "covered": r.test_coverage,
                            "evidence": r.test_evidence
                        }
                    }
                }
                for r in report.results
            ]
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report_dict, f, indent=2, ensure_ascii=False)
        
        # SHA256-Hash berechnen
        with open(output_path, 'rb') as f:
            sha256 = hashlib.sha256(f.read()).hexdigest()
        
        print(f"\n📄 JSON Report saved: {output_path}")
        print(f"🔐 SHA256: {sha256}")
        
        # Hash-File erstellen
        hash_file = output_path.with_suffix('.json.sha256')
        with open(hash_file, 'w') as f:
            f.write(f"{sha256}  {output_path.name}\n")


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="SSID Master Rules Coverage Checker"
    )
    parser.add_argument(
        '--rules',
        type=Path,
        required=True,
        help='Path to master_rules.yaml'
    )
    parser.add_argument(
        '--repo',
        type=Path,
        required=True,
        help='Path to SSID repository root'
    )
    parser.add_argument(
        '--output',
        type=Path,
        default=Path('coverage_report.json'),
        help='Output path for JSON report'
    )
    parser.add_argument(
        '--fail-under',
        type=float,
        default=100.0,
        help='Minimum required overall coverage percentage (default: 100.0)'
    )
    
    args = parser.parse_args()
    
    # Validierung
    if not args.rules.exists():
        print(f"❌ Error: Rules file not found: {args.rules}", file=sys.stderr)
        sys.exit(2)
    
    if not args.repo.exists():
        print(f"❌ Error: Repository path not found: {args.repo}", file=sys.stderr)
        sys.exit(2)
    
    # Coverage Check
    checker = CoverageChecker(args.rules, args.repo)
    report = checker.run()
    
    # Reports generieren
    ReportGenerator.generate_console_report(report)
    ReportGenerator.generate_json_report(report, args.output)
    
    # Exit Code basierend auf Coverage
    if report.overall_percentage < args.fail_under:
        print(f"\n❌ FAIL: Coverage {report.overall_percentage:.1f}% below threshold {args.fail_under}%")
        sys.exit(1)
    else:
        print(f"\n✅ PASS: Coverage {report.overall_percentage:.1f}% meets threshold {args.fail_under}%")
        sys.exit(0)


if __name__ == "__main__":
    main()
