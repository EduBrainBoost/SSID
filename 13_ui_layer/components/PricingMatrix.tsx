
import React, { useMemo, useState } from "react";
import { RegionToggle } from "./RegionToggle";
import { usePricingModel } from "../hooks/usePricingModel";

type TierId = "core_access" | "professional" | "enterprise_trust" | "global_proof_suite" | "interfederation_elite" | "sovereign_infrastructure";

export default function PricingMatrix() {
  const { model, registry, computeMonthly } = usePricingModel();
  const [selectedTier, setSelectedTier] = useState<TierId>("enterprise_trust");
  const [selectedRegions, setSelectedRegions] = useState<string[]>(registry?.did_regions?.["did:ssid:company-123"] ?? ["DACH"]);
  const [addons, setAddons] = useState<string[]>([]);
  const [bundles, setBundles] = useState<string[]>([]);
  const [discountMonths, setDiscountMonths] = useState<number | null>(null);

  if (!model) return <div>Pricing lädt…</div>;

  const tiers = model.tiers;
  const zoneMap = model.regional_zones;

  const result = useMemo(() => {
    return computeMonthly({
      tierId: selectedTier,
      regions: selectedRegions,
      addons,
      bundles,
      discountMonths
    });
  }, [selectedTier, selectedRegions, addons, bundles, discountMonths]);

  return (
    <div className="p-4 space-y-4">
      <h2 className="text-xl font-bold">SSID Pricing (v5.1)</h2>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        {tiers.map((t:any) => (
          <button
            key={t.id}
            onClick={() => setSelectedTier(t.id)}
            className={`border rounded-xl p-3 text-left ${selectedTier===t.id ? "border-black" : "border-gray-300"}`}
            >
            <div className="font-semibold">{t.name}</div>
            <div className="text-sm opacity-70">{typeof t.price_eur === "number" ? `${t.price_eur} €/Monat` : `${t.price_eur}`}</div>
            <div className="text-xs mt-2">DIDs: {t.dids_included}</div>
          </button>
        ))}
      </div>

      <RegionToggle zones={zoneMap} selected={selectedRegions} onChange={setSelectedRegions} />

      <div className="space-y-2">
        <h3 className="font-semibold">Add-ons</h3>
        <div className="flex flex-wrap gap-2">
          {model.addons?.map((a:any) => (
            <label key={a.id} className="flex items-center gap-2 border rounded-lg px-2 py-1">
              <input
                type="checkbox"
                checked={addons.includes(a.id)}
                onChange={(e) => {
                  const checked = e.target.checked;
                  setAddons((old) =>
                    checked ? Array.from(new Set([...old, a.id])) : old.filter(x => x !== a.id)
                  );
                }}
              />
              <span>{a.id} (+{a.price_eur}€)</span>
            </label>
          ))}
        </div>
      </div>

      <div className="space-y-2">
        <h3 className="font-semibold">Bundles</h3>
        <div className="flex flex-wrap gap-2">
          {model.bundles?.map((b:any) => (
            <label key={b.id} className="flex items-center gap-2 border rounded-lg px-2 py-1">
              <input
                type="checkbox"
                checked={bundles.includes(b.id)}
                onChange={(e) => {
                  const checked = e.target.checked;
                  setBundles((old) =>
                    checked ? Array.from(new Set([...old, b.id])) : old.filter(x => x !== b.id)
                  );
                }}
              />
              <span>{b.id} (+{b.price_eur}€)</span>
            </label>
          ))}
        </div>
      </div>

      <div className="space-y-2">
        <h3 className="font-semibold">Rabatt (Token-Lock)</h3>
        <select
          className="border rounded-lg p-2"
          value={discountMonths ?? ""}
          onChange={(e) => setDiscountMonths(e.target.value ? parseInt(e.target.value) : null)}
        >
          <option value="">Kein Rabatt</option>
          {model.discounts?.map((d:any) => (
            <option key={d.id} value={d.months}>
              {d.id} – {d.months} Mon (−{d.percent}%)
            </option>
          ))}
        </select>
      </div>

      <div className="border rounded-xl p-3">
        <div className="font-semibold">Monatliche Kosten</div>
        <div className="text-2xl">{result.total.toLocaleString("de-DE", { minimumFractionDigits: 2, maximumFractionDigits: 2 })} €</div>
        <div className="text-xs opacity-70">inkl. Regionalaufschlag & legitime Rabatte (OPA-enforced)</div>
      </div>
    </div>
  );
}
