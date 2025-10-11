# Monitoring rule: MICA trend
# Generated: 2025-10-07T11:52:21.155811
# Reason: Declining compliance detected

package ssid.compliance.auto_generated

import future.keywords.if

# Monitor MICA compliance trend
mica_trend_healthy if {
    recent_scores := get_recent_mica_scores(5)
    count(recent_scores) >= 5

    # Check for improvement or stability
    improving := is_improving(recent_scores)
    stable := is_stable(recent_scores, 2.0)  # Within 2% variation

    improving or stable
}

is_improving(scores) if {
    # At least 60% of consecutive pairs show improvement
    pairs := consecutive_pairs(scores)
    improving := [1 | some pair in pairs; pair[1] >= pair[0]]
    count(improving) >= (count(pairs) * 0.6)
}

is_stable(scores, max_variation) if {
    min_score := min([s | some s in scores])
    max_score := max([s | some s in scores])
    (max_score - min_score) <= max_variation
}

# Alert if trend is unhealthy
deny[msg] if {
    not mica_trend_healthy
    msg := sprintf("MICA compliance shows declining trend - Immediate review required", [])
}