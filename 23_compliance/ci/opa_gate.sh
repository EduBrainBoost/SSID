#!/usr/bin/env bash
set -euo pipefail
OPA_BIN="${OPA_BIN:-~/.opa/opa}"
MODEL_JSON="$1"
${OPA_BIN} eval --format pretty --data 23_compliance/policies/pricing_enforcement.rego --input "${MODEL_JSON}" 'data.ssid.pricing.allow' | tee /tmp/opa_pricing.out
grep -q "true" /tmp/opa_pricing.out
cat > /tmp/rat_input.json <<JSON
{ "model": $(cat "${MODEL_JSON}"), "request": { "tier": "global_proof_suite", "regions": ["DACH","EN-EU"], "bundles": ["global_bundle"] } }
JSON
${OPA_BIN} eval --format pretty --data 23_compliance/policies/rat_enforcement.rego --input /tmp/rat_input.json 'data.ssid.rat.allow' | tee /tmp/opa_rat.out
grep -q "true" /tmp/opa_rat.out
echo "OPA Gate: PASS"
