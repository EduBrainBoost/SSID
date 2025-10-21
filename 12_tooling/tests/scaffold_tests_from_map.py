#!/usr/bin/env python3
"""
Test Scaffold Generator (v6.0)
Generates pytest skeletons and fixtures from governance map.

Usage:
    python scaffold_tests_from_map.py --roots 03_core 23_compliance
"""

import sys
import json
import argparse
from pathlib import Path
from typing import List

def generate_pytest_skeleton(root_name: str, capabilities: List[str], policies: List[dict], output_dir: Path):
    """Generate pytest skeleton for a root."""

    test_content = f'''#!/usr/bin/env python3
"""
Policy Tests for {root_name} (v6.0 - Pilot)
Auto-generated test skeleton with xfail markers for missing business logic.
"""

import pytest
import json
import subprocess
from pathlib import Path

POLICY_PATH = Path("23_compliance/policies/{root_name.replace("_", "")}_policy_v6_0.rego")
FIXTURE_DIR = Path("11_test_simulation/testdata/{root_name}/v6_0")

def run_opa_eval(policy_path: Path, input_data: dict) -> dict:
    """Run OPA eval command."""
    cmd = [
        "opa",
        "eval",
        "--data", str(policy_path),
        "--input", "-",
        "--format", "json",
        "data.ssid.{root_name.replace("_", "")}.v6_0.allow"
    ]

    result = subprocess.run(
        cmd,
        input=json.dumps(input_data).encode(),
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        pytest.fail(f"OPA eval failed: {{result.stderr}}")

    return json.loads(result.stdout)

class TestHappyPath:
    """Happy path tests - basic functionality."""
'''

    for i, capability in enumerate(capabilities[:3], 1):  # 3 happy tests
        test_content += f'''
    @pytest.mark.xfail(reason="Business logic not implemented - stub only", strict=False)
    def test_{capability}_happy_{i}(self):
        """Test {capability} with valid input."""
        # Load fixture
        fixture_file = FIXTURE_DIR / "happy.jsonl"
        if not fixture_file.exists():
            pytest.skip(f"Fixture not found: {{fixture_file}}")

        with open(fixture_file) as f:
            lines = f.readlines()
            if len(lines) < {i}:
                pytest.skip("Not enough fixtures")

            test_case = json.loads(lines[{i-1}])

            # Run OPA evaluation
            result = run_opa_eval(POLICY_PATH, test_case["input"])

            
            assert result["result"][0]["expressions"][0]["value"] == test_case["expect_allow"]
'''

    test_content += '''

class TestBoundaryConditions:
    """Boundary condition tests."""
'''

    for i in range(1, 3):  # 2 boundary tests
        test_content += f'''
    @pytest.mark.xfail(reason="Business logic not implemented - stub only", strict=False)
    def test_boundary_case_{i}(self):
        """Test boundary condition {i}."""
        fixture_file = FIXTURE_DIR / "boundary.jsonl"
        if not fixture_file.exists():
            pytest.skip(f"Fixture not found: {{fixture_file}}")

        with open(fixture_file) as f:
            lines = f.readlines()
            if len(lines) < {i}:
                pytest.skip("Not enough fixtures")

            test_case = json.loads(lines[{i-1}])
            result = run_opa_eval(POLICY_PATH, test_case["input"])

            # Currently xfail - business logic needed
            assert result["result"][0]["expressions"][0]["value"] == test_case.get("expect_allow", False)
'''

    test_content += '''

class TestNegativeCases:
    """Negative test cases - expected failures."""
'''

    test_content += '''
    @pytest.mark.xfail(reason="Business logic not implemented - stub only", strict=False)
    def test_negative_case_1(self):
        """Test denial case."""
        fixture_file = FIXTURE_DIR / "negative.jsonl"
        if not fixture_file.exists():
            pytest.skip(f"Fixture not found: {fixture_file}")

        with open(fixture_file) as f:
            test_case = json.loads(f.readline())
            result = run_opa_eval(POLICY_PATH, test_case["input"])

            # Should deny
            assert result["result"][0]["expressions"][0]["value"] == test_case.get("expect_allow", False)
'''

    output_file = output_dir / f"test_{root_name}_policy_v6_0.py"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(test_content)

    print(f"Generated pytest skeleton: {output_file}")

def generate_fixtures(root_name: str, capabilities: List[str], output_dir: Path):
    """Generate test fixtures (JSONL format)."""

    fixture_dir = output_dir / root_name / "v6_0"
    fixture_dir.mkdir(parents=True, exist_ok=True)

    # Happy fixtures
    happy_fixtures = []
    for cap in capabilities[:3]:
        happy_fixtures.append({
            "input": {
                "action": f"test_{cap}",
                "resource": {"type": "test", "id": "test-id", "data": {}},
                "subject": {"id": "user:test", "roles": ["admin"]},
                "context": {"timestamp": "2025-10-13T00:00:00Z", "environment": "dev"}
            },
            "expect_allow": True,
            "note": f"TODO: Replace with real {cap} test data"
        })

    with open(fixture_dir / "happy.jsonl", 'w') as f:
        for fixture in happy_fixtures:
            f.write(json.dumps(fixture) + '\n')

    # Boundary fixtures
    boundary_fixtures = [
        {
            "input": {
                "action": "boundary_test",
                "resource": {"type": "test", "id": "", "data": {}},
                "subject": {"id": "user:test", "roles": []},
                "context": {"timestamp": "2025-10-13T00:00:00Z", "environment": "dev"}
            },
            "expect_allow": False,
            "note": "TODO: Real boundary condition"
        },
        {
            "input": {
                "action": "boundary_test_2",
                "resource": {"type": "test", "id": "x" * 1000, "data": {}},
                "subject": {"id": "user:test", "roles": ["guest"]},
                "context": {"timestamp": "2025-10-13T00:00:00Z", "environment": "dev"}
            },
            "expect_allow": False,
            "note": "TODO: Real boundary condition"
        }
    ]

    with open(fixture_dir / "boundary.jsonl", 'w') as f:
        for fixture in boundary_fixtures:
            f.write(json.dumps(fixture) + '\n')

    # Negative fixtures
    negative_fixtures = [
        {
            "input": {
                "action": "unauthorized_action",
                "resource": {"type": "test", "id": "test-id", "data": {}},
                "subject": {"id": "user:test", "roles": []},
                "context": {"timestamp": "2025-10-13T00:00:00Z", "environment": "prod"}
            },
            "expect_allow": False,
            "note": "TODO: Real negative test case"
        }
    ]

    with open(fixture_dir / "negative.jsonl", 'w') as f:
        for fixture in negative_fixtures:
            f.write(json.dumps(fixture) + '\n')

    print(f"Generated fixtures: {fixture_dir}")

def main():
    parser = argparse.ArgumentParser(description="Generate test scaffolds from governance map")
    parser.add_argument("--roots", nargs='+', required=True, help="Root names to generate tests for")
    parser.add_argument("--map", type=Path, default=Path("02_audit_logging/reports/root_24_governance_map_v6_0.json"))
    parser.add_argument("--test-output", type=Path, default=Path("11_test_simulation/tests"))
    parser.add_argument("--fixture-output", type=Path, default=Path("11_test_simulation/testdata"))

    args = parser.parse_args()

    # Load governance map
    with open(args.map) as f:
        gov_map = json.load(f)

    for root_name in args.roots:
        # Find root in map
        root_data = None
        for r in gov_map["roots"]:
            if r["root"] == root_name:
                root_data = r
                break

        if not root_data:
            print(f"WARNING: Root {root_name} not found in governance map", file=sys.stderr)
            continue

        capabilities = root_data["chart"]["capabilities"]
        policies = root_data["chart"]["policies"]

        print(f"\n=== Generating tests for {root_name} ===")
        generate_pytest_skeleton(root_name, capabilities, policies, args.test_output)
        generate_fixtures(root_name, capabilities, args.fixture_output)

    print("\n[OK] Test scaffolds generated")

if __name__ == "__main__":
    main()
