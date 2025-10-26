#!/usr/bin/env python3
"""
Constraint Validators - Cross-Field Mathematical Validation
============================================================
Validates mathematical constraints and cross-field dependencies
from the 4 Holy SoT Files.

These validators check relationships BETWEEN fields, not just
individual field values.

Total Constraint Rules: ~50 (5 from Part1 + ~45 from Part2/Part3/Master)
"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml


@dataclass
class ValidationResult:
    """Result of a single validation"""
    rule_id: str
    passed: bool
    severity: str
    message: str
    evidence: str
    timestamp: str


class ConstraintValidators:
    """Cross-field constraint validators"""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root

    def _load_yaml(self, yaml_file: str) -> Optional[Dict[str, Any]]:
        """Load YAML file and return data"""
        file_path = self.repo_root / yaml_file
        if not file_path.exists():
            return None

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except Exception:
            return None

    def _get_nested_value(self, data: Dict, path: str) -> Any:
        """Get value from nested dict using dot notation"""
        if data is None:
            return None

        keys = path.split(".")
        current = data
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        return current

    # ============================================================
    # PART 1 CONSTRAINTS (Token Economics)
    # ============================================================

    def validate_const_p1_001(self) -> ValidationResult:
        """
        CONST-P1-001: Distribution Sum = 100%

        The sum of all token distribution percentages MUST equal exactly 100%.
        From Part1: distribution.initial_allocation

        Expected breakdown:
        - Community: 40%
        - Development: 25%
        - Ecosystem: 15%
        - Foundation: 10%
        - Advisors: 10%
        """
        yaml_file = '20_foundation/tokenomics/token_economics.yaml'
        data = self._load_yaml(yaml_file)

        if data is None:
            return ValidationResult(
                rule_id='CONST-P1-001',
                passed=False,
                severity='CRITICAL',
                message=f'FAIL: YAML file not found: {yaml_file}',
                evidence=f'File: {yaml_file}',
                timestamp=datetime.now().isoformat()
            )

        # Extract distribution percentages
        community = self._get_nested_value(data, 'distribution.initial_allocation.community')
        development = self._get_nested_value(data, 'distribution.initial_allocation.development')
        ecosystem = self._get_nested_value(data, 'distribution.initial_allocation.ecosystem')
        foundation = self._get_nested_value(data, 'distribution.initial_allocation.foundation')
        advisors = self._get_nested_value(data, 'distribution.initial_allocation.advisors')

        # Convert string percentages to floats if needed
        def parse_percent(value):
            if value is None:
                return 0.0
            if isinstance(value, str):
                return float(value.rstrip('%'))
            return float(value)

        try:
            values = {
                'community': parse_percent(community),
                'development': parse_percent(development),
                'ecosystem': parse_percent(ecosystem),
                'foundation': parse_percent(foundation),
                'advisors': parse_percent(advisors)
            }

            total = sum(values.values())
            expected = 100.0
            tolerance = 0.01  # Allow 0.01% tolerance for floating point

            passed = abs(total - expected) <= tolerance

            if passed:
                message = f'PASS: Distribution sum = {total}% (within {tolerance}% of {expected}%)'
            else:
                message = f'FAIL: Distribution sum = {total}%, expected {expected}%. Breakdown: {values}'

            return ValidationResult(
                rule_id='CONST-P1-001',
                passed=passed,
                severity='CRITICAL',
                message=message,
                evidence=f'File: {yaml_file}, Fields: distribution.initial_allocation.*',
                timestamp=datetime.now().isoformat()
            )

        except (ValueError, TypeError) as e:
            return ValidationResult(
                rule_id='CONST-P1-001',
                passed=False,
                severity='CRITICAL',
                message=f'FAIL: Error parsing distribution values: {str(e)}',
                evidence=f'File: {yaml_file}',
                timestamp=datetime.now().isoformat()
            )

    def validate_const_p1_002(self) -> ValidationResult:
        """
        CONST-P1-002: Fee Split = 3% (1% + 2%)

        Total fee MUST equal sum of burn_fee + treasury_fee
        """
        yaml_file = '20_foundation/tokenomics/token_economics.yaml'
        data = self._load_yaml(yaml_file)

        if data is None:
            return ValidationResult(
                rule_id='CONST-P1-002',
                passed=False,
                severity='HIGH',
                message=f'FAIL: YAML file not found: {yaml_file}',
                evidence=f'File: {yaml_file}',
                timestamp=datetime.now().isoformat()
            )

        total_fee = self._get_nested_value(data, 'fees.transaction_fee')
        burn_fee = self._get_nested_value(data, 'fees.burn_fee')
        treasury_fee = self._get_nested_value(data, 'fees.treasury_fee')

        def parse_percent(value):
            if value is None:
                return 0.0
            if isinstance(value, str):
                return float(value.rstrip('%'))
            return float(value)

        try:
            total = parse_percent(total_fee)
            burn = parse_percent(burn_fee)
            treasury = parse_percent(treasury_fee)

            calculated_total = burn + treasury
            tolerance = 0.01

            passed = abs(total - calculated_total) <= tolerance

            if passed:
                message = f'PASS: Fee split correct: {total}% = {burn}% (burn) + {treasury}% (treasury)'
            else:
                message = f'FAIL: Fee split incorrect: {total}% != {burn}% + {treasury}% (= {calculated_total}%)'

            return ValidationResult(
                rule_id='CONST-P1-002',
                passed=passed,
                severity='HIGH',
                message=message,
                evidence=f'File: {yaml_file}, Fields: fees.*',
                timestamp=datetime.now().isoformat()
            )

        except (ValueError, TypeError) as e:
            return ValidationResult(
                rule_id='CONST-P1-002',
                passed=False,
                severity='HIGH',
                message=f'FAIL: Error parsing fee values: {str(e)}',
                evidence=f'File: {yaml_file}',
                timestamp=datetime.now().isoformat()
            )

    def validate_const_p1_003(self) -> ValidationResult:
        """
        CONST-P1-003: Burn Rate = 50% of transaction fee

        The burn_fee MUST be 50% of the total transaction_fee
        """
        yaml_file = '20_foundation/tokenomics/token_economics.yaml'
        data = self._load_yaml(yaml_file)

        if data is None:
            return ValidationResult(
                rule_id='CONST-P1-003',
                passed=False,
                severity='HIGH',
                message=f'FAIL: YAML file not found: {yaml_file}',
                evidence=f'File: {yaml_file}',
                timestamp=datetime.now().isoformat()
            )

        total_fee = self._get_nested_value(data, 'fees.transaction_fee')
        burn_fee = self._get_nested_value(data, 'fees.burn_fee')

        def parse_percent(value):
            if value is None:
                return 0.0
            if isinstance(value, str):
                return float(value.rstrip('%'))
            return float(value)

        try:
            total = parse_percent(total_fee)
            burn = parse_percent(burn_fee)

            expected_burn = total * 0.5
            tolerance = 0.01

            passed = abs(burn - expected_burn) <= tolerance

            if passed:
                message = f'PASS: Burn rate correct: {burn}% = 50% of {total}%'
            else:
                message = f'FAIL: Burn rate incorrect: {burn}% != 50% of {total}% (expected {expected_burn}%)'

            return ValidationResult(
                rule_id='CONST-P1-003',
                passed=passed,
                severity='HIGH',
                message=message,
                evidence=f'File: {yaml_file}, Fields: fees.transaction_fee, fees.burn_fee',
                timestamp=datetime.now().isoformat()
            )

        except (ValueError, TypeError) as e:
            return ValidationResult(
                rule_id='CONST-P1-003',
                passed=False,
                severity='HIGH',
                message=f'FAIL: Error parsing fee values: {str(e)}',
                evidence=f'File: {yaml_file}',
                timestamp=datetime.now().isoformat()
            )

    def validate_const_p1_004(self) -> ValidationResult:
        """
        CONST-P1-004: Daily Cap <= 0.5% of total supply

        The daily transaction cap MUST NOT exceed 0.5% of total supply
        """
        yaml_file = '20_foundation/tokenomics/token_economics.yaml'
        data = self._load_yaml(yaml_file)

        if data is None:
            return ValidationResult(
                rule_id='CONST-P1-004',
                passed=False,
                severity='MEDIUM',
                message=f'FAIL: YAML file not found: {yaml_file}',
                evidence=f'File: {yaml_file}',
                timestamp=datetime.now().isoformat()
            )

        daily_cap = self._get_nested_value(data, 'limits.daily_transaction_cap')

        def parse_percent(value):
            if value is None:
                return 0.0
            if isinstance(value, str):
                return float(value.rstrip('%'))
            return float(value)

        try:
            cap = parse_percent(daily_cap)
            max_allowed = 0.5

            passed = cap <= max_allowed

            if passed:
                message = f'PASS: Daily cap {cap}% <= {max_allowed}%'
            else:
                message = f'FAIL: Daily cap {cap}% exceeds maximum {max_allowed}%'

            return ValidationResult(
                rule_id='CONST-P1-004',
                passed=passed,
                severity='MEDIUM',
                message=message,
                evidence=f'File: {yaml_file}, Field: limits.daily_transaction_cap',
                timestamp=datetime.now().isoformat()
            )

        except (ValueError, TypeError) as e:
            return ValidationResult(
                rule_id='CONST-P1-004',
                passed=False,
                severity='MEDIUM',
                message=f'FAIL: Error parsing daily cap value: {str(e)}',
                evidence=f'File: {yaml_file}',
                timestamp=datetime.now().isoformat()
            )

    def validate_const_p1_005(self) -> ValidationResult:
        """
        CONST-P1-005: Monthly Cap <= 2.0% of total supply

        The monthly transaction cap MUST NOT exceed 2.0% of total supply
        """
        yaml_file = '20_foundation/tokenomics/token_economics.yaml'
        data = self._load_yaml(yaml_file)

        if data is None:
            return ValidationResult(
                rule_id='CONST-P1-005',
                passed=False,
                severity='MEDIUM',
                message=f'FAIL: YAML file not found: {yaml_file}',
                evidence=f'File: {yaml_file}',
                timestamp=datetime.now().isoformat()
            )

        monthly_cap = self._get_nested_value(data, 'limits.monthly_transaction_cap')

        def parse_percent(value):
            if value is None:
                return 0.0
            if isinstance(value, str):
                return float(value.rstrip('%'))
            return float(value)

        try:
            cap = parse_percent(monthly_cap)
            max_allowed = 2.0

            passed = cap <= max_allowed

            if passed:
                message = f'PASS: Monthly cap {cap}% <= {max_allowed}%'
            else:
                message = f'FAIL: Monthly cap {cap}% exceeds maximum {max_allowed}%'

            return ValidationResult(
                rule_id='CONST-P1-005',
                passed=passed,
                severity='MEDIUM',
                message=message,
                evidence=f'File: {yaml_file}, Field: limits.monthly_transaction_cap',
                timestamp=datetime.now().isoformat()
            )

        except (ValueError, TypeError) as e:
            return ValidationResult(
                rule_id='CONST-P1-005',
                passed=False,
                severity='MEDIUM',
                message=f'FAIL: Error parsing monthly cap value: {str(e)}',
                evidence=f'File: {yaml_file}',
                timestamp=datetime.now().isoformat()
            )

    # ============================================================
    # VALIDATION RUNNER
    # ============================================================

    def validate_all(self) -> List[ValidationResult]:
        """Run all constraint validators"""
        results = []

        # Part 1 Constraints
        results.append(self.validate_const_p1_001())
        results.append(self.validate_const_p1_002())
        results.append(self.validate_const_p1_003())
        results.append(self.validate_const_p1_004())
        results.append(self.validate_const_p1_005())

        return results


# ============================================================
# CLI INTERFACE
# ============================================================

if __name__ == "__main__":
    import sys

    repo_root = Path(__file__).parent.parent.parent.parent
    validator = ConstraintValidators(repo_root)

    results = validator.validate_all()

    passed = sum(1 for r in results if r.passed)
    failed = sum(1 for r in results if not r.passed)

    print(f"\nConstraint Validator Results:")
    print(f"=" * 80)
    print(f"Total: {len(results)} | Passed: {passed} | Failed: {failed}")
    print(f"=" * 80)

    for result in results:
        status = "✓ PASS" if result.passed else "✗ FAIL"
        print(f"{status} | {result.rule_id} | {result.severity:8} | {result.message}")

    print(f"=" * 80)

    sys.exit(0 if failed == 0 else 1)
