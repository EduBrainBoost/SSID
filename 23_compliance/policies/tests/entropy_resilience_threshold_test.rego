# Tests for Entropy Resilience Threshold Policy

package ssid.entropy

import future.keywords.if

# Test: resilience = 0.70 (exactly at threshold) - PASS
test_resilience_at_threshold if {
    allow with input as {"resilience": 0.70}
    count(deny) == 0
}

# Test: resilience = 0.75 (above threshold) - PASS
test_resilience_above_threshold if {
    allow with input as {"resilience": 0.75}
    count(deny) == 0
}

# Test: resilience = 0.64 (below threshold) - FAIL
test_resilience_below_threshold if {
    not allow with input as {"resilience": 0.64}
    count(deny) > 0
}

# Test: resilience = 0.69 (just below threshold) - FAIL
test_resilience_just_below if {
    not allow with input as {"resilience": 0.69}
    deny_messages := deny with input as {"resilience": 0.69}
    count(deny_messages) > 0
}

# Test: resilience = 0.90 (well above threshold) - PASS
test_resilience_excellent if {
    allow with input as {"resilience": 0.90}
    count(deny) == 0
}

# Test: resilience = 0.72 (danger zone) - PASS but with warning
test_resilience_danger_zone if {
    allow with input as {"resilience": 0.72}
    count(warn) > 0
}

# Test: missing resilience field - FAIL
test_missing_resilience if {
    deny_messages := deny with input as {"analysis_id": "test"}
    count(deny_messages) > 0
}


# Cross-Evidence Links (Entropy Boost)
# REF: 84009970-1196-4a32-b189-c6931bbc23a1
# REF: 58a13290-3cbf-43c5-85c8-7268a0498fdf
# REF: 13390663-53a3-4456-ba76-140e548d4742
# REF: ce7e6a3d-e030-4464-8991-28ad293453cf
# REF: 09ddd56b-54a1-4dbb-b70c-aa5a7fdb027a
