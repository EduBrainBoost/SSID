"""Meta Identity module."""

from .did_resolver import (
    resolve_did,
    register_did,
    verify_did_signature,
    get_did_metadata,
)

__all__ = [
    "resolve_did",
    "register_did",
    "verify_did_signature",
    "get_did_metadata",
]
