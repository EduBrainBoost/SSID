#!/usr/bin/env python3
"""
SSID Shard Matrix Verification Script
=====================================

Verifies that all 384 shards exist and are properly structured.

Version: 1.0.0
"""

from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent

ROOT_LAYERS = ['01_ai_layer', '02_audit_logging', '03_core', '04_deployment', '05_documentation', '06_data_pipeline', '07_governance_legal', '08_identity_score', '09_meta_identity', '10_interoperability', '11_test_simulation', '12_tooling', '13_ui_layer', '14_zero_time_auth', '15_infra', '16_codex', '17_observability', '18_data_layer', '19_adapters', '20_foundation', '21_post_quantum_crypto', '22_datasets', '23_compliance', '24_meta_orchestration']

SHARDS = ['01_identitaet_personen', '02_dokumente_nachweise', '03_zugang_berechtigungen', '04_kommunikation_daten', '05_gesundheit_medizin', '06_bildung_qualifikationen', '07_familie_soziales', '08_mobilitaet_fahrzeuge', '09_arbeit_karriere', '10_finanzen_banking', '11_versicherungen_risiken', '12_immobilien_grundstuecke', '13_unternehmen_gewerbe', '14_vertraege_vereinbarungen', '15_handel_transaktionen', '16_behoerden_verwaltung']

def verify_shard_matrix():
    """Verify all 384 shards exist"""

    missing = []
    incomplete = []

    for layer in ROOT_LAYERS:
        for shard in SHARDS:
            shard_path = REPO_ROOT / layer / "shards" / shard

            if not shard_path.exists():
                missing.append(f"{layer}/shards/{shard}")
                continue

            # Check required files
            required = ["chart.yaml", "README.md"]
            for req in required:
                if not (shard_path / req).exists():
                    incomplete.append(f"{layer}/shards/{shard}/{req}")

    # Report
    total = len(ROOT_LAYERS) * len(SHARDS)
    existing = total - len(missing)

    print(f"Shard Matrix Verification")
    print(f"=" * 80)
    print(f"Total Expected: {total}")
    print(f"Existing: {existing}")
    print(f"Missing: {len(missing)}")
    print(f"Incomplete: {len(incomplete)}")

    if missing:
        print(f"\nMissing Shards:")
        for m in missing[:10]:
            print(f"  - {m}")
        if len(missing) > 10:
            print(f"  ... and {len(missing) - 10} more")

    if incomplete:
        print(f"\nIncomplete Shards:")
        for i in incomplete[:10]:
            print(f"  - {i}")
        if len(incomplete) > 10:
            print(f"  ... and {len(incomplete) - 10} more")

    if not missing and not incomplete:
        print(f"\n[OK] All {total} shards are complete!")
        return 0
    else:
        print(f"\n[ERROR] Shard matrix incomplete")
        return 1

if __name__ == "__main__":
    exit(verify_shard_matrix())
