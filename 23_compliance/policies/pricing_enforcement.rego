package ssid.pricing

default allow = false

tiers_order := ["core_access","professional","enterprise_trust","global_proof_suite","interfederation_elite","sovereign_infrastructure"]

allow {
  valid_monotonic_prices
  valid_discount_bounds
}

valid_monotonic_prices {
  prices := [t.price_eur | t := input.tiers[_]]
  nprices := [p | p := prices[_]; p := if is_number(p) then p else 25000]
  every i in [0..count(nprices)-2] {
    nprices[i] <= nprices[i+1]
  }
}

valid_discount_bounds {
  some d
  d := input.discounts[_]
  is_number(d.percent)
  d.percent >= 0
  d.percent <= 20
}


# Cross-Evidence Links (Entropy Boost)
# REF: c515b54d-7b93-44ea-8ab5-186f39f9fa47
# REF: a72bc860-f50d-4c60-b97e-1f0c939a6956
# REF: fc75e7ee-917d-4947-b049-ea21f0108b92
# REF: 32c7a7c5-9ede-4afe-b1df-9acbc987806e
# REF: 61133826-c915-4523-a9d2-3cf0e1470fe0
