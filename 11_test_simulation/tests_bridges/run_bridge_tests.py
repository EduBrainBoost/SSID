#!/usr/bin/env python
"""
Bridge Test Runner
Runs all bridge tests and generates evidence report.
"""

import sys
import os
import importlib.util
import datetime
import json
import hashlib

# Add project root to path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, PROJECT_ROOT)


def load_module_from_path(module_name, file_path):
    """Dynamically load a module from a file path."""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec and spec.loader:
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    raise NotImplementedError("TODO: Implement this function")


def test_bridge(bridge_name, bridge_path, test_func):
    """Test a single bridge."""
    print(f"\nTesting: {bridge_name}")
    print("=" * 60)

    try:
        module = load_module_from_path(bridge_name, bridge_path)
        if module is None:
            print(f"  [FAIL] Could not load module")
            return False

        # Run test function
        result = test_func(module)
        if result:
            print(f"  [PASS] {bridge_name}")
            return True
        else:
            print(f"  [FAIL] {bridge_name}")
            return False

    except Exception as e:
        print(f"  [ERROR] {bridge_name}: {str(e)}")
        return False


def test_core_foundation(module):
    """Test 03_core -> 20_foundation bridge."""
    info = module.get_token_info()
    assert "symbol" in info
    assert info["symbol"] == "SSID"
    assert module.validate_token_operation("transfer", 1000) is True
    assert module.validate_token_operation("invalid", 1000) is False
    return True


def test_foundation_meta(module):
    """Test 20_foundation -> 24_meta_orchestration bridge."""
    import tempfile
    temp_file = os.path.join(tempfile.gettempdir(), "test_lock.json")

    result = module.record_registry_lock(temp_file)
    assert "ts" in result
    assert "hash" in result

    integrity = module.verify_lock_integrity(temp_file)
    assert integrity is True

    # Cleanup
    if os.path.exists(temp_file):
        os.remove(temp_file)

    return True


def test_ai_compliance(module):
    """Test 01_ai_layer -> 23_compliance bridge."""
    decision = {
        "confidence": 0.85,
        "explanation": "Test decision",
        "bias_score": 0.2,
    }

    result = module.validate_ai_decision(decision)
    assert result is True

    bad_decision = {"confidence": 0.5, "bias_score": 0.5}
    result = module.validate_ai_decision(bad_decision)
    assert result is False

    return True


def test_audit_compliance(module):
    """Test 02_audit_logging -> 23_compliance bridge."""
    entry = module.create_audit_entry("test", {"data": "value"})
    assert "timestamp" in entry
    assert "hash" in entry

    return True


def test_interop_identity(module):
    """Test 10_interoperability -> 09_meta_identity bridge."""
    did = "did:ssid:test123"
    doc = module.resolve_external_did(did)
    assert "id" in doc
    assert doc["id"] == did

    validation = module.validate_did_format(did)
    assert validation["valid"] is True

    return True


def test_auth_identity(module):
    """Test 14_zero_time_auth -> 08_identity_score bridge."""
    profile = {
        "kyc_verified": True,
        "credential_count": 10,
        "reputation_score": 0.9,
        "compliance_flags": 0.95,
        "activity_score": 0.8,
        "sanctions_hit": False,
        "fraud_suspected": False,
    }

    score = module.auth_trust_level(profile)
    assert isinstance(score, int)
    assert 0 <= score <= 100

    risk = module.classify_auth_risk(profile)
    assert risk in ["low", "medium", "high", "critical"]

    return True


def main():
    """Run all bridge tests."""
    print("Bridge Validation Test Suite")
    print("=" * 60)

    bridges = [
        ("03_core -> 20_foundation", "03_core/interconnect/bridge_foundation.py", test_core_foundation),
        ("20_foundation -> 24_meta_orchestration", "20_foundation/interconnect/bridge_meta_orchestration.py", test_foundation_meta),
        ("01_ai_layer -> 23_compliance", "01_ai_layer/interconnect/bridge_compliance.py", test_ai_compliance),
        ("02_audit_logging -> 23_compliance", "02_audit_logging/interconnect/bridge_compliance_push.py", test_audit_compliance),
        ("10_interoperability -> 09_meta_identity", "10_interoperability/interconnect/bridge_meta_identity.py", test_interop_identity),
        ("14_zero_time_auth -> 08_identity_score", "14_zero_time_auth/interconnect/bridge_identity_score.py", test_auth_identity),
    ]

    results = []
    for name, path, test_func in bridges:
        bridge_path = os.path.join(PROJECT_ROOT, path)
        passed = test_bridge(name, bridge_path, test_func)
        results.append((name, passed))

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)

    for name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} {name}")

    print(f"\nTotal: {passed_count}/{total_count} passed")

    # Generate evidence
    if passed_count == total_count:
        generate_evidence(passed_count)
        print("\n[SUCCESS] All bridges validated!")
        return 0
    else:
        print("\n[FAILURE] Some bridges failed validation")
        return 1


def generate_evidence(bridges_verified):
    """Generate evidence log."""
    evidence_dir = os.path.join(PROJECT_ROOT, "24_meta_orchestration/registry/logs")
    os.makedirs(evidence_dir, exist_ok=True)

    evidence = {
        "bridges_verified": bridges_verified,
        "status": "PASS",
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "test_runner": "manual",
    }

    evidence["hash"] = hashlib.sha256(
        json.dumps(evidence, sort_keys=True).encode()
    ).hexdigest()

    log_file = os.path.join(
        evidence_dir,
        f"bridge_validation_{datetime.datetime.utcnow().strftime('%Y%m%d')}.log"
    )

    with open(log_file, "a") as f:
        f.write(json.dumps(evidence) + "\n")

    print(f"\nEvidence logged to: {log_file}")
    print(json.dumps(evidence, indent=2))


if __name__ == "__main__":
    sys.exit(main())
