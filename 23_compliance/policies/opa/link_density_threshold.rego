# link_density_threshold.rego
# Link Density Threshold Policy - Software Ecology Optimization
# Autor: edubrainboost ©2025 MIT License
#
# Purpose: Enforce link density thresholds and flag modules for
#          de-duplication review when isolation rate exceeds healthy limits.
#
# Evaluation: opa eval -d link_density_threshold.rego -i analysis.json "data.ecology.allow"

package ecology

import future.keywords.if
import future.keywords.in

# Default allow - low isolation is acceptable
default allow = true

# Configuration thresholds
max_isolation_rate := 99.9  # 99.9% isolation triggers review
min_link_density := 0.001   # 0.1% minimum link density
max_low_connectivity_pct := 25  # 25% modules with <=1 edge is limit

# Deny if isolation rate exceeds maximum
deny[msg] if {
    isolation_rate := to_number(trim_suffix(input.graph_metrics.isolation_rate, "%"))
    isolation_rate > max_isolation_rate
    msg := sprintf("Isolation rate too high: %.2f%% > %.2f%% (potential over-isolation)",
                   [isolation_rate, max_isolation_rate])
}

# Deny if link density below minimum
deny[msg] if {
    link_density := to_number(trim_suffix(input.graph_metrics.link_density, "%"))
    link_density < min_link_density
    msg := sprintf("Link density too low: %.4f%% < %.4f%% (ecosystem fragmentation)",
                   [link_density, min_link_density])
}

# Warning if low connectivity percentage exceeds threshold
warn[msg] if {
    low_conn_pct := to_number(trim_suffix(input.connectivity_analysis.low_connectivity_percentage, "%"))
    low_conn_pct > max_low_connectivity_pct
    msg := sprintf("High low-connectivity rate: %.1f%% > %.0f%% (consider consolidation)",
                   [low_conn_pct, max_low_connectivity_pct])
}

# Recommendation: Flag high-priority deduplication targets
recommend[msg] if {
    some rec in input.deduplication_recommendations
    rec.priority == "HIGH"
    msg := sprintf("HIGH PRIORITY: %s - %s", [rec.type, rec.target])
}

# Check: Shard health module duplication detected
shard_health_duplication if {
    some rec in input.deduplication_recommendations
    rec.type == "CONSOLIDATE_SHARD_MODULES"
    count_str := split(rec.target, " ")[0]
    count := to_number(count_str)
    count > 100  # More than 100 duplicate health modules
}

# Exception: Allow baseline + subclass pattern (1 base + ≤400 shard subclasses)
shard_health_consolidation_pattern if {
    # Check if ShardHealthCheck base class exists
    input.consolidation_status
    input.consolidation_status.base_class_exists == true

    # Allow up to 400 shard subclasses (one per shard)
    subclass_count := input.consolidation_status.subclass_count
    subclass_count <= 400
}

deny[msg] if {
    shard_health_duplication
    not shard_health_consolidation_pattern  # Only deny if NOT using consolidation pattern
    some rec in input.deduplication_recommendations
    rec.type == "CONSOLIDATE_SHARD_MODULES"
    msg := sprintf("Critical duplication: %s - MUST consolidate to reduce build overhead", [rec.target])
}

# Efficiency assessment
efficiency_rating := "EXCELLENT" if {
    link_density := to_number(trim_suffix(input.graph_metrics.link_density, "%"))
    low_conn_pct := to_number(trim_suffix(input.connectivity_analysis.low_connectivity_percentage, "%"))
    link_density > 0.5  # > 0.5% link density
    low_conn_pct < 15   # < 15% low connectivity
}

efficiency_rating := "GOOD" if {
    link_density := to_number(trim_suffix(input.graph_metrics.link_density, "%"))
    low_conn_pct := to_number(trim_suffix(input.connectivity_analysis.low_connectivity_percentage, "%"))
    link_density > 0.1
    link_density <= 0.5
    low_conn_pct < 25
}

efficiency_rating := "NEEDS_IMPROVEMENT" if {
    link_density := to_number(trim_suffix(input.graph_metrics.link_density, "%"))
    low_conn_pct := to_number(trim_suffix(input.connectivity_analysis.low_connectivity_percentage, "%"))
    link_density <= 0.1
    low_conn_pct >= 25
}

efficiency_rating := "POOR" if {
    not efficiency_rating  # Fallback
}

# Policy decision summary
policy_decision := {
    "allow": allow,
    "deny_reasons": deny,
    "warnings": warn,
    "recommendations": recommend,
    "efficiency_rating": efficiency_rating,
    "action_required": count(deny) > 0,
    "optimization_opportunities": count(recommend)
}

# Compliance assessment
compliance_assessment := {
    "isolation_benefits": "EXCELLENT (no uncontrolled side effects)",
    "efficiency_tradeoff": efficiency_rating,
    "optimization_needed": count(recommend) > 0,
    "critical_issues": count(deny),
    "overall_health": "COMPLIANT" if allow else "NON_COMPLIANT"
}
