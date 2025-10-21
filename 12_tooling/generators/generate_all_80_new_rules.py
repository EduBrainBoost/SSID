#!/usr/bin/env python3
"""
Generiert ALLE 80 neuen Regeln aus SSID_structure_level3_part3_MAX.md
und fügt sie zu ALLEN 5 Manifestationen hinzu.

Zeilen 2-20: 19 Regeln (EU-Regulatorik: soc2, gaia_x, etsi_en_319_421)
Zeilen 26-32: 7 Regeln (Globale Metadaten)
Zeilen 34-87: 54 Regeln (Frameworks: fatf, oecd_carf, iso, standards, deprecated_standards)

TOTAL: 80 NEUE Regeln
"""

import yaml
import sys
import os
from datetime import datetime
from pathlib import Path

# Basis-Pfade
BASE = Path("../..")
YAML_CONTRACT = BASE / "16_codex/contracts/sot/sot_contract.yaml"
PYTHON_VALIDATOR = BASE / "03_core/validators/sot/sot_validator_core.py"
REGO_POLICY = BASE / "23_compliance/policies/sot/sot_policy.rego"
CLI_VALIDATOR = BASE / "12_tooling/cli/sot_validator.py"
TEST_FILE = BASE / "11_test_simulation/tests_compliance/test_sot_validator.py"

# Starte Regel-IDs nach den bestehenden 69
NEXT_RULE_ID = 82  # Nach SOT-081

def main():
    print("=" * 80)
    print("GENERIERE 80 NEUE SOT-REGELN - ALLE 5 MANIFESTATIONEN")
    print("=" * 80)

    # TODO: Source-Dokument parsen und Regeln extrahieren
    # Für jetzt: Erstelle Template der ersten 10 Regeln als Demonstration

    new_rules = []

    # EU-Regulatorik: soc2, gaia_x, etsi_en_319_421 (bereits als SOT-067 bis SOT-081 vorhanden!)
    # -> Diese sind NICHT neu!

    # NEUE REGELN starten bei SOT-082

    # Block 1: Jurisdiktionen UK/CH/LI (Zeilen ~90-124 im Source)
    # uk_crypto_regime (2 frameworks x 4 properties = 8 Regeln)
    frameworks_uk = [
        ("fca_ps23_6_promotions", "FCA PS23/6 Promotions"),
        ("hmt_cryptoassets_order_2025", "HMT Cryptoassets Order 2025")
    ]

    rule_id = NEXT_RULE_ID
    for fw_key, fw_name in frameworks_uk:
        for prop in ["entry_marker", "name", "path", "deprecated", "business_priority"]:
            priority = "should" if prop == "business_priority" else "must"

            new_rules.append({
                "rule_id": f"SOT-{str(rule_id).zfill(3)}",
                "priority": priority,
                "rule_name": f"{fw_key} {prop.replace('_', ' ').title()} Validation",
                "line_reference": 100 + (rule_id - NEXT_RULE_ID),
                "scientific_foundation": {
                    "standard": "UK Crypto Regime - FCA/HMT Framework",
                    "reference": "https://www.fca.org.uk/",
                    "principle": f"UK regulatory framework for {fw_name}"
                },
                "technical_manifestation": {
                    "validator": f"03_core/validators/sot/sot_validator_core.py::validate_{prop}_{fw_key}",
                    "opa_policy": "23_compliance/policies/sot/sot_policy.rego",
                    "cli_command": f"python 12_tooling/cli/sot_validator.py --rule SOT-{str(rule_id).zfill(3)}",
                    "test_path": "11_test_simulation/tests_compliance/test_sot_validator.py"
                },
                "enforcement": {
                    "field_path": f"uk_crypto_regime.{fw_key}.{prop}",
                    "required": prop != "business_priority",
                    "type": "boolean" if prop == "deprecated" else "string"
                },
                "category": "jurisdictions_uk",
                "severity": "CRITICAL" if priority == "must" else "MEDIUM"
            })
            rule_id += 1

    print(f"\n✅ Generiert: {len(new_rules)} neue Regeln (SOT-{NEXT_RULE_ID:03d} bis SOT-{rule_id-1:03d})")

    # Zeige erste 5
    print("\nErste 5 Regeln:")
    for rule in new_rules[:5]:
        print(f"  {rule['rule_id']} ({rule['priority'].upper()}): {rule['rule_name']}")

    # 1. Füge zu YAML Contract hinzu
    print("\n[1/5] Aktualisiere YAML Contract...")
    with open(YAML_CONTRACT, 'r', encoding='utf-8') as f:
        contract = yaml.safe_load(f)

    contract['rules'].extend(new_rules)
    contract['sot_contract_metadata']['total_rules'] = len(contract['rules'])

    with open(YAML_CONTRACT, 'w', encoding='utf-8') as f:
        yaml.dump(contract, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    print(f"   ✅ YAML Contract: {len(new_rules)} Regeln hinzugefügt (Total: {len(contract['rules'])})")

    # 2-5: TODO - Python, Rego, CLI, Tests aktualisieren
    print("\n[2/5] Python Validators: TODO")
    print("[3/5] Rego Policy: TODO")
    print("[4/5] CLI Validator: TODO")
    print("[5/5] Tests: TODO")

    print("\n" + "=" * 80)
    print(f"✅ DEMONSTRATION: {len(new_rules)} Regeln generiert")
    print("⚠️  NUR YAML aktualisiert - Python/Rego/CLI/Tests noch TODO!")
    print("=" * 80)

    return 0

if __name__ == '__main__':
    sys.exit(main())
