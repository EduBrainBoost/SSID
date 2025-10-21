"""
Test Enhanced Validators - Verify 6 Missing Rules Integration
==============================================================
This script tests the enhanced validation functions to verify they properly
enforce the specific requirements that were identified as missing/partial.

Tests:
- VG002: Breaking Changes Migration Guide completeness
- VG003: Deprecation 180-day notice enforcement
- VG004: RFC process structure validation
- DC003_CANARY: Canary deployment stages (5%→25%→50%→100%)
- TS005_MTLS: mTLS enforcement in every chart.yaml
- MD-PRINC-020: Auto-documentation generation

Run: python test_enhanced_validators.py
"""

from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from enhanced_validators import EnhancedValidators


def test_enhanced_validators():
    """Test all enhanced validators"""
    repo_root = Path(__file__).parent.parent.parent.parent  # Navigate to SSID root

    print("=" * 80)
    print("TESTING ENHANCED VALIDATORS - ROOT-24-LOCK ENFORCEMENT")
    print("=" * 80)
    print(f"Repository Root: {repo_root}")
    print()

    validator = EnhancedValidators(repo_root)

    # Run all enhanced validations
    results = validator.validate_all_enhanced()

    # Print results
    passed_count = 0
    failed_count = 0

    for result in results:
        status_symbol = "✅" if result.passed else "❌"
        print(f"\n{status_symbol} {result.rule_id} [{result.severity.value}]")
        print(f"   {result.message}")
        print(f"   Evidence:")
        for key, value in result.evidence.items():
            if isinstance(value, (list, dict)) and len(str(value)) > 100:
                print(f"     - {key}: {str(value)[:100]}...")
            else:
                print(f"     - {key}: {value}")

        if result.passed:
            passed_count += 1
        else:
            failed_count += 1

    # Summary
    print("\n" + "=" * 80)
    print(f"SUMMARY: {passed_count}/{len(results)} enhanced rules passed")
    print("=" * 80)

    if failed_count > 0:
        print(f"\n⚠️  {failed_count} enhanced rules need attention:")
        for result in results:
            if not result.passed:
                print(f"   - {result.rule_id}: {result.message}")

    return passed_count, failed_count


if __name__ == "__main__":
    passed, failed = test_enhanced_validators()
    sys.exit(0 if failed == 0 else 1)
