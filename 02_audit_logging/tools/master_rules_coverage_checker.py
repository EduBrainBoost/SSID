#!/usr/bin/env python3
"""
SSID Master Rules Coverage Checker v2.0.0
==========================================
Prüft, ob alle extrahierten Master-Regeln in den 5 SoT-Artefakten implementiert sind.

Usage:
    python master_rules_coverage_checker.py --rules master_rules.yaml --repo . --output coverage_report.json

Exit Codes:
    0 - 100% Coverage erreicht
    1 - Coverage-Lücken gefunden
    2 - Kritische Fehler (Datei nicht gefunden, Parse-Fehler etc.)
"""

import argparse
import json
import sys
import hashlib
import yaml
from pathlib import Path
from typing import Dict, List, Set, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
from collections import defaultdict


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class RuleCoverage:
    """Coverage für eine einzelne Regel"""
    rule_id: str
    category: str
    severity: str
    rule_text: str
    coverage: Dict[str, bool]  # artefact -> covered
    missing_in: List[str]
    evidence: Dict[str, List[str]]  # artefact -> file paths where found


@dataclass
class CoverageReport:
    """Gesamter Coverage-Report"""
    timestamp: str
    rules_yaml_sha256: str
    repo_path: str
    total_rules: int
    rules_with_100_coverage: int
    rules_with_gaps: int
    overall_coverage_percent: float
    coverage_by_artefact: Dict[str, float]
    rules: List[RuleCoverage]
    gaps: List[Dict[str, any]]


# ============================================================================
# SOT ARTEFAKT SCANNERS
# ============================================================================

class ContractScanner:
    """Scannt OpenAPI/JSON-Schema Contracts"""

    def __init__(self, repo_path: Path):
        self.repo_path = repo_path

    def find_contracts(self) -> List[Path]:
        """Findet alle Contract-Dateien"""
        contracts = []
        contracts.extend(self.repo_path.glob("**/contracts/*.openapi.yaml"))
        contracts.extend(self.repo_path.glob("**/contracts/schemas/*.schema.json"))
        return contracts

    def scan_for_rule(self, rule_id: str, rule_data: dict) -> Tuple[bool, List[str]]:
        """Prüft, ob eine Regel in Contracts nachweisbar ist"""
        contracts = self.find_contracts()
        evidence = []

        # Extract expected contract patterns from sot_mapping
        if "sot_mapping" not in rule_data:
            return False, []

        contract_mapping = rule_data["sot_mapping"].get("contract", "")
        if not contract_mapping:
            return False, []

        # Simple heuristic: search for keywords in contract files
        keywords = self._extract_keywords(contract_mapping)

        for contract_file in contracts:
            try:
                content = contract_file.read_text(encoding="utf-8")
                if any(kw.lower() in content.lower() for kw in keywords):
                    evidence.append(str(contract_file.relative_to(self.repo_path)))
            except Exception as e:
                print(f"Warning: Could not read {contract_file}: {e}", file=sys.stderr)

        return len(evidence) > 0, evidence

    @staticmethod
    def _extract_keywords(mapping_str: str) -> List[str]:
        """Extrahiert Keywords aus sot_mapping.contract"""
        # Example: "schema: pii_constraints.schema.json forbids pii_storage"
        # Keywords: ["pii_constraints", "pii_storage"]
        import re
        words = re.findall(r'\b\w{4,}\b', mapping_str)  # words with 4+ chars
        return [w for w in words if w not in ["schema", "with", "pattern", "requires", "forbids", "json", "yaml"]]


class CoreLogicScanner:
    """Scannt Core Logic (Python/Rust Implementations)"""

    def __init__(self, repo_path: Path):
        self.repo_path = repo_path

    def find_source_files(self) -> List[Path]:
        """Findet alle Source-Code-Dateien"""
        sources = []
        sources.extend(self.repo_path.glob("**/implementations/*/src/**/*.py"))
        sources.extend(self.repo_path.glob("**/implementations/*/src/**/*.rs"))
        sources.extend(self.repo_path.glob("03_core/**/*.py"))
        return sources

    def scan_for_rule(self, rule_id: str, rule_data: dict) -> Tuple[bool, List[str]]:
        """Prüft, ob eine Regel in Core Logic implementiert ist"""
        sources = self.find_source_files()
        evidence = []

        if "sot_mapping" not in rule_data:
            return False, []

        core_mapping = rule_data["sot_mapping"].get("core", "")
        if not core_mapping:
            return False, []

        keywords = self._extract_keywords(core_mapping)

        for source_file in sources:
            try:
                content = source_file.read_text(encoding="utf-8")
                if any(kw in content for kw in keywords):  # case-sensitive for code
                    evidence.append(str(source_file.relative_to(self.repo_path)))
            except Exception as e:
                print(f"Warning: Could not read {source_file}: {e}", file=sys.stderr)

        return len(evidence) > 0, evidence

    @staticmethod
    def _extract_keywords(mapping_str: str) -> List[str]:
        """Extrahiert Function/Class-Namen aus sot_mapping.core"""
        # Example: "pii_detector.py: runtime_check(), raise on violation"
        # Keywords: ["pii_detector", "runtime_check"]
        import re
        # Extract Python/Rust identifiers
        identifiers = re.findall(r'\b[a-z_][a-z0-9_]{3,}\b', mapping_str)
        return [i for i in identifiers if i not in ["assert", "raise", "return", "import"]]


class PolicyScanner:
    """Scannt OPA Policies & Semgrep Rules"""

    def __init__(self, repo_path: Path):
        self.repo_path = repo_path

    def find_policy_files(self) -> List[Path]:
        """Findet alle Policy-Dateien"""
        policies = []
        policies.extend(self.repo_path.glob("**/policies/*.yaml"))
        policies.extend(self.repo_path.glob("23_compliance/opa/*.rego"))
        policies.extend(self.repo_path.glob("**/policies/*.rego"))
        return policies

    def scan_for_rule(self, rule_id: str, rule_data: dict) -> Tuple[bool, List[str]]:
        """Prüft, ob eine Regel als Policy existiert"""
        policies = self.find_policy_files()
        evidence = []

        if "sot_mapping" not in rule_data:
            return False, []

        policy_mapping = rule_data["sot_mapping"].get("policy", "")
        if not policy_mapping:
            return False, []

        keywords = self._extract_keywords(policy_mapping)

        for policy_file in policies:
            try:
                content = policy_file.read_text(encoding="utf-8")
                if any(kw in content for kw in keywords):
                    evidence.append(str(policy_file.relative_to(self.repo_path)))
            except Exception as e:
                print(f"Warning: Could not read {policy_file}: {e}", file=sys.stderr)

        return len(evidence) > 0, evidence

    @staticmethod
    def _extract_keywords(mapping_str: str) -> List[str]:
        """Extrahiert Policy-Namen/Rules"""
        # Example: "opa/pii.rego: deny[msg] { pii_storage }"
        # Keywords: ["deny", "pii_storage"]
        import re
        identifiers = re.findall(r'\b[a-z_][a-z0-9_]{3,}\b', mapping_str)
        return [i for i in identifiers if i not in ["rego", "yaml", "msg"]]


class CLIScanner:
    """Scannt CLI-Tools (12_tooling/cli)"""

    def __init__(self, repo_path: Path):
        self.repo_path = repo_path

    def find_cli_files(self) -> List[Path]:
        """Findet alle CLI-Dateien"""
        cli_files = []
        cli_files.extend(self.repo_path.glob("12_tooling/cli/**/*.py"))
        cli_files.extend(self.repo_path.glob("12_tooling/cli/**/*.sh"))
        return cli_files

    def scan_for_rule(self, rule_id: str, rule_data: dict) -> Tuple[bool, List[str]]:
        """Prüft, ob eine Regel im CLI validiert wird"""
        cli_files = self.find_cli_files()
        evidence = []

        if "sot_mapping" not in rule_data:
            return False, []

        cli_mapping = rule_data["sot_mapping"].get("cli", "")
        if not cli_mapping:
            return False, []

        keywords = self._extract_keywords(cli_mapping)

        for cli_file in cli_files:
            try:
                content = cli_file.read_text(encoding="utf-8")
                if any(kw in content for kw in keywords):
                    evidence.append(str(cli_file.relative_to(self.repo_path)))
            except Exception as e:
                print(f"Warning: Could not read {cli_file}: {e}", file=sys.stderr)

        return len(evidence) > 0, evidence

    @staticmethod
    def _extract_keywords(mapping_str: str) -> List[str]:
        """Extrahiert CLI-Kommando-Namen"""
        # Example: "cli validate --naming: root pattern check"
        # Keywords: ["validate", "naming"]
        import re
        identifiers = re.findall(r'\b[a-z][a-z0-9-]{3,}\b', mapping_str)
        return [i for i in identifiers if i not in ["cli", "exit", "code"]]


class TestScanner:
    """Scannt Test Suites (conformance + unit/integration)"""

    def __init__(self, repo_path: Path):
        self.repo_path = repo_path

    def find_test_files(self) -> List[Path]:
        """Findet alle Test-Dateien"""
        tests = []
        tests.extend(self.repo_path.glob("**/conformance/**/*.py"))
        tests.extend(self.repo_path.glob("**/tests/**/*.py"))
        tests.extend(self.repo_path.glob("**/test_*.py"))
        return tests

    def scan_for_rule(self, rule_id: str, rule_data: dict) -> Tuple[bool, List[str]]:
        """Prüft, ob eine Regel durch Tests abgedeckt ist"""
        tests = self.find_test_files()
        evidence = []

        if "sot_mapping" not in rule_data:
            return False, []

        test_mapping = rule_data["sot_mapping"].get("test", "")
        if not test_mapping:
            return False, []

        keywords = self._extract_keywords(test_mapping)

        for test_file in tests:
            try:
                content = test_file.read_text(encoding="utf-8")
                if any(kw in content for kw in keywords):
                    evidence.append(str(test_file.relative_to(self.repo_path)))
            except Exception as e:
                print(f"Warning: Could not read {test_file}: {e}", file=sys.stderr)

        return len(evidence) > 0, evidence

    @staticmethod
    def _extract_keywords(mapping_str: str) -> List[str]:
        """Extrahiert Test-Funktionsnamen"""
        # Example: "test_pii.py::test_no_pii_storage()"
        # Keywords: ["test_no_pii_storage"]
        import re
        identifiers = re.findall(r'test_[a-z0-9_]+', mapping_str)
        return identifiers


# ============================================================================
# COVERAGE CHECKER ENGINE
# ============================================================================

class CoverageChecker:
    """Hauptklasse für Coverage-Checking"""

    def __init__(self, rules_yaml_path: Path, repo_path: Path):
        self.rules_yaml_path = rules_yaml_path
        self.repo_path = repo_path
        self.rules_data = self._load_rules()
        self.scanners = {
            "contract": ContractScanner(repo_path),
            "core": CoreLogicScanner(repo_path),
            "policy": PolicyScanner(repo_path),
            "cli": CLIScanner(repo_path),
            "test": TestScanner(repo_path),
        }

    def _load_rules(self) -> dict:
        """Lädt master_rules.yaml"""
        with open(self.rules_yaml_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def _compute_sha256(self, file_path: Path) -> str:
        """Berechnet SHA256-Hash einer Datei"""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

    def check_coverage(self) -> CoverageReport:
        """Führt vollständigen Coverage-Check durch"""
        rules_sha = self._compute_sha256(self.rules_yaml_path)
        timestamp = datetime.utcnow().isoformat() + "Z"

        all_rules_coverage = []
        coverage_by_artefact = defaultdict(int)
        total_rules = 0

        # Iterate through all rule categories
        for category_name, category_rules in self.rules_data.items():
            if not isinstance(category_rules, dict):
                continue
            if category_name in ["metadata", "sot_artefacts", "statistics", "coverage_strategy"]:
                continue

            for rule_id, rule_data in category_rules.items():
                if not isinstance(rule_data, dict):
                    continue

                total_rules += 1
                coverage = {}
                evidence = {}
                missing_in = []

                # Check coverage in all 5 artefacts
                for artefact_name, scanner in self.scanners.items():
                    covered, proof = scanner.scan_for_rule(rule_id, rule_data)
                    coverage[artefact_name] = covered
                    evidence[artefact_name] = proof

                    if covered:
                        coverage_by_artefact[artefact_name] += 1
                    else:
                        missing_in.append(artefact_name)

                rule_coverage = RuleCoverage(
                    rule_id=rule_id,
                    category=rule_data.get("category", "UNKNOWN"),
                    severity=rule_data.get("severity", "MEDIUM"),
                    rule_text=rule_data.get("rule", ""),
                    coverage=coverage,
                    missing_in=missing_in,
                    evidence=evidence
                )
                all_rules_coverage.append(rule_coverage)

        # Calculate statistics
        rules_with_100_coverage = sum(1 for r in all_rules_coverage if len(r.missing_in) == 0)
        rules_with_gaps = total_rules - rules_with_100_coverage
        overall_coverage = (rules_with_100_coverage / total_rules * 100) if total_rules > 0 else 0

        coverage_by_artefact_percent = {
            artefact: (count / total_rules * 100) if total_rules > 0 else 0
            for artefact, count in coverage_by_artefact.items()
        }

        # Identify gaps
        gaps = [
            {
                "rule_id": r.rule_id,
                "severity": r.severity,
                "missing_in": r.missing_in,
                "recommendation": self._generate_recommendation(r)
            }
            for r in all_rules_coverage if len(r.missing_in) > 0
        ]

        return CoverageReport(
            timestamp=timestamp,
            rules_yaml_sha256=rules_sha,
            repo_path=str(self.repo_path),
            total_rules=total_rules,
            rules_with_100_coverage=rules_with_100_coverage,
            rules_with_gaps=rules_with_gaps,
            overall_coverage_percent=round(overall_coverage, 2),
            coverage_by_artefact=coverage_by_artefact_percent,
            rules=all_rules_coverage,
            gaps=gaps
        )

    @staticmethod
    def _generate_recommendation(rule_coverage: RuleCoverage) -> str:
        """Generiert Empfehlungen für fehlende Coverage"""
        recommendations = []
        for artefact in rule_coverage.missing_in:
            if artefact == "contract":
                recommendations.append("Add OpenAPI/JSON-Schema definition in contracts/")
            elif artefact == "core":
                recommendations.append("Implement logic in implementations/*/src/ or 03_core/")
            elif artefact == "policy":
                recommendations.append("Add OPA policy in policies/*.rego or Semgrep rule")
            elif artefact == "cli":
                recommendations.append("Add CLI validation in 12_tooling/cli/")
            elif artefact == "test":
                recommendations.append("Add tests in conformance/ or tests/")
        return "; ".join(recommendations)


# ============================================================================
# OUTPUT FORMATTERS
# ============================================================================

class ConsoleFormatter:
    """Formatiert Coverage-Report für Console-Ausgabe"""

    @staticmethod
    def format(report: CoverageReport) -> str:
        """Erzeugt Console-Output"""
        lines = []
        lines.append("=" * 80)
        lines.append("SSID MASTER RULES COVERAGE REPORT")
        lines.append("=" * 80)
        lines.append(f"Timestamp:           {report.timestamp}")
        lines.append(f"Rules YAML SHA256:   {report.rules_yaml_sha256}")
        lines.append(f"Repository:          {report.repo_path}")
        lines.append("")
        lines.append("-" * 80)
        lines.append("COVERAGE SUMMARY")
        lines.append("-" * 80)
        lines.append(f"Total Rules:         {report.total_rules}")
        lines.append(f"100% Coverage:       {report.rules_with_100_coverage}")
        lines.append(f"With Gaps:           {report.rules_with_gaps}")
        lines.append(f"Overall Coverage:    {report.overall_coverage_percent}%")
        lines.append("")
        lines.append("Coverage by Artefact:")
        for artefact, percent in sorted(report.coverage_by_artefact.items()):
            lines.append(f"  {artefact:15} {percent:6.2f}%")
        lines.append("")

        if report.gaps:
            lines.append("-" * 80)
            lines.append(f"COVERAGE GAPS ({len(report.gaps)} rules)")
            lines.append("-" * 80)
            for gap in report.gaps[:20]:  # First 20
                lines.append(f"Rule: {gap['rule_id']} (Severity: {gap['severity']})")
                lines.append(f"  Missing in: {', '.join(gap['missing_in'])}")
                lines.append(f"  Recommendation: {gap['recommendation']}")
                lines.append("")

            if len(report.gaps) > 20:
                lines.append(f"... and {len(report.gaps) - 20} more gaps (see JSON report)")
                lines.append("")

        lines.append("=" * 80)
        if report.overall_coverage_percent == 100:
            lines.append("✅ SUCCESS: 100% COVERAGE ACHIEVED")
        else:
            lines.append("❌ FAILURE: Coverage gaps detected")
        lines.append("=" * 80)

        return "\n".join(lines)


class JSONFormatter:
    """Formatiert Coverage-Report als JSON"""

    @staticmethod
    def format(report: CoverageReport) -> str:
        """Erzeugt JSON-Output"""
        report_dict = {
            "timestamp": report.timestamp,
            "rules_yaml_sha256": report.rules_yaml_sha256,
            "repo_path": report.repo_path,
            "summary": {
                "total_rules": report.total_rules,
                "rules_with_100_coverage": report.rules_with_100_coverage,
                "rules_with_gaps": report.rules_with_gaps,
                "overall_coverage_percent": report.overall_coverage_percent,
                "coverage_by_artefact": report.coverage_by_artefact
            },
            "gaps": report.gaps,
            "detailed_rules": [
                {
                    "rule_id": r.rule_id,
                    "category": r.category,
                    "severity": r.severity,
                    "rule_text": r.rule_text,
                    "coverage": r.coverage,
                    "missing_in": r.missing_in,
                    "evidence": r.evidence
                }
                for r in report.rules
            ]
        }
        return json.dumps(report_dict, indent=2, ensure_ascii=False)


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="SSID Master Rules Coverage Checker - Verifies 100% coverage across 5 SoT Artefacts"
    )
    parser.add_argument("--rules", type=Path, required=True, help="Path to master_rules.yaml")
    parser.add_argument("--repo", type=Path, required=True, help="Path to SSID repository root")
    parser.add_argument("--output", type=Path, help="Path to output JSON report (optional)")
    parser.add_argument("--fail-under", type=float, default=100.0, help="Minimum coverage percentage required (default: 100)")

    args = parser.parse_args()

    # Validate inputs
    if not args.rules.exists():
        print(f"Error: Rules file not found: {args.rules}", file=sys.stderr)
        sys.exit(2)

    if not args.repo.exists():
        print(f"Error: Repository path not found: {args.repo}", file=sys.stderr)
        sys.exit(2)

    # Run coverage check
    print(f"Running coverage check...", file=sys.stderr)
    print(f"  Rules:      {args.rules}", file=sys.stderr)
    print(f"  Repository: {args.repo}", file=sys.stderr)
    print("", file=sys.stderr)

    checker = CoverageChecker(args.rules, args.repo)
    report = checker.check_coverage()

    # Output console report
    print(ConsoleFormatter.format(report))

    # Output JSON report if requested
    if args.output:
        json_output = JSONFormatter.format(report)
        args.output.write_text(json_output, encoding="utf-8")
        print(f"\nJSON report written to: {args.output}", file=sys.stderr)

        # SHA256 hash report
        sha256 = hashlib.sha256(json_output.encode("utf-8")).hexdigest()
        print(f"Report SHA256: {sha256}", file=sys.stderr)

    # Exit code based on coverage
    if report.overall_coverage_percent >= args.fail_under:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
