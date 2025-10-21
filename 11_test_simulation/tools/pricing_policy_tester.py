
import json, sys

def region_percent(r):
    return {"DACH":0,"EN-EU":5,"US-CAN":10,"LATAM":7,"APAC-EN":5,"MENA":10,"AFRICA-EN":5}.get(r,0)

def addon_price(a):
    return {"compliance_mesh":5000,"private_pqc_node":10000,"sla_247":3000,"dao_seat":7000,"govchain_bridge":8000}[a]

def bundle_price(b):
    return {"eu_bundle":300,"global_bundle":1000}[b]

def discount(term):
    return {0:0,12:5,24:10,36:15}.get(term,0)

def compute(input_data):
    base = input_data["base_price_eur"]
    add_total = sum(addon_price(a) for a in input_data.get("addons",[]))
    bun_total = sum(bundle_price(b) for b in input_data.get("bundles",[]))
    surcharge = sum(region_percent(r) for r in input_data.get("active_regions",[]))/100.0
    disc = discount(input_data.get("term_months",0))
    subtotal = (base + add_total + bun_total) * (1.0 + surcharge)
    total = round(subtotal * (1.0 - disc/100))
    return {"price_eur": total, "discount_percent": disc}

if __name__ == "__main__":
    data = json.loads(sys.stdin.read())
    print(json.dumps(compute(data)))
