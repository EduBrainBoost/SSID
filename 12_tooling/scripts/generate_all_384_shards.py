#!/usr/bin/env python3
"""
Generate all 384 shards (24 roots × 16 shards)

Creates complete shard structure for any missing shards:
- Directory structure
- chart.yaml
- implementations/default/
- manifest.yaml
- contracts/
- policies/
- docs/
- README.md
"""

import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# 24 Root directories
ROOTS = [
    "01_ai_layer",
    "02_audit_logging",
    "03_core",
    "04_deployment",
    "05_documentation",
    "06_data_pipeline",
    "07_governance_legal",
    "08_identity_score",
    "09_meta_identity",
    "10_interoperability",
    "11_test_simulation",
    "12_tooling",
    "13_ui_layer",
    "14_zero_time_auth",
    "15_infra",
    "16_codex",
    "17_observability",
    "18_data_layer",
    "19_adapters",
    "20_foundation",
    "21_post_quantum_crypto",
    "22_datasets",
    "23_compliance",
    "24_meta_orchestration"
]

# 16 Shards per root
SHARDS = [
    "01_identitaet_personen",
    "02_dokumente_nachweise",
    "03_zugang_berechtigungen",
    "04_kommunikation_daten",
    "05_gesundheit_medizin",
    "06_bildung_qualifikationen",
    "07_familie_soziales",
    "08_mobilitaet_fahrzeuge",
    "09_arbeit_karriere",
    "10_finanzen_banking",
    "11_versicherungen_risiken",
    "12_immobilien_grundstuecke",
    "13_unternehmen_gewerbe",
    "14_vertraege_vereinbarungen",
    "15_handel_transaktionen",
    "16_behoerden_verwaltung"
]

# Shard display names
SHARD_NAMES = {
    "01_identitaet_personen": "Identität & Personen",
    "02_dokumente_nachweise": "Dokumente & Nachweise",
    "03_zugang_berechtigungen": "Zugang & Berechtigungen",
    "04_kommunikation_daten": "Kommunikation & Daten",
    "05_gesundheit_medizin": "Gesundheit & Medizin",
    "06_bildung_qualifikationen": "Bildung & Qualifikationen",
    "07_familie_soziales": "Familie & Soziales",
    "08_mobilitaet_fahrzeuge": "Mobilität & Fahrzeuge",
    "09_arbeit_karriere": "Arbeit & Karriere",
    "10_finanzen_banking": "Finanzen & Banking",
    "11_versicherungen_risiken": "Versicherungen & Risiken",
    "12_immobilien_grundstuecke": "Immobilien & Grundstücke",
    "13_unternehmen_gewerbe": "Unternehmen & Gewerbe",
    "14_vertraege_vereinbarungen": "Verträge & Vereinbarungen",
    "15_handel_transaktionen": "Handel & Transaktionen",
    "16_behoerden_verwaltung": "Behörden & Verwaltung"
}


def get_repo_root() -> Path:
    """Get repository root path"""
    return Path(__file__).parents[2]


def create_chart_yaml(root: str, shard: str) -> Dict[str, Any]:
    """Generate chart.yaml content"""
    return {
        "apiVersion": "v2",
        "name": shard,
        "description": f"{SHARD_NAMES.get(shard, shard)} shard for {root}",
        "type": "application",
        "version": "1.0.0",
        "appVersion": "1.0.0",
        "keywords": [
            "ssid",
            root.replace("_", "-"),
            shard.replace("_", "-")
        ],
        "maintainers": [
            {
                "name": "SSID Team",
                "email": "team@ssid.example"
            }
        ],
        "sources": [
            "https://github.com/ssid/ssid"
        ],
        "annotations": {
            "category": "Infrastructure",
            "shard_id": shard,
            "root_id": root,
            "generated": datetime.now().isoformat()
        }
    }


def create_manifest_yaml(root: str, shard: str) -> Dict[str, Any]:
    """Generate manifest.yaml content for implementation"""
    return {
        "name": "default",
        "version": "1.0.0",
        "description": f"Default implementation for {SHARD_NAMES.get(shard, shard)}",
        "root": root,
        "shard": shard,
        "metadata": {
            "created": datetime.now().isoformat(),
            "status": "active",
            "type": "default"
        },
        "dependencies": [],
        "resources": {
            "cpu": "100m",
            "memory": "128Mi"
        },
        "capabilities": [
            "read",
            "write",
            "validate"
        ]
    }


def create_readme(root: str, shard: str) -> str:
    """Generate README.md content"""
    shard_name = SHARD_NAMES.get(shard, shard)
    return f"""# {shard_name}

Shard: `{shard}`
Root: `{root}`

## Overview

This shard handles {shard_name.lower()} functionality within the {root} layer.

## Structure

```
{shard}/
├── chart.yaml              # Helm chart definition
├── implementations/        # Implementation variants
│   └── default/           # Default implementation
│       └── manifest.yaml  # Implementation manifest
├── contracts/             # API contracts
├── policies/              # Policy definitions
├── docs/                  # Documentation
└── README.md              # This file
```

## Implementations

- **default**: Standard implementation for {shard_name.lower()}

## Contracts

Contract definitions are located in `contracts/` directory.

## Policies

Policy definitions are located in `policies/` directory.

## Documentation

Additional documentation is available in the `docs/` directory.

## Generated

This shard was generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} by the SSID shard generator.
"""


def create_contracts_readme(root: str, shard: str) -> str:
    """Generate contracts/README.md"""
    return f"""# Contracts

This directory contains API contracts for {SHARD_NAMES.get(shard, shard)}.

## Contract Types

- **input.yaml**: Input validation contracts
- **output.yaml**: Output format contracts
- **events.yaml**: Event definitions
- **errors.yaml**: Error definitions

## Usage

Contracts are enforced at runtime by the SSID validation layer.
"""


def create_policies_readme(root: str, shard: str) -> str:
    """Generate policies/README.md"""
    return f"""# Policies

This directory contains policy definitions for {SHARD_NAMES.get(shard, shard)}.

## Policy Types

- **access.rego**: Access control policies
- **validation.rego**: Data validation policies
- **compliance.rego**: Compliance policies

## Policy Engine

Policies are evaluated using Open Policy Agent (OPA).
"""


def create_docs_readme(root: str, shard: str) -> str:
    """Generate docs/README.md"""
    return f"""# Documentation

This directory contains detailed documentation for {SHARD_NAMES.get(shard, shard)}.

## Contents

- **architecture.md**: Architecture overview
- **api.md**: API documentation
- **examples.md**: Usage examples
- **testing.md**: Testing guide

## Contributing

When adding new functionality, please update the relevant documentation.
"""


def create_shard_structure(root: str, shard: str, dry_run: bool = False) -> bool:
    """
    Create complete shard structure

    Args:
        root: Root directory name
        shard: Shard name
        dry_run: If True, only print what would be created

    Returns:
        True if created, False if already exists
    """
    repo_root = get_repo_root()
    shard_path = repo_root / root / "shards" / shard

    if shard_path.exists():
        return False

    if dry_run:
        print(f"[DRY RUN] Would create: {root}/shards/{shard}")
        return True

    # Create directory structure
    shard_path.mkdir(parents=True, exist_ok=True)
    (shard_path / "implementations" / "default").mkdir(parents=True, exist_ok=True)
    (shard_path / "contracts").mkdir(parents=True, exist_ok=True)
    (shard_path / "policies").mkdir(parents=True, exist_ok=True)
    (shard_path / "docs").mkdir(parents=True, exist_ok=True)

    # Create chart.yaml
    chart_path = shard_path / "chart.yaml"
    with open(chart_path, 'w', encoding='utf-8') as f:
        yaml.dump(create_chart_yaml(root, shard), f, default_flow_style=False, sort_keys=False)

    # Create manifest.yaml
    manifest_path = shard_path / "implementations" / "default" / "manifest.yaml"
    with open(manifest_path, 'w', encoding='utf-8') as f:
        yaml.dump(create_manifest_yaml(root, shard), f, default_flow_style=False, sort_keys=False)

    # Create README files
    (shard_path / "README.md").write_text(create_readme(root, shard), encoding='utf-8')
    (shard_path / "contracts" / "README.md").write_text(create_contracts_readme(root, shard), encoding='utf-8')
    (shard_path / "policies" / "README.md").write_text(create_policies_readme(root, shard), encoding='utf-8')
    (shard_path / "docs" / "README.md").write_text(create_docs_readme(root, shard), encoding='utf-8')

    print(f"[OK] Created: {root}/shards/{shard}")
    return True


def generate_all_shards(dry_run: bool = False):
    """Generate all 384 shards"""
    print("=" * 80)
    print("SSID SHARD GENERATOR")
    print("=" * 80)
    print(f"Roots: {len(ROOTS)}")
    print(f"Shards per root: {len(SHARDS)}")
    print(f"Total combinations: {len(ROOTS) * len(SHARDS)}")
    print("=" * 80)

    if dry_run:
        print("\n[DRY RUN MODE - No files will be created]\n")

    created = 0
    skipped = 0

    for root in ROOTS:
        root_created = 0
        for shard in SHARDS:
            if create_shard_structure(root, shard, dry_run):
                created += 1
                root_created += 1
            else:
                skipped += 1

        if root_created > 0:
            print(f"  {root}: {root_created} shards created")

    print("\n" + "=" * 80)
    print(f"SUMMARY")
    print("=" * 80)
    print(f"Created: {created}")
    print(f"Already existed: {skipped}")
    print(f"Total: {created + skipped}")
    print("=" * 80)

    if not dry_run and created > 0:
        print(f"\n[SUCCESS] Generated {created} shards!")
        print(f"\nRun tests with:")
        print(f"  pytest 11_test_simulation/tests_structure/test_all_384_shards.py -v")


def verify_all_shards():
    """Verify all 384 shards exist"""
    print("\n" + "=" * 80)
    print("VERIFICATION")
    print("=" * 80)

    repo_root = get_repo_root()
    missing = []

    for root in ROOTS:
        for shard in SHARDS:
            shard_path = repo_root / root / "shards" / shard
            if not shard_path.exists():
                missing.append(f"{root}/shards/{shard}")

    if missing:
        print(f"\n❌ Missing {len(missing)} shards:")
        for shard in missing[:10]:  # Show first 10
            print(f"  - {shard}")
        if len(missing) > 10:
            print(f"  ... and {len(missing) - 10} more")
    else:
        print(f"\n✓ All 384 shards exist!")

    print("=" * 80)
    return len(missing) == 0


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate all 384 SSID shards")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be created without creating")
    parser.add_argument("--verify", action="store_true", help="Verify all shards exist")
    args = parser.parse_args()

    if args.verify:
        verify_all_shards()
    else:
        generate_all_shards(dry_run=args.dry_run)
        if not args.dry_run:
            verify_all_shards()
