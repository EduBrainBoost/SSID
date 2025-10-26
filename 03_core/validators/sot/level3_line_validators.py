"""
Level 3 Line Validators - Hash-Based Drift Detection
=====================================================
Total Rules: 4,896 (SOT-LINE-0001 through SOT-LINE-4896)
Source: 16_codex/structure/level3/sot_contract_expanded_TRUE.yaml
Generated: 2025-10-21
Status: 100% COMPLETE - All 4,896 Ebene-3 Line Rules from 4 Holy Files
=====================================================

This module implements parametrized line-level validation for all 4,896
Ebene-3 rules from the 4 holy SoT files. Each rule validates a single
line of source documentation using SHA256 hash-based drift detection.

The 4 Holy SoT Files (SACRED SOURCE - DO NOT MODIFY):
1. SSID_structure_level3_part1_MAX.md (1,257 lines)
2. SSID_structure_level3_part2_MAX.md (1,366 lines)
3. SSID_structure_level3_part3_MAX.md (1,210 lines)
4. ssid_master_definition_corrected_v1.1.1.md (1,063 lines)

Implementation Strategy:
- Parametrized approach (DRY principle)
- Single validate_sot_line(line_id) function handles all 4,896 rules
- Auto-loads rule definitions from sot_contract_expanded_TRUE.yaml
- Evidence-based validation with hash verification
- Severity levels: INFO, LOW, MEDIUM, HIGH, CRITICAL
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import hashlib
import yaml
from datetime import datetime


# Import from parent module
import sys
sys.path.insert(0, str(Path(__file__).parent))
from sot_validator_core import ValidationResult, Severity


class Level3LineValidator:
    """
    Level 3 Line Validator - Hash-based drift detection for all 1,276 lines.

    This validator implements byte-exact line-level validation using SHA256
    hash comparison against canonical source documents.
    """

    def __init__(self, repo_root: Path):
        """
        Initialize Level 3 validator.

        Args:
            repo_root: Path to SSID repository root
        """
        self.repo_root = Path(repo_root).resolve()
        self.contract_file = self.repo_root / "16_codex" / "structure" / "level3" / "sot_contract_expanded_TRUE.yaml"

        # Load contract rules (lazy-loaded)
        self._contract_rules: Optional[Dict[str, Any]] = None
        self._rules_loaded = False
        self._total_rules = 4896  # Total rules from 4 holy files

    def _load_contract_rules(self) -> Dict[str, Dict[str, Any]]:
        """
        Lazy-load contract rules from sot_contract_expanded.yaml.

        Returns:
            Dictionary mapping rule_id to rule definition
        """
        if self._rules_loaded and self._contract_rules is not None:
            return self._contract_rules

        if not self.contract_file.exists():
            # Return empty dict if file doesn't exist (fail gracefully)
            self._contract_rules = {}
            self._rules_loaded = True
            return self._contract_rules

        try:
            with open(self.contract_file, 'r', encoding='utf-8') as f:
                contract_data = yaml.safe_load(f)

            # Build lookup dict by rule_id
            rules_dict = {}
            for rule in contract_data.get('rules', []):
                rule_id = rule.get('rule_id')
                if rule_id:
                    rules_dict[rule_id] = rule

            self._contract_rules = rules_dict
            self._rules_loaded = True
            return self._contract_rules

        except Exception as e:
            # Fail gracefully - return empty dict
            print(f"Warning: Could not load sot_contract_expanded.yaml: {e}")
            self._contract_rules = {}
            self._rules_loaded = True
            return self._contract_rules

    def validate_sot_line(self, line_id: int) -> ValidationResult:
        """
        Validate SOT-LINE-{line_id:04d} - Line-level hash validation.

        This is a parametrized validator that handles all 1,276 Ebene-3 line rules.
        Each rule validates one specific line of a source document using SHA256
        hash-based drift detection.

        Args:
            line_id: Line number (1-1276)

        Returns:
            ValidationResult with hash verification evidence

        Example:
            >>> validator = Level3LineValidator(repo_root)
            >>> result = validator.validate_sot_line(1)
            >>> print(f"{result.rule_id}: {'PASS' if result.passed else 'FAIL'}")
            SOT-LINE-0001: PASS
        """
        rule_id = f"SOT-LINE-{line_id:04d}"

        # Load contract rules
        contract_rules = self._load_contract_rules()

        # Get rule definition
        rule_def = contract_rules.get(rule_id)

        if not rule_def:
            # Rule not found in contract - FAIL with INFO severity
            return ValidationResult(
                rule_id=rule_id,
                passed=False,
                severity=Severity.INFO,
                message=f"Rule definition not found for {rule_id} in sot_contract_expanded.yaml",
                evidence={
                    "error": "missing_rule_definition",
                    "contract_file": str(self.contract_file),
                    "contract_exists": self.contract_file.exists()
                }
            )

        # Extract rule metadata
        source_file_name = rule_def.get('source', 'UNKNOWN')
        target_line = rule_def.get('line_ref', 0)
        expected_hash = rule_def.get('hash_ref', '')
        category = rule_def.get('category', 'UNKNOWN')
        severity_str = rule_def.get('severity', 'INFO')

        # Map severity string to Enum
        try:
            severity = Severity[severity_str]
        except KeyError:
            severity = Severity.INFO

        # Construct source file path
        # Source files are in 16_codex/structure/ (THE HOLY SOT DIRECTORY)
        source_file = self.repo_root / "16_codex" / "structure" / source_file_name

        # Check if source file exists
        if not source_file.exists():
            return ValidationResult(
                rule_id=rule_id,
                passed=False,
                severity=severity,
                message=f"Source file not found: {source_file_name}",
                evidence={
                    "error": "source_file_not_found",
                    "source_file": str(source_file),
                    "line_ref": target_line,
                    "category": category
                }
            )

        # Read source file and compute hash
        try:
            with open(source_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # Check if line exists
            if target_line < 1 or target_line > len(lines):
                return ValidationResult(
                    rule_id=rule_id,
                    passed=False,
                    severity=Severity.HIGH,
                    message=f"Line {target_line} not found in {source_file_name} (total: {len(lines)} lines)",
                    evidence={
                        "error": "line_out_of_range",
                        "source_file": str(source_file),
                        "line_ref": target_line,
                        "total_lines": len(lines),
                        "category": category
                    }
                )

            # Get target line (1-indexed)
            actual_line = lines[target_line - 1]

            # Compute SHA256 hash
            actual_hash = hashlib.sha256(actual_line.encode('utf-8')).hexdigest()

            # Compare hashes
            passed = (actual_hash == expected_hash)

            return ValidationResult(
                rule_id=rule_id,
                passed=passed,
                severity=severity,
                message=f"{'PASS' if passed else 'FAIL'}: Line {target_line} hash {'matches' if passed else 'MISMATCH'} (category: {category})",
                evidence={
                    "source_file": str(source_file),
                    "line_ref": target_line,
                    "expected_hash": expected_hash,
                    "actual_hash": actual_hash,
                    "category": category,
                    "line_preview": actual_line[:100].strip() if len(actual_line) > 100 else actual_line.strip()
                }
            )

        except UnicodeDecodeError:
            return ValidationResult(
                rule_id=rule_id,
                passed=False,
                severity=Severity.MEDIUM,
                message=f"Unicode decode error reading {source_file_name}",
                evidence={
                    "error": "unicode_decode_error",
                    "source_file": str(source_file),
                    "line_ref": target_line,
                    "category": category
                }
            )

        except Exception as e:
            return ValidationResult(
                rule_id=rule_id,
                passed=False,
                severity=Severity.HIGH,
                message=f"Error validating line: {str(e)}",
                evidence={
                    "error": str(e),
                    "source_file": str(source_file),
                    "line_ref": target_line,
                    "category": category
                }
            )

    def validate_all_lines(self) -> List[ValidationResult]:
        """
        Validate all 4,896 Ebene-3 line rules from the 4 holy SoT files.

        Returns:
            List of 4,896 ValidationResult objects
        """
        results = []
        for line_id in range(1, self._total_rules + 1):  # 1-4896
            results.append(self.validate_sot_line(line_id))
        return results


# ================================================================
# CONVENIENCE FUNCTIONS FOR INTEGRATION WITH sot_validator_core.py
# ================================================================

def create_line_validator(repo_root: Path) -> Level3LineValidator:
    """
    Factory function to create Level3LineValidator instance.

    Args:
        repo_root: Path to SSID repository root

    Returns:
        Level3LineValidator instance
    """
    return Level3LineValidator(repo_root)


def validate_line_range(repo_root: Path, start: int, end: int) -> List[ValidationResult]:
    """
    Validate a range of line rules.

    Args:
        repo_root: Path to SSID repository root
        start: Starting line ID (inclusive)
        end: Ending line ID (inclusive)

    Returns:
        List of ValidationResult objects for the specified range
    """
    validator = Level3LineValidator(repo_root)
    results = []
    for line_id in range(start, end + 1):
        results.append(validator.validate_sot_line(line_id))
    return results
