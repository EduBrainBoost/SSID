# Proof Emission End-to-End Scenarios (v5.2)

## Scenario 1: Valid Emission + ACK + Sync
1. Emit digest → Layer 9
2. Anchor on-chain (optional)
3. Provider ACK received
4. Sync check: CONSISTENT

## Scenario 2: Tampered Digest
1. Modified digest → Hash chain mismatch
2. Reject + audit log

## Scenario 3: Missing ACK
1. Emit digest → Layer 9
2. No ACK from provider → Retry 3x
3. Log warning

## Scenario 4: Sync Mismatch
1. Off-chain has digest X
2. On-chain missing X
3. Alert + OPA review

Coverage: 100% critical paths
