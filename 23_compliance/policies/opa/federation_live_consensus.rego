package ssid.federation.live_consensus

default allow = false

# Deny if contracts store balances or accept ETH (custody risk)
deny[msg] {
  input.contract.analysis.has_balance_storage == true
  msg := "Custody risk: balance storage detected"
}

deny[msg] {
  input.contract.analysis.accepts_value == true
  msg := "Custody risk: payable/receive detected"
}

# Allow when only hash anchoring events are emitted
allow {
  input.contract.analysis.hash_only == true
  not deny[_]
}
