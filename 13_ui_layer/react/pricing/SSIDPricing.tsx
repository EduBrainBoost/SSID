import React, { useMemo, useState, useEffect } from "react";
import { evaluatePrice } from "./opaEval";

type TierId = "core_access" | "professional" | "enterprise_trust" | "global_proof_suite" | "interfederation_elite" | "sovereign_infrastructure";
type RegionCode = "DACH" | "EN-EU" | "US-CAN" | "LATAM" | "APAC-EN" | "MENA" | "AFRICA-EN";

const TIERS: { id: TierId; name: string; base: number }[] = [
  { id: "core_access", name: "Core Access", base: 29 },
  { id: "professional", name: "Professional", base: 99 },
  { id: "enterprise_trust", name: "Enterprise Trust", base: 499 },
  { id: "global_proof_suite", name: "Global Proof Suite", base: 2000 },
  { id: "interfederation_elite", name: "InterFederation Elite", base: 10000 },
  { id: "sovereign_infrastructure", name: "Sovereign Infrastructure", base: 25000 },
];

const ADDONS = [
  { id: "compliance_mesh", label: "Compliance Mesh (+5.000 €)" },
  { id: "private_pqc_node", label: "Private PQC Node (+10.000 €)" },
  { id: "sla_247", label: "24/7 SLA (+3.000 €)" },
  { id: "dao_seat", label: "DAO Seat (+7.000 €)" },
  { id: "govchain_bridge", label: "GovChain Bridge (+8.000 €)" },
] as const;

const BUNDLES = [
  { id: "eu_bundle", label: "EU Bundle (+300 €)" },
  { id: "global_bundle", label: "Global Bundle (+1.000 €)" },
] as const;

const REGIONS: { code: RegionCode; label: string }[] = [
  { code: "DACH", label: "DACH (0%)" },
  { code: "EN-EU", label: "EN-EU (+5%)" },
  { code: "US-CAN", label: "US-CAN (+10%)" },
  { code: "LATAM", label: "LATAM (+7%)" },
  { code: "APAC-EN", label: "APAC-EN (+5%)" },
  { code: "MENA", label: "MENA (+10%)" },
  { code: "AFRICA-EN", label: "AFRICA-EN (+5%)" },
];

function euro(n: number) {
  return (n.toFixed(2) + " €").replace(".", ",");
}

export default function SSIDPricing(): JSX.Element {
  const [tier, setTier] = useState<TierId>("global_proof_suite");
  const [regions, setRegions] = useState<RegionCode[]>(["DACH"]);
  const [addons, setAddons] = useState<string[]>([]);
  const [bundles, setBundles] = useState<string[]>([]);
  const [term, setTerm] = useState<number>(0);
  const [tokenLock, setTokenLock] = useState<boolean>(false);
  const base = useMemo(() => TIERS.find(t => t.id === tier)!.base, [tier]);

  useEffect(() => {
    // If discount selected, require token lock
    if (term > 0 && !tokenLock) setTokenLock(true);
  }, [term]);

  const payload = useMemo(() => ({
    tier: { id: tier },
    base_price_eur: base,
    active_regions: regions,
    addons,
    bundles,
    term_months: term,
    token_lock_proof: tokenLock
  }), [tier, base, regions, addons, bundles, term, tokenLock]);

  const [computed, setComputed] = useState<{ price_eur: number; discount_percent: number } | null>(null);
  const [engine, setEngine] = useState<"wasm" | "fallback">("fallback");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const res = await evaluatePrice(payload);
        if (!cancelled) {
          setComputed(res.value);
          setEngine(res.engine);
          setError(null);
        }
      } catch (e:any) {
        if (!cancelled) setError(e?.message ?? String(e));
      }
    })();
    return () => { cancelled = true; };
  }, [payload]);

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <h1 className="text-3xl font-bold mb-4">SSID Pricing – Live Kalkulation</h1>
      <div className="text-sm mb-4 opacity-70">Engine: <span className="font-mono">{engine}</span>{error ? ` – Fehler: ${error}` : ""}</div>

      <div className="grid md:grid-cols-2 gap-6">
        {/* Controls */}
        <div className="rounded-2xl p-4 border shadow-sm">
          <h2 className="text-xl font-semibold mb-3">Eingaben</h2>
          <label className="block mb-2">Stufe</label>
          <select value={tier} onChange={e => setTier(e.target.value as TierId)} className="w-full border rounded p-2 mb-4">
            {TIERS.map(t => <option key={t.id} value={t.id}>{t.name} ({euro(t.base)})</option>)}
          </select>

          <label className="block mb-2">Regionen (RAT)</label>
          <div className="flex flex-wrap gap-2 mb-4">
            {REGIONS.map(r => (
              <label key={r.code} className="inline-flex items-center gap-2 border rounded-full px-3 py-1">
                <input type="checkbox" checked={regions.includes(r.code)} onChange={(e) => {
                  setRegions(prev => e.target.checked ? [...new Set([...prev, r.code])] : prev.filter(x => x !== r.code));
                }} />
                <span>{r.label}</span>
              </label>
            ))}
          </div>

          <label className="block mb-2">Add-ons</label>
          <div className="flex flex-wrap gap-2 mb-4">
            {ADDONS.map(a => (
              <label key={a.id} className="inline-flex items-center gap-2 border rounded-full px-3 py-1">
                <input type="checkbox" checked={addons.includes(a.id)} onChange={(e) => {
                  setAddons(prev => e.target.checked ? [...new Set([...prev, a.id])] : prev.filter(x => x !== a.id));
                }} />
                <span>{a.label}</span>
              </label>
            ))}
          </div>

          <label className="block mb-2">Bundles</label>
          <div className="flex flex-wrap gap-2 mb-4">
            {BUNDLES.map(b => (
              <label key={b.id} className="inline-flex items-center gap-2 border rounded-full px-3 py-1">
                <input type="checkbox" checked={bundles.includes(b.id)} onChange={(e) => {
                  setBundles(prev => e.target.checked ? [...new Set([...prev, b.id])] : prev.filter(x => x !== b.id));
                }} />
                <span>{b.label}</span>
              </label>
            ))}
          </div>

          <label className="block mb-2">Laufzeit (Rabatt per Token-Lock)</label>
          <select value={term} onChange={e => setTerm(parseInt(e.target.value))} className="w-full border rounded p-2 mb-4">
            <option value={0}>Keine Bindung (0 %)</option>
            <option value={12}>12 Monate (−5 %)</option>
            <option value={24}>24 Monate (−10 %)</option>
            <option value={36}>36 Monate (−15 %)</option>
          </select>

          <label className="inline-flex items-center gap-2">
            <input type="checkbox" checked={tokenLock} onChange={e => setTokenLock(e.target.checked)} />
            <span>Token-Lock Nachweis</span>
          </label>
        </div>

        {/* Output */}
        <div className="rounded-2xl p-4 border shadow-sm">
          <h2 className="text-xl font-semibold mb-3">Ergebnis</h2>
          <pre className="bg-gray-50 p-3 rounded overflow-auto text-sm">{JSON.stringify(payload, null, 2)}</pre>
          <div className="mt-4 text-2xl font-bold">
            {computed ? `Preis: ${euro(computed.price_eur)} (Rabatt: ${computed.discount_percent}%)` : "Berechne…"}
          </div>
          <p className="text-sm opacity-70 mt-2">Preise sind **deterministisch** per OPA-Regelwerk berechnet; bei fehlendem WASM-Fetch nutzt die Komponente eine **JS-Fallback-Evaluation** mit identischer Logik.</p>
        </div>
      </div>
    </div>
  );
}
