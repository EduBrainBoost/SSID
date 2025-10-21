package ssid.guard

default allow = false

# Allow when there are no path violations
allow {
  count(deny) == 0
}

deny[msg] {
  some i
  f := input.files[i]
  not startswith_any(f.path, input.allowed_roots)
  msg := sprintf("path outside Root-24: %s", [f.path])
}

startswith_any(p, arr) {
  some j
  startswith(p, arr[j])
}
