"""
Complete SoT Test Suite - All 31,742 Rules (Parametrized)
Auto-generated from sot_rules_full.json

This test suite provides 100% coverage of all SoT rules through
parametrized tests. Each rule is tested individually, and aggregate
MoSCoW scorecard tests ensure overall compliance.

Test Count: 31,742 parametrized tests
Coverage: 100%
"""

import pytest
import json
import sys
from pathlib import Path
from typing import Dict, Any, List

# Add validator path
sys.path.insert(0, str(Path(__file__).parents[2] / '03_core' / 'validators' / 'sot'))

# Import validator engine
from sot_validator_engine import RuleValidationEngine

# Load rules registry
RULES_PATH = Path(__file__).parents[2] / '16_codex' / 'structure' / 'auto_generated' / 'sot_rules_full.json'

print(f"Loading rules from: {RULES_PATH}")
with open(RULES_PATH, 'r', encoding='utf-8') as f:
    REGISTRY = json.load(f)

print(f"Loaded {len(REGISTRY['rules'])} rules")

# Initialize validator engine (pass repo root, not registry)
REPO_ROOT = Path(__file__).parents[2]
ENGINE = RuleValidationEngine(REPO_ROOT)

# Generate test parameters (all rules with their metadata)
TEST_RULES = [
    (
        r['rule_id'],
        r.get('priority', 'UNKNOWN').upper(),
        r.get('category', 'UNKNOWN'),
        r.get('name', r['rule_id'])
    )
    for r in REGISTRY['rules']
]

print(f"Generated {len(TEST_RULES)} parametrized tests")


# ========================================================================
# PARAMETRIZED TESTS - Individual Rule Validation
# ========================================================================

@pytest.mark.parametrize("rule_id,priority,category,name", TEST_RULES)
def test_rule_validation(rule_id: str, priority: str, category: str, name: str):
    """
    Test validation for each individual rule

    This test runs 31,742 times (once per rule) and validates:
    - Rule can be found in validator
    - MUST rules have pass status
    - SHOULD rules have pass or warning status
    - All rules have valid status
    """
    result = ENGINE.validate_rule(rule_id)

    assert result is not None, f"Rule {rule_id} not found in validator"

    # MUST rules must pass (100% compliance required)
    if priority == 'MUST':
        assert result.status in ['pass', 'not_applicable'], \
            f"MUST rule {rule_id} ({name}) failed: {result.message}"

    # SHOULD rules should pass (warnings acceptable)
    elif priority == 'SHOULD':
        assert result.status in ['pass', 'warn', 'not_applicable'], \
            f"SHOULD rule {rule_id} ({name}) failed: {result.message}"

    # HAVE rules (best effort)
    elif priority == 'HAVE':
        assert result.status in ['pass', 'warn', 'info', 'not_applicable'], \
            f"HAVE rule {rule_id} ({name}) has critical failure: {result.message}"

    # All rules must have a valid status
    assert result.status in ['pass', 'fail', 'warn', 'info', 'not_applicable'], \
        f"Invalid status for rule {rule_id}: {result.status}"


# ========================================================================
# AGGREGATE TESTS - MoSCoW Priority Scorecards
# ========================================================================

@pytest.mark.parametrize("priority,min_pass_rate", [
    ('MUST', 100.0),
    ('SHOULD', 95.0),
    ('HAVE', 90.0),
    ('CAN', 80.0),
])
def test_priority_scorecard(priority: str, min_pass_rate: float):
    """
    Test MoSCoW scorecard for each priority level

    Ensures:
    - MUST: 100% pass rate (critical requirements)
    - SHOULD: ≥95% pass rate (high priority)
    - HAVE: ≥90% pass rate (medium priority)
    - CAN: ≥80% pass rate (optional)
    """
    results = ENGINE.validate_all()
    priority_results = [r for r in results.results if r['priority'] == priority]

    if not priority_results:
        pytest.skip(f"No rules with priority {priority}")

    passed = sum(1 for r in priority_results if r['status'] == 'pass')
    total = len(priority_results)
    pass_rate = (passed / total) * 100

    assert pass_rate >= min_pass_rate, \
        f"{priority} rules must have ≥{min_pass_rate}% pass rate (got {pass_rate:.2f}%)"


def test_overall_completeness():
    """
    Test overall system completeness

    Ensures:
    - All 31,742 rules are present
    - Overall pass rate ≥99.9%
    - No missing rules
    """
    results = ENGINE.validate_all()

    assert results.total_rules == 31742, \
        f"Expected 31,742 rules, got {results.total_rules}"

    overall_score = (results.passed / results.total_rules) * 100
    assert overall_score >= 99.9, \
        f"Overall pass rate must be ≥99.9% (got {overall_score:.2f}%)"

    # Ensure no rules missing
    assert len(results.results) == 31742, \
        f"Results count mismatch: expected 31,742, got {len(results.results)}"


def test_category_coverage():
    """
    Test that all expected categories are covered

    Ensures:
    - All major categories have rules
    - No orphaned rules
    """
    results = ENGINE.validate_all()

    categories = set(r['category'] for r in results.results)

    # Expected minimum categories
    expected_categories = {
        'global_foundations',
        'structure',
        'compliance',
        'security',
        'testing',
        'documentation',
    }

    assert categories >= expected_categories, \
        f"Missing categories: {expected_categories - categories}"

    # All rules must have a category
    uncategorized = [r for r in results.results if not r.get('category')]
    assert len(uncategorized) == 0, \
        f"Found {len(uncategorized)} uncategorized rules"


# ========================================================================
# MOSCOW SCORECARD TESTS - Detailed Compliance Checks
# ========================================================================

class TestMoSCoWScorecard:
    """Comprehensive MoSCoW scorecard tests"""

    def test_must_rules_100_percent(self):
        """MUST rules must have 100% pass rate (no exceptions)"""
        results = ENGINE.validate_all()
        must_results = [r for r in results.results if r['priority'] == 'MUST']

        passed = sum(1 for r in must_results if r['status'] == 'pass')
        total = len(must_results)
        pass_rate = (passed / total) * 100

        # Check for failures
        failures = [r for r in must_results if r['status'] not in ['pass', 'not_applicable']]

        assert pass_rate == 100.0, \
            f"MUST rules: {pass_rate:.2f}% (required: 100%). Failures: {len(failures)}"

    def test_should_rules_high_compliance(self):
        """SHOULD rules must have ≥95% pass rate"""
        results = ENGINE.validate_all()
        should_results = [r for r in results.results if r['priority'] == 'SHOULD']

        passed = sum(1 for r in should_results if r['status'] in ['pass', 'not_applicable'])
        total = len(should_results)
        pass_rate = (passed / total) * 100

        assert pass_rate >= 95.0, \
            f"SHOULD rules: {pass_rate:.2f}% (required: ≥95%)"

    def test_no_critical_failures(self):
        """No MUST rules should have critical failures"""
        results = ENGINE.validate_all()
        critical_failures = [
            r for r in results.results
            if r['priority'] == 'MUST' and r['status'] == 'fail'
        ]

        if critical_failures:
            failure_list = [f"{r['rule_id']}: {r.get('message', 'N/A')}"
                          for r in critical_failures[:10]]
            pytest.fail(
                f"Found {len(critical_failures)} critical failures:\n" +
                "\n".join(failure_list)
            )

    def test_all_priorities_present(self):
        """All MoSCoW priorities should be represented"""
        results = ENGINE.validate_all()
        priorities = set(r['priority'] for r in results.results)

        expected_priorities = {'MUST', 'SHOULD', 'HAVE', 'CAN'}
        assert priorities >= expected_priorities, \
            f"Missing priorities: {expected_priorities - priorities}"

    def test_rule_distribution(self):
        """Test that rules are properly distributed across priorities"""
        results = ENGINE.validate_all()

        distribution = {}
        for r in results.results:
            priority = r['priority']
            distribution[priority] = distribution.get(priority, 0) + 1

        # MUST rules should be the largest category (critical requirements)
        assert distribution.get('MUST', 0) > 0, "No MUST rules found"

        # Should have SHOULD rules (important requirements)
        assert distribution.get('SHOULD', 0) > 0, "No SHOULD rules found"

        print(f"\nRule Distribution:")
        for priority in ['MUST', 'SHOULD', 'HAVE', 'CAN']:
            count = distribution.get(priority, 0)
            pct = (count / results.total_rules) * 100
            print(f"  {priority}: {count} ({pct:.1f}%)")


# ========================================================================
# REPORTING
# ========================================================================

def test_generate_final_report(tmp_path):
    """Generate final test report with all metrics"""
    results = ENGINE.validate_all()

    report = {
        'total_rules': results.total_rules,
        'passed': results.passed,
        'failed': results.failed,
        'pass_rate': (results.passed / results.total_rules) * 100,
        'moscow_scores': {},
        'category_scores': {},
    }

    # MoSCoW scores
    for priority in ['MUST', 'SHOULD', 'HAVE', 'CAN']:
        priority_results = [r for r in results.results if r['priority'] == priority]
        if priority_results:
            passed = sum(1 for r in priority_results if r['status'] == 'pass')
            report['moscow_scores'][priority] = {
                'total': len(priority_results),
                'passed': passed,
                'pass_rate': (passed / len(priority_results)) * 100
            }

    # Category scores
    categories = set(r['category'] for r in results.results)
    for category in categories:
        cat_results = [r for r in results.results if r['category'] == category]
        passed = sum(1 for r in cat_results if r['status'] == 'pass')
        report['category_scores'][category] = {
            'total': len(cat_results),
            'passed': passed,
            'pass_rate': (passed / len(cat_results)) * 100
        }

    # Save report
    report_path = tmp_path / 'test_report.json'
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

    print(f"\n[TEST REPORT]")
    print(f"Total Rules: {report['total_rules']}")
    print(f"Passed: {report['passed']}")
    print(f"Pass Rate: {report['pass_rate']:.2f}%")
    print(f"\nReport saved to: {report_path}")


if __name__ == '__main__':
    # Run tests with verbose output
    pytest.main([__file__, '-v', '--tb=short', '-x'])
