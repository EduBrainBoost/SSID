package ssid.pricing.v5_2

default allow = false

import future.keywords.if

# Valid tiers
valid_tiers := ["core_access", "professional", "enterprise_trust", "global_proof_suite",
                "interfederation_elite", "sovereign_infrastructure", "partner_enterprise",
                "starter", "enterprise", "enterprise_plus", "sovereign"]

# Valid regions
valid_regions := ["DACH", "EN-EU", "US-CAN", "ASIA-PAC", "LATAM", "AFRICA", "MENA",
                  "OCEANIA", "NORDICS", "EASTERN-EU", "APAC-EN", "EU-WEST"]

# Valid addons
valid_addons := ["compliance_mesh", "pqc_node", "sla_24_7", "audit_feed",
                 "knowledge_graph", "federation_linker", "blockchain_anchor"]

# Allow if all checks pass
allow if {
  valid_tier
  valid_discount
  valid_region_list
  valid_addon_list
}

valid_tier if {
  input.tier
  input.tier == valid_tiers[_]
}

valid_discount if {
  input.discount_percent >= 0
  input.discount_percent <= 20
}

valid_region_list if {
  count(input.regions) > 0
  every region in input.regions {
    region == valid_regions[_]
  }
}

valid_addon_list if {
  # Addons are optional, but if present must be valid
  not input.addons
}

valid_addon_list if {
  input.addons
  every addon in input.addons {
    addon == valid_addons[_]
  }
}
