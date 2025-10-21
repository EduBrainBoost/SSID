# SSID Entropy Resilience Threshold Policy (PROMPT 5)
# Enforces minimum resilience threshold of 0.70 for trust entropy
# Exit: fail-defined if resilience < 0.70

package ssid.entropy

import future.keywords.if
import future.keywords.in

# Default: allow if resilience not provided (backwards compatibility)
default allow := true

# Deny if resilience below threshold
deny contains msg if {
    input.resilience
    input.resilience < 0.70
    msg := sprintf("Entropy resilience below threshold: %.4f < 0.70 [CRITICAL]", [input.resilience])
}

# Deny if resilience field missing from analysis
deny contains msg if {
    not input.resilience
    input.analysis_id  # Ensure this is actually an entropy analysis
    msg := "Entropy resilience field missing from trust_entropy_analysis.json [ERROR]"
}

# Warning if resilience in danger zone (0.70-0.75)
warn contains msg if {
    input.resilience
    input.resilience >= 0.70
    input.resilience < 0.75
    msg := sprintf("Entropy resilience in danger zone: %.4f (threshold: 0.70) [WARNING]", [input.resilience])
}

# Success condition
allow if {
    input.resilience >= 0.70
}

# Metadata for CI integration
metadata := {
    "policy": "entropy_resilience_threshold",
    "version": "1.0.0",
    "threshold": 0.70,
    "severity": "CRITICAL",
    "enforcement": "hard-block"
}
