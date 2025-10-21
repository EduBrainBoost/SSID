# SSID v5 Foundation Readiness Kit
UTC: 2025-10-12T10:29:40Z

## Drop-in Pfade (Projektwurzel = `C:\Users\bibel\Documents\Github\SSID`)

- `02_audit_logging/config/layer_readiness_policy.yaml`
- `03_core/simulation/layer9_proof_aggregator.py`
- `03_core/simulation/config/layer9_simulation.yaml`
- `03_core/simulation/samples/layer9_input.json`
- `11_test_simulation/layer_readiness_audit.py`
- `11_test_simulation/tests/test_layer_readiness_audit.py`
- `11_test_simulation/tests/test_layer9_proof_aggregator.py`
- `12_tooling/ci/layer_v5_foundation_check.yml`
- `16_codex/registry/registry_manifest_v5_global_proof_nexus.yaml`
- `23_compliance/claims/compliance_claims_matrix.yaml`
- `23_compliance/legal/disclaimers/compliance_claims_disclaimer.md`

## Ausführung (Read-only Audit)
```bash
python 11_test_simulation/layer_readiness_audit.py --project-root "C:\\Users\\bibel\\Documents\\Github\\SSID"
```

## Layer 9 Aggregation (Prototype)
```bash
python 03_core/simulation/layer9_proof_aggregator.py --input 03_core/simulation/samples/layer9_input.json --out 02_audit_logging/reports/layer9_output.json
```

## CI (GitHub Actions)
- Datei: `12_tooling/ci/layer_v5_foundation_check.yml` (pytest + Audit)

## Compliance
- Nicht-assertiv, juristischer Review erforderlich (siehe Disclaimer).
