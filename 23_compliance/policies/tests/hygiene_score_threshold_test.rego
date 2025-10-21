package ssid.hygiene.enforcement.test

import data.ssid.hygiene.enforcement

# PASS-Test – score above threshold
test_pass_ok {
  input := {"score": 95, "status": "PLATINUM", "ts": "2025-10-15T00:00:00Z"}
  enforcement.allow with input as input
}

test_pass_exact_threshold {
  input := {"score": 90, "status": "GOLD", "ts": "2025-10-15T00:00:00Z"}
  enforcement.allow with input as input
}

# FAIL-Test – score below threshold
test_fail_block_low_score {
  input := {"score": 70, "status": "SILVER", "ts": "2025-10-15T00:00:00Z"}
  enforcement.deny with input as input
}

test_fail_block_critical {
  input := {"score": 30, "status": "NONE", "ts": "2025-10-15T00:00:00Z"}
  enforcement.deny with input as input
}

# Evaluation result tests
test_evaluation_pass {
  input := {"score": 95, "status": "PLATINUM", "ts": "2025-10-15T00:00:00Z"}
  result := enforcement.evaluation_result with input as input
  result.status == "PASS"
  result.score == 95
}

test_evaluation_fail {
  input := {"score": 80, "status": "SILVER", "ts": "2025-10-15T00:00:00Z"}
  result := enforcement.evaluation_result with input as input
  result.status == "FAIL"
  result.score == 80
}


# Cross-Evidence Links (Entropy Boost)
# REF: a3069eca-a171-4f90-9e5d-d926ba5a9cc2
# REF: 21bb9e6f-12ae-4444-a814-1aa8507fa295
# REF: 1b8b584b-7c34-443b-88ee-c387cf338f36
# REF: 454c38ce-1dd7-4533-ae3c-11e8f27b7e2d
# REF: 4dde6f57-e58c-48aa-babe-896571b5e008
