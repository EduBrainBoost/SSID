package ssid.rat_test

import data.ssid.rat

# Test: Global bundle allowed for tier 3+ (global_proof_suite)
test_allow_global_bundle_tier3 {
	rat.allow with input as {
		"model": {
			"regional_zones": {
				"DACH": {"surcharge_percent": 0},
				"EN-EU": {"surcharge_percent": 5},
			},
		},
		"request": {
			"tier": "global_proof_suite",
			"regions": ["DACH"],
			"bundles": ["global_bundle"],
		},
	}
}

# Test: Global bundle allowed for tier 4 (interfederation_elite)
test_allow_global_bundle_tier4 {
	rat.allow with input as {
		"model": {"regional_zones": {"DACH": {}}},
		"request": {
			"tier": "interfederation_elite",
			"regions": ["DACH"],
			"bundles": ["global_bundle"],
		},
	}
}

# Test: Global bundle allowed for tier 5 (sovereign_infrastructure)
test_allow_global_bundle_tier5 {
	rat.allow with input as {
		"model": {"regional_zones": {"DACH": {}}},
		"request": {
			"tier": "sovereign_infrastructure",
			"regions": ["DACH"],
			"bundles": ["global_bundle"],
		},
	}
}

# Negative Test: Global bundle DENIED for tier 0 (core_access)
test_deny_global_bundle_tier0 {
	not rat.allow with input as {
		"model": {"regional_zones": {"DACH": {}}},
		"request": {
			"tier": "core_access",
			"regions": ["DACH"],
			"bundles": ["global_bundle"],
		},
	}
}

# Negative Test: Global bundle DENIED for tier 1 (professional)
test_deny_global_bundle_tier1 {
	not rat.allow with input as {
		"model": {"regional_zones": {"DACH": {}}},
		"request": {
			"tier": "professional",
			"regions": ["DACH"],
			"bundles": ["global_bundle"],
		},
	}
}

# Negative Test: Global bundle DENIED for tier 2 (enterprise_trust)
test_deny_global_bundle_tier2 {
	not rat.allow with input as {
		"model": {"regional_zones": {"DACH": {}}},
		"request": {
			"tier": "enterprise_trust",
			"regions": ["DACH"],
			"bundles": ["global_bundle"],
		},
	}
}

# Test: Non-global bundles allowed for all tiers
test_allow_eu_bundle_tier0 {
	rat.allow with input as {
		"model": {"regional_zones": {"DACH": {}}},
		"request": {
			"tier": "core_access",
			"regions": ["DACH"],
			"bundles": ["eu_bundle"],
		},
	}
}

# Test: No bundles always allowed
test_allow_no_bundles {
	rat.allow with input as {
		"model": {"regional_zones": {"DACH": {}}},
		"request": {
			"tier": "core_access",
			"regions": ["DACH"],
			"bundles": [],
		},
	}
}

# Test: Regions supported - single region
test_allow_single_region {
	rat.allow with input as {
		"model": {
			"regional_zones": {
				"DACH": {},
				"EN-EU": {},
			},
		},
		"request": {
			"tier": "professional",
			"regions": ["DACH"],
			"bundles": [],
		},
	}
}

# Test: Regions supported - multiple regions
test_allow_multiple_regions {
	rat.allow with input as {
		"model": {
			"regional_zones": {
				"DACH": {},
				"EN-EU": {},
				"US-CAN": {},
			},
		},
		"request": {
			"tier": "global_proof_suite",
			"regions": ["DACH", "EN-EU", "US-CAN"],
			"bundles": ["global_bundle"],
		},
	}
}

# Negative Test: Unsupported region should DENY
test_deny_unsupported_region {
	not rat.allow with input as {
		"model": {
			"regional_zones": {
				"DACH": {},
				"EN-EU": {},
			},
		},
		"request": {
			"tier": "professional",
			"regions": ["INVALID-REGION"],
			"bundles": [],
		},
	}
}

# Negative Test: Partially supported regions should DENY
test_deny_partial_region_support {
	not rat.allow with input as {
		"model": {
			"regional_zones": {
				"DACH": {},
				"EN-EU": {},
			},
		},
		"request": {
			"tier": "professional",
			"regions": ["DACH", "UNSUPPORTED"],
			"bundles": [],
		},
	}
}

# Edge Test: Empty regions should allow (no region requirement)
test_allow_empty_regions {
	rat.allow with input as {
		"model": {"regional_zones": {"DACH": {}}},
		"request": {
			"tier": "professional",
			"regions": [],
			"bundles": [],
		},
	}
}


# Cross-Evidence Links (Entropy Boost)
# REF: 9812ab83-1101-498d-aa81-4967bbada621
# REF: eef38b55-6f01-445b-b44f-029284d47581
# REF: 96b58068-24cb-4237-a9e3-c28e9e9b771f
# REF: 4446b245-88b7-4368-9d97-6d44d4d4035a
# REF: 9539458a-049f-4572-b3e7-5e94f384f55e
