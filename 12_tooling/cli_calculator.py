# -*- coding: utf-8 -*-
import sys, json
from pathlib import Path
from decimal import Decimal, getcontext

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent / "03_core"))

from fee_distribution_engine import distribute

getcontext().prec = 40

def main():
    if len(sys.argv) != 2:
        print("Usage: cli_calculator.py <amount_eur>")
        sys.exit(1)
    amount = Decimal(sys.argv[1])
    result = distribute(amount)
    # round to cents for display
    def r2(x): return x.quantize(Decimal("0.01"))
    out = {
        "amount": str(r2(amount)),
        "developer_reward": str(r2(result["developer_reward"])),
        "system_pool_total": str(r2(result["system_pool_total"])),
        "categories": {k: str(r2(v)) for k, v in result["categories"].items()}
    }
    print(json.dumps(out, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
