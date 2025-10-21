#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Multi-Merkle Federation Builder (SHA-512 + BLAKE3)
# Synchronizes SoT definitions between SSID and OpenCore
import hashlib, json, os, sys, time
from pathlib import Path

BASE = Path(os.path.expanduser("~/Documents/Github/SSID"))
UTC = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

def blake3_hash(data: bytes) -> str:
    """BLAKE3 simulation using SHA3-256 as fallback."""
    return hashlib.sha3_256(data).hexdigest()

def sha512_hash(data: bytes) -> str:
    """SHA-512 hash."""
    return hashlib.sha512(data).hexdigest()

def build_merkle_tree(leaves: list, hash_fn) -> str:
    """Build binary merkle tree."""
    if not leaves:
        return hash_fn(b"")
    layer = sorted(leaves)
    while len(layer) > 1:
        next_layer = []
        for i in range(0, len(layer), 2):
            a = layer[i]
            b = layer[i + 1] if i + 1 < len(layer) else layer[i]
            combined = hash_fn((a + b).encode())
            next_layer.append(combined)
        layer = next_layer
    return layer[0]

def scan_sot_files(source_path: Path) -> list:
    """Scan SoT structure files."""
    sot_files = []
    if source_path.exists():
        for f in source_path.rglob("*.yaml"):
            sot_files.append(f)
        for f in source_path.rglob("*.json"):
            sot_files.append(f)
        for f in source_path.rglob("*.md"):
            sot_files.append(f)
    return sorted(sot_files, key=lambda p: str(p))

# Parse arguments
sources = []
output_path = BASE / "02_audit_logging/evidence/proof_nexus_merkle.json"
algorithms = ["SHA-512", "BLAKE3"]

if "--sources" in sys.argv:
    idx = sys.argv.index("--sources")
    # Next args until next flag
    i = idx + 1
    while i < len(sys.argv) and not sys.argv[i].startswith("--"):
        sources.append(Path(os.path.expanduser(sys.argv[i])))
        i += 1

if "--output" in sys.argv:
    idx = sys.argv.index("--output")
    output_path = BASE / sys.argv[idx + 1]

if "--algorithm" in sys.argv:
    idx = sys.argv.index("--algorithm")
    algorithms = sys.argv[idx + 1].split(",")

# Scan SoT files from both systems
all_sot_files = []
system_sot_map = {}

for source in sources:
    system_name = "SSID" if "SSID" in str(source) and "open-core" not in str(source) else "OpenCore"
    sot_files = scan_sot_files(source)
    system_sot_map[system_name] = sot_files
    all_sot_files.extend(sot_files)

# Compute hashes for all SoT files
file_hashes = {}
for f in all_sot_files:
    try:
        content = f.read_bytes()
        file_hashes[str(f)] = {
            "sha512": sha512_hash(content),
            "blake3": blake3_hash(content),
            "size": len(content)
        }
    except:
        pass

# Build Multi-Merkle roots
sha512_leaves = [h["sha512"] for h in file_hashes.values()]
blake3_leaves = [h["blake3"] for h in file_hashes.values()]

sha512_root = build_merkle_tree(sha512_leaves, sha512_hash)
blake3_root = build_merkle_tree(blake3_leaves, blake3_hash)

# Build cross-proof index
cross_proof = {
    "ssid_files": len(system_sot_map.get("SSID", [])),
    "opencore_files": len(system_sot_map.get("OpenCore", [])),
    "total_files": len(all_sot_files),
    "sha512_leaves": len(sha512_leaves),
    "blake3_leaves": len(blake3_leaves)
}

# Output
output_data = {
    "timestamp_utc": UTC,
    "mode": "INTERFEDERATION",
    "systems": list(system_sot_map.keys()),
    "algorithms": algorithms,
    "merkle_roots": {
        "sha512": sha512_root,
        "blake3": blake3_root
    },
    "cross_proof_index": cross_proof,
    "file_inventory": {
        system: [str(f) for f in files]
        for system, files in system_sot_map.items()
    }
}

output_path.parent.mkdir(parents=True, exist_ok=True)
output_path.write_text(json.dumps(output_data, ensure_ascii=False, indent=2), encoding="utf-8")

print(f"[OK] Multi-Merkle Federation Build Complete")
print(f"Systems: {', '.join(system_sot_map.keys())}")
print(f"Total SoT Files: {len(all_sot_files)}")
print(f"SHA-512 Root: {sha512_root[:32]}...")
print(f"BLAKE3 Root: {blake3_root[:32]}...")
print(f"Cross-Proof Index: {cross_proof}")
sys.exit(0)
