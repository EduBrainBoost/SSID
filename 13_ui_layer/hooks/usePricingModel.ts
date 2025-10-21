
import { useEffect, useMemo, useState } from "react";

type ComputeArgs = {
  tierId: string;
  regions: string[];
  addons: string[];
  bundles: string[];
  discountMonths: number | null;
};

export function usePricingModel(){
  const [model, setModel] = useState<any>(null);
  const [registry, setRegistry] = useState<any>({ did_regions: {} });

  useEffect(() => {
    async function load(){
      try {
        const mj = await fetch("/07_governance_legal/docs/pricing/enterprise_subscription_model_v5.json").then(r=>r.json());
        setModel(mj);
      } catch(e){
        console.warn("JSON model missing, UI fallback requires server-side compile.");
      }
      try {
        const r = await fetch("/13_ui_layer/i18n/regions/region_activation_registry.json").then(r=>r.json());
        setRegistry(r);
      } catch(e) {}
    }
    load();
  }, []);

  const discountMap = useMemo(() => {
    const map: Record<number, number> = {};
    if(model?.discounts){
      for(const d of model.discounts){
        map[d.months] = d.percent;
      }
    }
    return map;
  }, [model]);

  function computeMonthly(args: ComputeArgs){
    if(!model) return { total: 0 };
    const tier = model.tiers.find((t:any)=>t.id===args.tierId);
    if(!tier) return { total: 0 };

    const zones = model.regional_zones || {};
    const surchargePct = Math.max(...args.regions.map(z => (zones[z]?.surcharge_percent ?? 0)), 0) / 100.0;

    const base = (typeof tier.price_eur === "number" ? tier.price_eur : 0);
    // extras (simplified; server-side validator enforces details)
    let addonsTotal = 0;
    for(const a of args.addons){
      const found = model.addons?.find((x:any)=>x.id===a);
      if(found) addonsTotal += found.price_eur;
    }
    let bundlesTotal = 0;
    for(const b of args.bundles){
      const found = model.bundles?.find((x:any)=>x.id===b);
      if(found) bundlesTotal += found.price_eur;
    }
    let total = (base + addonsTotal + bundlesTotal) * (1 + surchargePct);
    if(args.discountMonths && discountMap[args.discountMonths]){
      total = total * (1 - discountMap[args.discountMonths]/100.0);
    }
    return { total };
  }

  return { model, registry, computeMonthly };
}
