# -*- coding: utf-8 -*-
from decimal import Decimal, getcontext

getcontext().prec = 40

DEVELOPER_PERCENT = Decimal("0.01")  # 1% of amount
SYSTEM_POOL_PERCENT = Decimal("0.02")  # 2% of amount

# Exact normalized shares (as fraction of TOTAL amount)
SYSTEM_SHARES = {
    "legal_compliance": Decimal("0.003888888888888888888888888888888888888888"),
    "audit_security": Decimal("0.003333333333333333333333333333333333333334"),
    "technical_maintenance": Decimal("0.003333333333333333333333333333333333333334"),
    "dao_treasury": Decimal("0.002777777777777777777777777777777777777778"),
    "community_bonus": Decimal("0.002222222222222222222222222222222222222222"),
    "liquidity_reserve": Decimal("0.002222222222222222222222222222222222222222"),
    "marketing_partnerships": Decimal("0.002222222222222222222222222222222222222222"),
}

def distribute(amount: Decimal):
    """
    Returns exact distribution dict with Decimal values:
    - developer_reward
    - system_pool_total
    - per-category allocations summing to system_pool_total
    """
    dev = (amount * DEVELOPER_PERCENT)
    sys_total = (amount * SYSTEM_POOL_PERCENT)
    # build per-category
    per_cat = {k: (amount * v) for k, v in SYSTEM_SHARES.items()}
    # guard: sums must equal sys_total exactly
    s = sum(per_cat.values())
    if s != sys_total:
        # compensate potential rounding by adjusting the largest bucket minimally
        diff = sys_total - s
        largest_key = max(per_cat, key=lambda k: per_cat[k])
        per_cat[largest_key] += diff
    return {
        "developer_reward": dev,
        "system_pool_total": sys_total,
        "categories": per_cat
    }
