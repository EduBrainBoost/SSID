# Fee & Fairness Calculation Report (v5.4.3)
Generated: 2025-10-14 19:11:51 UTC

## Input: 7-Säulen absolute weights (as provided)
- legal_compliance: 0.35
- audit_security: 0.30
- technical_maintenance: 0.30
- dao_treasury: 0.25
- community_bonus: 0.20
- liquidity_reserve: 0.20
- marketing_partnerships: 0.20

Sum of weights: 1.80 (EXPECTED 1.80)

## Normalization Strategy
Normalized each weight by dividing by 1.80 and multiplying by the exact system pool (2% of total amount).

## Exact Shares (as fraction of TOTAL amount)
{
  "legal_compliance": "0.003888888888888888888888888888888888888888",
  "audit_security": "0.003333333333333333333333333333333333333334",
  "technical_maintenance": "0.003333333333333333333333333333333333333334",
  "dao_treasury": "0.002777777777777777777777777777777777777778",
  "community_bonus": "0.002222222222222222222222222222222222222222",
  "liquidity_reserve": "0.002222222222222222222222222222222222222222",
  "marketing_partnerships": "0.002222222222222222222222222222222222222222"
}

## Basis Points (of TOTAL amount, 1% = 100 bp)
{
  "legal_compliance": "38.88888888888888888888888888888888888888",
  "audit_security": "33.33333333333333333333333333333333333334",
  "technical_maintenance": "33.33333333333333333333333333333333333334",
  "dao_treasury": "27.77777777777777777777777777777777777778",
  "community_bonus": "22.22222222222222222222222222222222222222",
  "liquidity_reserve": "22.22222222222222222222222222222222222222",
  "marketing_partnerships": "22.22222222222222222222222222222222222222"
}

Sum of exact shares (percent of amount): 0.02000000000000000000000000000000000000000
Sum of exact shares (basis points): 200.0000000000000000000000000000000000000  # EXPECTED 200.0 bp

## Developer Share
- developer_percent_of_amount: 0.01 (exact 1%)

## Subscription Split (second source, fixed ratios)
{
  "system_operational": "0.50",
  "dao_treasury": "0.30",
  "developer_core": "0.10",
  "incentive_reserve": "0.10"
}
