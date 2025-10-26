
package ssid.security.quarantine

default quarantine = false
default deny = false

quarantine[msg] {
  input.positives > 0
  msg := sprintf("malware positives: %d", [input.positives])
}

deny[msg] {
  input.drift > 0
  msg := sprintf("integrity drift detected: %d files", [input.drift])
}
