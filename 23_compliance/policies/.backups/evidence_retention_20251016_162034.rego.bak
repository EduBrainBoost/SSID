# evidence_retention.rego - Evidence Retention Policy
# Author: edubrainboost ©2025 MIT License
#
# Evaluates evidence storage health and enforces retention limits:
# - Active file count within limits
# - Total storage size reasonable
# - Archive success rate acceptable
# - Permanent evidence preserved
#
# Input format:
# {
#   "permanent_count": 10,
#   "active_count": 45,
#   "archived_count": 120,
#   "total_size_mb": 85,
#   "archive_success_rate": 98.5
# }

package evidence_retention

# ===== Configuration Parameters =====

# Maximum active evidence files
max_active_files := 500

# Maximum total storage size (MB)
max_total_size_mb := 100

# Minimum archive success rate (%)
min_archive_success_rate := 95.0

# Maximum age for active evidence (days)
max_active_age_days := 14

# ===== Core Rules =====

# Active file count is within limits
active_count_healthy if {
    input.active_count <= max_active_files
}

# Total storage size is reasonable
storage_size_healthy if {
    input.total_size_mb <= max_total_size_mb
}

# Archive success rate is acceptable
archive_success_healthy if {
    input.archive_success_rate >= min_archive_success_rate
}

# No permanent evidence was deleted
permanent_evidence_preserved if {
    # Check that permanent count didn't decrease
    input.permanent_count >= 0
}

# ===== Deny Rules =====

deny[msg] if {
    not active_count_healthy
    msg := sprintf(
        "Active evidence count exceeds limit: %d files (max: %d)",
        [input.active_count, max_active_files]
    )
}

deny[msg] if {
    not storage_size_healthy
    msg := sprintf(
        "Evidence storage size exceeds limit: %.1f MB (max: %d MB)",
        [input.total_size_mb, max_total_size_mb]
    )
}

deny[msg] if {
    # Only check if archiving has occurred
    input.archived_count > 0
    not archive_success_healthy
    msg := sprintf(
        "Archive success rate too low: %.1f%% (min: %.1f%%)",
        [input.archive_success_rate, min_archive_success_rate]
    )
}

# ===== Warning Rules =====

warn[msg] if {
    # Warn if approaching active file limit
    active_count_healthy
    utilization := (input.active_count * 100.0) / max_active_files
    utilization > 80.0
    msg := sprintf(
        "Active evidence approaching limit: %d files (%.1f%% of capacity)",
        [input.active_count, utilization]
    )
}

warn[msg] if {
    # Warn if approaching storage limit
    storage_size_healthy
    utilization := (input.total_size_mb * 100.0) / max_total_size_mb
    utilization > 80.0
    msg := sprintf(
        "Evidence storage approaching limit: %.1f MB (%.1f%% of capacity)",
        [input.total_size_mb, utilization]
    )
}

warn[msg] if {
    # Warn if no archives exist yet
    not input.archived_count
    msg := "No archived evidence - rolling window not yet in effect"
}

# ===== Info Rules =====

info[msg] if {
    msg := sprintf(
        "Active evidence: %d files, %.1f MB",
        [input.active_count, input.total_size_mb]
    )
}

info[msg] if {
    input.archived_count > 0
    msg := sprintf(
        "Archived evidence: %d files (success rate: %.1f%%)",
        [input.archived_count, input.archive_success_rate]
    )
}

info[msg] if {
    input.permanent_count > 0
    msg := sprintf(
        "Permanent evidence: %d files (never deleted)",
        [input.permanent_count]
    )
}

# ===== Assessment =====

assessment := {
    "active_count_healthy": active_count_healthy,
    "storage_size_healthy": storage_size_healthy,
    "archive_success_healthy": archive_success_healthy,
    "permanent_evidence_preserved": permanent_evidence_preserved,
    "active_utilization_pct": active_utilization_pct,
    "storage_utilization_pct": storage_utilization_pct
}

active_utilization_pct := (input.active_count * 100.0) / max_active_files

storage_utilization_pct := (input.total_size_mb * 100.0) / max_total_size_mb

# ===== Policy Decision =====

policy_decision := {
    "allow": count(deny) == 0,
    "deny_reasons": deny,
    "warnings": warn,
    "info": info,
    "assessment": assessment,
    "recommendation": recommendation
}

# Recommendation based on assessment
recommendation := "Evidence storage healthy - no action required" if {
    count(deny) == 0
    count(warn) == 0
} else := "Execute rolling window cleanup immediately" if {
    not active_count_healthy
} else := "Execute rolling window cleanup soon" if {
    not storage_size_healthy
} else := "Monitor archive success rate" if {
    input.archived_count > 0
    not archive_success_healthy
} else := "Monitor warnings"

# ===== Testing =====

# Test case: Healthy evidence storage
test_healthy_evidence if {
    test_input := {
        "permanent_count": 10,
        "active_count": 45,
        "archived_count": 120,
        "total_size_mb": 25.5,
        "archive_success_rate": 98.5
    }

    result := policy_decision with input as test_input
    result.allow == true
}

# Test case: Too many active files
test_too_many_files if {
    test_input := {
        "permanent_count": 10,
        "active_count": 600,
        "archived_count": 120,
        "total_size_mb": 25.5,
        "archive_success_rate": 98.5
    }

    result := policy_decision with input as test_input
    result.allow == false
    count(result.deny_reasons) > 0
}

# Test case: Storage too large
test_storage_too_large if {
    test_input := {
        "permanent_count": 10,
        "active_count": 45,
        "archived_count": 120,
        "total_size_mb": 150.0,
        "archive_success_rate": 98.5
    }

    result := policy_decision with input as test_input
    result.allow == false
    count(result.deny_reasons) > 0
}

# Test case: Low archive success rate
test_low_archive_success if {
    test_input := {
        "permanent_count": 10,
        "active_count": 45,
        "archived_count": 120,
        "total_size_mb": 25.5,
        "archive_success_rate": 85.0
    }

    result := policy_decision with input as test_input
    result.allow == false
    count(result.deny_reasons) > 0
}
