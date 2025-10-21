# -*- coding: utf-8 -*-
from decimal import Decimal
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "03_core")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "08_identity_score")))
from fee_distribution_engine import distribute
from reward_handler import process_reward

def test_fee_distribution_exact_sum():
    amt = Decimal("1000")
    res = distribute(amt)
    assert res["developer_reward"] == amt * Decimal("0.01")
    assert res["system_pool_total"] == amt * Decimal("0.02")
    s = sum(res["categories"].values())
    assert s == res["system_pool_total"]

def test_distribution_values_example_rounding():
    amt = Decimal("1000")
    res = distribute(amt)
    # basic sanity: all categories positive
    for v in res["categories"].values():
        assert v > 0

def test_reward_handler_defaults_and_override():
    r = process_reward(Decimal("250"), user_override=False)
    assert r["cash"] == Decimal("100")
    assert r["token"] == Decimal("165")  # (250-100)*1.10
    r2 = process_reward(Decimal("250"), user_override=True)
    assert r2["cash"] == Decimal("250")
    assert r2["token"] == Decimal("0")
