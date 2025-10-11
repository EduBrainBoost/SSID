"""
Bridge: 03_core → 20_foundation
Purpose: Token operations interface - expose token metadata for core operations
Evidence: SHA-256 logged in 24_meta_orchestration/registry/logs/
"""

import sys
import os
from typing import Dict

# Add path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

try:
    from foundation.tokenomics.token_model import SSIDTokenModel  # type: ignore
except ImportError:
    # Fallback for direct imports
    try:
        from tokenomics.token_model import SSIDTokenModel  # type: ignore
    except ImportError:
        # Final fallback with absolute import
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "token_model",
            os.path.join(os.path.dirname(__file__), "../../20_foundation/tokenomics/token_model.py")
        )
        if spec and spec.loader:
            token_model = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(token_model)
            SSIDTokenModel = token_model.SSIDTokenModel
        else:
            raise ImportError("Could not load SSIDTokenModel")


def get_token_info() -> Dict[str, str]:
    """
    Retrieve current SSID Token model metadata.

    Returns:
        Dict containing token symbol, decimals, governance contract address
    """
    return {
        "symbol": SSIDTokenModel.symbol,
        "name": SSIDTokenModel.name,
        "decimals": str(SSIDTokenModel.decimals),
        "governance": SSIDTokenModel.governance_contract,
        "treasury": SSIDTokenModel.treasury_address,
    }


def validate_token_operation(operation: str, amount: int) -> bool:
    """
    Validate token operation against token model constraints.

    Args:
        operation: Type of operation (transfer, mint, burn)
        amount: Token amount (in smallest unit)

    Returns:
        True if operation is valid, False otherwise
    """
    if operation not in ["transfer", "mint", "burn"]:
        return False

    if amount < 0:
        return False

    # Check against total supply for minting
    if operation == "mint" and amount > SSIDTokenModel.total_supply:
        return False

    return True


if __name__ == "__main__":
    # Self-test
    print("Bridge: 03_core → 20_foundation")
    print("Token Info:", get_token_info())
    print("Valid transfer:", validate_token_operation("transfer", 1000))
    print("Invalid operation:", validate_token_operation("invalid", 1000))
