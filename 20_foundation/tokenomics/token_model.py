"""
SSID Token Model
Exposes token metadata and constants for inter-root dependencies.
"""

class SSIDTokenModel:
    """Core SSID Token model metadata."""

    symbol = "SSID"
    name = "Self-Sovereign Identity Token"
    decimals = 18
    total_supply = 1_000_000_000  # 1 billion tokens
    governance_contract = "0x0000000000000000000000000000000000000001"
    treasury_address = "0x0000000000000000000000000000000000000002"

    @staticmethod
    def get_metadata():
        """Return token metadata as dict."""
        return {
            "symbol": SSIDTokenModel.symbol,
            "name": SSIDTokenModel.name,
            "decimals": SSIDTokenModel.decimals,
            "total_supply": SSIDTokenModel.total_supply,
            "governance_contract": SSIDTokenModel.governance_contract,
            "treasury_address": SSIDTokenModel.treasury_address,
        }
