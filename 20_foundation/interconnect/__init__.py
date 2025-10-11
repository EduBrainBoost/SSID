"""Interconnect bridges for 20_foundation root."""

from .bridge_meta_orchestration import (
    record_registry_lock,
    get_last_sync_timestamp,
    verify_lock_integrity,
)

__all__ = [
    "record_registry_lock",
    "get_last_sync_timestamp",
    "verify_lock_integrity",
]
