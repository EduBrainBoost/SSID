# SSID CI Extended – YAML→JSON Compile + OPA Gate + Artifact Upload (v5.1)

## Jobs
- **Compile**: `scripts/compile_pricing.py` (YAML → JSON)
- **OPA Gate**: `scripts/opa_gate.sh` (fail-on-policy)
- **Artifact**: Upload `enterprise_subscription_model_v5.json`

## Voraussetzung
- Policies unter `23_compliance/policies/` (pricing_enforcement.rego, rat_enforcement.rego)
- Pricing-YAML unter `07_governance_legal/docs/pricing/enterprise_subscription_model_v5.yaml`
