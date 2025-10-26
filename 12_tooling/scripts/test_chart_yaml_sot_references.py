#!/usr/bin/env python3
"""Test that all chart.yaml files have SOT master index references"""

import yaml
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent

LAYERS = [
    "01_ai_layer", "02_audit_logging", "03_core", "04_deployment",
    "05_documentation", "06_data_pipeline", "07_governance_legal",
    "08_identity_score", "09_meta_identity", "10_interoperability",
    "11_test_simulation", "12_tooling", "13_ui_layer", "14_zero_time_auth",
    "15_infra", "16_codex", "17_observability", "18_data_layer",
    "19_adapters", "20_foundation", "21_post_quantum_crypto", "22_datasets",
    "23_compliance", "24_meta_orchestration"
]

SHARDS = [
    "01_identitaet_personen", "02_dokumente_nachweise", "03_zugang_berechtigungen",
    "04_kommunikation_daten", "05_gesundheit_medizin", "06_bildung_qualifikationen",
    "07_familie_soziales", "08_mobilitaet_fahrzeuge", "09_arbeit_karriere",
    "10_finanzen_banking", "11_versicherungen_risiken", "12_immobilien_grundstuecke",
    "13_unternehmen_gewerbe", "14_vertraege_vereinbarungen", "15_handel_transaktionen",
    "16_behoerden_verwaltung"
]

total = 0
with_sot = 0
without_sot = []

for layer in LAYERS:
    for shard in SHARDS:
        chart_path = REPO_ROOT / layer / "shards" / shard / "chart.yaml"

        if not chart_path.exists():
            continue

        total += 1

        try:
            with open(chart_path, 'r', encoding='utf-8') as f:
                chart = yaml.safe_load(f)

            if isinstance(chart, dict) and "sot_master_index" in chart:
                with_sot += 1
            else:
                without_sot.append(f"{layer}/{shard}")
        except:
            without_sot.append(f"{layer}/{shard}")

print(f"Total chart.yaml files: {total}")
print(f"With SOT reference: {with_sot}")
print(f"Without SOT reference: {len(without_sot)}")

if len(without_sot) == 0:
    print("[OK] All chart.yaml files have SOT master index references!")
    exit(0)
else:
    print(f"[WARN] {len(without_sot)} charts missing SOT references")
    for chart in without_sot[:10]:
        print(f"  - {chart}")
    exit(1)
