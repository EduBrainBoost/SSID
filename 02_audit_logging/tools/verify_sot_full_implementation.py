#!/usr/bin/env python3
"""
SoT Full Implementation Verifier - Forensic Integrity Tool

This tool performs automatic verification that ALL Source-of-Truth (SoT) rules
are implemented in tests with 100% coverage. Any missing rule is documented
line-by-line for audit purposes.

Forensic Purpose:
- Structural Integrity: All SoT rules must appear in test code
- Zero Tolerance: 100% coverage required (no exceptions)
- Audit Trail: Line-by-line documentation of missing rules
- CI/CD Integration: Automated verification in enforcement gate

Copyright: SSID Project
License: ROOT-24-LOCK compliant
Version: 1.0.0
"""

import sys
import os
import json
import re
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Set
from datetime import datetime, timezone

# Ensure UTF-8 encoding for Windows
if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')


class SoTImplementationVerifier:
    """
    Verifies that all Source-of-Truth (SoT) rules are implemented in tests.

    Performs forensic analysis of:
    1. SoT definitions in 16_codex/sot_definitions/
    2. Test implementations in 11_test_simulation/tests/
    3. Cross-verification with enforcement reports
    4. Coverage calculation and gap identification
    """

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.sot_dir = repo_root / "16_codex" / "sot_definitions"
        self.test_dir = repo_root / "11_test_simulation" / "tests"
        self.reports_dir = repo_root / "02_audit_logging" / "reports"
        self.policies_dir = repo_root / "23_compliance" / "policies"

        # Results structure
        self.results = {
            "verification_metadata": {
                "tool": "verify_sot_full_implementation.py",
                "version": "1.0.0",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "repository": "SSID"
            },
            "missing_rules": [],
            "coverage": {},
            "totals": {
                "sot_files": 0,
                "rules": 0,
                "implemented": 0,
                "missing": 0
            },
            "overall_coverage": 0.0,
            "test_files_scanned": [],
            "sot_files_analyzed": []
        }

    def verify_sot_implementation(self) -> Dict[str, Any]:
        """
        Main orchestration method for SoT implementation verification.

        Returns:
            Complete verification results with coverage statistics
        """
        print("=" * 70)
        print("SoT FULL IMPLEMENTATION VERIFIER - FORENSIC INTEGRITY TOOL")
        print("=" * 70)
        print()

        # Step 1: Discover SoT definition files
        print("Step 1: Discovering SoT definition files...")
        sot_files = self._discover_sot_files()
        print(f"  Found {len(sot_files)} SoT definition file(s)")
        if not sot_files:
            print("  [WARNING] No SoT definition files found!")
            print(f"  Expected location: {self.sot_dir}")
        print()

        # Step 2: Discover test files
        print("Step 2: Discovering test implementation files...")
        test_files = self._discover_test_files()
        print(f"  Found {len(test_files)} test file(s)")
        if not test_files:
            print("  [WARNING] No test files found!")
            print(f"  Expected location: {self.test_dir}")
        print()

        # Step 3: Extract SoT rules from definitions
        print("Step 3: Extracting SoT rules from definitions...")
        sot_rules = self._extract_sot_rules(sot_files)
        print(f"  Extracted {sum(len(rules) for rules in sot_rules.values())} total rule(s)")
        for sot_file, rules in sot_rules.items():
            print(f"    {sot_file}: {len(rules)} rule(s)")
        print()

        # Step 4: Build test content index
        print("Step 4: Indexing test file contents...")
        test_index = self._build_test_index(test_files)
        print(f"  Indexed {len(test_index)} test file(s)")
        print()

        # Step 5: Verify rule implementation
        print("Step 5: Verifying rule implementation in tests...")
        self._verify_rules_in_tests(sot_rules, test_index)
        print(f"  Implemented: {self.results['totals']['implemented']}/{self.results['totals']['rules']}")
        print(f"  Missing: {self.results['totals']['missing']}")
        print()

        # Step 6: Calculate coverage
        print("Step 6: Calculating coverage statistics...")
        self._calculate_coverage()
        print(f"  Overall Coverage: {self.results['overall_coverage']:.2f}%")
        print()

        # Step 7: Generate report
        print("Step 7: Generating forensic report...")
        report_path = self._generate_report()
        print(f"  Report: {report_path}")
        print()

        # Step 8: Display results
        self._display_results()

        print("=" * 70)
        if self.results['overall_coverage'] == 100.0:
            print("[OK] SoT Implementation: 100% VERIFIED")
        else:
            print(f"[WARNING] SoT Implementation: {self.results['overall_coverage']:.2f}% (GAPS DETECTED)")
        print("=" * 70)
        print()

        return self.results

    def _discover_sot_files(self) -> List[Path]:
        """Discover all SoT definition files."""
        sot_files = []

        if not self.sot_dir.exists():
            print(f"  [WARNING] SoT directory does not exist: {self.sot_dir}")
            return sot_files

        # Look for markdown files in sot_definitions
        for sot_file in self.sot_dir.glob("*.md"):
            sot_files.append(sot_file)
            self.results["sot_files_analyzed"].append(str(sot_file.relative_to(self.repo_root)))

        # Also check for YAML/JSON policy files
        if self.policies_dir.exists():
            for policy_file in self.policies_dir.glob("sot_*.yaml"):
                sot_files.append(policy_file)
                self.results["sot_files_analyzed"].append(str(policy_file.relative_to(self.repo_root)))

        self.results["totals"]["sot_files"] = len(sot_files)
        return sot_files

    def _discover_test_files(self) -> List[Path]:
        """Discover all test implementation files."""
        test_files = []

        if not self.test_dir.exists():
            print(f"  [WARNING] Test directory does not exist: {self.test_dir}")
            return test_files

        # Look for all Python test files
        for test_file in self.test_dir.glob("**/*.py"):
            if test_file.name.startswith("test_") or test_file.name.endswith("_test.py"):
                test_files.append(test_file)
                self.results["test_files_scanned"].append(str(test_file.relative_to(self.repo_root)))

        return test_files

    def _extract_sot_rules(self, sot_files: List[Path]) -> Dict[str, List[str]]:
        """
        Extract SoT rules from definition files.

        For markdown files: Extract non-empty, non-header lines
        For YAML files: Extract rule definitions
        """
        sot_rules = {}

        for sot_file in sot_files:
            rules = []

            try:
                content = sot_file.read_text(encoding='utf-8', errors='ignore')

                if sot_file.suffix == ".md":
                    # Markdown: Extract meaningful lines (not headers, not empty)
                    for line in content.splitlines():
                        line = line.strip()
                        if line and not line.startswith("#") and not line.startswith("---"):
                            # Skip common markdown elements
                            if not line.startswith("*") and not line.startswith("-") and not line.startswith(">"):
                                # This is a potential SoT rule
                                rules.append(line)

                elif sot_file.suffix in (".yaml", ".yml"):
                    # YAML: Look for rule definitions (simplified extraction)
                    for line in content.splitlines():
                        line = line.strip()
                        if ":" in line and not line.startswith("#"):
                            # Extract key from YAML
                            key = line.split(":")[0].strip()
                            if key and not key.startswith("-"):
                                rules.append(key)

                sot_rules[sot_file.name] = rules

            except Exception as e:
                print(f"  [ERROR] Failed to extract rules from {sot_file.name}: {e}")

        return sot_rules

    def _build_test_index(self, test_files: List[Path]) -> Dict[str, str]:
        """
        Build searchable index of test file contents.

        Returns:
            Dictionary mapping file paths to their contents
        """
        test_index = {}

        for test_file in test_files:
            try:
                content = test_file.read_text(encoding='utf-8', errors='ignore')
                test_index[str(test_file)] = content
            except Exception as e:
                print(f"  [ERROR] Failed to read test file {test_file.name}: {e}")

        return test_index

    def _verify_rules_in_tests(self, sot_rules: Dict[str, List[str]], test_index: Dict[str, str]):
        """
        Verify that each SoT rule is implemented in at least one test file.

        Uses fuzzy matching to account for slight variations in rule text.
        """
        for sot_file, rules in sot_rules.items():
            implemented_count = 0
            coverage_details = []

            for rule in rules:
                self.results["totals"]["rules"] += 1

                # Search for rule in test files
                found = self._find_rule_in_tests(rule, test_index)

                if found:
                    implemented_count += 1
                    self.results["totals"]["implemented"] += 1
                    coverage_details.append({
                        "rule": rule,
                        "status": "IMPLEMENTED",
                        "found_in": found
                    })
                else:
                    self.results["totals"]["missing"] += 1
                    self.results["missing_rules"].append({
                        "sot_file": sot_file,
                        "rule": rule,
                        "status": "MISSING",
                        "recommendation": "Implement test case for this SoT rule"
                    })
                    coverage_details.append({
                        "rule": rule,
                        "status": "MISSING",
                        "found_in": []
                    })

            # Calculate per-file coverage
            coverage_pct = (implemented_count / len(rules) * 100) if rules else 0.0
            self.results["coverage"][sot_file] = {
                "total_rules": len(rules),
                "implemented": implemented_count,
                "missing": len(rules) - implemented_count,
                "coverage_percent": round(coverage_pct, 2),
                "details": coverage_details
            }

    def _find_rule_in_tests(self, rule: str, test_index: Dict[str, str]) -> List[str]:
        """
        Find if a rule is implemented in any test file.

        Uses multiple matching strategies:
        1. Exact substring match
        2. Fuzzy match (normalized, case-insensitive)
        3. Keyword match (extract key terms)
        """
        found_in = []

        # Normalize rule for better matching
        rule_normalized = self._normalize_text(rule)
        rule_keywords = self._extract_keywords(rule)

        for test_file, content in test_index.items():
            content_normalized = self._normalize_text(content)

            # Strategy 1: Exact substring match
            if rule in content:
                found_in.append(test_file)
                continue

            # Strategy 2: Fuzzy match (normalized)
            if rule_normalized in content_normalized:
                found_in.append(test_file)
                continue

            # Strategy 3: Keyword match (at least 70% of keywords present)
            if self._keyword_match_score(rule_keywords, content_normalized) >= 0.7:
                found_in.append(test_file)
                continue

        return found_in

    def _normalize_text(self, text: str) -> str:
        """Normalize text for fuzzy matching."""
        # Remove special characters, convert to lowercase
        normalized = re.sub(r'[^a-z0-9\s]', '', text.lower())
        # Collapse multiple spaces
        normalized = re.sub(r'\s+', ' ', normalized)
        return normalized.strip()

    def _extract_keywords(self, text: str) -> Set[str]:
        """Extract significant keywords from text."""
        # Remove common words
        stopwords = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "from", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "do", "does", "did", "will", "would", "should", "could", "may", "might", "must", "can", "shall"}

        words = self._normalize_text(text).split()
        keywords = {word for word in words if len(word) > 3 and word not in stopwords}

        return keywords

    def _keyword_match_score(self, keywords: Set[str], content: str) -> float:
        """Calculate keyword match score (0-1)."""
        if not keywords:
            return 0.0

        matches = sum(1 for keyword in keywords if keyword in content)
        return matches / len(keywords)

    def _calculate_coverage(self):
        """Calculate overall coverage statistics."""
        total_rules = self.results["totals"]["rules"]
        implemented = self.results["totals"]["implemented"]

        if total_rules > 0:
            self.results["overall_coverage"] = round((implemented / total_rules) * 100, 2)
        else:
            self.results["overall_coverage"] = 0.0

    def _generate_report(self) -> Path:
        """Generate forensic report as JSON."""
        report_path = self.reports_dir / "sot_full_implementation_audit.json"

        # Ensure reports directory exists
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        # Write report
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        return report_path

    def _display_results(self):
        """Display verification results to console."""
        print("=" * 70)
        print("VERIFICATION RESULTS")
        print("=" * 70)
        print()

        print("Coverage by SoT File:")
        print("-" * 70)
        for sot_file, coverage in self.results["coverage"].items():
            status = "[OK]" if coverage["coverage_percent"] == 100.0 else "[WARNING]"
            print(f"{status} {sot_file}")
            print(f"     Implemented: {coverage['implemented']}/{coverage['total_rules']} ({coverage['coverage_percent']:.2f}%)")
            if coverage["missing"] > 0:
                print(f"     Missing: {coverage['missing']} rule(s)")
        print()

        if self.results["missing_rules"]:
            print("Missing SoT Rules (Line-by-Line):")
            print("-" * 70)
            for i, missing in enumerate(self.results["missing_rules"], 1):
                print(f"{i}. [{missing['sot_file']}]")
                print(f"   Rule: {missing['rule']}")
                print(f"   Status: {missing['status']}")
                print(f"   Recommendation: {missing['recommendation']}")
                print()
        else:
            print("[OK] No missing rules detected - 100% coverage achieved!")
            print()


def main():
    """Main execution function."""
    # Detect repository root
    repo_root = Path(__file__).resolve().parent.parent.parent

    print()
    print("SoT Full Implementation Verifier")
    print(f"Repository: {repo_root}")
    print()

    # Create verifier
    verifier = SoTImplementationVerifier(repo_root)

    # Run verification
    results = verifier.verify_sot_implementation()

    # Exit code based on coverage
    if results["overall_coverage"] == 100.0:
        print("SUCCESS: 100% SoT rule coverage verified")
        return 0
    else:
        print(f"WARNING: Only {results['overall_coverage']:.2f}% coverage - gaps detected")
        print(f"Missing rules: {results['totals']['missing']}")
        return 1  # Non-zero exit for CI/CD failure


if __name__ == "__main__":
    sys.exit(main())
