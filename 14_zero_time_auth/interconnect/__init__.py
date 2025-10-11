"""Interconnect bridges for 14_zero_time_auth root."""

from .bridge_identity_score import (
    auth_trust_level,
    check_auth_threshold,
    classify_auth_risk,
    recommend_auth_method,
)

__all__ = [
    "auth_trust_level",
    "check_auth_threshold",
    "classify_auth_risk",
    "recommend_auth_method",
]
