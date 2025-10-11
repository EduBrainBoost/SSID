#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
proof_emitter.py — On-chain Proof-Emit für Blueprint 4.2 Aktivierung
SAFE-FIX: schreibt nur nach 02_audit_logging/evidence/blockchain/emits/*.jsonl

Unterstützt:
- Web3.py mit EIP-1559 (Polygon Mumbai)
- DRY_RUN-Modus für Tests ohne Netzverbindung
- Deterministische Audit-Logs
- Non-custodial: Nur Hashes/URIs on-chain
"""

import os
import json
import hashlib
import sys
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[2]
ABI_PATH = ROOT / "20_foundation" / "smart_contracts" / "abi" / "ComplianceProofVerifier.json"
ADDR_PATH = ROOT / "20_foundation" / "smart_contracts" / "addresses.json"
EVID_DIR = ROOT / "02_audit_logging" / "evidence" / "blockchain" / "emits"
LOCK = ROOT / "24_meta_orchestration" / "registry" / "locks" / "registry_lock.yaml"


def load_registry_hash() -> str:
    """
    Compute SHA-256 hash of registry_lock.yaml as bytes32-compatible hex.

    Returns:
        str: Hex string starting with '0x' (64 chars after 0x)
    """
    raw = LOCK.read_bytes()
    h = hashlib.sha256(raw).digest()
    return "0x" + h.hex()


def log_emit(entry: dict):
    """
    Append entry to audit log in JSONL format.

    Args:
        entry: Dictionary with emit details
    """
    EVID_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.utcnow().isoformat(timespec='seconds') + "Z"
    entry = {"ts": ts, **entry}
    log_file = EVID_DIR / "blueprint42_proof.jsonl"
    with log_file.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def emit(proof_type: str, metadata_uri: str) -> dict:
    """
    Emit on-chain proof to Polygon Mumbai via ComplianceProofVerifier contract.

    Args:
        proof_type: Type of proof (e.g., "BLUEPRINT_4_2_ACTIVATION")
        metadata_uri: IPFS or HTTPS URI with proof metadata

    Returns:
        dict: Result with status, tx hash (if live), and registry_hash

    Environment Variables (for LIVE mode):
        MUMBAI_RPC_URL: RPC endpoint URL
        MUMBAI_PRIVATE_KEY: Private key for signing (0x prefixed)
        COMPLIANCE_VERIFIER_ADDR: Contract address (0x prefixed)
        DRY_RUN: Set to "1" to simulate without network
    """
    registry_hash = load_registry_hash()
    dry_run = os.getenv("DRY_RUN", "0") == "1"

    # Base log data
    base = {
        "component": "onchain_proof",
        "network": "polygon-mumbai",
        "proof_type": proof_type,
        "registry_hash": registry_hash,
        "metadata_uri": metadata_uri
    }

    # DRY_RUN mode: simulate without network
    if dry_run:
        log_emit({**base, "mode": "DRY_RUN", "tx": None, "status": "SIMULATED"})
        print(f"[DRY_RUN] Would emit proof: {proof_type}", file=sys.stderr)
        print(f"[DRY_RUN] Registry hash: {registry_hash}", file=sys.stderr)
        return {"status": "SIMULATED", "tx": None, "registry_hash": registry_hash}

    # LIVE mode: actual blockchain transaction
    try:
        from web3 import Web3
    except ImportError:
        log_emit({**base, "mode": "LIVE", "tx": None, "status": "ERROR", "error": "web3 not installed"})
        raise RuntimeError("web3 library not installed. Run: pip install web3")

    # Load environment
    rpc = os.getenv("MUMBAI_RPC_URL")
    priv = os.getenv("MUMBAI_PRIVATE_KEY")
    contract_addr_raw = os.getenv("COMPLIANCE_VERIFIER_ADDR")

    if not all([rpc, priv, contract_addr_raw]):
        missing = [k for k, v in {
            "MUMBAI_RPC_URL": rpc,
            "MUMBAI_PRIVATE_KEY": priv,
            "COMPLIANCE_VERIFIER_ADDR": contract_addr_raw
        }.items() if not v]
        error_msg = f"Missing required env vars: {', '.join(missing)}"
        log_emit({**base, "mode": "LIVE", "tx": None, "status": "ERROR", "error": error_msg})
        raise ValueError(error_msg)

    # Initialize Web3
    w3 = Web3(Web3.HTTPProvider(rpc))

    if not w3.is_connected():
        log_emit({**base, "mode": "LIVE", "tx": None, "status": "ERROR", "error": "RPC connection failed"})
        raise ConnectionError(f"Cannot connect to RPC: {rpc}")

    # Load account
    acct = w3.eth.account.from_key(priv)
    contract_addr = Web3.to_checksum_address(contract_addr_raw)

    # Load ABI
    abi = json.loads(ABI_PATH.read_text(encoding="utf-8"))
    contract = w3.eth.contract(address=contract_addr, abi=abi)

    # Build transaction (EIP-1559)
    nonce = w3.eth.get_transaction_count(acct.address)

    # Convert registry_hash to bytes32
    registry_hash_bytes = Web3.to_bytes(hexstr=registry_hash)

    tx = contract.functions.submitProof(
        registry_hash_bytes,
        proof_type,
        metadata_uri
    ).build_transaction({
        "from": acct.address,
        "nonce": nonce,
        "maxFeePerGas": w3.to_wei("30", "gwei"),
        "maxPriorityFeePerGas": w3.to_wei("2", "gwei"),
        "gas": 250000,
        "chainId": 80001  # Polygon Mumbai
    })

    # Sign and send
    signed = acct.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction).hex()

    log_emit({**base, "mode": "LIVE", "tx": tx_hash, "status": "SUBMITTED", "from": acct.address})

    print(f"[LIVE] Transaction submitted: {tx_hash}", file=sys.stderr)
    print(f"[LIVE] Explorer: https://mumbai.polygonscan.com/tx/{tx_hash}", file=sys.stderr)

    return {
        "status": "SUBMITTED",
        "tx": tx_hash,
        "registry_hash": registry_hash,
        "from": acct.address,
        "explorer_url": f"https://mumbai.polygonscan.com/tx/{tx_hash}"
    }


def main():
    """
    CLI entry point for proof emission.

    Usage:
        # Dry run (simulation)
        DRY_RUN=1 python proof_emitter.py

        # Live (requires secrets)
        MUMBAI_RPC_URL=... MUMBAI_PRIVATE_KEY=... COMPLIANCE_VERIFIER_ADDR=... python proof_emitter.py
    """
    # Standard use case for Blueprint 4.2 activation
    metadata_uri = os.getenv(
        "PROOF_METADATA_URI",
        "ipfs://blueprint42/manifest.json"  # CI can override
    )

    proof_type = "BLUEPRINT_4_2_ACTIVATION"

    try:
        result = emit(proof_type=proof_type, metadata_uri=metadata_uri)
        print(json.dumps(result, indent=2))
        sys.exit(0)
    except Exception as e:
        error_result = {
            "status": "ERROR",
            "error": str(e),
            "proof_type": proof_type
        }
        print(json.dumps(error_result, indent=2), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
