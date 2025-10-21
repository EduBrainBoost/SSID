#!/usr/bin/env bash
set -euo pipefail

OPA_BIN="${OPA_BIN:-~/.opa/opa}"
MODEL_JSON="$1"

echo "OPA Gate: pricing_enforcement.rego against ${MODEL_JSON}"
${OPA_BIN} eval --format pretty \
  --data 23_compliance/policies/pricing_enforcement.rego \
  --input "${MODEL_JSON}" 'data.ssid.pricing.allow' | tee /tmp/opa_pricing.out

if ! grep -q "true" /tmp/opa_pricing.out; then
  echo "::error::Policy gate failed: pricing_enforcement.rego did not allow model"
  exit 1
fi

echo "OPA Gate: rat_enforcement.rego bundle/global check"
cat > /tmp/rat_input.json <<JSON
{
  "model": $(cat "${MODEL_JSON}"),
  "request": { "tier": "global_proof_suite", "regions": ["DACH","EN-EU"], "bundles": ["global_bundle"] }
}
JSON

${OPA_BIN} eval --format pretty \
  --data 23_compliance/policies/rat_enforcement.rego \
  --input /tmp/rat_input.json 'data.ssid.rat.allow' | tee /tmp/opa_rat.out

if ! grep -q "true" /tmp/opa_rat.out; then
  echo "::error::Policy gate failed: rat_enforcement.rego denied request"
  exit 1
fi

echo "OPA Gate: PASS"
