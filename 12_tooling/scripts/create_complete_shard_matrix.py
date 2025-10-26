#!/usr/bin/env python3
"""
SSID Complete 24×16 Shard Matrix Generator
==========================================

Creates all 384 shards (24 layers × 16 shards) according to ssid_master_definition_corrected_v1.1.1.md

Version: 1.0.0
Author: SSID System
Date: 2025-10-24
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, List
from datetime import datetime

# Root directory
REPO_ROOT = Path(__file__).parent.parent.parent

# 24 Root Layers (according to master definition)
ROOT_LAYERS = [
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

# 16 Shards (Oberkategorien)
SHARDS = [
    {"id": "01", "name": "identitaet_personen", "desc": "DIDs, Ausweise, Profile, Authentifizierung"},
    {"id": "02", "name": "dokumente_nachweise", "desc": "Urkunden, Bescheinigungen, Zertifikate"},
    {"id": "03", "name": "zugang_berechtigungen", "desc": "Rollen, Rechte, Mandanten, Delegationen"},
    {"id": "04", "name": "kommunikation_daten", "desc": "Nachrichten, E-Mail, Chat, Datenaustausch"},
    {"id": "05", "name": "gesundheit_medizin", "desc": "Krankenakte, Rezepte, Impfpass, Behandlungen"},
    {"id": "06", "name": "bildung_qualifikationen", "desc": "Zeugnisse, Abschlüsse, Kurse, Weiterbildung"},
    {"id": "07", "name": "familie_soziales", "desc": "Geburt, Heirat, Scheidung, Adoption, Erbe"},
    {"id": "08", "name": "mobilitaet_fahrzeuge", "desc": "Führerschein, KFZ-Zulassung, Fahrzeugpapiere"},
    {"id": "09", "name": "arbeit_karriere", "desc": "Arbeitsverträge, Gehalt, Bewerbungen, Referenzen"},
    {"id": "10", "name": "finanzen_banking", "desc": "Konten, Zahlungen, Überweisungen, Kredite"},
    {"id": "11", "name": "versicherungen_risiken", "desc": "Versicherungsarten, Schäden, Claims, Policen"},
    {"id": "12", "name": "immobilien_grundstuecke", "desc": "Eigentum, Miete, Pacht, Grundbuch"},
    {"id": "13", "name": "unternehmen_gewerbe", "desc": "Firmendaten, Handelsregister, Lizenzen, B2B"},
    {"id": "14", "name": "vertraege_vereinbarungen", "desc": "Smart Contracts, Geschäftsverträge, AGBs"},
    {"id": "15", "name": "handel_transaktionen", "desc": "Käufe, Verkäufe, Rechnungen, Garantien"},
    {"id": "16", "name": "behoerden_verwaltung", "desc": "Ämter, Anträge, Genehmigungen, Steuern"}
]

# Layer descriptions
LAYER_DESCRIPTIONS = {
    "01_ai_layer": "AI/ML & Intelligenz",
    "02_audit_logging": "Nachweise & Beweisführung",
    "03_core": "Zentrale Logik",
    "04_deployment": "Auslieferung & Distribution",
    "05_documentation": "Dokumentation & I18N",
    "06_data_pipeline": "Datenfluss & Verarbeitung",
    "07_governance_legal": "Recht & Steuerung",
    "08_identity_score": "Reputation & Scoring",
    "09_meta_identity": "Digitale Identität",
    "10_interoperability": "Kompatibilität",
    "11_test_simulation": "Simulation & QA",
    "12_tooling": "Werkzeuge",
    "13_ui_layer": "Benutzeroberfläche",
    "14_zero_time_auth": "Sofort-Authentifizierung",
    "15_infra": "Infrastruktur",
    "16_codex": "Wissensbasis & Regeln",
    "17_observability": "Monitoring & Insights",
    "18_data_layer": "Datenhaltung",
    "19_adapters": "Anschlüsse & Schnittstellen",
    "20_foundation": "Grundlagen & Tokenomics",
    "21_post_quantum_crypto": "Zukunftskrypto",
    "22_datasets": "Datenbestände",
    "23_compliance": "Regeltreue",
    "24_meta_orchestration": "Zentrale Steuerung"
}


def create_chart_yaml(layer: str, shard: Dict) -> str:
    """Generate chart.yaml content for a shard"""

    shard_id = f"{shard['id']}_{shard['name']}"
    layer_desc = LAYER_DESCRIPTIONS.get(layer, layer)

    content = f"""# SSID Chart - {layer} / Shard {shard_id}
# Single Source of Truth (SoT)

metadata:
  shard_id: "{shard_id}"
  root_layer: "{layer}"
  version: "1.0.0"
  status: "active"
  created: "{datetime.now().isoformat()}"
  description: "{layer_desc} for {shard['desc']}"

governance:
  owner:
    team: "ssid_core"
    lead: "system_architect"
    contact: "team@ssid.org"
  reviewers:
    architecture: true
    compliance: true
    security: true
  change_process:
    rfc_required: true
    approval_quorum: 2

capabilities:
  MUST: []
  SHOULD: []
  HAVE: []

constraints:
  pii_storage: "forbidden"
  data_policy: "hash_only"
  custody: "non_custodial_code_only"

enforcement:
  static_analysis:
    - semgrep
    - bandit
  runtime_checks:
    - pii_detector
  audit:
    log_to: "02_audit_logging"

interfaces:
  contracts: []
  data_schemas: []
  authentication: "mTLS"

dependencies:
  required: []
  optional: []

compatibility:
  semver: "1.0.0"
  core_min_version: ">=3.0.0"

implementations:
  default: null
  available: []

conformance:
  test_framework: "pytest"
  contract_tests: []

orchestration:
  workflows: []

testing:
  unit:
    location: "tests/unit"
    min_coverage: 80
  integration:
    location: "tests/integration"
    min_coverage: 70
  contract:
    location: "conformance"
    min_coverage: 95
  e2e:
    location: "tests/e2e"
    min_coverage: 60

documentation:
  auto_generate: true
  manual: []

observability:
  metrics:
    exporter: "prometheus"
  tracing:
    exporter: "jaeger"
  logging:
    format: "json"
    pii_redaction: true
  alerting:
    enabled: true

evidence:
  strategy: "hash_ledger_with_anchoring"
  anchoring:
    chains:
      - ethereum
      - polygon
    frequency: "hourly"

security:
  threat_model: "docs/security/threat_model.md"
  secrets_management: "15_infra/vault"
  encryption:
    at_rest: "AES-256-GCM"
    in_transit: "TLS-1.3"

deployment:
  strategy: "blue-green"
  environments:
    - dev
    - staging
    - production

resources:
  compute:
    cpu: "100m"
    memory: "128Mi"
    autoscaling: true

roadmap:
  upcoming: []
"""
    return content


def create_readme(layer: str, shard: Dict) -> str:
    """Generate README.md content for a shard"""

    shard_id = f"{shard['id']}_{shard['name']}"
    layer_desc = LAYER_DESCRIPTIONS.get(layer, layer)

    content = f"""# {layer} - Shard {shard_id}

## Overview

**Layer:** {layer} - {layer_desc}
**Shard:** {shard_id} - {shard['desc']}
**Version:** 1.0.0
**Status:** Active

## Description

This shard implements {layer_desc.lower()} functionality for the {shard['desc'].lower()} domain.

## Structure

```
{shard_id}/
├── chart.yaml              # Single Source of Truth (SoT)
├── README.md              # This file
├── contracts/             # API contracts (OpenAPI, JSON Schema)
├── implementations/       # Concrete implementations
├── conformance/          # Contract tests
├── policies/             # Enforcement rules
└── docs/                 # Shard-specific documentation
```

## Getting Started

1. Review `chart.yaml` for capabilities and constraints
2. Check `contracts/` for API definitions
3. Explore `implementations/` for concrete code
4. Run `conformance/` tests to verify compliance

## Policies

- **PII Storage:** Forbidden
- **Data Policy:** Hash-only
- **Custody:** Non-custodial code only

## Contributing

See [CONTRIBUTING.md](../../CONTRIBUTING.md) for guidelines.

## License

See [LICENSE](../../LICENSE) for details.
"""
    return content


def create_shard_structure(layer: str, shard: Dict) -> None:
    """Create complete shard structure with all directories and files"""

    shard_id = f"{shard['id']}_{shard['name']}"
    shard_path = REPO_ROOT / layer / "shards" / shard_id

    # Create shard directory
    shard_path.mkdir(parents=True, exist_ok=True)

    # Create chart.yaml
    chart_file = shard_path / "chart.yaml"
    if not chart_file.exists():
        chart_file.write_text(create_chart_yaml(layer, shard), encoding='utf-8')
        print(f"  [+] Created {chart_file.relative_to(REPO_ROOT)}")

    # Create README.md
    readme_file = shard_path / "README.md"
    if not readme_file.exists():
        readme_file.write_text(create_readme(layer, shard), encoding='utf-8')
        print(f"  [+] Created {readme_file.relative_to(REPO_ROOT)}")

    # Create subdirectories
    subdirs = [
        "contracts",
        "implementations",
        "conformance",
        "policies",
        "docs"
    ]

    for subdir in subdirs:
        subdir_path = shard_path / subdir
        subdir_path.mkdir(exist_ok=True)

        # Create .gitkeep
        gitkeep = subdir_path / ".gitkeep"
        if not gitkeep.exists():
            gitkeep.write_text("", encoding='utf-8')


def create_layer_readme(layer: str) -> None:
    """Create README.md for layer's shards directory"""

    layer_desc = LAYER_DESCRIPTIONS.get(layer, layer)
    shards_path = REPO_ROOT / layer / "shards"
    readme_file = shards_path / "README.md"

    if readme_file.exists():
        return

    content = f"""# {layer} - Shards

## Overview

This directory contains all 16 shards for the **{layer}** layer ({layer_desc}).

## Structure

Each shard follows the SSID Master Definition v1.1.1 structure:

```
{layer}/shards/
├── 01_identitaet_personen/
├── 02_dokumente_nachweise/
├── 03_zugang_berechtigungen/
├── 04_kommunikation_daten/
├── 05_gesundheit_medizin/
├── 06_bildung_qualifikationen/
├── 07_familie_soziales/
├── 08_mobilitaet_fahrzeuge/
├── 09_arbeit_karriere/
├── 10_finanzen_banking/
├── 11_versicherungen_risiken/
├── 12_immobilien_grundstuecke/
├── 13_unternehmen_gewerbe/
├── 14_vertraege_vereinbarungen/
├── 15_handel_transaktionen/
└── 16_behoerden_verwaltung/
```

## Shard Details

Each shard contains:
- `chart.yaml` - Single Source of Truth (capabilities, policies, interfaces)
- `README.md` - Shard-specific documentation
- `contracts/` - API contracts (OpenAPI, JSON Schema)
- `implementations/` - Concrete implementations (Python, Rust, etc.)
- `conformance/` - Contract tests
- `policies/` - Enforcement rules
- `docs/` - Additional documentation

## Matrix Architecture

This is part of the **24×16 Matrix Architecture** (384 total shards):
- 24 Root Layers (vertical)
- 16 Shards per Layer (horizontal)

## References

- Master Definition: `16_codex/structure/ssid_master_definition_corrected_v1.1.1.md`
- Architecture Guide: `05_documentation/architecture/`
"""

    readme_file.write_text(content, encoding='utf-8')
    print(f"[+] Created {readme_file.relative_to(REPO_ROOT)}")


def generate_all_shards() -> Dict:
    """Generate all 384 shards (24 × 16)"""

    stats = {
        "total_layers": len(ROOT_LAYERS),
        "total_shards_per_layer": len(SHARDS),
        "total_shards": len(ROOT_LAYERS) * len(SHARDS),
        "created": 0,
        "skipped": 0,
        "layers": {}
    }

    print("=" * 80)
    print("SSID Complete 24×16 Shard Matrix Generator")
    print("=" * 80)
    print(f"\nGenerating {stats['total_shards']} shards...")
    print(f"  - {stats['total_layers']} layers")
    print(f"  - {stats['total_shards_per_layer']} shards per layer")
    print()

    for layer in ROOT_LAYERS:
        print(f"\n[{layer}]")
        print("-" * 80)

        layer_stats = {
            "created": 0,
            "skipped": 0
        }

        # Create shards directory
        shards_dir = REPO_ROOT / layer / "shards"
        shards_dir.mkdir(parents=True, exist_ok=True)

        # Create layer README
        create_layer_readme(layer)

        # Create all 16 shards
        for shard in SHARDS:
            shard_id = f"{shard['id']}_{shard['name']}"
            shard_path = shards_dir / shard_id

            if shard_path.exists():
                print(f"  [SKIP] {shard_id} (already exists)")
                layer_stats["skipped"] += 1
                stats["skipped"] += 1
            else:
                create_shard_structure(layer, shard)
                layer_stats["created"] += 1
                stats["created"] += 1

        stats["layers"][layer] = layer_stats
        print(f"\n  Summary: {layer_stats['created']} created, {layer_stats['skipped']} skipped")

    return stats


def generate_report(stats: Dict) -> None:
    """Generate completion report"""

    print("\n" + "=" * 80)
    print("SHARD MATRIX GENERATION COMPLETE")
    print("=" * 80)
    print(f"\nTotal Shards: {stats['total_shards']}")
    print(f"  [OK] Created: {stats['created']}")
    print(f"  [SKIP] Skipped (already exist): {stats['skipped']}")
    print(f"\nLayers: {stats['total_layers']}")
    print(f"Shards per Layer: {stats['total_shards_per_layer']}")

    # Save report
    report_path = REPO_ROOT / "02_audit_logging" / "reports" / "shard_matrix_generation_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)

    report = {
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "status": "complete",
        "statistics": stats,
        "master_definition": "16_codex/structure/ssid_master_definition_corrected_v1.1.1.md"
    }

    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\n[REPORT] Saved to: {report_path.relative_to(REPO_ROOT)}")

    # Create verification script
    verify_script = REPO_ROOT / "12_tooling" / "scripts" / "verify_shard_matrix.py"
    verify_content = f'''#!/usr/bin/env python3
"""
SSID Shard Matrix Verification Script
=====================================

Verifies that all 384 shards exist and are properly structured.

Version: 1.0.0
"""

from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent

ROOT_LAYERS = {ROOT_LAYERS!r}

SHARDS = {[s["id"] + "_" + s["name"] for s in SHARDS]!r}

def verify_shard_matrix():
    """Verify all 384 shards exist"""

    missing = []
    incomplete = []

    for layer in ROOT_LAYERS:
        for shard in SHARDS:
            shard_path = REPO_ROOT / layer / "shards" / shard

            if not shard_path.exists():
                missing.append(f"{{layer}}/shards/{{shard}}")
                continue

            # Check required files
            required = ["chart.yaml", "README.md"]
            for req in required:
                if not (shard_path / req).exists():
                    incomplete.append(f"{{layer}}/shards/{{shard}}/{{req}}")

    # Report
    total = len(ROOT_LAYERS) * len(SHARDS)
    existing = total - len(missing)

    print(f"Shard Matrix Verification")
    print(f"=" * 80)
    print(f"Total Expected: {{total}}")
    print(f"Existing: {{existing}}")
    print(f"Missing: {{len(missing)}}")
    print(f"Incomplete: {{len(incomplete)}}")

    if missing:
        print(f"\\nMissing Shards:")
        for m in missing[:10]:
            print(f"  - {{m}}")
        if len(missing) > 10:
            print(f"  ... and {{len(missing) - 10}} more")

    if incomplete:
        print(f"\\nIncomplete Shards:")
        for i in incomplete[:10]:
            print(f"  - {{i}}")
        if len(incomplete) > 10:
            print(f"  ... and {{len(incomplete) - 10}} more")

    if not missing and not incomplete:
        print(f"\\n[OK] All {{total}} shards are complete!")
        return 0
    else:
        print(f"\\n[ERROR] Shard matrix incomplete")
        return 1

if __name__ == "__main__":
    exit(verify_shard_matrix())
'''

    verify_script.write_text(verify_content, encoding='utf-8')
    verify_script.chmod(0o755)

    print(f"[VERIFY] Script: {verify_script.relative_to(REPO_ROOT)}")
    print("\n[OK] Shard matrix generation complete!")


def main():
    """Main entry point"""

    stats = generate_all_shards()
    generate_report(stats)


if __name__ == "__main__":
    main()
