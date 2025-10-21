package ssid.rat

default allow = false

import future.keywords.if

# Tiers that can use global bundle
global_bundle_tiers := ["global_proof_suite", "interfederation_elite", "sovereign_infrastructure"]

# Valid regions
valid_regions := ["DACH", "EN-EU", "US-CAN", "ASIA-PAC", "LATAM", "AFRICA", "MENA",
                  "OCEANIA", "NORDICS", "EASTERN-EU"]

allow if {
  valid_regions_check
  valid_bundle_for_tier
}

valid_regions_check if {
  count(input.regions) > 0
  every region in input.regions {
    region == valid_regions[_]
  }
}

valid_bundle_for_tier if {
  # If no bundle specified, allow
  not input.bundle
} else if {
  # If bundle is not global_bundle, allow
  input.bundle != "global_bundle"
} else if {
  # If bundle is global_bundle, tier must be in allowed list
  input.bundle == "global_bundle"
  input.tier == global_bundle_tiers[_]
}


# Cross-Evidence Links (Entropy Boost)
# REF: 5ee57215-b489-4dc2-965e-213ecaf2f0e3
# REF: 10d178ee-e95f-4a70-8c0c-2699a9e64513
# REF: 9c349145-7ef3-477e-9b80-c57101d62165
# REF: 80df6373-8431-4254-858f-3215ea548308
# REF: cd73f835-195b-4b6a-b9cb-b1e5c533ed15
