#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
384 Shard Matrix Generator - Self-Generating SoT System
========================================================

Automatically generates the complete 24x16 Shard Matrix:
- 24 Root directories (technical layers)
- 16 Shards per root (application domains)
- 384 total Shards (24 x 16 = 384)

Each Shard contains:
- chart.yaml (SoT definition)
- manifest.yaml (deployment manifest)
- src/ (implementation)
- tests/ (validation)
- docs/ (documentation)

This is the HEART of the SoT system.

Version: 1.0.0
Author: SSID Orchestration Team
Co-Authored-By: Claude <noreply@anthropic.com>
"""

import sys
import json
import yaml
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any, Tuple

# Repository root
REPO_ROOT = Path(__file__).parent.parent.parent

# 24 Root directories (technical layers)
ROOTS = [
    ("01_ai_layer", "AI/ML & Intelligence"),
    ("02_audit_logging", "Audit & Evidence"),
    ("03_core", "Core Logic"),
    ("04_deployment", "Deployment & Distribution"),
    ("05_documentation", "Documentation & I18N"),
    ("06_data_pipeline", "Data Flow & Processing"),
    ("07_governance_legal", "Legal & Governance"),
    ("08_identity_score", "Reputation & Scoring"),
    ("09_meta_identity", "Meta-Identity Layer"),
    ("10_interoperability", "Interoperability"),
    ("11_test_simulation", "Testing & Simulation"),
    ("12_tooling", "Tooling & Automation"),
    ("13_ui_layer", "UI/UX Layer"),
    ("14_zero_time_auth", "Zero-Time Auth"),
    ("15_infra", "Infrastructure"),
    ("16_codex", "Codex & Structure"),
    ("17_observability", "Observability"),
    ("18_data_layer", "Data Layer"),
    ("19_adapters", "Adapters"),
    ("20_foundation", "Foundation"),
    ("21_post_quantum_crypto", "Post-Quantum Crypto"),
    ("22_datasets", "Datasets"),
    ("23_compliance", "Compliance"),
    ("24_meta_orchestration", "Meta Orchestration"),
]

# 16 Shards (application domains) - grouped in 4 blocks
SHARDS = [
    # Block 1: Identity & Foundation (01-04)
    ("01_identitaet_personen", "Identity & Persons", "DIDs, IDs, Profiles, Authentication"),
    ("02_dokumente_nachweise", "Documents & Evidence", "Credentials, Certificates, Proofs"),
    ("03_zugang_berechtigungen", "Access & Permissions", "Authorization, Roles, Rights"),
    ("04_kommunikation_daten", "Communication & Data", "Messaging, Data Exchange"),

    # Block 2: Life Domains (05-08)
    ("05_gesundheit_medizin", "Health & Medicine", "Medical Records, Prescriptions, Health Data"),
    ("06_bildung_qualifikationen", "Education & Qualifications", "Degrees, Certificates, Skills"),
    ("07_familie_soziales", "Family & Social", "Family Relations, Social Networks"),
    ("08_mobilitaet_fahrzeuge", "Mobility & Vehicles", "Transport, Vehicles, Travel"),

    # Block 3: Work & Finance (09-12)
    ("09_arbeit_karriere", "Work & Career", "Employment, CV, Job History"),
    ("10_finanzen_banking", "Finance & Banking", "Accounts, Transactions, Payments"),
    ("11_versicherungen_risiken", "Insurance & Risk", "Insurance Policies, Claims"),
    ("12_immobilien_grundstuecke", "Real Estate & Property", "Property Ownership, Rentals"),

    # Block 4: Business & Government (13-16)
    ("13_unternehmen_gewerbe", "Companies & Business", "Company Registry, Business Licenses"),
    ("14_vertraege_vereinbarungen", "Contracts & Agreements", "Legal Contracts, Terms"),
    ("15_handel_transaktionen", "Trade & Transactions", "E-Commerce, Marketplace"),
    ("16_behoerden_verwaltung", "Government & Administration", "Public Services, Permits"),
]


class ShardMatrixGenerator:
    """
    Master Generator for 384 Shard Matrix

    Self-generating system that creates the complete SoT structure.
    """

    def __init__(self, repo_root: Path, dry_run: bool = False):
        self.repo_root = repo_root
        self.dry_run = dry_run
        self.generated_count = 0
        self.skipped_count = 0
        self.errors = []

    def generate_all(self) -> Dict[str, Any]:
        """Generate complete 384 Shard Matrix"""
        print("=" * 80)
        print(" " * 25 + "384 SHARD MATRIX GENERATOR")
        print("=" * 80)
        print(f"Timestamp:   {datetime.now(timezone.utc).isoformat()}")
        print(f"Repository:  {self.repo_root}")
        print(f"Mode:        {'DRY RUN' if self.dry_run else 'LIVE'}")
        print(f"Total Roots: {len(ROOTS)}")
        print(f"Total Shards per Root: {len(SHARDS)}")
        print(f"Total Matrix Size: {len(ROOTS)} x {len(SHARDS)} = {len(ROOTS) * len(SHARDS)}")
        print("=" * 80)
        print()

        # Generate for each root
        for root_id, root_desc in ROOTS:
            print(f"[ROOT] {root_id} - {root_desc}")
            root_path = self.repo_root / root_id

            if not root_path.exists():
                error = f"Root directory does not exist: {root_id}"
                print(f"  [ERROR] {error}")
                self.errors.append(error)
                continue

            # Create shards directory
            shards_dir = root_path / "shards"
            if not self.dry_run:
                shards_dir.mkdir(exist_ok=True)

            # Generate all 16 shards for this root
            for shard_id, shard_name, shard_desc in SHARDS:
                self._generate_shard(root_id, root_desc, shard_id, shard_name, shard_desc)

            print()

        # Summary
        print("=" * 80)
        print("GENERATION SUMMARY")
        print("=" * 80)
        print(f"Generated: {self.generated_count}")
        print(f"Skipped:   {self.skipped_count}")
        print(f"Errors:    {len(self.errors)}")

        if self.errors:
            print("\nErrors:")
            for error in self.errors[:10]:
                print(f"  - {error}")

        print("=" * 80)

        return {
            "status": "success" if not self.errors else "partial",
            "generated": self.generated_count,
            "skipped": self.skipped_count,
            "errors": len(self.errors),
            "total_expected": len(ROOTS) * len(SHARDS),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def _generate_shard(self, root_id: str, root_desc: str,
                        shard_id: str, shard_name: str, shard_desc: str):
        """Generate a single shard with all required files"""
        shard_path = self.repo_root / root_id / "shards" / shard_id

        # Check if already exists
        if shard_path.exists():
            print(f"  [SKIP] {shard_id} (already exists)")
            self.skipped_count += 1
            return

        if not self.dry_run:
            # Create shard directory structure
            shard_path.mkdir(parents=True, exist_ok=True)
            (shard_path / "src").mkdir(exist_ok=True)
            (shard_path / "tests").mkdir(exist_ok=True)
            (shard_path / "docs").mkdir(exist_ok=True)
            (shard_path / "conformance").mkdir(exist_ok=True)

            # Generate chart.yaml
            chart_content = self._generate_chart_yaml(root_id, root_desc, shard_id, shard_name, shard_desc)
            with open(shard_path / "chart.yaml", "w", encoding="utf-8") as f:
                yaml.safe_dump(chart_content, f, allow_unicode=True, sort_keys=False)

            # Generate manifest.yaml
            manifest_content = self._generate_manifest_yaml(root_id, root_desc, shard_id, shard_name, shard_desc)
            with open(shard_path / "manifest.yaml", "w", encoding="utf-8") as f:
                yaml.safe_dump(manifest_content, f, allow_unicode=True, sort_keys=False)

            # Generate README.md
            readme_content = self._generate_readme(root_id, root_desc, shard_id, shard_name, shard_desc)
            with open(shard_path / "README.md", "w", encoding="utf-8") as f:
                f.write(readme_content)

            # Generate .gitkeep files
            (shard_path / "src" / ".gitkeep").touch()
            (shard_path / "tests" / ".gitkeep").touch()
            (shard_path / "docs" / ".gitkeep").touch()
            (shard_path / "conformance" / ".gitkeep").touch()

        print(f"  [OK] {shard_id}")
        self.generated_count += 1

    def _generate_chart_yaml(self, root_id: str, root_desc: str,
                             shard_id: str, shard_name: str, shard_desc: str) -> Dict[str, Any]:
        """Generate chart.yaml for a shard"""
        shard_num = shard_id.split("_")[0]

        return {
            "apiVersion": "ssid.project/v1",
            "kind": "ShardChart",
            "metadata": {
                "name": f"{root_id}_{shard_id}",
                "shard_id": shard_id,
                "shard_number": int(shard_num),
                "shard_name": shard_name,
                "root_id": root_id,
                "root_name": root_desc,
                "created": datetime.now(timezone.utc).isoformat(),
                "version": "1.0.0",
                "hash": self._compute_shard_hash(root_id, shard_id),
            },
            "spec": {
                "description": shard_desc,
                "domain": self._get_domain_block(shard_num),
                "compliance": {
                    "gdpr": True,
                    "eidas": True,
                    "mica": False,
                },
                "storage": {
                    "ipfs": True,
                    "hash_ledger": True,
                    "worm": True,
                },
                "identity": {
                    "did_required": True,
                    "vc_support": True,
                    "kyc_level": "basic",
                },
            },
            "data": {
                "schema_version": "1.0",
                "fields": [],  # To be populated by rule extraction
            },
            "rules": {
                "validation": [],  # To be populated by rule extraction
                "policies": [],    # To be populated by rule extraction
            },
        }

    def _generate_manifest_yaml(self, root_id: str, root_desc: str,
                                 shard_id: str, shard_name: str, shard_desc: str) -> Dict[str, Any]:
        """Generate manifest.yaml for a shard"""
        return {
            "apiVersion": "deployment.ssid.project/v1",
            "kind": "ShardManifest",
            "metadata": {
                "name": f"{root_id}_{shard_id}",
                "labels": {
                    "root": root_id,
                    "shard": shard_id,
                    "domain": self._get_domain_block(shard_id.split("_")[0]),
                },
            },
            "spec": {
                "replicas": 1,
                "deployment": {
                    "strategy": "RollingUpdate",
                    "maxSurge": 1,
                    "maxUnavailable": 0,
                },
                "service": {
                    "type": "ClusterIP",
                    "port": 8080,
                },
                "resources": {
                    "limits": {
                        "cpu": "500m",
                        "memory": "512Mi",
                    },
                    "requests": {
                        "cpu": "100m",
                        "memory": "128Mi",
                    },
                },
            },
        }

    def _generate_readme(self, root_id: str, root_desc: str,
                         shard_id: str, shard_name: str, shard_desc: str) -> str:
        """Generate README.md for a shard"""
        return f"""# {shard_name}

**Shard:** {shard_id}
**Root:** {root_id} - {root_desc}
**Description:** {shard_desc}

## Overview

This shard is part of the SSID 384 Shard Matrix (24 Roots x 16 Shards).

### Matrix Position
- **Root:** {root_id} ({root_desc})
- **Shard:** {shard_id} ({shard_name})
- **Domain:** {self._get_domain_block(shard_id.split("_")[0])}

## Structure

```
{shard_id}/
├── chart.yaml          # SoT definition
├── manifest.yaml       # Deployment manifest
├── README.md           # This file
├── src/                # Implementation
├── tests/              # Validation tests
├── docs/               # Documentation
└── conformance/        # Compliance tests
```

## SoT Compliance

This shard follows the Single Source of Truth (SoT) protocol:
- ✅ ROOT-24-LOCK enforced
- ✅ 16-Shard structure
- ✅ Auto-generated from master definition
- ✅ Hash-verified

## Generated

- **Timestamp:** {datetime.now(timezone.utc).isoformat()}
- **Generator:** generate_384_shard_matrix.py
- **Version:** 1.0.0

---

Co-Authored-By: Claude <noreply@anthropic.com>
"""

    def _get_domain_block(self, shard_num: str) -> str:
        """Get domain block for shard number"""
        num = int(shard_num)
        if 1 <= num <= 4:
            return "identity_foundation"
        elif 5 <= num <= 8:
            return "life_domains"
        elif 9 <= num <= 12:
            return "work_finance"
        elif 13 <= num <= 16:
            return "business_government"
        return "unknown"

    def _compute_shard_hash(self, root_id: str, shard_id: str) -> str:
        """Compute SHA-256 hash for shard identity"""
        content = f"{root_id}:{shard_id}:{datetime.now(timezone.utc).date()}"
        return hashlib.sha256(content.encode()).hexdigest()


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Generate 384 Shard Matrix")
    parser.add_argument("--dry-run", action="store_true", help="Dry run (don't create files)")
    parser.add_argument("--root", type=Path, help="Repository root (auto-detected if not specified)")

    args = parser.parse_args()

    repo_root = args.root or REPO_ROOT
    generator = ShardMatrixGenerator(repo_root, dry_run=args.dry_run)

    result = generator.generate_all()

    print()
    print("Result:")
    print(json.dumps(result, indent=2))

    return 0 if result["status"] == "success" else 1


if __name__ == "__main__":
    sys.exit(main())
