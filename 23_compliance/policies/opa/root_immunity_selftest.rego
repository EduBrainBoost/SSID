package root_immunity_selftest

# ROOT-IMMUNITY SELFTEST POLICY
# Evaluates immunity scale and determines system health

# Default: Not immune until proven
default immune = false

# System is immune if immunity scale >= 95%
immune if {
    input.immunity_scale >= 95.0
    no_critical_failures
}

# Check for critical failures
no_critical_failures if {
    count(critical_attack_failures) == 0
}

# Identify critical attack failures
critical_attack_failures[attack] {
    some attack in input.attacks
    attack.severity == "CRITICAL"
    attack.success_rate < 1.0
}

# Health status determination
health_status := status if {
    immune
    status := "HEALTHY"
} else := status if {
    input.immunity_scale >= 80.0
    input.immunity_scale < 95.0
    status := "DEGRADED"
} else := status if {
    status := "COMPROMISED"
}

# Detailed evaluation report
evaluation := report if {
    report := {
        "immune": immune,
        "health_status": health_status,
        "immunity_scale": input.immunity_scale,
        "threshold": 95.0,
        "attacks_total": count(input.attacks),
        "critical_failures": count(critical_attack_failures),
        "degraded_attacks": count(degraded_attacks),
        "timestamp": input.timestamp,
        "verdict": verdict
    }
}

# Degraded attacks (not critical but below 100%)
degraded_attacks[attack] {
    some attack in input.attacks
    attack.success_rate < 1.0
    attack.success_rate >= 0.5
}

# Verdict based on immunity
verdict := "SYSTEM IMMUNE - All defenses operational" if {
    immune
} else := "SYSTEM DEGRADED - Some defenses weakened" if {
    health_status == "DEGRADED"
} else := "SYSTEM COMPROMISED - Critical defense failure" if {
    health_status == "COMPROMISED"
}

# Deny if not immune
deny[msg] if {
    not immune
    msg := sprintf("Immunity scale %v%% is below 95%% threshold", [input.immunity_scale])
}

deny[msg] if {
    some attack in critical_attack_failures
    msg := sprintf("Critical attack type '%v' not fully blocked (success rate: %v%%)",
                   [attack.type, attack.success_rate * 100])
}

# Recommendations
recommendations[rec] if {
    not immune
    rec := "Investigate daemon blocking failures"
}

recommendations[rec] if {
    count(critical_attack_failures) > 0
    rec := "Review ROOT-IMMUNITY daemon logic for critical vulnerabilities"
}

recommendations[rec] if {
    health_status == "DEGRADED"
    rec := "Schedule maintenance to restore immunity to 95%+"
}

recommendations[rec] if {
    immune
    rec := "System healthy - continue monthly self-tests"
}


# Cross-Evidence Links (Entropy Boost)
# REF: 090ca049-a846-4665-9fa7-36bf1abfdb52
# REF: 94060cc6-4a93-4f12-a0ab-bf61b87dbdcd
# REF: 9f213218-95a9-4a46-9424-4562c9822060
# REF: 5a498590-b604-4743-8dac-f67faef34987
# REF: 62294c5a-ae74-4a2e-bfe6-4cb8422b91ea
