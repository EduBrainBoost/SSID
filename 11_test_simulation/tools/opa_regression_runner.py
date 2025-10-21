#!/usr/bin/env python3
"""
OPA Regression Runner - v5.2 Compliance Matrix
Executes 25+ policy test fixtures against pricing and RAT enforcement policies.
Generates consolidated compliance report with PASS/FAIL, timing, and hash verification.
"""

import argparse
import hashlib
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

def sha256_file(path: Path) -> str:
    """Calculate SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()

def load_test_fixtures(fixture_path: Path) -> List[Dict[str, Any]]:
    """Load test fixtures from JSON file."""
    try:
        with open(fixture_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            elif isinstance(data, dict) and 'tests' in data:
                return data['tests']
            else:
                return [data]
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading fixtures from {fixture_path}: {e}", file=sys.stderr)
        return []

def run_opa_eval(
    policy_path: Path,
    query: str,
    input_data: Dict[str, Any],
    wasm_bundle: Optional[Path] = None
) -> Tuple[bool, Optional[Dict[str, Any]], float, Optional[str]]:
    """
    Run OPA evaluation and return (success, result, duration, error).

    Returns:
        (success, result_dict, duration_seconds, error_message)
    """
    start = time.time()

    try:
        # Write input data to temp file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
            json.dump(input_data, tmp)
            tmp_path = tmp.name

        # Build OPA command
        if wasm_bundle and wasm_bundle.exists():
            # Use WASM bundle
            cmd = [
                'opa', 'eval',
                '--bundle', str(wasm_bundle),
                '--input', tmp_path,
                '--format', 'json',
                query
            ]
        else:
            # Use Rego file
            cmd = [
                'opa', 'eval',
                '--data', str(policy_path),
                '--input', tmp_path,
                '--format', 'json',
                query
            ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )

        duration = time.time() - start

        # Clean up temp file
        Path(tmp_path).unlink(missing_ok=True)

        if result.returncode == 0:
            output = json.loads(result.stdout)
            return (True, output, duration, None)
        else:
            return (False, None, duration, result.stderr)

    except subprocess.TimeoutExpired:
        duration = time.time() - start
        return (False, None, duration, "OPA evaluation timeout")
    except json.JSONDecodeError as e:
        duration = time.time() - start
        return (False, None, duration, f"Invalid JSON output: {e}")
    except Exception as e:
        duration = time.time() - start
        return (False, None, duration, str(e))

def extract_opa_result(opa_output: Dict[str, Any]) -> Optional[bool]:
    """Extract boolean result from OPA JSON output."""
    try:
        if 'result' in opa_output:
            result_list = opa_output['result']
            if isinstance(result_list, list) and len(result_list) > 0:
                expressions = result_list[0].get('expressions', [])
                if expressions and len(expressions) > 0:
                    value = expressions[0].get('value')
                    if isinstance(value, bool):
                        return value
                    elif isinstance(value, dict):
                        # Handle structured result (e.g., {allow: true})
                        return value.get('allow', False)
        return None
    except (KeyError, IndexError, TypeError):
        return None

def run_test_suite(
    policy_path: Path,
    query: str,
    fixtures: List[Dict[str, Any]],
    wasm_bundle: Optional[Path] = None
) -> List[Dict[str, Any]]:
    """Run all test fixtures and collect results."""
    results = []

    for idx, fixture in enumerate(fixtures):
        test_name = fixture.get('name', f'test_{idx}')
        input_data = fixture.get('input', {})
        expected = fixture.get('expected', {})
        expected_result = expected.get('allow', False)

        success, opa_output, duration, error = run_opa_eval(
            policy_path, query, input_data, wasm_bundle
        )

        if success and opa_output:
            actual_result = extract_opa_result(opa_output)
            passed = (actual_result == expected_result)
        else:
            actual_result = None
            passed = False

        result = {
            'test_name': test_name,
            'passed': passed,
            'expected': expected_result,
            'actual': actual_result,
            'duration_seconds': round(duration, 4),
            'error': error,
            'input_summary': {
                k: (v if not isinstance(v, (dict, list)) else f"<{type(v).__name__}>")
                for k, v in list(input_data.items())[:5]
            }
        }

        results.append(result)

    return results

def main():
    parser = argparse.ArgumentParser(
        description='Run OPA regression test suite for v5.2 compliance'
    )
    parser.add_argument(
        '--pricing-policy',
        type=Path,
        default=Path('23_compliance/policies/pricing_enforcement_v5_2.rego'),
        help='Path to pricing enforcement policy'
    )
    parser.add_argument(
        '--rat-policy',
        type=Path,
        default=Path('23_compliance/policies/rat_enforcement_v5_2.rego'),
        help='Path to RAT enforcement policy'
    )
    parser.add_argument(
        '--pricing-wasm',
        type=Path,
        help='Path to pricing WASM bundle (optional)'
    )
    parser.add_argument(
        '--rat-wasm',
        type=Path,
        help='Path to RAT WASM bundle (optional)'
    )
    parser.add_argument(
        '--pricing-fixtures',
        type=Path,
        nargs='+',
        default=[
            Path('11_test_simulation/testdata/pricing_v5_2_happy.json'),
            Path('11_test_simulation/testdata/pricing_v5_2_edges.json')
        ],
        help='Pricing test fixture files'
    )
    parser.add_argument(
        '--rat-fixtures',
        type=Path,
        nargs='+',
        default=[
            Path('11_test_simulation/testdata/rat_v5_2_happy.json'),
            Path('11_test_simulation/testdata/rat_v5_2_edges.json')
        ],
        help='RAT test fixture files'
    )
    parser.add_argument(
        '--env',
        choices=['dev', 'stage', 'prod'],
        default='dev',
        help='Environment tag'
    )
    parser.add_argument(
        '--out',
        type=Path,
        required=True,
        help='Output report path (JSON)'
    )

    args = parser.parse_args()

    # Calculate policy hashes
    pricing_hash = sha256_file(args.pricing_policy) if args.pricing_policy.exists() else None
    rat_hash = sha256_file(args.rat_policy) if args.rat_policy.exists() else None
    pricing_wasm_hash = sha256_file(args.pricing_wasm) if args.pricing_wasm and args.pricing_wasm.exists() else None
    rat_wasm_hash = sha256_file(args.rat_wasm) if args.rat_wasm and args.rat_wasm.exists() else None

    # Load all fixtures
    pricing_fixtures = []
    for fixture_file in args.pricing_fixtures:
        if fixture_file.exists():
            pricing_fixtures.extend(load_test_fixtures(fixture_file))

    rat_fixtures = []
    for fixture_file in args.rat_fixtures:
        if fixture_file.exists():
            rat_fixtures.extend(load_test_fixtures(fixture_file))

    # Run pricing tests
    print(f"Running {len(pricing_fixtures)} pricing tests...")
    pricing_results = run_test_suite(
        args.pricing_policy,
        'data.ssid.pricing.v5_2.allow',
        pricing_fixtures,
        args.pricing_wasm
    )

    # Run RAT tests
    print(f"Running {len(rat_fixtures)} RAT tests...")
    rat_results = run_test_suite(
        args.rat_policy,
        'data.ssid.rat.enforcement.v5_2.valid',
        rat_fixtures,
        args.rat_wasm
    )

    # Calculate summary
    total_tests = len(pricing_results) + len(rat_results)
    pricing_passed = sum(1 for r in pricing_results if r['passed'])
    rat_passed = sum(1 for r in rat_results if r['passed'])
    total_passed = pricing_passed + rat_passed

    # Generate report
    report = {
        'version': '5.2',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'environment': args.env,
        'summary': {
            'total_tests': total_tests,
            'total_passed': total_passed,
            'total_failed': total_tests - total_passed,
            'pass_rate': round(total_passed / total_tests * 100, 2) if total_tests > 0 else 0,
            'pricing_tests': len(pricing_results),
            'pricing_passed': pricing_passed,
            'rat_tests': len(rat_results),
            'rat_passed': rat_passed
        },
        'policy_hashes': {
            'pricing_policy': pricing_hash,
            'rat_policy': rat_hash,
            'pricing_wasm': pricing_wasm_hash,
            'rat_wasm': rat_wasm_hash
        },
        'results': {
            'pricing': pricing_results,
            'rat': rat_results
        }
    }

    # Write report
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, sort_keys=True)

    # Print summary
    print(f"\n{'='*60}")
    print(f"OPA Regression Test Summary")
    print(f"{'='*60}")
    print(f"Total Tests:     {total_tests}")
    print(f"Passed:          {total_passed} ({report['summary']['pass_rate']}%)")
    print(f"Failed:          {total_tests - total_passed}")
    print(f"Pricing:         {pricing_passed}/{len(pricing_results)}")
    print(f"RAT:             {rat_passed}/{len(rat_results)}")
    print(f"{'='*60}")
    print(f"Report saved to: {args.out}")

    # Return exit code based on pass rate
    return 0 if total_passed == total_tests else 1

if __name__ == '__main__':
    sys.exit(main())
