"""Interconnect bridges for 10_interoperability root."""

from .bridge_meta_identity import (
    resolve_external_did,
    verify_external_did_signature,
    get_external_did_info,
    resolve_did_batch,
    validate_did_format,
)

__all__ = [
    "resolve_external_did",
    "verify_external_did_signature",
    "get_external_did_info",
    "resolve_did_batch",
    "validate_did_format",
]
