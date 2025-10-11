#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pytest Configuration - Automatic Proof Emission
SSID Phase 3 Implementation

Purpose:
- Automatically emit compliance proofs after each test execution
- Integrate with 03_evidence_system/blockchain/proof_emitter.py
- Enable immutable test evidence trails

Usage:
    Copy this to conftest.py in test directory:
    cp 11_test_simulation/conftest_proof_emitter.py 11_test_simulation/conftest.py

    Or merge with existing conftest.py.

Integration:
- Every pytest test execution → automatic proof emission
- Proof stored locally: 03_evidence_system/proofs/{date}/proofs.jsonl
- Optional blockchain anchoring (disabled by default)

Compliance:
- DORA: Automated audit trails
- GDPR Art. 30: Processing activity records
- MiCA: Test evidence for fraud detection
"""

import pytest
import sys
import os
from pathlib import Path

# Add project root to Python path
repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root))

from _03_evidence_system.blockchain.proof_emitter import ProofEmitter, ProofType


# Initialize proof emitter (shared across all tests)
_proof_emitter = None


def get_proof_emitter():
    """Get or create proof emitter instance"""
    global _proof_emitter

    if _proof_emitter is None:
        repo_root = Path(__file__).resolve().parents[1]

        # Check if blockchain should be enabled via environment variable
        enable_blockchain = os.environ.get("SSID_BLOCKCHAIN_PROOFS", "false").lower() == "true"

        _proof_emitter = ProofEmitter(repo_root, enable_blockchain=enable_blockchain)

    return _proof_emitter


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Pytest hook: Emit proof after each test execution.

    This hook is called after each test phase (setup, call, teardown).
    We only emit proofs for the 'call' phase (actual test execution).

    Args:
        item: Test item (contains test metadata)
        call: Test call information

    Yields:
        Test report outcome
    """
    # Execute test and get outcome
    outcome = yield
    report = outcome.get_result()

    # Only emit proof for test call phase (not setup/teardown)
    if report.when != "call":
        return

    # Get proof emitter
    try:
        emitter = get_proof_emitter()
    except Exception as e:
        print(f"Warning: Failed to initialize proof emitter: {e}")
        return

    # Prepare proof data
    proof_data = {
        "test_name": item.nodeid,
        "test_result": report.outcome,  # passed, failed, skipped
        "test_duration": report.duration,
        "test_module": item.module.__name__ if hasattr(item, 'module') else "unknown",
        "test_function": item.name
    }

    # Add failure information if test failed
    if report.failed:
        if hasattr(report, 'longrepr'):
            proof_data["failure_info"] = str(report.longrepr)[:500]  # Truncate for storage

    # Prepare metadata
    metadata = {
        "test_file": str(item.fspath),
        "test_line": item.location[1] if item.location else 0,
        "ci_workflow": os.environ.get("GITHUB_WORKFLOW", "local"),
        "commit_hash": os.environ.get("GITHUB_SHA", "local"),
        "branch": os.environ.get("GITHUB_REF_NAME", "local"),
        "runner": os.environ.get("RUNNER_NAME", "local")
    }

    # Prepare evidence references
    evidence_refs = [
        f"test_run:{item.nodeid}",
        f"ci_workflow:{metadata['ci_workflow']}"
    ]

    if metadata["commit_hash"] != "local":
        evidence_refs.append(f"commit:{metadata['commit_hash']}")

    # Emit proof
    try:
        proof = emitter.emit_proof(
            proof_type=ProofType.TEST_EXECUTION,
            proof_data=proof_data,
            evidence_refs=evidence_refs,
            metadata=metadata
        )

        # Print proof confirmation (visible in pytest output)
        if os.environ.get("SSID_VERBOSE_PROOFS", "false").lower() == "true":
            print(f"\n✅ Proof emitted: {proof.proof_id} (hash: {proof.proof_hash[:16]}...)")

    except Exception as e:
        print(f"\n⚠️  Warning: Failed to emit proof for {item.nodeid}: {e}")


@pytest.fixture(scope="session")
def proof_emitter():
    """
    Pytest fixture: Access to proof emitter in tests.

    Usage:
        def test_something(proof_emitter):
            # Manually emit a custom proof
            proof = proof_emitter.emit_proof(
                proof_type=ProofType.BADGE_INTEGRITY,
                proof_data={"badge_id": "test_badge"},
                evidence_refs=["manual_test"]
            )
    """
    return get_proof_emitter()


@pytest.fixture(scope="session", autouse=True)
def print_proof_summary(request):
    """
    Pytest fixture: Print proof summary at end of test session.

    Args:
        request: Pytest request object

    This fixture automatically runs at the end of the test session
    and prints a summary of all emitted proofs.
    """
    yield  # Run all tests first

    # Print summary at end of session
    try:
        emitter = get_proof_emitter()

        # Get today's proofs
        import time
        today_start = int(time.time()) - 86400  # Last 24 hours
        today_end = int(time.time())

        proofs = emitter.query_proofs(
            start_timestamp=today_start,
            end_timestamp=today_end
        )

        # Calculate statistics
        test_proofs = [p for p in proofs if p.proof_type == ProofType.TEST_EXECUTION.value]
        passed_tests = sum(1 for p in test_proofs if "passed" in p.metadata.get("test_result", ""))
        failed_tests = sum(1 for p in test_proofs if "failed" in p.metadata.get("test_result", ""))

        print("\n" + "=" * 70)
        print("SSID COMPLIANCE PROOF SUMMARY")
        print("=" * 70)
        print(f"Total proofs emitted today: {len(proofs)}")
        print(f"Test execution proofs: {len(test_proofs)}")
        print(f"  ✅ Passed: {passed_tests}")
        print(f"  ❌ Failed: {failed_tests}")
        print(f"Proof log: {emitter.proof_log}")
        print(f"Proof index: {emitter.proof_index_file}")

        if emitter.enable_blockchain:
            blockchain_proofs = sum(1 for p in proofs if p.blockchain_tx)
            print(f"Blockchain anchored: {blockchain_proofs}/{len(proofs)}")

        print("=" * 70)

    except Exception as e:
        print(f"\n⚠️  Warning: Failed to generate proof summary: {e}")


def pytest_configure(config):
    """
    Pytest hook: Configure proof emission system.

    Args:
        config: Pytest configuration object

    This hook runs once at pytest startup.
    """
    # Add custom markers for proof emission
    config.addinivalue_line(
        "markers",
        "emit_proof: Emit compliance proof for this test"
    )

    config.addinivalue_line(
        "markers",
        "no_proof: Skip proof emission for this test"
    )

    # Print configuration
    if config.option.verbose >= 1:
        print("\n" + "=" * 70)
        print("SSID COMPLIANCE PROOF SYSTEM INITIALIZED")
        print("=" * 70)

        blockchain_enabled = os.environ.get("SSID_BLOCKCHAIN_PROOFS", "false").lower() == "true"
        verbose_proofs = os.environ.get("SSID_VERBOSE_PROOFS", "false").lower() == "true"

        print(f"Blockchain anchoring: {'✅ ENABLED' if blockchain_enabled else '❌ DISABLED'}")
        print(f"Verbose proof output: {'✅ ENABLED' if verbose_proofs else '❌ DISABLED'}")
        print("=" * 70 + "\n")


# Optional: Custom assertion hook for proof emission
def pytest_assertrepr_compare(op, left, right):
    """
    Pytest hook: Custom assertion representations.

    This can be extended to emit proofs on specific assertion failures.
    """
    raise NotImplementedError("TODO: Implement this block")


# Optional: Add proof emission to xfail/skip
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_call(item):
    """
    Pytest hook: Wrap test execution.

    Can be used to emit proofs for skipped/xfail tests.
    """
    outcome = yield
    # Add custom logic if needed


# Environment variable documentation
"""
ENVIRONMENT VARIABLES:

SSID_BLOCKCHAIN_PROOFS (default: false)
    Enable blockchain proof anchoring to Polygon Mumbai.
    Set to "true" to enable.

    Example:
        export SSID_BLOCKCHAIN_PROOFS=true
        pytest

SSID_VERBOSE_PROOFS (default: false)
    Print proof confirmation after each test.
    Set to "true" to enable.

    Example:
        export SSID_VERBOSE_PROOFS=true
        pytest -v

GITHUB_WORKFLOW (set by GitHub Actions)
    CI workflow name. Automatically included in proof metadata.

GITHUB_SHA (set by GitHub Actions)
    Commit hash. Automatically included in proof metadata.

GITHUB_REF_NAME (set by GitHub Actions)
    Branch name. Automatically included in proof metadata.
"""

# Usage examples
"""
USAGE EXAMPLES:

1. Basic pytest execution (local proofs only):
   pytest

2. Enable blockchain anchoring:
   export SSID_BLOCKCHAIN_PROOFS=true
   pytest

3. Verbose proof output:
   export SSID_VERBOSE_PROOFS=true
   pytest -v

4. CI/CD integration (GitHub Actions):
   - name: Run tests with proof emission
     env:
       SSID_BLOCKCHAIN_PROOFS: true
       SSID_VERBOSE_PROOFS: true
     run: pytest -v --tb=short

5. Manual proof emission in test:
   def test_custom_proof(proof_emitter):
       # Your test code...

       # Manually emit a proof
       proof = proof_emitter.emit_proof(
           proof_type=ProofType.AUDIT_EVENT,
           proof_data={"event": "custom_check"},
           evidence_refs=["manual_audit"]
       )

       assert proof.proof_id is not None

6. Skip proof emission for specific test:
   @pytest.mark.no_proof
   def test_without_proof():
       # This test won't emit a proof
       raise NotImplementedError("TODO: Implement this block")
"""
