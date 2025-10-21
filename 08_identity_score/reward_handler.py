# -*- coding: utf-8 -*-
from decimal import Decimal, getcontext

getcontext().prec = 40

TOKEN_MULTIPLIER = Decimal("1.10")

def process_reward(amount_eur: Decimal, user_override: bool=False):
    """
    Hybrid payout model:
    - Up to 100 EUR fiat
    - Excess as token with multiplier, unless user_override=True
    Returns dict with 'cash' and 'token' amounts
    """
    cap = Decimal("100")
    if not user_override and amount_eur > cap:
        cash = cap
        token = (amount_eur - cap) * TOKEN_MULTIPLIER
        return {"cash": cash, "token": token}
    else:
        return {"cash": amount_eur, "token": Decimal("0")}
