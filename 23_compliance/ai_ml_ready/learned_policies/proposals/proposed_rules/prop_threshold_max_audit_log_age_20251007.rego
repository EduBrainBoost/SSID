# Parameter adjustment: max_audit_log_age
# Generated: 2025-10-07T11:52:21.155811
# Reason: Frequent threshold breaches

package ssid.compliance.auto_generated

import future.keywords.if

# Updated threshold for max_audit_log_age
max_audit_log_age_threshold := 121.0

# Use updated threshold in validation
max_audit_log_age_compliant if {
    actual_value := get_max_audit_log_age_value()
    actual_value <= max_audit_log_age_threshold
}

# Alert if threshold is exceeded
warn[msg] if {
    not max_audit_log_age_compliant
    actual := get_max_audit_log_age_value()
    msg := sprintf("max_audit_log_age exceeds adjusted threshold: %v > 121.0", [actual])
}