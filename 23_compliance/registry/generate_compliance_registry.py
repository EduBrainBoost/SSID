#!/usr/bin/env python3
"""
Compliance Registry Generator with Merkle Trees
================================================

Generates compliance_registry.json containing:
- Hash of all 4 manifestations per rule
- Merkle tree (4 leaves → 2 intermediate → 1 root) per rule
- Merkle roots per standard
- Global Merkle root

This enables real-time verification without CI.

Architecture:
    Rule Merkle Tree (4 manifestations):

                 ROOT_HASH
                /         \
           HASH(L1+L2)  HASH(L3+L4)
            /    \        /    \
          L1    L2      L3    L4
        (Py)  (Rego) (YAML) (CLI)

    Standard Merkle Tree:
        STANDARD_ROOT = Merkle(all rule roots)

    Global Merkle Tree:
        GLOBAL_ROOT = Merkle(all standard roots)

Author: SSID Compliance Team
Version: 1.0.0
Date: 2025-10-17
"""

import sys
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import argparse


# Repository root
REPO_ROOT = Path(__file__).resolve().parents[2]


# Rule definitions
RULES_CONFIG = {
    "soc2": {
        "name": "SOC 2 (Trust Services Criteria)",
        "version": "2017",
        "rules": {
            "CC1.1": "Integrity & Ethical Values",
            "CC2.1": "Monitoring Activities",
            "CC3.1": "Risk Assessment",
            "CC4.1": "Information & Communication",
            "CC5.1": "Control Activities",
            "CC6.1": "Logical Access Controls",
            "CC7.1": "System Operations"
        }
    },
    "gaia_x": {
        "name": "Gaia-X Trust Framework",
        "version": "22.10",
        "rules": {
            "GAIA-X-01": "Data Sovereignty",
            "GAIA-X-02": "Transparency and Trust",
            "GAIA-X-03": "Interoperability",
            "GAIA-X-04": "Portability",
            "GAIA-X-05": "Security by Design",
            "GAIA-X-06": "Federated Services"
        }
    },
    "etsi_en_319_421": {
        "name": "ETSI EN 319 421",
        "version": "1.1.1",
        "rules": {
            "ETSI-421-01": "Certificate Policy Requirements",
            "ETSI-421-02": "Certificate Lifecycle Management",
            "ETSI-421-03": "QTSP Requirements",
            "ETSI-421-04": "Cryptographic Controls",
            "ETSI-421-05": "Time-Stamping Services",
            "ETSI-421-06": "Trust Service Status List"
        }
    }
}


def sha256_file(filepath: Path) -> str:
    """Calculate SHA-256 hash of file"""
    sha256_hash = hashlib.sha256()

    if not filepath.exists():
        return "0" * 64  # Missing file

    try:
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        print(f"Warning: Could not hash {filepath}: {e}", file=sys.stderr)
        return "0" * 64


def sha256_string(text: str) -> str:
    """Calculate SHA-256 hash of string"""
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def rule_id_to_filename(rule_id: str) -> str:
    """Convert rule ID to safe filename"""
    return rule_id.replace(".", "_").replace("-", "_").lower()


def build_merkle_tree(hashes: List[str]) -> Dict:
    """
    Build Merkle tree from list of hashes

    Args:
        hashes: List of 4 leaf hashes (Python, Rego, YAML, CLI)

    Returns:
        Dict with leaf_hashes, intermediate_hashes, root_hash
    """
    if len(hashes) != 4:
        raise ValueError(f"Expected 4 leaf hashes, got {len(hashes)}")

    leaf_hashes = hashes.copy()

    # Level 1: Combine pairs (Python+Rego, YAML+CLI)
    left_intermediate = sha256_string(hashes[0] + hashes[1])
    right_intermediate = sha256_string(hashes[2] + hashes[3])

    intermediate_hashes = [left_intermediate, right_intermediate]

    # Level 2: Root (combine both intermediate hashes)
    root_hash = sha256_string(left_intermediate + right_intermediate)

    return {
        "leaf_hashes": leaf_hashes,
        "intermediate_hashes": intermediate_hashes,
        "root_hash": root_hash
    }


def get_manifestation_paths(standard: str, rule_id: str) -> Dict[str, Path]:
    """Get paths to all 4 manifestations"""
    rule_safe = rule_id_to_filename(rule_id)

    # Find Python file (may have additional descriptive suffix)
    python_dir = REPO_ROOT / "23_compliance" / "mappings" / standard / "src"
    python_files = list(python_dir.glob(f"{rule_safe}*.py"))
    python_path = python_files[0] if python_files else python_dir / f"{rule_safe}_MISSING.py"

    # Find YAML file
    yaml_dir = REPO_ROOT / "16_codex" / "contracts" / standard
    yaml_files = list(yaml_dir.glob(f"{rule_safe}*.yaml"))
    yaml_path = yaml_files[0] if yaml_files else yaml_dir / f"{rule_safe}_MISSING.yaml"

    return {
        "python": python_path,
        "rego": REPO_ROOT / "23_compliance" / "policies" / f"{standard}_{rule_safe}.rego",
        "yaml": yaml_path,
        "cli": REPO_ROOT / "12_tooling" / "scripts" / "compliance" / f"check_{standard}_{rule_safe}.py"
    }


def generate_manifestation_info(path: Path) -> Dict:
    """Generate manifestation metadata"""
    exists = path.exists()

    return {
        "path": str(path.relative_to(REPO_ROOT)) if exists else str(path.name),
        "hash": sha256_file(path),
        "size": path.stat().st_size if exists else 0,
        "exists": exists,
        "last_modified": datetime.fromtimestamp(path.stat().st_mtime).isoformat() if exists else None,
        "validation_status": "valid" if exists and path.stat().st_size > 50 else "invalid"
    }


def generate_rule_entry(standard: str, rule_id: str, rule_name: str) -> Dict:
    """Generate complete registry entry for a rule"""
    paths = get_manifestation_paths(standard, rule_id)

    # Generate manifestation info
    manifestations = {
        "python": generate_manifestation_info(paths["python"]),
        "rego": generate_manifestation_info(paths["rego"]),
        "yaml": generate_manifestation_info(paths["yaml"]),
        "cli": generate_manifestation_info(paths["cli"])
    }

    # Extract hashes for Merkle tree
    leaf_hashes = [
        manifestations["python"]["hash"],
        manifestations["rego"]["hash"],
        manifestations["yaml"]["hash"],
        manifestations["cli"]["hash"]
    ]

    # Build Merkle tree
    merkle_tree = build_merkle_tree(leaf_hashes)

    # Determine status
    all_exist = all(m["exists"] for m in manifestations.values())
    all_valid = all(m["validation_status"] == "valid" for m in manifestations.values())

    if all_exist and all_valid:
        status = "compliant"
    elif all_exist:
        status = "partial"
    elif any(m["exists"] for m in manifestations.values()):
        status = "partial"
    else:
        status = "missing"

    # Get latest modification time
    mod_times = [m["last_modified"] for m in manifestations.values() if m["last_modified"]]
    last_modified = max(mod_times) if mod_times else None

    return {
        "rule_id": rule_id,
        "name": rule_name,
        "manifestations": manifestations,
        "merkle_tree": merkle_tree,
        "status": status,
        "last_modified": last_modified
    }


def generate_standard_entry(standard: str, config: Dict) -> Dict:
    """Generate registry entry for entire standard"""
    rules = {}
    rule_merkle_roots = []

    for rule_id, rule_name in config["rules"].items():
        rule_entry = generate_rule_entry(standard, rule_id, rule_name)
        rules[rule_id] = rule_entry
        rule_merkle_roots.append(rule_entry["merkle_tree"]["root_hash"])

    # Build Merkle tree of all rule roots
    # Pad to power of 2 if needed
    while len(rule_merkle_roots) & (len(rule_merkle_roots) - 1) != 0:
        rule_merkle_roots.append("0" * 64)

    # Simple Merkle root (iteratively hash pairs)
    current_level = rule_merkle_roots
    while len(current_level) > 1:
        next_level = []
        for i in range(0, len(current_level), 2):
            combined = sha256_string(current_level[i] + current_level[i+1])
            next_level.append(combined)
        current_level = next_level

    standard_merkle_root = current_level[0]

    # Calculate compliance score
    total_rules = len(config["rules"])
    compliant_rules = sum(1 for r in rules.values() if r["status"] == "compliant")
    compliance_score = compliant_rules / total_rules if total_rules > 0 else 0.0

    return {
        "name": config["name"],
        "version": config.get("version", "unknown"),
        "rules": rules,
        "merkle_root": standard_merkle_root,
        "compliance_score": compliance_score
    }


def generate_registry() -> Dict:
    """Generate complete compliance registry"""
    print("Generating Compliance Meta-Registry...")
    print(f"Repository Root: {REPO_ROOT}")
    print()

    standards = {}
    standard_merkle_roots = []

    total_rules = 0
    total_manifestations = 0

    for standard, config in RULES_CONFIG.items():
        print(f"Processing {standard}...")
        standard_entry = generate_standard_entry(standard, config)
        standards[standard] = standard_entry
        standard_merkle_roots.append(standard_entry["merkle_root"])

        total_rules += len(config["rules"])
        total_manifestations += len(config["rules"]) * 4

        print(f"  - {len(config['rules'])} rules")
        print(f"  - Merkle Root: {standard_entry['merkle_root'][:16]}...")
        print(f"  - Compliance: {standard_entry['compliance_score']:.1%}")
        print()

    # Global Merkle root
    global_merkle_root = sha256_string("".join(standard_merkle_roots))

    # Calculate overall compliance
    all_compliant = sum(len(cfg["rules"]) for cfg in RULES_CONFIG.values())
    actual_compliant = sum(
        sum(1 for r in std["rules"].values() if r["status"] == "compliant")
        for std in standards.values()
    )
    overall_compliance = actual_compliant / all_compliant if all_compliant > 0 else 0.0

    # Build registry
    registry = {
        "metadata": {
            "version": "1.0.0",
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "generated_by": "generate_compliance_registry.py",
            "total_rules": total_rules,
            "total_manifestations": total_manifestations,
            "compliance_score": overall_compliance,
            "last_verified": datetime.utcnow().isoformat() + "Z"
        },
        "standards": standards,
        "merkle_roots": {
            standard: standards[standard]["merkle_root"]
            for standard in standards
        },
        "verification": {
            "global_merkle_root": global_merkle_root,
            "signature": None,  # Can be added later
            "verification_history": []
        }
    }

    return registry


def verify_registry(registry: Dict) -> bool:
    """Verify registry integrity by recalculating Merkle roots"""
    print("\nVerifying registry integrity...")

    all_valid = True

    # Verify each standard's Merkle root
    for standard, std_data in registry["standards"].items():
        rule_roots = [rule["merkle_tree"]["root_hash"] for rule in std_data["rules"].values()]

        # Pad to power of 2
        while len(rule_roots) & (len(rule_roots) - 1) != 0:
            rule_roots.append("0" * 64)

        # Recalculate
        current_level = rule_roots
        while len(current_level) > 1:
            next_level = []
            for i in range(0, len(current_level), 2):
                combined = sha256_string(current_level[i] + current_level[i+1])
                next_level.append(combined)
            current_level = next_level

        calculated_root = current_level[0]
        stored_root = std_data["merkle_root"]

        if calculated_root == stored_root:
            print(f"  ✓ {standard}: Merkle root valid")
        else:
            print(f"  ✗ {standard}: Merkle root MISMATCH")
            all_valid = False

    # Verify global root
    standard_roots = [registry["standards"][s]["merkle_root"] for s in registry["standards"]]
    calculated_global = sha256_string("".join(standard_roots))
    stored_global = registry["verification"]["global_merkle_root"]

    if calculated_global == stored_global:
        print(f"  ✓ Global Merkle root valid")
    else:
        print(f"  ✗ Global Merkle root MISMATCH")
        all_valid = False

    return all_valid


def main():
    parser = argparse.ArgumentParser(description="Generate Compliance Meta-Registry")
    parser.add_argument("--output", "-o", type=Path,
                        default=REPO_ROOT / "23_compliance" / "registry" / "compliance_registry.json",
                        help="Output path for registry JSON")
    parser.add_argument("--verify", action="store_true",
                        help="Verify registry after generation")
    parser.add_argument("--pretty", action="store_true",
                        help="Pretty-print JSON output")
    args = parser.parse_args()

    # Generate registry
    registry = generate_registry()

    # Write to file
    args.output.parent.mkdir(parents=True, exist_ok=True)

    with open(args.output, 'w', encoding='utf-8') as f:
        if args.pretty:
            json.dump(registry, f, indent=2, ensure_ascii=False)
        else:
            json.dump(registry, f, ensure_ascii=False)

    print(f"Registry written to: {args.output}")
    print(f"Total Rules: {registry['metadata']['total_rules']}")
    print(f"Total Manifestations: {registry['metadata']['total_manifestations']}")
    print(f"Overall Compliance: {registry['metadata']['compliance_score']:.1%}")
    print(f"Global Merkle Root: {registry['verification']['global_merkle_root']}")

    # Verify if requested
    if args.verify:
        if verify_registry(registry):
            print("\n✓ Registry verification PASSED")
            return 0
        else:
            print("\n✗ Registry verification FAILED")
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
