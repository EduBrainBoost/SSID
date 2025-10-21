// WASM-first evaluation with JS fallback that mirrors pricing_enforcement.rego
type InputPayload = {
  tier: { id: string },
  base_price_eur: number,
  active_regions: string[],
  addons: string[],
  bundles: string[],
  term_months: number,
  token_lock_proof: boolean,
};

function regionPercent(r: string): number {
  const map: Record<string, number> = { "DACH":0,"EN-EU":5,"US-CAN":10,"LATAM":7,"APAC-EN":5,"MENA":10,"AFRICA-EN":5 };
  return map[r] ?? 0;
}
function addonPrice(a: string): number {
  const m: Record<string, number> = { "compliance_mesh":5000,"private_pqc_node":10000,"sla_247":3000,"dao_seat":7000,"govchain_bridge":8000 };
  return m[a] ?? 0;
}
function bundlePrice(b: string): number {
  const m: Record<string, number> = { "eu_bundle":300,"global_bundle":1000 };
  return m[b] ?? 0;
}
function discount(term: number): number {
  const m: Record<number, number> = { 0:0, 12:5, 24:10, 36:15 };
  return m[term] ?? 0;
}

function computeFallback(input: InputPayload){
  const base = input.base_price_eur;
  const addTotal = input.addons.reduce((s,a)=>s+addonPrice(a), 0);
  const bunTotal = input.bundles.reduce((s,b)=>s+bundlePrice(b), 0);
  const surcharge = input.active_regions.reduce((s,r)=>s+regionPercent(r),0)/100;
  const disc = discount(input.term_months);
  // Token-lock required if discount > 0
  if (disc > 0 && !input.token_lock_proof) {
    throw new Error("Discount selected but token_lock_proof=false");
  }
  const subtotal = (base + addTotal + bunTotal) * (1 + surcharge);
  const total = Math.round(subtotal * (1 - (disc/100)));
  return { price_eur: total, discount_percent: disc };
}

// WASM loader stub: tries to fetch policy wasm if available in repo path; otherwise fallback
async function tryWasmEval(_input: InputPayload): Promise<{ price_eur: number, discount_percent: number } | null> {
  // Placeholder for real WASM evaluation hook – keep optional to avoid build coupling.
  // Implementers can replace this with 'opa-wasm' integration.
  return null;
}

export async function evaluatePrice(input: InputPayload): Promise<{ engine: "wasm"|"fallback"; value: { price_eur: number; discount_percent: number } }>{
  // Try WASM first
  try {
    const wasmRes = await tryWasmEval(input);
    if (wasmRes) return { engine: "wasm", value: wasmRes };
  } catch {}
  // Fallback
  const res = computeFallback(input);
  return { engine: "fallback", value: res };
}
