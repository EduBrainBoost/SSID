package ssid.hygiene.enforcement

# SSID – Hygiene Score Enforcement Policy
# Version: 1.0.0
# Status: ACTIVE
# Root-24-LOCK compliant – no external writes, no PII
# Purpose: Enforce minimum hygiene certificate score threshold

default allow = false
default deny = true

# Input format expected from CI JSON result:
# {
#   "score": 95,
#   "status": "PLATINUM",
#   "ts": "2025-10-15T03:00:00Z"
# }

# Threshold: Minimum acceptable hygiene score = 90
allow {
  input.score >= 90
}

# Explicit deny with reason
deny[reason] {
  not allow
  reason := sprintf("Hygiene score below threshold: %v < 90 (Status: %v)", [input.score, input.status])
}

# Helper: Get current evaluation result
evaluation_result = result {
  allow
  result := {
    "status": "PASS",
    "score": input.score,
    "threshold": 90,
    "timestamp": input.ts
  }
}

evaluation_result = result {
  not allow
  result := {
    "status": "FAIL",
    "score": input.score,
    "threshold": 90,
    "timestamp": input.ts,
    "reason": sprintf("Score %v below minimum threshold 90", [input.score])
  }
}
