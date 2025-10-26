
package ssid.meta.orchestrator

default deny = false

# Deny if required SoT artifacts are missing in boot report
deny[msg] {
  input.boot_report_required == true
  some i
  art := input.artifacts[i]
  art.priority == "MUST"
  not art.present
  msg := sprintf("missing MUST artifact: %s", [art.path])
}

# Warn if global boot score below threshold
warn[msg] {
  input.global_score < 90
  msg := sprintf("low global boot score: %d", [input.global_score])
}
