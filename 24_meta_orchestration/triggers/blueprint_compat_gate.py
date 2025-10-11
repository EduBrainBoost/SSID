#!/usr/bin/env python3
"""
Blueprint 4.2 Compatibility Gate
Blockiert Merge/Deploy, wenn 4.2-Delta-Anforderungen nicht erfüllt sind.

Exit codes:
  0 = PASS
  1 = FAIL
"""
import sys
import json
import hashlib
import yaml
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]  # 24_meta_orchestration
REPO = ROOT.parent  # SSID root


def req(path: str) -> Path:
    """Verify required path exists."""
    p = REPO / path
    if not p.exists():
        print(f"❌ FAIL: Missing required path: {path}", file=sys.stderr)
        sys.exit(1)
    return p


def sha256(b: bytes) -> str:
    """Compute SHA-256 hash with prefix."""
    return "sha256:" + hashlib.sha256(b).hexdigest()


def load_yaml(path: Path) -> dict:
    """Load YAML file safely."""
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"❌ FAIL: Cannot load YAML from {path}: {e}", file=sys.stderr)
        sys.exit(1)


def load_json(path: Path) -> dict:
    """Load JSON file safely."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"❌ FAIL: Cannot load JSON from {path}: {e}", file=sys.stderr)
        sys.exit(1)


def check_required_paths():
    """Verify all required Blueprint 4.2 artifacts exist."""
    must_paths = [
        "24_meta_orchestration/consortium/consortium_registry.yaml",
        "24_meta_orchestration/consortium/consensus_policy.yaml",
        "23_compliance/policy_as_code/rego_policies/ssid_compliance_policy.rego",
        "13_ui_layer/synced_views/sync_metadata.json",
        "23_compliance/ai_ml_ready/snapshot_diffs/index.json",
        "24_meta_orchestration/registry/manifests/blueprint_4_2_manifest.yaml",
        "23_compliance/governance/blueprint_4_2_rfc.yaml",
    ]
    print("🔍 Checking required paths...")
    for m in must_paths:
        req(m)
        print(f"  ✓ {m}")


def check_registry_lock():
    """Verify registry_lock.yaml contains required Blueprint 4.2 fields."""
    print("\n🔍 Checking registry lock fields...")
    lock_path = req("24_meta_orchestration/registry/locks/registry_lock.yaml")
    lock = load_yaml(lock_path)

    if "consortium_status" not in lock:
        print("❌ FAIL: Missing consortium_status in registry_lock.yaml", file=sys.stderr)
        sys.exit(1)
    print("  ✓ consortium_status present")

    if "compliance_evidence" not in lock:
        print("❌ FAIL: Missing compliance_evidence in registry_lock.yaml", file=sys.stderr)
        sys.exit(1)
    print("  ✓ compliance_evidence present")

    # Optional: Check blueprint_version
    if "blueprint_version" in lock:
        print(f"  ✓ blueprint_version: {lock['blueprint_version']}")


def check_sync_integrity():
    """Verify sync integrity hash matches technical/legal view contents."""
    print("\n🔍 Checking sync integrity hash...")

    meta_path = req("13_ui_layer/synced_views/sync_metadata.json")
    tech_path = req("13_ui_layer/synced_views/technical_dashboard.json")
    legal_path = req("13_ui_layer/synced_views/legal_narrative.md")

    meta = load_json(meta_path)
    tech_bytes = tech_path.read_bytes()
    legal_bytes = legal_path.read_bytes()

    computed_hash = hashlib.sha256(tech_bytes + legal_bytes).hexdigest()

    if "integrity_hash" not in meta:
        print("❌ FAIL: Missing integrity_hash in sync_metadata.json", file=sys.stderr)
        sys.exit(1)

    stored_hash = meta["integrity_hash"]

    # Check if stored hash starts with computed hash prefix (at least 16 chars)
    if not stored_hash.startswith(computed_hash[:16]):
        print(f"❌ FAIL: Sync integrity mismatch", file=sys.stderr)
        print(f"  Expected prefix: {computed_hash[:16]}", file=sys.stderr)
        print(f"  Got: {stored_hash[:16]}", file=sys.stderr)
        sys.exit(1)

    print(f"  ✓ Integrity hash verified: {computed_hash[:16]}...")


def check_snapshot_diff_index():
    """Verify snapshot diff index exists and is valid."""
    print("\n🔍 Checking snapshot diff index...")

    index_path = req("23_compliance/ai_ml_ready/snapshot_diffs/index.json")
    index = load_json(index_path)

    if "snapshots" not in index:
        print("❌ FAIL: Missing 'snapshots' key in index.json", file=sys.stderr)
        sys.exit(1)

    print(f"  ✓ Snapshot index valid with {len(index['snapshots'])} entries")


def check_consortium_quorum():
    """Verify consortium meets BFT quorum requirements."""
    print("\n🔍 Checking consortium quorum requirements...")

    registry_path = req("24_meta_orchestration/consortium/consortium_registry.yaml")
    registry = load_yaml(registry_path)

    if "members" not in registry:
        print("❌ FAIL: Missing 'members' in consortium_registry.yaml", file=sys.stderr)
        sys.exit(1)

    members = registry["members"]

    # Calculate weighted score and distinct signers
    total_weight = 0
    distinct_signers = 0

    for member in members:
        if member.get("status") == "active":
            distinct_signers += 1
            total_weight += member.get("weight", 1)

    print(f"  Active signers: {distinct_signers}")
    print(f"  Total weighted score: {total_weight}")

    # BFT requirements: ≥11 weight, ≥5 distinct signers
    if total_weight < 11:
        print(f"❌ FAIL: Insufficient weighted quorum (need ≥11, got {total_weight})", file=sys.stderr)
        sys.exit(1)

    if distinct_signers < 5:
        print(f"❌ FAIL: Insufficient distinct signers (need ≥5, got {distinct_signers})", file=sys.stderr)
        sys.exit(1)

    print("  ✓ BFT quorum requirements met")


def emit_onchain_proof():
    """
    Trigger on-chain proof emission after gate PASS.

    Checks if blockchain secrets are set:
    - If available: Run proof_emitter.py in LIVE mode
    - If not available: Run in DRY_RUN mode (simulation)

    Non-blocking: Errors are logged but don't fail the gate.
    """
    print("\n🔗 On-chain Proof Emission")
    print("-" * 60)

    emitter_path = REPO / "20_foundation" / "smart_contracts" / "proof_emitter.py"

    if not emitter_path.exists():
        print("⚠️  Proof emitter not found, skipping on-chain emit")
        return

    # Check if blockchain secrets are available
    required_secrets = ["MUMBAI_RPC_URL", "MUMBAI_PRIVATE_KEY", "COMPLIANCE_VERIFIER_ADDR"]
    has_secrets = all(os.getenv(k) for k in required_secrets)

    env = os.environ.copy()

    if has_secrets:
        print("✓ Blockchain secrets detected, running LIVE emit")
        env["DRY_RUN"] = "0"
    else:
        print("ℹ️  No blockchain secrets, running DRY_RUN simulation")
        env["DRY_RUN"] = "1"

    try:
        result = subprocess.run(
            [sys.executable, str(emitter_path)],
            capture_output=True,
            text=True,
            env=env,
            cwd=str(REPO),
            timeout=30
        )

        if result.returncode == 0:
            # Parse JSON output
            try:
                output = json.loads(result.stdout)
                status = output.get("status", "UNKNOWN")
                tx = output.get("tx")

                if status == "SUBMITTED" and tx:
                    print(f"✅ Proof submitted: {tx}")
                    print(f"   Explorer: https://mumbai.polygonscan.com/tx/{tx}")
                elif status == "SIMULATED":
                    print(f"✅ Proof simulated (DRY_RUN)")
                    print(f"   Registry hash: {output.get('registry_hash', 'N/A')}")
                else:
                    print(f"✓ Emit completed with status: {status}")
            except json.JSONDecodeError:
                print("✓ Emit completed")
                print(result.stdout)
        else:
            print(f"⚠️  Proof emitter returned error (exit {result.returncode})")
            if result.stderr:
                print(f"   Error: {result.stderr[:200]}")

    except subprocess.TimeoutExpired:
        print("⚠️  Proof emitter timed out after 30s")
    except Exception as e:
        print(f"⚠️  On-chain emit error: {e}")

    print("-" * 60)


def main():
    """Run all Blueprint 4.2 compatibility checks."""
    print("=" * 60)
    print("Blueprint 4.2 Compatibility Gate")
    print("=" * 60)

    try:
        check_required_paths()
        check_registry_lock()
        check_sync_integrity()
        check_snapshot_diff_index()
        check_consortium_quorum()

        print("\n" + "=" * 60)
        print("✅ Blueprint 4.2 Compatibility Gate PASS")
        print("=" * 60)

        # On-chain Proof-Emit (optional, if secrets set)
        emit_onchain_proof()

        sys.exit(0)

    except SystemExit:
        raise
    except Exception as e:
        print(f"\n❌ FAIL: Unexpected error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
