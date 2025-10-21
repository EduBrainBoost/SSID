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
